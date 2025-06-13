#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 20:25:55 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/genai/test_llama_provider.py

"""Test Llama provider implementation."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Iterator

from scitex.ai.genai.llama_provider import LlamaProvider
from scitex.ai.genai.provider_factory import ProviderConfig


class TestLlamaProvider:
    """Test suite for Llama provider."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = ProviderConfig(
            model="Meta-Llama-3-8B",
            temperature=0.7,
            max_tokens=512,
            timeout=30.0,
            max_retries=3,
            system_prompt="You are a helpful assistant.",
        )
        # Add Llama-specific attributes
        config.ckpt_dir = "/path/to/checkpoint"
        config.tokenizer_path = "/path/to/tokenizer.model"
        config.max_seq_len = 4096
        config.max_batch_size = 4
        return config

    @pytest.fixture
    def mock_llama(self):
        """Mock the Llama module."""
        with patch("scitex.ai.genai.llama_provider._Llama") as mock:
            # Mock the build method
            mock_generator = Mock()
            mock.build.return_value = mock_generator
            yield mock, mock_generator

    def test_init(self, config, mock_llama):
        """Test provider initialization."""
        mock_llama_class, mock_generator = mock_llama

        provider = LlamaProvider(config)

        assert provider.config == config
        assert provider.model_name == "Meta-Llama-3-8B"
        assert provider.ckpt_dir == "/path/to/checkpoint"
        assert provider.tokenizer_path == "/path/to/tokenizer.model"
        assert provider.max_seq_len == 4096
        assert provider.max_batch_size == 4
        assert provider.max_gen_len == 512

        # Verify Llama.build was called
        mock_llama_class.build.assert_called_once_with(
            ckpt_dir="/path/to/checkpoint",
            tokenizer_path="/path/to/tokenizer.model",
            max_seq_len=4096,
            max_batch_size=4,
        )

    def test_init_default_paths(self, mock_llama):
        """Test initialization with default model paths."""
        mock_llama_class, _ = mock_llama

        config = ProviderConfig(model="Meta-Llama-3-70B")
        provider = LlamaProvider(config)

        assert provider.ckpt_dir == "Meta-Llama-3-70B/"
        assert provider.tokenizer_path == "Meta-Llama-3-70B/tokenizer.model"

    def test_init_no_llama_package(self, config):
        """Test initialization when llama package is not installed."""
        with patch("scitex.ai.genai.llama_provider._Llama", None):
            with pytest.raises(ImportError, match="Llama package is not installed"):
                LlamaProvider(config)

    def test_environment_setup(self, config, mock_llama):
        """Test environment variable setup."""
        with patch.dict(os.environ, {}, clear=True):
            provider = LlamaProvider(config)

            assert os.environ["MASTER_ADDR"] == "localhost"
            assert os.environ["MASTER_PORT"] == "12355"
            assert os.environ["WORLD_SIZE"] == "1"
            assert os.environ["RANK"] == "0"

    def test_supported_models(self):
        """Test supported models list."""
        assert "Meta-Llama-3-8B" in LlamaProvider.SUPPORTED_MODELS
        assert "Meta-Llama-3-70B" in LlamaProvider.SUPPORTED_MODELS
        assert "Llama-2-7b" in LlamaProvider.SUPPORTED_MODELS

    def test_validate_messages_valid(self, config, mock_llama):
        """Test message validation with valid messages."""
        provider = LlamaProvider(config)

        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        # Should not raise
        provider.validate_messages(messages)

    def test_validate_messages_invalid_role(self, config, mock_llama):
        """Test message validation with invalid role."""
        provider = LlamaProvider(config)

        messages = [{"role": "invalid", "content": "Test"}]
        with pytest.raises(ValueError, match="Invalid role"):
            provider.validate_messages(messages)

    def test_format_messages(self, config, mock_llama):
        """Test message formatting."""
        provider = LlamaProvider(config)

        messages = [{"role": "user", "content": "Hello"}]
        formatted = provider.format_messages(messages)

        # Should include system prompt
        assert len(formatted) == 2
        assert formatted[0]["role"] == "system"
        assert formatted[0]["content"] == "You are a helpful assistant."
        assert formatted[1] == messages[0]

    def test_complete(self, config, mock_llama):
        """Test complete method."""
        _, mock_generator = mock_llama
        provider = LlamaProvider(config)

        # Mock the chat_completion response
        mock_generator.chat_completion.return_value = [
            {"generation": {"content": "Hello! I'm Llama, how can I help you?"}}
        ]

        # Test
        messages = [{"role": "user", "content": "Hello Llama"}]
        result = provider.complete(messages)

        assert result["content"] == "Hello! I'm Llama, how can I help you?"
        assert result["model"] == "Meta-Llama-3-8B"
        assert result["finish_reason"] == "stop"
        assert "usage" in result
        assert result["usage"]["prompt_tokens"] > 0
        assert result["usage"]["completion_tokens"] > 0

        # Verify chat_completion was called
        mock_generator.chat_completion.assert_called_once()
        call_args = mock_generator.chat_completion.call_args
        dialogs = call_args[0][0]
        assert len(dialogs) == 1
        assert len(dialogs[0]) == 2  # system + user message

    def test_stream(self, config, mock_llama):
        """Test stream method (simulated streaming)."""
        _, mock_generator = mock_llama
        provider = LlamaProvider(config)

        # Mock the chat_completion response
        mock_generator.chat_completion.return_value = [
            {"generation": {"content": "Hi!"}}
        ]

        # Test
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.stream(messages)

        # Verify it returns an iterator
        assert isinstance(result, Iterator)

        # Collect chunks
        chunks = list(result)
        # Should have one chunk per character plus final usage chunk
        assert len(chunks) == 4  # "H", "i", "!", usage
        assert chunks[0]["content"] == "H"
        assert chunks[1]["content"] == "i"
        assert chunks[2]["content"] == "!"
        assert chunks[3]["content"] == ""
        assert "usage" in chunks[3]

    def test_error_handling(self, config, mock_llama):
        """Test error handling in API calls."""
        _, mock_generator = mock_llama
        provider = LlamaProvider(config)

        # Mock inference error
        mock_generator.chat_completion.side_effect = Exception("Model error")

        # Test
        messages = [{"role": "user", "content": "Hello"}]
        with pytest.raises(RuntimeError, match="Llama inference error"):
            provider.complete(messages)

    def test_build_failure(self, config):
        """Test handling of model loading failure."""
        with patch("scitex.ai.genai.llama_provider._Llama") as mock_llama:
            mock_llama.build.side_effect = Exception("Failed to load checkpoint")

            with pytest.raises(RuntimeError, match="Failed to load Llama model"):
                LlamaProvider(config)

    def test_additional_kwargs(self, config, mock_llama):
        """Test that additional kwargs are passed through."""
        _, mock_generator = mock_llama
        provider = LlamaProvider(config)

        mock_generator.chat_completion.return_value = [
            {"generation": {"content": "Response"}}
        ]

        messages = [{"role": "user", "content": "Test"}]
        result = provider.complete(messages, top_p=0.95)

        # Verify top_p was passed
        call_kwargs = mock_generator.chat_completion.call_args[1]
        assert call_kwargs["top_p"] == 0.95
