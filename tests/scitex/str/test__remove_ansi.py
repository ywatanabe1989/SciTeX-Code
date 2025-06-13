#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__remove_ansi.py

"""Comprehensive tests for ANSI escape sequence removal functionality."""

import os
import pytest
from scitex.str import remove_ansi


class TestRemoveAnsiBasic:
    """Test basic ANSI code removal functionality."""

    def test_basic_color_codes(self):
        """Test removal of basic color codes."""
        colored = "\033[91mRed Text\033[0m"
        assert remove_ansi(colored) == "Red Text"
        
        green = "\033[92mGreen Text\033[0m"
        assert remove_ansi(green) == "Green Text"
        
        blue = "\033[94mBlue Text\033[0m"
        assert remove_ansi(blue) == "Blue Text"

    def test_multiple_codes(self):
        """Test removal of multiple ANSI codes."""
        text = "\033[1m\033[91mBold Red\033[0m Normal \033[92mGreen\033[0m"
        assert remove_ansi(text) == "Bold Red Normal Green"

    def test_no_codes(self):
        """Test with text that has no ANSI codes."""
        plain_text = "This is plain text"
        assert remove_ansi(plain_text) == plain_text
        
        unicode_text = "Unicode: café, naïve, résumé"
        assert remove_ansi(unicode_text) == unicode_text

    def test_empty_string(self):
        """Test with empty string."""
        assert remove_ansi("") == ""


class TestRemoveAnsiComplexSequences:
    """Test removal of complex ANSI escape sequences."""

    def test_cursor_control_sequences(self):
        """Test removal of cursor control sequences."""
        text = "\033[2J\033[H\033[1;32mHello\033[0m\033[?25l"
        assert remove_ansi(text) == "Hello"
        
        cursor_move = "\033[10;20HPositioned Text\033[0m"
        assert remove_ansi(cursor_move) == "Positioned Text"

    def test_complex_formatting(self):
        """Test removal of complex formatting sequences."""
        # Bold, italic, underline combinations
        text = "\033[1;3;4mBold Italic Underline\033[0m"
        assert remove_ansi(text) == "Bold Italic Underline"
        
        # 256-color codes
        color256 = "\033[38;5;196mBright Red\033[0m"
        assert remove_ansi(color256) == "Bright Red"
        
        # RGB color codes
        rgb_color = "\033[38;2;255;0;0mRGB Red\033[0m"
        assert remove_ansi(rgb_color) == "RGB Red"

    def test_terminal_control_sequences(self):
        """Test removal of terminal control sequences."""
        # Clear screen and home cursor
        clear_screen = "\033[2J\033[HContent"
        assert remove_ansi(clear_screen) == "Content"
        
        # Save/restore cursor position
        cursor_save = "\033[sText\033[u"
        assert remove_ansi(cursor_save) == "Text"
        
        # Hide/show cursor
        cursor_hide = "\033[?25lHidden\033[?25h"
        assert remove_ansi(cursor_hide) == "Hidden"


class TestRemoveAnsiEdgeCases:
    """Test edge cases and special scenarios."""

    def test_incomplete_sequences(self):
        """Test handling of incomplete ANSI sequences."""
        # Incomplete escape sequence
        incomplete = "\033[Incomplete sequence"
        result = remove_ansi(incomplete)
        # Should handle gracefully
        assert isinstance(result, str)
        
        # Malformed sequence
        malformed = "\033Normal text"
        result = remove_ansi(malformed)
        assert isinstance(result, str)

    def test_mixed_content(self):
        """Test text with mixed ANSI codes and special characters."""
        mixed = "\033[91mError:\033[0m File 'test.py', line 42\n\033[92mSuccess!\033[0m"
        expected = "Error: File 'test.py', line 42\nSuccess!"
        assert remove_ansi(mixed) == expected
        
        # Text with tabs and newlines
        tabbed = "\033[1mHeader\033[0m\n\tIndented\033[92m green\033[0m"
        expected_tabbed = "Header\n\tIndented green"
        assert remove_ansi(tabbed) == expected_tabbed

    def test_consecutive_sequences(self):
        """Test multiple consecutive ANSI sequences."""
        consecutive = "\033[1m\033[91m\033[4mTriple Format\033[0m\033[0m\033[0m"
        assert remove_ansi(consecutive) == "Triple Format"
        
        # Multiple resets
        resets = "Text\033[0m\033[0m\033[0m"
        assert remove_ansi(resets) == "Text"

    def test_embedded_sequences(self):
        """Test ANSI sequences embedded in text."""
        embedded = "Start\033[91mmiddle\033[0mend"
        assert remove_ansi(embedded) == "Startmiddleend"
        
        # Multiple embedded sequences
        multiple = "A\033[1mB\033[0mC\033[92mD\033[0mE"
        assert remove_ansi(multiple) == "ABCDE"


