#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 07:31:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_BrowserMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_BrowserMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import aiohttp
from playwright.async_api import Browser, async_playwright

from ._CaptchaHandler import CaptchaHandler
from ._CookieAutoAcceptor import CookieAutoAcceptor


class BrowserMixin:
    """Mixin for browser-based strategies with common functionality."""

    _shared_browser = None
    _shared_playwright = None

    def __init__(self, browser_backend: str = "local", zenrows_api_key: str = None, proxy_country: str = "us"):
        """Initialize browser mixin.
        
        Args:
            browser_backend: "local" or "zenrows"
            zenrows_api_key: API key for ZenRows (required if backend="zenrows")
            proxy_country: Country code for ZenRows proxy
        """
        self.cookie_acceptor = CookieAutoAcceptor()
        self.captcha_handler = CaptchaHandler()
        self.headless = True
        self.contexts = []
        self.pages = []
        
        # ZenRows configuration
        self.browser_backend = browser_backend or os.getenv("SCITEX_SCHOLAR_BROWSER_BACKEND", "local")
        self.zenrows_api_key = zenrows_api_key or os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        self.proxy_country = proxy_country or os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY", "us")

    def visible(self):
        """Set browser to visible mode (flag only, browser recreated on next use)."""
        if self.headless == False:
            return self
        self.headless = False
        self._shared_browser = None
        return self

    def invisible(self):
        """Set browser to headless mode (flag only, browser recreated on next use)."""
        if self.headless == True:
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

    async def get_browser(self) -> Browser:
        """Get or create browser instance with current visibility setting."""
        if (
            self._shared_browser is None
            or self._shared_browser.is_connected() is False
        ):
            if self._shared_playwright is None:
                self._shared_playwright = await async_playwright().start()

            if self.browser_backend == "zenrows":
                # Use ZenRows Scraping Browser
                if not self.zenrows_api_key:
                    raise ValueError("ZenRows API key required for zenrows backend")
                
                # Build connection URL
                connection_url = (
                    f"wss://browser.zenrows.com"
                    f"?apikey={self.zenrows_api_key}"
                    f"&proxy_country={self.proxy_country}"
                )
                
                # Connect to remote browser
                self._shared_browser = await self._shared_playwright.chromium.connect_over_cdp(
                    connection_url,
                    timeout=120000  # 2 minutes for remote connection
                )
            else:
                # Local browser
                self._shared_browser = (
                    await self._shared_playwright.chromium.launch(
                        headless=self.headless,
                        args=["--no-sandbox", "--disable-dev-shm-usage"],
                    )
                )

        return self._shared_browser

    # async def new_page(self, url=None):
    #     """Create new page/tab and optionally navigate to URL."""
    #     browser = await self.get_browser()
    #     context = await browser.new_context()
    #     page = await context.new_page()

    #     self.contexts.append(context)
    #     self.pages.append(page)

    #     if url:
    #         await page.goto(url)

    #     return page

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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all_pages()
        await self.close_session()

# EOF
