import io
import os
import sys
import tempfile
from unittest.mock import MagicMock, Mock, patch, mock_open

import pytest

from scitex.gen import Tee, tee


class TestTeeClass:
    """Test the Tee class functionality."""

    def test_tee_stdout_initialization(self):
        """Test Tee initialization with stdout."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            log_path = f.name

        try:
            tee_obj = Tee(sys.stdout, log_path)
            assert tee_obj._stream is sys.stdout
            assert tee_obj._is_stderr is False
            assert tee_obj._log_file is not None
        finally:
            tee_obj.close()
            os.unlink(log_path)

    def test_tee_stderr_initialization(self):
        """Test Tee initialization with stderr."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            log_path = f.name

        try:
            tee_obj = Tee(sys.stderr, log_path)
            assert tee_obj._stream is sys.stderr
            assert tee_obj._is_stderr is True
            assert tee_obj._log_file is not None
        finally:
            tee_obj.close()
            os.unlink(log_path)

    def test_tee_write_stdout(self):
        """Test writing to stdout through Tee."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            log_path = f.name

        mock_stdout = Mock()
        tee_obj = Tee(mock_stdout, log_path)

        try:
            test_msg = "Test stdout message\n"
            tee_obj.write(test_msg)

            # Check stdout was written to
            mock_stdout.write.assert_called_once_with(test_msg)

            # Check log file was written to
            tee_obj.close()
            with open(log_path, "r") as f:
                assert f.read() == test_msg
        finally:
            os.unlink(log_path)

    def test_tee_write_stderr_filters_progress_bars(self):
        """Test that stderr filters out progress bar patterns."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            log_path = f.name

        mock_stderr = Mock()
        tee_obj = Tee(mock_stderr, log_path)
        tee_obj._is_stderr = True

        try:
            # Write normal error message
            error_msg = "Error: Something went wrong\n"
            tee_obj.write(error_msg)

            # Write progress bar pattern (should be filtered)
            progress_msg = "  50%|██████████████      | 50/100 [00:10<00:10]"
            tee_obj.write(progress_msg)

            # Check stderr received both messages
            assert mock_stderr.write.call_count == 2

            # Check log file only has the error message
            tee_obj.close()
            with open(log_path, "r") as f:
                content = f.read()
                assert error_msg in content
                assert progress_msg not in content
        finally:
            os.unlink(log_path)

    def test_tee_flush(self):
        """Test flush method."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            log_path = f.name

        mock_stream = Mock()
        tee_obj = Tee(mock_stream, log_path)

        try:
            tee_obj.flush()
            mock_stream.flush.assert_called_once()
        finally:
            tee_obj.close()
            os.unlink(log_path)

    def test_tee_isatty(self):
        """Test isatty method delegation."""
        mock_stream = Mock()
        mock_stream.isatty.return_value = True

        with tempfile.NamedTemporaryFile(mode="w") as f:
            tee_obj = Tee(mock_stream, f.name)
            assert tee_obj.isatty() is True
            mock_stream.isatty.assert_called_once()
            tee_obj.close()

    def test_tee_fileno(self):
        """Test fileno method delegation."""
        mock_stream = Mock()
        mock_stream.fileno.return_value = 42

        with tempfile.NamedTemporaryFile(mode="w") as f:
            tee_obj = Tee(mock_stream, f.name)
            assert tee_obj.fileno() == 42
            mock_stream.fileno.assert_called_once()
            tee_obj.close()

    def test_tee_buffer_property(self):
        """Test buffer property delegation."""
        mock_stream = Mock()
        mock_buffer = Mock()
        mock_stream.buffer = mock_buffer

        with tempfile.NamedTemporaryFile(mode="w") as f:
            tee_obj = Tee(mock_stream, f.name)
            assert tee_obj.buffer is mock_buffer
            tee_obj.close()

    def test_tee_close(self):
        """Test explicit close method."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            log_path = f.name

        try:
            tee_obj = Tee(sys.stdout, log_path)
            tee_obj.write("Test before close\n")
            tee_obj.close()

            # Verify file was written
            with open(log_path, "r") as f:
                assert "Test before close\n" in f.read()

            # Verify double close doesn't raise
            tee_obj.close()
        finally:
            os.unlink(log_path)

    def test_tee_failed_file_open(self):
        """Test handling of failed file open."""
        # Try to open in a non-existent directory
        invalid_path = "/nonexistent/directory/test.log"

        with patch("scitex.gen._tee.printc") as mock_printc:
            tee_obj = Tee(sys.stdout, invalid_path)

            # Should print error message
            mock_printc.assert_called_once()
            assert "Failed to open log file" in mock_printc.call_args[0][0]

            # Should still work without crashing
            tee_obj.write("Test message")
            tee_obj.flush()
            tee_obj.close()