class TestRemoveAnsiSpecialCharacters:
    """Test ANSI removal with special characters and unicode."""

    def test_unicode_with_ansi(self):
        """Test unicode text with ANSI codes."""
        unicode_ansi = "\033[91mCafé\033[0m and \033[92mnaïve\033[0m"
        assert remove_ansi(unicode_ansi) == "Café and naïve"
        
        # Emoji with ANSI
        emoji_ansi = "\033[1m🎉 Celebration! 🎉\033[0m"
        assert remove_ansi(emoji_ansi) == "🎉 Celebration! 🎉"

    def test_special_whitespace(self):
        """Test with various whitespace characters."""
        # Non-breaking space
        nbsp = "\033[91mText\u00A0with\u00A0NBSP\033[0m"
        assert remove_ansi(nbsp) == "Text\u00A0with\u00A0NBSP"
        
        # Various unicode spaces
        spaces = "\033[1mText\u2000with\u2003spaces\033[0m"
        assert remove_ansi(spaces) == "Text\u2000with\u2003spaces"

    def test_control_characters(self):
        """Test with control characters mixed with ANSI."""
        # Bell character
        bell = "\033[91mAlert\033[0m\a"
        assert remove_ansi(bell) == "Alert\a"
        
        # Carriage return and line feed
        crlf = "\033[1mLine 1\033[0m\r\nLine 2"
        assert remove_ansi(crlf) == "Line 1\r\nLine 2"


class TestRemoveAnsiRealWorld:
    """Test real-world scenarios and use cases."""

    def test_terminal_output(self):
        """Test typical terminal output patterns."""
        # Git output style
        git_output = "\033[32m+\033[0m Added line\n\033[31m-\033[0m Removed line"
        expected = "+ Added line\n- Removed line"
        assert remove_ansi(git_output) == expected
        
        # Pytest output style
        pytest_output = "\033[32m.\033[0m\033[31mF\033[0m\033[33mE\033[0m"
        assert remove_ansi(pytest_output) == ".FE"

    def test_log_messages(self):
        """Test log message patterns."""
        # Error log
        error_log = "\033[91m[ERROR]\033[0m Database connection failed"
        assert remove_ansi(error_log) == "[ERROR] Database connection failed"
        
        # Info log with timestamp
        info_log = "\033[94m[INFO]\033[0m 2024-01-01 12:00:00 - Process started"
        expected = "[INFO] 2024-01-01 12:00:00 - Process started"
        assert remove_ansi(info_log) == expected

    def test_progress_indicators(self):
        """Test progress bar and spinner patterns."""
        # Progress bar
        progress = "\033[32m█████\033[0m\033[90m░░░░░\033[0m 50%"
        assert remove_ansi(progress) == "█████░░░░░ 50%"
        
        # Spinner
        spinner = "\033[1m|\033[0m Processing..."
        assert remove_ansi(spinner) == "| Processing..."

    def test_formatted_tables(self):
        """Test formatted table output."""
        table_row = "\033[1mName\033[0m     \033[1mAge\033[0m     \033[1mCity\033[0m"
        assert remove_ansi(table_row) == "Name     Age     City"
        
        data_row = "\033[32mJohn\033[0m     25      \033[94mNY\033[0m"
        assert remove_ansi(data_row) == "John     25      NY"


class TestRemoveAnsiValidation:
    """Test input validation and error handling."""

    def test_none_input(self):
        """Test behavior with None input."""
        # Function should handle None gracefully or raise appropriate error
        try:
            result = remove_ansi(None)
            # If it doesn't raise, result should be reasonable
            assert result is None or result == ""
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass

    def test_non_string_input(self):
        """Test behavior with non-string input."""
        # Integer input
        try:
            result = remove_ansi(123)
            # If it doesn't raise, result should be string
            assert isinstance(result, str)
        except (TypeError, AttributeError):
            # Expected behavior for non-string input
            pass
        
        # List input
        try:
            result = remove_ansi(["test"])
            assert isinstance(result, str)
        except (TypeError, AttributeError):
            pass

    def test_very_long_string(self):
        """Test with very long strings."""
        # Long string with ANSI codes
        long_text = "\033[91m" + "A" * 10000 + "\033[0m"
        result = remove_ansi(long_text)
        assert result == "A" * 10000
        assert len(result) == 10000

    def test_many_ansi_codes(self):
        """Test string with many ANSI codes."""
        # Create string with many alternating ANSI codes
        many_codes = ""
        for i in range(100):
            many_codes += f"\033[9{i%8}mChar{i}\033[0m"
        
        result = remove_ansi(many_codes)
        expected = "".join(f"Char{i}" for i in range(100))
        assert result == expected


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
