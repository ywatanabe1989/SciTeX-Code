#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 13:53:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/05_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/05_download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarPDFDownloader,
    ScholarURLFinder,
)


async def main_async():
    # Initialize with authenticated browser context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        # browser_mode="stealth",
        browser_mode="interactive",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )
    pdf_downloader = ScholarPDFDownloader(context)

    # Parameters
    OPENURL_RESOLVED_URL = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"
    OUTPUT_PATH = "/tmp/science.pdf"

    result = await pdf_downloader.download_from_url(
        OPENURL_RESOLVED_URL, OUTPUT_PATH
    )

    # Close browser context
    await context.close()
    await browser.close()

    return result

    # DOI = "10.1523/jneurosci.2929-12.2012"
    # OUTPUT_DIR = "/tmp/"

    # await pdf_downloader.download_from_doi(DOI, output_dir=OUTPUT_DIR)


import asyncio
import sys

try:
    result = asyncio.run(main_async())
    if result:
        print(f"Success! PDF downloaded to: {result}")
        sys.exit(0)
    else:
        print("Failed to download PDF")
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# EOF