class TestTeeFunction:
    """Test the tee function."""

    @patch("scitex.gen._tee.printc")
    @patch("os.makedirs")
    def test_tee_function_basic(self, mock_makedirs, mock_printc):
        """Test basic tee function usage."""
        mock_sys = Mock()
        mock_sys.stdout = Mock()
        mock_sys.stderr = Mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            stdout_tee, stderr_tee = tee(mock_sys, sdir=tmpdir)

            # Verify Tee objects were created
            assert isinstance(stdout_tee, Tee)
            assert isinstance(stderr_tee, Tee)
            assert stdout_tee._stream is mock_sys.stdout
            assert stderr_tee._stream is mock_sys.stderr

            # Clean up
            stdout_tee.close()
            stderr_tee.close()

    @patch("scitex.gen._tee.printc")
    @patch("os.makedirs")
    @patch("inspect.stack")
    def test_tee_function_auto_sdir(self, mock_stack, mock_makedirs, mock_printc):
        """Test tee function with automatic sdir determination."""
        # Mock the stack to return a fake filename
        mock_frame = Mock()
        mock_frame.filename = "/path/to/test_script.py"
        mock_stack.return_value = [None, mock_frame]

        mock_sys = Mock()
        mock_sys.stdout = Mock()
        mock_sys.stderr = Mock()

        stdout_tee, stderr_tee = tee(mock_sys)

        # Check that makedirs was called with the expected path
        expected_dir = "/path/to/test_script_out/logs/"
        mock_makedirs.assert_called_with(expected_dir, exist_ok=True)

        # Clean up
        stdout_tee.close()
        stderr_tee.close()

    @patch("scitex.gen._tee.printc")
    @patch("os.makedirs")
    @patch("inspect.stack")
    def test_tee_function_ipython_sdir(self, mock_stack, mock_makedirs, mock_printc):
        """Test tee function in IPython environment."""
        # Mock the stack to return an IPython filename
        mock_frame = Mock()
        mock_frame.filename = "/path/to/ipython/console.py"
        mock_stack.return_value = [None, mock_frame]

        mock_sys = Mock()
        mock_sys.stdout = Mock()
        mock_sys.stderr = Mock()

        with patch.dict(os.environ, {"USER": "testuser"}):
            stdout_tee, stderr_tee = tee(mock_sys)

        # Check that the temp directory was used
        expected_dir = "/tmp/testuser_out/logs/"
        mock_makedirs.assert_called_with(expected_dir, exist_ok=True)

        # Clean up
        stdout_tee.close()
        stderr_tee.close()

    @patch("scitex.gen._tee.printc")
    @patch("os.makedirs")
    def test_tee_function_verbose(self, mock_makedirs, mock_printc):
        """Test tee function with verbose output."""
        mock_sys = Mock()
        mock_sys.stdout = Mock()
        mock_sys.stderr = Mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            stdout_tee, stderr_tee = tee(mock_sys, sdir=tmpdir, verbose=True)

            # Check that printc was called with log file paths
            mock_printc.assert_called_once()
            assert (
                "Standard output/error are being logged at:"
                in mock_printc.call_args[0][0]
            )
            assert "stdout.log" in mock_printc.call_args[0][0]
            assert "stderr.log" in mock_printc.call_args[0][0]

            # Clean up
            stdout_tee.close()
            stderr_tee.close()

    @patch("scitex.gen._tee.printc")
    @patch("os.makedirs")
    def test_tee_function_not_verbose(self, mock_makedirs, mock_printc):
        """Test tee function with verbose=False."""
        mock_sys = Mock()
        mock_sys.stdout = Mock()
        mock_sys.stderr = Mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            stdout_tee, stderr_tee = tee(mock_sys, sdir=tmpdir, verbose=False)

            # Check that printc was not called
            mock_printc.assert_not_called()

            # Clean up
            stdout_tee.close()
            stderr_tee.close()


