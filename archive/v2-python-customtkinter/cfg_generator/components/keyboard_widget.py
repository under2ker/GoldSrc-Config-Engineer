"""
Interactive keyboard layout for CS 1.6 bind visualization.
Canvas-based rendering: one tk.Canvas instead of 110+ CTkButton widgets.
Keys are drawn as rectangles with tag_bind for click handling.
"""

import tkinter as tk
from typing import Optional, Callable

import customtkinter as ctk
from cfg_generator.theme import T

BIND_CATEGORIES = {
    "movement":      {"color": "#1F6FEB", "label": "Движение"},
    "weapon":        {"color": "#2EA043", "label": "Оружие"},
    "communication": {"color": "#D29922", "label": "Связь"},
    "buy":           {"color": "#F85149", "label": "Закупка"},
    "action":        {"color": "#8B5CF6", "label": "Действие"},
    "unbound":       {"color": None,      "label": "Свободна"},
}

MOVEMENT_KEYS = {"w", "a", "s", "d", "SPACE", "CTRL", "SHIFT", "ALT", "MWHEELUP", "MWHEELDOWN"}
WEAPON_KEYS = {"1", "2", "3", "4", "5", "q", "e", "r", "g", "f"}
COMM_KEYS = {"y", "u", "h", "t"}
BUY_KEYS = {"KP_INS", "KP_END", "KP_DOWNARROW", "KP_PGDN", "KP_LEFTARROW",
            "KP_5", "KP_RIGHTARROW", "KP_HOME", "KP_UPARROW", "KP_PGUP",
            "KP_ENTER", "KP_DEL", "KP_PLUS", "KP_MINUS", "KP_SLASH", "KP_MULTIPLY",
            "b", "m"}

MOVEMENT_CMDS = {"+forward", "+back", "+moveleft", "+moveright", "+jump",
                 "+duck", "+speed", "+use", "+moveup", "+movedown"}
WEAPON_CMDS = {"slot1", "slot2", "slot3", "slot4", "slot5", "lastinv",
               "+reload", "drop", "invnext", "invprev", "+attack", "+attack2"}
COMM_CMDS = {"messagemode", "messagemode2", "+voicerecord", "radio1", "radio2", "radio3"}

MAIN_ROWS = [
    [("ESC", "ESCAPE", 1.0), ("F1", "F1", 1.0), ("F2", "F2", 1.0), ("F3", "F3", 1.0),
     ("F4", "F4", 1.0), ("F5", "F5", 1.0), ("F6", "F6", 1.0), ("F7", "F7", 1.0),
     ("F8", "F8", 1.0), ("F9", "F9", 1.0), ("F10", "F10", 1.0), ("F11", "F11", 1.0), ("F12", "F12", 1.0)],
    [("~", "`", 1.0), ("1", "1", 1.0), ("2", "2", 1.0), ("3", "3", 1.0), ("4", "4", 1.0),
     ("5", "5", 1.0), ("6", "6", 1.0), ("7", "7", 1.0), ("8", "8", 1.0), ("9", "9", 1.0),
     ("0", "0", 1.0), ("-", "-", 1.0), ("=", "=", 1.0), ("Bksp", "BACKSPACE", 1.5)],
    [("Tab", "TAB", 1.5), ("Q", "q", 1.0), ("W", "w", 1.0), ("E", "e", 1.0), ("R", "r", 1.0),
     ("T", "t", 1.0), ("Y", "y", 1.0), ("U", "u", 1.0), ("I", "i", 1.0), ("O", "o", 1.0),
     ("P", "p", 1.0), ("[", "[", 1.0), ("]", "]", 1.0), ("\\", "\\", 1.0)],
    [("Caps", "CAPSLOCK", 1.7), ("A", "a", 1.0), ("S", "s", 1.0), ("D", "d", 1.0),
     ("F", "f", 1.0), ("G", "g", 1.0), ("H", "h", 1.0), ("J", "j", 1.0), ("K", "k", 1.0),
     ("L", "l", 1.0), (";", ";", 1.0), ("'", "'", 1.0), ("Enter", "ENTER", 1.8)],
    [("Shift", "SHIFT", 2.2), ("Z", "z", 1.0), ("X", "x", 1.0), ("C", "c", 1.0),
     ("V", "v", 1.0), ("B", "b", 1.0), ("N", "n", 1.0), ("M", "m", 1.0), (",", ",", 1.0),
     (".", ".", 1.0), ("/", "/", 1.0), ("Shift", "SHIFT", 2.3)],
    [("Ctrl", "CTRL", 1.5), ("Win", "WIN", 1.0), ("Alt", "ALT", 1.2),
     ("Space", "SPACE", 6.0),
     ("Alt", "ALT", 1.2), ("Win", "WIN", 1.0), ("Ctrl", "CTRL", 1.5)],
]

