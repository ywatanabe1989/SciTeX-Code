#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 22:17:03 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/_Tee.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/logging/_Tee.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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
from typing import Any, TextIO

from ..str._clean_path import clean_path
from ..str._printc import printc

"""Functions & Classes"""
def _get_logger():
    """Get logger lazily to avoid circular import during module initialization."""
    from scitex import logging

    return logging.getLogger(__name__)


class Tee:
    def __init__(self, stream: TextIO, log_path: str, verbose=True) -> None:
        self.verbose = verbose
        self._stream = stream
        self._log_path = log_path
        try:
            self._log_file = open(log_path, "w", buffering=1)  # Line buffering
            if verbose:
                # Show where logs are being saved using scitex logging
                logger = _get_logger()
                stream_name = "stderr" if stream is sys.stderr else "stdout"
                logger.info(f"Tee [{stream_name}]: {log_path}")
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
                if self.verbose:
                    # Use lazy logger to avoid circular import
                    logger = _get_logger()
                    logger.info(f"Tee: Closed log file: {self._log_path}")
                self._log_file = None  # Prevent double-close
            except Exception:
                pass

    def __del__(self):
        # Only attempt cleanup if Python is not shutting down
        # This prevents "Exception ignored" errors during interpreter shutdown
        if hasattr(self, "_log_file") and self._log_file is not None:
            try:
                # Check if the file object is still valid
                if (
                    hasattr(self._log_file, "closed")
                    and not self._log_file.closed
                ):
                    self.close()
            except Exception:
                # Silently ignore exceptions during cleanup
                pass


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
        logger = _get_logger()
        logger.info(message)
        # printc(message)

    return sys_stdout, sys_stderr


if __name__ == "__main__":
    # Argument Parser
    import matplotlib.pyplot as plt

    import scitex

    main = tee

    # import argparse
    # parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--var', '-v', type=int, default=1, help='')
    # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
    # args = parser.parse_args()
    # Main
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
        sys, plt, verbose=False
    )
    main(sys, CONFIG["SDIR"])
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
