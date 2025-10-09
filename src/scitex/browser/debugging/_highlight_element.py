#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 03:52:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/debugging/highlight_element.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/debugging/highlight_element.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Functionalities:
  - Highlights a Playwright element with red overlay for visual debugging
  - Scrolls element into view and displays a temporary visual indicator
  - Demonstrates element highlighting when run standalone

Dependencies:
  - packages:
    - playwright

IO:
  - input-files:
    - None
  - output-files:
    - None
"""

"""Imports"""
import argparse

from playwright.async_api import Locator

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Functions & Classes"""
async def highlight_element_async(element: Locator, duration_ms: int = 1_000, func_name: str = "highlight_element_async"):
    """Highlight element with red overlay rectangle.

    Args:
        element: Locator to highlight
        duration_ms: Duration to display highlight in milliseconds
        func_name: Name of calling function for logging context
    """
    await element.evaluate(
        """(element, duration) => {
            // Get element position and size
            const rect = element.getBoundingClientRect();

            // Create overlay div
            const overlay = document.createElement('div');
            overlay.id = 'highlight-overlay-' + Date.now();
            overlay.style.cssText = `
                position: fixed;
                top: ${rect.top}px;
                left: ${rect.left}px;
                width: ${rect.width}px;
                height: ${rect.height}px;
                border: 5px solid red;
                background-color: rgba(255, 0, 0, 0.2);
                pointer-events: none;
                z-index: 999999;
                box-shadow: 0 0 20px red;
            `;

            document.body.appendChild(overlay);

            // Scroll element into view
            element.scrollIntoView({behavior: 'smooth', block: 'center'});

            // Remove overlay after duration
            setTimeout(() => {
                if (overlay && overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, duration);
        }""",
        duration_ms,
    )
    await element.page.wait_for_timeout(duration_ms)


def main(args):
    logger.info("Element highlighting utility - use highlight_element_async() in your code")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    parser = argparse.ArgumentParser(description="Element highlighting utility for debugging")
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
