#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/SciTeX-Scholar/src/scitex_scholar/ai/_calc_cost.py

"""
Functionality:
    - Calculates usage costs for AI model API calls
    - Handles token-based pricing for different models
Input:
    - Model name
    - Number of input and output tokens used
Output:
    - Total cost in USD based on token usage
Prerequisites:
    - MODELS parameter dictionary with pricing information
    - pandas package
"""

from typing import Union, Any
import pandas as pd

from ._PARAMS import MODELS


def calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculates API usage cost based on token count.

    Example
    -------
    >>> cost = calc_cost("gpt-4", 100, 50)
    >>> print(f"${cost:.4f}")
    $0.0030

    Parameters
    ----------
    model : str
        Name of the AI model
    input_tokens : int
        Number of input tokens used
    output_tokens : int
        Number of output tokens used

    Returns
    -------
    float
        Total cost in USD

    Raises
    ------
    ValueError
        If model is not found in MODELS
    """
    models_df = pd.DataFrame(MODELS)
    indi = models_df["name"] == model

    if not indi.any():
        raise ValueError(f"Model '{model}' not found in pricing table")

    costs = models_df[["input_cost", "output_cost"]][indi]
    cost = (
        input_tokens * costs["input_cost"] + output_tokens * costs["output_cost"]
    ) / 1_000_000

    return cost.iloc[0]

# EOF