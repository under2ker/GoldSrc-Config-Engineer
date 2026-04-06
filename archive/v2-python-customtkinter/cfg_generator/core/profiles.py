"""
User profile management — save, load, switch, duplicate, delete.
Profiles stored as JSON in %APPDATA%/GoldSrcConfigEngineer/profiles/
"""

import gzip
import json
import os
import shutil
from datetime import datetime
from typing import Optional

from cfg_generator.core.generator import CfgConfig
from cfg_generator.logger import log

PROFILES_DIR = os.path.join(
    os.environ.get("APPDATA", "."), "GoldSrcConfigEngineer", "profiles"
)
HISTORY_DIR = os.path.join(
    os.environ.get("APPDATA", "."), "GoldSrcConfigEngineer", "history"
)
META_FILE = os.path.join(PROFILES_DIR, "_meta.json")
MAX_HISTORY = 20


COMPRESS_PROFILES = True


def _ensure_dirs():
    os.makedirs(PROFILES_DIR, exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)


def _write_json(path: str, data: dict, compress: bool = False):
    """Write JSON, optionally gzip-compressed (.json.gz)."""
    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    if compress:
        gz_path = path if path.endswith(".gz") else path + ".gz"
        with gzip.open(gz_path, "wb") as f:
            f.write(payload)
        if not path.endswith(".gz") and os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload.decode("utf-8"))


def _read_json(path: str) -> dict:
    """Read JSON, auto-detecting gzip compression."""
    if path.endswith(".gz") or (not os.path.isfile(path) and os.path.isfile(path + ".gz")):
        gz = path if path.endswith(".gz") else path + ".gz"
        with gzip.open(gz, "rb") as f:
            return json.loads(f.read().decode("utf-8"))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _cfg_to_dict(cfg: CfgConfig) -> dict:
    return {
        "settings": dict(cfg.settings),
        "binds": dict(cfg.binds),
        "buy_binds": dict(cfg.buy_binds),
        "aliases": list(cfg.aliases),
        "mode": cfg.mode,
        "mode_key": cfg.mode_key,
        "preset_name": cfg.preset_name,
        "description": cfg.description,
        "network_preset": cfg.network_preset,
        "visual_preset": cfg.visual_preset,
        "crosshair_preset": cfg.crosshair_preset,
        "include_practice": cfg.include_practice,
    }


_PROFILE_REQUIRED_FIELDS = {
    "settings": dict,
    "binds": dict,
    "buy_binds": dict,
    "aliases": list,
}
_PROFILE_DEFAULTS = {
    "settings": {},
    "binds": {},
    "buy_binds": {},
    "aliases": [],
    "mode": None,
    "mode_key": None,
    "preset_name": None,
    "description": "",
    "network_preset": None,
    "visual_preset": None,
    "crosshair_preset": None,
    "include_practice": False,
}

CURRENT_SCHEMA = 2


def _migrate_profile_data(data: dict) -> dict:
    """Ensure all required fields exist and have correct types."""
    config = data.get("config", {})
    for field, default in _PROFILE_DEFAULTS.items():
        if field not in config:
            config[field] = default
            log.info(f"Migration: added missing field '{field}' with default")
    for field, expected_type in _PROFILE_REQUIRED_FIELDS.items():
        if not isinstance(config.get(field), expected_type):
            config[field] = _PROFILE_DEFAULTS[field]
            log.warning(f"Migration: reset '{field}' to default (wrong type)")
    if not isinstance(config.get("aliases"), list):
        config["aliases"] = []
    data["config"] = config
    data.setdefault("schema_version", CURRENT_SCHEMA)
    return data


def _dict_to_cfg(data: dict) -> CfgConfig:
    cfg = CfgConfig()
    cfg.settings = data.get("settings") if isinstance(data.get("settings"), dict) else {}
    cfg.binds = data.get("binds") if isinstance(data.get("binds"), dict) else {}
    cfg.buy_binds = data.get("buy_binds") if isinstance(data.get("buy_binds"), dict) else {}
    cfg.aliases = data.get("aliases") if isinstance(data.get("aliases"), list) else []
    cfg.mode = data.get("mode")
    cfg.mode_key = data.get("mode_key")
    cfg.preset_name = data.get("preset_name")
    cfg.description = data.get("description", "")
    cfg.network_preset = data.get("network_preset")
    cfg.visual_preset = data.get("visual_preset")
    cfg.crosshair_preset = data.get("crosshair_preset")
    cfg.include_practice = data.get("include_practice", False)
    return cfg


# ─────────────────────────────────────────── meta (active profile tracking)

