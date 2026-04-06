"""
Weak-reference callback wrappers to prevent memory leaks when widgets
are destroyed but their callbacks still hold strong references.
"""

import weakref
from typing import Any, Callable, Optional


class WeakCallback:
    """Weak reference to a bound method that becomes a no-op after GC."""

    __slots__ = ("_ref", "_func_name", "_fallback")

    def __init__(self, method: Callable, fallback: Optional[Callable] = None):
        try:
            obj = method.__self__
            self._func_name = method.__func__.__name__
            self._ref = weakref.ref(obj)
        except AttributeError:
            self._ref = None
            self._func_name = None
            self._fallback = method
            return
        self._fallback = fallback

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._ref is not None:
            obj = self._ref()
            if obj is None:
                if self._fallback:
                    return self._fallback(*args, **kwargs)
                return None
            return getattr(obj, self._func_name)(*args, **kwargs)
        if self._fallback:
            return self._fallback(*args, **kwargs)
        return None

    @property
    def alive(self) -> bool:
        if self._ref is None:
            return self._fallback is not None
        return self._ref() is not None


def weak_method(method: Callable, fallback: Optional[Callable] = None) -> WeakCallback:
    """Create a WeakCallback from a bound method."""
    return WeakCallback(method, fallback)


def weak_bind(widget, event: str, method: Callable):
    """Bind an event to a widget using a weak reference to the method."""
    cb = WeakCallback(method)
    widget.bind(event, lambda e, _cb=cb: _cb(e))


def weak_command(method: Callable) -> Callable:
    """Return a weak-referenced command callback suitable for button/menu command= parameter."""
    cb = WeakCallback(method)
    return lambda *a, _cb=cb: _cb(*a)