class TestMainAlias:
    """Test the main function alias."""

    def test_main_is_tee(self):
        """Test that main is an alias for tee."""
        from scitex.gen import main, tee

        assert main is tee


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_tee.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-15 00:02:15 (ywatanabe)"
# # File: ./src/scitex/gen/_tee.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_tee.py"
# 
# """
# Functionality:
#     * Redirects and logs standard output and error streams
#     * Filters progress bar outputs from stderr logging
#     * Maintains original stdout/stderr functionality while logging
# Input:
#     * System stdout/stderr streams
#     * Output file paths for logging
# Output:
#     * Wrapped stdout/stderr objects with logging capability
#     * Log files containing stdout and stderr outputs
# Prerequisites:
#     * Python 3.6+
#     * scitex package for path handling and colored printing
# """
# 
# """Imports"""
# import os as _os
# import re
# import sys
# from typing import Any, List, TextIO
# 
# from ..str._clean_path import clean_path
# from ..path import split
# from ..str._printc import printc
# 
# """Functions & Classes"""
# # class Tee(object):
# #     """Duplicates output streams to both console and log files.
# 
# #     Example
# #     -------
# #     >>> import sys
# #     >>> sys.stdout = Tee(sys.stdout, "stdout.txt")
# #     >>> sys.stderr = Tee(sys.stderr, "stderr.txt")
# #     >>> print("Hello")  # Outputs to both console and stdout.txt
# #     >>> raise Exception("Error")  # Outputs to both console and stderr.txt
# #     """
# 
# #     def __init__(self, sys_stdout_or_stderr, spath):
# #         """
# #         Parameters
# #         ----------
# #         stream : TextIO
# #             Original output stream (sys.stdout or sys.stderr)
# #         log_path : str
# #             Path to log file
# #         """
# #         self._files = [sys_stdout_or_stderr, open(spath, "w")]
# #         self._is_stderr = sys_stdout_or_stderr is sys.stderr
# 
# #     def __getattr__(self, attr, *args):
# #         return self._wrap(attr, *args)
# 
# #     def _wrap(self, attr, *args):
# #         def g(*a, **kw):
# #             for f in self._files:
# #                 if self._is_stderr and f is not sys.stderr:
# #                     # Filter tqdm lines from log file
# #                     msg = a[0] if a else ""
# #                     if not re.match(r"^[\s]*[0-9]+%.*\[A*$", msg):
# #                         res = getattr(f, attr, *args)(*a, **kw)
# #                 else:
# #                     res = getattr(f, attr, *args)(*a, **kw)
# #             return res
# 
# #         return g
# 
# 
# class Tee:
#     def __init__(self, stream: TextIO, log_path: str) -> None:
#         self._stream = stream
#         try:
#             self._log_file = open(log_path, "w", buffering=1)  # Line buffering
#         except Exception as e:
#             printc(f"Failed to open log file {log_path}: {e}", c="red")
#             self._log_file = None
#         self._is_stderr = stream is sys.stderr
# 
#     def write(self, data: Any) -> None:
#         self._stream.write(data)
#         if self._log_file is not None:
#             if self._is_stderr:
#                 if isinstance(data, str) and not re.match(
#                     r"^[\s]*[0-9]+%.*\[A*$", data
#                 ):
#                     self._log_file.write(data)
#                     self._log_file.flush()  # Ensure immediate write
#             else:
#                 self._log_file.write(data)
#                 self._log_file.flush()  # Ensure immediate write
# 
#     def flush(self) -> None:
#         self._stream.flush()
#         if self._log_file is not None:
#             self._log_file.flush()
# 
#     def isatty(self) -> bool:
#         return self._stream.isatty()
# 
#     def fileno(self) -> int:
#         return self._stream.fileno()
# 
#     @property
#     def buffer(self):
#         return self._stream.buffer
# 
#     def close(self):
#         """Explicitly close the log file."""
#         if hasattr(self, "_log_file") and self._log_file is not None:
#             try:
#                 self._log_file.flush()
#                 self._log_file.close()
#                 self._log_file = None  # Prevent double-close
#             except Exception:
#                 pass
# 
#     def __del__(self):
#         # Only attempt cleanup if Python is not shutting down
#         # This prevents "Exception ignored" errors during interpreter shutdown
#         if hasattr(self, "_log_file") and self._log_file is not None:
#             try:
#                 # Check if the file object is still valid
#                 if hasattr(self._log_file, "closed") and not self._log_file.closed:
#                     self.close()
#             except Exception:
#                 # Silently ignore exceptions during cleanup
#                 pass
# 
# 
# # class Tee:
# #     def __init__(self, stream: TextIO, log_path: str) -> None:
# #         self._files: List[TextIO] = [stream, open(log_path, "w")]
# #         self._is_stderr: bool = stream is sys.stderr
# #         self._stream = stream
# 
# #     def write(self, data: Any) -> None:
# #         for file in self._files:
# #             if hasattr(file, 'write'):
# #                 if self._is_stderr and file is not sys.stderr:
# #                     if isinstance(data, str) and not re.match(r"^[\s]*[0-9]+%.*\[A*$", data):
# #                         file.write(data)
# #                 else:
# #                     file.write(data)
# 
# #     def flush(self) -> None:
# #         for file in self._files:
# #             if hasattr(file, 'flush'):
# #                 file.flush()
# 
# #     def isatty(self) -> bool:
# #         return getattr(self._stream, 'isatty', lambda: False)()
# 
# #     def fileno(self) -> int:
# #         """Delegate fileno to original stream for IPython compatibility"""
# #         return self._stream.fileno()
# 
# #     @property
# #     def buffer(self):
# #         return getattr(self._stream, 'buffer', self._stream)
# 
# 
# def tee(sys, sdir=None, verbose=True):
#     """Redirects stdout and stderr to both console and log files.
# 
#     Example
#     -------
#     >>> import sys
#     >>> sys.stdout, sys.stderr = tee(sys)
#     >>> print("abc")  # stdout
#     >>> print(1 / 0)  # stderr
# 
#     Parameters
#     ----------
#     sys_module : module
#         System module containing stdout and stderr
#     sdir : str, optional
#         Directory for log files
#     verbose : bool, default=True
#         Whether to print log file locations
# 
#     Returns
#     -------
#     tuple[Any, Any]
#         Wrapped stdout and stderr objects
#     """
#     import inspect
# 
#     ####################
#     ## Determine sdir
#     ## DO NOT MODIFY THIS
#     ####################
#     if sdir is None:
#         THIS_FILE = inspect.stack()[1].filename
#         if "ipython" in THIS_FILE:
#             THIS_FILE = f"/tmp/{_os.getenv('USER')}.py"
#         sdir = clean_path(_os.path.splitext(THIS_FILE)[0] + "_out")
# 
#     sdir = _os.path.join(sdir, "logs/")
#     _os.makedirs(sdir, exist_ok=True)
# 
#     spath_stdout = sdir + "stdout.log"
#     spath_stderr = sdir + "stderr.log"
#     sys_stdout = Tee(sys.stdout, spath_stdout)
#     sys_stderr = Tee(sys.stderr, spath_stderr)
# 
#     if verbose:
#         message = f"Standard output/error are being logged at:\n\t{spath_stdout}\n\t{spath_stderr}"
#         printc(message)
# 
#     return sys_stdout, sys_stderr
# 
# 
# main = tee
# 
# if __name__ == "__main__":
#     # # Argument Parser
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     # import argparse
#     # parser = argparse.ArgumentParser(description='')
#     # parser.add_argument('--var', '-v', type=int, default=1, help='')
#     # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
#     # args = parser.parse_args()
#     # Main
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
#     main(sys, CONFIG["SDIR"])
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_tee.py
# --------------------------------------------------------------------------------
