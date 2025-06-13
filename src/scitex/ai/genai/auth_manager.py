#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:00:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/auth_manager.py

"""
Handles API key management and validation for AI providers.

This module provides secure handling of API keys including:
- Environment variable retrieval
- Key validation
- Masked key display for security
"""

import os
from typing import Optional, Dict, Any


class AuthManager:
    """Manages API key authentication for AI providers.

    Example
    -------
    >>> auth = AuthManager("sk-abc123...", "OpenAI")
    >>> auth.validate_key()
    True
    >>> auth.get_masked_key()
    'sk-a****3...'

    Parameters
    ----------
    api_key : str
        The API key for authentication
    provider : str
        The provider name (e.g., "OpenAI", "Anthropic")
    """

    # Mapping of providers to environment variable names
    ENV_VAR_MAPPING: Dict[str, str] = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "Google": "GOOGLE_API_KEY",
        "Groq": "GROQ_API_KEY",
        "DeepSeek": "DEEPSEEK_API_KEY",
        "Perplexity": "PERPLEXITY_API_KEY",
        "Llama": "LLAMA_API_KEY",
    }

    def __init__(self, api_key: Optional[str], provider: str):
        """Initialize AuthManager with API key and provider.

        Parameters
        ----------
        api_key : Optional[str]
            The API key. If None, will attempt to get from environment
        provider : str
            The provider name
        """
        # Normalize provider name to lowercase
        self.provider = provider.lower()

        # Check if provider is known
        if self.provider not in [p.lower() for p in self.ENV_VAR_MAPPING.keys()]:
            raise ValueError(f"Unknown provider: {provider}")

        # Store private api key
        self._api_key = api_key or self.get_key_from_env(provider)

        if not self._api_key:
            raise ValueError(f"No API key provided for {provider}")

        # Public property for backward compatibility
        self.api_key = self._api_key

    def validate(self) -> bool:
        """Validate the API key format.

        Returns
        -------
        bool
            True if key appears valid, False otherwise

        Raises
        ------
        ValueError
            If API key is missing or invalid
        """
        if not self._api_key:
            raise ValueError("No API key configured")

        # Basic validation - ensure key is not empty and has reasonable length
        if len(self._api_key) < 10:
            raise ValueError(
                f"API key for {self.provider} appears to be invalid (too short)"
            )

        return True

    def get_masked_key(self) -> str:
        """Get a masked version of the API key for display.

        Returns
        -------
        str
            Masked API key showing only first few and last few characters
        """
        if not self._api_key:
            return "No API key"

        if len(self._api_key) <= 8:
            return "*****"

        # Match test expectation: show first 3 and last 4 characters with "..." in between
        return f"{self._api_key[:3]}...{self._api_key[-4:]}"

    def get_client_config(self) -> Dict[str, Any]:
        """Get client configuration for the provider.

        Returns
        -------
        Dict[str, any]
            Configuration dictionary for the provider client
        """
        config = {"api_key": self._api_key}

        # Provider-specific configurations
        if self.provider == "openai":
            # Check for optional organization
            org = os.getenv("OPENAI_ORGANIZATION")
            if org:
                config["organization"] = org
        elif self.provider == "anthropic":
            config["max_retries"] = 3
        elif self.provider == "google":
            # Google only needs API key
            pass

        return config

    @classmethod
    def get_key_from_env(cls, provider: str) -> Optional[str]:
        """Get API key from environment variable.

        Parameters
        ----------
        provider : str
            The provider name

        Returns
        -------
        Optional[str]
            The API key if found in environment, None otherwise
        """
        # Find the env var name case-insensitively
        for p, env_var in cls.ENV_VAR_MAPPING.items():
            if p.lower() == provider.lower():
                return os.getenv(env_var)

        # Try generic pattern if not found
        env_var = f"{provider.upper()}_API_KEY"
        return os.getenv(env_var)

    def get_api_key(self, provider: str, api_key: Optional[str] = None) -> str:
        """Get API key for a provider.

        This method is used by provider_base.py for compatibility.

        Parameters
        ----------
        provider : str
            The provider name
        api_key : Optional[str]
            Explicit API key, if None will use environment

        Returns
        -------
        str
            The API key

        Raises
        ------
        ValueError
            If no API key is found
        """
        if api_key:
            return api_key

        key = self.get_key_from_env(provider)
        if not key:
            raise ValueError(f"No API key provided for {provider}")

        return key

    def __repr__(self) -> str:
        """String representation of AuthManager."""
        return f"AuthManager(provider={self.provider}, key={self.get_masked_key()})"


# EOF
