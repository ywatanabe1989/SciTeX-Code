#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 14:25:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__OpenAI.py

"""Tests for scitex.ai._gen_ai._OpenAI module."""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from scitex.ai._gen_ai import OpenAI


class TestOpenAI:
    """Test suite for OpenAI class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
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
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'}):
            yield

    def test_init_with_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(model="gpt-4")
                assert openai_ai.api_key == 'test-api-key'
                assert openai_ai.model == "gpt-4"
                assert openai_ai.provider == "OpenAI"
                assert openai_ai.max_tokens == 8_192  # gpt-4 default

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicitly provided API key."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(
                    api_key="explicit-key",
                    model="gpt-3.5-turbo"
                )
                assert openai_ai.api_key == "explicit-key"

    def test_init_client(self, mock_env_api_key):
        """Test client initialization."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch('scitex.ai._gen_ai._OpenAI._OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                
                openai_ai = OpenAI(model="gpt-4")
                
                mock_openai_class.assert_called_once_with(api_key='test-api-key')
                assert openai_ai.client == mock_client

    @pytest.mark.parametrize("model,expected_max_tokens", [
        ("gpt-4-turbo", 128_000),
        ("gpt-4", 8_192),
        ("gpt-3.5-turbo-16k", 16_384),
        ("gpt-3.5-turbo", 4_096),
        ("unknown-model", 4_096),  # default
    ])
    def test_max_tokens_by_model(self, mock_env_api_key, model, expected_max_tokens):
        """Test that different models get appropriate max tokens."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(model=model)
                assert openai_ai.max_tokens == expected_max_tokens

    def test_o1_model_initialization(self, mock_env_api_key):
        """Test initialization with o1 models and reasoning effort."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                # Test various o1 model formats
                for effort in ["low", "midium", "high"]:
                    openai_ai = OpenAI(model=f"o1-{effort}")
                    assert openai_ai.model == "o1"  # effort stripped
                    assert openai_ai.passed_model == f"o1-{effort}"

    def test_api_call_static(self, mock_env_api_key, mock_openai_client):
        """Test static API call."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=mock_openai_client):
                openai_ai = OpenAI(model="gpt-4", stream=False)
                openai_ai.history = [{"role": "user", "content": "Test"}]
                
                result = openai_ai._api_call_static()
                
                assert result == "Test response"
                assert openai_ai.input_tokens == 10
                assert openai_ai.output_tokens == 20
                
                mock_openai_client.chat.completions.create.assert_called_once()
                call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
                assert call_kwargs['model'] == "gpt-4"
                assert call_kwargs['temperature'] == 1.0
                assert call_kwargs['max_tokens'] == 8_192

    def test_api_call_static_o1_model(self, mock_env_api_key, mock_openai_client):
        """Test static API call with o1 model."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=mock_openai_client):
                openai_ai = OpenAI(model="o1-low", stream=False)
                openai_ai.history = [{"role": "user", "content": "Test"}]
                
                result = openai_ai._api_call_static()
                
                # Check that max_tokens was removed for o1 models
                call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
                assert 'max_tokens' not in call_kwargs
                assert call_kwargs['reasoning_effort'] == 'low'
                assert call_kwargs['model'] == 'o1'

    def test_api_call_stream(self, mock_env_api_key):
        """Test streaming API call."""
        mock_client = Mock()
        
        # Mock stream chunks
        chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))], usage=Mock(prompt_tokens=5, completion_tokens=0)),
            Mock(choices=[Mock(delta=Mock(content=" world"))], usage=Mock(prompt_tokens=0, completion_tokens=10)),
            Mock(choices=[Mock(delta=Mock(content="!"))], usage=None),
        ]
        
        # Set up side effects for attribute access
        for chunk in chunks:
            if chunk.usage:
                chunk.usage.prompt_tokens = getattr(chunk.usage, 'prompt_tokens', 0)
                chunk.usage.completion_tokens = getattr(chunk.usage, 'completion_tokens', 0)
        
        mock_client.chat.completions.create.return_value = iter(chunks)
        
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=mock_client):
                openai_ai = OpenAI(model="gpt-4", stream=True)
                openai_ai.history = [{"role": "user", "content": "Test"}]
                
                result = list(openai_ai._api_call_stream())
                
                # Should yield complete sentences/words at punctuation
                assert len(result) >= 2  # At least "Hello " and "world!"
                assert ''.join(result) == "Hello world!"

    def test_api_call_stream_o1_model(self, mock_env_api_key, mock_openai_client):
        """Test streaming API call with o1 model falls back to static."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=mock_openai_client):
                with patch.object(OpenAI, '_api_call_static', return_value="Full response") as mock_static:
                    openai_ai = OpenAI(model="o1-high", stream=True)
                    openai_ai.history = [{"role": "user", "content": "Test"}]
                    
                    result = list(openai_ai._api_call_stream())
                    
                    # Should call static method and stream character by character
                    mock_static.assert_called_once()
                    assert ''.join(result) == "Full response"

    def test_api_format_history_text_only(self, mock_env_api_key):
        """Test formatting history with text-only messages."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(model="gpt-4")
                
                history = [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ]
                
                formatted = openai_ai._api_format_history(history)
                assert len(formatted) == 2
                assert formatted[0]["role"] == "user"
                assert formatted[0]["content"] == "Hello"

    def test_api_format_history_with_images(self, mock_env_api_key):
        """Test formatting history with image content."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(model="gpt-4")
                
                history = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's this?"},
                        {"type": "_image", "_image": "base64data"}
                    ]
                }]
                
                formatted = openai_ai._api_format_history(history)
                assert len(formatted) == 1
                assert len(formatted[0]["content"]) == 2
                assert formatted[0]["content"][0]["type"] == "text"
                assert formatted[0]["content"][1]["type"] == "image_url"
                assert formatted[0]["content"][1]["image_url"]["url"] == "data:image/jpeg;base64,base64data"

    def test_temperature_setting(self, mock_env_api_key, mock_openai_client):
        """Test temperature parameter is passed correctly."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=mock_openai_client):
                openai_ai = OpenAI(
                    model="gpt-4",
                    temperature=0.5
                )
                openai_ai.history = [{"role": "user", "content": "Test"}]
                openai_ai._api_call_static()
                
                # Check temperature was passed
                call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
                assert call_kwargs['temperature'] == 0.5

    def test_seed_parameter(self, mock_env_api_key, mock_openai_client):
        """Test seed parameter is passed correctly."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=mock_openai_client):
                openai_ai = OpenAI(
                    model="gpt-4",
                    seed=42
                )
                openai_ai.history = [{"role": "user", "content": "Test"}]
                openai_ai._api_call_static()
                
                # Check seed was passed
                call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
                assert call_kwargs['seed'] == 42

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_api_key, stream):
        """Test stream parameter handling."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(
                    model="gpt-4",
                    stream=stream
                )
                assert openai_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_api_key):
        """Test n_keep parameter for history management."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(
                    model="gpt-4",
                    n_keep=5
                )
                assert openai_ai.n_keep == 5

    def test_custom_max_tokens(self, mock_env_api_key):
        """Test custom max_tokens override."""
        with patch('scitex.ai._gen_ai._OpenAI.MODELS', MagicMock()):
            with patch.object(OpenAI, '_init_client', return_value=Mock()):
                openai_ai = OpenAI(
                    model="gpt-4",
                    max_tokens=1000
                )
                assert openai_ai.max_tokens == 1000  # Custom value, not default 8192

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_OpenAI.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-01-22 01:21:11 (ywatanabe)"
# # File: _OpenAI.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_OpenAI.py"
# 
# 
# """Imports"""
# import os
# from openai import OpenAI as _OpenAI
# from ._BaseGenAI import BaseGenAI
# 
# """Functions & Classes"""
# 
# 
# class OpenAI(BaseGenAI):
#     def __init__(
#         self,
#         system_setting="",
#         model="",
#         api_key=os.getenv("OPENAI_API_KEY"),
#         stream=False,
#         seed=None,
#         n_keep=1,
#         temperature=1.0,
#         chat_history=None,
#         max_tokens=None,
#     ):
#         self.passed_model = model
# 
#         # import scitex
#         # scitex.str.print_debug()
#         # scitex.gen.printc(model)
# 
#         if model.startswith("o"):
#             for reasoning_effort in ["low", "midium", "high"]:
#                 model = model.replace(f"-{reasoning_effort}", "")
# 
#         # Set max_tokens based on model
#         if max_tokens is None:
#             if "gpt-4-turbo" in model:
#                 max_tokens = 128_000
#             elif "gpt-4" in model:
#                 max_tokens = 8_192
#             elif "gpt-3.5-turbo-16k" in model:
#                 max_tokens = 16_384
#             elif "gpt-3.5" in model:
#                 max_tokens = 4_096
#             else:
#                 max_tokens = 4_096
# 
#         super().__init__(
#             system_setting=system_setting,
#             model=model,
#             api_key=api_key,
#             stream=stream,
#             n_keep=n_keep,
#             temperature=temperature,
#             provider="OpenAI",
#             chat_history=chat_history,
#             max_tokens=max_tokens,
#         )
# 
#     def _init_client(
#         self,
#     ):
#         client = _OpenAI(api_key=self.api_key)
#         return client
# 
#     def _api_call_static(self):
#         kwargs = dict(
#             model=self.passed_model,
#             messages=self.history,
#             seed=self.seed,
#             stream=False,
#             temperature=self.temperature,
#             max_tokens=self.max_tokens,
#         )
# 
#         # # o models adjustment
#         # import scitex
#         # scitex.str.print_debug()
#         # scitex.gen.printc(kwargs.get("model"))
# 
#         if kwargs.get("model").startswith("o"):
#             kwargs.pop("max_tokens")
#             for reasoning_effort in ["low", "midium", "high"]:
#                 if reasoning_effort in kwargs["model"]:
#                     kwargs["reasoning_effort"] = reasoning_effort
#                     kwargs["model"] = kwargs["model"].replace(
#                         f"-{reasoning_effort}", ""
#                     )
#         # import scitex
#         # scitex.str.print_debug()
#         # scitex.gen.printc(kwargs.get("model"))
#         # scitex.gen.printc(kwargs.get("reasoning_effort"))
#         # scitex.str.print_debug()
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
#             stream_options={"include_usage": True},
#         )
# 
#         if kwargs.get("model").startswith("o"):
#             for reasoning_effort in ["low", "midium", "high"]:
#                 kwargs["reasoning_effort"] = reasoning_effort
#                 kwargs["model"] = kwargs["model"].replace(f"-{reasoning_effort}", "")
#             full_response = self._api_call_static()
#             for char in full_response:
#                 yield char
#             return
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
#                         # Yield complete sentences or words
#                         if any(char in ".!?\n " for char in current_text):
#                             yield buffer
#                             buffer = ""
#                 except Exception as e:
#                     pass
# 
#         # Yield any remaining text
#         if buffer:
#             yield buffer
# 
#     def _api_format_history(self, history):
#         formatted_history = []
#         for msg in history:
#             if isinstance(msg["content"], list):
#                 content = []
#                 for item in msg["content"]:
#                     if item["type"] == "text":
#                         content.append({"type": "text", "text": item["text"]})
#                     elif item["type"] == "_image":
#                         content.append(
#                             {
#                                 "type": "image_url",
#                                 "image_url": {
#                                     "url": f"data:image/jpeg;base64,{item['_image']}"
#                                 },
#                             }
#                         )
#                 formatted_msg = {"role": msg["role"], "content": content}
#             else:
#                 formatted_msg = {
#                     "role": msg["role"],
#                     "content": msg["content"],
#                 }
#             formatted_history.append(formatted_msg)
#         return formatted_history
# 
# 
# def main() -> None:
#     import scitex
# 
#     ai = scitex.ai.GenAI(
#         model="o1-low",
#         api_key=os.getenv("OPENAI_API_KEY"),
#     )
# 
#     print(ai("hi, could you tell me what is in the pic?"))
# 
#     # print(
#     #     ai(
#     #         "hi, could you tell me what is in the pic?",
#     #         images=[
#     #             "/home/ywatanabe/Downloads/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#     #         ],
#     #     )
#     # )
#     pass
# 
# 
# # def main():
# #     model = "o1-mini"
# #     # model = "o1-preview"
# #     # model = "gpt-4o"
# #     stream = True
# #     max_tokens = 4906
# #     m = scitex.ai.GenAI(model, stream=stream, max_tokens=max_tokens)
# #     m("hi")
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # EOF
# """
# python -m scitex.ai._gen_ai._OpenAI
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_OpenAI.py
# --------------------------------------------------------------------------------
