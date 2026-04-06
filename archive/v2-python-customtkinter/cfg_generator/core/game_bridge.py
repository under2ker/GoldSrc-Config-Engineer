"""
Game Bridge — detect CS 1.6, deploy configs, send exec to running game.

How it works:
  1. Find CS 1.6 installation via Steam libraryfolders.vdf / registry / common paths
  2. Copy .cfg files into cstrike/ directory
  3. If game is running — simulate keystrokes to open console and exec the config
"""

import os
import shutil
import struct
import subprocess
import sys
import time
from typing import Optional

from cfg_generator.logger import log

_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    import ctypes
    import ctypes.wintypes

# ─────────────────────────────────────────── Windows API constants
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
VK_OEM_3 = 0xC0          # ` / ~ (console toggle)
VK_RETURN = 0x0D
SW_RESTORE = 9

if _IS_WINDOWS:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
else:
    user32 = None
    kernel32 = None

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

if _IS_WINDOWS:
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.wintypes.WORD),
            ("wScan", ctypes.wintypes.WORD),
            ("dwFlags", ctypes.wintypes.DWORD),
            ("time", ctypes.wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT(ctypes.Structure):
        class _INPUT_UNION(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]

        _fields_ = [
            ("type", ctypes.wintypes.DWORD),
            ("union", _INPUT_UNION),
        ]
else:
    KEYBDINPUT = None
    INPUT = None


# ─────────────────────────────────────────── game path detection

COMMON_STEAM_PATHS = [
    r"C:\Program Files (x86)\Steam",
    r"C:\Program Files\Steam",
    r"D:\Steam",
    r"D:\SteamLibrary",
    r"E:\Steam",
    r"E:\SteamLibrary",
    r"C:\Games\Steam",
    r"D:\Games\Steam",
]

COMMON_NOSTEAM_PATHS = [
    r"C:\Games\Counter-Strike 1.6",
    r"C:\CS 1.6",
    r"D:\Games\Counter-Strike 1.6",
    r"D:\CS",
    r"C:\Counter-Strike",
    r"D:\Counter-Strike",
    r"C:\Program Files (x86)\Counter-Strike 1.6",
]

HL_EXE_NAME = "hl.exe"
CSTRIKE_DIR = "cstrike"


def _require_windows(feature: str = "Game Bridge"):
    if not _IS_WINDOWS:
        raise RuntimeError(f"{feature} поддерживается только на Windows")


def find_steam_path() -> Optional[str]:
    """Find Steam installation via registry."""
    if not _IS_WINDOWS:
        return None
    try:
        import winreg
        for root_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for sub in (r"SOFTWARE\Valve\Steam", r"SOFTWARE\WOW6432Node\Valve\Steam"):
                try:
                    key = winreg.OpenKey(root_key, sub)
                    val, _ = winreg.QueryValueEx(key, "InstallPath")
                    winreg.CloseKey(key)
                    if os.path.isdir(val):
                        return val
                except Exception:
                    continue
    except Exception:
        pass
    for p in COMMON_STEAM_PATHS:
        if os.path.isdir(p):
            return p
    return None


def _parse_library_folders(steam_path: str) -> list[str]:
    """Parse libraryfolders.vdf for additional Steam library locations."""
    vdf = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if not os.path.isfile(vdf):
        vdf = os.path.join(steam_path, "config", "libraryfolders.vdf")
    if not os.path.isfile(vdf):
        return [steam_path]

    libs = [steam_path]
    try:
        with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip().strip('"')
                if os.sep in line or "/" in line:
                    candidate = line.replace("\\\\", "\\")
                    if os.path.isdir(candidate):
                        libs.append(candidate)
    except Exception:
        pass
    return libs


def find_game_path() -> Optional[str]:
    """Auto-detect CS 1.6 installation directory (containing hl.exe + cstrike/)."""
    steam = find_steam_path()
    candidates = []
    if steam:
        for lib in _parse_library_folders(steam):
            cs_dir = os.path.join(lib, "steamapps", "common", "Half-Life")
            candidates.append(cs_dir)

    candidates.extend(COMMON_NOSTEAM_PATHS)

    for d in candidates:
        hl = os.path.join(d, HL_EXE_NAME)
        cs = os.path.join(d, CSTRIKE_DIR)
        if os.path.isfile(hl) and os.path.isdir(cs):
            log.info(f"CS 1.6 found: {d}")
            return d

    return None


def get_cstrike_path(game_path: str) -> str:
    return os.path.join(game_path, CSTRIKE_DIR)


# ─────────────────────────────────────────── process detection

def is_game_running() -> bool:
    """Check if hl.exe is currently running."""
    if not _IS_WINDOWS:
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {HL_EXE_NAME}", "/NH"],
            capture_output=True, text=True, creationflags=0x08000000,
        )
        return HL_EXE_NAME.lower() in result.stdout.lower()
    except Exception:
        return False


