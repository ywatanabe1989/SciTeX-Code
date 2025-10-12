#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 00:41:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/automation/CookieHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/automation/CookieHandler.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

import json

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


class CookieAutoAcceptor:
    """Automatically handles cookie consent banners on web pages."""

    def __init__(self):
        self.name = self.__class__.__name__
        self.cookie_texts = [
            "Accept all cookies",
            "Accept All",
            "Accept cookies",
            "Accept",
            "I Accept",
            "OK",
            "Continue",
            "Agree",
            "Continue without an account",
            "Don't ask again",
        ]

        self.selectors = [
            "[data-testid*='accept']",
            "[id*='accept']",
            "[class*='accept']",
            "button[aria-label*='Accept']",
            ".cookie-banner button:first-of-type",
            "#cookie-banner button:first-of-type",
        ]

    async def inject_auto_acceptor_async(self, context):
        """Inject auto-acceptor script into browser context."""
        logger.warning(f"{self.name}: Use get_auto_acceptor_script instead")
        script = self.get_auto_acceptor_script()
        await context.add_init_script(script)
        logger.debug(f"{self.name}: Injected auto-acceptor script")

    def get_auto_acceptor_script(
        self,
    ):
        return f"""
        (() => {{
            const cookieTexts = {json.dumps(self.cookie_texts)};
            const selectors = {json.dumps(self.selectors)};

            function acceptCookies() {{
                // Try text-based buttons
                for (const text of cookieTexts) {{
                    const buttons = Array.from(document.querySelectorAll('button, a'));
                    const match = buttons.find(btn =>
                        btn.textContent.trim().toLowerCase() === text.toLowerCase() &&
                        !btn.hasAttribute('data-scitex-no-auto-click') &&  // SKIP SciTeX buttons!
                        !btn.closest('[data-scitex-no-auto-click]') &&  // SKIP if inside SciTeX container!
                        btn.id !== 'stop-automation-btn' &&  // SKIP manual download button by ID!
                        !btn.id.includes('scitex')  // SKIP any scitex-related button
                    );
                    if (match && match.offsetParent !== null) {{
                        match.click();
                        console.log('Auto-accepted cookies:', text);
                        return true;
                    }}
                }}

                // Try CSS selectors
                for (const selector of selectors) {{
                    try {{
                        const elements = document.querySelectorAll(selector);
                        for (const elem of elements) {{
                            // SKIP SciTeX buttons!
                            if (elem.hasAttribute('data-scitex-no-auto-click') ||
                                elem.closest('[data-scitex-no-auto-click]') ||
                                elem.id === 'stop-automation-btn' ||  // SKIP by ID!
                                elem.id.includes('scitex')) {{  // SKIP any scitex ID
                                continue;
                            }}

                            if (elem.offsetParent !== null) {{
                                elem.click();
                                console.log('Auto-accepted cookies:', selector);
                                return true;
                            }}
                        }}
                    }} catch (e) {{}}
                }}
                return false;
            }}

            // Check periodically
            const interval = setInterval(() => {{
                if (acceptCookies()) {{
                    clearInterval(interval);
                }}
            }}, 1000);

            // Stop after 30 seconds
            setTimeout(() => clearInterval(interval), 30000);
        }})();
        """

    async def check_cookie_banner_exists_async(self, page: Page) -> bool:
        """Check if a cookie banner is still visible."""
        try:
            exists = await page.locator(
                ".cookie-banner, [class*='cookie']"
            ).first.is_visible()
            logger.debug(f"{self.name}: Cookie banner exists: {exists}")
            return exists
        except:
            logger.debug(f"{self.name}: Cookie banner not found")
            return False


def main(args):
    """Demonstrate CookieAutoAcceptor functionality."""
    import asyncio

    from playwright.async_api import async_playwright

    from ..debugging import browser_logger

    async def demo():
        acceptor = CookieAutoAcceptor()

        async with async_playwright() as p:
            logger.info("Starting demo")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()

            await context.add_init_script(acceptor.get_auto_acceptor_script())

            page = await context.new_page()

            logger.info("Navigating to https://www.springer.com")
            await page.goto("https://www.springer.com", timeout=30000)

            logger.debug("Waiting for cookie banner detection")
            await asyncio.sleep(5)

            banner_exists = await acceptor.check_cookie_banner_exists_async(page)

            logger.success("Auto-acceptor demo complete")

            await browser.close()

    asyncio.run(demo())
    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="CookieAutoAcceptor demo")
    return parser.parse_args()


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# python -m scitex.browser.automation.CookieHandler

# EOF
