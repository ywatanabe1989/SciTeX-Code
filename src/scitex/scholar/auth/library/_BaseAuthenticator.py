#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 13:58:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/library/_BaseAuthenticator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/library/_BaseAuthenticator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Abstract base class for authenticators.

This module provides the base interface that all authenticators
(OpenAthens, Lean Library, etc.) must implement.
"""

"""Imports"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from scitex import logging

from ....errors import AuthenticationError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""


class BaseAuthenticator(ABC):
    """
    Abstract base class for authentication providers.

    All authentication providers (OpenAthens, EZProxy, Shibboleth, etc.)
    should inherit from this class and implement the required methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication provider.

        Args:
            config: Authenticator-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace("Authentication", "")

    @abstractmethod
    async def is_authenticate_async(self, verify_live: bool = False) -> bool:
        """
        Check if currently authenticate_async.

        Args:
            verify_live: If True, verify with actual request instead of just checking session

        Returns:
            True if authenticate_async, False otherwise
        """
        pass

    @abstractmethod
    async def authenticate_async(self, **kwargs) -> dict:
        """
        Perform authentication and return session data.

        Args:
            **kwargs: Authenticator-specific authentication parameters

        Returns:
            Dictionary containing session data (e.g., cookies, tokens)
        """
        pass

    @abstractmethod
    async def get_auth_headers_async(self) -> Dict[str, str]:
        """
        Get authentication headers for requests.

        Returns:
            Dictionary of headers to include in authenticate_async requests
        """
        pass

    @abstractmethod
    async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
        """
        Get authentication cookies for requests.

        Returns:
            List of cookie dictionaries
        """
        pass

    @abstractmethod
    async def logout_async(self) -> None:
        """Log out and clear authentication state."""
        pass

    @abstractmethod
    async def get_session_info_async(self) -> Dict[str, Any]:
        """
        Get information about current session.

        Returns:
            Dictionary containing session details (expiry, username, etc.)
        """
        pass

    def __str__(self) -> str:
        """String representation of provider."""
        return f"{self.name}Authenticator"

    def __repr__(self) -> str:
        """Detailed representation of provider."""
        return f"<{self.name}Authenticator(config={self.config})>"


if __name__ == "__main__":
    import asyncio

    async def main():
        """Example usage of BaseAuthenticator (through a concrete implementation)."""
        # This is an abstract class, so we'll demonstrate with OpenAthensAuthenticator
        from scitex.scholar.auth import OpenAthensAuthenticator

        # Initialize authenticator
        auth = OpenAthensAuthenticator(
            institution="University Example",
            username="your_username",
            password="your_password",
            browser_backend="local",  # or "zenrows"
        )

        try:
            # Check if already authenticate_async
            is_auth = await auth.is_authenticate_async()
            print(f"Initially authenticate_async: {is_auth}")

            if not is_auth:
                # Perform authentication
                print("Authenticating...")
                success = await auth.authenticate_async()
                print(f"Authentication successful: {success}")

            # Get authentication headers/cookies for requests
            headers = await auth.get_auth_headers_async()
            cookies = await auth.get_auth_cookies_async()
            print(f"Auth headers: {list(headers.keys())}")
            print(f"Auth cookies: {list(cookies.keys())}")

            # Get session info
            session_info = await auth.get_session_info_async()
            print(f"Session info: {session_info}")

        finally:
            # Always cleanup
            await auth.logout_async()
            print("Logged out successfully")

    # Run the example
    asyncio.run(main())

# EOF
