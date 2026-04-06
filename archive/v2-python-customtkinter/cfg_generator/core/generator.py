import json
import os
from datetime import datetime
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

_cache: dict[str, dict] = {}


_DEFAULTS: dict[str, dict] = {
    "cvars.json": {"mouse": {}, "video": {}, "audio": {}, "network": {}, "gameplay": {}},
    "modes.json": {},
    "presets.json": {},
    "hardware.json": {"gpu_vendors": {}, "performance_profiles": {}},
    "aliases.json": {"toggle_aliases": {}, "utility_aliases": {}},
    "buyscripts.json": {"weapons": {}, "equipment": {}, "presets": {}},
    "network_presets.json": {},
    "visual_presets.json": {},
    "crosshair_presets.json": {},
    "keyboard_layout.json": {"rows": []},
}

_load_warnings: list[str] = []


def get_load_warnings() -> list[str]:
    return list(_load_warnings)


def _load_json(filename: str) -> dict:
    if filename not in _cache:
        path = os.path.join(DATA_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"Expected dict, got {type(data).__name__}")
            _cache[filename] = data
        except FileNotFoundError:
            _load_warnings.append(f"Файл не найден: {filename} — используются дефолты")
            _cache[filename] = _DEFAULTS.get(filename, {})
        except (json.JSONDecodeError, ValueError) as exc:
            _load_warnings.append(f"Повреждён {filename}: {exc} — используются дефолты")
            _cache[filename] = _DEFAULTS.get(filename, {})
        except OSError as exc:
            _load_warnings.append(f"Ошибка чтения {filename}: {exc} — используются дефолты")
            _cache[filename] = _DEFAULTS.get(filename, {})
    return _cache[filename]


def clear_cache():
    _cache.clear()


# ------------------------------------------------------------------ data access
def get_all_cvars() -> dict:
    return _load_json("cvars.json")

def get_modes() -> dict:
    return _load_json("modes.json")

def get_presets() -> dict:
    return _load_json("presets.json")

def get_hardware_data() -> dict:
    return _load_json("hardware.json")

def get_aliases() -> dict:
    return _load_json("aliases.json")

def get_buyscripts() -> dict:
    return _load_json("buyscripts.json")

def get_network_presets() -> dict:
    return _load_json("network_presets.json")

def get_visual_presets() -> dict:
    return _load_json("visual_presets.json")

def get_crosshair_presets() -> dict:
    return _load_json("crosshair_presets.json")

def get_keyboard_layout() -> dict:
    return _load_json("keyboard_layout.json")

def get_templates() -> dict:
    return _load_json("templates.json")


# ------------------------------------------------------------------ CfgConfig
class CfgConfig:
    """Holds a mutable set of CS 1.6 CVAR settings, binds, and aliases."""

    def __init__(self):
        self.settings: dict[str, str] = {}
        self.binds: dict[str, str] = {}
        self.buy_binds: dict[str, str] = {}
        self.aliases: list[dict] = []
        self.buy_aliases: list[dict] = []
        self.mode: Optional[str] = None
        self.mode_key: Optional[str] = None
        self.preset_name: Optional[str] = None
        self.description: str = ""
        self.network_preset: Optional[str] = None
        self.visual_preset: Optional[str] = None
        self.crosshair_preset: Optional[str] = None
        self.include_practice: bool = False

    def set(self, cvar: str, value: str) -> None:
        self.settings[cvar] = value

    def get(self, cvar: str, default: str = "") -> str:
        return self.settings.get(cvar, default)

    def remove(self, cvar: str) -> None:
        self.settings.pop(cvar, None)

    def merge(self, other: dict[str, str]) -> None:
        self.settings.update(other)

    def merge_binds(self, binds: dict[str, str]) -> None:
        self.binds.update(binds)


# ------------------------------------------------------------------ helpers
CVAR_DESCRIPTIONS: dict[str, str] = {}

