#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 22:50:34 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/test__sh.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/test__sh.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2025-06-02 17:41:00 (ywatanabe)"

"""Comprehensive tests for shell command execution functionality."""

import subprocess
from unittest.mock import Mock, patch

import pytest
from scitex._sh import sh


class TestShBasic:
    """Test basic shell command execution functionality."""

    def test_function_exists(self):
        """Test that sh function is importable."""
        assert callable(sh)

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_successful_command(self, mock_color_text, mock_popen):
        """Test successful command execution."""
        # Mock subprocess behavior
        mock_process = Mock()
        mock_process.communicate.return_value = (b"hello world\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "echo 'hello world'"

        with patch("builtins.print") as mock_print:
            result = sh("echo 'hello world'", verbose=True)

        assert result == "hello world"
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_command_with_error(self, mock_color_text, mock_popen):
        """Test command execution with error."""
        # Mock subprocess behavior for error case
        mock_process = Mock()
        mock_process.communicate.return_value = (b"", b"command not found\n")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "nonexistent_command"

        with patch("builtins.print") as mock_print:
            result = sh("nonexistent_command", verbose=True)

        assert result == "command not found"
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_verbose_false(self, mock_color_text, mock_popen):
        """Test command execution with verbose=False."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        with patch("builtins.print") as mock_print:
            result = sh("echo test", verbose=False)

        assert result == "output"
        # Should not call color_text or print when verbose=False
        mock_color_text.assert_not_called()
        mock_print.assert_not_called()


class TestShSubprocessIntegration:
    """Test subprocess.Popen integration."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_subprocess_popen_called_correctly(
        self, mock_color_text, mock_popen
    ):
        """Test that subprocess.Popen is called with correct parameters."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"test\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "test command"

        sh("test command", verbose=False)

        # Verify subprocess.Popen was called with correct arguments
        mock_popen.assert_called_once_with(
            "test command",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_process_communicate_called(self, mock_color_text, mock_popen):
        """Test that process.communicate() is called."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        sh("command", verbose=False)

        mock_process.communicate.assert_called_once()

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_return_code_handling(self, mock_color_text, mock_popen):
        """Test handling of different return codes."""
        mock_process = Mock()
        mock_color_text.return_value = "command"
        mock_popen.return_value = mock_process

        # Test success case (returncode = 0)
        mock_process.communicate.return_value = (
            b"success output\n",
            b"error output\n",
        )
        mock_process.returncode = 0
        result = sh("command", verbose=False)
        assert result == "success output"

        # Test error case (returncode != 0)
        mock_process.communicate.return_value = (
            b"success output\n",
            b"error output\n",
        )
        mock_process.returncode = 1
        result = sh("command", verbose=False)
        assert result == "error output"


