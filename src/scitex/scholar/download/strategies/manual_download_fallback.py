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
    DownloadMonitorAndSync,
)

logger = logging.getLogger(__name__)


async def try_download_manual_async(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path,
    downloader_name: str = "ScholarPDFDownloader",
    config: ScholarConfig = None,
    doi: Optional[str] = None,
) -> Optional[Path]:
    """Manual download fallback strategy.

    Opens PDF URL in browser, shows instructions, and monitors downloads directory.
    When user manually downloads the PDF, it automatically detects and organizes it.

    NOTE: This method should NOT check the _scitex_is_manual_mode flag because
    it IS the manual mode implementation!

    Args:
        context: Browser context
        pdf_url: URL of the PDF to download
        output_path: Where to save the final PDF
        downloader_name: Name for logging
        config: Scholar configuration
        doi: Optional DOI for filename generation

    Returns:
        Path to downloaded file, or None if failed
    """
    config = config or ScholarConfig()
    page = None

    try:
        # Create new page and navigate to PDF
        page = await context.new_page()

        await browser_logger.info(
            page,
            f"{downloader_name}: Opening PDF for manual download...",
        )

        await page.goto(pdf_url, timeout=30000, wait_until='domcontentloaded')

        await browser_logger.info(
            page,
            f"{downloader_name}: Please download the PDF manually from this page",
        )

        # Setup monitoring
        downloads_dir = config.get_library_downloads_dir()
        master_dir = config.get_library_master_dir()
        monitor = DownloadMonitorAndSync(downloads_dir, master_dir)

        # Progress logger
        def log_progress(msg: str):
            logger.info(f"{downloader_name}: {msg}")

        # Extract DOI from URL if not provided
        if not doi and "doi.org/" in pdf_url:
            doi = pdf_url.split("doi.org/")[-1].split("?")[0].split("#")[0]
        elif not doi and "/doi/" in pdf_url:
            # Try to extract DOI from URL like /doi/10.1212/...
            import re
            match = re.search(r'/doi/(10\.\d+/[^\s?#]+)', pdf_url)
            if match:
                doi = match.group(1)

        # Show instructions and start monitoring
        log_progress(f"Monitoring {downloads_dir} for new PDFs...")
        log_progress("Please download the PDF manually from the browser")

        # Monitor for download (10 minutes timeout)
        temp_file = await monitor.monitor_for_new_download_async(
            timeout_sec=600,  # 10 minutes
            check_interval_sec=1.0,
            logger_func=log_progress,
        )

        if not temp_file:
            await browser_logger.error(
                page,
                f"{downloader_name}: No new PDF detected in 120 seconds",
            )
            logger.error(f"{downloader_name}: Download monitoring timeout")
            await page.close()
            return None

        await browser_logger.success(
            page,
            f"{downloader_name}: Detected: {temp_file.name} ({temp_file.stat().st_size / 1e6:.1f} MB)",
        )

        # Sync to library
        final_path = monitor.sync_to_final_destination(
            temp_file,
            doi=doi,
            url=pdf_url,
            content_type="main",
        )

        await browser_logger.success(
            page,
            f"{downloader_name}: Synced to library: {final_path.name}",
        )

        # Copy to requested output path
        if final_path and final_path.exists():
            import shutil
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(final_path), str(output_path))

            await browser_logger.success(
                page,
                f"{downloader_name}: Manual download complete!",
            )

            logger.success(f"{downloader_name}: Manual download saved to {output_path}")
            await page.close()
            return output_path

        await page.close()
        return None

    except Exception as e:
        logger.error(f"{downloader_name}: Manual download failed: {e}")
        if page:
            try:
                await browser_logger.error(
                    page,
                    f"{downloader_name}: Error: {type(e).__name__}",
                )
                await page.close()
            except Exception:
                pass
        return None


# EOF
