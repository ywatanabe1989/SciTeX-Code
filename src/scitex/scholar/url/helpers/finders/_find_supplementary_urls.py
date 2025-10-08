#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 12:00:44 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/finders/find_supplementary_urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Dict, List

from playwright.async_api import Page

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.browser import show_popup_and_capture_async

logger = logging.getLogger(__name__)


async def find_supplementary_urls(
    page: Page, config: ScholarConfig = None
) -> List[Dict]:
    """Find supplementary material URLs in a web page."""
    await show_popup_and_capture_async(page, "Finding Supplementary URLs...")

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
