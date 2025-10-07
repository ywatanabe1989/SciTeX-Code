#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 04:07:38 (ywatanabe)"
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

from scitex import logging

logger = logging.getLogger(__name__)


async def click_download_for_chrome_pdf_viewer_async(
    page,
    output_path: Path | str,
) -> bool:
    """
    Click download button in Chrome PDF viewer and save the PDF file.

    This function locates the download button in Chrome's built-in PDF viewer
    (typically at top-right corner) and triggers the download, then saves the
    file to the specified path.

    Args:
        page: Playwright page object showing a PDF in Chrome's PDF viewer
        output_path: Path where the PDF file should be saved

    Returns:
        bool: True if download succeeded and file is valid (>1KB), False otherwise

    Example:
        >>> await click_download_for_chrome_pdf_viewer_async(page, "paper.pdf")
        True

    Note:
        - Expects Chrome PDF viewer to be already loaded on the page
        - Download button position is at approximately (95%, 3%) of viewport
        - Waits up to 120 seconds for download to start
        - Waits 10 seconds for download to complete after starting
    """
    from ..debugging import show_popup_and_capture_async

    try:
        output_path = Path(output_path)
        viewport = page.viewport_size
        viewport_width = viewport["width"]
        viewport_height = viewport["height"]

        # Download button is typically at top-right corner (95%, 3%)
        download_button_x = int(viewport_width * 0.95)
        download_button_y = int(viewport_height * 0.03)

        # Click download button and wait for download to start
        async with page.expect_download(timeout=120_000) as download_info:
            await page.mouse.click(download_button_x, download_button_y)

        download = await download_info.value

        # Monitor download progress
        await show_popup_and_capture_async(
            page, "Chrome PDF: Monitoring download progress..."
        )

        download_path = await download.path()
        await page.wait_for_timeout(10_000)  # Wait for download to complete

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


# EOF
