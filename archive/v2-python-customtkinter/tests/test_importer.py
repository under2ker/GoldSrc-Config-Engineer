"""Tests for cfg_generator.io.importer."""

import os
import tempfile
import pytest
from cfg_generator.io.importer import import_from_file, SecurityError


class TestImporter:
    def test_import_simple_cfg(self):
        content = 'sensitivity "2.5"\nfps_max "300"\nbind "w" "+forward"\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False,
                                          encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            cfg, summary = import_from_file(path)
            assert "sensitivity" in cfg.settings
            assert cfg.settings["sensitivity"] == "2.5"
        finally:
            os.unlink(path)

    def test_import_blocks_dangerous(self):
        content = 'rcon_password "secret"\nsensitivity "2.5"\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False,
                                          encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            with pytest.raises(SecurityError):
                import_from_file(path)
        finally:
            os.unlink(path)

    def test_import_binds(self):
        content = 'bind "a" "+moveleft"\nbind "d" "+moveright"\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False,
                                          encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            cfg, _ = import_from_file(path)
            assert "a" in cfg.binds
            assert cfg.binds["a"] == "+moveleft"
        finally:
            os.unlink(path)

    def test_import_nonexistent_file(self):
        with pytest.raises(Exception):
            import_from_file("/nonexistent/file.cfg")
