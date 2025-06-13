#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 02:55:22 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__less.py

"""Test suite for scitex.gen._less module."""

import pytest
from unittest.mock import patch, MagicMock, call, mock_open
import tempfile
import os
from scitex.gen import less


class TestLess:
    """Test cases for the less function."""

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_basic_functionality(
        self, mock_tempfile, mock_remove, mock_get_ipython
    ):
        """Test that less properly displays output through IPython system command."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_file.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test
        test_output = "Hello, World!"
        less(test_output)

        # Verify
        mock_tempfile.assert_called_once_with(delete=False, mode="w+t")
        mock_file.write.assert_called_once_with(test_output)
        mock_ipython.system.assert_called_once_with(f"less {mock_file.name}")
        mock_remove.assert_called_once_with(mock_file.name)

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_with_multiline_output(
        self, mock_tempfile, mock_remove, mock_get_ipython
    ):
        """Test less with multi-line text output."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_multiline.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test with multi-line content
        test_output = """Line 1
Line 2
Line 3
This is a longer line with more content
Last line"""
        less(test_output)

        # Verify
        mock_file.write.assert_called_once_with(test_output)
        mock_ipython.system.assert_called_once_with(f"less {mock_file.name}")
        mock_remove.assert_called_once_with(mock_file.name)

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_with_special_characters(
        self, mock_tempfile, mock_remove, mock_get_ipython
    ):
        """Test less with special characters and unicode."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_special.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test with special characters
        test_output = "Special chars: @#$%^&*() Unicode: 你好世界 Émojis: 🚀💻"
        less(test_output)

        # Verify
        mock_file.write.assert_called_once_with(test_output)
        mock_ipython.system.assert_called_once()

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_temp_file_cleanup(self, mock_tempfile, mock_remove, mock_get_ipython):
        """Test that temporary file is created and cleaned up properly."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_cleanup.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test normal operation
        less("Test output")

        # Verify cleanup was called
        mock_remove.assert_called_once_with(mock_file.name)

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_error_no_cleanup(self, mock_tempfile, mock_remove, mock_get_ipython):
        """Test that cleanup is NOT called when system command fails."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_no_cleanup.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        # Simulate an error in system call
        mock_ipython.system.side_effect = Exception("System command failed")
        mock_get_ipython.return_value = mock_ipython

        # Test - should raise exception and NOT cleanup
        with pytest.raises(Exception, match="System command failed"):
            less("Test output")

        # Verify cleanup was NOT called due to exception
        mock_remove.assert_not_called()

    @patch("IPython.get_ipython")
    def test_less_error_handling(self, mock_get_ipython):
        """Test error handling when IPython is not available."""
        # Simulate IPython not being available
        mock_get_ipython.return_value = None

        # This should raise an AttributeError when trying to call .system()
        with pytest.raises(AttributeError):
            less("Test output")


class TestLessIPythonIntegration:
    """Test cases for IPython-specific functionality."""

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_in_ipython_environment(
        self, mock_tempfile, mock_remove, mock_get_ipython
    ):
        """Test less when running in actual IPython environment."""
        # Setup mocks to simulate IPython environment
        mock_file = MagicMock()
        mock_file.name = "/tmp/ipython_test.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_ipython.__class__.__name__ = "TerminalInteractiveShell"
        mock_get_ipython.return_value = mock_ipython

        # Test
        less("IPython test content")

        # Verify IPython system was called
        mock_ipython.system.assert_called_once()

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_system_command_execution(
        self, mock_tempfile, mock_remove, mock_get_ipython
    ):
        """Test that the system command is called correctly."""
        # Setup mocks
        mock_file = MagicMock()
        test_filename = "/tmp/less_test_123.txt"
        mock_file.name = test_filename
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test
        less("Command test")

        # Verify exact command
        expected_command = f"less {test_filename}"
        mock_ipython.system.assert_called_once_with(expected_command)


class TestLessEdgeCases:
    """Test edge cases for the less function."""

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_empty_output(self, mock_tempfile, mock_remove, mock_get_ipython):
        """Test less with empty string output."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/empty.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test with empty string
        less("")

        # Verify empty string was written
        mock_file.write.assert_called_once_with("")
        mock_ipython.system.assert_called_once()
        mock_remove.assert_called_once()

    @patch("IPython.get_ipython")
    @patch("os.remove")
    @patch("tempfile.NamedTemporaryFile")
    def test_less_very_large_output(self, mock_tempfile, mock_remove, mock_get_ipython):
        """Test less with very large output."""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = "/tmp/large.txt"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        mock_ipython = MagicMock()
        mock_get_ipython.return_value = mock_ipython

        # Test with large content
        large_output = "x" * 10000 + "\n" + "y" * 10000
        less(large_output)

        # Verify
        mock_file.write.assert_called_once_with(large_output)
        mock_ipython.system.assert_called_once()
        mock_remove.assert_called_once()


def test_main():
    """Main function for running tests."""
    pytest.main([__file__, "-xvs"])


if __name__ == "__main__":
    test_main()

# EOF
