#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/src/scitex/ai/genai/openai_provider.py

"""
OpenAI provider implementation for GenAI.
"""

from typing import List, Dict, Any, Optional, Generator
import logging

from .base_provider import BaseProvider, CompletionResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.

    Supports GPT-3.5, GPT-4, and other OpenAI models.
    """

    SUPPORTED_MODELS = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-4",
        "gpt-4-32k",
        "gpt-4-turbo-preview",
        "gpt-4-vision-preview",
        "gpt-4o",
        "gpt-4o-mini",
    ]

    DEFAULT_MODEL = "gpt-3.5-turbo"

    def __init__(self, config):
        """Initialize OpenAI provider."""
        self.config = config
        self.api_key = config.api_key
        self.model = config.model or self.DEFAULT_MODEL
        self.kwargs = config.kwargs or {}
        self.client = None

        # Initialize client
        self.init_client()

    def init_client(self) -> Any:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI as OpenAIClient

            self.client = OpenAIClient(api_key=self.api_key)
            return self.client
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

    def format_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format conversation history for OpenAI API."""
        # OpenAI uses the same format as our standard format
        return history

    def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        """Make a static API call to OpenAI."""
        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        # Add optional parameters
        for param in [
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "n",
            "logprobs",
        ]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        try:
            # Make API call
            response = self.client.chat.completions.create(**api_params)
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def call_stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[str, None, None]:
        """Make a streaming API call to OpenAI."""
        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        # Add optional parameters
        for param in [
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "n",
        ]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        try:
            # Make streaming API call
            stream = self.client.chat.completions.create(**api_params)

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming API error: {str(e)}")
            raise

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> CompletionResponse:
        """
        Generate completion using OpenAI API.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            CompletionResponse with generated text and usage info
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")

        # Format messages for OpenAI
        formatted_messages = self.format_messages(messages)

        # Use call_static for the actual API call
        response = self.call_static(formatted_messages, **kwargs)

        # Extract content and usage
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return CompletionResponse(
            content=content, input_tokens=input_tokens, output_tokens=output_tokens
        )

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for OpenAI API.

        OpenAI expects messages in the format::

            [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]

        For images, the content should be a list::

            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                ]
            }
        """
        formatted_messages = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            images = msg.get("images", [])

            if images and self.model in ["gpt-4-vision-preview", "gpt-4o"]:
                # Format with images
                content_parts = [{"type": "text", "text": content}]
                for img in images:
                    content_parts.append(
                        {"type": "image_url", "image_url": {"url": img}}
                    )
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
    ) -> Generator[str, None, None]:
        """Generate a streaming completion.

        Args:
            messages: List of messages in standard format
            **kwargs: Additional parameters

        Yields:
            Text chunks during streaming
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")

        # Format messages for OpenAI
        formatted_messages = self.format_messages(messages)

        # Use call_stream for the actual streaming
        yield from self.call_stream(formatted_messages, **kwargs)

    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            import tiktoken

            # Get the encoding for the model
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimate
            return len(text.split()) * 4 // 3

    @property
    def supports_images(self) -> bool:
        """Check if this provider/model supports image inputs."""
        return self.model in ["gpt-4-vision-preview", "gpt-4o", "gpt-4o-mini"]

    @property
    def supports_streaming(self) -> bool:
        """Check if this provider/model supports streaming."""
        return True  # All OpenAI chat models support streaming

    @property
    def max_context_length(self) -> int:
        """Get maximum context length for this model."""
        context_lengths = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo-preview": 128000,
            "gpt-4-vision-preview": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
        }
        return context_lengths.get(self.model, 4096)


# Auto-register when module is imported
from .base_provider import Provider
from .provider_factory import register_provider

register_provider(Provider.OPENAI.value, OpenAIProvider)
