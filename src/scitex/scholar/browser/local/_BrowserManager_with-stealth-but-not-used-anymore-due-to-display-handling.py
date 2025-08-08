#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 20:55:27 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/_BrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_BrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import subprocess
import time
from datetime import datetime

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging

from ...config._ScholarConfig import ScholarConfig
from ._BrowserMixin import BrowserMixin
from .utils._ChromeProfileManager import ChromeProfileManager
from .utils._CookieAutoAcceptor import CookieAutoAcceptor
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)

"""
Browser Manager with persistent context support.

_persistent_context is a **persistent browser context** that stays alive across multiple operations.

## Regular vs Persistent Context

**Regular context** (new each time):
```python
browser = await playwright.chromium.launch()
context = await browser.new_context()  # New context each time
page = await context.new_page()
```

**Persistent context** (reused):
```python
# Created once in _launch_persistent_context_async()
self._persistent_context = await self._persistent_playwright.chromium.launch_persistent_context(
    user_data_dir=str(profile_dir),  # Persistent profile
    headless=False,
    args=[...extensions...]
)

# Reused multiple times
if hasattr(self, "_persistent_context") and self._persistent_context:
    context = self._persistent_context  # Same context
```

## Benefits of Persistent Context

1. **Extensions persist** - Extensions loaded once, available for all pages
2. **Authentication cookies persist** - No need to re-login
3. **Profile data persistent** - Bookmarks, history, settings maintained
4. **Performance** - Faster page creation (no browser restart)
5. **Session continuity** - Maintains login state across operations

## In Your Code

`_persistent_context` is set in `_launch_persistent_context_async()` and reused in `get_authenticated_browser_and_context_async()`. This allows multiple pages to share the same authenticated, extension-enabled browser session.
"""


