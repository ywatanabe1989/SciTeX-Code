#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:40:50 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_fill_with_fallbacks.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


async def fill_with_fallbacks(
    page: Page, selector: str, value: str, method: str = "auto"
) -> bool:
    """Fill element using multiple fallback methods."""
    if method == "auto":
        methods_order = ["playwright", "type", "js"]
    else:
        methods_order = [method]

    methods = {
        "playwright": _fill_with_playwright,
        "type": _fill_with_typing,
        "js": _fill_with_js,
    }

    for method_name in methods_order:
        if method_name in methods:
            success = await methods[method_name](page, selector, value)
            if success:
                logger.debug(f"Fill successful with {method_name}: {selector}")
                return True

    logger.error(f"All fill methods failed for {selector}")
    return False


async def _fill_with_playwright(page: Page, selector: str, value: str) -> bool:
    try:
        await page.fill(selector, value, timeout=5000)
        return True
    except Exception:
        return False


async def _fill_with_typing(page: Page, selector: str, value: str) -> bool:
    try:
        await page.click(selector, timeout=5000)
        await page.keyboard.press("Control+a")
        await page.type(selector, value, delay=50)
        return True
    except Exception:
        return False


async def _fill_with_js(page: Page, selector: str, value: str) -> bool:
    try:
        result = await page.evaluate(
            """(selector, value) => {
            const element = document.querySelector(selector);
            if (element) {
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                return 'success';
            }
            return 'element not found';
        }""",
            selector,
            value,
        )
        return result == "success"
    except Exception:
        return False

# EOF
