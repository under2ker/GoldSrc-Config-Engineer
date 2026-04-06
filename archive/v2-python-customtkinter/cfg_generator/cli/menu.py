import os
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich import box

from cfg_generator.i18n import t, load_language, get_lang
from cfg_generator.core.generator import (
    CfgConfig,
    get_all_cvars,
    get_modes,
    get_presets,
    create_mode_config,
    create_preset_config,
    create_quick_config,
    compare_configs,
)
from cfg_generator.core.validator import validate_cfg_text, validate_config_dict
from cfg_generator.core.optimizer import (
    get_gpu_vendors,
    get_performance_profiles,
    optimize_config,
)
from cfg_generator.io.exporter import export_single_cfg, export_full_config_set
from cfg_generator.io.importer import import_from_file, import_from_url, SecurityError

console = Console()

current_config: Optional[CfgConfig] = None


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    banner = Text()
    banner.append("  CS 1.6 Deep CFG Generator  ", style="bold white on blue")
    console.print()
    console.print(Panel(banner, border_style="bright_blue", box=box.DOUBLE))
    console.print(f"  {t('app.subtitle')}  |  {t('app.version')}", style="dim")
    console.print()


def wait_for_enter():
    console.print()
    Prompt.ask(f"[dim]{t('menu.press_enter')}[/dim]")


def show_main_menu():
    global current_config

    while True:
        clear_screen()
        show_banner()

        if current_config:
            mode_info = current_config.mode or current_config.preset_name or "Custom"
            console.print(
                f"  [green]Active config:[/green] {mode_info} "
                f"([cyan]{len(current_config.settings)}[/cyan] settings)\n"
            )

        table = Table(
            title=t("menu.main_title"),
            box=box.ROUNDED,
            border_style="bright_blue",
            show_header=False,
            padding=(0, 2),
        )
        table.add_column("N", style="bold cyan", width=4)
        table.add_column("Option", style="white")

        menu_items = [
            ("1", t("menu.create_new")),
            ("2", t("menu.load_preset")),
            ("3", t("menu.game_mode")),
            ("4", t("menu.hardware_opt")),
            ("5", t("menu.export_cfg")),
            ("6", t("menu.pro_players")),
            ("7", t("menu.import_cfg")),
            ("8", t("menu.settings")),
            ("0", t("menu.exit")),
        ]

        for num, label in menu_items:
            table.add_row(num, label)

        console.print(table)
        console.print()

        choice = Prompt.ask(t("menu.select_option"), choices=["0","1","2","3","4","5","6","7","8"])

        if choice == "1":
            menu_create_config()
        elif choice == "2":
            menu_load_preset()
        elif choice == "3":
            menu_select_mode()
        elif choice == "4":
            menu_hardware()
        elif choice == "5":
            menu_export()
        elif choice == "6":
            menu_pro_players()
        elif choice == "7":
            menu_import()
        elif choice == "8":
            menu_settings()
        elif choice == "0":
            console.print("\n[bright_blue]GG WP![/bright_blue]\n")
            sys.exit(0)


def menu_create_config():
    global current_config
    clear_screen()
    show_banner()

    console.print(Panel(t("generator.title"), border_style="green"))
    console.print()

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("N", style="bold cyan", width=4)
    table.add_column("Option")
    table.add_row("1", t("generator.quick_setup"))
    table.add_row("2", t("generator.advanced"))
    console.print(table)
    console.print()

    choice = Prompt.ask(t("menu.select_option"), choices=["1", "2"])

    if choice == "1":
        _quick_setup()
    else:
        _advanced_setup()


def _quick_setup():
    global current_config
    console.print()

    modes = get_modes()
    lang = get_lang()
    name_key = f"name_{lang}" if lang != "en" else "name_en"
    mode_list = list(modes.keys())

    console.print("[bold]" + t("modes.title") + "[/bold]")
    for i, key in enumerate(mode_list, 1):
        console.print(f"  [cyan]{i}[/cyan]. {modes[key].get(name_key, key)}")
    console.print()

    mode_idx = IntPrompt.ask("Mode", default=1) - 1
    mode_idx = max(0, min(mode_idx, len(mode_list) - 1))
    mode_key = mode_list[mode_idx]

    sens = FloatPrompt.ask("Sensitivity", default=2.5)
    fps = IntPrompt.ask("fps_max", default=100)
    vol = FloatPrompt.ask("Volume (0-1)", default=0.7)

    current_config = create_quick_config(mode_key, sens, fps, vol)

    console.print(f"\n[green]{t('generator.config_ready')}[/green]")
    console.print(f"[dim]Mode: {modes[mode_key].get(name_key, mode_key)}[/dim]")
    console.print(f"[dim]Settings: {len(current_config.settings)}[/dim]")

    wait_for_enter()


