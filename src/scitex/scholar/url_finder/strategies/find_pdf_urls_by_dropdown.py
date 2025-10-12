#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/strategies/find_pdf_urls_by_dropdown.py
# ----------------------------------------
"""Find PDF URLs from dropdown/button elements."""

from typing import List
from playwright.async_api import Page
from scitex import logging
from scitex.browser.debugging import browser_logger
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


async def find_pdf_urls_by_dropdown(
    page: Page,
    url: str = None,
    config: ScholarConfig = None,
    func_name: str = "find_pdf_urls_by_dropdown",
) -> List[str]:
    """
    Find PDF URLs from dropdown buttons and download elements.

    Args:
        page: Playwright page object
        url: Current page URL (unused, for signature consistency)
        config: ScholarConfig instance
        func_name: Function name for logging

    Returns:
        List of PDF URLs found
    """
    try:
        config = config or ScholarConfig()

        dropdown_selectors = config.resolve(
            "dropdown_selectors",
            default=[
                'button:has-text("Download PDF")',
                'button:has-text("PDF")',
                'a:has-text("Download PDF")',
                ".pdf-download-button",
            ],
        )

        pdf_urls = []
        for selector in dropdown_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    href = await element.get_attribute("href")
                    if href and "pdf" in href.lower():
                        pdf_urls.append(href)
            except:
                continue

        if pdf_urls:
            logger.debug(f"{func_name}: Found {len(pdf_urls)} URLs from dropdowns")

        return pdf_urls
    except Exception as e:
        logger.debug(f"{func_name}: {str(e)}")
        return []


# EOF
