#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-06 17:05:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging

from ...config._ScholarConfig import ScholarConfig
from ._BrowserMixin import BrowserMixin
from .utils._ChromeExtensionManager import ChromeExtensionManager
from .utils._CookieAutoAcceptor import CookieAutoAcceptor
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)


class BrowserManager(BrowserMixin):
    """Manages a local browser instance with stealth enhancements and invisible mode."""

    def __init__(
        self,
        browser_mode=None,
        auth_manager=None,
        config: ScholarConfig = None,
    ):
        """
        Initialize BrowserManager with invisible browser capabilities.

        Args:
            auth_manager: Authentication manager instance
            config: Scholar configuration instance
        """
        # Store scholar_config for use by components like ChromeExtensionManager
        self.scholar_config = config or ScholarConfig()

        browser_mode = self.scholar_config.resolve(
            "browser_mode", browser_mode, default="interactive"
        )
        super().__init__(mode=browser_mode)

        self._set_interactive_or_stealth(browser_mode)

        # Library Authentication
        self.auth_manager = auth_manager
        if auth_manager is None:
            logger.fail(
                f"auth_manager not passed. University Authentication will not be enabled."
            )

        # Chrome Extension
        logger.warn(f"Profile name is set as extension in hardcoding")
        self.extension_manager = ChromeExtensionManager(
            profile_name="extension", config=self.scholar_config
        )

        # Stealth
        self.stealth_manager = StealthManager(
            self.viewport_size, self.spoof_dimension, self.window_position
        )

        # Cookie
        self.cookie_acceptor = CookieAutoAcceptor()

    def _set_interactive_or_stealth(self, browser_mode):
        # Interactive or Stealth
        if browser_mode == "interactive":
            self.headless = False
            self.spoof_dimension = False
            self.viewport_size = (1200, 800)
            self.window_position = (100, 100)
        elif browser_mode == "stealth":
            # Must be False for dimension spoofing to work
            self.headless = False
            self.spoof_dimension = True
            self.viewport_size = (1, 1)
            self.window_position = (0, 0)
        else:
            raise ValueError(
                "browser_mode must be eighther of 'interactive' or 'stealth'"
            )
        logger.warn("Browser initialized:")
        logger.warn(f"headless: {self.headless}")
        logger.warn(f"spoof_dimension: {self.spoof_dimension}")
        logger.warn(f"viewport_size: {self.viewport_size}")
        logger.warn(f"window_position: {self.window_position}")

    async def get_authenticate_async_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies and extensions loaded."""

        # Ensure auth_manager is passed
        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. To use this method, please initialize BrowserManager with an auth_manager."
            )

        # Ensure auth_manager has authenticate_async info
        await self.auth_manager.ensure_authenticate_async()

        # Use browser with Chrome profile for extension support
        browser = await self.get_browser_async_with_profile()

        # With persistent context, we already have the profile and extensions loaded
        if hasattr(self, "_shared_context") and self._shared_context:
            context = self._shared_context
            logger.success(
                "Using persistent context with profile and extensions"
            )
        else:
            # Fallback to regular context creation if persistent context not available
            logger.warning("Falling back to regular context creation")
            context_options = {}
            if (
                self.auth_manager
                and await self.auth_manager.is_authenticate_async()
            ):
                try:
                    auth_session = await self.auth_manager.authenticate_async()
                    if auth_session and "cookies" in auth_session:
                        context_options["storage_state"] = {
                            "cookies": auth_session["cookies"]
                        }
                except Exception as e:
                    logger.warning(f"Failed to get auth session: {e}")

            context = await self._create_stealth_context_async(
                browser, **context_options
            )

        return browser, context

    async def _create_stealth_context_async(
        self, browser: Browser, **context_options
    ) -> BrowserContext:
        """Creates a new browser context with stealth options and invisible mode applied."""
        stealth_options = self.stealth_manager.get_stealth_options()

        merged_options = {**stealth_options, **context_options}
        context = await browser.new_context(**merged_options)

        # Apply stealth script
        await context.add_init_script(self.stealth_manager.get_init_script())
        await context.add_init_script(
            self.stealth_manager.get_dimension_spoofing_script()
        )
        await context.add_init_script(
            self.cookie_acceptor.get_auto_acceptor_script()
        )
        return context

    async def get_browser_async_with_profile(self) -> Browser:
        if (
            self._shared_browser is None
            or self._shared_browser.is_connected() is False
        ):
            await self.auth_manager.ensure_authenticate_async()
            await self._ensure_playwright_started_async()
            await self._ensure_extensions_installed_async()
            await self._launch_persistent_context_async()
        return self._shared_browser

    async def _ensure_playwright_started_async(self):
        if self._shared_playwright is None:
            self._shared_playwright = await async_playwright().start()

    async def _ensure_extensions_installed_async(self):
        if not await self.extension_manager.check_extensions_installed_async():
            logger.error("Chrome extensions not verified")
            try:
                logger.warn("Trying install extensions")
                await self.extension_manager.install_extensions_manually_if_not_installed_async()
            except Exception as e:
                logger.error(f"Installation failed: {str(e)}")

        # Configure extensions after installation/verification
        try:
            logger.info("Configuring extensions for optimal operation...")
            await self.extension_manager.configure_all_extensions_async()
        except Exception as e:
            logger.error(f"Extension configuration failed: {str(e)}")

    async def _launch_persistent_context_async(self):
        launch_options = self._build_launch_options()

        # Clean up any existing singleton lock files that might prevent browser launch
        profile_dir = self.extension_manager.profile_dir

        # Multiple possible lock file locations
        lock_files = [
            profile_dir / "SingletonLock",
            profile_dir / "SingletonSocket",
            profile_dir / "SingletonCookie",
            profile_dir / "lockfile",
        ]

        removed_locks = 0
        for lock_file in lock_files:
            if lock_file.exists():
                try:
                    lock_file.unlink()
                    logger.info(
                        f"🧹 Removed Chrome lock file: {lock_file.name}"
                    )
                    removed_locks += 1
                except Exception as e:
                    logger.warning(f"Could not remove {lock_file.name}: {e}")

        if removed_locks > 0:
            logger.info(f"🧹 Cleaned up {removed_locks} Chrome lock files")
            # Wait a moment for the system to release file handles
            import time

            time.sleep(1)

        # Kill any lingering Chrome processes using this profile
        try:
            import subprocess

            profile_path_str = str(profile_dir)
            # Find and kill Chrome processes using this profile
            result = subprocess.run(
                ["pkill", "-f", f"user-data-dir={profile_path_str}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info(
                    "🧹 Killed lingering Chrome processes for this profile"
                )
                time.sleep(2)  # Give processes time to fully terminate
        except Exception as e:
            logger.debug(f"Chrome process cleanup attempt: {e}")

        # This show_asyncs a small screen with 4 extensions show_asyncn
        launch_options["headless"] = False
        self._shared_context = (
            await self._shared_playwright.chromium.launch_persistent_context(
                **launch_options
            )
        )

        await self._apply_stealth_scripts_async()
        
        # Load authentication cookies into the persistent context
        await self._load_auth_cookies_to_persistent_context_async()

        self._shared_browser = self._shared_context.browser

    def _build_launch_options(self):
        stealth_args = self.stealth_manager.get_stealth_options_additional()
        extension_args = self.extension_manager.get_extension_args()
        launch_args = stealth_args + extension_args

        # Debug: Show window args for stealth mode
        if self.spoof_dimension:
            window_args = [arg for arg in launch_args if "window-" in arg]
            logger.info(f"🎭 Stealth window args: {window_args}")

        return {
            "user_data_dir": str(self.extension_manager.profile_dir),
            "headless": self.headless,
            "args": launch_args,
            "viewport": {
                "width": self.viewport_size[0],
                "height": self.viewport_size[1],
            },
            "screen": {
                "width": self.viewport_size[0],
                "height": self.viewport_size[1],
            },
        }

    async def _apply_stealth_scripts_async(self):
        if self.spoof_dimension:
            await self._shared_context.add_init_script(
                self.stealth_manager.get_init_script()
            )
            await self._shared_context.add_init_script(
                self.stealth_manager.get_dimension_spoofing_script()
            )
            await self._shared_context.add_init_script(
                self.cookie_acceptor.get_auto_acceptor_script()
            )

    async def _load_auth_cookies_to_persistent_context_async(self):
        """Load authentication cookies into the persistent browser context."""
        if not self.auth_manager:
            logger.debug("No auth_manager available, skipping cookie loading")
            return
            
        try:
            # Check if we have authentication
            if await self.auth_manager.is_authenticate_async(verify_live=False):
                cookies = await self.auth_manager.get_auth_cookies_async()
                if cookies:
                    await self._shared_context.add_cookies(cookies)
                    logger.success(f"Loaded {len(cookies)} authentication cookies into persistent browser context")
                else:
                    logger.debug("No cookies available from auth manager")
            else:
                logger.debug("Not authenticated, skipping cookie loading")
        except Exception as e:
            logger.warning(f"Failed to load authentication cookies: {e}")

    async def check_lean_library_active_async(self, page, url, timeout_sec=5):
        """Check if Lean Library provides PDF access."""
        return await self.extension_manager.check_lean_library_active_async(
            page, url, timeout_sec=timeout_sec
        )

    # def get_page(self):
    #     """Get a new page with proper context management."""

    #     class PageManager:
    #         def __init__(self, browser_manager):
    #             self.browser_manager = browser_manager
    #             self.browser = None
    #             self.context = None
    #             self.page = None

    #         async def __aenter__(self):
    #             self.browser, self.context = (
    #                 await self.browser_manager.get_authenticate_async_context()
    #             )
    #             self.page = await self.context.new_page()

    #             # Inject advanced stealth scripts for Cloudflare evasion
    #             stealth_manager = StealthManager(
    #                 viewport_size=self.browser_manager.viewport_size,
    #                 spoof_dimension=self.browser_manager.spoof_dimension,
    #                 window_position=self.browser_manager.window_position,
    #             )
    #             await stealth_manager.inject_stealth_scripts(self.page)
    #             await stealth_manager.add_human_behavior_async(self.page)

    #             return self.page

    #         async def __aexit__(self, exc_type, exc_val, exc_tb):
    #             if self.page:
    #                 await self.page.close()

    #     return PageManager(self)

    async def take_screenshot_safe_async(
        self, page, path: str, description: str = "", timeout: int = 30000
    ):
        """Take screenshot in stealth mode without viewport changes."""
        try:
            await page.screenshot(path=path, timeout=timeout, full_page=True)
            logger.info(f"Screenshot saved: {description} -> {path}")

        except Exception as e:
            logger.warning(f"Screenshot failed for {description}: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)


if __name__ == "__main__":

    async def main(browser_mode="interactive"):
        """Example usage of BrowserManager with stealth features."""
        from ...auth import AuthenticationManager

        auth_manager = AuthenticationManager()
        browser_manager = BrowserManager(
            browser_mode=browser_mode,
            auth_manager=auth_manager,
        )

        browser = await browser_manager.get_browser_async_with_profile()
        page = await browser_manager._shared_context.new_page()

        # Test sites configuration
        test_sites = [
            {
                "name": "OpenAthens",
                "url": "https://my.openathens.net/account",
                "screenshot": f"/tmp/openathens_test-{browser_mode}.png",
                "description": "OpenAthens autehntication test",
            },
            {
                "name": "Lean Library",
                "url": "https://www.science.org/doi/10.1126/science.aao0702",
                "screenshot": f"/tmp/lean_library_test-{browser_mode}.png",
                "description": "Lean Library functionality with stealth",
            },
            {
                "name": "Bot Detection",
                "url": "https://bot.sannysoft.com/",
                "screenshot": f"/tmp/stealth_test_results-{browser_mode}.png",
                "description": "Bot detection test",
            },
            {
                "name": "Cookie Test",
                "url": "https://www.whatismybrowser.com/detect/are-cookies-enabled",
                "screenshot": f"/tmp/cookie_test-{browser_mode}.png",
                "description": "Cookie acceptance",
            },
            {
                "name": "Popup Test",
                "url": "https://popuptest.com/",
                "screenshot": f"/tmp/popup_test-{browser_mode}.png",
                "description": "Popup blocking",
            },
            {
                "name": "CAPTCHA Test",
                "url": "https://www.google.com/recaptcha/api2/demo",
                "screenshot": f"/tmp/captcha_test-{browser_mode}.png",
                "description": "CAPTCHA solving",
            },
        ]

        # Run tests for each site
        for site in test_sites:
            logger.info(f"🧪 Testing {site['name']}...")
            await page.goto(site["url"])
            await browser_manager.stealth_manager.human_delay_async(2000, 3000)

            await browser_manager.take_screenshot_safe_async(
                page, site["screenshot"], site["description"]
            )

            logger.info(f"  - {site['screenshot']} - {site['description']}")

        logger.success("🎯 All extension tests completed!")

    import argparse

    parser = argparse.ArgumentParser(description="BrowserManager testing")
    parser.add_argument(
        "--mode",
        choices=["interactive", "stealth"],
        default="interactive",
        help="Browser mode (default: interactive)",
    )

    args = parser.parse_args()
    asyncio.run(main(browser_mode=args.mode))


# python -m scitex.scholar.browser.local._BrowserManager

# EOF
