#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 12:00:03 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/finders/find_pdf_urls_by_zotero_translators.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List

from playwright.async_api import Page

from scitex import logging
from scitex.scholar.browser.utils import show_popup_message_async

from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner

logger = logging.getLogger(__name__)


async def find_pdf_urls_by_zotero_translators(
    page: Page, url: str
) -> List[str]:
    """
    Find PDF URLs using Zotero translator (FIRST strategy - most reliable).

    Args:
        page: Playwright page object with loaded content
        url: Current page URL

    Returns:
        List of PDF URLs extracted by Zotero translator
    """
    try:
        await show_popup_message_async(
            page, "Finding PDF URLs by Zotero Translators..."
        )

        runner = ZoteroTranslatorRunner()

        # Execute translator if one matches this URL
        urls_pdf = await runner.extract_urls_pdf_async(page)

        if urls_pdf:
            logger.info(f"Zotero translator found {len(urls_pdf)} PDF URLs")
            for pdf_url in urls_pdf:
                logger.debug(f"  - {pdf_url}")

        return urls_pdf

    except Exception as e:
        logger.error(f"Error running Zotero translator: {e}")
        return []

# EOF
