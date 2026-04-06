#!/usr/bin/env python3
"""
Benchmark suite for GoldSrc Config Engineer.
Measures startup, generation, export, import performance.
Saves results to benchmarks/results.json and compares with previous run.

Usage:
    python benchmarks/bench_all.py
"""

import json
import os
import sys
import time
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cfg_generator.core.generator import (
    get_modes, get_presets, create_mode_config, create_preset_config,
    create_quick_config, generate_single_cfg, clear_cache,
)
from cfg_generator.io.exporter import export_single_cfg, export_full_config_set
from cfg_generator.io.importer import parse_cfg_text
from cfg_generator.core.validator import validate_config_dict
from cfg_generator.core.diagnostics import run_diagnostics

RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


def bench(label: str, func, iterations: int = 1) -> float:
    """Run func *iterations* times and return average ms."""
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
    avg = sum(times) / len(times)
    mn = min(times)
    mx = max(times)
    print(f"  {label:<40} avg={avg:7.2f}ms  min={mn:7.2f}ms  max={mx:7.2f}ms  (n={iterations})")
    return avg


def main():
    print("=" * 60)
    print("GoldSrc Config Engineer — Benchmark Suite")
    print("=" * 60)

    results = {}

    print("\n--- JSON Loading ---")
    clear_cache()
    results["json_cold_load"] = bench("Cold load (all JSON)", lambda: (clear_cache(), get_modes(), get_presets()), 5)
    results["json_cached_load"] = bench("Cached load (all JSON)", lambda: (get_modes(), get_presets()), 50)

    print("\n--- Config Generation ---")
    modes = list(get_modes().keys())
    presets = list(get_presets().keys())

    results["gen_quick"] = bench("Quick config", create_quick_config, 20)
    results["gen_mode_avg"] = bench(f"Mode config (avg of {len(modes)})",
        lambda: [create_mode_config(m) for m in modes], 10)
    results["gen_preset_avg"] = bench(f"Preset config (avg of {len(presets)})",
        lambda: [create_preset_config(p) for p in presets], 10)

    cfg = create_quick_config()
    results["gen_single_cfg"] = bench("generate_single_cfg()", lambda: generate_single_cfg(cfg), 20)

    print("\n--- All Mode x Preset Combos ---")
    def _all_combos():
        for m in modes:
            for p in presets:
                c = create_mode_config(m)
                generate_single_cfg(c)
    results["gen_all_combos"] = bench(f"All {len(modes)}x{len(presets)} combos",
        _all_combos, 3)

    print("\n--- Validation & Diagnostics ---")
    results["validate"] = bench("validate_config_dict()", lambda: validate_config_dict(cfg.settings), 20)
    results["diagnostics"] = bench("run_diagnostics()", lambda: run_diagnostics(cfg), 20)

    print("\n--- Export ---")
    with tempfile.TemporaryDirectory() as tmp:
        import cfg_generator.io.exporter as exp
        old_dir = exp.OUTPUT_DIR
        exp.OUTPUT_DIR = tmp
        results["export_single"] = bench("export_single_cfg()", lambda: export_single_cfg(cfg, "bench.cfg"), 10)
        results["export_full"] = bench("export_full_config_set()", lambda: export_full_config_set(cfg), 5)
        exp.OUTPUT_DIR = old_dir

    print("\n--- Import / Parse ---")
    text = generate_single_cfg(cfg)
    results["parse_cfg"] = bench(f"parse_cfg_text() ({len(text)} chars)", lambda: parse_cfg_text(text), 20)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    previous = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            previous = json.load(f)

    for key, val in sorted(results.items()):
        prev = previous.get(key)
        delta = ""
        if prev is not None:
            diff = val - prev
            pct = (diff / prev) * 100 if prev else 0
            arrow = "↑" if diff > 0 else "↓"
            color = "REGRESS" if diff > prev * 0.1 else "ok"
            delta = f"  {arrow} {abs(diff):+.2f}ms ({pct:+.1f}%) [{color}]"
        print(f"  {key:<30} {val:7.2f}ms{delta}")

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
