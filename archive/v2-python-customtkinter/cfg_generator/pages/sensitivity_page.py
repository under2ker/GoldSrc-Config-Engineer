"""Sensitivity Calculator page — extracted from gui.py."""

import customtkinter as ctk

from cfg_generator.theme import T

SCROLLBAR_KW = dict(
    scrollbar_button_color=T.BORDER,
    scrollbar_button_hover_color=T.TEXT_MUTED,
)


class SensitivityPageMixin:
    """Mixin providing _p_sensitivity, _sc_calc, _draw_pro_bar, _sc_convert."""

    def _p_sensitivity(self):
        fr = ctk.CTkScrollableFrame(self._content, fg_color=T.BG_PRIMARY, **SCROLLBAR_KW)
        fr.pack(fill="both", expand=True)
        self._hdr(fr, "\U0001f5b1 Калькулятор чувствительности",
                  "Расчёт eDPI, cm/360 и сравнение с профессионалами")

        c1 = self._card(fr, "\U0001f4ca  Input Parameters", grid=True)
        c1.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(c1, text="Mouse DPI", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=0, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=(T.CARD_PAD, 6))
        self._sc_dpi = ctk.CTkEntry(c1, width=100, height=32, corner_radius=6,
                                     fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                     font=T.F_VAL, justify="center")
        self._sc_dpi.grid(row=0, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=(T.CARD_PAD, 6))
        self._sc_dpi.insert(0, "800")

        ctk.CTkLabel(c1, text="Sensitivity", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=1, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=6)
        self._sc_sens = ctk.CTkEntry(c1, width=100, height=32, corner_radius=6,
                                      fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                      font=T.F_VAL, justify="center")
        self._sc_sens.grid(row=1, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=6)
        if self.current_config and self.current_config.settings.get("sensitivity"):
            self._sc_sens.insert(0, self.current_config.settings["sensitivity"])
        else:
            self._sc_sens.insert(0, "2.5")

        ctk.CTkLabel(c1, text="m_yaw", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=2, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=6)
        self._sc_yaw = ctk.CTkEntry(c1, width=100, height=32, corner_radius=6,
                                     fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                     font=T.F_VAL, justify="center")
        self._sc_yaw.grid(row=2, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=6)
        self._sc_yaw.insert(0, "0.022")

        ctk.CTkButton(c1, text="\U0001f4ca  Calculate", height=38, corner_radius=T.BTN_R,
                      fg_color=T.GREEN, hover_color=T.GREEN_HOVER, font=T.F_LABEL,
                      command=self._sc_calc).grid(
            row=3, column=0, columnspan=2, padx=T.CARD_PAD,
            pady=(8, T.CARD_PAD), sticky="we")

        c2 = self._card(fr, "\U0001f4cb  Results")
        self._sc_result_fr = ctk.CTkFrame(c2, fg_color="transparent")
        self._sc_result_fr.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))
        self._sc_edpi_lbl = ctk.CTkLabel(self._sc_result_fr, text="eDPI: —",
                                          font=ctk.CTkFont(size=20, weight="bold"),
                                          text_color=T.BLUE)
        self._sc_edpi_lbl.pack(anchor="w")
        self._sc_cm_lbl = ctk.CTkLabel(self._sc_result_fr, text="cm/360\u00b0: —",
                                        font=ctk.CTkFont(size=20, weight="bold"),
                                        text_color=T.GREEN)
        self._sc_cm_lbl.pack(anchor="w", pady=(4, 0))
        self._sc_range_lbl = ctk.CTkLabel(self._sc_result_fr, text="",
                                           font=T.F_BODY, text_color=T.TEXT_SEC)
        self._sc_range_lbl.pack(anchor="w", pady=(8, 0))

        c3 = self._card(fr, "\u2b50  Pro Player Comparison")
        self._sc_bar_fr = ctk.CTkFrame(c3, fg_color="transparent", height=80)
        self._sc_bar_fr.pack(fill="x", padx=T.CARD_PAD, pady=(8, T.CARD_PAD))

        c4 = self._card(fr, "\U0001f500  Game Converter", grid=True)
        c4.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(c4, text="From Game", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=0, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=(T.CARD_PAD, 6))
        self._sc_game = ctk.CTkComboBox(c4, values=["CS:GO", "Valorant", "Quake", "Overwatch"],
                                         width=160, state="readonly", corner_radius=T.INPUT_R,
                                         fg_color=T.BG_TERTIARY, border_color=T.BORDER)
        self._sc_game.grid(row=0, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=(T.CARD_PAD, 6))
        self._sc_game.set("CS:GO")

        ctk.CTkLabel(c4, text="Other Sens", font=T.F_LABEL, text_color=T.TEXT,
                     width=140, anchor="w").grid(row=1, column=0, sticky="w",
                     padx=(T.CARD_PAD, 8), pady=6)
        self._sc_other = ctk.CTkEntry(c4, width=100, height=32, corner_radius=6,
                                       fg_color=T.BG_PRIMARY, border_color=T.BORDER,
                                       font=T.F_VAL, justify="center")
        self._sc_other.grid(row=1, column=1, sticky="w", padx=(0, T.CARD_PAD), pady=6)
        self._sc_other.insert(0, "2.0")

        self._sc_conv_lbl = ctk.CTkLabel(c4, text="CS 1.6 equivalent: —",
                                          font=T.F_H2, text_color=T.ORANGE)
        self._sc_conv_lbl.grid(row=2, column=0, columnspan=2, sticky="w",
                               padx=T.CARD_PAD, pady=(4, 4))

        ctk.CTkButton(c4, text="\U0001f500  Convert", height=36, corner_radius=T.BTN_R,
                      fg_color=T.BLUE, hover_color=T.BLUE_HOVER, font=T.F_LABEL,
                      command=self._sc_convert).grid(
            row=3, column=0, columnspan=2, padx=T.CARD_PAD,
            pady=(4, T.CARD_PAD), sticky="we")

        c5 = self._card(fr, "\U0001f4d6  Recommended eDPI Ranges")
        ranges = [
            ("Competitive",  "800 – 1200 eDPI", T.GREEN),
            ("KZ / Bhop",    "1200 – 2000 eDPI", T.BLUE),
            ("Surf",         "600 – 1000 eDPI", T.ORANGE),
            ("AWP Focus",    "600 – 900 eDPI", T.RED),
        ]
        for name, rng, color in ranges:
            row = ctk.CTkFrame(c5, fg_color="transparent")
            row.pack(fill="x", padx=T.CARD_PAD, pady=2)
            ctk.CTkLabel(row, text=f"\u25cf  {name}", font=T.F_LABEL,
                         text_color=color, width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=rng, font=T.F_MONO, text_color=T.TEXT_SEC).pack(side="left")
        ctk.CTkFrame(c5, height=8, fg_color="transparent").pack()

        self._sc_calc()

    def _sc_calc(self):
        try:
            dpi = float(self._sc_dpi.get())
            sens = float(self._sc_sens.get())
            yaw = float(self._sc_yaw.get())
        except ValueError:
            self._sc_edpi_lbl.configure(text="eDPI: invalid input")
            return

        edpi = dpi * sens
        cm360 = (2.54 * 360) / (dpi * sens * yaw) if (dpi * sens * yaw) != 0 else 0

        self._sc_edpi_lbl.configure(text=f"eDPI: {edpi:.0f}")
        self._sc_cm_lbl.configure(text=f"cm/360\u00b0: {cm360:.1f} cm")

        if edpi < 600:
            note = "Very low — extremely precise but slow turns"
        elif edpi < 1000:
            note = "Low — great for AWP players, precise aim"
        elif edpi < 1500:
            note = "Optimal competitive range"
        elif edpi < 2500:
            note = "Medium-high — good for KZ/movement"
        else:
            note = "Very high — fast but may sacrifice precision"
        self._sc_range_lbl.configure(text=note)

        self._draw_pro_bar(edpi)

    def _draw_pro_bar(self, user_edpi: float):
        for w in self._sc_bar_fr.winfo_children():
            w.destroy()

        pros = [
            ("f0rest", 1200), ("neo", 1600), ("SpawN", 2800),
            ("markeloff", 1400), ("HeatoN", 1520), ("Edward", 1800),
            ("cogu", 1600), ("starix", 1440), ("ave", 1520),
        ]

        min_e = min(p[1] for p in pros) * 0.5
        max_e = max(p[1] for p in pros) * 1.3
        bar_w = 500

        track = ctk.CTkFrame(self._sc_bar_fr, height=12, fg_color=T.BG_TERTIARY,
                              corner_radius=6)
        track.pack(fill="x", pady=(12, 0))

        for name, edpi in pros:
            pct = max(0, min(1, (edpi - min_e) / (max_e - min_e)))
            x_px = int(pct * bar_w)
            marker = ctk.CTkLabel(self._sc_bar_fr, text="\u25b2", font=ctk.CTkFont(size=10),
                                   text_color=T.TEXT_MUTED, width=10)
            marker.place(x=x_px, y=26)
            lbl = ctk.CTkLabel(self._sc_bar_fr, text=name, font=ctk.CTkFont(size=9),
                                text_color=T.TEXT_MUTED)
            lbl.place(x=x_px - 10, y=38)

        user_pct = max(0, min(1, (user_edpi - min_e) / (max_e - min_e)))
        user_x = int(user_pct * bar_w)
        you = ctk.CTkLabel(self._sc_bar_fr, text="\u25bc YOU", font=ctk.CTkFont(size=11, weight="bold"),
                            text_color=T.GREEN, width=40)
        you.place(x=max(0, user_x - 15), y=0)

    def _sc_convert(self):
        try:
            other_sens = float(self._sc_other.get())
        except ValueError:
            self._sc_conv_lbl.configure(text="CS 1.6 equivalent: invalid input")
            return
        game = self._sc_game.get()
        multipliers = {
            "CS:GO": 1.0,
            "Valorant": 3.18,
            "Quake": 0.5625,
            "Overwatch": 3.33,
        }
        factor = multipliers.get(game, 1.0)
        cs16_sens = other_sens * factor
        self._sc_conv_lbl.configure(text=f"CS 1.6 equivalent: {cs16_sens:.2f}")