def _advanced_setup():
    global current_config
    console.print()

    if current_config is None:
        current_config = create_mode_config("classic")

    cvars = get_all_cvars()
    lang = get_lang()
    desc_key = f"description_{lang}" if lang != "en" else "description_en"

    categories = [
        ("video", t("generator.category_video")),
        ("audio", t("generator.category_audio")),
        ("input", t("generator.category_input")),
        ("network", t("generator.category_network")),
        ("gameplay", t("generator.category_gameplay")),
    ]

    console.print("[bold]Select category to edit:[/bold]")
    for i, (key, label) in enumerate(categories, 1):
        console.print(f"  [cyan]{i}[/cyan]. {label}")
    console.print()

    cat_idx = IntPrompt.ask("Category", default=1) - 1
    cat_idx = max(0, min(cat_idx, len(categories) - 1))
    cat_key, cat_label = categories[cat_idx]

    cat_cvars = cvars.get(cat_key, {})
    cvar_list = list(cat_cvars.keys())

    clear_screen()
    show_banner()
    console.print(Panel(f"[bold]{cat_label}[/bold]", border_style="green"))

    table = Table(box=box.SIMPLE, border_style="dim")
    table.add_column("N", style="cyan", width=4)
    table.add_column("CVAR", style="bold")
    table.add_column("Current", style="yellow")
    table.add_column("Description")

    for i, cvar_name in enumerate(cvar_list, 1):
        cvar_info = cat_cvars[cvar_name]
        current_val = current_config.get(cvar_name, cvar_info.get("default", "—"))
        desc = cvar_info.get(desc_key, cvar_info.get("description_en", ""))
        table.add_row(str(i), cvar_name, current_val, desc)

    console.print(table)
    console.print()
    console.print("[dim]Enter CVAR number to edit, or 0 to go back[/dim]")

    while True:
        cvar_idx_str = Prompt.ask("CVAR #", default="0")
        try:
            cvar_idx = int(cvar_idx_str)
        except ValueError:
            continue
        if cvar_idx == 0:
            break
        if cvar_idx < 1 or cvar_idx > len(cvar_list):
            console.print(f"[red]{t('menu.invalid_choice')}[/red]")
            continue

        cvar_name = cvar_list[cvar_idx - 1]
        cvar_info = cat_cvars[cvar_name]
        current_val = current_config.get(cvar_name, cvar_info.get("default", ""))

        hint = ""
        if "range" in cvar_info:
            lo, hi = cvar_info["range"]
            hint = f" (range: {lo}—{hi})"
        elif "values" in cvar_info:
            hint = f" (values: {', '.join(cvar_info['values'])})"

        console.print(f"\n[bold]{cvar_name}[/bold]{hint}")
        console.print(f"Current: [yellow]{current_val}[/yellow]")

        new_val = Prompt.ask("New value", default=current_val)
        current_config.set(cvar_name, new_val)
        console.print(f"[green]{cvar_name} = \"{new_val}\"[/green]")

    console.print(f"\n[green]{t('generator.config_ready')}[/green]")
    wait_for_enter()


def menu_select_mode():
    global current_config
    clear_screen()
    show_banner()

    modes = get_modes()
    lang = get_lang()
    name_key = f"name_{lang}" if lang != "en" else "name_en"
    desc_key = f"description_{lang}" if lang != "en" else "description_en"

    console.print(Panel(t("modes.title"), border_style="green"))

    table = Table(box=box.ROUNDED, border_style="bright_blue")
    table.add_column("N", style="bold cyan", width=4)
    table.add_column("Mode", style="bold")
    table.add_column("Description")

    mode_list = list(modes.keys())
    for i, key in enumerate(mode_list, 1):
        mode = modes[key]
        table.add_row(
            str(i),
            mode.get(name_key, key),
            mode.get(desc_key, ""),
        )

    console.print(table)
    console.print()

    choice = IntPrompt.ask(t("menu.select_option"), default=1)
    idx = max(0, min(choice - 1, len(mode_list) - 1))
    mode_key = mode_list[idx]

    current_config = create_mode_config(mode_key)

    console.print(
        f"\n[green]{t('modes.selected', mode=modes[mode_key].get(name_key, mode_key))}[/green]"
    )
    console.print(f"[dim]Settings loaded: {len(current_config.settings)}[/dim]")

    wait_for_enter()


