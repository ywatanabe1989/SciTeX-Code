#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 23:02:31 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/ai/_gen_ai/test__Anthropic.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/ai/_gen_ai/test__Anthropic.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-06-01 14:20:00 (ywatanabe)"

"""Tests for scitex.ai._gen_ai._Anthropic module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
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
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-api-key"}):
            yield

    def test_init_with_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                assert anthropic_ai.api_key == "test-api-key"
                assert anthropic_ai.model == "claude-3-opus-20240229"
                assert anthropic_ai.provider == "Anthropic"

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicitly provided API key."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(
                    api_key="explicit-key", model="claude-3-opus-20240229"
                )
                assert anthropic_ai.api_key == "explicit-key"

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
                with pytest.raises(
                    ValueError,
                    match="ANTHROPIC_API_KEY environment variable not set",
                ):
                    Anthropic(model="claude-3-opus-20240229")

    def test_init_client(self, mock_env_api_key):
        """Test client initialization."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch("anthropic.Anthropic") as mock_anthropic_class:
                mock_client = Mock()
                mock_anthropic_class.return_value = mock_client

                anthropic_ai = Anthropic(model="claude-3-opus-20240229")

                mock_anthropic_class.assert_called_once_with(
                    api_key="test-api-key"
                )
                assert anthropic_ai.client == mock_client

    def test_max_tokens_for_sonnet_model(self, mock_env_api_key):
        """Test that Claude 3.7 Sonnet model gets higher max tokens."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-7-sonnet-2025-0219")
                assert anthropic_ai.max_tokens == 128_000

    def test_api_format_history_text_only(self, mock_env_api_key):
        """Test formatting history with text-only messages."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")

                history = [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"},
                ]

                formatted = anthropic_ai._api_format_history(history)
                assert len(formatted) == 2
                assert formatted[0]["role"] == "user"
                assert formatted[0]["content"] == "Hello"

    def test_api_format_history_with_images(self, mock_env_api_key):
        """Test formatting history with image content."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")

                history = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What's this?"},
                            {"type": "_image", "_image": "base64data"},
                        ],
                    }
                ]

                formatted = anthropic_ai._api_format_history(history)
                assert len(formatted) == 1
                assert len(formatted[0]["content"]) == 2
                assert formatted[0]["content"][0]["type"] == "text"
                assert formatted[0]["content"][1]["type"] == "image"
                assert (
                    formatted[0]["content"][1]["source"]["data"]
                    == "base64data"
                )

    def test_api_call_static(self, mock_env_api_key, mock_anthropic_client):
        """Test static API call."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                Anthropic, "_init_client", return_value=mock_anthropic_client
            ):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229", stream=False
                )
                anthropic_ai.history = [{"role": "user", "content": "Test"}]

                result = anthropic_ai._api_call_static()

                assert result == "Test response"
                assert anthropic_ai.input_tokens == 10
                assert anthropic_ai.output_tokens == 20

                mock_anthropic_client.messages.create.assert_called_once_with(
                    model="claude-3-opus-20240229",
                    max_tokens=100_000,
                    messages=anthropic_ai.history,
                    temperature=1.0,
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

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                Anthropic, "_init_client", return_value=mock_client
            ):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229", stream=True
                )
                anthropic_ai.history = [{"role": "user", "content": "Test"}]

                result = list(anthropic_ai._api_call_stream())

                assert result == ["Hello", " world"]
                assert anthropic_ai.input_tokens == 5
                assert anthropic_ai.output_tokens == 10

    def test_temperature_setting(
        self, mock_env_api_key, mock_anthropic_client
    ):
        """Test temperature parameter is passed correctly."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(
                Anthropic, "_init_client", return_value=mock_anthropic_client
            ):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229", temperature=0.5
                )
                anthropic_ai.history = [{"role": "user", "content": "Test"}]
                anthropic_ai._api_call_static()

                # Check temperature was passed
                call_kwargs = mock_anthropic_client.messages.create.call_args[
                    1
                ]
                assert call_kwargs["temperature"] == 0.5

    def test_model_validation(self, mock_env_api_key):
        """Test model validation through parent class."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ["claude-3-opus-20240229"]

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                # Should not raise error for valid model
                anthropic_ai = Anthropic(model="claude-3-opus-20240229")
                assert anthropic_ai.model == "claude-3-opus-20240229"

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_api_key, stream):
        """Test stream parameter handling."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229", stream=stream
                )
                assert anthropic_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_api_key):
        """Test n_keep parameter for history management."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", MagicMock()):
            with patch.object(Anthropic, "_init_client", return_value=Mock()):
                anthropic_ai = Anthropic(
                    model="claude-3-opus-20240229", n_keep=5
                )
                assert anthropic_ai.n_keep == 5

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_Anthropic.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-24 19:20:24 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Anthropic.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/ai/_gen_ai/_Anthropic.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# """
# Functionality:
#     - Implements Anthropic AI (Claude) interface
#     - Handles both streaming and static text generation
# Input:
#     - User prompts and chat history
#     - Model configurations and API credentials
# Output:
#     - Generated text responses from Claude models
#     - Token usage statistics
# Prerequisites:
#     - Anthropic API key (ANTHROPIC_API_KEY environment variable)
#     - anthropic package
# """
# 
# """Imports"""
# import sys
# from typing import Dict, Generator, List, Optional
# 
# import anthropic
# import matplotlib.pyplot as plt
# 
# from ._BaseGenAI import BaseGenAI
# 
# """Functions & Classes"""
# class Anthropic(BaseGenAI):
#     def __init__(
#         self,
#         system_setting: str = "",
#         api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY"),
#         model: str = "claude-3-opus-20240229",
#         stream: bool = False,
#         seed: Optional[int] = None,
#         n_keep: int = 1,
#         temperature: float = 1.0,
#         chat_history: Optional[List[Dict[str, str]]] = None,
#         max_tokens: int = 100_000,
#     ) -> None:
# 
#         if model == "claude-3-7-sonnet-2025-0219":
#             max_tokens = 128_000
# 
#         api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
# 
#         if not api_key:
#             raise ValueError("ANTHROPIC_API_KEY environment variable not set")
# 
#         super().__init__(
#             system_setting=system_setting,
#             model=model,
#             api_key=api_key,
#             stream=stream,
#             n_keep=n_keep,
#             temperature=temperature,
#             provider="Anthropic",
#             chat_history=chat_history,
#             max_tokens=max_tokens,
#         )
# 
#     def _init_client(self) -> anthropic.Anthropic:
#         return anthropic.Anthropic(api_key=self.api_key)
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
#                                 "type": "image",
#                                 "source": {
#                                     "type": "base64",
#                                     "media_type": "image/jpeg",
#                                     "data": item["_image"],
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
#     def _api_call_static(self) -> str:
#         output = self.client.messages.create(
#             model=self.model,
#             max_tokens=self.max_tokens,
#             messages=self.history,
#             temperature=self.temperature,
#         )
#         out_text = output.content[0].text
# 
#         self.input_tokens += output.usage.input_tokens
#         self.output_tokens += output.usage.output_tokens
# 
#         return out_text
# 
#     def _api_call_stream(self) -> Generator[str, None, None]:
#         with self.client.messages.stream(
#             model=self.model,
#             max_tokens=self.max_tokens,
#             messages=self.history,
#             temperature=self.temperature,
#         ) as stream:
#             for chunk in stream:
#                 try:
#                     self.input_tokens += chunk.message.usage.input_tokens
#                     self.output_tokens += chunk.message.usage.output_tokens
#                 except AttributeError:
#                     pass
# 
#                 if chunk.type == "content_block_delta":
#                     yield chunk.delta.text
# 
# 
# def main() -> None:
#     import scitex
# 
#     ai = scitex.ai.GenAI(
#         model="claude-3-5-sonnet-20241022",
#         api_key=os.getenv("ANTHROPIC_API_KEY"),
#         n_keep=10,
#     )
#     print(ai("hi"))
#     print(ai("My name is Yusuke"))
#     print(ai("do you remember my name?"))
# 
#     print(
#         ai(
#             "hi, could you tell me what is in the pic?",
#             images=[
#                 "/home/ywatanabe/Downloads/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#             ],
#         )
#     )
#     pass
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys, plt, verbose=False
#     )
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# 
# """
# python src/scitex/ai/_gen_ai/_Anthropic.py
# python -m src.scitex.ai._gen_ai._Anthropic
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_Anthropic.py
# --------------------------------------------------------------------------------
