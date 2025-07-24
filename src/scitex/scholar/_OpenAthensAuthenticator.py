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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse

import aiohttp
from playwright.async_api import async_playwright, Page, Browser
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..errors import ScholarError, SciTeXWarning
import warnings

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
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []  # Full cookie objects
        self._session_expiry: Optional[datetime] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[Any] = None  # Browser context for tabs
        self._page: Optional[Page] = None
        
        # Encryption setup
        self._cipher = self._setup_encryption()
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Log cookie storage location on first use
        if not hasattr(OpenAthensAuthenticator, '_location_logged'):
            logger.info(f"OpenAthens session cookies stored in: {self.cache_dir}")
            OpenAthensAuthenticator._location_logged = True
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def initialize(self):
        """Initialize the authenticator."""
        # Load cached session if available
        await self._load_session_cache()
        
    async def close(self):
        """Clean up resources."""
        if self._session:
            await self._session.close()
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
            
    async def authenticate(self, force: bool = False) -> bool:
        """
        Authenticate with OpenAthens via manual browser login.
        
        Args:
            force: Force re-authentication even if session exists
            
        Returns:
            True if authentication successful
        
        Note:
            Opens MyAthens (https://my.openathens.net/) for manual login.
            The system will detect successful login and capture the session.
        """
        # Check if we have a valid session
        if not force and await self.is_authenticated():
            logger.info("Using existing OpenAthens session")
            return True
            
        logger.info("Starting manual OpenAthens authentication")
        if self.email:
            logger.info(f"Account: {self.email}")
        
        try:
            # Use Playwright with visible browser for manual login
            async with async_playwright() as p:
                # Always use non-headless mode for manual login
                self._browser = await p.chromium.launch(headless=False)
                self._page = await self._browser.new_page()
                
                # Navigate to unified MyAthens login page
                logger.info(f"Opening MyAthens: {self.myathens_url}")
                await self._page.goto(self.myathens_url, wait_until='networkidle')
                
                # Let user complete login manually
                success = await self._perform_login()
                
                if success:
                    # Extract cookies
                    cookies = await self._page.context.cookies()
                    self._cookies = {c['name']: c['value'] for c in cookies}
                    self._full_cookies = cookies  # Save full cookie objects for reuse
                    self._session_expiry = datetime.now() + timedelta(hours=8)
                    
                    # Save session
                    await self._save_session_cache()
                    
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
                
    async def _perform_login(self) -> bool:
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
            print("\nThe system will detect successful login automatically.")
            print("="*60 + "\n")
            
            # Wait a moment for page to load
            await asyncio.sleep(2)
            
            # Try to auto-fill email if available
            if self.email:
                try:
                    # Look for email input field by various selectors
                    email_selectors = [
                        'input[type="email"]',
                        'input[name="email"]',
                        'input[id*="email"]',
                        'input[placeholder*="email" i]',
                        'input[placeholder*="institution" i]',
                        '#organisationSearchString',  # MyAthens specific
                        'input.form-control'  # Common class for form inputs
                    ]
                    
                    email_filled = False
                    for selector in email_selectors:
                        try:
                            # Check if element exists
                            element = await self._page.query_selector(selector)
                            if element:
                                # Clear and fill the field
                                await element.click()
                                await element.fill('')  # Clear first
                                await element.type(self.email, delay=50)  # Type with human-like delay
                                logger.info(f"Auto-filled email field with selector: {selector}")
                                email_filled = True
                                
                                # Give a moment for any autocomplete to appear
                                await asyncio.sleep(1)
                                
                                # Try to trigger autocomplete/dropdown
                                await self._page.keyboard.press('ArrowDown')
                                await asyncio.sleep(0.5)
                                
                                break
                        except Exception as e:
                            logger.debug(f"Failed to fill with selector {selector}: {e}")
                            continue
                    
                    if email_filled:
                        print("✓ Email auto-filled. Please select your institution from the dropdown.")
                    else:
                        logger.debug("Could not auto-fill email field")
                        
                except Exception as e:
                    logger.debug(f"Error during email auto-fill: {e}")
                    # Continue anyway - user can fill manually
            
            # Monitor for successful login
            max_wait_time = 300  # 5 minutes
            check_interval = 2  # Check every 2 seconds
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                current_url = self._page.url
                
                # Check for various success indicators
                # First check URL-based indicators (safe during navigation)
                url_indicators = [
                    # MyAthens account/app pages mean logged in
                    'my.openathens.net/account' in current_url,
                    'my.openathens.net/app' in current_url,
                    'openathens.net/account' in current_url.lower(),
                    
                    # Redirected to institution's authenticated area
                    'ezproxy' in current_url.lower(),
                    '/secure/' in current_url,
                    'sso.unimelb.edu.au' in current_url,  # Institution SSO
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
                
                if any(success_indicators):
                    logger.info("Login successful - capturing session")
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
                
                # Show progress to user
                if elapsed_time % 10 == 0 and elapsed_time > 0:
                    print(f"Waiting for login... ({elapsed_time}s elapsed)")
                
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
            
            print("\n✗ Login timeout - please try again")
            return False
            
        except Exception as e:
            logger.error(f"Manual login process failed: {e}")
            return False
            
    async def is_authenticated(self) -> bool:
        """Check if we have a valid authenticated session."""
        if not self._cookies or not self._session_expiry:
            return False
            
        if datetime.now() > self._session_expiry:
            logger.info("OpenAthens session expired")
            return False
            
        return True
        
    async def download_with_auth(
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
        if not await self.is_authenticated():
            raise OpenAthensError("Not authenticated. Call authenticate() first.")
            
        try:
            # Use browser for download
            logger.info(f"Downloading via OpenAthens browser: {url}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)  # Can be headless for downloads
                context = await browser.new_context()
                
                # Add cookies to browser context
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
                
                page = await context.new_page()
                
                # Set up download handling
                download_path = output_path.parent
                download_path.mkdir(parents=True, exist_ok=True)
                
                # Navigate to URL
                try:
                    # For PDFs, don't wait for networkidle as they may be large
                    wait_until = 'domcontentloaded' if 'pdf' in url.lower() else 'networkidle'
                    response = await page.goto(url, wait_until=wait_until, timeout=60000)
                    
                    # Handle common popups
                    await self._handle_popups(page)
                    
                    # Wait a bit for any redirects
                    await asyncio.sleep(2)
                    
                    # Check if we have a PDF
                    content_type = await page.evaluate('() => document.contentType || ""')
                    current_url = page.url
                    
                    if 'pdf' in content_type.lower() or 'pdf' in current_url.lower():
                        # We're on a PDF page
                        # For PDFs displayed in browser, we need to trigger download
                        
                        # Start waiting for download
                        async with page.expect_download() as download_info:
                            # Try different methods to trigger download
                            
                            # Method 1: Ctrl+S
                            await page.keyboard.press('Control+s')
                            await asyncio.sleep(1)
                            
                            # Method 2: Look for download button
                            download_btn = await page.query_selector(
                                'a[download], button:has-text("Download"), a:has-text("Download PDF")'
                            )
                            if download_btn:
                                await download_btn.click()
                            
                            try:
                                download = await download_info.value
                                await download.save_as(output_path)
                                logger.info(f"Downloaded via browser: {output_path}")
                                await browser.close()
                                return output_path
                            except:
                                pass
                        
                        # If download didn't work, try direct fetch of the PDF URL
                        pdf_content = await page.evaluate('''
                            async () => {
                                const response = await fetch(window.location.href);
                                const buffer = await response.arrayBuffer();
                                return btoa(String.fromCharCode(...new Uint8Array(buffer)));
                            }
                        ''')
                        
                        if pdf_content:
                            import base64
                            with open(output_path, 'wb') as f:
                                f.write(base64.b64decode(pdf_content))
                            logger.info(f"Downloaded via fetch: {output_path}")
                            await browser.close()
                            return output_path
                    
                    else:
                        # Not a PDF page, look for download link
                        logger.debug(f"Not a PDF page: {content_type}")
                        download_link = await page.query_selector(
                            'a[href*=".pdf"], a:has-text("Download PDF"), button:has-text("Download")'
                        )
                        
                        if download_link:
                            async with page.expect_download() as download_info:
                                await download_link.click()
                                download = await download_info.value
                                await download.save_as(output_path)
                                logger.info(f"Downloaded via link: {output_path}")
                                await browser.close()
                                return output_path
                                
                except Exception as e:
                    logger.error(f"Browser download failed: {e}")
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"OpenAthens download failed: {e}")
            
        return None
            
    async def _handle_popups(self, page) -> None:
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
                    button = await page.wait_for_selector(selector, timeout=2000)
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
            
    async def _handle_publisher_download(
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
    
    async def download_batch(
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
        if not await self.is_authenticated():
            raise OpenAthensError("Not authenticated. Call authenticate() first.")
            
        results = {}
        
        try:
            logger.info(f"Starting batch download of {len(downloads)} PDFs")
            
            async with async_playwright() as p:
                # Use persistent browser context for session
                browser = await p.chromium.launch(headless=True)
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
                        task = self._download_in_tab(context, url, output_path)
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
    
    async def _download_in_tab(
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
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Handle popups
            await self._handle_popups(page)
            
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
        
    async def get_authenticated_url(self, url: str) -> str:
        """
        Get an OpenAthens-authenticated URL.
        
        Note: With manual authentication through MyAthens, we rely on
        cookies rather than URL rewriting.
        """
        if not await self.is_authenticated():
            raise OpenAthensError("Not authenticated")
            
        # With MyAthens manual login, we use the original URL with cookies
        return url
    
    def _setup_encryption(self) -> Fernet:
        """
        Setup encryption for cookie storage.
        
        Uses a key derived from the user's email and a machine-specific salt.
        This provides reasonable security while being reproducible on the same machine.
        """
        # Get or create a machine-specific salt
        salt_file = self.cache_dir.parent / ".scitex_salt"
        if salt_file.exists():
            with open(salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            salt_file.parent.mkdir(parents=True, exist_ok=True)
            with open(salt_file, 'wb') as f:
                f.write(salt)
            # Restrict permissions
            os.chmod(salt_file, 0o600)
        
        # Derive key from email (or default) and salt
        password = (self.email or "default").encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def _encrypt_data(self, data: dict) -> str:
        """Encrypt sensitive data."""
        json_data = json.dumps(data)
        encrypted = self._cipher.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> dict:
        """Decrypt sensitive data."""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._cipher.decrypt(decoded)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.warning(f"Failed to decrypt session data: {e}")
            return None
        
    async def _save_session_cache(self):
        """Save session cookies to cache."""
        # Use email domain or 'default' for cache file name
        cache_name = "default"
        if self.email and "@" in self.email:
            cache_name = self.email.split("@")[1].replace(".", "_")
        
        cache_file = self.cache_dir / f"openathens_{cache_name}_session.enc"
        
        cache_data = {
            'cookies': self._cookies,
            'full_cookies': self._full_cookies,  # Save full cookie objects
            'expiry': self._session_expiry.isoformat() if self._session_expiry else None,
            'email': self.email,
        }
        
        # Encrypt the data
        encrypted_data = self._encrypt_data(cache_data)
        
        # Save encrypted data
        with open(cache_file, 'w') as f:
            json.dump({
                'version': 1,
                'encrypted': encrypted_data,
                'email_hash': base64.urlsafe_b64encode(
                    (self.email or "default").encode()
                ).decode()[:16]  # For identification only
            }, f)
        
        # Restrict file permissions
        os.chmod(cache_file, 0o600)
        logger.debug(f"Session saved to: {cache_file}")
            
    async def _load_session_cache(self):
        """Load session cookies from cache."""
        # Use email domain or 'default' for cache file name
        cache_name = "default"
        if self.email and "@" in self.email:
            cache_name = self.email.split("@")[1].replace(".", "_")
        
        # Try encrypted file first, then legacy JSON
        cache_file_enc = self.cache_dir / f"openathens_{cache_name}_session.enc"
        cache_file_json = self.cache_dir / f"openathens_{cache_name}_session.json"
        
        cache_file = cache_file_enc if cache_file_enc.exists() else cache_file_json
        
        if not cache_file.exists():
            return
            
        try:
            with open(cache_file, 'r') as f:
                file_data = json.load(f)
            
            # Check if it's encrypted format
            if 'encrypted' in file_data:
                # Decrypt the data
                cache_data = self._decrypt_data(file_data['encrypted'])
                if not cache_data:
                    logger.warning("Failed to decrypt session cache")
                    return
            else:
                # Legacy unencrypted format
                cache_data = file_data
                logger.info("Migrating unencrypted session to encrypted format")
                
            # Load if email matches or no email specified
            if not self.email or cache_data.get('email') == self.email:
                self._cookies = cache_data.get('cookies', {})
                self._full_cookies = cache_data.get('full_cookies', [])
                expiry_str = cache_data.get('expiry')
                if expiry_str:
                    self._session_expiry = datetime.fromisoformat(expiry_str)
                
                # If loaded from legacy format, save as encrypted
                if 'encrypted' not in file_data and self._cookies:
                    await self._save_session_cache()
                    # Remove old unencrypted file
                    if cache_file_json.exists():
                        cache_file_json.unlink()
                        logger.info("Removed unencrypted session file")
                    
        except Exception as e:
            logger.debug(f"Failed to load session cache: {e}")