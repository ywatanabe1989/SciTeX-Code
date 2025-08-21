#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:00:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_close_unwanted_pages.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_close_unwanted_pages.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from playwright.async_api import BrowserContext, Page

from scitex import log

logger = log.getLogger(__name__)


async def close_unwanted_pages(
    context: BrowserContext, max_attempts: int = 20
):
    """Close unwanted extension and blank pages while keeping at least one page open."""
    await asyncio.sleep(1)

    for attempt in range(max_attempts):
        try:
            unwanted_pages = [
                page
                for page in context.pages
                if (
                    "chrome-extension://" in page.url
                    or "app.pbapi.xyz" in page.url
                    or "options.html" in page.url
                    # or page.url == "about:blank"
                )
            ]

            if not unwanted_pages:
                logger.debug("Extension cleanup completed")
                break

            # Ensure context stays alive
            if len(context.pages) == len(unwanted_pages):
                await context.new_page()

            for page in unwanted_pages:
                try:
                    await page.close()
                    logger.debug(f"Closed unwanted page: {page.url}")
                except Exception as e:
                    logger.debug(f"Failed to close page {page.url}: {e}")

        except Exception as e:
            logger.debug(f"Cleanup attempt {attempt + 1} failed: {e}")

        await asyncio.sleep(2)

# EOF
