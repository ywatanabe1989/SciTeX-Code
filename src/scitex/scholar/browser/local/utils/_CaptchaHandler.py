#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 07:30:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/_CapthaHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import asyncio
import json
from scitex import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class CaptchaHandler:
    """Automatically handles CAPTCHA and 'I am not a robot' popups."""

    def __init__(self):
        self.name = self.__class__.__name__
        self.captcha_texts = [
            "I'm not a robot",
            "I am not a robot",
            "Not a robot",
            "Verify",
            "I'm human",
            "I am human",
        ]

        self.captcha_selectors = [
            "[id*='recaptcha']",
            "[class*='recaptcha']",
            ".g-recaptcha",
            "[aria-label*='not a robot']",
            "[title*='reCAPTCHA']",
            ".recaptcha-checkbox-border",
        ]

    async def inject_captcha_handler_async(self, context):
        """Inject auto-handler script for CAPTCHA."""
        script = f"""
(() => {{
    const captchaTexts = {json.dumps(self.captcha_texts)};
    const captchaSelectors = {json.dumps(self.captcha_selectors)};

    function handleCaptcha() {{
        // Try text-based CAPTCHA buttons
        for (const text of captchaTexts) {{
            const buttons = Array.from(document.querySelectorAll('button, div, span'));
            const match = buttons.find(btn =>
                btn.textContent.trim().toLowerCase().includes(text.toLowerCase()));
            if (match && match.offsetParent !== null) {{
                match.click();
                console.log('Auto-clicked CAPTCHA:', text);
                return true;
            }}
        }}

        // Try CAPTCHA selectors
        for (const selector of captchaSelectors) {{
            try {{
                const elements = document.querySelectorAll(selector);
                for (const elem of elements) {{
                    if (elem.offsetParent !== null) {{
                        elem.click();
                        console.log('Auto-clicked CAPTCHA:', selector);
                        return true;
                    }}
                }}
            }} catch (e) {{}}
        }}
        return false;
    }}

    // Check periodically
    const interval = setInterval(() => {{
        if (handleCaptcha()) {{
            clearInterval(interval);
        }}
    }}, 1000);

    // Stop after 30 seconds
    setTimeout(() => clearInterval(interval), 30000);
}})();
"""
        await context.add_init_script(script)

    async def handle_captcha_async(
        self, page: Page, wait_seconds: float = 2
    ) -> bool:
        """Try to handle 'I am not a robot' CAPTCHA."""
        await asyncio.sleep(wait_seconds)

        # Try text-based CAPTCHA buttons
        for text in self.captcha_texts:
            try:
                element = page.locator(f"*:has-text('{text}')").first
                if await element.is_visible():
                    await element.click()
                    logger.debug(f"Clicked CAPTCHA with text: {text}")
                    await asyncio.sleep(2)
                    return True
            except:
                continue

        # Try CAPTCHA selectors
        for selector in self.captcha_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    await element.click()
                    logger.debug(f"Clicked CAPTCHA element: {selector}")
                    await asyncio.sleep(2)
                    return True
            except:
                continue

        return False

    async def check_captcha_exists_async(self, page: Page) -> bool:
        """Check if a CAPTCHA is visible."""
        try:
            for selector in self.captcha_selectors:
                if await page.locator(selector).first.is_visible():
                    return True
            return False
        except:
            return False

# EOF
