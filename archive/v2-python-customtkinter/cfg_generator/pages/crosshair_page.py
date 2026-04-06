"""Crosshair Editor page — extracted from gui.py."""

import os
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from cfg_generator.theme import T
from cfg_generator.components.crosshair_canvas import (
    CrosshairCanvas, BACKGROUNDS, COLOR_PRESETS, CROSSHAIR_PRESETS,
)

SCROLLBAR_KW = dict(
    scrollbar_button_color=T.BORDER,
    scrollbar_button_hover_color=T.TEXT_MUTED,
)


class CrosshairPageMixin:
    """Mixin providing _p_crosshair and all _xh_* helpers."""

    def _p_crosshair(self):
        from tkinter import colorchooser

        fr = ctk.CTkFrame(self._content, fg_color=T.BG_PRIMARY)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\u271b Редактор прицела",
                  "Визуальный редактор — настройте и примените к конфигу")

        body = ctk.CTkFrame(fr, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=T.CONTENT_PX, pady=(8, 0))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)

        # ── LEFT: Canvas + bottom panels ──
        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))

        xh = CrosshairCanvas(left, width=380, height=380)
        xh.pack(pady=(4, 4))
        self._xh = xh

        bg_fr = ctk.CTkFrame(left, fg_color="transparent")
        bg_fr.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(bg_fr, text="Background:", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left", padx=(0, 4))
        self._xh_bg = ctk.CTkComboBox(
            bg_fr, values=list(BACKGROUNDS.keys()) + ["Custom"], width=100, height=26,
            state="readonly", corner_radius=6, font=ctk.CTkFont(size=11),
            fg_color=T.BG_TERTIARY, border_color=T.BORDER,
            command=lambda v: xh.set_background(v))
        self._xh_bg.pack(side="left", padx=(0, 8))
        self._xh_bg.set("Dark")

        ctk.CTkLabel(bg_fr, text="Zoom:", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left", padx=(0, 4))
        zoom_sl = ctk.CTkSlider(bg_fr, from_=2, to=8, number_of_steps=12, width=100,
                                 progress_color=T.BLUE, button_color="#FFF",
                                 button_hover_color=T.BLUE_HOVER,
                                 command=lambda v: xh.update_param("zoom", int(v)))
        zoom_sl.set(4)
        zoom_sl.pack(side="left", padx=(0, 4))
        self._xh_zoom_lbl = ctk.CTkLabel(bg_fr, text="4x", font=T.F_CAP,
                                           text_color=T.TEXT_MUTED)
        self._xh_zoom_lbl.pack(side="left")
        def _zoom_cmd(v):
            iv = int(v)
            self._xh_zoom_lbl.configure(text=f"{iv}x")
            self._debounce("xh_zoom", 16, lambda: xh.update_param("zoom", iv))
        zoom_sl.configure(command=_zoom_cmd)

        sim_fr = ctk.CTkFrame(left, fg_color="transparent")
        sim_fr.pack(fill="x", pady=(0, 4))
        ctk.CTkButton(sim_fr, text="\U0001f52b  Shoot", width=80, height=28,
                      corner_radius=6, fg_color=T.ORANGE, hover_color="#E5A82E",
                      font=ctk.CTkFont(size=11),
                      command=xh.simulate_shot).pack(side="left", padx=(0, 4))
        ctk.CTkButton(sim_fr, text="\U0001f4a5  Burst", width=80, height=28,
                      corner_radius=6, fg_color=T.RED, hover_color="#D32F2F",
                      font=ctk.CTkFont(size=11),
                      command=xh.simulate_burst).pack(side="left", padx=(0, 4))
        ctk.CTkButton(sim_fr, text="\U0001f504  Reset", width=80, height=28,
                      corner_radius=6, fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                      font=ctk.CTkFont(size=11),
                      command=lambda: (setattr(xh, "_anim_offset", 0), xh.draw())).pack(
            side="left", padx=(0, 4))
        self._xh_auto_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(sim_fr, text="Auto-animate", variable=self._xh_auto_var,
                        font=ctk.CTkFont(size=11), text_color=T.TEXT_SEC,
                        fg_color=T.BLUE, border_color=T.BORDER,
                        command=self._xh_toggle_auto).pack(side="left", padx=8)

        tools_fr = ctk.CTkFrame(left, fg_color="transparent")
        tools_fr.pack(fill="x", pady=(0, 4))
        ctk.CTkButton(tools_fr, text="📷 Save PNG", width=90, height=28,
                      corner_radius=6, fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                      font=ctk.CTkFont(size=11),
                      command=self._xh_export_png).pack(side="left", padx=(0, 4))
        ctk.CTkButton(tools_fr, text="↔ Side-by-Side", width=100, height=28,
                      corner_radius=6, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      font=ctk.CTkFont(size=11),
                      command=self._xh_side_by_side).pack(side="left", padx=(0, 4))
        ctk.CTkButton(tools_fr, text="👤 Силуэт", width=80, height=28,
                      corner_radius=6, fg_color=T.ORANGE, hover_color="#E5A82E",
                      font=ctk.CTkFont(size=11),
                      command=self._xh_toggle_silhouette).pack(side="left")

        pr_fr = ctk.CTkFrame(left, fg_color=T.BG_TERTIARY, corner_radius=8,
                              border_width=1, border_color=T.BORDER)
        pr_fr.pack(fill="x", pady=(4, 4))
        ctk.CTkLabel(pr_fr, text="Presets:", font=T.F_CAP,
                     text_color=T.TEXT_MUTED).pack(side="left", padx=(8, 4), pady=4)
        for name, preset in CROSSHAIR_PRESETS.items():
            ctk.CTkButton(pr_fr, text=name, width=0, height=24, corner_radius=6,
                          fg_color=T.BG_CARD_HOVER, hover_color=T.BORDER,
                          font=ctk.CTkFont(size=10),
                          command=lambda p=preset: self._xh_load_preset(p)).pack(
                side="left", padx=2, pady=4)

        code_fr = ctk.CTkFrame(left, fg_color=T.BG_TERTIARY, corner_radius=8,
                                border_width=1, border_color=T.BORDER)
        code_fr.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(code_fr, text="Generated Config", font=T.F_CAP,
                     text_color=T.TEXT_MUTED).pack(anchor="w", padx=8, pady=(6, 0))
        self._xh_code = ctk.CTkTextbox(code_fr, height=90, font=T.F_MONO,
                                        fg_color=T.BG_PRIMARY, border_width=0,
                                        corner_radius=6, wrap="none")
        self._xh_code.pack(fill="x", padx=8, pady=(4, 4))
        code_btn_fr = ctk.CTkFrame(code_fr, fg_color="transparent")
        code_btn_fr.pack(fill="x", padx=8, pady=(0, 6))
        ctk.CTkButton(code_btn_fr, text="\U0001f4cb Copy", width=70, height=26,
                      corner_radius=6, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      font=ctk.CTkFont(size=11),
                      command=self._xh_copy_code).pack(side="left", padx=(0, 4))
        ctk.CTkButton(code_btn_fr, text="\u2705 Применить", width=70, height=26,
                      corner_radius=6, fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                      font=ctk.CTkFont(size=11),
                      command=self._xh_apply).pack(side="left", padx=(0, 4))
        self._xh_info = ctk.CTkLabel(code_btn_fr, text="", font=T.F_CAP,
                                      text_color=T.TEXT_MUTED)
        self._xh_info.pack(side="right")

        # ── RIGHT: Controls panel ──
        right = ctk.CTkScrollableFrame(body, width=280, fg_color=T.BG_SECONDARY,
                                        corner_radius=T.CARD_R, **SCROLLBAR_KW)
        right.grid(row=0, column=1, sticky="nswe")

        sh = ctk.CTkFrame(right, fg_color=T.BG_TERTIARY, corner_radius=8,
                           border_width=1, border_color=T.BORDER)
        sh.pack(fill="x", padx=6, pady=(6, 4))
        ctk.CTkLabel(sh, text="\u271b  Shape", font=T.F_H2, text_color=T.TEXT).pack(
            anchor="w", padx=10, pady=(8, 4))

        ctk.CTkLabel(sh, text="Size", font=T.F_CAP, text_color=T.TEXT_SEC).pack(
            anchor="w", padx=10, pady=(4, 0))
        self._xh_size_seg = ctk.CTkSegmentedButton(
            sh, values=["Small", "Medium", "Large"], height=28,
            font=ctk.CTkFont(size=11), selected_color=T.BLUE,
            unselected_color=T.BG_CARD_HOVER,
            command=self._xh_size_change)
        self._xh_size_seg.pack(fill="x", padx=10, pady=4)
        self._xh_size_seg.set("Medium")

        for label, attr, lo, hi, default in [
            ("Thickness", "thickness", 1, 6, 2),
            ("Gap", "gap", 0, 20, 4),
            ("Length", "length", 1, 20, 6),
        ]:
            row_fr = ctk.CTkFrame(sh, fg_color="transparent")
            row_fr.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row_fr, text=label, font=T.F_CAP,
                         text_color=T.TEXT_SEC, width=70, anchor="w").pack(side="left")
            val_lbl = ctk.CTkLabel(row_fr, text=str(default), font=T.F_MONO,
                                    text_color=T.TEXT, width=24)
            val_lbl.pack(side="right")
            sl = ctk.CTkSlider(row_fr, from_=lo, to=hi, number_of_steps=hi - lo, width=120,
                                progress_color=T.BLUE, button_color="#FFF",
                                button_hover_color=T.BLUE_HOVER)
            sl.set(default)
            sl.pack(side="right", padx=4)
            def _sl_cmd(v, a=attr, lb=val_lbl):
                iv = int(v)
                lb.configure(text=str(iv))
                self._debounce(f"xh_{a}", 16, lambda: (
                    xh.update_param(a, iv), self._xh_refresh_code()))
            sl.configure(command=_sl_cmd)

        dot_fr = ctk.CTkFrame(sh, fg_color="transparent")
        dot_fr.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(dot_fr, text="Center Dot", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left")
        self._xh_dot_sw = ctk.CTkSwitch(dot_fr, text="", width=40,
                                          fg_color=T.BORDER, progress_color=T.BLUE,
                                          command=lambda: (
                                              xh.update_param("show_dot", self._xh_dot_sw.get()),
                                              self._xh_refresh_code()))
        self._xh_dot_sw.pack(side="right")

        ts_fr = ctk.CTkFrame(sh, fg_color="transparent")
        ts_fr.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkLabel(ts_fr, text="T-Style", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left")
        self._xh_ts_sw = ctk.CTkSwitch(ts_fr, text="", width=40,
                                         fg_color=T.BORDER, progress_color=T.BLUE,
                                         command=lambda: (
                                             xh.update_param("t_style", self._xh_ts_sw.get()),
                                             self._xh_refresh_code()))
        self._xh_ts_sw.pack(side="right")

        cl = ctk.CTkFrame(right, fg_color=T.BG_TERTIARY, corner_radius=8,
                           border_width=1, border_color=T.BORDER)
        cl.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(cl, text="\U0001f3a8  Color", font=T.F_H2, text_color=T.TEXT).pack(
            anchor="w", padx=10, pady=(8, 4))

        color_row = ctk.CTkFrame(cl, fg_color="transparent")
        color_row.pack(fill="x", padx=10, pady=4)
        self._xh_color_btns = []
        for hex_c, name, _ in COLOR_PRESETS:
            btn = ctk.CTkButton(color_row, text="", width=30, height=30, corner_radius=6,
                                fg_color=hex_c, hover_color=hex_c, border_width=2,
                                border_color=T.BORDER,
                                command=lambda c=hex_c: self._xh_set_color(c))
            btn.pack(side="left", padx=2)
            self._tip(btn, name)
            self._xh_color_btns.append((btn, hex_c))

        ctk.CTkButton(cl, text="\U0001f3a8  Custom Color...", height=28,
                      corner_radius=6, fg_color="transparent",
                      border_width=1, border_color=T.BORDER,
                      font=ctk.CTkFont(size=11), text_color=T.TEXT_SEC,
                      command=lambda: self._xh_custom_color(colorchooser)).pack(
            fill="x", padx=10, pady=4)

        outline_fr = ctk.CTkFrame(cl, fg_color="transparent")
        outline_fr.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkLabel(outline_fr, text="Outline", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left")
        self._xh_outline_sw = ctk.CTkSwitch(outline_fr, text="", width=40,
                                              fg_color=T.BORDER, progress_color=T.BLUE)
        self._xh_outline_sw.select()
        self._xh_outline_sw.configure(
            command=lambda: (xh.update_param("show_outline", self._xh_outline_sw.get()),
                             self._xh_refresh_code()))
        self._xh_outline_sw.pack(side="right")

        bh = ctk.CTkFrame(right, fg_color=T.BG_TERTIARY, corner_radius=8,
                           border_width=1, border_color=T.BORDER)
        bh.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(bh, text="\u2699  Behavior", font=T.F_H2, text_color=T.TEXT).pack(
            anchor="w", padx=10, pady=(8, 4))

        dyn_fr = ctk.CTkFrame(bh, fg_color="transparent")
        dyn_fr.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(dyn_fr, text="Dynamic", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left")
        self._xh_dyn_sw = ctk.CTkSwitch(dyn_fr, text="", width=40,
                                          fg_color=T.BORDER, progress_color=T.BLUE,
                                          command=lambda: (
                                              xh.update_param("dynamic", self._xh_dyn_sw.get()),
                                              self._xh_refresh_code()))
        self._xh_dyn_sw.pack(side="right")

        self._xh_dyn_warn = ctk.CTkLabel(bh, text="\u26a0\ufe0f Not recommended for competitive",
                                           font=ctk.CTkFont(size=10), text_color=T.ORANGE)

        trans_fr = ctk.CTkFrame(bh, fg_color="transparent")
        trans_fr.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkLabel(trans_fr, text="Translucent", font=T.F_CAP,
                     text_color=T.TEXT_SEC).pack(side="left")
        self._xh_trans_sw = ctk.CTkSwitch(trans_fr, text="", width=40,
                                            fg_color=T.BORDER, progress_color=T.BLUE,
                                            command=lambda: (
                                                xh.update_param("translucent", self._xh_trans_sw.get()),
                                                self._xh_refresh_code()))
        self._xh_trans_sw.pack(side="right")

        sc = ctk.CTkFrame(right, fg_color=T.BG_TERTIARY, corner_radius=8,
                           border_width=1, border_color=T.BORDER)
        sc.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(sc, text="\U0001f517  Share", font=T.F_H2, text_color=T.TEXT).pack(
            anchor="w", padx=10, pady=(8, 4))
        ctk.CTkButton(sc, text="\U0001f517  Copy Share Code", height=28,
                      corner_radius=6, fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
                      font=ctk.CTkFont(size=11),
                      command=self._xh_share).pack(fill="x", padx=10, pady=4)
        imp_row = ctk.CTkFrame(sc, fg_color="transparent")
        imp_row.pack(fill="x", padx=10, pady=(0, 8))
        self._xh_share_entry = ctk.CTkEntry(imp_row, placeholder_text="CSXH-...", height=28,
                                              corner_radius=6, fg_color=T.BG_PRIMARY,
                                              border_color=T.BORDER, font=ctk.CTkFont(size=11))
        self._xh_share_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(imp_row, text="Import", width=56, height=28, corner_radius=6,
                      fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
                      font=ctk.CTkFont(size=11),
                      command=self._xh_import_share).pack(side="left")

        ctk.CTkLabel(right, text="Preview is an approximation.\n"
                     "CS 1.6 crosshair rendering depends\non resolution and renderer.",
                     font=ctk.CTkFont(size=9), text_color=T.TEXT_MUTED,
                     wraplength=250, justify="left").pack(padx=10, pady=(4, 8))

        self._xh_refresh_code()

    # ── crosshair editor helpers ──

    def _xh_refresh_code(self):
        if not hasattr(self, "_xh"):
            return
        txt = self._xh.get_config_text()
        self._xh_code.configure(state="normal")
        self._xh_code.delete("1.0", "end")
        self._xh_code.insert("1.0", txt)
        self._xh_code.configure(state="disabled")
        n = len(self._xh.get_config_lines())
        sz = self._xh.get_size_name()
        self._xh_info.configure(text=f"Commands: {n}  |  Size: {sz}")

    def _xh_load_preset(self, preset: dict):
        self._xh.load_preset(preset)
        self._xh_refresh_code()

    def _xh_set_color(self, hex_c: str):
        self._xh.update_param("color", hex_c)
        for btn, c in self._xh_color_btns:
            btn.configure(border_color=T.BLUE if c == hex_c else T.BORDER)
        self._xh_refresh_code()

    def _xh_custom_color(self, colorchooser_mod):
        result = colorchooser_mod.askcolor(color=self._xh.color, title="Pick Crosshair Color")
        if result and result[1]:
            self._xh_set_color(result[1].upper())

    def _xh_size_change(self, value: str):
        defaults = {"Small": (1, 3, 4), "Medium": (2, 4, 6), "Large": (3, 6, 9)}
        t, g, l = defaults.get(value, (2, 4, 6))
        self._xh.thickness = t
        self._xh.gap = g
        self._xh.length = l
        self._xh.draw()
        self._xh_refresh_code()

    def _xh_toggle_auto(self):
        if self._xh_auto_var.get():
            self._xh.dynamic = True
            self._xh.start_auto_animate()
        else:
            self._xh.stop_auto_animate()

    def _xh_copy_code(self):
        txt = self._xh.get_config_text()
        self.clipboard_clear()
        self.clipboard_append(txt)
        self._toast("Crosshair config copied")

    def _xh_apply(self):
        self._ensure()
        for line in self._xh.get_config_lines():
            parts = line.split(None, 1)
            if len(parts) == 2:
                cvar = parts[0]
                val = parts[1].strip('"')
                self.current_config.set(cvar, val)
        self._upd()
        self._toast("Crosshair applied to config")

    def _xh_share(self):
        code = self._xh.to_share_code()
        self.clipboard_clear()
        self.clipboard_append(code)
        self._toast(f"Share code copied: {code[:20]}...")

    def _xh_import_share(self):
        code = self._xh_share_entry.get().strip()
        if not code:
            return
        if self._xh.from_share_code(code):
            self._xh_refresh_code()
            self._toast("Crosshair imported from share code")
        else:
            self._toast("Invalid share code", "error")

    def _xh_export_png(self):
        p = filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[("PNG", "*.png")], initialfile="crosshair.png")
        if not p:
            return
        try:
            canvas = self._xh.canvas
            ps = canvas.postscript(colormode="color")
            try:
                from PIL import Image, EpsImagePlugin
                EpsImagePlugin.gs_windows_binary = None
                img = Image.open(__import__("io").BytesIO(ps.encode("utf-8")))
                img.save(p, "PNG")
            except ImportError:
                ps_path = p.replace(".png", ".ps")
                with open(ps_path, "w") as f:
                    f.write(ps)
                self._toast(f"Saved as PostScript (PIL not installed): {ps_path}")
                return
            self._toast(f"Прицел сохранён: {os.path.basename(p)}")
        except Exception as e:
            self._toast(str(e), "error")

    def _xh_side_by_side(self):
        win = ctk.CTkToplevel(self)
        win.title("Сравнение прицелов — Side by Side")
        win.geometry("840x440")
        win.configure(fg_color=T.BG_PRIMARY)
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Ваш прицел", font=T.F_H2,
                     text_color=T.BLUE).grid(row=0, column=0, padx=20, pady=(10, 0))
        ctk.CTkLabel(win, text="Пресет", font=T.F_H2,
                     text_color=T.ORANGE).grid(row=0, column=1, padx=20, pady=(10, 0))

        xh1 = CrosshairCanvas(win, width=380, height=380)
        xh1.grid(row=1, column=0, padx=10, pady=10)
        for attr in ("color", "thickness", "gap", "length", "show_dot",
                     "show_outline", "t_style", "translucent", "dynamic"):
            setattr(xh1, attr, getattr(self._xh, attr))
        xh1._dirty = True
        xh1.draw()

        xh2 = CrosshairCanvas(win, width=380, height=380)
        xh2.grid(row=1, column=1, padx=10, pady=10)

        preset_fr = ctk.CTkFrame(win, fg_color="transparent")
        preset_fr.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        ctk.CTkLabel(preset_fr, text="Пресет:", font=T.F_LABEL,
                     text_color=T.TEXT).pack(side="left", padx=(0, 6))
        preset_names = list(CROSSHAIR_PRESETS.keys())
        cb = ctk.CTkComboBox(preset_fr, values=preset_names, width=160,
                              state="readonly", corner_radius=T.INPUT_R,
                              fg_color=T.BG_TERTIARY, border_color=T.BORDER)
        cb.pack(side="left")
        cb.set(preset_names[0])
        xh2.load_preset(CROSSHAIR_PRESETS[preset_names[0]])

        def _on_preset(name):
            preset = CROSSHAIR_PRESETS.get(name)
            if preset:
                xh2.load_preset(preset)
        cb.configure(command=_on_preset)

    def _xh_toggle_silhouette(self):
        xh = self._xh
        if hasattr(xh, "_silhouette_on") and xh._silhouette_on:
            xh._silhouette_on = False
            xh._dirty = True
            xh.draw()
            return
        xh._silhouette_on = True
        canvas = xh.canvas
        cx = canvas.winfo_width() // 2
        cy = canvas.winfo_height() // 2

        head_r = 8 * xh.zoom // 2
        body_h = 35 * xh.zoom // 2
        body_w = 14 * xh.zoom // 2
        canvas.create_oval(cx - head_r, cy - head_r - body_h // 2,
                           cx + head_r, cy + head_r - body_h // 2,
                           outline="#FF4444", width=2, stipple="gray50",
                           tags="silhouette")
        canvas.create_rectangle(cx - body_w, cy - body_h // 2 + head_r,
                                cx + body_w, cy + body_h // 2 + head_r,
                                outline="#FF4444", width=2, stipple="gray50",
                                tags="silhouette")