def _load_meta() -> dict:
    _ensure_dirs()
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"active": None}


def _save_meta(meta: dict):
    _ensure_dirs()
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────── profile CRUD

def list_profiles() -> list[dict]:
    """Return list of {name, filename, created_at, updated_at, mode, is_active}."""
    _ensure_dirs()
    meta = _load_meta()
    active = meta.get("active")
    profiles = []
    for fn in sorted(os.listdir(PROFILES_DIR)):
        if fn.startswith("_"):
            continue
        if not (fn.endswith(".json") or fn.endswith(".json.gz")):
            continue
        path = os.path.join(PROFILES_DIR, fn)
        try:
            data = _read_json(path)
            profiles.append({
                "name": data.get("name", fn.replace(".json.gz", "").replace(".json", "")),
                "filename": fn,
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "mode": data.get("config", {}).get("mode", "—"),
                "cvars": len(data.get("config", {}).get("settings", {})),
                "is_active": fn == active or fn + ".gz" == active or fn.replace(".gz", "") == active,
            })
        except Exception:
            continue
    return profiles


def save_profile(name: str, cfg: CfgConfig, filename: str | None = None) -> str:
    """Save CfgConfig as a named profile. Returns filename."""
    _ensure_dirs()
    if not filename:
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)
        filename = f"{safe}.json"

    path = os.path.join(PROFILES_DIR, filename)
    now = datetime.now().isoformat(timespec="seconds")

    existing = {}
    for candidate in (path, path + ".gz"):
        if os.path.exists(candidate):
            try:
                existing = _read_json(candidate)
            except Exception:
                pass
            break

    data = {
        "name": name,
        "schema_version": CURRENT_SCHEMA,
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "config": _cfg_to_dict(cfg),
    }

    try:
        _write_json(path, data, compress=COMPRESS_PROFILES)
    except PermissionError:
        raise PermissionError(f"Нет прав на запись профиля: {path}")
    except OSError as exc:
        raise OSError(f"Ошибка сохранения профиля: {exc}")

    actual_fn = filename + ".gz" if COMPRESS_PROFILES and not filename.endswith(".gz") else filename
    meta = _load_meta()
    meta["active"] = actual_fn
    _save_meta(meta)
    log.info(f"Profile saved: {name} ({actual_fn})")
    return actual_fn


def load_profile(filename: str) -> tuple[str, CfgConfig]:
    """Load profile by filename. Returns (name, CfgConfig).
    Automatically migrates old profiles to the current schema.
    Transparently reads both .json and .json.gz files."""
    path = os.path.join(PROFILES_DIR, filename)
    try:
        data = _read_json(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Профиль не найден: {filename}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Повреждённый профиль {filename}: {exc}")
    except OSError as exc:
        raise OSError(f"Ошибка чтения профиля {filename}: {exc}")

    data = _migrate_profile_data(data)

    if data.get("schema_version", 0) < CURRENT_SCHEMA:
        data["schema_version"] = CURRENT_SCHEMA
        try:
            _write_json(path, data, compress=COMPRESS_PROFILES)
            log.info(f"Profile migrated to schema v{CURRENT_SCHEMA}: {filename}")
        except OSError:
            pass

    meta = _load_meta()
    meta["active"] = filename
    _save_meta(meta)
    log.info(f"Profile loaded: {data.get('name', filename)}")
    return data.get("name", filename), _dict_to_cfg(data.get("config", {}))


def delete_profile(filename: str) -> bool:
    path = os.path.join(PROFILES_DIR, filename)
    for candidate in (path, path + ".gz", path.replace(".gz", "")):
        if os.path.exists(candidate):
            os.remove(candidate)
            meta = _load_meta()
            if meta.get("active") in (filename, filename + ".gz", filename.replace(".gz", "")):
                meta["active"] = None
                _save_meta(meta)
            log.info(f"Profile deleted: {filename}")
            return True
    return False


def rename_profile(filename: str, new_name: str) -> str:
    """Rename profile display name (keeps filename). Returns filename."""
    path = os.path.join(PROFILES_DIR, filename)
    data = _read_json(path)
    data["name"] = new_name
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _write_json(path, data, compress=COMPRESS_PROFILES)
    log.info(f"Profile renamed: {filename} -> {new_name}")
    return filename


def duplicate_profile(filename: str, new_name: str) -> str:
    """Clone a profile with a new name. Returns new filename."""
    path = os.path.join(PROFILES_DIR, filename)
    data = _read_json(path)

    data["name"] = new_name
    now = datetime.now().isoformat(timespec="seconds")
    data["created_at"] = now
    data["updated_at"] = now

    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in new_name)
    ext = ".json.gz" if COMPRESS_PROFILES else ".json"
    new_fn = f"{safe}{ext}"
    new_path = os.path.join(PROFILES_DIR, new_fn)
    _write_json(new_path, data, compress=COMPRESS_PROFILES)

    log.info(f"Profile duplicated: {filename} -> {new_fn}")
    return new_fn


