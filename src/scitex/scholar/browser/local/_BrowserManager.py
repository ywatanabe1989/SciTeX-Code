#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 05:09:31 (ywatanabe)"
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

from .._BrowserConfig import BrowserConfiguration, BrowserMode, get_browser_config
from ._BrowserMixin import BrowserMixin
from .utils._ChromeExtensionManager import ChromeExtensionManager
from .utils._CookieAutoAcceptor import CookieAutoAcceptor
from .utils._StealthManager import StealthManager

logger = logging.getLogger(__name__)


class BrowserManager(BrowserMixin):
    """Manages a local browser instance with stealth enhancements and invisible mode."""

    def __init__(
        self,
        auth_manager=None,
        headless: bool = True,
        profile_name: str = "scholar_default",
        spoof_dimension: bool = False,
        viewport_size: tuple = None,
        window_position: tuple = None,
        config: BrowserConfiguration = None,
    ):
        """
        Initialize BrowserManager with invisible browser capabilities.

        Args:
            auth_manager: Authentication manager instance
            headless: Whether to run in headless mode
            profile_name: Chrome profile name for extensions
            spoof_dimension: Enable invisible mode (1x1 pixel window + dimension spoofing)
            viewport_size: Custom viewport size (width, height). Defaults to (1920, 1080) or (1, 1) for invisible
            window_position: Window position (x, y). Only applies to visible windows
            config: BrowserConfiguration instance (overrides other parameters if provided)
        """
        # Use centralized config if provided, otherwise use individual parameters
        if config:
            self.config = config
            mode = "stealth" if config.headless else "interactive"
            super().__init__(mode=mode)
            self.headless = config.headless
            self.spoof_dimension = config.invisible
            self.viewport_size = config.viewport_size
            self.window_position = config.window_position
            self.profile_name = config.profile_name
            logger.info(f"🔧 Using centralized browser config: {config}")
        else:
            # Legacy parameter-based initialization - store parameters for use in init_browser
            mode = "stealth" if headless else "interactive"
            super().__init__(mode=mode)
            self.headless = headless
            self.spoof_dimension = spoof_dimension
            self.viewport_size = viewport_size
            self.window_position = window_position
            self.profile_name = profile_name

            # Set default viewport based on invisible mode
            if self.spoof_dimension:
                # self.viewport_size = self.viewport_size or (
                #     1,
                #     1,
                # )  # 1x1 pixel for invisibility
                self.headless = (
                    False  # Must be visible to bypass bot detection
                )
                logger.info("Invisible mode enabled")
            # else:
            #     self.viewport_size = self.viewport_size or (
            #         1920,
            #         1080,
            #     )  # Standard desktop size

            # Create config object for consistency
            self.config = BrowserConfiguration(
                mode=(
                    BrowserMode.INVISIBLE
                    if spoof_dimension
                    else BrowserMode.DEBUG
                ),
                headless=self.headless,
                invisible=self.spoof_dimension,
                viewport_size=self.viewport_size,
                window_position=self.window_position,
                capture_screenshots=False,
                profile_name=self.profile_name,
            )

        self.auth_manager = auth_manager
        if auth_manager is None:
            logger.warn(
                f"auth_manager not passed. University Authentication will not be enabled."
            )

        self.extension_manager = ChromeExtensionManager(self.profile_name)
        self.stealth_manager = StealthManager(
            viewport_size, spoof_dimension, window_position
        )
        self.cookie_acceptor = CookieAutoAcceptor()

    async def get_authenticated_context(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies and extensions loaded."""

        if self.auth_manager is None:
            raise ValueError(
                "Authentication manager is not set. Initialize BrowserManager with an auth_manager to use this method."
            )

        await self.auth_manager.ensure_authenticated()

        # Use browser with Chrome profile for extension support
        browser = await self.get_browser_with_profile()

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
                and await self.auth_manager.is_authenticated()
            ):
                try:
                    auth_session = await self.auth_manager.authenticate()
                    if auth_session and "cookies" in auth_session:
                        context_options["storage_state"] = {
                            "cookies": auth_session["cookies"]
                        }
                except Exception as e:
                    logger.warning(f"Failed to get auth session: {e}")

            context = await self._create_stealth_context(
                browser, **context_options
            )

        return browser, context

    async def _create_stealth_context(
        self, browser: Browser, **context_options
    ) -> BrowserContext:
        """Creates a new browser context with stealth options and invisible mode applied."""
        stealth_options = self.stealth_manager.get_stealth_options()

        # # Apply viewport size for invisible mode
        # if self.spoof_dimension or self.viewport_size:
        #     viewport_config = {
        #         "width": self.viewport_size[0],
        #         "height": self.viewport_size[1],
        #     }
        #     stealth_options["viewport"] = viewport_config
        #     logger.success(
        #         f"🖥️  Viewport set to: {self.viewport_size[0]}x{self.viewport_size[1]}"
        #     )

        merged_options = {**stealth_options, **context_options}
        context = await browser.new_context(**merged_options)

        # Apply stealth script
        await context.add_init_script(self.stealth_manager.get_init_script())
        await context.add_init_script(
            self.stealth_manager.get_spoofing_script()
        )

        # # This may be included in self.stealth_manager
        # # Apply dimension spoofing for invisible mode
        # dimension_spoof_script = (
        #     self._stealth_manager.get_dimension_spoofing_script()
        # )
        # if dimension_spoof_script:
        #     await context.add_init_script(dimension_spoof_script)
        #     logger.success("🎭 Dimension spoofing script injected")

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

            # This should be handled in self.extension_manager
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

            stealth_args = (
                self.stealth_manager.get_stealth_options_additional()
            )
            # Enhanced stealth launch arguments with invisible mode support
            # stealth_args = [
            #     "--no-sandbox",
            #     "--disable-dev-shm-usage",
            #     "--disable-blink-features=AutomationControlled",
            #     "--disable-web-security",
            #     "--disable-features=VizDisplayCompositor",
            #     "--disable-background-networking",
            #     "--disable-sync",
            #     "--disable-translate",
            #     "--disable-default-apps",
            #     "--enable-extensions",
            #     "--no-first-run",
            #     "--no-default-browser-check",
            #     "--disable-background-timer-throttling",
            #     "--disable-backgrounding-occluded-windows",
            #     "--disable-renderer-backgrounding",
            #     "--disable-field-trial-config",
            #     "--disable-client-side-phishing-detection",
            #     "--disable-component-update",
            #     "--disable-plugins-discovery",
            #     "--disable-hang-monitor",
            #     "--disable-prompt-on-repost",
            #     "--disable-domain-reliability",
            #     "--disable-infobars",
            #     "--disable-notifications",
            #     "--disable-popup-blocking",
            # ]

            # # Apply window size and position based on mode
            # if self.spoof_dimension:
            #     # 1x1 window for complete invisibility
            #     stealth_args.extend(
            #         ["--window-size=1,1", "--window-position=0,0"]
            #     )
            #     logger.info(
            #         "🎭 Invisible mode: Window set to 1x1 at position 0,0"
            #     )
            # else:
            #     # Standard window or custom size
            #     if self.viewport_size:
            #         stealth_args.append(
            #             f"--window-size={self.viewport_size[0]},{self.viewport_size[1]}"
            #         )
            #     else:
            #         stealth_args.append("--window-size=1920,1080")

            #     # Apply custom window position if specified
            #     if self.window_position:
            #         stealth_args.append(
            #             f"--window-position={self.window_position[0]},{self.window_position[1]}"
            #         )
            #         logger.info(
            #             f"📐 Window positioned at: {self.window_position[0]},{self.window_position[1]}"
            #         )

            # logger.info(
            #     f"🖥️ Browser window configuration: {'Invisible (1x1)' if self.spoof_dimension else f'{self.viewport_size[0]}x{self.viewport_size[1]}'}"
            # )

            # IMPORTANT: Use launch_persistent_context for profile + extensions
            # This ensures both authentication cookies AND extensions are active
            logger.info(
                "Using launch_persistent_context for profile and authentication"
            )

            if extension_dirs:
                # Load extensions explicitly with persistent context
                stealth_args.extend(
                    [
                        f"--load-extension={','.join(extension_dirs)}",
                        "--disable-extensions-file-access-check",
                    ]
                )
                logger.info(
                    f"Loading {len(extension_dirs)} extensions explicitly WITH profile"
                )
                # Fixme: Can we check if they are loaded actually afterwards? We would like to log it with logegr.success(f"Loaded ...")
            else:
                logger.fail("No extensions found to load explicitly")

            # Launch persistent context with BOTH profile AND extensions + invisible mode
            launch_options = {
                "user_data_dir": str(self.extension_manager.profile_dir),
                "headless": self.headless,
                "args": stealth_args,
            }

            # Apply invisible mode viewport settings to persistent context
            if self.spoof_dimension or self.viewport_size:
                launch_options["viewport"] = {
                    "width": self.viewport_size[0],
                    "height": self.viewport_size[1],
                }
                logger.info(
                    f"🎭 Persistent context viewport: {self.viewport_size[0]}x{self.viewport_size[1]}"
                )

            self._shared_context = await self._shared_playwright.chromium.launch_persistent_context(
                **launch_options
            )

            # Apply dimension spoofing to persistent context
            dimension_spoof_script = (
                self._stealth_manager.get_dimension_spoofing_script()
            )
            if dimension_spoof_script:
                await self._shared_context.add_init_script(
                    dimension_spoof_script
                )
                logger.info(
                    "🎭 Dimension spoofing applied to persistent context"
                )
            # Get browser from the persistent context
            self._shared_browser = self._shared_context.browser
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

    def get_page(self):
        """Get a new page with proper context management."""

        class PageManager:
            def __init__(self, browser_manager):
                self.browser_manager = browser_manager
                self.context = None
                self.page = None

            async def __aenter__(self):
                self.context = (
                    await self.browser_manager.get_authenticated_context()
                )
                self.page = await self.context.new_page()
                return self.page

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.page:
                    await self.page.close()
                if self.context:
                    await self.context.close()

        return PageManager(self)

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

# EOF
