#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/genai/test_deepseek_provider.py

"""Test DeepSeek provider implementation."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Iterator

from scitex.ai.genai.deepseek_provider import DeepSeekProvider
from scitex.ai.genai.provider_factory import ProviderConfig


class TestDeepSeekProvider:
    """Test suite for DeepSeek provider."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ProviderConfig(
            api_key="test-api-key",
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=100,
            timeout=30.0,
            max_retries=3,
            system_prompt="You are a helpful assistant.",
        )

    @pytest.fixture
    def provider(self, config):
        """Create test provider instance."""
        return DeepSeekProvider(config)

    def test_init(self, provider, config):
        """Test provider initialization."""
        assert provider.config == config
        assert provider.api_key == "test-api-key"
        assert provider.client is not None

    def test_init_with_env_key(self):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-api-key"}):
            config = ProviderConfig(model="deepseek-chat")
            provider = DeepSeekProvider(config)
            assert provider.api_key == "env-api-key"

    def test_supported_models(self):
        """Test supported models list."""
        assert "deepseek-chat" in DeepSeekProvider.SUPPORTED_MODELS
        assert "deepseek-coder" in DeepSeekProvider.SUPPORTED_MODELS

    def test_validate_messages_valid(self, provider):
        """Test message validation with valid messages."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        # Should not raise
        provider.validate_messages(messages)

    def test_validate_messages_invalid_role(self, provider):
        """Test message validation with invalid role."""
        messages = [{"role": "invalid", "content": "Test"}]
        with pytest.raises(ValueError, match="Invalid role"):
            provider.validate_messages(messages)

    def test_validate_messages_missing_content(self, provider):
        """Test message validation with missing content."""
        messages = [{"role": "user"}]
        with pytest.raises(ValueError, match="Missing content"):
            provider.validate_messages(messages)

    def test_format_messages(self, provider):
        """Test message formatting."""
        messages = [{"role": "user", "content": "Hello"}]
        formatted = provider.format_messages(messages)

        # Should include system prompt
        assert len(formatted) == 2
        assert formatted[0]["role"] == "system"
        assert formatted[0]["content"] == "You are a helpful assistant."
        assert formatted[1] == messages[0]

    def test_format_messages_no_system_prompt(self, config):
        """Test message formatting without system prompt."""
        config.system_prompt = None
        provider = DeepSeekProvider(config)

        messages = [{"role": "user", "content": "Hello"}]
        formatted = provider.format_messages(messages)

        assert formatted == messages

    @patch("openai.OpenAI")
    def test_complete(self, mock_openai_class, provider):
        """Test complete method."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Create new provider to use mocked client
        provider = DeepSeekProvider(provider.config)

        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
        mock_response.model = "deepseek-chat"

        mock_client.chat.completions.create.return_value = mock_response

        # Test
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.complete(messages)

        assert result["content"] == "Test response"
        assert result["usage"]["prompt_tokens"] == 10
        assert result["usage"]["completion_tokens"] == 20
        assert result["model"] == "deepseek-chat"

        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "deepseek-chat"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 100
        assert call_kwargs["stream"] is False

    @patch("openai.OpenAI")
    def test_stream(self, mock_openai_class, provider):
        """Test stream method."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Create new provider to use mocked client
        provider = DeepSeekProvider(provider.config)

        # Mock streaming response
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))], usage=None),
            Mock(choices=[Mock(delta=Mock(content=" world"))], usage=None),
            Mock(
                choices=[Mock(delta=Mock(content="!"))],
                usage=Mock(prompt_tokens=5, completion_tokens=3),
            ),
        ]

        mock_client.chat.completions.create.return_value = iter(mock_chunks)

        # Test
        messages = [{"role": "user", "content": "Hi"}]
        result = provider.stream(messages)

        # Verify it returns an iterator
        assert isinstance(result, Iterator)

        # Collect chunks
        chunks = list(result)
        assert len(chunks) == 3
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == " world"
        assert chunks[2]["content"] == "!"
        assert chunks[2]["usage"]["prompt_tokens"] == 5
        assert chunks[2]["usage"]["completion_tokens"] == 3

    @patch("openai.OpenAI")
    def test_error_handling(self, mock_openai_class, provider):
        """Test error handling in API calls."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Create new provider to use mocked client
        provider = DeepSeekProvider(provider.config)

        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Test
        messages = [{"role": "user", "content": "Hello"}]
        with pytest.raises(Exception, match="API Error"):
            provider.complete(messages)

    def test_client_initialization(self, config):
        """Test client is initialized with correct parameters."""
        with patch("openai.OpenAI") as mock_openai_class:
            provider = DeepSeekProvider(config)

            # Verify OpenAI client was initialized with correct params
            mock_openai_class.assert_called_once_with(
                api_key="test-api-key", base_url="https://api.deepseek.com/beta"
            )