def get_active_profile() -> Optional[str]:
    meta = _load_meta()
    return meta.get("active")


# ─────────────────────────────────────────── config history

def save_history_snapshot(cfg: CfgConfig, label: str = "") -> str:
    """Save a timestamped snapshot of the config. Returns snapshot filename."""
    _ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_label = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in label) if label else "snapshot"
    fn = f"{ts}_{safe_label}.json"
    path = os.path.join(HISTORY_DIR, fn)

    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "label": label or (cfg.mode or cfg.preset_name or "custom"),
        "config": _cfg_to_dict(cfg),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    _trim_history()
    log.info(f"History snapshot saved: {fn}")
    return fn


def list_history() -> list[dict]:
    """Return list of history entries sorted newest first."""
    _ensure_dirs()
    entries = []
    for fn in os.listdir(HISTORY_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(HISTORY_DIR, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries.append({
                "filename": fn,
                "timestamp": data.get("timestamp", ""),
                "label": data.get("label", ""),
                "cvars": len(data.get("config", {}).get("settings", {})),
            })
        except Exception:
            continue
    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries


def load_history_snapshot(filename: str) -> tuple[str, CfgConfig]:
    """Load a history snapshot. Returns (label, CfgConfig)."""
    path = os.path.join(HISTORY_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    log.info(f"History snapshot loaded: {filename}")
    return data.get("label", "snapshot"), _dict_to_cfg(data.get("config", {}))


MAX_HISTORY_SIZE_MB = 50


def _trim_history():
    """Keep only the newest MAX_HISTORY snapshots and enforce size cap."""
    entries = list_history()
    if len(entries) <= MAX_HISTORY:
        _trim_history_by_size()
        return
    for entry in entries[MAX_HISTORY:]:
        path = os.path.join(HISTORY_DIR, entry["filename"])
        try:
            os.remove(path)
            log.debug(f"History trimmed (count): {entry['filename']}")
        except Exception:
            pass
    _trim_history_by_size()


def _trim_history_by_size():
    """Remove oldest snapshots until history dir is under MAX_HISTORY_SIZE_MB."""
    _ensure_dirs()
    files = []
    total = 0
    for fn in os.listdir(HISTORY_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(HISTORY_DIR, fn)
        try:
            sz = os.path.getsize(path)
            files.append((fn, sz, os.path.getmtime(path)))
            total += sz
        except OSError:
            continue
    limit = MAX_HISTORY_SIZE_MB * 1024 * 1024
    if total <= limit:
        return
    files.sort(key=lambda x: x[2])
    for fn, sz, _ in files:
        if total <= limit:
            break
        path = os.path.join(HISTORY_DIR, fn)
        try:
            os.remove(path)
            total -= sz
            log.info(f"History trimmed (size): {fn}")
        except OSError:
            pass


# ─────────────────────────────────────────── autosave & crash recovery

AUTOSAVE_FILE = os.path.join(
    os.environ.get("APPDATA", "."), "GoldSrcConfigEngineer", "~autosave.json"
)
AUTOSAVE_INTERVAL = 60


def autosave(cfg: CfgConfig | None):
    """Save current config state to a temporary autosave file."""
    if cfg is None:
        return
    _ensure_dirs()
    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema_version": CURRENT_SCHEMA,
        "config": _cfg_to_dict(cfg),
    }
    try:
        with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def has_autosave() -> bool:
    """Check if an autosave file exists."""
    return os.path.isfile(AUTOSAVE_FILE)


def load_autosave() -> CfgConfig | None:
    """Load autosaved config. Returns None if not available or corrupted."""
    if not os.path.isfile(AUTOSAVE_FILE):
        return None
    try:
        with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        log.info("Autosave recovered")
        return _dict_to_cfg(data.get("config", {}))
    except Exception as exc:
        log.warning(f"Failed to load autosave: {exc}")
        return None


def clear_autosave():
    """Remove the autosave file (called after successful manual save)."""
    try:
        if os.path.isfile(AUTOSAVE_FILE):
            os.remove(AUTOSAVE_FILE)
    except OSError:
        pass
