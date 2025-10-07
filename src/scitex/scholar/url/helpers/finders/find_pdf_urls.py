#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 01:44:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/find_pdf_urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/find_pdf_urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
URL Finder Functions

Simple functions to find/extract URLs from web pages and metadata.
No classes, just functions that do one thing well.
"""

from typing import Dict, List

from playwright.async_api import Page

from scitex import logging
from scitex.scholar import ScholarConfig

from ._find_pdf_urls_by_direct_links import find_pdf_urls_by_direct_links
from ._find_pdf_urls_by_publisher_patterns import (
    find_pdf_urls_by_publisher_patterns,
)
from ._find_pdf_urls_by_view_button import find_pdf_urls_by_navigation
from ._find_pdf_urls_by_zotero_translators import (
    find_pdf_urls_by_zotero_translators,
)

logger = logging.getLogger(__name__)


async def find_pdf_urls(
    page: Page, base_url: str = None, config: ScholarConfig = None
) -> List[Dict]:
    """Find PDF URLs in a web page using multiple strategies without double counts."""
    from scitex.scholar.browser.utils import show_popup_message_async

    config = config or ScholarConfig()
    if base_url is None:
        base_url = page.url

    urls_pdf = []
    seen_urls = set()

    await show_popup_message_async(page, f"URL Finder: Finding PDFs at {base_url[:60]}...")

    # Strategy 1: Try Zotero translator FIRST (most reliable)
    await show_popup_message_async(page, "URL Finder: Trying Zotero translators...")
    translator_urls = await find_pdf_urls_by_zotero_translators(page, base_url)
    for url in translator_urls:
        if url not in seen_urls:
            seen_urls.add(url)
            urls_pdf.append({"url": url, "source": "zotero_translator"})

    if translator_urls:
        await show_popup_message_async(page, f"URL Finder: ✓ Zotero found {len(translator_urls)} URLs")
        await page.wait_for_timeout(1000)

    # Strategy 2: Find direct PDF links (fallback if no translator)
    await show_popup_message_async(page, "URL Finder: Checking direct PDF links...")
    direct_links = await find_pdf_urls_by_direct_links(page, config)
    for url in direct_links:
        if url not in seen_urls:
            seen_urls.add(url)
            urls_pdf.append({"url": url, "source": "direct_link"})

    if direct_links:
        await show_popup_message_async(page, f"URL Finder: ✓ Direct links found {len(direct_links)} URLs")
        await page.wait_for_timeout(1000)

    # Strategy 3: Try navigation to PDF URLs (for ScienceDirect etc)
    # This captures the final PDF URL after redirects
    if urls_pdf and any(
        domain in page.url.lower()
        for domain in ["sciencedirect.com", "cell.com", "elsevier.com"]
    ):
        await show_popup_message_async(page, "URL Finder: Navigating to resolve redirects...")
        # We have PDF URLs but they might be intermediate endpoints
        # Try to navigate to get the final URL
        navigation_urls = await find_pdf_urls_by_navigation(page, config)
        for url in navigation_urls:
            if url not in seen_urls:
                seen_urls.add(url)
                # Replace existing URL if it's an intermediate one
                for i, existing in enumerate(urls_pdf):
                    if (
                        "/pdfft?" in existing["url"]
                        and "pdf.sciencedirectassets.com" in url
                    ):
                        urls_pdf[i] = {"url": url, "source": "navigation"}
                        break
                else:
                    urls_pdf.append({"url": url, "source": "navigation"})

    # Strategy 4: Check for publisher patterns
    await show_popup_message_async(page, "URL Finder: Checking publisher patterns...")
    pattern_urls = find_pdf_urls_by_publisher_patterns(page, base_url)
    for url in pattern_urls:
        if url not in seen_urls:
            seen_urls.add(url)
            urls_pdf.append({"url": url, "source": "publisher_pattern"})

    if pattern_urls:
        await show_popup_message_async(page, f"URL Finder: ✓ Patterns found {len(pattern_urls)} URLs")
        await page.wait_for_timeout(1000)

    # Final result
    if len(urls_pdf):
        logger.success(
            f"Found {len(urls_pdf)} unique PDF URLs from {page.url}"
        )
        await show_popup_message_async(page, f"URL Finder: ✓ SUCCESS! Found {len(urls_pdf)} PDF URLs total")
        await page.wait_for_timeout(2000)
    else:
        logger.fail(f"Not found any PDF URLs from {page.url}")
        await show_popup_message_async(page, "URL Finder: ✗ No PDF URLs found")
        await page.wait_for_timeout(2000)

    source_counts = {}
    for item in urls_pdf:
        source = item["source"]
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in source_counts.items():
        logger.info(f"  - {source}: {count} URLs")

    return urls_pdf


# This downloaded PDF immediately
# https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf

# EOF
