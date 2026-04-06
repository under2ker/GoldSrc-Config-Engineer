"""
Global search palette (Ctrl+K) — command palette for CVAR search.
Toplevel window with fuzzy search across all CVARs, binds, and pages.
"""

import tkinter as tk
from typing import Optional, Callable

import customtkinter as ctk
from cfg_generator.theme import T
from cfg_generator.core.generator import get_all_cvars


class SearchEntry:
    """One searchable item."""
    __slots__ = ("name", "description", "category", "page_key", "icon")

    def __init__(self, name: str, description: str, category: str,
                 page_key: str, icon: str = ""):
        self.name = name
        self.description = description
        self.category = category
        self.page_key = page_key
        self.icon = icon


def _build_index() -> list[SearchEntry]:
    items: list[SearchEntry] = []
    cvars = get_all_cvars()
    for cat_key, cat_data in cvars.items():
        for cvar_name, cvar_info in cat_data.items():
            desc_ru = cvar_info.get("description_ru", "")
            desc_en = cvar_info.get("description_en", "")
            desc = desc_ru or desc_en
            cat_label = cat_key.capitalize()
            items.append(SearchEntry(cvar_name, desc, cat_label, "advanced", "⚙"))

    pages = [
        ("⚡ Быстрая настройка", "quick", "Страница"),
        ("🎮 Режимы игры", "modes", "Страница"),
        ("⭐ Про-пресеты", "presets", "Страница"),
        ("🌐 Сеть", "network", "Страница"),
        ("🖼 Графика", "visual", "Страница"),
        ("✛ Редактор прицела", "crosshair", "Страница"),
        ("🖥 Оборудование", "hardware", "Страница"),
        ("⌨ Клавиатура биндов", "keyboard", "Страница"),
        ("🖱 Калькулятор sens", "sensitivity", "Страница"),
        ("🔍 Диагностика", "diagnostics", "Страница"),
        ("🎬 Демо-настройки", "demo", "Страница"),
        ("👤 Профили", "profiles", "Страница"),
        ("📜 История", "history", "Страница"),
        ("🎮 Загрузка в игру", "deploy", "Страница"),
        ("🚀 Параметры запуска", "launch", "Страница"),
        ("📄 Просмотр конфига", "preview", "Страница"),
        ("⚙ Настройки", "settings", "Страница"),
    ]
    for label, key, cat in pages:
        items.append(SearchEntry(label, f"Перейти к: {label}", cat, key, "📄"))

    return items


def _fuzzy_match(query: str, text: str) -> bool:
    q = query.lower()
    t = text.lower()
    if q in t:
        return True
    qi = 0
    for ch in t:
        if qi < len(q) and ch == q[qi]:
            qi += 1
    return qi == len(q)


class SearchPalette(ctk.CTkToplevel):
    """Command palette window for global search."""

    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(master)
        self.overrideredirect(True)
        self._on_navigate = on_navigate

        w, h = 520, 400
        sx = master.winfo_rootx() + master.winfo_width() // 2 - w // 2
        sy = master.winfo_rooty() + 60
        self.geometry(f"{w}x{h}+{sx}+{sy}")
        self.configure(fg_color=T.BG_SECONDARY)
        self.attributes("-topmost", True)

        self._index = _build_index()
        self._filtered: list[SearchEntry] = list(self._index)
        self._selected = 0

        outer = ctk.CTkFrame(self, fg_color=T.BG_SECONDARY, corner_radius=12,
                              border_width=2, border_color=T.BLUE)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(hdr, text="🔍", font=ctk.CTkFont(size=16),
                     text_color=T.TEXT_MUTED, width=24).pack(side="left")
        self._entry = ctk.CTkEntry(
            hdr, placeholder_text="Поиск настроек, команд, страниц...",
            width=440, corner_radius=8, fg_color=T.BG_PRIMARY,
            border_color=T.BORDER, font=ctk.CTkFont(size=14),
        )
        self._entry.pack(side="left", padx=(6, 0), fill="x", expand=True)
        self._entry.bind("<KeyRelease>", self._on_key)
        self._entry.bind("<Return>", self._on_enter)
        self._entry.bind("<Escape>", lambda e: self.destroy())
        self._entry.bind("<Up>", self._on_up)
        self._entry.bind("<Down>", self._on_down)
        self._entry.focus_set()

        ctk.CTkFrame(outer, height=1, fg_color=T.BORDER).pack(fill="x", padx=12)

        self._results_fr = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=T.BORDER,
            scrollbar_button_hover_color=T.TEXT_MUTED,
        )
        self._results_fr.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        hint = ctk.CTkFrame(outer, fg_color="transparent")
        hint.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(hint, text="↑↓ навигация    Enter выбрать    Esc закрыть",
                     font=ctk.CTkFont(size=10), text_color=T.TEXT_MUTED).pack(anchor="w")

        self._render()

        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_out(self, _e):
        self.after(200, self._check_focus)

    def _check_focus(self):
        try:
            if not self.focus_get():
                self.destroy()
        except Exception:
            pass

    def _on_key(self, _e):
        q = self._entry.get().strip()
        if q:
            self._filtered = [it for it in self._index
                              if _fuzzy_match(q, it.name) or _fuzzy_match(q, it.description)]
        else:
            self._filtered = list(self._index)
        self._selected = 0
        self._render()

    def _on_up(self, _e):
        if self._selected > 0:
            self._selected -= 1
            self._render()

    def _on_down(self, _e):
        if self._selected < len(self._filtered) - 1:
            self._selected += 1
            self._render()

    def _on_enter(self, _e):
        if self._filtered:
            item = self._filtered[self._selected]
            self.destroy()
            self._on_navigate(item.page_key)

    def _render(self):
        for w in self._results_fr.winfo_children():
            w.destroy()

        show = self._filtered[:30]
        for i, item in enumerate(show):
            selected = i == self._selected
            bg = T.BG_CARD_HOVER if selected else "transparent"
            border = T.BLUE if selected else "transparent"

            row = ctk.CTkFrame(self._results_fr, fg_color=bg, corner_radius=6,
                                border_width=1 if selected else 0,
                                border_color=border, height=36)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=item.icon or "⚙", font=ctk.CTkFont(size=12),
                         text_color=T.TEXT_MUTED, width=20).pack(
                side="left", padx=(8, 4))

            ctk.CTkLabel(row, text=item.name, font=ctk.CTkFont(size=12),
                         text_color=T.TEXT, anchor="w").pack(
                side="left", padx=(0, 8))

            ctk.CTkLabel(row, text=item.category, font=ctk.CTkFont(size=10),
                         text_color=T.TEXT_MUTED, anchor="e").pack(
                side="right", padx=(0, 8))

            if item.description and item.description != item.name:
                desc_short = item.description[:50]
                ctk.CTkLabel(row, text=desc_short, font=ctk.CTkFont(size=10),
                             text_color=T.TEXT_SEC, anchor="w").pack(
                    side="left", padx=(0, 4))

            idx = i
            row.bind("<Button-1>", lambda e, j=idx: self._click(j))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, j=idx: self._click(j))

        if not show:
            ctk.CTkLabel(self._results_fr, text="Ничего не найдено",
                         font=ctk.CTkFont(size=12), text_color=T.TEXT_MUTED).pack(pady=20)

    def _click(self, idx: int):
        if idx < len(self._filtered):
            item = self._filtered[idx]
            self.destroy()
            self._on_navigate(item.page_key)
