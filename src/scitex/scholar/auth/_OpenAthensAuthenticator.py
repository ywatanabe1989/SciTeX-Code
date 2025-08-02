#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:43:00 (ywatanabe)"
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

This refactored version uses smaller, focused helper classes:
- SessionManager: Handles session state and validation
- CacheManager: Handles session caching operations
- LockManager: Handles concurrent authentication prevention
- BrowserAuthenticator: Handles browser-based authentication
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

from scitex import logging

from ...errors import ScholarError
from ..config import ScholarConfig
from ._BaseAuthenticator import BaseAuthenticator
from ._BrowserAuthenticator import BrowserAuthenticator
from ._CacheManager import CacheManager
from ._LockManager import LockManager
from ._SessionManager import SessionManager

logger = logging.getLogger(__name__)


class OpenAthensError(ScholarError):
    """Raised when OpenAthens authentication fails."""

    pass


class OpenAthensAuthenticator(BaseAuthenticator):
    """Handles OpenAthens authentication for institutional access.

    OpenAthens is a single sign-on system used by many universities
    and institutions to provide seamless access to academic resources.

    This refactored authenticator:
    1. Uses SessionManager for session state management
    2. Uses CacheManager for session persistence
    3. Uses LockManager for concurrent authentication prevention
    4. Uses BrowserAuthenticator for browser-based operations
    5. Maintains backward compatibility with original interface
    """

    MYATHENS_URL = "https://my.openathens.net/?passiveLogin=false"
    VERIFICATION_URL = "https://my.openathens.net/account"
    SUCCESS_INDICATORS = [
        "my.openathens.net/account",
        "my.openathens.net/app",
    ]

    def __init__(
        self,
        email: Optional[str] = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
        timeout: int = 300,
        debug_mode: bool = False,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize OpenAthens authenticator.

        Args:
            email: Institutional email for identification
            timeout: Authentication timeout in seconds
            debug_mode: Enable debug logging
            config: ScholarConfig instance (creates new if None)
        """
        BaseAuthenticator.__init__(
            self, config={"email": email, "debug_mode": debug_mode}
        )

        self.email = email
        self.timeout = timeout
        self.debug_mode = debug_mode

        # Initialize config
        if config is None:
            config = ScholarConfig()
        self.config = config

        # Initialize helper components
        self.session_manager = SessionManager(default_expiry_hours=8)
        self.cache_manager = CacheManager("openathens", self.config, email)
        self.browser_authenticator = BrowserAuthenticator(
            mode="interactive", timeout=timeout
        )

    async def _ensure_session_loaded_async(self) -> None:
        """Ensure session data is loaded from cache if available."""
        if not self.session_manager.has_valid_session_data():
            await self.cache_manager.load_session_async(self.session_manager)

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
                f"Using existing OpenAthens session{self.session_manager.format_expiry_info()}"
            )
            return self.session_manager.create_auth_response()

        # Use lock to prevent concurrent authentication
        lock_manager = LockManager(self.cache_manager.get_lock_file())
        
        try:
            async with lock_manager:
                # Double-check session after acquiring lock
                await self._ensure_session_loaded_async()
                if not force and await self.is_authenticated():
                    logger.info(
                        f"Using session authenticated by another process{self.session_manager.format_expiry_info()}"
                    )
                    return self.session_manager.create_auth_response()

                # Perform browser-based authentication
                return await self._perform_browser_authentication_async()
                
        except Exception as e:
            # Check if another process authenticated while we were waiting
            await self._ensure_session_loaded_async()
            if await self.is_authenticated():
                logger.info("Another process authenticated successfully")
                return self.session_manager.create_auth_response()
            raise

    async def _perform_browser_authentication_async(self) -> dict:
        """Perform the actual browser-based authentication."""
        logger.info("Starting manual OpenAthens authentication")
        if self.email:
            logger.info(f"Account: {self.email}")

        # Send email notification that user intervention is needed
        await self._notify_user_intervention_needed_async()

        async with async_playwright() as p:
            # Navigate to login page
            page = await self.browser_authenticator.navigate_to_login_async(
                self.MYATHENS_URL
            )
            
            # Display instructions to user
            self.browser_authenticator.display_login_instructions(
                self.email, self.timeout
            )

            # Wait for login completion
            success = await self.browser_authenticator.wait_for_login_completion_async(
                page, self.SUCCESS_INDICATORS
            )

            if success:
                # Send success notification
                await self._notify_authentication_success_async()
                return await self._handle_successful_authentication_async(page)
            else:
                # Send failure notification
                await self._notify_authentication_failed_async("Authentication timed out")
                await page.context.browser.close()
                raise OpenAthensError("Authentication failed or timed out")

    async def _handle_successful_authentication_async(self, page) -> dict:
        """Handle successful authentication by extracting and saving session."""
        # Extract session cookies
        simple_cookies, full_cookies = await self.browser_authenticator.extract_session_cookies_async(page)
        
        # Update session manager
        expiry = datetime.now() + timedelta(hours=8)
        self.session_manager.set_session_data(simple_cookies, full_cookies, expiry)

        # Save to cache
        await self.cache_manager.save_session_async(self.session_manager)
        
        logger.success(
            f"OpenAthens authentication successful{self.session_manager.format_expiry_info()}"
        )

        await page.context.browser.close()
        return self.session_manager.create_auth_response()

    async def is_authenticated(self, verify_live: bool = True) -> bool:
        """Check if we have a valid authenticated session.

        Args:
            verify_live: If True, performs a live check against OpenAthens

        Returns:
            True if authenticated, False otherwise
        """
        # Ensure session data is loaded
        await self._ensure_session_loaded_async()

        # Quick local checks
        if not self.session_manager.has_valid_session_data():
            logger.debug("No cookies or session expiry found")
            return False

        if self.session_manager.is_session_expired():
            logger.info("OpenAthens session expired")
            return False

        expiry = self.session_manager.get_session_expiry()
        logger.debug(f"Session valid until {expiry}")

        # Perform live verification if requested
        if verify_live:
            return await self._verify_live_authentication_async()

        return True

    async def _verify_live_authentication_async(self) -> bool:
        """Verify authentication with live check if needed."""
        if not self.session_manager.needs_live_verification():
            return True
            
        cookies = self.session_manager.get_full_cookies()
        is_authenticated = await self.browser_authenticator.verify_authentication_async(
            self.VERIFICATION_URL, cookies
        )
        
        if is_authenticated:
            self.session_manager.mark_live_verification()
            
        return is_authenticated


    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers (OpenAthens uses cookies, not headers)."""
        return {}

    async def get_auth_cookies(self) -> List[Dict[str, Any]]:
        """Get authentication cookies."""
        if not await self.is_authenticated():
            raise OpenAthensError("Not authenticated")
        return self.session_manager.get_full_cookies()

    async def logout(self, clear_cache=False) -> None:
        """Log out and clear authentication state."""
        self.session_manager.reset_session()

        # Clear cache if requested
        if clear_cache:
            self.cache_manager.clear_cache()

        logger.info("Logged out from OpenAthens")

    async def get_session_info(self) -> Dict[str, Any]:
        """Get information about current session."""
        if not await self.is_authenticated():
            return {"authenticated": False}

        session_info = self.session_manager.get_session_info()
        session_info.update({
            "authenticated": True,
            "email": self.email,
        })
        return session_info

    async def _notify_user_intervention_needed_async(self) -> None:
        """Send email notification that user intervention is needed for OpenAthens authentication."""
        try:
            from ..utils._email import send_email_async
            
            # Get notification email address (prefer UniMelb, fallback to configured)
            to_email = os.environ.get("UNIMELB_EMAIL") or os.environ.get("SCITEX_EMAIL_YWATANABE")
            from_email = os.environ.get("SCITEX_EMAIL_AGENT", "agent@scitex.ai")
            
            if not to_email:
                logger.debug("No email address configured for notifications")
                return
            
            subject = "SciTeX Scholar: OpenAthens Authentication Required"
            message = f"""
OpenAthens Authentication Required

The SciTeX Scholar system requires your intervention to complete OpenAthens authentication.

Details:
- System: SciTeX Scholar Module  
- Service: OpenAthens Single Sign-On
- Account: {self.email or 'Not specified'}
- Timeout: {self.timeout} seconds
- Login URL: {self.MYATHENS_URL}

Action Required:
1. A browser window should have opened automatically
2. Complete the OpenAthens login process:
   • Enter your institutional email
   • Select your institution when it appears
   • Complete login on your institution's page
   • You'll be redirected back to OpenAthens when done
3. The system will continue automatically once authenticated

If the browser didn't open or you missed it, you can manually navigate to:
{self.MYATHENS_URL}

This is an automated notification from the SciTeX Scholar authentication system.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            success = await send_email_async(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                message=message
            )
            
            if success:
                logger.success(f"User intervention notification sent to {to_email}")
            else:
                logger.debug("Failed to send user intervention notification")
                
        except Exception as e:
            logger.debug(f"Failed to send user intervention notification: {e}")
            # Don't fail authentication if notification fails

    async def _notify_authentication_success_async(self) -> None:
        """Send email notification that OpenAthens authentication was successful."""
        try:
            from ..utils._email import send_email_async
            
            to_email = os.environ.get("UNIMELB_EMAIL") or os.environ.get("SCITEX_EMAIL_YWATANABE")
            from_email = os.environ.get("SCITEX_EMAIL_AGENT", "agent@scitex.ai")
            
            if not to_email:
                return
            
            expiry_info = self.session_manager.format_expiry_info()
            
            subject = "SciTeX Scholar: OpenAthens Authentication Successful"
            message = f"""
OpenAthens Authentication Complete

Your OpenAthens authentication has been completed successfully.

Details:
- System: SciTeX Scholar Module
- Service: OpenAthens Single Sign-On  
- Account: {self.email or 'Not specified'}
- Session expires: {expiry_info}
- Verification URL: {self.VERIFICATION_URL}

Status: Authenticated ✓

You can now access institutional resources through SciTeX Scholar.
The system will use this session for automatic PDF downloads and research access.

This is an automated notification from the SciTeX Scholar authentication system.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            await send_email_async(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                message=message
            )
            
            logger.success(f"Authentication success notification sent to {to_email}")
            
        except Exception as e:
            logger.debug(f"Failed to send authentication success notification: {e}")

    async def _notify_authentication_failed_async(self, error_details: str) -> None:
        """Send email notification that OpenAthens authentication failed."""
        try:
            from ..utils._email import send_email_async
            
            to_email = os.environ.get("UNIMELB_EMAIL") or os.environ.get("SCITEX_EMAIL_YWATANABE")
            from_email = os.environ.get("SCITEX_EMAIL_AGENT", "agent@scitex.ai")
            
            if not to_email:
                return
            
            subject = "SciTeX Scholar: OpenAthens Authentication Failed"
            message = f"""
OpenAthens Authentication Failed

The OpenAthens authentication process was not completed successfully.

Details:
- System: SciTeX Scholar Module
- Service: OpenAthens Single Sign-On
- Account: {self.email or 'Not specified'}
- Error: {error_details}
- Timeout: {self.timeout} seconds

Status: Authentication failed ✗

Next Steps:
1. Check your internet connection
2. Verify your institutional email and credentials
3. Try the authentication process again
4. Contact your institution's IT support if problems persist

Manual login URL: {self.MYATHENS_URL}

This is an automated notification from the SciTeX Scholar authentication system.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            await send_email_async(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                message=message
            )
            
            logger.info(f"Authentication failure notification sent to {to_email}")
            
        except Exception as e:
            logger.debug(f"Failed to send authentication failure notification: {e}")





async def main():
    import argparse

    auth = OpenAthensAuthenticator()
    result = await auth.authenticate(force=False)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

# python -m scitex.scholar.auth._OpenAthensAuthenticator

# EOF
