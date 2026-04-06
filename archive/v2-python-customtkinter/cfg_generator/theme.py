"""
Design system for CS 1.6 GoldSrc Config Engineer.
All colors, fonts, and sizes in one place.
"""

import customtkinter as ctk


class T:
    """Theme constants — centralized design tokens."""

    _COLOR_KEYS = (
        "BG_PRIMARY",
        "BG_SECONDARY",
        "BG_TERTIARY",
        "BG_CARD_HOVER",
        "BORDER",
        "BORDER_ACCENT",
        "TEXT",
        "TEXT_SEC",
        "TEXT_MUTED",
        "BLUE",
        "BLUE_HOVER",
        "GREEN",
        "GREEN_HOVER",
        "ORANGE",
        "RED",
    )

    THEMES = {
        "midnight": {
            "BG_PRIMARY": "#0D1117",
            "BG_SECONDARY": "#161B22",
            "BG_TERTIARY": "#1C2333",
            "BG_CARD_HOVER": "#222D3D",
            "BORDER": "#30363D",
            "BORDER_ACCENT": "#1F6FEB",
            "TEXT": "#E6EDF3",
            "TEXT_SEC": "#8B949E",
            "TEXT_MUTED": "#484F58",
            "BLUE": "#1F6FEB",
            "BLUE_HOVER": "#388BFD",
            "GREEN": "#2EA043",
            "GREEN_HOVER": "#3FB950",
            "ORANGE": "#D29922",
            "RED": "#F85149",
        },
        "carbon": {
            "BG_PRIMARY": "#0A0A0A",
            "BG_SECONDARY": "#111111",
            "BG_TERTIARY": "#1A1A1A",
            "BG_CARD_HOVER": "#242424",
            "BORDER": "#333333",
            "BORDER_ACCENT": "#C8C8C8",
            "TEXT": "#EDEDED",
            "TEXT_SEC": "#A3A3A3",
            "TEXT_MUTED": "#525252",
            "BLUE": "#60A5FA",
            "BLUE_HOVER": "#93C5FD",
            "GREEN": "#4ADE80",
            "GREEN_HOVER": "#86EFAC",
            "ORANGE": "#FB923C",
            "RED": "#F87171",
        },
        "military": {
            "BG_PRIMARY": "#0D1A0D",
            "BG_SECONDARY": "#142014",
            "BG_TERTIARY": "#1A2E1A",
            "BG_CARD_HOVER": "#223822",
            "BORDER": "#2D4A2D",
            "BORDER_ACCENT": "#4ADE80",
            "TEXT": "#E8F5E9",
            "TEXT_SEC": "#A8C5A8",
            "TEXT_MUTED": "#4A6B4A",
            "BLUE": "#4ADE80",
            "BLUE_HOVER": "#6EE7A0",
            "GREEN": "#22C55E",
            "GREEN_HOVER": "#4ADE80",
            "ORANGE": "#FBBF24",
            "RED": "#EF4444",
        },
        "retro_cs": {
            "BG_PRIMARY": "#2A2A1A",
            "BG_SECONDARY": "#333322",
            "BG_TERTIARY": "#3D3D2A",
            "BG_CARD_HOVER": "#4A4A38",
            "BORDER": "#5C5C48",
            "BORDER_ACCENT": "#C8B040",
            "TEXT": "#F5F0D8",
            "TEXT_SEC": "#C8C4A8",
            "TEXT_MUTED": "#7A7858",
            "BLUE": "#C8B040",
            "BLUE_HOVER": "#D4C060",
            "GREEN": "#6B8E23",
            "GREEN_HOVER": "#8FBC4A",
            "ORANGE": "#E8A040",
            "RED": "#D05040",
        },
    }

    current_theme = "midnight"

    # ── Background ──
    BG_PRIMARY = THEMES["midnight"]["BG_PRIMARY"]
    BG_SECONDARY = THEMES["midnight"]["BG_SECONDARY"]
    BG_TERTIARY = THEMES["midnight"]["BG_TERTIARY"]
    BG_CARD_HOVER = THEMES["midnight"]["BG_CARD_HOVER"]

    # ── Borders ──
    BORDER = THEMES["midnight"]["BORDER"]
    BORDER_ACCENT = THEMES["midnight"]["BORDER_ACCENT"]

    # ── Text ──
    TEXT = THEMES["midnight"]["TEXT"]
    TEXT_SEC = THEMES["midnight"]["TEXT_SEC"]
    TEXT_MUTED = THEMES["midnight"]["TEXT_MUTED"]

    # ── Accent ──
    BLUE = THEMES["midnight"]["BLUE"]
    BLUE_HOVER = THEMES["midnight"]["BLUE_HOVER"]
    GREEN = THEMES["midnight"]["GREEN"]
    GREEN_HOVER = THEMES["midnight"]["GREEN_HOVER"]
    ORANGE = THEMES["midnight"]["ORANGE"]
    RED = THEMES["midnight"]["RED"]

    # ── Sizes ──
    SIDEBAR_W = 220
    CARD_R = 12
    BTN_R = 10
    INPUT_R = 8
    NAV_R = 8
    CARD_PAD = 20
    CONTENT_PX = 28
    CONTENT_PT = 28

    # ── Fonts (lazy — call init_fonts() once after root created) ──
    _fonts_ready = False

    @classmethod
    def get_theme_names(cls) -> list[str]:
        return sorted(cls.THEMES.keys())

    @classmethod
    def set_theme(cls, name: str) -> None:
        key = name.lower()
        palette = cls.THEMES.get(key)
        if palette is None:
            raise ValueError(f"Unknown theme: {name!r}. Use one of {cls.get_theme_names()!r}.")
        for attr in cls._COLOR_KEYS:
            setattr(cls, attr, palette[attr])
        cls.current_theme = key

    @classmethod
    def init_fonts(cls):
        if cls._fonts_ready:
            return
        cls._fonts_ready = True
        cls.F_LOGO = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        cls.F_LOGO2 = ctk.CTkFont(family="Segoe UI", size=14)
        cls.F_VER = ctk.CTkFont(family="Segoe UI", size=11)
        cls.F_H1 = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        cls.F_H2 = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        cls.F_BODY = ctk.CTkFont(family="Segoe UI", size=14)
        cls.F_LABEL = ctk.CTkFont(family="Segoe UI", size=13)
        cls.F_CAP = ctk.CTkFont(family="Segoe UI", size=11)
        cls.F_BTN = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        cls.F_NAV = ctk.CTkFont(family="Segoe UI", size=14)
        cls.F_SEC = ctk.CTkFont(family="Segoe UI", size=10)
        cls.F_MONO = ctk.CTkFont(family="Consolas", size=12)
        cls.F_VAL = ctk.CTkFont(family="Consolas", size=14)
        cls.F_STATUS = ctk.CTkFont(family="Segoe UI", size=11)
