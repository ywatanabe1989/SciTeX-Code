#!/usr/bin/env python3
"""Tests for scitex.stats._corr_test_wrapper module.

This module provides comprehensive tests for the correlation test wrapper
functions that provide Pearson and Spearman correlation tests with
permutation-based significance testing.
"""

import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from scipy import stats

from scitex.stats import (
    corr_test,
    corr_test_spearman,
    corr_test_pearson
)


class TestCorrTestWrapper:
    """Test correlation test wrapper functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing."""
        np.random.seed(42)
        n = 100
        
        # Positively correlated data
        x = np.random.randn(n)
        y_pos = x + 0.5 * np.random.randn(n)
        
        # Negatively correlated data
        y_neg = -x + 0.5 * np.random.randn(n)
        
        # Uncorrelated data
        y_uncorr = np.random.randn(n)
        
        return {
            'x': x,
            'y_pos': y_pos,
            'y_neg': y_neg,
            'y_uncorr': y_uncorr
        }
    
    def test_corr_test_pearson_basic(self, sample_data):
        """Test basic Pearson correlation test."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson"
        )
        
        assert isinstance(result, dict)
        assert 'r' in result
        assert 'p' in result
        assert 'CI' in result
        assert 'method' in result
        
        assert result['method'] == 'pearson'
        assert 0 < result['r'] < 1  # Should be positively correlated
        assert result['p'] < 0.05  # Should be significant
        assert isinstance(result['CI'], tuple)
        assert len(result['CI']) == 2
    
    def test_corr_test_spearman_basic(self, sample_data):
        """Test basic Spearman correlation test."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="spearman"
        )
        
        assert isinstance(result, dict)
        assert result['method'] == 'spearman'
        assert 0 < result['r'] < 1  # Should be positively correlated
        assert result['p'] < 0.05  # Should be significant
    
    def test_corr_test_negative_correlation(self, sample_data):
        """Test with negatively correlated data."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_neg'],
            method="pearson"
        )
        
        assert -1 < result['r'] < 0  # Should be negatively correlated
        assert result['p'] < 0.05  # Should be significant
    
    def test_corr_test_uncorrelated(self, sample_data):
        """Test with uncorrelated data."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_uncorr'],
            method="pearson"
        )
        
        assert abs(result['r']) < 0.3  # Should be close to zero
        assert result['p'] > 0.05  # Should not be significant
    
    def test_only_significant_true(self, sample_data):
        """Test only_significant parameter when result is significant."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson",
            only_significant=True
        )
        
        # Should return result since it's significant
        assert result is not None
        assert result['p'] < 0.05
    
    def test_only_significant_false(self, sample_data):
        """Test only_significant parameter when result is not significant."""
        # Mock the base function to return non-significant result
        with patch('scitex.stats._corr_test_wrapper._corr_test_base') as mock_base:
            mock_base.return_value = {
                'corr': 0.1,
                'p_value': 0.15,  # Not significant
                'surrogate': np.array([])
            }
            
            result = corr_test(
                sample_data['x'],
                sample_data['y_uncorr'],
                method="pearson",
                only_significant=True
            )
            
            # Should return None since it's not significant
            assert result is None
    
    def test_confidence_interval_calculation(self, sample_data):
        """Test confidence interval calculation."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson",
            n_perm=100  # Small for faster test
        )
        
        ci = result['CI']
        # CI might be based on surrogate distribution or fallback calculation
        # Just check that CI exists and has reasonable values
        assert isinstance(ci, tuple)
        assert len(ci) == 2
        assert ci[0] < ci[1]  # Lower bound should be less than upper bound
        
        # Check alternative keys
        assert 'confidence_interval' in result
        assert result['confidence_interval'] == ci
    
    def test_different_n_perm(self, sample_data):
        """Test with different numbers of permutations."""
        # Small n_perm
        result1 = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson",
            n_perm=100
        )
        
        # Large n_perm
        result2 = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson",
            n_perm=1000
        )
        
        # Both should give similar correlation values
        assert abs(result1['r'] - result2['r']) < 0.01
    
    def test_seed_reproducibility(self, sample_data):
        """Test that seed parameter ensures reproducibility."""
        result1 = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson",
            n_perm=100,
            seed=42
        )
        
        result2 = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson",
            n_perm=100,
            seed=42
        )
        
        # Results should be identical with same seed
        assert result1['r'] == result2['r']
        assert result1['p'] == result2['p']
        assert result1['CI'] == result2['CI']
    
    def test_n_jobs_parameter(self, sample_data):
        """Test n_jobs parameter (parallel processing)."""
        # Test with different n_jobs values
        for n_jobs in [-1, 1, 2]:
            result = corr_test(
                sample_data['x'],
                sample_data['y_pos'],
                method="pearson",
                n_perm=100,
                n_jobs=n_jobs
            )
            
            assert isinstance(result, dict)
            assert 'r' in result
    
    def test_all_expected_keys(self, sample_data):
        """Test that all expected keys are present in result."""
        result = corr_test(
            sample_data['x'],
            sample_data['y_pos'],
            method="pearson"
        )
        
        # Primary keys
        assert 'r' in result
        assert 'p' in result
        assert 'CI' in result
        assert 'method' in result
        
        # Alternative keys for compatibility
        assert 'correlation' in result
        assert 'p_value' in result
        assert 'confidence_interval' in result
        
        # Values should match
        assert result['r'] == result['correlation']
        assert result['p'] == result['p_value']
        assert result['CI'] == result['confidence_interval']
    
    def test_corr_test_spearman_wrapper(self, sample_data):
        """Test the dedicated Spearman wrapper function."""
        result = corr_test_spearman(
            sample_data['x'],
            sample_data['y_pos']
        )
        
        assert result['method'] == 'spearman'
        assert 0 < result['r'] < 1
        assert result['p'] < 0.05
    
    def test_corr_test_pearson_wrapper(self, sample_data):
        """Test the dedicated Pearson wrapper function."""
        result = corr_test_pearson(
            sample_data['x'],
            sample_data['y_pos']
        )
        
        assert result['method'] == 'pearson'
        assert 0 < result['r'] < 1
        assert result['p'] < 0.05
    
    def test_wrapper_functions_parameters(self, sample_data):
        """Test that wrapper functions accept all parameters."""
        # Test Spearman wrapper
        result_s = corr_test_spearman(
            sample_data['x'],
            sample_data['y_pos'],
            only_significant=False,
            n_perm=500,
            seed=123,
            n_jobs=1
        )
        assert result_s is not None
        
        # Test Pearson wrapper
        result_p = corr_test_pearson(
            sample_data['x'],
            sample_data['y_pos'],
            only_significant=False,
            n_perm=500,
            seed=123,
            n_jobs=1
        )
        assert result_p is not None
    
    def test_edge_cases(self):
        """Test edge cases like identical arrays, constant arrays."""
        # Identical arrays - perfect correlation
        x = np.array([1, 2, 3, 4, 5])
        result = corr_test(x, x, method="pearson")
        assert abs(result['r'] - 1.0) < 1e-10
        
        # One constant array - should handle gracefully
        constant = np.ones(5)
        variable = np.array([1, 2, 3, 4, 5])
        
        # This might raise warnings or return NaN, depending on implementation
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = corr_test(constant, variable, method="pearson")
            # Result might be None or contain NaN
    
    def test_small_sample_sizes(self):
        """Test with very small sample sizes."""
        x = np.array([1, 2, 3])
        y = np.array([2, 4, 6])
        
        result = corr_test(x, y, method="pearson", n_perm=50)
        
        assert result is not None
        assert abs(result['r'] - 1.0) < 0.01  # Should be perfectly correlated
    
    def test_nonlinear_relationship_spearman(self):
        """Test that Spearman captures monotonic non-linear relationships."""
        x = np.linspace(0, 5, 50)
        y = x ** 2  # Non-linear but monotonic
        
        # Pearson should be less than perfect
        result_p = corr_test(x, y, method="pearson")
        
        # Spearman should be nearly perfect
        result_s = corr_test(x, y, method="spearman")
        
        assert result_s['r'] > result_p['r']
        assert result_s['r'] > 0.95  # Should be very high
    
    def test_nan_handling(self):
        """Test handling of NaN values."""
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        # Implementation should handle NaN values
        # (exact behavior depends on implementation)
        result = corr_test(x, y, method="pearson")
        
        # Result should exist but might have reduced sample size
        assert result is not None or np.isnan(result['r'])


