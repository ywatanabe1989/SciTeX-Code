#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 21:17:40 (ywatanabe)"
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
from pathlib import Path

from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarEngine,
    ScholarPDFDownloader,
    ScholarURLFinder,
)


async def main_async():
    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=ScholarAuthManager(),
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine()
    url_finder = ScholarURLFinder(context)
    pdf_downloader = ScholarPDFDownloader(context)

    # Parameters
    QUERY_TITLE = "Hippocampal ripples down-regulate synapses"

    # 1. Search for metadata
    print("----------------------------------------")
    print("1. Searching for metadata...")
    print("----------------------------------------")
    metadata = await engine.search_async(title=QUERY_TITLE)
    doi = metadata.get("id").get("doi")

    # 2. Find URLs
    print("----------------------------------------")
    print("2. Finding URLs...")
    print("----------------------------------------")
    urls = await url_finder.find_urls(doi=doi)

    # 3. Download PDFs
    print("----------------------------------------")
    print("3. Downloading PDFs...")
    print("----------------------------------------")
    urls_pdf = [url_and_source["url"] for url_and_source in urls["urls_pdf"]]
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

    # ----------------------------------------
    # 1. Searching for metadata...
    # ----------------------------------------
    # INFO: Extension cleanup completed
    # Semantic_Scholar returned title: Hippocampal ripples down-regulate synapses
    # CrossRef returned title: Hippocampal ripples down-regulate synapses
    # OpenAlex returned title: Hippocampal ripples down-regulate synapses
    # PubMed returned title: Hippocampal ripples down-regulate synapses
    # ----------------------------------------
    # 2. Finding URLs...
    # ----------------------------------------
    # INFO: Resolving DOI: 10.1126/science.aao0702
    # INFO: Resolved to: https://www.science.org/doi/10.1126/science.aao0702
    # INFO: Finding resolver link for DOI: 10.1126/science.aao0702
    # WARNING: Could not find resolver link with any strategy
    # WARNING: Could not resolve OpenURL
    # SUCCESS: Loaded 681 Zotero translators
    # INFO: Executing Zotero translator: Atypon Journals
    # SUCCESS: Zotero Translator extracted 3 URLs
    # SUCCESS: Zotero translator found 3 PDF URLs
    # SUCCESS: Publisher-specific pattern matching found 1 PDF URLs
    # SUCCESS: Found 4 unique PDF URLs
    # INFO:   - zotero_translator: 3 URLs
    # INFO:   - direct_link: 1 URLs
    # ----------------------------------------
    # 3. Downloading PDFs...
    # ----------------------------------------
    # INFO: Trying method: From Response Body
    # INFO: Trying to download from response body
    # WARNING: Method failed: From Response Body
    # INFO: Trying method: Chrome PDF
    # INFO: PDF viewer detected
    # SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_00.pdf (1.2 MB)
    # SUCCESS: Downloaded via Chrome PDF Viewer
    # SUCCESS: Successfully downloaded using: Chrome PDF
    # INFO: Trying method: From Response Body
    # INFO: Trying to download from response body
    # WARNING: Method failed: From Response Body
    # INFO: Trying method: Chrome PDF
    # INFO: PDF viewer detected
    # SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_01.pdf (1.1 MB)
    # SUCCESS: Downloaded via Chrome PDF Viewer
    # SUCCESS: Successfully downloaded using: Chrome PDF
    # INFO: Trying method: From Response Body
    # INFO: Trying to download from response body
    # WARNING: Method failed: From Response Body
    # INFO: Trying method: Chrome PDF
    # INFO: PDF viewer detected
    # SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_02.pdf (1.5 MB)
    # SUCCESS: Downloaded via Chrome PDF Viewer
    # SUCCESS: Successfully downloaded using: Chrome PDF
    # INFO: Trying method: From Response Body
    # INFO: Trying to download from response body
    # WARNING: Method failed: From Response Body
    # INFO: Trying method: Chrome PDF
    # INFO: PDF viewer not detected
    # WARNING: Method failed: Chrome PDF
    # FAIL: All download methods failed for https://www.science.org/doi/pdf/10.1126/science.aao0702


asyncio.run(main_async())

# EOF
