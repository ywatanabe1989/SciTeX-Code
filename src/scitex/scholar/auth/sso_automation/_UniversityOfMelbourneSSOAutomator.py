#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 18:51:11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/sso_automation/_UniversityOfMelbourneSSOAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/sso_automation/_UniversityOfMelbourneSSOAutomator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""University of Melbourne SSO automation."""

from typing import Optional

from playwright.async_api import Page, TimeoutError

from ...browser._BrowserUtils import BrowserUtils
from ...config import ScholarConfig
from ._BaseSSOAutomator import BaseSSOAutomator


class UniversityOfMelbourneSSOAutomator(BaseSSOAutomator):
    """SSO automator for University of Melbourne."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
        **kwargs,
    ):
        """Initialize UniMelb SSO automator.

        Args:
            username: UniMelb username (defaults to UNIMELB_SSO_USERNAME env var)
            password: UniMelb password (defaults to UNIMELB_SSO_PASSWORD env var)
            config: ScholarConfig
            **kwargs: Additional arguments for BaseSSOAutomator
        """
        # Get credentials from environment if not provided
        if config is None:
            config = ScholarConfig()

        username = config.resolve("sso_username", username, default="")
        password = config.resolve("sso_password", password, default="")

        super().__init__(username=username, password=password, **kwargs)

    def get_institution_name(self) -> str:
        """Get human-readable institution name."""
        return "University of Melbourne"

    def get_institution_id(self) -> str:
        """Get machine-readable institution ID."""
        return "unimelb"

    def is_sso_page(self, url: str) -> bool:
        """Check if URL is UniMelb SSO page."""
        sso_domains = [
            "login.unimelb.edu.au",
            "okta.unimelb.edu.au",
            "authenticate_async.unimelb.edu.au",
            "sso.unimelb.edu.au",
        ]
        return any(domain in url.lower() for domain in sso_domains)

    async def perform_login_async(self, page: Page) -> bool:
        """Perform UniMelb login flow using proven working patterns."""
        try:
            self.logger.info("Starting UniMelb SSO login with proven patterns")

            # Step 1: Handle username entry (first step - proven working pattern)
            username_success = await self._handle_username_step_async(page)
            if not username_success:
                # Try generic login as fallback
                self.logger.info(
                    "Trying generic login form detection as fallback"
                )
                username_success = await self._handle_generic_login_async(page)
                if not username_success:
                    return False

            # Step 2: Handle password entry (second step)
            password_success = await self._handle_password_step_async(page)
            if not password_success:
                return False

            # Step 3: Handle 2FA if needed
            await self._handle_duo_authentication_async(page)

            # Step 4: Wait for completion
            success = await self._wait_for_completion_async(page)

            # Only send notification on failure (no spam for successful auth)
            if not success:
                await self.notify_user_async(
                    "authentication_failed",
                    error="Login process timed out or failed",
                )

            return success

        except Exception as e:
            self.logger.error(f"UniMelb SSO login failed: {e}")
            await self._take_debug_screenshot_async(page)

            # Send failure notification
            await self.notify_user_async("authentication_failed", error=str(e))

            return False

    async def _handle_username_step_async(self, page: Page) -> bool:
        """Handle username entry using proven working selector."""
        try:
            # Use the proven working selector from your implementation
            username_selector = "input[name='identifier']"

            success = await BrowserUtils.reliable_fill_async(
                page, username_selector, self.username
            )
            if not success:
                self.logger.error("Failed to fill username field")
                return False

            self.logger.info(f"Filled username: {self.username}")

            # Click Next button using proven working selector and JavaScript click
            next_selector = "input.button-primary[value='Next']"
            success = await BrowserUtils.reliable_click_async(
                page, next_selector
            )
            if not success:
                self.logger.error("Failed to click Next button")
                return False

            self.logger.info("Next button clicked successfully")

            # Small delay for page transition
            await page.wait_for_timeout(1000)
            return True

        except Exception as e:
            self.logger.error(f"Username step failed: {e}")
            return False

    async def _handle_password_step_async(self, page: Page) -> bool:
        """Handle password entry using proven working selector."""
        try:
            # Use the proven working selector for password
            password_selector = "input[name='credentials.passcode']"

            success = await BrowserUtils.reliable_fill_async(
                page, password_selector, self.password
            )
            if not success:
                self.logger.error("Failed to fill password field")
                return False

            self.logger.info("Password filled successfully")

            # Click Verify button using proven working selector and JavaScript click
            verify_selector = "input[type='submit'][value='Verify']"
            success = await BrowserUtils.reliable_click_async(
                page, verify_selector
            )
            if not success:
                self.logger.error("Failed to click Verify button")
                return False

            self.logger.info("Verify button clicked successfully")
            return True

        except Exception as e:
            self.logger.error(f"Password step failed: {e}")
            return False

    async def _handle_generic_login_async(self, page: Page) -> bool:
        """Handle generic login form as fallback."""
        try:
            # Find any username/email input field
            username_elements = await page.query_selector_all(
                'input[type="text"], input[type="email"], input[name*="user"], input[id*="user"]'
            )

            if username_elements:
                await page.evaluate(
                    '(args) => { args.element.value = args.value; args.element.dispatchEvent(new Event("input", { bubbles: true })); }',
                    {"element": username_elements[0], "value": self.username},
                )
                self.logger.info("Filled generic username field")

            # Find any password field
            password_elements = await page.query_selector_all(
                'input[type="password"]'
            )
            if password_elements:
                await page.evaluate(
                    '(args) => { args.element.value = args.value; args.element.dispatchEvent(new Event("input", { bubbles: true })); }',
                    {"element": password_elements[0], "value": self.password},
                )
                self.logger.info("Filled generic password field")

            # Find and click submit button
            login_buttons = await page.query_selector_all(
                'button:has-text("Log"), button:has-text("Sign"), button[type="submit"], input[type="submit"]'
            )

            if login_buttons:
                await login_buttons[0].click()
                self.logger.info("Generic login button clicked")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Generic login failed: {e}")
            return False

    async def _handle_duo_authentication_async(self, page: Page) -> bool:
        """Handle Duo 2FA using proven working patterns."""
        try:
            # Quick check for Duo auth elements
            duo_elements = await page.query_selector_all(
                ".authenticator-verify-list"
            )

            if not duo_elements:
                try:
                    await page.wait_for_selector(
                        ".authenticator-verify-list", timeout=3000
                    )
                except TimeoutError:
                    return True  # No 2FA required

            self.logger.info("Duo 2FA detected, handling...")

            # Try push notification first (proven working pattern)
            push_buttons = await page.query_selector_all(
                'xpath=//h3[contains(text(), "Get a push notification")]/../..//a[contains(@class, "button")]'
            )

            if push_buttons:
                await push_buttons[0].click()
                self.logger.success(
                    "Push notification requested - check your device"
                )

                # Send notification to user - USER INTERVENTION REQUIRED
                await self.notify_user_async(
                    "2fa_required",
                    timeout=60,
                    method="Duo Push Notification",
                    device="Registered mobile device",
                    action="Tap 'Approve' on your device",
                )

            else:
                # Fallback to any auth method
                auth_buttons = await page.query_selector_all(
                    ".authenticator-button a.button"
                )
                if auth_buttons:
                    await auth_buttons[0].click()
                    self.logger.info(
                        "Alternative authentication method selected"
                    )

                    # Send notification for alternative auth - USER INTERVENTION REQUIRED
                    await self.notify_user_async(
                        "2fa_required",
                        timeout=60,
                        method="Alternative 2FA method",
                        device="Follow instructions on screen",
                        action="Complete authentication on your device",
                    )

            return True

        except Exception as e:
            self.logger.error(f"Duo authentication handling failed: {e}")
            return False

    async def _wait_for_completion_async(self, page: Page) -> bool:
        """Wait for login completion using proven success detection."""
        try:
            self.logger.info("Waiting for login completion...")

            for ii in range(60):
                await page.wait_for_timeout(1000)

                try:
                    # Check if moved away from SSO
                    if not self.is_sso_page(page.url):
                        self.logger.success(
                            "Login successful - redirected away from SSO"
                        )
                        return True

                    # Check for success indicators only if context is still valid
                    success_elements = await page.query_selector_all(
                        'input[name="prompt"], .chat-interface, .dashboard, .main-content'
                    )
                    if success_elements:
                        self.logger.success(
                            "Login successful - found success elements"
                        )
                        return True

                except Exception as context_error:
                    # Context destroyed likely means navigation happened (success)
                    if "Execution context was destroyed" in str(context_error):
                        await page.wait_for_timeout(2000)
                        if not self.is_sso_page(page.url):
                            self.logger.success(
                                "Login successful - context destroyed due to navigation"
                            )
                            return True

                if ii > 0 and ii % 10 == 0:
                    self.logger.info(f"Still waiting... ({60-ii}s remaining)")

            return False

        except Exception as e:
            self.logger.error(f"Error waiting for completion: {e}")
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
                / f"unimelb_debug_{int(time.time())}.png"
            )
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path))
            self.logger.debug(f"Debug screenshot: {screenshot_path}")
        except Exception as e:
            self.logger.debug(f"Screenshot failed: {e}")


if __name__ == "__main__":
    import asyncio

    def main():
        """Test UniMelb SSO automator."""
        import asyncio

        from playwright.async_api import async_playwright

        async def test_automator():
            automator = UniversityOfMelbourneSSOAutomator()

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()

                try:
                    await page.goto("https://sso.unimelb.edu.au/")
                    success = await automator.perform_login_async(page)
                    print(f"Login success: {success}")

                    await page.wait_for_timeout(5000)
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    await browser.close()

        asyncio.run(test_automator())

    main()


# python -m scitex.scholar.auth.sso_automation._UniversityOfMelbourneSSOAutomator

# EOF
