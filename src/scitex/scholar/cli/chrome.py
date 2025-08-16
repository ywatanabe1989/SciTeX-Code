#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 23:48:09 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/chrome.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/chrome.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio

from scitex import logging

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Launch browser with chrome extensions and academic authentication for manual configuration"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://google.com",
        help="URL to launch (default: https://google.com)",
    )
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=3600,
        help="Timeout in seconds (default: 3600)",
    )
    parser.add_argument(
        "--profile_name",
        type=str,
        default="system",
        help="Profile name to use (default: system)",
    )
    return parser


async def main_async():
    """Manually open ScholarBrowserManager with extensions and authentications."""
    from scitex.scholar.auth import ScholarAuthManager
    from scitex.scholar.browser import ScholarBrowserManager

    parser = create_parser()
    args = parser.parse_args()

    auth_manager = ScholarAuthManager()
    await auth_manager.ensure_authenticate_async()

    browser_manager = ScholarBrowserManager(
        chrome_profile_name=args.profile_name,
        browser_mode="interactive",
        auth_manager=auth_manager,
    )

    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )
    page = await context.new_page()

    logger.info(f"Navigating to {args.url}")
    try:
        # Add timeout and wait for network to be mostly idle
        await page.goto(
            args.url,
            wait_until="domcontentloaded",
            timeout=30000,
        )
        logger.success(f"Successfully loaded {args.url}")

        # Wait a bit more for dynamic content
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
            logger.success("Page fully loaded (network idle)")
        except Exception as e:
            logger.warn(f"Network not idle after 10s, continuing anyway: {e}")

    except Exception as e:
        logger.error(f"Failed to load {args.url}: {e}")
        logger.info("Browser will remain open for manual navigation")

    logger.info(
        f"Keeping browser open for {args.timeout_sec} seconds. Press Ctrl+C to close early."
    )

    try:
        await asyncio.sleep(args.timeout_sec)
        logger.info("Timeout reached, closing browser")
    except KeyboardInterrupt:
        logger.info("Interrupted by user, closing browser")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main_async())

# EOF
