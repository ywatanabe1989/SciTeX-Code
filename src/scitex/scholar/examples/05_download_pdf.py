#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 07:38:41 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/05_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/05_download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarPDFDownloader capabilities
- Shows authenticated PDF downloading with multiple fallback methods
- Validates stealth browser integration for protected content
- Tests PDF download with Chrome PDF viewer detection

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- PDF URL to download from
- Output path for downloaded file

Output:
- Downloaded PDF file at specified location
- Console output showing download progress and method used
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_pdf_download(
    pdf_url: str = None, output_path: str = None, browser_mode: str = "stealth"
) -> str:
    """Demonstrate PDF downloading capabilities.

    Parameters
    ----------
    pdf_url : str, optional
        URL of PDF to download
    output_path : str, optional
        Path to save downloaded PDF
    browser_mode : str, default="stealth"
        Browser mode for downloading

    Returns
    -------
    str
        Path to downloaded PDF file
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarPDFDownloader,
    )

    # Default parameters
    default_url = "https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf"
    default_output = "/tmp/hippocampal_ripples-downloaded.pdf"

    download_url = pdf_url or default_url
    save_path = output_path or default_output

    print(f"🌐 Initializing browser manager ({browser_mode} mode)...")
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=browser_mode,
        auth_manager=ScholarAuthManager(),
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    print("📥 Initializing PDF downloader...")
    pdf_downloader = ScholarPDFDownloader(context)

    print(f"📄 Downloading PDF from: {download_url}")
    print(f"💾 Saving to: {save_path}")

    saved_path = await pdf_downloader.download_from_url(
        download_url,
        output_path=save_path,
    )

    if saved_path:
        print(f"✅ Successfully downloaded: {saved_path}")
    else:
        print("❌ Download failed")

    return saved_path


async def main_async(args) -> str:
    """Main async function to demonstrate PDF downloading.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    str
        Path to downloaded file
    """
    print("📥 Scholar PDF Downloader Demonstration")
    print("=" * 40)

    result = await demonstrate_pdf_download(
        pdf_url=args.pdf_url,
        output_path=args.output_path,
        browser_mode=args.browser_mode,
    )

    print("✅ PDF download demonstration completed")
    return result


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
        result = asyncio.run(main_async(args))
        return 0 if result else 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar PDF downloading capabilities"
    )
    parser.add_argument(
        "--pdf_url",
        "-u",
        type=str,
        default="https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf",
        help="PDF URL to download (default: %(default)s)",
    )
    parser.add_argument(
        "--output_path",
        "-o",
        type=str,
        default="/tmp/hippocampal_ripples-downloaded.pdf",
        help="Output path for downloaded PDF (default: %(default)s)",
    )
    parser.add_argument(
        "--browser_mode",
        "-bm",
        type=str,
        choices=["interactive", "stealth"],
        default="stealth",
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
