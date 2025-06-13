#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 02:55:27 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__paste.py

"""Test suite for scitex.gen._paste module."""

import pytest
from unittest.mock import patch, MagicMock, call
import textwrap
from scitex.gen import paste


class TestPaste:
    """Test cases for the paste function."""

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_basic_functionality(self, mock_pyperclip_paste, mock_exec):
        """Test basic paste and execution functionality."""
        # Setup mock clipboard content
        clipboard_content = "print('Hello from clipboard')"
        mock_pyperclip_paste.return_value = clipboard_content

        # Test
        paste()

        # Verify
        mock_pyperclip_paste.assert_called_once()
        mock_exec.assert_called_once_with(clipboard_content)

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_with_indented_code(self, mock_pyperclip_paste, mock_exec):
        """Test paste with indented code (dedenting)."""
        # Setup mock clipboard content with indentation
        clipboard_content = """
            def hello():
                print('Hello')
                return 42
            
            result = hello()
        """
        mock_pyperclip_paste.return_value = clipboard_content

        # Expected dedented content
        expected_dedented = textwrap.dedent(clipboard_content)

        # Test
        paste()

        # Verify dedenting was applied
        mock_exec.assert_called_once_with(expected_dedented)

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_multiline_code(self, mock_pyperclip_paste, mock_exec):
        """Test paste with multiline code."""
        # Setup mock clipboard content
        clipboard_content = """
x = 10
y = 20
z = x + y
print(f'Result: {z}')
"""
        mock_pyperclip_paste.return_value = clipboard_content

        # Test
        paste()

        # Verify
        mock_pyperclip_paste.assert_called_once()
        mock_exec.assert_called_once_with(textwrap.dedent(clipboard_content))

    @patch("builtins.print")
    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_syntax_error(self, mock_pyperclip_paste, mock_exec, mock_print):
        """Test paste with code that has syntax errors."""
        # Setup mock clipboard content with syntax error
        clipboard_content = "print('Missing closing quote"
        mock_pyperclip_paste.return_value = clipboard_content

        # Setup exec to raise SyntaxError
        mock_exec.side_effect = SyntaxError("EOL while scanning string literal")

        # Test
        paste()

        # Verify error was caught and printed
        mock_print.assert_called_once()
        error_msg = mock_print.call_args[0][0]
        assert "Could not execute clipboard content:" in error_msg
        assert "EOL while scanning string literal" in error_msg

    @patch("builtins.print")
    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_runtime_error(self, mock_pyperclip_paste, mock_exec, mock_print):
        """Test paste with code that raises runtime errors."""
        # Setup mock clipboard content
        clipboard_content = "1 / 0"
        mock_pyperclip_paste.return_value = clipboard_content

        # Setup exec to raise ZeroDivisionError
        mock_exec.side_effect = ZeroDivisionError("division by zero")

        # Test
        paste()

        # Verify error was caught and printed
        mock_print.assert_called_once()
        error_msg = mock_print.call_args[0][0]
        assert "Could not execute clipboard content:" in error_msg
        assert "division by zero" in error_msg

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_empty_clipboard(self, mock_pyperclip_paste, mock_exec):
        """Test paste with empty clipboard."""
        # Setup mock empty clipboard
        mock_pyperclip_paste.return_value = ""

        # Test
        paste()

        # Verify exec was called with empty string
        mock_exec.assert_called_once_with("")

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_whitespace_only(self, mock_pyperclip_paste, mock_exec):
        """Test paste with whitespace-only content."""
        # Setup mock whitespace content
        clipboard_content = "   \n\t  \n   "
        mock_pyperclip_paste.return_value = clipboard_content

        # Test
        paste()

        # Verify exec was called with dedented whitespace
        mock_exec.assert_called_once_with(textwrap.dedent(clipboard_content))

    @patch("builtins.print")
    @patch("pyperclip.paste")
    def test_paste_clipboard_access_error(self, mock_pyperclip_paste, mock_print):
        """Test paste when clipboard access fails."""
        # Setup pyperclip to raise an exception
        mock_pyperclip_paste.side_effect = Exception("Clipboard access denied")

        # Test
        paste()

        # Verify error was caught and printed
        mock_print.assert_called_once()
        error_msg = mock_print.call_args[0][0]
        assert "Could not execute clipboard content:" in error_msg
        assert "Clipboard access denied" in error_msg


class TestPasteEdgeCases:
    """Test edge cases for the paste function."""

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_with_unicode(self, mock_pyperclip_paste, mock_exec):
        """Test paste with unicode characters."""
        # Setup mock clipboard content with unicode
        clipboard_content = "print('Hello 世界! 🚀')"
        mock_pyperclip_paste.return_value = clipboard_content

        # Test
        paste()

        # Verify
        mock_exec.assert_called_once_with(clipboard_content)

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_with_complex_indentation(self, mock_pyperclip_paste, mock_exec):
        """Test paste with complex mixed indentation."""
        # Setup mock clipboard content with complex indentation
        clipboard_content = """
            class MyClass:
                def __init__(self):
                    self.value = 42
                    
                def method(self):
                    if self.value > 0:
                        print("Positive")
                    else:
                        print("Non-positive")
        """
        mock_pyperclip_paste.return_value = clipboard_content

        # Test
        paste()

        # Verify dedenting was applied correctly
        expected = textwrap.dedent(clipboard_content)
        mock_exec.assert_called_once_with(expected)

    @patch("builtins.print")
    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_with_import_error(self, mock_pyperclip_paste, mock_exec, mock_print):
        """Test paste with code that raises ImportError."""
        # Setup mock clipboard content
        clipboard_content = "import nonexistent_module"
        mock_pyperclip_paste.return_value = clipboard_content

        # Setup exec to raise ImportError
        mock_exec.side_effect = ImportError("No module named 'nonexistent_module'")

        # Test
        paste()

        # Verify error was caught and printed
        mock_print.assert_called_once()
        error_msg = mock_print.call_args[0][0]
        assert "Could not execute clipboard content:" in error_msg
        assert "No module named 'nonexistent_module'" in error_msg


class TestPasteIntegration:
    """Integration tests for paste function."""

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_executes_in_correct_namespace(self, mock_pyperclip_paste, mock_exec):
        """Test that pasted code executes in the correct namespace."""
        # Setup mock clipboard content
        clipboard_content = "test_var = 123"
        mock_pyperclip_paste.return_value = clipboard_content

        # Test
        paste()

        # Verify exec was called
        mock_exec.assert_called_once_with(clipboard_content)

    @patch("builtins.exec")
    @patch("pyperclip.paste")
    def test_paste_preserves_line_endings(self, mock_pyperclip_paste, mock_exec):
        """Test that paste preserves different line ending styles."""
        # Test with Unix line endings
        clipboard_content = "line1\nline2\nline3"
        mock_pyperclip_paste.return_value = clipboard_content
        paste()
        mock_exec.assert_called_with(clipboard_content)

        # Test with Windows line endings
        clipboard_content = "line1\r\nline2\r\nline3"
        mock_pyperclip_paste.return_value = clipboard_content
        paste()
        # textwrap.dedent should handle this correctly
        mock_exec.assert_called_with(textwrap.dedent(clipboard_content))


def test_main():
    """Main function for running tests."""
    pytest.main([__file__, "-xvs"])


if __name__ == "__main__":
    test_main()

# EOF
