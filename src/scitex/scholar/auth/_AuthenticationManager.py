#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 12:09:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_AuthenticationManager.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_AuthenticationManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Authentication manager for coordinating multiple authentication providers.

This module manages different authentication methods and provides a unified
interface for authentication operations.
"""

"""Imports"""
import logging
from typing import Any, Dict, List, Optional

from ...errors import AuthenticationError
from ._BaseAuthenticator import BaseAuthenticator

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""


class AuthenticationManager:
    """
    Manages multiple authentication providers.

    This class coordinates between different authentication methods
    (OpenAthens, Lean Library, etc.) and provides a unified interface.
    """

    def __init__(self, email: Optional[str] = None):
        """Initialize the authentication manager.

        Args:
            email: User's institutional email for authentication
        """
        self.email = email
        self.providers: Dict[str, BaseAuthenticator] = {}
        self.active_provider: Optional[str] = None

    def register_provider(
        self, name: str, provider: BaseAuthenticator
    ) -> None:
        """Register an authentication provider with email context."""
        if not isinstance(provider, BaseAuthenticator):
            raise TypeError(
                f"Provider must inherit from BaseAuthenticator, got {type(provider)}"
            )

        # Pass email to provider if it supports it
        if hasattr(provider, "email") and self.email:
            provider.email = self.email

        self.providers[name] = provider
        logger.info(f"Registered authentication provider: {name}")

    def set_active_provider(self, name: str) -> None:
        """
        Set the active authentication provider.

        Args:
            name: Name of the provider to activate

        Raises:
            ValueError: If provider not found
        """
        if name not in self.providers:
            raise ValueError(
                f"Provider '{name}' not found. "
                f"Available providers: {list(self.providers.keys())}"
            )
        self.active_provider = name
        logger.info(f"Set active authentication provider: {name}")

    def get_active_provider(self) -> Optional[BaseAuthenticator]:
        """
        Get the currently active provider.

        Returns:
            Active authentication provider or None
        """
        if self.active_provider:
            return self.providers.get(self.active_provider)
        return None

    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """
        Check if authenticated with any provider.

        Args:
            verify_live: If True, verify with actual request

        Returns:
            True if authenticated with any provider
        """
        # Check active provider first
        if self.active_provider:
            provider = self.providers[self.active_provider]
            if await provider.is_authenticated(verify_live):
                return True

        # Check all other providers
        for name, provider in self.providers.items():
            if name != self.active_provider:
                if await provider.is_authenticated(verify_live):
                    self.active_provider = name
                    return True

        return False

    # async def authenticate(
    #     self,
    #     provider_name: Optional[str] = None,
    #     **kwargs
    # ) -> bool:
    #     """
    #     Authenticate with specified or active provider.

    #     Args:
    #         provider_name: Name of provider to use (uses active if None)
    #         **kwargs: Authentication parameters

    #     Returns:
    #         True if authentication successful

    #     Raises:
    #         AuthenticationError: If no provider available or auth fails
    #     """
    #     if provider_name:
    #         if provider_name not in self.providers:
    #             raise AuthenticationError(
    #                 f"Provider '{provider_name}' not found"
    #             )
    #         provider = self.providers[provider_name]
    #     elif self.active_provider:
    #         provider = self.providers[self.active_provider]
    #     else:
    #         raise AuthenticationError("No authentication provider configured")

    #     success = await provider.authenticate(**kwargs)
    #     if success and provider_name:
    #         self.active_provider = provider_name

    #     return success

    async def authenticate(
        self, provider_name: Optional[str] = None, **kwargs
    ) -> dict:
        """Authenticate with specified or active provider.

        Args:
            provider_name: Name of provider to use (uses active if None)
            **kwargs: Authentication parameters

        Returns:
            Authentication result dictionary

        Raises:
            AuthenticationError: If no provider available or auth fails
        """
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

        result = await provider.authenticate(**kwargs)
        if result and provider_name:
            self.active_provider = provider_name
        return result

    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers from active provider.

        Returns:
            Dictionary of headers

        Raises:
            AuthenticationError: If not authenticated
        """
        provider = self.get_active_provider()
        if not provider:
            raise AuthenticationError("No active authentication provider")

        if not await provider.is_authenticated():
            raise AuthenticationError("Not authenticated")

        return await provider.get_auth_headers()

    async def get_auth_cookies(self) -> List[Dict[str, Any]]:
        """
        Get authentication cookies from active provider.

        Returns:
            List of cookie dictionaries

        Raises:
            AuthenticationError: If not authenticated
        """
        provider = self.get_active_provider()
        if not provider:
            raise AuthenticationError("No active authentication provider")

        if not await provider.is_authenticated():
            raise AuthenticationError("Not authenticated")

        return await provider.get_auth_cookies()

    async def logout(self) -> None:
        """Log out from all providers."""
        for provider in self.providers.values():
            try:
                await provider.logout()
            except Exception as e:
                logger.warning(f"Error logging out from {provider}: {e}")

        self.active_provider = None

    def list_providers(self) -> List[str]:
        """
        List all registered providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

# EOF
