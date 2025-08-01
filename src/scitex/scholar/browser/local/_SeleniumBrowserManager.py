#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 12:16:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/_SeleniumBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_SeleniumBrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from scitex import logging

from ._ChromeExtensionManager import ChromeExtensionManager

logger = logging.getLogger(__name__)


class SeleniumBrowserManager:
    """Browser manager using Selenium with Chrome profiles and extensions."""
    
    def __init__(
        self,
        profile_name: str = "scholar_default",
        headless: bool = False,
        auth_manager=None
    ):
        """Initialize Selenium browser manager.
        
        Args:
            profile_name: Chrome profile name
            headless: Whether to run Chrome in headless mode
            auth_manager: Optional authentication manager
        """
        self.profile_manager = ChromeExtensionManager(profile_name)
        self.headless = headless
        self.auth_manager = auth_manager
        self._driver = None
        
    def get_driver(self) -> webdriver.Chrome:
        """Get or create Chrome driver.
        
        Returns:
            Chrome WebDriver instance
        """
        if self._driver is None:
            self._driver = self.profile_manager.create_driver(headless=self.headless)
            logger.info("Chrome driver created")
            
            # Apply authentication if available
            if self.auth_manager:
                self._apply_authentication()
                
        return self._driver
        
    def _apply_authentication(self):
        """Apply authentication cookies to the browser."""
        if not self.auth_manager or not self._driver:
            return
            
        try:
            # Get authentication cookies
            auth_session = self.auth_manager.get_session()
            if auth_session and auth_session.cookies:
                # Navigate to a domain to set cookies
                self._driver.get("https://www.google.com")
                
                # Add cookies
                for cookie in auth_session.cookies:
                    try:
                        self._driver.add_cookie(cookie)
                    except Exception as e:
                        logger.warning(f"Failed to add cookie: {e}")
                        
                logger.info("Authentication cookies applied")
                
        except Exception as e:
            logger.error(f"Failed to apply authentication: {e}")
            
    async def get_driver_async(self) -> webdriver.Chrome:
        """Async wrapper for getting driver.
        
        Returns:
            Chrome WebDriver instance
        """
        return await asyncio.to_thread(self.get_driver)
        
    def navigate(self, url: str, wait_time: int = 10):
        """Navigate to a URL with optional wait.
        
        Args:
            url: URL to navigate to
            wait_time: Time to wait for page load
        """
        driver = self.get_driver()
        driver.get(url)
        
        if wait_time > 0:
            WebDriverWait(driver, wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
    async def navigate_async(self, url: str, wait_time: int = 10):
        """Async navigation.
        
        Args:
            url: URL to navigate to
            wait_time: Time to wait for page load
        """
        await asyncio.to_thread(self.navigate, url, wait_time)
        
    def close(self):
        """Close the browser."""
        if self._driver:
            try:
                self._driver.quit()
                logger.info("Chrome driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            finally:
                self._driver = None
                
    async def close_async(self):
        """Async close."""
        await asyncio.to_thread(self.close)
        
    @asynccontextmanager
    async def async_context(self):
        """Async context manager for browser lifecycle.
        
        Usage:
            async with browser_manager.async_context() as driver:
                await browser_manager.navigate_async("https://example.com")
                # Use driver...
        """
        try:
            driver = await self.get_driver_async()
            yield driver
        finally:
            await self.close_async()
            
    def __enter__(self):
        """Context manager entry."""
        return self.get_driver()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def check_extensions(self) -> dict:
        """Check installed extensions.
        
        Returns:
            Dictionary of extension installation status
        """
        return self.profile_manager.check_extensions_installed()
        
    def install_extensions(self):
        """Open interactive extension installation."""
        self.profile_manager.install_extensions_interactive()
        
    def get_profile_info(self) -> dict:
        """Get Chrome profile information.
        
        Returns:
            Profile information dictionary
        """
        return self.profile_manager.get_profile_info()


# EOF