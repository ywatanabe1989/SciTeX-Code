#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-15 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

"""
Factory for creating AI provider instances.

This module provides a factory pattern for instantiating different AI providers
with consistent configuration.
"""

from enum import Enum
from typing import Any, Dict, Optional, Type, Union
import os

from .base_provider import BaseProvider, Provider
from .provider_base import ProviderConfig


class ProviderRegistry:
    """Registry for managing AI providers and their aliases."""

    def __init__(self):
        """Initialize the registry with provider storage and aliases."""
        self._providers: Dict[Provider, Type[BaseProvider]] = {}
        self._aliases: Dict[str, Provider] = {
            # OpenAI aliases
            "openai": Provider.OPENAI,
            "gpt": Provider.OPENAI,
            "gpt-3": Provider.OPENAI,
            "gpt-3.5": Provider.OPENAI,
            "gpt-4": Provider.OPENAI,
            "gpt-4o": Provider.OPENAI,
            "o1": Provider.OPENAI,
            # Anthropic aliases
            "anthropic": Provider.ANTHROPIC,
            "claude": Provider.ANTHROPIC,
            "claude-2": Provider.ANTHROPIC,
            "claude-3": Provider.ANTHROPIC,
            "claude-3-opus": Provider.ANTHROPIC,
            "claude-3-sonnet": Provider.ANTHROPIC,
            "claude-3-haiku": Provider.ANTHROPIC,
            # Google aliases
            "google": Provider.GOOGLE,
            "gemini": Provider.GOOGLE,
            "bard": Provider.GOOGLE,
            "bison": Provider.GOOGLE,
            "palm": Provider.GOOGLE,
            # Groq aliases
            "groq": Provider.GROQ,
            "mixtral": Provider.GROQ,
            "llama": Provider.GROQ,
            "llama2": Provider.GROQ,
            "llama3": Provider.GROQ,
            # Perplexity aliases
            "perplexity": Provider.PERPLEXITY,
            "pplx": Provider.PERPLEXITY,
            # DeepSeek aliases
            "deepseek": Provider.DEEPSEEK,
            "deepseek-coder": Provider.DEEPSEEK,
            "deepseek-chat": Provider.DEEPSEEK,
        }

    def register(self, provider: Provider, provider_class: Type[BaseProvider]) -> None:
        """
        Register a provider implementation.

        Parameters
        ----------
        provider : Provider
            Provider enum value
        provider_class : Type[BaseProvider]
            Provider implementation class
        """
        self._providers[provider] = provider_class

    def get(self, provider: Provider) -> Type[BaseProvider]:
        """
        Get a registered provider class.

        Parameters
        ----------
        provider : Provider
            Provider enum value

        Returns
        -------
        Type[BaseProvider]
            Provider implementation class

        Raises
        ------
        ValueError
            If provider is not registered
        """
        if provider not in self._providers:
            raise ValueError(f"Provider {provider} is not registered")
        return self._providers[provider]

    def resolve_provider(self, provider_or_model: str) -> Provider:
        """
        Resolve a provider from a string or model name.

        Parameters
        ----------
        provider_or_model : str
            Provider name, alias, or model name

        Returns
        -------
        Provider
            Resolved provider enum value

        Raises
        ------
        ValueError
            If provider cannot be resolved
        """
        provider_lower = provider_or_model.lower()

        # Direct provider name match
        for p in Provider:
            if p.value == provider_lower:
                return p

        # Alias match
        if provider_lower in self._aliases:
            return self._aliases[provider_lower]

        # Try to infer from model name patterns
        model_patterns = {
            Provider.OPENAI: [
                "gpt-",
                "o1-",
                "text-davinci",
                "text-curie",
                "text-babbage",
                "text-ada",
            ],
            Provider.ANTHROPIC: ["claude-"],
            Provider.GOOGLE: ["gemini-", "palm-", "bison"],
            Provider.GROQ: ["mixtral-", "llama-"],
            Provider.PERPLEXITY: ["pplx-", "perplexity-"],
            Provider.DEEPSEEK: ["deepseek-"],
        }

        for provider, patterns in model_patterns.items():
            if any(provider_lower.startswith(pattern) for pattern in patterns):
                return provider

        raise ValueError(f"Cannot resolve provider from: {provider_or_model}")

    def list_providers(self) -> list[Provider]:
        """
        List registered providers.

        Returns
        -------
        list[Provider]
            List of registered provider enums
        """
        return list(self._providers.keys())