NUMPAD_ROWS = [
    [("NL", "NUMLOCK", 1.0), ("/", "KP_SLASH", 1.0), ("*", "KP_MULTIPLY", 1.0), ("-", "KP_MINUS", 1.0)],
    [("7", "KP_HOME", 1.0), ("8", "KP_UPARROW", 1.0), ("9", "KP_PGUP", 1.0), ("+", "KP_PLUS", 1.0)],
    [("4", "KP_LEFTARROW", 1.0), ("5", "KP_5", 1.0), ("6", "KP_RIGHTARROW", 1.0)],
    [("1", "KP_END", 1.0), ("2", "KP_DOWNARROW", 1.0), ("3", "KP_PGDN", 1.0), ("Ent", "KP_ENTER", 1.0)],
    [("0", "KP_INS", 2.0), (".", "KP_DEL", 1.0)],
]

MOUSE_KEYS = [
    ("LMB", "MOUSE1"), ("RMB", "MOUSE2"), ("M3", "MOUSE3"),
    ("M4", "MOUSE4"), ("M5", "MOUSE5"),
    ("WH\u2191", "MWHEELUP"), ("WH\u2193", "MWHEELDOWN"),
]


def _categorize_bind(bind_key: str, bind_cmd: str) -> str:
    bk = bind_key.upper()
    cmd_lo = bind_cmd.lower().strip('"').strip()

    if cmd_lo in MOVEMENT_CMDS or bk in {k.upper() for k in MOVEMENT_KEYS}:
        return "movement"
    if cmd_lo in WEAPON_CMDS or bk in {k.upper() for k in WEAPON_KEYS}:
        return "weapon"
    if cmd_lo in COMM_CMDS or bk in {k.upper() for k in COMM_KEYS}:
        return "communication"
    if bk in {k.upper() for k in BUY_KEYS} or "buy" in cmd_lo:
        return "buy"
    return "action"


_UNBOUND_FG = "#2A3040"
_UNBOUND_TEXT = "#6A7080"
_KEY_FONT = ("Segoe UI", 9)
_UNIT = 36
_PAD = 2
_RAD = 4


