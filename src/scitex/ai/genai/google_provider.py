#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/genai/google_provider.py

"""Google Generative AI (Gemini) provider implementation using the new component-based architecture.

This module provides integration with Google's Gemini models through the google.generativeai API.
"""

import os
from typing import Dict, List, Iterator, Optional, Any

try:
    from google import genai
except ImportError:
    raise ImportError(
        "google-generativeai package is required for Google provider. "
        "Install with: pip install google-generativeai"
    )

from .base_provider import BaseProvider, ProviderConfig


class GoogleProvider(BaseProvider):
    """Google Generative AI (Gemini) provider implementation."""

    SUPPORTED_MODELS = [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash",
        "gemini-2.0-flash-thinking-exp-01-21",
        "gemini-2.0-pro-exp-02-05",
        "gemini-2.0-flash-lite-preview-02-05",
    ]

    DEFAULT_MODEL = "gemini-1.5-pro-latest"

    def __init__(self, config: ProviderConfig):
        """Initialize Google provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.api_key = config.api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Google API key not provided. Set GOOGLE_API_KEY environment variable or pass api_key."
            )

        # Initialize Google Generative AI client
        self.client = genai.Client(api_key=self.api_key)

        # Set default max_tokens if not provided
        if self.config.max_tokens is None:
            self.config.max_tokens = 32_768

    def validate_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Validate message format.

        Args:
            messages: List of message dictionaries

        Raises:
            ValueError: If messages are invalid
        """
        if not messages:
            raise ValueError("Messages cannot be empty")

        for msg in messages:
            if "role" not in msg:
                raise ValueError(f"Missing role in message: {msg}")
            if "content" not in msg:
                raise ValueError(f"Missing content in message: {msg}")
            if msg["role"] not in ["system", "user", "assistant", "model"]:
                raise ValueError(f"Invalid role: {msg['role']}")

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for Google Generative AI API.

        Google expects a specific format with 'parts' and 'model' role instead of 'assistant'.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted messages for Google API
        """
        formatted = []

        # Add system prompt if configured
        if self.config.system_prompt:
            formatted.append(
                {"role": "user", "parts": [{"text": self.config.system_prompt}]}
            )
            formatted.append(
                {
                    "role": "model",
                    "parts": [
                        {"text": "I understand. I will follow these instructions."}
                    ],
                }
            )

        # Format user messages
        for msg in messages:
            role = msg["role"]
            # Convert assistant to model for Google API
            if role == "assistant":
                role = "model"
            elif role == "system":
                # System messages are handled as user messages in Google API
                role = "user"

            # Check if already formatted with parts
            if isinstance(msg.get("parts"), list):
                formatted.append({"role": role, "parts": msg["parts"]})
            else:
                formatted.append({"role": role, "parts": [{"text": msg["content"]}]})

        return formatted

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate a completion.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API

        Returns:
            Completion response dictionary
        """
        self.validate_messages(messages)
        formatted_messages = self.format_messages(messages)

        # Merge config parameters with kwargs
        model = self.config.model or self.DEFAULT_MODEL

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=formatted_messages,
                # Google API doesn't support all OpenAI parameters directly
                # Temperature and other settings would need to be set via generation_config
            )

            # Extract token usage if available
            usage = {}
            if hasattr(response, "usage_metadata"):
                usage = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": (
                        response.usage_metadata.prompt_token_count
                        + response.usage_metadata.candidates_token_count
                    ),
                }

            return {
                "content": response.text,
                "model": model,
                "usage": usage,
                "finish_reason": "stop",
            }
        except Exception as e:
            raise RuntimeError(f"Google Generative AI error: {str(e)}")

    def stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """Stream a completion.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API

        Yields:
            Chunks of the completion
        """
        self.validate_messages(messages)
        formatted_messages = self.format_messages(messages)

        model = self.config.model or self.DEFAULT_MODEL

        try:
            stream = self.client.models.generate_content_stream(
                model=model,
                contents=formatted_messages,
            )

            total_prompt_tokens = 0
            total_completion_tokens = 0

            for chunk in stream:
                if chunk and hasattr(chunk, "text") and chunk.text:
                    # Track token usage if available
                    if hasattr(chunk, "usage_metadata"):
                        if hasattr(chunk.usage_metadata, "prompt_token_count"):
                            total_prompt_tokens += (
                                chunk.usage_metadata.prompt_token_count
                            )
                        if hasattr(chunk.usage_metadata, "candidates_token_count"):
                            total_completion_tokens += (
                                chunk.usage_metadata.candidates_token_count
                            )

                    yield {
                        "content": chunk.text,
                        "model": model,
                    }

            # Yield final chunk with usage info if we collected any
            if total_prompt_tokens > 0 or total_completion_tokens > 0:
                yield {
                    "content": "",
                    "usage": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens,
                    },
                    "finish_reason": "stop",
                }

        except Exception as e:
            raise RuntimeError(f"Google Generative AI error: {str(e)}")
