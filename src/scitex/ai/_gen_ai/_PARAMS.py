#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 06:38:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_PARAMS.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ai/_gen_ai/_PARAMS.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/PARAMS.py"

import pandas as pd

# https://api-docs.deepseek.com/quick_start/pricing
DEEPSEEK_MODELS = [
    {
        "name": "deepseek-reasoner",
        "input_cost": 0.14,
        "output_cost": 2.19,
        "api_key_env": "DEEPSEEK_API_KEY",
        "provider": "DeepSeek",
    },
    {
        "name": "deepseek-chat",
        "input_cost": 0.014,
        "output_cost": 0.28,
        "api_key_env": "DEEPSEEK_API_KEY",
        "provider": "DeepSeek",
    },
    {
        "name": "deepseek-coder",
        "input_cost": 0.014,
        "output_cost": 0.28,
        "api_key_env": "DEEPSEEK_API_KEY",
        "provider": "DeepSeek",
    },
]

# https://openai.com/api/pricing/
OPENAI_MODELS = [
    # o3
    {
        "name": "o3",
        "input_cost": 10.00,
        "output_cost": 40.00,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o3-mini",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o3-mini-low",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o3-mini-medium",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o3-mini-high",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    # o4
    {
        "name": "o4-mini",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o4-mini-low",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o4-mini-medium",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o4-mini-high",
        "input_cost": 1.10,
        "output_cost": 4.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    # o1
    {
        "name": "o1",
        "input_cost": 15.00,
        "output_cost": 7.50,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o1-low",
        "input_cost": 15.00,
        "output_cost": 7.50,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "o1-medium",
        "input_cost": 15.00,
        "output_cost": 7.50,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    # {
    #     "name": "o1-high",
    #     "input_cost": 1.10,
    #     "output_cost": 4.40,
    #     "api_key_env": "OPENAI_API_KEY",
    #     "provider": "OpenAI",
    # },
    # ------------------------------
    # For everyday tasks
    # ------------------------------
    # GPT-4.1
    {
        "name": "gpt-4.1",
        "input_cost": 2.00,
        "output_cost": 8.00,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "gpt-4.1-mini",
        "input_cost": 0.40,
        "output_cost": 1.60,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "gpt-4.1-nano",
        "input_cost": 0.10,
        "output_cost": 0.40,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    # GPT-4
    {
        "name": "gpt-4",
        "input_cost": 30.00,
        "output_cost": 60.00,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "gpt-4o",
        "input_cost": 5.00,
        "output_cost": 15.00,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "gpt-4o-mini",
        "input_cost": 0.150,
        "output_cost": 0.600,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "gpt-4-turbo",
        "input_cost": 10.00,
        "output_cost": 30.00,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
    {
        "name": "gpt-3.5-turbo",
        "input_cost": 0.50,
        "output_cost": 1.50,
        "api_key_env": "OPENAI_API_KEY",
        "provider": "OpenAI",
    },
]

# https://docs.anthropic.com/en/docs/about-claude/models/all-models
# https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching#pricing
# https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table
ANTHROPIC_MODELS = [
    {
        "name": "claude-opus-4-1-20250805",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-opus-4-20250514",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-sonnet-4-5-20250929",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-sonnet-4-20250514",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-3-7-sonnet-20250219",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-3-5-sonnet-20241022",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-3-5-haiku-20241022",
        "input_cost": 0.80,
        "output_cost": 4.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-3-5-sonnet-20240620",
        "input_cost": 3.00,
        "output_cost": 15.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-3-opus-20240229",
        "input_cost": 15.00,
        "output_cost": 75.00,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
    {
        "name": "claude-3-haiku-20240307",
        "input_cost": 0.25,
        "output_cost": 1.25,
        "api_key_env": "ANTHROPIC_API_KEY",
        "provider": "Anthropic",
    },
]


# https://ai.google.dev/gemini-api/docs/pricing
GOOGLE_MODELS = [
    {
        "name": "gemini-2.5-pro",
        "input_cost": 2.50,
        "output_cost": 10.00,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.5-flash",
        "input_cost": 0.30,
        "output_cost": 2.50,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.5-flash-lite",
        "input_cost": 0.10,
        "output_cost": 0.40,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.0-flash",
        "input_cost": 0.10,
        "output_cost": 0.40,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.0-flash-lite",
        "input_cost": 0.075,
        "output_cost": 0.30,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
]

PERPLEXITY_MODELS = [
    {
        "name": "llama-3.1-sonar-small-128k-online",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3.1-sonar-large-128k-online",
        "input_cost": 1.00,
        "output_cost": 1.00,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3.1-sonar-huge-128k-online",
        "input_cost": 5.00,
        "output_cost": 5.00,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3.1-sonar-small-128k-chat",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3.1-sonar-large-128k-chat",
        "input_cost": 1.00,
        "output_cost": 1.00,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3-sonar-small-32k-chat",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3-sonar-small-32k-online",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3-sonar-large-32k-chat",
        "input_cost": 1.00,
        "output_cost": 1.00,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3-sonar-large-32k-online",
        "input_cost": 1.00,
        "output_cost": 1.00,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3-8b-instruct",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "llama-3-70b-instruct",
        "input_cost": 1.00,
        "output_cost": 1.00,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
    {
        "name": "mixtral-8x7b-instruct",
        "input_cost": 0.60,
        "output_cost": 0.60,
        "api_key_env": "PERPLEXITY_API_KEY",
        "provider": "Perplexity",
    },
]

LLAMA_MODELS = [
    {
        "name": "llama-3-70b",
        "input_cost": 0.00,
        "output_cost": 0.00,
        "api_key_env": "LLAMA_API_KEY",
        "provider": "Llama",
    },
    {
        "name": "llama-3-70-instruct",
        "input_cost": 0.00,
        "output_cost": 0.00,
        "api_key_env": "LLAMA_API_KEY",
        "provider": "Llama",
    },
    {
        "name": "llama-3-8b",
        "input_cost": 0.00,
        "output_cost": 0.00,
        "api_key_env": "LLAMA_API_KEY",
        "provider": "Llama",
    },
]

# https://console.groq.com/docs/models
GROQ_MODELS = [
    {
        "name": "deepseek-r1-distill-llama-70b",
        "input_cost": 0.01,
        "output_cost": 0.01,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama-3.3-70b-versatile",
        "input_cost": 0.04,
        "output_cost": 0.04,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama-3.2-1b-preview",
        "input_cost": 0.04,
        "output_cost": 0.04,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama-3.2-3b-preview",
        "input_cost": 0.06,
        "output_cost": 0.06,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama-3.1-70b-versatile",
        "input_cost": 0.59,
        "output_cost": 0.79,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama-3.1-8b-instant",
        "input_cost": 0.05,
        "output_cost": 0.08,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama3-70b-8192",
        "input_cost": 0.59,
        "output_cost": 0.79,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama3-8b-8192",
        "input_cost": 0.05,
        "output_cost": 0.08,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "mixtral-8x7b-32768",
        "input_cost": 0.24,
        "output_cost": 0.24,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "gemma-7b-it",
        "input_cost": 0.07,
        "output_cost": 0.07,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "gemma2-9b-it",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama3-groq-70b-8192-tool-use-preview",
        "input_cost": 0.89,
        "output_cost": 0.89,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama3-groq-8b-8192-tool-use-preview",
        "input_cost": 0.19,
        "output_cost": 0.19,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
    {
        "name": "llama-guard-3-8b",
        "input_cost": 0.20,
        "output_cost": 0.20,
        "api_key_env": "GROQ_API_KEY",
        "provider": "Groq",
    },
]

MODELS = pd.DataFrame(
    OPENAI_MODELS
    + ANTHROPIC_MODELS
    + GOOGLE_MODELS
    + PERPLEXITY_MODELS
    + LLAMA_MODELS
    + DEEPSEEK_MODELS
    + GROQ_MODELS
)


# curl -L -X GET 'https://api.deepseek.com/models' \
# -H 'Accept: application/json' \
# -H 'Authorization: Bearer sk-43412ea536ff482e87a38010231ce7c3'

# EOF
