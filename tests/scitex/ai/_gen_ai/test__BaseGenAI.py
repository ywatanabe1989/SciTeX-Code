#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 23:03:36 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/ai/_gen_ai/test__BaseGenAI.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/ai/_gen_ai/test__BaseGenAI.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2025-06-01 13:40:00 (ywatanabe)"

"""Tests for scitex.ai._gen_ai._BaseGenAI module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from scitex.ai._gen_ai import BaseGenAI


class ConcreteGenAI(BaseGenAI):
    """Concrete implementation of BaseGenAI for testing."""

    def _init_client(self):
        """Returns mock client."""
        return Mock()

    def _api_call_static(self):
        """Returns test text."""
        return "Test response"

    def _api_call_stream(self):
        """Returns test stream."""
        for chunk in ["Test", " ", "stream", " ", "response"]:
            yield chunk


class TestBaseGenAI:
    """Test suite for BaseGenAI abstract class."""

    @pytest.fixture
    def gen_ai(self):
        """Create a concrete instance for testing."""
        with patch(
            "scitex.ai._gen_ai._PARAMS.MODELS",
            {
                "name": ["test-model"],
                "provider": ["TestProvider"],
                "api_key_env": ["TEST_API_KEY"],
            },
        ):
            return ConcreteGenAI(
                model="test-model",
                api_key="test-key-1234",
                provider="TestProvider",
            )

    def test_initialization(self):
        """Test BaseGenAI initialization."""
        with patch(
            "scitex.ai._gen_ai._PARAMS.MODELS",
            {
                "name": ["test-model"],
                "provider": ["TestProvider"],
                "api_key_env": ["TEST_API_KEY"],
            },
        ):
            ai = ConcreteGenAI(
                system_setting="You are a helpful assistant",
                model="test-model",
                api_key="test-key",
                stream=True,
                seed=42,
                n_keep=5,
                temperature=0.7,
                provider="TestProvider",
                max_tokens=2048,
            )

            assert ai.system_setting == "You are a helpful assistant"
            assert ai.model == "test-model"
            assert ai.api_key == "test-key"
            assert ai.stream is True
            assert ai.seed == 42
            assert ai.n_keep == 5
            assert ai.temperature == 0.7
            assert ai.max_tokens == 2048
            assert ai.provider == "TestProvider"

    def test_masked_api_key(self, gen_ai):
        """Test API key masking."""
        assert gen_ai.masked_api_key == "test****1234"

    def test_list_models_all(self):
        """Test listing all available models."""
        mock_models = MagicMock()
        mock_models.name.tolist.return_value = ["model1", "model2", "model3"]
        mock_models.provider.tolist.return_value = [
            "Provider1",
            "Provider2",
            "Provider3",
        ]
        mock_models.__len__.return_value = 3

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            models = BaseGenAI.list_models()
            assert models == ["model1", "model2", "model3"]

    def test_list_models_by_provider(self):
        """Test listing models by specific provider."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ["model1", "model2"]
        mock_models.provider.tolist.return_value = [
            "TestProvider",
            "TestProvider",
        ]
        mock_models["api_key_env"] = ["TEST_API_KEY", "TEST_API_KEY"]

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            models = BaseGenAI.list_models(provider="TestProvider")
            assert len(models) == 2

    def test_reset(self, gen_ai):
        """Test resetting conversation history."""
        gen_ai.history = [{"role": "user", "content": "test"}]
        gen_ai.reset()
        assert gen_ai.history == []

        gen_ai.reset("New system setting")
        assert len(gen_ai.history) == 1
        assert gen_ai.history[0]["role"] == "system"
        assert gen_ai.history[0]["content"] == "New system setting"

    def test_update_history_text(self, gen_ai):
        """Test updating history with text content."""
        gen_ai.update_history("user", "Hello")
        assert len(gen_ai.history) == 1
        assert gen_ai.history[0]["role"] == "user"
        assert gen_ai.history[0]["content"] == "Hello"

    def test_update_history_with_images(self, gen_ai):
        """Test updating history with images."""
        with patch.object(
            gen_ai, "_ensure_base64_encoding", return_value="base64_image"
        ):
            gen_ai.update_history("user", "Look at this", images=["image.jpg"])

            assert len(gen_ai.history) == 1
            assert gen_ai.history[0]["role"] == "user"
            assert isinstance(gen_ai.history[0]["content"], list)
            assert gen_ai.history[0]["content"][0]["type"] == "text"
            assert gen_ai.history[0]["content"][1]["type"] == "_image"

    def test_ensure_alternative_history(self, gen_ai):
        """Test ensuring alternating roles in history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "user", "content": "Hi again"},
        ]
        result = gen_ai._ensure_alternative_history(history)
        assert len(result) == 1
        assert result[0]["content"] == "Hello\n\nHi again"

    def test_ensure_start_from_user(self):
        """Test ensuring history starts with user message."""
        history = [
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "Hello"},
        ]
        result = BaseGenAI._ensure_start_from_user(history)
        assert len(result) == 1
        assert result[0]["role"] == "user"

    def test_call_static_mode(self, gen_ai):
        """Test calling in static (non-streaming) mode."""
        gen_ai.stream = False
        result = gen_ai("Test prompt")
        assert result == "Test response"
        assert len(gen_ai.history) == 2  # user + assistant

    def test_call_stream_mode(self, gen_ai):
        """Test calling in streaming mode."""
        gen_ai.stream = True
        result = gen_ai("Test prompt")
        assert result == "Test stream response"

    def test_call_with_prompt_file(self, gen_ai):
        """Test calling with prompt from file."""
        with patch(
            "scitex.ai._gen_ai._BaseGenAI.load",
            return_value=["Line 1", "Line 2"],
        ):
            gen_ai.stream = False
            result = gen_ai(prompt_file="test.txt")
            assert result == "Test response"

    def test_call_empty_prompt(self, gen_ai):
        """Test calling with empty prompt."""
        result = gen_ai("")
        assert result is None

    def test_verify_model_valid(self):
        """Test model verification with valid model."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ["test-model"]

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            ai = ConcreteGenAI(
                model="test-model", api_key="test", provider="Test"
            )
            # Should not raise an Exception

    def test_verify_model_invalid(self):
        """Test model verification with invalid model."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ["valid-model"]

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with pytest.raises(ValueError, match="not supported"):
                ConcreteGenAI(
                    model="invalid-model", api_key="test", provider="Test"
                )

    def test_to_stream(self):
        """Test converting string to stream."""
        stream = BaseGenAI._to_stream("Hello world")
        chunks = list(stream)
        assert chunks == ["Hello world"]

        stream = BaseGenAI._to_stream(["Hello", " ", "world"])
        chunks = list(stream)
        assert chunks == ["Hello", " ", "world"]

    def test_cost_calculation(self, gen_ai):
        """Test cost calculation."""
        gen_ai.input_tokens = 100
        gen_ai.output_tokens = 50

        with patch(
            "scitex.ai._gen_ai._BaseGenAI.calc_cost", return_value=0.15
        ):
            assert gen_ai.cost == 0.15

    def test_n_keep_history_limit(self, gen_ai):
        """Test that history is limited by n_keep."""
        gen_ai.n_keep = 3

        # Add more messages than n_keep
        for i in range(5):
            gen_ai.update_history("user", f"Message {i}")

        assert len(gen_ai.history) <= gen_ai.n_keep

    def test_error_handling(self, gen_ai):
        """Test error message handling."""
        gen_ai._error_messages.append("Test error")

        error_flag, error_obj = gen_ai.gen_error(return_stream=False)
        assert error_flag is True
        assert error_obj == "Test error"

    def test_format_output(self, gen_ai):
        """Test output formatting."""
        with patch(
            "scitex.ai._gen_ai._BaseGenAI.format_output_func",
            return_value="Formatted",
        ):
            gen_ai.stream = False
            result = gen_ai("Test", format_output=True)
            assert (
                result == "Test response"
            )  # Our mock doesn't apply formatting

    @pytest.mark.parametrize(
        "image_input,expected_type",
        [
            ("path/to/image.jpg", str),
            (b"image_bytes", str),
        ],
    )
    def test_ensure_base64_encoding(self, image_input, expected_type):
        """Test base64 encoding of images."""
        with patch("PIL.Image.open"):
            result = BaseGenAI._ensure_base64_encoding(image_input)
            assert isinstance(result, expected_type)

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise errors if not implemented."""

        class IncompleteGenAI(BaseGenAI):
            pass

        with pytest.raises(TypeError):
            IncompleteGenAI()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_BaseGenAI.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 11:55:54 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_BaseGenAI.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/ai/_gen_ai/_BaseGenAI.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import base64
