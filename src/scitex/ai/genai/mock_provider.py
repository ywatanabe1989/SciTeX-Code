#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-15 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

"""
Mock provider for testing purposes.
"""

from typing import List, Dict, Any, Optional, Iterator, Generator
from .base_provider import BaseProvider, CompletionResponse, Provider
from .provider_factory import register_provider


class MockProvider(BaseProvider):
    """Mock provider for testing."""

    def __init__(self, config):
        """Initialize mock provider."""
        self.config = config
        self.api_key = config.api_key
        self.model = config.model or "mock-model"
        self.stream_mode = config.stream
        self.system_prompt = config.system_prompt
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.seed = config.seed
        self.n_draft = config.n_draft
        self.client = None  # Mock client

    def init_client(self) -> Any:
        """Initialize the mock client."""
        self.client = {"mock": True}  # Mock client object
        return self.client

    def format_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format conversation history."""
        # Mock implementation - just return as-is
        return history

    def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        """Make a static API call."""
        # Mock response
        content = f"Mock response to: {messages[-1]['content']}"
        return {
            "choices": [
                {
                    "message": {"content": content, "role": "assistant"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(content),
                "total_tokens": len(str(messages)) + len(content),
            },
        }

    def call_stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[str, None, None]:
        """Make a streaming API call."""
        response = f"Mock streaming response to: {messages[-1]['content']}"
        for word in response.split():
            yield word + " "

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> CompletionResponse:
        """Generate a mock completion."""
        # Ensure client is initialized
        if not self.client:
            self.init_client()

        # Format history
        formatted_messages = self.format_history(messages)

        # Make API call
        response = self.call_static(formatted_messages, **kwargs)

        # Extract content
        content = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})

        return CompletionResponse(
            content=content,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=response["choices"][0].get("finish_reason", "stop"),
            provider_response=response,
        )

    def stream(self, messages: List[Dict[str, Any]], **kwargs) -> Iterator[str]:
        """Stream mock completions."""
        # Ensure client is initialized
        if not self.client:
            self.init_client()

        # Format history
        formatted_messages = self.format_history(messages)

        # Stream response
        for chunk in self.call_stream(formatted_messages, **kwargs):
            yield chunk

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(text) // 4  # Mock implementation

    @property
    def supports_images(self) -> bool:
        """Check if provider supports images."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        return True

    @property
    def max_context_length(self) -> int:
        """Get maximum context length."""
        return 4096


# Auto-register when module is imported
register_provider(Provider.MOCK.value, MockProvider)

## EOF
