#!/usr/bin/env python3
"""
Build script for GoldSrc Config Engineer — creates a standalone .exe
using PyInstaller.

Usage:
    python build.py            Build one-file windowed exe
    python build.py --onedir   Build one-dir distribution (faster startup)
    python build.py --console  Include console window for debugging
"""

import argparse
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def build(onedir: bool = False, console: bool = False):
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name", "GoldSrcConfigEngineer",
    ]

    if onedir:
        cmd.append("--onedir")
    else:
        cmd.append("--onefile")

    if not console:
        cmd.append("--windowed")

    icon_path = os.path.join(ROOT, "assets", "icon.ico")
    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    data_dirs = [
        ("cfg_generator/data", "cfg_generator/data"),
        ("cfg_generator/i18n", "cfg_generator/i18n"),
    ]
    for src, dst in data_dirs:
        full_src = os.path.join(ROOT, src)
        if os.path.exists(full_src):
            cmd.extend(["--add-data", f"{full_src}{os.pathsep}{dst}"])

    assets_dir = os.path.join(ROOT, "assets")
    if os.path.exists(assets_dir):
        cmd.extend(["--add-data", f"{assets_dir}{os.pathsep}assets"])

    hidden = [
        "customtkinter",
        "cfg_generator",
        "cfg_generator.core",
        "cfg_generator.core.generator",
        "cfg_generator.core.validator",
        "cfg_generator.core.optimizer",
        "cfg_generator.core.profiles",
        "cfg_generator.core.diagnostics",
        "cfg_generator.io",
        "cfg_generator.io.exporter",
        "cfg_generator.io.importer",
        "cfg_generator.gui",
        "cfg_generator.theme",
        "cfg_generator.logger",
    ]
    for mod in hidden:
        cmd.extend(["--hidden-import", mod])

    excludes = [
        "matplotlib", "scipy", "numpy", "pandas",
        "unittest", "test", "xmlrpc", "lib2to3",
        "pydoc", "doctest", "pdb", "profile",
        "distutils", "setuptools", "pip",
    ]
    for mod in excludes:
        cmd.extend(["--exclude-module", mod])

    cmd.append(os.path.join(ROOT, "main.py"))

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        out = "dist/GoldSrcConfigEngineer" + (".exe" if not onedir else "")
        print(f"\nBuild successful! Output: {out}")
    else:
        print(f"\nBuild failed with code {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build GoldSrc Config Engineer .exe")
    parser.add_argument("--onedir", action="store_true",
                        help="Build as one-directory instead of one-file")
    parser.add_argument("--console", action="store_true",
                        help="Include console window for debugging")
    args = parser.parse_args()
    sys.exit(build(args.onedir, args.console))
