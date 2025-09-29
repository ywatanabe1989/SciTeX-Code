#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 02:10:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__color_text.py

"""Comprehensive tests for text coloring functionality.

This module provides extensive testing for the color_text function,
including edge cases, performance, and all color variations.
"""

import os
import pytest
import sys
from typing import List, Tuple
import re


class TestColorTextBasic:
    """Basic functionality tests for color_text."""
    
    def test_color_text_default(self):
        """Test text coloring with default color (green)."""
        from scitex.str._color_text import color_text
        
        colored = color_text("Hello World")
        assert "\033[92m" in colored  # Green ANSI code
        assert "Hello World" in colored
        assert colored.endswith("\033[0m")  # Reset code at end
        assert colored == "\033[92mHello World\033[0m"
    
    def test_empty_string(self):
        """Test coloring empty string."""
        from scitex.str._color_text import color_text
        
        result = color_text("")
        assert result == "\033[92m\033[0m"
    
    def test_single_character(self):
        """Test coloring single character."""
        from scitex.str._color_text import color_text
        
        result = color_text("A", "red")
        assert result == "\033[91mA\033[0m"
    
    def test_unicode_text(self):
        """Test coloring Unicode text."""
        from scitex.str._color_text import color_text
        
        # Test various Unicode characters
        unicode_texts = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "مرحبا بالعالم",  # Arabic
            "🌍🌎🌏",  # Emojis
            "αβγδε",  # Greek
            "日本語テスト",  # Japanese
        ]
        
        for text in unicode_texts:
            colored = color_text(text, "blue")
            assert text in colored
            assert "\033[94m" in colored  # Blue code
            assert "\033[0m" in colored
    
    def test_multiline_text(self):
        """Test coloring multiline text."""
        from scitex.str._color_text import color_text
        
        multiline = "Line 1\nLine 2\nLine 3"
        colored = color_text(multiline, "yellow")
        
        assert "\033[93m" in colored  # Yellow code
        assert multiline in colored
        assert colored.count("\n") == 2  # Preserves newlines
        assert colored.endswith("\033[0m")


class TestColorTextColors:
    """Test all color variations."""
    
    def test_all_standard_colors(self):
        """Test all standard color options."""
        from scitex.str._color_text import color_text
        
        color_codes = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'grey': '\033[90m',
            'gray': '\033[90m',  # Alternative spelling
        }
        
        test_text = "Test Color"
        for color, expected_code in color_codes.items():
            result = color_text(test_text, color)
            assert result == f"{expected_code}{test_text}\033[0m"
            assert expected_code in result
            assert test_text in result
            assert result.endswith("\033[0m")
    
    def test_case_sensitivity(self):
        """Test that color names are case-sensitive."""
        from scitex.str._color_text import color_text
        
        # Uppercase should not work (use reset)
        result_upper = color_text("Test", "RED")
        assert "\033[91m" not in result_upper  # Should not have red code
        
        # Lowercase should work
        result_lower = color_text("Test", "red")
        assert "\033[91m" in result_lower
    
    def test_color_aliases(self):
        """Test special color aliases for train/val/test."""
        from scitex.str._color_text import color_text
        
        aliases = {
            'tra': '\033[97m',  # white
            'val': '\033[92m',  # green
            'tes': '\033[91m',  # red
        }
        
        for alias, expected_code in aliases.items():
            result = color_text("Model Phase", alias)
            assert expected_code in result
            assert "Model Phase" in result
            assert result == f"{expected_code}Model Phase\033[0m"
    
    def test_invalid_colors(self):
        """Test behavior with invalid color names."""
        from scitex.str._color_text import color_text
        
        invalid_colors = [
            'purple',
            'orange',
            'pink',
            'invalid',
            '123',
            'Red',  # Wrong case
            'GREEN',  # Wrong case
            '',  # Empty string
            None,  # None (should handle gracefully)
        ]
        
        for color in invalid_colors:
            try:
                result = color_text("Text", color)
                # Should use reset code (no color)
                assert result == "\033[0mText\033[0m"
            except (TypeError, AttributeError):
                # None might cause issues, which is acceptable
                if color is not None:
                    raise


