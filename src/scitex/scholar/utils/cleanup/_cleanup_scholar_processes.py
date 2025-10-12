#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-07 22:49:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/_cleanup.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/utils/_cleanup.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Process cleanup utilities for Scholar."""

from scitex import logging

logger = logging.getLogger(__name__)


def cleanup_scholar_processes(signal_num=None, frame=None):
    """Cleanup function to stop all Scholar browser processes gracefully."""
    import sys

    if signal_num:
        logger.info(
            f"Received signal {signal_num}, cleaning up Scholar processes..."
        )

    try:
        import subprocess

        # Kill Chrome/Chromium processes (suppress stderr)
        subprocess.run(
            ["pkill", "-f", "chrome"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False,
        )
        subprocess.run(
            ["pkill", "-f", "chromium"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False,
        )

        # Kill Xvfb displays
        subprocess.run(
            ["pkill", "Xvfb"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False,
        )
    except Exception as e:
        logger.debug(f"Cleanup error: {e}")

    # Exit after cleanup if called from signal handler
    if signal_num:
        sys.exit(128 + signal_num)


def cleanup_scholar_processes(signal_num=None, frame=None):
    """Cleanup function to stop all Scholar browser processes gracefully."""
    if signal_num:
        logger.info(
            f"Received signal {signal_num}, cleaning up Scholar processes..."
        )

    try:
        import subprocess

        # Kill Chrome/Chromium processes (suppress stderr)
        subprocess.run(
            ["pkill", "-f", "chrome"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False,
        )
        subprocess.run(
            ["pkill", "-f", "chromium"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False,
        )

        # Kill Xvfb displays
        subprocess.run(
            ["pkill", "Xvfb"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False,
        )
    except Exception as e:
        logger.debug(f"Cleanup error: {e}")

# EOF
