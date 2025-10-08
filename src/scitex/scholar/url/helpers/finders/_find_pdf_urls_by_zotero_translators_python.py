#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 03:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/_find_pdf_urls_by_zotero_translators_python.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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
    from scitex.scholar.url.helpers.finders import find_pdf_urls_by_zotero_translators_python

    pdf_urls = await find_pdf_urls_by_zotero_translators_python(page, url)
"""

from typing import List

from playwright.async_api import Page

from scitex import logging
from scitex.browser import show_popup_and_capture_async

try:
    from zotero_translators_python.core.registry import TranslatorRegistry
    PYTHON_TRANSLATORS_AVAILABLE = True
except ImportError:
    PYTHON_TRANSLATORS_AVAILABLE = False
    TranslatorRegistry = None

logger = logging.getLogger(__name__)


async def find_pdf_urls_by_zotero_translators_python(
    page: Page, url: str
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
        ...     pdf_urls = await find_pdf_urls_by_zotero_translators_python(page, page.url)
        ...     print(f"Found {len(pdf_urls)} PDF URLs")
    """
    if not PYTHON_TRANSLATORS_AVAILABLE:
        logger.warning(
            "zotero-translators-python not installed. "
            "Install with: pip install zotero-translators-python"
        )
        return []

    try:
        await show_popup_and_capture_async(
            page, "Finding PDF URLs using Python Zotero Translators..."
        )

        # Get registry of all available translators
        registry = TranslatorRegistry()

        # Find matching translator for this URL
        matching_translator = registry.get_translator_for_url(url)

        if not matching_translator:
            logger.debug(f"No Python translator matches URL: {url}")
            return []

        # Try the matching translator
        all_pdf_urls = []
        try:
            logger.info(f"Trying {matching_translator.LABEL} translator...")

            # Extract PDF URLs using the translator
            pdf_urls = await matching_translator.extract_pdf_urls_async(page)

            if pdf_urls:
                logger.success(
                    f"{matching_translator.LABEL} found {len(pdf_urls)} PDF URL(s)",
                    c="green"
                )
                for i, pdf_url in enumerate(pdf_urls, 1):
                    logger.debug(f"  {i}. {pdf_url}")

                all_pdf_urls.extend(pdf_urls)
            else:
                logger.debug(f"{matching_translator.LABEL} found no PDF URLs")

        except Exception as e:
            logger.warning(
                f"{matching_translator.LABEL} extraction failed: {e}",
                c="yellow"
            )

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in all_pdf_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        if unique_urls:
            logger.success(
                f"Total: {len(unique_urls)} unique PDF URL(s) from Python translators",
                c="green"
            )
        else:
            logger.info("No PDF URLs found by Python translators")

        return unique_urls

    except Exception as e:
        logger.error(f"Error running Python Zotero translators: {e}", c="red")
        return []


# EOF
