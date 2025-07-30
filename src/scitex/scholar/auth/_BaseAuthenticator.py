#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:04:00 (ywatanabe)"
# File: ./src/scitex/scholar/auth/_BaseAuthenticator.py
# ----------------------------------------

"""
Abstract base class for authenticators.

This module provides the base interface that all authenticators
(OpenAthens, Lean Library, etc.) must implement.
"""

"""Imports"""
from scitex import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...errors import AuthenticationError

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
    async def is_authenticated(self, verify_live: bool = False) -> bool:
        """
        Check if currently authenticated.
        
        Args:
            verify_live: If True, verify with actual request instead of just checking session
            
        Returns:
            True if authenticated, False otherwise
        """
        pass
        
    @abstractmethod
    async def authenticate(self, **kwargs) -> dict:
        """
        Perform authentication and return session data.
        
        Args:
            **kwargs: Authenticator-specific authentication parameters
            
        Returns:
            Dictionary containing session data (e.g., cookies, tokens)
        """
        pass
        
    @abstractmethod
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for requests.
        
        Returns:
            Dictionary of headers to include in authenticated requests
        """
        pass
        
    @abstractmethod
    async def get_auth_cookies(self) -> List[Dict[str, Any]]:
        """
        Get authentication cookies for requests.
        
        Returns:
            List of cookie dictionaries
        """
        pass
        
    @abstractmethod
    async def logout(self) -> None:
        """Log out and clear authentication state."""
        pass
        
    @abstractmethod
    async def get_session_info(self) -> Dict[str, Any]:
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

# EOF