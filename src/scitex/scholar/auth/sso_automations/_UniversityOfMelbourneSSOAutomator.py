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
        """Perform UniMelb login flow."""
        try:
            self.logger.info("Starting UniMelb SSO login")

            # Wait for and fill username
            username_selectors = [
                "input[name='username']",
                "input[id='username']",
                "input[name='okta-signin-username']",
                "input[id='okta-signin-username']",
                "input[type='text'][name*='user']",
                "input[type='email']",
            ]

            username_field = None
            for selector in username_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    username_field = selector
                    break
                except TimeoutError:
                    continue

            if not username_field:
                self.logger.error("Could not find username field")
                return False

            self.logger.debug(f"Found username field: {username_field}")
            await page.fill(username_field, self.username)

            # Fill password - might be on same page or next page
            password_selectors = [
                "input[name='password']",
                "input[id='password']",
                "input[name='okta-signin-password']",
                "input[id='okta-signin-password']",
                "input[type='password']",
            ]

            # Check if password field is already visible
            password_visible = False
            for selector in password_selectors:
                if await page.locator(selector).count() > 0:
                    await page.fill(selector, self.password)
                    password_visible = True
                    self.logger.debug(f"Filled password field: {selector}")
                    break

            # Submit form (might be username only first)
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Sign in')",
                "button:has-text('Log in')",
                "button:has-text('Next')",
                "#okta-signin-submit",
            ]

            for selector in submit_selectors:
                if await page.locator(selector).count() > 0:
                    await page.click(selector)
                    self.logger.debug(f"Clicked submit: {selector}")
                    break

            # If password wasn't visible, wait for next page
            if not password_visible:
                await page.wait_for_load_state("networkidle")

                # Now fill password
                for selector in password_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        await page.fill(selector, self.password)
                        self.logger.debug(
                            f"Filled password on second page: {selector}"
                        )
                        break
                    except TimeoutError:
                        continue

                # Submit again
                for selector in submit_selectors:
                    if await page.locator(selector).count() > 0:
                        await page.click(selector)
                        self.logger.debug(f"Clicked final submit: {selector}")
                        break

            # Wait for redirect away from SSO
            self.logger.info("Waiting for SSO completion...")

            # Wait up to 30 seconds for redirect
            for _ in range(30):
                await page.wait_for_timeout(1000)
                if not self.is_sso_page(page.url):
                    self.logger.success("SSO login successful")
                    return True

                # Check for 2FA or other prompts
                if "duo" in page.url.lower() or "2fa" in page.url.lower():
                    self.logger.info(
                        "2FA required - please complete in browser"
                    )
                    # In non-headless mode, user can complete 2FA
                    if not self.headless:
                        # Wait longer for 2FA
                        for _ in range(60):
                            await page.wait_for_timeout(1000)
                            if not self.is_sso_page(page.url):
                                self.logger.success(
                                    "SSO login successful after 2FA"
                                )
                                return True

            self.logger.warning("SSO login timed out")
            return False

        except Exception as e:
            self.logger.error(f"SSO login failed: {e}")

            # Take screenshot for debugging
            try:
                screenshot_path = (
                    Path.home() / ".scitex" / "scholar" / "sso_error.png"
                )
                await page.screenshot(path=str(screenshot_path))
                self.logger.debug(
                    f"Error screenshot saved to {screenshot_path}"
                )
            except:
                pass

            return False

# EOF
