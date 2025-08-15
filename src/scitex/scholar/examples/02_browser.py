#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 01:30:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/scholar/examples/browser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./scholar/examples/browser.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.browser import ScholarBrowserManager


async def main_async():
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode="interactive",
        auth_manager=ScholarAuthManager(),
    )

    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    page = await context.new_page()

    await page.goto("https://scitex.ai")

    await asyncio.sleep(10)


asyncio.run(main_async())

# EOF
