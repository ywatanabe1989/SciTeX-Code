#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 09:59:56 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-one-entry.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline-for-one-entry.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio
from pathlib import Path

from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarEngine,
    ScholarPDFDownloader,
    ScholarURLFinder,
)


async def main_async():
    parser = argparse.ArgumentParser(
        description="Full pipeline for searching and downloading academic papers"
    )
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        default="Hippocampal ripples down-regulate synapses",
        help="Query title for paper search",
    )
    parser.add_argument(
        "--use_cache",
        action="store_true",
        help="Use caching",
    )
    parser.add_argument(
        "--browser-mode",
        default="interactive",
        choices=["interactive", "stealth"],
        help="Browser mode",
    )
    parser.add_argument(
        "--chrome-profile",
        default="system",
        help="Chrome profile name",
    )

    args = parser.parse_args()

    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name=args.chrome_profile,
        browser_mode=args.browser_mode,
        auth_manager=ScholarAuthManager(),
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine()
    url_finder = ScholarURLFinder(context, use_cache=args.use_cache)
    pdf_downloader = ScholarPDFDownloader(context, use_cache=args.use_cache)

    # 1. Search for metadata
    print("----------------------------------------")
    print("1. Searching for metadata...")
    print("----------------------------------------")
    metadata = await engine.search_async(title=args.title)
    doi = metadata.get("id").get("doi")

    # 2. Find URLs
    print("----------------------------------------")
    print("2. Finding URLs...")
    print("----------------------------------------")
    urls = await url_finder.find_urls(doi=doi)
    from pprint import pprint

    pprint(urls)

    # 3. Download PDFs
    print("----------------------------------------")
    print("3. Downloading PDFs...")
    print("----------------------------------------")
    urls_pdf = [url_and_source["url"] for url_and_source in urls["urls_pdf"]]
    __import__("ipdb").set_trace()
    downloaded_paths = []
    for i_pdf_url, pdf_url in enumerate(urls_pdf):
        output_path = (
            Path("/tmp/scholar_pipeline") / f"paper_{i_pdf_url:02d}.pdf"
        )
        is_downloaded = await pdf_downloader.download_from_url(
            pdf_url, output_path
        )
        if is_downloaded:
            downloaded_paths.append(output_path)


asyncio.run(main_async())

# /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-one-entry.py

# EOF