class TestShOutputHandling:
    """Test output handling and processing."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_output_decoding(self, mock_color_text, mock_popen):
        """Test that output is properly decoded from bytes."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"utf-8 output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        result = sh("command", verbose=False)
        assert result == "utf-8 output"
        assert isinstance(result, str)

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_output_stripping(self, mock_color_text, mock_popen):
        """Test that output is properly stripped of whitespace."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b"  output with spaces  \n\n",
            b"",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        result = sh("command", verbose=False)
        assert result == "output with spaces"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_error_output_decoding(self, mock_color_text, mock_popen):
        """Test that error output is properly decoded."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"", b"error message\n")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        result = sh("command", verbose=False)
        assert result == "error message"
        assert isinstance(result, str)

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_empty_output(self, mock_color_text, mock_popen):
        """Test handling of empty output."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        result = sh("command", verbose=False)
        assert result == ""


class TestShVerboseMode:
    """Test verbose mode functionality."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_verbose_command_display(self, mock_color_text, mock_popen):
        """Test that command is displayed when verbose=True."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "colored command"

        with patch("builtins.print") as mock_print:
            sh("test command", verbose=True)

        # Should call color_text to format command
        mock_color_text.assert_called_once_with("test command", "yellow")

        # Should print both command and output
        assert mock_print.call_count == 2

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_verbose_output_display(self, mock_color_text, mock_popen):
        """Test that output is displayed when verbose=True."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"command output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "colored command"

        with patch("builtins.print") as mock_print:
            result = sh("command", verbose=True)

        # Verify output content
        assert result == "command output"

        # Check that print was called for output
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert "command output" in print_calls

    @patch("subprocess.Popen")
    def test_verbose_false_no_print(self, mock_popen):
        """Test that nothing is printed when verbose=False."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        with patch("builtins.print") as mock_print:
            with patch("scitex.str.color_text") as mock_color_text:
                sh("command", verbose=False)

        mock_print.assert_not_called()
        mock_color_text.assert_not_called()


class TestShEdgeCases:
    """Test edge cases and error conditions."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_unicode_output(self, mock_color_text, mock_popen):
        """Test handling of unicode in output."""
        mock_process = Mock()
        # Unicode characters in bytes
        unicode_output = "Hello café naïve résumé".encode("utf-8")
        mock_process.communicate.return_value = (unicode_output + b"\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        result = sh("command", verbose=False)
        assert result == "Hello café naïve résumé"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_multiline_output(self, mock_color_text, mock_popen):
        """Test handling of multiline output."""
        mock_process = Mock()
        multiline_output = b"line1\nline2\nline3\n"
        mock_process.communicate.return_value = (multiline_output, b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command"

        result = sh("command", verbose=False)
        assert result == "line1\nline2\nline3"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_special_characters_in_command(self, mock_color_text, mock_popen):
        """Test commands with special characters."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "special command"

        special_command = "echo 'Hello & World' | grep Hello"
        result = sh(special_command, verbose=False)

        # Verify command was passed correctly to subprocess
        mock_popen.assert_called_once_with(
            special_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_empty_command(self, mock_color_text, mock_popen):
        """Test behavior with empty command string."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = ""

        result = sh("", verbose=False)
        assert result == ""

        mock_popen.assert_called_once_with(
            "", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )


class TestShRealWorldScenarios:
    """Test real-world usage scenarios."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_ls_command_simulation(self, mock_color_text, mock_popen):
        """Test simulated ls command."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b"file1.txt\nfile2.py\ndir1\n",
            b"",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "ls"

        result = sh("ls", verbose=False)
        assert result == "file1.txt\nfile2.py\ndir1"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_pwd_command_simulation(self, mock_color_text, mock_popen):
        """Test simulated pwd command."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"/home/user/project\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "pwd"

        result = sh("pwd", verbose=False)
        assert result == "/home/user/project"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_git_command_simulation(self, mock_color_text, mock_popen):
        """Test simulated git command."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b"On branch main\nnothing to commit\n",
            b"",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "git status"

        result = sh("git status", verbose=False)
        assert result == "On branch main\nnothing to commit"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_python_command_simulation(self, mock_color_text, mock_popen):
        """Test simulated python command."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"Hello from Python\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = (
            "python -c 'print(\"Hello from Python\")'"
        )

        result = sh("python -c 'print(\"Hello from Python\")'", verbose=False)
        assert result == "Hello from Python"


class TestShErrorHandling:
    """Test error handling scenarios."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_command_not_found(self, mock_color_text, mock_popen):
        """Test handling of command not found error."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b"",
            b"command not found: badcommand\n",
        )
        mock_process.returncode = 127
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "badcommand"

        result = sh("badcommand", verbose=False)
        assert result == "command not found: badcommand"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_permission_denied(self, mock_color_text, mock_popen):
        """Test handling of permission denied error."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"", b"Permission denied\n")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "restricted_command"

        result = sh("restricted_command", verbose=False)
        assert result == "Permission denied"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_syntax_error_in_command(self, mock_color_text, mock_popen):
        """Test handling of syntax errors in shell commands."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b"",
            b"syntax error near unexpected token\n",
        )
        mock_process.returncode = 2
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "echo (()"

        result = sh("echo (()", verbose=False)
        assert result == "syntax error near unexpected token"


class TestShIntegration:
    """Integration tests for complete workflows."""

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_chained_commands(self, mock_color_text, mock_popen):
        """Test execution of chained shell commands."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"filtered_output\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "ls | grep .py"

        result = sh("ls | grep .py", verbose=False)
        assert result == "filtered_output"

        # Verify the full command was passed to shell
        mock_popen.assert_called_once_with(
            "ls | grep .py",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_command_with_arguments(self, mock_color_text, mock_popen):
        """Test commands with multiple arguments."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b"command executed with args\n",
            b"",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "command --flag value"

        result = sh("command --flag value", verbose=False)
        assert result == "command executed with args"

    @patch("subprocess.Popen")
    @patch("scitex.str.color_text")
    def test_environment_variable_usage(self, mock_color_text, mock_popen):
        """Test commands that use environment variables."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b"/home/user\n", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_color_text.return_value = "echo $HOME"

        result = sh("echo $HOME", verbose=False)
        assert result == "/home/user"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/_sh.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-13 22:51:08 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/_sh.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/_sh.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# # Time-stamp: "2024-11-03 02:23:16 (ywatanabe)"
# 
# import subprocess
# 
# import scitex
# 
# 
# def sh(command_str, verbose=True):
#     """
#     Executes a shell command from Python.
# 
#     Parameters:
#     - command_str (str): The command string to execute.
# 
#     Returns:
#     - output (str): The standard output from the executed command.
#     """
#     if verbose:
#         print(scitex.str.color_text(f"{command_str}", "yellow"))
# 
#     process = subprocess.Popen(
#         command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#     )
#     output, error = process.communicate()
#     if process.returncode == 0:
#         out = output.decode("utf-8").strip()
#     else:
#         out = error.decode("utf-8").strip()
# 
#     if verbose:
#         print(out)
# 
#     return out
# 
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys, plt, verbose=False
#     )
#     sh("ls")
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/_sh.py
# --------------------------------------------------------------------------------
