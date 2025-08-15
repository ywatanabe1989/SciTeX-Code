#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 18:08:22 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/06_download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path
from typing import List
from typing import Optional

from scitex import logging
from scitex.scholar.download import ScholarPDFDownloader
from playwright.async_api import BrowserContext

from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser import BrowserManager
from scitex.scholar.metadata.urls import URLHandler

logger = logging.getLogger(__name__)


async def download_pdf_direct(
    context: BrowserContext, pdf_url: str, output_path: Path
):
    """Download PDF using request context (bypasses Chrome PDF viewer)."""
    response = await context.request.get(pdf_url)
    if response.ok and response.headers.get("content-type", "").startswith(
        "application/pdf"
    ):
        content = await response.body()
        with open(output_path, "wb") as f:
            f.write(content)
        size_MiB = os.path.getsize(output_path) / 1024 / 1024
        logger.success(
            f"Downloaded: {pdf_url} to {output_path} ({size_MiB:.2f} MiB)"
        )
        return True
    logger.fail(f"Not downloaded {pdf_url} to {output_path}")
    return False


async def download_pdfs_direct(
    context: BrowserContext,
    pdf_urls: List[str],
    output_paths: Optional[List[Path]] = None,
):
    if output_paths is None:
        output_paths = [
            Path("/tmp/") / os.path.basename(pdf_url) for pdf_url in pdf_urls
        ]

    for ii_pdf, (url_pdf, output_path) in enumerate(
        zip(pdf_urls, output_paths)
    ):
        success = await download_pdf_direct(context, url_pdf, output_path)


await download_pdfs_direct(context, pdf_urls)


async def main(doi):
    pdf_downloader = ScholarPDFDownloader()
    await pdf_downloader.download_from_doi(doi)


import asyncio

asyncio.run(main("10.1523/jneurosci.2929-12.2012"))

# EOF
