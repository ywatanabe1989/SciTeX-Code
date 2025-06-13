#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 08:06:00 (ywatanabe)"
# File: ./tests/scitex/stats/test__multiple_corrections.py

import pytest
import numpy as np
from unittest.mock import patch, Mock


def test_bonferroni_correction_basic():
    """Test basic Bonferroni correction functionality."""
    from scitex.stats import bonferroni_correction
    
    # Sample p-values
    p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    result = bonferroni_correction(p_values)
    
    assert isinstance(result, np.ndarray)
    assert len(result) == len(p_values)
    assert all(result >= p_values)  # Corrected p-values should be larger


def test_bonferroni_correction_single_value():
    """Test Bonferroni correction with single p-value."""
    from scitex.stats import bonferroni_correction
    
    p_values = np.array([0.01])
    result = bonferroni_correction(p_values)
    
    assert isinstance(result, np.ndarray)
    assert len(result) == 1
    assert result[0] == 0.01  # Single value should remain unchanged


def test_bonferroni_correction_alpha_parameter():
    """Test Bonferroni correction with different alpha values."""
    from scitex.stats import bonferroni_correction
    
    p_values = np.array([0.01, 0.02, 0.03])
    
    # Test with different alpha values
    result1 = bonferroni_correction(p_values, alpha=0.05)
    result2 = bonferroni_correction(p_values, alpha=0.01)
    
    assert isinstance(result1, np.ndarray)
    assert isinstance(result2, np.ndarray)
    # Results should be same (Bonferroni just multiplies by n)
    np.testing.assert_array_equal(result1, result2)


def test_fdr_correction_basic():
    """Test basic FDR correction functionality."""
    from scitex.stats import fdr_correction
    
    # Sample p-values
    p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    result = fdr_correction(p_values)
    
    assert isinstance(result, np.ndarray)
    assert len(result) == len(p_values)


def test_fdr_correction_methods():
    """Test FDR correction with different methods."""
    from scitex.stats import fdr_correction
    
    p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    
    # Test different methods
    result_indep = fdr_correction(p_values, method="indep")
    result_negcorr = fdr_correction(p_values, method="negcorr")
    
    assert isinstance(result_indep, np.ndarray)
    assert isinstance(result_negcorr, np.ndarray)


def test_bonferroni_vs_fdr():
    """Test difference between Bonferroni and FDR corrections."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    p_values = np.array([0.001, 0.01, 0.02, 0.03, 0.04])
    
    bonf_result = bonferroni_correction(p_values)
    fdr_result = fdr_correction(p_values)
    
    # Bonferroni should be more conservative (larger p-values)
    assert np.mean(bonf_result) >= np.mean(fdr_result)


def test_multiple_corrections_edge_cases():
    """Test multiple corrections with edge cases."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    # All identical p-values
    p_values = np.array([0.05, 0.05, 0.05])
    bonf_result = bonferroni_correction(p_values)
    fdr_result = fdr_correction(p_values)
    
    assert isinstance(bonf_result, np.ndarray)
    assert isinstance(fdr_result, np.ndarray)


def test_multiple_corrections_extreme_values():
    """Test multiple corrections with extreme p-values."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    # Very small and large p-values
    p_values = np.array([0.0001, 0.999, 0.5])
    
    bonf_result = bonferroni_correction(p_values)
    fdr_result = fdr_correction(p_values)
    
    assert isinstance(bonf_result, np.ndarray)
    assert isinstance(fdr_result, np.ndarray)
    assert all(bonf_result <= 1.0)  # Should not exceed 1.0


@patch('scitex.stats._multiple_corrections._bonf_impl')
def test_bonferroni_wrapper_calls_implementation(mock_bonf_impl):
    """Test that Bonferroni wrapper calls underlying implementation."""
    from scitex.stats import bonferroni_correction
    
    # Mock the implementation
    mock_bonf_impl.return_value = (np.array([True, False]), np.array([0.02, 0.04]))
    
    p_values = np.array([0.01, 0.02])
    result = bonferroni_correction(p_values, alpha=0.05)
    
    # Verify implementation was called
    mock_bonf_impl.assert_called_once_with(p_values, alpha=0.05)
    
    # Verify result
    np.testing.assert_array_equal(result, np.array([0.02, 0.04]))


@patch('scitex.stats._multiple_corrections._fdr_impl')
def test_fdr_wrapper_calls_implementation(mock_fdr_impl):
    """Test that FDR wrapper calls underlying implementation."""
    from scitex.stats import fdr_correction
    
    # Mock the implementation
    mock_fdr_impl.return_value = (np.array([True, False]), np.array([0.015, 0.025]))
    
    p_values = np.array([0.01, 0.02])
    result = fdr_correction(p_values, alpha=0.05, method="indep")
    
    # Verify implementation was called
    mock_fdr_impl.assert_called_once_with(p_values, alpha=0.05, method="indep")
    
    # Verify result
    np.testing.assert_array_equal(result, np.array([0.015, 0.025]))


def test_corrections_with_empty_array():
    """Test corrections with empty p-value array."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    # Empty array
    p_values = np.array([])
    
    bonf_result = bonferroni_correction(p_values)
    fdr_result = fdr_correction(p_values)
    
    assert isinstance(bonf_result, np.ndarray)
    assert isinstance(fdr_result, np.ndarray)
    assert len(bonf_result) == 0
    assert len(fdr_result) == 0


def test_corrections_return_types():
    """Test that corrections return correct types."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    p_values = np.array([0.01, 0.02, 0.03])
    
    bonf_result = bonferroni_correction(p_values)
    fdr_result = fdr_correction(p_values)
    
    # Should return numpy arrays
    assert isinstance(bonf_result, np.ndarray)
    assert isinstance(fdr_result, np.ndarray)
    
    # Should contain floats
    assert bonf_result.dtype in [np.float32, np.float64]
    assert fdr_result.dtype in [np.float32, np.float64]


def test_corrections_invalid_alpha():
    """Test corrections with invalid alpha values."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    p_values = np.array([0.01, 0.02, 0.03])
    
    # Invalid alpha values
    with pytest.raises((ValueError, AssertionError)):
        bonferroni_correction(p_values, alpha=-0.1)
    
    with pytest.raises((ValueError, AssertionError)):
        bonferroni_correction(p_values, alpha=1.5)
    
    with pytest.raises((ValueError, AssertionError)):
        fdr_correction(p_values, alpha=-0.1)


def test_corrections_consistency():
    """Test that corrections are consistent."""
    from scitex.stats import bonferroni_correction, fdr_correction
    
    p_values = np.array([0.01, 0.02, 0.03])
    
    # Same inputs should give same outputs
    bonf1 = bonferroni_correction(p_values)
    bonf2 = bonferroni_correction(p_values)
    
    fdr1 = fdr_correction(p_values)
    fdr2 = fdr_correction(p_values)
    
    np.testing.assert_array_equal(bonf1, bonf2)
    np.testing.assert_array_equal(fdr1, fdr2)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])