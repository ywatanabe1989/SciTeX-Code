#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 08:31:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import random

from playwright.async_api import Browser, BrowserContext, Page

from ._BrowserMixin import BrowserMixin


class BrowserManager(BrowserMixin):
    def __init__(self, auth_manager=None):
        super().__init__()
        self.auth_manager = auth_manager
        self._authenticated_context = None

    async def get_authenticated_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""
        # await self._ensure_authentication()
        await self.auth_manager.ensure_authenticated()

        if self._authenticated_context:
            return await self.get_browser(), self._authenticated_context

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

        self._authenticated_context = await self._create_stealth_context(
            browser, **context_options
        )
        await self.cookie_acceptor.inject_auto_acceptor(
            self._authenticated_context
        )
        return browser, self._authenticated_context

    # async def _ensure_authentication(self):
    #     """Ensure authentication is verified and handle if needed."""
    #     if self._auth_verified:
    #         # Verify session is still valid
    #         if not await self._verify_session():
    #             self._auth_verified = False
    #             self._authenticated_context = None

    #     if not self._auth_verified:
    #         print("=" * 50)
    #         print("AUTHENTICATION REQUIRED")
    #         print("=" * 50)
    #         print("Opening authentication interface...")
    #         print(f"{'=' * 50}\n")

    #         await self.auth_manager.authenticate()
    #         self._auth_verified = True

    #     # if self._auth_verified or not self.auth_manager:
    #     #     self._auth_verified = True
    #     #     return

    #     # if await self.auth_manager.is_authenticated(verify_live=False):
    #     #     self._auth_verified = True
    #     #     return

    #     # print(f"\n{'='*50}")
    #     # print("AUTHENTICATION REQUIRED")
    #     # print(f"{'='*50}")
    #     # print("Opening authentication interface...")
    #     # print(f"{'='*50}\n")

    #     # await self.auth_manager.authenticate()
    #     # self._auth_verified = True

    async def _verify_session(self) -> bool:
        """Verify that the current session is still valid."""
        if not self._authenticated_context:
            return False

        try:
            page = await self._authenticated_context.new_page()
            # Test with a simple institutional resource
            await page.goto("https://my.openathens.net/account", timeout=10000)
            content = await page.content()
            is_valid = (
                "login" not in content.lower()
                and "sign in" not in content.lower()
            )
            await page.close()
            return is_valid
        except Exception:
            return False

    async def _create_stealth_context(
        self, browser: Browser, **context_options
    ) -> BrowserContext:
        """Creates a browser context with settings to appear more human."""
        stealth_options = {
            "viewport": await self.random_viewport(),
            "user_agent": self.user_agent_rotator.get_random(),
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com",
            },
        }

        merged_options = {**stealth_options, **context_options}
        context = await browser.new_context(**merged_options)

        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            window.chrome = {
                runtime: {},
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4,
            });
        """
        )

        await self.cookie_acceptor.inject_auto_acceptor(context)
        await self.captcha_handler.inject_captcha_handler(context)

        return context

    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add random human-like delay."""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)

    async def human_click(self, page: Page, element):
        """Simulate human-like clicking with mouse movement."""
        await element.hover()
        await self.human_delay(200, 500)
        await element.click()

    async def human_mouse_move(self, page: Page):
        """Random mouse movement to simulate human presence."""
        await page.mouse.move(
            random.randint(100, 800), random.randint(100, 600)
        )

    async def human_scroll(self, page: Page):
        """Simulate human-like scrolling behavior."""
        scroll_distance = random.randint(300, 800)
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await self.human_delay(500, 1500)

    async def human_type(self, page: Page, selector: str, text: str):
        """Type text with human-like delays."""
        element = page.locator(selector)
        await element.click()
        for char in text:
            await element.type(char)
            await self.human_delay(50, 200)

    async def random_viewport(self) -> dict:
        """Generate random viewport size."""
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1280, "height": 720},
        ]
        return random.choice(viewports)

    async def cleanup_authenticated_context(self):
        """Clean up cached authenticated context."""
        if self._authenticated_context:
            await self._authenticated_context.close()
            self._authenticated_context = None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_authenticated_context()
        await super().__aexit__(exc_type, exc_val, exc_tb)

# EOF
