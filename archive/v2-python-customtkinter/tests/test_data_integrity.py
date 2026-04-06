"""Tests for JSON data file integrity."""

import json
import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "cfg_generator", "data")


def _load(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestDataIntegrity:
    def test_cvars_json_valid(self):
        data = _load("cvars.json")
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_modes_json_valid(self):
        data = _load("modes.json")
        assert isinstance(data, dict)
        assert len(data) >= 6
        for key, mode in data.items():
            assert "name_en" in mode or "name_ru" in mode
            assert "settings" in mode

    def test_presets_json_valid(self):
        data = _load("presets.json")
        assert isinstance(data, dict)
        assert len(data) >= 10
        for key, preset in data.items():
            assert "name" in preset
            assert "settings" in preset
            assert "sensitivity" in preset["settings"]

    def test_network_presets_json_valid(self):
        data = _load("network_presets.json")
        assert isinstance(data, dict)
        for key, preset in data.items():
            assert "settings" in preset
            assert "rate" in preset["settings"]

    def test_aliases_json_valid(self):
        data = _load("aliases.json")
        assert isinstance(data, (dict, list))

    def test_buyscripts_json_valid(self):
        data = _load("buyscripts.json")
        assert isinstance(data, (dict, list))

    def test_hardware_json_valid(self):
        data = _load("hardware.json")
        assert isinstance(data, dict)
        assert "gpu_vendors" in data or "performance_profiles" in data
