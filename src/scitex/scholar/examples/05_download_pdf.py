#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 02:53:53 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/05_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/05_download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio


async def main_async():
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarPDFDownloader,
    )

    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=ScholarAuthManager(),
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


asyncio.run(main_async())

# EOF
