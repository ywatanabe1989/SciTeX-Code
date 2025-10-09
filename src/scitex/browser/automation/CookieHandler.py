#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 01:57:11 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/utils/_CookieAutoAcceptor.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json

from playwright.async_api import Page

from scitex import logging

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
            "Continue without an account",
            "Don't ask again",
        ]

        self.selectors = [
            "[data-testid*='accept']",
            "[id*='accept']",
            "[class*='accept']",
            "button[aria-label*='Accept']",
            ".cookie-banner button:first-of-type",
            "#cookie-banner button:first-of-type",
        ]

    async def inject_auto_acceptor_async(self, context):
        """Inject auto-acceptor script into browser context."""
        logger.warn("Use get_auto_acceptor_script instead")
        script = self.get_auto_acceptor_script()
        await context.add_init_script(script)

    def get_auto_acceptor_script(
        self,
    ):
        return f"""
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

    # async def accept_cookies_async(
    #     self, page: Page, wait_seconds: float = 2
    # ) -> bool:
    #     """Try to automatically accept cookies on the page.

    #     Returns:
    #         True if cookies were accepted, False otherwise
    #     """
    #     await asyncio.sleep(wait_seconds)

    #     # Try text-based selection first
    #     for text in self.cookie_texts:
    #         try:
    #             button = page.locator(f"button:has-text('{text}')").first
    #             if await button.is_visible():
    #                 await button.click()
    #                 logger.debug(f"Clicked cookie button with text: {text}")
    #                 await asyncio.sleep(1)
    #                 return True
    #         except:
    #             continue

    #     # Try common selectors
    #     for selector in self.selectors:
    #         try:
    #             element = page.locator(selector).first
    #             if await element.is_visible():
    #                 await element.click()
    #                 logger.debug(f"Clicked cookie element: {selector}")
    #                 await asyncio.sleep(1)
    #                 return True
    #         except:
    #             continue

    #     return False

    async def check_cookie_banner_exists_async(self, page: Page) -> bool:
        """Check if a cookie banner is still visible."""
        try:
            return await page.locator(
                ".cookie-banner, [class*='cookie']"
            ).first.is_visible()
        except:
            return False


def main(args):
    """Demonstrate CookieAutoAcceptor functionality."""
    import asyncio
    from playwright.async_api import async_playwright

    async def demo():
        acceptor = CookieAutoAcceptor()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()

            # Inject auto-acceptor
            await context.add_init_script(acceptor.get_auto_acceptor_script())

            page = await context.new_page()
            await page.goto("https://www.springer.com", timeout=30000)

            # Wait to see cookie acceptance in action
            await asyncio.sleep(5)

            # Check if banner still exists
            banner_exists = await acceptor.check_cookie_banner_exists_async(page)
            print(f"✓ Cookie banner exists: {banner_exists}")
            print("✓ Auto-acceptor demo complete")

            await browser.close()

    asyncio.run(demo())
    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description="CookieAutoAcceptor demo")
    return parser.parse_args()


def run_main():
    """Run main function."""
    args = parse_args()
    exit_status = main(args)
    return exit_status


if __name__ == "__main__":
    run_main()

# python -m scitex.browser.automation.CookieHandler

# EOF