def get_hl_window() -> Optional[int]:
    """Find the Half-Life / Counter-Strike window handle."""
    if not _IS_WINDOWS:
        return None
    titles = ["Half-Life", "Counter-Strike", "Counter-Strike 1.6"]
    for title in titles:
        hwnd = user32.FindWindowW(None, title)
        if hwnd:
            return hwnd
    hwnd = user32.FindWindowW("Valve001", None)
    if hwnd:
        return hwnd
    return None


# ─────────────────────────────────────────── deploy config

def deploy_config_files(game_path: str, cfg_content: str,
                        modular_files: dict[str, str] | None = None) -> list[str]:
    """
    Deploy config files to CS 1.6 cstrike/ directory.
    Returns list of written file paths.
    """
    cs = get_cstrike_path(game_path)
    written = []

    autoexec_path = os.path.join(cs, "autoexec.cfg")
    with open(autoexec_path, "w", encoding="utf-8") as f:
        f.write(cfg_content)
    written.append(autoexec_path)

    if modular_files:
        config_dir = os.path.join(cs, "config")
        os.makedirs(config_dir, exist_ok=True)
        for rel_name, content in modular_files.items():
            full = os.path.join(cs, rel_name)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            written.append(full)

    log.info(f"Deployed {len(written)} files to {cs}")
    return written


