#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chrome PDF Viewer Download Strategy"""

from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.browser.stealth import HumanBehavior
from scitex.scholar.browser import (
    browser_logger,
    click_center_async,
    click_download_for_chrome_pdf_viewer_async,
    detect_chrome_pdf_viewer_async,
    show_grid_async,
)

logger = logging.getLogger(__name__)


async def try_download_chrome_pdf_viewer_async(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path,
    downloader_name: str = "ScholarPDFDownloader",
) -> Optional[Path]:
    """Download PDF from Chrome PDF viewer with human-like behavior."""
    page = None
    try:
        page = await context.new_page()

        # Step 1: Navigate and wait for networkidle
        await browser_logger.debug(
            page, f"{downloader_name}: Chrome PDF: Navigating to URL..."
        )
        await browser_logger.info(
            page,
            f"{downloader_name}: Chrome PDF: Navigating to {pdf_url[:60]}...",
        )
        await HumanBehavior.random_delay_async(
            1000, 2000, "before navigation"
        )
        # Navigate and wait for initial networkidle
        await page.goto(pdf_url, wait_until="networkidle", timeout=60_000)
        await browser_logger.debug(
            page, f"{downloader_name}: Chrome PDF: Loaded page at {page.url}"
        )
        await browser_logger.info(
            page,
            f"{downloader_name}: Chrome PDF: Initial load at {page.url[:80]}",
        )

        # Step 2: Wait for PDF rendering and any post-load network activity
        await browser_logger.debug(
            page, f"{downloader_name}: Chrome PDF: Waiting for PDF rendering..."
        )
        await browser_logger.info(
            page,
            f"{downloader_name}: Chrome PDF: Waiting for PDF rendering (networkidle)...",
        )
        try:
            # Wait for network to be fully idle (catches post-load PDF requests)
            await page.wait_for_load_state("networkidle", timeout=30_000)
            await browser_logger.success(
                page,
                f"{downloader_name}: Chrome PDF: Network idle, PDF should be rendered",
            )
            await browser_logger.success(
                page,
                f"{downloader_name}: Chrome PDF: ✓ Network idle, PDF rendered",
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
            await browser_logger.debug(
                page, f"{downloader_name}: Network idle timeout (non-fatal): {e}"
            )
            await browser_logger.info(
                page,
                f"{downloader_name}: Chrome PDF: Network still active, continuing anyway",
            )
            await page.wait_for_timeout(2000)

        # Step 2.5: Extra wait for PDF viewer iframe/embed to fully load
        # Chrome PDF viewer can take additional time to initialize
        await browser_logger.info(
            page,
            f"{downloader_name}: Chrome PDF: Waiting extra for PDF viewer to initialize (10s)...",
        )
        await page.wait_for_timeout(10000)  # Additional 10 seconds

        # Step 3: Detect PDF viewer
        await browser_logger.debug(
            page, f"{downloader_name}: Chrome PDF: Detecting PDF viewer..."
        )
        await browser_logger.info(
            page, f"{downloader_name}: Chrome PDF: Detecting PDF viewer..."
        )
        if not await detect_chrome_pdf_viewer_async(page):
            await browser_logger.warning(
                page,
                f"{downloader_name}: Chrome PDF: No PDF viewer detected at {page.url}",
            )
            await browser_logger.warning(
                page, f"{downloader_name}: Chrome PDF: ✗ No PDF viewer detected!"
            )
            await page.wait_for_timeout(2000)  # Show message for 2s
            await page.close()
            return None

        # Step 4: PDF viewer detected!
        await browser_logger.success(
            page,
            f"{downloader_name}: Chrome PDF: PDF viewer detected, attempting download...",
        )
        await browser_logger.success(
            page, f"{downloader_name}: Chrome PDF: ✓ PDF viewer detected!"
        )
        await HumanBehavior.random_delay_async(1000, 2000, "viewing PDF")

        # Step 5: Show grid and click center
        await browser_logger.info(
            page, f"{downloader_name}: Chrome PDF: Showing grid overlay..."
        )
        await show_grid_async(page)
        await browser_logger.info(
            page, f"{downloader_name}: Chrome PDF: Clicking center of PDF..."
        )
        await click_center_async(page)

        # Step 6: Click download button
        await browser_logger.debug(
            page, f"{downloader_name}: Chrome PDF: Clicking download button..."
        )
        await browser_logger.info(
            page, f"{downloader_name}: Chrome PDF: Clicking download button..."
        )
        is_downloaded = await click_download_for_chrome_pdf_viewer_async(
            page, output_path
        )

        # Step 7: Wait for download to complete (use networkidle for patience)
        await browser_logger.debug(
            page,
            f"{downloader_name}: Chrome PDF: Waiting for download to complete...",
        )
        await browser_logger.info(
            page,
            f"{downloader_name}: Chrome PDF: Waiting for download (networkidle up to 30s)...",
        )
        try:
            # Wait for any download-related network activity to complete
            await page.wait_for_load_state("networkidle", timeout=30_000)
            await browser_logger.debug(
                page,
                f"{downloader_name}: Chrome PDF: Network idle after download click",
            )
            await browser_logger.success(
                page,
                f"{downloader_name}: Chrome PDF: ✓ Download network activity complete",
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
            await browser_logger.debug(
                page,
                f"{downloader_name}: Download networkidle timeout (non-fatal): {e}",
            )
            await browser_logger.info(
                page,
                f"{downloader_name}: Chrome PDF: Network timeout, checking file...",
            )
            await page.wait_for_timeout(2000)

        # Step 8: Check if file was actually downloaded
        if is_downloaded and output_path.exists():
            file_size = output_path.stat().st_size
            if file_size > 1000:  # At least 1KB
                await browser_logger.success(
                    page,
                    f"{downloader_name}: Chrome PDF: Downloaded {file_size/1024:.1f}KB from {pdf_url}",
                )
                await browser_logger.success(
                    page,
                    f"{downloader_name}: Chrome PDF: ✓ SUCCESS! Downloaded {file_size/1024:.1f}KB",
                )
                await page.wait_for_timeout(2000)  # Show success for 2s
                await page.close()
                return output_path
            else:
                await browser_logger.warning(
                    page,
                    f"{downloader_name}: Chrome PDF: File too small ({file_size} bytes), likely failed",
                )
                await browser_logger.warning(
                    page,
                    f"{downloader_name}: Chrome PDF: ✗ File too small ({file_size} bytes)",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return None

        await browser_logger.info(
            page, f"{downloader_name}: Chrome PDF: ✗ Download did not complete"
        )
        await page.wait_for_timeout(2000)
        await page.close()

        if is_downloaded:
            await browser_logger.success(
                page,
                f"{downloader_name}: Downloaded via Chrome PDF Viewer: from {pdf_url} to {output_path}",
            )
            return output_path
        else:
            await browser_logger.debug(
                page,
                f"{downloader_name}: Chrome PDF Viewer method didn't work for: {pdf_url}",
            )
            return None

    except Exception as ee:
        if page:
            await browser_logger.fail(
                page,
                f"{downloader_name}: Chrome PDF Viewer failed to download from {pdf_url} to {output_path}: {str(ee)}",
            )
            try:
                await browser_logger.info(
                    page,
                    f"{downloader_name}: Chrome PDF: ✗ EXCEPTION: {str(ee)[:100]}",
                )
                await page.wait_for_timeout(3000)  # Show error for 3s
            except Exception as popup_error:
                logger.debug(
                    f"{downloader_name}: Could not show error popup: {popup_error}"
                )
            finally:
                try:
                    await page.close()
                except Exception as close_error:
                    logger.debug(
                        f"{downloader_name}: Error closing page: {close_error}"
                    )
        return None


# EOF
