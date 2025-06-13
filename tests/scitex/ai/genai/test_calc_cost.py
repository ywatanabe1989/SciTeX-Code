#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 07:59:00 (ywatanabe)"
# File: ./tests/scitex/ai/genai/test_calc_cost.py

import pytest
import pandas as pd
from unittest.mock import patch, Mock


def test_calc_cost_basic_functionality():
    """Test basic cost calculation functionality."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Test with typical usage
    cost = calc_cost("gpt-4", input_tokens=100, output_tokens=50)
    
    # Should return a float cost
    assert isinstance(cost, float)
    assert cost >= 0  # Cost should be non-negative


def test_calc_cost_zero_tokens():
    """Test cost calculation with zero tokens."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Test with zero input and output tokens
    cost = calc_cost("gpt-4", input_tokens=0, output_tokens=0)
    
    assert isinstance(cost, float)
    assert cost == 0.0  # No tokens should cost nothing


def test_calc_cost_only_input_tokens():
    """Test cost calculation with only input tokens."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    cost = calc_cost("gpt-4", input_tokens=100, output_tokens=0)
    
    assert isinstance(cost, float)
    assert cost > 0  # Should have some cost for input tokens


def test_calc_cost_only_output_tokens():
    """Test cost calculation with only output tokens."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    cost = calc_cost("gpt-4", input_tokens=0, output_tokens=50)
    
    assert isinstance(cost, float)
    assert cost > 0  # Should have some cost for output tokens


def test_calc_cost_different_models():
    """Test cost calculation for different AI models."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Test different models (assuming they exist in MODELS)
    models_to_test = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus-20240229"]
    
    for model in models_to_test:
        try:
            cost = calc_cost(model, input_tokens=100, output_tokens=50)
            assert isinstance(cost, float)
            assert cost >= 0
        except (KeyError, ValueError):
            # Model might not exist in MODELS, skip
            pass


def test_calc_cost_large_token_counts():
    """Test cost calculation with large token counts."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Test with large token counts
    cost = calc_cost("gpt-4", input_tokens=10000, output_tokens=5000)
    
    assert isinstance(cost, float)
    assert cost > 0


@patch('scitex.ai.genai.calc_cost.MODELS')
def test_calc_cost_with_mocked_models(mock_models):
    """Test cost calculation with mocked MODELS data."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Mock MODELS DataFrame
    mock_models_df = pd.DataFrame({
        'name': ['test-model'],
        'input_cost_per_1k_tokens': [0.01],
        'output_cost_per_1k_tokens': [0.02]
    })
    mock_models.set_index.return_value = mock_models_df.set_index('name')
    
    cost = calc_cost("test-model", input_tokens=1000, output_tokens=1000)
    
    # With mock prices: (1000/1000) * 0.01 + (1000/1000) * 0.02 = 0.03
    assert abs(cost - 0.03) < 1e-6


def test_calc_cost_invalid_model():
    """Test cost calculation with invalid model name."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Test with non-existent model
    with pytest.raises(KeyError):
        calc_cost("non-existent-model", input_tokens=100, output_tokens=50)


def test_calc_cost_negative_tokens():
    """Test cost calculation with negative token counts."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Negative tokens should raise an error or be handled gracefully
    with pytest.raises((ValueError, AssertionError)):
        calc_cost("gpt-4", input_tokens=-100, output_tokens=50)
    
    with pytest.raises((ValueError, AssertionError)):
        calc_cost("gpt-4", input_tokens=100, output_tokens=-50)


def test_calc_cost_return_type():
    """Test that calc_cost returns correct type."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    cost = calc_cost("gpt-4", input_tokens=100, output_tokens=50)
    
    # Should always return float
    assert isinstance(cost, float)
    assert not isinstance(cost, int)  # Should be float, not int


def test_calc_cost_precision():
    """Test cost calculation precision."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Test with small token counts for precision
    cost1 = calc_cost("gpt-4", input_tokens=1, output_tokens=1)
    cost2 = calc_cost("gpt-4", input_tokens=2, output_tokens=2)
    
    # Cost should scale proportionally
    assert cost2 > cost1
    assert abs(cost2 - 2 * cost1) < 1e-6  # Should be approximately double


def test_calc_cost_consistency():
    """Test that cost calculation is consistent."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Same inputs should give same outputs
    cost1 = calc_cost("gpt-4", input_tokens=100, output_tokens=50)
    cost2 = calc_cost("gpt-4", input_tokens=100, output_tokens=50)
    
    assert cost1 == cost2


def test_calc_cost_additive_property():
    """Test that cost calculation has additive property."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Calculate costs separately
    cost_input_only = calc_cost("gpt-4", input_tokens=100, output_tokens=0)
    cost_output_only = calc_cost("gpt-4", input_tokens=0, output_tokens=50)
    
    # Calculate combined cost
    cost_combined = calc_cost("gpt-4", input_tokens=100, output_tokens=50)
    
    # Should be approximately equal (within floating point precision)
    assert abs(cost_combined - (cost_input_only + cost_output_only)) < 1e-10


@patch('scitex.ai.genai.calc_cost.MODELS')
def test_calc_cost_models_access(mock_models):
    """Test that calc_cost properly accesses MODELS data."""
    from scitex.ai.genai.calc_cost import calc_cost
    
    # Mock MODELS to track access
    mock_df = Mock()
    mock_models.__getitem__.return_value = mock_df
    mock_df.loc.__getitem__.return_value = {'input_cost_per_1k_tokens': 0.01, 'output_cost_per_1k_tokens': 0.02}
    
    calc_cost("test-model", input_tokens=1000, output_tokens=500)
    
    # Verify MODELS was accessed
    mock_models.__getitem__.assert_called()


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])