# import sys
# from abc import ABC, abstractmethod
# from typing import Any, Dict, Generator, List, Optional, Union
# 
# import matplotlib.pyplot as plt
# import numpy as np
# 
# from ...io._load import load
# from ._calc_cost import calc_cost
# from ._format_output_func import format_output_func
# from ._PARAMS import MODELS
# 
# 
# class BaseGenAI(ABC):
#     def __init__(
#         self,
#         system_setting: str = "",
#         model: str = "",
#         api_key: str = "",
#         stream: bool = False,
#         seed: Optional[int] = None,
#         n_keep: int = 1,
#         temperature: float = 1.0,
#         provider: str = "",
#         chat_history: Optional[List[Dict[str, str]]] = None,
#         max_tokens: int = 4_096,
#     ) -> None:
#         self.provider = provider
#         self.system_setting = system_setting
#         self.model = model
#         self.api_key = api_key
#         self.stream = stream
#         self.seed = seed
#         self.n_keep = n_keep
#         self.temperature = temperature
#         self.max_tokens = max_tokens
#         self.input_tokens = 0
#         self.output_tokens = 0
#         self._error_messages: List[str] = []
# 
#         self.reset(system_setting)
#         self.history = chat_history if chat_history else []
# 
#         try:
#             self.verify_model()
#             self.client = self._init_client()
#         except Exception as error:
#             print(error)
#             self._error_messages.append(f"\nError:\n{str(error)}")
# 
#     @classmethod
#     def list_models(cls, provider: Optional[str] = None) -> List[str]:
#         """List available models for the provider. If provider is None, list all models."""
#         if provider:
#             indi = [
#                 provider.lower() in api_key_env.lower()
#                 for api_key_env in MODELS["api_key_env"]
#             ]
#             models = MODELS[indi].name.tolist()
#             providers = MODELS[indi].provider.tolist()
# 
#         else:
#             indi = np.arange(len(MODELS))
#             models = MODELS.name.tolist()
#             providers = MODELS.provider.tolist()
# 
#         for provider, model in zip(providers, models):
#             print(f"- {provider} - {model}")
# 
#         return models
# 
#     def gen_error(
#         self, return_stream: bool
#     ) -> tuple[bool, Optional[Union[str, Generator]]]:
#         error_exists = bool(self._error_messages)
#         if not error_exists:
#             return False, None
# 
#         error_msgs = self._error_messages
#         self._error_messages = []
# 
#         if not self.stream:
#             return True, "".join(error_msgs)
# 
#         stream_obj = self._to_stream(error_msgs)
#         return True, (
#             self._yield_stream(stream_obj) if not return_stream else stream_obj
#         )
# 
#     def __call__(
#         self,
#         prompt: Optional[str] = None,
#         prompt_file: Optional[str] = None,
#         images: List[Any] = None,
#         format_output: bool = False,
#         return_stream: bool = False,
#     ) -> Union[str, Generator]:
# 
#         # ----------------------------------------
#         # Handles Prompt and Prompt File
#         if (not prompt) and (not prompt_file):
#             print("Please input prompt\n")
#             return
# 
#         if prompt_file:
#             file_content = load(prompt_file)
#             # Escape special characters
#             escaped_content = [repr(line)[1:-1] for line in file_content]
#             prompt = (
#                 str(prompt).strip() + "\n\n" + str("\n".join(escaped_content)).strip()
#             )
# 
#         # if prompt_file:
#         #     prompt = (
#         #         str(prompt).strip()
#         #         + "\n\n"
#         #         + str("\n".join(load(prompt_file))).strip()
#         #     )
# 
#         if prompt.strip() == "":
#             print("Please input prompt\n")
#             return
#         # ----------------------------------------
# 
#         self.update_history("user", prompt or "", images=images)
# 
#         error_flag, error_obj = self.gen_error(return_stream)
#         if error_flag:
#             return error_obj
# 
#         try:
#             if not self.stream:
#                 return self._call_static(format_output)
# 
#             if return_stream:
#                 self.stream, orig_stream = return_stream, self.stream
#                 stream_obj = self._call_stream(format_output)
#                 self.stream = orig_stream
#                 return stream_obj
# 
#             return self._yield_stream(self._call_stream(format_output))
# 
#         except Exception as error:
#             self._error_messages.append(f"\nError:\n{str(error)}")
#             error_flag, error_obj = self.gen_error(return_stream)
#             if error_flag:
#                 return error_obj
# 
#     def _yield_stream(self, stream_obj: Generator) -> str:
#         accumulated = []
#         for chunk in stream_obj:
#             if chunk:
#                 sys.stdout.write(chunk)
#                 sys.stdout.flush()
#                 accumulated.append(chunk)
#         result = "".join(accumulated)
#         self.update_history("assistant", result)
#         return result
# 
#     def _call_static(self, format_output: bool = True) -> str:
#         out_text = self._api_call_static()
#         out_text = format_output_func(out_text) if format_output else out_text
#         self.update_history("assistant", out_text)
#         return out_text
# 
#     def _call_stream(self, format_output: Optional[bool] = None) -> Generator:
#         return self._api_call_stream()
# 
#     @abstractmethod
#     def _init_client(self) -> Any:
#         """Returns client"""
#         pass
# 
#     def _api_format_history(self, history):
#         """Returns chat_history by handling differences in API expectations"""
#         return history
# 
#     @abstractmethod
#     def _api_call_static(self) -> str:
#         """Returns out_text by handling differences in API expectations"""
#         pass
# 
#     @abstractmethod
#     def _api_call_stream(self) -> Generator:
#         """Returns stream by handling differences in API expectations"""
#         pass
# 
#     def _get_available_models(self) -> List[str]:
#         indi = [
#             self.provider.lower() in api_key_env.lower()
#             for api_key_env in MODELS["api_key_env"]
#         ]
#         return MODELS[indi].name.tolist()
# 
#     @property
#     def available_models(self) -> List[str]:
#         return self._get_available_models()
# 
#     def reset(self, system_setting: str = "") -> None:
#         self.history = []
#         if system_setting:
#             self.history.append({"role": "system", "content": system_setting})
# 
#     def _ensure_alternative_history(
#         self, history: List[Dict[str, str]]
#     ) -> List[Dict[str, str]]:
#         if len(history) < 2:
#             return history
# 
#         if history[-1]["role"] == history[-2]["role"]:
#             last_content = history.pop()["content"]
#             history[-1]["content"] += f"\n\n{last_content}"
#             return self._ensure_alternative_history(history)
# 
#         return history
# 
#     @staticmethod
#     def _ensure_start_from_user(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
#         if history and history[0]["role"] != "user":
#             history.pop(0)
#         return history
# 
#     @staticmethod
#     def _ensure_base64_encoding(image, max_size=512):
#         import io
# 
#         from PIL import Image
# 
#         def resize_image(img):
#             # Calculate new dimensions while maintaining aspect ratio
#             ratio = max_size / max(img.size)
#             if ratio < 1:
#                 new_size = tuple(int(dim * ratio) for dim in img.size)
#                 img = img.resize(new_size, Image.Resampling.LANCZOS)
#             return img
# 
#         if isinstance(image, str):
#             try:
#                 # Try to open and resize as file path
#                 img = Image.open(image)
#                 img = resize_image(img)
#                 buffer = io.BytesIO()
#                 img.save(buffer, format="JPEG")
#                 return base64.b64encode(buffer.getvalue()).decode("utf-8")
#             except:
#                 # If fails, assume it's already base64 string
#                 return image
#         elif isinstance(image, bytes):
#             # Convert bytes to image, resize, then back to base64
#             img = Image.open(io.BytesIO(image))
#             img = resize_image(img)
#             buffer = io.BytesIO()
#             img.save(buffer, format="JPEG")
#             return base64.b64encode(buffer.getvalue()).decode("utf-8")
#         else:
#             raise ValueError("Unsupported image format")
# 
#     def update_history(self, role: str, content: str, images=None) -> None:
#         if images is not None:
#             content = [
#                 {"type": "text", "text": content},
#                 *[
#                     {
#                         "type": "_image",
#                         "_image": self._ensure_base64_encoding(image),
#                     }
#                     for image in images
#                 ],
#             ]
# 
#         self.history.append({"role": role, "content": content})
# 
#         if len(self.history) > self.n_keep:
#             self.history = self.history[-self.n_keep :]
# 
#         self.history = self._ensure_alternative_history(self.history)
#         self.history = self._ensure_start_from_user(self.history)
#         self.history = self._api_format_history(self.history)
# 
#     def verify_model(self) -> None:
#         if self.model not in self.available_models:
#             message = (
#                 f"Specified model {self.model} is not supported for the API Key ({self.masked_api_key}). "
#                 f"Available models for {str(self)} are as follows:\n{self.available_models}"
#             )
#             raise ValueError(message)
# 
#     @property
#     def masked_api_key(self) -> str:
#         return f"{self.api_key[:4]}****{self.api_key[-4:]}"
# 
#     def _add_masked_api_key(self, text: str) -> str:
#         return text + f"\n(API Key: {self.masked_api_key}"
# 
#     @property
#     def cost(self) -> float:
#         return calc_cost(self.model, self.input_tokens, self.output_tokens)
# 
#     @staticmethod
#     def _to_stream(string: Union[str, List[str]]) -> Generator[str, None, None]:
#         """Converts string or list of strings to generator for streaming."""
#         chunks = string if isinstance(string, list) else [string]
#         for chunk in chunks:
#             if chunk:
#                 yield chunk
# 
# 
# def main() -> None:
#     pass
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# """
# python src/scitex/ai/_gen_ai/_BaseGenAI.py
# python -m src.scitex.ai._gen_ai._BaseGenAI
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_BaseGenAI.py
# --------------------------------------------------------------------------------
