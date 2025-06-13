#!/usr/bin/env python3
"""Tests for scitex.gen._shell module."""

import pytest
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, call
from scitex.gen import run_shellscript, run_shellcommand


class TestRunShellCommand:
    """Test cases for run_shellcommand function."""

    @patch("subprocess.run")
    @patch("builtins.print")
    def test_run_shellcommand_success(self, mock_print, mock_subprocess_run):
        """Test successful command execution."""
        # Mock successful command
        mock_result = MagicMock()
        mock_result.stdout = "Hello, World!"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        # Run command
        result = run_shellcommand("echo", "Hello, World!")

        # Verify subprocess was called correctly
        mock_subprocess_run.assert_called_once_with(
            ["echo", "Hello, World!"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Verify result
        assert result["stdout"] == "Hello, World!"
        assert result["stderr"] == ""
        assert result["exit_code"] == 0

        # Verify print messages
        mock_print.assert_any_call("Command executed successfully")
        mock_print.assert_any_call("Output:", "Hello, World!")

    @patch("subprocess.run")
    @patch("builtins.print")
    def test_run_shellcommand_failure(self, mock_print, mock_subprocess_run):
        """Test failed command execution."""
        # Mock failed command
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "Command not found"
        mock_result.returncode = 1
        mock_subprocess_run.return_value = mock_result

        # Run command
        result = run_shellcommand("nonexistent_command")

        # Verify result
        assert result["stdout"] == ""
        assert result["stderr"] == "Command not found"
        assert result["exit_code"] == 1

        # Verify print messages
        mock_print.assert_any_call("Command failed with error code:", 1)
        mock_print.assert_any_call("Error:", "Command not found")

    @patch("subprocess.run")
    def test_run_shellcommand_with_multiple_args(self, mock_subprocess_run):
        """Test command with multiple arguments."""
        mock_result = MagicMock()
        mock_result.stdout = "file1.txt file2.txt"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        # Run command with multiple args
        result = run_shellcommand("ls", "-la", "/tmp")

        # Verify subprocess was called with all args
        mock_subprocess_run.assert_called_once_with(
            ["ls", "-la", "/tmp"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        assert result["exit_code"] == 0

    @patch("subprocess.run")
    def test_run_shellcommand_empty_output(self, mock_subprocess_run):
        """Test command with empty output."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = run_shellcommand("true")

        assert result["stdout"] == ""
        assert result["stderr"] == ""
        assert result["exit_code"] == 0

    @patch("subprocess.run")
    def test_run_shellcommand_multiline_output(self, mock_subprocess_run):
        """Test command with multiline output."""
        mock_result = MagicMock()
        mock_result.stdout = "line1\nline2\nline3"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = run_shellcommand("cat", "file.txt")

        assert result["stdout"] == "line1\nline2\nline3"
        assert result["exit_code"] == 0


class TestRunShellScript:
    """Test cases for run_shellscript function."""

    @patch("scitex.gen._shell.run_shellcommand")
    @patch("subprocess.run")
    @patch("os.access")
    def test_run_shellscript_already_executable(
        self, mock_access, mock_subprocess_run, mock_run_shellcommand
    ):
        """Test running script that's already executable."""
        # Mock script is already executable
        mock_access.return_value = True
        mock_run_shellcommand.return_value = {
            "stdout": "Script output",
            "stderr": "",
            "exit_code": 0,
        }

        # Run script
        result = run_shellscript("/path/to/script.sh", "arg1", "arg2")

        # Verify chmod was NOT called
        mock_subprocess_run.assert_not_called()

        # Verify run_shellcommand was called with script and args
        mock_run_shellcommand.assert_called_once_with(
            "/path/to/script.sh", "arg1", "arg2"
        )

        assert result["exit_code"] == 0

    @patch("scitex.gen._shell.run_shellcommand")
    @patch("subprocess.run")
    @patch("os.access")
    def test_run_shellscript_make_executable(
        self, mock_access, mock_subprocess_run, mock_run_shellcommand
    ):
        """Test running script that needs to be made executable."""
        # Mock script is NOT executable
        mock_access.return_value = False
        mock_run_shellcommand.return_value = {
            "stdout": "Script output",
            "stderr": "",
            "exit_code": 0,
        }

        # Run script
        result = run_shellscript("/path/to/script.sh")

        # Verify chmod was called
        mock_subprocess_run.assert_called_once_with(
            ["chmod", "+x", "/path/to/script.sh"]
        )

        # Verify run_shellcommand was called
        mock_run_shellcommand.assert_called_once_with("/path/to/script.sh")

        assert result["exit_code"] == 0

    @patch("scitex.gen._shell.run_shellcommand")
    @patch("os.access")
    def test_run_shellscript_no_args(self, mock_access, mock_run_shellcommand):
        """Test running script with no arguments."""
        mock_access.return_value = True
        mock_run_shellcommand.return_value = {
            "stdout": "No args output",
            "stderr": "",
            "exit_code": 0,
        }

        result = run_shellscript("/path/to/script.sh")

        mock_run_shellcommand.assert_called_once_with("/path/to/script.sh")
        assert result["stdout"] == "No args output"

    def test_run_shellscript_integration(self):
        """Integration test with real temporary script."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            # Write a simple script
            f.write('#!/bin/bash\necho "Hello from script: $1"')
            script_path = f.name

        try:
            # Run the script
            result = run_shellscript(script_path, "TestArg")

            # Verify output
            assert result["exit_code"] == 0
            assert "Hello from script: TestArg" in result["stdout"]
            assert result["stderr"] == ""

            # Verify script was made executable
            assert os.access(script_path, os.X_OK)
        finally:
            # Clean up
            os.unlink(script_path)


class TestEdgeCases:
    """Test edge cases for shell module."""

    @patch("subprocess.run")
    def test_command_with_special_characters(self, mock_subprocess_run):
        """Test command with special shell characters."""
        mock_result = MagicMock()
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        # Special characters should be passed as-is
        result = run_shellcommand("echo", "Hello $USER", "test|pipe", "test&bg")

        mock_subprocess_run.assert_called_once_with(
            ["echo", "Hello $USER", "test|pipe", "test&bg"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    @patch("subprocess.run")
    @patch("builtins.print")
    def test_command_with_nonzero_exit_success(self, mock_print, mock_subprocess_run):
        """Test command that exits with non-zero but might be considered success."""
        mock_result = MagicMock()
        mock_result.stdout = "Partial match found"
        mock_result.stderr = ""
        mock_result.returncode = 1  # grep returns 1 when no match
        mock_subprocess_run.return_value = mock_result

        result = run_shellcommand("grep", "pattern", "file.txt")

        # Function still returns the result
        assert result["exit_code"] == 1
        assert result["stdout"] == "Partial match found"

        # But prints it as failure
        mock_print.assert_any_call("Command failed with error code:", 1)

    @patch("subprocess.run")
    def test_command_with_both_stdout_and_stderr(self, mock_subprocess_run):
        """Test command that produces both stdout and stderr."""
        mock_result = MagicMock()
        mock_result.stdout = "Normal output"
        mock_result.stderr = "Warning: deprecated option"
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = run_shellcommand("some_command", "--deprecated-flag")

        assert result["stdout"] == "Normal output"
        assert result["stderr"] == "Warning: deprecated option"
        assert result["exit_code"] == 0


if __name__ == "__main__":
    import os
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
