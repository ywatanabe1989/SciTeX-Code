#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/src/scitex/ai/genai/groq_provider.py

"""
Groq provider implementation for GenAI.

Provides access to Groq's API with models like Llama, Mixtral, etc.
"""

from typing import List, Dict, Any, Optional, Generator
import logging
import os

from .base_provider import BaseProvider, CompletionResponse, Provider
from .provider_factory import register_provider

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    """
    Groq provider implementation.

    Supports Llama 3, Mixtral, and other models available through Groq.
    """

    SUPPORTED_MODELS = [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "llama2-70b-4096",
        "mixtral-8x7b-32768",
        "gemma-7b-it",
    ]

    DEFAULT_MODEL = "llama3-8b-8192"

    def __init__(self, config):
        """Initialize Groq provider."""
        self.config = config
        self.api_key = config.api_key or os.getenv("GROQ_API_KEY")
        self.model = config.model or self.DEFAULT_MODEL
        self.kwargs = config.kwargs or {}

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided and not found in environment")

        # Import Groq client
        try:
            from groq import Groq as GroqClient

            self.client = GroqClient(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Groq package not installed. Install with: pip install groq"
            )

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> CompletionResponse:
        """
        Generate completion using Groq API.

        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            CompletionResponse with generated text and usage info
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")

        # Format messages for Groq (same as OpenAI format)
        formatted_messages = self.format_messages(messages)

        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,
        }

        # Add optional parameters
        for param in ["temperature", "max_tokens", "top_p", "stop", "seed"]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        # Groq has a max token limit of 8000
        if "max_tokens" in api_params:
            api_params["max_tokens"] = min(api_params["max_tokens"], 8000)

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
            logger.error(f"Groq API error: {str(e)}")
            raise

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for Groq API.

        Groq uses the same message format as OpenAI.
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

        # Format messages for Groq
        formatted_messages = self.format_messages(messages)

        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
        }

        # Add optional parameters
        for param in ["temperature", "max_tokens", "top_p", "stop", "seed"]:
            if param in kwargs:
                api_params[param] = kwargs[param]

        # Groq has a max token limit of 8000
        if "max_tokens" in api_params:
            api_params["max_tokens"] = min(api_params["max_tokens"], 8000)

        try:
            # Make streaming API call
            stream = self.client.chat.completions.create(**api_params)

            # Track content
            full_content = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield content

            # Estimate tokens for streaming (Groq doesn't provide usage in stream)
            input_tokens = self.count_tokens(str(formatted_messages))
            output_tokens = self.count_tokens(full_content)

            # Return final response
            return CompletionResponse(
                content=full_content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"Groq streaming error: {str(e)}")
            raise

    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens (estimated)
        """
        # Groq doesn't provide a token counter, so estimate
        # Llama tokenization is roughly similar to GPT
        return len(text.split()) * 4 // 3

    @property
    def supports_images(self) -> bool:
        """Check if this provider/model supports image inputs."""
        # Groq doesn't currently support multimodal inputs
        return False

    @property
    def supports_streaming(self) -> bool:
        """Check if this provider/model supports streaming."""
        return True

    @property
    def max_context_length(self) -> int:
        """Get maximum context length for this model."""
        context_lengths = {
            "llama3-8b-8192": 8192,
            "llama3-70b-8192": 8192,
            "llama2-70b-4096": 4096,
            "mixtral-8x7b-32768": 32768,
            "gemma-7b-it": 8192,
        }
        return context_lengths.get(self.model, 8192)


# Auto-register when module is imported
register_provider(Provider.GROQ.value, GroqProvider)
