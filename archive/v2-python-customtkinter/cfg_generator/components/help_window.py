"""
Built-in Help Window (F1) — sectioned reference for GoldSrc Config Engineer.
"""

import tkinter as tk
from typing import Optional

import customtkinter as ctk

from cfg_generator.theme import T

HELP_SECTIONS = [
    ("Быстрый старт", [
        "1. Перейдите в «Быстрая настройка» и выберите режим игры",
        "2. Настройте чувствительность, FPS и громкость",
        "3. Нажмите «⚡ Создать конфиг»",
        "4. Перейдите в «Экспорт» и сохраните файл",
        "5. Скопируйте .cfg в папку CS 1.6: cstrike/",
        "6. В консоли CS введите: exec autoexec.cfg",
    ]),
    ("Горячие клавиши", [
        "Ctrl+G    —  Создать конфиг",
        "Ctrl+S    —  Сохранить профиль",
        "Ctrl+E    —  Экспорт .cfg",
        "Ctrl+I    —  Импорт .cfg",
        "Ctrl+K    —  Глобальный поиск",
        "Ctrl+Z    —  Отмена (Undo)",
        "Ctrl+Y    —  Повтор (Redo)",
        "Ctrl+D    —  Диагностика",
        "Ctrl+P    —  Предпросмотр",
        "F1        —  Справка (это окно)",
        "F5        —  Обновить превью",
        "F12       —  Debug-оверлей",
    ]),
    ("Режимы игры", [
        "Режим определяет базовые CVAR: скорость, деньги, раунды, оружие и т.д.",
        "Доступные режимы: Competitive 5v5, Public, Deathmatch, AWP Only,",
        "GunGame, Knife, Zombie, Surf, KZ, HNS, Retake, 1v1 Arena и др.",
        "Выберите режим → настройки автоматически применятся к конфигу.",
    ]),
    ("Про-пресеты", [
        "Пресеты — это настройки профессиональных игроков.",
        "Включают чувствительность, раскладку клавиш, видео и звук.",
        "Вы можете применить пресет как основу и доработать вручную.",
    ]),
    ("Профили", [
        "Профиль — сохранённая конфигурация со всеми настройками.",
        "Создание: настройте конфиг → Профили → «Сохранить»",
        "Доступные действия: загрузка, переименование, дублирование, удаление.",
        "Автосохранение защищает от потери при вылете.",
    ]),
    ("Прицел (Crosshair Editor)", [
        "WYSIWYG-редактор прицела с превью в реальном времени.",
        "Настройки: цвет, толщина, зазор, длина, T-стиль, динамика.",
        "Доступны пресеты, экспорт PNG, side-by-side сравнение.",
        "Share Code: делитесь настройками прицела через код CSXH-...",
    ]),
    ("Экспорт и загрузка в игру", [
        "Одиночный файл: autoexec.cfg с вашими настройками.",
        "Полный набор: autoexec.cfg + userconfig.cfg + buy.cfg и др.",
        "Загрузка в игру: автоматическое копирование в папку CS 1.6",
        "  и выполнение exec через симуляцию нажатий.",
        "Очистка клиента: удаление мусорных файлов из cstrike/.",
    ]),
    ("Диагностика", [
        "Автоматический анализ конфига: скоринг, ошибки, предупреждения.",
        "Проверяет: диапазоны CVAR, конфликты биндов, безопасность.",
        "Запускается автоматически после каждого экспорта.",
        "Кнопка «Авто-фикс» исправляет найденные проблемы.",
    ]),
    ("Калькулятор чувствительности", [
        "eDPI = DPI мыши × sensitivity в игре",
        "cm/360 = расстояние (в см) для полного поворота на 360°",
        "Профессионалы обычно играют на 800–1600 eDPI.",
    ]),
    ("FAQ", [
        "Q: Конфиг не применяется в игре?",
        "A: Убедитесь что файл в cstrike/, а не cstrike_russian/.",
        "",
        "Q: Чувствительность не меняется?",
        "A: Проверьте что m_rawinput «1» и нет конфликтов в других .cfg.",
        "",
        "Q: FPS ниже ожидаемого?",
        "A: Добавьте -noforcemaccel -noforcemparms в параметры запуска.",
        "   Используйте gl_vsync 0 и fps_max 999.",
    ]),
]


