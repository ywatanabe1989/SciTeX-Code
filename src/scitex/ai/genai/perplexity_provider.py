#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/genai/perplexity_provider.py

"""Perplexity AI provider implementation using the new component-based architecture.

This module provides integration with Perplexity's API using an OpenAI-compatible interface.
Perplexity offers access to various Llama and Mixtral models with online search capabilities.
"""

import os
from typing import Dict, List, Iterator, Optional, Any
import openai
from openai import OpenAI

from .base_provider import BaseProvider, ProviderConfig


class PerplexityProvider(BaseProvider):
    """Perplexity AI provider implementation."""

    SUPPORTED_MODELS = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-huge-128k-online",
        "llama-3.1-sonar-small-128k-chat",
        "llama-3.1-sonar-large-128k-chat",
        "llama-3-sonar-small-32k-chat",
        "llama-3-sonar-small-32k-online",
        "llama-3-sonar-large-32k-chat",
        "llama-3-sonar-large-32k-online",
        "llama-3-8b-instruct",
        "llama-3-70b-instruct",
        "mixtral-8x7b-instruct",
    ]

    DEFAULT_MODEL = "llama-3.1-sonar-small-128k-online"

    def __init__(self, config: ProviderConfig):
        """Initialize Perplexity provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.api_key = config.api_key or os.getenv("PERPLEXITY_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Perplexity API key not provided. Set PERPLEXITY_API_KEY environment variable or pass api_key."
            )

        # Initialize OpenAI client with Perplexity endpoint
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")

        # Set default max_tokens based on model if not provided
        if self.config.max_tokens is None:
            if "128k" in (config.model or self.DEFAULT_MODEL):
                self.config.max_tokens = 128_000
            else:
                self.config.max_tokens = 32_000

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
            if msg["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Invalid role: {msg['role']}")

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for Perplexity API.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted messages
        """
        formatted = []

        # Add system prompt if configured
        if self.config.system_prompt:
            formatted.append({"role": "system", "content": self.config.system_prompt})

        # Add user messages
        formatted.extend(messages)

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
        params = {
            "model": self.config.model or self.DEFAULT_MODEL,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False,
        }
        params.update(kwargs)

        try:
            response = self.client.chat.completions.create(**params)

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }
        except Exception as e:
            raise RuntimeError(f"Perplexity API error: {str(e)}")

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

        # Merge config parameters with kwargs
        params = {
            "model": self.config.model or self.DEFAULT_MODEL,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True,
        }
        params.update(kwargs)

        try:
            stream = self.client.chat.completions.create(**params)

            for chunk in stream:
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield {
                            "content": content,
                            "model": (
                                chunk.model
                                if hasattr(chunk, "model")
                                else params["model"]
                            ),
                        }

                # Check for usage in final chunk
                if hasattr(chunk, "usage") and chunk.usage:
                    yield {
                        "content": "",
                        "usage": {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        },
                        "finish_reason": (
                            chunk.choices[0].finish_reason if chunk.choices else None
                        ),
                    }
                elif chunk.choices and chunk.choices[0].finish_reason == "stop":
                    # Handle case where usage might be in a stop chunk
                    yield {
                        "content": "",
                        "finish_reason": "stop",
                    }

        except Exception as e:
            raise RuntimeError(f"Perplexity API error: {str(e)}")
