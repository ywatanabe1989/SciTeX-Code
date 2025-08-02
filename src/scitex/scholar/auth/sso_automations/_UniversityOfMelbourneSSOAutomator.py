#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 17:41:57 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/sso_automations/_UniversityOfMelbourneSSOAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/sso_automations/_UniversityOfMelbourneSSOAutomator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""University of Melbourne SSO automation."""

from pathlib import Path
from typing import Optional

from playwright.async_api import Page, TimeoutError

from ._BaseSSOAutomator import BaseSSOAutomator


class UniversityOfMelbourneSSOAutomator(BaseSSOAutomator):
    """SSO automator for University of Melbourne."""

    def __init__(
        self,
        username: Optional[str] = os.environ.get("UNIMELB_SSO_USERNAME", ""),
        password: Optional[str] = os.environ.get("UNIMELB_SSO_PASSWORD", ""),
        **kwargs,
    ):
        """Initialize UniMelb SSO automator.

        Args:
            username: UniMelb username (defaults to UNIMELB_SSO_USERNAME env var)
            password: UniMelb password (defaults to UNIMELB_SSO_PASSWORD env var)
            **kwargs: Additional arguments for BaseSSOAutomator
        """
        # Get credentials from environment if not provided
        username = username
        password = password

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
            "authenticate.unimelb.edu.au",
            "sso.unimelb.edu.au",
        ]
        return any(domain in url.lower() for domain in sso_domains)

    async def perform_login(self, page: Page) -> bool:
        """Perform UniMelb login flow using proven working patterns."""
        try:
            self.logger.info("Starting UniMelb SSO login with proven patterns")

            # Import BrowserAuthenticator for reliable methods
            from .._BrowserAuthenticator import BrowserAuthenticator
            browser_auth = BrowserAuthenticator(mode=self.mode)

            # Step 1: Handle username entry (first step - proven working pattern)
            username_success = await self._handle_username_step(page, browser_auth)
            if not username_success:
                # Try generic login as fallback
                self.logger.info("Trying generic login form detection as fallback")
                username_success = await self._handle_generic_login(page, browser_auth) 
                if not username_success:
                    return False

            # Step 2: Handle password entry (second step)
            password_success = await self._handle_password_step(page, browser_auth)
            if not password_success:
                return False

            # Step 3: Handle 2FA if needed
            await self._handle_duo_authentication(page)

            # Step 4: Wait for completion
            success = await self._wait_for_completion(page)
            
            # Send notification about authentication result
            if success:
                await self.notify_user_async(
                    "authentication_success",
                    cookie_count="Multiple",
                    expires_at="8 hours from now"
                )
            else:
                await self.notify_user_async(
                    "authentication_failed", 
                    error="Login process timed out or failed"
                )
                
            return success

        except Exception as e:
            self.logger.error(f"UniMelb SSO login failed: {e}")
            await self._take_debug_screenshot(page)
            
            # Send failure notification
            await self.notify_user_async(
                "authentication_failed",
                error=str(e)
            )
            
            return False

    async def _handle_username_step(self, page: Page, browser_auth) -> bool:
        """Handle username entry using proven working selector."""
        try:
            # Use the proven working selector from your implementation
            username_selector = "input[name='identifier']"
            
            success = await browser_auth.reliable_fill_async(page, username_selector, self.username)
            if not success:
                self.logger.error("Failed to fill username field")
                return False
                
            self.logger.info(f"Filled username: {self.username}")
            
            # Click Next button using proven working selector and JavaScript click
            next_selector = "input.button-primary[value='Next']"
            success = await browser_auth.reliable_click_async(page, next_selector)
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

    async def _handle_password_step(self, page: Page, browser_auth) -> bool:
        """Handle password entry using proven working selector."""
        try:
            # Use the proven working selector for password
            password_selector = "input[name='credentials.passcode']"
            
            success = await browser_auth.reliable_fill_async(page, password_selector, self.password)
            if not success:
                self.logger.error("Failed to fill password field")
                return False
                
            self.logger.info("Password filled successfully")
            
            # Click Verify button using proven working selector and JavaScript click
            verify_selector = "input[type='submit'][value='Verify']"
            success = await browser_auth.reliable_click_async(page, verify_selector)
            if not success:
                self.logger.error("Failed to click Verify button")
                return False
                
            self.logger.info("Verify button clicked successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Password step failed: {e}")
            return False

    async def _handle_generic_login(self, page: Page, browser_auth) -> bool:
        """Handle generic login form as fallback."""
        try:
            # Find any username/email input field
            username_elements = await page.query_selector_all(
                'input[type="text"], input[type="email"], input[name*="user"], input[id*="user"]'
            )
            
            if username_elements:
                await page.evaluate(
                    '(element, value) => { element.value = value; element.dispatchEvent(new Event("input", { bubbles: true })); }',
                    username_elements[0], self.username
                )
                self.logger.info("Filled generic username field")

            # Find any password field
            password_elements = await page.query_selector_all('input[type="password"]')
            if password_elements:
                await page.evaluate(
                    '(element, value) => { element.value = value; element.dispatchEvent(new Event("input", { bubbles: true })); }',
                    password_elements[0], self.password
                )
                self.logger.info("Filled generic password field")

            # Find and click submit button
            login_buttons = await page.query_selector_all(
                'button:has-text("Log"), button:has-text("Sign"), button[type="submit"], input[type="submit"]'
            )
            
            if login_buttons:
                await page.evaluate('(element) => element.click()', login_buttons[0])
                self.logger.info("Generic login button clicked")
                return True
                
            return False

        except Exception as e:
            self.logger.error(f"Generic login failed: {e}")
            return False

    async def _handle_duo_authentication(self, page: Page) -> bool:
        """Handle Duo 2FA using proven working patterns."""
        try:
            # Quick check for Duo auth elements
            duo_elements = await page.query_selector_all('.authenticator-verify-list')
            
            if not duo_elements:
                try:
                    await page.wait_for_selector('.authenticator-verify-list', timeout=3000)
                except TimeoutError:
                    return True  # No 2FA required

            self.logger.info("Duo 2FA detected, handling...")

            # Try push notification first (proven working pattern)
            push_buttons = await page.query_selector_all(
                'xpath=//h3[contains(text(), "Get a push notification")]/../..//a[contains(@class, "button")]'
            )

            if push_buttons:
                await push_buttons[0].click()
                self.logger.success("Push notification requested - check your device")
                
                # Send notification to user
                await self.notify_user_async(
                    "2fa_required",
                    timeout=60,
                    method="Duo Push Notification",
                    device="Registered mobile device",
                    action="Tap 'Approve' on your device"
                )
                
            else:
                # Fallback to any auth method
                auth_buttons = await page.query_selector_all('.authenticator-button a.button')
                if auth_buttons:
                    await auth_buttons[0].click()
                    self.logger.info("Alternative authentication method selected")

            return True

        except Exception as e:
            self.logger.error(f"Duo authentication handling failed: {e}")
            return False

    async def _wait_for_completion(self, page: Page) -> bool:
        """Wait for login completion using proven success detection."""
        try:
            self.logger.info("Waiting for login completion...")
            
            # Wait up to 60 seconds (extended for 2FA)
            for i in range(60):
                await page.wait_for_timeout(1000)
                
                # Check if moved away from SSO
                if not self.is_sso_page(page.url):
                    self.logger.success("Login successful - redirected away from SSO")
                    return True
                
                # Check for success indicators
                success_elements = await page.query_selector_all(
                    'input[name="prompt"], .chat-interface, .dashboard, .main-content'
                )
                
                if success_elements:
                    self.logger.success("Login successful - found success elements")
                    return True
                
                # Progress indicator
                if i > 0 and i % 10 == 0:
                    self.logger.info(f"Still waiting... ({60-i}s remaining)")

            self.logger.error("Login completion timed out")
            return False

        except Exception as e:
            self.logger.error(f"Error waiting for completion: {e}")
            return False

    async def _take_debug_screenshot(self, page: Page):
        """Take debug screenshot."""
        try:
            from pathlib import Path
            import time
            
            screenshot_path = Path.home() / ".scitex" / "scholar" / f"unimelb_debug_{int(time.time())}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path))
            self.logger.debug(f"Debug screenshot: {screenshot_path}")
        except Exception as e:
            self.logger.debug(f"Screenshot failed: {e}")


# EOF

# EOF
