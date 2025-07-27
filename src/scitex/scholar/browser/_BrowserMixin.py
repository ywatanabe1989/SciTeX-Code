#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 15:16:26 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_BrowserMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_BrowserMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from ._CookieAutoAcceptor import CookieAutoAcceptor


class BrowserMixin:
    """Mixin for browser-based strategies with common functionality."""

    def __init__(self):
        self.cookie_acceptor = CookieAutoAcceptor()

    async def create_browser_context(
        self, playwright_instance, **context_options
    ):
        """Create browser context with cookie auto-acceptance."""
        browser = await playwright_instance.chromium.launch(
            headless=getattr(self, "headless", True)
        )
        context = await browser.new_context(**context_options)

        # Inject cookie auto-acceptor
        await self.cookie_acceptor.inject_auto_acceptor(context)

        return browser, context

# EOF
