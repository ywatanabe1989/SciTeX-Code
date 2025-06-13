#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/tests/scitex/ai/genai/test_groq_provider.py

"""
Tests for Groq provider implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
import os

from scitex.ai.genai.groq_provider import GroqProvider
from scitex.ai.genai.base_provider import CompletionResponse
from scitex.ai.genai.provider_base import ProviderConfig


class TestGroqProvider:
    """Test Groq provider functionality."""

    @pytest.fixture
    def mock_groq_client(self):
        """Create a mock Groq client."""
        with patch("scitex.ai.genai.groq_provider.GroqClient") as mock:
            yield mock

    @pytest.fixture
    def groq_provider(self, mock_groq_client):
        """Create a Groq provider instance."""
        config = ProviderConfig(api_key="test-groq-key", model="llama3-8b-8192")
        return GroqProvider(config)

    def test_init_with_api_key(self, mock_groq_client):
        """Test initialization with API key."""
        config = ProviderConfig(api_key="test-key")
        provider = GroqProvider(config)

        assert provider.api_key == "test-key"
        assert provider.model == "llama3-8b-8192"  # Default
        mock_groq_client.assert_called_once_with(api_key="test-key")

    def test_init_from_environment(self, mock_groq_client):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "env-key"}):
            config = ProviderConfig()
            provider = GroqProvider(config)

            assert provider.api_key == "env-key"
            mock_groq_client.assert_called_once_with(api_key="env-key")

    def test_init_no_api_key(self, mock_groq_client):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = ProviderConfig()
            with pytest.raises(ValueError, match="GROQ_API_KEY not provided"):
                GroqProvider(config)

    def test_complete(self, groq_provider, mock_groq_client):
        """Test completion generation."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Test response from Llama"),
                finish_reason="stop",
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=15, completion_tokens=25, total_tokens=40
        )

        mock_groq_client.return_value.chat.completions.create.return_value = (
            mock_response
        )

        # Test completion
        messages = [{"role": "user", "content": "Hello, Llama!"}]
        response = groq_provider.complete(messages, temperature=0.7)

        # Verify response
        assert isinstance(response, CompletionResponse)
        assert response.content == "Test response from Llama"
        assert response.input_tokens == 15
        assert response.output_tokens == 25
        assert response.finish_reason == "stop"

        # Verify API call
        mock_groq_client.return_value.chat.completions.create.assert_called_once()
        call_args = mock_groq_client.return_value.chat.completions.create.call_args[1]
        assert call_args["model"] == "llama3-8b-8192"
        assert call_args["temperature"] == 0.7
        assert call_args["stream"] is False

    def test_complete_with_max_tokens(self, groq_provider, mock_groq_client):
        """Test that max_tokens is capped at 8000."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Response"), finish_reason="stop")
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )

        mock_groq_client.return_value.chat.completions.create.return_value = (
            mock_response
        )

        messages = [{"role": "user", "content": "Test"}]
        # Try to set max_tokens above limit
        response = groq_provider.complete(messages, max_tokens=10000)

        # Verify it was capped
        call_args = mock_groq_client.return_value.chat.completions.create.call_args[1]
        assert call_args["max_tokens"] == 8000

    def test_stream(self, groq_provider, mock_groq_client):
        """Test streaming completion."""
        # Mock streaming response
        mock_chunks = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" from"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" Llama"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=None))]),
        ]

        mock_groq_client.return_value.chat.completions.create.return_value = iter(
            mock_chunks
        )

        messages = [{"role": "user", "content": "Test streaming"}]

        # Collect streamed content
        chunks = []
        for chunk in groq_provider.stream(messages):
            chunks.append(chunk)

        # Verify chunks
        assert chunks == ["Hello", " from", " Llama"]

        # The generator should return a CompletionResponse at the end
        # Note: In the actual implementation, this would be handled differently

    def test_format_messages(self, groq_provider):
        """Test message formatting."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        formatted = groq_provider.format_messages(messages)

        # Groq uses same format as input
        assert formatted == messages

    def test_validate_messages(self, groq_provider):
        """Test message validation."""
        # Valid messages
        valid = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
        assert groq_provider.validate_messages(valid) is True

        # Empty messages
        assert groq_provider.validate_messages([]) is False

        # Invalid role
        invalid = [{"role": "invalid", "content": "Test"}]
        assert groq_provider.validate_messages(invalid) is False

        # Missing content
        invalid = [{"role": "user"}]
        assert groq_provider.validate_messages(invalid) is False

    def test_supports_images(self, groq_provider):
        """Test that Groq doesn't support images."""
        assert groq_provider.supports_images is False

    def test_supports_streaming(self, groq_provider):
        """Test that Groq supports streaming."""
        assert groq_provider.supports_streaming is True

    def test_max_context_length(self, groq_provider):
        """Test context length for different models."""
        # Default model
        assert groq_provider.max_context_length == 8192

        # Test different models
        groq_provider.model = "mixtral-8x7b-32768"
        assert groq_provider.max_context_length == 32768

        groq_provider.model = "llama2-70b-4096"
        assert groq_provider.max_context_length == 4096

        # Unknown model defaults to 8192
        groq_provider.model = "unknown-model"
        assert groq_provider.max_context_length == 8192

    def test_count_tokens(self, groq_provider):
        """Test token counting estimation."""
        text = "This is a test sentence with several words."
        # Should be roughly 8 words * 4/3 ≈ 10-11 tokens
        tokens = groq_provider.count_tokens(text)
        assert 8 <= tokens <= 12  # Allow some variance

    def test_api_error_handling(self, groq_provider, mock_groq_client):
        """Test API error handling."""
        # Mock an API error
        mock_groq_client.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(Exception, match="API Error"):
            groq_provider.complete(messages)

    def test_invalid_message_format(self, groq_provider):
        """Test handling of invalid message format."""
        invalid_messages = [{"invalid": "format"}]

        with pytest.raises(ValueError, match="Invalid message format"):
            groq_provider.complete(invalid_messages)
