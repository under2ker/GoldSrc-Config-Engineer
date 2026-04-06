"""Deploy to Game page — extracted from gui.py."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from cfg_generator.theme import T
from cfg_generator.core.generator import generate_single_cfg
from cfg_generator.core.game_bridge import (
    find_game_path, is_game_running, get_hl_window,
    deploy_config_files, deploy_userconfig, exec_in_game,
    deploy_and_exec, get_cstrike_path,
    CLEAN_CATEGORIES, scan_cleanup, execute_cleanup, _size_fmt,
)

SCROLLBAR_KW = dict(
    scrollbar_button_color=T.BORDER,
    scrollbar_button_hover_color=T.TEXT_MUTED,
)


class DeployPageMixin:
    """Mixin providing _p_deploy and all _dp_* / _cl_* helpers."""

    def _p_deploy(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f3ae Загрузка в игру",
                  "Установка конфига в папку CS 1.6 и отправка exec в запущенную игру")

        c_path = self._card(fr, "\U0001f4c2  Путь к CS 1.6")
        path_row = ctk.CTkFrame(c_path, fg_color="transparent")
        path_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, 4))

        self._dp_path = ctk.CTkEntry(path_row, width=440, corner_radius=T.INPUT_R,
                                      fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                      placeholder_text="Путь к папке с hl.exe...")
        self._dp_path.pack(side="left", padx=(0, 6))

        ctk.CTkButton(path_row, text="Обзор", width=80, corner_radius=T.BTN_R,
                      fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                      command=self._dp_browse).pack(side="left", padx=(0, 6))
        ctk.CTkButton(path_row, text="Автопоиск", width=100, corner_radius=T.BTN_R,
                      fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      command=self._dp_autodetect).pack(side="left")

        self._dp_path_status = ctk.CTkLabel(c_path, text="", font=T.F_CAP,
                                             text_color=T.TEXT_MUTED)
        self._dp_path_status.pack(anchor="w", padx=T.CARD_PAD, pady=(0, 8))

        detected = find_game_path()
        if detected:
            self._dp_path.insert(0, detected)
            self._dp_path_status.configure(
                text=f"✅ Обнаружен: {detected}", text_color=T.GREEN)
        else:
            self._dp_path_status.configure(
                text="⚠️ CS 1.6 не обнаружена — укажите путь вручную", text_color=T.ORANGE)

        c_status = self._card(fr, "\U0001f4e1  Статус игры")
        st_row = ctk.CTkFrame(c_status, fg_color="transparent")
        st_row.pack(fill="x", padx=T.CARD_PAD, pady=(8, 4))

        self._dp_status_dot = ctk.CTkLabel(st_row, text="●", font=ctk.CTkFont(size=18),
                                            text_color=T.TEXT_MUTED, width=24)
        self._dp_status_dot.pack(side="left")
        self._dp_status_txt = ctk.CTkLabel(st_row, text="Проверка...", font=T.F_LABEL,
                                            text_color=T.TEXT)
        self._dp_status_txt.pack(side="left", padx=(4, 0))

        ctk.CTkButton(st_row, text="⟳ Обновить", width=100, height=28,
                      corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                      hover_color=T.BORDER, font=T.F_CAP,
                      command=self._dp_refresh_status).pack(side="right")

        self._dp_hl_info = ctk.CTkLabel(c_status, text="", font=T.F_CAP,
                                         text_color=T.TEXT_MUTED)
        self._dp_hl_info.pack(anchor="w", padx=T.CARD_PAD, pady=(0, 8))
        self._dp_refresh_status()

        c_deploy = self._card(fr, "\U0001f680  Действия")

        if not self.current_config:
            ctk.CTkLabel(c_deploy, text="⚠️ Конфиг не загружен. Сначала создайте конфиг.",
                         font=T.F_BODY, text_color=T.ORANGE).pack(
                padx=T.CARD_PAD, pady=T.CARD_PAD)
        else:
            btn_grid = ctk.CTkFrame(c_deploy, fg_color="transparent")
            btn_grid.pack(fill="x", padx=T.CARD_PAD, pady=(8, 4))
            btn_grid.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkButton(btn_grid, text="📥  Записать autoexec.cfg в cstrike/",
                          height=44, corner_radius=T.BTN_R,
                          fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                          font=ctk.CTkFont(size=13, weight="bold"),
                          command=self._dp_deploy_autoexec).grid(
                row=0, column=0, padx=(0, 4), pady=4, sticky="we")

            ctk.CTkButton(btn_grid, text="📥  Записать userconfig.cfg",
                          height=44, corner_radius=T.BTN_R,
                          fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                          font=ctk.CTkFont(size=13, weight="bold"),
                          command=self._dp_deploy_userconfig).grid(
                row=0, column=1, padx=(4, 0), pady=4, sticky="we")

            ctk.CTkButton(btn_grid, text="🚀  Записать и отправить exec в игру",
                          height=50, corner_radius=T.BTN_R,
                          fg_color="#8B5CF6", hover_color="#7C3AED",
                          font=ctk.CTkFont(size=14, weight="bold"),
                          command=self._dp_deploy_and_exec).grid(
                row=1, column=0, columnspan=2, padx=0, pady=(4, 4), sticky="we")

            info_text = (
                "💡  autoexec.cfg — выполняется при каждом запуске игры\n"
                "💡  userconfig.cfg — выполняется при смене карты / подключении\n"
                "💡  «Записать и отправить exec» — запишет файл и отправит команду exec прямо в консоль CS 1.6\n"
                "⚠️  Для отправки exec игра должна быть запущена и иметь привязку консоли на клавишу ~ (тильда)"
            )
            ctk.CTkLabel(c_deploy, text=info_text, font=T.F_CAP,
                         text_color=T.TEXT_MUTED, justify="left",
                         wraplength=600).pack(anchor="w", padx=T.CARD_PAD, pady=(4, 8))

        c_opts = self._card(fr, "⚙  Параметры деплоя")
        self._dp_backup = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(c_opts, text="Создать резервную копию перед перезаписью",
                        variable=self._dp_backup, font=T.F_LABEL, text_color=T.TEXT,
                        fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                        border_color=T.BORDER).pack(
            anchor="w", padx=T.CARD_PAD, pady=(8, 4))

        self._dp_exec_close = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(c_opts, text="Закрывать консоль после exec (~)",
                        variable=self._dp_exec_close, font=T.F_LABEL, text_color=T.TEXT,
                        fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                        border_color=T.BORDER).pack(
            anchor="w", padx=T.CARD_PAD, pady=(0, 8))

        c_clean = self._card(fr, "🧹  Очистка клиента")
        ctk.CTkLabel(c_clean, text="Удаление мусора, грязных конфигов, скачанного контента и временных файлов",
                     font=T.F_CAP, text_color=T.TEXT_SEC).pack(
            anchor="w", padx=T.CARD_PAD, pady=(0, 6))

        self._cl_vars: dict[str, tk.BooleanVar] = {}
        cl_scroll = ctk.CTkScrollableFrame(c_clean, height=220, fg_color=T.BG_PRIMARY,
                                            corner_radius=T.INPUT_R, **SCROLLBAR_KW)
        cl_scroll.pack(fill="x", padx=T.CARD_PAD, pady=(0, 4))

        for cat_key, cat in CLEAN_CATEGORIES.items():
            var = tk.BooleanVar(value=cat.get("default", False))
            self._cl_vars[cat_key] = var
            row_fr = ctk.CTkFrame(cl_scroll, fg_color="transparent")
            row_fr.pack(fill="x", pady=1)
            ctk.CTkCheckBox(row_fr, text=cat["label"], variable=var,
                            font=T.F_LABEL, text_color=T.TEXT,
                            fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                            border_color=T.BORDER).pack(anchor="w", padx=(4, 4))
            ctk.CTkLabel(row_fr, text=cat["description"], font=T.F_CAP,
                         text_color=T.TEXT_MUTED).pack(anchor="w", padx=(30, 4))

        cl_btn_row = ctk.CTkFrame(c_clean, fg_color="transparent")
        cl_btn_row.pack(fill="x", padx=T.CARD_PAD, pady=(4, 4))

        ctk.CTkButton(cl_btn_row, text="🔍  Сканировать", height=36,
                      corner_radius=T.BTN_R, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._dp_clean_scan).pack(side="left", padx=(0, 6))

        ctk.CTkButton(cl_btn_row, text="🧹  Очистить клиент", height=36,
                      corner_radius=T.BTN_R, fg_color=T.RED, hover_color="#DC2626",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._dp_clean_execute).pack(side="left", padx=(0, 6))

        ctk.CTkButton(cl_btn_row, text="Выбрать всё", height=28, width=100,
                      corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                      hover_color=T.BORDER, font=T.F_CAP,
                      command=lambda: self._dp_clean_toggle(True)).pack(side="right", padx=(4, 0))
        ctk.CTkButton(cl_btn_row, text="Снять всё", height=28, width=100,
                      corner_radius=T.BTN_R, fg_color=T.BG_CARD_HOVER,
                      hover_color=T.BORDER, font=T.F_CAP,
                      command=lambda: self._dp_clean_toggle(False)).pack(side="right")

        self._cl_result_lbl = ctk.CTkLabel(c_clean, text="", font=T.F_CAP,
                                            text_color=T.TEXT_MUTED, justify="left",
                                            wraplength=600)
        self._cl_result_lbl.pack(anchor="w", padx=T.CARD_PAD, pady=(0, 8))

        c_log = self._card(fr, "\U0001f4cb  Лог операций")
        self._dp_log = ctk.CTkTextbox(c_log, height=120, font=T.F_MONO,
                                       fg_color=T.BG_PRIMARY, border_width=1,
                                       border_color=T.BORDER, corner_radius=T.INPUT_R,
                                       wrap="word")
        self._dp_log.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        self._dp_log.insert("1.0", "Готов к работе...\n")
        self._dp_log.configure(state="disabled")

    def _dp_log_msg(self, msg: str):
        self._dp_log.configure(state="normal")
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._dp_log.insert("end", f"[{ts}] {msg}\n")
        self._dp_log.see("end")
        self._dp_log.configure(state="disabled")

    def _dp_browse(self):
        d = filedialog.askdirectory(title="Выберите папку CS 1.6 (где лежит hl.exe)")
        if not d:
            return
        hl = os.path.join(d, "hl.exe")
        cs = os.path.join(d, "cstrike")
        if os.path.isfile(hl) and os.path.isdir(cs):
            self._dp_path.delete(0, "end")
            self._dp_path.insert(0, d)
            self._dp_path_status.configure(
                text="✅ Путь подтверждён: hl.exe и cstrike/ найдены", text_color=T.GREEN)
        else:
            self._dp_path_status.configure(
                text="❌ В выбранной папке не найден hl.exe или cstrike/", text_color=T.RED)

    def _dp_autodetect(self):
        detected = find_game_path()
        if detected:
            self._dp_path.delete(0, "end")
            self._dp_path.insert(0, detected)
            self._dp_path_status.configure(
                text=f"✅ Обнаружен: {detected}", text_color=T.GREEN)
            self._toast("CS 1.6 найдена автоматически")
        else:
            self._dp_path_status.configure(
                text="❌ Не удалось найти CS 1.6. Укажите путь вручную.", text_color=T.RED)
            self._toast("CS 1.6 не найдена", "warning")

    def _dp_refresh_status(self):
        running = is_game_running()
        if running:
            hwnd = get_hl_window()
            self._dp_status_dot.configure(text_color=T.GREEN)
            self._dp_status_txt.configure(text="CS 1.6 запущена", text_color=T.GREEN)
            wnd_info = f"Окно найдено (HWND: {hwnd})" if hwnd else "Процесс найден, окно не обнаружено"
            self._dp_hl_info.configure(text=f"hl.exe запущен  •  {wnd_info}")
        else:
            self._dp_status_dot.configure(text_color=T.RED)
            self._dp_status_txt.configure(text="CS 1.6 не запущена", text_color=T.TEXT_MUTED)
            self._dp_hl_info.configure(text="Процесс hl.exe не обнаружен")

    def _dp_get_game_path(self) -> str | None:
        gp = self._dp_path.get().strip()
        if not gp:
            self._toast("Укажите путь к CS 1.6", "warning")
            return None
        if not os.path.isfile(os.path.join(gp, "hl.exe")):
            self._toast("hl.exe не найден в указанной папке", "error")
            return None
        if not os.path.isdir(os.path.join(gp, "cstrike")):
            self._toast("Папка cstrike/ не найдена", "error")
            return None
        return gp

    def _dp_make_backup(self, game_path: str):
        cs = get_cstrike_path(game_path)
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        for fn in ("autoexec.cfg", "userconfig.cfg"):
            src = os.path.join(cs, fn)
            if os.path.isfile(src):
                backup_dir = os.path.join(cs, "config_backups")
                os.makedirs(backup_dir, exist_ok=True)
                dst = os.path.join(backup_dir, f"{fn}.bak_{ts}")
                import shutil
                shutil.copy2(src, dst)
                self._dp_log_msg(f"Бэкап: {fn} → config_backups/{os.path.basename(dst)}")

    def _dp_deploy_autoexec(self):
        if not self.current_config:
            self._toast("Нет конфига для загрузки", "warning")
            return
        gp = self._dp_get_game_path()
        if not gp:
            return
        try:
            if self._dp_backup.get():
                self._dp_make_backup(gp)
            cfg_text = generate_single_cfg(self.current_config)
            written = deploy_config_files(gp, cfg_text)
            self._dp_log_msg(f"✅ Записано {len(written)} файлов в cstrike/")
            self._dp_log_msg(f"   Главный: {written[0]}")
            self._toast(f"autoexec.cfg записан в {get_cstrike_path(gp)}")
        except Exception as e:
            self._dp_log_msg(f"❌ Ошибка: {e}")
            self._toast(str(e), "error")

    def _dp_deploy_userconfig(self):
        if not self.current_config:
            self._toast("Нет конфига для загрузки", "warning")
            return
        gp = self._dp_get_game_path()
        if not gp:
            return
        try:
            if self._dp_backup.get():
                self._dp_make_backup(gp)
            cfg_text = generate_single_cfg(self.current_config)
            path = deploy_userconfig(gp, cfg_text)
            self._dp_log_msg("✅ Записан userconfig.cfg")
            self._dp_log_msg(f"   Путь: {path}")
            self._toast("userconfig.cfg записан — применится при смене карты")
        except Exception as e:
            self._dp_log_msg(f"❌ Ошибка: {e}")
            self._toast(str(e), "error")

    def _dp_deploy_and_exec(self):
        if not self.current_config:
            self._toast("Нет конфига для загрузки", "warning")
            return
        gp = self._dp_get_game_path()
        if not gp:
            return
        try:
            if self._dp_backup.get():
                self._dp_make_backup(gp)
            cfg_text = generate_single_cfg(self.current_config)
            ok, msg = deploy_and_exec(gp, cfg_text)
            for line in msg.split("\n"):
                self._dp_log_msg(line)
            self._dp_refresh_status()
            if ok:
                self._toast("Конфиг загружен в игру!", "success")
            else:
                self._toast(msg, "error")
        except Exception as e:
            self._dp_log_msg(f"❌ Ошибка: {e}")
            self._toast(str(e), "error")

    def _dp_clean_toggle(self, state: bool):
        for var in self._cl_vars.values():
            var.set(state)

    def _dp_clean_scan(self):
        gp = self._dp_get_game_path()
        if not gp:
            return
        selected = [k for k, v in self._cl_vars.items() if v.get()]
        if not selected:
            self._toast("Выберите хотя бы одну категорию", "warning")
            return
        result = scan_cleanup(gp, selected)
        self._cl_scan_result = result
        total_files = sum(d["count"] for d in result.values())
        total_size = sum(d["size"] for d in result.values())

        lines = []
        for cat_key, data in result.items():
            cat = CLEAN_CATEGORIES[cat_key]
            if data["count"] > 0:
                lines.append(f"  • {cat['label']}: {data['count']} объектов, {_size_fmt(data['size'])}")
            else:
                lines.append(f"  • {cat['label']}: чисто ✓")

        summary = (
            f"📊 Результат сканирования:\n"
            + "\n".join(lines)
            + f"\n\n  Итого: {total_files} объектов, {_size_fmt(total_size)}"
        )
        self._cl_result_lbl.configure(text=summary)
        self._dp_log_msg(f"Сканирование: найдено {total_files} объектов ({_size_fmt(total_size)})")

    def _dp_clean_execute(self):
        gp = self._dp_get_game_path()
        if not gp:
            return
        selected = [k for k, v in self._cl_vars.items() if v.get()]
        if not selected:
            self._toast("Выберите хотя бы одну категорию", "warning")
            return

        if is_game_running():
            ok = messagebox.askokcancel(
                "CS 1.6 запущена",
                "CS 1.6 сейчас запущена.\n"
                "Рекомендуется закрыть игру перед очисткой.\n\n"
                "Продолжить всё равно?",
            )
            if not ok:
                return

        result = scan_cleanup(gp, selected)
        total_files = sum(d["count"] for d in result.values())
        total_size = sum(d["size"] for d in result.values())

        if total_files == 0:
            self._toast("Нечего удалять — клиент чистый", "info")
            self._dp_log_msg("Очистка: нечего удалять")
            return

        ok = messagebox.askyesno(
            "Подтверждение очистки",
            f"Будет удалено {total_files} объектов ({_size_fmt(total_size)}).\n"
            f"Конфиги будут сохранены в config_backups/.\n\n"
            f"Продолжить?",
        )
        if not ok:
            return

        self._dp_log_msg(f"🧹 Начало очистки ({total_files} объектов)...")
        removed, freed, errors = execute_cleanup(gp, result, backup=self._dp_backup.get())
        self._dp_log_msg(f"✅ Удалено: {removed} объектов, освобождено {_size_fmt(freed)}")
        if errors:
            for err in errors:
                self._dp_log_msg(f"⚠️ {err}")
            self._toast(f"Очистка завершена с {len(errors)} ошибками", "warning")
        else:
            self._toast(f"Клиент очищен! Удалено {removed} объектов, освобождено {_size_fmt(freed)}")
        self._cl_result_lbl.configure(
            text=f"✅ Очистка завершена: удалено {removed} объектов, освобождено {_size_fmt(freed)}")
