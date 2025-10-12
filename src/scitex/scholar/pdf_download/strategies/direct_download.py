#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 07:59:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdf_download/strategies/direct_download.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdf_download/strategies/direct_download.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Direct Download Strategy"""

from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar.browser import browser_logger

logger = logging.getLogger(__name__)


async def try_download_direct_async(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path,
    func_name: str = "try_download_direct_async",
) -> Optional[Path]:
    """Handle direct download that triggers ERR_ABORTED."""
    page = None
    try:
        page = await context.new_page()
        await browser_logger.info(
            page, f"{func_name}: Trying direct download from {pdf_url}"
        )

        download_occurred = False

        async def handle_download(download):
            nonlocal download_occurred
            await download.save_as(output_path)
            download_occurred = True

        page.on("download", handle_download)

        # Step 1: Navigate
        await browser_logger.info(
            page,
            f"{func_name}: Direct Download: Navigating to {pdf_url[:60]}...",
        )
        try:
            await page.goto(pdf_url, wait_until="load", timeout=60_000)
            await browser_logger.info(
                page,
                f"{func_name}: Direct Download: Loaded at {page.url[:80]}",
            )
        except Exception as ee:
            if "ERR_ABORTED" in str(ee):
                await browser_logger.info(
                    page,
                    f"{func_name}: Direct Download: ERR_ABORTED detected - likely direct download",
                )
                await browser_logger.info(
                    page,
                    f"{func_name}: Direct Download: ERR_ABORTED (download may have started)",
                )
                await page.wait_for_timeout(5_000)
            else:
                await browser_logger.info(
                    page,
                    f"{func_name}: Direct Download: ✗ Error: {str(ee)[:80]}",
                )
                await page.wait_for_timeout(2000)
                raise ee

        # Step 2: Check result
        if download_occurred and output_path.exists():
            size_MiB = output_path.stat().st_size / 1024 / 1024
            await browser_logger.info(
                page,
                f"{func_name}: Direct download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)",
            )
            await browser_logger.info(
                page,
                f"{func_name}: Direct Download: ✓ Downloaded {size_MiB:.2f} MB",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return output_path
        else:
            await browser_logger.debug(
                page,
                f"{func_name}: Direct download: No download event occurred",
            )
            await browser_logger.info(
                page,
                f"{func_name}: Direct Download: ✗ No download event occurred",
            )
            await page.wait_for_timeout(2000)

        await page.close()
        return None

    except Exception as ee:
        if page is not None:
            await browser_logger.warning(
                page, f"{func_name}: Direct download failed: {ee}"
            )
            try:
                await browser_logger.info(
                    page,
                    f"{func_name}: Direct Download: ✗ EXCEPTION: {str(ee)[:100]}",
                )
                await page.wait_for_timeout(2000)
            except Exception as popup_error:
                logger.debug(
                    f"{func_name}: Could not show error popup: {popup_error}"
                )
            finally:
                try:
                    await page.close()
                except Exception as close_error:
                    logger.debug(
                        f"{func_name}: Error closing page: {close_error}"
                    )
        return None

# EOF
