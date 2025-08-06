#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 04:22:32 (ywatanabe)"
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
    """Mixin for local browser-based strategies with common functionality.

    Browser Modes:
    - interactive: For human interaction (authentication, debugging) - 1280x720 viewport
    - stealth: For automated operations (scraping, downloading) - 1x1 viewport

    Note: Always runs browser in visible system mode (never truly headless)
    but uses viewport sizing to control interaction vs stealth behavior.
    """

    _shared_browser = None
    _shared_playwright = None

    def __init__(self, mode):
        """Initialize browser mixin.

        Args:
            mode: Browser mode - 'interactive' or 'stealth'
        """
        assert mode in ["interactive", "stealth"]

        self.cookie_acceptor = CookieAutoAcceptor()
        self.captcha_handler = CaptchaHandler()
        self.mode = mode
        self.contexts = []
        self.pages = []

    @classmethod
    async def get_shared_browser_async(cls) -> Browser:
        """Get or create shared browser instance (deprecated - use get_browser_async)."""
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
    async def cleanup_shared_browser_async(cls):
        """Clean up shared browser instance (call on app shutdown)."""
        if cls._shared_browser:
            await cls._shared_browser.close()
            cls._shared_browser = None
        if cls._shared_playwright:
            await cls._shared_playwright.stop()
            cls._shared_playwright = None

    async def get_browser_async(self) -> Browser:
        """Get or create a local browser instance with the current mode setting."""
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
                "--enable-extensions",  # Enable extensions support
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

            # Always run in visible mode (never headless)
            # This is safer for bot detection while providing flexibility via viewport sizing
            self._shared_browser = (
                await self._shared_playwright.chromium.launch(
                    headless=False,
                    args=stealth_args,
                )
            )
        return self._shared_browser

    async def new_page(self, url=None):
        """Create new page/tab and optionally navigate to URL."""
        browser = await self.get_browser_async()
        context = await browser.new_context()
        await context.add_init_script(
            self.cookie_acceptor.get_auto_acceptor_script()
        )
        # await self.cookie_acceptor.inject_auto_acceptor_async(context)
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

    async def create_browser_context_async(
        self, playwright_instance, **context_options
    ):
        """Create browser context with cookie auto-acceptance."""
        # Use headless mode for stealth, visible for interactive
        is_headless = self.mode == "stealth"
        browser = await playwright_instance.chromium.launch(
            headless=is_headless
        )

        # Smart viewport sizing based on mode
        if "viewport" not in context_options:
            if self.mode == "stealth":
                # For stealth mode: use minimal viewport to avoid detection
                context_options["viewport"] = {"width": 1, "height": 1}
            else:  # interactive mode
                # For interactive mode: use human-friendly size
                context_options["viewport"] = {"width": 1280, "height": 720}

        context = await browser.new_context(**context_options)
        await context.add_init_script(
            self.cookie_acceptor.get_auto_acceptor_script()
        )
        # await self.cookie_acceptor.inject_auto_acceptor_async(context)
        return browser, context

    async def get_session_async(self, timeout: int = 30) -> aiohttp.ClientSession:
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

    async def accept_cookies_async(self, page_index=0, wait_seconds=2):
        """Manually accept cookies on specific page."""
        if 0 <= page_index < len(self.pages):
            return await self.cookie_acceptor.accept_cookies_async(
                self.pages[page_index], wait_seconds
            )
        return False

    def interactive(self):
        """Set browser to interactive mode (human-friendly viewport)."""
        if self.mode == "interactive":
            return self
        self.mode = "interactive"
        self._shared_browser = None
        return self

    def stealth(self):
        """Set browser to stealth mode (minimal viewport for bot detection avoidance)."""
        if self.mode == "stealth":
            return self
        self.mode = "stealth"
        self._shared_browser = None
        return self

    async def show_async(self):
        """Switch browser to interactive mode and recreate all existing pages at current URLs."""
        if self.mode == "interactive":
            return self
        self.mode = "interactive"
        await self._restart_contexts_async()
        return self

    async def hide_async(self):
        """Switch browser to stealth mode and recreate all existing pages at current URLs."""
        if self.mode == "stealth":
            return self
        self.mode = "stealth"
        await self._restart_contexts_async()
        return self

    async def _restart_contexts_async(self):
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
            async def scrape_async(self, url):
                page = await self.new_page(url)
                return await page.content()

        # Usage
        browser = MyBrowser()

        # Interactive mode with tab management
        browser.interactive()  # Human-friendly viewport
        content1 = await browser.scrape_async("https://example.com")

        # Switch to stealth mode
        browser.stealth()  # Minimal viewport for bot detection avoidance
        content2 = await browser.scrape_async("https://example.com")
        content3 = await browser.scrape_async("https://google.com")

        # Browser now has 3 tabs open
        print(f"Open tabs: {len(browser.pages)}")

        #
        await browser.show_async()  # Make interactive (1280x720)
        await browser.hide_async()  # Make stealth (1x1)

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
