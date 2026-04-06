import os
import shutil
import tempfile
from datetime import datetime

from cfg_generator.core.generator import (
    CfgConfig,
    generate_autoexec,
    generate_aliases_cfg,
    generate_buyscripts_cfg,
    generate_communication_cfg,
    generate_video_cfg,
    generate_audio_cfg,
    generate_mouse_cfg,
    generate_network_cfg,
    generate_crosshair_cfg,
    generate_hud_cfg,
    generate_bindings_cfg,
    generate_single_cfg,
)
from cfg_generator.logger import log

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output")


class ExportError(Exception):
    """Raised when export fails due to I/O or permission issues."""


def _check_writable(directory: str):
    """Verify *directory* exists and is writable. Raises ExportError if not."""
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as exc:
            raise ExportError(f"Не удалось создать папку {directory}: {exc}")
    try:
        probe = os.path.join(directory, f".write_test_{os.getpid()}.tmp")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
    except OSError as exc:
        raise ExportError(f"Папка {directory} недоступна для записи: {exc}")


def _safe_write(path: str, content: str):
    """Atomic-ish write: write to temp, then rename. Detects locked files."""
    directory = os.path.dirname(path)
    try:
        fd, tmp = tempfile.mkstemp(suffix=".cfg.tmp", dir=directory)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        if os.path.exists(path):
            try:
                os.replace(tmp, path)
            except PermissionError:
                os.remove(tmp)
                raise ExportError(
                    f"Файл {os.path.basename(path)} заблокирован другим процессом"
                )
        else:
            os.rename(tmp, path)
    except ExportError:
        raise
    except OSError as exc:
        raise ExportError(f"Ошибка записи {os.path.basename(path)}: {exc}")


def ensure_output_dir() -> str:
    _check_writable(OUTPUT_DIR)
    return OUTPUT_DIR


def export_single_cfg(cfg: CfgConfig, filename: str = "autoexec.cfg") -> str:
    """Export a single all-in-one .cfg file. Returns the full path."""
    if not filename.endswith(".cfg"):
        filename += ".cfg"

    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, filename)
    content = generate_single_cfg(cfg)
    _safe_write(path, content)
    log.info(f"Exported: {path}")
    return path


def export_full_config_set(cfg: CfgConfig) -> dict[str, str]:
    """
    Export a full modular config set matching GoldSrc Config Engineer v3.0 spec.
    Returns dict of filename -> path.

    Structure:
        cstrike/
        ├── autoexec.cfg
        └── config/
            ├── aliases.cfg
            ├── bindings.cfg
            ├── network.cfg
            ├── video.cfg
            ├── audio.cfg
            ├── mouse.cfg
            ├── crosshair.cfg
            ├── hud.cfg
            ├── buyscripts.cfg
            ├── communication.cfg
            └── modes/
                └── ...
    """
    ensure_output_dir()
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    root = os.path.join(OUTPUT_DIR, f"cstrike_{ts}")
    config_dir = os.path.join(root, "config")
    modes_dir = os.path.join(config_dir, "modes")
    os.makedirs(modes_dir, exist_ok=True)

    exported: dict[str, str] = {}

    file_generators = {
        "config/aliases.cfg":       generate_aliases_cfg,
        "config/network.cfg":       generate_network_cfg,
        "config/video.cfg":         generate_video_cfg,
        "config/audio.cfg":         generate_audio_cfg,
        "config/mouse.cfg":         generate_mouse_cfg,
        "config/crosshair.cfg":     generate_crosshair_cfg,
        "config/hud.cfg":           generate_hud_cfg,
        "config/buyscripts.cfg":    generate_buyscripts_cfg,
        "config/communication.cfg": generate_communication_cfg,
        "config/bindings.cfg":      generate_bindings_cfg,
    }

    for rel_path, gen_func in file_generators.items():
        full_path = os.path.join(root, rel_path)
        content = gen_func(cfg)
        _safe_write(full_path, content)
        exported[rel_path] = full_path

    mode_key = cfg.mode_key or "classic"
    autoexec_content = generate_autoexec(cfg, mode_key)
    autoexec_path = os.path.join(root, "autoexec.cfg")
    _safe_write(autoexec_path, autoexec_content)
    exported["autoexec.cfg"] = autoexec_path

    log.info(f"Full config set exported: {root}")
    return exported


def backup_existing(target_dir: str) -> str | None:
    """Backup existing configs before overwriting."""
    if not os.path.exists(target_dir):
        return None

    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir = os.path.join(OUTPUT_DIR, backup_name)
    shutil.copytree(target_dir, backup_dir)
    return backup_dir
