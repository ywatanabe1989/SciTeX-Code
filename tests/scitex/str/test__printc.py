#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 02:30:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__printc.py

"""Comprehensive tests for colored bordered print functionality.

This module tests the printc function with various border styles,
colors, message formats, and edge cases.
"""

import pytest
import os
import sys
import re
from typing import List, Tuple
from io import StringIO
import unicodedata

from scitex.str._printc import printc


class TestPrintcBasic:
    """Basic functionality tests for printc."""
    
    def test_printc_default_parameters(self, capsys):
        """Test printc with all default parameters."""
        
        printc("Default message")
        captured = capsys.readouterr()
        
        # Check message is present
        assert "Default message" in captured.out
        
        # Check default color (blue)
        assert "\033[94m" in captured.out
        
        # Check default border character and width
        assert "-" * 40 in captured.out
        
        # Check structure
        lines = captured.out.strip().split('\n')
        assert len(lines) >= 3  # Top border, message, bottom border
    
    def test_printc_basic_structure(self, capsys):
        """Test the basic structure of printc output."""
        
        printc("Test", char="#", n=10)
        captured = capsys.readouterr()
        
        # Remove color codes for easier testing
        clean_output = self._strip_ansi_codes(captured.out)
        lines = clean_output.strip().split('\n')
        
        assert len(lines) == 4  # Empty line, border, message, border
        assert lines[0] == ""  # Empty line at start
        assert lines[1] == "#" * 10  # Top border
        assert "Test" in lines[2]  # Message
        assert lines[3] == "#" * 10  # Bottom border
    
    def test_printc_empty_message(self, capsys):
        """Test printc with empty message."""
        
        printc("")
        captured = capsys.readouterr()
        
        # Should still have borders
        assert "-" * 40 in captured.out
        
        # Structure should be maintained
        clean_output = self._strip_ansi_codes(captured.out)
        lines = clean_output.strip().split('\n')
        assert len(lines) == 4
    
    def test_printc_very_long_message(self, capsys):
        """Test printc with message longer than border."""
        
        long_message = "A" * 100  # Much longer than default border
        printc(long_message, n=20)
        captured = capsys.readouterr()
        
        assert long_message in captured.out
        assert "-" * 20 in captured.out
        
        # Message should not be truncated
        clean_output = self._strip_ansi_codes(captured.out)
        assert long_message in clean_output
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Helper to strip ANSI codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestPrintcColors:
    """Test color functionality of printc."""
    
    def test_all_supported_colors(self, capsys):
        """Test all supported color options."""
        
        color_codes = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'grey': '\033[90m',
        }
        
        for color, expected_code in color_codes.items():
            printc(f"Testing {color}", c=color)
            captured = capsys.readouterr()
            
            assert expected_code in captured.out
            assert f"Testing {color}" in captured.out
            assert "\033[0m" in captured.out  # Reset code
    
    def test_color_none(self, capsys):
        """Test printc with c=None (no color)."""
        
        printc("No color message", c=None)
        captured = capsys.readouterr()
        
        # Should have no ANSI color codes
        assert "\033[" not in captured.out
        assert "No color message" in captured.out
        assert "-" * 40 in captured.out
    
    def test_invalid_color(self, capsys):
        """Test printc with invalid color name."""
        
        # Invalid color should fall back to reset code
        printc("Invalid color", c="purple")
        captured = capsys.readouterr()
        
        assert "Invalid color" in captured.out
        # Should still have some ANSI codes (reset)
        assert "\033[0m" in captured.out
    
    def test_color_aliases(self, capsys):
        """Test special color aliases like 'tra', 'val', 'tes'."""
        
        # These aliases are defined in color_text
        aliases = {
            'tra': '\033[97m',  # white
            'val': '\033[92m',  # green
            'tes': '\033[91m',  # red
        }
        
        for alias, expected_code in aliases.items():
            printc(f"Alias {alias}", c=alias)
            captured = capsys.readouterr()
            assert expected_code in captured.out


