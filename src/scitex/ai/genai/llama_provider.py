#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/genai/llama_provider.py

"""Llama provider implementation using the new component-based architecture.

This module provides integration with local Llama models through the official Llama library.
It supports loading and running Llama models locally with full control over model parameters.
"""

import os
from typing import Dict, List, Iterator, Optional, Any

try:
    from llama import Llama as _Llama
    from llama import Dialog
except ImportError:
    _Llama = None
    Dialog = None
    print(
        "Warning: llama package not installed. "
        "Install with the official Meta Llama repository instructions."
    )

from .base_provider import BaseProvider, ProviderConfig


class LlamaProvider(BaseProvider):
    """Llama provider implementation for local model inference."""

    SUPPORTED_MODELS = [
        "Meta-Llama-3-8B",
        "Meta-Llama-3-70B",
        "Meta-Llama-3.1-8B",
        "Meta-Llama-3.1-70B",
        "Meta-Llama-3.1-405B",
        "Llama-2-7b",
        "Llama-2-13b",
        "Llama-2-70b",
    ]

    DEFAULT_MODEL = "Meta-Llama-3-8B"

    def __init__(self, config: ProviderConfig):
        """Initialize Llama provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.model_name = config.model or self.DEFAULT_MODEL

        # Llama-specific configuration
        self.ckpt_dir = getattr(config, "ckpt_dir", None) or f"{self.model_name}/"
        self.tokenizer_path = (
            getattr(config, "tokenizer_path", None)
            or f"{self.model_name}/tokenizer.model"
        )
        self.max_seq_len = getattr(config, "max_seq_len", 32_768)
        self.max_batch_size = getattr(config, "max_batch_size", 4)
        self.max_gen_len = config.max_tokens

        # Configure environment variables for distributed inference
        self._setup_environment()

        # Initialize the Llama model
        if _Llama is None:
            raise ImportError(
                "Llama package is not installed. Please install it from the official Meta repository."
            )

        try:
            self.generator = _Llama.build(
                ckpt_dir=self.ckpt_dir,
                tokenizer_path=self.tokenizer_path,
                max_seq_len=self.max_seq_len,
                max_batch_size=self.max_batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Llama model: {str(e)}")

    def _setup_environment(self):
        """Set up environment variables for distributed inference."""
        env_vars = {
            "MASTER_ADDR": os.getenv("MASTER_ADDR", "localhost"),
            "MASTER_PORT": os.getenv("MASTER_PORT", "12355"),
            "WORLD_SIZE": os.getenv("WORLD_SIZE", "1"),
            "RANK": os.getenv("RANK", "0"),
        }

        for key, value in env_vars.items():
            os.environ[key] = value

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
        """Format messages for Llama API.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted messages for Llama
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

        # Convert to Llama Dialog format
        dialogs: List[Dialog] = [formatted_messages]

        # Merge config parameters with kwargs
        params = {
            "max_gen_len": self.max_gen_len,
            "temperature": self.config.temperature or 1.0,
            "top_p": kwargs.get("top_p", 0.9),
        }

        try:
            results = self.generator.chat_completion(dialogs, **params)

            result = results[0]
            content = result["generation"]["content"]

            # Estimate token counts (Llama doesn't provide exact counts)
            prompt_tokens = len(
                " ".join(msg["content"] for msg in formatted_messages).split()
            )
            completion_tokens = len(content.split())

            return {
                "content": content,
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                "finish_reason": "stop",
            }
        except Exception as e:
            raise RuntimeError(f"Llama inference error: {str(e)}")

    def stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """Stream a completion.

        Note: Llama doesn't have native streaming support, so this simulates streaming
        by yielding characters one at a time.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for the API

        Yields:
            Chunks of the completion
        """
        # Get the full response
        response = self.complete(messages, **kwargs)
        content = response["content"]

        # Simulate streaming by yielding characters
        for i, char in enumerate(content):
            yield {
                "content": char,
                "model": self.model_name,
            }

        # Yield final chunk with usage info
        yield {
            "content": "",
            "usage": response["usage"],
            "finish_reason": "stop",
        }
