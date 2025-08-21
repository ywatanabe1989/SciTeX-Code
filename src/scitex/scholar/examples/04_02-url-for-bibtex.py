#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 19:08:10 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_02-url-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/04_02-url-for-bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio


async def main_async():
    from pprint import pprint

    import numpy as np

    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarConfig,
        ScholarEngine,
        ScholarURLFinder,
    )
    from scitex.scholar.utils import parse_bibtex

    # Parameters
    USE_CACHE_ENGINES = True
    USE_CACHE_URL_FINDER = False
    N_SAMPLES = None
    BROWSER_MODE = ["interactive", "stealth"][0]

    # Data
    BITEX_PATH = [
        "./data/openaccess.bib",
        "./data/paywalled.bib",
        "./data/pac.bib",
    ][2]
    ENTRIES = parse_bibtex(BITEX_PATH)
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
    engine = ScholarEngine(config=config, use_cache=USE_CACHE_ENGINES)
    url_finder = ScholarURLFinder(
        context,
        config=config,
        use_cache=USE_CACHE_URL_FINDER,
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


asyncio.run(main_async())

# /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py | ctee.sh log-$(date +%Y%m%d_%H%M%S).log

# EOF
