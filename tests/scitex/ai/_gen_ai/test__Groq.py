#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 14:35:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__Groq.py

"""Tests for scitex.ai._gen_ai._Groq module."""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from scitex.ai._gen_ai import Groq


class TestGroq:
    """Test suite for Groq class."""

    @pytest.fixture
    def mock_groq_client(self):
        """Create a mock Groq client."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    @pytest.fixture
    def mock_env_api_key(self):
        """Mock environment variable for API key."""
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-api-key'}):
            yield

    def test_init_with_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(model="llama3-8b-8192")
                assert groq_ai.api_key == 'test-api-key'
                assert groq_ai.model == "llama3-8b-8192"
                assert groq_ai.provider == "Groq"
                assert groq_ai.max_tokens == 8000  # min(8000, 8000)
                assert groq_ai.temperature == 0.5  # default

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicitly provided API key."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(
                    api_key="explicit-key",
                    model="llama3-8b-8192"
                )
                assert groq_ai.api_key == "explicit-key"

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
                with pytest.raises(ValueError, match="GROQ_API_KEY environment variable not set"):
                    Groq(model="llama3-8b-8192")

    def test_init_client(self, mock_env_api_key):
        """Test client initialization."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch('scitex.ai._gen_ai._Groq._Groq') as mock_groq_class:
                mock_client = Mock()
                mock_groq_class.return_value = mock_client
                
                groq_ai = Groq(model="llama3-8b-8192")
                
                mock_groq_class.assert_called_once_with(api_key='test-api-key')
                assert groq_ai.client == mock_client

    def test_max_tokens_limit(self, mock_env_api_key):
        """Test that max_tokens is limited to 8000."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                # Test with value over 8000
                groq_ai = Groq(model="llama3-8b-8192", max_tokens=10000)
                assert groq_ai.max_tokens == 8000  # Should be capped at 8000
                
                # Test with value under 8000
                groq_ai = Groq(model="llama3-8b-8192", max_tokens=5000)
                assert groq_ai.max_tokens == 5000

    def test_api_call_static(self, mock_env_api_key, mock_groq_client):
        """Test static API call."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=mock_groq_client):
                groq_ai = Groq(model="llama3-8b-8192", stream=False)
                groq_ai.history = [{"role": "user", "content": "Test"}]
                
                result = groq_ai._api_call_static()
                
                assert result == "Test response"
                assert groq_ai.input_tokens == 10
                assert groq_ai.output_tokens == 20
                
                mock_groq_client.chat.completions.create.assert_called_once()
                call_kwargs = mock_groq_client.chat.completions.create.call_args[1]
                assert call_kwargs['model'] == "llama3-8b-8192"
                assert call_kwargs['temperature'] == 0.5
                assert call_kwargs['max_tokens'] == 8000
                assert call_kwargs['stream'] == False

    def test_api_call_stream(self, mock_env_api_key):
        """Test streaming API call."""
        mock_client = Mock()
        
        # Mock stream chunks
        chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))]),
            Mock(choices=[Mock(delta=Mock(content=" world"))]),
            Mock(choices=[Mock(delta=Mock(content=None))]),  # Empty chunk
            Mock(choices=[Mock(delta=Mock(content="!"))]),
        ]
        
        mock_client.chat.completions.create.return_value = iter(chunks)
        
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=mock_client):
                groq_ai = Groq(model="llama3-8b-8192", stream=True)
                groq_ai.history = [{"role": "user", "content": "Test"}]
                
                result = list(groq_ai._api_call_stream())
                
                # Should yield only non-empty chunks
                assert result == ["Hello", " world", "!"]

    def test_temperature_setting(self, mock_env_api_key, mock_groq_client):
        """Test temperature parameter is passed correctly."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=mock_groq_client):
                groq_ai = Groq(
                    model="llama3-8b-8192",
                    temperature=0.8
                )
                groq_ai.history = [{"role": "user", "content": "Test"}]
                groq_ai._api_call_static()
                
                # Check temperature was passed
                call_kwargs = mock_groq_client.chat.completions.create.call_args[1]
                assert call_kwargs['temperature'] == 0.8

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_api_key, stream):
        """Test stream parameter handling."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(
                    model="llama3-8b-8192",
                    stream=stream
                )
                assert groq_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_api_key):
        """Test n_keep parameter for history management."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(
                    model="llama3-8b-8192",
                    n_keep=5
                )
                assert groq_ai.n_keep == 5

    def test_seed_parameter(self, mock_env_api_key):
        """Test seed parameter initialization."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(
                    model="llama3-8b-8192",
                    seed=42
                )
                assert groq_ai.seed == 42

    def test_system_setting(self, mock_env_api_key):
        """Test system setting initialization."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                system_msg = "You are a helpful assistant"
                groq_ai = Groq(
                    model="llama3-8b-8192",
                    system_setting=system_msg
                )
                assert groq_ai.system_setting == system_msg

    def test_chat_history_parameter(self, mock_env_api_key):
        """Test chat_history parameter initialization."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                history = [{"role": "user", "content": "Previous message"}]
                groq_ai = Groq(
                    model="llama3-8b-8192",
                    chat_history=history
                )
                assert groq_ai.chat_history == history

    def test_default_model(self, mock_env_api_key):
        """Test default model is llama3-8b-8192."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(api_key="test-key")
                assert groq_ai.model == "llama3-8b-8192"

    def test_streaming_empty_chunks(self, mock_env_api_key):
        """Test streaming handles empty chunks correctly."""
        mock_client = Mock()
        
        # Mock chunks with some empty content
        chunks = [
            Mock(choices=[Mock(delta=Mock(content="Start"))]),
            Mock(choices=[Mock(delta=Mock(content=""))]),  # Empty string
            Mock(choices=[Mock(delta=Mock(content=None))]),  # None
            Mock(choices=[]),  # No choices
            Mock(choices=[Mock(delta=Mock(content="End"))]),
        ]
        
        mock_client.chat.completions.create.return_value = iter(chunks)
        
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=mock_client):
                groq_ai = Groq(model="llama3-8b-8192", stream=True)
                groq_ai.history = [{"role": "user", "content": "Test"}]
                
                result = list(groq_ai._api_call_stream())
                
                # Should only yield non-empty content
                assert result == ["Start", "End"]

    @pytest.mark.parametrize("model", [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
    ])
    def test_different_models(self, mock_env_api_key, model):
        """Test initialization with different Groq models."""
        with patch('scitex.ai._gen_ai._Groq.MODELS', MagicMock()):
            with patch.object(Groq, '_init_client', return_value=Mock()):
                groq_ai = Groq(model=model)
                assert groq_ai.model == model

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_Groq.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-28 02:47:54 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_gen_ai/_Groq.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Groq.py"
# 
# """
# Functionality:
#     - Implements GLOQ AI interface
#     - Handles both streaming and static text generation
# Input:
#     - User prompts and chat history
#     - Model configurations and API credentials
# Output:
#     - Generated text responses
#     - Token usage statistics
# Prerequisites:
#     - GLOQ API key (GLOQ_API_KEY environment variable)
#     - gloq package
# """
# 
# """Imports"""
# import os
# import sys
# from typing import Any, Dict, Generator, List, Optional, Union
# 
# from groq import Groq as _Groq
# import matplotlib.pyplot as plt
# 
# from ._BaseGenAI import BaseGenAI
# 
# """Functions & Classes"""
# 
# 
# class Groq(BaseGenAI):
#     def __init__(
#         self,
#         system_setting: str = "",
#         api_key: Optional[str] = os.getenv("GROQ_API_KEY"),
#         model: str = "llama3-8b-8192",
#         stream: bool = False,
#         seed: Optional[int] = None,
#         n_keep: int = 1,
#         temperature: float = 0.5,
#         chat_history: Optional[List[Dict[str, str]]] = None,
#         max_tokens: int = 8000,
#     ) -> None:
#         max_tokens = min(max_tokens, 8000)
#         if not api_key:
#             raise ValueError("GROQ_API_KEY environment variable not set")
# 
#         super().__init__(
#             system_setting=system_setting,
#             model=model,
#             api_key=api_key,
#             stream=stream,
#             n_keep=n_keep,
#             temperature=temperature,
#             provider="Groq",
#             chat_history=chat_history,
#             max_tokens=max_tokens,
#         )
# 
#     def _init_client(self) -> Any:
#         return _Groq(api_key=self.api_key)
# 
#     def _api_call_static(self) -> str:
#         output = self.client.chat.completions.create(
#             model=self.model,
#             messages=self.history,
#             temperature=self.temperature,
#             max_tokens=self.max_tokens,
#             stream=False,
#         )
#         out_text = output.choices[0].message.content
# 
#         self.input_tokens += output.usage.prompt_tokens
#         self.output_tokens += output.usage.completion_tokens
# 
#         return out_text
# 
#     def _api_call_stream(self) -> Generator[str, None, None]:
#         stream = self.client.chat.completions.create(
#             model=self.model,
#             messages=self.history,
#             temperature=self.temperature,
#             max_tokens=self.max_tokens,
#             stream=True,
#         )
# 
#         for chunk in stream:
#             if chunk.choices[0].delta.content:
#                 yield chunk.choices[0].delta.content
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_Groq.py
# --------------------------------------------------------------------------------