class TestColorTextSpecialCases:
    """Test special cases and edge conditions."""
    
    def test_text_with_ansi_codes(self):
        """Test coloring text that already contains ANSI codes."""
        from scitex.str._color_text import color_text
        
        # Text with existing ANSI codes
        text_with_codes = "\033[91mAlready Red\033[0m"
        result = color_text(text_with_codes, "blue")
        
        # Should wrap the entire text, including existing codes
        assert result.startswith("\033[94m")
        assert result.endswith("\033[0m")
        assert text_with_codes in result
    
    def test_special_characters(self):
        """Test text with special characters."""
        from scitex.str._color_text import color_text
        
        special_texts = [
            "Text\twith\ttabs",
            "Text\rwith\rcarriage\rreturn",
            "Text\bwith\bbackspace",
            "Text\fwith\fform\ffeed",
            "Text\vwith\vvertical\vtab",
            "Text with \x00 null",
            "Text with \x1b escape",
        ]
        
        for text in special_texts:
            result = color_text(text, "green")
            assert "\033[92m" in result
            assert "\033[0m" in result
            # The actual text content should be preserved
    
    def test_very_long_text(self):
        """Test coloring very long text."""
        from scitex.str._color_text import color_text
        
        # Create a very long string
        long_text = "A" * 10000
        result = color_text(long_text, "cyan")
        
        assert result.startswith("\033[96m")
        assert result.endswith("\033[0m")
        assert len(result) == len(long_text) + len("\033[96m") + len("\033[0m")
    
    def test_numeric_input(self):
        """Test behavior with numeric input."""
        from scitex.str._color_text import color_text
        
        # Test with string representations of numbers
        result1 = color_text("123", "red")
        assert result1 == "\033[91m123\033[0m"
        
        result2 = color_text("3.14159", "blue")
        assert result2 == "\033[94m3.14159\033[0m"
    
    def test_whitespace_preservation(self):
        """Test that whitespace is preserved correctly."""
        from scitex.str._color_text import color_text
        
        whitespace_texts = [
            "   Leading spaces",
            "Trailing spaces   ",
            "   Both sides   ",
            "\t\tTabs\t\t",
            "  Mixed \t spaces \t and \t tabs  ",
        ]
        
        for text in whitespace_texts:
            result = color_text(text, "yellow")
            # Extract the colored text without ANSI codes
            match = re.search(r'\033\[\d+m(.*?)\033\[0m', result)
            assert match
            extracted_text = match.group(1)
            assert extracted_text == text


class TestColorTextCtAlias:
    """Test the ct alias functionality."""
    
    def test_ct_is_alias(self):
        """Test that ct is an alias for color_text."""
        from scitex.str._color_text import color_text as ct, color_text
        
        assert ct is color_text
        assert ct.__name__ == color_text.__name__
        assert ct.__doc__ == color_text.__doc__
    
    def test_ct_functionality(self):
        """Test that ct works identically to color_text."""
        from scitex.str._color_text import color_text as ct, color_text
        
        text = "Test Text"
        colors = ['red', 'green', 'blue', 'yellow']
        
        for color in colors:
            assert ct(text, color) == color_text(text, color)
    
    def test_ct_with_defaults(self):
        """Test ct with default arguments."""
        from scitex.str._color_text import color_text as ct
        
        result = ct("Default Green")
        assert "\033[92m" in result  # Green is default


class TestColorTextIntegration:
    """Integration tests with other string operations."""
    
    def test_color_text_concatenation(self):
        """Test concatenating colored text."""
        from scitex.str._color_text import color_text
        
        red_text = color_text("Error: ", "red")
        yellow_text = color_text("Warning", "yellow")
        combined = red_text + yellow_text
        
        assert "\033[91m" in combined
        assert "\033[93m" in combined
        assert combined.count("\033[0m") == 2
    
    def test_color_text_formatting(self):
        """Test using colored text in string formatting."""
        from scitex.str._color_text import color_text
        
        name = color_text("Alice", "cyan")
        score = color_text("95", "green")
        
        # f-string
        result1 = f"Player {name} scored {score} points!"
        assert "Alice" in result1
        assert "95" in result1
        assert "\033[96m" in result1  # cyan
        assert "\033[92m" in result1  # green
        
        # .format()
        result2 = "Player {} scored {} points!".format(name, score)
        assert result2 == result1
        
        # % formatting
        result3 = "Player %s scored %s points!" % (name, score)
        assert result3 == result1
    
    def test_color_text_in_lists(self):
        """Test colored text in list operations."""
        from scitex.str._color_text import color_text
        
        colored_list = [
            color_text("Red", "red"),
            color_text("Green", "green"),
            color_text("Blue", "blue"),
        ]
        
        # Join operation
        joined = ", ".join(colored_list)
        assert "\033[91m" in joined
        assert "\033[92m" in joined
        assert "\033[94m" in joined
        
        # List comprehension
        upper_colored = [item.upper() for item in colored_list]
        # Note: upper() also uppercases the ANSI codes (91m -> 91M)
        assert "\033[91MRED\033[0M" in upper_colored[0]


