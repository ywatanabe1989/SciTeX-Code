#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 11:08:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Browser, BrowserContext, Page

from ._BrowserMixin import BrowserMixin
from ._StealthManager import StealthManager


class BrowserManager(BrowserMixin):
    def __init__(self, auth_manager=None):
        super().__init__()
        self.auth_manager = auth_manager
        self.stealth_manager = StealthManager()
        # self._authenticated_context = None

    async def get_authenticated_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""
        await self.auth_manager.ensure_authenticated()

        # Use the shared browser from BrowserMixin which respects visibility
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
        await self.cookie_acceptor.inject_auto_acceptor(context)

        return browser, context

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
        stealth_options = self.stealth_manager.get_stealth_options()
        merged_options = {**stealth_options, **context_options}
        context = await browser.new_context(**merged_options)
        await context.add_init_script(self.stealth_manager.get_init_script())
        await self.cookie_acceptor.inject_auto_acceptor(context)
        # await self.captcha_handler.inject_captcha_handler(context)
        return context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

# EOF
