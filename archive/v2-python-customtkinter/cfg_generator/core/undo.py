"""
Undo/Redo system using the Command pattern.
Tracks config changes and allows Ctrl+Z / Ctrl+Y rollbacks.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cfg_generator.core.generator import CfgConfig


@dataclass
class ConfigChange:
    """Single reversible change to a CfgConfig."""
    kind: str
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    description: str = ""


class UndoManager:
    """Manages undo/redo stacks for config changes."""

    def __init__(self, max_size: int = 50):
        self._max = max_size
        self._undo: list[ConfigChange] = []
        self._redo: list[ConfigChange] = []
        self._cfg: Optional[CfgConfig] = None

    def bind_config(self, cfg: CfgConfig):
        self._cfg = cfg

    @property
    def can_undo(self) -> bool:
        return len(self._undo) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo) > 0

    @property
    def undo_count(self) -> int:
        return len(self._undo)

    @property
    def undo_description(self) -> str:
        if self._undo:
            c = self._undo[-1]
            return c.description or f"{c.key}: {c.old_value} → {c.new_value}"
        return ""

    @property
    def redo_description(self) -> str:
        if self._redo:
            c = self._redo[-1]
            return c.description or f"{c.key}: {c.old_value} → {c.new_value}"
        return ""

    def record_set(self, key: str, old_value: Optional[str], new_value: str):
        change = ConfigChange("set", key, old_value, new_value,
                              f"{key}: {old_value or '—'} → {new_value}")
        self._push(change)

    def record_bind(self, key: str, old_cmd: Optional[str], new_cmd: str):
        change = ConfigChange("bind", key, old_cmd, new_cmd,
                              f"bind {key}: {old_cmd or '—'} → {new_cmd}")
        self._push(change)

    def record_remove(self, key: str, old_value: str):
        change = ConfigChange("remove", key, old_value, None,
                              f"Удалён: {key} = {old_value}")
        self._push(change)

    def _push(self, change: ConfigChange):
        self._undo.append(change)
        if len(self._undo) > self._max:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self) -> Optional[ConfigChange]:
        if not self._undo or not self._cfg:
            return None
        change = self._undo.pop()
        self._apply_reverse(change)
        self._redo.append(change)
        return change

    def redo(self) -> Optional[ConfigChange]:
        if not self._redo or not self._cfg:
            return None
        change = self._redo.pop()
        self._apply_forward(change)
        self._undo.append(change)
        return change

    def _apply_reverse(self, c: ConfigChange):
        cfg = self._cfg
        if c.kind == "set":
            if c.old_value is not None:
                cfg.settings[c.key] = c.old_value
            else:
                cfg.settings.pop(c.key, None)
        elif c.kind == "bind":
            if c.old_value is not None:
                cfg.binds[c.key] = c.old_value
            else:
                cfg.binds.pop(c.key, None)
        elif c.kind == "remove":
            if c.old_value is not None:
                cfg.settings[c.key] = c.old_value

    def _apply_forward(self, c: ConfigChange):
        cfg = self._cfg
        if c.kind == "set":
            if c.new_value is not None:
                cfg.settings[c.key] = c.new_value
            else:
                cfg.settings.pop(c.key, None)
        elif c.kind == "bind":
            if c.new_value is not None:
                cfg.binds[c.key] = c.new_value
            else:
                cfg.binds.pop(c.key, None)
        elif c.kind == "remove":
            cfg.settings.pop(c.key, None)

    def clear(self):
        self._undo.clear()
        self._redo.clear()
