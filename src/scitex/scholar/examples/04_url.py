#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 18:59:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_url.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/04_url.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from scitex.scholar import ScholarAuthManager, ScholarBrowserManager, ScholarURLFinder


async def main_async():
    # Initialize with authenticated browser context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Create URL handler
    url_finder = ScholarURLFinder(context)

    # Get all URLs for a paper
    doi = "10.1038/s41467-023-44201-2"
    urls = await url_finder.find_urls(
        doi=doi,
    )


asyncio.run(main_async())

# EOF
