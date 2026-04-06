import os
import re
import requests
from typing import Optional
from cfg_generator.core.generator import CfgConfig
from cfg_generator.core.validator import validate_cfg_text, check_dangerous

CVAR_PATTERN = re.compile(r'^(\S+)\s+"([^"]*)"')
BIND_PATTERN = re.compile(r'^bind\s+"([^"]+)"\s+"([^"]+)"', re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"^\s*//")


def parse_cfg_text(text: str) -> CfgConfig:
    """Parse raw .cfg text into a CfgConfig object."""
    cfg = CfgConfig()

    for line in text.splitlines():
        line = line.strip()
        if not line or COMMENT_PATTERN.match(line):
            continue

        bind_match = BIND_PATTERN.match(line)
        if bind_match:
            key = bind_match.group(1)
            cmd = bind_match.group(2)
            cfg.binds[key] = cmd
            continue

        cvar_match = CVAR_PATTERN.match(line)
        if cvar_match:
            cvar_name = cvar_match.group(1)
            cvar_value = cvar_match.group(2)
            if cvar_name.lower() != "bind":
                cfg.settings[cvar_name] = cvar_value
            continue

    return cfg


def import_from_file(filepath: str) -> tuple[CfgConfig, str]:
    """
    Import from a local .cfg file.
    Returns (config, validation_summary).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    dangers = check_dangerous(text)
    if dangers:
        danger_text = "\n".join(dangers)
        raise SecurityError(
            f"Dangerous commands detected:\n{danger_text}"
        )

    cfg = parse_cfg_text(text)
    result = validate_cfg_text(text)

    summary = (
        f"Commands: {result.total_count}, "
        f"Valid: {result.valid_count}, "
        f"Warnings: {len(result.warnings)}, "
        f"Errors: {len(result.errors)}"
    )

    return cfg, summary


def import_from_url(url: str, timeout: int = 15) -> tuple[CfgConfig, str]:
    """
    Download and import a .cfg from URL.
    Returns (config, validation_summary).
    """
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to download: {e}")

    text = resp.text

    dangers = check_dangerous(text)
    if dangers:
        danger_text = "\n".join(dangers)
        raise SecurityError(
            f"Dangerous commands detected:\n{danger_text}"
        )

    cfg = parse_cfg_text(text)
    result = validate_cfg_text(text)

    summary = (
        f"Commands: {result.total_count}, "
        f"Valid: {result.valid_count}, "
        f"Warnings: {len(result.warnings)}, "
        f"Errors: {len(result.errors)}"
    )

    return cfg, summary


class SecurityError(Exception):
    """Raised when dangerous commands are detected in imported configs."""
    pass
