#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 15:23:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/library/_OpenAthensAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/library/_OpenAthensAuthenticator.py"
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
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

from scitex import logging

from ....errors import ScholarError
from ...config import ScholarConfig
from .._BrowserAuthenticator import BrowserAuthenticator
from ._BaseAuthenticator import BaseAuthenticator
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
        email: Optional[str] = None,
        timeout: int = 300,
        debug_mode: Optional[bool] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize OpenAthens authenticator.

        Args:
            email: Institutional email for identification (uses config if None)
            timeout: Authentication timeout in seconds
            debug_mode: Enable debug logging (uses config if None)
            config: ScholarConfig instance (creates new if None)
        """
        # Initialize config first
        if config is None:
            config = ScholarConfig()
        self.scholar_config = config  # Store ScholarConfig separately from BaseAuthenticator's config

        # Use config resolution for email and debug_mode
        self.email = self.scholar_config.resolve(
            "openathens_email", email, None, str
        )
        self.debug_mode = self.scholar_config.resolve(
            "debug_mode", debug_mode, False, bool
        )
        self.timeout = timeout  # Keep timeout as passed parameter

        BaseAuthenticator.__init__(
            self, config={"email": self.email, "debug_mode": self.debug_mode}
        )

        # Initialize helper components
        self.session_manager = SessionManager(default_expiry_hours=8)
        self.cache_manager = CacheManager(
            "openathens", self.scholar_config, self.email
        )

        # Create SSO automator for institution-specific automation
        sso_automator = self._create_sso_automator(
            openathens_email=self.email, config=self.scholar_config
        )

        self.browser_authenticator = BrowserAuthenticator(
            mode="interactive", timeout=timeout, sso_automator=sso_automator
        )

    def _create_sso_automator(self, openathens_email=None, config=None):
        """Create appropriate SSO automator based on email domain."""
        try:
            from ..sso_automation import SSOAutomator

            openathens_email = config.resolve(
                "openathens_email", openathens_email, default=None
            )
            return SSOAutomator(email=openathens_email, config=config)
        except Exception as e:
            logger.warn(f"SSO automators not available\n{str(e)}")
            return None

    async def _ensure_session_loaded_async(self) -> None:
        """Ensure session data is loaded from cache if available."""
        if not self.session_manager.has_valid_session_data():
            await self.cache_manager.load_session_async(self.session_manager)

    async def authenticate_async(self, force: bool = False, **kwargs) -> dict:
        """Authenticate with OpenAthens and return session data.

        Args:
            force: Force re-authentication even if session exists
            **kwargs: Additional parameters

        Returns:
            Dictionary containing session cookies
        """
        # Check if we have a valid session
        if not force and await self.is_authenticate_async():
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
                if not force and await self.is_authenticate_async():
                    logger.info(
                        f"Using session authenticate_async by another process{self.session_manager.format_expiry_info()}"
                    )
                    return self.session_manager.create_auth_response()

                # Perform browser-based authentication
                return await self._perform_browser_authentication_async()

        except Exception as e:
            # Check if another process authenticated while we were waiting
            await self._ensure_session_loaded_async()
            if await self.is_authenticated_async():
                logger.info("Another process authenticated successfully")
                return self.session_manager.create_auth_response()
            raise

    async def _perform_browser_authentication_async(self) -> dict:
        """Perform OpenAthens authentication with automatic SSO automation."""
        logger.info("Starting OpenAthens authentication")
        if self.email:
            logger.info(f"Account: {self.email}")

        # Note: Email notification will be sent later when 2FA is required
        # await self._notify_user_intervention_needed_async()

        async with async_playwright() as p:
            # Always start with OpenAthens page
            page = await self.browser_authenticator.navigate_to_login_async(
                self.MYATHENS_URL
            )

            # Display simple instructions
            self._display_login_instructions()

            # Wait for login completion (includes all automation)
            success = await self.browser_authenticator.wait_for_login_completion_async(
                page, self.SUCCESS_INDICATORS
            )

            if success:
                # Send success notification
                await self._notify_authentication_success_async()
                return await self._handle_successful_authentication_async(page)
            else:
                # Authentication failed
                await self._notify_authentication_failed_async(
                    "Authentication timed out"
                )
                await page.context.browser.close()
                raise OpenAthensError("Authentication failed or timed out")

    async def _handle_successful_authentication_async(self, page) -> dict:
        """Handle successful authentication by extracting and saving session."""
        # Extract session cookies
        simple_cookies, full_cookies = (
            await self.browser_authenticator.extract_session_cookies_async(
                page
            )
        )

        # Update session manager
        expiry = datetime.now() + timedelta(hours=8)
        self.session_manager.set_session_data(
            simple_cookies, full_cookies, expiry
        )

        # Save to cache
        await self.cache_manager.save_session_async(self.session_manager)

        logger.success(
            f"OpenAthens authentication successful{self.session_manager.format_expiry_info()}"
        )

        await page.context.browser.close()
        return self.session_manager.create_auth_response()

    async def is_authenticate_async(self, verify_live: bool = True) -> bool:
        """Check if we have a valid authenticate_async session.

        Args:
            verify_live: If True, performs a live check against OpenAthens

        Returns:
            True if authenticate_async, False otherwise
        """
        # Ensure session data is loaded
        await self._ensure_session_loaded_async()

        # Quick local checks
        if not self.session_manager.has_valid_session_data():
            logger.debug("No cookies or session expiry found")
            return False

        if self.session_manager.is_session_expired():
            logger.warn("OpenAthens session expired")
            return False

        expiry = self.session_manager.get_session_async_expiry()
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
        is_authenticate_async = (
            await self.browser_authenticator.verify_authentication_async(
                self.VERIFICATION_URL, cookies
            )
        )

        if is_authenticate_async:
            self.session_manager.mark_live_verification()

        return is_authenticate_async

    async def get_auth_headers_async(self) -> Dict[str, str]:
        """Get authentication headers (OpenAthens uses cookies, not headers)."""
        return {}

    async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
        """Get authentication cookies."""
        if not await self.is_authenticate_async():
            raise OpenAthensError("Not authenticate_async")
        return self.session_manager.get_full_cookies()

    async def logout_async(self, clear_cache=False) -> None:
        """Log out and clear authentication state."""
        self.session_manager.reset_session()

        # Clear cache if requested
        if clear_cache:
            self.cache_manager.clear_cache()

        logger.info("Logged out from OpenAthens")

    def _display_login_instructions(self) -> None:
        """Display simple login instructions to user."""
        logger.info("OpenAthens Authentication")
        logger.info("This will automatically:")
        logger.info("1. Fill in your institutional email")
        logger.info("2. Select your institution")
        logger.info("3. Handle institution SSO if needed")
        logger.info("4. Manual completion if automation fails")

        if self.email:
            logger.info(f"Account: {self.email}")
        logger.info(f"Timeout: {self.timeout} seconds")

    async def get_session_info_async(self) -> Dict[str, Any]:
        """Get information about current session."""
        if not await self.is_authenticate_async():
            return {"authenticate_async": False}

        session_info = self.session_manager.get_session_info_async()
        session_info.update(
            {
                "authenticate_async": True,
                "email": self.email,
            }
        )
        return session_info

    async def _notify_user_intervention_needed_async(self) -> None:
        """Send email notification that user intervention is needed for OpenAthens authentication."""
        try:
            from ..utils._email import send_email_async

            # Get notification email addresses from config
            to_email = self.scholar_config.resolve(
                "notification_email", None, None, str
            )
            from_email = self.scholar_config.resolve(
                "notification_from_email", None, "agent@scitex.ai", str
            )

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
3. The system will continue automatically once authenticate_async

If the browser didn't open or you missed it, you can manually navigate to:
{self.MYATHENS_URL}

This is an automated notification from the SciTeX Scholar authentication system.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()

            success = await send_email_async(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                message=message,
            )

            if success:
                logger.success(
                    f"User intervention notification sent to {to_email}"
                )
            else:
                logger.debug("Failed to send user intervention notification")

        except Exception as e:
            logger.debug(f"Failed to send user intervention notification: {e}")
            # Don't fail authentication if notification fails

    async def _notify_authentication_success_async(self) -> None:
        """Send email notification that OpenAthens authentication was successful."""
        try:
            from ..utils._email import send_email_async

            # Get notification email addresses from config
            to_email = self.scholar_config.resolve(
                "notification_email", None, None, str
            )
            from_email = self.scholar_config.resolve(
                "notification_from_email", None, "agent@scitex.ai", str
            )

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
                message=message,
            )

            logger.success(
                f"Authentication success notification sent to {to_email}"
            )

        except Exception as e:
            logger.debug(
                f"Failed to send authentication success notification: {e}"
            )

    async def _notify_authentication_failed_async(
        self, error_details: str
    ) -> None:
        """Send email notification that OpenAthens authentication failed."""
        try:
            from ..utils._email import send_email_async

            # Get notification email addresses from config
            to_email = self.scholar_config.resolve(
                "notification_email", None, None, str
            )
            from_email = self.scholar_config.resolve(
                "notification_from_email", None, "agent@scitex.ai", str
            )

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
                message=message,
            )

            logger.info(
                f"Authentication failure notification sent to {to_email}"
            )

        except Exception as e:
            logger.debug(
                f"Failed to send authentication failure notification: {e}"
            )


if __name__ == "__main__":
    import asyncio

    async def main():
        import argparse

        parser = argparse.ArgumentParser(
            description="OpenAthens authenticator with automatic SSO automation"
        )
        parser.add_argument(
            "--force", action="store_true", help="Force re-authentication"
        )
        parser.add_argument(
            "--manual",
            action="store_true",
            help="Skip automation and require manual intervention",
        )
        parser.add_argument(
            "--email", type=str, help="Override institutional email"
        )
        args = parser.parse_args()

        # Create authenticator
        auth = OpenAthensAuthenticator(email=args.email)

        # Check if already authenticated (unless forced)
        if not args.force:
            try:
                is_authenticated = await auth.is_authenticated_async()
                if is_authenticated:
                    logger.success(
                        "Already authenticated! Using cached session."
                    )
                    session_info = await auth.get_session_info_async()
                    logger.info("Current session details:")
                    for key, value in session_info.items():
                        if key != "cookies":  # Don't log sensitive data
                            logger.info(f"  {key}: {value}")
                    return 0
                else:
                    logger.info(
                        "No valid session found, proceeding with authentication..."
                    )
            except Exception as e:
                logger.debug(f"Session check failed: {e}")
                logger.info("Proceeding with authentication...")

        if args.manual:
            logger.info("Manual mode requested - automation will be skipped")
            # Temporarily disable automation by removing SSO automator
            auth.browser_authenticator.sso_automator = None

        try:
            # Always attempt full authentication flow with SSO automation
            result = await auth.authenticate_async(force=args.force)

            if result:
                logger.success("Authentication completed successfully!")
                logger.info("Session details:")
                session_info = await auth.get_session_info_async()
                for key, value in session_info.items():
                    if key != "cookies":  # Don't log sensitive cookie data
                        logger.info(f"  {key}: {value}")

                # Show available cookies count
                if "cookies" in result:
                    logger.info(f"  cookies_count: {len(result['cookies'])}")
            else:
                logger.error("Authentication failed")

        except Exception as e:
            logger.error(f"Authentication error: {e}")

            # Show helpful information for debugging
            logger.info("Troubleshooting tips:")
            logger.info("1. Check your institutional email configuration")
            logger.info("2. Verify your institution has OpenAthens access")
            logger.info("3. Try with --manual flag for manual authentication")
            logger.info("4. Try with --force flag to ignore cache")

            return 1

        return 0

    exit_code = asyncio.run(main())


# python -m scitex.scholar.auth._OpenAthensAuthenticator

# EOF