def menu_load_preset():
    global current_config
    clear_screen()
    show_banner()

    presets = get_presets()
    lang = get_lang()
    desc_key = f"description_{lang}" if lang != "en" else "description_en"

    console.print(Panel(t("preset.title"), border_style="green"))

    table = Table(box=box.ROUNDED, border_style="bright_blue")
    table.add_column("N", style="bold cyan", width=4)
    table.add_column("Player", style="bold")
    table.add_column(t("preset.team"))
    table.add_column(t("preset.role"), style="dim")
    table.add_column("Sens", style="yellow")

    preset_list = list(presets.keys())
    for i, key in enumerate(preset_list, 1):
        p = presets[key]
        sens = p.get("settings", {}).get("sensitivity", "?")
        table.add_row(
            str(i),
            p.get("name", key),
            p.get("team", ""),
            p.get("role", ""),
            sens,
        )

    console.print(table)
    console.print()

    choice = IntPrompt.ask(t("preset.select"), default=1)
    idx = max(0, min(choice - 1, len(preset_list) - 1))
    preset_key = preset_list[idx]

    current_config = create_preset_config(preset_key)

    console.print(
        f"\n[green]{t('preset.applied', name=presets[preset_key].get('name', preset_key))}[/green]"
    )

    wait_for_enter()


def menu_hardware():
    global current_config
    clear_screen()
    show_banner()

    if current_config is None:
        current_config = create_mode_config("classic")

    console.print(Panel(t("hardware.title"), border_style="green"))

    vendors = get_gpu_vendors()
    console.print(f"[bold]{t('hardware.select_gpu')}[/bold]")
    for i, (key, name) in enumerate(vendors, 1):
        console.print(f"  [cyan]{i}[/cyan]. {name}")
    console.print()
    v_choice = IntPrompt.ask(t("menu.select_option"), default=1)
    v_idx = max(0, min(v_choice - 1, len(vendors) - 1))
    gpu_vendor = vendors[v_idx][0]

    console.print()
    profiles = get_performance_profiles()
    console.print(f"[bold]{t('hardware.select_profile')}[/bold]")
    for i, (key, name) in enumerate(profiles, 1):
        console.print(f"  [cyan]{i}[/cyan]. {name}")
    console.print()
    p_choice = IntPrompt.ask(t("menu.select_option"), default=3)
    p_idx = max(0, min(p_choice - 1, len(profiles) - 1))
    perf_profile = profiles[p_idx][0]

    current_config, tips, launch_opts = optimize_config(
        current_config, gpu_vendor, perf_profile
    )

    console.print(f"\n[green]{t('hardware.applied')}[/green]")

    if tips:
        console.print(f"\n[bold]{t('hardware.tips_title')}:[/bold]")
        for tip in tips:
            console.print(f"  [yellow]*[/yellow] {tip}")

    if launch_opts:
        console.print(f"\n[bold]{t('hardware.launch_options')}:[/bold]")
        console.print(f"  [cyan]{launch_opts}[/cyan]")

    wait_for_enter()


def menu_export():
    global current_config
    clear_screen()
    show_banner()

    if current_config is None:
        console.print(f"[red]{t('export.no_config')}[/red]")
        wait_for_enter()
        return

    console.print(Panel(t("export.title"), border_style="green"))
    console.print()

    console.print("  [cyan]1[/cyan]. Single autoexec.cfg")
    console.print("  [cyan]2[/cyan]. Full config set (split by category)")
    console.print()

    choice = Prompt.ask(t("menu.select_option"), choices=["1", "2"])

    if choice == "1":
        filename = Prompt.ask(t("export.filename"), default="autoexec.cfg")
        try:
            path = export_single_cfg(current_config, filename)
            console.print(f"\n[green]{t('export.success', path=path)}[/green]")

            console.print("\n[bold]Preview:[/bold]")
            preview = current_config.to_cfg_string()
            preview_lines = preview.splitlines()[:20]
            for line in preview_lines:
                console.print(f"  [dim]{line}[/dim]")
            if len(preview.splitlines()) > 20:
                console.print(f"  [dim]... ({len(preview.splitlines())} lines total)[/dim]")
        except Exception as e:
            console.print(f"\n[red]{t('export.error', error=str(e))}[/red]")
    else:
        try:
            exported = export_full_config_set(current_config)
            console.print(f"\n[green]{t('common.done')}[/green]")
            for fname, fpath in exported.items():
                console.print(f"  [cyan]{fname}[/cyan] -> {fpath}")
        except Exception as e:
            console.print(f"\n[red]{t('export.error', error=str(e))}[/red]")

    wait_for_enter()


