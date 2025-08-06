#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 13:00:00"
# Author: Yusuke Watanabe
# File: _ShibbolethAuthenticator.py

"""
Shibboleth authentication for institutional access to academic papers.

This module provides authentication through Shibboleth single sign-on
to enable legal PDF downloads via institutional subscriptions.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin, parse_qs

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


class ShibbolethError(ScholarError):
    """Raised when Shibboleth authentication fails."""
    pass


class ShibbolethAuthenticator(BaseAuthenticator):
    """
    Handles Shibboleth authentication for institutional access.

    Shibboleth is a single sign-on (SSO) system that provides federated
    identity management and access control for academic resources.

    This authenticator:
    1. Authenticates via institutional Identity Provider (IdP)
    2. Handles SAML assertions and attribute exchange
    3. Maintains authenticate_async sessions
    4. Returns session cookies for use by download strategies
    """

    def __init__(
        self,
        institution: Optional[str] = None,
        idp_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        entity_id: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        timeout: int = 120,
        debug_mode: bool = False,
        **kwargs,
    ):
        """
        Initialize Shibboleth authenticator.

        Args:
            institution: Institution name (e.g., 'University of Example')
            idp_url: Identity Provider URL
            username: Username for authentication
            password: Password for authentication
            entity_id: Entity ID for the institution
            cache_dir: Directory for session cache
            timeout: Authentication timeout in seconds
            debug_mode: Enable debug logging
        """
        super().__init__(
            config={
                "institution": institution,
                "idp_url": idp_url,
                "username": username,
                "entity_id": entity_id,
                "debug_mode": debug_mode,
            }
        )

        self.institution = institution
        self.idp_url = idp_url
        self.username = username
        self.password = password
        self.entity_id = entity_id
        self.timeout = timeout
        self.debug_mode = debug_mode

        # Session cache directory
        self.cache_dir = (
            cache_dir or Path.home() / ".scitex" / "scholar" / "shibboleth_sessions"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Session file path
        self.session_file = self.cache_dir / f"session_{self._get_session_async_key()}.json"

        # Session management
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []
        self._session_expiry: Optional[datetime] = None
        self._saml_attributes: Dict[str, Any] = {}

        # Common Shibboleth endpoints and patterns
        self.wayf_urls = [
            "https://wayf.surfnet.nl",  # Dutch federation
            "https://discovery.eduserv.org.uk",  # UK federation
            "https://wayf.incommonfederation.org",  # InCommon (US)
            "https://ds.aai.switch.ch",  # Swiss federation
            "https://discovery.shibboleth.net",  # Generic discovery
        ]
        
        # Common IdP login patterns
        self.idp_patterns = {
            "username_field": [
                "input[name='j_username']",
                "input[name='username']",
                "input[name='user']",
                "input[id*='username']",
                "input[type='text']",
            ],
            "password_field": [
                "input[name='j_password']",
                "input[name='password']",
                "input[name='pass']",
                "input[id*='password']",
                "input[type='password']",
            ],
            "submit_button": [
                "button[type='submit']",
                "input[type='submit']",
                "button[name='_eventId_proceed']",
                "button:has-text('Login')",
                "button:has-text('Sign in')",
            ],
        }
        
        # Load existing session
        self._load_session()

    def _get_session_async_key(self) -> str:
        """Generate unique session key for this configuration."""
        key_parts = []
        if self.institution:
            key_parts.append(self.institution.replace(" ", "_"))
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
                        self._saml_attributes = data.get("saml_attributes", {})
                        logger.info("Loaded existing Shibboleth session")
                    else:
                        logger.info("Existing Shibboleth session expired")
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
                    "institution": self.institution,
                    "username": self.username,
                    "saml_attributes": self._saml_attributes,
                }
                with open(self.session_file, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info("Saved Shibboleth session")
            except Exception as e:
                logger.warning(f"Failed to save session: {e}")

    async def authenticate_async(self, force: bool = False, **kwargs) -> dict:
        """
        Authenticate with Shibboleth and return session data.

        The Shibboleth authentication flow typically involves:
        1. Accessing a protected resource
        2. Redirect to WAYF (Where Are You From) service
        3. Selecting institution
        4. Redirect to institution's IdP
        5. Authentication at IdP
        6. SAML assertion sent back to Service Provider
        7. Access granted to resource

        Args:
            force: Force re-authentication even if session exists
            **kwargs: Additional parameters (e.g., resource_url)

        Returns:
            Dictionary containing session cookies and SAML attributes

        Raises:
            ShibbolethError: If authentication fails
        """
        if async_playwright is None:
            raise ShibbolethError(
                "Playwright is required for Shibboleth authentication. "
                "Install with: pip install playwright && playwright install chromium"
            )

        # Check existing session
        if not force and await self.is_authenticate_async():
            logger.info("Using existing Shibboleth session")
            return {
                "cookies": self._cookies,
                "full_cookies": self._full_cookies,
                "saml_attributes": self._saml_attributes,
            }

        # Get resource URL to access (triggers Shibboleth flow)
        resource_url = kwargs.get("resource_url", "https://www.nature.com/siteindex")
        
        logger.info(f"Authenticating with Shibboleth for {self.institution or 'institution'}")

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
                
                # Step 1: Access protected resource
                await page.goto(resource_url, wait_until="networkidle")
                
                # Step 2: Look for institutional login option
                login_found = await self._find_institutional_login_async(page)
                
                if login_found:
                    # Click institutional login
                    await login_found.click()
                    await page.wait_for_load_state("networkidle")
                
                # Step 3: Handle WAYF/Discovery Service
                wayf_handled = await self._handle_wayf_selection_async(page)
                
                if not wayf_handled and not self.idp_url:
                    raise ShibbolethError("Could not find institution selection page")
                
                # Step 4: Handle IdP login
                if self.idp_url and page.url.startswith(self.idp_url):
                    await self._handle_idp_login_async(page)
                else:
                    # Try to detect and handle IdP automatically
                    await self._handle_idp_login_async(page)
                
                # Step 5: Wait for redirect back to resource
                try:
                    await page.wait_for_function(
                        f"""() => {{
                            return !window.location.href.includes('idp') && 
                                   !window.location.href.includes('wayf') &&
                                   !window.location.href.includes('discovery');
                        }}""",
                        timeout=30000
                    )
                except:
                    # Continue anyway - might still be authenticate_async
                    pass
                
                # Extract cookies and SAML attributes
                cookies = await context.cookies()
                
                # Try to extract SAML attributes from page or headers
                self._saml_attributes = await self._extract_saml_attributes_async(page)
                
                # Convert cookies
                self._cookies = {c["name"]: c["value"] for c in cookies}
                self._full_cookies = cookies
                
                # Set session expiry (typically 8-12 hours for Shibboleth)
                self._session_expiry = datetime.now() + timedelta(hours=8)
                
                # Save session
                self._save_session_async()
                
                logger.info("Shibboleth authentication successful")
                return {
                    "cookies": self._cookies,
                    "full_cookies": self._full_cookies,
                    "saml_attributes": self._saml_attributes,
                }
                
            except Exception as e:
                logger.error(f"Shibboleth authentication failed: {e}")
                raise ShibbolethError(f"Authentication failed: {str(e)}")
            finally:
                await browser.close()

    async def _find_institutional_login_async(self, page: Page) -> Optional[Any]:
        """Find and return institutional login link/button."""
        selectors = [
            "a:has-text('Institutional')",
            "a:has-text('Institution')",
            "a:has-text('Shibboleth')",
            "a:has-text('Federation')",
            "a:has-text('Access through your institution')",
            "button:has-text('Institutional')",
            "a[href*='shibboleth']",
            "a[href*='wayf']",
            "a[href*='idp']",
        ]
        
        for selector in selectors:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                logger.debug(f"Found institutional login: {selector}")
                return element
                
        return None

    async def _handle_wayf_selection_async(self, page: Page) -> bool:
        """Handle WAYF/Discovery Service institution selection."""
        # Check if we're on a WAYF page
        wayf_indicators = ["wayf", "discovery", "ds.", "where are you from"]
        current_url = page.url.lower()
        page_content = await page.content()
        
        is_wayf = any(ind in current_url for ind in wayf_indicators) or \
                  any(ind in page_content.lower() for ind in wayf_indicators)
        
        if not is_wayf:
            return False
            
        logger.info("Detected WAYF/Discovery Service page")
        
        # Try to find institution selector
        if self.institution:
            # Search for institution in dropdown/list
            selectors = [
                f"option:has-text('{self.institution}')",
                f"a:has-text('{self.institution}')",
                f"li:has-text('{self.institution}')",
            ]
            
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    # If it's an option, select it
                    if await element.evaluate("el => el.tagName") == "OPTION":
                        select = await element.evaluate_handle("el => el.parentElement")
                        await select.select_option(value=await element.get_attribute("value"))
                        # Find and click submit button
                        submit = await page.query_selector("button[type='submit'], input[type='submit']")
                        if submit:
                            await submit.click()
                    else:
                        # Direct click
                        await element.click()
                    
                    await page.wait_for_load_state("networkidle")
                    return True
                    
        # If automated selection fails, might need manual intervention
        if self.debug_mode:
            logger.info("Please select your institution manually")
            await asyncio.sleep(30)  # Give time for manual selection
            
        return False

    async def _handle_idp_login_async(self, page: Page) -> None:
        """Handle login at the Identity Provider."""
        logger.info("Handling IdP login page")
        
        # Get credentials
        if not self.username:
            self.username = input("Shibboleth username: ")
        if not self.password:
            import getpass
            self.password = getpass.getpass("Shibboleth password: ")
        
        # Try each username field pattern
        username_filled = False
        for selector in self.idp_patterns["username_field"]:
            field = await page.query_selector(selector)
            if field and await field.is_visible():
                await field.fill(self.username)
                username_filled = True
                break
                
        if not username_filled:
            raise ShibbolethError("Could not find username field")
            
        # Try each password field pattern
        password_filled = False
        for selector in self.idp_patterns["password_field"]:
            field = await page.query_selector(selector)
            if field and await field.is_visible():
                await field.fill(self.password)
                password_filled = True
                break
                
        if not password_filled:
            raise ShibbolethError("Could not find password field")
            
        # Try each submit button pattern
        for selector in self.idp_patterns["submit_button"]:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                await button.click()
                break
        
        # Wait for authentication to complete
        await page.wait_for_load_state("networkidle")

    async def _extract_saml_attributes_async(self, page: Page) -> Dict[str, Any]:
        """Try to extract SAML attributes from the page."""
        attributes = {}
        
        try:
            # Some SPs expose attributes in meta tags
            meta_tags = await page.query_selector_all("meta[name^='shib-']")
            for tag in meta_tags:
                name = await tag.get_attribute("name")
                content = await tag.get_attribute("content")
                if name and content:
                    attr_name = name.replace("shib-", "")
                    attributes[attr_name] = content
                    
            # Check for common attribute patterns in page
            if not attributes:
                # Try to find email/eppn
                email_pattern = r'[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}'
                page_text = await page.text_content()
                if page_text:
                    emails = re.findall(email_pattern, page_text)
                    if emails and self.username in emails[0]:
                        attributes["eppn"] = emails[0]
                        
        except Exception as e:
            logger.debug(f"Could not extract SAML attributes: {e}")
            
        return attributes

    async def is_authenticate_async(self, verify_live: bool = False) -> bool:
        """
        Check if we have a valid authenticate_async session.

        Args:
            verify_live: If True, performs a live check

        Returns:
            True if authenticate_async, False otherwise
        """
        # Check if we have session data
        if not self._cookies or not self._session_expiry:
            return False
            
        # Check if session is expired
        if datetime.now() > self._session_expiry:
            logger.info("Shibboleth session expired")
            return False
            
        # If requested, verify session is still valid
        if verify_live:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    
                    # Add cookies
                    await context.add_cookies(self._full_cookies)
                    
                    page = await context.new_page()
                    
                    # Try to access a protected resource
                    test_url = "https://www.nature.com/nature"
                    response = await page.goto(test_url, wait_until="networkidle")
                    
                    # Check if we're redirected to login
                    is_valid = not any(
                        ind in page.url.lower() 
                        for ind in ["login", "wayf", "idp", "shibboleth"]
                    )
                    
                    await browser.close()
                    
                    if not is_valid:
                        logger.info("Shibboleth session no longer valid")
                        self._cookies = {}
                        self._full_cookies = []
                        self._session_expiry = None
                        
                    return is_valid
                    
            except Exception as e:
                logger.warning(f"Failed to verify session: {e}")
                return False
                
        return True

    async def get_auth_headers_async(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Shibboleth typically uses cookies rather than headers,
        but some SPs may use additional headers.
        """
        headers = {}

        # Some Shibboleth deployments use these headers
        if self._saml_attributes:
            if "eppn" in self._saml_attributes:
                headers["X-Shibboleth-eppn"] = self._saml_attributes["eppn"]
            if "affiliation" in self._saml_attributes:
                headers["X-Shibboleth-affiliation"] = self._saml_attributes[
                    "affiliation"
                ]

        return headers

    async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
        """Get authentication cookies."""
        if not await self.is_authenticate_async():
            raise ShibbolethError("Not authenticate_async")
        return self._full_cookies

    async def logout_async(self) -> None:
        """
        Log out and clear authentication state.

        Note: Shibboleth logout_async is complex as it involves:
        - Local application logout_async
        - IdP logout_async
        - Optional Single Logout (SLO) to all SPs
        """
        self._cookies = {}
        self._full_cookies = []
        self._session_expiry = None
        self._saml_attributes = {}
        
        # Remove session file
        if self.session_file.exists():
            self.session_file.unlink()
            
        logger.info("Logged out from Shibboleth")

    async def get_session_info_async(self) -> Dict[str, Any]:
        """Get information about current session."""
        is_authenticate_async = await self.is_authenticate_async()
        
        return {
            "authenticate_async": is_authenticate_async,
            "provider": "Shibboleth",
            "institution": self.institution,
            "username": self.username,
            "idp_url": self.idp_url,
            "entity_id": self.entity_id,
            "saml_attributes": self._saml_attributes,
            "session_expiry": self._session_expiry.isoformat() if self._session_expiry else None,
            "cookies_count": len(self._cookies),
        }

    def detect_shibboleth_sp(self, url: str) -> Optional[Dict[str, str]]:
        """
        Detect if a URL is protected by Shibboleth.

        Args:
            url: URL to check

        Returns:
            Dictionary with SP information if detected, None otherwise
        """
        parsed = urlparse(url)
        domain = parsed.netloc

        # Common Shibboleth SP paths
        shibboleth_paths = [
            "/Shibboleth.sso",
            "/shibboleth",
            "/saml",
            "/idp",
            "/wayf",
            "/ds",  # Discovery Service
        ]

        # Check for common Shibboleth indicators
        indicators = {
            "jstor.org": {
                "sp_type": "jstor",
                "wayf": "https://www.jstor.org/wayf",
            },
            "projectmuse.org": {
                "sp_type": "muse",
                "wayf": "https://muse.jhu.edu/wayf",
            },
            "ebscohost.com": {
                "sp_type": "ebsco",
                "wayf": "https://search.ebscohost.com/wayf",
            },
            "ieee.org": {
                "sp_type": "ieee",
                "wayf": "https://ieeexplore.ieee.org/servlet/wayf",
            },
            "sciencedirect.com": {
                "sp_type": "elsevier",
                "wayf": "https://www.sciencedirect.com/wayf",
            },
        }

        for domain_pattern, info in indicators.items():
            if domain_pattern in domain:
                return info

        return None

    def get_wayf_url(self, sp_url: str) -> Optional[str]:
        """
        Get the WAYF (Where Are You From) URL for a Service Provider.

        Args:
            sp_url: Service Provider URL

        Returns:
            WAYF URL if known, None otherwise
        """
        sp_info = self.detect_shibboleth_sp(sp_url)
        if sp_info and "wayf" in sp_info:
            return sp_info["wayf"]

        # Return generic WAYF URL based on region
        # This would need to be configured based on user's location
        return self.wayf_urls[0]  # Default to first WAYF

    async def create_authenticate_async_browser(self) -> tuple[Browser, Any]:
        """
        Create a browser instance with Shibboleth authentication.

        Returns:
            Tuple of (browser, context) with authentication cookies set
        """
        if not await self.is_authenticate_async():
            await self.authenticate_async()

        if async_playwright is None:
            raise ShibbolethError("Playwright is required")

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