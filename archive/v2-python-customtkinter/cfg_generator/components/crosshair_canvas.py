"""
WYSIWYG Crosshair Canvas — real-time crosshair rendering for CS 1.6.
Draws the crosshair on a tkinter Canvas with zoom, outline,
backgrounds, dynamic animation, and T-style support.
"""

import base64
import json
import tkinter as tk
from typing import Optional

import customtkinter as ctk

from cfg_generator.theme import T


BACKGROUNDS = {
    "Dark":    "#2A2A2A",
    "Light":   "#8A8A78",
    "Dust2":   "#B8A680",
    "Nuke":    "#9A9A8A",
    "Inferno": "#8B7355",
}

COLOR_PRESETS = [
    ("#00FF00", "Green",   "1"),
    ("#FF0000", "Red",     "2"),
    ("#0000FF", "Blue",    "3"),
    ("#FFFF00", "Yellow",  "4"),
    ("#00FFFF", "Cyan",    "5"),
    ("#FF00FF", "Magenta", "1"),
    ("#FFFFFF", "White",   "1"),
]

CROSSHAIR_PRESETS = {
    "Competitive": dict(color="#00FF00", thickness=2, gap=3, length=5,
                        show_dot=False, t_style=False, dynamic=False, translucent=False,
                        show_outline=True),
    "Visible":     dict(color="#00FFFF", thickness=2, gap=4, length=7,
                        show_dot=False, t_style=False, dynamic=False, translucent=False,
                        show_outline=True),
    "Training":    dict(color="#FF0000", thickness=3, gap=5, length=8,
                        show_dot=False, t_style=False, dynamic=True, translucent=False,
                        show_outline=True),
    "Minimal":     dict(color="#00FF00", thickness=1, gap=2, length=3,
                        show_dot=False, t_style=False, dynamic=False, translucent=True,
                        show_outline=False),
    "Red Dot":     dict(color="#FF0000", thickness=1, gap=1, length=2,
                        show_dot=True, t_style=False, dynamic=False, translucent=False,
                        show_outline=True),
    "Cyan Large":  dict(color="#00FFFF", thickness=3, gap=5, length=10,
                        show_dot=False, t_style=False, dynamic=False, translucent=False,
                        show_outline=True),
    "Classic":     dict(color="#00FF00", thickness=2, gap=4, length=6,
                        show_dot=False, t_style=False, dynamic=False, translucent=False,
                        show_outline=True),
    "T-Style":     dict(color="#00FF00", thickness=2, gap=3, length=6,
                        show_dot=False, t_style=True, dynamic=False, translucent=False,
                        show_outline=True),
}


