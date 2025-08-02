#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 03:45:00 (claude)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_OpenAthensAutomation.py
# ----------------------------------------

"""
OpenAthens institutional authentication automation.

This module provides scalable automation for OpenAthens SSO that can be extended
to support multiple institutions beyond University of Melbourne.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from playwright.async_api import Page, TimeoutError

from scitex import logging
from ..utils._email import send_email_async

logger = logging.getLogger(__name__)


def _get_timestamp() -> str:
    """Get timestamp for logging and screenshots."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


async def _debug_screenshot(page: Page, description: str) -> None:
    """Take debug screenshot with timestamp."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        screenshot_path = Path(__file__).parent.parent.parent.parent / ".dev" / f"debug_{timestamp}_{description}.png"
        await page.screenshot(path=str(screenshot_path))
        logger.info(f"[{_get_timestamp()}] 📸 Screenshot saved: {screenshot_path}")
    except Exception as e:
        logger.debug(f"Screenshot failed: {e}")


class OpenAthensAutomation:
    """Handles OpenAthens institutional authentication automation."""
    
    def __init__(self, institution_config: Optional[Dict[str, Any]] = None):
        """Initialize OpenAthens automation.
        
        Args:
            institution_config: Configuration for specific institution
        """
        self.institution_config = institution_config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for University of Melbourne."""
        return {
            "institution_name": "University of Melbourne",
            "institution_email": os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL", ""),
            "sso_username": os.environ.get("UNIMELB_SSO_USERNAME", ""),
            "sso_password": os.environ.get("UNIMELB_SSO_PASSWORD", ""),
            "notification_email": os.environ.get("UNIMELB_EMAIL") or os.environ.get("SCITEX_EMAIL_YWATANABE", ""),
            "sso_domains": [
                "login.unimelb.edu.au",
                "okta.unimelb.edu.au", 
                "authenticate.unimelb.edu.au",
                "sso.unimelb.edu.au"
            ],
            "username_selector": "input[name='identifier']",
            "password_selector": "input[name='credentials.passcode']",
            "next_button_selector": "input.button-primary[value='Next']",
            "verify_button_selector": "input[type='submit'][value='Verify']"
        }
    
    async def perform_openathens_authentication_async(self, page: Page) -> bool:
        """Perform complete OpenAthens authentication flow.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            logger.info("Starting OpenAthens institutional authentication")
            
            # Send initial notification
            await self._notify_user_intervention_async("authentication_started")
            
            # Step 1: Navigate to OpenAthens
            await page.goto("https://my.openathens.net/?passiveLogin=false", wait_until="domcontentloaded")
            logger.info("Navigated to OpenAthens")
            
            # Step 2: Analyze page content first
            await self._analyze_page_content_async(page, "initial_openathens")
            
            # Step 3: Handle cookie banner if present
            await self._handle_cookie_banner_async(page)
            
            # Step 4: Analyze page after cookie handling
            await self._analyze_page_content_async(page, "after_cookies")
            
            # Step 5: Fill institutional email and select institution
            success = await self._handle_institution_selection_async(page)
            if not success:
                # Analyze page state when selection fails
                await self._analyze_page_content_async(page, "selection_failed")
                await self._notify_user_intervention_async("institution_selection_failed")
                return False
            
            # Step 6: Analyze page after successful selection
            await self._analyze_page_content_async(page, "after_selection")
            
            # Step 6.5: Handle cookies again if they reappeared
            await self._handle_cookie_banner_async(page)
            
            # Step 7: Handle UniMelb SSO login
            success = await self._handle_unimelb_sso_login_async(page)
            if not success:
                await self._notify_user_intervention_async("sso_login_failed")
                return False
            
            # Step 5: Handle 2FA if needed
            await self._handle_2fa_async(page)
            
            # Step 6: Wait for authentication completion
            success = await self._wait_for_completion_async(page)
            
            if success:
                await self._notify_user_intervention_async("authentication_success")
                logger.success("OpenAthens authentication completed successfully")
            else:
                await self._notify_user_intervention_async("authentication_timeout")
                logger.error("OpenAthens authentication timed out")
            
            return success
            
        except Exception as e:
            logger.error(f"OpenAthens authentication failed: {e}")
            await self._notify_user_intervention_async("authentication_error", error=str(e))
            return False
    
    async def _handle_cookie_banner_async(self, page: Page) -> bool:
        """Handle cookie acceptance banner."""
        try:
            # Wait for page to load and cookie banner to potentially appear
            await asyncio.sleep(2)
            
            # Try multiple strategies to find and click cookie acceptance
            
            # Strategy 1: Look for "Accept all cookies" button specifically
            accept_all_btn = await page.query_selector('button:has-text("Accept all cookies")')
            if accept_all_btn:
                await accept_all_btn.click()
                logger.info("Clicked 'Accept all cookies' button")
                await asyncio.sleep(1)
                return True
            
            # Strategy 2: Look for any button containing "Accept all"
            buttons = await page.query_selector_all('button')
            for button in buttons:
                try:
                    text = await button.text_content()
                    if text and 'accept all' in text.lower():
                        await button.click()
                        logger.info(f"Clicked cookie button: {text}")
                        await asyncio.sleep(1)
                        return True
                except:
                    continue
            
            # Strategy 3: Use JavaScript to find and click cookie buttons (enhanced)
            result = await page.evaluate("""
                () => {
                    // Look for buttons with cookie-related text (comprehensive list)
                    const buttons = Array.from(document.querySelectorAll('button, a, div[role="button"], span[role="button"]'));
                    const cookieTexts = [
                        'accept all cookies',
                        'accept all',
                        'accept cookies',
                        'allow all',
                        'ok',
                        'got it',
                        'i accept',
                        'agree',
                        'continue'
                    ];
                    
                    for (let button of buttons) {
                        const text = (button.textContent || '').toLowerCase().trim();
                        
                        // Check if button text matches any cookie acceptance phrases
                        for (let cookieText of cookieTexts) {
                            if (text.includes(cookieText)) {
                                // Make sure the button is visible and clickable
                                if (button.offsetParent !== null) {
                                    try {
                                        button.click();
                                        return 'clicked: ' + text;
                                    } catch (e) {
                                        continue;
                                    }
                                }
                            }
                        }
                    }
                    
                    // Also try to find and dismiss any overlay/modal that might be blocking
                    const overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="popup"], [class*="banner"]');
                    for (let overlay of overlays) {
                        const closeButton = overlay.querySelector('button[aria-label*="close"], button[title*="close"], .close, [class*="close"]');
                        if (closeButton && closeButton.offsetParent !== null) {
                            closeButton.click();
                            return 'closed overlay';
                        }
                    }
                    
                    return 'no cookie buttons found';
                }
            """)
            
            if 'clicked' in result:
                logger.info(f"Cookie banner handled via JavaScript: {result}")
                await asyncio.sleep(1)
                return True
            
            # Strategy 4: Use PyAutoGUI as fallback for cookie clicking
            try:
                from ._PyAutoGUIAutomation import PyAutoGUIAutomation
                
                logger.info("Trying PyAutoGUI for cookie banner...")
                pyautogui_automation = PyAutoGUIAutomation(confidence=0.6)
                
                # Try to click common cookie acceptance text
                cookie_texts = ["Accept all cookies", "Accept all", "OK", "Got it", "I accept"]
                for cookie_text in cookie_texts:
                    success = await pyautogui_automation.find_and_click_text_async(cookie_text)
                    if success:
                        logger.info(f"✅ PyAutoGUI successfully clicked cookie: '{cookie_text}'")
                        await asyncio.sleep(1)
                        return True
                
                logger.debug("PyAutoGUI couldn't find cookie buttons")
                
            except Exception as e:
                logger.debug(f"PyAutoGUI cookie handling failed: {e}")
            
            logger.debug("No cookie banner found or already handled")
            return True  # Continue even if no cookie banner
            
        except Exception as e:
            logger.debug(f"Cookie banner handling failed: {e}")
            return True  # Don't fail authentication for cookie issues
    
    async def _analyze_page_content_async(self, page: Page, stage: str) -> Dict[str, Any]:
        """Analyze page content and structure for debugging."""
        try:
            # Get page info
            page_info = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        readyState: document.readyState,
                        
                        // Form elements
                        inputCount: document.querySelectorAll('input').length,
                        buttonCount: document.querySelectorAll('button').length,
                        formCount: document.querySelectorAll('form').length,
                        
                        // Specific elements we're looking for
                        hasInstitutionInput: !!document.querySelector('input[placeholder*="Institution"], input[placeholder*="email"], #type-ahead'),
                        hasCookieBanner: !!document.querySelector('[class*="cookie"], [id*="cookie"]') || 
                                        Array.from(document.querySelectorAll('*')).some(el => 
                                            el.textContent && el.textContent.includes('cookies')),
                        hasUnimelbOption: Array.from(document.querySelectorAll('*')).some(el => 
                                         el.textContent && el.textContent.includes('University of Melbourne')),
                        
                        // Get all button texts
                        buttonTexts: Array.from(document.querySelectorAll('button')).map(btn => btn.textContent?.trim()).filter(Boolean),
                        
                        // Get all input placeholders
                        inputPlaceholders: Array.from(document.querySelectorAll('input')).map(inp => inp.placeholder).filter(Boolean),
                        
                        // Check for dropdown/suggestions
                        hasVisibleDropdown: document.querySelectorAll('[class*="dropdown"], [class*="suggestion"], [class*="autocomplete"]').length > 0,
                        
                        // Get page text (first 500 chars for debugging)
                        pageText: document.body.innerText.substring(0, 500)
                    };
                }
            """)
            
            logger.info(f"Page Analysis [{stage}]:")
            logger.info(f"  Title: {page_info['title']}")
            logger.info(f"  URL: {page_info['url']}")
            logger.info(f"  Elements: {page_info['inputCount']} inputs, {page_info['buttonCount']} buttons")
            logger.info(f"  Institution input: {page_info['hasInstitutionInput']}")
            logger.info(f"  Cookie banner: {page_info['hasCookieBanner']}")
            logger.info(f"  UniMelb option: {page_info['hasUnimelbOption']}")
            logger.info(f"  Visible dropdown: {page_info['hasVisibleDropdown']}")
            
            if page_info['buttonTexts']:
                logger.info(f"  Button texts: {page_info['buttonTexts']}")
            
            if page_info['inputPlaceholders']:
                logger.info(f"  Input placeholders: {page_info['inputPlaceholders']}")
            
            # Save HTML content for debugging
            html_content = await page.content()
            debug_path = Path(__file__).parent.parent.parent.parent / ".dev" / f"openathens_{stage}.html"
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"  HTML saved: {debug_path}")
            
            return page_info
            
        except Exception as e:
            logger.error(f"Page analysis failed: {e}")
            return {}
    
    async def _handle_institution_selection_async(self, page: Page) -> bool:
        """Handle institutional email entry and selection."""
        try:
            institution_email = self.institution_config.get("institution_email")
            if not institution_email:
                logger.error("No institutional email configured")
                return False
            
            logger.info(f"Filling institutional email: {institution_email}")
            
            # Find and fill the institution search field
            search_selector = 'input[placeholder*="Institution"], input[placeholder*="email"], #type-ahead'
            search_field = await page.wait_for_selector(search_selector, timeout=10000)
            
            if not search_field:
                logger.error("Institution search field not found")
                return False
            
            # Fill the field and trigger events to activate dropdown
            await search_field.fill(institution_email)
            logger.info("Institution email filled")
            
            # Use the proven simple keyboard navigation approach
            # This approach works reliably: Fill → Enter → 5sec → ArrowDown → Enter
            logger.info(f"[{_get_timestamp()}] Using proven simple keyboard navigation...")
            await _debug_screenshot(page, "institution_selection_start")
            
            success = await self._simple_keyboard_navigation_async(page, search_field)
            if success:
                logger.success(f"[{_get_timestamp()}] ✅ Institution selection successful!")
                return True
            
            logger.error(f"[{_get_timestamp()}] ❌ Institution selection failed")
            await _debug_screenshot(page, "institution_selection_failed")
            return False
            
        except Exception as e:
            logger.error(f"Institution selection failed: {e}")
            return False
    
    async def _wait_for_navigation_async(self, page: Page, timeout: int = 15) -> bool:
        """Wait for navigation away from OpenAthens after institution selection.
        
        Args:
            page: Playwright page object
            timeout: Maximum time to wait for navigation
            
        Returns:
            True if navigation successful, False if timeout
        """
        try:
            initial_url = page.url
            logger.info(f"Waiting for navigation from: {initial_url}")
            
            # Wait for navigation with multiple checks
            for i in range(timeout):
                await asyncio.sleep(1)
                current_url = page.url
                
                # Check if we've navigated away from OpenAthens
                if current_url != initial_url:
                    logger.info(f"Navigation detected: {initial_url} -> {current_url}")
                    
                    # Check if we're now on an SSO page
                    if self._is_sso_page(current_url):
                        logger.success(f"Successfully navigated to SSO page: {current_url}")
                        return True
                    elif "my.openathens.net" not in current_url:
                        logger.success(f"Successfully navigated away from OpenAthens: {current_url}")
                        return True
                    else:
                        logger.info(f"Navigation detected but still on OpenAthens: {current_url}")
                
                # Progress indicator
                if i > 0 and i % 5 == 0:
                    logger.info(f"Still waiting for navigation... ({timeout-i}s remaining)")
            
            logger.error(f"Navigation timeout after {timeout}s")
            return False
            
        except Exception as e:
            logger.error(f"Navigation waiting failed: {e}")
            return False
    
    async def _ocr_click_institution_async(self, page: Page) -> bool:
        """Use OCR to find and click institution option."""
        try:
            from ._OCRAutomation import ocr_click_university_of_melbourne
            
            logger.info("🔍 Attempting OCR-based institution selection...")
            success = await ocr_click_university_of_melbourne(page)
            
            if success:
                # Wait for navigation after OCR click
                await asyncio.sleep(3)
                current_url = page.url
                
                # Check if we navigated away from OpenAthens
                if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                    logger.success("OCR click successful - navigated to SSO page")
                    return True
                else:
                    logger.info("OCR click executed but no navigation detected")
                    return False
            else:
                logger.error("OCR-based institution selection failed")
                return False
                
        except Exception as e:
            logger.error(f"OCR institution selection failed: {e}")
            return False
    
    async def _pyautogui_click_institution_async(self, page: Page) -> bool:
        """Use PyAutoGUI screen automation to find and click institution option."""
        try:
            logger.info("🖱️  Attempting PyAutoGUI-based institution selection...")
            success = await pyautogui_click_university_of_melbourne()
            
            if success:
                # Wait for navigation after PyAutoGUI click
                await asyncio.sleep(3)
                current_url = page.url
                
                # Check if we navigated away from OpenAthens
                if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                    logger.success("PyAutoGUI click successful - navigated to SSO page")
                    return True
                else:
                    logger.info("PyAutoGUI click executed but no navigation detected")
                    return False
            else:
                logger.error("PyAutoGUI-based institution selection failed")
                return False
                
        except Exception as e:
            logger.error(f"PyAutoGUI institution selection failed: {e}")
            return False
    
    async def _tab_key_navigation_async(self, page: Page, search_field) -> bool:
        """Use Tab key to navigate to University of Melbourne option and press Enter."""
        try:
            logger.info("🔄 Attempting Tab key navigation to UniMelb option...")
            
            # Make sure search field is focused
            await search_field.focus()
            await asyncio.sleep(0.5)
            
            # Press Tab key to move focus to the first dropdown option
            await page.keyboard.press('Tab')
            await asyncio.sleep(0.5)
            
            # Check if we're now on University of Melbourne option
            focused_element = await page.evaluate("""
                () => {
                    const focused = document.activeElement;
                    if (focused) {
                        return {
                            text: focused.textContent || '',
                            tag: focused.tagName,
                            classes: focused.className,
                            hasUnimelb: (focused.textContent || '').includes('University of Melbourne')
                        };
                    }
                    return null;
                }
            """)
            
            logger.info(f"Focused element: {focused_element}")
            
            if focused_element and focused_element.get('hasUnimelb'):
                logger.info("✅ Tab navigation focused on University of Melbourne!")
                
                # Press Enter to select
                await page.keyboard.press('Enter')
                await asyncio.sleep(2)
                
                # Check if navigation occurred
                current_url = page.url
                if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                    logger.success("Tab + Enter navigation successful!")
                    return True
                else:
                    logger.info("Tab + Enter executed but no navigation detected")
                    
                    # Try Space key as alternative
                    await page.keyboard.press('Space')
                    await asyncio.sleep(2)
                    
                    current_url = page.url
                    if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                        logger.success("Tab + Space navigation successful!")
                        return True
                    else:
                        logger.info("Tab + Space also didn't trigger navigation")
                        return False
            else:
                logger.info("Tab navigation didn't focus on University of Melbourne")
                
                # Try pressing Tab a few more times to find the right option
                for i in range(5):
                    await page.keyboard.press('Tab')
                    await asyncio.sleep(0.3)
                    
                    focused_element = await page.evaluate("""
                        () => {
                            const focused = document.activeElement;
                            if (focused && (focused.textContent || '').includes('University of Melbourne')) {
                                return {
                                    text: focused.textContent,
                                    hasUnimelb: true
                                };
                            }
                            return null;
                        }
                    """)
                    
                    if focused_element and focused_element.get('hasUnimelb'):
                        logger.info(f"✅ Found UniMelb on Tab attempt {i+2}!")
                        
                        # Press Enter to select
                        await page.keyboard.press('Enter')
                        await asyncio.sleep(2)
                        
                        current_url = page.url
                        if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                            logger.success("Tab navigation successful!")
                            return True
                        
                        # Try Space as alternative
                        await page.keyboard.press('Space')
                        await asyncio.sleep(2)
                        
                        current_url = page.url
                        if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                            logger.success("Tab + Space navigation successful!")
                            return True
                
                logger.info("Couldn't find UniMelb option through Tab navigation")
                return False
                
        except Exception as e:
            logger.error(f"Tab key navigation failed: {e}")
            return False
    
    async def _simple_keyboard_navigation_async(self, page: Page, search_field) -> bool:
        """Use simple Fill → Enter → 5sec → ArrowDown → Enter approach."""
        try:
            logger.info(f"[{_get_timestamp()}] 🔄 Starting simple keyboard navigation...")
            await _debug_screenshot(page, "01_before_keyboard_nav")
            
            # Focus on search field
            await search_field.focus()
            logger.info(f"[{_get_timestamp()}] 🎯 Search field focused")
            await asyncio.sleep(0.5)
            
            # Press Enter to activate dropdown
            await page.keyboard.press('Enter')
            logger.info(f"[{_get_timestamp()}] ⏎ Pressed Enter to activate dropdown")
            await _debug_screenshot(page, "02_after_enter_pressed")
            
            # Wait 5 seconds for dropdown to appear
            logger.info(f"[{_get_timestamp()}] ⏳ Waiting 5 seconds for dropdown...")
            await asyncio.sleep(5)
            await _debug_screenshot(page, "03_after_5sec_wait")
            
            # Press ArrowDown to select first option (which should be UniMelb)
            await page.keyboard.press('ArrowDown')
            logger.info(f"[{_get_timestamp()}] ⬇️ Pressed ArrowDown to select first option")
            await asyncio.sleep(1)
            await _debug_screenshot(page, "04_after_arrow_down")
            
            # Press Enter to confirm selection
            await page.keyboard.press('Enter')
            logger.info(f"[{_get_timestamp()}] ⏎ Pressed Enter to confirm selection")
            await asyncio.sleep(3)
            await _debug_screenshot(page, "05_after_final_enter")
            
            # Check if navigation occurred
            current_url = page.url
            logger.info(f"[{_get_timestamp()}] 🌐 Current URL: {current_url}")
            
            if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                logger.success(f"[{_get_timestamp()}] ✅ Simple keyboard navigation successful!")
                await _debug_screenshot(page, "06_success_page")
                return True
            else:
                logger.info(f"[{_get_timestamp()}] ❌ Enter didn't navigate, trying Space...")
                
                # Try Space as backup
                await page.keyboard.press('Space')
                await asyncio.sleep(3)
                await _debug_screenshot(page, "07_after_space_fallback")
                
                current_url = page.url
                if "my.openathens.net" not in current_url or self._is_sso_page(current_url):
                    logger.success(f"[{_get_timestamp()}] ✅ Simple keyboard navigation with Space successful!")
                    return True
                else:
                    logger.info(f"[{_get_timestamp()}] ❌ Simple keyboard navigation failed")
                    await _debug_screenshot(page, "08_final_failure")
                    return False
                    
        except Exception as e:
            logger.error(f"[{_get_timestamp()}] ❌ Simple keyboard navigation failed: {e}")
            await _debug_screenshot(page, "09_exception_error")
            return False
    
    async def _handle_unimelb_sso_login_async(self, page: Page) -> bool:
        """Handle University of Melbourne SSO login based on working spark project approach."""
        try:
            logger.info(f"[{_get_timestamp()}] 🔐 Starting UniMelb SSO login...")
            await _debug_screenshot(page, "sso_login_start")
            
            # Get credentials from config
            username = self.institution_config.get("sso_username")
            password = self.institution_config.get("sso_password")
            
            if not username or not password:
                logger.error(f"[{_get_timestamp()}] ❌ Missing SSO credentials in configuration")
                return False
            
            # Wait for login form - username field
            try:
                username_field = await page.wait_for_selector('input[name="identifier"]', timeout=10000)
                await username_field.fill(username)
                logger.info(f"[{_get_timestamp()}] 👤 Username filled")
                await _debug_screenshot(page, "sso_username_filled")
                await asyncio.sleep(0.5)
                
                # Click Next button
                next_button = await page.wait_for_selector('input.button-primary[value="Next"]', timeout=5000)
                await next_button.click()
                logger.info(f"[{_get_timestamp()}] ➡️ Next button clicked")
                await asyncio.sleep(2)
                await _debug_screenshot(page, "sso_after_next")
                
                # Wait for password field
                password_field = await page.wait_for_selector('input[name="credentials.passcode"]', timeout=10000)
                await password_field.fill(password)
                logger.info(f"[{_get_timestamp()}] 🔒 Password filled")
                await _debug_screenshot(page, "sso_password_filled")
                
                # Click Verify button
                verify_button = await page.wait_for_selector('input[type="submit"][value="Verify"]', timeout=5000)
                await verify_button.click()
                logger.info(f"[{_get_timestamp()}] ✅ Verify button clicked")
                await asyncio.sleep(3)
                await _debug_screenshot(page, "sso_after_verify")
                
                # Handle Duo 2FA if it appears
                await self._handle_duo_2fa_async(page)
                
                logger.success(f"[{_get_timestamp()}] ✅ UniMelb SSO login completed")
                return True
                
            except Exception as e:
                logger.error(f"[{_get_timestamp()}] ❌ SSO login failed: {e}")
                await _debug_screenshot(page, "sso_login_error")
                return False
                
        except Exception as e:
            logger.error(f"[{_get_timestamp()}] ❌ UniMelb SSO handling failed: {e}")
            return False
    
    async def _handle_duo_2fa_async(self, page: Page) -> bool:
        """Handle Duo 2FA authentication."""
        try:
            logger.info(f"[{_get_timestamp()}] 🔒 Checking for Duo 2FA...")
            await _debug_screenshot(page, "2fa_check_start")
            
            # Check if we're on a Duo authentication page
            try:
                auth_list = await page.wait_for_selector('.authenticator-verify-list', timeout=5000)
                logger.info(f"[{_get_timestamp()}] 🛡️ Duo 2FA detected")
                await _debug_screenshot(page, "2fa_page_detected")
                
                # Look for push notification option
                try:
                    push_button = await page.wait_for_selector('xpath=//h3[contains(text(), "Get a push notification")]/../..//a[contains(@class, "button")]', timeout=3000)
                    await push_button.click()
                    logger.info(f"[{_get_timestamp()}] 🔔 Push notification requested - check your device!")
                    await _debug_screenshot(page, "2fa_push_requested")
                    
                    # Send notification to user
                    await self._notify_user_intervention_async("duo_push_requested")
                    
                except:
                    # Try any authentication button as fallback
                    try:
                        auth_button = await page.wait_for_selector('.authenticator-button a.button', timeout=3000)
                        await auth_button.click()
                        logger.info(f"[{_get_timestamp()}] 📱 Alternative 2FA method selected")
                        await _debug_screenshot(page, "2fa_alternative_selected")
                        
                        await self._notify_user_intervention_async("duo_alternative_requested")
                    except:
                        logger.warning(f"[{_get_timestamp()}] ⚠️ No 2FA options found - manual intervention required")
                        await _debug_screenshot(page, "2fa_no_options")
                        await self._notify_user_intervention_async("duo_manual_required")
                        return False
                
                # Wait for authentication completion with regular checks
                logger.info(f"[{_get_timestamp()}] ⏳ Waiting for 2FA completion...")
                max_wait_time = 60  # 60 seconds total
                check_interval = 10  # Check every 10 seconds
                
                for attempt in range(max_wait_time // check_interval):
                    await asyncio.sleep(check_interval)
                    
                    current_url = page.url
                    logger.info(f"[{_get_timestamp()}] 🔍 2FA check {attempt + 1}/{max_wait_time // check_interval}: {current_url}")
                    
                    # Check if we've navigated away from SSO (authentication complete)
                    if not current_url.startswith("https://sso.unimelb.edu.au"):
                        logger.success(f"[{_get_timestamp()}] ✅ 2FA authentication completed - URL changed!")
                        await _debug_screenshot(page, "2fa_completed")
                        return True
                    
                    # Check if we're on a success page or final destination
                    try:
                        # Look for completion indicators
                        completion_check = await page.evaluate("""
                            () => {
                                return {
                                    hasPromptField: !!document.querySelector('input[name="prompt"]'),
                                    hasSuccessIndicator: document.body.innerText.toLowerCase().includes('success') ||
                                                        document.body.innerText.toLowerCase().includes('complete'),
                                    title: document.title,
                                    bodyText: document.body.innerText.substring(0, 200)
                                };
                            }
                        """)
                        
                        if completion_check['hasPromptField'] or completion_check['hasSuccessIndicator']:
                            logger.success(f"[{_get_timestamp()}] ✅ 2FA authentication completed - success indicators found!")
                            await _debug_screenshot(page, "2fa_completed")
                            return True
                            
                    except Exception as e:
                        logger.debug(f"Error checking completion: {e}")
                
                logger.warning(f"[{_get_timestamp()}] ⏰ 2FA timeout after {max_wait_time}s - continuing anyway")
                await _debug_screenshot(page, "2fa_timeout")
                return True  # Continue even if timeout, might still work
                    
            except:
                # No 2FA required
                logger.info(f"[{_get_timestamp()}] ℹ️ No 2FA required")
                await _debug_screenshot(page, "2fa_not_required")
                return True
                
        except Exception as e:
            logger.error(f"[{_get_timestamp()}] ❌ 2FA handling failed: {e}")
            await _debug_screenshot(page, "2fa_error")
            return True  # Continue anyway
    
    async def _select_institution_from_dropdown_async(self, page: Page) -> bool:
        """Try to select institution from dropdown using multiple strategies."""
        institution_name = self.institution_config.get("institution_name", "University of Melbourne")
        
        try:
            logger.info(f"Attempting to select: {institution_name}")
            
            # Strategy 1: Enhanced JavaScript selection with detailed logging
            result = await page.evaluate(f"""
                () => {{
                    const institutionName = '{institution_name}';
                    const elements = Array.from(document.querySelectorAll('*'));
                    
                    // Find all elements containing the institution name
                    const candidates = elements.filter(el => 
                        el.textContent && el.textContent.includes(institutionName)
                    );
                    
                    console.log('Institution selection attempt:');
                    console.log('- Institution name:', institutionName);
                    console.log('- Total elements:', elements.length);
                    console.log('- Candidates found:', candidates.length);
                    
                    // Log candidate details
                    candidates.forEach((el, i) => {{
                        console.log(`Candidate ${{i+1}}:`, {{
                            tag: el.tagName,
                            text: el.textContent.substring(0, 100),
                            visible: el.offsetParent !== null,
                            classes: el.className,
                            id: el.id
                        }});
                    }});
                    
                    // Try clicking each candidate with multiple strategies
                    for (let i = 0; i < candidates.length; i++) {{
                        const element = candidates[i];
                        console.log(`Attempting to click candidate ${{i+1}}...`);
                        
                        // Strategy 1: Direct click
                        try {{
                            if (element.offsetParent !== null) {{ // Check if visible
                                element.click();
                                console.log('✓ Direct click succeeded on candidate', i+1);
                                
                                // Wait a moment and check if URL changed
                                setTimeout(() => {{
                                    console.log('URL after click:', window.location.href);
                                }}, 1000);
                                
                                return `direct_click_success_candidate_${{i+1}}`;
                            }}
                        }} catch (e1) {{
                            console.log('✗ Direct click failed:', e1.message);
                        }}
                        
                        // Strategy 2: Parent element click
                        try {{
                            const parent = element.parentElement;
                            if (parent && parent.offsetParent !== null) {{
                                parent.click();
                                console.log('✓ Parent click succeeded on candidate', i+1);
                                return `parent_click_success_candidate_${{i+1}}`;
                            }}
                        }} catch (e2) {{
                            console.log('✗ Parent click failed:', e2.message);
                        }}
                        
                        // Strategy 3: Find the row container (most likely to work)
                        try {{
                            const rowContainer = element.closest('div, li, tr');
                            if (rowContainer && rowContainer !== element && rowContainer.offsetParent !== null) {{
                                // Look for arrow or clickable elements within the row
                                const arrow = rowContainer.querySelector('svg, .arrow, [class*="arrow"], [class*="chevron"]');
                                if (arrow) {{
                                    arrow.click();
                                    console.log('✓ Arrow click succeeded on candidate', i+1);
                                    return `arrow_click_success_candidate_${{i+1}}`;
                                }} else {{
                                    // Click the entire row container
                                    rowContainer.click();
                                    console.log('✓ Row container click succeeded on candidate', i+1);
                                    return `row_click_success_candidate_${{i+1}}`;
                                }}
                            }}
                        }} catch (e3) {{
                            console.log('✗ Row container click failed:', e3.message);
                        }}
                        
                        // Strategy 4: Find closest interactive element
                        try {{
                            const interactive = element.closest('div[onclick], a, button, [role="button"], .clickable, [tabindex]');
                            if (interactive && interactive !== element && interactive.offsetParent !== null) {{
                                interactive.click();
                                console.log('✓ Interactive element click succeeded on candidate', i+1);
                                return `interactive_click_success_candidate_${{i+1}}`;
                            }}
                        }} catch (e4) {{
                            console.log('✗ Interactive element click failed:', e4.message);
                        }}
                        
                        // Strategy 4: Synthetic mouse event
                        try {{
                            const rect = element.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {{ // Element has dimensions
                                const mouseEvent = new MouseEvent('click', {{
                                    view: window,
                                    bubbles: true,
                                    cancelable: true,
                                    clientX: rect.left + rect.width / 2,
                                    clientY: rect.top + rect.height / 2
                                }});
                                
                                element.dispatchEvent(mouseEvent);
                                console.log('✓ Mouse event succeeded on candidate', i+1);
                                return `mouse_event_success_candidate_${{i+1}}`;
                            }}
                        }} catch (e4) {{
                            console.log('✗ Mouse event failed:', e4.message);
                        }}
                    }}
                    
                    console.log('All click strategies failed for all candidates');
                    return 'all_strategies_failed';
                }}
            """)
            
            logger.info(f"JavaScript selection result: {result}")
            
            if 'success' in result:
                await asyncio.sleep(2)  # Wait for potential navigation
                return True
            
            # Strategy 2: Playwright-based element clicking
            logger.info("Trying Playwright-based selection...")
            elements = await page.query_selector_all('*')
            
            for element in elements:
                try:
                    text_content = await element.text_content()
                    if text_content and institution_name in text_content:
                        # Check if element is visible and attached
                        if await element.is_visible() and await element.is_enabled():
                            logger.info(f"Found visible element with text: {text_content[:50]}...")
                            await element.click(force=True)  # Force click
                            await asyncio.sleep(2)
                            return True
                except Exception as e:
                    logger.debug(f"Element click failed: {e}")
                    continue
            
            # Strategy 3: Keyboard navigation as final fallback
            logger.info("Trying keyboard navigation as fallback...")
            return await self._select_institution_keyboard_async(page, None)
            
        except Exception as e:
            logger.error(f"Dropdown selection failed: {e}")
            return False
    
    async def _select_institution_keyboard_async(self, page: Page, search_field) -> bool:
        """Use keyboard navigation to select institution."""
        try:
            # Focus on the search field
            await search_field.focus()
            
            # Press down arrow to select first suggestion
            await search_field.press('ArrowDown')
            await asyncio.sleep(0.5)
            
            # Press Enter to confirm selection
            await search_field.press('Enter')
            await asyncio.sleep(2)
            
            # Check if we moved away from the search page
            current_url = page.url
            if 'my.openathens.net' not in current_url or 'sso' in current_url.lower():
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Keyboard navigation failed: {e}")
            return False
    
    async def _handle_sso_login_async(self, page: Page) -> bool:
        """Handle SSO login with username and password."""
        try:
            # Wait for SSO page to load
            await asyncio.sleep(2)
            
            current_url = page.url
            if not self._is_sso_page(current_url):
                # Try waiting a bit more for redirect
                await asyncio.sleep(3)
                current_url = page.url
                
            if not self._is_sso_page(current_url):
                logger.error(f"Not redirected to SSO page: {current_url}")
                return False
            
            logger.info("On SSO page, handling login")
            
            # Step 1: Handle username entry
            success = await self._handle_username_step_async(page)
            if not success:
                return False
            
            # Step 2: Handle password entry  
            success = await self._handle_password_step_async(page)
            if not success:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"SSO login failed: {e}")
            return False
    
    async def _handle_username_step_async(self, page: Page) -> bool:
        """Handle username entry step."""
        try:
            username = self.institution_config.get("sso_username")
            if not username:
                logger.error("No SSO username configured")
                return False
            
            username_selector = self.institution_config.get("username_selector", "input[name='identifier']")
            
            # Wait for username field
            username_field = await page.wait_for_selector(username_selector, timeout=15000)
            if not username_field:
                logger.error("Username field not found")
                return False
            
            # Fill username using Playwright's fill method
            await username_field.fill(username)
            logger.info(f"Username filled: {username}")
            
            # Click Next button
            next_selector = self.institution_config.get("next_button_selector", "input.button-primary[value='Next']")
            next_button = await page.wait_for_selector(next_selector, timeout=10000)
            
            if next_button:
                await page.evaluate(f'document.querySelector("{next_selector}").click()')
                logger.info("Next button clicked")
                await asyncio.sleep(2)
                return True
            else:
                logger.error("Next button not found")
                return False
                
        except Exception as e:
            logger.error(f"Username step failed: {e}")
            return False
    
    async def _handle_password_step_async(self, page: Page) -> bool:
        """Handle password entry step."""
        try:
            password = self.institution_config.get("sso_password")
            if not password:
                logger.error("No SSO password configured")
                return False
            
            password_selector = self.institution_config.get("password_selector", "input[name='credentials.passcode']")
            
            # Wait for password field
            password_field = await page.wait_for_selector(password_selector, timeout=15000)
            if not password_field:
                logger.error("Password field not found")
                return False
            
            # Fill password using Playwright's fill method
            await password_field.fill(password)
            logger.info("Password filled")
            
            # Click Verify button
            verify_selector = self.institution_config.get("verify_button_selector", "input[type='submit'][value='Verify']")
            verify_button = await page.wait_for_selector(verify_selector, timeout=10000)
            
            if verify_button:
                await page.evaluate(f'document.querySelector("{verify_selector}").click()')
                logger.info("Verify button clicked")
                await asyncio.sleep(2)
                return True
            else:
                logger.error("Verify button not found")
                return False
                
        except Exception as e:
            logger.error(f"Password step failed: {e}")
            return False
    
    async def _handle_2fa_async(self, page: Page) -> bool:
        """Handle 2FA authentication."""
        try:
            # Wait briefly to see if 2FA page appears
            await asyncio.sleep(3)
            
            # Check for Duo/2FA elements
            duo_elements = await page.query_selector_all('.authenticator-verify-list, .duo-frame, iframe[src*="duo"]')
            
            if not duo_elements:
                # Try waiting a bit more
                try:
                    await page.wait_for_selector('.authenticator-verify-list', timeout=5000)
                except TimeoutError:
                    # No 2FA required
                    return True
            
            logger.info("2FA detected, requesting push notification")
            await self._notify_user_intervention_async("2fa_required")
            
            # Try to click push notification
            push_result = await page.evaluate("""
                () => {
                    // Look for push notification elements
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (let element of elements) {
                        const text = element.textContent || '';
                        if (text.includes('push notification') || text.includes('Push') || text.includes('Send Push')) {
                            element.click();
                            return 'Push notification requested';
                        }
                    }
                    
                    // Try any authentication button
                    const authButtons = document.querySelectorAll('.authenticator-button a.button, button');
                    if (authButtons.length > 0) {
                        authButtons[0].click();
                        return 'Authentication method selected';
                    }
                    
                    return 'No authentication options found';
                }
            """)
            
            logger.info(f"2FA result: {push_result}")
            
            if 'requested' in push_result or 'selected' in push_result:
                await self._notify_user_intervention_async("2fa_push_sent")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"2FA handling failed: {e}")
            return False
    
    async def _wait_for_completion_async(self, page: Page, timeout: int = 60) -> bool:
        """Wait for authentication completion."""
        try:
            logger.info("Waiting for authentication completion...")
            
            for i in range(timeout):
                await asyncio.sleep(1)
                
                current_url = page.url
                
                # Check if moved away from SSO page
                if not self._is_sso_page(current_url) and 'my.openathens.net' in current_url:
                    # Check for success indicators
                    if '/account' in current_url or '/app' in current_url:
                        logger.success("Authentication completed - redirected to account page") 
                        return True
                
                # Progress updates
                if i > 0 and i % 10 == 0:
                    logger.info(f"Still waiting for completion... ({timeout-i}s remaining)")
            
            logger.error("Authentication completion timed out")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            return False
    
    def _is_sso_page(self, url: str) -> bool:
        """Check if current URL is an SSO page."""
        sso_domains = self.institution_config.get("sso_domains", [])
        return any(domain in url.lower() for domain in sso_domains)
    
    async def _notify_user_intervention_async(self, event_type: str, **kwargs) -> None:
        """Send email notification about authentication events."""
        try:
            to_email = self.institution_config.get("notification_email")
            from_email = os.environ.get("SCITEX_EMAIL_AGENT", "agent@scitex.ai")
            
            if not to_email:
                logger.debug("No notification email configured")
                return
            
            subject, message = self._generate_notification_content(event_type, **kwargs)
            
            await send_email_async(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                message=message
            )
            
            logger.success(f"Notification sent: {event_type}")
            
        except Exception as e:
            logger.debug(f"Failed to send notification: {e}")
    
    def _generate_notification_content(self, event_type: str, **kwargs) -> tuple[str, str]:
        """Generate notification content for different events."""
        institution = self.institution_config.get("institution_name", "Your Institution")
        
        if event_type == "authentication_started":
            subject = f"SciTeX Scholar: OpenAthens Authentication Started - {institution}"
            message = f"""
OpenAthens Authentication Process Started

The SciTeX Scholar system is attempting to authenticate with {institution} via OpenAthens.

Details:
- Institution: {institution}
- Process: OpenAthens institutional authentication
- Status: Authentication started

The system will guide you through the process and send updates as needed.

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
            
        elif event_type == "2fa_required":
            subject = f"SciTeX Scholar: 2FA Required - {institution}"
            message = f"""
