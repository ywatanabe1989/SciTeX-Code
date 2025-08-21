#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 05:47:12 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio


async def main_async():
    from pathlib import Path
    from pprint import pprint

    import numpy as np

    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarConfig,
        ScholarEngine,
        ScholarPDFDownloader,
        ScholarURLFinder,
    )
    from scitex.scholar.utils import parse_bibtex

    # Data
    N_SAMPLES = 5
    BIBTEX_OPENACCESS = "./data/scholar/openaccess.bib"
    BIBTEX_PAYWALLED = "./data/scholar/openaccess.bib"
    ENTRIES = parse_bibtex(BIBTEX_OPENACCESS) + parse_bibtex(BIBTEX_PAYWALLED)
    ENTRIES = np.random.permutation(ENTRIES)[:N_SAMPLES].tolist()
    QUERY_TITLES = [entry.get("title") for entry in ENTRIES]
    pprint(QUERY_TITLES)

    # Config
    config = ScholarConfig()

    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        # browser_mode="stealth",
        browser_mode="interactive",
        auth_manager=ScholarAuthManager(config=config),
        config=config,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine(config=config)
    url_finder = ScholarURLFinder(context, config=config)
    pdf_downloader = ScholarPDFDownloader(context, config=config)

    # 1. Search for metadata
    print("----------------------------------------")
    print("1. Searching for metadata...")
    print("----------------------------------------")
    batched_metadata = await engine.search_batch_async(titles=QUERY_TITLES)
    pprint(batched_metadata)
    dois = [
        metadata.get("id", {}).get("doi")
        for metadata in batched_metadata
        if metadata and metadata.get("id")
    ]
    pprint(dois)

    # 2. Find URLs
    print("----------------------------------------")
    print("2. Finding URLs...")
    print("----------------------------------------")
    batched_urls = await url_finder.find_urls_batch(dois=dois)
    pprint(batched_urls)

    # 3. Download PDFs
    print("----------------------------------------")
    print("3. Downloading PDFs...")
    print("----------------------------------------")

    batched_urls_pdf = [
        url_and_source["url"]
        for urls in batched_urls
        for url_and_source in urls.get("urls_pdf", [])
    ]

    downloaded_paths = []
    for idx_url, pdf_url in enumerate(batched_urls_pdf):
        output_path = (
            Path("/tmp/scholar_pipeline") / f"paper_{idx_url:02d}.pdf"
        )
        __import__("ipdb").set_trace()
        is_downloaded = await pdf_downloader.download_from_url(
            pdf_url, output_path
        )
        if is_downloaded:
            downloaded_paths.append(output_path)


asyncio.run(main_async())

# EOF
