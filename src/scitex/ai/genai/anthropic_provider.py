#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/src/scitex/ai/genai/anthropic_provider.py

"""
Anthropic provider implementation for GenAI.
"""

from typing import List, Dict, Any, Optional, Generator
import logging

from .base_provider import BaseProvider, CompletionResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """
    Anthropic provider implementation.

    Supports Claude 3 models (Opus, Sonnet, Haiku).
    """

    SUPPORTED_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2",
    ]

    DEFAULT_MODEL = "claude-3-sonnet-20240229"

    def __init__(self, config):
        """Initialize Anthropic provider."""
        self.config = config
        self.api_key = config.api_key
        self.model = config.model or self.DEFAULT_MODEL
        self.kwargs = config.kwargs or {}

        # Import Anthropic client
        try:
            from anthropic import Anthropic as AnthropicClient

            self.client = AnthropicClient(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> CompletionResponse:
        """
        Generate completion using Anthropic API.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            CompletionResponse with generated text and usage info
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")

        # Format messages for Anthropic
        formatted_messages = self.format_messages(messages)

        # Extract system message if present
        system_message = None
        user_messages = []

        for msg in formatted_messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        # Add system message if present
        if system_message:
            api_params["system"] = system_message

        # Add optional parameters
        for param in ["temperature", "top_p", "top_k", "stop_sequences"]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        try:
            # Make API call
            response = self.client.messages.create(**api_params)

            # Extract content
            content = response.content[0].text if response.content else ""

            # Extract usage
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens
                + response.usage.output_tokens,
            }

            return CompletionResponse(content=content, usage=usage)

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for Anthropic API.

        Anthropic expects messages in the format::

            [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]

        System messages are passed separately.

        For images, the content should be a list::

            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}
                ]
            }
        """
        formatted_messages = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            images = msg.get("images", [])

            if images and self.model.startswith("claude-3"):
                # Format with images (only Claude 3 supports images)
                content_parts = [{"type": "text", "text": content}]

                for img in images:
                    if img.startswith("data:"):
                        # Extract base64 data
                        header, data = img.split(",", 1)
                        media_type = header.split(":")[1].split(";")[0]

                        content_parts.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": data,
                                },
                            }
                        )
                    else:
                        # URL images not directly supported, would need to download first
                        logger.warning("URL images not directly supported by Anthropic")

                formatted_messages.append({"role": role, "content": content_parts})
            else:
                # Regular text message
                formatted_messages.append({"role": role, "content": content})

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

        # Format messages for Anthropic
        formatted_messages = self.format_messages(messages)

        # Extract system message if present
        system_message = None
        user_messages = []

        for msg in formatted_messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
        }

        # Add system message if present
        if system_message:
            api_params["system"] = system_message

        # Add optional parameters
        for param in ["temperature", "top_p", "top_k", "stop_sequences"]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        try:
            # Make streaming API call
            full_content = ""
            prompt_tokens = 0
            completion_tokens = 0

            with self.client.messages.stream(**api_params) as stream:
                for text in stream.text_stream:
                    full_content += text
                    yield text

                # Get final message with usage info
                message = stream.get_final_message()
                if hasattr(message, "usage"):
                    prompt_tokens = message.usage.input_tokens
                    completion_tokens = message.usage.output_tokens

            # Return final response
            return CompletionResponse(
                content=full_content,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            )

        except Exception as e:
            logger.error(f"Anthropic streaming error: {str(e)}")
            raise

    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            # Anthropic uses its own tokenizer
            return self.client.count_tokens(text)
        except Exception:
            # Fallback: rough estimate (Claude tends to use fewer tokens than GPT)
            return len(text.split()) * 3 // 4

    @property
    def supports_images(self) -> bool:
        """Check if this provider/model supports image inputs."""
        # Only Claude 3 models support images
        return self.model.startswith("claude-3")

    @property
    def supports_streaming(self) -> bool:
        """Check if this provider/model supports streaming."""
        return True  # All Anthropic models support streaming

    @property
    def max_context_length(self) -> int:
        """Get maximum context length for this model."""
        context_lengths = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
        }
        return context_lengths.get(self.model, 100000)


# Auto-register when module is imported
from .base_provider import Provider
from .provider_factory import register_provider

register_provider(Provider.ANTHROPIC.value, AnthropicProvider)
