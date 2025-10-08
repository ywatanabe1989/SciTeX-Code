#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 01:33:45 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/zotero_translators_python/ssrn.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/zotero_translators_python/ssrn.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Python implementation of SSRN Zotero translator.

Original JavaScript: /url/helpers/finders/zotero_translators/SSRN.js
Key logic: Line 124 - attr(doc, 'a.primary[data-abstract-id]', 'href')

This Python version bypasses the complex Zotero translator infrastructure
and directly extracts the PDF download link.
"""

import re
from typing import List

from playwright.async_api import Page
from .base import BaseTranslator


class SSRNTranslator(BaseTranslator):
    """SSRN PDF URL extractor - Python implementation."""

    LABEL = "SSRN"
    TARGET_PATTERN = r"^https?://(www|papers|hq)\.ssrn\.com/"

    @classmethod
    def matches_url(cls, url: str) -> bool:
        """Check if URL matches SSRN pattern.

        Args:
            url: URL to check

        Returns:
            True if URL matches SSRN paper page pattern
        """
        return bool(re.match(cls.TARGET_PATTERN, url))

    @classmethod
    async def extract_pdf_urls_async(cls, page: Page) -> List[str]:
        """Extract PDF URL from SSRN page.

        Args:
            page: Playwright page on SSRN paper page

        Returns:
            List containing PDF URL if found, empty list otherwise
        """
        # Wait for download button to load (up to 5 seconds)
        try:
            await page.wait_for_selector(
                "a.primary[data-abstract-id]", timeout=5000
            )
        except:
            pass  # Continue even if timeout

        # Extract the PDF URL using the same selector as SSRN.js line 124
        pdf_url = await page.evaluate(
            """
            () => {
                const link = document.querySelector('a.primary[data-abstract-id]');
                return link ? link.href : null;
            }
        """
        )

        return [pdf_url] if pdf_url else []


if __name__ == "__main__":
    import asyncio

    from playwright.async_api import async_playwright

    async def main():
        """Demonstration of SSRNTranslator usage."""
        # Example SSRN paper URL
        test_url = (
            "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5293145"
        )

        print(f"Testing SSRNTranslator with URL: {test_url}")
        print(f"URL matches pattern: {SSRNTranslator.matches_url(test_url)}\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            print("Navigating to SSRN page...")
            await page.goto(test_url)
            await page.wait_for_load_state("networkidle")

            print("Extracting PDF URLs...")
            pdf_urls = await SSRNTranslator.extract_pdf_urls_async(page)

            print(f"\nResults:")
            print(f"  Found {len(pdf_urls)} PDF URL(s)")
            for url in pdf_urls:
                print(f"  - {url}")

            await browser.close()

    asyncio.run(main())


# python -m scitex.scholar.url.helpers.finders.zotero_translators_python.ssrn
# pytest /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/zotero_translators_py/test_ssrn.py -v

# EOF
