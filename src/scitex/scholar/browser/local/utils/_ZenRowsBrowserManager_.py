#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 19:30:32 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/utils/_ZenRowsBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_ZenRowsBrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Dict

from playwright.async_api import Browser, BrowserContext, async_playwright

from scitex import log

from .._BrowserMixin import BrowserMixin
from ._CookieAutoAcceptor import CookieAutoAcceptor
from ._StealthManager import StealthManager

logger = log.getLogger(__name__)


class ZenRowsBrowserManager(BrowserMixin):
    def __init__(
        self,
        headless: bool = False,
        auth_manager=None,
        stealth_manager=None,
        viewport_size=(1920, 1080),
        spoof_dimension=False,
        proxy_username=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME"),
        proxy_password=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD"),
        proxy_domain=os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN", "superproxy.zenrows.com"
        ),
        proxy_port=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_PORT", "1337"),
        proxy_country=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY", None),
        **kwargs,
    ):

        super().__init__(mode="stealth")

        self.auth_manager = auth_manager
        self.headless = headless
        self.viewport_size = viewport_size
        self.spoof_dimension = spoof_dimension

        # Use passed stealth_manager or create new one
        self.stealth_manager = stealth_manager or StealthManager(
            viewport_size=viewport_size, spoof_dimension=spoof_dimension
        )
        self.cookie_acceptor = CookieAutoAcceptor()

        self._proxy_username = proxy_username
        self._proxy_password = proxy_password
        self._proxy_domain = proxy_domain
        self._proxy_port = proxy_port
        self._proxy_country = proxy_country
        self._proxy_config = self._build_proxy_config()

        self._shared_browser = None
        self._shared_playwright = None

    def _build_proxy_config(self) -> Dict[str, Any]:
        if self._proxy_username and self._proxy_password:
            username = self._proxy_username
            if self._proxy_country:
                username = (
                    f"{self._proxy_username}-country-{self._proxy_country}"
                )
                logger.debug(
                    f"Using ZenRows proxy with country routing: {self._proxy_country.upper()}"
                )

            return {
                "server": f"http://{self._proxy_domain}:{self._proxy_port}",
                "username": username,
                "password": self._proxy_password,
            }
        raise ValueError("ZenRows proxy credentials required")

    async def get_browser(self) -> Browser:
        if (
            self._shared_browser is None
            or not self._shared_browser.is_connected()
        ):
            logger.debug("Launching browser with ZenRows proxy...")

            if self._shared_playwright is None:
                self._shared_playwright = await async_playwright().start()

            stealth_args = (
                self.stealth_manager.get_stealth_options_additional()
            )

            launch_options = {
                "headless": self.headless,
                "proxy": self._proxy_config,
                "args": stealth_args
                + [
                    "--window-size=1920,1080",
                    "--start-maximized",
                ],
                "ignore_default_args": ["--enable-automation"],
            }

            self._shared_browser = (
                await self._shared_playwright.chromium.launch(**launch_options)
            )
            logger.success("Launched browser with ZenRows proxy")

        return self._shared_browser

    async def get_authenticated_browser_and_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. "
                "To use this method, please initialize ScholarBrowserManager with an auth_manager."
            )

        await self.auth_manager.ensure_authenticate_async()

        browser = await self.get_browser()

        if self.auth_manager:
            await self.auth_manager.ensure_authenticate_async()
            auth_options = await self.auth_manager.get_auth_options()
        else:
            auth_options = {}

        stealth_options = self.stealth_manager.get_stealth_options()
        context_options = {**stealth_options, **auth_options}

        context = await browser.new_context(**context_options)

        # Apply stealth scripts
        await context.add_init_script(self.stealth_manager.get_init_script())
        await context.add_init_script(
            self.stealth_manager.get_dimension_spoofing_script()
        )
        await context.add_init_script(
            self.cookie_acceptor.get_auto_acceptor_script()
        )

        return browser, context

# EOF