def deploy_userconfig(game_path: str, cfg_content: str) -> str:
    """Write to userconfig.cfg — auto-executed on map change / connect."""
    cs = get_cstrike_path(game_path)
    path = os.path.join(cs, "userconfig.cfg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"// Auto-deployed by GoldSrc Config Engineer\n")
        f.write(cfg_content)
    log.info(f"Deployed userconfig.cfg to {cs}")
    return path


# ─────────────────────────────────────────── send exec to running game

def _send_key(vk: int, scan: int = 0):
    """Send a single key press + release via SendInput."""
    _require_windows("SendInput")
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = scan
    inp.union.ki.dwFlags = 0
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    time.sleep(0.02)

    inp.union.ki.dwFlags = KEYEVENTF_KEYUP
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    time.sleep(0.02)


def _send_char(char: str):
    """Send a single character via WM_CHAR to the foreground window."""
    hwnd = user32.GetForegroundWindow()
    user32.PostMessageW(hwnd, WM_CHAR, ord(char), 0)
    time.sleep(0.01)


def _type_string(text: str):
    """Type a string character by character."""
    for ch in text:
        _send_char(ch)
    time.sleep(0.05)


def exec_in_game(command: str = "exec autoexec.cfg") -> bool:
    """
    Send an exec command to a running CS 1.6 instance.

    Steps:
      1. Find the HL window
      2. Bring it to foreground
      3. Press ` to open console
      4. Type the command
      5. Press Enter
      6. Press ` to close console

    Returns True if the command was sent successfully.
    """
    hwnd = get_hl_window()
    if not hwnd:
        log.warning("exec_in_game: HL window not found")
        return False

    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
            time.sleep(0.2)

        user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        _send_key(VK_OEM_3)
        time.sleep(0.3)

        _type_string(command)
        time.sleep(0.1)

        _send_key(VK_RETURN)
        time.sleep(0.2)

        _send_key(VK_OEM_3)
        time.sleep(0.1)

        log.info(f"Sent to game console: {command}")
        return True

    except Exception as e:
        log.error(f"exec_in_game failed: {e}")
        return False


# ─────────────────────────────────────────── client cleanup

CLEAN_CATEGORIES: dict[str, dict] = {
    "configs": {
        "label": "Конфиги (config.cfg, userconfig.cfg, violence.cfg и др.)",
        "description": "Сбрасывает грязные конфиги, которые накопили мусорные команды",
        "files": [
            "config.cfg", "userconfig.cfg", "violence.cfg",
            "game.cfg", "listenserver.cfg", "server.cfg",
            "skill.cfg", "banned.cfg", "language.cfg",
        ],
        "default": True,
    },
    "custom_cfgs": {
        "label": "Пользовательские .cfg файлы",
        "description": "Удаляет все .cfg кроме системных (autoexec, config, valve)",
        "glob": "*.cfg",
        "keep": {"autoexec.cfg", "config.cfg", "game.cfg", "violence.cfg",
                 "listenserver.cfg", "server.cfg", "skill.cfg", "language.cfg"},
        "default": False,
    },
    "downloads": {
        "label": "Загруженный контент с серверов",
        "description": "Модели, звуки, спрайты, карты — скачанные с игровых серверов",
        "dirs": ["downloads", "download"],
        "default": True,
    },
    "custom_models": {
        "label": "Пользовательские модели и скины",
        "description": "Кастомные модели игроков и оружия в models/player/ и models/",
        "dirs_content": ["models/player"],
        "default": False,
    },
    "custom_sounds": {
        "label": "Пользовательские звуки",
        "description": "Звуковые файлы, не входящие в стандартную игру",
        "dirs_content": ["sound"],
        "default": False,
    },
    "custom_sprites": {
        "label": "Пользовательские спрайты",
        "description": "Кастомные спрайты HUD / прицелов / эффектов",
        "dirs_content": ["sprites"],
        "default": False,
    },
    "demos": {
        "label": "Демо-записи (.dem)",
        "description": "Записанные демки матчей",
        "glob": "*.dem",
        "default": False,
    },
    "screenshots": {
        "label": "Скриншоты",
        "description": "Сделанные в игре скриншоты",
        "glob": "*.bmp",
        "dirs": ["screenshots"],
        "default": False,
    },
    "logos": {
        "label": "Логотипы / спреи",
        "description": "Пользовательские граффити-спреи",
        "dirs": ["logos", "tempdecal.wad"],
        "default": False,
    },
    "logs": {
        "label": "Логи и консоль",
        "description": "qconsole.log, condebug и прочие логи",
        "files_root": ["qconsole.log"],
        "files": ["condebug.log", "voice_ban.dt", "voice_decompressed.wav"],
        "default": True,
    },
    "temp": {
        "label": "Временные / кэш файлы",
        "description": "Временные файлы движка и кэш",
        "files_root": ["custom.hpk"],
        "dirs_root": ["SAVE"],
        "default": True,
    },
    "registry": {
        "label": "Реестр (настройки видео/звука Half-Life)",
        "description": "Сброс ключей HKCU\\Software\\Valve\\Half-Life\\Settings",
        "registry_key": r"Software\Valve\Half-Life\Settings",
        "default": False,
    },
}


def _size_fmt(size: int) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ТБ"


def _dir_size(path: str) -> int:
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def scan_cleanup(game_path: str, categories: list[str]) -> dict[str, dict]:
    """
    Scan what will be cleaned. Returns dict:
      category_key -> { "files": [paths], "dirs": [paths], "size": int, "count": int }
    """
    cs = get_cstrike_path(game_path)
    root = game_path
    result = {}

    for cat_key in categories:
        cat = CLEAN_CATEGORIES.get(cat_key)
        if not cat:
            continue

        found_files: list[str] = []
        found_dirs: list[str] = []
        total_size = 0

        # individual files in cstrike/
        for fn in cat.get("files", []):
            fp = os.path.join(cs, fn)
            if os.path.isfile(fp):
                found_files.append(fp)
                total_size += os.path.getsize(fp)

        # individual files in game root
        for fn in cat.get("files_root", []):
            fp = os.path.join(root, fn)
            if os.path.isfile(fp):
                found_files.append(fp)
                total_size += os.path.getsize(fp)

        # directories in cstrike/ (remove whole dir)
        for dn in cat.get("dirs", []):
            dp = os.path.join(cs, dn)
            if os.path.isdir(dp):
                found_dirs.append(dp)
                total_size += _dir_size(dp)
            elif os.path.isfile(dp):
                found_files.append(dp)
                total_size += os.path.getsize(dp)

        # directories in game root
        for dn in cat.get("dirs_root", []):
            dp = os.path.join(root, dn)
            if os.path.isdir(dp):
                found_dirs.append(dp)
                total_size += _dir_size(dp)

        # content inside dirs (don't remove dir itself, just contents)
        for dn in cat.get("dirs_content", []):
            dp = os.path.join(cs, dn)
            if os.path.isdir(dp):
                for entry in os.listdir(dp):
                    ep = os.path.join(dp, entry)
                    if os.path.isfile(ep):
                        found_files.append(ep)
                        total_size += os.path.getsize(ep)
                    elif os.path.isdir(ep):
                        found_dirs.append(ep)
                        total_size += _dir_size(ep)

        # glob pattern in cstrike/
        if "glob" in cat:
            import glob as _glob
            keep = cat.get("keep", set())
            for fp in _glob.glob(os.path.join(cs, cat["glob"])):
                if os.path.basename(fp).lower() not in {k.lower() for k in keep}:
                    if fp not in found_files:
                        found_files.append(fp)
                        total_size += os.path.getsize(fp)

        count = len(found_files) + len(found_dirs)
        result[cat_key] = {
            "files": found_files,
            "dirs": found_dirs,
            "size": total_size,
            "count": count,
        }

    return result


def execute_cleanup(game_path: str, scan_result: dict[str, dict],
                    backup: bool = True) -> tuple[int, int, list[str]]:
    """
    Execute the cleanup based on scan results.
    Returns (files_removed, bytes_freed, errors).
    """
    cs = get_cstrike_path(game_path)
    files_removed = 0
    bytes_freed = 0
    errors: list[str] = []

    if backup:
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(cs, "config_backups", f"cleanup_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
    else:
        backup_dir = None

    for cat_key, data in scan_result.items():
        cat = CLEAN_CATEGORIES.get(cat_key, {})

        # handle registry
        if cat.get("registry_key"):
            try:
                import winreg
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, cat["registry_key"])
                log.info(f"Registry key deleted: {cat['registry_key']}")
            except FileNotFoundError:
                pass
            except Exception as e:
                errors.append(f"Реестр: {e}")
            continue

        for fp in data["files"]:
            try:
                sz = os.path.getsize(fp)
                if backup_dir and fp.endswith(".cfg"):
                    dst = os.path.join(backup_dir, os.path.basename(fp))
                    shutil.copy2(fp, dst)
                os.remove(fp)
                files_removed += 1
                bytes_freed += sz
            except Exception as e:
                errors.append(f"{os.path.basename(fp)}: {e}")

        for dp in data["dirs"]:
            try:
                sz = _dir_size(dp)
                shutil.rmtree(dp, ignore_errors=True)
                files_removed += 1
                bytes_freed += sz
            except Exception as e:
                errors.append(f"{os.path.basename(dp)}/: {e}")

    log.info(f"Cleanup done: {files_removed} items, {_size_fmt(bytes_freed)} freed")
    return files_removed, bytes_freed, errors


def deploy_and_exec(game_path: str, cfg_content: str,
                    modular_files: dict[str, str] | None = None) -> tuple[bool, str]:
    """
    Full pipeline: deploy config files + exec in running game.
    Returns (success, message).
    """
    try:
        written = deploy_config_files(game_path, cfg_content, modular_files)
    except Exception as e:
        return False, f"Ошибка записи файлов: {e}"

    msg = f"Записано {len(written)} файлов в {get_cstrike_path(game_path)}"

    if is_game_running():
        ok = exec_in_game("exec autoexec.cfg")
        if ok:
            msg += "\n✅ Команда exec отправлена в игру"
        else:
            msg += "\n⚠️ Не удалось отправить exec (откройте консоль вручную)"
    else:
        msg += "\n💡 CS 1.6 не запущена — конфиг применится при следующем запуске"

    return True, msg
