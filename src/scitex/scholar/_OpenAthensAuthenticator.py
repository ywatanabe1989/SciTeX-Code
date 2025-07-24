#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 12:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_OpenAthensAuthenticator.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_OpenAthensAuthenticator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
OpenAthens authentication for institutional access to academic papers.

This module provides authentication through OpenAthens single sign-on
to enable legal PDF downloads via institutional subscriptions.
"""

import asyncio
import logging
import re
import json
import base64
import fcntl
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse

import aiohttp
from playwright.async_api import async_playwright, Page, Browser

from ..errors import ScholarError, SciTeXWarning
import warnings
# BrowserAutomation removed - not needed

logger = logging.getLogger(__name__)


class OpenAthensError(ScholarError):
    """Raised when OpenAthens authentication fails."""
    pass


class OpenAthensAuthenticator:
    """
    Handles OpenAthens authentication for institutional access.
    
    OpenAthens is a single sign-on system used by many universities
    and institutions to provide seamless access to academic resources.
    
    This authenticator:
    1. Logs in via the institution's identity provider
    2. Maintains authenticated sessions
    3. Provides authenticated download capabilities
    4. Handles session refresh automatically
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        timeout: int = 300,  # 5 minutes for manual login
        debug_mode: bool = False,
    ):
        """
        Initialize OpenAthens authenticator.
        
        Args:
            email: Institutional email for identification (e.g., 'user@institution.edu')
            cache_dir: Directory for session cache
            timeout: Authentication timeout in seconds (default: 5 minutes)
        
        Note:
            Uses the unified MyAthens interface at https://my.openathens.net/
            Authentication is done manually in the browser.
        """
        self.email = email
        self.myathens_url = "https://my.openathens.net/?passiveLogin=false"
        self.cache_dir = Path(cache_dir or Path.home() / ".scitex" / "scholar" / "openathens_sessions")
        self.timeout = timeout
        self.debug_mode = debug_mode
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []  # Full cookie objects
        self._session_expiry: Optional[datetime] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[Any] = None  # Browser context for tabs
        self._page: Optional[Page] = None
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Log cookie storage location on first use
        if not hasattr(OpenAthensAuthenticator, '_location_logged'):
            logger.info(f"OpenAthens session cookies stored in: {self.cache_dir}")
            OpenAthensAuthenticator._location_logged = True
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_async()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_async()
        
    async def initialize_async(self):
        """Initialize the authenticator."""
        # Load cached session if available
        await self._load_session_cache_async()
        
    async def close_async(self):
        """Clean up resources."""
        if self._session:
            await self._session.close()
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
            
    async def authenticate_async(self, force: bool = False) -> bool:
        """
        Authenticate with OpenAthens via manual browser login.
        
        Args:
            force: Force re-authentication even if session exists
            
        Returns:
            True if authentication successful
        
        Note:
            Opens MyAthens (https://my.openathens.net/) for manual login.
            The system will detect successful login and capture the session.
            Uses file locking to prevent concurrent authentication attempts.
        """
        # Check if we have a valid session
        if not force and await self.is_authenticated_async():
            logger.info("Using existing OpenAthens session")
            return True
            
        # Use file-based lock to prevent concurrent authentication
        lock_file = self.cache_dir / "openathens_auth.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to acquire lock with timeout
        max_wait = 300  # 5 minutes max wait
        start_time = time.time()
        lock_acquired = False
        
        while time.time() - start_time < max_wait:
            try:
                # Try to open lock file with exclusive access
                lock_fd = None
                lock_fd = open(lock_file, 'w')
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                lock_acquired = True
                logger.info("Acquired authentication lock")
                break
            except (IOError, OSError):
                # Lock is held by another process
                if lock_fd:
                    lock_fd.close()
                    
                # Check if we now have a valid session (another process may have authenticated)
                await self._load_session_cache_async()
                if await self.is_authenticated_async():
                    logger.info("Another process authenticated successfully")
                    return True
                    
                # Wait before retrying
                logger.debug("Waiting for authentication lock...")
                await asyncio.sleep(2)
                
        if not lock_acquired:
            raise OpenAthensError("Could not acquire authentication lock after 5 minutes")
            
        try:
            # Double-check session after acquiring lock
            await self._load_session_cache_async()
            if not force and await self.is_authenticated_async():
                logger.info("Using session authenticated by another process")
                return True
                
            logger.info("Starting manual OpenAthens authentication")
            if self.email:
                logger.info(f"Account: {self.email}")
            
            try:
                # Use Playwright with visible browser for manual login
                async with async_playwright() as p:
                    # Always use non-headless mode for manual login
                    self._browser = await p.chromium.launch(headless=False)
                    context = await self._browser.new_context()
                    
                    # DISABLED: Browser automation setup
                    # The user requested no popup block checking during authentication
                    # await BrowserAutomationHelper.setup_context_automation(context)
                    
                    self._page = await context.new_page()
                    
                    # DISABLED: Page automation setup
                    # await BrowserAutomationHelper.setup_page_automation(self._page)
                    
                    # Navigate to unified MyAthens login page
                    logger.info(f"Opening MyAthens: {self.myathens_url}")
                    # Use domcontentloaded for better compatibility
                    await self._page.goto(self.myathens_url, wait_until='domcontentloaded')
                    
                    # DISABLED: Initial popup handling
                    # The user requested no popup block checking during authentication
                    # await BrowserAutomationHelper.wait_and_handle_interruptions(self._page)
                    
                    # Let user complete login manually
                    success = await self._perform_login_async()
                    
                    if success:
                        # Extract cookies
                        cookies = await self._page.context.cookies()
                        self._cookies = {c['name']: c['value'] for c in cookies}
                        self._full_cookies = cookies  # Save full cookie objects for reuse
                        self._session_expiry = datetime.now() + timedelta(hours=8)
                        
                        # Save session
                        await self._save_session_cache_async()
                        
                        logger.info("OpenAthens authentication successful")
                        return True
                    else:
                        raise OpenAthensError("Authentication failed or timed out")
                        
            except Exception as e:
                logger.error(f"OpenAthens authentication error: {e}")
                raise OpenAthensError(f"Authentication failed: {str(e)}")
            finally:
                if self._page:
                    await self._page.close()
                if self._browser:
                    await self._browser.close()
                    
        finally:
            # Release lock
            if lock_acquired and lock_fd:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                lock_fd.close()
                try:
                    lock_file.unlink()
                except:
                    pass
                logger.debug("Released authentication lock")
                
    async def _perform_login_async(self) -> bool:
        """
        Open browser for manual OpenAthens login and capture authentication cookies.
        
        This approach:
        1. Opens the OpenAthens login page
        2. Auto-fills email if available
        3. Waits for user to complete login manually
        4. Captures cookies after successful authentication
        """
        try:
            logger.info("Opening browser for manual OpenAthens login")
            
            # Show login instructions
            print("\n" + "="*60)
            print("OpenAthens Authentication Required")
            print("="*60)
            print(f"\nMyAthens login page is opening...")
            if self.email:
                print(f"Account: {self.email}")
            print("\nPlease complete the login process:")
            print("1. Enter your institutional email" + (" (auto-filled)" if self.email else ""))
            print("2. Click your institution when it appears") 
            print("3. Complete login on your institution's page")
            print("4. You'll be redirected back to OpenAthens when done")
            print("\n⚠️  Note: The browser will stay open during the entire login process")
            print("The system will detect successful login automatically.")
            print("="*60 + "\n")
            
            # Wait a moment for page to load
            await asyncio.sleep(2)
            
            # DISABLED AUTO-FILL - It might be causing the premature closing issue
            # Users can type their email manually
            print("\n⚠️  Auto-fill is disabled to prevent authentication issues.")
            print("Please type your email manually and select your institution.")
            
            # Comment out auto-fill code for now
            # if self.email:
            #     try:
            #         ... auto-fill code ...
            #     except Exception as e:
            #         logger.debug(f"Error during email auto-fill: {e}")
            
            # Monitor for successful login
            max_wait_time = 300  # 5 minutes
            check_interval = 2  # Check every 2 seconds
            elapsed_time = 0
            last_popup_check = 0
            
            # Track if we've seen an SSO page (to ensure we've started login)
            seen_sso_page = False
            initial_url = self._page.url
            
            while elapsed_time < max_wait_time:
                current_url = self._page.url
                
                # Track if we've navigated to SSO
                if 'sso.unimelb.edu.au' in current_url or 'login' in current_url.lower():
                    seen_sso_page = True
                    logger.debug(f"Detected SSO/login page: {current_url}")
                
                # DISABLED: Popup handling during authentication
                # The user requested no popup block checking during authentication
                # if elapsed_time - last_popup_check >= 5:  # Check every 5 seconds
                #     try:
                #         await BrowserAutomationHelper.handle_cookie_consent(self._page)
                #         await BrowserAutomationHelper.close_popups(self._page)
                #         last_popup_check = elapsed_time
                #     except Exception as e:
                #         logger.debug(f"Error handling popups during login: {e}")
                
                # Check for various success indicators
                # First check URL-based indicators (safe during navigation)
                url_indicators = [
                    # MyAthens account/app pages mean logged in
                    'my.openathens.net/account' in current_url,
                    'my.openathens.net/app' in current_url,
                    
                    # Note: We should NOT check for just 'my.openathens.net' as that includes the login page!
                    # SSO URLs like sso.unimelb.edu.au are login pages, NOT success!
                ]
                
                # If URL indicates possible success, check for logout button
                has_logout_button = False
                if any(url_indicators):
                    try:
                        # Use evaluate to avoid context destruction issues
                        has_logout_button = await self._page.evaluate('''
                            () => {
                                const links = document.querySelectorAll('a, button');
                                for (const link of links) {
                                    const text = link.textContent.toLowerCase();
                                    if (text.includes('logout') || text.includes('sign out') || text.includes('log out')) {
                                        return true;
                                    }
                                }
                                return false;
                            }
                        ''')
                    except:
                        # Ignore errors during navigation
                        pass
                
                success_indicators = url_indicators + [has_logout_button]
                
                # Only consider it success if we've gone through SSO first
                if any(success_indicators) and (seen_sso_page or elapsed_time > 30):
                    logger.info(f"Login successful detected at URL: {current_url}")
                    print("\n✓ Login detected! Capturing session...")
                    
                    # Log captured cookies for debugging
                    cookies = await self._page.context.cookies()
                    logger.debug(f"Captured {len(cookies)} cookies")
                    
                    # Show important cookies (without values for security)
                    important_cookies = []
                    for cookie in cookies:
                        if any(key in cookie['name'].lower() for key in ['auth', 'session', 'token', 'openathens']):
                            important_cookies.append(cookie['name'])
                    
                    if important_cookies:
                        logger.info(f"Important cookies captured: {', '.join(important_cookies)}")
                    
                    return True
                
                # Log current state for debugging (but not too often)
                if elapsed_time % 10 == 0:
                    logger.debug(f"Still waiting for login completion. Current URL: {current_url[:50]}...")
                
                # Show progress to user
                if elapsed_time % 10 == 0 and elapsed_time > 0:
                    print(f"Waiting for login... ({elapsed_time}s elapsed)")
                    print(f"  Current URL: {current_url[:60]}...")
                
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
            
            print("\n✗ Login timeout - please try again")
            return False
            
        except Exception as e:
            logger.error(f"Manual login process failed: {e}")
            return False
            
    async def is_authenticated_async(self, verify_live: bool = False) -> bool:
        """
        Check if we have a valid authenticated session.
        
        Args:
            verify_live: If True, performs a live check against OpenAthens servers.
                        This is more reliable but slower. If False, only checks
                        local cookie existence and expiry.
        
        Returns:
            True if authenticated, False otherwise
        """
        # First do quick local checks
        if not self._cookies or not self._session_expiry:
            logger.debug("No cookies or session expiry found")
            return False
            
        if datetime.now() > self._session_expiry:
            logger.info("OpenAthens session expired")
            return False
        
        logger.debug(f"Session valid until {self._session_expiry}, cookies: {len(self._cookies)} items")
        
        # If live verification requested, do actual check
        if verify_live:
            is_auth, details = await self.verify_authentication_async()
            logger.info(f"Live verification result: {details}")
            return is_auth
        
        # Otherwise trust the local state
        return True
    
    async def verify_authentication_async(self) -> tuple[bool, str]:
        """
        Verify OpenAthens authentication by checking access to MyAthens account page.
        
        This is more reliable than just checking cookies as it verifies the session
        is actually valid with the OpenAthens servers.
        
        Returns:
            (is_authenticated, details) - Authentication status and explanation
        """
        # First do basic checks
        if not self._cookies:
            return False, "No session cookies found"
            
        if self._session_expiry and datetime.now() > self._session_expiry:
            return False, "Session expired"
        
        # Now do live verification
        try:
            logger.debug("Performing live authentication verification")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)  # Use headless for quick check
                context = await browser.new_context()
                
                # Add cookies to context
                if self._full_cookies:
                    await context.add_cookies(self._full_cookies)
                else:
                    await context.add_cookies([
                        {
                            'name': name,
                            'value': value,
                            'domain': '.openathens.net',
                            'path': '/'
                        }
                        for name, value in self._cookies.items()
                    ])
                
                page = await context.new_page()
                
                # Navigate to MyAthens account page - requires authentication
                response = await page.goto(
                    "https://my.openathens.net/account",
                    wait_until='domcontentloaded',
                    timeout=15000
                )
                
                # Wait for navigation to settle
                try:
                    await page.wait_for_load_state('networkidle', timeout=5000)
                except:
                    pass  # Timeout is ok, page might have ongoing requests
                
                current_url = page.url
                
                # Check 1: Are we on any authenticated MyAthens page?
                if "my.openathens.net" in current_url and any(path in current_url for path in ["/account", "/app", "/library"]):
                    # Double-check for logout button as confirmation
                    has_logout = await page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('a, button');
                            for (const el of elements) {
                                const text = el.textContent.toLowerCase();
                                if (text.includes('sign out') || 
                                    text.includes('logout') ||
                                    text.includes('log out')) {
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    
                    await browser.close()
                    
                    if has_logout:
                        return True, f"Authenticated: Successfully accessed MyAthens page at {current_url}"
                    else:
                        return True, f"Authenticated: On MyAthens page at {current_url} (no logout button found)"
                
                # Check 2: Were we redirected to login? (not authenticated)
                if "login" in current_url or "signin" in current_url:
                    await browser.close()
                    return False, "Not authenticated: Redirected to login page"
                
                # Check 3: Look for organization search field (login page)
                try:
                    org_search = await page.query_selector('#organisationSearchString')
                    if org_search:
                        await browser.close()
                        return False, "Not authenticated: On organization search page"
                except:
                    pass
                
                await browser.close()
                
                # Unclear state
                return False, f"Authentication unclear - ended at: {current_url}"
                
        except Exception as e:
            logger.error(f"Authentication verification failed: {e}")
            return False, f"Verification error: {str(e)}"
        
    async def download_with_auth_async(
        self,
        url: str,
        output_path: Path,
        chunk_size: int = 8192
    ) -> Optional[Path]:
        """
        Download a file using OpenAthens authenticated browser session.
        
        Args:
            url: URL to download
            output_path: Where to save the file
            chunk_size: Not used (kept for compatibility)
            
        Returns:
            Path to downloaded file or None if failed
        """
        if not await self.is_authenticated_async():
            raise OpenAthensError("Not authenticated. Call authenticate_async() first.")
            
        try:
            # Use browser for download
            logger.info(f"Downloading via OpenAthens browser: {url}")
            logger.debug(f"Using {len(self._cookies)} cookies, full_cookies: {len(self._full_cookies) if self._full_cookies else 0}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=not self.debug_mode)  # Use visible browser in debug mode
                context = await browser.new_context()
                
                # For Nature and similar publishers, we need to go through their auth flow
                # instead of just adding OpenAthens cookies
                if 'nature.com' in url or 'springer.com' in url:
                    return await self._download_via_publisher_auth_async(browser, context, url, output_path)
                else:
                    # For other sites, continue with the standard approach
                    return await self._download_with_cookies_async(browser, context, url, output_path)
                    
        except Exception as e:
            logger.error(f"OpenAthens download failed: {e}")
            
        return None
            
    async def _handle_popups_async(self, page) -> None:
        """
        Handle common popups like cookie consent, notifications, etc.
        """
        try:
            # Common cookie consent selectors
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept all")',
                'button:has-text("Accept cookies")',
                'button:has-text("I agree")',
                'button:has-text("OK")',
                'button[id*="accept"]',
                'button[class*="accept"]',
                'a:has-text("Accept")',
            ]
            
            for selector in cookie_selectors:
                try:
                    button = await page.wait_for_selector(selector, timeout=5000)
                    if button:
                        await button.click()
                        logger.debug(f"Clicked popup button: {selector}")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
                    
            # Close any notification popups
            close_selectors = [
                'button[aria-label="Close"]',
                'button:has-text("Close")',
                'button:has-text("×")',
                'button.close',
                'a.close',
            ]
            
            for selector in close_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        logger.debug(f"Closed popup: {selector}")
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Popup handling error (non-critical): {e}")
            
    async def _handle_publisher_download_async(
        self,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """
        Handle publisher-specific download flows.
        
        Some publishers require additional navigation after OpenAthens auth.
        """
        # This would be extended with publisher-specific logic
        # For now, return None to fall back to other methods
        logger.debug(f"Publisher-specific download not implemented for {url}")
        return None
    
    async def download_batch_async(
        self,
        downloads: List[Tuple[str, Path]],
        max_concurrent: int = 3
    ) -> Dict[str, Optional[Path]]:
        """
        Download multiple PDFs concurrently using browser tabs.
        
        Args:
            downloads: List of (url, output_path) tuples
            max_concurrent: Maximum number of concurrent downloads
            
        Returns:
            Dict mapping URLs to downloaded paths (or None if failed)
        """
        if not await self.is_authenticated_async():
            raise OpenAthensError("Not authenticated. Call authenticate_async() first.")
            
        results = {}
        
        try:
            logger.info(f"Starting batch download of {len(downloads)} PDFs")
            
            async with async_playwright() as p:
                # Use persistent browser context for session
                browser = await p.chromium.launch(headless=not self.debug_mode)
                context = await browser.new_context()
                
                # Add cookies to context
                if self._full_cookies:
                    # Use full cookie objects if available
                    await context.add_cookies(self._full_cookies)
                else:
                    # Fallback to simple cookies
                    await context.add_cookies([
                        {
                            'name': name,
                            'value': value,
                            'domain': '.openathens.net',
                            'path': '/'
                        }
                        for name, value in self._cookies.items()
                    ])
                
                # Process downloads in batches
                for i in range(0, len(downloads), max_concurrent):
                    batch = downloads[i:i + max_concurrent]
                    
                    # Create tasks for concurrent downloads
                    tasks = []
                    for url, output_path in batch:
                        task = self._download_in_tab_async(context, url, output_path)
                        tasks.append(task)
                    
                    # Wait for batch to complete
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for (url, output_path), result in zip(batch, batch_results):
                        if isinstance(result, Exception):
                            logger.error(f"Download failed for {url}: {result}")
                            results[url] = None
                        else:
                            results[url] = result
                            
                await browser.close()
                
        except Exception as e:
            logger.error(f"Batch download error: {e}")
            
        # Log summary
        successful = sum(1 for path in results.values() if path is not None)
        logger.info(f"Batch download complete: {successful}/{len(downloads)} successful")
        
        return results
    
    async def _download_in_tab_async(
        self,
        context,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """
        Download a single PDF in a browser tab.
        
        Args:
            context: Browser context
            url: URL to download
            output_path: Where to save the file
            
        Returns:
            Path to downloaded file or None if failed
        """
        page = None
        try:
            # Create new tab
            page = await context.new_page()
            logger.debug(f"Opening tab for: {url}")
            
            # Navigate to URL
            # Use domcontentloaded for better compatibility
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Handle popups
            await self._handle_popups_async(page)
            
            # Wait for page to stabilize
            await asyncio.sleep(2)
            
            # Check content type
            content_type = await page.evaluate('() => document.contentType || ""')
            current_url = page.url
            
            if 'pdf' in content_type.lower() or 'pdf' in current_url.lower():
                # PDF page - try to download
                
                # Method 1: If it's a direct PDF URL, fetch the content
                if current_url.endswith('.pdf') or 'pdf' in content_type.lower():
                    try:
                        # Use page's network context to download
                        response = await page.evaluate(f'''
                            async () => {{
                                const response = await fetch("{current_url}");
                                const blob = await response.blob();
                                const buffer = await blob.arrayBuffer();
                                return btoa(String.fromCharCode(...new Uint8Array(buffer)));
                            }}
                        ''')
                        
                        if response:
                            import base64
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(base64.b64decode(response))
                            logger.info(f"Downloaded: {output_path.name}")
                            return output_path
                    except Exception as e:
                        logger.debug(f"Direct fetch failed: {e}")
                
                # Method 2: Look for download button
                download_btn = await page.query_selector(
                    'a[download], button:has-text("Download"), a:has-text("Download PDF")'
                )
                if download_btn:
                    # Set up download handler
                    async with page.expect_download() as download_info:
                        await download_btn.click()
                        try:
                            download = await asyncio.wait_for(download_info.value, timeout=30)
                            await download.save_as(output_path)
                            logger.info(f"Downloaded via button: {output_path.name}")
                            return output_path
                        except asyncio.TimeoutError:
                            logger.debug("Download timeout")
                            
            else:
                # Not a PDF page - look for PDF link
                pdf_link = await page.query_selector(
                    'a[href*=".pdf"], a:has-text("Download PDF"), a:has-text("PDF")'
                )
                
                if pdf_link:
                    # Click and download
                    async with page.expect_download() as download_info:
                        await pdf_link.click()
                        try:
                            download = await asyncio.wait_for(download_info.value, timeout=30)
                            await download.save_as(output_path)
                            logger.info(f"Downloaded via link: {output_path.name}")
                            return output_path
                        except asyncio.TimeoutError:
                            logger.debug("Download timeout")
                            
        except Exception as e:
            logger.error(f"Tab download error for {url}: {e}")
        finally:
            if page:
                await page.close()
                
        return None
        
    async def _download_via_publisher_auth_async(self, browser, context, url: str, output_path: Path) -> Optional[Path]:
        """Handle publisher-specific authentication flow (e.g., Nature, Springer)."""
        # Configure context to accept cookies automatically
        await context.add_init_script("""
            // Auto-accept cookies by overriding document.cookie setter
            Object.defineProperty(document, 'cookie', {
                set: function(value) {
                    this._cookie = value;
                    return true;
                },
                get: function() {
                    return this._cookie;
                }
            });
        """)
        
        page = await context.new_page()
        
        try:
            # Navigate to the article page
            logger.info(f"Navigating to publisher page: {url}")
            await page.goto(url, wait_until='domcontentloaded')
            
            # Handle cookie consent
            await self._handle_popups_async(page)
            await page.wait_for_timeout(2000)
            
            # Look for "Access through your institution" button
            # Try multiple selectors as different publishers use different markup
            access_selectors = [
                'text="Access through your institution"',
                'a:has-text("Access through your institution")',
                'button:has-text("Access through your institution")',
                '[data-track-action="institution-login"]',
                '.access-through-institution',
                'a[href*="institutional-access"]'
            ]
            
            access_button = None
            for selector in access_selectors:
                try:
                    access_button = await page.wait_for_selector(selector, timeout=5000)
                    if access_button:
                        logger.info(f"Found institution access button with selector: {selector}")
                        break
                except:
                    continue
            
            if access_button:
                # Ensure button is visible and clickable
                await access_button.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                
                # Try to click with retry
                for attempt in range(3):
                    try:
                        await access_button.click()
                        logger.info("Clicked institution access button")
                        break
                    except Exception as e:
                        if attempt < 2:
                            logger.warning(f"Click attempt {attempt + 1} failed, retrying...")
                            await page.wait_for_timeout(2000)
                        else:
                            raise e
                
                await page.wait_for_timeout(3000)
                
                # Now we should be on the institution selection page
                # Type the institution name
                institution_input = await page.query_selector('input[type="text"]')
                if institution_input:
                    await institution_input.fill("University of Melbourne")
                    await page.wait_for_timeout(2000)
                    
                    # Look for submit button or institution link
                    submit_btn = await page.query_selector('button[type="submit"]')
                    if submit_btn:
                        await submit_btn.click()
                    
                    # Wait for navigation to SSO/OpenAthens
                    await page.wait_for_timeout(5000)
                    
                    # Check if we're on SSO page and need to login
                    current_url = page.url
                    if 'sso.unimelb.edu.au' in current_url or 'openathens' in current_url:
                        logger.info("On SSO/OpenAthens page, adding cookies")
                        # Add OpenAthens cookies
                        if self._full_cookies:
                            await context.add_cookies(self._full_cookies)
                        
                        # Refresh to use cookies
                        await page.reload()
                        await page.wait_for_timeout(5000)
            
            # Now check if we have access to the PDF
            return await self._extract_pdf_from_page_async(page, output_path)
            
        except Exception as e:
            logger.error(f"Publisher auth flow failed: {e}")
            return None
        finally:
            await page.close()
    
    async def _download_with_cookies_async(self, browser, context, url: str, output_path: Path) -> Optional[Path]:
        """Standard download with OpenAthens cookies."""
        # Add cookies to context
        if self._full_cookies:
            await context.add_cookies(self._full_cookies)
        else:
            await context.add_cookies([
                {
                    'name': name,
                    'value': value,
                    'domain': '.openathens.net',
                    'path': '/'
                }
                for name, value in self._cookies.items()
            ])
        
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self._handle_popups_async(page)
            await page.wait_for_timeout(2000)
            
            return await self._extract_pdf_from_page_async(page, output_path)
            
        except Exception as e:
            logger.error(f"Download with cookies failed: {e}")
            return None
        finally:
            await page.close()
            await browser.close()
    
    async def _extract_pdf_from_page_async(self, page, output_path: Path) -> Optional[Path]:
        """Extract PDF from the current page."""
        # Check if current page is a PDF
        content_type = await page.evaluate('() => document.contentType || ""')
        current_url = page.url
        
        if 'pdf' in content_type.lower() or 'pdf' in current_url.lower():
            logger.info("Page appears to be a PDF")
            # Try to download the PDF content
            try:
                pdf_content = await page.evaluate('''
                    async () => {
                        const response = await fetch(window.location.href);
                        const buffer = await response.arrayBuffer();
                        return btoa(String.fromCharCode(...new Uint8Array(buffer)));
                    }
                ''')
                
                if pdf_content:
                    import base64
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(pdf_content))
                    logger.info(f"Downloaded PDF: {output_path}")
                    return output_path
            except Exception as e:
                logger.error(f"Failed to extract PDF content: {e}")
        
        # Look for PDF download links
        pdf_link = await page.query_selector('a[href*=".pdf"], a:has-text("Download PDF")')
        if pdf_link:
            pdf_url = await pdf_link.get_attribute('href')
            if pdf_url:
                logger.info(f"Found PDF link: {pdf_url}")
                # Make it absolute if needed
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin(current_url, pdf_url)
                
                # Download the PDF
                response = await page.context.request.get(pdf_url)
                if response.ok:
                    pdf_content = await response.body()
                    if pdf_content and pdf_content.startswith(b'%PDF'):
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(pdf_content)
                        logger.info(f"Downloaded PDF from link: {output_path}")
                        return output_path
        
        return None
    
    async def get_authenticated_url_async(self, url: str) -> str:
        """
        Get an OpenAthens-authenticated URL.
        
        Note: With manual authentication through MyAthens, we rely on
        cookies rather than URL rewriting.
        """
        if not await self.is_authenticated_async():
            raise OpenAthensError("Not authenticated")
            
        # With MyAthens manual login, we use the original URL with cookies
        return url
    
        
    async def _save_session_cache_async(self):
        """Save session cookies to cache."""
        # Use email domain or 'default' for cache file name
        cache_name = "default"
        if self.email and "@" in self.email:
            cache_name = self.email.split("@")[1].replace(".", "_")
        
        # Use plain JSON file for debugging
        cache_file = self.cache_dir / f"openathens_{cache_name}_session.json"
        
        cache_data = {
            'cookies': self._cookies,
            'full_cookies': self._full_cookies,  # Save full cookie objects
            'expiry': self._session_expiry.isoformat() if self._session_expiry else None,
            'email': self.email,
            'version': 2  # Version 2 = unencrypted for debugging
        }
        
        # Save as plain JSON
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        # Still restrict file permissions for some security
        os.chmod(cache_file, 0o600)
        logger.info(f"Session saved to (unencrypted): {cache_file}")
            
    async def _load_session_cache_async(self):
        """Load session cookies from cache."""
        # Use email domain or 'default' for cache file name
        cache_name = "default"
        if self.email and "@" in self.email:
            cache_name = self.email.split("@")[1].replace(".", "_")
        
        # Try JSON file first, then encrypted file (for backward compatibility)
        cache_file_json = self.cache_dir / f"openathens_{cache_name}_session.json"
        cache_file_enc = self.cache_dir / f"openathens_{cache_name}_session.enc"
        
        cache_file = cache_file_json if cache_file_json.exists() else cache_file_enc
        
        if not cache_file.exists():
            logger.debug(f"No session cache found at {cache_file_json}")
            return
            
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # For encrypted files, skip them for now
            if 'encrypted' in cache_data:
                logger.warning("Found encrypted session file - please re-authenticate to create unencrypted session")
                return
                
            # Load if email matches or no email specified (case-insensitive)
            if not self.email or cache_data.get('email', '').lower() == self.email.lower():
                self._cookies = cache_data.get('cookies', {})
                self._full_cookies = cache_data.get('full_cookies', [])
                expiry_str = cache_data.get('expiry')
                if expiry_str:
                    self._session_expiry = datetime.fromisoformat(expiry_str)
                
                logger.info(f"Loaded session from cache: {len(self._cookies)} cookies, expires: {self._session_expiry}")
                
                # Log cookie names for debugging
                if self._cookies:
                    cookie_names = list(self._cookies.keys())[:5]  # Show first 5
                    logger.debug(f"Cookie names: {cookie_names}...")
                if self._full_cookies:
                    logger.debug(f"Full cookies: {len(self._full_cookies)} objects")
                    
        except Exception as e:
            logger.error(f"Failed to load session cache: {e}")