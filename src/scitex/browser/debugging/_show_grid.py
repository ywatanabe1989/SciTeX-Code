#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 00:27:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/debugging/_show_grid.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/debugging/_show_grid.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Functionalities:
  - Displays a coordinate grid overlay on a webpage for debugging layout
  - Shows major grid lines every 100px and minor lines every 20px
  - Demonstrates grid overlay when run standalone

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

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Functions & Classes"""
async def show_grid_async(page, func_name: str = "show_grid_async"):
    from ._browser_logger import browser_logger

    await browser_logger.debug(page, f"{func_name}: Showing Grid...")
    await page.evaluate(
        """() => {
        // Remove existing grid if present
        const existingGrid = document.getElementById('scitex-debug-grid');
        if (existingGrid) {
            existingGrid.remove();
        }

        const canvas = document.createElement('canvas');
        canvas.id = 'scitex-debug-grid';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '9998';  // Below popups (9999) but above content
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const ctx = canvas.getContext('2d');
        ctx.font = '12px Arial';

        // Vertical lines
        for (let xx = 0; xx < canvas.width; xx += 20) {
            ctx.strokeStyle = xx % 100 === 0 ? 'rgba(255, 0, 0, 0.8)' : 'rgba(255, 0, 0, 0.2)';
            ctx.lineWidth = xx % 100 === 0 ? 2 : 1;
            ctx.beginPath();
            ctx.moveTo(xx, 0);
            ctx.lineTo(xx, canvas.height);
            ctx.stroke();
            if (xx % 100 === 0) {
                ctx.fillStyle = 'rgba(255, 0, 0, 0.9)';
                ctx.fillText(xx, xx + 5, 15);
            }
        }

        // Horizontal lines
        for (let yy = 0; yy < canvas.height; yy += 20) {
            ctx.strokeStyle = yy % 100 === 0 ? 'rgba(255, 0, 0, 0.8)' : 'rgba(255, 0, 0, 0.2)';
            ctx.lineWidth = yy % 100 === 0 ? 2 : 1;
            ctx.beginPath();
            ctx.moveTo(0, yy);
            ctx.lineTo(canvas.width, yy);
            ctx.stroke();
            if (yy % 100 === 0) {
                ctx.fillStyle = 'rgba(255, 0, 0, 0.9)';
                ctx.fillText(yy, 5, yy + 15);
            }
        }

        document.body.appendChild(canvas);
    }"""
    )


def main(args):
    logger.debug("Grid overlay utility - use show_grid_async() in your code")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    parser = argparse.ArgumentParser(
        description="Grid overlay utility for debugging"
    )
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
