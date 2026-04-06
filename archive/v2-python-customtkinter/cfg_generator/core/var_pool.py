"""
tkinter Variable pool — reuse StringVar / IntVar / DoubleVar / BooleanVar
instances across page rebuilds instead of creating new ones each time.
"""

import tkinter as tk
from typing import Any, TypeVar

T = TypeVar("T", tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)

_pools: dict[type, list] = {
    tk.StringVar: [],
    tk.IntVar: [],
    tk.DoubleVar: [],
    tk.BooleanVar: [],
}

_active: dict[str, tk.Variable] = {}


def acquire(var_type: type[T], key: str, default: Any = None, master: tk.Misc | None = None) -> T:
    """Get or create a tkinter Variable from the pool, keyed by name.
    If a variable with this key already exists and has the same type, reuse it."""
    if key in _active:
        existing = _active[key]
        if isinstance(existing, var_type):
            if default is not None:
                existing.set(default)
            return existing

    pool = _pools.get(var_type, [])
    if pool:
        var = pool.pop()
        if default is not None:
            var.set(default)
    else:
        var = var_type(master=master, value=default if default is not None else "")

    _active[key] = var
    return var


def release(key: str):
    """Return a variable to the pool for reuse."""
    if key not in _active:
        return
    var = _active.pop(key)
    var_type = type(var)
    pool = _pools.get(var_type)
    if pool is not None and len(pool) < 100:
        pool.append(var)


def release_prefix(prefix: str):
    """Release all variables whose keys start with the given prefix."""
    keys = [k for k in _active if k.startswith(prefix)]
    for k in keys:
        release(k)


def get(key: str) -> tk.Variable | None:
    """Get a variable by key without creating it."""
    return _active.get(key)


def pool_stats() -> dict:
    """Return pool statistics for debug overlay."""
    return {
        "active": len(_active),
        "pooled_str": len(_pools[tk.StringVar]),
        "pooled_int": len(_pools[tk.IntVar]),
        "pooled_dbl": len(_pools[tk.DoubleVar]),
        "pooled_bool": len(_pools[tk.BooleanVar]),
    }
