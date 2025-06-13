#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/src/scitex/ai/genai/__init__.py

"""
GenAI module for unified access to multiple AI providers.

This module provides a consistent interface for interacting with various
AI providers (OpenAI, Anthropic, Google, etc.) with built-in cost tracking,
chat history management, and error handling.
"""

from typing import List, Dict, Any, Optional, Union
import logging

from .provider_factory import Provider, create_provider, GenAI as GenAIFactory
from .auth_manager import AuthManager
from .chat_history import ChatHistory
from .cost_tracker import CostTracker
from .response_handler import ResponseHandler
from .base_provider import BaseProvider, CompletionResponse

# Import legacy providers for backward compatibility
from .anthropic import Anthropic
from .openai import OpenAI
from .google import Google
from .groq import Groq
from .deepseek import DeepSeek
from .llama import Llama
from .perplexity import Perplexity
from .genai_factory import genai_factory

logger = logging.getLogger(__name__)


class GenAI:
    """
    Unified interface for multiple AI providers.

    This class provides a consistent API for interacting with various AI providers
    while handling authentication, chat history, cost tracking, and response processing.

    Args:
        provider: Provider name (e.g., 'openai', 'anthropic', 'google')
        api_key: Optional API key (if not provided, will use environment variable)
        model: Model name (if not provided, will use provider's default)
        system_prompt: Optional system prompt to prepend to conversations
        **kwargs: Additional provider-specific configuration

    Example:
        >>> from scitex.ai.genai import GenAI
        >>>
        >>> # Basic usage
        >>> ai = GenAI(provider="openai")
        >>> response = ai.complete("What is the capital of France?")
        >>> print(response)
        "The capital of France is Paris."
        >>>
        >>> # With specific model and system prompt
        >>> ai = GenAI(
        ...     provider="anthropic",
        ...     model="claude-3-opus-20240229",
        ...     system_prompt="You are a helpful geography expert."
        ... )
        >>> response = ai.complete("Tell me about Paris.")
        >>>
        >>> # Check costs
        >>> print(ai.get_cost_summary())
        "Total cost: $0.015 | Requests: 2 | Tokens: 1,234"
    """

    def __init__(
        self,
        provider: Union[str, Provider],
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Initialize GenAI with specified provider."""
        # Store provider name
        if isinstance(provider, str):
            self.provider_name = provider.lower()
        else:
            self.provider_name = provider.value

        # Initialize components
        self.auth_manager = AuthManager(api_key, self.provider_name)
        self.chat_history = ChatHistory(n_keep=-1)  # Keep all messages by default
        self.response_handler = ResponseHandler()

        # Get API key from auth manager if not provided
        if api_key is None:
            api_key = self.auth_manager.api_key

        # Create provider instance
        self.provider = create_provider(
            provider=self.provider_name, api_key=api_key, model=model, **kwargs
        )

        # Initialize cost tracker with provider and model
        # Note: provider instance may have a model attribute set during initialization
        actual_model = getattr(self.provider, "model", None) or model or "unknown"
        self.cost_tracker = CostTracker(provider=self.provider_name, model=actual_model)

        # Add system prompt if provided
        if system_prompt:
            self.chat_history.add_message("system", system_prompt)

        logger.info(f"Initialized GenAI with provider: {self.provider_name}")

    def complete(
        self, prompt: str, images: Optional[List[str]] = None, **kwargs
    ) -> str:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: The input prompt
            images: Optional list of image URLs or base64 strings
            **kwargs: Additional provider-specific parameters

        Returns:
            The generated response text

        Raises:
            ValueError: If the provider doesn't support images but images are provided
            Exception: Provider-specific exceptions
        """
        # Add user message to history
        self.chat_history.add_message("user", prompt, images)

        # Get messages for API call
        messages = [msg.to_dict() for msg in self.chat_history.get_messages()]

        # Call provider
        try:
            response: CompletionResponse = self.provider.complete(
                messages=messages, **kwargs
            )
        except Exception as e:
            logger.error(f"Provider {self.provider_name} failed: {str(e)}")
            raise

        # Process response - CompletionResponse has a content attribute
        content = response.content

        # Add assistant message to history
        self.chat_history.add_message("assistant", content)

        # Track costs - CompletionResponse has input_tokens and output_tokens
        self.cost_tracker.update(
            input_tokens=response.input_tokens, output_tokens=response.output_tokens
        )

        return content

    def complete_async(self, prompt: str, images: Optional[List[str]] = None, **kwargs):
        """
        Async version of complete method.

        Args:
            prompt: The input prompt
            images: Optional list of image URLs or base64 strings
            **kwargs: Additional provider-specific parameters

        Returns:
            Awaitable that resolves to the generated response text
        """
        raise NotImplementedError("Async completion not yet implemented")

    def stream(self, prompt: str, images: Optional[List[str]] = None, **kwargs):
        """
        Stream completions for the given prompt.

        Args:
            prompt: The input prompt
            images: Optional list of image URLs or base64 strings
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of the generated response
        """
        raise NotImplementedError("Streaming not yet implemented")

    def clear_history(self):
        """Clear the chat history."""
        self.chat_history.clear()
        logger.info("Chat history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        return self.chat_history.messages

    def get_cost_summary(self) -> str:
        """Get a summary of costs incurred."""
        return self.cost_tracker.get_summary()

    def get_detailed_costs(self) -> Dict[str, Any]:
        """Get detailed cost breakdown."""
        return {
            "total_cost": self.cost_tracker.total_cost,
            "total_prompt_tokens": self.cost_tracker.total_prompt_tokens,
            "total_completion_tokens": self.cost_tracker.total_completion_tokens,
            "request_count": self.cost_tracker.request_count,
            "cost_by_model": self.cost_tracker.cost_by_model,
        }

    def reset_costs(self):
        """Reset cost tracking."""
        self.cost_tracker.reset()
        logger.info("Cost tracking reset")

    def __repr__(self) -> str:
        """String representation of GenAI instance."""
        return (
            f"GenAI(provider='{self.provider_name}', "
            f"model='{self.provider.model}', "
            f"requests={self.cost_tracker.request_count})"
        )


# Convenience function for one-off completions
def complete(
    prompt: str,
    provider: Union[str, Provider] = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function for one-off completions without managing state.

    Args:
        prompt: The input prompt
        provider: Provider name or enum
        model: Optional model name
        api_key: Optional API key
        **kwargs: Additional parameters

    Returns:
        The generated response text

    Example:
        >>> from scitex.ai.genai import complete
        >>> response = complete("What is 2+2?", provider="anthropic")
        >>> print(response)
        "2 + 2 = 4"
    """
    genai = GenAI(provider=provider, model=model, api_key=api_key)
    return genai.complete(prompt, **kwargs)


# Export public API
__all__ = [
    # New API
    "GenAI",
    "GenAIFactory",
    "complete",
    "Provider",
    "create_provider",
    "AuthManager",
    "ChatHistory",
    "CostTracker",
    "ResponseHandler",
    # Legacy API for backward compatibility
    "genai_factory",
    "Anthropic",
    "OpenAI",
    "Google",
    "Groq",
    "DeepSeek",
    "Llama",
    "Perplexity",
]
