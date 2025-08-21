#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:00:58 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/02_browser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/02_browser.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarBrowserManager usage with authentication
- Shows browser initialization and basic navigation
- Validates authenticated browser context creation

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Authentication credentials from environment or cache
- Chrome profile configuration

Output:
- Console output showing browser initialization status
- Opens browser window navigating to scitex.ai
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_browser_usage() -> bool:
    """Demonstrate browser manager with authentication.
    
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    from scitex.scholar.auth import ScholarAuthManager
    from scitex.scholar.browser import ScholarBrowserManager
    
    print("🌐 Initializing browser with authentication...")
    
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="interactive",
        auth_manager=ScholarAuthManager(),
    )

    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    page = await context.new_page()
    
    print("📖 Navigating to scitex.ai...")
    await page.goto("https://scitex.ai")
    
    print("⏳ Waiting 10 seconds for demonstration...")
    await asyncio.sleep(10)
    
    print("✅ Browser demonstration completed")
    return True


async def main_async(args) -> bool:
    """Main async function to handle browser demonstration.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    bool
        Success status
    """
    print("🌐 Scholar Browser Manager Example")
    print("=" * 40)

    success = await demonstrate_browser_usage()
    
    if success:
        print("✅ Browser workflow completed successfully")
    else:
        print("❌ Browser workflow failed")

    return success


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
    success = asyncio.run(main_async(args))
    return 0 if success else 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar browser management workflow"
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
