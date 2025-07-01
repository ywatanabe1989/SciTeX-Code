#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/SciTeX-Scholar/src/scitex_scholar/ai/_PARAMS.py

"""AI model parameters and pricing for literature review tasks."""

import pandas as pd

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
ANTHROPIC_MODELS = [
    {
        "name": "claude-opus-4-20250514",
        "input_cost": 15.00,
        "output_cost": 75.00,
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
        "name": "gemini-2.5-flash-preview-04-17",
        "input_cost": 0.15,
        "output_cost": 3.50,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.5-pro-exp-03-25",
        "input_cost": 1.25,
        "output_cost": 10.00,
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
        "name": "gemini-2.0-flash-lite-preview-02-05",
        "input_cost": 0.075,
        "output_cost": 0.30,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.0-pro-exp-02-05",
        "input_cost": None,
        "output_cost": None,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.0-flash-thinking-exp-01-21",
        "input_cost": None,
        "output_cost": None,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-exp-1206",
        "input_cost": None,
        "output_cost": None,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-2.0-flash-exp",
        "input_cost": None,
        "output_cost": None,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-1.5-pro-latest",
        "input_cost": 3.50,
        "output_cost": 10.50,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-1.5-pro",
        "input_cost": 3.50,
        "output_cost": 10.50,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-1.5-flash-latest",
        "input_cost": 0.15,
        "output_cost": 0.0375,
        "api_key_env": "GOOGLE_API_KEY",
        "provider": "Google",
    },
    {
        "name": "gemini-1.5-flash",
        "input_cost": 0.15,
        "output_cost": 0.0375,
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

MODELS = pd.DataFrame(
    OPENAI_MODELS
    + ANTHROPIC_MODELS
    + GOOGLE_MODELS
    + PERPLEXITY_MODELS
)

# EOF