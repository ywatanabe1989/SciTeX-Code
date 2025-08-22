#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:23:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Executes full scholar pipeline for BibTeX processing
- Searches metadata for papers from BibTeX entries
- Finds URLs for academic papers using DOIs
- Downloads PDFs from discovered URLs with authentication
- Manages browser sessions with auth for paywalled content

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio, numpy, pathlib

Input:
- BibTeX files with academic paper entries
- Browser profile for authentication

Output:
- Downloaded PDF files to /tmp/scholar_pipeline/
- Metadata and URL information for papers
"""

"""Imports"""
import argparse
import asyncio
from pathlib import Path
from pprint import pprint

import numpy as _np

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def process_bibtex_entries(
    bibtex_path: str,
    n_samples: int = None,
    use_cache: bool = True,
    browser_mode: str = "stealth",
    output_dir: str = "/tmp/scholar_pipeline",
) -> dict:
    """Process BibTeX entries through full scholar pipeline.

    Parameters
    ----------
    bibtex_path : str
        Path to BibTeX file
    n_samples : int, optional
        Number of entries to process (None for all)
    use_cache : bool
        Whether to use cached results
    browser_mode : str
        Browser mode ('interactive' or 'stealth')
    output_dir : str
        Directory for downloaded PDFs

    Returns
    -------
    dict
        Results containing metadata, URLs, and download paths
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarConfig,
        ScholarEngine,
        ScholarPDFDownloader,
        ScholarURLFinder,
    )
    from scitex.scholar.utils import parse_bibtex

    # Parse BibTeX entries
    entries = parse_bibtex(bibtex_path)
    if n_samples:
        entries = _np.random.permutation(entries)[:n_samples].tolist()

    query_titles = [entry.get("title") for entry in entries]
    print(f"Processing {len(query_titles)} entries from {bibtex_path}")
    pprint(query_titles[:5])  # Show first 5 titles

    # Initialize configuration
    config = ScholarConfig()

    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=browser_mode,
        auth_manager=ScholarAuthManager(config=config),
        config=config,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine(config=config, use_cache=use_cache)
    url_finder = ScholarURLFinder(context, config=config, use_cache=use_cache)
    pdf_downloader = ScholarPDFDownloader(
        context, config=config, use_cache=False
    )

    results = {}

    # Step 1: Search for metadata
    print("=" * 50)
    print("1. Searching for metadata...")
    print("=" * 50)
    batched_metadata = await engine.search_batch_async(titles=query_titles)
    results["metadata"] = batched_metadata
    print(
        f"Found metadata for {len([m for m in batched_metadata if m])} papers"
    )

    # Step 2: Find URLs
    print("=" * 50)
    print("2. Finding URLs...")
    print("=" * 50)
    dois = [
        metadata.get("id", {}).get("doi")
        for metadata in batched_metadata
        if metadata and metadata.get("id")
    ]
    print(f"Extracted {len([d for d in dois if d])} DOIs")

    batched_urls = await url_finder.find_urls_batch(dois=dois)
    results["urls"] = batched_urls

    pdf_urls_found = sum(
        len(urls.get("urls_pdf", [])) for urls in batched_urls if urls
    )
    print(f"Found {pdf_urls_found} PDF URLs")

    # Step 3: Download PDFs
    print("=" * 50)
    print("3. Downloading PDFs...")
    print("=" * 50)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    batched_urls_pdf = [
        url_and_source["url"]
        for urls in batched_urls
        if urls
        for url_and_source in urls.get("urls_pdf", [])
    ]

    downloaded_paths = []

    for idx_url, pdf_url in enumerate(batched_urls_pdf):
        if not pdf_url:
            continue

        file_path = output_path / f"paper_{idx_url:02d}.pdf"
        print(f"Downloading {idx_url + 1}/{len(batched_urls_pdf)}: {pdf_url}")

        # Reinitialize browser context for each download
        browser_manager_download = ScholarBrowserManager(
            chrome_profile_name="system",
            browser_mode="interactive",  # Use interactive for downloads
            auth_manager=ScholarAuthManager(config=config),
            config=config,
        )
        browser_dl, context_dl = (
            await browser_manager_download.get_authenticated_browser_and_context_async()
        )
        pdf_downloader_dl = ScholarPDFDownloader(
            context_dl, config=config, use_cache=False
        )

        try:
            is_downloaded = await pdf_downloader_dl.download_from_url(
                pdf_url, file_path
            )
            if is_downloaded:
                downloaded_paths.append(str(file_path))
                print(f"✅ Downloaded: {file_path.name}")
            else:
                print(f"❌ Failed to download: {pdf_url}")
        except Exception as ee:
            print(f"❌ Error downloading {pdf_url}: {ee}")
        finally:
            # Clean up browser context
            await context_dl.close()
            await browser_dl.close()

    results["downloaded_paths"] = downloaded_paths

    print("=" * 50)
    print(f"Pipeline completed: {len(downloaded_paths)} PDFs downloaded")
    print("=" * 50)

    # Clean up main browser
    await context.close()
    await browser.close()

    return results


async def main_async(args) -> dict:
    """Main async function for BibTeX processing pipeline.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        Pipeline results
    """
    results = await process_bibtex_entries(
        bibtex_path=args.bibtex_path,
        n_samples=args.n_samples,
        use_cache=not args.no_cache,
        browser_mode=args.browser_mode,
        output_dir=args.output_dir,
    )

    print("Final Results Summary:")
    print(f"- Metadata entries: {len([m for m in results['metadata'] if m])}")
    print(f"- URL batches: {len(results['urls'])}")
    print(f"- Downloaded PDFs: {len(results['downloaded_paths'])}")

    return results


def main(args) -> int:
    """Main function wrapper for asyncio execution.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit status code
    """
    try:
        asyncio.run(main_async(args))
        return 0
    except Exception as ee:
        print(f"❌ Error: {ee}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process BibTeX entries through full scholar pipeline"
    )

    parser.add_argument(
        "--bibtex_path",
        "-b",
        type=str,
        default="./data/scholar/pac.bib",
        help="Path to BibTeX file (default: %(default)s)",
    )

    parser.add_argument(
        "--n_samples",
        "-n",
        type=int,
        default=None,
        help="Number of entries to process (default: all)",
    )

    parser.add_argument(
        "--no_cache",
        "-nc",
        action="store_true",
        default=False,
        help="Disable caching (default: %(default)s)",
    )

    parser.add_argument(
        "--browser_mode",
        "-m",
        type=str,
        choices=["interactive", "stealth"],
        default="stealth",
        help="Browser mode (default: %(default)s)",
    )

    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="/tmp/scholar_pipeline",
        help="Output directory for PDFs (default: %(default)s)",
    )

    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
