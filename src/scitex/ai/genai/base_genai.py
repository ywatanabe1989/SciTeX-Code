#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 11:55:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_BaseGenAI.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/ai/_gen_ai/_BaseGenAI.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import base64
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from ...io._load import load
from .calc_cost import calc_cost
from .format_output_func import format_output_func
from .params import MODELS


class BaseGenAI(ABC):
    def __init__(
        self,
        system_setting: str = "",
        model: str = "",
        api_key: str = "",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 1.0,
        provider: str = "",
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 4_096,
    ) -> None:
        self.provider = provider
        self.system_setting = system_setting
        self.model = model
        self.api_key = api_key
        self.stream = stream
        self.seed = seed
        self.n_keep = n_keep
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.input_tokens = 0
        self.output_tokens = 0
        self._error_messages: List[str] = []

        self.reset(system_setting)
        self.history = chat_history if chat_history else []

        try:
            self.verify_model()
            self.client = self._init_client()
        except Exception as error:
            print(error)
            self._error_messages.append(f"\nError:\n{str(error)}")

    @classmethod
    def list_models(cls, provider: Optional[str] = None) -> List[str]:
        """List available models for the provider. If provider is None, list all models."""
        if provider:
            indi = [
                provider.lower() in api_key_env.lower()
                for api_key_env in MODELS["api_key_env"]
            ]
            models = MODELS[indi].name.tolist()
            providers = MODELS[indi].provider.tolist()

        else:
            indi = np.arange(len(MODELS))
            models = MODELS.name.tolist()
            providers = MODELS.provider.tolist()

        for provider, model in zip(providers, models):
            print(f"- {provider} - {model}")

        return models

    def gen_error(
        self, return_stream: bool
    ) -> tuple[bool, Optional[Union[str, Generator]]]:
        error_exists = bool(self._error_messages)
        if not error_exists:
            return False, None

        error_msgs = self._error_messages
        self._error_messages = []

        if not self.stream:
            return True, "".join(error_msgs)

        stream_obj = self._to_stream(error_msgs)
        return True, (
            self._yield_stream(stream_obj) if not return_stream else stream_obj
        )

    def __call__(
        self,
        prompt: Optional[str] = None,
        prompt_file: Optional[str] = None,
        images: List[Any] = None,
        format_output: bool = False,
        return_stream: bool = False,
    ) -> Union[str, Generator]:

        # ----------------------------------------
        # Handles Prompt and Prompt File
        if (not prompt) and (not prompt_file):
            print("Please input prompt\n")
            return

        if prompt_file:
            file_content = load(prompt_file)
            # Escape special characters
            escaped_content = [repr(line)[1:-1] for line in file_content]
            prompt = (
                str(prompt).strip() + "\n\n" + str("\n".join(escaped_content)).strip()
            )

        # if prompt_file:
        #     prompt = (
        #         str(prompt).strip()
        #         + "\n\n"
        #         + str("\n".join(load(prompt_file))).strip()
        #     )

        if prompt.strip() == "":
            print("Please input prompt\n")
            return
        # ----------------------------------------

        self.update_history("user", prompt or "", images=images)

        error_flag, error_obj = self.gen_error(return_stream)
        if error_flag:
            return error_obj

        try:
            if not self.stream:
                return self._call_static(format_output)

            if return_stream:
                self.stream, orig_stream = return_stream, self.stream
                stream_obj = self._call_stream(format_output)
                self.stream = orig_stream
                return stream_obj

            return self._yield_stream(self._call_stream(format_output))

        except Exception as error:
            self._error_messages.append(f"\nError:\n{str(error)}")
            error_flag, error_obj = self.gen_error(return_stream)
            if error_flag:
                return error_obj

    def _yield_stream(self, stream_obj: Generator) -> str:
        accumulated = []
        for chunk in stream_obj:
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
                accumulated.append(chunk)
        result = "".join(accumulated)
        self.update_history("assistant", result)
        return result

    def _call_static(self, format_output: bool = True) -> str:
        out_text = self._api_call_static()
        out_text = format_output_func(out_text) if format_output else out_text
        self.update_history("assistant", out_text)
        return out_text

    def _call_stream(self, format_output: Optional[bool] = None) -> Generator:
        return self._api_call_stream()

    @abstractmethod
    def _init_client(self) -> Any:
        """Returns client"""
        pass

    def _api_format_history(self, history):
        """Returns chat_history by handling differences in API expectations"""
        return history

    @abstractmethod
    def _api_call_static(self) -> str:
        """Returns out_text by handling differences in API expectations"""
        pass

    @abstractmethod
    def _api_call_stream(self) -> Generator:
        """Returns stream by handling differences in API expectations"""
        pass

    def _get_available_models(self) -> List[str]:
        indi = [
            self.provider.lower() in api_key_env.lower()
            for api_key_env in MODELS["api_key_env"]
        ]
        return MODELS[indi].name.tolist()

    @property
    def available_models(self) -> List[str]:
        return self._get_available_models()

    def reset(self, system_setting: str = "") -> None:
        self.history = []
        if system_setting:
            self.history.append({"role": "system", "content": system_setting})

    def _ensure_alternative_history(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        if len(history) < 2:
            return history

        if history[-1]["role"] == history[-2]["role"]:
            last_content = history.pop()["content"]
            history[-1]["content"] += f"\n\n{last_content}"
            return self._ensure_alternative_history(history)

        return history

    @staticmethod
    def _ensure_start_from_user(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if history and history[0]["role"] != "user":
            history.pop(0)
        return history

    @staticmethod
    def _ensure_base64_encoding(image, max_size=512):
        import io

        from PIL import Image

        def resize_image(img):
            # Calculate new dimensions while maintaining aspect ratio
            ratio = max_size / max(img.size)
            if ratio < 1:
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            return img

        if isinstance(image, str):
            try:
                # Try to open and resize as file path
                img = Image.open(image)
                img = resize_image(img)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG")
                return base64.b64encode(buffer.getvalue()).decode("utf-8")
            except:
                # If fails, assume it's already base64 string
                return image
        elif isinstance(image, bytes):
            # Convert bytes to image, resize, then back to base64
            img = Image.open(io.BytesIO(image))
            img = resize_image(img)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        else:
            raise ValueError("Unsupported image format")

    def update_history(self, role: str, content: str, images=None) -> None:
        if images is not None:
            content = [
                {"type": "text", "text": content},
                *[
                    {
                        "type": "_image",
                        "_image": self._ensure_base64_encoding(image),
                    }
                    for image in images
                ],
            ]

        self.history.append({"role": role, "content": content})

        if len(self.history) > self.n_keep:
            self.history = self.history[-self.n_keep :]

        self.history = self._ensure_alternative_history(self.history)
        self.history = self._ensure_start_from_user(self.history)
        self.history = self._api_format_history(self.history)

    def verify_model(self) -> None:
        if self.model not in self.available_models:
            message = (
                f"Specified model {self.model} is not supported for the API Key ({self.masked_api_key}). "
                f"Available models for {str(self)} are as follows:\n{self.available_models}"
            )
            raise ValueError(message)

    @property
    def masked_api_key(self) -> str:
        return f"{self.api_key[:4]}****{self.api_key[-4:]}"

    def _add_masked_api_key(self, text: str) -> str:
        return text + f"\n(API Key: {self.masked_api_key}"

    @property
    def cost(self) -> float:
        return calc_cost(self.model, self.input_tokens, self.output_tokens)

    @staticmethod
    def _to_stream(string: Union[str, List[str]]) -> Generator[str, None, None]:
        """Converts string or list of strings to generator for streaming."""
        chunks = string if isinstance(string, list) else [string]
        for chunk in chunks:
            if chunk:
                yield chunk


def main() -> None:
    pass


if __name__ == "__main__":
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
    main()
    scitex.gen.close(CONFIG, verbose=False, notify=False)

"""
python src/scitex/ai/_gen_ai/_BaseGenAI.py
python -m src.scitex.ai._gen_ai._BaseGenAI
"""

# EOF
