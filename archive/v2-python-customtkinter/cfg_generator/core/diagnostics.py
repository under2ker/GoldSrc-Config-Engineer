"""
Config Diagnostics — automated analysis, scoring, and recommendations.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from cfg_generator.core.generator import CfgConfig, get_all_cvars


@dataclass
class DiagnosticItem:
    severity: str          # "ok", "warning", "error", "info"
    category: str          # "Network", "Mouse", "Video", "Audio", "Binds", "General"
    message: str
    fix_key: Optional[str] = None
    fix_value: Optional[str] = None


@dataclass
class DiagnosticReport:
    items: list[DiagnosticItem] = field(default_factory=list)
    score: int = 100

    @property
    def ok_count(self) -> int:
        return sum(1 for i in self.items if i.severity == "ok")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.items if i.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.items if i.severity == "error")


def _g(cfg: CfgConfig, key: str, default: str = "") -> str:
    return cfg.settings.get(key, default)


def _gf(cfg: CfgConfig, key: str, default: float = 0.0) -> float:
    try:
        return float(cfg.settings.get(key, str(default)))
    except (ValueError, TypeError):
        return default


def _gi(cfg: CfgConfig, key: str, default: int = 0) -> int:
    try:
        return int(float(cfg.settings.get(key, str(default))))
    except (ValueError, TypeError):
        return default


def run_diagnostics(cfg: CfgConfig) -> DiagnosticReport:
    """Run all diagnostic checks and return a scored report."""
    report = DiagnosticReport()
    items = report.items
    penalty = 0

    # ── Network ──
    rate = _gi(cfg, "rate", 0)
    if rate == 0:
        items.append(DiagnosticItem("error", "Network", "rate is 0 — no data will be received",
                                    "rate", "25000"))
        penalty += 15
    elif rate < 10000:
        items.append(DiagnosticItem("warning", "Network",
                                    f"rate ({rate}) is low — may cause lag, recommended 25000",
                                    "rate", "25000"))
        penalty += 5
    else:
        items.append(DiagnosticItem("ok", "Network", f"rate ({rate}) is adequate"))

    cmdrate = _gi(cfg, "cl_cmdrate", 0)
    if cmdrate > 0 and cmdrate < 50:
        items.append(DiagnosticItem("warning", "Network",
                                    f"cl_cmdrate ({cmdrate}) is low — recommended 101",
                                    "cl_cmdrate", "101"))
        penalty += 5
    elif cmdrate >= 50:
        items.append(DiagnosticItem("ok", "Network", f"cl_cmdrate ({cmdrate}) OK"))

    updrate = _gi(cfg, "cl_updaterate", 0)
    if updrate > 0 and updrate < 50:
        items.append(DiagnosticItem("warning", "Network",
                                    f"cl_updaterate ({updrate}) is low — recommended 101",
                                    "cl_updaterate", "101"))
        penalty += 5
    elif updrate >= 50:
        items.append(DiagnosticItem("ok", "Network", f"cl_updaterate ({updrate}) OK"))

    interp = _gf(cfg, "ex_interp", -1)
    if interp > 0.05:
        items.append(DiagnosticItem("warning", "Network",
                                    f"ex_interp ({interp}) too high — recommended 0.01",
                                    "ex_interp", "0.01"))
        penalty += 5
    elif 0 < interp <= 0.05:
        items.append(DiagnosticItem("ok", "Network", f"ex_interp ({interp}) OK"))

    # ── Mouse ──
    rawinput = _gi(cfg, "m_rawinput", -1)
    if rawinput == 0:
        items.append(DiagnosticItem("warning", "Mouse",
                                    "m_rawinput is OFF — raw input recommended for consistent aim",
                                    "m_rawinput", "1"))
        penalty += 5
    elif rawinput == 1:
        items.append(DiagnosticItem("ok", "Mouse", "Raw input enabled"))

    sens = _gf(cfg, "sensitivity", 0)
    if sens > 0:
        if sens < 0.5:
            items.append(DiagnosticItem("warning", "Mouse",
                                        f"Sensitivity ({sens}) extremely low — may be unusable"))
            penalty += 3
        elif sens > 10:
            items.append(DiagnosticItem("warning", "Mouse",
                                        f"Sensitivity ({sens}) very high — most pros use 1.5–3.5"))
            penalty += 3
        elif 1.0 <= sens <= 4.0:
            items.append(DiagnosticItem("ok", "Mouse",
                                        f"Sensitivity ({sens}) in pro range (1.0–4.0)"))
        else:
            items.append(DiagnosticItem("info", "Mouse",
                                        f"Sensitivity ({sens}) outside typical pro range (1.0–4.0)"))

    m_filter = _gi(cfg, "m_filter", -1)
    if m_filter == 1:
        items.append(DiagnosticItem("info", "Mouse",
                                    "Mouse filter is ON — adds slight smoothing"))

    # ── Video / Performance ──
    fps_max = _gi(cfg, "fps_max", 0)
    if fps_max == 0:
        items.append(DiagnosticItem("error", "Video",
                                    "fps_max is 0 — game may run unstable",
                                    "fps_max", "100"))
        penalty += 10
    elif fps_max > 500:
        items.append(DiagnosticItem("info", "Video",
                                    f"fps_max ({fps_max}) very high — may cause instability on older hardware"))
    elif fps_max < 30:
        items.append(DiagnosticItem("warning", "Video",
                                    f"fps_max ({fps_max}) extremely low",
                                    "fps_max", "100"))
        penalty += 8
    else:
        items.append(DiagnosticItem("ok", "Video", f"fps_max ({fps_max}) OK"))

    developer = _gi(cfg, "developer", 0)
    if developer >= 1:
        items.append(DiagnosticItem("warning", "Video",
                                    "developer mode is enabled — disable for normal play",
                                    "developer", "0"))
        penalty += 3

    dynamic_xhair = _gi(cfg, "cl_dynamiccrosshair", -1)
    if dynamic_xhair == 1:
        items.append(DiagnosticItem("warning", "Video",
                                    "cl_dynamiccrosshair is ON — not recommended for competitive",
                                    "cl_dynamiccrosshair", "0"))
        penalty += 3
    elif dynamic_xhair == 0:
        items.append(DiagnosticItem("ok", "Video", "Dynamic crosshair disabled"))

    # ── Audio ──
    volume = _gf(cfg, "volume", -1)
    if volume > 0.9:
        items.append(DiagnosticItem("warning", "Audio",
                                    f"Volume ({volume}) very high — may miss footstep nuances"))
        penalty += 2
    elif 0 < volume <= 0.9:
        items.append(DiagnosticItem("ok", "Audio", f"Volume ({volume}) OK"))

    # ── Binds ──
    bind_cmds: dict[str, list[str]] = {}
    for key, cmd in cfg.binds.items():
        bind_cmds.setdefault(cmd, []).append(key)
    for key, cmd in cfg.buy_binds.items():
        bind_cmds.setdefault(cmd, []).append(key)

    conflicting = {k: keys for k, keys in bind_cmds.items() if len(keys) > 1}
    if conflicting:
        for cmd, keys in list(conflicting.items())[:3]:
            items.append(DiagnosticItem("info", "Binds",
                                        f"Multiple keys for '{cmd}': {', '.join(keys)}"))
    else:
        if cfg.binds:
            items.append(DiagnosticItem("ok", "Binds", "No conflicting binds detected"))

    # ── General completeness ──
    if not cfg.binds:
        items.append(DiagnosticItem("warning", "General",
                                    "No binds configured — you may want to load a mode"))
        penalty += 5

    total_cvars = len(cfg.settings)
    if total_cvars < 5:
        items.append(DiagnosticItem("warning", "General",
                                    f"Only {total_cvars} CVARs — config may be incomplete"))
        penalty += 5
    elif total_cvars >= 15:
        items.append(DiagnosticItem("ok", "General",
                                    f"{total_cvars} CVARs configured — comprehensive config"))

    # ── cl_lc / cl_lw ──
    cl_lc = _gi(cfg, "cl_lc", -1)
    if cl_lc == 0:
        items.append(DiagnosticItem("error", "Network",
                                    "cl_lc is 0 — lag compensation disabled, hit registration will suffer",
                                    "cl_lc", "1"))
        penalty += 10
    elif cl_lc == 1:
        items.append(DiagnosticItem("ok", "Network", "Lag compensation enabled"))

    cl_lw = _gi(cfg, "cl_lw", -1)
    if cl_lw == 0:
        items.append(DiagnosticItem("warning", "Network",
                                    "cl_lw is 0 — client-side weapon prediction disabled",
                                    "cl_lw", "1"))
        penalty += 5

    # ── hud_fastswitch ──
    fastswitch = _gi(cfg, "hud_fastswitch", -1)
    if fastswitch == 0:
        items.append(DiagnosticItem("info", "General",
                                    "hud_fastswitch is OFF — weapon switching will require confirmation",
                                    "hud_fastswitch", "1"))

    report.score = max(0, 100 - penalty)
    return report


def apply_fix(cfg: CfgConfig, item: DiagnosticItem) -> bool:
    """Apply a single diagnostic fix to the config."""
    if item.fix_key and item.fix_value:
        cfg.set(item.fix_key, item.fix_value)
        return True
    return False


def apply_all_fixes(cfg: CfgConfig, report: DiagnosticReport) -> int:
    """Apply all fixable issues. Returns count of applied fixes."""
    count = 0
    for item in report.items:
        if item.severity in ("warning", "error") and item.fix_key:
            if apply_fix(cfg, item):
                count += 1
    return count
