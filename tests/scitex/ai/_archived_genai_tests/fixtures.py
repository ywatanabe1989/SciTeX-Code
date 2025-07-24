#!/usr/bin/env python3
"""Test fixtures for GenAI module tests."""

from typing import Dict, Any, List, Generator
from unittest.mock import Mock, MagicMock
import pytest


# Mock response objects for different providers
class MockAnthropicResponse:
    """Mock Anthropic API response."""

    def __init__(
        self,
        content: str = "Test response",
        input_tokens: int = 10,
        output_tokens: int = 20,
    ):
        self.content = [Mock(text=content)]
        self.usage = Mock(input_tokens=input_tokens, output_tokens=output_tokens)


class MockOpenAIResponse:
    """Mock OpenAI API response."""

    def __init__(
        self,
        content: str = "Test response",
        input_tokens: int = 10,
        output_tokens: int = 20,
    ):
        self.choices = [Mock(message=Mock(content=content), finish_reason="stop")]
        self.usage = Mock(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )


class MockGoogleResponse:
    """Mock Google API response."""

    def __init__(self, content: str = "Test response"):
        self.candidates = [Mock(content=Mock(parts=[Mock(text=content)]))]


# Mock streaming chunks
class MockAnthropicChunk:
    """Mock Anthropic streaming chunk."""

    def __init__(self, text: str):
        self.content_delta = Mock(text=text)
        self.type = "content_block_delta"


class MockOpenAIChunk:
    """Mock OpenAI streaming chunk."""

    def __init__(self, text: str):
        self.delta = Mock(content=text)
        self.choices = [Mock(delta=self.delta)]


# Fixtures
@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client."""
    client = MagicMock()

    # Configure messages.create for static calls
    client.messages.create.return_value = MockAnthropicResponse()

    # Configure messages.create for streaming
    def mock_stream(*args, **kwargs):
        if kwargs.get("stream", False):
            chunks = [
                MockAnthropicChunk("Hello"),
                MockAnthropicChunk(" world"),
                MockAnthropicChunk("!"),
            ]
            return iter(chunks)
        return MockAnthropicResponse()

    client.messages.create.side_effect = mock_stream

    return client


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    client = MagicMock()

    # Configure chat.completions.create
    client.chat.completions.create.return_value = MockOpenAIResponse()

    return client


@pytest.fixture
def mock_google_client():
    """Create a mock Google client."""
    client = MagicMock()

    # Configure generate_content
    client.generate_content.return_value = MockGoogleResponse()

    return client


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"},
        {"role": "user", "content": "What's the weather like?"},
    ]


@pytest.fixture
def sample_messages_with_images():
    """Sample messages with images for testing."""
    return [
        {
            "role": "user",
            "content": "What's in this image?",
            "images": ["base64encodedimagedata"],
        }
    ]


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-1234567890"


@pytest.fixture
def mock_env_vars(monkeypatch, mock_api_key):
    """Set mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", mock_api_key)
    monkeypatch.setenv("ANTHROPIC_API_KEY", mock_api_key)
    monkeypatch.setenv("GOOGLE_API_KEY", mock_api_key)
    monkeypatch.setenv("GROQ_API_KEY", mock_api_key)


@pytest.fixture
def mock_models_df():
    """Mock MODELS dataframe for testing."""
    import pandas as pd

    data = {
        "name": [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "gemini-pro",
            "gemini-pro-vision",
        ],
        "provider": ["openai", "openai", "anthropic", "anthropic", "google", "google"],
        "cost_1k_input_tokens": [0.01, 0.001, 0.015, 0.003, 0.001, 0.001],
        "cost_1k_output_tokens": [0.03, 0.002, 0.075, 0.015, 0.002, 0.002],
        "max_tokens": [8192, 4096, 4096, 4096, 32768, 32768],
        "supports_images": [True, False, True, True, False, True],
        "supports_streaming": [True, True, True, True, True, True],
        "api_key_env": [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_API_KEY",
        ],
    }

    return pd.DataFrame(data)


@pytest.fixture
def mock_cost_data():
    """Mock cost calculation data."""
    return {
        "provider": "openai",
        "model": "gpt-4",
        "input_tokens": 100,
        "output_tokens": 200,
        "expected_cost": 0.001 + 0.006,  # $0.007
    }
