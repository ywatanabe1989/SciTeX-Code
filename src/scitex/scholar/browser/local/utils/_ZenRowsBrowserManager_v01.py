#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 19:03:06 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/utils/_ZenrowsBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_ZenrowsBrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Manages a local browser that routes traffic through the ZenRows proxy network."""
from typing import Any, Dict

from playwright.async_api import Browser, async_playwright

from scitex import logging

from ._BrowserManager import BrowserManager

logger = logging.getLogger(__name__)


class ZenRowsBrowserManager(BrowserManager):
    """
    Manages a local browser routed through the ZenRows Proxy network.

    This combines full local browser control with ZenRows' residential IPs
    and anti-bot bypass capabilities. It requires proxy credentials.
    """

    def __init__(
        self,
        headless: bool = False,
        auth_manager=None,
        proxy_username=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME"),
        proxy_password=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD"),
        proxy_domain=os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN", "superproxy.zenrows.com"
        ),
        proxy_port=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_PORT", "1337"),
        proxy_country=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY", None),
        **kwargs,
    ):
        """
        Initialize a local browser with ZenRows proxy support.

        Proxy credentials can be passed directly or sourced from environment
        variables.

        Args:
            headless: Run browser in headless mode.
            auth_manager: Authentication manager instance.
            proxy_username (str): ZenRows proxy username.
            proxy_password (str): ZenRows proxy password.
            proxy_domain (str): Proxy domain, defaults to ZenRows.
            proxy_port (str): Proxy port, defaults to ZenRows.
            proxy_country (str): Country code for proxy routing (e.g., 'au', 'us').
            **kwargs: Additional browser options.
        """
        super().__init__(
            auth_manager=auth_manager,
            headless=headless,
        )
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password
        self._proxy_domain = proxy_domain
        self._proxy_port = proxy_port
        self._proxy_country = proxy_country
        self._proxy_config = self._build_proxy_config()

    def _build_proxy_config(self) -> Dict[str, Any]:
        """Builds the ZenRows proxy configuration for Playwright."""
        if self._proxy_username and self._proxy_password:
            # ZenRows supports country routing by appending country code to username
            # Format: username-country-XX where XX is the 2-letter country code
            username = self._proxy_username
            if self._proxy_country:
                # Try different formats as ZenRows documentation varies
                username = (
                    f"{self._proxy_username}-country-{self._proxy_country}"
                )
                logger.info(
                    f"Using ZenRows proxy with country routing: {self._proxy_country.upper()}"
                )

            logger.info(f"Using ZenRows proxy credentials: {username}")
            return {
                "server": f"http://{self._proxy_domain}:{self._proxy_port}",
                "username": username,
                "password": self._proxy_password,
            }
        raise ValueError(
            "ZenRows proxy credentials required. Pass them to the constructor or "
            "set SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME and "
            "SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD environment variables."
        )

    async def get_browser(self) -> Browser:
        """Get or create a browser instance with ZenRows proxy configuration."""
        if (
            self._shared_browser is None
            or not self._shared_browser.is_connected()
        ):
            logger.info("Launching local browser with ZenRows proxy...")
            if self._shared_playwright is None:
                self._shared_playwright = await async_playwright().start()

            # Enhanced stealth arguments for ZenRows
            # Note: Removed --single-process as it conflicts with proxy usage
            launch_options = {
                "headless": self.headless,
                "proxy": self._proxy_config,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                    "--start-maximized",
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ],
                "ignore_default_args": ["--enable-automation"],
            }
            self._shared_browser = (
                await self._shared_playwright.chromium.launch(**launch_options)
            )
            logger.success("Launched browser with ZenRows proxy")
        return self._shared_browser


if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    async def main():
        from scitex.scholar.auth import AuthenticationManager
        from scitex.scholar.browser.local._BrowserManager import BrowserManager
        from scitex.scholar.browser.local._ZenRowsBrowserManager import (
            ZenRowsBrowserManager,
        )

        auth_manager = AuthenticationManager()
        await auth_manager.authenticate()

        screenshots_dir = Path("./screenshots")
        screenshots_dir.mkdir(exist_ok=True)

        test_sites = [
            ("ip", "https://httpbin.org/ip", "Shows your public IP address"),
            (
                "headers",
                "https://httpbin.org/headers",
                "HTTP headers sent by browser",
            ),
            (
                "bot_detection",
                "https://bot.sannysoft.com/",
                "Bot tests - green=good, red=detected",
            ),
            (
                "fingerprint",
                "https://pixelscan.net/",
                "Browser fingerprinting analysis",
            ),
            (
                "webrtc",
                "https://browserleaks.com/webrtc",
                "WebRTC IP leak test",
            ),
        ]

        async def test_browser(browser_type, browser_manager):
            print(f"\n=== {browser_type} ===")
            browser = await browser_manager.get_browser()

            for test_name, url, description in test_sites:
                page = await browser.new_page()
                print(f"\n{test_name}: {description}")

                try:
                    await page.goto(
                        url, timeout=30000, wait_until="domcontentloaded"
                    )

                    if test_name in ["ip", "headers"]:
                        content = await page.text_content("pre")
                        print(f"Result: {content.strip()}")
                    else:
                        await page.wait_for_timeout(5000)

                    screenshot_path = (
                        screenshots_dir
                        / f"{browser_type.lower().replace(' ', '_')}_{test_name}.png"
                    )
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"Screenshot saved: {screenshot_path}")

                except Exception as ee:
                    print(f"Failed: {str(ee)[:50]}...")

                await page.close()

        regular_manager = BrowserManager(
            auth_manager=auth_manager, headless=False
        )
        await test_browser("regular", regular_manager)

        zenrows_manager = ZenRowsBrowserManager(
            auth_manager=auth_manager, headless=False
        )
        await test_browser("zenrows", zenrows_manager)

        print(f"\nScreenshots saved in: {screenshots_dir.absolute()}")

    asyncio.run(main())

# python -m scitex.scholar.browser.local._ZenRowsBrowserManager

# EOF
