"""Tests for cfg_generator.core.validator."""

import pytest
from cfg_generator.core.validator import validate_config_dict


class TestValidator:
    def test_valid_config(self):
        settings = {"sensitivity": "2.5", "fps_max": "100", "volume": "0.7"}
        r = validate_config_dict(settings)
        assert r.is_valid
        assert r.valid_count > 0

    def test_empty_config(self):
        r = validate_config_dict({})
        assert r.total_count == 0

    def test_invalid_values_still_parses(self):
        settings = {"sensitivity": "abc", "fps_max": "-1"}
        r = validate_config_dict(settings)
        assert r.total_count == 2
