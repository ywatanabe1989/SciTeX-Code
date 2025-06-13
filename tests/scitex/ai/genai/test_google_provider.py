#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/genai/test_google_provider.py

"""Test Google Generative AI provider implementation."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Iterator

from scitex.ai.genai.google_provider import GoogleProvider
from scitex.ai.genai.provider_factory import ProviderConfig


class TestGoogleProvider:
    """Test suite for Google provider."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ProviderConfig(
            api_key="test-api-key",
            model="gemini-1.5-pro-latest",
            temperature=0.7,
            max_tokens=None,  # Will be set to default
            timeout=30.0,
            max_retries=3,
            system_prompt="You are a helpful assistant.",
        )

    @pytest.fixture
    def provider(self, config):
        """Create test provider instance."""
        with patch("google.genai.Client"):
            return GoogleProvider(config)

    def test_init(self, config):
        """Test provider initialization."""
        with patch("google.genai.Client") as mock_client:
            provider = GoogleProvider(config)
            assert provider.config == config
            assert provider.api_key == "test-api-key"
            assert provider.client is not None
            # Should set default max_tokens
            assert provider.config.max_tokens == 32_768
            mock_client.assert_called_once_with(api_key="test-api-key")

    def test_init_with_env_key(self):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-api-key"}):
            with patch("google.genai.Client"):
                config = ProviderConfig(model="gemini-1.5-pro-latest")
                provider = GoogleProvider(config)
                assert provider.api_key == "env-api-key"

    def test_init_no_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            config = ProviderConfig(model="gemini-1.5-pro-latest")
            with pytest.raises(ValueError, match="Google API key not provided"):
                GoogleProvider(config)

    def test_supported_models(self):
        """Test supported models list."""
        assert "gemini-1.5-pro-latest" in GoogleProvider.SUPPORTED_MODELS
        assert "gemini-1.5-flash-latest" in GoogleProvider.SUPPORTED_MODELS
        assert "gemini-2.0-flash-exp" in GoogleProvider.SUPPORTED_MODELS

    def test_validate_messages_valid(self, provider):
        """Test message validation with valid messages."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "model", "content": "How can I help?"},
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
        """Test message formatting for Google API."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        formatted = provider.format_messages(messages)

        # Should include system prompt as user/model exchange
        assert len(formatted) == 4
        assert formatted[0]["role"] == "user"
        assert formatted[0]["parts"][0]["text"] == "You are a helpful assistant."
        assert formatted[1]["role"] == "model"
        assert formatted[2]["role"] == "user"
        assert formatted[2]["parts"][0]["text"] == "Hello"
        assert formatted[3]["role"] == "model"  # assistant -> model
        assert formatted[3]["parts"][0]["text"] == "Hi there!"

    def test_format_messages_no_system_prompt(self, config):
        """Test message formatting without system prompt."""
        config.system_prompt = None
        with patch("google.genai.Client"):
            provider = GoogleProvider(config)

        messages = [{"role": "user", "content": "Hello"}]
        formatted = provider.format_messages(messages)

        assert len(formatted) == 1
        assert formatted[0]["role"] == "user"
        assert formatted[0]["parts"][0]["text"] == "Hello"

    def test_format_messages_with_parts(self, provider):
        """Test formatting messages that already have parts."""
        messages = [{"role": "user", "parts": [{"text": "Hello"}]}]
        formatted = provider.format_messages(messages)

        # Skip system prompt for this test
        assert formatted[-1]["role"] == "user"
        assert formatted[-1]["parts"] == [{"text": "Hello"}]

    def test_complete(self, provider):
        """Test complete method."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini"
        mock_response.usage_metadata = Mock(
            prompt_token_count=10, candidates_token_count=20
        )

        provider.client.models.generate_content = Mock(return_value=mock_response)

        # Test
        messages = [{"role": "user", "content": "Hello Gemini"}]
        result = provider.complete(messages)

        assert result["content"] == "This is a test response from Gemini"
        assert result["usage"]["prompt_tokens"] == 10
        assert result["usage"]["completion_tokens"] == 20
        assert result["usage"]["total_tokens"] == 30
        assert result["model"] == "gemini-1.5-pro-latest"
        assert result["finish_reason"] == "stop"

        # Verify API call
        provider.client.models.generate_content.assert_called_once()
        call_args = provider.client.models.generate_content.call_args
        assert call_args[1]["model"] == "gemini-1.5-pro-latest"

    def test_stream(self, provider):
        """Test stream method."""
        # Mock streaming response
        mock_chunks = [
            Mock(text="Hello", usage_metadata=None),
            Mock(text=" from", usage_metadata=None),
            Mock(
                text=" Gemini!",
                usage_metadata=Mock(prompt_token_count=5, candidates_token_count=3),
            ),
        ]

        provider.client.models.generate_content_stream = Mock(
            return_value=iter(mock_chunks)
        )

        # Test
        messages = [{"role": "user", "content": "Hi"}]
        result = provider.stream(messages)

        # Verify it returns an iterator
        assert isinstance(result, Iterator)

        # Collect chunks
        chunks = list(result)
        assert len(chunks) == 4  # 3 content chunks + 1 usage chunk
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == " from"
        assert chunks[2]["content"] == " Gemini!"
        assert chunks[3]["content"] == ""
        assert chunks[3]["usage"]["prompt_tokens"] == 5
        assert chunks[3]["usage"]["completion_tokens"] == 3

    def test_error_handling(self, provider):
        """Test error handling in API calls."""
        # Mock API error
        provider.client.models.generate_content = Mock(
            side_effect=Exception("API Error")
        )

        # Test
        messages = [{"role": "user", "content": "Hello"}]
        with pytest.raises(RuntimeError, match="Google Generative AI error"):
            provider.complete(messages)

    def test_complete_without_usage_metadata(self, provider):
        """Test complete when response has no usage metadata."""
        # Mock response without usage metadata
        mock_response = Mock()
        mock_response.text = "Response without usage"
        mock_response.usage_metadata = None

        provider.client.models.generate_content = Mock(return_value=mock_response)

        # Test
        messages = [{"role": "user", "content": "Test"}]
        result = provider.complete(messages)

        assert result["content"] == "Response without usage"
        assert result["usage"] == {}

    def test_system_message_conversion(self, provider):
        """Test that system messages are converted to user messages."""
        messages = [
            {"role": "system", "content": "Additional context"},
            {"role": "user", "content": "Question"},
        ]
        formatted = provider.format_messages(messages)

        # Find the additional context message (after initial system prompt)
        context_msg = next(
            m for m in formatted if "Additional context" in m["parts"][0]["text"]
        )
        assert context_msg["role"] == "user"  # system -> user