class BrowserManager(BrowserMixin):
    """Manages a local browser instance with stealth enhancements and invisible mode."""

    def __init__(
        self,
        browser_mode=None,
        auth_manager=None,
        chrome_profile_name=None,
        config: ScholarConfig = None,
    ):
        """
        Initialize BrowserManager with invisible browser capabilities.

        Args:
            auth_manager: Authentication manager instance
            config: Scholar configuration instance
        """
        # Store scholar_config for use by components like ChromeProfileManager
        self.config = config or ScholarConfig()

        self.browser_mode = self.config.resolve(
            "browser_mode", browser_mode, default="interactive"
        )
        super().__init__(mode=self.browser_mode)

        self._set_interactive_or_stealth(browser_mode)

        # Library Authentication
        self.auth_manager = auth_manager
        if auth_manager is None:
            logger.fail(
                f"auth_manager not passed. University Authentication will not be enabled."
            )

        # Chrome Extension
        self.chrome_profile_manager = ChromeProfileManager(
            chrome_profile_name, config=self.config
        )

        # Stealth
        self.stealth_manager = StealthManager(
            self.viewport_size, self.spoof_dimension
        )

        # Cookie
        self.cookie_acceptor = CookieAutoAcceptor()

        # Initialize persistent browser attributes
        self._persistent_browser = None
        self._persistent_context = None
        self._persistent_playwright = None

    def _set_interactive_or_stealth(self, browser_mode):
        # Interactive or Stealth
        if browser_mode == "interactive":
            self.headless = False
            self.spoof_dimension = False
            self.viewport_size = (1920, 1080)
            self.display = 0
        elif browser_mode == "stealth":
            # Must be False for dimension spoofing to work
            self.headless = False
            self.spoof_dimension = True
            # This only affects internal viewport, not window size
            # self.viewport_size = (1, 1)
            self.viewport_size = (1920, 1080)
            self.display = 99
        else:
            raise ValueError(
                "browser_mode must be eighther of 'interactive' or 'stealth'"
            )
        logger.warn("Browser initialized:")
        logger.warn(f"headless: {self.headless}")
        logger.warn(f"spoof_dimension: {self.spoof_dimension}")
        logger.warn(f"viewport_size: {self.viewport_size}")

    async def get_authenticated_browser_and_context_async(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies and extensions loaded."""

        # Ensure auth_manager is passed
        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. "
                "To use this method, please initialize BrowserManager with an auth_manager."
            )

        # Ensure auth_manager has authenticate_async info
        await self.auth_manager.ensure_authenticate_async()

        # Use browser with Chrome profile for extension support
        browser = (
            await self._get_persistent_browser_with_profile_but_not_with_auth_async()
        )

        # With persistent context, we already have the profile and extensions loaded
        if hasattr(self, "_persistent_context") and self._persistent_context:
            context = self._persistent_context
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
        # stealth_options = self.stealth_manager.get_stealth_options()
        stealth_options = {}
        context = await browser.new_context(
            {**stealth_options, **context_options}
        )

        # # Apply stealth script
        # await context.add_init_script(self.stealth_manager.get_init_script())
        # await context.add_init_script(
        #     self.stealth_manager.get_dimension_spoofing_script()
        # )
        # await context.add_init_script(
        #     self.cookie_acceptor.get_auto_acceptor_script()
        # )
        return context

    # ########################################
    # Persistent Context
    # ########################################
    async def _get_persistent_browser_with_profile_but_not_with_auth_async(
        self,
    ) -> Browser:
        if (
            self._persistent_browser is None
            or self._persistent_browser.is_connected() is False
        ):
            await self.auth_manager.ensure_authenticate_async()
            await self._ensure_playwright_started_async()
            await self._ensure_extensions_installed_async()
            await self._launch_persistent_context_async()
        return self._persistent_browser

    async def _ensure_playwright_started_async(self):
        if self._persistent_playwright is None:
            self._persistent_playwright = await async_playwright().start()

    async def _ensure_extensions_installed_async(self):
        if not self.chrome_profile_manager.check_extensions_installed():
            logger.error("Chrome extensions not verified")
            try:
                logger.warn("Trying install extensions")
                await self.chrome_profile_manager.install_extensions_manually_if_not_installed_async()
            except Exception as e:
                logger.error(f"Installation failed: {str(e)}")

    async def _launch_persistent_context_async(self):
        launch_options = self._build_launch_options()

        # Clean up any existing singleton lock files that might prevent browser launch
        profile_dir = self.chrome_profile_manager.profile_dir

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
                    logger.info(f"Removed Chrome lock file: {lock_file.name}")
                    removed_locks += 1
                except Exception as e:
                    logger.warning(f"Could not remove {lock_file.name}: {e}")

        if removed_locks > 0:
            logger.info(f"Cleaned up {removed_locks} Chrome lock files")
            # Wait a moment for the system to release file handles
            time.sleep(1)

        # Kill any lingering Chrome processes using this profile
        try:
            profile_path_str = str(profile_dir)
            # Find and kill Chrome processes using this profile
            result = subprocess.run(
                ["pkill", "-f", f"user-data-dir={profile_path_str}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info(
                    "Killed lingering Chrome processes for this profile"
                )
                time.sleep(2)  # Give processes time to fully terminate
        except Exception as e:
            logger.debug(f"Chrome process cleanup attempt: {e}")

        # This show_asyncs a small screen with 4 extensions show_asyncn
        launch_options["headless"] = False
        self._persistent_context = await self._persistent_playwright.chromium.launch_persistent_context(
            **launch_options
        )

        await self._close_unwanted_extension_pages_async()
        asyncio.create_task(self._close_unwanted_extension_pages_async())
        await self._apply_stealth_scripts_to_persistent_context_async()
        await self._load_auth_cookies_to_persistent_context_async()
        self._persistent_browser = self._persistent_context.browser

    async def _close_unwanted_extension_pages_async(self):
        await asyncio.sleep(1)

        for _ in range(20):
            try:
                unwanted_pages = [
                    page
                    for page in self._persistent_context.pages
                    if (
                        "chrome-extension://" in page.url
                        or "app.pbapi.xyz" in page.url
                        or "options.html" in page.url
                        # or "page:blacnk" in page.url
                    )
                ]

                if not unwanted_pages:
                    logger.info("Extension cleanup completed")
                    break

                # Ensure context stays alive
                if len(self._persistent_context.pages) == len(unwanted_pages):
                    await self._persistent_context.new_page()

                for page in unwanted_pages:
                    await page.close()
                    logger.info(f"Closed unwanted page: {page.url}")

            except Exception as e:
                logger.debug(f"Cleanup attempt failed: {e}")

            await asyncio.sleep(2)

    def _verify_xvfb_running(self):
        """Verify Xvfb virtual display is running"""
        try:
            result = subprocess.run(
                ["xdpyinfo", "-display", f":{self.display}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                logger.success(f"Xvfb display :{self.display} is running")
                return True
            else:
                logger.error(f"Xvfb display :{self.display} not found")
                return False
        except Exception as e:
            logger.error(f"Cannot verify Xvfb: {e}")
            return False

    def _build_launch_options(self):
        # stealth_args = self.stealth_manager.get_stealth_options_additional()
        stealth_args = []
        extension_args = self.chrome_profile_manager.get_extension_args()

        if self.spoof_dimension:
            if self._verify_xvfb_running():
                stealth_args.extend(
                    [
                        "--display=:99",
                        "--window-size=1920,1080",
                    ]
                )
            else:
                raise RuntimeError("Xvfb not running")

        no_welcome_args = [
            "--disable-extensions-file-access-check",
            "--disable-extensions-http-throttling",
            "--disable-component-extensions-with-background-pages",
        ]

        launch_args = extension_args + stealth_args + no_welcome_args

        # Debug: Show window args for stealth mode
        if self.spoof_dimension:
            window_args = [arg for arg in launch_args if "window-" in arg]
            logger.warn(f"Stealth window args: {window_args}")

        return {
            "user_data_dir": str(self.chrome_profile_manager.profile_dir),
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

    async def _apply_stealth_scripts_to_persistent_context_async(self):
        if self.spoof_dimension:
            await self._persistent_context.add_init_script(
                self.stealth_manager.get_init_script()
            )
            await self._persistent_context.add_init_script(
                self.stealth_manager.get_dimension_spoofing_script()
            )
            await self._persistent_context.add_init_script(
                self.cookie_acceptor.get_auto_acceptor_script()
            )

    async def _load_auth_cookies_to_persistent_context_async(self):
        """Load authentication cookies into the persistent browser context."""
        if not self.auth_manager:
            logger.debug("No auth_manager available, skipping cookie loading")
            return

        try:
            # Check if we have authentication
            if await self.auth_manager.is_authenticate_async(
                verify_live=False
            ):
                cookies = await self.auth_manager.get_auth_cookies_async()
                if cookies:
                    await self._persistent_context.add_cookies(cookies)
                    logger.success(
                        f"Loaded {len(cookies)} authentication cookies into persistent browser context"
                    )
                else:
                    logger.debug("No cookies available from auth manager")
            else:
                logger.debug("Not authenticated, skipping cookie loading")
        except Exception as e:
            logger.warning(f"Failed to load authentication cookies: {e}")

    # async def take_screenshot_safe_async(
    #     self,
    #     page,
    #     fname: str,
    #     timeout_sec: float = 30.0,
    #     timeout_after_sec: float = 30.0,
    #     full_page: bool = True,
    # ):
    #     """Take screenshot in stealth mode without viewport changes."""
    #     screenshots_dir = self.config.get_screenshots_dir(
    #         screenshot_type="log"
    #     )
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     path = os.path.join(
    #         str(screenshots_dir),
    #         f"{fname}-{timestamp}-{self.browser_mode}.png",
    #     )
    #     try:
    #         await page.screenshot(
    #             path=path, timeout=timeout_sec * 1000, full_page=full_page
    #         )
    #         logger.success(f"Saved: {path}")

    #         start_time = asyncio.get_event_loop().time()
    #         while (
    #             asyncio.get_event_loop().time() - start_time
    #             < timeout_after_sec
    #         ):
    #             if os.path.exists(path) and os.path.getsize(path) > 0:
    #                 break
    #             await asyncio.sleep(0.1)
    #             # time.sleep(1)
    #     except Exception as e:
    #         logger.fail(f"Screenshot failed for {path}: {e}")

    async def take_screenshot_safe_async(
        self,
        page,
        fname: str,
        timeout_sec: float = 30.0,
        timeout_after_sec: float = 30.0,
        full_page: bool = False,
    ):
        """Take screenshot in stealth mode without viewport changes."""
        screenshots_dir = self.config.get_screenshots_dir(
            screenshot_type="log"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            str(screenshots_dir),
            f"{fname}-{timestamp}-{self.browser_mode}.png",
        )

        try:
            if self.spoof_dimension:
                await page.set_viewport_size({"width": 1920, "height": 1080})
                await asyncio.sleep(1)

            await page.screenshot(
                path=path, timeout=timeout_sec * 1000, full_page=full_page
            )
            logger.success(f"Saved: {path}")

            if self.spoof_dimension:
                await page.set_viewport_size({"width": 1, "height": 1})

            await asyncio.sleep(3)
        except Exception as e:
            logger.fail(f"Screenshot failed for {path}: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)


if __name__ == "__main__":

    async def main(browser_mode="interactive"):
        """Example usage of BrowserManager with stealth features."""
        from ...auth import AuthenticationManager

        auth_manager = AuthenticationManager()
        browser_manager = BrowserManager(
            chrome_profile_name="system",
            browser_mode=browser_mode,
            auth_manager=auth_manager,
        )

        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        page = await context.new_page()

        # Test sites configuration
        test_sites = [
            # {
            #     "name": "Extensions Test",
            #     "url": "",
            #     "screenshot_fname": "openathens_test",
            # },
            {
                "name": "SSO Test",
                "url": "https://sso.unimelb.edu.au/",
                "screenshot_fname": "unimelb_sso_test",
            },
            {
                "name": "OpenAthens",
                "url": "https://my.openathens.net/account",
                "screenshot_fname": "openathens_test",
            },
            {
                "name": "CAPTCHA Test",
                "url": "https://www.google.com/recaptcha/api2/demo",
                "screenshot_fname": "captcha_test",
            },
            {
                "name": "Nature Test",
                "url": "https://www.nature.com/articles/s41593-025-01990-7",
                "screenshot_fname": "nature_test",
            },
            {
                "name": "Google Test",
                "url": "https://www.google.com",
                "screenshot_fname": "google_test",
            },
        ]

        # Run tests for each site
        for site in test_sites:
            try:
                await page.goto(site["url"])
                await browser_manager.stealth_manager.human_delay_async(
                    2000, 3000
                )
                # time.sleep(1)
                # time.sleep(60)
                await browser_manager.take_screenshot_safe_async(
                    page, site["screenshot_fname"]
                )
            except Exception as e:
                logger.fail(f"Failed to process {site['name']}: {e}")
                continue

    import argparse

    parser = argparse.ArgumentParser(description="BrowserManager testing")
    parser.add_argument(
        "--stealth",
        action="store_true",
        help="Use stealth mode (default: interactive)",
    )
    args = parser.parse_args()

    browser_mode = "stealth" if args.stealth else "interactive"
    asyncio.run(main(browser_mode=browser_mode))

# python -m scitex.scholar.browser.local._BrowserManager --stealth
# python -m scitex.scholar.browser.local._BrowserManager

# EOF
