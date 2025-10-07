#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 01:12:05 (ywatanabe)"
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
from scitex.scholar.browser.local.utils._HumanBehavior import HumanBehavior

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
            "use_cache_pdf_downloader", use_cache
        )
        self.cache_dir = self.config.get_pdf_downloader_cache_dir()

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
            is_downloaded = await method_func(pdf_url, output_path)
            if is_downloaded:
                import shutil

                shutil.copy2(output_path, cache_path)
                return output_path

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

            try:
                await show_popup_and_capture_async(
                    page, "Trying download via URL navigation..."
                )
                await page.goto(pdf_url, wait_until="load", timeout=60_000)
            except Exception as ee:
                if "ERR_ABORTED" in str(ee):
                    logger.info(
                        "ERR_ABORTED detected - likely direct download"
                    )
                    await page.wait_for_timeout(5_000)
                else:
                    raise ee

            await page.close()

            if download_occurred and output_path.exists():
                size_MiB = output_path.stat().st_size / 1024 / 1024
                logger.success(
                    f"Direct download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
                )
                return output_path

            return None

        except Exception as ee:
            logger.warn(f"Direct download failed: {ee}")
            if page is not None:
                await page.close()
            return None

    async def _try_download_from_chrome_pdf_viewer_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from Chrome PDF viewer with human-like behavior."""
        page = None
        try:
            page = await self.context.new_page()

            await HumanBehavior.random_delay_async(
                1000, 2000, "before navigation"
            )
            await page.goto(pdf_url, wait_until="load", timeout=30_000)

            await HumanBehavior.random_delay_async(2000, 3000, "PDF loading")

            if not await detect_chrome_pdf_viewer_async(page):
                logger.debug("No PDF viewer detected")
                await page.close()
                return None

            await HumanBehavior.random_delay_async(1000, 2000, "viewing PDF")

            await show_grid_async(page)
            await click_center_async(page)
            is_downloaded = (
                await click_download_for_chrome_pdf_viewer_async(
                    page, output_path
                )
            )

            await HumanBehavior.random_delay_async(
                1000, 2000, "after download click"
            )
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
            await show_popup_and_capture_async(
                page, "Checking Auto Downloading..."
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
            await page.wait_for_timeout(60_000)

            if download_path and download_path.exists():
                size_MiB = download_path.stat().st_size / 1024 / 1024
                logger.success(
                    f"Auto-download: from {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
                )
                await page.close()
                return output_path

            if not response.ok:
                logger.fail(
                    f"Page not reached: {pdf_url} (reason: {response.status})"
                )
                await page.close()
                return None

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
                await page.close()
                return output_path

            logger.info("Failed download from response body")
            await page.close()
            return None

        except Exception as ee:
            logger.info("Failed download from response body")
            if page is not None:
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

        browser_manager = ScholarBrowserManager(
            chrome_profile_name="system",
            browser_mode="stealth",
            auth_manager=ScholarAuthManager(),
            use_zenrows_proxy=False,
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )

        pdf_downloader = ScholarPDFDownloader(context)

        # PDF_URL = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"
        # OUTPUT_PATH = "/tmp/hippocampal_ripples-by-stealth.pdf"

        PDF_URL = (
            "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9942397"
        )
        OUTPUT_PATH = "/tmp/IEEE_PAPER.pdf"

        saved_path = await pdf_downloader.download_from_url(
            PDF_URL,
            OUTPUT_PATH,
        )

    asyncio.run(main_async())

# EOF
