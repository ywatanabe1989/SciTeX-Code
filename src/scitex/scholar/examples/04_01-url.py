#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:01:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/04_01-url.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarURLFinder capabilities for PDF discovery
- Shows URL resolution through multiple methods (DOI, OpenURL, Zotero translators)
- Validates authenticated browser context for URL finding
- Displays comprehensive URL finding results

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- DOI for URL resolution
- Authenticated browser context

Output:
- Console output with discovered URLs and their sources
- PDF URLs from multiple discovery methods
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_url_finding(doi: str = None, use_cache: bool = False) -> dict:
    """Demonstrate URL finding capabilities.
    
    Parameters
    ----------
    doi : str, optional
        DOI to find URLs for
    use_cache : bool, default=False
        Whether to use cached results
        
    Returns
    -------
    dict
        URL finding results
    """
    from scitex.scholar import ScholarAuthManager, ScholarBrowserManager, ScholarURLFinder
    
    search_doi = doi or "10.1016/j.smrv.2020.101353"
    
    print("🌐 Initializing authenticated browser context...")
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="interactive",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    print(f"🔍 Creating URL finder (cache: {use_cache})...")
    url_finder = ScholarURLFinder(context, use_cache=use_cache)

    print(f"🔗 Finding URLs for DOI: {search_doi}")
    urls = await url_finder.find_urls(doi=search_doi)

    print("📊 URL Finding Results:")
    print("=" * 50)
    pprint(urls)
    
    return urls


async def main_async(args) -> dict:
    """Main async function to demonstrate URL finding.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        URL finding results
    """
    print("🔗 Scholar URL Finder Demonstration")
    print("=" * 40)
    
    results = await demonstrate_url_finding(
        doi=args.doi,
        use_cache=not args.no_cache
    )
    
    print("✅ URL finding demonstration completed")
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
        description="Demonstrate Scholar URL finding capabilities"
    )
    parser.add_argument(
        "--doi", 
        "-d",
        type=str,
        default="10.1016/j.smrv.2020.101353",
        help="DOI to find URLs for (default: %(default)s)",
    )
    parser.add_argument(
        "--no_cache",
        "-nc",
        action="store_true",
        default=False,
        help="Disable caching for URL finder (default: %(default)s)",
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
