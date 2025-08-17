#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 20:53:16 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/ScholarPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import base64
from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import BrowserContext, Page, async_playwright

from scitex import logging
from scitex.scholar import ScholarURLFinder
from scitex.scholar.browser import PlaywrightVision

logger = logging.getLogger(__name__)

# Timing differences:
# 1. `timeout=60_000` - Maximum wait time for operation to complete
# 2. `page.wait_for_timeout(5_000)` - Fixed delay (like sleep but async)
# 3. `time.sleep()` - Blocks entire thread (avoid in async code)


class ScholarPDFDownloader:
    def __init__(
        self,
        context: BrowserContext,
    ):
        self.context = context
        self.url_finder = ScholarURLFinder(self.context)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def download_from_url(
        self, pdf_url: str, output_path: Union[str, Path]
    ) -> Optional[Path]:
        """
        Main download method that tries all options in order.
        Returns the path if successful, None otherwise.
        """

        # Output path with parent directory ensured
        if isinstance(output_path, str):
            output_path = Path(output_path)
        if not str(output_path).endswith(".pdf"):
            output_path = Path(str(output_path) + ".pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Try each download method in order of reliability/speed
        try_download_methods = [
            (
                "From Response Body",
                self._try_download_from_response_body_async,
            ),
            (
                "Chrome PDF",
                self._try_download_from_chrome_pdf_viewer_async,
            ),
        ]

        for method_name, method_func in try_download_methods:
            logger.info(f"Trying method: {method_name}")
            is_downloaded = await method_func(pdf_url, output_path)
            if is_downloaded:
                logger.success(f"Successfully downloaded using: {method_name}")
                return is_downloaded
            else:
                logger.warning(f"Method failed: {method_name}")

        logger.fail(f"All download methods failed for {pdf_url}")
        return None

    async def _try_download_from_response_body_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from HTTP response body."""
        page = None
        try:
            logger.info("Trying to download from response body")
            page = await self.context.new_page()

            response = await page.goto(
                pdf_url, wait_until="load", timeout=60_000
            )
            await page.wait_for_timeout(5_000)

            if not response.ok:
                logger.fail(
                    f"Page not reached: {pdf_url} (reason: {response.status})"
                )
                await page.close()
                return None

            content = await response.body()

            if content[:4] == b"%PDF":
                with open(output_path, "wb") as file_:
                    file_.write(content)
                size_MiB = len(content) / 1024 / 1024
                logger.success(
                    f"Response body download: {output_path} ({size_MiB:.2f} MiB)"
                )
                await page.close()
                return output_path

            await page.close()
            return None

        except Exception as ee:
            logger.warn("Failed download from response body")
            if page is not None:
                await page.close()
            return None

    async def _try_download_from_chrome_pdf_viewer_async(
        self, pdf_url: str, output_path: Path
    ) -> Optional[Path]:
        """Download PDF from Chrome PDF viewer."""
        page = None
        try:
            page = await self.context.new_page()
            await page.goto(pdf_url, wait_until="load", timeout=60_000)

            if not await detect_pdf_viewer_async(page):
                await page.close()
                return None

            await show_grid_async(page)
            await click_center_async(page)

            is_downloaded = (
                await click_download_button_from_chrome_pdf_viewer_async(
                    page, output_path
                )
            )
            await page.close()

            if is_downloaded:
                logger.success("Downloaded via Chrome PDF Viewer")
                return output_path
            else:
                logger.fail("Failed via Chrome PDF Viewer")
                return None

        except Exception as ee:
            logger.fail(f"Chrome PDF Viewer failed: {str(ee)}")
            if page:
                await page.close()
            return None

    async def download_from_urls(
        self, pdf_urls: List[str], output_dir: Union[str, Path] = "/tmp/"
    ) -> List[Path]:
        """Download multiple PDFs."""
        output_paths = [
            Path(str(output_dir)) / os.path.basename(pdf_url)
            for pdf_url in pdf_urls
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


async def detect_pdf_viewer_async(page):
    await page.wait_for_load_state("networkidle")
    detected = await page.evaluate(
        """
    () => {
        return !!(
            document.querySelector('embed[type="application/pdf"]') ||
            document.querySelector('iframe[src*=".pdf"]') ||
            document.querySelector('object[type="application/pdf"]') ||
            window.PDFViewerApplication ||
            document.querySelector('[data-testid="pdf-viewer"]')
        );
    }
    """
    )
    if detected:
        logger.info("PDF viewer detected")
        return True
    else:
        logger.info("PDF viewer not detected")
        return False


async def show_grid_async(page):
    await page.evaluate(
        """() => {
        const canvas = document.createElement('canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '9999';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const ctx = canvas.getContext('2d');
        ctx.font = '12px Arial';

        for (let xx = 0; xx < canvas.width; xx += 20) {
            ctx.strokeStyle = xx % 100 === 0 ? 'red' : '#ffcccc';
            ctx.lineWidth = xx % 100 === 0 ? 1 : 0.5;
            ctx.beginPath();
            ctx.moveTo(xx, 0);
            ctx.lineTo(xx, canvas.height);
            ctx.stroke();
            if (xx % 100 === 0) {
                ctx.fillStyle = 'red';
                ctx.fillText(xx, xx + 5, 15);
            }
        }

        for (let yy = 0; yy < canvas.height; yy += 20) {
            ctx.strokeStyle = yy % 100 === 0 ? 'red' : '#ffcccc';
            ctx.lineWidth = yy % 100 === 0 ? 1 : 0.5;
            ctx.beginPath();
            ctx.moveTo(0, yy);
            ctx.lineTo(canvas.width, yy);
            ctx.stroke();
            if (yy % 100 === 0) {
                ctx.fillStyle = 'red';
                ctx.fillText(yy, 5, yy + 15);
            }
        }

        document.body.appendChild(canvas);
    }"""
    )


async def click_center_async(page):
    viewport_size = page.viewport_size
    center_x = viewport_size["width"] // 2
    center_y = viewport_size["height"] // 2
    clicked = await page.mouse.click(center_x, center_y)
    await page.wait_for_timeout(1_000)
    return clicked


async def click_download_button_from_chrome_pdf_viewer_async(
    page, spath_pdf
) -> Optional[Path]:
    """Download PDF from Chrome PDF viewer using percentage-based coordinates."""
    try:
        spath_pdf = str(spath_pdf)
        viewport = page.viewport_size
        width = viewport["width"]
        height = viewport["height"]

        # Download button typically at top-right (95% width, 3% height)
        x_percent = 95
        y_percent = 3

        x_download = int(width * x_percent / 100)
        y_download = int(height * y_percent / 100)

        async with page.expect_download() as download_info:
            await page.mouse.click(x_download, y_download)

        download = await download_info.value
        await download.save_as(spath_pdf)

        if os.path.exists(spath_pdf):
            file_size_MB = os.path.getsize(spath_pdf) / 1e6
            logger.success(f"Downloaded: {spath_pdf} ({file_size_MB:.1f} MB)")
            return True

        return False

    except Exception as ee:
        logger.error(f"Chrome page download failed: {ee}")
        return False


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

        # Parameters
        PDF_URL = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"
        OUTPUT_PATH = "/tmp/hippocampal_ripples-by-stealth.pdf"

        # Main
        saved_path = await pdf_downloader.download_from_url(
            PDF_URL,
            output_path=OUTPUT_PATH,
        )

        if saved_path:
            logger.success(f"PDF downloaded successfully to: {saved_path}")
        else:
            logger.error("Failed to download PDF")

    asyncio.run(main_async())

# python -m scitex.scholar.download.ScholarPDFDownloader

# EOF
