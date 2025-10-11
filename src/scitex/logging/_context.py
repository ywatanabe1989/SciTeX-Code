#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 22:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/_context.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/logging/_context.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Context manager for temporary logging to specific files.

Provides clean API for adding/removing file handlers during execution.
"""

import logging as _logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Union

from ._formatters import SciTeXFileFormatter


@contextmanager
def log_to_file(
    file_path: Union[str, Path],
    level: int = _logging.DEBUG,
    mode: str = 'w',
    formatter: Optional[_logging.Formatter] = None,
):
    """Context manager to temporarily log all output to a specific file.

    Usage:
        from scitex import logging
        logger = logging.getLogger(__name__)

        with logging.log_to_file("/path/to/log.txt"):
            logger.info("This goes to both console and /path/to/log.txt")
            logger.success("This too!")

    Args:
        file_path: Path to log file
        level: Logging level for this handler (default: DEBUG)
        mode: File mode ('w' for overwrite, 'a' for append)
        formatter: Custom formatter (default: SciTeXFileFormatter)

    Yields:
        The file handler (can be ignored)
    """
    # Ensure directory exists
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create handler
    handler = _logging.FileHandler(str(file_path), mode=mode)
    handler.setLevel(level)

    # Set formatter
    if formatter is None:
        formatter = SciTeXFileFormatter()
    handler.setFormatter(formatter)

    # Add to root logger
    root_logger = _logging.getLogger()
    root_logger.addHandler(handler)

    # Log where output is going (lazy import to avoid circular dependency)
    def _log_info():
        try:
            from scitex import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Logging to: {file_path}")
        except:
            pass  # Silently fail if logging not ready

    _log_info()

    try:
        yield handler
    finally:
        # Clean up handler
        root_logger.removeHandler(handler)
        handler.close()

        # Log completion (lazy import)
        def _log_saved():
            try:
                from scitex import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Log saved: {file_path}")
            except:
                pass

        _log_saved()


__all__ = ['log_to_file']

# EOF
