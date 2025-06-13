#!/usr/bin/env python3
"""Mock provider implementation for tests."""

from typing import Any, Dict, List, Generator
from scitex.ai.genai.base_provider import BaseProvider


class TestMockProvider(BaseProvider):
    """Complete mock provider for testing."""

    def __init__(self, config):
        self.config = config
        self.client = None

    def init_client(self) -> Any:
        """Initialize mock client."""
        self.client = {"mock": True}
        return self.client

    def format_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format history for provider."""
        return history

    def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        """Make static API call."""
        return {
            "choices": [
                {
                    "message": {"content": "Mock response", "role": "assistant"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    def call_stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[str, None, None]:
        """Make streaming API call."""
        yield "Mock "
        yield "streaming "
        yield "response"

    def complete(self, messages):
        """Complete method for compatibility."""
        return self.call_static(messages)

    def stream(self, messages):
        """Stream method for compatibility."""
        return self.call_stream(messages)

    def count_tokens(self, text):
        """Count tokens."""
        return len(text) // 4

    @property
    def supports_images(self) -> bool:
        return True

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def max_context_length(self) -> int:
        return 4096


## EOF
