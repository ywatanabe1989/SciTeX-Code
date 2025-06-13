#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:30:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/base_provider.py

"""
Abstract base class for AI provider implementations.

This module defines the interface that all AI providers must implement,
ensuring consistency across different providers (OpenAI, Anthropic, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Generator, Optional


class Provider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    LLAMA = "llama"
    PERPLEXITY = "perplexity"
    MOCK = "mock"  # For testing

    def __str__(self):
        return self.value


class Role(str, Enum):
    """Message roles for chat conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ProviderConfig:
    """Configuration for AI providers."""

    provider: str
    model: str
    api_key: Optional[str] = None
    system_prompt: str = ""
    temperature: float = 1.0
    max_tokens: int = 4096
    stream: bool = False
    seed: Optional[int] = None
    n_keep: int = 1


@dataclass
class CompletionResponse:
    """Standard response format for completions."""

    content: str
    input_tokens: int
    output_tokens: int
    finish_reason: str = "stop"
    provider_response: Optional[Any] = None


class BaseProvider(ABC):
    """Abstract base class for AI providers.

    All AI provider implementations must inherit from this class
    and implement the required abstract methods.

    Example
    -------
    >>> class MyProvider(BaseProvider):
    ...     def init_client(self) -> Any:
    ...         return MyAPIClient(self.api_key)
    ...
    ...     def format_history(self, history: List[Dict]) -> List[Dict]:
    ...         # Provider-specific formatting
    ...         return history
    ...
    ...     def call_static(self, messages: List[Dict], **kwargs) -> Any:
    ...         # Make API call
    ...         return self.client.complete(messages)
    ...
    ...     def call_stream(self, messages: List[Dict], **kwargs) -> Generator:
    ...         # Make streaming API call
    ...         for chunk in self.client.stream(messages):
    ...             yield chunk
    """

    @abstractmethod
    def init_client(self) -> Any:
        """Initialize the provider-specific client.

        This method should create and configure the API client
        for the specific provider (e.g., OpenAI client, Anthropic client).

        Returns
        -------
        Any
            The initialized client object
        """
        pass

    @abstractmethod
    def format_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format conversation history for the provider's API.

        Different providers may expect different formats for conversation
        history. This method converts the standard format to the
        provider-specific format.

        Parameters
        ----------
        history : List[Dict[str, Any]]
            Standard format conversation history

        Returns
        -------
        List[Dict[str, Any]]
            Provider-specific formatted history
        """
        pass

    @abstractmethod
    def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        """Make a static (non-streaming) API call.

        Parameters
        ----------
        messages : List[Dict[str, Any]]
            Formatted conversation messages
        **kwargs
            Additional provider-specific parameters

        Returns
        -------
        Any
            Provider-specific response object
        """
        pass

    @abstractmethod
    def call_stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[str, None, None]:
        """Make a streaming API call.

        Parameters
        ----------
        messages : List[Dict[str, Any]]
            Formatted conversation messages
        **kwargs
            Additional provider-specific parameters

        Yields
        ------
        str
            Response text chunks
        """
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming responses.

        Returns
        -------
        bool
            True if streaming is supported
        """
        pass

    @property
    @abstractmethod
    def supports_images(self) -> bool:
        """Whether this provider supports image inputs.

        Returns
        -------
        bool
            True if images are supported
        """
        pass

    @property
    @abstractmethod
    def max_context_length(self) -> int:
        """Maximum context length in tokens.

        Returns
        -------
        int
            Maximum number of tokens
        """
        pass

    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities summary.

        Returns
        -------
        Dict[str, Any]
            Dictionary of provider capabilities
        """
        return {
            "supports_streaming": self.supports_streaming,
            "supports_images": self.supports_images,
            "max_context_length": self.max_context_length,
        }

    def extract_tokens_from_response(self, response: Any) -> Dict[str, int]:
        """Extract token usage from provider response.

        Default implementation returns zeros. Providers should override
        to extract actual token counts from their response format.

        Parameters
        ----------
        response : Any
            Provider-specific response object

        Returns
        -------
        Dict[str, int]
            Dictionary with 'input_tokens' and 'output_tokens'
        """
        return {"input_tokens": 0, "output_tokens": 0}

    def handle_rate_limit(self, error: Exception) -> bool:
        """Handle rate limit errors.

        Default implementation returns False. Providers can override
        to implement retry logic or other handling.

        Parameters
        ----------
        error : Exception
            The error that occurred

        Returns
        -------
        bool
            True if the error was handled and operation should retry
        """
        return False

    def validate_model(self, model: str) -> bool:
        """Validate if a model is supported.

        Default implementation returns True. Providers should override
        to validate against their supported models.

        Parameters
        ----------
        model : str
            Model name to validate

        Returns
        -------
        bool
            True if model is supported
        """
        return True

    def get_error_message(self, error: Exception) -> str:
        """Extract user-friendly error message.

        Default implementation returns string representation.
        Providers can override for better error messages.

        Parameters
        ----------
        error : Exception
            The error that occurred

        Returns
        -------
        str
            User-friendly error message
        """
        return str(error)


# EOF
