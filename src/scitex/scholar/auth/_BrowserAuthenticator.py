#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:43:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_BrowserAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_BrowserAuthenticator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Browser-based authentication operations.

This module handles browser interactions for authentication,
including login detection, navigation, and session verification.
"""

import asyncio
from typing import Any, Dict, List, Optional

from playwright.async_api import Browser, Page, async_playwright

from scitex import logging

from ..browser.local._BrowserMixin import BrowserMixin

logger = logging.getLogger(__name__)


class BrowserAuthenticator(BrowserMixin):
    """Handles browser-based authentication operations."""

    def __init__(self, mode: str = "interactive", timeout: int = 300):
        """Initialize browser authenticator.
        
        Args:
            mode: Browser mode - 'interactive' for authentication, 'stealth' for scraping
            timeout: Timeout for browser operations in seconds
        """
        super().__init__(mode=mode)
        self.timeout = timeout

    async def navigate_to_login_async(self, url: str) -> Page:
        """Navigate to login URL and return page.
        
        Args:
            url: Login URL to navigate to
            
        Returns:
            Page object for further operations
        """
        # Use the BrowserMixin's get_browser method to get properly configured browser
        browser = await self.get_browser()
        
        # Create context with proper interactive viewport settings
        context_options = {}
        if self.mode == "interactive":
            context_options["viewport"] = {"width": 1280, "height": 720}
        else:
            context_options["viewport"] = {"width": 1, "height": 1}
            
        context = await browser.new_context(**context_options)
        await self.cookie_acceptor.inject_auto_acceptor(context)
        page = await context.new_page()
        
        logger.info(f"Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        
        # Check for cookie banner and warn if present
        if await self.cookie_acceptor.check_cookie_banner_exists(page):
            logger.warning("Cookie banner detected - may need manual acceptance")
        
        return page

    async def wait_for_login_completion_async(self, page: Page, success_indicators: List[str]) -> bool:
        """Wait for login completion by monitoring URL changes and handling SSO automation.
        
        Args:
            page: Browser page to monitor
            success_indicators: List of URL patterns indicating successful login
            
        Returns:
            True if login successful, False if timed out
        """
        max_wait_time = self.timeout
        check_interval = 2
        elapsed_time = 0
        seen_sso_page = False

        while elapsed_time < max_wait_time:
            current_url = page.url

            # Track SSO navigation
            if self._is_sso_page(current_url):
                seen_sso_page = True
                logger.debug(f"Detected SSO/login page: {current_url}")

            # Check for University of Melbourne SSO and automate it
            if self._is_unimelb_sso_page(current_url):
                logger.info("University of Melbourne SSO detected - attempting automation")
                sso_success = await self._handle_unimelb_sso_async(page)
                if sso_success:
                    logger.success("University of Melbourne SSO automation completed")
                    # Continue waiting for final success after SSO
                else:
                    logger.warning("University of Melbourne SSO automation failed - manual intervention required")

            # Check for success
            if self._check_success_indicators(current_url, success_indicators):
                if await self._verify_login_success(page, seen_sso_page, elapsed_time):
                    logger.info(f"Login successful detected at URL: {current_url}")
                    logger.success("Login detected! Capturing session...")
                    return True

            # Show progress
            if elapsed_time % 10 == 0 and elapsed_time > 0:
                logger.info(f"Waiting for login... ({elapsed_time}s elapsed)")

            await asyncio.sleep(check_interval)
            elapsed_time += check_interval

        logger.error("Login timeout - please try again")
        return False

    async def verify_authentication_async(self, verification_url: str, cookies: List[Dict[str, Any]]) -> bool:
        """Verify authentication by checking access to protected page.
        
        Args:
            verification_url: URL to test access to
            cookies: Authentication cookies to use
            
        Returns:
            True if authentication verified, False otherwise
        """
        try:
            # Use stealth mode for verification (minimal viewport)
            original_mode = self.mode
            self.mode = "stealth"
            
            async with async_playwright() as p:
                browser, context = await self.create_browser_context(p)
                
                # Add cookies
                if cookies:
                    await context.add_cookies(cookies)

                page = await context.new_page()

                # Navigate to verification URL
                response = await page.goto(
                    verification_url,
                    wait_until="domcontentloaded",
                    timeout=15000,
                )

                current_url = page.url
                is_authenticated = self._check_authenticated_page(current_url)
                
                await browser.close()
                
                if is_authenticated:
                    logger.success(f"Verified live authentication at {current_url}")
                else:
                    logger.debug(f"Authentication verification failed at {current_url}")
                    
                return is_authenticated

        except Exception as e:
            logger.error(f"Authentication verification failed: {e}")
            return False
        finally:
            # Restore original mode setting
            self.mode = original_mode

    async def extract_session_cookies_async(self, page: Page) -> tuple[Dict[str, str], List[Dict[str, Any]]]:
        """Extract session cookies from browser page.
        
        Args:
            page: Browser page to extract cookies from
            
        Returns:
            Tuple of (simple_cookies_dict, full_cookies_list)
        """
        cookies = await page.context.cookies()
        simple_cookies = {c["name"]: c["value"] for c in cookies}
        return simple_cookies, cookies

    async def reliable_click_async(self, page: Page, selector: str) -> bool:
        """Perform reliable click using JavaScript (proven working pattern).
        
        Args:
            page: Browser page
            selector: CSS selector for element to click
            
        Returns:
            True if click successful, False otherwise
        """
        try:
            element = await page.wait_for_selector(selector, timeout=10000)
            if element:
                await page.evaluate('(element) => element.click()', element)
                logger.debug(f"JavaScript click successful on: {selector}")
                return True
            else:
                logger.error(f"Element not found for reliable click: {selector}")
                return False
        except Exception as e:
            logger.error(f"Reliable click failed on {selector}: {e}")
            return False

    async def reliable_fill_async(self, page: Page, selector: str, value: str) -> bool:
        """Perform reliable form fill using direct value setting (proven working pattern).
        
        Args:
            page: Browser page
            selector: CSS selector for input element
            value: Value to set
            
        Returns:
            True if fill successful, False otherwise
        """
        try:
            element = await page.wait_for_selector(selector, timeout=10000)
            if element:
                # Use JavaScript for direct value setting (faster than typing)
                await page.evaluate(
                    '(element, value) => { element.value = value; element.dispatchEvent(new Event("input", { bubbles: true })); }',
                    element, value
                )
                logger.debug(f"Direct value set successful on: {selector}")
                return True
            else:
                logger.error(f"Element not found for reliable fill: {selector}")
                return False
        except Exception as e:
            logger.error(f"Reliable fill failed on {selector}: {e}")
            return False

    def display_login_instructions(self, email: Optional[str], timeout: int) -> None:
        """Display login instructions to user using proper logging.
        
        Args:
            email: User email to display
            timeout: Timeout to display
        """
        logger.info("OpenAthens Authentication Required")
        logger.info("MyAthens login page is opening...")
        if email:
            logger.info(f"Account: {email}")
        logger.info("Please complete the login process:")
        logger.info("1. Enter your institutional email")
        logger.info("2. Click your institution when it appears")
        logger.info("3. Complete login on your institution's page")
        logger.info("4. You'll be redirected back to OpenAthens when done")
        logger.info(f"5. Timeout is {timeout} seconds")
        logger.info("6. Close the window after successful login")
        
        # Show environment variables
        logger.debug("OpenAthens Environment Variables:")
        for key, value in os.environ.items():
            if "SCITEX_SCHOLAR_OPENATHENS" in key:
                logger.debug(f"  {key}: {value}")

    def _is_sso_page(self, url: str) -> bool:
        """Check if URL indicates SSO/login page."""
        return "sso" in url.lower() or "login" in url.lower()

    def _check_success_indicators(self, url: str, indicators: List[str]) -> bool:
        """Check if URL matches any success indicators."""
        return any(indicator in url for indicator in indicators)

    async def _verify_login_success(self, page: Page, seen_sso_page: bool, elapsed_time: int) -> bool:
        """Verify login success with additional checks."""
        # Additional verification logic can be added here
        return seen_sso_page or elapsed_time > 30

    def _check_authenticated_page(self, url: str) -> bool:
        """Check if URL indicates authenticated page."""
        authenticated_patterns = ["/account", "/app", "/library"]
        unauthenticated_patterns = ["login", "signin"]
        
        # Check for unauthenticated patterns first
        if any(pattern in url for pattern in unauthenticated_patterns):
            return False
            
        # Check for authenticated patterns
        return any(pattern in url for pattern in authenticated_patterns)

    def _is_unimelb_sso_page(self, url: str) -> bool:
        """Check if URL is University of Melbourne SSO page."""
        unimelb_domains = [
            "login.unimelb.edu.au",
            "okta.unimelb.edu.au", 
            "authenticate.unimelb.edu.au",
            "sso.unimelb.edu.au",
        ]
        return any(domain in url.lower() for domain in unimelb_domains)

    async def _handle_unimelb_sso_async(self, page: Page) -> bool:
        """Handle University of Melbourne SSO automation using proven working patterns."""
        try:
            import os
            
            # Get credentials from environment
            username = os.environ.get("UNIMELB_SSO_USERNAME")
            password = os.environ.get("UNIMELB_SSO_PASSWORD")
            
            if not username or not password:
                logger.warning("UniMelb credentials not found in environment variables")
                logger.info("Set UNIMELB_SSO_USERNAME and UNIMELB_SSO_PASSWORD environment variables")
                return False
                
            logger.info("Starting University of Melbourne SSO automation")
            
            # Check if this is the OpenAthens institution search page
            current_url = page.url
            if "my.openathens.net" in current_url:
                return await self._handle_openathens_institution_selection(page)
            
            # Handle UniMelb SSO login page (two-step process)
            elif self._is_unimelb_sso_page(current_url):
                return await self._handle_unimelb_login_steps(page, username, password)
                
            return False
            
        except Exception as e:
            logger.error(f"UniMelb SSO automation failed: {e}")
            return False

    async def _handle_openathens_institution_selection(self, page: Page) -> bool:
        """Handle OpenAthens institution selection for UniMelb."""
        try:
            logger.info("Handling OpenAthens institution selection")
            
            # Step 1: Fill institution search with UniMelb email
            email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL", "")
            if not email:
                logger.error("No OpenAthens email found")
                return False
                
            # Use the proven working selector for institution search
            institution_input_selector = "#type-ahead"
            success = await self.reliable_fill_async(page, institution_input_selector, email)
            if not success:
                logger.error("Failed to fill institution search field")
                return False
                
            logger.info(f"Filled institution search with: {email}")
            
            # Step 2: Wait for dropdown and select University of Melbourne
            await page.wait_for_timeout(2000)  # Wait for dropdown to appear
            
            # Use JavaScript to find and click University of Melbourne
            result = await page.evaluate('''
                () => {
                    const elements = document.querySelectorAll('*');
                    for (let element of elements) {
                        if (element.textContent && element.textContent.includes('University of Melbourne')) {
                            let clickable = element;
                            while (clickable && !clickable.onclick && clickable.tagName !== 'BUTTON' && !clickable.getAttribute('role')) {
                                clickable = clickable.parentElement;
                            }
                            if (clickable) {
                                clickable.click();
                                return 'University of Melbourne selected';
                            } else {
                                element.click();
                                return 'University of Melbourne clicked directly';
                            }
                        }
                    }
                    return 'University of Melbourne not found';
                }
            ''')
            
            if 'selected' in result or 'clicked' in result:
                logger.success(result)
                return True
            else:
                logger.error(result)
                return False
                
        except Exception as e:
            logger.error(f"OpenAthens institution selection failed: {e}")
            return False

    async def _handle_unimelb_login_steps(self, page: Page, username: str, password: str) -> bool:
        """Handle University of Melbourne login steps (proven working patterns)."""
        try:
            logger.info("Handling UniMelb login steps")
            
            # Step 1: Handle username entry (first step)
            username_success = await self._handle_unimelb_username_step(page, username)
            if not username_success:
                logger.error("Username step failed")
                return False
                
            # Step 2: Handle password entry (second step)  
            password_success = await self._handle_unimelb_password_step(page, password)
            if not password_success:
                logger.error("Password step failed")
                return False
                
            # Step 3: Handle potential 2FA
            await self._handle_unimelb_duo_2fa(page)
            
            return True
            
        except Exception as e:
            logger.error(f"UniMelb login steps failed: {e}")
            return False

    async def _handle_unimelb_username_step(self, page: Page, username: str) -> bool:
        """Handle username entry using proven working selector."""
        try:
            # Use proven working selector for username
            username_selector = "input[name='identifier']"
            
            success = await self.reliable_fill_async(page, username_selector, username)
            if not success:
                logger.error("Failed to fill username field")
                return False
                
            logger.info(f"Filled username: {username}")
            
            # Click Next button using proven working selector
            next_selector = "input.button-primary[value='Next']"
            success = await self.reliable_click_async(page, next_selector)
            if not success:
                logger.error("Failed to click Next button")
                return False
                
            logger.info("Next button clicked successfully")
            
            # Wait for page transition
            await page.wait_for_timeout(1000)
            return True
            
        except Exception as e:
            logger.error(f"Username step failed: {e}")
            return False

    async def _handle_unimelb_password_step(self, page: Page, password: str) -> bool:
        """Handle password entry using proven working selector."""
        try:
            # Use proven working selector for password
            password_selector = "input[name='credentials.passcode']"
            
            success = await self.reliable_fill_async(page, password_selector, password)
            if not success:
                logger.error("Failed to fill password field")
                return False
                
            logger.info("Password filled successfully")
            
            # Click Verify button using proven working selector
            verify_selector = "input[type='submit'][value='Verify']"
            success = await self.reliable_click_async(page, verify_selector)
            if not success:
                logger.error("Failed to click Verify button")
                return False
                
            logger.info("Verify button clicked successfully")
            return True
            
        except Exception as e:
            logger.error(f"Password step failed: {e}")
            return False

    async def _handle_unimelb_duo_2fa(self, page: Page) -> bool:
        """Handle Duo 2FA if it appears."""
        try:
            # Quick check for Duo elements
            duo_elements = await page.query_selector_all('.authenticator-verify-list')
            
            if not duo_elements:
                try:
                    await page.wait_for_selector('.authenticator-verify-list', timeout=3000)
                except TimeoutError:
                    return True  # No 2FA required
                    
            logger.info("Duo 2FA detected - attempting to handle push notification")
            
            # Try push notification (proven working pattern)
            push_buttons = await page.query_selector_all(
                'xpath=//h3[contains(text(), "Get a push notification")]/../..//a[contains(@class, "button")]'
            )
            
            if push_buttons:
                await push_buttons[0].click()
                logger.success("Push notification requested - please check your device")
                
                # Send notification to user via SSO notification system
                await self._notify_2fa_required()
                
            else:
                # Fallback to any available auth method
                auth_buttons = await page.query_selector_all('.authenticator-button a.button')
                if auth_buttons:
                    await auth_buttons[0].click()
                    logger.info("Alternative 2FA method selected")
                else:
                    logger.warning("No 2FA methods found - manual intervention may be required")
                    
            return True
            
        except Exception as e:
            logger.error(f"Duo 2FA handling failed: {e}")
            return False

    async def _notify_2fa_required(self) -> None:
        """Send 2FA notification using centralized SSO notification system."""
        try:
            # Create a temporary SSO automator instance for notification
            from .sso_automations._UniversityOfMelbourneSSOAutomator import UniversityOfMelbourneSSOAutomator
            
            # Create temporary automator instance for notification
            temp_automator = UniversityOfMelbourneSSOAutomator()
            
            # Send notification via centralized system
            await temp_automator.notify_user_async(
                "2fa_required",
                timeout=self.timeout,
                method="Duo Push Notification",
                device="Registered mobile device"
            )
            
        except Exception as e:
            logger.debug(f"Failed to send 2FA notification: {e}")
            # Don't fail authentication if notification fails


# EOF