#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 14:45:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__Perplexity.py

"""Tests for scitex.ai._gen_ai._Perplexity module."""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from scitex.ai._gen_ai import Perplexity


class TestPerplexity:
    """Test suite for Perplexity class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI-compatible client."""
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
        with patch.dict(os.environ, {'PERPLEXITY_API_KEY': 'test-api-key'}):
            yield

    def test_init_with_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(model="llama-3.1-sonar-small-128k-online")
                assert perplexity_ai.api_key == 'test-api-key'
                assert perplexity_ai.model == "llama-3.1-sonar-small-128k-online"
                assert perplexity_ai.provider == "Perplexity"
                assert perplexity_ai.max_tokens == 128_000  # 128k model

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicitly provided API key."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(
                    api_key="explicit-key",
                    model="llama-3.1-sonar-small-128k-online"
                )
                assert perplexity_ai.api_key == "explicit-key"

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
                with pytest.raises(ValueError, match="PERPLEXITY_API_KEY environment variable not set"):
                    Perplexity(model="llama-3.1-sonar-small-128k-online")

    def test_init_client(self, mock_env_api_key):
        """Test client initialization with Perplexity API endpoint."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch('scitex.ai._gen_ai._Perplexity.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                
                perplexity_ai = Perplexity(model="llama-3.1-sonar-small-128k-online")
                
                # Check that OpenAI client is initialized with Perplexity endpoint
                mock_openai_class.assert_called_once_with(
                    api_key='test-api-key',
                    base_url="https://api.perplexity.ai"
                )
                assert perplexity_ai.client == mock_client

    @pytest.mark.parametrize("model,expected_max_tokens", [
        ("llama-3.1-sonar-small-128k-online", 128_000),
        ("llama-3.1-sonar-large-128k-online", 128_000),
        ("llama-3.1-sonar-huge-128k-online", 128_000),
        ("llama-3-sonar-small-32k-chat", 32_000),
        ("llama-3-sonar-large-32k-online", 32_000),
        ("mixtral-8x7b-instruct", 32_000),  # Default for non-128k
    ])
    def test_max_tokens_by_model(self, mock_env_api_key, model, expected_max_tokens):
        """Test that different models get appropriate max tokens."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(model=model)
                assert perplexity_ai.max_tokens == expected_max_tokens

    def test_api_call_static(self, mock_env_api_key, mock_openai_client):
        """Test static API call."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=mock_openai_client):
                perplexity_ai = Perplexity(model="llama-3.1-sonar-small-128k-online", stream=False)
                perplexity_ai.history = [{"role": "user", "content": "Test"}]
                
                # Mock print to suppress output during test
                with patch('builtins.print'):
                    result = perplexity_ai._api_call_static()
                
                assert result == "Test response"
                assert perplexity_ai.input_tokens == 10
                assert perplexity_ai.output_tokens == 20
                
                mock_openai_client.chat.completions.create.assert_called_once()
                call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
                assert call_kwargs['model'] == "llama-3.1-sonar-small-128k-online"
                assert call_kwargs['temperature'] == 1.0
                assert call_kwargs['max_tokens'] == 128_000
                assert call_kwargs['stream'] == False

    def test_api_call_stream(self, mock_env_api_key):
        """Test streaming API call."""
        mock_client = Mock()
        
        # Mock stream chunks with finish_reason
        chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"), finish_reason=None)], usage=None),
            Mock(choices=[Mock(delta=Mock(content=" world"), finish_reason=None)], usage=None),
            Mock(choices=[Mock(delta=Mock(content="!"), finish_reason="stop")], 
                 usage=Mock(prompt_tokens=5, completion_tokens=10)),
        ]
        
        # Set up message attribute for the chunk with finish_reason
        chunks[2].message = Mock(usage=Mock(input_tokens=5, output_tokens=10))
        
        mock_client.chat.completions.create.return_value = iter(chunks)
        
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=mock_client):
                perplexity_ai = Perplexity(model="llama-3.1-sonar-small-128k-online", stream=True)
                perplexity_ai.history = [{"role": "user", "content": "Test"}]
                
                # Mock print to suppress output during test
                with patch('builtins.print'):
                    result = list(perplexity_ai._api_call_stream())
                
                assert result == ["Hello", " world", "!"]
                # Token counts might be updated from the finish chunk

    def test_temperature_setting(self, mock_env_api_key, mock_openai_client):
        """Test temperature parameter is passed correctly."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=mock_openai_client):
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    temperature=0.5
                )
                perplexity_ai.history = [{"role": "user", "content": "Test"}]
                
                with patch('builtins.print'):
                    perplexity_ai._api_call_static()
                
                # Check temperature was passed
                call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
                assert call_kwargs['temperature'] == 0.5

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_api_key, stream):
        """Test stream parameter handling."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    stream=stream
                )
                assert perplexity_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_api_key):
        """Test n_keep parameter for history management."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    n_keep=5
                )
                assert perplexity_ai.n_keep == 5

    def test_seed_parameter(self, mock_env_api_key):
        """Test seed parameter initialization."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    seed=42
                )
                assert perplexity_ai.seed == 42

    def test_system_setting(self, mock_env_api_key):
        """Test system setting initialization."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                system_msg = "You are a helpful research assistant"
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    system_setting=system_msg
                )
                assert perplexity_ai.system_setting == system_msg

    def test_chat_history_parameter(self, mock_env_api_key):
        """Test chat_history parameter initialization."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                history = [{"role": "user", "content": "Previous message"}]
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    chat_history=history
                )
                assert perplexity_ai.chat_history == history

    def test_custom_max_tokens(self, mock_env_api_key):
        """Test custom max_tokens override."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    max_tokens=50000
                )
                assert perplexity_ai.max_tokens == 50000  # Custom value

    def test_get_available_models(self, mock_env_api_key):
        """Test _get_available_models method."""
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=Mock()):
                perplexity_ai = Perplexity(model="llama-3.1-sonar-small-128k-online")
                
                models = perplexity_ai._get_available_models()
                
                assert isinstance(models, list)
                assert "llama-3.1-sonar-small-128k-online" in models
                assert "llama-3.1-sonar-large-128k-online" in models
                assert "llama-3.1-sonar-huge-128k-online" in models
                assert "mixtral-8x7b-instruct" in models

    def test_empty_chunk_handling(self, mock_env_api_key):
        """Test handling of empty chunks in streaming."""
        mock_client = Mock()
        
        # Mock chunks with some empty content
        chunks = [
            Mock(choices=[Mock(delta=Mock(content="Start"), finish_reason=None)], usage=None),
            Mock(choices=[Mock(delta=Mock(content=""), finish_reason=None)], usage=None),
            Mock(choices=[Mock(delta=Mock(content=None), finish_reason=None)], usage=None),
            Mock(choices=[], usage=None),  # No choices
            Mock(choices=[Mock(delta=Mock(content="End"), finish_reason="stop")], usage=None),
        ]
        
        mock_client.chat.completions.create.return_value = iter(chunks)
        
        with patch('scitex.ai._gen_ai._Perplexity.MODELS', MagicMock()):
            with patch.object(Perplexity, '_init_client', return_value=mock_client):
                perplexity_ai = Perplexity(model="llama-3.1-sonar-small-128k-online", stream=True)
                perplexity_ai.history = [{"role": "user", "content": "Test"}]
                
                with patch('builtins.print'):
                    result = list(perplexity_ai._api_call_stream())
                
                # Should only yield non-empty content
                assert result == ["Start", "End"]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_Perplexity.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-11 04:11:10 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_gen_ai/_Perplexity.py
