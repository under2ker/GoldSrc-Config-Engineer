import json
import os
from typing import Optional

_current_lang = "ru"
_strings: dict = {}
_i18n_dir = os.path.dirname(os.path.abspath(__file__))


def load_language(lang: str = "ru") -> None:
    global _current_lang, _strings
    _current_lang = lang
    path = os.path.join(_i18n_dir, f"{lang}.json")
    with open(path, "r", encoding="utf-8") as f:
        _strings = json.load(f)


def t(key: str, **kwargs) -> str:
    """Translate a key, with optional format params."""
    parts = key.split(".")
    val = _strings
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p, key)
        else:
            return key
    if isinstance(val, str) and kwargs:
        return val.format(**kwargs)
    return val if isinstance(val, str) else key


def get_lang() -> str:
    return _current_lang