def _build_cvar_descriptions() -> dict[str, str]:
    global CVAR_DESCRIPTIONS
    if CVAR_DESCRIPTIONS:
        return CVAR_DESCRIPTIONS
    cvars_db = get_all_cvars()
    for _cat, cvars in cvars_db.items():
        for cvar_name, info in cvars.items():
            CVAR_DESCRIPTIONS[cvar_name] = info.get("description_ru",
                                             info.get("description_en", ""))
    return CVAR_DESCRIPTIONS


def _categorize_settings(settings: dict[str, str]) -> dict[str, dict[str, str]]:
    cvars_db = get_all_cvars()
    cvar_to_cat: dict[str, str] = {}
    for cat, cvars in cvars_db.items():
        for cvar_name in cvars:
            cvar_to_cat[cvar_name] = cat

    categorized: dict[str, dict[str, str]] = {}
    for cvar, value in settings.items():
        cat = cvar_to_cat.get(cvar, "other")
        categorized.setdefault(cat, {})[cvar] = value

    return categorized


def _fmt_cvar_line(cvar: str, value: str, descs: dict[str, str], col: int = 40) -> str:
    """Format a CVAR line with aligned comment."""
    if value.startswith('"') and value.endswith('"'):
        base = f'{cvar} {value}'
    else:
        base = f'{cvar} "{value}"'
    desc = descs.get(cvar, "")
    if desc:
        pad = max(1, col - len(base))
        return f'{base}{" " * pad}// {desc}'
    return base


# ------------------------------------------------------------------ modular generation

def generate_aliases_cfg(cfg: CfgConfig) -> str:
    """Generate aliases.cfg content."""
    lines = [
        "// ================================================================",
        "// ALIASES.CFG — All script aliases",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]

    aliases_db = get_aliases()
    sections = [
        ("movement",      "MOVEMENT ALIASES"),
        ("weapon",        "WEAPON ALIASES"),
        ("communication", "COMMUNICATION ALIASES"),
        ("utility",       "UTILITY ALIASES"),
    ]

    if cfg.mode_key == "kz":
        sections.append(("kz_specific", "KZ-SPECIFIC ALIASES"))
    elif cfg.mode_key == "surf":
        sections.append(("surf_specific", "SURF-SPECIFIC ALIASES"))

    if cfg.include_practice:
        sections.append(("practice", "PRACTICE MODE (sv_cheats 1)"))

    for sec_key, sec_label in sections:
        sec_data = aliases_db.get(sec_key, {})
        alias_list = sec_data.get("aliases", [])
        if not alias_list:
            continue

        lines.append(f"// --------------------------------")
        lines.append(f"// {sec_label}")
        lines.append(f"// --------------------------------")
        lines.append("")

        for a in alias_list:
            safety = a.get("safety", "SAFE")
            desc = a.get("description", "")
            marker = f"[{safety}]"
            name = a.get("name", "")

            if "plus" in a:
                lines.append(f'alias "{name}" "{a["plus"]}"'.ljust(50) + f'// {marker} {desc} (нажатие)')
                minus_name = name.replace("+", "-", 1)
                lines.append(f'alias "{minus_name}" "{a["minus"]}"'.ljust(50) + f'// {marker} {desc} (отпускание)')
            elif a.get("type") == "cycle":
                states = a.get("states", [])
                lines.append(f'// {desc}')
                for st in states:
                    lines.append(
                        f'alias "{st["name"]}" "{st["command"]}; alias {name} {st["next"]}"'
                        .ljust(50) + f'// {marker}'
                    )
                lines.append(f'alias "{name}" "{states[0]["name"]}"'.ljust(50) + f'// {marker} init')
            elif a.get("type") == "toggle":
                on_cmd = a["on"]["command"]
                off_cmd = a["off"]["command"]
                on_name = f"{name}_on"
                off_name = f"{name}_off"
                lines.append(f'// {desc}')
                lines.append(
                    f'alias "{on_name}" "{on_cmd}; alias {name} {off_name}"'
                    .ljust(50) + f'// {marker}'
                )
                lines.append(
                    f'alias "{off_name}" "{off_cmd}; alias {name} {on_name}"'
                    .ljust(50) + f'// {marker}'
                )
                lines.append(f'alias "{name}" "{on_name}"'.ljust(50) + f'// {marker} init')
            elif a.get("type") == "kz_chain":
                cid = a.get("chain_id") or name or "kz_chain"
                steps = a.get("steps", [])
                lines.append(f"// {desc}")
                lines.append(
                    f'// KZ chain: bind "KEY" "{cid}_go" — one press per step ({len(steps)} steps)'
                )
                for i, cmd in enumerate(steps):
                    cur = f"{cid}_{i + 1}"
                    nxt = f"{cid}_{i + 2}" if i < len(steps) - 1 else f"{cid}_1"
                    lines.append(
                        f'alias "{cur}" "{cmd}; alias {cid}_go {nxt}"'
                        .ljust(50) + f"// {marker}"
                    )
                lines.append(
                    f'alias "{cid}_go" "{cid}_1"'.ljust(50) + f"// {marker} entry"
                )
            else:
                cmd = a.get("command", "")
                lines.append(f'alias "{name}" "{cmd}"'.ljust(50) + f'// {marker} {desc}')

            lines.append("")

    return "\n".join(lines)


