#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 10:55:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/pdf/click_download_for_chrome_pdf_viewer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path
from typing import Optional

from scitex import logging

logger = logging.getLogger(__name__)


async def click_download_for_chrome_pdf_viewer(
    page, spath_pdf
) -> Optional[Path]:
    """Download PDF from Chrome PDF viewer with dynamic waiting."""
    from scitex.browser.debugging import show_popup_and_capture

    try:
        spath_pdf = Path(spath_pdf)
        viewport = page.viewport_size
        width = viewport["width"]
        height = viewport["height"]

        x_download = int(width * 95 / 100)
        y_download = int(height * 3 / 100)

        async with page.expect_download(timeout=120_000) as download_info:
            await page.mouse.click(x_download, y_download)

        download = await download_info.value

        # Monitor download progress
        await show_popup_and_capture(page, "Monitoring download process...")
        download_path = await download.path()
        await page.wait_for_timeout(10_000)
        if download_path:
            # Wait for download to finish
            await download.save_as(spath_pdf)

            if spath_pdf.exists() and spath_pdf.stat().st_size > 1024:
                file_size_MB = spath_pdf.stat().st_size / 1e6
                logger.success(
                    f"Downloaded: {spath_pdf} ({file_size_MB:.1f} MB)"
                )
                return True

    except Exception as ee:
        logger.error(f"Chrome page download failed: {ee}")
        return False



# Backward compatibility alias
click_download_for_chrome_pdf_viewer_async = click_download_for_chrome_pdf_viewer


# EOF
