#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 20:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_AuthenticationProviders.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_AuthenticationProviders.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Authentication providers for SciTeX Scholar.

This module provides a unified interface for various academic authentication systems.
Each provider handles authentication and provides cookies/headers for authenticated requests.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..errors import AuthenticationError

logger = logging.getLogger(__name__)


class AuthenticationProvider(ABC):
    """
    Abstract base class for authentication providers.
    
    All authentication providers (OpenAthens, EZProxy, Shibboleth, etc.)
    should inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace("Authentication", "")
        
    @abstractmethod
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """
        Check if currently authenticated.
        
        Args:
            verify_live: If True, perform live verification against auth servers
            
        Returns:
            True if authenticated, False otherwise
        """
        pass
    
    @abstractmethod
    async def authenticate(self, force: bool = False) -> bool:
        """
        Perform authentication.
        
        Args:
            force: Force re-authentication even if already authenticated
            
        Returns:
            True if authentication successful
        """
        pass
    
    @abstractmethod
    async def get_authenticated_session(self) -> Dict[str, Any]:
        """
        Get session data for authenticated requests.
        
        Returns:
            Dictionary with:
                - cookies: List of cookie dicts for requests
                - headers: Dict of headers to add to requests
                - context: Any additional context needed
        """
        pass
    
    async def verify_authentication(self) -> Tuple[bool, str]:
        """
        Verify authentication with detailed status.
        
        Returns:
            (is_authenticated, status_message)
        """
        try:
            is_auth = await self.is_authenticated(verify_live=True)
            if is_auth:
                return True, f"{self.name} authentication verified"
            else:
                return False, f"{self.name} not authenticated"
        except Exception as e:
            return False, f"{self.name} verification failed: {str(e)}"
    
    def __str__(self) -> str:
        return f"{self.name}Authentication"


class OpenAthensAuthentication(AuthenticationProvider):
    """
    OpenAthens authentication provider.
    
    This is fully implemented and uses browser-based authentication
    with manual login and 2FA support.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Import the existing OpenAthens authenticator
        from ._OpenAthensAuthenticator import OpenAthensAuthenticator
        
        self.authenticator = OpenAthensAuthenticator(
            email=config.get("email"),
            timeout=config.get("timeout", 30),
            debug_mode=config.get("debug_mode", False),
        )
        
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """Check if OpenAthens session is valid."""
        return await self.authenticator.is_authenticated(verify_live=verify_live)
    
    async def authenticate(self, force: bool = False) -> bool:
        """Open browser for OpenAthens login."""
        return await self.authenticator.authenticate_async(force=force)
    
    async def get_authenticated_session(self) -> Dict[str, Any]:
        """Get OpenAthens cookies and headers."""
        if not await self.is_authenticated():
            raise AuthenticationError("Not authenticated with OpenAthens")
            
        # Get cookies from authenticator
        cookies = []
        if hasattr(self.authenticator, '_full_cookies') and self.authenticator._full_cookies:
            cookies = self.authenticator._full_cookies
        elif hasattr(self.authenticator, '_cookies') and self.authenticator._cookies:
            # Convert simple cookies to full format
            cookies = [
                {
                    'name': name,
                    'value': value,
                    'domain': '.openathens.net',
                    'path': '/'
                }
                for name, value in self.authenticator._cookies.items()
            ]
        
        return {
            'cookies': cookies,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'context': {
                'provider': 'OpenAthens',
                'email': self.config.get('email')
            }
        }


class EZProxyAuthentication(AuthenticationProvider):
    """
    EZProxy authentication provider (placeholder).
    
    EZProxy is a web proxy that provides remote access to licensed content.
    Implementation pending.
    """
    
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """Check EZProxy authentication status."""
        logger.debug("EZProxy authentication check not yet implemented")
        return False
    
    async def authenticate(self, force: bool = False) -> bool:
        """Authenticate with EZProxy."""
        raise NotImplementedError(
            "EZProxy authentication not yet implemented. "
            "EZProxy support is planned for a future release. "
            "Please use OpenAthens authentication for now."
        )
    
    async def get_authenticated_session(self) -> Dict[str, Any]:
        """Get EZProxy session data."""
        raise NotImplementedError("EZProxy session management not yet implemented")


class ShibbolethAuthentication(AuthenticationProvider):
    """
    Shibboleth authentication provider (placeholder).
    
    Shibboleth is a standards-based, open source software package 
    for web single sign-on across or within organizational boundaries.
    Implementation pending.
    """
    
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """Check Shibboleth authentication status."""
        logger.debug("Shibboleth authentication check not yet implemented")
        return False
    
    async def authenticate(self, force: bool = False) -> bool:
        """Authenticate with Shibboleth."""
        raise NotImplementedError(
            "Shibboleth authentication not yet implemented. "
            "Shibboleth/SAML support is planned for a future release. "
            "Please use OpenAthens authentication for now."
        )
    
    async def get_authenticated_session(self) -> Dict[str, Any]:
        """Get Shibboleth session data."""
        raise NotImplementedError("Shibboleth session management not yet implemented")