def generate_buyscripts_cfg(cfg: CfgConfig) -> str:
    """Generate buyscripts.cfg content."""
    lines = [
        "// ================================================================",
        "// BUYSCRIPTS.CFG — Buy script aliases and binds",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
        "// --------------------------------",
        "// BUY PRESET ALIASES",
        "// --------------------------------",
        "",
    ]

    bs = get_buyscripts()
    for key, preset in bs.get("presets", {}).items():
        cmd = preset["commands"]
        desc = preset.get("description", preset.get("name", ""))
        lines.append(f'alias "{key}" "{cmd}"'.ljust(50) + f'// [SAFE] {desc}')

    lines.append("")
    lines.append("// --------------------------------")
    lines.append("// BUY BINDS (Numpad)")
    lines.append("// --------------------------------")
    lines.append("")

    for key, alias in bs.get("default_binds", {}).items():
        bsd = bs.get("presets", {}).get(alias, {})
        desc = bsd.get("description", alias)
        lines.append(f'bind "{key}" "{alias}"'.ljust(50) + f'// {desc}')

    lines.append("")
    return "\n".join(lines)


def generate_communication_cfg(cfg: CfgConfig) -> str:
    """Generate communication.cfg content."""
    lines = [
        "// ================================================================",
        "// COMMUNICATION.CFG — Chat, radio, callouts",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
        "// --------------------------------",
        "// VOICE",
        "// --------------------------------",
        "",
    ]
    descs = _build_cvar_descriptions()

    voice_settings = {
        "voice_enable": "1",
        "voice_scale": "1.0",
    }
    for cvar, val in voice_settings.items():
        lines.append(_fmt_cvar_line(cvar, val, descs))
    lines.append("")

    lines.append("// --------------------------------")
    lines.append("// CHAT BINDS")
    lines.append("// --------------------------------")
    lines.append("")
    lines.append('bind "y" "messagemode"'.ljust(50) + "// Общий чат")
    lines.append('bind "u" "messagemode2"'.ljust(50) + "// Командный чат")
    lines.append("")

    lines.append("// --------------------------------")
    lines.append("// RADIO MENUS")
    lines.append("// --------------------------------")
    lines.append("")
    lines.append('bind "z" "radio1"'.ljust(50) + "// Радио-меню 1")
    lines.append('bind "x" "radio2"'.ljust(50) + "// Радио-меню 2")
    lines.append('bind "c" "radio3"'.ljust(50) + "// Радио-меню 3")
    lines.append("")

    return "\n".join(lines)


