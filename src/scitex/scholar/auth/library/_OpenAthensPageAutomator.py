#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:43:52 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/library/_OpenAthensPageAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""OpenAthens page automation for institutional email entry and selection."""

import asyncio
from typing import Optional

from playwright.async_api import BrowserContext, Page

# from scitex.scholar.browser import BrowserUtils
from scitex.scholar.browser.utils import click_with_fallbacks
from scitex.scholar.config import ScholarConfig

from ..sso_automation._BaseSSOAutomator import BaseSSOAutomator


class OpenAthensPageAutomator(BaseSSOAutomator):
    """Automator for the initial OpenAthens page (my.openathens.net)."""

    def __init__(
        self,
        openathens_email: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
        **kwargs,
    ):
        """Initialize OpenAthens page automator.

        Args:
            openathens_email: Institutional email for OpenAthens
            config: ScholarConfig instance
            **kwargs: Additional arguments
        """
        if config is None:
            config = ScholarConfig()

        # Resolve email from config
        self.openathens_email = config.resolve(
            "openathens_email", openathens_email, default=""
        )

        super().__init__(**kwargs)

    def get_institution_name(self) -> str:
        """Get human-readable name."""
        return "OpenAthens"

    def get_institution_id(self) -> str:
        """Get machine-readable ID."""
        return "openathens"

    def is_sso_page(self, url: str) -> bool:
        """Check if URL is OpenAthens login page."""
        openathens_patterns = [
            "my.openathens.net",
            "openathens.net/login",
            "openathens.net/?passiveLogin",
        ]
        return any(pattern in url.lower() for pattern in openathens_patterns)

    async def perform_login_async(self, page: Page) -> bool:
        """Perform OpenAthens email entry and institution selection."""
        try:
            self.logger.info("Starting OpenAthens page automation")

            if not self.openathens_email:
                self.logger.error("No OpenAthens email configured")
                return False

            # Step 1: Enter institutional email
            success = await self._enter_institutional_email_async(page)
            if not success:
                return False

            # Step 2: Wait for institution selection to appear and select it
            success = await self._select_institution_async(page)
            if not success:
                return False

            # Step 3: Wait for redirect to institution SSO
            success = await self._wait_for_institution_redirect_async(page)

            return success

        except Exception as e:
            self.logger.error(f"OpenAthens page automation failed: {e}")
            await self._take_debug_screenshot_async(page)
            return False

    async def _enter_institutional_email_async(self, page) -> bool:
        """Enter institutional email in OpenAthens form."""
        try:
            self.logger.info(
                f"Entering institutional email: {self.openathens_email}"
            )

            # The correct selector from Puppeteer testing
            email_selector = "#type-ahead"

            # Wait for and fill the email field
            try:
                await page.wait_for_selector(email_selector, timeout=10000)
                await page.fill(email_selector, self.openathens_email)
                self.logger.info("Successfully filled OpenAthens email field")

                # Press Enter to trigger the search/autocomplete
                await page.press(email_selector, "Enter")
                self.logger.info("Pressed Enter to trigger institution search")

                # Wait for institution dropdown to appear
                await page.wait_for_timeout(2000)
                return True

            except Exception as e:
                self.logger.error(f"Failed to fill email field: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to enter email: {e}")
            return False

    async def _submit_email_form_async(self, page: Page) -> bool:
        """Submit email form or trigger next step."""
        try:
            # Try pressing Enter first
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            # Try clicking submit/continue buttons
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Continue')",
                "button:has-text('Next')",
                "button:has-text('Submit')",
                "button:has-text('Go')",
                ".submit-button",
                ".continue-button",
            ]

            for selector in submit_selectors:
                try:
                    element = await page.wait_for_selector(
                        selector, timeout=2000
                    )
                    if element:
                        success = await click_with_fallbacks(page, selector)
                        if success:
                            self.logger.info(
                                f"Successfully clicked submit using: {selector}"
                            )
                            await page.wait_for_timeout(1000)
                            return True
                except TimeoutError:
                    continue

            self.logger.info(
                "No explicit submit button found, assuming form submitted automatically"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to submit email form: {e}")
            return False

    # async def _select_institution_async(self, page) -> bool:
    #     """Select institution from the list that appears (generic for any institution)."""
    #     try:
    #         self.logger.info("Waiting for institution selection to appear...")

    #         # Wait for institution dropdown to appear
    #         institution_selector = ".wayfinder-item"

    #         try:
    #             # Wait for any institution option to appear
    #             await page.wait_for_selector(
    #                 institution_selector, timeout=10000
    #             )
    #             self.logger.info("Found institution dropdown options")

    #             # Get all available institution options
    #             institution_elements = await page.query_selector_all(
    #                 institution_selector
    #             )

    #             if len(institution_elements) == 1:
    #                 # Only one option available, click it
    #                 await institution_elements[0].click()
    #                 institution_text = await institution_elements[
    #                     0
    #                 ].text_content()
    #                 self.logger.success(
    #                     f"Selected institution: {institution_text.strip()}"
    #                 )

    #             elif len(institution_elements) > 1:
    #                 # Multiple options - try to find best match based on email domain
    #                 selected = await self._select_best_institution_match(
    #                     page, institution_elements
    #                 )
    #                 if not selected:
    #                     # If no good match, select the first one
    #                     await institution_elements[0].click()
    #                     institution_text = await institution_elements[
    #                         0
    #                     ].text_content()
    #                     self.logger.info(
    #                         f"Selected first available institution: {institution_text.strip()}"
    #                     )
    #             else:
    #                 self.logger.error("No institution options found")
    #                 return False

    #             # Wait a moment for redirect to start
    #             await page.wait_for_timeout(2000)
    #             return True

    #         except Exception as e:
    #             self.logger.error(f"Failed to click institution option: {e}")
    #             return False

    #     except Exception as e:
    #         self.logger.error(f"Failed to select institution: {e}")
    #         return False

    async def _select_institution_async(self, page) -> bool:
        """Select institution from the list that appears (generic for any institution)."""
        try:
            self.logger.info("Waiting for institution selection to appear...")

            institution_selector = ".wayfinder-item"
            await page.wait_for_selector(institution_selector, timeout=10000)
            self.logger.info("Found institution dropdown options")

            institution_elements = await page.query_selector_all(
                institution_selector
            )

            if len(institution_elements) == 1:
                # Get text BEFORE clicking
                institution_text = await institution_elements[0].text_content()
                await institution_elements[0].click()
                self.logger.success(
                    f"Selected institution: {institution_text.strip()}"
                )
            elif len(institution_elements) > 1:
                selected = await self._select_best_institution_match(
                    page, institution_elements
                )
                if not selected:
                    # Get text BEFORE clicking
                    institution_text = await institution_elements[
                        0
                    ].text_content()
                    await institution_elements[0].click()
                    self.logger.info(
                        f"Selected first available institution: {institution_text.strip()}"
                    )
            else:
                self.logger.error("No institution options found")
                return False

            await page.wait_for_timeout(2000)
            return True

        except Exception as e:
            self.logger.error(f"Failed to select institution: {e}")
            return False

    async def _select_best_institution_match(
        self, page, institution_elements
    ) -> bool:
        """Try to select the best matching institution based on email domain."""
        try:
            email_domain = (
                self.openathens_email.split("@")[1].lower()
                if "@" in self.openathens_email
                else ""
            )

            # Domain-specific matching logic
            domain_keywords = {
                "unimelb.edu.au": ["melbourne", "unimelb"],
                "stanford.edu": ["stanford"],
                "mit.edu": ["mit", "massachusetts"],
                "harvard.edu": ["harvard"],
                "oxford.ac.uk": ["oxford"],
                "cambridge.ac.uk": ["cambridge"],
                # Add more mappings as needed
            }

            if email_domain in domain_keywords:
                keywords = domain_keywords[email_domain]

                for element in institution_elements:
                    text = await element.text_content()
                    text_lower = text.lower()

                    if any(keyword in text_lower for keyword in keywords):
                        await element.click()
                        self.logger.success(
                            f"Selected matched institution: {text.strip()}"
                        )
                        return True

            # Generic fallback - look for university in the name
            if "university" in email_domain or "edu" in email_domain:
                for element in institution_elements:
                    text = await element.text_content()
                    if "university" in text.lower():
                        await element.click()
                        self.logger.info(
                            f"Selected university institution: {text.strip()}"
                        )
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to match institution: {e}")
            return False

    async def _wait_for_institution_redirect_async(self, page) -> bool:
        """Wait for redirect to institution SSO page."""
        try:
            self.logger.info("Waiting for redirect to institution SSO...")

            # Wait for URL to change away from OpenAthens
            for i in range(30):  # Wait up to 30 seconds
                current_url = page.url

                if not self.is_sso_page(current_url):
                    self.logger.success(
                        f"Redirected to institution SSO: {current_url[:50]}..."
                    )
                    return True

                await page.wait_for_timeout(1000)

            self.logger.error("Timeout waiting for institution redirect")
            return False

        except Exception as e:
            self.logger.error(f"Failed waiting for redirect: {e}")
            return False

    async def _take_debug_screenshot_async(self, page: Page):
        """Take debug screenshot."""
        try:
            import time
            from pathlib import Path

            screenshot_path = (
                Path.home()
                / ".scitex"
                / "scholar"
                / f"openathens_debug_{int(time.time())}.png"
            )
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path))
            self.logger.debug(f"Debug screenshot: {screenshot_path}")
        except Exception as e:
            self.logger.debug(f"Screenshot failed: {e}")


if __name__ == "__main__":
    import asyncio

    def main():
        """Test OpenAthens page automator."""
        from playwright.async_api import async_playwright

        async def test_automator():
            automator = OpenAthensPageAutomator()

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()

                try:
                    await page.goto(
                        "https://my.openathens.net/?passiveLogin=false"
                    )
                    success = await automator.perform_login_async(page)
                    print(f"OpenAthens automation success: {success}")

                    await page.wait_for_timeout(10000)
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    await browser.close()

        asyncio.run(test_automator())

    main()

# python -m scitex.scholar.auth.sso_automation._OpenAthensPageAutomator

# EOF
