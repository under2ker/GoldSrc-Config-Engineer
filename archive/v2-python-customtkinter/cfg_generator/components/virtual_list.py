"""
VirtualList — renders only visible items in a scrollable container.
Greatly reduces widget count for large lists (presets, history, CVARs).
"""

import tkinter as tk
from typing import Callable, Any, Optional

import customtkinter as ctk

from cfg_generator.theme import T


class VirtualList(ctk.CTkFrame):
    """
    Scrollable frame that only creates widgets for visible items.

    Usage:
        vl = VirtualList(parent, item_height=60, render_fn=my_render)
        vl.set_items(data_list)

    render_fn(parent_frame, item, index) -> ctk.CTkFrame or widget
    """

    def __init__(self, parent, item_height: int = 50,
                 render_fn: Optional[Callable] = None,
                 overscan: int = 3, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._item_height = item_height
        self._render_fn = render_fn
        self._overscan = overscan
        self._items: list[Any] = []
        self._visible_widgets: dict[int, ctk.CTkFrame] = {}
        self._last_visible: tuple[int, int] = (-1, -1)

        self._canvas = tk.Canvas(self, bg=T.BG_PRIMARY, highlightthickness=0,
                                 borderwidth=0)
        self._scrollbar = ctk.CTkScrollbar(self, command=self._canvas.yview,
                                            button_color=T.BORDER,
                                            button_hover_color=T.TEXT_MUTED)
        self._inner = tk.Frame(self._canvas, bg=T.BG_PRIMARY)

        def _yscroll(*args):
            self._scrollbar.set(*args)
            self.after_idle(self._update_visible)

        self._canvas.configure(yscrollcommand=_yscroll)
        self._window_id = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw")

        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel_linux)
        self._canvas.bind("<Button-5>", self._on_mousewheel_linux)
        self._inner.bind("<MouseWheel>", self._on_mousewheel)
        self._inner.bind("<Button-4>", self._on_mousewheel_linux)
        self._inner.bind("<Button-5>", self._on_mousewheel_linux)

    def set_items(self, items: list):
        self._items = items
        self._clear_widgets()
        total_h = len(items) * self._item_height
        self._inner.configure(height=total_h)
        self._canvas.configure(scrollregion=(0, 0, self._canvas.winfo_width(), total_h))
        self._canvas.yview_moveto(0)
        self._update_visible()

    def _clear_widgets(self):
        for w in self._visible_widgets.values():
            w.destroy()
        self._visible_widgets.clear()
        self._last_visible = (-1, -1)

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._window_id, width=event.width)
        if self._items:
            total_h = len(self._items) * self._item_height
            self._canvas.configure(scrollregion=(0, 0, event.width, total_h))
        self._update_visible()

    def _on_mousewheel(self, event):
        if event.delta:
            self._canvas.yview_scroll(int(-event.delta / 120), "units")
        self.after(10, self._update_visible)

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(3, "units")
        self.after(10, self._update_visible)

    def _update_visible(self):
        if not self._items or not self._render_fn:
            return

        canvas_h = self._canvas.winfo_height()
        if canvas_h < 10:
            return

        y_top = self._canvas.canvasy(0)
        y_bot = y_top + canvas_h

        first = max(0, int(y_top / self._item_height) - self._overscan)
        last = min(len(self._items) - 1,
                   int(y_bot / self._item_height) + self._overscan)

        if (first, last) == self._last_visible:
            return
        self._last_visible = (first, last)

        needed = set(range(first, last + 1))
        existing = set(self._visible_widgets.keys())

        for idx in existing - needed:
            self._visible_widgets[idx].destroy()
            del self._visible_widgets[idx]

        for idx in needed - existing:
            if idx >= len(self._items):
                continue
            frame = tk.Frame(self._inner, bg=T.BG_PRIMARY)
            frame.place(x=0, y=idx * self._item_height,
                        relwidth=1.0, height=self._item_height)
            frame.bind("<MouseWheel>", self._on_mousewheel)
            self._render_fn(frame, self._items[idx], idx)
            self._visible_widgets[idx] = frame

    def refresh(self):
        self._last_visible = (-1, -1)
        self._clear_widgets()
        self._update_visible()
