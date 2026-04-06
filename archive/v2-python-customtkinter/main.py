#!/usr/bin/env python3
"""
CS 1.6 Deep CFG Generator — AI-powered professional config generator.

Usage:
    python main.py              GUI mode (default)
    python main.py --cli        Interactive CLI mode
    python main.py --quick      Quick config generation (CLI)
    python main.py --mode kz    Generate config for specific mode (CLI)
    python main.py --preset fnatic_f0rest   Load pro-player preset (CLI)
    python main.py --lang en    Set language (ru/en)
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cfg_generator.core.generator import (
    create_mode_config,
    create_preset_config,
    create_quick_config,
    get_modes,
    get_presets,
)
from cfg_generator.io.exporter import export_single_cfg


def parse_args():
    parser = argparse.ArgumentParser(
        description="CS 1.6 Deep CFG Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode instead of GUI",
    )
    parser.add_argument(
        "--lang",
        choices=["ru", "en"],
        default="ru",
        help="Interface language (default: ru)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick generation with defaults (implies --cli)",
    )
    parser.add_argument(
        "--mode",
        choices=list(get_modes().keys()),
        help="Game mode — implies CLI output",
    )
    parser.add_argument(
        "--preset",
        choices=list(get_presets().keys()),
        help="Pro-player preset key — implies CLI output",
    )
    parser.add_argument(
        "--sensitivity",
        type=float,
        default=None,
        help="Mouse sensitivity (overrides mode default)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=None,
        help="fps_max value (overrides mode default)",
    )
    parser.add_argument(
        "--output",
        default="autoexec.cfg",
        help="Output filename (default: autoexec.cfg)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    cli_mode = args.cli or args.quick or args.mode or args.preset

    if cli_mode:
        from cfg_generator.i18n import load_language
        from rich.console import Console

        console = Console()
        load_language(args.lang)

        if args.preset:
            cfg = create_preset_config(args.preset)
            if args.sensitivity is not None:
                cfg.set("sensitivity", str(args.sensitivity))
            if args.fps is not None:
                cfg.set("fps_max", str(args.fps))
            console.print(f"[green]Preset loaded: {args.preset}[/green]")
        elif args.mode:
            cfg = create_mode_config(args.mode)
            if args.sensitivity is not None:
                cfg.set("sensitivity", str(args.sensitivity))
            if args.fps is not None:
                cfg.set("fps_max", str(args.fps))
            console.print(f"[green]Mode: {args.mode}[/green]")
        else:
            cfg = create_quick_config(
                sensitivity=args.sensitivity or 2.5,
                fps_max=args.fps or 100,
            )
            console.print("[green]Quick config generated[/green]")

        path = export_single_cfg(cfg, args.output)
        console.print(f"[green]Saved to: {path}[/green]")
        console.print(f"[dim]Settings: {len(cfg.settings)}[/dim]")

        console.print("\n[bold]Preview:[/bold]")
        for line in cfg.to_cfg_string().splitlines()[:15]:
            console.print(f"  [dim]{line}[/dim]")
    else:
        from cfg_generator.gui import run
        run()


if __name__ == "__main__":
    main()
