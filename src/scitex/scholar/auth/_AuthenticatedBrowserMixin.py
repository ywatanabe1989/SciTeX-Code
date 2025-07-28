#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-29 01:06:19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_AuthenticatedBrowserMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_AuthenticatedBrowserMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import logging

import aiohttp
from playwright.async_api import Browser, BrowserContext

from ..browser._BrowserMixin import BrowserMixin

logger = logging.getLogger(__name__)


class AuthenticatedBrowserMixin(BrowserMixin):
    """Mixin that provides authenticated browser context with reuse capability."""

    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self._authenticated_context = None

    #     self._auth_verified = False

    # async def _ensure_authentication(self):
    #     """Ensure authentication is verified and handle if needed."""
    #     if self._auth_verified:
    #         return

    #     if not self.auth_manager:
    #         self._auth_verified = True
    #         return

    #     # Check if already authenticated
    #     if await self.auth_manager.is_authenticated(verify_live=False):
    #         logger.info("Using existing authentication session")
    #         self._auth_verified = True
    #         return

    #     # Need to authenticate
    #     print(f"\n{'='*50}")
    #     print("AUTHENTICATION REQUIRED")
    #     print(f"{'='*50}")
    #     print("Institutional access authentication needed.")
    #     print("Opening authentication interface...")
    #     print(f"{'='*50}\n")

    #     try:
    #         result = await self.auth_manager.authenticate()
    #         if result:
    #             logger.info("Authentication successful")
    #             self._auth_verified = True
    #         else:
    #             logger.warning("Authentication failed")
    #     except Exception as e:
    #         logger.error(f"Authentication error: {e}")

    async def get_authenticated_browser_context(
        self, **context_options
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""
        # Ensure authentication first
        await self._ensure_authentication()

        if self._authenticated_context:
            return await self.get_browser(), self._authenticated_context

        auth_session = None
        if self.auth_manager and await self.auth_manager.is_authenticated():
            try:
                auth_session = await self.auth_manager.authenticate()
            except Exception as e:
                logger.debug(f"Failed to get auth session: {e}")

        browser = await self.get_browser()

        if auth_session and "cookies" in auth_session:
            context_options["storage_state"] = {
                "cookies": auth_session["cookies"]
            }

        context = await browser.new_context(**context_options)
        await self.cookie_acceptor.inject_auto_acceptor(context)
        self._authenticated_context = context
        return browser, context

    async def cleanup_browser_context(self):
        """Clean up cached browser context (but keep shared browser)."""
        if self._authenticated_context:
            await self._authenticated_context.close()
            self._authenticated_context = None

    async def get_authenticated_session(
        self, timeout: int = 30
    ) -> aiohttp.ClientSession:
        """Get or create aiohttp session with authentication cookies."""
        if (
            not hasattr(self, "_auth_session")
            or self._auth_session is None
            or self._auth_session.closed
        ):
            connector = aiohttp.TCPConnector()
            client_timeout = aiohttp.ClientTimeout(total=timeout)

            cookies = None
            if (
                self.auth_manager
                and await self.auth_manager.is_authenticated()
            ):
                try:
                    auth_cookies = await self.auth_manager.get_auth_cookies()
                    cookies = aiohttp.CookieJar()
                    for cookie in auth_cookies:
                        cookies.update_cookies([cookie])
                except Exception as e:
                    logger.debug(f"Failed to get auth cookies: {e}")

            self._auth_session = aiohttp.ClientSession(
                connector=connector, timeout=client_timeout, cookie_jar=cookies
            )
        return self._auth_session

    async def close_authenticated_session(self):
        """Close the authenticated aiohttp session."""
        if (
            hasattr(self, "_auth_session")
            and self._auth_session
            and not self._auth_session.closed
        ):
            await self._auth_session.close()
            self._auth_session = None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_authenticated_session()
        await self.cleanup_browser_context()
        await super().__aexit__(exc_type, exc_val, exc_tb)

# EOF
