"""
Centralized image cache — avoids loading the same icon multiple times.
Usage:
    from cfg_generator.components.image_cache import get_icon
    icon = get_icon("export", size=(20, 20))
"""

import os
from typing import Optional

_cache: dict[str, object] = {}

ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")


def get_icon(name: str, size: tuple[int, int] = (20, 20),
             light_path: Optional[str] = None,
             dark_path: Optional[str] = None) -> object:
    """Return a CTkImage for the given icon name, creating and caching if needed.
    Falls back to None if the icon file doesn't exist or customtkinter is unavailable."""
    key = f"{name}_{size[0]}x{size[1]}"
    if key in _cache:
        return _cache[key]

    try:
        import customtkinter as ctk
        from PIL import Image
    except ImportError:
        return None

    if not light_path:
        light_path = os.path.join(ICONS_DIR, f"{name}.png")
    if not dark_path:
        dark_path = os.path.join(ICONS_DIR, f"{name}_dark.png")
        if not os.path.isfile(dark_path):
            dark_path = light_path

    if not os.path.isfile(light_path):
        _cache[key] = None
        return None

    try:
        light_img = Image.open(light_path).resize(size, Image.LANCZOS)
        dark_img = Image.open(dark_path).resize(size, Image.LANCZOS) if dark_path != light_path else light_img
        icon = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=size)
        _cache[key] = icon
        return icon
    except Exception:
        _cache[key] = None
        return None


def clear_cache():
    """Clear the icon cache to free memory."""
    _cache.clear()


def cache_stats() -> dict:
    """Return cache statistics for debug overlay."""
    total = len(_cache)
    loaded = sum(1 for v in _cache.values() if v is not None)
    return {"total_keys": total, "loaded_icons": loaded}