class KeyboardWidget(ctk.CTkFrame):
    """Canvas-based keyboard visualization — one widget instead of 110+ buttons."""

    def __init__(self, parent, binds: Optional[dict] = None,
                 buy_binds: Optional[dict] = None,
                 on_key_click: Optional[Callable] = None, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._binds: dict[str, str] = {}
        self._buy_binds: dict[str, str] = {}
        self._on_key_click = on_key_click
        self._key_items: dict[str, tuple[int, int]] = {}

        if binds:
            self._binds = {k.lower(): v for k, v in binds.items()}
        if buy_binds:
            self._buy_binds = {k.lower(): v for k, v in buy_binds.items()}

        main_w = int(_UNIT * 15.5) + 10
        np_w = _UNIT * 4 + 20
        canvas_w = main_w + np_w + 16
        main_h = _UNIT * 6 + 12
        mouse_h = _UNIT + 10
        legend_h = 24
        canvas_h = main_h + mouse_h + legend_h + 16

        self._canvas = tk.Canvas(self, width=canvas_w, height=canvas_h,
                                 bg=T.BG_PRIMARY, highlightthickness=0)
        self._canvas.pack()
        self._canvas_w = canvas_w
        self._build()

    def _build(self):
        c = self._canvas
        all_binds = {**self._binds, **self._buy_binds}

        y = 4
        for row_data in MAIN_ROWS:
            x = 4
            for label, cs_key, width_u in row_data:
                w = max(int(_UNIT * width_u), _UNIT) - _PAD * 2
                h = _UNIT - _PAD * 2
                self._draw_key(c, x, y, w, h, label, cs_key, all_binds)
                x += max(int(_UNIT * width_u), _UNIT)
            y += _UNIT

        np_x0 = int(_UNIT * 15.5) + 14
        np_y0 = 4 + _UNIT
        c.create_text(np_x0 + _UNIT * 2, np_y0 - 6, text="Numpad",
                      fill=T.TEXT_MUTED, font=("Segoe UI", 8))
        for row_data in NUMPAD_ROWS:
            x = np_x0
            for label, cs_key, width_u in row_data:
                w = max(int(_UNIT * width_u), _UNIT) - _PAD * 2
                h = _UNIT - _PAD * 2
                self._draw_key(c, x, np_y0, w, h, label, cs_key, all_binds)
                x += max(int(_UNIT * width_u), _UNIT)
            np_y0 += _UNIT

        mouse_y = y + 6
        c.create_text(30, mouse_y + _UNIT // 2 - 2, text="Мышь",
                      fill=T.TEXT_MUTED, font=("Segoe UI", 8))
        mx = 60
        for label, cs_key in MOUSE_KEYS:
            w = 50
            h = _UNIT - _PAD * 2
            self._draw_key(c, mx, mouse_y, w, h, label, cs_key, all_binds)
            mx += 54

        legend_y = mouse_y + _UNIT + 8
        lx = 8
        for cat_key, cat_data in BIND_CATEGORIES.items():
            if cat_key == "unbound":
                continue
            color = cat_data["color"]
            c.create_rectangle(lx, legend_y, lx + 10, legend_y + 10,
                               fill=color, outline="")
            c.create_text(lx + 14, legend_y + 5, text=cat_data["label"],
                          fill=T.TEXT_SEC, font=("Segoe UI", 8), anchor="w")
            lx += 80

    def _draw_key(self, c: tk.Canvas, x: int, y: int, w: int, h: int,
                  label: str, cs_key: str, all_binds: dict):
        cs_lower = cs_key.lower()
        cmd = all_binds.get(cs_lower, "")

        if cmd:
            cat = _categorize_bind(cs_key, cmd)
            fill = BIND_CATEGORIES[cat]["color"]
            text_c = "#FFFFFF"
        else:
            fill = _UNBOUND_FG
            text_c = _UNBOUND_TEXT

        tag = f"key_{cs_lower}"
        rect_id = c.create_rectangle(x + _PAD, y + _PAD, x + w, y + h,
                                      fill=fill, outline="", tags=tag)
        text_id = c.create_text(x + _PAD + w // 2, y + _PAD + h // 2,
                                 text=label, fill=text_c, font=_KEY_FONT, tags=tag)
        self._key_items[cs_lower] = (rect_id, text_id)

        c.tag_bind(tag, "<Enter>", lambda e, r=rect_id, f=fill: self._hover_enter(r, f))
        c.tag_bind(tag, "<Leave>", lambda e, r=rect_id, f=fill: self._hover_leave(r, f))
        c.tag_bind(tag, "<Button-1>", lambda e, k=cs_key, cm=cmd: self._click(k, cm))

        if cmd:
            c.tag_bind(tag, "<Enter>",
                       lambda e, r=rect_id, f=fill, k=cs_key, cm=cmd: (
                           self._hover_enter(r, f),
                           self._show_tooltip(e, f"{k}  →  {cm}")),
                       add=False)
            c.tag_bind(tag, "<Leave>",
                       lambda e, r=rect_id, f=fill: (
                           self._hover_leave(r, f), self._hide_tooltip()),
                       add=False)

    def _hover_enter(self, rect_id: int, base_fill: str):
        try:
            r, g, b = self._canvas.winfo_rgb(base_fill)
            lighter = f"#{min(r // 256 + 30, 255):02x}{min(g // 256 + 30, 255):02x}{min(b // 256 + 30, 255):02x}"
            self._canvas.itemconfig(rect_id, fill=lighter)
        except Exception:
            pass

    def _hover_leave(self, rect_id: int, base_fill: str):
        try:
            self._canvas.itemconfig(rect_id, fill=base_fill)
        except Exception:
            pass

    _tip_win: Optional[tk.Toplevel] = None
    _tip_label: Optional[tk.Label] = None

    def _show_tooltip(self, event, text: str):
        if KeyboardWidget._tip_win is None or not KeyboardWidget._tip_win.winfo_exists():
            tw = tk.Toplevel(self)
            tw.wm_overrideredirect(True)
            tw.configure(bg=T.BORDER)
            lbl = tk.Label(tw, text=text, bg="#22293A", fg="#FFFFFF",
                           padx=6, pady=3, font=("Segoe UI", 9))
            lbl.pack(padx=1, pady=1)
            KeyboardWidget._tip_win = tw
            KeyboardWidget._tip_label = lbl
        else:
            KeyboardWidget._tip_label.configure(text=text)
            KeyboardWidget._tip_win.deiconify()

        rx = self._canvas.winfo_rootx() + event.x + 12
        ry = self._canvas.winfo_rooty() + event.y - 28
        KeyboardWidget._tip_win.wm_geometry(f"+{rx}+{ry}")
        KeyboardWidget._tip_win.lift()

    def _hide_tooltip(self):
        if KeyboardWidget._tip_win and KeyboardWidget._tip_win.winfo_exists():
            KeyboardWidget._tip_win.withdraw()

    def _click(self, cs_key: str, cmd: str):
        if self._on_key_click:
            self._on_key_click(cs_key, cmd)

    def update_binds(self, binds: dict, buy_binds: dict):
        self._binds = {k.lower(): v for k, v in binds.items()}
        self._buy_binds = {k.lower(): v for k, v in buy_binds.items()}
        all_binds = {**self._binds, **self._buy_binds}

        c = self._canvas
        for cs_lower, (rect_id, text_id) in self._key_items.items():
            cmd = all_binds.get(cs_lower, "")
            if cmd:
                cat = _categorize_bind(cs_lower, cmd)
                fill = BIND_CATEGORIES[cat]["color"]
                text_c = "#FFFFFF"
            else:
                fill = _UNBOUND_FG
                text_c = _UNBOUND_TEXT
            c.itemconfig(rect_id, fill=fill)
            c.itemconfig(text_id, fill=text_c)

    def get_stats(self) -> dict:
        all_binds = {**self._binds, **self._buy_binds}
        total = len(self._key_items)
        bound = sum(1 for k in self._key_items if all_binds.get(k, ""))
        cats: dict[str, int] = {}
        for k in self._key_items:
            cmd = all_binds.get(k, "")
            if cmd:
                cat = _categorize_bind(k, cmd)
                cats[cat] = cats.get(cat, 0) + 1
        return {"total_keys": total, "bound": bound, "free": total - bound, "categories": cats}
