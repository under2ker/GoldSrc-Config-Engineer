import os
import threading
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from cfg_generator.core.perf import mark, DebugStats, format_timeline, count_widgets
from cfg_generator.theme import T
from cfg_generator.core.generator import (
    CfgConfig, get_all_cvars, get_modes, get_presets, get_hardware_data,
    get_network_presets, get_visual_presets, get_crosshair_presets,
    get_aliases, get_buyscripts, get_templates, create_mode_config, create_preset_config,
    create_quick_config, compare_configs,
    apply_network_preset, apply_visual_preset, apply_crosshair_preset,
    generate_single_cfg,
)
from cfg_generator.core.validator import validate_config_dict
from cfg_generator.core.optimizer import optimize_config
from cfg_generator.io.exporter import export_single_cfg, export_full_config_set
from cfg_generator.io.importer import import_from_file, import_from_url, SecurityError
from cfg_generator.core.profiles import (
    list_profiles, save_profile, load_profile, delete_profile,
    rename_profile, duplicate_profile, get_active_profile,
    save_history_snapshot, list_history, load_history_snapshot,
    autosave, has_autosave, load_autosave, clear_autosave,
    AUTOSAVE_INTERVAL,
)
from cfg_generator.components.crosshair_canvas import (
    CrosshairCanvas, BACKGROUNDS, COLOR_PRESETS, CROSSHAIR_PRESETS,
)
from cfg_generator.core.diagnostics import (
    run_diagnostics, apply_fix, apply_all_fixes, DiagnosticReport,
)
from cfg_generator.core.game_bridge import (
    find_game_path, is_game_running, get_hl_window,
    deploy_config_files, deploy_userconfig, exec_in_game,
    deploy_and_exec, get_cstrike_path,
    CLEAN_CATEGORIES, scan_cleanup, execute_cleanup, _size_fmt,
)
from cfg_generator.components.radar_chart import RadarChart, config_to_radar_values
from cfg_generator.components.keyboard_widget import KeyboardWidget
from cfg_generator.components.search_palette import SearchPalette
from cfg_generator.components.skeleton import SkeletonScreen
from cfg_generator.components.help_window import HelpWindow
from cfg_generator.core.undo import UndoManager
from cfg_generator.core.weakbind import weak_method
from cfg_generator.core import var_pool
from cfg_generator.pages import (
    CrosshairPageMixin, DeployPageMixin, PreviewPageMixin, SensitivityPageMixin,
)
from cfg_generator.core.generator import get_load_warnings
from cfg_generator.logger import log

VERSION = "2.4.0"


def _load_json_safe(filename: str):
    """Prefetch helper — load a JSON data file silently, triggering its cache."""
    try:
        from cfg_generator.core.generator import _load_json
        _load_json(filename)
    except Exception:
        pass


SCROLLBAR_KW = dict(
    scrollbar_button_color=T.BORDER,
    scrollbar_button_hover_color=T.TEXT_MUTED,
)


# ─────────────────────────────────────────────── Tooltip (single Toplevel pool)
class Tooltip:
    """Hover tooltip using a single shared Toplevel to minimize overhead."""
    _shared_tip: Optional[tk.Toplevel] = None
    _shared_label: Optional[tk.Label] = None

    def __init__(self, widget, text: str, delay: int = 500):
        self._widget = widget
        self._text = text
        self._delay = delay
        self._after_id: Optional[str] = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._cancel, add="+")

    @classmethod
    def _ensure_tip(cls, master):
        if cls._shared_tip is None or not cls._shared_tip.winfo_exists():
            tw = tk.Toplevel(master)
            tw.wm_overrideredirect(True)
            tw.configure(bg=T.BORDER)
            inner = tk.Frame(tw, bg="#22293A", padx=8, pady=4)
            inner.pack(padx=1, pady=1)
            lbl = tk.Label(inner, text="", bg="#22293A", fg=T.TEXT,
                           font=("Segoe UI", 11), wraplength=240, justify="left")
            lbl.pack()
            tw.withdraw()
            cls._shared_tip = tw
            cls._shared_label = lbl

    def _schedule(self, _e):
        self._cancel()
        self._after_id = self._widget.after(self._delay, self._show)

    def _cancel(self, _e=None):
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        self._ensure_tip(self._widget)
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() - 30
        Tooltip._shared_label.configure(text=self._text)
        Tooltip._shared_tip.wm_geometry(f"+{x}+{y}")
        Tooltip._shared_tip.deiconify()
        Tooltip._shared_tip.lift()

    def _hide(self):
        if Tooltip._shared_tip and Tooltip._shared_tip.winfo_exists():
            Tooltip._shared_tip.withdraw()


# ─────────────────────────────────────────────── Toast notification
class Toast(ctk.CTkFrame):
    """Auto-dismissing notification in bottom-right corner."""

    def __init__(self, master, message: str, kind: str = "success", duration: int = 3500):
        super().__init__(master, corner_radius=10, fg_color=T.BG_TERTIARY,
                         border_width=1, border_color=self._border(kind))
        icons = {"success": "\u2705", "error": "\u274c", "warning": "\u26a0\ufe0f", "info": "\u2139\ufe0f"}
        icon = icons.get(kind, "\u2139\ufe0f")
        colors = {"success": T.GREEN, "error": T.RED, "warning": T.ORANGE, "info": T.BLUE}

        ctk.CTkLabel(self, text=f" {icon}  {message}", font=ctk.CTkFont(size=13),
                     text_color=T.TEXT, wraplength=300).pack(padx=14, pady=10)
        left = ctk.CTkFrame(self, width=3, fg_color=colors.get(kind, T.BLUE),
                            corner_radius=2)
        left.place(x=0, rely=0.15, relheight=0.7)

        self.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        self.after(duration, self._dismiss)

    @staticmethod
    def _border(kind):
        return {"success": T.GREEN, "error": T.RED, "warning": T.ORANGE}.get(kind, T.BORDER)

    def _dismiss(self):
        self.destroy()


# ─────────────────────────────────────────────── Splash Screen
class SplashScreen(ctk.CTkToplevel):
    """Brief loading screen shown on startup."""

    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        w, h = 380, 200
        sx = self.winfo_screenwidth() // 2 - w // 2
        sy = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{sx}+{sy}")
        self.configure(fg_color=T.BG_PRIMARY)

        ctk.CTkLabel(self, text="CS 1.6", font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=T.TEXT).pack(pady=(36, 0))
        ctk.CTkLabel(self, text="GoldSrc Config Engineer", font=ctk.CTkFont(size=16),
                     text_color=T.BLUE).pack(pady=(2, 0))
        ctk.CTkLabel(self, text=f"v{VERSION}", font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_MUTED).pack(pady=(4, 0))

        self._bar = ctk.CTkProgressBar(self, width=240, height=6,
                                        progress_color=T.BLUE, fg_color=T.BORDER,
                                        corner_radius=3)
        self._bar.pack(pady=(20, 0))
        self._bar.set(0)

        ctk.CTkLabel(self, text="Loading...", font=ctk.CTkFont(size=11),
                     text_color=T.TEXT_MUTED).pack(pady=(8, 0))

        self._progress = 0.0
        self._animate()

    def _animate(self):
        if self._progress < 1.0:
            self._progress += 0.08
            self._bar.set(min(self._progress, 1.0))
            self.after(50, self._animate)


