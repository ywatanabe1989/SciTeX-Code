#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 09:16:00 (ywatanabe)"
# File: ./tests/scitex/str/test__color_text_enhanced.py

"""Comprehensive tests for text coloring functionality."""

import pytest
import re


class TestColorTextBasic:
    """Test basic color_text functionality."""

    def test_import(self):
        """Test that color_text can be imported."""
        from scitex.str._color_text import color_text
        assert callable(color_text)

    def test_basic_coloring(self):
        """Test basic text coloring with default color."""
        from scitex.str._color_text import color_text
        
        result = color_text("Hello")
        assert "Hello" in result
        assert "\033[92m" in result  # Green ANSI code
        assert "\033[0m" in result   # Reset ANSI code

    def test_empty_string(self):
        """Test coloring empty string."""
        from scitex.str._color_text import color_text
        
        result = color_text("")
        assert result == "\033[92m\033[0m"  # Green + reset

    def test_multiline_text(self):
        """Test coloring multiline text."""
        from scitex.str._color_text import color_text
        
        text = "Line 1\nLine 2\nLine 3"
        result = color_text(text, "blue")
        assert "Line 1\nLine 2\nLine 3" in result
        assert "\033[94m" in result  # Blue ANSI code
        assert "\033[0m" in result   # Reset ANSI code

    def test_unicode_text(self):
        """Test coloring Unicode text."""
        from scitex.str._color_text import color_text
        
        unicode_text = "Hello 世界 🌍 café"
        result = color_text(unicode_text, "cyan")
        assert unicode_text in result
        assert "\033[96m" in result  # Cyan ANSI code


class TestColorTextColors:
    """Test all available colors and aliases."""

    def test_all_standard_colors(self):
        """Test all standard ANSI colors."""
        from scitex.str._color_text import color_text
        
        expected_codes = {
            "red": "\033[91m",
            "green": "\033[92m", 
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "grey": "\033[90m",
            "gray": "\033[90m",  # Alternative spelling
        }
        
        for color, expected_code in expected_codes.items():
            result = color_text("Test", color)
            assert expected_code in result
            assert "Test" in result
            assert "\033[0m" in result  # Reset code

    def test_color_aliases(self):
        """Test special color aliases."""
        from scitex.str._color_text import color_text
        
        # Test machine learning aliases
        tra_result = color_text("Train", "tra")
        val_result = color_text("Valid", "val") 
        tes_result = color_text("Test", "tes")
        
        assert "\033[97m" in tra_result  # tra -> white
        assert "\033[92m" in val_result  # val -> green
        assert "\033[91m" in tes_result  # tes -> red

    def test_case_sensitivity(self):
        """Test that color names are case sensitive."""
        from scitex.str._color_text import color_text
        
        # Lowercase should work
        result_lower = color_text("Test", "red")
        assert "\033[91m" in result_lower
        
        # Uppercase should fallback to reset
        result_upper = color_text("Test", "RED")
        assert "\033[0m" in result_upper

    def test_invalid_color(self):
        """Test behavior with invalid color names."""
        from scitex.str._color_text import color_text
        
        # Should fallback to reset code
        result = color_text("Test", "nonexistent_color")
        assert "Test" in result
        assert result.startswith("\033[0m")  # Should start with reset


class TestColorTextEdgeCases:
    """Test edge cases and error conditions."""

    def test_none_input(self):
        """Test with None as text input."""
        from scitex.str._color_text import color_text
        
        # Should handle None gracefully
        result = color_text(None)
        assert "None" in result

    def test_numeric_input(self):
        """Test with numeric input."""
        from scitex.str._color_text import color_text
        
        result = color_text(123, "blue")
        assert "123" in result
        assert "\033[94m" in result

    def test_boolean_input(self):
        """Test with boolean input."""
        from scitex.str._color_text import color_text
        
        result_true = color_text(True, "green")
        result_false = color_text(False, "red")
        
        assert "True" in result_true
        assert "False" in result_false

    def test_special_characters(self):
        """Test with special characters and escape sequences."""
        from scitex.str._color_text import color_text
        
        special_text = "!@#$%^&*()[]{}|\\:;\"'<>,.?/`~"
        result = color_text(special_text, "magenta")
        assert special_text in result
        assert "\033[95m" in result

    def test_ansi_codes_in_input(self):
        """Test with text that already contains ANSI codes."""
        from scitex.str._color_text import color_text
        
        text_with_ansi = "Already \033[91mcolored\033[0m text"
        result = color_text(text_with_ansi, "blue")
        assert text_with_ansi in result
        assert "\033[94m" in result  # New blue color


class TestColorTextAlias:
    """Test the ct alias."""

    def test_ct_alias_exists(self):
        """Test that ct alias is available."""
        from scitex.str._color_text import color_text as ct, color_text
        
        assert ct is color_text

    def test_ct_alias_functionality(self):
        """Test that ct alias works identically to color_text."""
        from scitex.str._color_text import color_text as ct, color_text
        
        text = "Test message"
        color = "yellow"
        
        result_ct = ct(text, color)
        result_color_text = color_text(text, color)
        
        assert result_ct == result_color_text

    def test_ct_alias_import(self):
        """Test importing ct alias directly."""
        from scitex.str._color_text import color_text as ct
        
        result = ct("Hello", "cyan")
        assert "Hello" in result
        assert "\033[96m" in result


class TestColorTextFormat:
    """Test output format and structure."""

    def test_ansi_format(self):
        """Test that output follows correct ANSI format."""
        from scitex.str._color_text import color_text
        
        result = color_text("Test", "red")
        
        # Should follow pattern: start_code + text + reset_code
        pattern = r'\033\[91mTest\033\[0m'
        assert re.fullmatch(pattern, result)

    def test_reset_code_consistency(self):
        """Test that reset code is always the same."""
        from scitex.str._color_text import color_text
        
        colors = ["red", "green", "blue", "yellow"]
        for color in colors:
            result = color_text("Test", color)
            assert result.endswith("\033[0m")

    def test_no_nested_codes(self):
        """Test that color codes are not nested improperly."""
        from scitex.str._color_text import color_text
        
        result = color_text("Test", "green")
        
        # Count ANSI escape sequences
        ansi_count = result.count("\033[")
        assert ansi_count == 2  # Should be exactly start + reset

    def test_return_type(self):
        """Test that function always returns a string."""
        from scitex.str._color_text import color_text
        
        inputs = ["text", 123, True, None, [], {}]
        for inp in inputs:
            result = color_text(inp)
            assert isinstance(result, str)


class TestColorTextPerformance:
    """Test performance and efficiency."""

    def test_large_text(self):
        """Test with large text input."""
        from scitex.str._color_text import color_text
        
        large_text = "A" * 10000
        result = color_text(large_text, "blue")
        
        assert large_text in result
        assert "\033[94m" in result
        assert result.endswith("\033[0m")

    def test_repeated_calls(self):
        """Test repeated function calls for consistency."""
        from scitex.str._color_text import color_text
        
        text = "Consistent test"
        color = "magenta"
        
        results = [color_text(text, color) for _ in range(100)]
        
        # All results should be identical
        assert all(r == results[0] for r in results)

    def test_memory_efficiency(self):
        """Test that function doesn't leak memory."""
        from scitex.str._color_text import color_text
        import gc
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create many colored strings
        for i in range(1000):
            _ = color_text(f"Test {i}", "red")
        
        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not have significant object growth
        assert final_objects - initial_objects < 100


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])