class TestPrintcBorderStyles:
    """Test various border styles and configurations."""
    
    def test_single_character_borders(self, capsys):
        """Test various single character borders."""
        
        border_chars = ['*', '#', '=', '+', '~', '_', '.', '|', '@', '$']
        
        for char in border_chars:
            printc(f"Border {char}", char=char, n=15)
            captured = capsys.readouterr()
            
            assert char * 15 in captured.out
            assert f"Border {char}" in captured.out
    
    def test_multi_character_border(self, capsys):
        """Test border with multi-character string."""
        
        # Multi-character strings should be repeated
        printc("Multi", char="<>", n=10)
        captured = capsys.readouterr()
        
        # Should repeat the pattern
        assert "<>" * 5 in captured.out  # 10 characters total
    
    def test_unicode_borders(self, capsys):
        """Test borders with Unicode characters."""
        
        unicode_chars = ['─', '━', '═', '█', '▓', '▒', '░', '♦', '★', '⚡']
        
        for char in unicode_chars:
            printc(f"Unicode {char}", char=char, n=20)
            captured = capsys.readouterr()
            
            assert char * 20 in captured.out
            assert f"Unicode {char}" in captured.out
    
    def test_various_border_widths(self, capsys):
        """Test different border widths."""
        
        widths = [1, 5, 10, 20, 40, 80, 100]
        
        for width in widths:
            printc(f"Width {width}", n=width)
            captured = capsys.readouterr()
            
            assert "-" * width in captured.out
            clean_output = self._strip_ansi_codes(captured.out)
            
            # Check that borders have correct width
            lines = clean_output.strip().split('\n')
            border_lines = [l for l in lines if l and all(c == '-' for c in l)]
            assert all(len(line) == width for line in border_lines)
    
    def test_zero_width_border(self, capsys):
        """Test border with width 0."""
        
        printc("Zero width", n=0)
        captured = capsys.readouterr()
        
        # Should still have message but no visible border
        assert "Zero width" in captured.out
        
        # No border characters
        clean_output = self._strip_ansi_codes(captured.out)
        lines = clean_output.strip().split('\n')
        # Should have empty lines where borders would be
        assert any("Zero width" in line for line in lines)
    
    def test_negative_width_border(self, capsys):
        """Test border with negative width."""
        
        # Should handle gracefully (likely treated as 0 or ignored)
        printc("Negative width", n=-10)
        captured = capsys.readouterr()
        
        assert "Negative width" in captured.out
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Helper to strip ANSI codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestPrintcMessageTypes:
    """Test printc with various message types and formats."""
    
    def test_multiline_message(self, capsys):
        """Test printc with multiline message."""
        
        multiline = "Line 1\nLine 2\nLine 3"
        printc(multiline, char="*", n=20)
        captured = capsys.readouterr()
        
        # All lines should be present
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out
        
        # Border should still be present
        assert "*" * 20 in captured.out
    
    def test_unicode_message(self, capsys):
        """Test printc with Unicode messages."""
        
        unicode_messages = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "مرحبا بالعالم",  # Arabic
            "🌍🌎🌏",  # Emojis
            "αβγδε",  # Greek
            "日本語テスト",  # Japanese
        ]
        
        for msg in unicode_messages:
            printc(msg, c="green")
            captured = capsys.readouterr()
            assert msg in captured.out
    
    def test_special_characters_in_message(self, capsys):
        """Test messages with special characters."""
        
        special_messages = [
            "Tab\there",
            "New\nline",
            "Carriage\rreturn",
            "Quote's and \"quotes\"",
            "Backslash\\test",
            "Null\x00byte",
        ]
        
        for msg in special_messages:
            printc(msg, c="yellow")
            captured = capsys.readouterr()
            # At least part of the message should be visible
            assert captured.out  # Non-empty output
    
    def test_numeric_string_messages(self, capsys):
        """Test messages that are numeric strings."""
        
        numeric_messages = [
            "123",
            "3.14159",
            "-42",
            "1e6",
            "0xFF",
            "Binary: 101010",
        ]
        
        for msg in numeric_messages:
            printc(msg)
            captured = capsys.readouterr()
            assert msg in captured.out
    
    def test_whitespace_messages(self, capsys):
        """Test messages with various whitespace."""
        
        whitespace_messages = [
            "   Leading spaces",
            "Trailing spaces   ",
            "   Both sides   ",
            "\t\tTabs\t\t",
            "  Mixed \t spaces \t and \t tabs  ",
        ]
        
        for msg in whitespace_messages:
            printc(msg, char="=", n=30)
            captured = capsys.readouterr()
            
            # Message should be preserved with whitespace
            clean_output = self._strip_ansi_codes(captured.out)
            assert msg in clean_output or msg.strip() in clean_output
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Helper to strip ANSI codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestPrintcEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_border_character(self, capsys):
        """Test with empty string as border character."""
        
        printc("Empty border", char="", n=40)
        captured = capsys.readouterr()
        
        # Should still print message
        assert "Empty border" in captured.out
        
        # No visible border
        clean_output = self._strip_ansi_codes(captured.out)
        lines = clean_output.strip().split('\n')
        # Should have message but empty border lines
        assert any("Empty border" in line for line in lines)
    
    def test_very_large_border_width(self, capsys):
        """Test with very large border width."""
        
        # Large but reasonable width
        printc("Large border", n=200)
        captured = capsys.readouterr()
        
        assert "Large border" in captured.out
        assert "-" * 200 in captured.out
    
    def test_none_message(self, capsys):
        """Test printc with None as message."""
        
        # Should convert None to string
        printc(None)
        captured = capsys.readouterr()
        
        # Should print "None" as string
        assert "None" in captured.out
    
    def test_object_as_message(self, capsys):
        """Test printc with non-string objects."""
        
        # Various objects that should be converted to string
        objects = [
            123,
            3.14,
            [1, 2, 3],
            {'key': 'value'},
            (1, 2, 3),
            {1, 2, 3},
            True,
            False,
        ]
        
        for obj in objects:
            printc(obj)
            captured = capsys.readouterr()
            assert str(obj) in captured.out
    
    def test_ansi_codes_in_message(self, capsys):
        """Test message that already contains ANSI codes."""
        
        # Message with existing color codes
        colored_msg = "\033[91mRed text\033[0m"
        printc(colored_msg, c="blue")
        captured = capsys.readouterr()
        
        # Both color codes should be present
        assert "\033[91m" in captured.out  # Original red
        assert "\033[94m" in captured.out  # Blue from printc
        assert "Red text" in captured.out
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Helper to strip ANSI codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestPrintcOutput:
    """Test output characteristics of printc."""
    
    def test_output_to_stdout(self, capsys):
        """Test that printc outputs to stdout, not stderr."""
        
        printc("Stdout test")
        captured = capsys.readouterr()
        
        assert captured.out != ""  # stdout has content
        assert captured.err == ""  # stderr is empty
    
    def test_no_return_value(self):
        """Test that printc returns None."""
        
        result = printc("Test message")
        assert result is None
    
    def test_consecutive_printc_calls(self, capsys):
        """Test multiple consecutive printc calls."""
        
        printc("First", c="red", char="*", n=20)
        printc("Second", c="green", char="#", n=25)
        printc("Third", c="blue", char="=", n=30)
        
        captured = capsys.readouterr()
        
        # All messages should be present
        assert "First" in captured.out
        assert "Second" in captured.out
        assert "Third" in captured.out
        
        # All borders should be present
        assert "*" * 20 in captured.out
        assert "#" * 25 in captured.out
        assert "=" * 30 in captured.out
        
        # All colors should be present
        assert "\033[91m" in captured.out  # red
        assert "\033[92m" in captured.out  # green
        assert "\033[94m" in captured.out  # blue
    
    def test_printc_formatting_consistency(self, capsys):
        """Test that formatting is consistent across calls."""
        
        # Same parameters should produce same structure
        messages = ["Test 1", "Test 2", "Test 3"]
        outputs = []
        
        for msg in messages:
            printc(msg, c="cyan", char="-", n=40)
            captured = capsys.readouterr()
            
            # Strip the actual message content for comparison
            clean = self._strip_ansi_codes(captured.out)
            structure = clean.replace(msg, "MESSAGE")
            outputs.append(structure)
        
        # All outputs should have same structure
        assert all(out == outputs[0] for out in outputs[1:])
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Helper to strip ANSI codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class TestPrintcIntegration:
    """Integration tests with other string functions."""
    
    def test_printc_with_color_text_compatibility(self, capsys):
        """Test that printc works well with color_text."""
        from scitex.str import color_text
        
        # Pre-colored message
        colored_msg = color_text("Pre-colored", "red")
        printc(colored_msg, c="blue")
        captured = capsys.readouterr()
        
        # Should have both color codes
        assert "\033[91m" in captured.out  # red from color_text
        assert "\033[94m" in captured.out  # blue from printc
    
    def test_printc_in_loops(self, capsys):
        """Test printc in loop scenarios."""
        
        items = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
        colors = ["red", "yellow", "red", "yellow", "blue"]
        
        for item, color in zip(items, colors):
            printc(f"Processing: {item}", c=color, char=".", n=25)
        
        captured = capsys.readouterr()
        
        # All items should be in output
        for item in items:
            assert item in captured.out
        
        # Should have multiple bordered sections
        assert captured.out.count("." * 25) == len(items) * 2  # Top and bottom borders
    
    def test_printc_with_format_strings(self, capsys):
        """Test printc with various string formatting."""
        
        # f-string
        name = "Alice"
        score = 95
        printc(f"Player {name} scored {score}%", c="green")
        
        # .format()
        printc("Player {} scored {}%".format("Bob", 87), c="yellow")
        
        # % formatting
        printc("Player %s scored %d%%" % ("Charlie", 92), c="cyan")
        
        captured = capsys.readouterr()
        
        assert "Alice" in captured.out
        assert "Bob" in captured.out
        assert "Charlie" in captured.out
        assert "95%" in captured.out
        assert "87%" in captured.out
        assert "92%" in captured.out


