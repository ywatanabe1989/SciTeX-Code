#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 11:51:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/ScholarPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

__FILE__ = __file__
import asyncio
import hashlib
import shutil
from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar import ScholarConfig, ScholarURLFinder
from scitex.scholar.browser import (
    click_center_async,
    click_download_for_chrome_pdf_viewer_async,
    detect_chrome_pdf_viewer_async,
    show_grid_async,
    browser_logger,
)
from scitex.browser.stealth import HumanBehavior

logger = logging.getLogger(__name__)


class ScholarPDFDownloader:
    """Download PDFs from academic publishers with authentication support.

    Logging Strategy:
    - Uses `logger` for terminal-only logs (batch operations, coordination, cache)
    - Uses `await browser_logger` for browser automation logs (creates visual popups on page)
    - All messages prefixed with self.name for traceability
    """
    def __init__(
        self,
        context: BrowserContext,
        config: ScholarConfig = None,
        use_cache=False,
    ):
        self.name = self.__class__.__name__
        self.config = config if config else ScholarConfig()
        self.context = context
        self.url_finder = ScholarURLFinder(self.context, config=config)
        self.use_cache = self.config.resolve("use_cache_download", use_cache)
        self.cache_dir = self.config.get_cache_dowload_dir()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    # 1. Main entry points
    # ----------------------------------------

    async def download_from_dois_batch(
        self,
        dois: List[str],
        output_dir: str = "/tmp/",
        max_concurrent: int = 3,
    ) -> List[List[Path]]:
        """Download PDFs for multiple DOIs in batch with parallel processing."""
        if not dois:
            return []

        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(doi: str):
            async with semaphore:
                return await self.download_from_doi(
                    doi=doi, output_dir=output_dir
                )

        tasks = [download_with_semaphore(doi) for doi in dois]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_results = []
        for ii_result, result in enumerate(results):
            if isinstance(result, Exception):
                logger.debug(f"{self.name}: Batch download error for DOI {ii_result}: {result}")
                batch_results.append([])
            else:
                batch_results.append(result or [])

        return batch_results

    async def download_from_doi(
        self, doi: str, output_dir: str = "/tmp/"
    ) -> List[Path]:
        """Download PDFs for a given DOI."""
        output_dir = Path(str(output_dir))
        urls = await self.url_finder.find_urls(doi=doi)
        pdf_urls = [url_pdf_entry["url"] for url_pdf_entry in urls["url_pdf"]]
        saved_paths = await self.download_from_urls(
            pdf_urls, output_dir=output_dir
        )
        return saved_paths

    async def download_from_urls(
        self, pdf_urls: List[str], output_dir: Union[str, Path] = "/tmp/"
    ) -> List[Path]:
        """Download multiple PDFs."""
        if not pdf_urls:
            return []

        output_paths = [
            Path(str(output_dir)) / f"{ii_pdf:03d}_{os.path.basename(pdf_url)}"
            for ii_pdf, pdf_url in enumerate(pdf_urls)
        ]

        saved_paths = []
        for ii_pdf, (url_pdf, output_path) in enumerate(
            zip(pdf_urls, output_paths), 1
        ):
            logger.info(f"{self.name}: Downloading PDF {ii_pdf}/{len(pdf_urls)}: {url_pdf}")
            saved_path = await self.download_from_url(url_pdf, output_path)
            if saved_path:
                saved_paths.append(saved_path)

        logger.success(f"{self.name}: Downloaded {len(saved_paths)}/{len(pdf_urls)} PDFs successfully")
        return saved_paths

    async def download_from_url(
        self, pdf_url: str, output_path: Union[str, Path]
    ) -> Optional[Path]:
        """Main download method with caching support."""

        if not pdf_url:
            logger.warning(f"{self.name}: PDF URL passed but not valid: {pdf_url}")
            return None

        if isinstance(output_path, str):
            output_path = Path(output_path)
        if not str(output_path).endswith(".pdf"):
            output_path = Path(str(output_path) + ".pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cache_path = self.get_cache_path(pdf_url)
        if cache_path.exists() and cache_path.stat().st_size > 1024:
            shutil.copy2(cache_path, output_path)
            size_MiB = output_path.stat().st_size / 1024 / 1024
            logger.success(
                f"{self.name}: Cache hit: {pdf_url} -> {output_path} ({size_MiB:.2f} MiB)"
            )
            return output_path

        try_download_methods = [
            ("Chrome PDF", self._try_download_from_chrome_pdf_viewer_async),
            ("Direct Download", self._try_direct_download_async),
            (
                "From Response Body",
                self._try_download_from_response_body_async,
            ),
        ]

        for method_name, method_func in try_download_methods:
            logger.info(f"{self.name}: Trying method: {method_name}")
            try:
                is_downloaded = await method_func(pdf_url, output_path)
                if is_downloaded:
                    shutil.copy2(output_path, cache_path)
                    logger.success(f"{self.name}: Successfully downloaded via {method_name}")
                    return output_path
                else:
                    logger.debug(f"{self.name}: {method_name} returned None (failed or not applicable)")
            except Exception as e:
                logger.warning(f"{self.name}: {method_name} raised exception: {e}")
                import traceback

                logger.debug(f"{self.name}: Traceback: {traceback.format_exc()}")

        logger.fail(f"{self.name}: All download methods failed for {pdf_url}")
        return None

    # 2. Download strategy implementations
    # ----------------------------------------
    async def _try_direct_download_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Handle direct download that triggers ERR_ABORTED."""
        page = None
        try:
            page = await self.context.new_page()
            await browser_logger.info(page, f"{self.name}: Trying direct download from {pdf_url}")

            download_occurred = False

            async def handle_download(download):
                nonlocal download_occurred
                await download.save_as(output_path)
                download_occurred = True

            page.on("download", handle_download)

            # Step 1: Navigate
            await browser_logger.info(page, f"{self.name}: Direct Download: Navigating to {pdf_url[:60]}..."
            )
            try:
                await page.goto(pdf_url, wait_until="load", timeout=60_000)
                await browser_logger.info(page, f"{self.name}: Direct Download: Loaded at {page.url[:80]}"
                )
            except Exception as ee:
                if "ERR_ABORTED" in str(ee):
                    await browser_logger.info(page, f"{self.name}: Direct Download: ERR_ABORTED detected - likely direct download")
                    await browser_logger.info(page, f"{self.name}: Direct Download: ERR_ABORTED (download may have started)",
                    )
                    await page.wait_for_timeout(5_000)
                else:
                    await browser_logger.info(page, f"{self.name}: Direct Download: ✗ Error: {str(ee)[:80]}"
                    )
                    await page.wait_for_timeout(2000)
                    raise ee

            # Step 2: Check result
            if download_occurred and output_path.exists():
                size_MiB = output_path.stat().st_size / 1024 / 1024
                await browser_logger.success(page, f"{self.name}: Direct download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)")
                await browser_logger.success(page, f"{self.name}: Direct Download: ✓ SUCCESS! Downloaded {size_MiB:.2f} MB",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return output_path
            else:
                await browser_logger.debug(page, f"{self.name}: Direct download: No download event occurred")
                await browser_logger.info(page, f"{self.name}: Direct Download: ✗ No download event occurred"
                )
                await page.wait_for_timeout(2000)

            await page.close()
            return None

        except Exception as ee:
            if page is not None:
                await browser_logger.warning(page, f"{self.name}: Direct download failed: {ee}")
                try:
                    await browser_logger.info(page, f"{self.name}: Direct Download: ✗ EXCEPTION: {str(ee)[:100]}"
                    )
                    await page.wait_for_timeout(2000)
                except Exception as popup_error:
                    logger.debug(f"{self.name}: Could not show error popup: {popup_error}")
                finally:
                    try:
                        await page.close()
                    except Exception as close_error:
                        logger.debug(f"{self.name}: Error closing page: {close_error}")
            return None

    async def _try_download_from_chrome_pdf_viewer_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from Chrome PDF viewer with human-like behavior."""
        page = None
        try:
            page = await self.context.new_page()

            # Step 1: Navigate and wait for networkidle
            await browser_logger.debug(page, f"{self.name}: Chrome PDF: Navigating to URL...")
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Navigating to {pdf_url[:60]}..."
            )
            await HumanBehavior.random_delay_async(
                1000, 2000, "before navigation"
            )
            # Navigate and wait for initial networkidle
            await page.goto(pdf_url, wait_until="networkidle", timeout=60_000)
            await browser_logger.debug(page, f"{self.name}: Chrome PDF: Loaded page at {page.url}")
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Initial load at {page.url[:80]}"
            )

            # Step 2: Wait for PDF rendering and any post-load network activity
            await browser_logger.debug(page, f"{self.name}: Chrome PDF: Waiting for PDF rendering...")
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Waiting for PDF rendering (networkidle)..."
            )
            try:
                # Wait for network to be fully idle (catches post-load PDF requests)
                await page.wait_for_load_state("networkidle", timeout=30_000)
                await browser_logger.success(page, f"{self.name}: Chrome PDF: Network idle, PDF should be rendered")
                await browser_logger.success(page, f"{self.name}: Chrome PDF: ✓ Network idle, PDF rendered"
                )
                await page.wait_for_timeout(2000)
            except Exception as e:
                await browser_logger.debug(page, f"{self.name}: Network idle timeout (non-fatal): {e}")
                await browser_logger.info(page, f"{self.name}: Chrome PDF: Network still active, continuing anyway"
                )
                await page.wait_for_timeout(2000)

            # Step 2.5: Extra wait for PDF viewer iframe/embed to fully load
            # Chrome PDF viewer can take additional time to initialize
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Waiting extra for PDF viewer to initialize (10s)...",
            )
            await page.wait_for_timeout(10000)  # Additional 10 seconds

            # Step 3: Detect PDF viewer
            await browser_logger.debug(page, f"{self.name}: Chrome PDF: Detecting PDF viewer...")
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Detecting PDF viewer..."
            )
            if not await detect_chrome_pdf_viewer_async(page):
                await browser_logger.warning(page, f"{self.name}: Chrome PDF: No PDF viewer detected at {page.url}")
                await browser_logger.warning(page, f"{self.name}: Chrome PDF: ✗ No PDF viewer detected!"
                )
                await page.wait_for_timeout(2000)  # Show message for 2s
                await page.close()
                return None

            # Step 4: PDF viewer detected!
            await browser_logger.success(page, f"{self.name}: Chrome PDF: PDF viewer detected, attempting download...")
            await browser_logger.success(page, f"{self.name}: Chrome PDF: ✓ PDF viewer detected!"
            )
            await HumanBehavior.random_delay_async(1000, 2000, "viewing PDF")

            # Step 5: Show grid and click center
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Showing grid overlay..."
            )
            await show_grid_async(page)
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Clicking center of PDF..."
            )
            await click_center_async(page)

            # Step 6: Click download button
            await browser_logger.debug(page, f"{self.name}: Chrome PDF: Clicking download button...")
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Clicking download button..."
            )
            is_downloaded = await click_download_for_chrome_pdf_viewer_async(
                page, output_path
            )

            # Step 7: Wait for download to complete (use networkidle for patience)
            await browser_logger.debug(page, f"{self.name}: Chrome PDF: Waiting for download to complete...")
            await browser_logger.info(page, f"{self.name}: Chrome PDF: Waiting for download (networkidle up to 30s)...",
            )
            try:
                # Wait for any download-related network activity to complete
                await page.wait_for_load_state("networkidle", timeout=30_000)
                await browser_logger.debug(page, f"{self.name}: Chrome PDF: Network idle after download click")
                await browser_logger.success(page, f"{self.name}: Chrome PDF: ✓ Download network activity complete"
                )
                await page.wait_for_timeout(2000)
            except Exception as e:
                await browser_logger.debug(page, f"{self.name}: Download networkidle timeout (non-fatal): {e}")
                await browser_logger.info(page, f"{self.name}: Chrome PDF: Network timeout, checking file..."
                )
                await page.wait_for_timeout(2000)

            # Step 8: Check if file was actually downloaded
            if is_downloaded and output_path.exists():
                file_size = output_path.stat().st_size
                if file_size > 1000:  # At least 1KB
                    await browser_logger.success(page, f"{self.name}: Chrome PDF: Downloaded {file_size/1024:.1f}KB from {pdf_url}")
                    await browser_logger.success(page, f"{self.name}: Chrome PDF: ✓ SUCCESS! Downloaded {file_size/1024:.1f}KB",
                    )
                    await page.wait_for_timeout(2000)  # Show success for 2s
                    await page.close()
                    return output_path
                else:
                    await browser_logger.warning(page, f"{self.name}: Chrome PDF: File too small ({file_size} bytes), likely failed")
                    await browser_logger.warning(page, f"{self.name}: Chrome PDF: ✗ File too small ({file_size} bytes)",
                    )
                    await page.wait_for_timeout(2000)
                    await page.close()
                    return None

            await browser_logger.info(page, f"{self.name}: Chrome PDF: ✗ Download did not complete"
            )
            await page.wait_for_timeout(2000)
            await page.close()

            if is_downloaded:
                await browser_logger.success(page, f"{self.name}: Downloaded via Chrome PDF Viewer: from {pdf_url} to {output_path}")
                return output_path
            else:
                await browser_logger.debug(page, f"{self.name}: Chrome PDF Viewer method didn't work for: {pdf_url}")
                return None

        except Exception as ee:
            if page:
                await browser_logger.fail(page, f"{self.name}: Chrome PDF Viewer failed to download from {pdf_url} to {output_path}: {str(ee)}")
                try:
                    await browser_logger.info(page, f"{self.name}: Chrome PDF: ✗ EXCEPTION: {str(ee)[:100]}"
                    )
                    await page.wait_for_timeout(3000)  # Show error for 3s
                except Exception as popup_error:
                    logger.debug(f"{self.name}: Could not show error popup: {popup_error}")
                finally:
                    try:
                        await page.close()
                    except Exception as close_error:
                        logger.debug(f"{self.name}: Error closing page: {close_error}")
            return None

    async def _try_download_from_response_body_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from HTTP response body."""
        page = None
        try:
            page = await self.context.new_page()
            await browser_logger.info(page, f"{self.name}: Trying to download {pdf_url} from response body")

            # Step 1: Navigate
            await browser_logger.info(page, f"{self.name}: Response Body: Navigating to {pdf_url[:60]}..."
            )

            download_path = None

            async def handle_download(download):
                nonlocal download_path
                await download.save_as(output_path)
                download_path = output_path

            page.on("download", handle_download)

            response = await page.goto(
                pdf_url, wait_until="load", timeout=60_000
            )

            await browser_logger.info(page, f"{self.name}: Response Body: Loaded, waiting for auto-download (60s)...",
            )
            await page.wait_for_timeout(60_000)

            # Check if auto-download occurred
            if download_path and download_path.exists():
                size_MiB = download_path.stat().st_size / 1024 / 1024
                await browser_logger.success(page, f"{self.name}: Auto-download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)")
                await browser_logger.success(page, f"{self.name}: Response Body: ✓ Auto-download SUCCESS! {size_MiB:.2f} MB",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return output_path

            # Step 2: Check response
            await browser_logger.info(page, f"{self.name}: Response Body: Checking response (status: {response.status})...",
            )

            if not response.ok:
                await browser_logger.fail(page, f"{self.name}: Page not reached: {pdf_url} (reason: {response.status})")
                await browser_logger.fail(page, f"{self.name}: Response Body: ✗ HTTP {response.status}"
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return None

            # Step 3: Extract from response body
            await browser_logger.info(page, f"{self.name}: Response Body: Extracting PDF from response body..."
            )
            content = await response.body()
            content_type = response.headers.get("content-type", "")

            is_pdf = (
                content[:4] == b"%PDF" or "application/pdf" in content_type
            )

            is_html = (
                content[:15].lower().startswith(b"<!doctype html")
                or content[:6].lower().startswith(b"<html")
                or "text/html" in content_type
            )

            if is_pdf and not is_html and len(content) > 1024:
                with open(output_path, "wb") as file_:
                    file_.write(content)
                size_MiB = len(content) / 1024 / 1024
                await browser_logger.success(page, f"{self.name}: Response body download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)")
                await browser_logger.success(page, f"{self.name}: Response Body: ✓ SUCCESS! Extracted {size_MiB:.2f} MB",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return output_path

            await browser_logger.warning(page, f"{self.name}: Failed download from response body")
            await browser_logger.warning(page, f"{self.name}: Response Body: ✗ Not PDF (type: {content_type}, size: {len(content)})",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return None

        except Exception as ee:
            if page is not None:
                await browser_logger.warning(page, f"{self.name}: Failed download from response body: {ee}")
                try:
                    await browser_logger.info(page, f"{self.name}: Response Body: ✗ EXCEPTION: {str(ee)[:100]}"
                    )
                    await page.wait_for_timeout(2000)
                except Exception as popup_error:
                    logger.debug(f"{self.name}: Could not show error popup: {popup_error}")
                finally:
                    try:
                        await page.close()
                    except Exception as close_error:
                        logger.debug(f"{self.name}: Error closing page: {close_error}")
            return None

    # 3. Helper functions
    # ----------------------------------------

    def get_cache_path(self, pdf_url: str) -> Path:
        """Generate cache path from PDF URL hash."""
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.pdf"


async def main_async(args):
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarEngine,
        ScholarURLFinder,
    )
    from scitex.scholar.auth import AuthenticationGateway

    # ---------------------------------------
    # Context Preparation
    # ---------------------------------------
    # Authenticated Browser and Context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=args.browser_mode,
        auth_manager=auth_manager,
        use_zenrows_proxy=False,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Authentication Gateway
    auth_gateway = AuthenticationGateway(
        auth_manager=auth_manager,
        browser_manager=browser_manager,
    )
    _url_context = await auth_gateway.prepare_context_async(
        doi=args.doi, context=context
    )

    # ---------------------------------------
    # URL Finder
    # ---------------------------------------
    url_finder = ScholarURLFinder(context, use_cache=False)
    urls = await url_finder.find_urls(doi=args.doi)
    pdf_url = urls.get("urls_pdf", [])[0].get("url")

    # ---------------------------------------
    # Main: PDF Dowanlod
    # ---------------------------------------
    pdf_downloader = ScholarPDFDownloader(context)
    await pdf_downloader.download_from_url(
        pdf_url,
        args.output,
    )


def main(args):
    import asyncio

    asyncio.run(main_async(args))

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download a PDF using DOI with authentication support"
    )
    parser.add_argument(
        "--doi",
        type=str,
        required=True,
        help="DOI of the paper (e.g., 10.1088/1741-2552/aaf92e)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/tmp/downloaded_paper.pdf",
        help="Output path for the PDF (default: /tmp/downloaded_paper.pdf)",
    )
    parser.add_argument(
        "--browser-mode",
        type=str,
        choices=["stealth", "interactive", "manual"],
        default="stealth",
        help="Browser mode (default: stealth)",
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

"""
python -m scitex.scholar.download.ScholarPDFDownloader \
    --browser-mode interactive \
    --doi "10.3389/fnins.2024.1417748"
    --doi "10.1016/j.clinph.2024.09.017"

"""

# EOF
