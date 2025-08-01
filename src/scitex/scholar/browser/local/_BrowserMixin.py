#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 19:18:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/_BrowserMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_BrowserMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import aiohttp
from playwright.async_api import Browser, async_playwright

from .utils._CaptchaHandler import CaptchaHandler
from .utils._CookieAutoAcceptor import CookieAutoAcceptor


class BrowserMixin:
    """Mixin for local browser-based strategies with common functionality."""

    _shared_browser = None
    _shared_playwright = None

    def __init__(self, headless: bool = True):
        """Initialize browser mixin."""
        self.cookie_acceptor = CookieAutoAcceptor()
        self.captcha_handler = CaptchaHandler()
        self.headless = headless
        self.contexts = []
        self.pages = []

    @classmethod
    async def get_shared_browser(cls) -> Browser:
        """Get or create shared browser instance (deprecated - use get_browser)."""
        if (
            cls._shared_browser is None
            or cls._shared_browser.is_connected() is False
        ):
            if cls._shared_playwright is None:
                cls._shared_playwright = await async_playwright().start()
            cls._shared_browser = await cls._shared_playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
        return cls._shared_browser

    @classmethod
    async def cleanup_shared_browser(cls):
        """Clean up shared browser instance (call on app shutdown)."""
        if cls._shared_browser:
            await cls._shared_browser.close()
            cls._shared_browser = None
        if cls._shared_playwright:
            await cls._shared_playwright.stop()
            cls._shared_playwright = None

    async def get_browser(self) -> Browser:
        """Get or create a local browser instance with the current visibility setting."""
        if (
            self._shared_browser is None
            or self._shared_browser.is_connected() is False
        ):
            if self._shared_playwright is None:
                self._shared_playwright = await async_playwright().start()

            # Enhanced stealth launch arguments
            stealth_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-default-apps",
                "--disable-extensions-except=*",  # Allow extensions to load
                "--load-extension=*",  # Load extensions
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-plugins-discovery",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-domain-reliability",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-popup-blocking",
                "--window-size=1920,1080",
            ]

            # Use standard headless mode
            headless_mode = self.headless

            # Launch a local browser with stealth settings
            self._shared_browser = (
                await self._shared_playwright.chromium.launch(
                    headless=headless_mode,
                    args=stealth_args,
                )
            )
        return self._shared_browser

    async def new_page(self, url=None):
        """Create new page/tab and optionally navigate to URL."""
        browser = await self.get_browser()
        context = await browser.new_context()
        await self.cookie_acceptor.inject_auto_acceptor(context)
        page = await context.new_page()
        self.contexts.append(context)
        self.pages.append(page)
        if url:
            await page.goto(url)
        return page

    async def close_page(self, page_index):
        """Close specific page/tab by index."""
        if 0 <= page_index < len(self.pages):
            await self.contexts[page_index].close()
            self.contexts.pop(page_index)
            self.pages.pop(page_index)

    async def close_all_pages(self):
        """Close all pages/tabs."""
        for context in self.contexts:
            await context.close()
        self.contexts.clear()
        self.pages.clear()

    async def create_browser_context(
        self, playwright_instance, **context_options
    ):
        """Create browser context with cookie auto-acceptance."""
        browser = await playwright_instance.chromium.launch(
            headless=self.headless
        )
        context = await browser.new_context(**context_options)
        await self.cookie_acceptor.inject_auto_acceptor(context)
        return browser, context

    async def get_session(self, timeout: int = 30) -> aiohttp.ClientSession:
        """Get or create basic aiohttp session."""
        if (
            not hasattr(self, "_session")
            or self._session is None
            or self._session.closed
        ):
            connector = aiohttp.TCPConnector()
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            self._session = aiohttp.ClientSession(
                connector=connector, timeout=client_timeout
            )
        return self._session

    async def close_session(self):
        """Close the aiohttp session."""
        if (
            hasattr(self, "_session")
            and self._session
            and not self._session.closed
        ):
            await self._session.close()
            self._session = None

    async def accept_cookies(self, page_index=0, wait_seconds=2):
        """Manually accept cookies on specific page."""
        if 0 <= page_index < len(self.pages):
            return await self.cookie_acceptor.accept_cookies(
                self.pages[page_index], wait_seconds
            )
        return False

    def visible(self):
        """Set browser to visible mode (flag only, browser recreated on next use)."""
        if self.headless is False:
            return self
        self.headless = False
        self._shared_browser = None
        return self

    def invisible(self):
        """Set browser to headless mode (flag only, browser recreated on next use)."""
        if self.headless is True:
            return self
        self.headless = True
        self._shared_browser = None
        return self

    async def show(self):
        """Switch browser to visible mode and recreate all existing pages at current URLs."""
        if not self.headless:
            return self
        self.headless = False
        await self._restart_contexts()
        return self

    async def hide(self):
        """Switch browser to headless mode and recreate all existing pages at current URLs."""
        if self.headless:
            return self
        self.headless = True
        await self._restart_contexts()
        return self

    async def _restart_contexts(self):
        page_urls = [page.url for page in self.pages]
        await self.close_all_pages()
        self._shared_browser = None
        for url in page_urls:
            await self.new_page(url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all_pages()
        await self.close_session()


if __name__ == "__main__":
    import asyncio

    async def main():
        from scitex.scholar.browser.local._BrowserMixin import BrowserMixin

        class MyBrowser(BrowserMixin):
            async def scrape(self, url):
                page = await self.new_page(url)
                return await page.content()

        # Usage
        browser = MyBrowser()

        # Visible mode with tab management
        browser.visible()  # Flag Only
        content1 = await browser.scrape("https://example.com")

        # Switch to headless mode
        browser.invisible()  # Flag Only
        content2 = await browser.scrape("https://example.com")
        content3 = await browser.scrape("https://google.com")

        # Browser now has 3 tabs open
        print(f"Open tabs: {len(browser.pages)}")

        #
        await browser.show()  # Make visible
        await browser.hide()  # Make headless

        # Access specific pages
        first_page = browser.pages[0]
        await first_page.screenshot(path="screenshot.png")

        # Close specific tab
        await browser.close_page(0)

        # Close all tabs
        await browser.close_all_pages()

    asyncio.run(main())

#  python -m scitex.scholar.browser.local._BrowserMixin

# EOF