class CrosshairCanvas(ctk.CTkFrame):
    """Real-time crosshair preview on a tkinter Canvas."""

    def __init__(self, parent, width: int = 400, height: int = 400):
        super().__init__(parent, fg_color=T.BG_TERTIARY, corner_radius=T.CARD_R,
                         border_width=1, border_color=T.BORDER)
        self.canvas = tk.Canvas(
            self, width=width, height=height,
            bg="#2A2A2A", highlightthickness=0, cursor="crosshair",
        )
        self.canvas.pack(padx=4, pady=4)

        self.color: str = "#00FF00"
        self.thickness: int = 2
        self.gap: int = 4
        self.length: int = 6
        self.show_dot: bool = False
        self.show_outline: bool = True
        self.outline_color: str = "#000000"
        self.t_style: bool = False
        self.translucent: bool = False
        self.dynamic: bool = False
        self.zoom: int = 4

        self._anim_offset: float = 0
        self._anim_id: Optional[str] = None
        self._auto_anim: bool = False
        self._auto_id: Optional[str] = None

        self._dirty: bool = True
        self._item_ids: dict[str, list[int]] = {"outline": [], "fill": [], "dot": []}
        self._prev_hash: int = 0

        self.canvas.bind("<Configure>", lambda e: self._mark_dirty())
        self.after(100, self.draw)

    def _mark_dirty(self):
        self._dirty = True
        self.draw()

    # ─────────────────────────────────── drawing

    def _compute_hash(self, cw: int, ch: int) -> int:
        return hash((cw, ch, self.color, self.thickness, self.gap,
                      self.length, self.zoom, self.show_dot, self.show_outline,
                      self.outline_color, self.t_style, self.translucent,
                      self.dynamic, round(self._anim_offset, 2)))

    def draw(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        h = self._compute_hash(cw, ch)
        if h == self._prev_hash and not self._dirty:
            return
        self._prev_hash = h
        self._dirty = False

        cx = cw // 2
        cy = ch // 2
        z = self.zoom
        gap = int((self.gap + self._anim_offset) * z)
        length = self.length * z
        thick = max(1, self.thickness * z)

        lines: list[tuple[int, int, int, int]] = []
        if not self.t_style:
            lines.append((cx - thick // 2, cy - gap - length,
                          cx + thick // 2, cy - gap))
        lines.append((cx - thick // 2, cy + gap,
                      cx + thick // 2, cy + gap + length))
        lines.append((cx - gap - length, cy - thick // 2,
                      cx - gap, cy + thick // 2))
        lines.append((cx + gap, cy - thick // 2,
                      cx + gap + length, cy + thick // 2))

        num_lines = len(lines)
        pad = max(1, z // 2)
        stipple = "gray50" if self.translucent else ""

        o_ids = self._item_ids["outline"]
        f_ids = self._item_ids["fill"]
        d_ids = self._item_ids["dot"]

        need_outline = num_lines if self.show_outline else 0
        need_fill = num_lines
        need_dot = 1 if self.show_dot else 0

        self._resize_pool(o_ids, need_outline, self.outline_color)
        self._resize_pool(f_ids, need_fill, self.color)
        self._resize_pool(d_ids, need_dot, self.color)

        for i in range(need_outline):
            x1, y1, x2, y2 = lines[i]
            self.canvas.coords(o_ids[i], x1 - pad, y1 - pad, x2 + pad, y2 + pad)
            self.canvas.itemconfig(o_ids[i], fill=self.outline_color, stipple="",
                                   state="normal")

        for i in range(need_fill):
            x1, y1, x2, y2 = lines[i]
            self.canvas.coords(f_ids[i], x1, y1, x2, y2)
            self.canvas.itemconfig(f_ids[i], fill=self.color, stipple=stipple,
                                   state="normal")

        if need_dot:
            ds = max(1, z // 2)
            self.canvas.coords(d_ids[0], cx - ds, cy - ds, cx + ds, cy + ds)
            self.canvas.itemconfig(d_ids[0], fill=self.color, stipple="",
                                   state="normal")

    def _resize_pool(self, pool: list[int], needed: int, default_fill: str):
        """Grow or hide items in a pool to match `needed` count."""
        while len(pool) < needed:
            iid = self.canvas.create_rectangle(0, 0, 0, 0,
                                                fill=default_fill, outline="", tags="xh")
            pool.append(iid)
        for i in range(needed, len(pool)):
            self.canvas.itemconfig(pool[i], state="hidden")

    # ─────────────────────────────────── param update

    def update_param(self, param: str, value):
        setattr(self, param, value)
        self._dirty = True
        self.draw()

    def load_preset(self, preset: dict):
        for k, v in preset.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self._dirty = True
        self.draw()

    # ─────────────────────────────────── background

    def set_background(self, name: str, custom_color: str | None = None):
        if name == "Custom" and custom_color:
            self.canvas.configure(bg=custom_color)
        else:
            self.canvas.configure(bg=BACKGROUNDS.get(name, "#2A2A2A"))
        self._dirty = True
        self.draw()

    # ─────────────────────────────────── animation

    def simulate_shot(self):
        if not self.dynamic:
            return
        self._anim_offset = 8
        self._animate_recovery()

    def _animate_recovery(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        if self._anim_offset > 0.5:
            self._anim_offset *= 0.85
            self.draw()
            self._anim_id = self.after(16, self._animate_recovery)
        else:
            self._anim_offset = 0
            self._anim_id = None
            self.draw()

    def simulate_burst(self, shots: int = 5, interval: int = 120):
        for i in range(shots):
            self.after(i * interval, self.simulate_shot)

    def start_auto_animate(self):
        self._auto_anim = True
        self._auto_tick()

    def stop_auto_animate(self):
        self._auto_anim = False
        if self._auto_id:
            self.after_cancel(self._auto_id)
            self._auto_id = None

    def _auto_tick(self):
        if not self._auto_anim:
            return
        self.simulate_burst(3, 100)
        self._auto_id = self.after(3000, self._auto_tick)

    # ─────────────────────────────────── config generation

    def get_size_name(self) -> str:
        avg = (self.thickness + self.gap) // 2
        if avg <= 2:
            return "small"
        elif avg <= 4:
            return "medium"
        return "large"

    def get_color_code(self) -> str:
        for hex_c, _, code in COLOR_PRESETS:
            if hex_c.upper() == self.color.upper():
                return code
        return "1"

    def get_config_lines(self) -> list[str]:
        return [
            f'cl_crosshair_color "{self.get_color_code()}"',
            f'cl_crosshair_size "{self.get_size_name()}"',
            f'cl_crosshair_translucent "{1 if self.translucent else 0}"',
            f'cl_dynamiccrosshair "{1 if self.dynamic else 0}"',
        ]

    def get_config_text(self) -> str:
        lines = [
            "// ─── CROSSHAIR ───────────────────────────",
            *self.get_config_lines(),
        ]
        return "\n".join(lines)

    # ─────────────────────────────────── share codes

    def to_share_code(self) -> str:
        data = {
            "c": self.color, "t": self.thickness, "g": self.gap,
            "l": self.length, "d": self.show_dot, "o": self.show_outline,
            "ts": self.t_style, "tr": self.translucent, "dy": self.dynamic,
        }
        payload = json.dumps(data, separators=(",", ":"))
        encoded = base64.urlsafe_b64encode(payload.encode()).decode()
        return f"CSXH-{encoded}"

    def from_share_code(self, code: str) -> bool:
        if not code.startswith("CSXH-"):
            return False
        try:
            payload = base64.urlsafe_b64decode(code[5:]).decode()
            data = json.loads(payload)
            mapping = {
                "c": "color", "t": "thickness", "g": "gap", "l": "length",
                "d": "show_dot", "o": "show_outline", "ts": "t_style",
                "tr": "translucent", "dy": "dynamic",
            }
            for short, attr in mapping.items():
                if short in data:
                    setattr(self, attr, data[short])
            self.draw()
            return True
        except Exception:
            return False

    # ─────────────────────────────────── import from cfg text

    def import_from_cfg_text(self, text: str):
        import re
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r'cl_crosshair_color\s+"?(\d)"?', line)
            if m:
                code_to_color = {"1": "#00FF00", "2": "#FF0000", "3": "#0000FF",
                                 "4": "#FFFF00", "5": "#00FFFF"}
                self.color = code_to_color.get(m.group(1), "#00FF00")
            m = re.match(r'cl_crosshair_size\s+"?(auto|small|medium|large)"?', line)
            if m:
                sz = m.group(1)
                defaults = {"auto": (2, 4, 5), "small": (1, 3, 4),
                            "medium": (2, 4, 6), "large": (3, 6, 9)}
                t, g, l = defaults.get(sz, (2, 4, 6))
                self.thickness, self.gap, self.length = t, g, l
            m = re.match(r'cl_crosshair_translucent\s+"?([01])"?', line)
            if m:
                self.translucent = m.group(1) == "1"
            m = re.match(r'cl_dynamiccrosshair\s+"?([01])"?', line)
            if m:
                self.dynamic = m.group(1) == "1"
        self.draw()
