#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 13:30:34 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_take_screenshot.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_take_screenshot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from datetime import datetime

from playwright.async_api import Page

from scitex import logging
from scitex.scholar import ScholarConfig

logger = logging.getLogger(__name__)


async def take_screenshot(
    page: Page,
    category: str,
    message: str,
    full_page: bool = False,
    config: ScholarConfig = None,
):
    """Take screenshot for debugging purposes."""
    try:
        config = config or ScholarConfig()
        screenshot_category_dir = config.get_screenshots_dir(category)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = (
            screenshot_category_dir / f"{message}-{timestamp}.png"
        )

        # Main
        await page.screenshot(
            path=str(screenshot_path), full_page=full_page, timeout=10_000
        )
        logger.success(f"Screenshot saved: {str(screenshot_path)}")
    except Exception as e:
        logger.fail(f"Screenshot not saved: {str(screenshot_path)}\n{str(e)}")

# EOF
