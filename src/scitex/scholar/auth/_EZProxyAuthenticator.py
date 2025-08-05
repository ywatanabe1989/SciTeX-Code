#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 12:30:00"
# Author: Yusuke Watanabe
# File: _EZProxyAuthenticator.py

"""
EZProxy authentication for institutional access to academic papers.

This module provides authentication through EZProxy systems
to enable legal PDF download_asyncs via institutional subscriptions.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse

from scitex import logging

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    async_playwright = None
    Page = None
    Browser = None

from ...errors import ScholarError
from ._BaseAuthenticator import BaseAuthenticator

logger = logging.getLogger(__name__)


class EZProxyError(ScholarError):
    """Raised when EZProxy authentication fails."""
    pass


class EZProxyAuthenticator(BaseAuthenticator):
    """
    Handles EZProxy authentication for institutional access.

    EZProxy is a web proxy server used by libraries to provide remote access
    to restricted digital resources.

    This authenticator:
    1. Authenticates via institutional EZProxy server
    2. Maintains authenticate_async sessions
    3. Returns session cookies for use by download_async strategies
    """

    def __init__(
        self,
        proxy_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        institution: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        timeout: int = 60,
        debug_mode: bool = False,
        **kwargs,
    ):
        """
        Initialize EZProxy authenticator.

        Args:
            proxy_url: EZProxy server URL (e.g., 'https://ezproxy.library.edu')
            username: Username for authentication
            password: Password for authentication
            institution: Institution name
            cache_dir: Directory for session cache
            timeout: Authentication timeout in seconds
            debug_mode: Enable debug logging
        """
        super().__init__(
            config={
                "proxy_url": proxy_url,
                "username": username,
                "institution": institution,
                "debug_mode": debug_mode,
            }
        )

        self.proxy_url = proxy_url
        self.username = username
        self.password = password
        self.institution = institution
        self.timeout = timeout
        self.debug_mode = debug_mode

        # Session cache directory
        self.cache_dir = (
            cache_dir or Path.home() / ".scitex" / "scholar" / "ezproxy_sessions"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Session file path
        self.session_file = self.cache_dir / f"session_{self._get_session_async_key()}.json"

        # Session management
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []
        self._session_expiry: Optional[datetime] = None
        
        # Load existing session
        self._load_session()

    def _get_session_async_key(self) -> str:
        """Generate unique session key for this configuration."""
        key_parts = []
        if self.proxy_url:
            key_parts.append(urlparse(self.proxy_url).netloc)
        if self.username:
            key_parts.append(self.username)
        return "_".join(key_parts) or "default"

    def _load_session(self) -> None:
        """Load existing session from cache."""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                    
                # Check if session is expired
                expiry_str = data.get("expiry")
                if expiry_str:
                    expiry = datetime.fromisoformat(expiry_str)
                    if expiry > datetime.now():
                        self._cookies = data.get("cookies", {})
                        self._full_cookies = data.get("full_cookies", [])
                        self._session_expiry = expiry
                        logger.info("Loaded existing EZProxy session")
                    else:
                        logger.info("Existing EZProxy session expired")
                        self.session_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load session: {e}")

    def _save_session_async(self) -> None:
        """Save current session to cache."""
        if self._cookies and self._session_expiry:
            try:
                data = {
                    "cookies": self._cookies,
                    "full_cookies": self._full_cookies,
                    "expiry": self._session_expiry.isoformat(),
                    "proxy_url": self.proxy_url,
                    "username": self.username,
                }
                with open(self.session_file, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info("Saved EZProxy session")
            except Exception as e:
                logger.warning(f"Failed to save session: {e}")

    async def authenticate_async(self, force: bool = False, **kwargs) -> dict:
        """
        Authenticate with EZProxy and return session data.

        Args:
            force: Force re-authentication even if session exists
            **kwargs: Additional parameters

        Returns:
            Dictionary containing session cookies

        Raises:
            EZProxyError: If authentication fails
        """
        if async_playwright is None:
            raise EZProxyError(
                "Playwright is required for EZProxy authentication. "
                "Install with: pip install playwright && playwright install chromium"
            )

        # Check existing session
        if not force and await self.is_authenticate_async():
            logger.info("Using existing EZProxy session")
            return {"cookies": self._cookies, "full_cookies": self._full_cookies}

        if not self.proxy_url:
            raise EZProxyError("EZProxy URL not configured")

        logger.info(f"Authenticating with EZProxy at {self.proxy_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=not self.debug_mode,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate to EZProxy login
                await page.goto(self.proxy_url, wait_until="networkidle")
                
                # Detect login form type
                login_performed = False
                
                # Try standard username/password fields
                if await page.query_selector("input[type='text'], input[name='user'], input[name='username']"):
                    username_field = await page.query_selector(
                        "input[type='text'], input[name='user'], input[name='username']"
                    )
                    password_field = await page.query_selector(
                        "input[type='password'], input[name='pass'], input[name='password']"
                    )
                    
                    if username_field and password_field:
                        # Get credentials if not provided
                        if not self.username:
                            self.username = input("EZProxy username: ")
                        if not self.password:
                            import getpass
                            self.password = getpass.getpass("EZProxy password: ")
                        
                        # Fill credentials
                        await username_field.fill(self.username)
                        await password_field.fill(self.password)
                        
                        # Find and click login button
                        login_button = await page.query_selector(
                            "input[type='submit'], button[type='submit'], button:has-text('Login'), button:has-text('Sign in')"
                        )
                        if login_button:
                            await login_button.click()
                            login_performed = True
                
                # If no standard form, check for SSO redirect
                if not login_performed:
                    # Look for institutional SSO links
                    sso_link = await page.query_selector(
                        "a:has-text('Institutional Login'), a:has-text('SSO'), a:has-text('Single Sign-On')"
                    )
                    if sso_link:
                        await sso_link.click()
                        await page.wait_for_load_state("networkidle")
                        
                        # Handle SSO authentication (institution-specific)
                        logger.info("Redirected to institutional SSO")
                        # This would need institution-specific handling
                
                # Wait for authentication to complete
                if login_performed:
                    try:
                        # Wait for either success or error
                        await page.wait_for_function(
                            """() => {
                                // Check for common success indicators
                                if (window.location.href.includes('menu') || 
                                    window.location.href.includes('connect') ||
                                    document.body.textContent.includes('successfully logged in')) {
                                    return true;
                                }
                                // Check for error messages
                                if (document.querySelector('.error, .alert-danger, [class*="error"]')) {
                                    throw new Error('Login failed');
                                }
                                return false;
                            }""",
                            timeout=30000
                        )
                    except Exception as e:
                        if "Login failed" in str(e):
                            raise EZProxyError("Invalid credentials")
                        # Continue if timeout - might still be authenticate_async
                
                # Extract cookies
                cookies = await context.cookies()
                
                # Convert cookies to format needed
                self._cookies = {c["name"]: c["value"] for c in cookies}
                self._full_cookies = cookies
                
                # Set session expiry (typically 8 hours for EZProxy)
                self._session_expiry = datetime.now() + timedelta(hours=8)
                
                # Save session
                self._save_session_async()
                
                logger.info("EZProxy authentication successful")
                return {"cookies": self._cookies, "full_cookies": self._full_cookies}
                
            except Exception as e:
                logger.error(f"EZProxy authentication failed: {e}")
                raise EZProxyError(f"Authentication failed: {str(e)}")
            finally:
                await browser.close()

    async def is_authenticate_async(self, verify_live: bool = False) -> bool:
        """
        Check if we have a valid authenticate_async session.

        Args:
            verify_live: If True, performs a live check against EZProxy

        Returns:
            True if authenticate_async, False otherwise
        """
        # Check if we have session data
        if not self._cookies or not self._session_expiry:
            return False
            
        # Check if session is expired
        if datetime.now() > self._session_expiry:
            logger.info("EZProxy session expired")
            return False
            
        # If requested, verify session is still valid
        if verify_live and self.proxy_url:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    
                    # Add cookies
                    await context.add_cookies(self._full_cookies)
                    
                    page = await context.new_page()
                    
                    # Try to access a proxied resource
                    test_url = f"{self.proxy_url}/menu"
                    response = await page.goto(test_url, wait_until="networkidle")
                    
                    # Check if we're still logged in
                    if response and response.status == 200:
                        # Check for login form - if present, session invalid
                        login_form = await page.query_selector(
                            "input[type='password'], form[action*='login']"
                        )
                        is_valid = login_form is None
                    else:
                        is_valid = False
                        
                    await browser.close()
                    
                    if not is_valid:
                        logger.info("EZProxy session no longer valid")
                        self._cookies = {}
                        self._full_cookies = []
                        self._session_expiry = None
                        
                    return is_valid
                    
            except Exception as e:
                logger.warning(f"Failed to verify session: {e}")
                return False
                
        return True

    async def get_auth_headers_async(self) -> Dict[str, str]:
        """Get authentication headers."""
        # EZProxy typically doesn't use headers for auth
        return {}

    async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
        """Get authentication cookies."""
        if not await self.is_authenticate_async():
            raise EZProxyError("Not authenticate_async")
        return self._full_cookies

    async def logout_async(self) -> None:
        """Log out and clear authentication state."""
        self._cookies = {}
        self._full_cookies = []
        self._session_expiry = None
        
        # Remove session file
        if self.session_file.exists():
            self.session_file.unlink()
            
        logger.info("Logged out from EZProxy")

    async def get_session_info_async(self) -> Dict[str, Any]:
        """Get information about current session."""
        is_authenticate_async = await self.is_authenticate_async()
        
        return {
            "authenticate_async": is_authenticate_async,
            "provider": "EZProxy",
            "username": self.username,
            "institution": self.institution,
            "proxy_url": self.proxy_url,
            "session_expiry": self._session_expiry.isoformat() if self._session_expiry else None,
            "cookies_count": len(self._cookies),
        }

    def transform_url(self, url: str) -> str:
        """
        Transform a URL to go through the EZProxy server.

        Args:
            url: Original URL

        Returns:
            Transformed URL that goes through EZProxy

        Example:
            Input: https://www.nature.com/articles/s41586-021-03819-2
            Output: https://ezproxy.library.edu/login?url=https://www.nature.com/articles/s41586-021-03819-2
        """
        if not self.proxy_url:
            return url

        # URL encode the target URL
        encoded_url = quote(url, safe='')
        
        # Different EZProxy configurations use different patterns
        # Try to detect the pattern from the proxy URL
        if "/login" in self.proxy_url:
            # Already has login path
            return f"{self.proxy_url}?url={encoded_url}"
        else:
            # Add login path
            base_url = self.proxy_url.rstrip('/')
            return f"{base_url}/login?url={encoded_url}"

    async def create_authenticate_async_browser(self) -> tuple[Browser, Any]:
        """
        Create a browser instance with EZProxy authentication.

        Returns:
            Tuple of (browser, context) with authentication cookies set
        """
        if not await self.is_authenticate_async():
            await self.authenticate_async()

        if async_playwright is None:
            raise EZProxyError("Playwright is required")

        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=not self.debug_mode,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Add authentication cookies
        await context.add_cookies(self._full_cookies)
        
        return browser, context

# EOF