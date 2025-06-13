#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-28 02:47:54 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_Groq.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_Groq.py"

"""
Functionality:
    - Implements GLOQ AI interface
    - Handles both streaming and static text generation
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses
    - Token usage statistics
Prerequisites:
    - GLOQ API key (GLOQ_API_KEY environment variable)
    - gloq package
"""

"""Imports"""
import os
import sys
from typing import Any, Dict, Generator, List, Optional, Union

from groq import Groq as _Groq
import matplotlib.pyplot as plt

from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


class Groq(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        api_key: Optional[str] = os.getenv("GROQ_API_KEY"),
        model: str = "llama3-8b-8192",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 0.5,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 8000,
    ) -> None:
        max_tokens = min(max_tokens, 8000)
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        super().__init__(
            system_setting=system_setting,
            model=model,
            api_key=api_key,
            stream=stream,
            n_keep=n_keep,
            temperature=temperature,
            provider="Groq",
            chat_history=chat_history,
            max_tokens=max_tokens,
        )

    def _init_client(self) -> Any:
        return _Groq(api_key=self.api_key)

    def _api_call_static(self) -> str:
        output = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
        )
        out_text = output.choices[0].message.content

        self.input_tokens += output.usage.prompt_tokens
        self.output_tokens += output.usage.completion_tokens

        return out_text

    def _api_call_stream(self) -> Generator[str, None, None]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# EOF