# 
# """
# Functionality:
#     - Implements Perplexity AI interface using OpenAI-compatible API
#     - Provides access to Llama and Mixtral models
# Input:
#     - User prompts and chat history
#     - Model configurations and API credentials
# Output:
#     - Generated text responses from Perplexity models
#     - Token usage statistics
# Prerequisites:
#     - Perplexity API key
#     - openai package
# """
# 
# """Imports"""
# import os
# import sys
# from pprint import pprint
# from typing import Dict, Generator, List, Optional
# 
# import matplotlib.pyplot as plt
# from openai import OpenAI
# 
# from ._BaseGenAI import BaseGenAI
# 
# """Functions & Classes"""
# 
# 
# class Perplexity(BaseGenAI):
#     def __init__(
#         self,
#         system_setting: str = "",
#         model: str = "",
#         api_key: str = "",
#         stream: bool = False,
#         seed: Optional[int] = None,
#         n_keep: int = 1,
#         temperature: float = 1.0,
#         chat_history: Optional[List[Dict[str, str]]] = None,
#         max_tokens: Optional[int] = None,  # Added parameter
#     ) -> None:
#         # Set max_tokens based on model if not provided
#         if max_tokens is None:
#             max_tokens = 128_000 if "128k" in model else 32_000
# 
#         super().__init__(
#             system_setting=system_setting,
#             model=model,
#             api_key=api_key,
#             stream=stream,
#             n_keep=n_keep,
#             temperature=temperature,
#             provider="Perplexity",
#             chat_history=chat_history,
#             max_tokens=max_tokens,
#         )
# 
#     def _init_client(self) -> OpenAI:
#         return OpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
#         # return OpenAI(
#         #     api_key=self.api_key, base_url="https://api.perplexity.ai/chat/completions"
#         # )
# 
#     def _api_call_static(self) -> str:
#         output = self.client.chat.completions.create(
#             model=self.model,
#             messages=self.history,
#             max_tokens=self.max_tokens,
#             stream=False,
#             temperature=self.temperature,
#         )
# 
#         print(output)
# 
#         out_text = output.choices[0].message.content
#         self.input_tokens += output.usage.prompt_tokens
#         self.output_tokens += output.usage.completion_tokens
# 
#         return out_text
# 
#     def _api_call_stream(self) -> Generator[str, None, None]:
#         stream = self.client.chat.completions.create(
#             model=self.model,
#             messages=self.history,
#             max_tokens=self.max_tokens,
#             n=1,
#             stream=self.stream,
#             temperature=self.temperature,
#         )
# 
#         for chunk in stream:
#             if chunk and chunk.choices[0].finish_reason == "stop":
#                 print(chunk.choices)
#                 try:
#                     self.input_tokens += chunk.usage.prompt_tokens
#                     self.output_tokens += chunk.usage.completion_tokens
#                 except AttributeError:
#                     pass
# 
#             if chunk.choices:
#                 current_text = chunk.choices[0].delta.content
#                 if current_text:
#                     yield current_text
# 
#     def _get_available_models(self) -> List[str]:
#         return [
#             "llama-3.1-sonar-small-128k-online",
#             "llama-3.1-sonar-large-128k-online",
#             "llama-3.1-sonar-huge-128k-online",
#             "llama-3.1-sonar-small-128k-chat",
#             "llama-3.1-sonar-large-128k-chat",
#             "llama-3-sonar-small-32k-chat",
#             "llama-3-sonar-small-32k-online",
#             "llama-3-sonar-large-32k-chat",
#             "llama-3-sonar-large-32k-online",
#             "llama-3-8b-instruct",
#             "llama-3-70b-instruct",
#             "mixtral-8x7b-instruct",
#         ]
# 
# 
# def main() -> None:
#     from ._genai_factory import genai_factory as GenAI
# 
#     models = [
#         "llama-3.1-sonar-small-128k-online",
#         "llama-3.1-sonar-large-128k-online",
#         "llama-3.1-sonar-huge-128k-online",
#     ]
#     ai = GenAI(model=models[0], api_key=os.getenv("PERPLEXITY_API_KEY"), stream=False)
#     out = ai("tell me about important citations for epilepsy prediction with citations")
#     print(out)
# 
# 
# def main():
#     import requests
# 
#     url = "https://api.perplexity.ai/chat/completions"
# 
#     payload = {
#         "model": "llama-3.1-sonar-small-128k-online",
#         "messages": [
#             {"role": "system", "content": "Be precise and concise."},
#             {
#                 "role": "user",
#                 "content": "tell me useful citations (scientific peer-reviewed papers) for epilepsy seizure prediction.",
#             },
#         ],
#         "max_tokens": 4096,
#         "temperature": 0.2,
#         "top_p": 0.9,
#         "search_domain_filter": ["perplexity.ai"],
#         "return_images": False,
#         "return_related_questions": False,
#         "search_recency_filter": "month",
#         "top_k": 0,
#         "stream": False,
#         "presence_penalty": 0,
#         "frequency_penalty": 1,
#     }
#     api_key = os.getenv("PERPLEXITY_API_KEY")
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json",
#     }
# 
#     response = requests.request("POST", url, json=payload, headers=headers)
# 
#     pprint(response.json()["citations"])
#     # pprint(response["citations"])
# 
#     # print(response.url)
#     # print(response.links)
#     # print(dir(response))
#     # print(response.text["citations"])
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_Perplexity.py
# --------------------------------------------------------------------------------
