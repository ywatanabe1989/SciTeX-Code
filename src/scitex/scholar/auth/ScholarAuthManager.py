#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:28:44 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/auth/ScholarAuthManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/ScholarAuthManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Authentication manager for coordinating multiple authentication providers.

This module manages different authentication methods and provides a unified
interface for authentication operations.
"""


from typing import Any, Dict, List, Optional

from scitex import log
from scitex.errors import AuthenticationError
from scitex.scholar.config import ScholarConfig

from .library._BaseAuthenticator import BaseAuthenticator
from .library._EZProxyAuthenticator import EZProxyAuthenticator
from .library._OpenAthensAuthenticator import OpenAthensAuthenticator
from .library._ShibbolethAuthenticator import ShibbolethAuthenticator

logger = log.getLogger(__name__)


class ScholarAuthManager:
    """
    Manages multiple authentication providers.

    This class coordinates between different authentication methods
    (OpenAthens, Lean Library, etc.) and provides a unified interface.
    """

    def __init__(
        self,
        email_openathens: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_OPENATHENS_EMAIL"
        ),
        email_ezproxy: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_EZPROXY_EMAIL"
        ),
        email_shibboleth: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_SHIBBOLETH_EMAIL"
        ),
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize the authentication manager.

        Args:
            email_openathens: User's institutional email for OpenAthens authentication
            email_ezproxy: User's institutional email for EZProxy authentication
            email_shibboleth: User's institutional email for Shibboleth authentication
            config: ScholarConfig instance (creates new if None)
        """
        # Initialize config
        self.config = config or ScholarConfig()
        self.auth_session = None
        self.providers: Dict[str, BaseAuthenticator] = {}
        self.active_provider: Optional[str] = None

        if not any([email_openathens, email_ezproxy, email_shibboleth]):
            logger.warn(
                "No authentication provider configured. "
                "Set SCITEX_SCHOLAR_OPENATHENS_EMAIL or other provider email."
            )
            return

        for email, provider_str, provider_authenticator in [
            (email_openathens, "openathens", OpenAthensAuthenticator),
            (email_ezproxy, "ezproxy", EZProxyAuthenticator),
            (email_shibboleth, "shibboleth", ShibbolethAuthenticator),
        ]:
            if email:
                self._register_provider(
                    provider_str,
                    provider_authenticator(
                        email=email,
                        config=self.config,
                    ),
                )

    async def ensure_authenticate_async(
        self,
        provider_name: Optional[str] = None,
        verify_live: bool = True,
        **kwargs,
    ) -> bool:
        if await self.is_authenticate_async(verify_live=verify_live):
            return True

        if await self.authenticate_async(
            provider_name=provider_name, **kwargs
        ):
            return True

        raise AuthenticationError("Authentication not ensured")

    async def is_authenticate_async(self, verify_live: bool = True) -> bool:
        """Check if authenticate_async with any provider."""
        # Check active provider first
        if self.active_provider:
            provider = self.providers[self.active_provider]
            if await provider.is_authenticate_async(verify_live):
                return True

        # Check all other providers
        for name, provider in self.providers.items():
            if name != self.active_provider:
                if await provider.is_authenticate_async(verify_live):
                    self.active_provider = name
                    return True

        logger.debug("Not authenticate_async.")
        return False

    async def authenticate_async(
        self, provider_name: Optional[str] = None, **kwargs
    ) -> dict:
        """Authenticate with specified or active provider."""
        if provider_name:
            if provider_name not in self.providers:
                raise AuthenticationError(
                    f"Provider '{provider_name}' not found"
                )
            provider = self.providers[provider_name]
        elif self.active_provider:
            provider = self.providers[self.active_provider]
        else:
            raise AuthenticationError("No authentication provider configured")

        self.auth_session = await provider.authenticate_async(**kwargs)
        if self.auth_session and provider_name:
            self.active_provider = provider_name

        logger.success(f"Authentication succeeded by {provider_name}.")

        return self.auth_session

    async def get_auth_headers_async(self) -> Dict[str, str]:
        """Get authentication headers from active provider."""
        await self.ensure_authenticate_async()
        provider = self.get_active_provider()
        # if not provider:
        #     raise AuthenticationError("No active authentication provider")

        # if not await provider.is_authenticate_async():
        #     raise AuthenticationError("Not authenticate_async")

        return await provider.get_auth_headers_async()

    async def get_auth_options(self) -> dict:
        await self.ensure_authenticate_async()
        if self.auth_session and "cookies" in self.auth_session:
            return {"storage_state": {"cookies": self.auth_session["cookies"]}}
        return {}

    # async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
    #     """Get authentication cookies from active provider."""
    #     provider = self.get_active_provider()
    #     if not provider:
    #         raise AuthenticationError("No active authentication provider")

    #     if not await provider.is_authenticate_async():
    #         raise AuthenticationError("Not authenticate_async")

    #     authenticated_cookies = await provider.get_auth_cookies_async()

    #     return authenticated_cookies

    async def get_auth_cookies_async(
        self, essential_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get authentication cookies from active provider."""
        await self.ensure_authenticate_async()
        provider = self.get_active_provider()
        # if not provider:
        #     raise AuthenticationError("No active authentication provider")
        # if not await provider.is_authenticate_async():
        #     raise AuthenticationError("Not authenticate_async")

        authenticated_cookies = await provider.get_auth_cookies_async()

        if not essential_only:
            return authenticated_cookies

        # Filter by provider type
        if self.active_provider == "openathens":
            essential_names = [
                "oa-session",
                "oa-xsrf-token",
                "oatmpsid",
                "oalastorg",
            ]
        elif self.active_provider == "ezproxy":
            essential_names = ["ezproxy", "session_id"]  # adjust as needed
        elif self.active_provider == "shibboleth":
            essential_names = [
                "shib_session",
                "_shibsession_",
            ]  # adjust as needed
        else:
            return authenticated_cookies

        filtered_cookies = [
            cookie
            for cookie in authenticated_cookies
            if cookie["name"] in essential_names
        ]

        logger.debug(
            f"Filtered to {len(filtered_cookies)} essential cookies for {self.active_provider}"
        )
        return filtered_cookies

    def _register_provider(
        self, name: str, provider: BaseAuthenticator
    ) -> None:
        """Register an authentication provider with email context."""
        if not isinstance(provider, BaseAuthenticator):
            raise TypeError(
                f"Provider must inherit from BaseAuthenticator, got {type(provider)}"
            )
        self.providers[name] = provider
        if not self.active_provider:
            self.active_provider = name
        logger.debug(f"Registered authentication provider: {name}")

    def set_active_provider(self, name: str) -> None:
        """Set the active authentication provider."""
        if name not in self.providers:
            raise ValueError(
                f"Provider '{name}' not found. "
                f"Available providers: {list(self.providers.keys())}"
            )
        self.active_provider = name
        logger.debug(f"Set active authentication provider: {name}")

    def get_active_provider(self) -> Optional[BaseAuthenticator]:
        """Get the currently active provider."""
        if self.active_provider:
            return self.providers.get(self.active_provider)
        else:
            raise ValueError(
                f"Active provider not found. Please set active provider"
            )

    async def logout_async(self) -> None:
        """Log out from all providers."""
        for provider in self.providers.values():
            try:
                await provider.logout_async()
                logger.success(f"Logged out from {provider}")
            except Exception as e:
                logger.warn(f"Error logging out from {provider}: {e}")

        self.active_provider = None
        self.auth_session = None

    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self.providers.keys())


if __name__ == "__main__":
    import asyncio

    async def main():
        import os

        from scitex.scholar.auth import ScholarAuthManager

        auth_manager = ScholarAuthManager(
            email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
        )
        providers = auth_manager.list_providers()

        is_authenticate_async = await auth_manager.ensure_authenticate_async()

        headers = await auth_manager.get_auth_headers_async()
        cookies = await auth_manager.get_auth_cookies_async()

    asyncio.run(main())

# python -m scitex.scholar.auth.ScholarAuthManager

# EOF