# Global registry instance
_registry = ProviderRegistry()

# Auto-register providers when they're imported
_auto_register_called = False


def _auto_register():
    """Auto-register available provider implementations."""
    global _auto_register_called
    if _auto_register_called:
        return
    _auto_register_called = True

    # Try to import and register providers
    try:
        # Import providers here to trigger their registration
        # Each provider module should register itself when imported
        from . import mock_provider  # For testing
        from . import anthropic_provider
        from . import openai_provider
        from . import google_provider
        from . import groq_provider
        from . import perplexity_provider
        from . import deepseek_provider
        from . import llama_provider
    except ImportError as e:
        # Log import errors but continue
        import warnings

        warnings.warn(f"Failed to import some providers: {e}")


class ModelRegistry:
    """Registry for model information."""

    @staticmethod
    def get_models_for_provider(provider: str) -> list[str]:
        """Get available models for a provider."""
        # This would be implemented with actual model data
        return []


# Module-level convenience functions
def register_provider(name: str, provider_class: Type[BaseProvider]) -> None:
    """
    Register a provider implementation.

    Parameters
    ----------
    name : str
        Provider name
    provider_class : Type[BaseProvider]
        Provider implementation class
    """
    provider = _registry.resolve_provider(name)
    _registry.register(provider, provider_class)


def create_provider(
    provider: str,
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    system_prompt: Optional[str] = None,
    stream: bool = False,
    seed: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 0.0,
    n_draft: int = 1,
    **kwargs: Any,
) -> BaseProvider:
    """
    Create a provider instance.

    Parameters
    ----------
    provider : str
        Provider name, alias, or model name
    api_key : Optional[str]
        API key for authentication
    model : str
        Model name to use
    system_prompt : Optional[str]
        System prompt to prepend to messages
    stream : bool
        Whether to stream responses
    seed : Optional[int]
        Random seed for reproducibility
    max_tokens : Optional[int]
        Maximum tokens in response
    temperature : float
        Sampling temperature
    n_draft : int
        Number of drafts to generate
    **kwargs : Any
        Additional provider-specific parameters

    Returns
    -------
    BaseProvider
        Provider instance
    """
    # Auto-register providers
    _auto_register()

    # Resolve provider
    provider_enum = _registry.resolve_provider(provider)

    # Get provider class
    provider_class = _registry.get(provider_enum)

    # Create configuration
    config = ProviderConfig(
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        stream=stream,
        seed=seed,
        max_tokens=max_tokens,
        temperature=temperature,
        n_draft=n_draft,
        kwargs=kwargs,
    )

    # Instantiate provider
    return provider_class(config)


def GenAI(
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    system_prompt: Optional[str] = None,
    stream: bool = False,
    seed: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 0.0,
    n_draft: int = 1,
    provider: Optional[str] = None,
    **kwargs: Any,
) -> BaseProvider:
    """
    Create an AI provider instance (backward compatibility).

    This function maintains backward compatibility with the old API.
    If provider is not specified, it infers from the model name.

    Parameters
    ----------
    api_key : Optional[str]
        API key for authentication
    model : str
        Model name to use
    system_prompt : Optional[str]
        System prompt to prepend to messages
    stream : bool
        Whether to stream responses
    seed : Optional[int]
        Random seed for reproducibility
    max_tokens : Optional[int]
        Maximum tokens in response
    temperature : float
        Sampling temperature
    n_draft : int
        Number of drafts to generate
    provider : Optional[str]
        Provider name (if not specified, inferred from model)
    **kwargs : Any
        Additional provider-specific parameters

    Returns
    -------
    BaseProvider
        Provider instance
    """
    # If provider is explicitly specified, use it
    if provider:
        return create_provider(
            provider=provider,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            stream=stream,
            seed=seed,
            max_tokens=max_tokens,
            temperature=temperature,
            n_draft=n_draft,
            **kwargs,
        )

    # Otherwise, try to infer from model name
    return create_provider(
        provider=model,  # Let resolve_provider handle it
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        stream=stream,
        seed=seed,
        max_tokens=max_tokens,
        temperature=temperature,
        n_draft=n_draft,
        **kwargs,
    )


## EOF
