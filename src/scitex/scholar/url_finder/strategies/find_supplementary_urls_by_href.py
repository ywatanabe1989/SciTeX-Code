#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 01:19:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/strategies/find_supplementary_urls_by_href.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/strategies/find_supplementary_urls_by_href.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

from typing import Dict, List

from playwright.async_api import Page

from scitex import logging
from scitex.browser import browser_logger
from scitex.scholar import ScholarConfig

logger = logging.getLogger(__name__)


async def find_supplementary_urls_by_href(
    page: Page, config: ScholarConfig = None
) -> List[Dict]:
    """Find supplementary material URLs in a web page."""
    await browser_logger.debug(page, "Finding Supplementary URLs...")

    config = config or ScholarConfig()
    supplementary_selectors = config.resolve(
        "supplementary_selectors",
        default=[
            'a[href*="supplementary"]',
            'a[href*="supplement"]',
            'a[href*="additional"]',
        ],
    )

    try:
        supplementary = await page.evaluate(
            f"""() => {{
            const results = [];
            const selectors = {supplementary_selectors};
            const seen_urls = new Set();

            selectors.forEach(selector => {{
                document.querySelectorAll(selector).forEach(link => {{
                    if (link.href && !seen_urls.has(link.href)) {{
                        seen_urls.add(link.href);
                        results.push({{
                            url: link.href,
                            description: link.textContent.trim(),
                            source: 'href_pattern'
                        }});
                    }}
                }});
            }});
            return results;
        }}"""
        )
        return supplementary
    except Exception as e:
        logger.error(f"Error finding supplementary URLs: {e}")
        return []

# EOF
