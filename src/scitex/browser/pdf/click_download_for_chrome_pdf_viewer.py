#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 03:24:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/pdf/click_download_for_chrome_pdf_viewer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/pdf/click_download_for_chrome_pdf_viewer.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path

__FILE__ = __file__

"""
Functionalities:
  - Clicks download button in Chrome PDF viewer and saves PDF file
  - Locates download button at top-right corner of PDF viewer
  - Verifies successful download with file size check
  - Demonstrates PDF download when run standalone

Dependencies:
  - packages:
    - playwright

IO:
  - input-files:
    - None
  - output-files:
    - User-specified PDF output path
"""

"""Imports"""
import argparse

from scitex import logging

logger = logging.getLogger(__name__)
from ..debugging import browser_logger

"""Functions & Classes"""
async def click_download_for_chrome_pdf_viewer_async(
    page,
    output_path: Path | str,
    verbose: bool = False,
    func_name="click_download_for_chrome_pdf_viewer_async",
) -> bool:
    """
    Click download button in Chrome PDF viewer and save the PDF file.

    This function locates the download button in Chrome's built-in PDF viewer
    (typically at top-right corner) and triggers the download, then saves the
    file to the specified path.

    Args:
        page: Playwright page object showing a PDF in Chrome's PDF viewer
        output_path: Path where the PDF file should be saved
        verbose: Enable visual feedback via popup system (default False)

    Returns:
        bool: True if download succeeded and file is valid (>1KB), False otherwise

    Example:
        >>> await click_download_for_chrome_pdf_viewer_async(
        ...     page, "paper.pdf", verbose=True
        ... )
        True

    Note:
        - Expects Chrome PDF viewer to be already loaded on the page
        - Download button position is at approximately (95%, 3%) of viewport
        - Waits up to 120 seconds for download to start
        - Waits 10 seconds for download to complete after starting
    """
    try:
        output_path = Path(output_path)

        # Ensure .pdf extension
        if not str(output_path).endswith(".pdf"):
            output_path = Path(str(output_path) + ".pdf")

        viewport = page.viewport_size
        viewport_width = viewport["width"]
        viewport_height = viewport["height"]

        # Download button is typically at top-right corner (95%, 3%)
        download_button_x = int(viewport_width * 0.95)
        download_button_y = int(viewport_height * 0.03)

        if verbose:
            await browser_logger.debug(
                page,
                f"{func_name}: Clicking PDF download button...",
            )

        # Click download button and wait for download to start
        async with page.expect_download(timeout=120_000) as download_info:
            await page.mouse.click(download_button_x, download_button_y)

        download = await download_info.value

        # Monitor download progress with real-time updates
        if verbose:
            await browser_logger.info(
                page,
                f"{func_name}: Download started, monitoring progress...",
            )

        # Wait for download to complete and get final path
        download_path = await download.path()

        # Show download completion
        if download_path:
            temp_size = Path(download_path).stat().st_size if Path(download_path).exists() else 0
            size_mb = temp_size / (1024 * 1024)
            if verbose:
                await browser_logger.success(
                    page,
                    f"{func_name}: Download complete! Size: {size_mb:.2f} MB",
                )

        await page.wait_for_timeout(2_000)  # Brief pause to show completion message

        if download_path:
            # Save download to specified path
            await download.save_as(output_path)

            # Verify download succeeded
            if output_path.exists() and output_path.stat().st_size > 1024:
                file_size_mb = output_path.stat().st_size / 1e6
                logger.success(
                    f"Downloaded PDF: {output_path} ({file_size_mb:.1f} MB)"
                )
                return True

        return False

    except Exception as e:
        logger.error(f"Chrome PDF viewer download failed: {e}")
        return False


def main(args):
    logger.debug(
        "Chrome PDF download utility - use click_download_for_chrome_pdf_viewer_async() in your code"
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    parser = argparse.ArgumentParser(
        description="Chrome PDF viewer download utility"
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