def menu_pro_players():
    global current_config
    clear_screen()
    show_banner()

    presets = get_presets()
    lang = get_lang()

    console.print(Panel(t("preset.title"), border_style="green"))

    table = Table(box=box.ROUNDED, border_style="bright_blue")
    table.add_column("N", style="bold cyan", width=4)
    table.add_column("Player", style="bold")
    table.add_column(t("preset.team"))
    table.add_column(t("preset.country"), style="dim")
    table.add_column(t("preset.role"))
    table.add_column("Sens", style="yellow")
    table.add_column("fps_max", style="yellow")

    preset_list = list(presets.keys())
    for i, key in enumerate(preset_list, 1):
        p = presets[key]
        s = p.get("settings", {})
        table.add_row(
            str(i),
            p.get("name", key),
            p.get("team", ""),
            p.get("country", ""),
            p.get("role", ""),
            s.get("sensitivity", "?"),
            s.get("fps_max", "?"),
        )

    console.print(table)
    console.print()

    if current_config:
        console.print(f"  [cyan]C[/cyan]. {t('preset.compare')}")

    console.print(f"  [cyan]0[/cyan]. {t('menu.back')}")
    console.print()

    choice_str = Prompt.ask(t("menu.select_option"))

    if choice_str.lower() == "c" and current_config:
        _compare_menu(preset_list)
    elif choice_str == "0":
        return
    else:
        try:
            idx = int(choice_str) - 1
            if 0 <= idx < len(preset_list):
                current_config = create_preset_config(preset_list[idx])
                console.print(
                    f"\n[green]{t('preset.applied', name=presets[preset_list[idx]].get('name', ''))}[/green]"
                )
        except ValueError:
            console.print(f"[red]{t('menu.invalid_choice')}[/red]")

    wait_for_enter()


def _compare_menu(preset_list: list[str]):
    presets = get_presets()
    console.print()
    console.print("[bold]Select preset to compare:[/bold]")
    for i, key in enumerate(preset_list, 1):
        console.print(f"  [cyan]{i}[/cyan]. {presets[key].get('name', key)}")

    choice = IntPrompt.ask(t("menu.select_option"), default=1)
    idx = max(0, min(choice - 1, len(preset_list) - 1))
    preset_key = preset_list[idx]

    diffs = compare_configs(current_config, preset_key)

    if not diffs:
        console.print("\n[green]No differences found![/green]")
        return

    table = Table(
        title=t("compare.title"),
        box=box.ROUNDED,
        border_style="yellow",
    )
    table.add_column(t("compare.parameter"), style="bold")
    table.add_column(t("compare.your_config"), style="cyan")
    table.add_column(
        t("compare.pro_config", name=presets[preset_key].get("name", "")),
        style="yellow",
    )

    for param, your_val, pro_val in diffs:
        table.add_row(param, your_val, pro_val)

    console.print()
    console.print(table)


def menu_import():
    global current_config
    clear_screen()
    show_banner()

    console.print(Panel(t("import.title"), border_style="green"))
    console.print()
    console.print(f"  [cyan]1[/cyan]. {t('import.from_file')}")
    console.print(f"  [cyan]2[/cyan]. {t('import.from_url')}")
    console.print()

    choice = Prompt.ask(t("menu.select_option"), choices=["1", "2"])

    try:
        if choice == "1":
            path = Prompt.ask(t("import.enter_path"))
            cfg, summary = import_from_file(path)
        else:
            url = Prompt.ask(t("import.enter_url"))
            cfg, summary = import_from_url(url)

        current_config = cfg
        console.print(
            f"\n[green]{t('import.success', count=len(cfg.settings))}[/green]"
        )
        console.print(f"[dim]{summary}[/dim]")
    except FileNotFoundError:
        console.print(f"\n[red]{t('import.file_not_found', path=path)}[/red]")
    except SecurityError as e:
        console.print(f"\n[red]{str(e)}[/red]")
    except Exception as e:
        console.print(f"\n[red]{t('import.error', error=str(e))}[/red]")

    wait_for_enter()


def menu_settings():
    clear_screen()
    show_banner()

    console.print(Panel(t("menu.settings"), border_style="green"))
    console.print()

    current_lang = get_lang()
    console.print(f"  Current language: [cyan]{current_lang}[/cyan]")
    console.print()
    console.print("  [cyan]1[/cyan]. Russian (RU)")
    console.print("  [cyan]2[/cyan]. English (EN)")
    console.print()

    choice = Prompt.ask(t("menu.select_option"), choices=["1", "2"])
    if choice == "1":
        load_language("ru")
    else:
        load_language("en")

    console.print(f"\n[green]{t('common.done')}[/green]")
    wait_for_enter()
