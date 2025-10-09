#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 04:13:32 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/interaction/fill_with_fallbacks.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/interaction/fill_with_fallbacks.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


# 1. Main entry point
# ---------------------------------------
async def fill_with_fallbacks_async(
    page: Page, selector: str, value: str, method: str = "auto", verbose: bool = False
) -> bool:
    """Fill element using multiple fallback methods.

    Args:
        page: Playwright page object
        selector: CSS selector for the element
        value: Value to fill
        method: Fill method ("auto", "playwright", "type", "js")
        verbose: Enable visual feedback via popup system (default False)

    Returns:
        bool: True if fill successful, False otherwise
    """
    from ..debugging import browser_logger

    if method == "auto":
        methods_order = ["playwright", "type", "js"]
    else:
        methods_order = [method]

    methods = {
        "playwright": _fill_with_playwright,
        "type": _fill_with_typing,
        "js": _fill_with_js,
    }

    if verbose:
        await browser_logger.info(
            page, f"Attempting fill: {selector}", verbose=verbose
        )

    for method_name in methods_order:
        if method_name in methods:
            success = await methods[method_name](page, selector, value)
            if success:
                logger.debug(f"Fill successful with {method_name}: {selector}")
                if verbose:
                    await browser_logger.info(
                        page, f"✓ Fill successful ({method_name}): {selector}", verbose=verbose
                    )
                return True

    logger.error(f"All fill methods failed for {selector}")
    if verbose:
        await browser_logger.info(
            page, f"✗ All fill methods failed: {selector}", verbose=verbose
        )
    return False


# 2. Helper functions
# ---------------------------------------
async def _fill_with_playwright(page: Page, selector: str, value: str) -> bool:
    try:
        await page.fill(selector, value, timeout=5000)
        return True
    except Exception:
        return False


async def _fill_with_typing(page: Page, selector: str, value: str) -> bool:
    try:
        await page.click(selector, timeout=5000)
        await page.keyboard.press("Control+a")
        await page.type(selector, value, delay=50)
        return True
    except Exception:
        return False


async def _fill_with_js(page: Page, selector: str, value: str) -> bool:
    try:
        result = await page.evaluate(
            """(selector, value) => {
                const element = document.querySelector(selector);
                if (element) {
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'success';
                }
                return 'element not found';
            }""",
            selector,
            value,
        )
        return result == "success"
    except Exception:
        return False


def main(args):
    """Demonstrate fill_with_fallbacks functionality."""
    import asyncio
    from playwright.async_api import async_playwright
    from ..debugging import browser_logger

    async def demo():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await browser_logger.info(
                page, "Fill with Fallbacks: Starting demo", verbose=True
            )

            # Navigate to a page with input fields
            await page.goto("https://www.google.com", timeout=30000)

            await browser_logger.info(
                page, "Testing fill with fallbacks...", verbose=True
            )

            # Try to fill the search box
            success = await fill_with_fallbacks_async(
                page,
                "textarea[name='q']",  # Google search box
                "SciTeX browser automation",
                verbose=True
            )

            if success:
                logger.success("Fill demonstration completed successfully")
            else:
                logger.warning("Fill demonstration: no input element found")

            await browser_logger.info(
                page, "✓ Demo complete", verbose=True
            )

            await asyncio.sleep(2)
            await browser.close()

    asyncio.run(demo())
    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description="Fill with fallbacks demo")
    return parser.parse_args()


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
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

# python -m scitex.browser.interaction.fill_with_fallbacks

# EOF
