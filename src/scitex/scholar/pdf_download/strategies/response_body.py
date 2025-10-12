#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 08:02:32 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdf_download/strategies/response_body.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdf_download/strategies/response_body.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Response Body Download Strategy"""

from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar.browser import browser_logger

logger = logging.getLogger(__name__)


async def try_download_response_body_async(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path,
    func_name: str = "try_download_response_body_async",
) -> Optional[Path]:
    """Download PDF from HTTP response body."""
    # Check if manual mode is active - skip immediately
    if (
        hasattr(context, "_scitex_is_manual_mode")
        and context._scitex_is_manual_mode
    ):
        logger.info(f"{func_name}: Skipping because manual mode is active...")
        return None

    page = None
    try:
        page = await context.new_page()
        await browser_logger.info(
            page,
            f"{func_name}: Trying to download {pdf_url} from response body",
        )

        # Step 1: Navigate
        await browser_logger.info(
            page,
            f"{func_name}: Navigating to {pdf_url[:60]}...",
        )

        download_path = None
        download_handler_active = True

        async def handle_download(download):
            nonlocal download_path
            # Only handle downloads if NOT in manual mode
            if (
                hasattr(context, "_scitex_is_manual_mode")
                and context._scitex_is_manual_mode
            ):
                logger.info(
                    f"{func_name}: Ignoring download (manual mode active)"
                )
                return

            if download_handler_active:
                await download.save_as(output_path)
                download_path = output_path

        page.on("download", handle_download)

        response = await page.goto(pdf_url, wait_until="load", timeout=60_000)

        await browser_logger.info(
            page,
            f"{func_name}: Loaded, waiting for auto-download (60s)...",
        )

        # Wait for download, but check for manual mode activation every second
        for i in range(60):
            # Check if manual mode was activated - ABORT IMMEDIATELY
            if (
                hasattr(context, "_scitex_is_manual_mode")
                and context._scitex_is_manual_mode
            ):
                logger.info(f"{func_name}: Manual mode activated, aborting")
                download_handler_active = False  # Disable handler
                page.remove_listener(
                    "download", handle_download
                )  # Remove listener
                await page.close()
                return None

            await page.wait_for_timeout(1000)  # Wait 1 second

            # Check if download already happened
            if download_path and download_path.exists():
                break

        # Check if auto-download occurred
        if download_path and download_path.exists():
            size_MiB = download_path.stat().st_size / 1024 / 1024
            await browser_logger.info(
                page,
                f"{func_name}: Auto-download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)",
            )
            await browser_logger.info(
                page,
                f"{func_name}: ✓ Auto-download {size_MiB:.2f} MB",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return output_path

        # Step 2: Check response
        await browser_logger.info(
            page,
            f"{func_name}: Checking response (status: {response.status})...",
        )

        if not response.ok:
            await browser_logger.fail(
                page,
                f"{func_name}: Page not reached: {pdf_url} (reason: {response.status})",
            )
            await browser_logger.fail(
                page,
                f"{func_name}: ✗ HTTP {response.status}",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return None

        # Step 3: Extract from response body
        await browser_logger.info(
            page,
            f"{func_name}: Extracting PDF from response body...",
        )
        content = await response.body()
        content_type = response.headers.get("content-type", "")

        is_pdf = content[:4] == b"%PDF" or "application/pdf" in content_type

        is_html = (
            content[:15].lower().startswith(b"<!doctype html")
            or content[:6].lower().startswith(b"<html")
            or "text/html" in content_type
        )

        if is_pdf and not is_html and len(content) > 1024:
            with open(output_path, "wb") as file_:
                file_.write(content)
            size_MiB = len(content) / 1024 / 1024
            await browser_logger.info(
                page,
                f"{func_name}: Response body download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)",
            )
            await browser_logger.info(
                page,
                f"{func_name}: ✓ Extracted {size_MiB:.2f} MB",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return output_path

        await browser_logger.warning(
            page, f"{func_name}: Failed download from response body"
        )
        await browser_logger.warning(
            page,
            f"{func_name}: ✗ Not PDF (type: {content_type}, size: {len(content)})",
        )
        await page.wait_for_timeout(2000)
        await page.close()
        return None

    except Exception as ee:
        if page is not None:
            await browser_logger.warning(
                page,
                f"{func_name}: Failed download from response body: {ee}",
            )
            try:
                await browser_logger.info(
                    page,
                    f"{func_name}: ✗ EXCEPTION: {str(ee)[:100]}",
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
