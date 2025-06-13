#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/src/scitex/ai/genai/deepseek_provider.py

"""
DeepSeek provider implementation for GenAI.

Provides access to DeepSeek's API for code generation and chat.
Uses OpenAI-compatible API endpoint.
"""

from typing import List, Dict, Any, Optional, Generator
import logging
import os

from .base_provider import BaseProvider, CompletionResponse, Provider
from .provider_factory import register_provider

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseProvider):
    """
    DeepSeek provider implementation.

    Supports DeepSeek Chat and DeepSeek Coder models.
    """

    SUPPORTED_MODELS = [
        "deepseek-chat",
        "deepseek-coder",
    ]

    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self, config):
        """Initialize DeepSeek provider."""
        self.config = config
        self.api_key = config.api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = config.model or self.DEFAULT_MODEL
        self.kwargs = config.kwargs or {}

        if not self.api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not provided and not found in environment"
            )

        # Import OpenAI client (DeepSeek uses OpenAI-compatible API)
        try:
            from openai import OpenAI as OpenAIClient

            # DeepSeek uses a custom base URL
            self.client = OpenAIClient(
                api_key=self.api_key, base_url="https://api.deepseek.com/beta"
            )
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> CompletionResponse:
        """
        Generate completion using DeepSeek API.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            CompletionResponse with generated text and usage info
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")

        # Format messages for DeepSeek (same as OpenAI format)
        formatted_messages = self.format_messages(messages)

        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": formatted_messages,
        }

        # Add optional parameters
        for param in ["temperature", "max_tokens", "top_p", "stop", "seed", "n"]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        try:
            # Make API call
            response = self.client.chat.completions.create(**api_params)

            # Extract content and usage
            content = response.choices[0].message.content
            usage = response.usage

            return CompletionResponse(
                content=content,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                finish_reason=response.choices[0].finish_reason,
                provider_response=response,
            )

        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for DeepSeek API.

        DeepSeek uses the same message format as OpenAI.
        """
        formatted_messages = []

        for msg in messages:
            formatted_msg = {"role": msg["role"], "content": msg["content"]}
            formatted_messages.append(formatted_msg)

        return formatted_messages

    def validate_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """Validate message format."""
        if not messages:
            return False

        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if "role" not in msg or "content" not in msg:
                return False
            if msg["role"] not in ["system", "user", "assistant"]:
                return False

        return True

    def stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[str, None, CompletionResponse]:
        """Generate a streaming completion.

        Args:
            messages: List of messages in standard format
            **kwargs: Additional parameters

        Yields:
            Text chunks during streaming

        Returns:
            Final CompletionResponse when complete
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")

        # Format messages for DeepSeek
        formatted_messages = self.format_messages(messages)

        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
        }

        # Add optional parameters
        for param in ["temperature", "max_tokens", "top_p", "stop", "seed", "n"]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        try:
            # Make streaming API call
            stream = self.client.chat.completions.create(**api_params)

            # Track content and usage
            full_content = ""
            prompt_tokens = 0
            completion_tokens = 0

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield content

                # Try to get usage info from chunks (if available)
                if hasattr(chunk, "usage") and chunk.usage:
                    if hasattr(chunk.usage, "prompt_tokens"):
                        prompt_tokens = chunk.usage.prompt_tokens
                    if hasattr(chunk.usage, "completion_tokens"):
                        completion_tokens = chunk.usage.completion_tokens

            # If no usage info from stream, estimate
            if prompt_tokens == 0:
                prompt_tokens = self.count_tokens(str(formatted_messages))
            if completion_tokens == 0:
                completion_tokens = self.count_tokens(full_content)

            # Return final response
            return CompletionResponse(
                content=full_content,
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"DeepSeek streaming error: {str(e)}")
            raise

    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens (estimated)
        """
        # DeepSeek uses similar tokenization to GPT models
        # Rough estimate: 1 token ≈ 4 characters or 0.75 words
        return len(text.split()) * 4 // 3

    @property
    def supports_images(self) -> bool:
        """Check if this provider/model supports image inputs."""
        # DeepSeek currently doesn't support multimodal inputs
        return False

    @property
    def supports_streaming(self) -> bool:
        """Check if this provider/model supports streaming."""
        return True

    @property
    def max_context_length(self) -> int:
        """Get maximum context length for this model."""
        # DeepSeek models typically support 4K-16K context
        context_lengths = {
            "deepseek-chat": 4096,
            "deepseek-coder": 16384,
        }
        return context_lengths.get(self.model, 4096)


# Auto-register when module is imported
register_provider(Provider.DEEPSEEK.value, DeepSeekProvider)
