#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-29 03:19:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Browser, BrowserContext

from ._BrowserMixin import BrowserMixin


class BrowserManager(BrowserMixin):
    def __init__(self, auth_manager=None):
        super().__init__()
        self.auth_manager = auth_manager
        self._authenticated_context = None
        self._auth_verified = False

    async def get_authenticated_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""
        await self._ensure_authentication()

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

        self._authenticated_context = await browser.new_context(
            **context_options
        )
        await self.cookie_acceptor.inject_auto_acceptor(
            self._authenticated_context
        )
        return browser, self._authenticated_context

    async def _ensure_authentication(self):
        """Ensure authentication is verified and handle if needed."""
        if self._auth_verified:
            # Verify session is still valid
            if not await self._verify_session():
                self._auth_verified = False
                self._authenticated_context = None

        if not self._auth_verified:
            print("=" * 50)
            print("AUTHENTICATION REQUIRED")
            print("=" * 50)
            print("Opening authentication interface...")
            print(f"{'=' * 50}\n")

            await self.auth_manager.authenticate()
            self._auth_verified = True

        # if self._auth_verified or not self.auth_manager:
        #     self._auth_verified = True
        #     return

        # if await self.auth_manager.is_authenticated(verify_live=False):
        #     self._auth_verified = True
        #     return

        # print(f"\n{'='*50}")
        # print("AUTHENTICATION REQUIRED")
        # print(f"{'='*50}")
        # print("Opening authentication interface...")
        # print(f"{'='*50}\n")

        # await self.auth_manager.authenticate()
        # self._auth_verified = True

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

    async def _create_context(self):
        """Create new browser context with stealth settings."""
        context = await self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Add stealth JavaScript
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            window.chrome = {
                runtime: {},
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """
        )

        return context

    async def cleanup_authenticated_context(self):
        """Clean up cached authenticated context."""
        if self._authenticated_context:
            await self._authenticated_context.close()
            self._authenticated_context = None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_authenticated_context()
        await super().__aexit__(exc_type, exc_val, exc_tb)

# EOF
