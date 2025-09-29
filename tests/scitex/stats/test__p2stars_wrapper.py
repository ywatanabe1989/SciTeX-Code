#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 08:04:00 (ywatanabe)"
# File: ./tests/scitex/stats/test__p2stars_wrapper.py

import pytest
import numpy as np


def test_p2stars_wrapper_single_value():
    """Test p2stars wrapper with single p-value."""
    from scitex.stats import p2stars
    
    # Highly significant
    result = p2stars(0.0001)
    assert isinstance(result, str)
    assert result == "***"
    
    # Moderately significant
    result = p2stars(0.005)
    assert result == "**"
    
    # Barely significant
    result = p2stars(0.03)
    assert result == "*"
    
    # Not significant
    result = p2stars(0.1)
    assert result == "ns"


def test_p2stars_wrapper_array_input():
    """Test p2stars wrapper with array input."""
    from scitex.stats import p2stars
    
    # Array of p-values
    p_values = np.array([0.0001, 0.005, 0.03, 0.1])
    result = p2stars(p_values)
    
    assert isinstance(result, list)
    assert len(result) == 4
    assert result == ["***", "**", "*", "ns"]


def test_p2stars_wrapper_list_input():
    """Test p2stars wrapper with list input."""
    from scitex.stats import p2stars
    
    # List of p-values
    p_values = [0.0005, 0.01, 0.04, 0.15]
    result = p2stars(p_values)
    
    assert isinstance(result, list)
    assert len(result) == 4
    assert result == ["***", "**", "*", "ns"]


def test_p2stars_wrapper_custom_thresholds():
    """Test p2stars wrapper with custom thresholds."""
    from scitex.stats import p2stars
    
    # Custom thresholds
    custom_thresholds = [0.01, 0.05]
    result = p2stars(0.02, thresholds=custom_thresholds)
    
    assert isinstance(result, str)
    assert result == "*"  # Between 0.01 and 0.05


def test_p2stars_wrapper_custom_symbols():
    """Test p2stars wrapper with custom symbols."""
    from scitex.stats import p2stars
    
    # Custom symbols
    custom_symbols = ["+++", "++", "+"]
    result = p2stars(0.0001, symbols=custom_symbols)
    
    assert isinstance(result, str)
    assert result == "+++"


def test_p2stars_wrapper_custom_thresholds_and_symbols():
    """Test p2stars wrapper with both custom thresholds and symbols."""
    from scitex.stats import p2stars
    
    # Custom thresholds and symbols
    custom_thresholds = [0.01, 0.05]
    custom_symbols = ["HIGH", "LOW"]
    
    result = p2stars(0.002, thresholds=custom_thresholds, symbols=custom_symbols)
    assert result == "HIGH"
    
    result = p2stars(0.03, thresholds=custom_thresholds, symbols=custom_symbols)
    assert result == "LOW"
    
    result = p2stars(0.1, thresholds=custom_thresholds, symbols=custom_symbols)
    assert result == "ns"


def test_p2stars_wrapper_edge_cases():
    """Test p2stars wrapper with edge cases."""
    from scitex.stats import p2stars
    
    # Exactly on threshold
    result = p2stars(0.05)
    assert result == "*"
    
    # Exactly on highest significance threshold
    result = p2stars(0.001)
    assert result == "***"
    
    # Zero p-value (perfectly significant)
    result = p2stars(0.0)
    assert result == "***"
    
    # P-value of 1 (not significant at all)
    result = p2stars(1.0)
    assert result == "ns"


def test_p2stars_wrapper_invalid_pvalues():
    """Test p2stars wrapper with invalid p-values."""
    from scitex.stats import p2stars
    
    # P-values outside [0, 1] range should be handled gracefully
    with pytest.raises((ValueError, AssertionError)):
        p2stars(-0.1)
    
    with pytest.raises((ValueError, AssertionError)):
        p2stars(1.5)


