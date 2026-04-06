"""Tests for the exporter — safe write, lock detection, error handling."""

import os
import pytest

from cfg_generator.core.generator import CfgConfig, create_quick_config
from cfg_generator.io import exporter


@pytest.fixture(autouse=True)
def tmp_output(tmp_path, monkeypatch):
    """Redirect OUTPUT_DIR to temp directory."""
    monkeypatch.setattr(exporter, "OUTPUT_DIR", str(tmp_path / "output"))


class TestExportSingleCfg:
    def test_export_creates_file(self):
        cfg = create_quick_config()
        path = exporter.export_single_cfg(cfg, "test.cfg")
        assert os.path.isfile(path)
        assert path.endswith("test.cfg")

    def test_export_content_not_empty(self):
        cfg = create_quick_config()
        path = exporter.export_single_cfg(cfg)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100

    def test_export_adds_cfg_extension(self):
        cfg = create_quick_config()
        path = exporter.export_single_cfg(cfg, "test")
        assert path.endswith("test.cfg")


class TestExportFullSet:
    def test_full_export_creates_files(self):
        cfg = create_quick_config()
        exported = exporter.export_full_config_set(cfg)
        assert "autoexec.cfg" in exported
        assert "config/network.cfg" in exported
        for rel, path in exported.items():
            assert os.path.isfile(path), f"{rel} not created"


class TestCheckWritable:
    def test_writable_dir(self, tmp_path):
        exporter._check_writable(str(tmp_path))

    def test_nonexistent_creates(self, tmp_path):
        new_dir = str(tmp_path / "new_dir")
        exporter._check_writable(new_dir)
        assert os.path.isdir(new_dir)


class TestSafeWrite:
    def test_write_new_file(self, tmp_path):
        path = str(tmp_path / "new.cfg")
        exporter._safe_write(path, "// test content")
        assert os.path.isfile(path)
        with open(path, "r") as f:
            assert f.read() == "// test content"

    def test_overwrite_file(self, tmp_path):
        path = str(tmp_path / "existing.cfg")
        with open(path, "w") as f:
            f.write("old")
        exporter._safe_write(path, "new")
        with open(path, "r") as f:
            assert f.read() == "new"
