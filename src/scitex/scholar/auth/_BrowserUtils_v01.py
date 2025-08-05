#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 01:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_BrowserUtils.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_BrowserUtils.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Shared browser utilities to avoid circular dependencies.

This module contains browser automation utilities that can be used
by both BrowserAuthenticator and SSO automators without creating
circular dependencies.
"""

from playwright.async_api import Page, TimeoutError
from scitex import logging

logger = logging.getLogger(__name__)


class BrowserUtils:
    """Shared browser automation utilities."""

    @staticmethod
    async def reliable_fill_async(page: Page, selector: str, value: str) -> bool:
        """Perform reliable form fill using direct value setting (proven working pattern).
        
        Args:
            page: Browser page
            selector: CSS selector for input element
            value: Value to set
            
        Returns:
            True if fill successful, False otherwise
        """
        try:
            # Use JavaScript to directly set value (most reliable method)
            result = await page.evaluate(
                f"""
                () => {{
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        element.value = '{value}';
                        element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return 'success';
                    }}
                    return 'element not found';
                }}
                """
            )
            
            if result == 'success':
                logger.debug(f"Successfully filled field: {selector}")
                return True
            else:
                logger.error(f"Failed to fill field {selector}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Reliable fill failed for {selector}: {e}")
            return False

    @staticmethod
    async def reliable_click_async(page: Page, selector: str) -> bool:
        """Perform reliable click using JavaScript (proven working pattern).
        
        Args:
            page: Browser page
            selector: CSS selector for element to click
            
        Returns:
            True if click successful, False otherwise
        """
        try:
            # Use JavaScript to directly trigger click (most reliable method)
            result = await page.evaluate(
                f"""
                () => {{
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        element.click();
                        return 'success';
                    }}
                    return 'element not found';
                }}
                """
            )
            
            if result == 'success':
                logger.debug(f"Successfully clicked element: {selector}")
                return True
            else:
                logger.error(f"Failed to click element {selector}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Reliable click failed for {selector}: {e}")
            return False

    @staticmethod
    async def wait_for_element_async(page: Page, selector: str, timeout: int = 5000) -> bool:
        """Wait for element to appear.
        
        Args:
            page: Browser page
            selector: CSS selector for element
            timeout: Timeout in milliseconds
            
        Returns:
            True if element appeared, False if timeout
        """
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except TimeoutError:
            logger.debug(f"Element not found within timeout: {selector}")
            return False

# EOF