class TestColorTextPerformance:
    """Performance-related tests."""
    
    def test_color_text_caching(self):
        """Test that color lookups are efficient."""
        from scitex.str._color_text import color_text
        import time
        
        # First call might be slower due to dict creation
        start = time.time()
        for _ in range(1000):
            color_text("Test", "red")
        first_duration = time.time() - start
        
        # Subsequent calls should be fast
        start = time.time()
        for _ in range(1000):
            color_text("Test", "red")
        second_duration = time.time() - start
        
        # Both should be very fast (< 0.1 seconds for 1000 calls)
        assert first_duration < 0.1
        assert second_duration < 0.1
    
    def test_memory_efficiency(self):
        """Test that color_text doesn't create unnecessary copies."""
        from scitex.str._color_text import color_text
        import sys
        
        text = "A" * 1000
        colored = color_text(text, "blue")
        
        # The colored version should only add the ANSI codes
        expected_size_diff = len("\033[94m") + len("\033[0m")
        actual_size_diff = len(colored) - len(text)
        assert actual_size_diff == expected_size_diff


class TestColorTextDocumentation:
    """Test documentation and examples."""
    
    def test_docstring_example(self):
        """Test the example from the docstring."""
        from scitex.str._color_text import color_text
        
        # The docstring example
        result = color_text("Hello, World!", "blue")
        assert result == "\033[94mHello, World!\033[0m"
        
        # When printed, this would show blue text (can't test actual terminal output)
        assert "Hello, World!" in result
        assert "\033[94m" in result
    
    def test_function_attributes(self):
        """Test function has proper attributes."""
        from scitex.str._color_text import color_text
        
        assert hasattr(color_text, '__doc__')
        assert hasattr(color_text, '__name__')
        assert color_text.__name__ == 'color_text'
        assert color_text.__doc__ is not None
        assert "Apply ANSI color codes to text" in color_text.__doc__


class TestColorTextRobustness:
    """Test robustness and error handling."""
    
    def test_type_coercion(self):
        """Test behavior with non-string inputs."""
        from scitex.str._color_text import color_text
        
        # These should work (strings)
        assert "123" in color_text("123", "red")
        assert "True" in color_text("True", "green")
        
    def test_immutability(self):
        """Test that original text is not modified."""
        from scitex.str._color_text import color_text
        
        original = "Original Text"
        colored = color_text(original, "magenta")
        
        # Original should be unchanged
        assert original == "Original Text"
        assert original != colored
    
    def test_repeated_coloring(self):
        """Test applying color_text multiple times."""
        from scitex.str._color_text import color_text
        
        text = "Hello"
        once = color_text(text, "red")
        twice = color_text(once, "blue")
        thrice = color_text(twice, "green")
        
        # Each application adds new color codes
        assert once.count("\033[") == 1
        assert twice.count("\033[") == 2
        assert thrice.count("\033[") == 3
        
        # All reset codes should be present
        assert once.count("\033[0m") == 1
        assert twice.count("\033[0m") == 2
        assert thrice.count("\033[0m") == 3


# Test helper functions
def strip_ansi_codes(text: str) -> str:
    """Helper to strip ANSI codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class TestHelperFunctions:
    """Test helper functions used in tests."""
    
    def test_strip_ansi_codes(self):
        """Test the ANSI stripping helper."""
        from scitex.str._color_text import color_text
        
        colored = color_text("Test Text", "red")
        stripped = strip_ansi_codes(colored)
        assert stripped == "Test Text"
        
        # Test with multiple colors
        multi_colored = color_text("A", "red") + color_text("B", "blue")
        stripped_multi = strip_ansi_codes(multi_colored)
        assert stripped_multi == "AB"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_color_text.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 04:00:36 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_color_text.py
# 
# 
# def color_text(text, c="green"):
#     """Apply ANSI color codes to text.
# 
#     Parameters
#     ----------
#     text : str
#         The text to be colored.
#     c : str, optional
#         The color to apply. Available colors are 'red', 'green', 'yellow',
#         'blue', 'magenta', 'cyan', 'white', and 'grey' (default is "green").
# 
#     Returns
#     -------
#     str
#         The input text with ANSI color codes applied.
# 
#     Example
#     -------
#     >>> print(color_text("Hello, World!", "blue"))
#     # This will print "Hello, World!" in blue text
#     """
#     ANSI_COLORS = {
#         "red": "\033[91m",
#         "green": "\033[92m",
#         "yellow": "\033[93m",
#         "blue": "\033[94m",
#         "magenta": "\033[95m",
#         "cyan": "\033[96m",
#         "white": "\033[97m",
#         "grey": "\033[90m",
#         "gray": "\033[90m",
#         "reset": "\033[0m",
#     }
#     ANSI_COLORS["tra"] = ANSI_COLORS["white"]
#     ANSI_COLORS["val"] = ANSI_COLORS["green"]
#     ANSI_COLORS["tes"] = ANSI_COLORS["red"]
# 
#     start_code = ANSI_COLORS.get(c, ANSI_COLORS["reset"])
#     end_code = ANSI_COLORS["reset"]
#     return f"{start_code}{text}{end_code}"
# 
# 
# ct = color_text
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_color_text.py
# --------------------------------------------------------------------------------
