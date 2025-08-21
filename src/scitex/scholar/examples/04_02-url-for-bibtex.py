#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:01:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_02-url-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/04_02-url-for-bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates batch URL finding workflow for BibTeX files
- Shows integration of ScholarEngine and ScholarURLFinder
- Processes multiple papers from BibTeX format efficiently
- Validates complete metadata-to-URL pipeline

Dependencies:
- scripts:
  - None
- packages:
  - scitex, numpy, asyncio

Input:
- ./data/scholar/openaccess.bib
- ./data/scholar/paywalled.bib  
- ./data/scholar/pac.bib

Output:
- Console output showing metadata and URL finding progress
- Batch results for all papers in selected BibTeX file
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import numpy as np

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def process_bibtex_urls(
    bibtex_path: str,
    use_cache_engines: bool = True,
    use_cache_url_finder: bool = False,
    n_samples: int = None,
    browser_mode: str = "interactive"
) -> tuple:
    """Process BibTeX file to find URLs for all papers.
    
    Parameters
    ----------
    bibtex_path : str
        Path to BibTeX file
    use_cache_engines : bool, default=True
        Whether to use cache for search engines
    use_cache_url_finder : bool, default=False
        Whether to use cache for URL finder
    n_samples : int, optional
        Number of samples to process
    browser_mode : str, default="interactive"
        Browser mode for URL finding
        
    Returns
    -------
    tuple
        (metadata_results, url_results)
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarConfig,
        ScholarEngine,
        ScholarURLFinder,
    )
    from scitex.scholar.utils import parse_bibtex

    print(f"📚 Parsing BibTeX file: {bibtex_path}")
    entries = parse_bibtex(bibtex_path)
    
    if n_samples:
        entries = np.random.permutation(entries)[:n_samples].tolist()
        print(f"🔢 Sampling {n_samples} entries")
    
    query_titles = [entry.get("title") for entry in entries]
    print(f"📝 Found {len(query_titles)} paper titles")
    pprint(query_titles)

    print("⚙️ Initializing configuration...")
    config = ScholarConfig()

    print(f"🌐 Initializing browser ({browser_mode} mode)...")
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=browser_mode,
        auth_manager=ScholarAuthManager(config=config),
        config=config,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    print("🔧 Initializing components...")
    engine = ScholarEngine(config=config, use_cache=use_cache_engines)
    url_finder = ScholarURLFinder(
        context,
        config=config,
        use_cache=use_cache_url_finder,
    )

    print("=" * 50)
    print("🔍 1. Searching for metadata...")
    print("=" * 50)
    batched_metadata = await engine.search_batch_async(titles=query_titles)
    pprint(batched_metadata)

    print("=" * 50)
    print("🔗 2. Finding URLs...")
    print("=" * 50)
    dois = [
        metadata.get("id", {}).get("doi")
        for metadata in batched_metadata
        if metadata and metadata.get("id")
    ]
    batched_urls = await url_finder.find_urls_batch(dois=dois)
    pprint(batched_urls)
    
    return batched_metadata, batched_urls


async def main_async(args) -> tuple:
    """Main async function to process BibTeX URLs.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    tuple
        (metadata_results, url_results)
    """
    print("🔗 Scholar BibTeX URL Finding Demonstration")
    print("=" * 40)
    
    bibtex_files = [
        "./data/scholar/openaccess.bib",
        "./data/scholar/paywalled.bib", 
        "./data/scholar/pac.bib",
    ]
    
    selected_path = bibtex_files[args.bibtex_index]
    
    results = await process_bibtex_urls(
        bibtex_path=selected_path,
        use_cache_engines=not args.no_cache_engines,
        use_cache_url_finder=not args.no_cache_url_finder,
        n_samples=args.n_samples,
        browser_mode=args.browser_mode
    )
    
    print("✅ BibTeX URL finding demonstration completed")
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
        Exit status code (0 for success, 1 for failure)
    """
    try:
        asyncio.run(main_async(args))
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate batch URL finding for BibTeX files"
    )
    parser.add_argument(
        "--bibtex_index",
        "-b",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="BibTeX file index (0: openaccess, 1: paywalled, 2: pac) (default: %(default)s)",
    )
    parser.add_argument(
        "--n_samples",
        "-n",
        type=int,
        default=None,
        help="Number of samples to process (default: %(default)s)",
    )
    parser.add_argument(
        "--no_cache_engines",
        "-nce",
        action="store_true",
        default=False,
        help="Disable caching for search engines (default: %(default)s)",
    )
    parser.add_argument(
        "--no_cache_url_finder",
        "-ncu",
        action="store_true", 
        default=False,
        help="Disable caching for URL finder (default: %(default)s)",
    )
    parser.add_argument(
        "--browser_mode",
        "-bm",
        type=str,
        choices=["interactive", "stealth"],
        default="interactive",
        help="Browser mode (default: %(default)s)",
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