def generate_video_cfg(cfg: CfgConfig) -> str:
    """Generate video.cfg content."""
    lines = [
        "// ================================================================",
        "// VIDEO.CFG — Video and rendering settings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]
    descs = _build_cvar_descriptions()
    categorized = _categorize_settings(cfg.settings)

    video_settings = categorized.get("video", {})
    for cvar, val in sorted(video_settings.items()):
        lines.append(_fmt_cvar_line(cvar, val, descs))
    lines.append("")
    return "\n".join(lines)


def generate_audio_cfg(cfg: CfgConfig) -> str:
    """Generate audio.cfg content."""
    lines = [
        "// ================================================================",
        "// AUDIO.CFG — Sound settings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]
    descs = _build_cvar_descriptions()
    categorized = _categorize_settings(cfg.settings)

    audio_settings = categorized.get("audio", {})
    for cvar, val in sorted(audio_settings.items()):
        lines.append(_fmt_cvar_line(cvar, val, descs))
    lines.append("")
    return "\n".join(lines)


def generate_mouse_cfg(cfg: CfgConfig) -> str:
    """Generate mouse.cfg content."""
    lines = [
        "// ================================================================",
        "// MOUSE.CFG — Mouse and sensitivity settings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]
    descs = _build_cvar_descriptions()
    categorized = _categorize_settings(cfg.settings)

    input_settings = categorized.get("input", {})
    for cvar, val in sorted(input_settings.items()):
        lines.append(_fmt_cvar_line(cvar, val, descs))
    lines.append("")
    return "\n".join(lines)


def generate_network_cfg(cfg: CfgConfig) -> str:
    """Generate network.cfg content."""
    lines = [
        "// ================================================================",
        "// NETWORK.CFG — Network and rate settings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]
    descs = _build_cvar_descriptions()
    categorized = _categorize_settings(cfg.settings)

    net_settings = categorized.get("network", {})
    for cvar, val in sorted(net_settings.items()):
        lines.append(_fmt_cvar_line(cvar, val, descs))
    lines.append("")
    return "\n".join(lines)


def generate_crosshair_cfg(cfg: CfgConfig) -> str:
    """Generate crosshair.cfg content."""
    lines = [
        "// ================================================================",
        "// CROSSHAIR.CFG — Crosshair settings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]
    descs = _build_cvar_descriptions()

    xhair_cvars = [
        "cl_crosshair_size", "cl_crosshair_color",
        "cl_crosshair_translucent", "cl_dynamiccrosshair",
    ]
    for cvar in xhair_cvars:
        val = cfg.get(cvar)
        if val:
            lines.append(_fmt_cvar_line(cvar, val, descs))

    lines.append("")
    return "\n".join(lines)


def generate_hud_cfg(cfg: CfgConfig) -> str:
    """Generate hud.cfg content."""
    lines = [
        "// ================================================================",
        "// HUD.CFG — HUD and interface settings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
    ]
    descs = _build_cvar_descriptions()
    categorized = _categorize_settings(cfg.settings)

    gameplay_settings = categorized.get("gameplay", {})
    for cvar, val in sorted(gameplay_settings.items()):
        if cvar.startswith("cl_crosshair"):
            continue
        lines.append(_fmt_cvar_line(cvar, val, descs))

    lines.append("")
    return "\n".join(lines)


def generate_bindings_cfg(cfg: CfgConfig) -> str:
    """Generate bindings.cfg content."""
    lines = [
        "// ================================================================",
        "// BINDINGS.CFG — All key bindings",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
        "unbindall".ljust(50) + "// Сбросить все бинды перед назначением",
        "",
    ]

    kb = get_keyboard_layout()
    binds = kb.get("default_binds", {})
    for bk, bd in cfg.binds.items():
        binds[bk] = {"command": bd, "description": ""}

    sections = {
        "MOVEMENT": ["w", "a", "s", "d", "SPACE", "CTRL", "SHIFT"],
        "WEAPONS": ["1", "2", "3", "4", "5", "q", "r", "g"],
        "COMBAT": ["MOUSE1", "MOUSE2", "MOUSE3", "MOUSE4", "MOUSE5", "MWHEELUP", "MWHEELDOWN"],
        "COMMUNICATION": ["y", "u", "z", "x", "c", "v"],
        "UTILITY": ["e", "t", "f", "b", "`", "TAB"],
        "F-KEYS": [f"F{i}" for i in range(1, 13)],
        "NAVIGATION": ["INS", "DEL", "HOME", "END", "PGUP", "PGDN", "PAUSE"],
        "NUMPAD (BUY)": [
            "KP_INS", "KP_END", "KP_DOWNARROW", "KP_PGDN",
            "KP_LEFTARROW", "KP_5", "KP_RIGHTARROW",
            "KP_HOME", "KP_UPARROW", "KP_PGUP",
            "KP_ENTER", "KP_PLUS", "KP_MINUS", "KP_DEL",
            "KP_SLASH", "KP_MULTIPLY",
        ],
    }

    used_keys: set[str] = set()

    for sec_name, keys in sections.items():
        sec_lines = []
        for key in keys:
            bd = binds.get(key)
            if bd:
                cmd = bd["command"] if isinstance(bd, dict) else bd
                desc = bd.get("description", "") if isinstance(bd, dict) else ""
                line = f'bind "{key}" "{cmd}"'
                if desc:
                    line = line.ljust(50) + f"// {desc}"
                sec_lines.append(line)
                used_keys.add(key)
        if sec_lines:
            lines.append(f"// --------------------------------")
            lines.append(f"// {sec_name}")
            lines.append(f"// --------------------------------")
            lines.append("")
            lines.extend(sec_lines)
            lines.append("")

    extra = {k: v for k, v in binds.items() if k not in used_keys}
    if extra:
        lines.append("// --------------------------------")
        lines.append("// OTHER BINDS")
        lines.append("// --------------------------------")
        lines.append("")
        for key, bd in sorted(extra.items()):
            cmd = bd["command"] if isinstance(bd, dict) else bd
            desc = bd.get("description", "") if isinstance(bd, dict) else ""
            line = f'bind "{key}" "{cmd}"'
            if desc:
                line = line.ljust(50) + f"// {desc}"
            lines.append(line)
        lines.append("")

    return "\n".join(lines)


def generate_autoexec(cfg: CfgConfig, mode_key: str = "classic") -> str:
    """Generate the master autoexec.cfg that loads all modules."""
    lines = [
        "// ================================================================",
        "// AUTOEXEC.CFG — Master Config Loader",
        "// Generated by GoldSrc Config Engineer v3.0",
        f"// Mode: {cfg.mode or 'Classic'}",
        f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "// ================================================================",
        "",
        'echo "==============================="',
        'echo " Loading configuration..."',
        'echo "==============================="',
        "",
        'exec "config/aliases.cfg"'.ljust(50) + "// 1. Алиасы (до биндов!)",
        'exec "config/network.cfg"'.ljust(50) + "// 2. Сеть",
        'exec "config/video.cfg"'.ljust(50) + "// 3. Видео",
        'exec "config/audio.cfg"'.ljust(50) + "// 4. Звук",
        'exec "config/mouse.cfg"'.ljust(50) + "// 5. Мышь",
        'exec "config/crosshair.cfg"'.ljust(50) + "// 6. Кроссхейр",
        'exec "config/hud.cfg"'.ljust(50) + "// 7. HUD",
        'exec "config/buyscripts.cfg"'.ljust(50) + "// 8. Buy-скрипты",
        'exec "config/communication.cfg"'.ljust(50) + "// 9. Коммуникация",
        'exec "config/bindings.cfg"'.ljust(50) + "// 10. Бинды (после алиасов!)",
    ]

    modes = get_modes()
    for mk in modes:
        prefix = "" if mk == mode_key else "// "
        lines.append(f'{prefix}exec "config/modes/{mk}.cfg"'.ljust(50) + f"// Mode: {mk}")

    if cfg.include_practice:
        lines.append('exec "config/practice.cfg"'.ljust(50) + "// Практика (sv_cheats 1)")

    lines.append("")
    lines.append('echo "==============================="')
    lines.append('echo " Configuration loaded!"')
    lines.append('echo "==============================="')
    lines.append("")

    return "\n".join(lines)


def _console_banner(cfg: CfgConfig) -> list[str]:
    """Echo lines that render a styled banner in the CS 1.6 console (ASCII only)."""
    n_cvars = len(cfg.settings)
    n_binds = len(cfg.binds) + len(cfg.buy_binds)
    profile = cfg.preset_name or cfg.mode or "Custom"
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    e = []
    e.append('echo ""')
    e.append('echo "=============================================="')
    e.append('echo " .d8888b.   .d8888b.   .d8888b.  8888888888   "')
    e.append('echo "d88P  Y88b d88P  Y88b d88P  Y88b 888          "')
    e.append('echo "888    888 Y88b.      888    888 888           "')
    e.append('echo "888         Y888b.    888        8888888       "')
    e.append('echo "888  88888     Y88b.  888        888           "')
    e.append('echo "888    888       888  888    888 888           "')
    e.append('echo "Y88b  d88P Y88b  d88P Y88b  d88P 888          "')
    e.append('echo " Y8888P88   Y8888PP    Y8888PP  8888888888    "')
    e.append('echo ""')
    e.append('echo "  GoldSrc Config Engineer :: CS 1.6"')
    e.append('echo "=============================================="')
    e.append('echo ""')
    e.append(f'echo "  [*] Config loaded: {profile}"')
    e.append(f'echo "  [*] CVars applied: {n_cvars}"')
    e.append(f'echo "  [*] Binds set:     {n_binds}"')
    e.append(f'echo "  [*] Generated:     {date}"')
    e.append('echo ""')
    e.append('echo "  -----------------------------------------------"')
    e.append('echo "   Settings applied successfully!"')
    e.append('echo "   GL HF! :)"')
    e.append('echo "  -----------------------------------------------"')
    e.append('echo ""')
    return e


def generate_single_cfg(cfg: CfgConfig) -> str:
    """Generate a single all-in-one .cfg file (legacy mode)."""
    lines: list[str] = []
    descs = _build_cvar_descriptions()

    lines.append("// ================================================================")
    lines.append("// Generated by GoldSrc Config Engineer v3.0")
    if cfg.mode:
        lines.append(f"// Mode: {cfg.mode}")
    if cfg.preset_name:
        lines.append(f"// Preset: {cfg.preset_name}")
    lines.append(f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if cfg.description:
        lines.append(f"// {cfg.description}")
    lines.append("// ================================================================")
    lines.append("")

    # console banner at the top
    lines.extend(_console_banner(cfg))
    lines.append("")

    categories = _categorize_settings(cfg.settings)
    category_labels = {
        "video": "VIDEO",
        "audio": "AUDIO",
        "input": "MOUSE / INPUT",
        "network": "NETWORK",
        "gameplay": "GAMEPLAY / HUD",
        "other": "OTHER",
    }

    for cat_key in ["network", "video", "audio", "input", "gameplay", "other"]:
        cat_settings = categories.get(cat_key, {})
        if not cat_settings:
            continue
        lines.append(f"// === {category_labels.get(cat_key, cat_key.upper())} ===")
        for cvar, value in sorted(cat_settings.items()):
            lines.append(_fmt_cvar_line(cvar, value, descs))
        lines.append("")

    if cfg.binds:
        lines.append("// === BINDS ===")
        for key, cmd in sorted(cfg.binds.items()):
            lines.append(f'bind "{key}" "{cmd}"')
        lines.append("")

    if cfg.buy_binds:
        lines.append("// === BUY BINDS ===")
        for key, cmd in sorted(cfg.buy_binds.items()):
            lines.append(f'bind "{key}" "{cmd}"')
        lines.append("")

    return "\n".join(lines)


# keep backward compat
CfgConfig.to_cfg_string = lambda self, **kw: generate_single_cfg(self)


# ------------------------------------------------------------------ factories

def create_mode_config(mode_key: str) -> CfgConfig:
    modes = get_modes()
    if mode_key not in modes:
        raise ValueError(f"Unknown mode: {mode_key}")

    mode_data = modes[mode_key]
    cfg = CfgConfig()
    cfg.mode = mode_data.get("name_en", mode_key)
    cfg.mode_key = mode_key
    cfg.merge(mode_data.get("settings", {}))
    cfg.merge_binds(mode_data.get("binds", {}))
    if "buy_binds" in mode_data:
        cfg.buy_binds.update(mode_data["buy_binds"])
    return cfg


def create_preset_config(preset_key: str) -> CfgConfig:
    presets = get_presets()
    if preset_key not in presets:
        raise ValueError(f"Unknown preset: {preset_key}")

    preset_data = presets[preset_key]
    cfg = CfgConfig()
    cfg.preset_name = preset_data.get("name", preset_key)
    cfg.description = preset_data.get("description_en", "")
    cfg.merge(preset_data.get("settings", {}))
    return cfg


def create_quick_config(
    mode: str = "classic",
    sensitivity: float = 2.5,
    fps_max: int = 100,
    volume: float = 0.7,
) -> CfgConfig:
    cfg = create_mode_config(mode)
    cfg.set("sensitivity", str(sensitivity))
    cfg.set("fps_max", str(fps_max))
    cfg.set("volume", str(volume))
    return cfg


def apply_network_preset(cfg: CfgConfig, preset_key: str) -> None:
    presets = get_network_presets()
    if preset_key in presets:
        cfg.merge(presets[preset_key].get("settings", {}))
        cfg.network_preset = preset_key


def apply_visual_preset(cfg: CfgConfig, preset_key: str) -> None:
    presets = get_visual_presets()
    if preset_key in presets:
        cfg.merge(presets[preset_key].get("settings", {}))
        cfg.visual_preset = preset_key


def apply_crosshair_preset(cfg: CfgConfig, preset_key: str) -> None:
    presets = get_crosshair_presets()
    if preset_key in presets:
        cfg.merge(presets[preset_key].get("settings", {}))
        cfg.crosshair_preset = preset_key


def apply_hardware_optimization(
    cfg: CfgConfig, gpu_vendor: str, performance_profile: str
) -> list[str]:
    hw_data = get_hardware_data()
    tips: list[str] = []

    gpu_data = hw_data.get("gpu_vendor", {}).get(gpu_vendor)
    if gpu_data:
        cfg.merge(gpu_data.get("optimizations", {}))
        tips = gpu_data.get("tips_ru", gpu_data.get("tips_en", []))

    profile_data = hw_data.get("performance_profiles", {}).get(performance_profile)
    if profile_data:
        cfg.merge(profile_data.get("settings", {}))

    return tips


def compare_configs(
    user_cfg: CfgConfig, preset_key: str
) -> list[tuple[str, str, str]]:
    presets = get_presets()
    if preset_key not in presets:
        return []

    preset_settings = presets[preset_key].get("settings", {})
    diffs: list[tuple[str, str, str]] = []

    all_keys = set(user_cfg.settings.keys()) | set(preset_settings.keys())
    for key in sorted(all_keys):
        user_val = user_cfg.settings.get(key, "—")
        preset_val = preset_settings.get(key, "—")
        if user_val != preset_val:
            diffs.append((key, user_val, preset_val))

    return diffs
