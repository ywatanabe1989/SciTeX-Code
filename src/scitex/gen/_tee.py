#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-15 00:02:15 (ywatanabe)"
# File: ./src/scitex/gen/_tee.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_tee.py"

"""
Functionality:
    * Redirects and logs standard output and error streams
    * Filters progress bar outputs from stderr logging
    * Maintains original stdout/stderr functionality while logging
Input:
    * System stdout/stderr streams
    * Output file paths for logging
Output:
    * Wrapped stdout/stderr objects with logging capability
    * Log files containing stdout and stderr outputs
Prerequisites:
    * Python 3.6+
    * scitex package for path handling and colored printing
"""

"""Imports"""
import os as _os
import re
import sys
from typing import Any, List, TextIO

from ..str._clean_path import clean_path
from ..path import split
from ..str._printc import printc

"""Functions & Classes"""
# class Tee(object):
#     """Duplicates output streams to both console and log files.

#     Example
#     -------
#     >>> import sys
#     >>> sys.stdout = Tee(sys.stdout, "stdout.txt")
#     >>> sys.stderr = Tee(sys.stderr, "stderr.txt")
#     >>> print("Hello")  # Outputs to both console and stdout.txt
#     >>> raise Exception("Error")  # Outputs to both console and stderr.txt
#     """

#     def __init__(self, sys_stdout_or_stderr, spath):
#         """
#         Parameters
#         ----------
#         stream : TextIO
#             Original output stream (sys.stdout or sys.stderr)
#         log_path : str
#             Path to log file
#         """
#         self._files = [sys_stdout_or_stderr, open(spath, "w")]
#         self._is_stderr = sys_stdout_or_stderr is sys.stderr

#     def __getattr__(self, attr, *args):
#         return self._wrap(attr, *args)

#     def _wrap(self, attr, *args):
#         def g(*a, **kw):
#             for f in self._files:
#                 if self._is_stderr and f is not sys.stderr:
#                     # Filter tqdm lines from log file
#                     msg = a[0] if a else ""
#                     if not re.match(r"^[\s]*[0-9]+%.*\[A*$", msg):
#                         res = getattr(f, attr, *args)(*a, **kw)
#                 else:
#                     res = getattr(f, attr, *args)(*a, **kw)
#             return res

#         return g


class Tee:
    def __init__(self, stream: TextIO, log_path: str) -> None:
        self._stream = stream
        try:
            self._log_file = open(log_path, "w", buffering=1)  # Line buffering
        except Exception as e:
            printc(f"Failed to open log file {log_path}: {e}", c="red")
            self._log_file = None
        self._is_stderr = stream is sys.stderr

    def write(self, data: Any) -> None:
        self._stream.write(data)
        if self._log_file is not None:
            if self._is_stderr:
                if isinstance(data, str) and not re.match(
                    r"^[\s]*[0-9]+%.*\[A*$", data
                ):
                    self._log_file.write(data)
                    self._log_file.flush()  # Ensure immediate write
            else:
                self._log_file.write(data)
                self._log_file.flush()  # Ensure immediate write

    def flush(self) -> None:
        self._stream.flush()
        if self._log_file is not None:
            self._log_file.flush()

    def isatty(self) -> bool:
        return self._stream.isatty()

    def fileno(self) -> int:
        return self._stream.fileno()

    @property
    def buffer(self):
        return self._stream.buffer

    def close(self):
        """Explicitly close the log file."""
        if hasattr(self, "_log_file") and self._log_file is not None:
            try:
                self._log_file.flush()
                self._log_file.close()
                self._log_file = None  # Prevent double-close
            except Exception:
                pass

    def __del__(self):
        # Only attempt cleanup if Python is not shutting down
        # This prevents "Exception ignored" errors during interpreter shutdown
        if hasattr(self, "_log_file") and self._log_file is not None:
            try:
                # Check if the file object is still valid
                if hasattr(self._log_file, "closed") and not self._log_file.closed:
                    self.close()
            except Exception:
                # Silently ignore exceptions during cleanup
                pass


# class Tee:
#     def __init__(self, stream: TextIO, log_path: str) -> None:
#         self._files: List[TextIO] = [stream, open(log_path, "w")]
#         self._is_stderr: bool = stream is sys.stderr
#         self._stream = stream

#     def write(self, data: Any) -> None:
#         for file in self._files:
#             if hasattr(file, 'write'):
#                 if self._is_stderr and file is not sys.stderr:
#                     if isinstance(data, str) and not re.match(r"^[\s]*[0-9]+%.*\[A*$", data):
#                         file.write(data)
#                 else:
#                     file.write(data)

#     def flush(self) -> None:
#         for file in self._files:
#             if hasattr(file, 'flush'):
#                 file.flush()

#     def isatty(self) -> bool:
#         return getattr(self._stream, 'isatty', lambda: False)()

#     def fileno(self) -> int:
#         """Delegate fileno to original stream for IPython compatibility"""
#         return self._stream.fileno()

#     @property
#     def buffer(self):
#         return getattr(self._stream, 'buffer', self._stream)


def tee(sys, sdir=None, verbose=True):
    """Redirects stdout and stderr to both console and log files.

    Example
    -------
    >>> import sys
    >>> sys.stdout, sys.stderr = tee(sys)
    >>> print("abc")  # stdout
    >>> print(1 / 0)  # stderr

    Parameters
    ----------
    sys_module : module
        System module containing stdout and stderr
    sdir : str, optional
        Directory for log files
    verbose : bool, default=True
        Whether to print log file locations

    Returns
    -------
    tuple[Any, Any]
        Wrapped stdout and stderr objects
    """
    import inspect

    ####################
    ## Determine sdir
    ## DO NOT MODIFY THIS
    ####################
    if sdir is None:
        THIS_FILE = inspect.stack()[1].filename
        if "ipython" in THIS_FILE:
            THIS_FILE = f"/tmp/{_os.getenv('USER')}.py"
        sdir = clean_path(_os.path.splitext(THIS_FILE)[0] + "_out")

    sdir = _os.path.join(sdir, "logs/")
    _os.makedirs(sdir, exist_ok=True)

    spath_stdout = sdir + "stdout.log"
    spath_stderr = sdir + "stderr.log"
    sys_stdout = Tee(sys.stdout, spath_stdout)
    sys_stderr = Tee(sys.stderr, spath_stderr)

    if verbose:
        message = f"Standard output/error are being logged at:\n\t{spath_stdout}\n\t{spath_stderr}"
        printc(message)

    return sys_stdout, sys_stderr


main = tee

if __name__ == "__main__":
    # # Argument Parser
    import matplotlib.pyplot as plt
    import scitex

    # import argparse
    # parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--var', '-v', type=int, default=1, help='')
    # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
    # args = parser.parse_args()
    # Main
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, verbose=False)
    main(sys, CONFIG["SDIR"])
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
