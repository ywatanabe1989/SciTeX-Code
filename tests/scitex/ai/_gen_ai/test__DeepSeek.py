#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 23:04:12 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/ai/_gen_ai/test__DeepSeek.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/ai/_gen_ai/test__DeepSeek.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2025-06-01 14:30:00 (ywatanabe)"

"""Tests for scitex.ai._gen_ai._DeepSeek module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from scitex.ai._gen_ai import DeepSeek


class TestDeepSeek:
    """Test suite for DeepSeek class."""

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
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-api-key"}):
            yield

    def test_init_with_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                deepseek_ai = DeepSeek(model="deepseek-chat")
                assert deepseek_ai.api_key == "test-api-key"
                assert deepseek_ai.model == "deepseek-chat"
                assert deepseek_ai.provider == "DeepSeek"
                assert deepseek_ai.max_tokens == 4096  # default

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicitly provided API key."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                deepseek_ai = DeepSeek(
                    api_key="explicit-key", model="deepseek-chat"
                )
                assert deepseek_ai.api_key == "explicit-key"

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
                with pytest.raises(
                    ValueError,
                    match="DEEPSEEK_API_KEY environment variable not set",
                ):
                    DeepSeek(model="deepseek-chat")

    def test_init_client(self, mock_env_api_key):
        """Test client initialization with DeepSeek API endpoint."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch(
                "scitex.ai._gen_ai._DeepSeek._OpenAI"
            ) as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client

                deepseek_ai = DeepSeek(model="deepseek-chat")

                # Check that OpenAI client is initialized with DeepSeek endpoint
                mock_openai_class.assert_called_once_with(
                    api_key="test-api-key",
                    base_url="https://api.deepseek.com/beta",
                )
                assert deepseek_ai.client == mock_client

    def test_api_call_static(self, mock_env_api_key, mock_openai_client):
        """Test static API call."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                DeepSeek, "_init_client", return_value=mock_openai_client
            ):
                deepseek_ai = DeepSeek(model="deepseek-chat", stream=False)
                deepseek_ai.history = [{"role": "user", "content": "Test"}]

                result = deepseek_ai._api_call_static()

                assert result == "Test response"
                assert deepseek_ai.input_tokens == 10
                assert deepseek_ai.output_tokens == 20

                mock_openai_client.chat.completions.create.assert_called_once()
                call_kwargs = (
                    mock_openai_client.chat.completions.create.call_args[1]
                )
                assert call_kwargs["model"] == "deepseek-chat"
                assert call_kwargs["temperature"] == 1.0
                assert call_kwargs["max_tokens"] == 4096
                assert call_kwargs["stream"] == False

    def test_api_call_stream(self, mock_env_api_key):
        """Test streaming API call."""
        mock_client = Mock()

        # Mock stream chunks
        chunks = [
            Mock(
                choices=[Mock(delta=Mock(content="Hello"))],
                usage=Mock(prompt_tokens=5, completion_tokens=0),
            ),
            Mock(
                choices=[Mock(delta=Mock(content=" world"))],
                usage=Mock(prompt_tokens=0, completion_tokens=10),
            ),
            Mock(choices=[Mock(delta=Mock(content="!"))], usage=None),
        ]

        # Set up side effects for attribute access
        for chunk in chunks:
            if chunk.usage:
                chunk.usage.prompt_tokens = getattr(
                    chunk.usage, "prompt_tokens", 0
                )
                chunk.usage.completion_tokens = getattr(
                    chunk.usage, "completion_tokens", 0
                )

        mock_client.chat.completions.create.return_value = iter(chunks)

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                DeepSeek, "_init_client", return_value=mock_client
            ):
                deepseek_ai = DeepSeek(model="deepseek-chat", stream=True)
                deepseek_ai.history = [{"role": "user", "content": "Test"}]

                result = list(deepseek_ai._api_call_stream())

                # Should yield complete sentences/words at punctuation
                assert len(result) >= 2  # At least "Hello " and "world!"
                assert "".join(result) == "Hello world!"

    def test_temperature_setting(self, mock_env_api_key, mock_openai_client):
        """Test temperature parameter is passed correctly."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                DeepSeek, "_init_client", return_value=mock_openai_client
            ):
                deepseek_ai = DeepSeek(model="deepseek-chat", temperature=0.5)
                deepseek_ai.history = [{"role": "user", "content": "Test"}]
                deepseek_ai._api_call_static()

                # Check temperature was passed
                call_kwargs = (
                    mock_openai_client.chat.completions.create.call_args[1]
                )
                assert call_kwargs["temperature"] == 0.5

    def test_seed_parameter(self, mock_env_api_key, mock_openai_client):
        """Test seed parameter is passed correctly."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                DeepSeek, "_init_client", return_value=mock_openai_client
            ):
                deepseek_ai = DeepSeek(model="deepseek-chat", seed=42)
                deepseek_ai.history = [{"role": "user", "content": "Test"}]
                deepseek_ai._api_call_static()

                # Check seed was passed
                call_kwargs = (
                    mock_openai_client.chat.completions.create.call_args[1]
                )
                assert call_kwargs["seed"] == 42

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_api_key, stream):
        """Test stream parameter handling."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                deepseek_ai = DeepSeek(model="deepseek-chat", stream=stream)
                assert deepseek_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_api_key):
        """Test n_keep parameter for history management."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                deepseek_ai = DeepSeek(model="deepseek-chat", n_keep=5)
                assert deepseek_ai.n_keep == 5

    def test_custom_max_tokens(self, mock_env_api_key):
        """Test custom max_tokens override."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                deepseek_ai = DeepSeek(model="deepseek-chat", max_tokens=8192)
                assert deepseek_ai.max_tokens == 8192  # Custom value

    def test_system_setting(self, mock_env_api_key):
        """Test system setting initialization."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                system_msg = "You are a helpful coding assistant"
                deepseek_ai = DeepSeek(
                    model="deepseek-chat", system_setting=system_msg
                )
                assert deepseek_ai.system_setting == system_msg

    def test_chat_history_parameter(self, mock_env_api_key):
        """Test chat_history parameter initialization."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                history = [{"role": "user", "content": "Previous message"}]
                deepseek_ai = DeepSeek(
                    model="deepseek-chat", chat_history=history
                )
                assert deepseek_ai.chat_history == history

    def test_default_model(self, mock_env_api_key):
        """Test default model is deepseek-chat."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(DeepSeek, "_init_client", return_value=Mock()):
                deepseek_ai = DeepSeek(api_key="test-key")
                assert deepseek_ai.model == "deepseek-chat"

    def test_Exception_handling_in_stream(self, mock_env_api_key):
        """Test Exception handling in streaming mode."""
        mock_client = Mock()

        # Mock chunks with Exception
        def chunk_generator():
            yield Mock(choices=[Mock(delta=Mock(content="Part"))], usage=None)
            raise Exception("Stream error")

        mock_client.chat.completions.create.return_value = chunk_generator()

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                DeepSeek, "_init_client", return_value=mock_client
            ):
                deepseek_ai = DeepSeek(model="deepseek-chat", stream=True)
                deepseek_ai.history = [{"role": "user", "content": "Test"}]

                # Should raise the Exception
                with pytest.raises(Exception, match="Stream error"):
                    list(deepseek_ai._api_call_stream())

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_DeepSeek.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-08 20:33:49 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_gen_ai/_DeepSeek.py
# 
# """
# 1. Functionality:
#    - Implements DeepSeek Code LLM API interface
# 2. Input:
#    - Text prompts for code generation
# 3. Output:
#    - Generated code responses (streaming or static)
# 4. Prerequisites:
#    - DEEPSEEK_API_KEY environment variable
#    - requests library
# """
# 
# """Imports"""
# import json
# import os
# import sys
# from typing import Dict, Generator, List, Optional
# 
# import scitex
# import requests
# 
# from ._BaseGenAI import BaseGenAI
# 
# """Warnings"""
# # scitex.pd.ignore_SettingWithCopyWarning()
# # warnings.simplefilter("ignore", UserWarning)
# # with warnings.catch_warnings():
# #     warnings.simplefilter("ignore", UserWarning)
# 
# """Parameters"""
# # from scitex.io import load_configs
# # CONFIG = load_configs()
# 
# """Functions & Classes"""
# from openai import OpenAI as _OpenAI
# 
# """Functions & Classes"""
# 
# 
# class DeepSeek(BaseGenAI):
#     def __init__(
#         self,
#         system_setting="",
#         model="deepseek-chat",
#         api_key="",
#         stream=False,
#         seed=None,
#         n_keep=1,
#         temperature=1.0,
#         chat_history=None,
#         max_tokens=4096,
#     ):
#         super().__init__(
#             system_setting=system_setting,
#             model=model,
#             api_key=api_key,
#             stream=stream,
#             n_keep=n_keep,
#             temperature=temperature,
#             provider="DeepSeek",
#             chat_history=chat_history,
#             max_tokens=max_tokens,
#         )
# 
#     def _init_client(self):
#         # client = _OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
#         client = _OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/beta")
# 
#         return client
# 
#     def _api_call_static(self):
#         kwargs = dict(
#             model=self.model,
#             messages=self.history,
#             seed=self.seed,
#             stream=False,
#             temperature=self.temperature,
#             max_tokens=self.max_tokens,
#         )
# 
#         output = self.client.chat.completions.create(**kwargs)
#         self.input_tokens += output.usage.prompt_tokens
#         self.output_tokens += output.usage.completion_tokens
# 
#         out_text = output.choices[0].message.content
# 
#         return out_text
# 
#     def _api_call_stream(self):
#         kwargs = dict(
#             model=self.model,
#             messages=self.history,
#             max_tokens=self.max_tokens,
#             n=1,
#             stream=self.stream,
#             seed=self.seed,
#             temperature=self.temperature,
#         )
# 
#         stream = self.client.chat.completions.create(**kwargs)
#         buffer = ""
# 
#         for chunk in stream:
#             if chunk:
#                 try:
#                     self.input_tokens += chunk.usage.prompt_tokens
#                 except:
#                     pass
#                 try:
#                     self.output_tokens += chunk.usage.completion_tokens
#                 except:
#                     pass
# 
#                 try:
#                     current_text = chunk.choices[0].delta.content
#                     if current_text:
#                         buffer += current_text
#                         if any(char in ".!?\n " for char in current_text):
#                             yield buffer
#                             buffer = ""
#                 except Exception as e:
#                     pass
# 
#         if buffer:
#             yield buffer
# 
# 
# if __name__ == "__main__":
#     # -----------------------------------
#     # Initiatialization of scitex format
#     # -----------------------------------
#     import sys
# 
#     import matplotlib.pyplot as plt
# 
#     # Configurations
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys,
#         plt,
#         verbose=False,
#         agg=True,
#         # sdir_suffix="",
#     )
# 
#     # # Argument parser
#     # script_mode = scitex.gen.is_script()
#     # import argparse
#     # parser = argparse.ArgumentParser(description='')
#     # parser.add_argument('--var', '-v', type=int, choices=None, default=1, help='(default: %%(default)s)')
#     # parser.add_argument('--flag', '-f', action='store_true', default=False, help='(default: %%(default)s)')
#     # args = parser.parse_args()
#     # scitex.gen.print_block(args, c='yellow')
# 
#     # -----------------------------------
#     # Main
#     # -----------------------------------
#     def main():
#         # Example usage
#         client = DeepSeek()
#         prompt = "Hello, how can I help you?"
#         response = client.complete(prompt)
#         print(response)
#         return 0
#     
#     exit_status = main()
# 
#     # -----------------------------------
#     # Cleanup scitex format
#     # -----------------------------------
#     scitex.gen.close(
#         CONFIG,
#         verbose=False,
#         notify=False,
#         message="",
#         exit_status=exit_status,
#     )
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_DeepSeek.py
# --------------------------------------------------------------------------------
