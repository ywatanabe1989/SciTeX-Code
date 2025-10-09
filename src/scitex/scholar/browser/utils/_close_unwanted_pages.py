#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 23:10:17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/utils/_close_unwanted_pages.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_close_unwanted_pages.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

import asyncio

from playwright.async_api import BrowserContext, Page

from scitex import logging

logger = logging.getLogger(__name__)

# https://app.pbapi.xyz/dashboard?originSource=EXTENSION&onboarding=1


async def close_unwanted_pages(
    context: BrowserContext, delay_sec=1, max_attempts: int = 20
):
    """Close unwanted extension and blank pages while keeping at least one page open."""
    await asyncio.sleep(delay_sec)

    for attempt in range(max_attempts):
        try:
            # Get current pages first to avoid stale references
            current_pages = list(context.pages)

            unwanted_pages = [
                page
                for page in current_pages
                if (
                    "chrome-extension://" in page.url
                    or "pbapi.xyz" in page.url  # Changed to match both app.pbapi.xyz and pbapi.xyz
                    or "options.html" in page.url
                    # or page.url == "about:blank"
                )
            ]

            if not unwanted_pages:
                logger.debug("Extension cleanup completed")
                break

            # Ensure context stays alive - create new page BEFORE closing if needed
            if len(current_pages) == len(unwanted_pages):
                new_page = await context.new_page()
                logger.debug(f"Created new page to keep context alive: {new_page.url}")

            # Close unwanted pages
            closed_count = 0
            for page in unwanted_pages:
                try:
                    page_url = page.url  # Store URL before closing
                    await page.close()
                    closed_count += 1
                    logger.debug(f"Closed unwanted page: {page_url}")
                except Exception as e:
                    logger.debug(f"Failed to close page {page.url}: {e}")

            if closed_count > 0:
                logger.debug(f"Closed {closed_count} unwanted page(s) on attempt {attempt + 1}")

        except Exception as e:
            logger.debug(f"Cleanup attempt {attempt + 1} failed: {e}")

        await asyncio.sleep(2)

# EOF