class LeanLibraryAuthentication(AuthenticationProvider):
    """
    Lean Library authentication provider (placeholder).
    
    Lean Library is a browser extension that helps users access library resources.
    Implementation pending.
    """
    
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """Check Lean Library authentication status."""
        logger.debug("Lean Library authentication check not yet implemented")
        return False
    
    async def authenticate(self, force: bool = False) -> bool:
        """Authenticate with Lean Library."""
        raise NotImplementedError(
            "Lean Library authentication not yet implemented. "
            "Browser extension integration is planned for a future release. "
            "Please use OpenAthens authentication for now."
        )
    
    async def get_authenticated_session(self) -> Dict[str, Any]:
        """Get Lean Library session data."""
        raise NotImplementedError("Lean Library session management not yet implemented")


class IPBasedAuthentication(AuthenticationProvider):
    """
    IP-based authentication provider.
    
    Many institutions provide access based on IP address ranges.
    This provider detects if the current IP has access.
    """
    
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """Check if current IP has institutional access."""
        if not verify_live:
            # Quick check - assume authenticated if on campus network
            # This is a simplified check
            return self._is_campus_network()
        
        # Live check - try accessing a known paywalled resource
        try:
            import aiohttp
            test_url = "https://www.nature.com/articles/nature07201"  # Classic test paper
            
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, allow_redirects=False) as response:
                    # If we get 200 or see PDF options, we likely have IP access
                    if response.status == 200:
                        text = await response.text()
                        return "Download PDF" in text or "Full text" in text
                    return False
        except Exception as e:
            logger.debug(f"IP access check failed: {e}")
            return False
    
    async def authenticate(self, force: bool = False) -> bool:
        """No authentication needed for IP-based access."""
        is_auth = await self.is_authenticated(verify_live=True)
        if is_auth:
            logger.info("IP-based access detected")
            return True
        else:
            logger.info(
                "No IP-based access detected. You may need to use VPN "
                "or be on campus network for institutional access."
            )
            return False
    
    async def get_authenticated_session(self) -> Dict[str, Any]:
        """IP-based access doesn't need special session data."""
        return {
            'cookies': [],
            'headers': {},
            'context': {
                'provider': 'IP-based',
                'note': 'Using institutional IP access'
            }
        }
    
    def _is_campus_network(self) -> bool:
        """Simple check if on campus network (can be enhanced)."""
        # This is a placeholder - real implementation would check:
        # - Current IP against known institutional ranges
        # - VPN connection status
        # - Network SSID for campus WiFi
        return False


class AuthenticationManager:
    """
    Manages multiple authentication providers.
    
    This class handles the registration and use of multiple authentication
    providers, trying them in order until one succeeds.
    """
    
    def __init__(self):
        """Initialize authentication manager."""
        self.providers: List[AuthenticationProvider] = []
        self._authenticated_provider: Optional[AuthenticationProvider] = None
        
    def register_provider(self, provider: AuthenticationProvider):
        """
        Register an authentication provider.
        
        Args:
            provider: Authentication provider instance
        """
        logger.info(f"Registered {provider.name} authentication provider")
        self.providers.append(provider)
        
    async def ensure_authenticated(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure at least one provider is authenticated.
        
        Returns:
            (success, provider_name)
        """
        # First check if any provider is already authenticated
        for provider in self.providers:
            try:
                if await provider.is_authenticated():
                    self._authenticated_provider = provider
                    return True, provider.name
            except NotImplementedError:
                continue
            except Exception as e:
                logger.debug(f"{provider.name} check failed: {e}")
                
        # Try to authenticate with each provider
        for provider in self.providers:
            try:
                logger.info(f"Attempting authentication with {provider.name}")
                if await provider.authenticate_async():
                    self._authenticated_provider = provider
                    return True, provider.name
            except NotImplementedError as e:
                logger.info(f"{provider.name}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"{provider.name} authentication failed: {e}")
                
        return False, None
    
    async def get_authenticated_session(self) -> Optional[Dict[str, Any]]:
        """
        Get session data from the authenticated provider.
        
        Returns:
            Session data or None if not authenticated
        """
        if self._authenticated_provider:
            try:
                return await self._authenticated_provider.get_authenticated_session()
            except Exception as e:
                logger.error(f"Failed to get session from {self._authenticated_provider.name}: {e}")
                
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all registered providers."""
        status = {
            'registered_providers': [p.name for p in self.providers],
            'authenticated_provider': self._authenticated_provider.name if self._authenticated_provider else None,
            'total_providers': len(self.providers)
        }
        return status


# Factory function for creating providers
def create_authentication_provider(
    provider_type: str,
    config: Optional[Dict[str, Any]] = None
) -> AuthenticationProvider:
    """
    Create an authentication provider by type.
    
    Args:
        provider_type: Type of provider ('openathens', 'ezproxy', etc.)
        config: Provider-specific configuration
        
    Returns:
        Authentication provider instance
        
    Raises:
        ValueError: If provider type is unknown
    """
    providers = {
        'openathens': OpenAthensAuthentication,
        'ezproxy': EZProxyAuthentication,
        'shibboleth': ShibbolethAuthentication,
        'lean_library': LeanLibraryAuthentication,
        'ip_based': IPBasedAuthentication,
    }
    
    provider_type = provider_type.lower()
    if provider_type not in providers:
        raise ValueError(
            f"Unknown authentication provider: {provider_type}. "
            f"Available providers: {', '.join(providers.keys())}"
        )
        
    return providers[provider_type](config)


# Export main classes
__all__ = [
    'AuthenticationProvider',
    'OpenAthensAuthentication',
    'EZProxyAuthentication', 
    'ShibbolethAuthentication',
    'LeanLibraryAuthentication',
    'IPBasedAuthentication',
    'AuthenticationManager',
    'create_authentication_provider'
]