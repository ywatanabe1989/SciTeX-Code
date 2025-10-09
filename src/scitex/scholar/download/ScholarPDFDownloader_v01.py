#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 08:06:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/ScholarPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__
import asyncio
import hashlib
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
    show_popup_and_capture_async,
)
from scitex.browser.stealth import HumanBehavior

logger = logging.getLogger(__name__)


class ScholarPDFDownloader:
    def __init__(
        self,
        context: BrowserContext,
        config: ScholarConfig = None,
        use_cache=False,
    ):
        self.config = config if config else ScholarConfig()
        self.context = context
        self.url_finder = ScholarURLFinder(self.context, config=config)
        self.use_cache = self.config.resolve(
            "use_cache_download", use_cache
        )
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
                logger.debug(
                    f"Batch download error for DOI {ii_result}: {result}"
                )
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
            logger.info(f"Downloading PDF {ii_pdf}/{len(pdf_urls)}: {url_pdf}")
            saved_path = await self.download_from_url(url_pdf, output_path)
            if saved_path:
                saved_paths.append(saved_path)

        logger.info(
            f"Downloaded {len(saved_paths)}/{len(pdf_urls)} PDFs successfully"
        )
        return saved_paths

    async def download_from_url(
        self, pdf_url: str, output_path: Union[str, Path]
    ) -> Optional[Path]:
        """Main download method with caching support."""
        import shutil

        if not pdf_url:
            logger.warn(f"PDF URL passed but not valid: {pdf_url}")
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
            logger.info(
                f"Cache hit: {pdf_url} -> {output_path} ({size_MiB:.2f} MiB)"
            )
            return output_path

        try_download_methods = [
            ("Direct Download", self._try_direct_download_async),
            ("Chrome PDF", self._try_download_from_chrome_pdf_viewer_async),
            (
                "From Response Body",
                self._try_download_from_response_body_async,
            ),
        ]

        for method_name, method_func in try_download_methods:
            logger.info(f"Trying method: {method_name}")
            try:
                is_downloaded = await method_func(pdf_url, output_path)
                if is_downloaded:
                    import shutil

                    shutil.copy2(output_path, cache_path)
                    logger.success(
                        f"Successfully downloaded via {method_name}"
                    )
                    return output_path
                else:
                    logger.debug(
                        f"{method_name} returned None (failed or not applicable)"
                    )
            except Exception as e:
                logger.warning(f"{method_name} raised exception: {e}")
                import traceback

                logger.debug(f"Traceback: {traceback.format_exc()}")

        logger.fail(f"All download methods failed for {pdf_url}")
        return None

    # 2. Download strategy implementations
    # ----------------------------------------

    async def _try_direct_download_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Handle direct download that triggers ERR_ABORTED."""
        page = None
        try:
            logger.info(f"Trying direct download from {pdf_url}")
            page = await self.context.new_page()

            download_occurred = False

            async def handle_download(download):
                nonlocal download_occurred
                await download.save_as(output_path)
                download_occurred = True

            page.on("download", handle_download)

            # Step 1: Navigate
            await show_popup_and_capture_async(
                page, f"Direct Download: Navigating to {pdf_url[:60]}..."
            )
            try:
                await page.goto(pdf_url, wait_until="load", timeout=60_000)
                await show_popup_and_capture_async(
                    page, f"Direct Download: Loaded at {page.url[:80]}"
                )
            except Exception as ee:
                if "ERR_ABORTED" in str(ee):
                    logger.info(
                        "ERR_ABORTED detected - likely direct download"
                    )
                    await show_popup_and_capture_async(
                        page,
                        "Direct Download: ERR_ABORTED (download may have started)",
                    )
                    await page.wait_for_timeout(5_000)
                else:
                    await show_popup_and_capture_async(
                        page, f"Direct Download: ✗ Error: {str(ee)[:80]}"
                    )
                    await page.wait_for_timeout(2000)
                    raise ee

            # Step 2: Check result
            if download_occurred and output_path.exists():
                size_MiB = output_path.stat().st_size / 1024 / 1024
                logger.success(
                    f"Direct download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
                )
                await show_popup_and_capture_async(
                    page,
                    f"Direct Download: ✓ SUCCESS! Downloaded {size_MiB:.2f} MB",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return output_path
            else:
                logger.debug("Direct download: No download event occurred")
                await show_popup_and_capture_async(
                    page, "Direct Download: ✗ No download event occurred"
                )
                await page.wait_for_timeout(2000)

            await page.close()
            return None

        except Exception as ee:
            logger.warn(f"Direct download failed: {ee}")
            if page is not None:
                try:
                    await show_popup_and_capture_async(
                        page, f"Direct Download: ✗ EXCEPTION: {str(ee)[:100]}"
                    )
                    await page.wait_for_timeout(2000)
                except:
                    pass
                await page.close()
            return None

    async def _try_download_from_chrome_pdf_viewer_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from Chrome PDF viewer with human-like behavior."""
        page = None
        try:
            page = await self.context.new_page()

            # Step 1: Navigate and wait for networkidle
            logger.debug("Chrome PDF: Navigating to URL...")
            await show_popup_and_capture_async(
                page, f"Chrome PDF: Navigating to {pdf_url[:60]}..."
            )
            await HumanBehavior.random_delay_async(
                1000, 2000, "before navigation"
            )
            # Navigate and wait for initial networkidle
            await page.goto(pdf_url, wait_until="networkidle", timeout=60_000)
            logger.debug(f"Chrome PDF: Loaded page at {page.url}")
            await show_popup_and_capture_async(
                page, f"Chrome PDF: Initial load at {page.url[:80]}"
            )

            # Step 2: Wait for PDF rendering and any post-load network activity
            logger.debug("Chrome PDF: Waiting for PDF rendering...")
            await show_popup_and_capture_async(
                page, "Chrome PDF: Waiting for PDF rendering (networkidle)..."
            )
            try:
                # Wait for network to be fully idle (catches post-load PDF requests)
                await page.wait_for_load_state("networkidle", timeout=30_000)
                logger.success(
                    "Chrome PDF: Network idle, PDF should be rendered"
                )
                await show_popup_and_capture_async(
                    page, "Chrome PDF: ✓ Network idle, PDF rendered"
                )
                await page.wait_for_timeout(2000)
            except Exception as e:
                logger.debug(f"Network idle timeout (non-fatal): {e}")
                await show_popup_and_capture_async(
                    page, "Chrome PDF: Network still active, continuing anyway"
                )
                await page.wait_for_timeout(2000)

            # Step 2.5: Extra wait for PDF viewer iframe/embed to fully load
            # Chrome PDF viewer can take additional time to initialize
            await show_popup_and_capture_async(
                page,
                "Chrome PDF: Waiting extra for PDF viewer to initialize (10s)...",
            )
            await page.wait_for_timeout(10000)  # Additional 10 seconds

            # Step 3: Detect PDF viewer
            logger.debug("Chrome PDF: Detecting PDF viewer...")
            await show_popup_and_capture_async(
                page, "Chrome PDF: Detecting PDF viewer..."
            )
            if not await detect_chrome_pdf_viewer_async(page):
                logger.debug(
                    f"Chrome PDF: No PDF viewer detected at {page.url}"
                )
                await show_popup_and_capture_async(
                    page, "Chrome PDF: ✗ No PDF viewer detected!"
                )
                await page.wait_for_timeout(2000)  # Show message for 2s
                await page.close()
                return None

            # Step 4: PDF viewer detected!
            logger.info(
                "Chrome PDF: PDF viewer detected, attempting download..."
            )
            await show_popup_and_capture_async(
                page, "Chrome PDF: ✓ PDF viewer detected!"
            )
            await HumanBehavior.random_delay_async(1000, 2000, "viewing PDF")

            # Step 5: Show grid and click center
            await show_popup_and_capture_async(
                page, "Chrome PDF: Showing grid overlay..."
            )
            await show_grid_async(page)
            await show_popup_and_capture_async(
                page, "Chrome PDF: Clicking center of PDF..."
            )
            await click_center_async(page)

            # Step 6: Click download button
            logger.debug("Chrome PDF: Clicking download button...")
            await show_popup_and_capture_async(
                page, "Chrome PDF: Clicking download button..."
            )
            is_downloaded = await click_download_for_chrome_pdf_viewer_async(
                page, output_path
            )

            # Step 7: Wait for download to complete (use networkidle for patience)
            logger.debug("Chrome PDF: Waiting for download to complete...")
            await show_popup_and_capture_async(
                page,
                "Chrome PDF: Waiting for download (networkidle up to 30s)...",
            )
            try:
                # Wait for any download-related network activity to complete
                await page.wait_for_load_state("networkidle", timeout=30_000)
                logger.debug("Chrome PDF: Network idle after download click")
                await show_popup_and_capture_async(
                    page, "Chrome PDF: ✓ Download network activity complete"
                )
                await page.wait_for_timeout(2000)
            except Exception as e:
                logger.debug(f"Download networkidle timeout (non-fatal): {e}")
                await show_popup_and_capture_async(
                    page, "Chrome PDF: Network timeout, checking file..."
                )
                await page.wait_for_timeout(2000)

            # Step 8: Check if file was actually downloaded
            if is_downloaded and output_path.exists():
                file_size = output_path.stat().st_size
                if file_size > 1000:  # At least 1KB
                    logger.success(
                        f"Chrome PDF: Downloaded {file_size/1024:.1f}KB from {pdf_url}"
                    )
                    await show_popup_and_capture_async(
                        page,
                        f"Chrome PDF: ✓ SUCCESS! Downloaded {file_size/1024:.1f}KB",
                    )
                    await page.wait_for_timeout(2000)  # Show success for 2s
                    await page.close()
                    return output_path
                else:
                    logger.warning(
                        f"Chrome PDF: File too small ({file_size} bytes), likely failed"
                    )
                    await show_popup_and_capture_async(
                        page,
                        f"Chrome PDF: ✗ File too small ({file_size} bytes)",
                    )
                    await page.wait_for_timeout(2000)
                    await page.close()
                    return None

            await show_popup_and_capture_async(
                page, "Chrome PDF: ✗ Download did not complete"
            )
            await page.wait_for_timeout(2000)
            await page.close()

            if is_downloaded:
                logger.success(
                    f"Downloaded via Chrome PDF Viewer: from {pdf_url} to {output_path}"
                )
                return output_path
            else:
                logger.debug(
                    f"Chrome PDF Viewer method didn't work for: {pdf_url}"
                )
                return None

        except Exception as ee:
            logger.fail(
                f"Chrome PDF Viewer failed to download from {pdf_url} to {output_path}: {str(ee)}"
            )
            if page:
                try:
                    await show_popup_and_capture_async(
                        page, f"Chrome PDF: ✗ EXCEPTION: {str(ee)[:100]}"
                    )
                    await page.wait_for_timeout(3000)  # Show error for 3s
                except:
                    pass  # Don't fail on popup error
                await page.close()
            return None

    async def _try_download_from_response_body_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from HTTP response body."""
        page = None
        try:
            logger.info(f"Trying to download {pdf_url} from response body")
            page = await self.context.new_page()

            # Step 1: Navigate
            await show_popup_and_capture_async(
                page, f"Response Body: Navigating to {pdf_url[:60]}..."
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

            await show_popup_and_capture_async(
                page,
                f"Response Body: Loaded, waiting for auto-download (60s)...",
            )
            await page.wait_for_timeout(60_000)

            # Check if auto-download occurred
            if download_path and download_path.exists():
                size_MiB = download_path.stat().st_size / 1024 / 1024
                logger.success(
                    f"Auto-download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
                )
                await show_popup_and_capture_async(
                    page,
                    f"Response Body: ✓ Auto-download SUCCESS! {size_MiB:.2f} MB",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return output_path

            # Step 2: Check response
            await show_popup_and_capture_async(
                page,
                f"Response Body: Checking response (status: {response.status})...",
            )

            if not response.ok:
                logger.fail(
                    f"Page not reached: {pdf_url} (reason: {response.status})"
                )
                await show_popup_and_capture_async(
                    page, f"Response Body: ✗ HTTP {response.status}"
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return None

            # Step 3: Extract from response body
            await show_popup_and_capture_async(
                page, "Response Body: Extracting PDF from response body..."
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
                logger.success(
                    f"Response body download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
                )
                await show_popup_and_capture_async(
                    page,
                    f"Response Body: ✓ SUCCESS! Extracted {size_MiB:.2f} MB",
                )
                await page.wait_for_timeout(2000)
                await page.close()
                return output_path

            logger.info("Failed download from response body")
            await show_popup_and_capture_async(
                page,
                f"Response Body: ✗ Not PDF (type: {content_type}, size: {len(content)})",
            )
            await page.wait_for_timeout(2000)
            await page.close()
            return None

        except Exception as ee:
            logger.info(f"Failed download from response body: {ee}")
            if page is not None:
                try:
                    await show_popup_and_capture_async(
                        page, f"Response Body: ✗ EXCEPTION: {str(ee)[:100]}"
                    )
                    await page.wait_for_timeout(2000)
                except:
                    pass
                await page.close()
            return None

    # 3. Helper functions
    # ----------------------------------------

    def get_cache_path(self, pdf_url: str) -> Path:
        """Generate cache path from PDF URL hash."""
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.pdf"


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )
        from scitex.scholar.auth import AuthenticationGateway

        # Test IEEE paper (requires authentication)
        DOI = "10.1109/niles56402.2022.9942397"
        PDF_URL = (
            "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9942397"
        )
        OUTPUT_PATH = "/tmp/IEEE_PAPER.pdf"

        DOI = "https://doi.org/10.1088/1741-2552/aaf92e"
        PDF_URL = (
            "https://iopscience.iop.org/article/10.1088/1741-2552/aaf92e/pdf"
        )
        OUTPUT_PATH = "/tmp/JNE_PAPER.pdf"

        DOI = "10.1038/nature12373"
        PDF_URL = "https://www.nature.com/articles/nature12373.pdf"
        OUTPUT_PATH = "/tmp/NATURE_PAPER.pdf"

        # Modules
        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            chrome_profile_name="system",
            # browser_mode="stealth",
            browser_mode="interactive",
            auth_manager=auth_manager,
            use_zenrows_proxy=False,
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        auth_gateway = AuthenticationGateway(
            auth_manager=auth_manager,
            browser_manager=browser_manager,
        )
        _url_context = await auth_gateway.prepare_context_async(
            doi=DOI, context=context
        )
        pdf_downloader = ScholarPDFDownloader(context)

        # Now download with authenticated context
        saved_path = await pdf_downloader.download_from_url(
            PDF_URL,
            OUTPUT_PATH,
        )

        if saved_path:
            logger.success(f"PDF downloaded to: {saved_path}")
        else:
            logger.fail("PDF download failed")

    asyncio.run(main_async())

# python -m download.ScholarPDFDownloader

# EOF