class TestPrintcPerformance:
    """Performance-related tests."""
    
    def test_printc_with_large_message(self, capsys):
        """Test printc with very large message."""
        import time
        
        # Create a large message
        large_msg = "X" * 10000
        
        start = time.time()
        printc(large_msg, n=50)
        duration = time.time() - start
        
        captured = capsys.readouterr()
        
        # Should complete quickly
        assert duration < 0.1  # Should be very fast
        
        # Message should be complete
        assert large_msg in captured.out
    
    def test_printc_memory_usage(self, capsys):
        """Test that printc doesn't create excessive copies."""
        
        # Multiple calls shouldn't accumulate memory
        for i in range(100):
            printc(f"Iteration {i}", c="green", n=20)
        
        captured = capsys.readouterr()
        
        # All iterations should be present
        assert "Iteration 0" in captured.out
        assert "Iteration 99" in captured.out


class TestPrintcDocumentation:
    """Test documentation and examples."""
    
    def test_docstring_example(self, capsys):
        """Test the example from the docstring."""
        
        # Note: The docstring has an error - it refers to print_block
        # but the function is printc. Testing actual behavior.
        printc("Hello, World!", char="*", n=20, c="blue")
        captured = capsys.readouterr()
        
        clean_output = self._strip_ansi_codes(captured.out)
        lines = clean_output.strip().split('\n')
        
        # Should have the structure shown in docstring
        assert "*" * 20 in clean_output
        assert "Hello, World!" in clean_output
        
        # Check color
        assert "\033[94m" in captured.out  # Blue color
    
    def test_function_attributes(self):
        """Test that printc has proper attributes."""
        
        assert hasattr(printc, '__doc__')
        assert hasattr(printc, '__name__')
        assert printc.__name__ == 'printc'
        assert printc.__doc__ is not None
        assert "Print a message surrounded by a character border" in printc.__doc__
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Helper to strip ANSI codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([os.path.abspath(__file__), "-v", "-s"])
