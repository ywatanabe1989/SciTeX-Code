#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/genai/test_perplexity_provider.py

"""Test Perplexity provider implementation."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Iterator

from scitex.ai.genai.perplexity_provider import PerplexityProvider
from scitex.ai.genai.provider_factory import ProviderConfig


class TestPerplexityProvider:
    """Test suite for Perplexity provider."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ProviderConfig(
            api_key="test-api-key",
            model="llama-3.1-sonar-small-128k-online",
            temperature=0.7,
            max_tokens=None,  # Will be set based on model
            timeout=30.0,
            max_retries=3,
            system_prompt="Be precise and concise.",
        )

    @pytest.fixture
    def provider(self, config):
        """Create test provider instance."""
        return PerplexityProvider(config)

    def test_init(self, provider, config):
        """Test provider initialization."""
        assert provider.config == config
        assert provider.api_key == "test-api-key"
        assert provider.client is not None
        # Should set max_tokens based on model
        assert provider.config.max_tokens == 128_000  # 128k model

    def test_init_with_env_key(self):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "env-api-key"}):
            config = ProviderConfig(model="llama-3.1-sonar-small-128k-online")
            provider = PerplexityProvider(config)
            assert provider.api_key == "env-api-key"

    def test_init_32k_model(self):
        """Test max_tokens for 32k model."""
        config = ProviderConfig(
            api_key="test-key", model="llama-3-sonar-small-32k-chat"
        )
        provider = PerplexityProvider(config)
        assert provider.config.max_tokens == 32_000

    def test_supported_models(self):
        """Test supported models list."""
        assert (
            "llama-3.1-sonar-small-128k-online" in PerplexityProvider.SUPPORTED_MODELS
        )
        assert (
            "llama-3.1-sonar-large-128k-online" in PerplexityProvider.SUPPORTED_MODELS
        )
        assert "llama-3-70b-instruct" in PerplexityProvider.SUPPORTED_MODELS
        assert "mixtral-8x7b-instruct" in PerplexityProvider.SUPPORTED_MODELS

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
        messages = [{"role": "user", "content": "What is epilepsy?"}]
        formatted = provider.format_messages(messages)

        # Should include system prompt
        assert len(formatted) == 2
        assert formatted[0]["role"] == "system"
        assert formatted[0]["content"] == "Be precise and concise."
        assert formatted[1] == messages[0]

    def test_format_messages_no_system_prompt(self, config):
        """Test message formatting without system prompt."""
        config.system_prompt = None
        provider = PerplexityProvider(config)

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
        provider = PerplexityProvider(provider.config)

        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(content="Test response with citations"),
                finish_reason="stop",
            )
        ]
        mock_response.usage = Mock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )
        mock_response.model = "llama-3.1-sonar-small-128k-online"

        mock_client.chat.completions.create.return_value = mock_response

        # Test
        messages = [{"role": "user", "content": "Tell me about epilepsy"}]
        result = provider.complete(messages)

        assert result["content"] == "Test response with citations"
        assert result["usage"]["prompt_tokens"] == 10
        assert result["usage"]["completion_tokens"] == 20
        assert result["usage"]["total_tokens"] == 30
        assert result["model"] == "llama-3.1-sonar-small-128k-online"
        assert result["finish_reason"] == "stop"

        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "llama-3.1-sonar-small-128k-online"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 128_000
        assert call_kwargs["stream"] is False

    @patch("openai.OpenAI")
    def test_stream(self, mock_openai_class, provider):
        """Test stream method."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Create new provider to use mocked client
        provider = PerplexityProvider(provider.config)

        # Mock streaming response
        mock_chunks = [
            Mock(
                choices=[Mock(delta=Mock(content="Epilepsy is"), finish_reason=None)],
                usage=None,
                model="llama-3.1-sonar-small-128k-online",
            ),
            Mock(
                choices=[
                    Mock(delta=Mock(content=" a neurological"), finish_reason=None)
                ],
                usage=None,
            ),
            Mock(
                choices=[Mock(delta=Mock(content=" disorder."), finish_reason="stop")],
                usage=Mock(prompt_tokens=5, completion_tokens=5, total_tokens=10),
            ),
        ]

        mock_client.chat.completions.create.return_value = iter(mock_chunks)

        # Test
        messages = [{"role": "user", "content": "What is epilepsy?"}]
        result = provider.stream(messages)

        # Verify it returns an iterator
        assert isinstance(result, Iterator)

        # Collect chunks
        chunks = list(result)
        assert len(chunks) >= 3
        assert chunks[0]["content"] == "Epilepsy is"
        assert chunks[1]["content"] == " a neurological"
        assert chunks[2]["content"] == " disorder."

        # Find the chunk with usage info
        usage_chunk = next((c for c in chunks if "usage" in c), None)
        assert usage_chunk is not None
        assert usage_chunk["usage"]["prompt_tokens"] == 5
        assert usage_chunk["usage"]["completion_tokens"] == 5

    @patch("openai.OpenAI")
    def test_error_handling(self, mock_openai_class, provider):
        """Test error handling in API calls."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Create new provider to use mocked client
        provider = PerplexityProvider(provider.config)

        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Test
        messages = [{"role": "user", "content": "Hello"}]
        with pytest.raises(RuntimeError, match="Perplexity API error"):
            provider.complete(messages)

    def test_client_initialization(self, config):
        """Test client is initialized with correct parameters."""
        with patch("openai.OpenAI") as mock_openai_class:
            provider = PerplexityProvider(config)

            # Verify OpenAI client was initialized with correct params
            mock_openai_class.assert_called_once_with(
                api_key="test-api-key", base_url="https://api.perplexity.ai"
            )

    def test_additional_kwargs(self, provider):
        """Test that additional kwargs are passed through."""
        with patch.object(provider.client.chat.completions, "create") as mock_create:
            mock_response = Mock()
            mock_response.choices = [
                Mock(message=Mock(content="Response"), finish_reason="stop")
            ]
            mock_response.usage = Mock(
                prompt_tokens=5, completion_tokens=10, total_tokens=15
            )
            mock_response.model = "llama-3.1-sonar-small-128k-online"
            mock_create.return_value = mock_response

            messages = [{"role": "user", "content": "Test"}]
            # Perplexity-specific parameters
            result = provider.complete(
                messages,
                search_domain_filter=["perplexity.ai"],
                return_images=False,
                search_recency_filter="month",
            )

            # Verify additional params were passed
            call_kwargs = mock_create.call_args.kwargs
            assert "search_domain_filter" in call_kwargs
            assert "return_images" in call_kwargs
            assert "search_recency_filter" in call_kwargs
