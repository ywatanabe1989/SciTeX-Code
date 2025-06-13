#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-11 04:11:10 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_Perplexity.py

"""
Functionality:
    - Implements Perplexity AI interface using OpenAI-compatible API
    - Provides access to Llama and Mixtral models
Input:
    - User prompts and chat history
    - Model configurations and API credentials
Output:
    - Generated text responses from Perplexity models
    - Token usage statistics
Prerequisites:
    - Perplexity API key
    - openai package

DEPRECATED: This module is deprecated. Please use perplexity_provider.py instead.
The new provider-based architecture offers better modularity and maintainability.
"""

"""Imports"""
import os
import sys
from pprint import pprint
from typing import Dict, Generator, List, Optional
import warnings

import matplotlib.pyplot as plt
from openai import OpenAI

from .base_genai import BaseGenAI

warnings.warn(
    "perplexity.py is deprecated. Please use perplexity_provider.py instead. "
    "See PROVIDER_MIGRATION_GUIDE.md for migration instructions.",
    DeprecationWarning,
    stacklevel=2,
)

"""Functions & Classes"""


class Perplexity(BaseGenAI):
    def __init__(
        self,
        system_setting: str = "",
        model: str = "",
        api_key: str = "",
        stream: bool = False,
        seed: Optional[int] = None,
        n_keep: int = 1,
        temperature: float = 1.0,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None,  # Added parameter
    ) -> None:
        # Set max_tokens based on model if not provided
        if max_tokens is None:
            max_tokens = 128_000 if "128k" in model else 32_000

        super().__init__(
            system_setting=system_setting,
            model=model,
            api_key=api_key,
            stream=stream,
            n_keep=n_keep,
            temperature=temperature,
            provider="Perplexity",
            chat_history=chat_history,
            max_tokens=max_tokens,
        )

    def _init_client(self) -> OpenAI:
        return OpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
        # return OpenAI(
        #     api_key=self.api_key, base_url="https://api.perplexity.ai/chat/completions"
        # )

    def _api_call_static(self) -> str:
        output = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=self.max_tokens,
            stream=False,
            temperature=self.temperature,
        )

        print(output)

        out_text = output.choices[0].message.content
        self.input_tokens += output.usage.prompt_tokens
        self.output_tokens += output.usage.completion_tokens

        return out_text

    def _api_call_stream(self) -> Generator[str, None, None]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=self.max_tokens,
            n=1,
            stream=self.stream,
            temperature=self.temperature,
        )

        for chunk in stream:
            if chunk and chunk.choices[0].finish_reason == "stop":
                print(chunk.choices)
                try:
                    self.input_tokens += chunk.usage.prompt_tokens
                    self.output_tokens += chunk.usage.completion_tokens
                except AttributeError:
                    pass

            if chunk.choices:
                current_text = chunk.choices[0].delta.content
                if current_text:
                    yield current_text

    def _get_available_models(self) -> List[str]:
        return [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-huge-128k-online",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-sonar-large-128k-chat",
            "llama-3-sonar-small-32k-chat",
            "llama-3-sonar-small-32k-online",
            "llama-3-sonar-large-32k-chat",
            "llama-3-sonar-large-32k-online",
            "llama-3-8b-instruct",
            "llama-3-70b-instruct",
            "mixtral-8x7b-instruct",
        ]


def main() -> None:
    from ._genai_factory import genai_factory as GenAI

    models = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-huge-128k-online",
    ]
    ai = GenAI(model=models[0], api_key=os.getenv("PERPLEXITY_API_KEY"), stream=False)
    out = ai("tell me about important citations for epilepsy prediction with citations")
    print(out)


def main():
    import requests

    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {
                "role": "user",
                "content": "tell me useful citations (scientific peer-reviewed papers) for epilepsy seizure prediction.",
            },
        ],
        "max_tokens": 4096,
        "temperature": 0.2,
        "top_p": 0.9,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
    }
    api_key = os.getenv("PERPLEXITY_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    pprint(response.json()["citations"])
    # pprint(response["citations"])

    # print(response.url)
    # print(response.links)
    # print(dir(response))
    # print(response.text["citations"])


if __name__ == "__main__":
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
    main()
    scitex.gen.close(CONFIG, verbose=False, notify=False)

# EOF
