"""Tests for the Undo/Redo system."""

import pytest
from cfg_generator.core.generator import CfgConfig
from cfg_generator.core.undo import UndoManager


class TestUndoManager:
    def setup_method(self):
        self.cfg = CfgConfig()
        self.cfg.settings["sensitivity"] = "2.5"
        self.um = UndoManager(max_size=5)
        self.um.bind_config(self.cfg)

    def test_initial_state(self):
        assert not self.um.can_undo
        assert not self.um.can_redo
        assert self.um.undo_count == 0

    def test_record_and_undo(self):
        self.um.record_set("sensitivity", "2.5", "3.0")
        self.cfg.settings["sensitivity"] = "3.0"
        assert self.um.can_undo
        assert self.um.undo_count == 1

        change = self.um.undo()
        assert change is not None
        assert self.cfg.settings["sensitivity"] == "2.5"

    def test_redo(self):
        self.um.record_set("sensitivity", "2.5", "3.0")
        self.cfg.settings["sensitivity"] = "3.0"
        self.um.undo()
        assert self.cfg.settings["sensitivity"] == "2.5"
        assert self.um.can_redo

        change = self.um.redo()
        assert change is not None
        assert self.cfg.settings["sensitivity"] == "3.0"

    def test_redo_cleared_on_new_action(self):
        self.um.record_set("sensitivity", "2.5", "3.0")
        self.cfg.settings["sensitivity"] = "3.0"
        self.um.undo()
        assert self.um.can_redo

        self.um.record_set("sensitivity", "2.5", "4.0")
        assert not self.um.can_redo

    def test_max_size(self):
        for i in range(10):
            self.um.record_set("sensitivity", str(i), str(i + 1))
        assert self.um.undo_count == 5

    def test_undo_empty_returns_none(self):
        assert self.um.undo() is None

    def test_redo_empty_returns_none(self):
        assert self.um.redo() is None

    def test_bind_change(self):
        self.cfg.binds["mouse1"] = "+attack"
        self.um.record_bind("mouse1", "+attack", "+jump")
        self.cfg.binds["mouse1"] = "+jump"

        self.um.undo()
        assert self.cfg.binds["mouse1"] == "+attack"

    def test_remove(self):
        self.um.record_remove("sensitivity", "2.5")
        del self.cfg.settings["sensitivity"]

        self.um.undo()
        assert self.cfg.settings["sensitivity"] == "2.5"

    def test_clear(self):
        self.um.record_set("sensitivity", "2.5", "3.0")
        self.um.clear()
        assert not self.um.can_undo
        assert not self.um.can_redo

    def test_descriptions(self):
        self.um.record_set("sensitivity", "2.5", "3.0")
        assert "sensitivity" in self.um.undo_description
        assert "2.5" in self.um.undo_description
        assert "3.0" in self.um.undo_description
