"""Tests for profile management — save, load, validate, migrate, autosave."""

import json
import os
import tempfile
import pytest

from cfg_generator.core.generator import CfgConfig
from cfg_generator.core import profiles as prof


@pytest.fixture(autouse=True)
def tmp_dirs(tmp_path, monkeypatch):
    """Redirect profile and history directories to temp for isolation."""
    p_dir = str(tmp_path / "profiles")
    h_dir = str(tmp_path / "history")
    monkeypatch.setattr(prof, "PROFILES_DIR", p_dir)
    monkeypatch.setattr(prof, "HISTORY_DIR", h_dir)
    monkeypatch.setattr(prof, "META_FILE", os.path.join(p_dir, "_meta.json"))
    monkeypatch.setattr(prof, "AUTOSAVE_FILE", str(tmp_path / "~autosave.json"))
    os.makedirs(p_dir, exist_ok=True)
    os.makedirs(h_dir, exist_ok=True)


class TestProfileCRUD:
    def _make_cfg(self) -> CfgConfig:
        cfg = CfgConfig()
        cfg.settings["sensitivity"] = "2.5"
        cfg.binds["mouse1"] = "+attack"
        cfg.mode = "classic"
        return cfg

    def test_save_and_load(self):
        cfg = self._make_cfg()
        fn = prof.save_profile("Test", cfg)
        name, loaded = prof.load_profile(fn)
        assert name == "Test"
        assert loaded.settings["sensitivity"] == "2.5"

    def test_list_profiles(self):
        cfg = self._make_cfg()
        prof.save_profile("Alpha", cfg)
        prof.save_profile("Beta", cfg)
        items = prof.list_profiles()
        names = {p["name"] for p in items}
        assert "Alpha" in names
        assert "Beta" in names

    def test_delete_profile(self):
        cfg = self._make_cfg()
        fn = prof.save_profile("ToDelete", cfg)
        assert prof.delete_profile(fn)
        items = prof.list_profiles()
        assert all(p["name"] != "ToDelete" for p in items)

    def test_rename_profile(self):
        cfg = self._make_cfg()
        fn = prof.save_profile("OldName", cfg)
        prof.rename_profile(fn, "NewName")
        name, _ = prof.load_profile(fn)
        assert name == "NewName"

    def test_duplicate_profile(self):
        cfg = self._make_cfg()
        fn = prof.save_profile("Original", cfg)
        new_fn = prof.duplicate_profile(fn, "Clone")
        name, loaded = prof.load_profile(new_fn)
        assert name == "Clone"
        assert loaded.settings["sensitivity"] == "2.5"

    def test_active_profile(self):
        cfg = self._make_cfg()
        fn = prof.save_profile("Active", cfg)
        assert prof.get_active_profile() == fn


class TestProfileValidation:
    def test_migrate_missing_fields(self, tmp_path):
        """Profile with missing fields should auto-migrate."""
        fn = "old.json"
        path = os.path.join(prof.PROFILES_DIR, fn)
        data = {
            "name": "Legacy",
            "config": {
                "settings": {"sensitivity": "3.0"},
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        name, cfg = prof.load_profile(fn)
        assert name == "Legacy"
        assert cfg.settings["sensitivity"] == "3.0"
        assert isinstance(cfg.binds, dict)
        assert isinstance(cfg.buy_binds, dict)
        assert isinstance(cfg.aliases, list)

    def test_corrupted_profile_raises(self):
        fn = "corrupt.json"
        path = os.path.join(prof.PROFILES_DIR, fn)
        with open(path, "w") as f:
            f.write("{bad json")
        with pytest.raises(ValueError, match="Повреждённый"):
            prof.load_profile(fn)

    def test_missing_profile_raises(self):
        with pytest.raises(FileNotFoundError, match="не найден"):
            prof.load_profile("nonexistent.json")


class TestHistory:
    def test_save_and_list(self):
        cfg = CfgConfig()
        cfg.settings["rate"] = "25000"
        prof.save_history_snapshot(cfg, "test_snap")
        items = prof.list_history()
        assert len(items) >= 1
        assert items[0]["label"] == "test_snap"

    def test_load_snapshot(self):
        cfg = CfgConfig()
        cfg.settings["rate"] = "25000"
        fn = prof.save_history_snapshot(cfg, "load_test")
        label, loaded = prof.load_history_snapshot(fn)
        assert loaded.settings["rate"] == "25000"


class TestAutosave:
    def test_autosave_cycle(self):
        cfg = CfgConfig()
        cfg.settings["sensitivity"] = "5.0"
        prof.autosave(cfg)
        assert prof.has_autosave()

        recovered = prof.load_autosave()
        assert recovered is not None
        assert recovered.settings["sensitivity"] == "5.0"

        prof.clear_autosave()
        assert not prof.has_autosave()

    def test_autosave_none(self):
        prof.autosave(None)
        assert not prof.has_autosave()

    def test_load_no_autosave(self):
        assert prof.load_autosave() is None
