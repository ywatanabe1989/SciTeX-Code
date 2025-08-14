#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 20:06:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/_PDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/_PDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path
from typing import List, Optional

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser import BrowserManager
from scitex.scholar.metadata.urls import URLHandler

logger = logging.getLogger(__name__)


class PDFDownloader:
    def __init__(
        self,
        chrome_profile_name: str = "system",
        browser_mode: str = "stealth",
    ):
        self.chrome_profile_name = chrome_profile_name
        self.browser_mode = browser_mode
        self.browser_manager = None
        self.context = None
        self.url_handler = None

    async def __aenter__(self):
        self.browser_manager = BrowserManager(
            chrome_profile_name=self.chrome_profile_name,
            browser_mode=self.browser_mode,
            auth_manager=AuthenticationManager(),
        )
        browser, self.context = (
            await self.browser_manager.get_authenticated_browser_and_context_async()
        )
        self.url_handler = URLHandler(self.context)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser_manager:
            await self.browser_manager.close()

    async def download_pdf_direct(
        self, pdf_url: str, output_path: Path
    ) -> bool:
        response = await self.context.request.get(pdf_url)
        if response.ok and response.headers.get("content-type", "").startswith(
            "application/pdf"
        ):
            content = await response.body()
            with open(output_path, "wb") as file_:
                file_.write(content)
            size_MiB = os.path.getsize(output_path) / 1024 / 1024
            logger.success(
                f"Downloaded: {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
            )
            return True
        logger.fail(f"Not downloaded {pdf_url} to {output_path}")
        return False

    async def download_pdfs_direct(
        self, pdf_urls: List[str], output_paths: Optional[List[Path]] = None
    ):
        if output_paths is None:
            output_paths = [
                Path("/tmp/") / os.path.basename(pdf_url)
                for pdf_url in pdf_urls
            ]

        for ii_pdf, (url_pdf, output_path) in enumerate(
            zip(pdf_urls, output_paths)
        ):
            await self.download_pdf_direct(url_pdf, output_path)

    async def download_from_doi(
        self, doi: str, output_dir: Path = Path("/tmp/")
    ):
        urls = await self.url_handler.get_all_urls(doi=doi)
        pdf_urls = [url_pdf_entry["url"] for url_pdf_entry in urls["url_pdf"]]
        await self.download_pdfs_direct(pdf_urls)


if __name__ == "__main__":

    async def main(doi):
        async with PDFDownloader() as downloader:
            await downloader.download_from_doi(doi)

    import asyncio

    asyncio.run(main("10.1523/jneurosci.2929-12.2012"))

# EOF
