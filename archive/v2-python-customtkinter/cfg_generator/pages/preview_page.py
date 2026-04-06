"""Live Preview page — extracted from gui.py."""

import re
import tkinter as tk

import customtkinter as ctk

from cfg_generator.theme import T
from cfg_generator.core.generator import (
    get_all_cvars, get_aliases, get_buyscripts,
)

SCROLLBAR_KW = dict(
    scrollbar_button_color=T.BORDER,
    scrollbar_button_hover_color=T.TEXT_MUTED,
)


class PreviewPageMixin:
    """Mixin providing _p_preview, _pv_*, and _syntax_highlight."""

    def _p_preview(self):
        fr = ctk.CTkFrame(self._content, fg_color=T.BG_PRIMARY)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f4c4 Просмотр конфига",
                  "Включайте/выключайте бинды, алиасы и настройки — код обновляется в реальном времени")

        if not self.current_config:
            c = self._card(fr)
            ctk.CTkLabel(c, text="Конфиг не загружен. Сначала создайте его.",
                         font=T.F_BODY, text_color=T.ORANGE).pack(padx=T.CARD_PAD, pady=T.CARD_PAD)
            return

        self._ensure()
        self._pv_vars: dict[str, tk.BooleanVar] = {}

        body = ctk.CTkFrame(fr, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=T.CONTENT_PX, pady=(8, 0))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left_tabs = ctk.CTkTabview(body, fg_color=T.BG_TERTIARY,
                                    segmented_button_fg_color=T.BG_SECONDARY,
                                    segmented_button_selected_color=T.BLUE,
                                    segmented_button_unselected_color=T.BG_SECONDARY)
        left_tabs.grid(row=0, column=0, sticky="nswe", padx=(0, 6))

        tab_binds = left_tabs.add("Бинды")
        sc_binds = ctk.CTkScrollableFrame(tab_binds, fg_color="transparent", **SCROLLBAR_KW)
        sc_binds.pack(fill="both", expand=True)
        cfg = self.current_config

        tab_aliases = left_tabs.add("Алиасы")
        sc_aliases = ctk.CTkScrollableFrame(tab_aliases, fg_color="transparent", **SCROLLBAR_KW)
        sc_aliases.pack(fill="both", expand=True)

        tab_settings = left_tabs.add("Настройки")
        sc_settings = ctk.CTkScrollableFrame(tab_settings, fg_color="transparent", **SCROLLBAR_KW)
        sc_settings.pack(fill="both", expand=True)
        cat_names = {"network": "Сеть", "video": "Видео", "audio": "Звук",
                     "input": "Мышь", "gameplay": "Геймплей/HUD", "other": "Прочее"}
        cvars_db = get_all_cvars()
        cvar_to_cat: dict[str, str] = {}
        for cat, cvs in cvars_db.items():
            for cn in cvs:
                cvar_to_cat[cn] = cat
        categorized: dict[str, list[tuple[str, str]]] = {}
        for cvar, val in sorted(cfg.settings.items()):
            cat = cvar_to_cat.get(cvar, "other")
            categorized.setdefault(cat, []).append((cvar, val))

        tab_buy = left_tabs.add("Buy-скрипты")
        sc_buy = ctk.CTkScrollableFrame(tab_buy, fg_color="transparent", **SCROLLBAR_KW)
        sc_buy.pack(fill="both", expand=True)

        self._ui_chunk_gen = getattr(self, "_ui_chunk_gen", 0) + 1
        _pv_gen = self._ui_chunk_gen

        aliases_db = get_aliases()
        sec_names = {"movement": "Движение", "weapon": "Оружие",
                     "communication": "Коммуникация", "utility": "Утилиты",
                     "kz_specific": "KZ", "surf_specific": "Сёрф",
                     "practice": "Тренировка"}

        alias_flat: list = []
        for sec_key, sec_data in aliases_db.items():
            alias_list = sec_data.get("aliases", [])
            if not alias_list:
                continue
            alias_flat.append(("ah", sec_key))
            for a in alias_list:
                alias_flat.append(("aa", sec_key, a))

        settings_flat: list = []
        for cat in ["network", "video", "audio", "input", "gameplay", "other"]:
            items = categorized.get(cat)
            if not items:
                continue
            settings_flat.append(("sh", cat))
            for cvar, val in items:
                settings_flat.append(("sr", cvar, val))

        bind_rows: list[tuple[str, str, str]] = []
        for key, cmd in sorted(cfg.binds.items()):
            bind_rows.append(("bind", key, cmd))
        if cfg.buy_binds:
            bind_rows.append(("bh", "", ""))
            for key, cmd in sorted(cfg.buy_binds.items()):
                bind_rows.append(("bbind", key, cmd))

        buy_presets = list(get_buyscripts().get("presets", {}).items())

        def add_bind_row(row: tuple, _idx: int):
            if _pv_gen != self._ui_chunk_gen:
                return
            kind = row[0]
            if kind == "bind":
                _, key, cmd = row
                var = tk.BooleanVar(value=True)
                self._pv_vars[f"bind_{key}"] = var
                ctk.CTkCheckBox(sc_binds, text=f'bind "{key}" "{cmd}"',
                                variable=var, font=T.F_MONO, text_color=T.TEXT,
                                fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                                border_color=T.BORDER, height=24,
                                command=self._pv_refresh).pack(anchor="w", padx=6, pady=1)
            elif kind == "bh":
                ctk.CTkLabel(sc_binds, text="── Buy-бинды ──", font=T.F_CAP,
                             text_color=T.ORANGE).pack(anchor="w", padx=6, pady=(8, 2))
            else:
                _, key, cmd = row
                var = tk.BooleanVar(value=True)
                self._pv_vars[f"buybind_{key}"] = var
                ctk.CTkCheckBox(sc_binds, text=f'bind "{key}" "{cmd}"',
                                variable=var, font=T.F_MONO, text_color=T.TEXT,
                                fg_color=T.ORANGE, hover_color="#E5A82E",
                                border_color=T.BORDER, height=24,
                                command=self._pv_refresh).pack(anchor="w", padx=6, pady=1)

        def add_alias_row(row, _idx: int):
            if _pv_gen != self._ui_chunk_gen:
                return
            if row[0] == "ah":
                sec_key = row[1]
                ctk.CTkLabel(sc_aliases, text=f"── {sec_names.get(sec_key, sec_key)} ──",
                             font=T.F_CAP, text_color=T.ORANGE).pack(anchor="w", padx=6, pady=(6, 2))
                return
            _x, sec_key, a = row
            name = a.get("name", "")
            desc = a.get("description", name)
            safety = a.get("safety", "SAFE")
            var = tk.BooleanVar(value=(safety == "SAFE" and sec_key in ("movement", "weapon", "utility")))
            self._pv_vars[f"alias_{sec_key}_{name}"] = var
            color = T.GREEN if safety == "SAFE" else T.ORANGE if safety == "WAIT" else T.RED
            ctk.CTkCheckBox(sc_aliases, text=f"[{safety}] {name} — {desc}",
                            variable=var, font=ctk.CTkFont(size=11),
                            text_color=T.TEXT, fg_color=color,
                            hover_color=T.BLUE_HOVER, border_color=T.BORDER,
                            height=22, command=self._pv_refresh).pack(
                anchor="w", padx=6, pady=1)

        def add_settings_row(row, _idx: int):
            if _pv_gen != self._ui_chunk_gen:
                return
            if row[0] == "sh":
                cat = row[1]
                ctk.CTkLabel(sc_settings, text=f"── {cat_names.get(cat, cat)} ──",
                             font=T.F_CAP, text_color=T.BLUE).pack(anchor="w", padx=6, pady=(6, 2))
                return
            _x, cvar, val = row
            var = tk.BooleanVar(value=True)
            self._pv_vars[f"cvar_{cvar}"] = var
            ctk.CTkCheckBox(sc_settings, text=f'{cvar} "{val}"',
                            variable=var, font=T.F_MONO, text_color=T.TEXT,
                            fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                            border_color=T.BORDER, height=22,
                            command=self._pv_refresh).pack(anchor="w", padx=6, pady=1)

        def add_buy_row(item: tuple, _idx: int):
            if _pv_gen != self._ui_chunk_gen:
                return
            key, preset = item
            var = tk.BooleanVar(value=True)
            self._pv_vars[f"buyalias_{key}"] = var
            desc = preset.get("description", preset.get("name", key))
            ctk.CTkCheckBox(sc_buy, text=f"{key} — {desc}",
                            variable=var, font=ctk.CTkFont(size=11),
                            text_color=T.TEXT, fg_color=T.GREEN,
                            hover_color=T.GREEN_HOVER, border_color=T.BORDER,
                            height=22, command=self._pv_refresh).pack(
                anchor="w", padx=6, pady=1)

        def finish_preview():
            if _pv_gen != self._ui_chunk_gen:
                return
            self._pv_refresh()

        def phase_buy():
            self._ui_chunked(buy_presets, 24, add_buy_row, on_done=finish_preview, cancel_gen=_pv_gen)

        def phase_settings():
            self._ui_chunked(settings_flat, 32, add_settings_row, on_done=phase_buy, cancel_gen=_pv_gen)

        def phase_aliases():
            self._ui_chunked(alias_flat, 28, add_alias_row, on_done=phase_settings, cancel_gen=_pv_gen)

        def phase_binds():
            self._ui_chunked(bind_rows, 36, add_bind_row, on_done=phase_aliases, cancel_gen=_pv_gen)

        phase_binds()

        right_fr = ctk.CTkFrame(body, fg_color=T.BG_TERTIARY, corner_radius=T.CARD_R,
                                 border_width=1, border_color=T.BORDER)
        right_fr.grid(row=0, column=1, sticky="nswe", padx=(6, 0))
        ctk.CTkLabel(right_fr, text="\U0001f4c4  Сгенерированный код", font=T.F_H2,
                     text_color=T.TEXT).pack(anchor="w", padx=12, pady=(8, 4))
        self._pv_code = ctk.CTkTextbox(right_fr, font=T.F_MONO, fg_color=T.BG_PRIMARY,
                                        border_width=1, border_color=T.BORDER,
                                        corner_radius=T.INPUT_R, wrap="none")
        self._pv_code.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        btn_fr = ctk.CTkFrame(right_fr, fg_color="transparent")
        btn_fr.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkButton(btn_fr, text="\U0001f4cb  Копировать", height=32, corner_radius=T.BTN_R,
                      fg_color=T.BLUE, hover_color=T.BLUE_HOVER, font=T.F_LABEL,
                      command=self._pv_copy_code).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btn_fr, text="\u2705  Применить к конфигу", height=32, corner_radius=T.BTN_R,
                      fg_color=T.GREEN, hover_color=T.GREEN_HOVER, font=T.F_LABEL,
                      command=self._pv_apply).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btn_fr, text="\u2611  Все ВКЛ", height=32, width=80, corner_radius=T.BTN_R,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER, font=ctk.CTkFont(size=11),
                      command=lambda: self._pv_toggle_all(True)).pack(side="right", padx=(4, 0))
        ctk.CTkButton(btn_fr, text="\u2610  Все ВЫКЛ", height=32, width=80, corner_radius=T.BTN_R,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER, font=ctk.CTkFont(size=11),
                      command=lambda: self._pv_toggle_all(False)).pack(side="right")
        self._pv_count_lbl = ctk.CTkLabel(right_fr, text="", font=T.F_CAP,
                                            text_color=T.TEXT_MUTED)
        self._pv_count_lbl.pack(padx=12, pady=(0, 4))

    def _pv_refresh(self):
        self._debounce("pv_refresh", 100, self._pv_refresh_impl)

    def _pv_refresh_impl(self):
        if not hasattr(self, "_pv_vars"):
            return
        lines: list[str] = []
        lines.append("// ================================================================")
        lines.append("// Конфиг собран в GoldSrc Config Engineer")
        lines.append("// ================================================================")
        lines.append("")

        active_cvars = 0
        active_binds = 0
        active_aliases = 0

        settings_lines: dict[str, list[str]] = {}
        for key, var in self._pv_vars.items():
            if not var.get():
                continue
            if key.startswith("cvar_"):
                cvar = key[5:]
                val = self.current_config.settings.get(cvar, "")
                cat = "settings"
                settings_lines.setdefault(cat, []).append(f'{cvar} "{val}"')
                active_cvars += 1

        if settings_lines.get("settings"):
            lines.append("// === НАСТРОЙКИ ===")
            lines.extend(settings_lines["settings"])
            lines.append("")

        bind_lines = []
        for key, var in self._pv_vars.items():
            if not var.get():
                continue
            if key.startswith("bind_"):
                bk = key[5:]
                cmd = self.current_config.binds.get(bk, "")
                bind_lines.append(f'bind "{bk}" "{cmd}"')
                active_binds += 1
            elif key.startswith("buybind_"):
                bk = key[8:]
                cmd = self.current_config.buy_binds.get(bk, "")
                bind_lines.append(f'bind "{bk}" "{cmd}"')
                active_binds += 1
        if bind_lines:
            lines.append("// === БИНДЫ ===")
            lines.extend(bind_lines)
            lines.append("")

        alias_lines = []
        aliases_db = get_aliases()
        for key, var in self._pv_vars.items():
            if not var.get():
                continue
            if key.startswith("alias_"):
                parts = key[6:].split("_", 1)
                if len(parts) == 2:
                    sec_key, name = parts
                    sec_data = aliases_db.get(sec_key, {})
                    for a in sec_data.get("aliases", []):
                        if a.get("name") == name:
                            if "plus" in a:
                                alias_lines.append(f'alias "{name}" "{a["plus"]}"')
                                minus = name.replace("+", "-", 1)
                                alias_lines.append(f'alias "{minus}" "{a["minus"]}"')
                            elif a.get("command"):
                                alias_lines.append(f'alias "{name}" "{a["command"]}"')
                            active_aliases += 1
                            break
        if alias_lines:
            lines.append("// === АЛИАСЫ ===")
            lines.extend(alias_lines)
            lines.append("")

        buy_lines = []
        bs = get_buyscripts()
        for key, var in self._pv_vars.items():
            if not var.get():
                continue
            if key.startswith("buyalias_"):
                bk = key[9:]
                preset = bs.get("presets", {}).get(bk)
                if preset:
                    buy_lines.append(f'alias "{bk}" "{preset["commands"]}"')
        if buy_lines:
            lines.append("// === BUY-СКРИПТЫ ===")
            lines.extend(buy_lines)
            lines.append("")

        code = "\n".join(lines)
        self._pv_code.configure(state="normal")
        self._pv_code.delete("1.0", "end")
        self._pv_code.insert("1.0", code)
        self._syntax_highlight(self._pv_code)
        self._pv_code.configure(state="disabled")

        total = active_cvars + active_binds + active_aliases
        self._pv_count_lbl.configure(
            text=f"Активно: {active_cvars} настроек, {active_binds} биндов, {active_aliases} алиасов  |  {len(code.splitlines())} строк")

    def _pv_copy_code(self):
        txt = self._pv_code.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(txt)
        self._toast(f"Скопировано ({len(txt.splitlines())} строк)")

    def _pv_apply(self):
        self._ensure()
        for key, var in self._pv_vars.items():
            if key.startswith("cvar_") and not var.get():
                cvar = key[5:]
                self.current_config.remove(cvar)
            if key.startswith("bind_") and not var.get():
                bk = key[5:]
                self.current_config.binds.pop(bk, None)
            if key.startswith("buybind_") and not var.get():
                bk = key[8:]
                self.current_config.buy_binds.pop(bk, None)
        self._upd()
        self._toast("Конфиг обновлён по выбранным элементам")

    def _pv_toggle_all(self, state: bool):
        for var in self._pv_vars.values():
            var.set(state)
        self._pv_refresh()

    def _syntax_highlight(self, tb: ctk.CTkTextbox):
        tb.tag_config("comment",  foreground="#6A9955")
        tb.tag_config("command",  foreground="#569CD6")
        tb.tag_config("value",    foreground="#CE9178")
        tb.tag_config("exec_cmd", foreground="#C586C0")
        tb.tag_config("section",  foreground="#DCDCAA")

        content = tb.get("1.0", "end")
        for i, line in enumerate(content.splitlines(), 1):
            idx = f"{i}.0"
            end = f"{i}.{len(line)}"
            stripped = line.lstrip()
            if stripped.startswith("// ===") or stripped.startswith("// ---"):
                tb.tag_add("section", idx, end)
            elif stripped.startswith("//"):
                tb.tag_add("comment", idx, end)
            elif stripped.startswith("exec "):
                tb.tag_add("exec_cmd", idx, end)
            else:
                m = re.match(r'^(bind|alias|unbindall)\b', stripped, re.I)
                if m:
                    tb.tag_add("command", idx, f"{i}.{len(line) - len(line.lstrip()) + m.end()}")
                m2 = re.findall(r'"([^"]*)"', line)
                for val in m2:
                    start = line.find(f'"{val}"')
                    if start >= 0:
                        tb.tag_add("value", f"{i}.{start}", f"{i}.{start + len(val) + 2}")
                parts = stripped.split(None, 1)
                if parts and not stripped.startswith("//") and not stripped.startswith("bind") and not stripped.startswith("alias"):
                    cmd = parts[0]
                    if not cmd.startswith('"'):
                        tb.tag_add("command", f"{i}.{len(line) - len(stripped)}", f"{i}.{len(line) - len(stripped) + len(cmd)}")
