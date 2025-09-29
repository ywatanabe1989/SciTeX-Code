#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__print_block.py

"""Tests for block printing functionality."""

import os
import pytest
from unittest.mock import patch


from scitex.str._printc import printc

class TestPrintcBasic:
    """Test basic printc functionality."""
    
    def test_printc_basic_message(self, capsys):
        """Test basic message printing with default parameters."""
        
        printc("Test Message")
        captured = capsys.readouterr()
        
        assert "Test Message" in captured.out
        assert "-" in captured.out  # Default border character
        assert captured.out.count("-") >= 40  # Default width
    
    def test_printc_custom_character(self, capsys):
        """Test printing with custom border character."""
        
        printc("Custom Border", char="*")
        captured = capsys.readouterr()
        
        assert "Custom Border" in captured.out
        assert "*" in captured.out
        assert "-" not in captured.out  # Should not use default char
    
    def test_printc_custom_width(self, capsys):
        """Test printing with custom border width."""
        
        printc("Width Test", char="#", n=20)
        captured = capsys.readouterr()
        
        assert "Width Test" in captured.out
        assert "#" * 20 in captured.out  # Should have exact width
    
    def test_printc_no_color(self, capsys):
        """Test printing without color."""
        
        printc("No Color", c=None)
        captured = capsys.readouterr()
        
        assert "No Color" in captured.out
        assert "-" in captured.out


class TestPrintcColors:
    """Test printc color functionality."""
    
    @pytest.mark.parametrize("color", [
        "red", "green", "yellow", "blue", "magenta", "cyan", "white", "grey"
    ])
    def test_printc_valid_colors(self, capsys, color):
        """Test printing with valid color options."""
        
        printc("Color Test", c=color)
        captured = capsys.readouterr()
        
        assert "Color Test" in captured.out
        # Color codes should be present (ANSI escape sequences)
        assert "\x1b[" in captured.out or "Color Test" in captured.out
    
    def test_printc_default_color(self, capsys):
        """Test printing with default color (cyan)."""
        
        printc("Default Color")
        captured = capsys.readouterr()
        
        assert "Default Color" in captured.out
        # Should have color codes for cyan
        assert "\x1b[" in captured.out or "Default Color" in captured.out
    
    def test_printc_invalid_color_handling(self, capsys):
        """Test behavior with invalid color (should still work)."""
        
        # This should not crash, even with invalid color
        printc("Invalid Color", c="invalidcolor")
        captured = capsys.readouterr()
        
        assert "Invalid Color" in captured.out


class TestPrintcEdgeCases:
    """Test edge cases and special inputs."""
    
    def test_printc_empty_message(self, capsys):
        """Test printing empty message."""
        
        printc("")
        captured = capsys.readouterr()
        
        assert "-" in captured.out  # Border should still appear
        lines = captured.out.strip().split('\n')
        assert len(lines) >= 3  # Should have top border, content, bottom border
    
    def test_printc_multiline_message(self, capsys):
        """Test printing multiline message."""
        
        multiline_msg = "Line 1\nLine 2\nLine 3"
        printc(multiline_msg)
        captured = capsys.readouterr()
        
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out
        assert "-" in captured.out
    
    def test_printc_unicode_message(self, capsys):
        """Test printing unicode characters."""
        
        unicode_msg = "Unicode: 測試 🚀 ñáöü"
        printc(unicode_msg)
        captured = capsys.readouterr()
        
        assert "Unicode:" in captured.out
        assert "測試" in captured.out
        assert "🚀" in captured.out
    
    def test_printc_long_message(self, capsys):
        """Test printing very long message."""
        
        long_msg = "A" * 100  # Message longer than default border
        printc(long_msg, n=20)  # Short border
        captured = capsys.readouterr()
        
        assert long_msg in captured.out
        assert "-" * 20 in captured.out
    
    def test_printc_special_characters(self, capsys):
        """Test printing message with special characters."""
        
        special_msg = "Special: @#$%^&*()_+{}|:<>?[]\\;'\",./"
        printc(special_msg)
        captured = capsys.readouterr()
        
        assert "Special:" in captured.out
        assert "@#$%^&*" in captured.out


