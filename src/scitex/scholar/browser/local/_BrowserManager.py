#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 19:26:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging

from ._BrowserMixin import BrowserMixin
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)


class BrowserManager(BrowserMixin):
    """Manages a local browser instance with stealth enhancements."""

    def __init__(self, auth_manager=None, headless: bool = True):
        super().__init__(headless=headless)
        self.auth_manager = auth_manager
        if auth_manager is None:
            logger.info(f"auth_manager not passed")
        self.stealth_manager = StealthManager()

    async def get_authenticated_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""

        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. Initialize BrowserManager with an auth_manager to use this method."
            )

        await self.auth_manager.ensure_authenticated()

        browser = await self.get_browser()
        context_options = {}
        if self.auth_manager and await self.auth_manager.is_authenticated():
            try:
                auth_session = await self.auth_manager.authenticate()
                if auth_session and "cookies" in auth_session:
                    context_options["storage_state"] = {
                        "cookies": auth_session["cookies"]
                    }
            except Exception:
                pass

        context = await self._create_stealth_context(
            browser, **context_options
        )
        return browser, context

    async def _create_stealth_context(
        self, browser: Browser, **context_options
    ) -> BrowserContext:
        """Creates a new browser context with stealth options applied."""
        stealth_options = self.stealth_manager.get_stealth_options()
        merged_options = {**stealth_options, **context_options}
        context = await browser.new_context(**merged_options)
        await context.add_init_script(self.stealth_manager.get_init_script())
        await self.cookie_acceptor.inject_auto_acceptor(context)
        return context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)


if __name__ == "__main__":
    import asyncio

    async def main():
        """Example usage of BrowserManager with stealth features."""
        # Initialize browser manager
        manager = BrowserManager(
            auth_manager=None,
            headless=False,  # Start in headless mode
        )

        # Create a new page with stealth features
        page = await manager.new_page()
        context = manager.contexts[-1]

        # Navigate to a site that checks for bots
        await page.goto("https://bot.sannysoft.com/")
        await page.wait_for_timeout(2000)

        # Take screenshot to verify stealth
        await page.screenshot(path="stealth_test.png")
        print("Screenshot saved as stealth_test.png")

        # Example: Handle cookie consent automatically
        await page.goto("https://www.cookiebot.com/en/")
        await page.wait_for_timeout(
            3000
        )  # Cookie acceptor works automatically

        # Check if we passed bot detection
        # This is a simple check - real sites have more sophisticated detection
        content = await page.content()
        if "HeadlessChrome" not in content:
            print("✓ Passed basic bot detection")
        else:
            print("✗ Failed bot detection")

        # Show browser for debugging (only works if started with headless=False)
        # await manager.show()

        # Access multiple pages
        page2 = await context.new_page()
        await page2.goto("https://example.com")

        print(f"Total pages open: {len(context.pages)}")

        # Close specific page
        await page2.close()

        print("Browser manager closed successfully")

    # Run the example
    asyncio.run(main())

# python -m scitex.scholar.browser.local._BrowserManager

# WebDriver preresent (failed) # why?

# EOF
