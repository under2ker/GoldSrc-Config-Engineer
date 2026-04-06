"""
Performance profiling and monitoring utilities.
Provides startup timeline, debug overlay data, and benchmarks.
"""

import time
import sys
from typing import Optional

_t0 = time.perf_counter()
_timeline: list[tuple[float, str]] = []


def mark(label: str):
    """Record a timestamped event in the startup timeline."""
    elapsed = time.perf_counter() - _t0
    _timeline.append((elapsed, label))


def get_timeline() -> list[tuple[float, str]]:
    return list(_timeline)


def format_timeline() -> str:
    lines = []
    for t, label in _timeline:
        lines.append(f"[{t:7.3f}s] {label}")
    return "\n".join(lines)


def get_memory_mb() -> float:
    """Current process RSS in MB."""
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


def count_widgets(root) -> int:
    """Recursively count all tkinter child widgets."""
    count = 0
    try:
        children = root.winfo_children()
        count = len(children)
        for child in children:
            count += count_widgets(child)
    except Exception:
        pass
    return count


def count_after_tasks(root) -> int:
    """Estimate active after() tasks via tk internal call."""
    try:
        return len(root.tk.call("after", "info"))
    except Exception:
        return 0


class DebugStats:
    """Collects runtime stats for the debug overlay."""

    def __init__(self):
        self.fps = 0.0
        self.ram_mb = 0.0
        self.widget_count = 0
        self.after_count = 0
        self.cache_size = 0
        self.var_pool_stats: dict = {}
        self.img_cache_stats: dict = {}
        self.last_draw_ms = 0.0
        self.startup_time = 0.0
        self.page_cache_count = 0
        self._prev_widget_count = 0
        self._log_counter = 0

    def update(self, root):
        self.ram_mb = get_memory_mb()
        self.widget_count = count_widgets(root)
        self.after_count = count_after_tasks(root)
        if _timeline:
            self.startup_time = _timeline[-1][0]
        try:
            from cfg_generator.core.var_pool import pool_stats
            self.var_pool_stats = pool_stats()
        except Exception:
            pass
        try:
            from cfg_generator.components.image_cache import cache_stats
            self.img_cache_stats = cache_stats()
        except Exception:
            pass
        if hasattr(root, "_page_last_used"):
            self.page_cache_count = len(root._page_last_used)

        self._log_counter += 1
        if self._log_counter >= 30:
            self._log_counter = 0
            self._log_leak_report(root)

    def _log_leak_report(self, root):
        """Periodic leak report to log (every ~60 sec at 2 sec update interval)."""
        import logging
        logger = logging.getLogger("perf.leaks")
        delta = self.widget_count - self._prev_widget_count
        sign = "+" if delta > 0 else ""
        logger.debug(
            f"[LEAK-WATCH] widgets={self.widget_count} ({sign}{delta}) "
            f"after={self.after_count} ram={self.ram_mb:.0f}MB "
            f"vars_active={self.var_pool_stats.get('active', '?')} "
            f"pages_cached={self.page_cache_count}"
        )
        self._prev_widget_count = self.widget_count

    def to_lines(self) -> list[str]:
        lines = [
            f"RAM: {self.ram_mb:.0f} MB",
            f"Widgets: {self.widget_count}",
            f"After tasks: {self.after_count}",
            f"Startup: {self.startup_time:.2f}s",
        ]
        if self.last_draw_ms > 0:
            lines.append(f"Draw: {self.last_draw_ms:.1f}ms")
        va = self.var_pool_stats.get("active", 0)
        vp = sum(self.var_pool_stats.get(k, 0) for k in ("pooled_str", "pooled_int", "pooled_dbl", "pooled_bool"))
        if va or vp:
            lines.append(f"Vars: {va} active, {vp} pooled")
        if self.page_cache_count:
            lines.append(f"Pages cached: {self.page_cache_count}")
        return lines


mark("perf module loaded")
