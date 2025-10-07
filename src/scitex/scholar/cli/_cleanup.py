#!/usr/bin/env python3
"""Process cleanup utilities for Scholar."""

from scitex import logging

logger = logging.getLogger(__name__)


def cleanup_scholar_processes(signal_num=None, frame=None):
    """Cleanup function to stop all Scholar browser processes gracefully."""
    if signal_num:
        logger.info(f"Received signal {signal_num}, cleaning up Scholar processes...")

    try:
        import subprocess
        # Kill Chrome/Chromium processes (suppress stderr)
        subprocess.run(
            ["pkill", "-f", "chrome"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False
        )
        subprocess.run(
            ["pkill", "-f", "chromium"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False
        )

        # Kill Xvfb displays
        subprocess.run(
            ["pkill", "Xvfb"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            check=False
        )
    except Exception as e:
        logger.debug(f"Cleanup error: {e}")
