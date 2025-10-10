#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manual Download Fallback Strategy"""

from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.browser import browser_logger
from scitex.scholar.download.strategies.manual_download_utils import (
    complete_manual_download_workflow_async,
)

logger = logging.getLogger(__name__)


async def try_download_manual_async(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path,
    downloader_name: str = "ScholarPDFDownloader",
    config: ScholarConfig = None,
) -> Optional[Path]:
    """Manual download fallback with monitoring and syncing.

    This method is used as a last resort when all automatic methods fail.
    It shows a manual download button, monitors the temp downloads directory,
    and syncs the downloaded file to the final destination with proper naming.
    """
    page = None
    try:
        page = await context.new_page()
        await browser_logger.info(
            page, f"{downloader_name}: Starting manual download fallback for {pdf_url}"
        )

        # Navigate to the PDF URL
        await browser_logger.info(
            page,
            f"{downloader_name}: Manual Download: Navigating to {pdf_url[:60]}...",
        )
        await page.goto(pdf_url, wait_until="load", timeout=60_000)
        await browser_logger.info(
            page,
            f"{downloader_name}: Manual Download: Loaded at {page.url[:80]}",
        )

        # Get temp and final directories from config
        if config is None:
            config = ScholarConfig()

        temp_downloads_dir = config.get_library_downloads_dir()
        final_pdfs_dir = config.get_library_pdfs_dir()

        # Extract DOI from URL if possible
        doi = None
        if "doi.org/" in pdf_url:
            # Extract DOI from doi.org URL
            doi_match = pdf_url.split("doi.org/")[-1].split("?")[0].split("#")[0]
            doi = doi_match if doi_match else None

        # Run complete manual download workflow
        final_path = await complete_manual_download_workflow_async(
            page=page,
            temp_downloads_dir=temp_downloads_dir,
            final_pdfs_dir=final_pdfs_dir,
            doi=doi,
            url=pdf_url,
            content_type="main",
            sequence_index=None,
            button_timeout_sec=300,  # 5 minutes to click button
            download_timeout_sec=120,  # 2 minutes to download
        )

        if final_path and final_path.exists():
            # Copy to the requested output_path
            import shutil
            shutil.copy2(str(final_path), str(output_path))

            await browser_logger.success(
                page,
                f"{downloader_name}: Manual Download: ✓ SUCCESS! Copied to {output_path.name}",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return output_path
        else:
            await browser_logger.warning(
                page,
                f"{downloader_name}: Manual Download: ✗ No file downloaded",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return None

    except Exception as ee:
        if page is not None:
            await browser_logger.fail(
                page,
                f"{downloader_name}: Manual download failed: {ee}",
            )
            try:
                await browser_logger.info(
                    page,
                    f"{downloader_name}: Manual Download: ✗ EXCEPTION: {str(ee)[:100]}",
                )
                await page.wait_for_timeout(2000)
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