# ─────────────────────────────────────────────── Main App
class App(CrosshairPageMixin, DeployPageMixin, PreviewPageMixin, SensitivityPageMixin, ctk.CTk):
    _executor = ThreadPoolExecutor(max_workers=2)

    def __init__(self):
        super().__init__()
        mark("CTk.__init__ done")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        T.init_fonts()

        self.title("CS 1.6 — GoldSrc Config Engineer")
        self.geometry("1140x760")
        self.minsize(1050, 600)
        self.configure(fg_color=T.BG_PRIMARY)

        self.withdraw()
        splash = SplashScreen(self)
        splash.update()

        self.current_config: Optional[CfgConfig] = None
        self._undo = UndoManager()
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._search_win: Optional[SearchPalette] = None
        self._debug_stats = DebugStats()
        self._debug_visible = False
        self._toast_pool: list[ctk.CTkFrame] = []
        self._debounce_ids: dict[str, str] = {}
        self._current_page_key: Optional[str] = None
        self._prev_page_key: Optional[str] = None
        self._page_cache: dict[str, ctk.CTkFrame] = {}
        self._page_last_used: dict[str, float] = {}
        self._page_gc_id: Optional[str] = None
        self._resizing = False
        self._resize_after_id: Optional[str] = None

        mark("pre-build")
        self._build()
        mark("post-build")
        self._bind_hotkeys()
        self.bind("<Configure>", weak_method(self._on_resize))
        self._nav("dashboard")
        mark("dashboard shown")

        self.after(800, lambda: (splash.destroy(), self.deiconify()))
        self.after(1200, self._startup_checks)
        self._start_autosave()
        self.after(1500, self._background_preload)
        mark("init complete")

    # ────────────────────────────────────────────── startup
    def _startup_checks(self):
        warnings = get_load_warnings()
        for w in warnings:
            self._toast(w, "warning")
            log.warning(w)

        if has_autosave() and self.current_config is None:
            recovered = load_autosave()
            if recovered:
                self.current_config = recovered
                self._upd()
                self._toast("Восстановлен несохранённый конфиг", "info")
                clear_autosave()

    def _start_autosave(self):
        autosave(self.current_config)
        self.after(AUTOSAVE_INTERVAL * 1000, self._start_autosave)

    def _background_preload(self):
        """Preload heavy data in background thread after UI is visible."""
        def _preload():
            get_all_cvars()
            get_aliases()
            get_buyscripts()
            get_crosshair_presets()
            get_templates()
            mark("background preload done")
        threading.Thread(target=_preload, daemon=True).start()

    def _debounce(self, key: str, delay_ms: int, callback):
        """Cancel previous pending call for *key* and schedule a new one."""
        old = self._debounce_ids.pop(key, None)
        if old:
            self.after_cancel(old)
        self._debounce_ids[key] = self.after(delay_ms, callback)

    def _ui_chunked(
        self,
        items: list,
        batch_size: int,
        build_one,
        *,
        on_done=None,
        delay_ms: int = 1,
        cancel_gen: Optional[int] = None,
    ):
        """Create widgets in batches so the Tk event loop stays responsive."""
        if not items:
            if on_done:
                on_done()
            return

        start = [0]

        def tick():
            if cancel_gen is not None and cancel_gen != getattr(self, "_ui_chunk_gen", 0):
                return
            end = min(start[0] + batch_size, len(items))
            for i in range(start[0], end):
                build_one(items[i], i)
            start[0] = end
            if start[0] < len(items):
                self.after(delay_ms, tick)
            elif on_done:
                on_done()

        tick()

    # ────────────────────────────────────────────── resize animation pause
    def _on_resize(self, event):
        if event.widget is not self:
            return
        if not self._resizing:
            self._resizing = True
            self._pause_animations()
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(200, self._resume_after_resize)

    def _resume_after_resize(self):
        self._resizing = False
        self._resize_after_id = None
        self._resume_animations()

    def _pause_animations(self):
        if hasattr(self, "_xh") and hasattr(self._xh, "stop_auto_animate"):
            self._xh.stop_auto_animate()

    def _resume_animations(self):
        if (hasattr(self, "_xh") and hasattr(self, "_xh_auto_var")
                and self._xh_auto_var.get()):
            self._xh.start_auto_animate()

    # ────────────────────────────────────────────── debug overlay (F12)
    def _toggle_debug(self):
        if self._debug_visible:
            if hasattr(self, "_debug_frame"):
                self._debug_frame.place_forget()
            self._debug_visible = False
            return
        self._debug_visible = True
        if not hasattr(self, "_debug_frame"):
            df = ctk.CTkFrame(self, fg_color="#000000", corner_radius=8,
                               border_width=1, border_color=T.BLUE)
            df.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=40)
            self._debug_frame = df
            self._debug_label = ctk.CTkLabel(df, text="loading...",
                                              font=ctk.CTkFont(family="Consolas", size=10),
                                              text_color="#00FF00", justify="left")
            self._debug_label.pack(padx=8, pady=6)
        else:
            self._debug_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=40)
        self._update_debug()

    def _update_debug(self):
        if not self._debug_visible:
            return
        self._debug_stats.update(self)
        lines = self._debug_stats.to_lines()
        lines.append(f"Config: {'yes' if self.current_config else 'no'}")
        lines.append(f"Undo stack: {self._undo.undo_count}")
        self._debug_label.configure(text="\n".join(lines))
        self.after(2000, self._update_debug)

    # ────────────────────────────────────────────── custom title bar
    def _build_titlebar(self):
        tb = ctk.CTkFrame(self, height=34, fg_color=T.BG_SECONDARY, corner_radius=0)
        tb.grid(row=0, column=0, columnspan=2, sticky="we")
        tb.grid_propagate(False)
        self._titlebar = tb

        ctk.CTkLabel(tb, text="  CS 1.6 — GoldSrc Config Engineer",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SEC).pack(side="left", padx=(8, 0))

        # search button
        ctk.CTkButton(tb, text="🔍 Ctrl+K", width=90, height=24,
                      corner_radius=6, fg_color=T.BG_TERTIARY,
                      hover_color=T.BG_CARD_HOVER, text_color=T.TEXT_MUTED,
                      font=ctk.CTkFont(size=10),
                      command=self._open_search).pack(side="left", padx=(12, 0))

        # undo/redo buttons
        self._undo_btn = ctk.CTkButton(tb, text="↶", width=28, height=24,
                                        corner_radius=6, fg_color="transparent",
                                        hover_color=T.BG_TERTIARY, text_color=T.TEXT_MUTED,
                                        font=ctk.CTkFont(size=14),
                                        command=self._do_undo)
        self._undo_btn.pack(side="left", padx=(8, 0))
        self._redo_btn = ctk.CTkButton(tb, text="↷", width=28, height=24,
                                        corner_radius=6, fg_color="transparent",
                                        hover_color=T.BG_TERTIARY, text_color=T.TEXT_MUTED,
                                        font=ctk.CTkFont(size=14),
                                        command=self._do_redo)
        self._redo_btn.pack(side="left", padx=(2, 0))

        # window controls (right side)
        close_btn = ctk.CTkButton(tb, text="✕", width=36, height=24,
                                   corner_radius=0, fg_color="transparent",
                                   hover_color=T.RED, text_color=T.TEXT,
                                   font=ctk.CTkFont(size=14),
                                   command=self.destroy)
        close_btn.pack(side="right", padx=(0, 4))

        max_btn = ctk.CTkButton(tb, text="□", width=36, height=24,
                                 corner_radius=0, fg_color="transparent",
                                 hover_color=T.BG_TERTIARY, text_color=T.TEXT_MUTED,
                                 font=ctk.CTkFont(size=12),
                                 command=self._toggle_maximize)
        max_btn.pack(side="right")

        min_btn = ctk.CTkButton(tb, text="─", width=36, height=24,
                                 corner_radius=0, fg_color="transparent",
                                 hover_color=T.BG_TERTIARY, text_color=T.TEXT_MUTED,
                                 font=ctk.CTkFont(size=12),
                                 command=self.iconify)
        min_btn.pack(side="right")

        self._maximized = False
        self._drag_x = 0
        self._drag_y = 0
        tb.bind("<Button-1>", self._tb_start_drag)
        tb.bind("<B1-Motion>", self._tb_drag)
        tb.bind("<Double-Button-1>", lambda e: self._toggle_maximize())

    def _tb_start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _tb_drag(self, event):
        if self._maximized:
            return
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _toggle_maximize(self):
        if self._maximized:
            self.geometry(self._restore_geo)
            self._maximized = False
        else:
            self._restore_geo = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
            self._maximized = True

    # ────────────────────────────────────────────── layout
    def _build(self):
        self.overrideredirect(True)
        self._build_titlebar()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        sb = ctk.CTkFrame(self, width=T.SIDEBAR_W, corner_radius=0,
                          fg_color=T.BG_SECONDARY, border_width=0)
        sb.grid(row=1, column=0, sticky="nswe")
        sb.grid_propagate(False)
        self._sidebar = sb

        # logo (compact)
        ctk.CTkLabel(sb, text="CS 1.6  CFG", font=T.F_LOGO, text_color=T.TEXT).pack(pady=(14, 0))
        ctk.CTkLabel(sb, text=f"v{VERSION}", font=T.F_VER,
                     text_color=T.TEXT_MUTED).pack(pady=(0, 4))

        # profile selector
        pf = ctk.CTkFrame(sb, fg_color="transparent")
        pf.pack(fill="x", padx=10, pady=(0, 4))
        self._prof_cb = ctk.CTkComboBox(
            pf, values=["(нет)"], width=148, height=26, state="readonly",
            corner_radius=6, fg_color=T.BG_TERTIARY, border_color=T.BORDER,
            font=ctk.CTkFont(size=10),
            command=self._on_profile_switch,
        )
        self._prof_cb.pack(side="left", padx=(0, 3))
        self._prof_cb.set("(нет)")
        ctk.CTkButton(pf, text="+", width=26, height=26, corner_radius=6,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._quick_save_profile).pack(side="left")
        self._refresh_profile_list()

        # ── scrollable nav area ──
        nav_scroll = ctk.CTkScrollableFrame(sb, fg_color="transparent",
                                             scrollbar_button_color=T.BG_SECONDARY,
                                             scrollbar_button_hover_color=T.BORDER)
        nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self._sep(nav_scroll)
        self._nav_btn(nav_scroll, "dashboard", "\U0001f3e0  Главная")
        self._sep(nav_scroll)
        self._sec_label(nav_scroll, "КОНФИГУРАЦИЯ")
        nav1 = [
            ("quick",      "\u26a1  Быстрая настройка"),
            ("templates",  "\U0001f4cb  Шаблоны"),
            ("modes",      "\U0001f3ae  Режимы игры"),
            ("presets",    "\u2b50  Про-пресеты"),
            ("favorites",  "\u2b50  Избранное"),
            ("network",    "\U0001f310  Сеть"),
            ("visual",     "\U0001f5bc  Графика"),
            ("crosshair",  "\u271b  Редактор прицела"),
            ("hardware",   "\U0001f5a5  Оборудование"),
            ("advanced",   "\u2699  Расширенные"),
        ]
        for k, lbl in nav1:
            self._nav_btn(nav_scroll, k, lbl)

        self._sep(nav_scroll)
        self._sec_label(nav_scroll, "ФАЙЛЫ")
        nav2 = [
            ("export",  "\U0001f4e4  Экспорт"),
            ("import",  "\U0001f4e5  Импорт"),
            ("compare", "\U0001f500  Сравнение"),
        ]
        for k, lbl in nav2:
            self._nav_btn(nav_scroll, k, lbl)

        self._sep(nav_scroll)
        self._sec_label(nav_scroll, "ИНСТРУМЕНТЫ")
        nav3 = [
            ("keyboard",    "\u2328  Клавиатура биндов"),
            ("buyscript",   "\U0001f6d2  Редактор закупки"),
            ("sensitivity", "\U0001f5b1  Калькулятор sens"),
            ("diagnostics", "\U0001f50d  Диагностика"),
            ("demo",        "\U0001f3ac  Демо-настройки"),
            ("profiles",    "\U0001f464  Профили"),
            ("history",     "\U0001f4dc  История"),
            ("deploy",      "\U0001f3ae  Загрузка в игру"),
            ("launch",      "\U0001f680  Параметры запуска"),
            ("preview",     "\U0001f4c4  Просмотр конфига"),
            ("settings",    "\u2699  Настройки"),
        ]
        for k, lbl in nav3:
            self._nav_btn(nav_scroll, k, lbl)

        # status (compact, pinned at bottom)
        st_fr = ctk.CTkFrame(sb, fg_color="transparent")
        st_fr.pack(side="bottom", fill="x", padx=10, pady=(0, 8))
        ctk.CTkFrame(st_fr, height=1, fg_color=T.BORDER).pack(fill="x", pady=(0, 6))

        self._prog_bar = ctk.CTkProgressBar(st_fr, height=5, width=180,
                                             progress_color=T.BLUE, fg_color=T.BORDER,
                                             corner_radius=3)
        self._prog_bar.pack(fill="x", pady=(0, 3))
        self._prog_bar.set(0)
        self._prog_lbl = ctk.CTkLabel(st_fr, text="0%", font=T.F_CAP,
                                       text_color=T.TEXT_MUTED, anchor="w")
        self._prog_lbl.pack(fill="x", pady=(0, 3))

        row = ctk.CTkFrame(st_fr, fg_color="transparent")
        row.pack(fill="x")
        self._st_dot = ctk.CTkLabel(row, text="\u25cf", font=ctk.CTkFont(size=10),
                                     text_color=T.TEXT_MUTED, width=14)
        self._st_dot.pack(side="left")
        self._st_txt = ctk.CTkLabel(row, text="Конфиг не загружен", font=T.F_STATUS,
                                     text_color=T.TEXT_MUTED, anchor="w")
        self._st_txt.pack(side="left", padx=4)

        # separator line between sidebar & content
        ctk.CTkFrame(self, width=1, fg_color=T.BORDER, corner_radius=0).grid(
            row=1, column=0, sticky="nse")

        self._content = ctk.CTkFrame(self, fg_color=T.BG_PRIMARY, corner_radius=0)
        self._content.grid(row=1, column=1, sticky="nswe")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

    def _sep(self, parent):
        ctk.CTkFrame(parent, height=1, fg_color=T.BORDER).pack(fill="x", padx=14, pady=6)

    def _sec_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=T.F_SEC,
                     text_color=T.TEXT_MUTED, anchor="w").pack(
            fill="x", padx=18, pady=(1, 2))

    _PREFETCH_DELAY = 300
    _PAGE_DATA_LOADERS = {
        "modes":       lambda: get_modes(),
        "presets":     lambda: get_presets(),
        "compare":     lambda: get_presets(),
        "crosshair":   lambda: _load_json_safe("crosshair_presets.json"),
        "network":     lambda: _load_json_safe("network_presets.json"),
        "visual":      lambda: _load_json_safe("visual_presets.json"),
        "hardware":    lambda: get_hardware_data(),
        "keyboard":    lambda: _load_json_safe("keyboard_layouts.json"),
        "buyscript":   lambda: _load_json_safe("buyscripts.json"),
    }

    def _nav_btn(self, parent, key, text):
        btn = ctk.CTkButton(
            parent, text=text, font=ctk.CTkFont(size=12), height=32,
            corner_radius=T.NAV_R, fg_color="transparent",
            text_color=T.TEXT_SEC, hover_color=T.BG_TERTIARY,
            anchor="w", command=lambda k=key: self._nav(k),
        )
        btn.pack(fill="x", padx=6, pady=0)
        self._nav_btns[key] = btn
        btn.bind("<Enter>", lambda e, k=key: self._on_nav_hover_enter(k))
        btn.bind("<Leave>", lambda e, k=key: self._on_nav_hover_leave(k))

    def _on_nav_hover_enter(self, key):
        """Schedule data prefetch after hovering for _PREFETCH_DELAY ms."""
        if key == self._current_page_key:
            return
        self._debounce(f"_prefetch_{key}", self._PREFETCH_DELAY,
                       lambda k=key: self._prefetch_page_data(k))

    def _on_nav_hover_leave(self, key):
        """Cancel pending prefetch if hover ends early."""
        old = self._debounce_ids.pop(f"_prefetch_{key}", None)
        if old:
            self.after_cancel(old)

    def _prefetch_page_data(self, key):
        """Trigger background data loading for a page."""
        loader = self._PAGE_DATA_LOADERS.get(key)
        if loader:
            threading.Thread(target=loader, daemon=True).start()

    def _bind_hotkeys(self):
        nav_keys = {"1": "quick", "2": "modes", "3": "presets", "4": "network",
                    "5": "visual", "6": "crosshair", "7": "hardware", "8": "advanced"}
        for digit, page in nav_keys.items():
            self.bind(f"<Control-Key-{digit}>", lambda e, p=page: self._nav(p))
        self.bind("<Control-s>", lambda e: self._hotkey_save())
        self.bind("<Control-S>", lambda e: self._hotkey_save())
        self.bind("<Control-g>", lambda e: self._hotkey_gen())
        self.bind("<Control-G>", lambda e: self._hotkey_gen())
        self.bind("<Control-e>", lambda e: self._nav("export"))
        self.bind("<Control-i>", lambda e: self._nav("import"))
        self.bind("<Control-k>", lambda e: self._open_search())
        self.bind("<Control-K>", lambda e: self._open_search())
        self.bind("<F1>", lambda e: self._open_help())
        self.bind("<F12>", lambda e: self._toggle_debug())
        self.bind("<Control-z>", lambda e: self._do_undo())
        self.bind("<Control-Z>", lambda e: self._do_undo())
        self.bind("<Control-y>", lambda e: self._do_redo())
        self.bind("<Control-Y>", lambda e: self._do_redo())

    def _hotkey_save(self):
        if self.current_config:
            try:
                p = export_single_cfg(self.current_config)
                self._toast(f"Saved: {os.path.basename(p)}")
            except Exception as ex:
                self._toast(str(ex), "error")
        else:
            self._toast("Нет конфига для сохранения", "warning")

    def _hotkey_gen(self):
        self._nav("quick")

    def _open_search(self):
        if self._search_win and self._search_win.winfo_exists():
            self._search_win.destroy()
            self._search_win = None
            return
        self._search_win = SearchPalette(self, self._nav)

    def _open_help(self):
        HelpWindow(self)

    def _do_undo(self):
        change = self._undo.undo()
        if change:
            self._upd()
            self._toast(f"↶ Отмена: {change.description}", "info")
        else:
            self._toast("Нечего отменять", "warning")

    def _do_redo(self):
        change = self._undo.redo()
        if change:
            self._upd()
            self._toast(f"↷ Повтор: {change.description}", "info")
        else:
            self._toast("Нечего повторять", "warning")

    _PAGE_GC_INTERVAL = 60_000
    _PAGE_TTL = 300
    _HEAVY_PAGES = {
        "crosshair", "compare", "preview", "keyboard",
        "sensitivity", "diagnostics", "deploy", "buyscript",
        "advanced", "favorites", "export", "import",
        "profiles", "history", "templates", "demo",
    }

    # ────────────────────────────────────────────── navigation
    _HEAVY_PAGE_ATTRS = {
        "crosshair": ("_xh", "_xh_code", "_xh_color_btns", "_xh_auto_var"),
        "preview":   ("_pv_vars", "_pv_code", "_pv_count_lbl"),
        "deploy":    ("_dp_log", "_cl_vars", "_cl_result_lbl", "_cl_scan_result"),
        "keyboard":  (),
        "sensitivity": ("_sc_bar_fr",),
        "advanced":  ("_adv",),
    }

    def _nav(self, key):
        for k, b in self._nav_btns.items():
            if k == key:
                b.configure(fg_color=T.BLUE, text_color="#FFFFFF", hover_color=T.BLUE_HOVER)
            else:
                b.configure(fg_color="transparent", text_color=T.TEXT_SEC,
                            hover_color=T.BG_TERTIARY)

        self._cleanup_leaving_page()
        for w in self._content.winfo_children():
            w.destroy()

        self._prev_page_key = self._current_page_key
        self._current_page_key = key
        self._page_last_used[key] = time.time()
        if self._prev_page_key:
            self._page_last_used[self._prev_page_key] = time.time()

        pages = {
            "dashboard": self._p_dashboard,
            "quick": self._p_quick, "templates": self._p_templates,
            "favorites": self._p_favorites,
            "modes": self._p_modes,
            "presets": self._p_presets, "network": self._p_network,
            "visual": self._p_visual, "crosshair": self._p_crosshair,
            "hardware": self._p_hardware, "advanced": self._p_advanced,
            "export": self._p_export, "import": self._p_import,
            "compare": self._p_compare,
            "keyboard": self._p_keyboard, "buyscript": self._p_buyscript,
            "sensitivity": self._p_sensitivity, "diagnostics": self._p_diagnostics,
            "demo": self._p_demo,
            "profiles": self._p_profiles, "history": self._p_history,
            "deploy": self._p_deploy, "launch": self._p_launch,
            "preview": self._p_preview, "settings": self._p_settings,
        }

        build_fn = pages[key]
        if key in self._HEAVY_PAGES:
            skel = SkeletonScreen(self._content)
            skel.pack(fill="both", expand=True)
            self.update_idletasks()

            def _load_after_skeleton():
                if self._current_page_key != key:
                    return
                skel.destroy()
                build_fn()
            self.after(10, _load_after_skeleton)
        else:
            build_fn()

        if self._page_gc_id is None:
            self._page_gc_id = self.after(self._PAGE_GC_INTERVAL, self._gc_pages)

    def _cleanup_leaving_page(self):
        """Release heavy references and pooled vars when leaving a page."""
        leaving = self._current_page_key
        if not leaving:
            return
        if leaving == "crosshair" and hasattr(self, "_xh"):
            if hasattr(self._xh, "stop_auto_animate"):
                self._xh.stop_auto_animate()
            if hasattr(self._xh, "canvas"):
                self._xh.canvas.delete("all")
        attrs = self._HEAVY_PAGE_ATTRS.get(leaving, ())
        for attr in attrs:
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass
        var_pool.release_prefix(f"{leaving}_")

    def _gc_pages(self):
        """Garbage-collect stale page data references older than _PAGE_TTL."""
        now = time.time()
        keep = {self._current_page_key, self._prev_page_key}
        stale = [k for k, ts in self._page_last_used.items()
                 if k not in keep and now - ts > self._PAGE_TTL]
        for k in stale:
            self._page_last_used.pop(k, None)
            for attr in self._HEAVY_PAGE_ATTRS.get(k, ()):
                if hasattr(self, attr):
                    try:
                        delattr(self, attr)
                    except Exception:
                        pass
        self._page_gc_id = self.after(self._PAGE_GC_INTERVAL, self._gc_pages)

    def _upd(self):
        if self.current_config:
            c = self.current_config
            name = c.mode or c.preset_name or "Свой"
            self._st_dot.configure(text_color=T.GREEN)
            self._st_txt.configure(text=f"{name}  ({len(c.settings)} параметров)",
                                    text_color=T.TEXT_SEC)
            sections = [
                bool(c.settings), bool(c.binds), bool(c.mode_key),
                c.network_preset is not None, c.visual_preset is not None,
                c.crosshair_preset is not None,
                any(k.startswith("sensitivity") or k.startswith("m_") for k in c.settings),
                any(k.startswith("volume") or k.startswith("snd_") for k in c.settings),
                any(k.startswith("fps_") or k.startswith("gl_") for k in c.settings),
                any(k.startswith("rate") or k.startswith("cl_cmdrate") for k in c.settings),
            ]
            done = sum(sections)
            total = len(sections)
            pct = done / total
            self._prog_bar.set(pct)
            color = T.GREEN if pct >= 0.8 else T.BLUE if pct >= 0.4 else T.ORANGE
            self._prog_bar.configure(progress_color=color)
            self._prog_lbl.configure(text=f"{int(pct * 100)}%  ({done}/{total})")
        else:
            self._st_dot.configure(text_color=T.TEXT_MUTED)
            self._st_txt.configure(text="Конфиг не загружен", text_color=T.TEXT_MUTED)
            self._prog_bar.set(0)
            self._prog_lbl.configure(text="0%")

    def _toast(self, msg, kind="success"):
        Toast(self, msg, kind)

    # ────────────────────────────────────────────── ui helpers
    def _hdr(self, parent, title, sub=""):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=T.CONTENT_PX, pady=(T.CONTENT_PT, 0))
        ctk.CTkLabel(f, text=title, font=T.F_H1, text_color=T.TEXT).pack(anchor="w")
        if sub:
            ctk.CTkLabel(f, text=sub, font=T.F_BODY, text_color=T.TEXT_SEC).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(f, height=1, fg_color=T.BORDER).pack(fill="x", pady=(14, 0))

    def _card(self, parent, title="", grid=False, collapsible=False, **kw) -> ctk.CTkFrame:
        c = ctk.CTkFrame(parent, corner_radius=T.CARD_R, fg_color=T.BG_TERTIARY,
                         border_width=1, border_color=T.BORDER)
        c.pack(fill="x", padx=T.CONTENT_PX, pady=8, **kw)
        c.bind("<Enter>", lambda e: c.configure(border_color=T.BLUE_HOVER))
        c.bind("<Leave>", lambda e: c.configure(border_color=T.BORDER))

        body = ctk.CTkFrame(c, fg_color="transparent") if (title and (grid or collapsible)) else None

        if title:
            hdr = ctk.CTkFrame(c, fg_color="transparent")
            hdr.pack(fill="x", padx=T.CARD_PAD, pady=(T.CARD_PAD - 4, 0))
            ctk.CTkLabel(hdr, text=title, font=T.F_H2, text_color=T.TEXT).pack(side="left", anchor="w")
            if collapsible and body is not None:
                _collapsed = [False]
                toggle_lbl = ctk.CTkLabel(hdr, text="\u25bc", font=T.F_CAP,
                                           text_color=T.TEXT_MUTED, cursor="hand2")
                toggle_lbl.pack(side="right", padx=4)

                def _toggle(_e=None):
                    _collapsed[0] = not _collapsed[0]
                    if _collapsed[0]:
                        body.pack_forget()
                        toggle_lbl.configure(text="\u25b6")
                    else:
                        sep.pack(fill="x", padx=T.CARD_PAD, pady=(8, 0))
                        body.pack(fill="x")
                        toggle_lbl.configure(text="\u25bc")
                toggle_lbl.bind("<Button-1>", _toggle)

            sep = ctk.CTkFrame(c, height=1, fg_color=T.BORDER)
            sep.pack(fill="x", padx=T.CARD_PAD, pady=(8, 0))

        if body is not None:
            body.pack(fill="x")
            return body
        if grid:
            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(fill="x")
            return inner
        return c

    def _tip(self, widget, text: str):
        Tooltip(widget, text)

    def _slider_row(self, parent, label, from_, to, default, steps, fmt="{:.1f}", row=0):
        ctk.CTkLabel(parent, text=label, font=T.F_LABEL, text_color=T.TEXT,
                     width=130, anchor="w").grid(row=row, column=0, sticky="w", padx=(T.CARD_PAD, 8), pady=8)
        sf = ctk.CTkFrame(parent, fg_color="transparent")
        sf.grid(row=row, column=1, sticky="we", padx=(0, 8), pady=8)
        sf.grid_columnconfigure(0, weight=1)

        val_entry = ctk.CTkEntry(sf, width=60, height=30, corner_radius=6,
                                  fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                  font=T.F_VAL, justify="center")
        val_entry.pack(side="right", padx=(8, T.CARD_PAD))
        val_entry.insert(0, fmt.format(default))

        slider = ctk.CTkSlider(sf, from_=from_, to=to, number_of_steps=steps,
                                progress_color=T.BLUE, button_color="#FFFFFF",
                                button_hover_color=T.BLUE_HOVER)
        slider.set(default)
        slider.pack(side="left", fill="x", expand=True)

        def on_slide(v):
            val_entry.delete(0, "end")
            val_entry.insert(0, fmt.format(v))
        slider.configure(command=on_slide)

        def on_entry(e=None):
            try:
                v = float(val_entry.get())
                v = max(from_, min(to, v))
                slider.set(v)
            except ValueError:
                pass
        val_entry.bind("<Return>", on_entry)
        val_entry.bind("<FocusOut>", on_entry)

        return slider, val_entry

    def _action_btn(self, parent, text, command, color=None, **kw):
        fg = color or T.GREEN
        hv = T.GREEN_HOVER if fg == T.GREEN else T.BLUE_HOVER
        return ctk.CTkButton(parent, text=text, font=T.F_BTN, height=48,
                              corner_radius=T.BTN_R, fg_color=fg, hover_color=hv,
                              command=command, **kw)

    def _ensure(self):
        if not self.current_config:
            self.current_config = create_mode_config("classic")
            self._upd()

    # ═══════════════════════════════════════════════ DASHBOARD
    def _p_dashboard(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)

        # welcome header
        wf = ctk.CTkFrame(fr, fg_color="transparent")
        wf.pack(fill="x", padx=T.CONTENT_PX, pady=(T.CONTENT_PT, 0))
        ctk.CTkLabel(wf, text="Добро пожаловать!", font=T.F_H1,
                     text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(wf, text="GoldSrc Config Engineer — профессиональный генератор конфигов CS 1.6",
                     font=T.F_BODY, text_color=T.TEXT_SEC).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(wf, height=1, fg_color=T.BORDER).pack(fill="x", pady=(14, 0))

        # quick actions
        qa = self._card(fr, "⚡  Быстрые действия")
        qa_row = ctk.CTkFrame(qa, fg_color="transparent")
        qa_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        qa_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        actions = [
            ("⚡ Быстрая\nнастройка", T.GREEN, T.GREEN_HOVER, lambda: self._nav("quick")),
            ("📥 Импорт\nконфига", T.BLUE, T.BLUE_HOVER, lambda: self._nav("import")),
            ("📤 Экспорт\nконфига", T.ORANGE, "#E8A840", lambda: self._nav("export")),
            ("⭐ Про-пресеты", "#8B5CF6", "#7C3AED", lambda: self._nav("presets")),
        ]
        for i, (txt, fg, hv, cmd) in enumerate(actions):
            ctk.CTkButton(qa_row, text=txt, height=64, corner_radius=T.BTN_R,
                          fg_color=fg, hover_color=hv,
                          font=ctk.CTkFont(size=13, weight="bold"),
                          command=cmd).grid(row=0, column=i, padx=4, sticky="we")

        # current profile card
        cp = self._card(fr, "📋  Текущий конфиг")
        if self.current_config:
            cfg = self.current_config
            name = cfg.preset_name or cfg.mode or "Пользовательский"
            info_fr = ctk.CTkFrame(cp, fg_color="transparent")
            info_fr.pack(fill="x", padx=T.CARD_PAD, pady=(8, 4))
            info_fr.grid_columnconfigure(1, weight=1)

            pairs = [
                ("Профиль:", name),
                ("Параметры:", f"{len(cfg.settings)} cvar"),
                ("Бинды:", f"{len(cfg.binds)} + {len(cfg.buy_binds)} buy"),
                ("Режим:", cfg.mode or "—"),
                ("Сеть:", cfg.network_preset or "—"),
            ]
            for r, (lbl, val) in enumerate(pairs):
                ctk.CTkLabel(info_fr, text=lbl, font=T.F_LABEL,
                             text_color=T.TEXT_MUTED, anchor="w", width=100).grid(
                    row=r, column=0, sticky="w", pady=1)
                ctk.CTkLabel(info_fr, text=val, font=T.F_LABEL,
                             text_color=T.TEXT, anchor="w").grid(
                    row=r, column=1, sticky="w", padx=(4, 0), pady=1)

            btn_fr = ctk.CTkFrame(cp, fg_color="transparent")
            btn_fr.pack(fill="x", padx=T.CARD_PAD, pady=(4, T.CARD_PAD))
            ctk.CTkButton(btn_fr, text="Редактировать", width=130, height=32,
                          corner_radius=T.BTN_R, fg_color=T.BLUE,
                          hover_color=T.BLUE_HOVER, font=T.F_CAP,
                          command=lambda: self._nav("advanced")).pack(side="left", padx=(0, 4))
            ctk.CTkButton(btn_fr, text="Экспорт", width=100, height=32,
                          corner_radius=T.BTN_R, fg_color=T.GREEN,
                          hover_color=T.GREEN_HOVER, font=T.F_CAP,
                          command=lambda: self._nav("export")).pack(side="left", padx=(0, 4))
            ctk.CTkButton(btn_fr, text="Диагностика", width=120, height=32,
                          corner_radius=T.BTN_R, fg_color=T.ORANGE,
                          hover_color="#E8A840", font=T.F_CAP,
                          command=lambda: self._nav("diagnostics")).pack(side="left")
        else:
            ctk.CTkLabel(cp, text="Конфиг ещё не создан. Начните с быстрой настройки или импорта.",
                         font=T.F_BODY, text_color=T.TEXT_MUTED).pack(
                padx=T.CARD_PAD, pady=T.CARD_PAD)

        # recent history
        hc = self._card(fr, "🕐  Последние конфиги")
        history = list_history()[:5]
        if history:
            for item in history:
                rf = ctk.CTkFrame(hc, fg_color="transparent")
                rf.pack(fill="x", padx=T.CARD_PAD, pady=2)
                ctk.CTkLabel(rf, text=f"📄  {item.get('label', 'snapshot')}",
                             font=T.F_CAP, text_color=T.TEXT, anchor="w").pack(
                    side="left")
                ctk.CTkLabel(rf, text=item.get("date", ""),
                             font=T.F_CAP, text_color=T.TEXT_MUTED).pack(
                    side="right", padx=(8, 0))
            ctk.CTkFrame(hc, height=4, fg_color="transparent").pack()
        else:
            ctk.CTkLabel(hc, text="История пуста", font=T.F_CAP,
                         text_color=T.TEXT_MUTED).pack(padx=T.CARD_PAD, pady=T.CARD_PAD)

        # tips
        tc = self._card(fr, "💡  Советы")
        import random
        tips = [
            "Большинство про-игроков CS 1.6 используют sensitivity от 1.5 до 3.5",
            "m_rawinput 1 — обязательно для точного прицеливания",
            "fps_max 101 — оптимальное значение для серверов с tickrate 100",
            "cl_cmdrate и cl_updaterate 101 — стандарт для соревновательной игры",
            "ex_interp 0.01 — минимизирует интерполяцию для LAN",
            "hud_fastswitch 1 — моментальное переключение оружия без лишнего клика",
            "Используйте Ctrl+S для быстрого сохранения конфига",
            "Страница «Диагностика» проверит ваш конфиг на типичные ошибки",
            "Вы можете загрузить конфиг прямо в запущенную CS 1.6 через «Загрузка в игру»",
            "Визуальный редактор прицела позволяет настроить crosshair без запуска игры",
        ]
        ctk.CTkLabel(tc, text=f"  {random.choice(tips)}",
                     font=T.F_LABEL, text_color=T.TEXT_SEC,
                     wraplength=600).pack(padx=T.CARD_PAD, pady=T.CARD_PAD, anchor="w")

    # ═══════════════════════════════════════════════ QUICK SETUP
    def _p_quick(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\u26a1 Быстрая настройка", "Создайте конфиг в один клик    (Ctrl+G)")

        # Game Settings card
        c1 = self._card(fr, "\U0001f3af  Настройки игры", grid=True, collapsible=True)
        c1.grid_columnconfigure(1, weight=1)
        modes = get_modes()
        mk = list(modes.keys())
        ml = [modes[k].get("name_ru", k) for k in mk]
        lbl_gm = ctk.CTkLabel(c1, text="Game Mode", font=T.F_LABEL, text_color=T.TEXT,
                     width=130, anchor="w")
        lbl_gm.grid(row=0, column=0, sticky="w", padx=(T.CARD_PAD, 8), pady=(T.CARD_PAD, 8))
        self._tip(lbl_gm, "Select game mode (classic, kz, surf...)")
        self._q_mode = ctk.CTkComboBox(c1, values=ml, width=280, state="readonly",
                                        corner_radius=T.INPUT_R, fg_color=T.BG_TERTIARY,
                                        border_color=T.BORDER, button_color=T.BORDER,
                                        dropdown_fg_color=T.BG_TERTIARY)
        self._q_mode.grid(row=0, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=(T.CARD_PAD, 8))
        self._q_mode.set(ml[0])
        self._q_mk = mk

        # Controls card
        c2 = self._card(fr, "\U0001f5b1  Управление", grid=True, collapsible=True)
        c2.grid_columnconfigure(1, weight=1)
        self._q_sens, self._q_sens_e = self._slider_row(c2, "Sensitivity", 0.5, 10, 2.5, 190, row=0)
        self._tip(self._q_sens, "Mouse sensitivity (lower = more precise)")

        # Performance card
        c3 = self._card(fr, "\U0001f3ae  Производительность", grid=True, collapsible=True)
        c3.grid_columnconfigure(1, weight=1)
        self._q_fps, self._q_fps_e = self._slider_row(c3, "fps_max", 20, 1000, 100, 98, fmt="{:.0f}", row=0)
        self._tip(self._q_fps, "Max FPS (100 = standard, 999 = unlimited)")

        # Audio card
        c4 = self._card(fr, "\U0001f50a  Звук", grid=True, collapsible=True)
        c4.grid_columnconfigure(1, weight=1)
        self._q_vol, self._q_vol_e = self._slider_row(c4, "Volume", 0, 1, 0.7, 20, row=0)
        self._tip(self._q_vol, "Master volume (0 = mute, 1 = full)")

        # Generate button
        bf = ctk.CTkFrame(fr, fg_color="transparent")
        bf.pack(fill="x", padx=T.CONTENT_PX, pady=(12, 20))
        self._q_btn = self._action_btn(bf, "\u26a1  Создать конфиг", self._do_quick)
        self._q_btn.pack(fill="x")
        self._tip(self._q_btn, "Generate config with current settings  (Ctrl+G)")

    def _do_quick(self):
        self._q_btn.configure(text="\u23f3  Создание...", state="disabled")
        self.update_idletasks()

        txt = self._q_mode.get()
        modes = get_modes()
        idx = 0
        for i, k in enumerate(self._q_mk):
            if modes[k].get("name_ru", k) == txt:
                idx = i
                break

        try:
            sens = float(self._q_sens_e.get())
        except ValueError:
            sens = self._q_sens.get()
        try:
            fps = int(float(self._q_fps_e.get()))
        except ValueError:
            fps = int(self._q_fps.get())
        try:
            vol = float(self._q_vol_e.get())
        except ValueError:
            vol = self._q_vol.get()

        self.current_config = create_quick_config(
            self._q_mk[idx], round(sens, 1), fps, round(vol, 1))
        save_history_snapshot(self.current_config, f"quick_{self._q_mk[idx]}")
        log.info(f"Quick config: mode={self._q_mk[idx]}, sens={sens}, fps={fps}, vol={vol}")
        self._upd()
        self._q_btn.configure(text="\u2705  Конфиг создан!", state="normal",
                              fg_color=T.BLUE)
        self._toast(f"Config: {len(self.current_config.settings)} cvars, "
                    f"{len(self.current_config.binds)} binds")
        self.after(2000, lambda: self._q_btn.configure(text="\u26a1  Создать конфиг",
                                                        fg_color=T.GREEN))
        self._pulse_btn(self._q_btn, 0)

    def _pulse_btn(self, btn, step):
        colors = [T.GREEN, T.GREEN_HOVER, T.GREEN, T.GREEN_HOVER, T.GREEN]
        if step < len(colors):
            btn.configure(fg_color=colors[step])
            self.after(120, lambda: self._pulse_btn(btn, step + 1))

    # ═══════════════════════════════════════════════ TEMPLATES
    def _p_templates(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "📋 Шаблоны конфигов",
                  "Начните с готового шаблона — предзаполняет все настройки, бинды и режим")

        templates = get_templates()
        for tkey, tpl in templates.items():
            icon = tpl.get("icon", "📋")
            name_ru = tpl.get("name_ru", tpl.get("name", tkey))
            desc = tpl.get("description_ru", "")

            c = self._card(fr, f"{icon}  {name_ru}")
            ctk.CTkLabel(c, text=desc, font=T.F_CAP, text_color=T.TEXT_SEC,
                         wraplength=500, justify="left").pack(
                anchor="w", padx=T.CARD_PAD, pady=(0, 4))

            info_row = ctk.CTkFrame(c, fg_color="transparent")
            info_row.pack(fill="x", padx=T.CARD_PAD, pady=(0, 4))
            settings = tpl.get("settings", {})
            binds = tpl.get("binds", {})
            mode = tpl.get("mode", "—")
            ctk.CTkLabel(info_row, text=f"⚙ {len(settings)} CVAR  |  🎮 {len(binds)} биндов  |  📂 {mode}",
                         font=T.F_CAP, text_color=T.TEXT_MUTED).pack(side="left")

            ctk.CTkButton(c, text="Применить шаблон", height=34, corner_radius=T.BTN_R,
                          fg_color=T.GREEN, hover_color=T.GREEN_HOVER, font=T.F_LABEL,
                          command=lambda k=tkey: self._apply_template(k)).pack(
                padx=T.CARD_PAD, pady=(0, T.CARD_PAD), anchor="w")

    def _apply_template(self, key: str):
        templates = get_templates()
        tpl = templates.get(key)
        if not tpl:
            return
        cfg = CfgConfig()
        for k, v in tpl.get("settings", {}).items():
            cfg.settings[k] = v
        for k, v in tpl.get("binds", {}).items():
            cfg.binds[k] = v
        cfg.mode = tpl.get("mode")
        cfg.mode_key = tpl.get("mode")
        cfg.description = tpl.get("name_ru", tpl.get("name", key))
        self.current_config = cfg
        self._upd()
        self._toast(f"Шаблон «{tpl.get('name_ru', key)}» применён")
        self._nav("export")

    # ═══════════════════════════════════════════════ FAVORITES
    def _p_favorites(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "⭐ Избранные параметры",
                  "Быстрый доступ к отмеченным CVAR — нажмите ⭐ чтобы добавить")

        if not hasattr(self, "_fav_cvars"):
            self._fav_cvars: set[str] = set()

        if not self.current_config:
            c = self._card(fr)
            ctk.CTkLabel(c, text="Конфиг не загружен. Сначала создайте его.",
                         font=T.F_BODY, text_color=T.ORANGE).pack(
                padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        all_cvars = get_all_cvars()
        desc_map: dict[str, str] = {}
        for cat_data in all_cvars.values():
            for cn, ci in cat_data.items():
                desc_map[cn] = ci.get("description_ru", ci.get("description_en", ""))
        # Add all button
        add_c = self._card(fr, "🔍  Добавить в избранное")
        add_row = ctk.CTkFrame(add_c, fg_color="transparent")
        add_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        self._fav_search = ctk.CTkEntry(add_row, placeholder_text="Введите имя CVAR...",
                                         width=300, corner_radius=T.INPUT_R,
                                         fg_color=T.BG_PRIMARY, border_color=T.BORDER)
        self._fav_search.pack(side="left", padx=(0, 6))
        ctk.CTkButton(add_row, text="⭐ Добавить", width=100, height=32,
                      corner_radius=T.BTN_R, fg_color=T.ORANGE, hover_color="#E5A82E",
                      command=self._fav_add_from_search).pack(side="left")

        if not self._fav_cvars:
            c = self._card(fr, "💡  Подсказка")
            ctk.CTkLabel(c, text="Избранное пусто. Введите имя CVAR выше или\n"
                                 "перейдите в «Расширенные» и нажмите ⭐ рядом с параметром.",
                         font=T.F_BODY, text_color=T.TEXT_MUTED, wraplength=500,
                         justify="left").pack(padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        fc = self._card(fr, f"⭐  Избранные ({len(self._fav_cvars)})")
        self._ui_chunk_gen = getattr(self, "_ui_chunk_gen", 0) + 1
        _fav_gen = self._ui_chunk_gen
        fav_sorted = sorted(self._fav_cvars)

        def _fav_row(cvar_name: str, _idx: int):
            if _fav_gen != self._ui_chunk_gen:
                return
            row = ctk.CTkFrame(fc, fg_color="transparent")
            row.pack(fill="x", padx=T.CARD_PAD, pady=2)
            ctk.CTkLabel(row, text=cvar_name, font=T.F_MONO, text_color=T.TEXT,
                         width=180, anchor="w").pack(side="left")
            val = self.current_config.settings.get(cvar_name, "—")
            ent = ctk.CTkEntry(row, width=120, corner_radius=T.INPUT_R,
                                fg_color=T.BG_PRIMARY, border_color=T.BORDER)
            ent.pack(side="left", padx=(6, 0))
            ent.insert(0, val)
            ctk.CTkButton(row, text="✓", width=30, height=26, corner_radius=6,
                          fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                          command=lambda n=cvar_name, e=ent: self._fav_set(n, e)).pack(
                side="left", padx=(4, 0))
            ctk.CTkButton(row, text="✕", width=30, height=26, corner_radius=6,
                          fg_color=T.RED, hover_color="#D32F2F",
                          command=lambda n=cvar_name: self._fav_remove(n)).pack(
                side="left", padx=(2, 0))
            desc = desc_map.get(cvar_name, "")
            if desc:
                ctk.CTkLabel(row, text=desc[:50], font=ctk.CTkFont(size=10),
                             text_color=T.TEXT_MUTED).pack(side="left", padx=(8, 0))

        self._ui_chunked(fav_sorted, 16, _fav_row, cancel_gen=_fav_gen)

    def _fav_add_from_search(self):
        name = self._fav_search.get().strip()
        if name:
            self._fav_cvars.add(name)
            self._nav("favorites")
            self._toast(f"⭐ {name} добавлен в избранное")

    def _fav_set(self, name: str, entry):
        val = entry.get().strip()
        if val and self.current_config:
            old = self.current_config.settings.get(name)
            self.current_config.settings[name] = val
            self._undo.record_set(name, old, val)
            self._toast(f"{name} = {val}")

    def _fav_remove(self, name: str):
        self._fav_cvars.discard(name)
        self._nav("favorites")
        self._toast(f"Убрано из избранного: {name}")

    # ═══════════════════════════════════════════════ MODES
    def _p_modes(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f3ae Режимы игры", "Выберите режим с оптимизированными настройками")

        for key, data in get_modes().items():
            c = self._card(fr)
            c.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(c, text=data.get("name_ru", key), font=T.F_H2,
                         text_color=T.TEXT).grid(row=0, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(T.CARD_PAD, 0))
            ctk.CTkLabel(c, text=data.get("description_ru", ""), font=T.F_CAP,
                         text_color=T.TEXT_SEC, wraplength=500).grid(
                row=1, column=0, sticky="w", padx=T.CARD_PAD, pady=(4, T.CARD_PAD))
            ctk.CTkButton(c, text="Загрузить", width=90, height=34, corner_radius=T.BTN_R,
                          fg_color=T.BLUE, hover_color=T.BLUE_HOVER, font=T.F_LABEL,
                          command=lambda k=key: self._load_mode(k)).grid(
                row=0, column=1, rowspan=2, padx=T.CARD_PAD, pady=T.CARD_PAD, sticky="e")

    def _load_mode(self, k):
        self.current_config = create_mode_config(k)
        log.info(f"Mode loaded: {k}")
        self._upd()
        self._toast(f"{get_modes()[k].get('name_ru', k)} — {len(self.current_config.settings)} cvars")

    # ═══════════════════════════════════════════════ PRESETS
    def _p_presets(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\u2b50 Про-пресеты", "Загрузите конфиг легендарных игроков")

        for key, d in get_presets().items():
            c = self._card(fr)
            c.grid_columnconfigure(1, weight=1)
            s = d.get("settings", {})
            ctk.CTkLabel(c, text=d.get("name", key), font=T.F_H2,
                         text_color=T.TEXT).grid(row=0, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(T.CARD_PAD, 0))
            info = f"{d.get('team','')}  \u2502  {d.get('role','')}  \u2502  sens: {s.get('sensitivity','?')}  \u2502  fps: {s.get('fps_max','?')}"
            ctk.CTkLabel(c, text=info, font=T.F_CAP, text_color=T.TEXT_SEC).grid(
                row=1, column=0, sticky="w", padx=T.CARD_PAD, pady=(2, 0))
            ctk.CTkLabel(c, text=d.get("description_ru", ""), font=T.F_CAP,
                         text_color=T.TEXT_MUTED).grid(
                row=2, column=0, sticky="w", padx=T.CARD_PAD, pady=(2, T.CARD_PAD))
            ctk.CTkButton(c, text="Загрузить", width=90, height=34, corner_radius=T.BTN_R,
                          fg_color=T.BLUE, hover_color=T.BLUE_HOVER, font=T.F_LABEL,
                          command=lambda k=key: self._load_preset(k)).grid(
                row=0, column=1, rowspan=3, padx=T.CARD_PAD, pady=T.CARD_PAD, sticky="e")

    def _load_preset(self, k):
        self.current_config = create_preset_config(k)
        log.info(f"Preset loaded: {k}")
        self._upd()
        self._toast(f"{get_presets()[k].get('name', k)} loaded")

    # ═══════════════════════════════════════════════ NETWORK
    def _p_network(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f310 Сетевые настройки", "Оптимизируйте rate для вашего подключения")
        self._ensure()

        for key, d in get_network_presets().items():
            c = self._card(fr)
            c.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(c, text=f"{d['name']}  ({d['ping_range']} ms)", font=T.F_H2,
                         text_color=T.TEXT).grid(row=0, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(T.CARD_PAD, 0))
            ctk.CTkLabel(c, text=d.get("description", ""), font=T.F_CAP,
                         text_color=T.TEXT_SEC).grid(row=1, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(2, 0))
            vals = "  ".join(f"{k}={v}" for k, v in d.get("settings", {}).items())
            ctk.CTkLabel(c, text=vals, font=T.F_MONO, text_color=T.TEXT_MUTED,
                         wraplength=500).grid(row=2, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(4, T.CARD_PAD))
            ctk.CTkButton(c, text="Применить", width=90, height=34, corner_radius=T.BTN_R,
                          fg_color=T.GREEN, hover_color=T.GREEN_HOVER, font=T.F_LABEL,
                          command=lambda k=key: self._apply_net(k)).grid(
                row=0, column=1, rowspan=3, padx=T.CARD_PAD, pady=T.CARD_PAD, sticky="e")

    def _apply_net(self, k):
        self._ensure()
        apply_network_preset(self.current_config, k)
        self._upd()
        self._toast(f"Network preset '{k}' applied")

    # ═══════════════════════════════════════════════ VISUAL
    def _p_visual(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f5bc Графические пресеты", "Настройки рендеринга для вашего сценария")
        self._ensure()

        for key, d in get_visual_presets().items():
            c = self._card(fr)
            c.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(c, text=d.get("name", key), font=T.F_H2,
                         text_color=T.TEXT).grid(row=0, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(T.CARD_PAD, 0))
            ctk.CTkLabel(c, text=d.get("description", ""), font=T.F_CAP,
                         text_color=T.TEXT_SEC).grid(row=1, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(2, 0))
            n = len(d.get("settings", {}))
            ctk.CTkLabel(c, text=f"{n} settings", font=T.F_CAP,
                         text_color=T.TEXT_MUTED).grid(row=2, column=0, sticky="w",
                         padx=T.CARD_PAD, pady=(2, T.CARD_PAD))
            ctk.CTkButton(c, text="Применить", width=90, height=34, corner_radius=T.BTN_R,
                          fg_color=T.GREEN, hover_color=T.GREEN_HOVER, font=T.F_LABEL,
                          command=lambda k=key: self._apply_vis(k)).grid(
                row=0, column=1, rowspan=3, padx=T.CARD_PAD, pady=T.CARD_PAD, sticky="e")

    def _apply_vis(self, k):
        self._ensure()
        apply_visual_preset(self.current_config, k)
        self._upd()
        self._toast(f"Visual preset '{k}' applied")

    # _p_crosshair + _xh_* → pages/crosshair_page.py (CrosshairPageMixin)

    # ═══════════════════════════════════════════════ HARDWARE
    def _p_hardware(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f5a5 Оптимизация оборудования", "Настройки для вашей видеокарты и цели производительности")
        self._ensure()

        hw = get_hardware_data()
        gk = list(hw.get("gpu_vendor", {}).keys())
        gl = [hw["gpu_vendor"][v].get("name_ru", v) for v in gk]
        pk = list(hw.get("performance_profiles", {}).keys())
        pl = [hw["performance_profiles"][p].get("name_ru", p) for p in pk]

        c = self._card(fr, "\u2699  Settings", grid=True, collapsible=True)
        c.grid_columnconfigure(1, weight=1)

        lbl_gpu = ctk.CTkLabel(c, text="GPU Vendor", font=T.F_LABEL, text_color=T.TEXT,
                     width=130, anchor="w")
        lbl_gpu.grid(row=0, column=0, sticky="w", padx=(T.CARD_PAD, 8), pady=(T.CARD_PAD, 8))
        self._tip(lbl_gpu, "Select your GPU manufacturer for specific optimizations")
        self._hw_gpu = ctk.CTkComboBox(c, values=gl, width=260, state="readonly",
                                        corner_radius=T.INPUT_R, fg_color=T.BG_TERTIARY,
                                        border_color=T.BORDER)
        self._hw_gpu.grid(row=0, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=(T.CARD_PAD, 8))
        self._hw_gpu.set(gl[0])
        self._hw_gk = gk

        ctk.CTkLabel(c, text="Performance", font=T.F_LABEL, text_color=T.TEXT,
                     width=130, anchor="w").grid(row=1, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=8)
        self._hw_prof = ctk.CTkComboBox(c, values=pl, width=260, state="readonly",
                                         corner_radius=T.INPUT_R, fg_color=T.BG_TERTIARY,
                                         border_color=T.BORDER)
        self._hw_prof.grid(row=1, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=8)
        self._hw_prof.set(pl[2] if len(pl) > 2 else pl[0])
        self._hw_pk = pk

        btn = self._action_btn(c, "\u26a1  Apply Optimization", self._do_hw)
        btn.grid(row=2, column=0, columnspan=2, padx=T.CARD_PAD,
                 pady=(8, T.CARD_PAD), sticky="we")

        self._hw_tips = ctk.CTkFrame(fr, fg_color="transparent")
        self._hw_tips.pack(fill="x", padx=T.CONTENT_PX, pady=(0, 16))

    def _do_hw(self):
        self._ensure()
        hw = get_hardware_data()
        gt = self._hw_gpu.get()
        gk = self._hw_gk[0]
        for k in self._hw_gk:
            if hw["gpu_vendor"][k].get("name_ru", k) == gt:
                gk = k
                break
        pt = self._hw_prof.get()
        ppk = self._hw_pk[0]
        for k in self._hw_pk:
            if hw["performance_profiles"][k].get("name_ru", k) == pt:
                ppk = k
                break
        self.current_config, tips, launch = optimize_config(self.current_config, gk, ppk)
        self._upd()
        for w in self._hw_tips.winfo_children():
            w.destroy()
        if tips:
            tc = self._card(self._hw_tips, "\U0001f4a1  Tips")
            for t in tips:
                ctk.CTkLabel(tc, text=f"  \u2022  {t}", font=T.F_CAP,
                             text_color=T.TEXT_SEC, wraplength=550, anchor="w").pack(
                    anchor="w", padx=T.CARD_PAD, pady=2)
            ctk.CTkFrame(tc, height=4, fg_color="transparent").pack()
        if launch:
            lc = self._card(self._hw_tips, "\U0001f680  Launch Options")
            e = ctk.CTkEntry(lc, width=500, fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                             corner_radius=T.INPUT_R, font=T.F_MONO)
            e.pack(padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
            e.insert(0, launch)
            e.configure(state="readonly")
        self._toast("Hardware optimization applied")

    # ═══════════════════════════════════════════════ ADVANCED
    def _p_advanced(self):
        fr = ctk.CTkFrame(self._content, fg_color=T.BG_PRIMARY)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\u2699 Расширенные настройки", "Тонкая настройка каждого параметра CVAR")
        self._ensure()

        tabs = ctk.CTkTabview(fr, fg_color=T.BG_TERTIARY, segmented_button_fg_color=T.BG_SECONDARY,
                               segmented_button_selected_color=T.BLUE,
                               segmented_button_unselected_color=T.BG_SECONDARY)
        tabs.pack(fill="both", expand=True, padx=T.CONTENT_PX, pady=(12, 4))

        cvars = get_all_cvars()
        cats = {"video": "Video", "audio": "Audio", "input": "Mouse",
                "network": "Network", "gameplay": "Gameplay"}
        self._adv: dict[str, ctk.CTkEntry] = {}

        self._ui_chunk_gen = getattr(self, "_ui_chunk_gen", 0) + 1
        _gen = self._ui_chunk_gen
        cat_list = list(cats.items())

        def adv_row(sc, i: int, cn: str, ci: dict):
            desc = ci.get("description_ru", ci.get("description_en", ""))
            cv = self.current_config.get(cn, ci.get("default", ""))
            hint = ""
            if "range" in ci:
                hint = f"  [{ci['range'][0]}—{ci['range'][1]}]"
            elif "values" in ci:
                hint = f"  ({', '.join(ci['values'])})"
            ctk.CTkLabel(sc, text=cn, font=T.F_LABEL, text_color=T.TEXT).grid(
                row=i, column=0, sticky="w", padx=(12, 4), pady=3)
            e = ctk.CTkEntry(sc, width=110, height=30, corner_radius=6,
                              fg_color=T.BG_PRIMARY, border_color=T.BORDER, font=T.F_VAL)
            e.grid(row=i, column=1, sticky="w", padx=4, pady=3)
            e.insert(0, cv)
            self._adv[cn] = e
            ctk.CTkLabel(sc, text=f"{desc}{hint}", font=T.F_CAP,
                         text_color=T.TEXT_MUTED).grid(row=i, column=2, sticky="w",
                         padx=(8, 12), pady=3)

        def fill_cat(ci: int):
            if ci >= len(cat_list) or _gen != self._ui_chunk_gen:
                return
            ck, cl = cat_list[ci]
            tab = tabs.add(cl)
            sc = ctk.CTkScrollableFrame(tab, fg_color="transparent", **SCROLLBAR_KW)
            sc.pack(fill="both", expand=True)
            sc.grid_columnconfigure(1, weight=1)
            pairs = list(cvars.get(ck, {}).items())

            def one(pair, row_idx):
                cn, cinfo = pair
                adv_row(sc, row_idx, cn, cinfo)

            self._ui_chunked(
                pairs, 22, one,
                on_done=lambda: fill_cat(ci + 1),
                cancel_gen=_gen,
            )

        fill_cat(0)

        bf = ctk.CTkFrame(fr, fg_color="transparent")
        bf.pack(fill="x", padx=T.CONTENT_PX, pady=(2, 12))
        ctk.CTkButton(bf, text="\u2705  Apply", height=40, corner_radius=T.BTN_R,
                      fg_color=T.GREEN, hover_color=T.GREEN_HOVER, font=T.F_LABEL,
                      command=self._adv_apply).pack(side="left", padx=(0, 8))
        ctk.CTkButton(bf, text="\U0001f50d  Validate", height=40, corner_radius=T.BTN_R,
                      fg_color=T.BLUE, hover_color=T.BLUE_HOVER, font=T.F_LABEL,
                      command=self._adv_val).pack(side="left")

    def _adv_apply(self):
        for cn, e in self._adv.items():
            v = e.get().strip()
            if v:
                self.current_config.set(cn, v)
        self._upd()
        self._toast(f"{len(self._adv)} parameters applied")

    def _adv_val(self):
        self._adv_apply()
        r = validate_config_dict(self.current_config.settings)
        if r.is_valid and not r.warnings:
            self._toast(f"Validation OK: {r.valid_count}/{r.total_count} valid")
        else:
            parts = [f"Checked: {r.total_count}, Valid: {r.valid_count}"]
            if r.warnings:
                parts.append("Warnings:\n" + "\n".join(f"  ! {w}" for w in r.warnings))
            if r.errors:
                parts.append("Errors:\n" + "\n".join(f"  X {e}" for e in r.errors))
            messagebox.showwarning("Validation", "\n".join(parts))

    # ═══════════════════════════════════════════════ EXPORT
    def _p_export(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f4e4 Экспорт конфига", "Предпросмотр и сохранение .cfg файлов")

        if not self.current_config:
            c = self._card(fr)
            ctk.CTkLabel(c, text="Конфиг не загружен.\nИспользуйте Быструю настройку, Режимы или Пресеты.",
                         font=T.F_BODY, text_color=T.ORANGE).pack(padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        c = self._card(fr, "\U0001f4be  Параметры сохранения", grid=True)
        c.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(c, text="Имя файла:", font=T.F_LABEL, text_color=T.TEXT).grid(
            row=0, column=0, sticky="e", padx=(T.CARD_PAD, 4), pady=(T.CARD_PAD, 8))
        self._exp_fn = ctk.CTkEntry(c, width=200, corner_radius=T.INPUT_R,
                                     fg_color=T.BG_PRIMARY, border_color=T.BORDER)
        self._exp_fn.grid(row=0, column=1, sticky="w", padx=4, pady=(T.CARD_PAD, 8))
        self._exp_fn.insert(0, "autoexec.cfg")
        self._btn_exp_single = ctk.CTkButton(c, text="Сохранить .cfg", height=36,
                      corner_radius=T.BTN_R, fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                      font=T.F_LABEL, command=self._exp_single)
        self._btn_exp_single.grid(row=0, column=2, padx=(4, T.CARD_PAD),
                      pady=(T.CARD_PAD, 8), sticky="w")

        self._btn_exp_full = ctk.CTkButton(c, text="\U0001f4c1  Сохранить полный набор (GoldSrc v3.0)",
                      height=40, corner_radius=T.BTN_R, fg_color=T.BLUE,
                      hover_color=T.BLUE_HOVER, font=T.F_LABEL, command=self._exp_full)
        self._btn_exp_full.grid(
            row=1, column=0, columnspan=3, padx=T.CARD_PAD, pady=(0, 4), sticky="we")

        ctk.CTkButton(c, text="\U0001f4be  Сохранить как...", height=36, corner_radius=T.BTN_R,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER, font=T.F_LABEL,
                      command=self._exp_saveas).grid(
            row=2, column=0, columnspan=3, padx=T.CARD_PAD, pady=(0, 4), sticky="we")
        ctk.CTkButton(c, text="📦  Пакетный экспорт всех профилей", height=36,
                      corner_radius=T.BTN_R, fg_color=T.ORANGE, hover_color="#E5A82E",
                      font=T.F_LABEL, command=self._exp_batch).grid(
            row=3, column=0, columnspan=3, padx=T.CARD_PAD, pady=(0, T.CARD_PAD), sticky="we")

        ctk.CTkLabel(fr, text="Предпросмотр", font=T.F_H2, text_color=T.TEXT).pack(
            anchor="w", padx=T.CONTENT_PX + 4, pady=(10, 4))
        tb = ctk.CTkTextbox(fr, font=T.F_MONO, fg_color=T.BG_TERTIARY,
                             border_width=1, border_color=T.BORDER, corner_radius=T.CARD_R,
                             wrap="none", height=300)
        tb.pack(fill="both", expand=True, padx=T.CONTENT_PX, pady=(0, 16))
        tb.insert("1.0", generate_single_cfg(self.current_config))
        tb.configure(state="disabled")

    def _exp_single(self):
        fn = self._exp_fn.get().strip() or "autoexec.cfg"
        btn = getattr(self, "_btn_exp_single", None)
        if btn:
            btn.configure(text="⏳ Сохранение...", state="disabled")
            self.update_idletasks()

        def _finish():
            try:
                p = export_single_cfg(self.current_config, fn)
                self._toast(f"Saved: {os.path.basename(p)}")
                self._auto_diagnostics()
            except Exception as e:
                self._toast(str(e), "error")
            finally:
                if btn and btn.winfo_exists():
                    btn.configure(text="Сохранить .cfg", state="normal")
        self.after(10, _finish)

    def _exp_full(self):
        btn = getattr(self, "_btn_exp_full", None)
        if btn:
            btn.configure(text="⏳ Экспорт...", state="disabled")
        self._toast("⏳ Экспорт полного набора...", "info")

        def _do_export():
            try:
                exported = export_full_config_set(self.current_config)
                root = os.path.dirname(next(iter(exported.values())))
                self.after(0, lambda: self._exp_full_done(exported, root))
            except Exception as e:
                self.after(0, lambda: self._toast(str(e), "error"))
            finally:
                if btn:
                    self.after(0, lambda: btn.configure(
                        text="\U0001f4c1  Сохранить полный набор (GoldSrc v3.0)", state="normal")
                              if btn.winfo_exists() else None)

        self._executor.submit(_do_export)

    def _exp_full_done(self, exported, root):
        self._toast(f"Полный набор: {len(exported)} файлов сохранено")
        self._auto_diagnostics()
        messagebox.showinfo("Сохранено",
            f"Сохранено в:\n{os.path.normpath(root)}\n\nФайлы:\n" +
            "\n".join(f"  {k}" for k in exported))

    def _auto_diagnostics(self):
        if not self.current_config:
            return
        try:
            report = run_diagnostics(self.current_config)
            emoji = "✅" if report.score >= 80 else "⚠️" if report.score >= 50 else "❌"
            self._toast(f"{emoji} Диагностика: {report.score}/100 ({report.warning_count} warn, {report.error_count} err)",
                        "info" if report.score >= 80 else "warning")
        except Exception:
            pass

    def _exp_batch(self):
        profiles = list_profiles()
        if not profiles:
            self._toast("Нет сохранённых профилей для экспорта", "warning")
            return
        target = filedialog.askdirectory(title="Выберите папку для пакетного экспорта")
        if not target:
            return
        count = 0
        for p in profiles:
            try:
                name, cfg = load_profile(p["filename"])
                content = generate_single_cfg(cfg)
                safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
                path = os.path.join(target, f"{safe_name}.cfg")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                count += 1
            except Exception as exc:
                log.warning(f"Batch export skip {p['filename']}: {exc}")
        self._toast(f"Экспортировано {count} из {len(profiles)} профилей → {target}")

    def _exp_saveas(self):
        p = filedialog.asksaveasfilename(defaultextension=".cfg",
            filetypes=[("CFG", "*.cfg"), ("All", "*.*")], initialfile="autoexec.cfg")
        if not p:
            return
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(generate_single_cfg(self.current_config))
            self._toast(f"Saved: {os.path.basename(p)}")
        except Exception as e:
            self._toast(str(e), "error")

    # ═══════════════════════════════════════════════ IMPORT
    def _p_import(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f4e5 Импорт конфига", "Загрузите существующий .cfg из файла или URL")

        # Drag & Drop zone
        dz = ctk.CTkFrame(fr, height=80, fg_color=T.BG_TERTIARY, corner_radius=T.CARD_R,
                            border_width=2, border_color=T.BORDER)
        dz.pack(fill="x", padx=T.CONTENT_PX, pady=(0, 8))
        dz.pack_propagate(False)
        dz_lbl = ctk.CTkLabel(dz, text="📂  Перетащите .cfg файл сюда\nили нажмите для выбора",
                               font=ctk.CTkFont(size=13), text_color=T.TEXT_MUTED,
                               justify="center")
        dz_lbl.pack(expand=True)
        dz.bind("<Button-1>", lambda e: self._browse_and_import())
        dz_lbl.bind("<Button-1>", lambda e: self._browse_and_import())
        try:
            dz.drop_target_register("DND_Files")
            dz.dnd_bind("<<Drop>>", self._on_drop_cfg)
        except Exception:
            pass

        c1 = self._card(fr, "\U0001f4c2  Из файла")
        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        self._imp_fp = ctk.CTkEntry(row, placeholder_text="Path to .cfg file...", width=380,
                                     corner_radius=T.INPUT_R, fg_color=T.BG_PRIMARY,
                                     border_color=T.BORDER)
        self._imp_fp.pack(side="left", padx=(0, 6))
        ctk.CTkButton(row, text="Обзор", width=80, corner_radius=T.BTN_R,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                      command=self._browse_cfg).pack(side="left", padx=(0, 6))
        ctk.CTkButton(row, text="Импорт", width=80, corner_radius=T.BTN_R,
                      fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                      command=self._do_imp_f).pack(side="left")

        c2 = self._card(fr, "\U0001f310  Из URL")
        row2 = ctk.CTkFrame(c2, fg_color="transparent")
        row2.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        self._imp_url = ctk.CTkEntry(row2, placeholder_text="https://example.com/config.cfg",
                                      width=380, corner_radius=T.INPUT_R, fg_color=T.BG_PRIMARY,
                                      border_color=T.BORDER)
        self._imp_url.pack(side="left", padx=(0, 6))
        ctk.CTkButton(row2, text="Скачать", width=100, corner_radius=T.BTN_R,
                      fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      command=self._do_imp_u).pack(side="left")

    def _browse_cfg(self):
        p = filedialog.askopenfilename(filetypes=[("CFG", "*.cfg"), ("All", "*.*")])
        if p:
            self._imp_fp.delete(0, "end")
            self._imp_fp.insert(0, p)

    def _do_imp_f(self):
        p = self._imp_fp.get().strip()
        if not p:
            return
        try:
            cfg, s = import_from_file(p)
            self.current_config = cfg
            self._upd()
            self._toast(f"Imported: {s}")
        except SecurityError as e:
            self._toast(str(e), "warning")
        except FileNotFoundError:
            self._toast(f"File not found: {p}", "error")
        except Exception as e:
            self._toast(str(e), "error")

    def _do_imp_u(self):
        u = self._imp_url.get().strip()
        if not u:
            return
        self._toast("⏳ Загрузка...", "info")

        def _download():
            try:
                cfg, s = import_from_url(u)
                self.after(0, lambda: self._finish_url_import(cfg, s))
            except SecurityError as e:
                self.after(0, lambda: self._toast(str(e), "warning"))
            except Exception as e:
                self.after(0, lambda: self._toast(str(e), "error"))

        threading.Thread(target=_download, daemon=True).start()

    def _finish_url_import(self, cfg, s):
        self.current_config = cfg
        self._upd()
        self._toast(f"Imported: {s}")

    def _browse_and_import(self):
        p = filedialog.askopenfilename(filetypes=[("CFG", "*.cfg"), ("All", "*.*")])
        if p:
            self._import_file(p)

    def _on_drop_cfg(self, event):
        path = event.data.strip().strip("{}")
        if path.lower().endswith(".cfg"):
            self._import_file(path)
        else:
            self._toast("Поддерживаются только .cfg файлы", "warning")

    def _import_file(self, path: str):
        try:
            cfg, s = import_from_file(path)
            self.current_config = cfg
            self._upd()
            self._toast(f"Импорт: {s}")
        except SecurityError as e:
            self._toast(str(e), "warning")
        except FileNotFoundError:
            self._toast(f"Файл не найден: {path}", "error")
        except Exception as e:
            self._toast(str(e), "error")

    # ═══════════════════════════════════════════════ COMPARE
    def _p_compare(self):
        fr = ctk.CTkFrame(self._content, fg_color=T.BG_PRIMARY)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f500 Сравнение конфигов", "Сравните ваш конфиг с про-пресетом")

        if not self.current_config:
            c = self._card(fr)
            ctk.CTkLabel(c, text="Сначала загрузите конфиг.", font=T.F_BODY,
                         text_color=T.ORANGE).pack(padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        presets = get_presets()
        pk = list(presets.keys())
        pl = [presets[k].get("name", k) for k in pk]

        c = self._card(fr)
        c.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(c, text="Сравнить с:", font=T.F_LABEL, text_color=T.TEXT).grid(
            row=0, column=0, sticky="w", padx=T.CARD_PAD, pady=T.CARD_PAD)
        self._cmp_cb = ctk.CTkComboBox(c, values=pl, width=260, state="readonly",
                                        corner_radius=T.INPUT_R, fg_color=T.BG_TERTIARY,
                                        border_color=T.BORDER)
        self._cmp_cb.grid(row=0, column=1, sticky="w", padx=6, pady=T.CARD_PAD)
        self._cmp_cb.set(pl[0])
        self._cmp_pk = pk
        ctk.CTkButton(c, text="Сравнить", width=100, height=34, corner_radius=T.BTN_R,
                      fg_color=T.BLUE, hover_color=T.BLUE_HOVER, font=T.F_LABEL,
                      command=self._do_cmp).grid(row=0, column=2, padx=(4, T.CARD_PAD), pady=T.CARD_PAD)

        self._cmp_sc = ctk.CTkScrollableFrame(fr, fg_color=T.BG_PRIMARY)
        self._cmp_sc.pack(fill="both", expand=True, padx=T.CONTENT_PX, pady=(4, 12))

    _CMP_BATCH = 20

    def _do_cmp(self):
        for w in self._cmp_sc.winfo_children():
            w.destroy()
        txt = self._cmp_cb.get()
        ppk = self._cmp_pk[0]
        presets = get_presets()
        for k in self._cmp_pk:
            if presets[k].get("name", k) == txt:
                ppk = k
                break
        diffs = compare_configs(self.current_config, ppk)

        ref_settings = presets[ppk].get("settings", {})
        axes, va, vb = config_to_radar_values(self.current_config.settings, ref_settings)
        radar = RadarChart(self._cmp_sc, size=340)
        radar.set_data(axes, va, vb, "Ваш конфиг", f"Pro: {txt}")
        radar.pack(pady=(8, 8))

        if not diffs:
            ctk.CTkLabel(self._cmp_sc, text="\u2705  Различий нет!", font=T.F_H2,
                         text_color=T.GREEN).pack(pady=20)
            return

        ctk.CTkFrame(self._cmp_sc, height=1, fg_color=T.BORDER).pack(
            fill="x", padx=10, pady=(4, 8))

        tbl = ctk.CTkFrame(self._cmp_sc, fg_color="transparent")
        tbl.pack(fill="x")
        tbl.grid_columnconfigure((0, 1, 2), weight=1)
        hf = T.F_LABEL
        ctk.CTkLabel(tbl, text="Параметр", font=hf, text_color=T.TEXT).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        ctk.CTkLabel(tbl, text="Ваш конфиг", font=hf, text_color=T.BLUE).grid(
            row=0, column=1, sticky="w", padx=6, pady=(8, 4))
        ctk.CTkLabel(tbl, text=f"Pro: {txt}", font=hf, text_color=T.ORANGE).grid(
            row=0, column=2, sticky="w", padx=6, pady=(8, 4))
        ctk.CTkFrame(tbl, height=1, fg_color=T.BORDER).grid(
            row=1, column=0, columnspan=3, sticky="we", padx=10, pady=2)

        self._cmp_diffs = diffs
        self._cmp_pro_name = txt
        self._cmp_tbl = tbl
        self._cmp_loaded = 0
        self._cmp_load_next_batch()

    def _cmp_load_next_batch(self):
        """Progressively render diff rows in batches of _CMP_BATCH."""
        if not hasattr(self, "_cmp_diffs") or not hasattr(self, "_cmp_tbl"):
            return
        tbl = self._cmp_tbl
        diffs = self._cmp_diffs
        start = self._cmp_loaded
        end = min(start + self._CMP_BATCH, len(diffs))

        for i in range(start, end):
            row = i + 2
            p, yv, pv = diffs[i]
            ctk.CTkLabel(tbl, text=p, font=T.F_CAP, text_color=T.TEXT).grid(
                row=row, column=0, sticky="w", padx=10, pady=1)
            ctk.CTkLabel(tbl, text=yv, font=T.F_MONO, text_color=T.BLUE).grid(
                row=row, column=1, sticky="w", padx=6, pady=1)
            ctk.CTkLabel(tbl, text=pv, font=T.F_MONO, text_color=T.ORANGE).grid(
                row=row, column=2, sticky="w", padx=6, pady=1)

        self._cmp_loaded = end

        if end < len(diffs):
            self.after(1, self._cmp_load_next_batch)
        else:
            ctk.CTkLabel(tbl, text=f"{len(diffs)} различий",
                         font=T.F_CAP, text_color=T.TEXT_MUTED).grid(
                row=len(diffs) + 2, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 4))
            ctk.CTkButton(self._cmp_sc, text="📄  Экспорт сравнения", height=34,
                          corner_radius=T.BTN_R, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                          font=T.F_LABEL, command=self._cmp_export).pack(pady=(8, 4))


    def _cmp_export(self):
        if not hasattr(self, "_cmp_diffs") or not self._cmp_diffs:
            self._toast("Нечего экспортировать", "warning")
            return
        p = filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("HTML", "*.html")],
            initialfile="comparison.txt")
        if not p:
            return
        try:
            lines = [f"Сравнение: Ваш конфиг vs Pro: {self._cmp_pro_name}",
                     f"{'='*60}", ""]
            lines.append(f"{'Параметр':<30} {'Ваш':<15} {'Pro':<15}")
            lines.append("-" * 60)
            for param, your_val, pro_val in self._cmp_diffs:
                lines.append(f"{param:<30} {your_val:<15} {pro_val:<15}")
            lines.append("")
            lines.append(f"Итого различий: {len(self._cmp_diffs)}")
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self._toast(f"Сравнение сохранено: {os.path.basename(p)}")
        except Exception as e:
            self._toast(str(e), "error")

    # ═══════════════════════════════════════════════ BUY SCRIPT EDITOR
    def _p_buyscript(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "🛒 Редактор закупки",
                  "Составьте buy-скрипт визуально — выберите оружие и экипировку")
        self._ensure()

        bs_data = get_buyscripts()
        self._bs_selected: list[tuple[str, str, int]] = []
        self._bs_total_cost = 0

        weapons = bs_data.get("weapons", {})
        categories = [
            ("Пистолеты", weapons.get("pistols", {})),
            ("Дробовики", weapons.get("shotguns", {})),
            ("Пистолеты-пулемёты", weapons.get("smgs", {})),
            ("Винтовки", weapons.get("rifles", {})),
            ("Пулемёты", weapons.get("mg", {})),
        ]
        for cat_name, items in categories:
            c = self._card(fr, f"🔫  {cat_name}")
            row = ctk.CTkFrame(c, fg_color="transparent")
            row.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
            for key, info in items.items():
                name = info.get("name", key)
                price = info.get("price", 0)
                cmd = info.get("command", "")
                ctk.CTkButton(
                    row, text=f"{name}\n${price}", width=110, height=50,
                    corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                    hover_color=T.BORDER, text_color=T.TEXT,
                    font=ctk.CTkFont(size=10),
                    command=lambda n=name, c=cmd, p=price: self._bs_add(n, c, p),
                ).pack(side="left", padx=2)

        equipment = bs_data.get("equipment", {})
        ec = self._card(fr, "🛡  Экипировка")
        er = ctk.CTkFrame(ec, fg_color="transparent")
        er.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        for key, info in equipment.items():
            name = info.get("name", key)
            price = info.get("price", 0)
            cmd = info.get("command", "")
            ctk.CTkButton(
                er, text=f"{name}\n${price}", width=110, height=50,
                corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                hover_color=T.BORDER, text_color=T.TEXT,
                font=ctk.CTkFont(size=10),
                command=lambda n=name, c=cmd, p=price: self._bs_add(n, c, p),
            ).pack(side="left", padx=2)

        # result card
        rc = self._card(fr, "📋  Собранный скрипт")
        self._bs_cost_lbl = ctk.CTkLabel(rc, text="Стоимость: $0",
                                          font=ctk.CTkFont(size=16, weight="bold"),
                                          text_color=T.GREEN)
        self._bs_cost_lbl.pack(anchor="w", padx=T.CARD_PAD, pady=(8, 4))

        self._bs_items_lbl = ctk.CTkLabel(rc, text="Нажмите на оружие / экипировку чтобы добавить",
                                           font=T.F_CAP, text_color=T.TEXT_SEC,
                                           wraplength=500, justify="left")
        self._bs_items_lbl.pack(anchor="w", padx=T.CARD_PAD, pady=(0, 4))

        self._bs_code = ctk.CTkTextbox(rc, height=80, font=T.F_MONO,
                                        fg_color=T.BG_PRIMARY, border_width=1,
                                        border_color=T.BORDER, corner_radius=T.INPUT_R,
                                        wrap="word")
        self._bs_code.pack(fill="x", padx=T.CARD_PAD, pady=(0, 4))

        btn_r = ctk.CTkFrame(rc, fg_color="transparent")
        btn_r.pack(fill="x", padx=T.CARD_PAD, pady=(0, T.CARD_PAD))

        ctk.CTkLabel(btn_r, text="Привязать к:", font=T.F_LABEL,
                     text_color=T.TEXT).pack(side="left")
        self._bs_bind_key = ctk.CTkComboBox(
            btn_r, values=["KP_INS", "KP_END", "KP_DOWNARROW", "KP_PGDN",
                           "KP_LEFTARROW", "KP_5", "KP_RIGHTARROW", "KP_HOME",
                           "KP_UPARROW", "KP_PGUP", "F1", "F2", "F3", "F4"],
            width=140, state="readonly", corner_radius=T.INPUT_R,
            fg_color=T.BG_TERTIARY, border_color=T.BORDER)
        self._bs_bind_key.pack(side="left", padx=(6, 6))
        self._bs_bind_key.set("KP_INS")

        ctk.CTkButton(btn_r, text="Применить бинд", height=32,
                      corner_radius=T.BTN_R, fg_color=T.GREEN,
                      hover_color=T.GREEN_HOVER, font=T.F_CAP,
                      command=self._bs_apply).pack(side="left", padx=(4, 6))
        ctk.CTkButton(btn_r, text="Очистить", height=32,
                      corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                      hover_color=T.BORDER, font=T.F_CAP,
                      command=self._bs_clear).pack(side="left")
        ctk.CTkButton(btn_r, text="Копировать", height=32,
                      corner_radius=T.BTN_R, fg_color=T.BLUE,
                      hover_color=T.BLUE_HOVER, font=T.F_CAP,
                      command=self._bs_copy).pack(side="right")

    def _bs_add(self, name: str, cmd: str, price: int):
        self._bs_selected.append((name, cmd, price))
        self._bs_total_cost += price
        self._bs_refresh()

    def _bs_refresh(self):
        if self._bs_selected:
            names = [f"{n} (${p})" for n, _, p in self._bs_selected]
            self._bs_items_lbl.configure(text=" → ".join(names))
            color = T.RED if self._bs_total_cost > 16000 else T.ORANGE if self._bs_total_cost > 5000 else T.GREEN
            self._bs_cost_lbl.configure(text=f"Стоимость: ${self._bs_total_cost}", text_color=color)
            cmds = "; ".join(cmd for _, cmd, _ in self._bs_selected)
            alias_name = "buy_custom"
            code = f'alias "{alias_name}" "{cmds}"\n'
            bind_key = self._bs_bind_key.get()
            code += f'bind "{bind_key}" "{alias_name}"'
            self._bs_code.delete("1.0", "end")
            self._bs_code.insert("1.0", code)
        else:
            self._bs_items_lbl.configure(text="Нажмите на оружие / экипировку чтобы добавить")
            self._bs_cost_lbl.configure(text="Стоимость: $0", text_color=T.GREEN)
            self._bs_code.delete("1.0", "end")

    def _bs_clear(self):
        self._bs_selected.clear()
        self._bs_total_cost = 0
        self._bs_refresh()

    def _bs_apply(self):
        if not self._bs_selected:
            self._toast("Сначала выберите оружие", "warning")
            return
        cmds = "; ".join(cmd for _, cmd, _ in self._bs_selected)
        alias_name = "buy_custom"
        bind_key = self._bs_bind_key.get().lower()
        self.current_config.settings[f"_alias_{alias_name}"] = cmds
        self.current_config.buy_binds[bind_key] = alias_name
        self._upd()
        self._toast(f"Buy-скрипт привязан к {bind_key} (${self._bs_total_cost})")

    def _bs_copy(self):
        code = self._bs_code.get("1.0", "end").strip()
        if code:
            self.clipboard_clear()
            self.clipboard_append(code)
            self._toast("Скопировано в буфер")

    # ═══════════════════════════════════════════════ KEYBOARD BIND TESTER
    def _p_keyboard(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "⌨ Клавиатура биндов",
                  "Визуальная раскладка — цвет показывает категорию бинда")

        self._ensure()
        cfg = self.current_config

        kb = KeyboardWidget(fr, binds=cfg.binds, buy_binds=cfg.buy_binds,
                            on_key_click=self._kb_on_click)
        kb.pack(padx=T.CONTENT_PX, pady=(12, 4))
        self._kb_widget = kb

        stats = kb.get_stats()
        sc = self._card(fr, "📊  Статистика биндов", grid=True)
        sc.grid_columnconfigure((0, 1, 2, 3), weight=1)
        stat_items = [
            ("Всего клавиш", str(stats["total_keys"]), T.TEXT),
            ("Назначено", str(stats["bound"]), T.GREEN),
            ("Свободно", str(stats["free"]), T.TEXT_MUTED),
            ("Категории", str(len(stats["categories"])), T.BLUE),
        ]
        for i, (lbl, val, clr) in enumerate(stat_items):
            ctk.CTkLabel(sc, text=val, font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=clr).grid(row=0, column=i, pady=(8, 0))
            ctk.CTkLabel(sc, text=lbl, font=T.F_CAP,
                         text_color=T.TEXT_SEC).grid(row=1, column=i, pady=(0, 8))

        dc = self._card(fr, "🔍  Информация о клавише")
        self._kb_info_lbl = ctk.CTkLabel(dc, text="Нажмите на клавишу для просмотра бинда",
                                          font=T.F_BODY, text_color=T.TEXT_MUTED)
        self._kb_info_lbl.pack(padx=T.CARD_PAD, pady=T.CARD_PAD)

        self._kb_edit_fr = ctk.CTkFrame(dc, fg_color="transparent")
        self._kb_edit_fr.pack(fill="x", padx=T.CARD_PAD, pady=(0, T.CARD_PAD))
        self._kb_edit_fr.pack_forget()

    def _kb_on_click(self, cs_key: str, cmd: str):
        if cmd:
            self._kb_info_lbl.configure(
                text=f"Клавиша:  {cs_key}\nБинд:  {cmd}",
                text_color=T.TEXT)
        else:
            self._kb_info_lbl.configure(
                text=f"Клавиша:  {cs_key}\nНе назначена",
                text_color=T.TEXT_MUTED)

        for w in self._kb_edit_fr.winfo_children():
            w.destroy()
        self._kb_edit_fr.pack(fill="x", padx=T.CARD_PAD, pady=(0, T.CARD_PAD))

        row = ctk.CTkFrame(self._kb_edit_fr, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Команда:", font=T.F_LABEL,
                     text_color=T.TEXT).pack(side="left")
        entry = ctk.CTkEntry(row, width=300, corner_radius=T.INPUT_R,
                              fg_color=T.BG_PRIMARY, border_color=T.BORDER)
        entry.pack(side="left", padx=(6, 6))
        if cmd:
            entry.insert(0, cmd)

        def _apply():
            new_cmd = entry.get().strip()
            if new_cmd:
                self.current_config.binds[cs_key.lower()] = new_cmd
            else:
                self.current_config.binds.pop(cs_key.lower(), None)
            self._kb_widget.update_binds(self.current_config.binds,
                                          self.current_config.buy_binds)
            self._upd()
            self._toast(f"Бинд {cs_key} обновлён")

        ctk.CTkButton(row, text="Применить", width=90, height=28,
                      corner_radius=T.BTN_R, fg_color=T.GREEN,
                      hover_color=T.GREEN_HOVER, font=T.F_CAP,
                      command=_apply).pack(side="left")

    # ═══════════════════════════════════════════════ DEMO SETTINGS
    def _p_demo(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "🎬 Демо-настройки",
                  "Настройки записи и просмотра демо-файлов")
        self._ensure()

        # record settings
        rc = self._card(fr, "🔴  Запись демо")
        self._dm_auto = tk.BooleanVar(
            value=self.current_config.settings.get("cl_autodemo", "0") == "1")
        ctk.CTkCheckBox(rc, text="Автозапись демо (cl_autodemo 1)",
                        variable=self._dm_auto, font=T.F_LABEL, text_color=T.TEXT,
                        fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                        border_color=T.BORDER).pack(
            anchor="w", padx=T.CARD_PAD, pady=(8, 4))

        ctk.CTkLabel(rc, text="Бинды для управления демо:", font=T.F_LABEL,
                     text_color=T.TEXT_SEC).pack(anchor="w", padx=T.CARD_PAD, pady=(8, 2))
        demo_binds = [
            ("F5", "record demo", "Начать запись"),
            ("F6", "stop", "Остановить запись"),
            ("F7", "playdemo", "Воспроизвести последнее демо"),
            ("F8", "viewdemo", "Просмотр демо"),
        ]
        self._dm_bind_vars: dict[str, tk.BooleanVar] = {}
        for key, cmd, desc in demo_binds:
            var = tk.BooleanVar(
                value=self.current_config.binds.get(key.lower(), "") in (cmd, f'"{cmd}"'))
            self._dm_bind_vars[key] = var
            ctk.CTkCheckBox(rc, text=f"{key} → {cmd}  ({desc})",
                            variable=var, font=T.F_CAP, text_color=T.TEXT,
                            fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                            border_color=T.BORDER).pack(
                anchor="w", padx=(T.CARD_PAD + 16, T.CARD_PAD), pady=2)
        ctk.CTkFrame(rc, height=4, fg_color="transparent").pack()

        # playback settings
        pc = self._card(fr, "▶️  Настройки просмотра")
        pc_grid = ctk.CTkFrame(pc, fg_color="transparent")
        pc_grid.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        pc_grid.grid_columnconfigure(1, weight=1)

        cvars_demo = [
            ("cl_draw_only_deathnotices", "Только килфид (для фрагмуви)", "0"),
            ("cl_righthand", "Оружие справа", "1"),
            ("viewmodel_fov", "FOV модели оружия", "90"),
            ("cl_bob", "Покачивание оружия", "0"),
            ("cl_bobup", "Подъём оружия при ходьбе", "0"),
        ]
        self._dm_cvars: dict[str, ctk.CTkEntry] = {}
        for i, (cvar, desc, default) in enumerate(cvars_demo):
            ctk.CTkLabel(pc_grid, text=desc, font=T.F_CAP, text_color=T.TEXT,
                         anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            e = ctk.CTkEntry(pc_grid, width=80, corner_radius=T.INPUT_R,
                             fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                             font=T.F_VAL, justify="center")
            e.grid(row=i, column=1, sticky="w", padx=(8, 0), pady=3)
            e.insert(0, self.current_config.settings.get(cvar, default))
            self._dm_cvars[cvar] = e

        # presets
        prc = self._card(fr, "🎞️  Пресеты демо")
        pr_row = ctk.CTkFrame(prc, fg_color="transparent")
        pr_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        demo_presets = [
            ("Фрагмуви", {"cl_draw_only_deathnotices": "1", "cl_righthand": "1",
                          "viewmodel_fov": "90", "cl_bob": "0", "cl_bobup": "0",
                          "crosshair": "0", "cl_shadows": "0", "r_drawviewmodel": "0"}),
            ("Обзор матча", {"cl_draw_only_deathnotices": "0", "cl_righthand": "1",
                             "viewmodel_fov": "90", "cl_bob": "0.01", "cl_bobup": "0.5",
                             "crosshair": "1", "r_drawviewmodel": "1"}),
            ("Стрим", {"cl_draw_only_deathnotices": "0", "cl_righthand": "1",
                       "viewmodel_fov": "68", "cl_bob": "0.01", "cl_bobup": "0.5",
                       "crosshair": "1", "r_drawviewmodel": "1", "cl_shadows": "1"}),
        ]
        for name, settings in demo_presets:
            ctk.CTkButton(pr_row, text=name, height=36, corner_radius=T.BTN_R,
                          fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                          font=T.F_LABEL,
                          command=lambda s=settings: self._dm_apply_preset(s)).pack(
                side="left", padx=(0, 6))

        # apply button
        bf = ctk.CTkFrame(fr, fg_color="transparent")
        bf.pack(fill="x", padx=T.CONTENT_PX, pady=(8, 20))
        ctk.CTkButton(bf, text="✅  Применить настройки демо", height=44,
                      corner_radius=T.BTN_R, fg_color=T.GREEN,
                      hover_color=T.GREEN_HOVER,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._dm_apply).pack(fill="x")

    def _dm_apply_preset(self, settings: dict):
        for cvar, val in settings.items():
            if cvar in self._dm_cvars:
                self._dm_cvars[cvar].delete(0, "end")
                self._dm_cvars[cvar].insert(0, val)
            self.current_config.set(cvar, val)
        self._upd()
        self._toast("Пресет демо применён")

    def _dm_apply(self):
        if self._dm_auto.get():
            self.current_config.set("cl_autodemo", "1")
        else:
            self.current_config.set("cl_autodemo", "0")

        demo_binds_map = {
            "F5": "record demo",
            "F6": "stop",
            "F7": "playdemo",
            "F8": "viewdemo",
        }
        for key, cmd in demo_binds_map.items():
            if self._dm_bind_vars.get(key, tk.BooleanVar()).get():
                self.current_config.binds[key.lower()] = cmd
            else:
                self.current_config.binds.pop(key.lower(), None)

        for cvar, entry in self._dm_cvars.items():
            val = entry.get().strip()
            if val:
                self.current_config.set(cvar, val)

        self._upd()
        self._toast("Настройки демо применены")

    # ─────────────────────────────────────────────── profile helpers
    def _refresh_profile_list(self):
        profiles = list_profiles()
        names = [p["name"] for p in profiles]
        if not names:
            names = ["(none)"]
        self._prof_cb.configure(values=names)
        active_fn = get_active_profile()
        active_name = "(none)"
        for p in profiles:
            if p["is_active"]:
                active_name = p["name"]
                break
        self._prof_cb.set(active_name)

    def _on_profile_switch(self, selected: str):
        if selected == "(none)":
            return
        profiles = list_profiles()
        for p in profiles:
            if p["name"] == selected:
                try:
                    name, cfg = load_profile(p["filename"])
                    self.current_config = cfg
                    self._upd()
                    self._toast(f"Profile loaded: {name}")
                except Exception as e:
                    self._toast(str(e), "error")
                return

    def _quick_save_profile(self):
        dlg = ctk.CTkInputDialog(text="Profile name:", title="Save Profile")
        name = dlg.get_input()
        if not name:
            return
        if not self.current_config:
            self._toast("Нет конфига для сохранения", "warning")
            return
        save_profile(name, self.current_config)
        save_history_snapshot(self.current_config, f"profile_{name}")
        self._refresh_profile_list()
        self._toast(f"Profile saved: {name}")

    # ═══════════════════════════════════════════════ SENSITIVITY CALCULATOR
    # _p_sensitivity + _sc_* → pages/sensitivity_page.py (SensitivityPageMixin)

    # ═══════════════════════════════════════════════ DIAGNOSTICS
    def _p_diagnostics(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f50d Диагностика конфига",
                  "Автоматический анализ с оценкой и рекомендациями")

        if not self.current_config:
            c = self._card(fr)
            ctk.CTkLabel(c, text="Конфиг не загружен. Сначала создайте его.",
                         font=T.F_BODY, text_color=T.ORANGE).pack(padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        report = run_diagnostics(self.current_config)
        self._diag_report = report

        # Score card
        sc = self._card(fr, "\U0001f3c6  Score")
        score_color = T.GREEN if report.score >= 80 else T.ORANGE if report.score >= 50 else T.RED
        score_row = ctk.CTkFrame(sc, fg_color="transparent")
        score_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, 4))
        ctk.CTkLabel(score_row, text=f"{report.score}/100",
                     font=ctk.CTkFont(size=36, weight="bold"),
                     text_color=score_color).pack(side="left")
        summary = ctk.CTkFrame(score_row, fg_color="transparent")
        summary.pack(side="left", padx=20)
        ctk.CTkLabel(summary, text=f"\u2705 {report.ok_count} OK", font=T.F_LABEL,
                     text_color=T.GREEN).pack(anchor="w")
        ctk.CTkLabel(summary, text=f"\u26a0\ufe0f {report.warning_count} Warnings", font=T.F_LABEL,
                     text_color=T.ORANGE).pack(anchor="w")
        ctk.CTkLabel(summary, text=f"\u274c {report.error_count} Errors", font=T.F_LABEL,
                     text_color=T.RED).pack(anchor="w")

        bar = ctk.CTkProgressBar(sc, height=10, width=400, corner_radius=5,
                                  progress_color=score_color, fg_color=T.BORDER)
        bar.pack(padx=T.CARD_PAD, pady=(4, T.CARD_PAD))
        bar.set(report.score / 100)

        # Fixable count
        fixable = sum(1 for i in report.items
                      if i.severity in ("warning", "error") and i.fix_key)
        if fixable > 0:
            bf = ctk.CTkFrame(fr, fg_color="transparent")
            bf.pack(fill="x", padx=T.CONTENT_PX, pady=(4, 0))
            ctk.CTkButton(bf, text=f"\u2699  Apply All Fixes ({fixable})", height=40,
                          corner_radius=T.BTN_R, fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                          font=T.F_LABEL, command=lambda: self._diag_fix_all(fr)).pack(fill="x")

        # Details
        icons = {"ok": "\u2705", "warning": "\u26a0\ufe0f", "error": "\u274c", "info": "\u2139\ufe0f"}
        colors = {"ok": T.GREEN, "warning": T.ORANGE, "error": T.RED, "info": T.BLUE}

        categories_seen: dict[str, list] = {}
        for item in report.items:
            categories_seen.setdefault(item.category, []).append(item)

        for cat, items_list in categories_seen.items():
            dc = self._card(fr, f"  {cat}", collapsible=True)
            for item in items_list:
                row = ctk.CTkFrame(dc, fg_color="transparent")
                row.pack(fill="x", padx=(T.CARD_PAD - 4), pady=2)
                icon = icons.get(item.severity, "\u2022")
                clr = colors.get(item.severity, T.TEXT)
                ctk.CTkLabel(row, text=f"{icon}  {item.message}", font=T.F_LABEL,
                             text_color=clr, wraplength=500, anchor="w").pack(
                    side="left", fill="x", expand=True)
                if item.fix_key and item.severity in ("warning", "error"):
                    ctk.CTkButton(row, text="Fix", width=50, height=26, corner_radius=6,
                                  fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                                  font=ctk.CTkFont(size=11),
                                  command=lambda i=item: self._diag_fix_one(i)).pack(
                        side="right", padx=(4, 0))
            ctk.CTkFrame(dc, height=6, fg_color="transparent").pack()

    def _diag_fix_one(self, item):
        if self.current_config:
            apply_fix(self.current_config, item)
            self._upd()
            self._toast(f"Fixed: {item.fix_key} = {item.fix_value}")
            self._nav("diagnostics")

    def _diag_fix_all(self, fr):
        if self.current_config and hasattr(self, "_diag_report"):
            count = apply_all_fixes(self.current_config, self._diag_report)
            self._upd()
            self._toast(f"Applied {count} fixes")
            self._nav("diagnostics")

    # ═══════════════════════════════════════════════ PROFILES
    def _p_profiles(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f464 Профили пользователя", "Сохранение, загрузка и управление профилями")

        # Actions card
        ac = self._card(fr, "\u2795  Actions")
        bf = ctk.CTkFrame(ac, fg_color="transparent")
        bf.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        ctk.CTkButton(bf, text="\U0001f4be  Save Current as Profile", height=36,
                      corner_radius=T.BTN_R, fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                      font=T.F_LABEL, command=self._prof_save_new).pack(side="left", padx=(0, 8))
        ctk.CTkButton(bf, text="\U0001f4c2  Import Profile (.json)", height=36,
                      corner_radius=T.BTN_R, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      font=T.F_LABEL, command=self._prof_import).pack(side="left")

        # Profiles list
        profiles = list_profiles()
        if not profiles:
            nc = self._card(fr)
            ctk.CTkLabel(nc, text="No profiles yet. Save your first profile above.",
                         font=T.F_BODY, text_color=T.TEXT_MUTED).pack(
                padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        for p in profiles:
            pc = self._card(fr)
            pc.grid_columnconfigure(1, weight=1)

            active_dot = "\u25cf " if p["is_active"] else "  "
            dot_color = T.GREEN if p["is_active"] else T.TEXT_MUTED

            name_row = ctk.CTkFrame(pc, fg_color="transparent")
            name_row.pack(fill="x", padx=T.CARD_PAD, pady=(T.CARD_PAD, 0))
            ctk.CTkLabel(name_row, text=active_dot, font=ctk.CTkFont(size=14),
                         text_color=dot_color, width=16).pack(side="left")
            ctk.CTkLabel(name_row, text=p["name"], font=T.F_H2,
                         text_color=T.TEXT).pack(side="left")

            info_text = f"Mode: {p['mode'] or '—'}  \u2502  {p['cvars']} CVARs  \u2502  Updated: {p['updated_at'][:10] if p['updated_at'] else '—'}"
            ctk.CTkLabel(pc, text=info_text, font=T.F_CAP,
                         text_color=T.TEXT_SEC).pack(anchor="w", padx=T.CARD_PAD, pady=(4, 0))

            btn_row = ctk.CTkFrame(pc, fg_color="transparent")
            btn_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
            fn = p["filename"]
            ctk.CTkButton(btn_row, text="Load", width=60, height=28, corner_radius=6,
                          fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                          font=ctk.CTkFont(size=11),
                          command=lambda f=fn: self._prof_load(f)).pack(side="left", padx=(0, 4))
            ctk.CTkButton(btn_row, text="Duplicate", width=70, height=28, corner_radius=6,
                          fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                          font=ctk.CTkFont(size=11),
                          command=lambda f=fn: self._prof_dup(f)).pack(side="left", padx=(0, 4))
            ctk.CTkButton(btn_row, text="Rename", width=60, height=28, corner_radius=6,
                          fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                          font=ctk.CTkFont(size=11),
                          command=lambda f=fn: self._prof_rename(f)).pack(side="left", padx=(0, 4))
            ctk.CTkButton(btn_row, text="Delete", width=60, height=28, corner_radius=6,
                          fg_color=T.RED, hover_color="#D32F2F",
                          font=ctk.CTkFont(size=11),
                          command=lambda f=fn: self._prof_del(f)).pack(side="left")

    def _prof_save_new(self):
        dlg = ctk.CTkInputDialog(text="Profile name:", title="Save Profile")
        name = dlg.get_input()
        if not name:
            return
        if not self.current_config:
            self._toast("Нет конфига для сохранения", "warning")
            return
        save_profile(name, self.current_config)
        save_history_snapshot(self.current_config, f"profile_{name}")
        self._refresh_profile_list()
        self._toast(f"Profile saved: {name}")
        self._nav("profiles")

    def _prof_load(self, fn):
        try:
            name, cfg = load_profile(fn)
            self.current_config = cfg
            self._upd()
            self._refresh_profile_list()
            self._toast(f"Profile loaded: {name}")
        except Exception as e:
            self._toast(str(e), "error")

    def _prof_dup(self, fn):
        dlg = ctk.CTkInputDialog(text="New profile name:", title="Duplicate Profile")
        name = dlg.get_input()
        if not name:
            return
        try:
            duplicate_profile(fn, name)
            self._refresh_profile_list()
            self._toast(f"Profile duplicated: {name}")
            self._nav("profiles")
        except Exception as e:
            self._toast(str(e), "error")

    def _prof_rename(self, fn):
        dlg = ctk.CTkInputDialog(text="New name:", title="Rename Profile")
        name = dlg.get_input()
        if not name:
            return
        try:
            rename_profile(fn, name)
            self._refresh_profile_list()
            self._toast(f"Profile renamed: {name}")
            self._nav("profiles")
        except Exception as e:
            self._toast(str(e), "error")

    def _prof_del(self, fn):
        if messagebox.askyesno("Delete Profile", "Are you sure you want to delete this profile?"):
            delete_profile(fn)
            self._refresh_profile_list()
            self._toast("Profile deleted")
            self._nav("profiles")

    def _prof_import(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON Profile", "*.json"), ("All", "*.*")])
        if not path:
            return
        import json as _json
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            name = data.get("name", os.path.basename(path).replace(".json", ""))
            cfg = CfgConfig()
            cfg_data = data.get("config", data)
            cfg.settings = cfg_data.get("settings", {})
            cfg.binds = cfg_data.get("binds", {})
            cfg.buy_binds = cfg_data.get("buy_binds", {})
            cfg.mode = cfg_data.get("mode")
            cfg.mode_key = cfg_data.get("mode_key")
            save_profile(name, cfg)
            self._refresh_profile_list()
            self._toast(f"Profile imported: {name}")
            self._nav("profiles")
        except Exception as e:
            self._toast(str(e), "error")

    # ═══════════════════════════════════════════════ CONFIG HISTORY
    def _p_history(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f4dc История конфигов",
                  "Автосохранённые снапшоты с возможностью отката и сравнения")

        entries = list_history()
        if not entries:
            c = self._card(fr)
            ctk.CTkLabel(c, text="История пуста.\nСоздайте или сохраните конфиг для первого снапшота.",
                         font=T.F_BODY, text_color=T.TEXT_MUTED).pack(
                padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        # Diff section
        if len(entries) >= 2:
            dc = self._card(fr, "🔍  Сравнить два снапшота")
            dr = ctk.CTkFrame(dc, fg_color="transparent")
            dr.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
            snap_labels = [f"{e['timestamp'][:19]} — {e['label']}" for e in entries]
            ctk.CTkLabel(dr, text="A:", font=T.F_LABEL, text_color=T.BLUE).pack(side="left")
            self._hist_a = ctk.CTkComboBox(dr, values=snap_labels, width=260,
                                            state="readonly", corner_radius=T.INPUT_R,
                                            fg_color=T.BG_TERTIARY, border_color=T.BORDER)
            self._hist_a.pack(side="left", padx=(4, 8))
            self._hist_a.set(snap_labels[0])
            ctk.CTkLabel(dr, text="B:", font=T.F_LABEL, text_color=T.ORANGE).pack(side="left")
            self._hist_b = ctk.CTkComboBox(dr, values=snap_labels, width=260,
                                            state="readonly", corner_radius=T.INPUT_R,
                                            fg_color=T.BG_TERTIARY, border_color=T.BORDER)
            self._hist_b.pack(side="left", padx=(4, 8))
            self._hist_b.set(snap_labels[1] if len(snap_labels) > 1 else snap_labels[0])
            self._hist_entries = entries
            ctk.CTkButton(dr, text="Diff", width=60, height=28, corner_radius=T.BTN_R,
                          fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                          command=self._hist_diff).pack(side="left")

            self._hist_diff_fr = ctk.CTkFrame(dc, fg_color="transparent")
            self._hist_diff_fr.pack(fill="x", padx=T.CARD_PAD, pady=(0, 4))

        ctk.CTkLabel(fr, text=f"  {len(entries)} снапшотов (макс. {20})",
                     font=T.F_CAP, text_color=T.TEXT_MUTED).pack(
            anchor="w", padx=T.CONTENT_PX, pady=(4, 0))

        for entry in entries:
            ec = self._card(fr)
            ec.grid_columnconfigure(1, weight=1)

            ts = entry["timestamp"][:19].replace("T", "  ")
            name_row = ctk.CTkFrame(ec, fg_color="transparent")
            name_row.pack(fill="x", padx=T.CARD_PAD, pady=(T.CARD_PAD, 0))
            ctk.CTkLabel(name_row, text=f"\U0001f553  {ts}", font=T.F_LABEL,
                         text_color=T.TEXT).pack(side="left")
            ctk.CTkLabel(name_row, text=f"  \u2502  {entry['label']}  \u2502  {entry['cvars']} CVARs",
                         font=T.F_CAP, text_color=T.TEXT_SEC).pack(side="left", padx=8)

            btn_row = ctk.CTkFrame(ec, fg_color="transparent")
            btn_row.pack(fill="x", padx=T.CARD_PAD, pady=(6, T.CARD_PAD))
            fn = entry["filename"]
            ctk.CTkButton(btn_row, text="\u21a9  Откатить", width=90, height=28,
                          corner_radius=6, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                          font=ctk.CTkFont(size=11),
                          command=lambda f=fn: self._hist_rollback(f)).pack(side="left")

    def _hist_diff(self):
        a_txt = self._hist_a.get()
        b_txt = self._hist_b.get()
        a_idx = next((i for i, e in enumerate(self._hist_entries)
                      if f"{e['timestamp'][:19]} — {e['label']}" == a_txt), 0)
        b_idx = next((i for i, e in enumerate(self._hist_entries)
                      if f"{e['timestamp'][:19]} — {e['label']}" == b_txt), 0)
        try:
            _, cfg_a = load_history_snapshot(self._hist_entries[a_idx]["filename"])
            _, cfg_b = load_history_snapshot(self._hist_entries[b_idx]["filename"])
        except Exception as e:
            self._toast(str(e), "error")
            return

        for w in self._hist_diff_fr.winfo_children():
            w.destroy()

        all_keys = sorted(set(cfg_a.settings.keys()) | set(cfg_b.settings.keys()))
        diffs = []
        for k in all_keys:
            va = cfg_a.settings.get(k, "—")
            vb = cfg_b.settings.get(k, "—")
            if va != vb:
                diffs.append((k, va, vb))

        if not diffs:
            ctk.CTkLabel(self._hist_diff_fr, text="✅ Различий нет!",
                         font=T.F_LABEL, text_color=T.GREEN).pack(pady=4)
            return

        hdr = ctk.CTkFrame(self._hist_diff_fr, fg_color="transparent")
        hdr.pack(fill="x")
        hdr.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(hdr, text="Параметр", font=T.F_LABEL, text_color=T.TEXT).grid(
            row=0, column=0, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(hdr, text="Снапшот A", font=T.F_LABEL, text_color=T.BLUE).grid(
            row=0, column=1, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(hdr, text="Снапшот B", font=T.F_LABEL, text_color=T.ORANGE).grid(
            row=0, column=2, sticky="w", padx=4, pady=2)

        for i, (param, va, vb) in enumerate(diffs[:30], 1):
            ctk.CTkLabel(hdr, text=param, font=T.F_MONO, text_color=T.TEXT).grid(
                row=i, column=0, sticky="w", padx=4, pady=1)
            ctk.CTkLabel(hdr, text=str(va), font=T.F_MONO, text_color=T.BLUE).grid(
                row=i, column=1, sticky="w", padx=4, pady=1)
            ctk.CTkLabel(hdr, text=str(vb), font=T.F_MONO, text_color=T.ORANGE).grid(
                row=i, column=2, sticky="w", padx=4, pady=1)

        ctk.CTkLabel(self._hist_diff_fr, text=f"Всего различий: {len(diffs)}",
                     font=T.F_CAP, text_color=T.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

    def _hist_rollback(self, fn):
        try:
            label, cfg = load_history_snapshot(fn)
            self.current_config = cfg
            self._upd()
            self._toast(f"Rolled back to: {label}")
        except Exception as e:
            self._toast(str(e), "error")

    # _p_deploy + _dp_* + _cl_* → pages/deploy_page.py (DeployPageMixin)

    # ═══════════════════════════════════════════════ LAUNCH OPTIONS
    def _p_launch(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f680 Параметры запуска",
                  "Сборка параметров запуска Steam для hl.exe")

        c = self._card(fr, "\u2699  Options", collapsible=True)
        opts = [
            ("noforcemparms",  "Disable forced mouse params", "-noforcemparms -noforcemaccel -noforcemspd", True),
            ("nojoy",          "Disable joystick",            "-nojoy",        True),
            ("noipx",          "Disable IPX networking",      "-noipx",        True),
            ("gl",             "OpenGL renderer",             "-gl",           True),
            ("32bpp",          "32-bit color depth",          "-32bpp",        True),
            ("novid",          "Skip intro video",            "-novid",        True),
            ("console",        "Open console on start",       "-console",      False),
            ("stretchaspect",  "Stretch aspect ratio",        "-stretchaspect", False),
            ("nofbo",          "Disable framebuffer objects",  "-nofbo",       False),
            ("nomsaa",         "Disable MSAA",                "-nomsaa",       False),
            ("dev",            "Developer mode",              "-dev",          False),
        ]
        self._lo_vars: dict[str, tk.BooleanVar] = {}
        for i, (key, desc, _, default) in enumerate(opts):
            var = tk.BooleanVar(value=default)
            self._lo_vars[key] = var
            cb = ctk.CTkCheckBox(c, text=desc, variable=var, font=T.F_LABEL,
                                  text_color=T.TEXT, fg_color=T.BLUE,
                                  hover_color=T.BLUE_HOVER, border_color=T.BORDER,
                                  command=self._lo_update)
            cb.pack(anchor="w", padx=T.CARD_PAD, pady=3)

        c2 = self._card(fr, "\U0001f4bb  Custom Parameters", grid=True, collapsible=True)
        c2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(c2, text="Resolution", font=T.F_LABEL, text_color=T.TEXT,
                     width=120, anchor="w").grid(row=0, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=(8, 4))
        res_fr = ctk.CTkFrame(c2, fg_color="transparent")
        res_fr.grid(row=0, column=1, sticky="w", pady=(8, 4))
        self._lo_w = ctk.CTkEntry(res_fr, width=70, height=30, corner_radius=6,
                                   fg_color=T.BG_PRIMARY, border_color=T.BORDER, font=T.F_VAL)
        self._lo_w.pack(side="left")
        self._lo_w.insert(0, "1024")
        ctk.CTkLabel(res_fr, text=" x ", font=T.F_LABEL, text_color=T.TEXT_SEC).pack(side="left")
        self._lo_h = ctk.CTkEntry(res_fr, width=70, height=30, corner_radius=6,
                                   fg_color=T.BG_PRIMARY, border_color=T.BORDER, font=T.F_VAL)
        self._lo_h.pack(side="left")
        self._lo_h.insert(0, "768")

        ctk.CTkLabel(c2, text="Refresh Rate", font=T.F_LABEL, text_color=T.TEXT,
                     width=120, anchor="w").grid(row=1, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=4)
        self._lo_hz = ctk.CTkEntry(c2, width=70, height=30, corner_radius=6,
                                    fg_color=T.BG_PRIMARY, border_color=T.BORDER, font=T.F_VAL)
        self._lo_hz.grid(row=1, column=1, sticky="w", pady=4)
        self._lo_hz.insert(0, "75")
        ctk.CTkLabel(c2, text="Hz", font=T.F_CAP, text_color=T.TEXT_MUTED).grid(
            row=1, column=1, sticky="w", padx=(80, 0), pady=4)

        for w in (self._lo_w, self._lo_h, self._lo_hz):
            w.bind("<KeyRelease>", lambda e: self._lo_update())

        # Result
        rc = self._card(fr, "\U0001f4cb  Generated Launch Options")
        self._lo_result = ctk.CTkTextbox(rc, height=80, font=T.F_MONO,
                                          fg_color=T.BG_PRIMARY, border_width=1,
                                          border_color=T.BORDER, corner_radius=T.INPUT_R,
                                          wrap="word")
        self._lo_result.pack(fill="x", padx=T.CARD_PAD, pady=(8, 4))
        bf = ctk.CTkFrame(rc, fg_color="transparent")
        bf.pack(fill="x", padx=T.CARD_PAD, pady=(0, T.CARD_PAD))
        ctk.CTkButton(bf, text="\U0001f4cb  Copy to Clipboard", height=36,
                      corner_radius=T.BTN_R, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      font=T.F_LABEL, command=self._lo_copy).pack(side="left")

        self._lo_update()

    def _lo_update(self):
        opts_map = {
            "noforcemparms": "-noforcemparms -noforcemaccel -noforcemspd",
            "nojoy": "-nojoy", "noipx": "-noipx", "gl": "-gl", "32bpp": "-32bpp",
            "novid": "-novid", "console": "-console", "stretchaspect": "-stretchaspect",
            "nofbo": "-nofbo", "nomsaa": "-nomsaa", "dev": "-dev",
        }
        parts = []
        for key, flag in opts_map.items():
            if self._lo_vars.get(key) and self._lo_vars[key].get():
                parts.append(flag)
        try:
            w = int(self._lo_w.get())
            h = int(self._lo_h.get())
            parts.append(f"-w {w} -h {h}")
        except ValueError:
            pass
        try:
            hz = int(self._lo_hz.get())
            if hz > 0:
                parts.append(f"-freq {hz}")
        except ValueError:
            pass
        result = " ".join(parts)
        self._lo_result.configure(state="normal")
        self._lo_result.delete("1.0", "end")
        self._lo_result.insert("1.0", result)
        self._lo_result.configure(state="disabled")

    def _lo_copy(self):
        self.clipboard_clear()
        txt = self._lo_result.get("1.0", "end").strip()
        self.clipboard_append(txt)
        self._toast("Launch options copied to clipboard")
        log.info(f"Launch options copied: {txt}")

    # ═══════════════════════════════════════════════ LIVE PREVIEW (interactive)
    # _p_preview + _pv_* + _syntax_highlight → pages/preview_page.py (PreviewPageMixin)

    # ═══════════════════════════════════════════════ SETTINGS
    def _p_settings(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\u2699 Настройки", "Параметры приложения")

        # General
        c1 = self._card(fr, "\U0001f310  Общие", grid=True, collapsible=True)
        c1.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(c1, text="Язык", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=0, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=(8, 4))
        self._set_lang = ctk.CTkComboBox(c1, values=["Русский", "English"], width=200,
                                          state="readonly", corner_radius=T.INPUT_R,
                                          fg_color=T.BG_TERTIARY, border_color=T.BORDER)
        self._set_lang.grid(row=0, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=(8, 4))
        self._set_lang.set("Русский")

        ctk.CTkLabel(c1, text="Тема оформления", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=1, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=4)
        theme_names = {"midnight": "Midnight (тёмно-синяя)", "carbon": "Carbon (чёрная)",
                       "military": "Military (зелёная)", "retro_cs": "Retro CS (олива)"}
        tl = list(theme_names.values())
        self._set_theme = ctk.CTkComboBox(c1, values=tl, width=200, state="readonly",
                                           corner_radius=T.INPUT_R, fg_color=T.BG_TERTIARY,
                                           border_color=T.BORDER,
                                           command=self._on_theme_change)
        self._set_theme.grid(row=1, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=4)
        cur_label = theme_names.get(T.current_theme, tl[0])
        self._set_theme.set(cur_label)
        self._theme_map = {v: k for k, v in theme_names.items()}

        ctk.CTkLabel(c1, text="Режим по умолчанию", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=2, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=4)
        modes = get_modes()
        ml = [modes[k].get("name_ru", k) for k in modes]
        self._set_mode = ctk.CTkComboBox(c1, values=ml, width=200, state="readonly",
                                          corner_radius=T.INPUT_R, fg_color=T.BG_TERTIARY,
                                          border_color=T.BORDER)
        self._set_mode.grid(row=2, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=4)
        self._set_mode.set(ml[0])

        ctk.CTkLabel(c1, text="Папка вывода", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=3, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=4)
        from cfg_generator.io.exporter import OUTPUT_DIR
        od_fr = ctk.CTkFrame(c1, fg_color="transparent")
        od_fr.grid(row=3, column=1, sticky="we", padx=(0, T.CARD_PAD), pady=4)
        self._set_outdir = ctk.CTkEntry(od_fr, width=300, corner_radius=T.INPUT_R,
                                         fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                         font=T.F_CAP)
        self._set_outdir.pack(side="left", padx=(0, 4))
        self._set_outdir.insert(0, os.path.normpath(OUTPUT_DIR))
        self._set_outdir.configure(state="readonly")
        ctk.CTkButton(od_fr, text="...", width=36, height=28, corner_radius=6,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                      command=self._set_browse_dir).pack(side="left")

        # Export
        c2 = self._card(fr, "\U0001f4e4  Настройки экспорта", grid=True, collapsible=True)
        c2.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(c2, text="Формат по умолчанию", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=0, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=(8, 4))
        self._set_fmt = ctk.CTkComboBox(c2, values=["Single file", "Modular set"], width=200,
                                         state="readonly", corner_radius=T.INPUT_R,
                                         fg_color=T.BG_TERTIARY, border_color=T.BORDER)
        self._set_fmt.grid(row=0, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=(8, 4))
        self._set_fmt.set("Single file")

        ctk.CTkLabel(c2, text="Конец строки", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=1, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=4)
        self._set_le = ctk.CTkComboBox(c2, values=["LF (Unix)", "CRLF (Windows)"], width=200,
                                        state="readonly", corner_radius=T.INPUT_R,
                                        fg_color=T.BG_TERTIARY, border_color=T.BORDER)
        self._set_le.grid(row=1, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=4)
        self._set_le.set("LF (Unix)")

        self._set_ts = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(c2, text="Добавлять дату в комментарии", variable=self._set_ts,
                        font=T.F_LABEL, text_color=T.TEXT, fg_color=T.BLUE,
                        hover_color=T.BLUE_HOVER, border_color=T.BORDER).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=T.CARD_PAD, pady=4)

        self._set_sep = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(c2, text="Добавлять разделители секций", variable=self._set_sep,
                        font=T.F_LABEL, text_color=T.TEXT, fg_color=T.BLUE,
                        hover_color=T.BLUE_HOVER, border_color=T.BORDER).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=T.CARD_PAD, pady=(4, 8))

        # About
        c3 = self._card(fr, "\u2139\ufe0f  О программе")
        ctk.CTkLabel(c3, text=f"GoldSrc Config Engineer v{VERSION}",
                     font=T.F_H2, text_color=T.TEXT).pack(padx=T.CARD_PAD, pady=(8, 2))
        ctk.CTkLabel(c3, text="Профессиональный генератор конфигов CS 1.6",
                     font=T.F_CAP, text_color=T.TEXT_SEC).pack(padx=T.CARD_PAD, pady=(0, 4))
        ctk.CTkLabel(c3, text="Ctrl+S Save  |  Ctrl+G Generate  |  Ctrl+1..8 Navigate",
                     font=T.F_MONO, text_color=T.TEXT_MUTED).pack(padx=T.CARD_PAD, pady=(0, 4))

        log_dir = os.path.join(os.environ.get("APPDATA", "."), "GoldSrcConfigEngineer", "logs")
        ctk.CTkButton(c3, text="\U0001f4c2  Open Log Directory", height=34,
                      corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                      hover_color=T.BORDER, font=T.F_CAP,
                      command=lambda: os.startfile(log_dir) if os.path.exists(log_dir) else None).pack(
            padx=T.CARD_PAD, pady=(0, T.CARD_PAD))

    def _set_browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self._set_outdir.configure(state="normal")
            self._set_outdir.delete(0, "end")
            self._set_outdir.insert(0, d)
            self._set_outdir.configure(state="readonly")
            self._toast(f"Output dir: {d}", "info")

    def _on_theme_change(self, value: str):
        theme_key = self._theme_map.get(value, "midnight")
        T.set_theme(theme_key)
        self._toast(f"Тема «{value}» будет полностью применена при перезапуске", "info")


def run():
    mark("run() called")
    log.info(f"Starting GoldSrc Config Engineer v{VERSION}")
    app = App()
    mark("App created, entering mainloop")
    if "--profile-startup" in __import__("sys").argv:
        log.info("Startup timeline:\n" + format_timeline())
    app.mainloop()
