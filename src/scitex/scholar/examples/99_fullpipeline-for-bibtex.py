#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 23:29:37 (ywatanabe)"
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

    # Parameters
    USE_CACHE = True
    N_SAMPLES = None
    BROWSER_MODE = ["interactive", "stealth"][1]

    # Data
    BIBTEX_OPENACCESS = "./data/openaccess.bib"
    BIBTEX_PAYWALLED = "./data/paywalled.bib"
    BIBTEX_PAC = "./data/papers.bib"
    ENTRIES = parse_bibtex(BIBTEX_PAC)
    ENTRIES = np.random.permutation(ENTRIES)[:N_SAMPLES].tolist()
    QUERY_TITLES = [entry.get("title") for entry in ENTRIES]
    pprint(QUERY_TITLES)

    # Config
    config = ScholarConfig()

    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=BROWSER_MODE,
        auth_manager=ScholarAuthManager(config=config),
        config=config,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine(config=config, use_cache=USE_CACHE)
    url_finder = ScholarURLFinder(
        context,
        config=config,
        use_cache=True,
    )
    pdf_downloader = ScholarPDFDownloader(
        context, config=config, use_cache=USE_CACHE
    )

    # 1. Search for metadata
    print("----------------------------------------")
    print("1. Searching for metadata...")
    print("----------------------------------------")
    batched_metadata = await engine.search_batch_async(titles=QUERY_TITLES)
    pprint(batched_metadata)

    # 2. Find URLs
    print("----------------------------------------")
    print("2. Finding URLs...")
    print("----------------------------------------")
    dois = [
        metadata.get("id", {}).get("doi")
        for metadata in batched_metadata
        if metadata and metadata.get("id")
    ]
    batched_urls = await url_finder.find_urls_batch(dois=dois)
    pprint(batched_urls)

    # [pprint(urls.get("urls_pdf")) for urls in batched_urls]

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
        print(pdf_url)
        if pdf_url:

            # # This fails; I think the shared context between url_finder and pdf_downloader might cause problem
            browser_manager = ScholarBrowserManager(
                chrome_profile_name="system",
                # browser_mode=BROWSER_MODE,
                browser_mode="interactive",
                auth_manager=ScholarAuthManager(config=config),
                config=config,
            )
            browser, context = (
                await browser_manager.get_authenticated_browser_and_context_async()
            )

            pdf_downloader = ScholarPDFDownloader(
                context, config=config, use_cache=False
            )
            is_downloaded = await pdf_downloader.download_from_url(
                pdf_url, output_path
            )
            if is_downloaded:
                downloaded_paths.append(output_path)


asyncio.run(main_async())

# EOF