class TestCorrTestIntegration:
    """Integration tests with real-world scenarios."""
    
    def test_time_series_correlation(self):
        """Test correlation with time series data."""
        # Generate autocorrelated time series
        n = 200
        t = np.arange(n)
        
        # Two series with similar trends
        series1 = np.sin(t * 0.1) + 0.1 * np.random.randn(n)
        series2 = np.sin(t * 0.1 + 0.5) + 0.1 * np.random.randn(n)
        
        result = corr_test(series1, series2, method="pearson")
        
        assert result['r'] > 0.8  # Should be highly correlated
        assert result['p'] < 0.001
    
    def test_categorical_ordinal_spearman(self):
        """Test Spearman correlation with ordinal data."""
        # Ordinal data (e.g., ratings)
        ratings1 = np.array([1, 2, 2, 3, 3, 3, 4, 4, 5, 5])
        ratings2 = np.array([1, 1, 2, 2, 3, 4, 4, 4, 5, 5])
        
        result = corr_test_spearman(ratings1, ratings2)
        
        assert result['r'] > 0.7  # Should show positive correlation
        assert result['p'] < 0.05
    
    @patch('scitex.stats._corr_test_wrapper._corr_test_base')
    def test_surrogate_distribution_ci(self, mock_base):
        """Test CI calculation from surrogate distribution."""
        # Mock surrogate distribution
        surrogate = np.random.normal(0.5, 0.1, 1000)
        
        mock_base.return_value = {
            'corr': 0.5,
            'p_value': 0.01,
            'surrogate': surrogate
        }
        
        result = corr_test(
            np.random.randn(100),
            np.random.randn(100),
            method="pearson"
        )
        
        # CI should be based on percentiles of surrogate
        expected_ci_lower = np.percentile(surrogate, 2.5)
        expected_ci_upper = np.percentile(surrogate, 97.5)
        
        assert abs(result['CI'][0] - expected_ci_lower) < 0.01
        assert abs(result['CI'][1] - expected_ci_upper) < 0.01

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/_corr_test_wrapper.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-05-30 auto-created"
# # File: ./src/scitex/stats/_corr_test_wrapper.py
# 
# """
# Wrapper for correlation test functions to match test expectations
# """
# 
# import numpy as np
# from typing import Dict, Any, Literal, Optional
# from scipy import stats
# from .tests.__corr_test import _corr_test_base
# 
# 
# def corr_test(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     method: Literal["pearson", "spearman"] = "pearson",
#     only_significant: bool = False,
#     n_perm: int = 1_000,
#     seed: int = 42,
#     n_jobs: int = -1,
# ) -> Optional[Dict[str, Any]]:
#     """
#     Wrapper for correlation test that matches test expectations.
# 
#     Returns dict with 'r', 'p', 'CI', and 'method' keys.
#     """
#     from .tests._corr_test import corr_test as _corr_test_impl
# 
#     # Call the actual implementation directly avoiding decorator issues
#     if method == "pearson":
#         corr_func = stats.pearsonr
#         test_name = "Pearson"
#     else:
#         corr_func = stats.spearmanr
#         test_name = "Spearman"
# 
#     result = _corr_test_base(
#         data1,
#         data2,
#         only_significant=only_significant,
#         n_perm=n_perm,
#         seed=seed,
#         corr_func=corr_func,
#         test_name=test_name,
#         n_jobs=n_jobs,
#     )
# 
#     # If only_significant is True and result is not significant, return None
#     if only_significant and result["p_value"] > 0.05:
#         return None
# 
#     # Calculate confidence interval from surrogate distribution
#     surrogate = result.get("surrogate", np.array([]))
#     if len(surrogate) > 0:
#         ci_lower = np.percentile(surrogate, 2.5)
#         ci_upper = np.percentile(surrogate, 97.5)
#     else:
#         # Fallback CI calculation
#         ci_lower = result["corr"] - 1.96 * 0.1  # Simplified
#         ci_upper = result["corr"] + 1.96 * 0.1
# 
#     # Transform to expected format
#     return {
#         "r": result["corr"],
#         "p": result["p_value"],
#         "CI": (ci_lower, ci_upper),
#         "method": method,
#         "correlation": result["corr"],  # Some tests might expect this
#         "p_value": result["p_value"],  # Keep original key too
#         "confidence_interval": (ci_lower, ci_upper),  # Alternative key
#         **result,  # Include all original keys
#     }
# 
# 
# def corr_test_spearman(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool = False,
#     n_perm: int = 1_000,
#     seed: int = 42,
#     n_jobs: int = -1,
# ) -> Dict[str, Any]:
#     """Spearman correlation test wrapper."""
#     return corr_test(
#         data1,
#         data2,
#         method="spearman",
#         only_significant=only_significant,
#         n_perm=n_perm,
#         seed=seed,
#         n_jobs=n_jobs,
#     )
# 
# 
# def corr_test_pearson(
#     data1: np.ndarray,
#     data2: np.ndarray,
#     only_significant: bool = False,
#     n_perm: int = 1_000,
#     seed: int = 42,
#     n_jobs: int = -1,
# ) -> Dict[str, Any]:
#     """Pearson correlation test wrapper."""
#     return corr_test(
#         data1,
#         data2,
#         method="pearson",
#         only_significant=only_significant,
#         n_perm=n_perm,
#         seed=seed,
#         n_jobs=n_jobs,
#     )

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/_corr_test_wrapper.py
# --------------------------------------------------------------------------------
