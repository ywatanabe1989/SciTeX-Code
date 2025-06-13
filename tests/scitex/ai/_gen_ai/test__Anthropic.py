#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 14:20:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__Anthropic.py

"""Tests for scitex.ai._gen_ai._Anthropic module."""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from scitex.ai._gen_ai import Anthropic


class TestAnthropic:
    """Test suite for Anthropic class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_client.messages.create.return_value = mock_response
        return mock_client

    @pytest.fixture
    def mock_env_api_key(self):
        """Mock environment variable for API key."""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-api-key'}):
            yield

    def test_init_with_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                assert anthropic_ai.api_key == 'test-api-key'
                assert anthropic_ai.model == "claude-3-opus-20240229"
                assert anthropic_ai.provider == "Anthropic"

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicitly provided API key."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(
                    api_key="explicit-key",
                    model="claude-3-opus-20240229"
                )
                assert anthropic_ai.api_key == "explicit-key"

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
                with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable not set"):
                    Anthropic(model="claude-3-opus-20240229")

    def test_init_client(self, mock_env_api_key):
        """Test client initialization."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch('anthropic.Anthropic') as mock_anthropic_class:
                mock_client = Mock()
                mock_anthropic_class.return_value = mock_client
                
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                
                mock_anthropic_class.assert_called_once_with(api_key='test-api-key')
                assert anthropic_ai.client == mock_client

    def test_max_tokens_for_sonnet_model(self, mock_env_api_key):
        """Test that Claude 3.7 Sonnet model gets higher max tokens."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-7-sonnet-2025-0219")
                assert anthropic_ai.max_tokens == 128_000

    def test_api_format_history_text_only(self, mock_env_api_key):
        """Test formatting history with text-only messages."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                
                history = [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ]
                
                formatted = anthropic_ai._api_format_history(history)
                assert len(formatted) == 2
                assert formatted[0]["role"] == "user"
                assert formatted[0]["content"] == "Hello"

    def test_api_format_history_with_images(self, mock_env_api_key):
        """Test formatting history with image content."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                
                history = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's this?"},
                        {"type": "_image", "_image": "base64data"}
                    ]
                }]
                
                formatted = anthropic_ai._api_format_history(history)
                assert len(formatted) == 1
                assert len(formatted[0]["content"]) == 2
                assert formatted[0]["content"][0]["type"] == "text"
                assert formatted[0]["content"][1]["type"] == "image"
                assert formatted[0]["content"][1]["source"]["data"] == "base64data"

    def test_api_call_static(self, mock_env_api_key, mock_anthropic_client):
        """Test static API call."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=mock_anthropic_client):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229", stream=False)
                anthropic_ai.history = [{"role": "user", "content": "Test"}]
                
                result = anthropic_ai._api_call_static()
                
                assert result == "Test response"
                assert anthropic_ai.input_tokens == 10
                assert anthropic_ai.output_tokens == 20
                
                mock_anthropic_client.messages.create.assert_called_once_with(
                    model="claude-3-opus-20240229",
                    max_tokens=100_000,
                    messages=anthropic_ai.history,
                    temperature=1.0
                )

    def test_api_call_stream(self, mock_env_api_key):
        """Test streaming API call."""
        mock_client = Mock()
        mock_stream = MagicMock()
        
        # Mock stream chunks
        chunks = [
            Mock(type="content_block_delta", delta=Mock(text="Hello")),
            Mock(type="content_block_delta", delta=Mock(text=" world")),
        ]
        chunks[0].message.usage.input_tokens = 5
        chunks[0].message.usage.output_tokens = 10
        
        mock_stream.__enter__.return_value = iter(chunks)
        mock_stream.__exit__.return_value = None
        mock_client.messages.stream.return_value = mock_stream
        
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=mock_client):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229", stream=True)
                anthropic_ai.history = [{"role": "user", "content": "Test"}]
                
                result = list(anthropic_ai._api_call_stream())
                
                assert result == ["Hello", " world"]
                assert anthropic_ai.input_tokens == 5
                assert anthropic_ai.output_tokens == 10

    def test_temperature_setting(self, mock_env_api_key, mock_anthropic_client):
        """Test temperature parameter is passed correctly."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=mock_anthropic_client):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229",
                    temperature=0.5
                )
                anthropic_ai.history = [{"role": "user", "content": "Test"}]
                anthropic_ai._api_call_static()
                
                # Check temperature was passed
                call_kwargs = mock_anthropic_client.messages.create.call_args[1]
                assert call_kwargs['temperature'] == 0.5

    def test_model_validation(self, mock_env_api_key):
        """Test model validation through parent class."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ['claude-3-opus-20240229']
        
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', mock_models):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                # Should not raise error for valid model
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                assert anthropic_ai.model == "claude-3-opus-20240229"

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_api_key, stream):
        """Test stream parameter handling."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229",
                    stream=stream
                )
                assert anthropic_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_api_key):
        """Test n_keep parameter for history management."""
        with patch('scitex.ai._gen_ai._Anthropic.MODELS', MagicMock()):
            with patch.object(Anthropic, '_init_client', return_value=Mock()):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229",
                    n_keep=5
                )
                assert anthropic_ai.n_keep == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
