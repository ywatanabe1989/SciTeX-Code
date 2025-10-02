#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:21:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_find_and_download.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Integrated example: Find PDF URL and download immediately.

This demonstrates the complete workflow:
1. Find PDF URL with navigation to get authenticated URL
2. Download PDF immediately in the same browser context
3. Avoid session expiration issues
"""

import argparse
import asyncio
from pathlib import Path

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


async def find_and_download_pdf(
    doi: str, output_dir: str = "/tmp", browser_mode: str = "stealth"
) -> Path:
    """
    Find PDF URL and download it immediately in the same session.

    This avoids the redirect issue when trying to use authenticated URLs later.
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarPDFDownloader,
        ScholarURLFinder,
    )

    logger.info(f"Processing DOI: {doi}")

    # Initialize browser with authentication
    logger.info(f"Initializing browser ({browser_mode} mode)...")
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode=browser_mode,
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Find PDF URLs
    logger.info("Finding PDF URLs...")
    url_finder = ScholarURLFinder(context, use_cache=False)
    urls = await url_finder.find_urls(doi=doi)

    # Extract PDF URLs - handle both old and new structure
    pdf_urls = urls.get("urls_pdf", urls.get("url_pdf", []))
    if not pdf_urls:
        logger.error(f"No PDF URLs found for DOI: {doi}")
        return None

    # Get the best PDF URL (prefer navigation source for authenticated URLs)
    best_pdf_url = None
    for pdf_info in pdf_urls:
        if isinstance(pdf_info, dict):
            if pdf_info.get("source") == "navigation":
                best_pdf_url = pdf_info.get("url")
                break
        elif isinstance(pdf_info, str):
            # Handle simple string URLs
            best_pdf_url = pdf_info
            break

    if not best_pdf_url and pdf_urls:
        # Fallback to first available PDF URL
        if isinstance(pdf_urls[0], dict):
            best_pdf_url = pdf_urls[0].get("url")
        else:
            best_pdf_url = pdf_urls[0]

    logger.info(f"Found PDF URL: {best_pdf_url[:80]}...")

    # Download PDF immediately in the same context
    logger.info("Downloading PDF...")
    pdf_downloader = ScholarPDFDownloader(context)

    # Create output filename from DOI
    safe_filename = doi.replace("/", "_").replace(".", "_") + ".pdf"
    output_path = Path(output_dir) / safe_filename

    saved_path = await pdf_downloader.download_from_url(
        best_pdf_url,
        output_path=str(output_path),
    )

    if saved_path:
        logger.success(f"Downloaded PDF to: {saved_path}")
    else:
        logger.error("Failed to download PDF")

    # Clean up
    await browser.close()

    return saved_path


async def main_async(args):
    """Main async function."""
    logger.info("Scholar Find & Download Demonstration")
    logger.info("=" * 40)

    result = await find_and_download_pdf(
        doi=args.doi,
        output_dir=args.output_dir,
        browser_mode=args.browser_mode,
    )

    if result:
        logger.success(f"Success! PDF saved to: {result}")
    else:
        logger.error("Failed to download PDF")

    return result


def main(args):
    """Main function wrapper."""
    try:
        result = asyncio.run(main_async(args))
        return 0 if result else 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Find and download PDF in one integrated session"
    )
    parser.add_argument(
        "--doi",
        "-d",
        type=str,
        default="10.1016/j.neubiorev.2020.07.005",
        help="DOI to find and download (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="/tmp",
        help="Output directory for PDF (default: %(default)s)",
    )
    parser.add_argument(
        "--browser-mode",
        "-bm",
        type=str,
        choices=["interactive", "stealth"],
        default="stealth",
        help="Browser mode (default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main():
    """Initialize scitex framework and run."""
    global CONFIG, CC, sys

    import sys

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
        sys,
        None,
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

# /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_find_and_download.py --doi 10.1016/j.neubiorev.2020.07.005 -bm interactive

# EOF
