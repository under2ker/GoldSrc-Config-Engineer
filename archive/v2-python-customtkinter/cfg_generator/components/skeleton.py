"""
Skeleton screen component — animated shimmer placeholders
shown while pages load (lazy loading visual feedback).
"""

import tkinter as tk
import customtkinter as ctk
from cfg_generator.theme import T


class SkeletonBlock(ctk.CTkFrame):
    """A single shimmer placeholder bar."""

    def __init__(self, master, width=300, height=20, **kw):
        super().__init__(master, width=width, height=height,
                         corner_radius=6, fg_color=T.BG_TERTIARY, **kw)
        self.configure(width=width, height=height)
        self.pack_propagate(False)
        self.grid_propagate(False)
        self._shimmer_canvas = tk.Canvas(
            self, width=width, height=height,
            bg=self._apply_appearance_mode(T.BG_TERTIARY),
            highlightthickness=0, bd=0,
        )
        self._shimmer_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._grad_id = None
        self._phase = 0.0
        self._blk_w = width
        self._blk_h = height
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._animate()

    def stop(self):
        self._running = False
        if self._grad_id:
            try:
                self.after_cancel(self._grad_id)
            except Exception:
                pass
            self._grad_id = None

    def _animate(self):
        if not self._running:
            return
        c = self._shimmer_canvas
        c.delete("shimmer")
        gx = int(self._phase * (self._blk_w + 80)) - 80
        c.create_rectangle(
            gx, 0, gx + 80, self._blk_h,
            fill=T.BG_CARD_HOVER, outline="", tags="shimmer",
        )
        self._phase += 0.04
        if self._phase > 1.0:
            self._phase = 0.0
        self._grad_id = self.after(30, self._animate)

    def destroy(self):
        self.stop()
        super().destroy()


class SkeletonScreen(ctk.CTkFrame):
    """Full skeleton layout mimicking a typical page: header + cards."""

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=T.BG_PRIMARY, **kw)
        self._blocks: list[SkeletonBlock] = []
        self._build()
        self._start_all()

    def _build(self):
        self._add_block(width=280, height=28, pady=(20, 4), padx=24)
        self._add_block(width=400, height=14, pady=(0, 16), padx=24)

        for _ in range(3):
            card = ctk.CTkFrame(self, fg_color=T.BG_SECONDARY, corner_radius=10)
            card.pack(fill="x", padx=24, pady=(0, 10))
            inner_pad = 14
            b1 = SkeletonBlock(card, width=200, height=16)
            b1.pack(anchor="w", padx=inner_pad, pady=(inner_pad, 6))
            self._blocks.append(b1)
            b2 = SkeletonBlock(card, width=340, height=12)
            b2.pack(anchor="w", padx=inner_pad, pady=(0, 4))
            self._blocks.append(b2)
            b3 = SkeletonBlock(card, width=260, height=12)
            b3.pack(anchor="w", padx=inner_pad, pady=(0, inner_pad))
            self._blocks.append(b3)

    def _add_block(self, width, height, **pack_kw):
        b = SkeletonBlock(self, width=width, height=height)
        b.pack(anchor="w", **pack_kw)
        self._blocks.append(b)

    def _start_all(self):
        for b in self._blocks:
            b.start()

    def stop_all(self):
        for b in self._blocks:
            b.stop()

    def destroy(self):
        self.stop_all()
        super().destroy()
