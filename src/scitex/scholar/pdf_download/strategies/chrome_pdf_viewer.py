#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 08:18:35 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdf_download/strategies/chrome_pdf_viewer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdf_download/strategies/chrome_pdf_viewer.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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
    func_name: str = "ScholarPDFDownloader",
) -> Optional[Path]:
    """Download PDF from Chrome PDF viewer with human-like behavior."""
    page = None
    try:
        # Ensure output_path is Path object
        if not isinstance(output_path, Path):
            output_path = Path(output_path)

        logger.debug(f"{func_name}: Chrome PDF: Starting download")
        logger.debug(f"  URL: {pdf_url} (type: {type(pdf_url)})")
        logger.debug(f"  Output: {output_path} (type: {type(output_path)})")
        logger.debug(f"  Downloader: {func_name} (type: {type(func_name)})")

        page = await context.new_page()

        # Get browser's download directory and capture files before download
        import time

        from scitex.scholar.config import ScholarConfig

        config = ScholarConfig()
        browser_downloads_dir = config.get_library_downloads_dir()
        files_before = (
            set(browser_downloads_dir.glob("*"))
            if browser_downloads_dir.exists()
            else set()
        )
        download_start_time = time.time()
        logger.info(
            f"{func_name}: Monitoring {browser_downloads_dir} ({len(files_before)} files)"
        )

        # Step 1: Navigate and wait for networkidle
        await browser_logger.debug(
            page, f"{func_name}: Chrome PDF: Navigating to URL..."
        )
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: Navigating to {str(pdf_url)[:60]}...",
        )
        # Create HumanBehavior instance for delays
        human = HumanBehavior()
        await human.random_delay_async(1000, 2000, page=page)

        # Navigate and wait for initial networkidle
        await page.goto(str(pdf_url), wait_until="networkidle", timeout=60_000)
        await browser_logger.debug(
            page,
            f"{func_name}: Chrome PDF: Loaded page at {str(page.url)}",
        )
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: Initial load at {str(page.url)[:80]}",
        )

        # Step 2: Wait for PDF rendering and any post-load network activity
        await browser_logger.debug(
            page,
            f"{func_name}: Chrome PDF: Waiting for PDF rendering...",
        )
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: Waiting for PDF rendering (networkidle)...",
        )
        try:
            # Wait for network to be fully idle (catches post-load PDF requests)
            await page.wait_for_load_state("networkidle", timeout=30_000)
            await browser_logger.info(
                page,
                f"{func_name}: Chrome PDF: Network idle, PDF should be rendered",
            )
            await browser_logger.info(
                page,
                f"{func_name}: Chrome PDF: ✓ Network idle, PDF rendered",
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
            await browser_logger.debug(
                page,
                f"{func_name}: Network idle timeout (non-fatal): {e}",
            )
            await browser_logger.info(
                page,
                f"{func_name}: Chrome PDF: Network still active, continuing anyway",
            )
            await page.wait_for_timeout(2000)

        # Step 2.5: Extra wait for PDF viewer iframe/embed to fully load
        # Chrome PDF viewer can take additional time to initialize
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: Waiting extra for PDF viewer to initialize (10s)...",
        )
        await page.wait_for_timeout(10000)  # Additional 10 seconds

        # Step 3: Detect PDF viewer
        await browser_logger.debug(
            page, f"{func_name}: Chrome PDF: Detecting PDF viewer..."
        )
        await browser_logger.info(
            page, f"{func_name}: Chrome PDF: Detecting PDF viewer..."
        )
        if not await detect_chrome_pdf_viewer_async(page):
            await browser_logger.warning(
                page,
                f"{func_name}: Chrome PDF: No PDF viewer detected at {str(page.url)}",
            )
            await browser_logger.warning(
                page,
                f"{func_name}: Chrome PDF: ✗ No PDF viewer detected!",
            )
            await page.wait_for_timeout(2000)  # Show message for 2s
            await page.close()
            return None

        # Step 4: PDF viewer detected!
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: PDF viewer detected, attempting download...",
        )
        await browser_logger.info(
            page, f"{func_name}: Chrome PDF: ✓ PDF viewer detected!"
        )

        # Wait for PDF to fully render for visual feedback (especially in interactive mode)
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: Waiting for PDF to render (5s)...",
        )
        await page.wait_for_timeout(5000)  # 5 seconds for visual confirmation
        await human.random_delay_async(1000, 2000, page=page)

        # Step 5: Show grid and click center
        await browser_logger.info(
            page, f"{func_name}: Chrome PDF: Showing grid overlay..."
        )
        await show_grid_async(page)
        await browser_logger.info(
            page, f"{func_name}: Chrome PDF: Clicking center of PDF..."
        )
        await click_center_async(page)

        # Step 6: Click download button
        await browser_logger.debug(
            page, f"{func_name}: Chrome PDF: Clicking download button..."
        )
        await browser_logger.info(
            page, f"{func_name}: Chrome PDF: Clicking download button..."
        )
        is_downloaded = await click_download_for_chrome_pdf_viewer_async(
            page, output_path
        )

        # Step 7: Wait for download to complete (use networkidle for patience)
        await browser_logger.debug(
            page,
            f"{func_name}: Chrome PDF: Waiting for download to complete...",
        )
        await browser_logger.info(
            page,
            f"{func_name}: Chrome PDF: Waiting for download (networkidle up to 30s)...",
        )
        try:
            # Wait for any download-related network activity to complete
            await page.wait_for_load_state("networkidle", timeout=30_000)
            await browser_logger.debug(
                page,
                f"{func_name}: Chrome PDF: Network idle after download click",
            )
            await browser_logger.info(
                page,
                f"{func_name}: Chrome PDF: ✓ Download network activity complete",
            )
            await page.wait_for_timeout(2000)
        except Exception as e:
            await browser_logger.debug(
                page,
                f"{func_name}: Download networkidle timeout (non-fatal): {e}",
            )
            await browser_logger.info(
                page,
                f"{func_name}: Chrome PDF: Network timeout, checking file...",
            )
            await page.wait_for_timeout(2000)

        # Step 8: Check if file was actually downloaded
        # Check browser download directory for new files (even if Playwright event didn't fire)
        files_after = (
            set(browser_downloads_dir.glob("*"))
            if browser_downloads_dir.exists()
            else set()
        )
        new_files = files_after - files_before
        download_duration = time.time() - download_start_time

        logger.info(f"{func_name}: Checking download result...")
        logger.info(
            f"{func_name}:  is_downloaded (Playwright): {is_downloaded}"
        )
        logger.info(f"{func_name}:  output_path: {output_path}")
        logger.info(f"{func_name}:  Files before: {len(files_before)}")
        logger.info(f"{func_name}:  Files after: {len(files_after)}")
        logger.info(f"{func_name}:  New files: {len(new_files)}")

        if new_files:
            # Found new file(s) in download directory
            downloaded_file = max(new_files, key=lambda p: p.stat().st_mtime)
            file_size = downloaded_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            logger.info(
                f"{func_name}: Found downloaded file: {downloaded_file.name}"
            )
            logger.info(f"{func_name}:  Size: {file_size_mb:.2f} MB")
            logger.info(f"{func_name}:  Duration: {download_duration:.1f}s")
            logger.info(f"{func_name}:  Location: {downloaded_file}")

            if file_size > 1000:  # At least 1KB
                # Rename to desired output filename
                import shutil

                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(downloaded_file), str(output_path))

                await browser_logger.info(
                    page,
                    f"{func_name}: ✓ Downloaded {file_size_mb:.2f} MB in {download_duration:.1f}s",
                )
                await browser_logger.info(
                    page,
                    f"{func_name}: ✓ Saved to: {str(output_path)}",
                )
                logger.info(
                    f"{func_name}: Downloaded PDF: {output_path} ({file_size_mb:.2f} MB)"
                )
                await page.wait_for_timeout(3000)
                await page.close()
                return output_path

        if is_downloaded and output_path.exists():
            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            if file_size > 1000:  # At least 1KB
                await browser_logger.info(
                    page,
                    f"{func_name}: ✓ Downloaded {file_size_mb:.2f} MB",
                )
                await browser_logger.info(
                    page,
                    f"{func_name}: ✓ Saved to: {str(output_path)}",
                )
                logger.info(
                    f"{func_name}: Downloaded PDF: {output_path} ({file_size_mb:.2f} MB)"
                )
                await page.wait_for_timeout(3000)  # Show info for 3s
                await page.close()
                return output_path
            else:
                await browser_logger.warning(
                    page,
                    f"{func_name}: ✗ File too small: {file_size} bytes",
                )
                logger.warning(
                    f"{func_name}: Download failed - file too small: {file_size} bytes"
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return None
        elif output_path.exists():
            # File exists but is_downloaded is False - still check file
            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            if file_size > 1000:
                await browser_logger.info(
                    page,
                    f"{func_name}: ✓ File found: {file_size_mb:.2f} MB",
                )
                await browser_logger.info(
                    page,
                    f"{func_name}: ✓ Saved to: {str(output_path)}",
                )
                logger.info(
                    f"{func_name}: Downloaded PDF: {output_path} ({file_size_mb:.2f} MB)"
                )
                await page.wait_for_timeout(3000)
                await page.close()
                return output_path

        await browser_logger.warning(
            page, f"{func_name}: ✗ Download did not complete"
        )
        logger.warning(
            f"{func_name}: Download did not complete (is_downloaded={is_downloaded}, exists={output_path.exists()})"
        )
        await page.wait_for_timeout(2000)
        await page.close()

        if is_downloaded:
            await browser_logger.info(
                page,
                f"{func_name}: Downloaded via Chrome PDF Viewer from {str(pdf_url)} to {str(output_path)}",
            )
            return output_path
        else:
            await browser_logger.debug(
                page,
                f"{func_name}: Chrome PDF Viewer method did not work for {str(pdf_url)}",
            )
            return None

    except Exception as ee:
        # Log error safely without browser popup (avoids recursive errors)
        error_msg = f"{func_name}: Chrome PDF Viewer failed: {type(ee).__name__}: {str(ee)}"
        logger.error(error_msg)
        logger.debug(f"  URL: {pdf_url}")
        logger.debug(f"  Output: {output_path}")

        if page:
            try:
                await browser_logger.info(
                    page,
                    f"{func_name}: Chrome PDF: ✗ EXCEPTION: {type(ee).__name__}",
                )
                await page.wait_for_timeout(2000)  # Show error for 2s
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
