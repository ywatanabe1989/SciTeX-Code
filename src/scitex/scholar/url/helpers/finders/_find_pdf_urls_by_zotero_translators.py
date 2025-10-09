#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 01:39:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/_find_pdf_urls_by_zotero_translators.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/_find_pdf_urls_by_zotero_translators.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Find PDF URLs using Python Zotero translators.

This module uses the zotero-translators-python package instead of running
JavaScript translators. It provides better performance, reliability, and
maintainability compared to the JavaScript-based approach.

Features:
- 100+ Python translators available
- No JavaScript execution overhead
- Better error handling
- Easier debugging
- Type safety

Usage:
    from scitex.scholar.url.helpers.finders import find_pdf_urls_by_zotero_translators

    pdf_urls = await find_pdf_urls_by_zotero_translators(page, url)
"""

from typing import List

from playwright.async_api import Page
from zotero_translators_python.core.registry import TranslatorRegistry

from scitex import logging
from scitex.browser import browser_logger

logger = logging.getLogger(__name__)


async def find_pdf_urls_by_zotero_translators(
    page: Page,
    url: str,
    func_name: str = "find_pdf_urls_by_zotero_translators",
) -> List[str]:
    """
    Find PDF URLs using Python-based Zotero translators.

    This is the preferred method over JavaScript translators due to:
    - Better performance (no JS eval overhead)
    - Better reliability (proper error handling)
    - Better maintainability (Python codebase)
    - Better debugging (Python stack traces)

    Args:
        page: Playwright page object with loaded content
        url: Current page URL to extract PDFs from

    Returns:
        List of PDF URLs extracted by matching translators
        Empty list if no translator matches or extraction fails

    Examples:
        >>> async with async_playwright() as p:
        ...     browser = await p.chromium.launch()
        ...     page = await browser.new_page()
        ...     await page.goto("https://www.nature.com/articles/nature12345")
        ...     pdf_urls = await find_pdf_urls_by_zotero_translators(page, page.url)
        ...     print(f"Found {len(pdf_urls)} PDF URLs")
    """
    try:
        await browser_logger.info(
            page,
            f"{func_name}: Finding PDF URLs using Python Zotero Translators...",
        )

        # Get registry of all available translators
        registry = TranslatorRegistry()

        # Find matching translator for this URL
        matching_translator = registry.get_translator_for_url(url)

        if not matching_translator:
            logger.debug(
                f"{func_name}: No Python translator matches URL: {url}"
            )
            return []

        # Try the matching translator
        all_pdf_urls = []
        try:
            logger.info(
                f"{func_name}: Trying {matching_translator.LABEL} translator..."
            )

            # Extract PDF URLs using the translator
            pdf_urls = await matching_translator.extract_pdf_urls_async(page)

            if pdf_urls:
                logger.success(
                    f"{func_name}: {matching_translator.LABEL} found {len(pdf_urls)} PDF URL(s)",
                    c="green",
                )
                for i_pdf, pdf_url in enumerate(pdf_urls, 1):
                    logger.debug(f"{func_name}  {i_pdf}. {pdf_url}")

                all_pdf_urls.extend(pdf_urls)
            else:
                logger.debug(
                    f"{func_name}: {matching_translator.LABEL} found no PDF URLs"
                )

        except Exception as e:
            logger.warning(
                f"{func_name}: {matching_translator.LABEL} extraction failed: {e}",
                c="yellow",
            )

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url_pdf in all_pdf_urls:
            if url_pdf not in seen:
                seen.add(url_pdf)
                unique_urls.append(url_pdf)

        if unique_urls:
            logger.info(
                f"{func_name}: Total: {len(unique_urls)} unique PDF URL(s) from Python translators",
                c="green",
            )
        else:
            logger.info(
                f"{func_name}: No PDF URLs found by Python translators"
            )

        return unique_urls

    except Exception as e:
        logger.warn(
            f"{func_name}: Error running Python Zotero translators: {e}",
        )
        return []

# EOF