def test_p2stars_wrapper_empty_input():
    """Test p2stars wrapper with empty input."""
    from scitex.stats import p2stars
    
    # Empty list
    result = p2stars([])
    assert isinstance(result, list)
    assert len(result) == 0
    
    # Empty array
    result = p2stars(np.array([]))
    assert isinstance(result, list)
    assert len(result) == 0


def test_p2stars_wrapper_mixed_significance():
    """Test p2stars wrapper with mixed significance levels."""
    from scitex.stats import p2stars
    
    # Mixed significance levels
    p_values = [0.0001, 0.006, 0.02, 0.06, 0.15]
    result = p2stars(p_values)
    
    expected = ["***", "**", "*", "ns", "ns"]
    assert result == expected


def test_p2stars_wrapper_return_types():
    """Test that p2stars wrapper returns correct types."""
    from scitex.stats import p2stars
    
    # Single value should return string
    result = p2stars(0.01)
    assert isinstance(result, str)
    
    # Array/list should return list of strings
    result = p2stars([0.01, 0.05])
    assert isinstance(result, list)
    assert all(isinstance(r, str) for r in result)


def test_p2stars_wrapper_nan_handling():
    """Test p2stars wrapper with NaN values."""
    from scitex.stats import p2stars
    
    # Single NaN
    result = p2stars(np.nan)
    # Should handle NaN gracefully (might return 'ns' or raise error)
    assert result in ["ns", "nan"] or result is None


def test_p2stars_wrapper_large_arrays():
    """Test p2stars wrapper with large arrays."""
    from scitex.stats import p2stars
    
    # Large array of random p-values
    np.random.seed(42)
    large_pvalues = np.random.uniform(0, 1, 1000)
    
    result = p2stars(large_pvalues)
    
    assert isinstance(result, list)
    assert len(result) == 1000
    assert all(r in ["***", "**", "*", "ns"] for r in result)


def test_p2stars_wrapper_consistency():
    """Test that p2stars wrapper is consistent."""
    from scitex.stats import p2stars
    
    # Same input should give same output
    p_value = 0.02
    result1 = p2stars(p_value)
    result2 = p2stars(p_value)
    
    assert result1 == result2

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/_p2stars_wrapper.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-05-30 auto-created"
# # File: ./src/scitex/stats/_p2stars_wrapper.py
# 
# """
# Wrapper for p2stars to handle array inputs and match test expectations
# """
# 
# import numpy as np
# from typing import Union, List
# 
# 
# def p2stars(
#     input_data: Union[float, np.ndarray, List],
#     thresholds: List[float] = None,
#     symbols: List[str] = None,
# ) -> Union[str, List[str]]:
#     """
#     Wrapper for p2stars that handles array inputs and returns 'ns' for non-significant.
# 
#     Parameters
#     ----------
#     input_data : float, np.ndarray, or List
#         P-value(s) to convert
#     thresholds : List[float], optional
#         Custom significance thresholds (default: [0.001, 0.01, 0.05])
#     symbols : List[str], optional
#         Custom symbols for each threshold (default: ['***', '**', '*'])
#     """
#     from ._p2stars import p2stars as _p2stars_impl
# 
#     # Handle custom thresholds/symbols
#     if thresholds is not None and symbols is not None:
# 
#         def custom_p2stars(p):
#             try:
#                 p_float = float(p)
#                 for threshold, symbol in zip(thresholds, symbols):
#                     if p_float <= threshold:
#                         return symbol
#                 return "ns"
#             except (ValueError, TypeError):
#                 return "NA"
# 
#         if isinstance(input_data, (np.ndarray, list)):
#             return [custom_p2stars(p) for p in input_data]
#         else:
#             return custom_p2stars(input_data)
# 
#     # Default behavior
#     if isinstance(input_data, (np.ndarray, list)):
#         return [_p2stars_impl(p, ns=True) for p in input_data]
#     else:
#         # Single value - use ns=True to return 'ns' instead of empty string
#         return _p2stars_impl(input_data, ns=True)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/_p2stars_wrapper.py
# --------------------------------------------------------------------------------
