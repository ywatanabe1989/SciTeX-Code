#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 19:41:41 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/ScholarBrowserManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/ScholarBrowserManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Union

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging
from scitex.scholar.config import ScholarConfig

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


class ScholarBrowserManager(BrowserMixin):
    """Manages a local browser instance with stealth enhancements and invisible mode."""

    def __init__(
        self,
        browser_mode=None,
        auth_manager=None,
        chrome_profile_name=None,
        use_zenrows_proxy=False,
        config: ScholarConfig = None,
    ):
        """
        Initialize ScholarBrowserManager with invisible browser capabilities.

        Args:
            auth_manager: Authentication manager instance
            config: Scholar configuration instance
        """
        # Store scholar_config for use by components like ChromeProfileManager
        self.config = config or ScholarConfig()

        # Browser
        self.browser_mode = self.config.resolve(
            "browser_mode", browser_mode, default="interactive"
        )
        super().__init__(mode=self.browser_mode)
        self._set_interactive_or_stealth(browser_mode)

        # ZenRows
        self.use_zenrows_proxy = use_zenrows_proxy
        if use_zenrows_proxy:
            from .utils._ZenRowsProxyManager import ZenRowsProxyManager

            self.zenrows_proxy_manager = ZenRowsProxyManager(config=config)

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
        logger.debug("Browser initialized:")
        logger.debug(f"headless: {self.headless}")
        logger.debug(f"spoof_dimension: {self.spoof_dimension}")
        logger.debug(f"viewport_size: {self.viewport_size}")

    # async def _get_zenrows_browser_and_context_async(
    #     self,
    # ) -> tuple[Browser, BrowserContext]:
    #     if self.auth_manager is None:
    #         raise ValueError(
    #             "Authentication manager is not set. "
    #             "To use this method, please initialize ScholarBrowserManager with an auth_manager."
    #         )

    #     await self.auth_manager.ensure_authenticate_async()

    #     from .utils._ZenRowsBrowserManager import ZenRowsBrowserManager

    #     zenrows_manager = ZenRowsBrowserManager(
    #         auth_manager=self.auth_manager,
    #         zenrows_api_key=self.zenrows_api_key,
    #         # Pass stealth settings
    #         stealth_manager=self.stealth_manager,
    #         viewport_size=self.viewport_size,
    #         spoof_dimension=self.spoof_dimension,
    #     )

    #     return await zenrows_manager.get_authenticated_browser_and_context()

    async def get_authenticated_browser_and_context_async(
        self, **context_options
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies and extensions loaded."""
        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. "
                "To use this method, please initialize ScholarBrowserManager with an auth_manager."
            )

        await self.auth_manager.ensure_authenticate_async()

        browser = (
            await self._get_persistent_browser_with_profile_but_not_with_auth_async()
        )

        if hasattr(self, "_persistent_context") and self._persistent_context:
            context = self._persistent_context
            logger.success(
                "Using persistent context with profile and extensions"
            )
        else:
            logger.warn("Falling back to regular context creation")

            auth_options = await self.auth_manager.get_auth_options()
            context_options.update(auth_options)

            context = await self._new_context_async(browser, **context_options)

        return browser, context

    # async def get_authenticated_browser_and_context_async(
    #     self,
    # ) -> tuple[Browser, BrowserContext]:
    #     """Get browser context with authentication cookies and extensions loaded."""

    #     # Ensure auth_manager is passed
    #     if self.auth_manager is None:
    #         raise ValueError(
    #             "Authentication manager is not set. "
    #             "To use this method, please initialize ScholarBrowserManager with an auth_manager."
    #         )

    #     # Ensure auth_manager has authenticate_async info
    #     await self.auth_manager.ensure_authenticate_async()

    #     # Use browser with Chrome profile for extension support
    #     browser = (
    #         await self._get_persistent_browser_with_profile_but_not_with_auth_async()
    #     )

    #     # With persistent context, we already have the profile and extensions loaded
    #     if hasattr(self, "_persistent_context") and self._persistent_context:
    #         context = self._persistent_context
    #         logger.success(
    #             "Using persistent context with profile and extensions"
    #         )
    #     else:
    #         # Fallback to regular context creation if persistent context not available
    #         logger.warn("Falling back to regular context creation")
    #         context_options = {}
    #         if (
    #             self.auth_manager
    #             and await self.auth_manager.is_authenticate_async()
    #         ):
    #             try:
    #                 auth_session = await self.auth_manager.authenticate_async()
    #                 if auth_session and "cookies" in auth_session:
    #                     context_options["storage_state"] = {
    #                         "cookies": auth_session["cookies"]
    #                     }
    #             except Exception as e:
    #                 logger.warn(f"Failed to get auth session: {e}")

    #         context = await self._new_context_async(browser, **context_options)

    #     return browser, context

    async def _new_context_async(
        self, browser: Browser, **context_options
    ) -> BrowserContext:
        """Creates a new browser context with stealth options and invisible mode applied."""
        stealth_options = self.stealth_manager.get_stealth_options()
        context = await browser.new_context(
            {**stealth_options, **context_options}
        )

        # Apply stealth script
        await context.add_init_script(self.stealth_manager.get_init_script())
        await context.add_init_script(
            self.stealth_manager.get_dimension_spoofing_script()
        )
        await context.add_init_script(
            self.cookie_acceptor.get_auto_acceptor_script()
        )
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
            self._verify_xvfb_running()
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
        persistent_context_launch_options = (
            self._build_persistent_context_launch_options()
        )

        # # Create preferences to disable PDF viewer and force downloads
        # self._set_pdf_download_preferences()

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
                    logger.debug(f"Removed Chrome lock file: {lock_file.name}")
                    removed_locks += 1
                except Exception as e:
                    logger.warn(f"Could not remove {lock_file.name}: {e}")

        if removed_locks > 0:
            logger.debug(f"Cleaned up {removed_locks} Chrome lock files")
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
                logger.debug(
                    "Killed lingering Chrome processes for this profile"
                )
                time.sleep(2)  # Give processes time to fully terminate
        except Exception as e:
            logger.debug(f"Chrome process cleanup attempt: {e}")

        # This show_asyncs a small screen with 4 extensions show_asyncn
        persistent_context_launch_options["headless"] = False
        self._persistent_context = await self._persistent_playwright.chromium.launch_persistent_context(
            **persistent_context_launch_options
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
                    logger.debug("Extension cleanup completed")
                    break

                # Ensure context stays alive
                if len(self._persistent_context.pages) == len(unwanted_pages):
                    await self._persistent_context.new_page()

                for page in unwanted_pages:
                    await page.close()
                    logger.debug(f"Closed unwanted page: {page.url}")

            except Exception as e:
                logger.debug(f"Cleanup attempt failed: {e}")

            await asyncio.sleep(2)

    # def _set_pdf_download_preferences(self):
    #     """Set Chrome preferences to disable PDF viewer and force downloads."""
    #     try:
    #         import json

    #         profile_dir = Path(self.chrome_profile_manager.profile_dir)
    #         default_dir = profile_dir / "Default"
    #         default_dir.mkdir(exist_ok=True)

    #         preferences_file = default_dir / "Preferences"

    #         # Load existing preferences if they exist
    #         if preferences_file.exists():
    #             with open(preferences_file, "r") as f:
    #                 preferences = json.load(f)
    #         else:
    #             preferences = {}

    #         # Add PDF download preferences
    #         preferences.update(
    #             {
    #                 "plugins": {
    #                     "always_open_pdf_externally": True,
    #                     "open_pdf_in_system_reader": True,
    #                 },
    #                 "download": {
    #                     "prompt_for_download": False,
    #                     "directory_upgrade": True,
    #                     "extensions_to_open": "",
    #                 },
    #             }
    #         )

    #         # Write updated preferences
    #         with open(preferences_file, "w") as f:
    #             json.dump(preferences, f, indent=2)

    #         logger.success(
    #             f"Set PDF download preferences in {preferences_file}"
    #         )
    #     except Exception as e:
    #         logger.warn(f"Could not set PDF preferences: {e}")

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
                logger.debug(f"Starting Xvfb display :{self.display}")
                subprocess.Popen(
                    [
                        "Xvfb",
                        f":{self.display}",
                        "-screen",
                        "0",
                        "1920x1080x24",
                        "-ac",
                        "+extension",
                        "GLX",
                        "+render",
                        "-noreset",
                    ]
                )
                time.sleep(2)
                return self._verify_xvfb_running()
        except Exception as e:
            logger.error(f"Cannot verify Xvfb: {e}")
            return False

    def _build_persistent_context_launch_options(self):
        stealth_args = self.stealth_manager.get_stealth_options_additional()
        extension_args = self.chrome_profile_manager.get_extension_args()
        pdf_download_args = [
            "--always-open-pdf-externally",
            "--disable-plugins-discovery",
            "--plugin-policy=block",
        ]

        stealth_args.extend(
            [
                f"--display=:{self.display}",
                "--window-size=1920,1080",
            ]
        )

        no_welcome_args = [
            "--disable-extensions-file-access-check",
            "--disable-extensions-http-throttling",
            "--disable-component-extensions-with-background-pages",
        ]

        launch_args = (
            extension_args + stealth_args + no_welcome_args + pdf_download_args
        )

        # Debug: Show window args for stealth mode
        if self.spoof_dimension:
            window_args = [arg for arg in launch_args if "window-" in arg]
            logger.debug(f"Stealth window args: {window_args}")

        proxy_config = None
        if self.use_zenrows_proxy:
            proxy_config = self.zenrows_proxy_manager.get_proxy_config()

        return {
            "user_data_dir": str(self.chrome_profile_manager.profile_dir),
            "headless": self.headless,
            "args": launch_args,
            "accept_downloads": True,  # Enable download handling
            "proxy": proxy_config,
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
            logger.warn(f"Failed to load authentication cookies: {e}")

    async def take_screenshot_async(
        self,
        page,
        path: Union[str, Path],
        timeout_sec: float = 30.0,
        timeout_after_sec: float = 30.0,
        full_page: bool = False,
    ):
        """Take screenshot without viewport changes."""
        try:
            await page.screenshot(
                path=path, timeout=timeout_sec * 1000, full_page=full_page
            )
            logger.success(f"Saved: {path}")
        except Exception as e:
            logger.fail(f"Screenshot failed for {path}: {e}")

    async def start_periodic_screenshots_async(
        self,
        page,
        output_dir: Union[str, Path],
        prefix: str = "periodic",
        interval_seconds: int = 1,
        duration_seconds: int = 10,
        verbose: bool = False,
    ):
        """
        Start taking periodic screenshots in the background.

        Args:
            page: The page to screenshot
            prefix: Prefix for screenshot filenames
            interval_seconds: Seconds between screenshots
            duration_seconds: Total duration to take screenshots (0 = infinite)
            verbose: Whether to log each screenshot

        Returns:
            asyncio.Task that can be cancelled to stop screenshots
        """

        async def take_periodic_screenshots():
            elapsed = 0
            step = 0

            while duration_seconds == 0 or elapsed < duration_seconds:
                step += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[
                    :-3
                ]  # Include milliseconds
                path = os.path.join(
                    str(output_dir),
                    f"{prefix}_step{step:03d}_{timestamp}-{self.browser_mode}.png",
                )

                try:
                    await page.screenshot(path=path)
                    if verbose:
                        logger.debug(f"Screenshot {step}: {path}")
                    elif step == 1:
                        logger.debug(
                            f"Started periodic screenshots: {prefix}_*"
                        )
                except Exception as e:
                    if verbose:
                        logger.debug(f"Screenshot {step} failed: {e}")

                await asyncio.sleep(interval_seconds)
                elapsed += interval_seconds

            logger.debug(f"Completed {step} periodic screenshots for {prefix}")

        # Start the task in background
        task = asyncio.create_task(take_periodic_screenshots())
        return task

    async def stop_periodic_screenshots_async(self, task: asyncio.Task):
        """Stop periodic screenshots task."""
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.debug("Periodic screenshots stopped")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """Close browser while preserving authentication and extension data."""
        try:
            if (
                self._persistent_context
                and not self._persistent_context.browser.is_connected()
            ):
                logger.debug("Browser already closed")
                return

            if self._persistent_context:
                await self._persistent_context.close()
                logger.debug("Closed persistent browser context")

            if (
                self._persistent_browser
                and self._persistent_browser.is_connected()
            ):
                await self._persistent_browser.close()
                logger.debug("Closed persistent browser")

            if self._persistent_playwright:
                await self._persistent_playwright.stop()
                logger.debug("Stopped Playwright instance")

        except Exception as e:
            logger.warn(f"Error during browser cleanup: {e}")
        finally:
            # Reset references but keep auth_manager and chrome_profile_manager
            self._persistent_context = None
            self._persistent_browser = None
            self._persistent_playwright = None


if __name__ == "__main__":

    async def main(browser_mode="interactive"):
        """Example usage of ScholarBrowserManager with stealth features."""
        from scitex.scholar import ScholarAuthManager, ScholarBrowserManager

        browser_manager = ScholarBrowserManager(
            chrome_profile_name="system",
            browser_mode=browser_mode,
            auth_manager=ScholarAuthManager(),
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
            #     "screenshot_spath": "/tmp/openathens_test.png",
            # },
            # {
            #     "name": "SSO Test",
            #     "url": "https://sso.unimelb.edu.au/",
            #     "screenshot_spath": "/tmp/unimelb_sso_test.png",
            # },
            # {
            #     "name": "OpenAthens",
            #     "url": "https://my.openathens.net/account",
            #     "screenshot_spath": "/tmp/openathens_test.png",
            # },
            # {
            #     "name": "CAPTCHA Test",
            #     "url": "https://www.google.com/recaptcha/api2/demo",
            #     "screenshot_spath": "/tmp/captcha_test.png",
            # },
            {
                "name": "Nature Test",
                "url": "https://www.nature.com/articles/s41593-025-01990-7",
                "screenshot_spath": "/tmp/nature_test.png",
            },
            # {
            #     "name": "Google Test",
            #     "url": "https://www.google.com",
            #     "screenshot_spath": "/tmp/google_test.png",
            # },
        ]

        # Run tests for each site
        for site in test_sites:
            try:
                await page.goto(
                    site["url"], wait_until="domcontentloaded", timeout=30000
                )

                await browser_manager.take_screenshot_async(
                    page, site["screenshot_spath"]
                )
            except Exception as e:
                logger.fail(f"Failed to process {site['name']}: {e}")
                continue

    import argparse

    parser = argparse.ArgumentParser(
        description="ScholarBrowserManager testing"
    )
    parser.add_argument(
        "--stealth",
        action="store_true",
        help="Use stealth mode (default: interactive)",
    )
    args = parser.parse_args()

    browser_mode = "stealth" if args.stealth else "interactive"
    asyncio.run(main(browser_mode=browser_mode))

# python -m scitex.scholar.browser.local.ScholarBrowserManager --stealth
# python -m scitex.scholar.browser.local.ScholarBrowserManager

# EOF
