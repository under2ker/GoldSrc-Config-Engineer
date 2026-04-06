"""
Radar (spider) chart for config comparison.
Optimized: grid drawn once, data polygons updated via coords()/itemconfig().
"""

import math
import tkinter as tk
from typing import Optional

import customtkinter as ctk
from cfg_generator.theme import T


class RadarChart(ctk.CTkFrame):
    """Canvas-based radar chart comparing two configs across several axes."""

    def __init__(self, parent, size: int = 340, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._size = size
        self._cx = size // 2
        self._cy = size // 2
        self._radius = size // 2 - 40

        self._canvas = tk.Canvas(
            self, width=size, height=size,
            bg=T.BG_PRIMARY, highlightthickness=0,
        )
        self._canvas.pack()

        self._axes: list[str] = []
        self._values_a: list[float] = []
        self._values_b: list[float] = []
        self._label_a = "Ваш конфиг"
        self._label_b = "Про-пресет"

        self._grid_drawn = False
        self._poly_a_id: Optional[int] = None
        self._poly_b_id: Optional[int] = None
        self._dots_a: list[int] = []
        self._dots_b: list[int] = []
        self._legend_ids: list[int] = []

    def set_data(self, axes: list[str],
                 values_a: list[float], values_b: list[float],
                 label_a: str = "Ваш конфиг", label_b: str = "Про-пресет"):
        axes_changed = axes != self._axes
        self._axes = axes
        self._values_a = values_a
        self._values_b = values_b
        self._label_a = label_a
        self._label_b = label_b

        if axes_changed or not self._grid_drawn:
            self._draw_full()
        else:
            self._update_polygons()

    def _draw_full(self):
        c = self._canvas
        c.delete("all")
        c.configure(bg=T.BG_PRIMARY)
        self._poly_a_id = None
        self._poly_b_id = None
        self._dots_a.clear()
        self._dots_b.clear()
        self._legend_ids.clear()

        n = len(self._axes)
        if n < 3:
            self._grid_drawn = False
            return

        cx, cy, r = self._cx, self._cy, self._radius
        angles = [2 * math.pi * i / n - math.pi / 2 for i in range(n)]
        self._angles = angles

        for level in (0.25, 0.5, 0.75, 1.0):
            pts = []
            for a in angles:
                pts.append(cx + r * level * math.cos(a))
                pts.append(cy + r * level * math.sin(a))
            c.create_polygon(pts, fill="", outline=T.BORDER, width=1, tags="grid")

        for i, a in enumerate(angles):
            x_end = cx + r * math.cos(a)
            y_end = cy + r * math.sin(a)
            c.create_line(cx, cy, x_end, y_end, fill=T.BORDER, width=1, tags="grid")

            lx = cx + (r + 22) * math.cos(a)
            ly = cy + (r + 22) * math.sin(a)
            c.create_text(lx, ly, text=self._axes[i], fill=T.TEXT_SEC,
                          font=("Segoe UI", 9), anchor="center", tags="grid")

        self._grid_drawn = True
        self._create_polygons()
        self._create_legend()

    def _create_polygons(self):
        c = self._canvas
        n = len(self._axes)
        if n < 3:
            return

        cx, cy, r = self._cx, self._cy, self._radius

        zero_pts = [cx, cy] * n

        self._poly_b_id = c.create_polygon(
            zero_pts, fill="#D2992220", outline=T.ORANGE,
            width=2, stipple="gray50", tags="data")
        self._dots_b = []
        for _ in range(n):
            d = c.create_oval(0, 0, 0, 0, fill=T.ORANGE, outline="", tags="data")
            self._dots_b.append(d)

        self._poly_a_id = c.create_polygon(
            zero_pts, fill="#1F6FEB20", outline=T.BLUE,
            width=2, stipple="gray50", tags="data")
        self._dots_a = []
        for _ in range(n):
            d = c.create_oval(0, 0, 0, 0, fill=T.BLUE, outline="", tags="data")
            self._dots_a.append(d)

        self._update_polygons()

    def _update_polygons(self):
        c = self._canvas
        n = len(self._axes)
        if n < 3:
            return

        cx, cy, r = self._cx, self._cy, self._radius
        angles = self._angles

        if self._poly_b_id and self._values_b:
            pts_b = []
            for i, a in enumerate(angles):
                v = max(0.0, min(1.0, self._values_b[i]))
                pts_b.extend([cx + r * v * math.cos(a), cy + r * v * math.sin(a)])
            c.coords(self._poly_b_id, *pts_b)
            for i in range(n):
                px, py = pts_b[i * 2], pts_b[i * 2 + 1]
                c.coords(self._dots_b[i], px - 3, py - 3, px + 3, py + 3)

        if self._poly_a_id and self._values_a:
            pts_a = []
            for i, a in enumerate(angles):
                v = max(0.0, min(1.0, self._values_a[i]))
                pts_a.extend([cx + r * v * math.cos(a), cy + r * v * math.sin(a)])
            c.coords(self._poly_a_id, *pts_a)
            for i in range(n):
                px, py = pts_a[i * 2], pts_a[i * 2 + 1]
                c.coords(self._dots_a[i], px - 3, py - 3, px + 3, py + 3)

    def _create_legend(self):
        c = self._canvas
        legend_y = self._size - 12
        c.create_rectangle(10, legend_y - 8, 22, legend_y, fill=T.BLUE, outline="", tags="legend")
        c.create_text(26, legend_y - 4, text=self._label_a, fill=T.BLUE,
                      font=("Segoe UI", 9), anchor="w", tags="legend")
        c.create_rectangle(160, legend_y - 8, 172, legend_y, fill=T.ORANGE, outline="", tags="legend")
        c.create_text(176, legend_y - 4, text=self._label_b, fill=T.ORANGE,
                      font=("Segoe UI", 9), anchor="w", tags="legend")


def config_to_radar_values(settings: dict, reference: dict) -> tuple[list[str], list[float], list[float]]:
    """
    Convert two settings dicts to normalized radar values.
    Axes: Sensitivity, FPS, Network, Audio, Visual, Gameplay.
    """
    axes = ["Sensitivity", "FPS", "Network", "Audio", "Visual", "Gameplay"]

    def _norm(val_str, lo, hi):
        try:
            v = float(val_str)
        except (TypeError, ValueError):
            return 0.5
        if hi == lo:
            return 0.5
        return max(0.0, min(1.0, (v - lo) / (hi - lo)))

    def _extract(s):
        sens = _norm(s.get("sensitivity", "2.5"), 0.5, 6.0)
        fps = _norm(s.get("fps_max", "100"), 30, 999)
        rate = _norm(s.get("rate", "25000"), 5000, 100000)
        cmd = _norm(s.get("cl_cmdrate", "30"), 10, 105)
        upd = _norm(s.get("cl_updaterate", "20"), 10, 105)
        net = (rate + cmd + upd) / 3
        vol = _norm(s.get("volume", "0.7"), 0, 1)
        snd = _norm(s.get("snd_noextraupdate", "0"), 0, 1)
        audio = (vol + (1 - snd)) / 2
        fb = _norm(s.get("fps_max", "100"), 30, 300)
        gl = 1.0 if s.get("gl_overbright", "") == "1" else 0.5
        visual = (fb + gl) / 2
        hud = 1.0 if s.get("hud_fastswitch", "") == "1" else 0.5
        ri = 1.0 if s.get("m_rawinput", "") == "1" else 0.3
        gameplay = (hud + ri) / 2
        return [sens, fps, net, audio, visual, gameplay]

    va = _extract(settings)
    vb = _extract(reference)
    return axes, va, vb
