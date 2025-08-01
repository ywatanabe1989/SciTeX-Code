#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 21:46:49 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging

from ._BrowserMixin import BrowserMixin
from ._ChromeExtensionManager import ChromeExtensionManager
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)


class BrowserManager(BrowserMixin):
    """Manages a local browser instance with stealth enhancements."""

    def __init__(
        self,
        auth_manager=None,
        headless: bool = True,
        profile_name: str = "scholar_default",
    ):
        super().__init__(headless=headless)
        self.auth_manager = auth_manager
        if auth_manager is None:
            logger.warn(f"auth_manager not passed")
        self.extension_manager = ChromeExtensionManager(profile_name)
        self.stealth_manager = StealthManager()

    async def get_authenticated_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""

        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. Initialize BrowserManager with an auth_manager to use this method."
            )

        await self.auth_manager.ensure_authenticated()

        # Use browser with Chrome profile for extension support
        browser = await self.get_browser_with_profile()

        # Create context with stealth options and auth cookies
        context_options = {}
        if self.auth_manager and await self.auth_manager.is_authenticated():
            try:
                auth_session = await self.auth_manager.authenticate()
                if auth_session and "cookies" in auth_session:
                    context_options["storage_state"] = {
                        "cookies": auth_session["cookies"]
                    }
            except Exception as e:
                logger.warning(f"Failed to get auth session: {e}")

        # Create stealth context with Chrome profile data
        context = await self._create_stealth_context(
            browser, **context_options
        )

        return browser, context

    async def _create_stealth_context(
        self, browser: Browser, **context_options
    ) -> BrowserContext:
        """Creates a new browser context with stealth options applied."""
        stealth_options = self.stealth_manager.get_stealth_options()
        merged_options = {**stealth_options, **context_options}
        context = await browser.new_context(**merged_options)
        await context.add_init_script(self.stealth_manager.get_init_script())
        await self.cookie_acceptor.inject_auto_acceptor(context)
        return context

    async def get_browser_with_profile(self) -> Browser:
        """Get browser instance with Chrome profile loaded for extensions."""
        if (
            self._shared_browser is None
            or self._shared_browser.is_connected() is False
        ):
            if self._shared_playwright is None:
                self._shared_playwright = await async_playwright().start()

            # Build extension paths for explicit loading
            extension_dirs = []
            extensions_path = (
                self.extension_manager.profile_dir / "Default" / "Extensions"
            )
            if extensions_path.exists():
                for ext_dir in extensions_path.iterdir():
                    if ext_dir.is_dir():
                        # Find the latest version directory
                        version_dirs = [
                            d for d in ext_dir.iterdir() if d.is_dir()
                        ]
                        if version_dirs:
                            latest_version = max(
                                version_dirs, key=lambda x: x.name
                            )
                            extension_dirs.append(str(latest_version))
                            logger.info(
                                f"Found extension: {ext_dir.name} -> {latest_version}"
                            )

            # Enhanced stealth launch arguments
            stealth_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-default-apps",
                "--enable-extensions",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-plugins-discovery",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-domain-reliability",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-popup-blocking",
                "--window-size=1920,1080",
            ]

            # Choose between user-data-dir or load-extension (not both)
            if extension_dirs:
                # Use explicit extension loading
                stealth_args.extend(
                    [
                        f"--load-extension={','.join(extension_dirs)}",
                        "--disable-extensions-file-access-check",
                    ]
                )
                logger.info(
                    f"Loading {len(extension_dirs)} extensions explicitly"
                )

                # Use regular launch with explicit extensions
                self._shared_browser = (
                    await self._shared_playwright.chromium.launch(
                        headless=self.headless,
                        args=stealth_args,
                    )
                )
            else:
                # Fallback to user-data-dir if no extensions found
                stealth_args.append(
                    f"--user-data-dir={self.extension_manager.profile_dir}"
                )
                logger.info("Using user-data-dir for profile")

                self._shared_browser = (
                    await self._shared_playwright.chromium.launch(
                        headless=self.headless,
                        args=stealth_args,
                    )
                )
        return self._shared_browser

    async def has_lean_library_pdf_button(self, page, url):
        await page.goto(url)

        # Wait for Lean Library to load and process
        await page.wait_for_timeout(3000)

        # Look for Lean Library PDF indicators
        pdf_selectors = [
            '[data-lean-library="pdf"]',
            ".lean-library-pdf",
            'button:has-text("PDF")',
            'a:has-text("Get PDF")',
            ".ll-pdf-button",
        ]

        for selector in pdf_selectors:
            pdf_button = await page.query_selector(selector)
            if pdf_button:
                return True

        return False

    async def setup_extensions(self):
        """Setup extensions interactively if not installed."""
        status = await self.extension_manager.check_extensions_installed()
        missing = [k for k, v in status.items() if not v]

        if missing:
            print(f"Missing extensions: {len(missing)}")
            await self.extension_manager.install_extensions_interactive()
        else:
            print("All extensions already installed")

    async def check_lean_library_active(self, page, url):
        """Check if Lean Library provides PDF access."""
        return await self.extension_manager.check_lean_library_active(
            page, url
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)


if __name__ == "__main__":
    import asyncio

    async def main():
        """Example usage of BrowserManager with stealth features."""
        # Initialize browser manager
        manager = BrowserManager(
            auth_manager=None,
            headless=False,  # Start in headless mode
        )

        # Chrome extensions one-time interactive setup
        await manager.setup_extensions()

        # Create a new page with stealth features
        page = await manager.new_page()
        context = manager.contexts[-1]

        url_science = "https://www.science.org/doi/10.1126/science.aao0702"
        if await manager.has_lean_library_pdf_button(page, url_science):
            print("PDF Lean Library Button Found")

        # Navigate to a site that checks for bots
        await page.goto("https://bot.sannysoft.com/")
        await page.wait_for_timeout(2000)

        # Take screenshot to verify stealth
        await page.screenshot(path="stealth_test.png")
        print("Screenshot saved as stealth_test.png")

        # Example: Handle cookie consent automatically
        await page.goto("https://www.cookiebot.com/en/")
        await page.wait_for_timeout(
            3000
        )  # Cookie acceptor works automatically

        # Check if we passed bot detection
        # This is a simple check - real sites have more sophisticated detection
        content = await page.content()
        if "HeadlessChrome" not in content:
            print("✓ Passed basic bot detection")
        else:
            print("✗ Failed bot detection")

        # Show browser for debugging (only works if started with headless=False)
        # await manager.show()

        # Access multiple pages
        page2 = await context.new_page()
        await page2.goto("https://example.com")

        print(f"Total pages open: {len(context.pages)}")

        # Close specific page
        await page2.close()

        print("Browser manager closed successfully")

    # Run the example
    asyncio.run(main())

# python -m scitex.scholar.browser.local._BrowserManager

# WebDriver preresent (failed) # why?

# EOF
