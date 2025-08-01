#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 19:14:21 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/utils/_StealthManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_StealthManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import random

from playwright.async_api import Browser, BrowserContext, Page

from scitex import logging

logger = logging.getLogger(__name__)


class StealthManager:
    def __init__(self):
        # Updated user agents with current Chrome versions
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
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

    def get_stealth_options(self) -> dict:
        return {
            "viewport": self.get_random_viewport(),
            "user_agent": self.get_random_user_agent(),
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com/",
            },
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }

    def get_init_script(self) -> str:
        return """
// Remove webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

// Set realistic languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Mock chrome object
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// Mock plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {
            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        },
        {
            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
            description: "Portable Document Format", 
            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            length: 1,
            name: "Chrome PDF Viewer"
        }
    ],
});

// Set hardware concurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8,
});

// Mock permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// Mock WebGL vendor
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter(parameter);
};

// Hide automation indicators
['webdriver', '__driver_evaluate', '__webdriver_evaluate', '__selenium_evaluate', 
 '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped', 
 '__selenium_unwrapped', '__fxdriver_unwrapped', '__webdriver_script_function', 
 '__webdriver_script_func', '__webdriver_script_fn', '__fxdriver_script_fn',
 '__selenium_script_fn', '__webdriver_func', '__webdriver_fn'].forEach(prop => {
    delete window[prop];
    delete document[prop];
});

// Fix toString issues
window.navigator.chrome = {
    runtime: {},
};

// Override the `languages` property
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// Fix Notification permission
Object.defineProperty(navigator, 'permissions', {
    get: () => {
        return {
            query: async (permissionDesc) => {
                if (permissionDesc.name === 'notifications') {
                    return Promise.resolve({ state: 'granted' });
                }
                return Promise.resolve({ state: 'prompt' });
            }
        };
    }
});
"""

    async def human_delay(self, min_ms: int = 1000, max_ms: int = 3000):
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


if __name__ == "__main__":
    import asyncio

    from playwright.async_api import async_playwright

    async def main():
        """Example usage of StealthManager for bot detection evasion."""
        stealth_manager = StealthManager()

        async with async_playwright() as p:
            # Launch browser with stealth options
            browser = await p.chromium.launch(
                headless=False,  # Use visible mode to see the effect
                **stealth_manager.get_stealth_options(),
            )

            # Create context with stealth options
            context = await browser.new_context(
                **stealth_manager.get_stealth_options()
            )

            # Inject stealth scripts
            await context.add_init_script(stealth_manager.get_init_script())

            # Create a new page
            page = await context.new_page()

            # Test 1: Bot detection site
            print("Testing stealth on bot detection site...")
            await page.goto("https://bot.sannysoft.com/")
            await stealth_manager.human_delay(2000, 3000)

            # Take screenshot
            await page.screenshot(path="stealth_test_results.png")
            print("Screenshot saved as stealth_test_results.png")

            # Test 2: Human-like interactions
            print("\nTesting human-like behavior...")
            await page.goto("https://www.google.com")

            # Human-like mouse movement
            await stealth_manager.human_mouse_move(page)

            # Human-like scrolling
            await stealth_manager.human_scroll(page)

            # Human-like typing
            search_box = 'textarea[name="q"], input[name="q"]'
            if await page.locator(search_box).count() > 0:
                await stealth_manager.human_type(
                    page, search_box, "playwright stealth mode"
                )
                print("Typed search query with human-like delays")

            # Test 3: Check fingerprint
            await page.goto("https://fingerprintjs.github.io/fingerprintjs/")
            await stealth_manager.human_delay(3000, 4000)

            # Extract some detection results
            try:
                visitor_id = await page.locator(".visitor-id").inner_text()
                print(f"\nFingerprint visitor ID: {visitor_id}")
            except:
                print("\nCould not extract fingerprint data")

            # Clean up
            await browser.close()

        print("\nStealth manager test completed!")

    # Run the example
    asyncio.run(main())

# python -m scitex.scholar.browser.local.utils._StealthManager

# EOF