class TestPrintcParameters:
    """Test parameter combinations and validation."""
    
    def test_printc_zero_width(self, capsys):
        """Test behavior with zero width border."""
        
        printc("Zero Width", n=0)
        captured = capsys.readouterr()
        
        assert "Zero Width" in captured.out
        # Should handle gracefully, even if border is empty
    
    def test_printc_negative_width(self, capsys):
        """Test behavior with negative width."""
        
        printc("Negative Width", n=-5)
        captured = capsys.readouterr()
        
        assert "Negative Width" in captured.out
        # Should handle gracefully
    
    def test_printc_large_width(self, capsys):
        """Test with very large width."""
        
        printc("Large Width", n=200)
        captured = capsys.readouterr()
        
        assert "Large Width" in captured.out
        assert "-" * 200 in captured.out
    
    def test_printc_multi_character_border(self, capsys):
        """Test with multi-character border (should use first char)."""
        
        printc("Multi Char", char="ABC")
        captured = capsys.readouterr()
        
        assert "Multi Char" in captured.out
        # Should repeat the string as-is
        assert "ABC" in captured.out


class TestPrintcFormatting:
    """Test output formatting and structure."""
    
    def test_printc_output_structure(self, capsys):
        """Test that output has correct structure (border-message-border)."""
        
        printc("Structure Test", char="=", n=30)
        captured = capsys.readouterr()
        
        lines = captured.out.strip().split('\n')
        # Should have: empty line, border, message, border, empty line
        assert len(lines) >= 4
        
        # Find border lines
        border_lines = [line for line in lines if "=" in line and len(line.strip()) > 0]
        assert len(border_lines) >= 2  # Top and bottom borders
        
        # Check border content
        expected_border = "=" * 30
        assert any(expected_border in line for line in border_lines)
    
    def test_printc_newlines_in_output(self, capsys):
        """Test that output includes proper newlines."""
        
        printc("Newline Test")
        captured = capsys.readouterr()
        
        # Should start and end with newlines
        assert captured.out.startswith('\n')
        assert captured.out.endswith('\n')


class TestPrintcIntegration:
    """Test integration with color_text function."""
    
    @patch('scitex.str._print_block.color_text')
    def test_printc_color_text_called(self, mock_color_text, capsys):
        """Test that color_text is called when color is specified."""
        
        mock_color_text.return_value = "colored_text"
        
        printc("Color Integration", c="blue")
        
        # color_text should be called with the formatted text and color
        mock_color_text.assert_called_once()
        args, kwargs = mock_color_text.call_args
        assert "Color Integration" in args[0]
        assert args[1] == "blue"
    
    @patch('scitex.str._print_block.color_text')
    def test_printc_no_color_text_call(self, mock_color_text, capsys):
        """Test that color_text is not called when color is None."""
        
        printc("No Color", c=None)
        
        # color_text should not be called
        mock_color_text.assert_not_called()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_print_block.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-03 03:44:47 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/str/_print_block.py
# 
# from ._color_text import color_text
# 
# 
# def printc(message, char="-", n=40, c="cyan"):
#     """Print a message surrounded by a character border.
# 
#     This function prints a given message surrounded by a border made of
#     a specified character. The border can be colored if desired.
# 
#     Parameters
#     ----------
#     message : str
#         The message to be printed inside the border.
#     char : str, optional
#         The character used to create the border (default is "-").
#     n : int, optional
#         The width of the border (default is 40).
#     c : str, optional
#         The color of the border. Can be 'red', 'green', 'yellow', 'blue',
#         'magenta', 'cyan', 'white', or 'grey' (default is None, which means no color).
# 
#     Returns
#     -------
#     None
# 
#     Example
#     -------
#     >>> print_block("Hello, World!", char="*", n=20, c="blue")
#     ********************
#     * Hello, World!    *
#     ********************
# 
#     Note: The actual output will be in green color.
#     """
#     border = char * n
#     text = f"\n{border}\n{message}\n{border}\n"
#     if c is not None:
#         text = color_text(text, c)
#     print(text)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_print_block.py
# --------------------------------------------------------------------------------
