#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 08:27:03 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_CookieAutoAcceptor.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_CookieAutoAcceptor.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

import json
import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class CookieAutoAcceptor:
    """Automatically handles cookie consent banners on web pages."""

    def __init__(self):
        self.cookie_texts = [
            "Accept all cookies",
            "Accept All",
            "Accept cookies",
            "Accept",
            "I Accept",
            "OK",
            "Continue",
            "Agree",
        ]

        self.selectors = [
            "[data-testid*='accept']",
            "[id*='accept']",
            "[class*='accept']",
            "button[aria-label*='Accept']",
            ".cookie-banner button:first-of-type",
            "#cookie-banner button:first-of-type",
        ]

    async def inject_auto_acceptor(self, context):
        """Inject auto-acceptor script into browser context."""
        script = f"""
        (() => {{
            const cookieTexts = {json.dumps(self.cookie_texts)};
            const selectors = {json.dumps(self.selectors)};

            function acceptCookies() {{
                // Try text-based buttons
                for (const text of cookieTexts) {{
                    const buttons = Array.from(document.querySelectorAll('button, a'));
                    const match = buttons.find(btn =>
                        btn.textContent.trim().toLowerCase() === text.toLowerCase()
                    );
                    if (match && match.offsetParent !== null) {{
                        match.click();
                        console.log('Auto-accepted cookies:', text);
                        return true;
                    }}
                }}

                // Try CSS selectors
                for (const selector of selectors) {{
                    try {{
                        const elements = document.querySelectorAll(selector);
                        for (const elem of elements) {{
                            if (elem.offsetParent !== null) {{
                                elem.click();
                                console.log('Auto-accepted cookies:', selector);
                                return true;
                            }}
                        }}
                    }} catch (e) {{}}
                }}
                return false;
            }}

            // Check periodically
            const interval = setInterval(() => {{
                if (acceptCookies()) {{
                    clearInterval(interval);
                }}
            }}, 1000);

            // Stop after 30 seconds
            setTimeout(() => clearInterval(interval), 30000);
        }})();
        """
        await context.add_init_script(script)

    async def accept_cookies(
        self, page: Page, wait_seconds: float = 2
    ) -> bool:
        """Try to automatically accept cookies on the page.

        Returns:
            True if cookies were accepted, False otherwise
        """
        await asyncio.sleep(wait_seconds)

        # Try text-based selection first
        for text in self.cookie_texts:
            try:
                button = page.locator(f"button:has-text('{text}')").first
                if await button.is_visible():
                    await button.click()
                    logger.debug(f"Clicked cookie button with text: {text}")
                    await asyncio.sleep(1)
                    return True
            except:
                continue

        # Try common selectors
        for selector in self.selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    await element.click()
                    logger.debug(f"Clicked cookie element: {selector}")
                    await asyncio.sleep(1)
                    return True
            except:
                continue

        return False

    async def check_cookie_banner_exists(self, page: Page) -> bool:
        """Check if a cookie banner is still visible."""
        try:
            return await page.locator(
                ".cookie-banner, [class*='cookie']"
            ).first.is_visible()
        except:
            return False


# # Usage
# ### Cookie Auto-Acceptance
# ```python
# from scitex.scholar.browser import CookieAutoAcceptor

# acceptor = CookieAutoAcceptor()

# # Inject into browser context
# await acceptor.inject_auto_acceptor(context)

# # Manual acceptance on page
# success = await acceptor.accept_cookies(page)
# ```

# EOF
