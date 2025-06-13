#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 11:57:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_genai_factory.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/ai/_gen_ai/_genai_factory.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import random

from .anthropic import Anthropic
from .deepseek import DeepSeek
from .google import Google
from .groq import Groq
from .llama import Llama
from .openai import OpenAI
from .params import MODELS
from .perplexity import Perplexity


def genai_factory(
    model="gpt-3.5-turbo",
    stream=False,
    api_key=None,
    seed=None,
    temperature=1.0,
    n_keep=1,
    chat_history=None,
    max_tokens=4096,
):
    """Factory function to create an instance of an AI model handler."""
    AVAILABLE_MODELS = MODELS.name.tolist()

    if model not in AVAILABLE_MODELS:
        raise ValueError(
            f'Model "{model}" is not available. Please choose from:{MODELS.name.tolist()}'
        )

    provider = MODELS[MODELS.name == model].provider.iloc[0]

    # model_class = globals()[provider]
    model_class = {
        "OpenAI": OpenAI,
        "Anthropic": Anthropic,
        "Google": Google,
        "Llama": Llama,
        "Perplexity": Perplexity,
        "DeepSeek": DeepSeek,
        "Groq": Groq,
    }[provider]

    # Select a random API key from the list
    if isinstance(api_key, (list, tuple)):
        api_key = random.choice(api_key)

    return model_class(
        model=model,
        stream=stream,
        api_key=api_key,
        seed=seed,
        temperature=temperature,
        n_keep=n_keep,
        chat_history=chat_history,
        max_tokens=max_tokens,
    )


# EOF
