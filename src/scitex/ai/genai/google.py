#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-06 13:47:23 (ywatanabe)"
# File: _Google.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Google.py"


"""
Functionality:
    - Implements Google's Generative AI (Gemini) interface
    - Handles both streaming and static text generation
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses from Gemini models
    - Token usage statistics
Prerequisites:
    - Google API key (GOOGLE_API_KEY environment variable)
    - google.generativeai package

DEPRECATED: This module is deprecated. Please use google_provider.py instead.
The new provider-based architecture offers better modularity and maintainability.
"""

"""Imports"""
import os
import sys
from pprint import pprint
from typing import Any, Dict, Generator, List, Optional
import warnings

import matplotlib.pyplot as plt
import scitex

from google import genai

from .base_genai import BaseGenAI

warnings.warn(
    "google.py is deprecated. Please use google_provider.py instead. "
    "See PROVIDER_MIGRATION_GUIDE.md for migration instructions.",
    DeprecationWarning,
    stacklevel=2,
)

"""Functions & Classes"""


class Google(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        api_key: Optional[str] = os.getenv("GOOGLE_API_KEY"),
        model: str = "gemini-1.5-pro-latest",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 1.0,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 32_768,
    ) -> None:

        api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        super().__init__(
            system_setting=system_setting,
            model=model,
            api_key=api_key,
            stream=stream,
            seed=seed,
            n_keep=n_keep,
            temperature=temperature,
            provider="Google",
            chat_history=chat_history,
            max_tokens=max_tokens,
        )

    def _init_client(self) -> Any:
        return genai.Client(api_key=self.api_key)

    def _api_call_static(self) -> str:
        response = self.client.models.generate_content(
            model=self.model, contents=self.history
        )

        try:
            self.input_tokens += response.usage_metadata.prompt_token_count
            self.output_tokens += response.usage_metadata.candidates_token_count
        except:
            pass

        return response.text

    def _api_call_stream(self) -> Generator[str, None, None]:
        # print("========================================")
        # pprint(self.history)
        # print("========================================")

        # return self.client.models.generate_content_stream(
        #     model=self.model, contents=self.history
        # )

        for chunk in self.client.models.generate_content_stream(
            model=self.model, contents=self.history
        ):
            if chunk:
                try:
                    self.input_tokens += chunk.usage_metadata.prompt_token_count
                    self.output_tokens += chunk.usage_metadata.candidates_token_count
                except:
                    pass

                yield chunk.text

    def _api_format_history(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Formats the chat history for the Google Generative AI API."""
        formatted_history = []
        for item in history:
            if isinstance(item.get("parts"), list):
                # Rename role from assistant to model
                if item.get("role") == "assistant":
                    item["role"] = "model"
                formatted_history.append(item)
            else:
                formatted_history.append(
                    {
                        "role": item["role"],
                        "parts": [{"text": item["content"]}],
                    }
                )
        # print(formatted_history)
        return formatted_history


def main() -> None:
    ai = scitex.ai.GenAI(
        # "gemini-2.0-flash-exp",
        # "gemini-2.0-flash",
        # "gemini-2.0-flash-lite-preview-02-05",
        # "gemini-2.0-pro-exp-02-05",
        "gemini-2.0-flash-thinking-exp-01-21",
        stream=True,
        n_keep=10,
    )
    print(ai("hi"))
    print(ai("My name is Yusuke"))
    print(ai("do you remember my name?"))


if __name__ == "__main__":
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
    main()
    scitex.gen.close(CONFIG, verbose=False, notify=False)


"""
python src/scitex/ai/_gen_ai/_Google.py
python -m src.scitex.ai._gen_ai._Google
"""


# EOF
