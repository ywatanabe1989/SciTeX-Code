#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 20:02:05 (ywatanabe)"
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
from pathlib import Path
from typing import List, Union

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar import ScholarAuthManager, ScholarBrowserManager, ScholarURLFinder

logger = logging.getLogger(__name__)


class ScholarPDFDownloader:
    def __init__(
        self,
        chrome_profile_name: str = "system",
        browser_mode: str = "stealth",
    ):
        self.chrome_profile_name = chrome_profile_name
        self.browser_mode = browser_mode
        self.browser_manager = None
        self.context = None
        self.url_finder = None

    async def __aenter__(self):
        self.browser_manager = ScholarBrowserManager(
            chrome_profile_name=self.chrome_profile_name,
            browser_mode=self.browser_mode,
            auth_manager=ScholarAuthManager(),
        )
        browser, self.context = (
            await self.browser_manager.get_authenticated_browser_and_context_async()
        )
        self.url_finder = ScholarURLFinder(self.context)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    # async def download_from_url(self, pdf_url: str, output_path: Path) -> bool:
    #     # Extension
    #     if not str(output_path).endswith(".pdf"):
    #         output_path = Path(str(output_path) + ".pdf")

    #     # Download
    #     response = await self.context.request.get(pdf_url)

    #     # Save PDF contents
    #     if response.ok and response.headers.get("content-type", "").startswith(
    #         "application/pdf"
    #     ):
    #         content = await response.body()
    #         with open(output_path, "wb") as file_:
    #             file_.write(content)
    #         size_MiB = os.path.getsize(output_path) / 1024 / 1024
    #         logger.success(
    #             f"Downloaded: {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
    #         )
    #         return output_path
    #     logger.fail(f"Not downloaded {pdf_url} to {output_path}")
    #     return False

    async def download_from_url(
        self, pdf_url: str, output_path: Path, timeout_sec: int = 30
    ) -> bool:
        # Extension
        if not str(output_path).endswith(".pdf"):
            output_path = Path(str(output_path) + ".pdf")

        # Download with CAPTCHA wait
        start_time = asyncio.get_event_loop().time()

        while True:
            if asyncio.get_event_loop().time() - start_time > timeout_sec:
                logger.fail(
                    f"Timeout waiting for CAPTCHA resolution: {pdf_url}"
                )
                return False

            response = await self.context.request.get(pdf_url)
            content_type = response.headers.get("content-type", "")

            if "text/html" in content_type:
                logger.warning(
                    f"CAPTCHA detected for {pdf_url}. Waiting for extension to solve..."
                )
                await asyncio.sleep(5)
                continue

            if response.ok and content_type.startswith("application/pdf"):
                content = await response.body()
                with open(output_path, "wb") as file_:
                    file_.write(content)
                size_MiB = os.path.getsize(output_path) / 1024 / 1024
                logger.success(
                    f"Downloaded: {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
                )
                return output_path

            logger.fail(f"Not downloaded {pdf_url} to {output_path}")
            return False

    async def download_from_urls(
        self, pdf_urls: List[str], output_dir: Union[str, Path] = "/tmp/"
    ):
        output_paths = [
            Path(str(output_dir)) / os.path.basename(pdf_url)
            for pdf_url in pdf_urls
        ]

        saved_paths = []
        for ii_pdf, (url_pdf, output_path) in enumerate(
            zip(pdf_urls, output_paths)
        ):
            saved_path = await self.download_from_url(url_pdf, output_path)
            if saved_path:
                saved_paths.append(saved_path)
        return saved_paths

    async def download_from_doi(self, doi: str, output_dir: str = "/tmp/"):
        output_dir = Path(str(output_dir))
        urls = await self.url_finder.find_urls(doi=doi)
        pdf_urls = [url_pdf_entry["url"] for url_pdf_entry in urls["url_pdf"]]
        saved_paths = await self.download_from_urls(
            pdf_urls, output_dir=output_dir
        )
        return saved_paths


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from scitex.scholar import ScholarPDFDownloader

        # Parameters
        DOI = "10.1523/jneurosci.2929-12.2012"
        OUTPUT_DIR = "/tmp/"

        # Main
        async with ScholarPDFDownloader() as downloader:
            saved_paths = await downloader.download_from_doi(
                DOI, output_dir=OUTPUT_DIR
            )

    asyncio.run(main_async())

# python -m scholar.download.ScholarPDFDownloader

# EOF
