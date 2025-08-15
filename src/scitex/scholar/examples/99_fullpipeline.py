#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 20:12:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from scitex.logging import configure_logging
from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarEngine,
    ScholarPDFDownloader,
    ScholarURLFinder,
)

configure_logging("success")


async def main_async():
    # Parameters
    QUERY_TITLE = "Attention is All You Need"
    QUERY_TITLE = "Hippocampal ripples down-regulate synapses"
    OUTPUT_DIR = "/tmp/papers/"
    BROWSER_MODE = ["stealth", "interactive"][1]

    # Step 0: Instantiate classes
    print(f"\n{'-'*40}\nStep 0: Instantiate classes\n{'-'*40}")
    engine = ScholarEngine()
    browser_manager = ScholarBrowserManager(
        auth_manager=ScholarAuthManager(),
        browser_mode=BROWSER_MODE,
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )
    url_finder = ScholarURLFinder(context)
    pdf_downloader = ScholarPDFDownloader(context)

    # Step 1: Query -> Metadata with DOI
    print(f"\n{'-'*40}\nStep 1: Query -> Metadata with DOI\n{'-'*40}")
    metadata = await engine.search_async(title=QUERY_TITLE)
    doi = metadata.get("id").get("doi")

    # Step 2: Get URLs for the paper
    print(f"\n{'-'*40}\nStep 2: Get URLs for the paper\n{'-'*40}")
    urls = await url_finder.find_urls(doi=doi)

    __import__("ipdb").set_trace()

    # Step 3: Download PDF
    print(f"\n{'-'*40}\nStep 3: Download PDF\n{'-'*40}")
    paths = await pdf_downloader.download_from_doi(doi, output_dir=OUTPUT_DIR)

    print(paths)

    # await browser.close()


asyncio.run(main_async())

# EOF
