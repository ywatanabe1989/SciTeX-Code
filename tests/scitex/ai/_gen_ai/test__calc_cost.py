#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 23:03:53 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/ai/_gen_ai/test__calc_cost.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/ai/_gen_ai/test__calc_cost.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2025-06-01 13:55:00 (ywatanabe)"

"""Tests for scitex.ai._gen_ai._calc_cost module."""

import pytest
import pandas as pd
from unittest.mock import patch
from scitex.ai._gen_ai import calc_cost


class TestCalcCost:
    """Test suite for calc_cost function."""

    @pytest.fixture
    def mock_models(self):
        """Create mock MODELS DataFrame for testing."""
        return pd.DataFrame({
            'name': ['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'free-model'],
            'input_cost': [30.00, 0.50, 15.00, 0.00],
            'output_cost': [60.00, 1.50, 75.00, 0.00],
            'provider': ['OpenAI', 'OpenAI', 'Anthropic', 'Test']
        })

    def test_calc_cost_gpt4(self, mock_models):
        """Test cost calculation for GPT-4."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            # 1000 input tokens, 500 output tokens
            cost = calc_cost("gpt-4", 1000, 500)

            # Expected: (1000 * 30.00 + 500 * 60.00) / 1,000,000
            expected = (1000 * 30.00 + 500 * 60.00) / 1_000_000
            assert cost == expected
            assert cost == 0.06  # $0.06

    def test_calc_cost_gpt35_turbo(self, mock_models):
        """Test cost calculation for GPT-3.5-turbo."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            # 5000 input tokens, 2000 output tokens
            cost = calc_cost("gpt-3.5-turbo", 5000, 2000)

            # Expected: (5000 * 0.50 + 2000 * 1.50) / 1,000,000
            expected = (5000 * 0.50 + 2000 * 1.50) / 1_000_000
            assert cost == expected
            assert cost == 0.0055  # $0.0055

    def test_calc_cost_claude(self, mock_models):
        """Test cost calculation for Claude."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            # 2000 input tokens, 1000 output tokens
            cost = calc_cost("claude-3-opus", 2000, 1000)

            # Expected: (2000 * 15.00 + 1000 * 75.00) / 1,000,000
            expected = (2000 * 15.00 + 1000 * 75.00) / 1_000_000
            assert cost == expected
            assert cost == 0.105  # $0.105

    def test_calc_cost_zero_tokens(self, mock_models):
        """Test cost calculation with zero tokens."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            cost = calc_cost("gpt-4", 0, 0)
            assert cost == 0.0

    def test_calc_cost_only_input_tokens(self, mock_models):
        """Test cost calculation with only input tokens."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            cost = calc_cost("gpt-4", 1000, 0)
            expected = (1000 * 30.00 + 0 * 60.00) / 1_000_000
            assert cost == expected
            assert cost == 0.03

    def test_calc_cost_only_output_tokens(self, mock_models):
        """Test cost calculation with only output tokens."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            cost = calc_cost("gpt-4", 0, 1000)
            expected = (0 * 30.00 + 1000 * 60.00) / 1_000_000
            assert cost == expected
            assert cost == 0.06

    def test_calc_cost_free_model(self, mock_models):
        """Test cost calculation for free models (zero cost)."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            cost = calc_cost("free-model", 10000, 10000)
            assert cost == 0.0

    def test_calc_cost_invalid_model(self, mock_models):
        """Test error handling for invalid model name."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            with pytest.raises(ValueError, match="Model 'invalid-model' not found"):
                calc_cost("invalid-model", 100, 100)

    def test_calc_cost_large_token_counts(self, mock_models):
        """Test cost calculation with large token counts."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            # 1 million input tokens, 500k output tokens for GPT-4
            cost = calc_cost("gpt-4", 1_000_000, 500_000)

            # Expected: (1,000,000 * 30.00 + 500,000 * 60.00) / 1,000,000
            expected = (1_000_000 * 30.00 + 500_000 * 60.00) / 1_000_000
            assert cost == expected
            assert cost == 60.0  # $60.00

    @pytest.mark.parametrize("input_tokens,output_tokens", [
        (100, 50),
        (1000, 500),
        (10000, 5000),
        (100000, 50000),
    ])
    def test_calc_cost_various_token_counts(self, mock_models, input_tokens, output_tokens):
        """Test cost calculation with various token counts."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            cost = calc_cost("gpt-3.5-turbo", input_tokens, output_tokens)

            expected = (input_tokens * 0.50 + output_tokens * 1.50) / 1_000_000
            assert cost == expected
            assert cost >= 0  # Cost should never be negative

    def test_calc_cost_precision(self, mock_models):
        """Test that cost calculation maintains proper precision."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            # Test with values that might cause floating point issues
            cost = calc_cost("gpt-4", 333, 777)

            expected = (333 * 30.00 + 777 * 60.00) / 1_000_000
            assert abs(cost - expected) < 1e-10  # Allow for tiny floating point errors

    def test_calc_cost_with_real_models_dataframe(self):
        """Test with actual MODELS DataFrame structure."""
        # Import the real MODELS to test integration
        from scitex.ai._gen_ai import MODELS

        # Test with a known model
        if "gpt-3.5-turbo" in MODELS['name'].values:
            cost = calc_cost("gpt-3.5-turbo", 1000, 500)
            assert isinstance(cost, float)
            assert cost >= 0

    def test_calc_cost_return_type(self, mock_models):
        """Test that calc_cost always returns a float."""
        with patch('scitex.ai._gen_ai._PARAMS.MODELS', mock_models):
            cost = calc_cost("gpt-4", 100, 100)
            assert isinstance(cost, float)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_calc_cost.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 01:37:36 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_gen_ai/_calc_cost.py
# 
# """
# Functionality:
#     - Calculates usage costs for AI model API calls
#     - Handles token-based pricing for different models
# Input:
#     - Model name
#     - Number of input and output tokens used
# Output:
#     - Total cost in USD based on token usage
# Prerequisites:
#     - MODELS parameter dictionary with pricing information
#     - pandas package
# """
# 
# from typing import Union, Any
# import pandas as pd
# 
# from ._PARAMS import MODELS
# 
# 
# def calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
#     """Calculates API usage cost based on token count.
# 
#     Example
#     -------
#     >>> cost = calc_cost("gpt-4", 100, 50)
#     >>> print(f"${cost:.4f}")
#     $0.0030
# 
#     Parameters
#     ----------
#     model : str
#         Name of the AI model
#     input_tokens : int
#         Number of input tokens used
#     output_tokens : int
#         Number of output tokens used
# 
#     Returns
#     -------
#     float
#         Total cost in USD
# 
#     Raises
#     ------
#     ValueError
#         If model is not found in MODELS
#     """
#     models_df = pd.DataFrame(MODELS)
#     indi = models_df["name"] == model
# 
#     if not indi.any():
#         raise ValueError(f"Model '{model}' not found in pricing table")
# 
#     costs = models_df[["input_cost", "output_cost"]][indi]
#     cost = (
#         input_tokens * costs["input_cost"] + output_tokens * costs["output_cost"]
#     ) / 1_000_000
# 
#     return cost.iloc[0]
# 
# 
# # def calc_cost(model, input_tokens, output_tokens):
# #     indi = MODELS["name"] == model
# #     costs = MODELS[["input_cost", "output_cost"]][indi]
# #     cost = (
# #         input_tokens * costs["input_cost"]
# #         + output_tokens * costs["output_cost"]
# #     ) / 1_000_000
# #     return cost.iloc[0]
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_calc_cost.py
# --------------------------------------------------------------------------------