Two-Factor Authentication Required

Your {institution} account requires 2FA verification to complete login.

Action Required:
- Check your registered mobile device
- Approve the push notification or enter verification code
- Authentication will continue automatically once verified

System: SciTeX Scholar Module
Institution: {institution}
Status: Awaiting 2FA approval

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
            
        elif event_type == "2fa_push_sent":
            subject = f"SciTeX Scholar: Push Notification Sent - {institution}"
            message = f"""
Push Notification Sent to Your Device

A push notification has been sent to your registered device for {institution} authentication.

Action Required:
- Check your mobile device
- Tap "Approve" on the authentication request
- Authentication will complete automatically once approved

System: SciTeX Scholar Module
Institution: {institution}
Status: Push notification sent

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
            
        elif event_type == "authentication_success":
            subject = f"SciTeX Scholar: Authentication Successful - {institution}"
            message = f"""
OpenAthens Authentication Completed Successfully

Your {institution} authentication via OpenAthens has been completed.

Details:
- Institution: {institution}
- Process: OpenAthens institutional authentication
- Status: Authentication successful
- Access: Institutional resources now available

You can now access institutional resources through SciTeX Scholar.

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
            
        else:
            # Generic notification
            subject = f"SciTeX Scholar: {event_type.replace('_', ' ').title()} - {institution}"
            message = f"""
OpenAthens Authentication Update

Event: {event_type.replace('_', ' ').title()}
Institution: {institution}
Details: {kwargs}

This is an automated notification from the SciTeX Scholar authentication system.
            """.strip()
        
        return subject, message


# Factory function for creating institution-specific configurations
def create_institution_config(institution: str) -> Dict[str, Any]:
    """Create configuration for specific institutions."""
    
    if institution.lower() == "unimelb" or institution.lower() == "university of melbourne":
        return {
            "institution_name": "University of Melbourne",
            "institution_email": os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL", ""),
            "sso_username": os.environ.get("UNIMELB_SSO_USERNAME", ""),
            "sso_password": os.environ.get("UNIMELB_SSO_PASSWORD", ""),
            "notification_email": os.environ.get("UNIMELB_EMAIL") or os.environ.get("SCITEX_EMAIL_YWATANABE", ""),
            "sso_domains": [
                "login.unimelb.edu.au",
                "okta.unimelb.edu.au",
                "authenticate.unimelb.edu.au", 
                "sso.unimelb.edu.au"
            ],
            "username_selector": "input[name='identifier']",
            "password_selector": "input[name='credentials.passcode']", 
            "next_button_selector": "input.button-primary[value='Next']",
            "verify_button_selector": "input[type='submit'][value='Verify']"
        }
    
    # Add more institutions here as needed
    # elif institution.lower() == "stanford":
    #     return {...}
    
    else:
        raise ValueError(f"Unsupported institution: {institution}")


# EOF