class HelpWindow(ctk.CTkToplevel):
    """Modal-ish help window opened by F1."""

    _instance: Optional["HelpWindow"] = None

    def __init__(self, master):
        if HelpWindow._instance and HelpWindow._instance.winfo_exists():
            HelpWindow._instance.focus()
            return
        super().__init__(master)
        HelpWindow._instance = self

        self.title("Справка — GoldSrc Config Engineer")
        self.geometry("720x600")
        self.configure(fg_color=T.BG_PRIMARY)
        self.transient(master)
        self.grab_set()

        self._build()
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F1>", lambda e: self.destroy())

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=T.BG_SECONDARY, height=50)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="📖  Справка", font=T.F_H1, text_color=T.TEXT).pack(
            side="left", padx=16, pady=8)
        ctk.CTkButton(top, text="✕", width=36, height=36, corner_radius=T.BTN_R,
                       fg_color="transparent", hover_color=T.BG_CARD_HOVER,
                       font=T.F_LABEL, command=self.destroy).pack(side="right", padx=8, pady=8)

        paned = ctk.CTkFrame(self, fg_color="transparent")
        paned.pack(fill="both", expand=True, padx=8, pady=8)

        sidebar = ctk.CTkScrollableFrame(paned, fg_color=T.BG_SECONDARY, width=180,
                                          corner_radius=T.CARD_R)
        sidebar.pack(side="left", fill="y", padx=(0, 8))

        self._content = ctk.CTkScrollableFrame(paned, fg_color=T.BG_PRIMARY,
                                                corner_radius=T.CARD_R)
        self._content.pack(side="left", fill="both", expand=True)

        self._section_frames: list[ctk.CTkFrame] = []
        self._section_btns: list[ctk.CTkButton] = []

        for i, (title, _lines) in enumerate(HELP_SECTIONS):
            btn = ctk.CTkButton(sidebar, text=title, height=32, corner_radius=T.BTN_R,
                                 fg_color="transparent", hover_color=T.BG_CARD_HOVER,
                                 text_color=T.TEXT_SEC, font=T.F_LABEL, anchor="w",
                                 command=lambda idx=i: self._scroll_to(idx))
            btn.pack(fill="x", padx=4, pady=2)
            self._section_btns.append(btn)

        for title, lines in HELP_SECTIONS:
            frame = ctk.CTkFrame(self._content, fg_color=T.BG_SECONDARY,
                                  corner_radius=T.CARD_R)
            frame.pack(fill="x", padx=4, pady=(0, 8))
            ctk.CTkLabel(frame, text=title, font=T.F_H2, text_color=T.BLUE).pack(
                anchor="w", padx=12, pady=(10, 4))
            for line in lines:
                ctk.CTkLabel(frame, text=line, font=T.F_BODY, text_color=T.TEXT,
                              wraplength=450, anchor="w", justify="left").pack(
                    anchor="w", padx=16, pady=1)
            ctk.CTkFrame(frame, fg_color="transparent", height=8).pack()
            self._section_frames.append(frame)

    def _scroll_to(self, idx: int):
        for i, btn in enumerate(self._section_btns):
            if i == idx:
                btn.configure(fg_color=T.BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=T.TEXT_SEC)
        target = self._section_frames[idx]
        self._content._parent_canvas.yview_moveto(0)
        self.update_idletasks()
        try:
            y = target.winfo_y()
            total = self._content._parent_canvas.bbox("all")[3]
            if total > 0:
                self._content._parent_canvas.yview_moveto(y / total)
        except Exception:
            pass

    def destroy(self):
        HelpWindow._instance = None
        super().destroy()
