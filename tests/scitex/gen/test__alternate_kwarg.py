#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 20:00:00 (Claude)"
# File: /tests/scitex/gen/test__alternate_kwarg.py

import pytest
from scitex.gen import alternate_kwarg


class TestAlternateKwarg:
    """Test cases for alternate_kwarg function."""

    def test_alternate_key_used_when_primary_missing(self):
        """Test that alternate key is used when primary key is missing."""
        kwargs = {"alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == "alt_value"
        assert "alt_key" not in result

    def test_primary_key_preserved_when_present(self):
        """Test that primary key value is preserved when present."""
        kwargs = {"primary_key": "primary_value", "alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == "primary_value"
        assert "alt_key" not in result

    def test_none_value_in_primary_key_replaced(self):
        """Test that None value in primary key is replaced by alternate."""
        kwargs = {"primary_key": None, "alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == "alt_value"
        assert "alt_key" not in result

    def test_empty_string_in_primary_key_replaced(self):
        """Test that empty string in primary key is replaced by alternate."""
        kwargs = {"primary_key": "", "alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == "alt_value"
        assert "alt_key" not in result

    def test_false_value_in_primary_key_replaced(self):
        """Test that False value in primary key is replaced by alternate."""
        kwargs = {"primary_key": False, "alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == "alt_value"
        assert "alt_key" not in result

    def test_zero_value_in_primary_key_replaced(self):
        """Test that 0 value in primary key is replaced by alternate."""
        kwargs = {"primary_key": 0, "alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == "alt_value"
        assert "alt_key" not in result

    def test_no_alternate_key_present(self):
        """Test behavior when alternate key is not present."""
        kwargs = {"other_key": "other_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] is None
        assert result["other_key"] == "other_value"

    def test_neither_key_present(self):
        """Test behavior when neither key is present."""
        kwargs = {"other_key": "other_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] is None

    def test_modifies_original_dict(self):
        """Test that the function modifies the original dictionary."""
        kwargs = {"alt_key": "alt_value"}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert kwargs is result  # Same object reference
        assert "alt_key" not in kwargs
        assert "primary_key" in kwargs

    def test_complex_values(self):
        """Test with complex data types as values."""
        kwargs = {"alt_key": {"nested": "value"}}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == {"nested": "value"}
        assert "alt_key" not in result

    def test_list_values(self):
        """Test with list values."""
        kwargs = {"primary_key": [], "alt_key": [1, 2, 3]}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        # Empty list is falsy, so it should be replaced
        assert result["primary_key"] == [1, 2, 3]
        assert "alt_key" not in result

    @pytest.mark.parametrize(
        "primary_val,alt_val,expected",
        [
            (None, "alt", "alt"),
            ("", "alt", "alt"),
            (False, "alt", "alt"),
            (0, "alt", "alt"),
            ("primary", "alt", "primary"),
            (True, "alt", True),
            (1, "alt", 1),
            ("non-empty", "alt", "non-empty"),
        ],
    )
    def test_parametrized_values(self, primary_val, alt_val, expected):
        """Parametrized test for various value combinations."""
        kwargs = {"primary_key": primary_val, "alt_key": alt_val}
        result = alternate_kwarg(kwargs, "primary_key", "alt_key")
        assert result["primary_key"] == expected

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_alternate_kwarg.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 13:30:41 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_alternate_kwarg.py
# 
# 
# def alternate_kwarg(kwargs, primary_key, alternate_key):
#     alternate_value = kwargs.pop(alternate_key, None)
#     kwargs[primary_key] = kwargs.get(primary_key) or alternate_value
#     return kwargs
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_alternate_kwarg.py
# --------------------------------------------------------------------------------
