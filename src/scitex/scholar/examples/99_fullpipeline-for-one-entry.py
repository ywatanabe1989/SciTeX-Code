#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:02:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-one-entry.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline-for-one-entry.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates complete Scholar workflow for single paper processing
- Shows end-to-end pipeline from search to PDF download
- Integrates all Scholar components in sequence
- Tests full automated academic paper acquisition workflow

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio, pathlib

Input:
- Paper title for search query
- Browser and caching configuration

Output:
- Downloaded PDF files in specified directory
- Console output showing pipeline progress
- Comprehensive metadata and URL information
"""

"""Imports"""
import argparse
import asyncio
from pathlib import Path
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def run_full_pipeline(
    title: str,
    use_cache: bool = False,
    browser_mode: str = "interactive",
    chrome_profile: str = "system",
    output_dir: str = "/tmp/scholar_pipeline"
) -> list:
    """Run complete Scholar pipeline for a single paper.
    
    Parameters
    ----------
    title : str
        Paper title to search for
    use_cache : bool, default=False
        Whether to use caching
    browser_mode : str, default="interactive"
        Browser mode for URL finding and downloading
    chrome_profile : str, default="system"
        Chrome profile to use
    output_dir : str, default="/tmp/scholar_pipeline"
        Directory to save downloaded PDFs
        
    Returns
    -------
    list
        List of downloaded PDF file paths
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarEngine,
        ScholarPDFDownloader,
        ScholarURLFinder,
    )

    print(f"🌐 Initializing browser ({browser_mode} mode, profile: {chrome_profile})...")
    browser_manager = ScholarBrowserManager(
        chrome_profile_name=chrome_profile,
        browser_mode=browser_mode,
        auth_manager=ScholarAuthManager(),
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    print("🔧 Initializing Scholar components...")
    engine = ScholarEngine()
    url_finder = ScholarURLFinder(context, use_cache=use_cache)
    pdf_downloader = ScholarPDFDownloader(context, use_cache=use_cache)

    print("=" * 50)
    print("🔍 1. Searching for metadata...")
    print("=" * 50)
    print(f"📝 Query title: {title}")
    
    metadata = await engine.search_async(title=title)
    doi = metadata.get("id", {}).get("doi")
    
    if not doi:
        print("❌ No DOI found for the paper")
        return []
    
    print(f"🆔 Found DOI: {doi}")

    print("=" * 50)
    print("🔗 2. Finding URLs...")
    print("=" * 50)
    
    urls = await url_finder.find_urls(doi=doi)
    print("📊 URL Finding Results:")
    pprint(urls)

    if not urls.get("urls_pdf"):
        print("❌ No PDF URLs found")
        return []

    print("=" * 50)
    print("📥 3. Downloading PDFs...")
    print("=" * 50)
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    urls_pdf = [url_info["url"] for url_info in urls["urls_pdf"]]
    print(f"📄 Found {len(urls_pdf)} PDF URLs to download")
    
    downloaded_paths = []
    for i_pdf_url, pdf_url in enumerate(urls_pdf):
        output_file = output_path / f"paper_{i_pdf_url:02d}.pdf"
        
        print(f"📥 Downloading PDF {i_pdf_url + 1}/{len(urls_pdf)}: {pdf_url}")
        
        saved_path = await pdf_downloader.download_from_url(pdf_url, output_file)
        
        if saved_path:
            downloaded_paths.append(saved_path)
            print(f"✅ Downloaded: {saved_path}")
        else:
            print(f"❌ Failed to download: {pdf_url}")
    
    print(f"\n📊 Download Summary: {len(downloaded_paths)}/{len(urls_pdf)} PDFs downloaded")
    return downloaded_paths


async def main_async(args) -> list:
    """Main async function to run the full pipeline.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    list
        List of downloaded PDF paths
    """
    print("🚀 Scholar Full Pipeline Demonstration")
    print("=" * 40)
    
    results = await run_full_pipeline(
        title=args.title,
        use_cache=args.use_cache,
        browser_mode=args.browser_mode,
        chrome_profile=args.chrome_profile,
        output_dir=args.output_dir
    )
    
    if results:
        print("✅ Full pipeline completed successfully")
        print(f"📁 Downloaded files: {results}")
    else:
        print("❌ No files were downloaded")
    
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
        results = asyncio.run(main_async(args))
        return 0 if results else 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run complete Scholar pipeline for single paper processing"
    )
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        default="Hippocampal ripples down-regulate synapses",
        help="Query title for paper search (default: %(default)s)",
    )
    parser.add_argument(
        "--use_cache",
        "-c",
        action="store_true",
        help="Use caching for URL finder and PDF downloader (default: %(default)s)",
    )
    parser.add_argument(
        "--browser_mode",
        "-bm",
        type=str,
        default="interactive",
        choices=["interactive", "stealth"],
        help="Browser mode (default: %(default)s)",
    )
    parser.add_argument(
        "--chrome_profile",
        "-cp",
        type=str,
        default="system",
        help="Chrome profile name (default: %(default)s)",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="/tmp/scholar_pipeline",
        help="Output directory for downloaded PDFs (default: %(default)s)",
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
