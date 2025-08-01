#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 12:22:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/_HybridBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_HybridBrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Hybrid browser manager that uses Playwright by default and Selenium for extensions."""

import asyncio
from typing import Optional, Union
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from selenium import webdriver

from scitex import logging
from ._BrowserMixin import BrowserMixin
from ._ChromeExtensionManager import ChromeExtensionManager
from ._SeleniumBrowserManager import SeleniumBrowserManager

logger = logging.getLogger(__name__)


class HybridBrowserManager(BrowserMixin):
    """Browser manager that intelligently switches between Playwright and Selenium.
    
    - Uses Playwright for general browsing (faster, better API)
    - Uses Selenium when Chrome extensions are needed
    """
    
    def __init__(
        self,
        auth_manager=None,
        headless: bool = True,
        use_extensions: bool = False,
        profile_name: str = "scholar_default"
    ):
        """Initialize hybrid browser manager.
        
        Args:
            auth_manager: Authentication manager for cookies
            headless: Run browser in headless mode
            use_extensions: Use Selenium with Chrome extensions
            profile_name: Chrome profile name for extensions
        """
        super().__init__(headless=headless)
        self.auth_manager = auth_manager
        self.use_extensions = use_extensions
        self.profile_name = profile_name
        
        # Managers
        self._selenium_manager = None
        self._playwright = None
        self._browser = None
        
    async def get_browser(self) -> Browser:
        """Get Playwright browser (when not using extensions)."""
        if self.use_extensions:
            raise ValueError(
                "Cannot get Playwright browser when use_extensions=True. "
                "Use get_selenium_driver() instead."
            )
            
        if not self._browser:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            
        return self._browser
        
    def get_selenium_driver(self) -> webdriver.Chrome:
        """Get Selenium driver with Chrome extensions."""
        if not self.use_extensions:
            raise ValueError(
                "Selenium driver only available when use_extensions=True"
            )
            
        if not self._selenium_manager:
            self._selenium_manager = SeleniumBrowserManager(
                profile_name=self.profile_name,
                headless=self.headless,
                auth_manager=self.auth_manager
            )
            
        return self._selenium_manager.get_driver()
        
    async def get_authenticated_context(self) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies."""
        if self.use_extensions:
            raise NotImplementedError(
                "Authenticated context not available for Selenium. "
                "Authentication is applied directly to the driver."
            )
            
        browser = await self.get_browser()
        context_options = {}
        
        if self.auth_manager and await self.auth_manager.is_authenticated():
            try:
                auth_session = await self.auth_manager.authenticate()
                if auth_session and auth_session.cookies:
                    # Convert cookies to Playwright format
                    cookies = []
                    for cookie in auth_session.cookies:
                        cookies.append({
                            "name": cookie["name"],
                            "value": cookie["value"],
                            "domain": cookie.get("domain", ""),
                            "path": cookie.get("path", "/"),
                            "secure": cookie.get("secure", False),
                            "httpOnly": cookie.get("httpOnly", False),
                        })
                    context_options["storage_state"] = {"cookies": cookies}
            except Exception as e:
                logger.error(f"Failed to apply authentication: {e}")
                
        context = await browser.new_context(**context_options)
        return browser, context
        
    async def navigate_async(self, url: str, wait_time: int = 10):
        """Navigate to URL using appropriate browser."""
        if self.use_extensions:
            # Use Selenium
            await asyncio.to_thread(
                self._selenium_manager.navigate, url, wait_time
            )
        else:
            # Use Playwright
            browser = await self.get_browser()
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            if wait_time > 0:
                await page.wait_for_load_state("networkidle")
            return page
            
    def check_extensions(self) -> dict:
        """Check installed Chrome extensions."""
        profile_manager = ChromeExtensionManager(self.profile_name)
        return profile_manager.check_extensions_installed()
        
    def install_extensions(self):
        """Interactively install Chrome extensions."""
        profile_manager = ChromeExtensionManager(self.profile_name)
        profile_manager.install_extensions_interactive()
        
    async def close(self):
        """Close all browser instances."""
        # Close Selenium
        if self._selenium_manager:
            await asyncio.to_thread(self._selenium_manager.close)
            self._selenium_manager = None
            
        # Close Playwright
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            
    @asynccontextmanager
    async def async_context(self):
        """Async context manager for browser lifecycle."""
        try:
            if self.use_extensions:
                driver = await asyncio.to_thread(self.get_selenium_driver)
                yield driver
            else:
                browser = await self.get_browser()
                context = await browser.new_context()
                page = await context.new_page()
                yield page
        finally:
            await self.close()
            
    def switch_to_extensions_mode(self):
        """Switch to using Selenium with extensions."""
        self.use_extensions = True
        
    def switch_to_playwright_mode(self):
        """Switch to using Playwright (no extensions)."""
        self.use_extensions = False


# Example usage
async def example():
    """Example of using the hybrid browser manager."""
    
    # Use Playwright for fast browsing
    manager = HybridBrowserManager(use_extensions=False)
    async with manager.async_context() as page:
        await page.goto("https://example.com")
        print(f"Title: {await page.title()}")
    
    # Use Selenium for extension-required tasks
    manager = HybridBrowserManager(use_extensions=True)
    manager.install_extensions()  # One-time setup
    
    driver = manager.get_selenium_driver()
    driver.get("https://scholar.google.com")
    # Extensions are loaded and working
    manager.close()


# EOF