#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 20:21:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_OpenAthensAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_OpenAthensAuthenticator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""OpenAthens authentication for institutional access to academic papers.

This module provides authentication through OpenAthens single sign-on
to enable legal PDF downloads via institutional subscriptions.
"""

import asyncio
import fcntl
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import Browser, Page, async_playwright

from scitex import logging

from ...errors import ScholarError
from ..browser.local._BrowserMixin import BrowserMixin
from ._BaseAuthenticator import BaseAuthenticator

logger = logging.getLogger(__name__)


class OpenAthensError(ScholarError):
    """Raised when OpenAthens authentication fails."""

    pass


class OpenAthensAuthenticator(BaseAuthenticator, BrowserMixin):
    """Handles OpenAthens authentication for institutional access.

    OpenAthens is a single sign-on system used by many universities
    and institutions to provide seamless access to academic resources.

    This authenticator:
    1. Logs in via the institution's identity provider
    2. Maintains authenticated sessions
    3. Returns session cookies for use by download strategies
    """

    def __init__(
        self,
        email: Optional[str] = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
        cache_dir: Optional[Path] = None,
        timeout: int = 300,
        debug_mode: bool = False,
        proxy_country: str = "us",
    ):
        """Initialize OpenAthens authenticator.

        Args:
            email: Institutional email for identification
            cache_dir: Directory for session cache
            timeout: Authentication timeout in seconds
            debug_mode: Enable debug logging
        """
        BaseAuthenticator.__init__(
            self, config={"email": email, "debug_mode": debug_mode}
        )
        # Always show browser for manual authentication
        BrowserMixin.__init__(
            self,
            headless=False,
        )

        self.email = email
        self.myathens_url = "https://my.openathens.net/?passiveLogin=false"
        self.timeout = timeout
        self.debug_mode = debug_mode

        # Cache management (integrated directly)
        import hashlib

        base_dir = cache_dir or Path.home() / ".scitex" / "scholar"
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()[:8]
        identifier = f"user_{email_hash}"

        self.cache_dir = base_dir / identifier
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.cache_dir, 0o700)

        self.cache_file = self.cache_dir / "openathens_session.json"
        self.lock_file = self.cache_dir / f"openathens_{identifier}_auth.lock"

        # Session management
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []
        self._session_expiry: Optional[datetime] = None
        self._last_live_verified_at = None
        self._live_verification_cache_seconds = 300  # 5 minutes

    async def authenticate(self, force: bool = False, **kwargs) -> dict:
        """Authenticate with OpenAthens and return session data.

        Args:
            force: Force re-authentication even if session exists
            **kwargs: Additional parameters

        Returns:
            Dictionary containing session cookies
        """
        # Check if we have a valid session
        if not force and await self.is_authenticated():
            logger.success(
                f"Using existing OpenAthens session{self._format_expiry_info()}"
            )
            return {
                "cookies": self._full_cookies,
                "simple_cookies": self._cookies,
                "expiry": self._session_expiry,
            }

        # Use file-based lock to prevent concurrent authentication
        lock_file = self.lock_file

        # Try to acquire lock with timeout
        max_wait = 300  # 5 minutes max wait
        start_time = time.time()
        lock_acquired = False
        lock_fd = None

        while time.time() - start_time < max_wait:
            try:
                lock_fd = open(lock_file, "w")
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                lock_acquired = True
                logger.info("Acquired authentication lock")
                break
            except (IOError, OSError):
                if lock_fd:
                    lock_fd.close()
                # Check if another process authenticated
                await self._load_session_cache()
                if await self.is_authenticated():
                    logger.info("Another process authenticated successfully")
                    return {
                        "cookies": self._full_cookies,
                        "simple_cookies": self._cookies,
                        "expiry": self._session_expiry,
                    }
                logger.debug("Waiting for authentication lock...")
                await asyncio.sleep(2)

        if not lock_acquired:
            raise OpenAthensError(
                "Could not acquire authentication lock after 5 minutes"
            )

        try:
            # Double-check session after acquiring lock
            await self._load_session_cache()
            if not force and await self.is_authenticated():
                logger.info(
                    f"Using session authenticated by another process{self._format_expiry_info()}"
                )
                return {
                    "cookies": self._full_cookies,
                    "simple_cookies": self._cookies,
                    "expiry": self._session_expiry,
                }

            logger.info("Starting manual OpenAthens authentication")
            if self.email:
                logger.info(f"Account: {self.email}")

            # Perform authentication by user interaction
            async with async_playwright() as p:
                # Use BrowserMixin to create context with cookie auto-acceptance
                browser, context = await self.create_browser_context(p)
                page = await context.new_page()

                # Navigate to MyAthens
                logger.info(f"Opening MyAthens: {self.myathens_url}")
                await page.goto(
                    self.myathens_url, wait_until="domcontentloaded"
                )

                # Check if cookie banner still exists (should be auto-accepted)
                if await self.cookie_acceptor.check_cookie_banner_exists(page):
                    print(
                        "\nCookie banner detected - please accept cookies manually before proceeding"
                    )

                # Show login instructions
                print("\n" + "=" * 60)
                print("OpenAthens Authentication Required")
                print("=" * 60)
                print(f"\nMyAthens login page is opening...")
                if self.email:
                    print(f"Account: {self.email}")
                print("\nPlease complete the login process:")
                print("1. Enter your institutional email")
                print("2. Click your institution when it appears")
                print("3. Complete login on your institution's page")
                print("4. You'll be redirected back to OpenAthens when done")
                print(f"5. Timeout is {self.timeout} seconds")
                print("6. Close the window after successful login")
                print("\nOpenAthens Environment Variables:")
                for key, value in os.environ.items():
                    if "SCITEX_SCHOLAR_OPENATHENS" in key:
                        print(f"  {key}: {value}")
                print("=" * 60 + "\n")

                # Wait for successful login
                success = await self._wait_for_login(page)

                if success:
                    # Extract cookies
                    cookies = await page.context.cookies()
                    self._cookies = {c["name"]: c["value"] for c in cookies}
                    self._full_cookies = cookies
                    self._session_expiry = datetime.now() + timedelta(hours=8)

                    # Save session
                    await self._save_session_cache()
                    logger.success(
                        f"OpenAthens authentication successful{self._format_expiry_info()}"
                    )

                    await browser.close()
                    return {
                        "cookies": self._full_cookies,
                        "simple_cookies": self._cookies,
                        "expiry": self._session_expiry,
                    }
                else:
                    await browser.close()
                    raise OpenAthensError("Authentication failed or timed out")

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

    def _recently_live_verified(self) -> bool:
        """Check if live verification was done recently."""
        if self._last_live_verified_at is None:
            return False

        elapsed = time.time() - self._last_live_verified_at
        return elapsed < self._live_verification_cache_seconds

    async def is_authenticated(self, verify_live: bool = True) -> bool:
        """Check if we have a valid authenticated session.

        Args:
            verify_live: If True, performs a live check against OpenAthens

        Returns:
            True if authenticated, False otherwise
        """
        # Load session from cache if not already loaded
        if not self._cookies and not self._session_expiry:
            await self._load_session_cache()

        # First do quick local checks
        if not self._cookies or not self._session_expiry:
            logger.debug("No cookies or session expiry found")
            return False

        if datetime.now() > self._session_expiry:
            logger.info("OpenAthens session expired")
            return False

        logger.debug(f"Session valid until {self._session_expiry}")

        # If live verification requested, do actual check
        if verify_live:
            if self._recently_live_verified():
                return True
            return await self._verify_authentication_live()

        return True

    async def _verify_authentication_live(self) -> bool:
        """Verify authentication by checking access to MyAthens account page."""
        if self._recently_live_verified():
            return True

        try:
            async with async_playwright() as p:
                # Use BrowserMixin with headless mode for verification
                self.headless = True
                browser, context = await self.create_browser_context(p)

                # Add cookies
                if self._full_cookies:
                    await context.add_cookies(self._full_cookies)

                page = await context.new_page()

                # Navigate to MyAthens account page
                response = await page.goto(
                    "https://my.openathens.net/account",
                    wait_until="domcontentloaded",
                    timeout=15000,
                )

                current_url = page.url

                # Check if we're on authenticated page
                if "my.openathens.net" in current_url and any(
                    path in current_url
                    for path in ["/account", "/app", "/library"]
                ):
                    await browser.close()
                    logger.success(
                        f"Verified live authentication at {current_url}"
                    )
                    return True

                # Check if redirected to login
                if "login" in current_url or "signin" in current_url:
                    await browser.close()
                    return False

                await browser.close()
                return False

        except Exception as e:
            logger.error(f"Authentication verification failed: {e}")
            return False
        finally:
            # Reset headless to False for actual authentication
            self.headless = False

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers (OpenAthens uses cookies, not headers)."""
        return {}

    async def get_auth_cookies(self) -> List[Dict[str, Any]]:
        """Get authentication cookies."""
        if not await self.is_authenticated():
            raise OpenAthensError("Not authenticated")
        return self._full_cookies

    async def logout(self, clear_cache=False) -> None:
        """Log out and clear authentication state."""
        self._cookies = {}
        self._full_cookies = []
        self._session_expiry = None

        # Clear cache
        if self.cache_file.exists() and clear_cache:
            self.cache_file.unlink()

        logger.info("Logged out from OpenAthens")

    async def get_session_info(self) -> Dict[str, Any]:
        """Get information about current session."""
        if not await self.is_authenticated():
            return {"authenticated": False}

        return {
            "authenticated": True,
            "email": self.email,
            "expiry": (
                self._session_expiry.isoformat()
                if self._session_expiry
                else None
            ),
            "cookie_count": len(self._cookies),
        }

    async def _wait_for_login(self, page: Page) -> bool:
        """Wait for successful login completion."""
        max_wait_time = self.timeout
        check_interval = 2
        elapsed_time = 0
        seen_sso_page = False

        while elapsed_time < max_wait_time:
            current_url = page.url

            # Track if we've navigated to SSO
            if "sso" in current_url.lower() or "login" in current_url.lower():
                seen_sso_page = True
                logger.debug(f"Detected SSO/login page: {current_url}")

            # Check for success indicators
            url_indicators = [
                "my.openathens.net/account" in current_url,
                "my.openathens.net/app" in current_url,
            ]

            # If URL indicates possible success, check for logout button
            has_logout_button = False
            if any(url_indicators):
                try:
                    has_logout_button = await page.evaluate(
                        """() => {
                        const links = document.querySelectorAll('a, button');
                        for (const link of links) {
                            const text = link.textContent.toLowerCase();
                            if (text.includes('logout') || text.includes('sign out')) {
                                return true;
                            }
                        }
                        return false;
                    }"""
                    )
                except:
                    pass

            if any(url_indicators) and (seen_sso_page or elapsed_time > 30):
                logger.info(f"Login successful detected at URL: {current_url}")
                logger.success("\n✓ Login detected! Capturing session...")
                return True

            # Show progress
            if elapsed_time % 10 == 0 and elapsed_time > 0:
                logger.info(f"Waiting for login... ({elapsed_time}s elapsed)")

            await asyncio.sleep(check_interval)
            elapsed_time += check_interval

        logger.fail("\n✗ Login timeout - please try again")
        return False

    async def _save_session_cache(self):
        """Save session cookies to cache."""
        cache_data = {
            "cookies": self._cookies,
            "full_cookies": self._full_cookies,
            "expiry": (
                self._session_expiry.isoformat()
                if self._session_expiry
                else None
            ),
            "email": self.email,
            "version": 2,
        }

        with open(self.cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)

        os.chmod(self.cache_file, 0o600)
        logger.success(f"Session saved to: {self.cache_file}")

    async def _load_session_cache(self):
        """Load session cookies from cache."""
        if not self.cache_file.exists():
            logger.debug(f"No session cache found at {self.cache_file}")
            return

        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            # Skip encrypted files
            if "encrypted" in cache_data:
                logger.warning(
                    "Found encrypted session file - please re-authenticate"
                )
                return

            # Load if email matches or no email specified
            if (
                not self.email
                or cache_data.get("email", "").lower() == self.email.lower()
            ):
                self._cookies = cache_data.get("cookies", {})
                self._full_cookies = cache_data.get("full_cookies", [])
                expiry_str = cache_data.get("expiry")
                if expiry_str:
                    self._session_expiry = datetime.fromisoformat(expiry_str)

                logger.info(
                    f"Loaded session from cache ({self.cache_file}): "
                    f"{len(self._cookies)} cookies{self._format_expiry_info()}"
                )
        except Exception as e:
            logger.error(f"Failed to load session cache: {e}")

    def _format_expiry_info(self) -> str:
        """Format expiry information for display."""
        if not self._session_expiry:
            return ""

        now = datetime.now()
        remaining = self._session_expiry - now
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)

        return f" (expires in {hours}h {minutes}m)"

    async def download_with_auth_async(self, url: str, output_path: Path) -> Optional[Path]:
        """Download a file using authenticated session.
        
        Args:
            url: URL to download from
            output_path: Path to save the downloaded file
            
        Returns:
            Path to the downloaded file if successful, None otherwise
        """
        from pathlib import Path
        import aiofiles
        import httpx
        
        try:
            # Ensure we're authenticated
            if not await self.is_authenticated():
                logger.warning("Not authenticated - attempting to authenticate")
                auth_result = await self.authenticate()
                if not auth_result:
                    logger.error("Failed to authenticate for download")
                    return None
            
            # Get auth cookies
            cookies = await self.get_auth_cookies()
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            
            # Get auth headers
            headers = await self.get_auth_headers()
            headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            logger.info(f"Downloading {url} with OpenAthens authentication")
            
            # Create output directory if needed
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with authentication
            async with httpx.AsyncClient(
                cookies=cookie_dict,
                headers=headers,
                follow_redirects=True,
                timeout=30.0
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Check if it's a PDF
                content_type = response.headers.get('content-type', '')
                if 'pdf' not in content_type.lower() and not url.endswith('.pdf'):
                    logger.warning(f"Response may not be a PDF. Content-Type: {content_type}")
                
                # Save the file
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(response.content)
                
                logger.success(f"Downloaded to {output_path}")
                return output_path
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during download: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Failed to download with OpenAthens auth: {e}")
            return None


async def main():
    import argparse

    auth = OpenAthensAuthenticator()
    result = await auth.authenticate(force=False)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

# python -m scitex.scholar.auth._OpenAthensAuthenticator

# EOF
