"""Tests for cfg_generator.core.generator."""

import pytest
from cfg_generator.core.generator import (
    CfgConfig, create_mode_config, create_preset_config, create_quick_config,
    generate_single_cfg, compare_configs, get_modes, get_presets,
    apply_network_preset, apply_visual_preset, apply_crosshair_preset,
    get_network_presets, get_visual_presets, get_crosshair_presets,
)


class TestCfgConfig:
    def test_create_empty(self):
        cfg = CfgConfig()
        assert cfg.settings == {}
        assert cfg.binds == {}

    def test_set_get(self):
        cfg = CfgConfig()
        cfg.set("sensitivity", "2.5")
        assert cfg.get("sensitivity") == "2.5"
        assert cfg.get("unknown", "default") == "default"

    def test_merge(self):
        cfg = CfgConfig()
        cfg.merge({"rate": "25000", "cl_cmdrate": "101"})
        assert len(cfg.settings) == 2
        assert cfg.settings["rate"] == "25000"

    def test_merge_binds(self):
        cfg = CfgConfig()
        cfg.merge_binds({"w": "+forward", "s": "+back"})
        assert cfg.binds["w"] == "+forward"

    def test_remove(self):
        cfg = CfgConfig()
        cfg.set("test", "1")
        cfg.remove("test")
        assert "test" not in cfg.settings


class TestModeConfigs:
    def test_all_modes_generate(self):
        modes = get_modes()
        assert len(modes) > 0
        for key in modes:
            cfg = create_mode_config(key)
            assert isinstance(cfg, CfgConfig)
            assert len(cfg.settings) > 0

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            create_mode_config("nonexistent_mode_xyz")

    def test_classic_mode_has_binds(self):
        cfg = create_mode_config("classic")
        assert len(cfg.binds) > 0


class TestPresetConfigs:
    def test_all_presets_generate(self):
        presets = get_presets()
        assert len(presets) >= 10
        for key in presets:
            cfg = create_preset_config(key)
            assert isinstance(cfg, CfgConfig)
            assert len(cfg.settings) > 0

    def test_unknown_preset_raises(self):
        with pytest.raises(ValueError):
            create_preset_config("nonexistent_preset_xyz")

    def test_preset_has_sensitivity(self):
        presets = get_presets()
        for key in presets:
            cfg = create_preset_config(key)
            assert "sensitivity" in cfg.settings


class TestQuickConfig:
    def test_defaults(self):
        cfg = create_quick_config()
        assert cfg.settings["sensitivity"] == "2.5"
        assert cfg.settings["fps_max"] == "100"
        assert cfg.settings["volume"] == "0.7"

    def test_custom_values(self):
        cfg = create_quick_config("classic", 3.0, 300, 0.5)
        assert cfg.settings["sensitivity"] == "3.0"
        assert cfg.settings["fps_max"] == "300"


class TestGenerateCfg:
    def test_output_not_empty(self):
        cfg = create_quick_config()
        text = generate_single_cfg(cfg)
        assert len(text) > 100
        assert "sensitivity" in text

    def test_contains_echo_banner(self):
        cfg = create_quick_config()
        text = generate_single_cfg(cfg)
        assert 'echo "' in text
        assert "GoldSrc Config Engineer" in text

    def test_contains_binds(self):
        cfg = create_mode_config("classic")
        text = generate_single_cfg(cfg)
        assert "bind" in text


class TestCompare:
    def test_compare_returns_diffs(self):
        cfg = create_quick_config("classic", 5.0, 999, 0.1)
        presets = get_presets()
        pk = list(presets.keys())[0]
        diffs = compare_configs(cfg, pk)
        assert isinstance(diffs, list)

    def test_compare_same_is_empty(self):
        presets = get_presets()
        pk = list(presets.keys())[0]
        cfg = create_preset_config(pk)
        diffs = compare_configs(cfg, pk)
        assert len(diffs) == 0


class TestNetworkPresets:
    def test_all_apply(self):
        presets = get_network_presets()
        for key in presets:
            cfg = CfgConfig()
            apply_network_preset(cfg, key)
            assert "rate" in cfg.settings


class TestVisualPresets:
    def test_all_apply(self):
        presets = get_visual_presets()
        for key in presets:
            cfg = CfgConfig()
            apply_visual_preset(cfg, key)
            assert len(cfg.settings) > 0


class TestCrosshairPresets:
    def test_all_apply(self):
        presets = get_crosshair_presets()
        for key in presets:
            cfg = CfgConfig()
            apply_crosshair_preset(cfg, key)
            assert len(cfg.settings) > 0
