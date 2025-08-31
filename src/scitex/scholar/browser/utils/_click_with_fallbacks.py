#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 11:09:38 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_with_fallbacks.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_click_with_fallbacks.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Page

from scitex import log

logger = log.getLogger(__name__)


async def click_with_fallbacks(
    page: Page, selector: str, method: str = "auto"
) -> bool:
    """Click element using multiple fallback methods."""
    if method == "auto":
        methods_order = ["playwright", "force", "js"]
    else:
        methods_order = [method]

    methods = {
        "playwright": _click_with_playwright,
        "force": _click_with_force,
        "js": _click_with_js,
    }

    for method_name in methods_order:
        if method_name in methods:
            success = await methods[method_name](page, selector)
            if success:
                logger.debug(
                    f"Click successful with {method_name}: {selector}"
                )
                return True

    logger.error(f"All click methods failed for {selector}")
    return False


async def _click_with_playwright(page: Page, selector: str) -> bool:
    try:
        await page.click(selector, timeout=5000)
        return True
    except Exception:
        return False


async def _click_with_force(page: Page, selector: str) -> bool:
    try:
        await page.click(selector, force=True, timeout=5000)
        return True
    except Exception:
        return False


async def _click_with_js(page: Page, selector: str) -> bool:
    try:
        result = await page.evaluate(
            """(selector) => {
            const element = document.querySelector(selector);
            if (element) {
                element.click();
                return 'success';
            }
            return 'element not found';
        }""",
            selector,
        )
        return result == "success"
    except Exception:
        return False

# EOF
