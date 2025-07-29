#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 07:45:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_StealthManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/_StealthManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import logging
import random

from playwright.async_api import Browser, BrowserContext, Page

logger = logging.getLogger(__name__)


class StealthManager:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]
        self.viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1280, "height": 720},
        ]

    def get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)

    def get_random_viewport(self) -> dict:
        return random.choice(self.viewports)

    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)

    async def human_click(self, page: Page, element):
        await element.hover()
        await self.human_delay(200, 500)
        await element.click()

    async def human_mouse_move(self, page: Page):
        await page.mouse.move(
            random.randint(100, 800), random.randint(100, 600)
        )

    async def human_scroll(self, page: Page):
        scroll_distance = random.randint(300, 800)
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await self.human_delay(500, 1500)

    async def human_type(self, page: Page, selector: str, text: str):
        element = page.locator(selector)
        await element.click()
        for char in text:
            await element.type(char)
            await self.human_delay(50, 200)

    def get_stealth_options(self) -> dict:
        return {
            "viewport": self.get_random_viewport(),
            "user_agent": self.get_random_user_agent(),
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

    def get_init_script(self) -> str:
        return """
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

# EOF
