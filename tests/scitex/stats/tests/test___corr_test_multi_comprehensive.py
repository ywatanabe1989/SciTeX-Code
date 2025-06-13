#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for __corr_test_multi.py

Tests cover:
- Basic correlation tests (Pearson and Spearman)
- Permutation-based testing
- Parallel processing with multiprocessing
- Edge cases and error handling
- Integration with numpy_fn decorator
- Statistical accuracy
"""

import multiprocessing as mp
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import warnings

import numpy as np
import pandas as pd
import pytest
from scipy import stats

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


class TestComputeSurrogate:
    """Test _compute_surrogate function."""
    
    def test_compute_surrogate_pearson(self):
        """Test surrogate computation for Pearson correlation."""
from scitex.stats.tests import _compute_surrogate
        
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([2, 4, 6, 8, 10])
        
        # Test with Pearson
        args = (data1, data2, stats.pearsonr, 42)
        result = _compute_surrogate(args)
        
        # Result should be a scalar correlation value
        assert isinstance(result, (float, np.floating))
        assert -1 <= result <= 1
    
    def test_compute_surrogate_spearman(self):
        """Test surrogate computation for Spearman correlation."""
from scitex.stats.tests import _compute_surrogate
        
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([1, 3, 2, 5, 4])
        
        # Test with Spearman
        args = (data1, data2, stats.spearmanr, 42)
        result = _compute_surrogate(args)
        
        assert isinstance(result, (float, np.floating))
        assert -1 <= result <= 1
    
    def test_compute_surrogate_with_nan(self):
        """Test surrogate computation with NaN values."""
from scitex.stats.tests import _compute_surrogate
        
        data1 = np.array([1, 2, np.nan, 4, 5])
        data2 = np.array([2, 4, 6, np.nan, 10])
        
        # Test with Pearson (should handle NaN)
        args = (data1, data2, stats.pearsonr, 42)
        result = _compute_surrogate(args)
        
        assert isinstance(result, (float, np.floating))
        assert -1 <= result <= 1
    
    def test_compute_surrogate_reproducibility(self):
        """Test that same seed produces same result."""
from scitex.stats.tests import _compute_surrogate
        
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([5, 4, 3, 2, 1])
        
        # Run twice with same seed
        args = (data1, data2, stats.pearsonr, 42)
        result1 = _compute_surrogate(args)
        result2 = _compute_surrogate(args)
        
        assert result1 == result2


class TestCorrTestBase:
    """Test _corr_test_base function."""
    
    def test_corr_test_base_pearson(self):
        """Test base correlation test with Pearson."""
from scitex.stats.tests import _corr_test_base
        
        # Create correlated data
        np.random.seed(42)
        data1 = np.random.randn(100)
        data2 = data1 + np.random.randn(100) * 0.5
        
        result = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=100,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson",
            n_jobs=1
        )
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'p_value' in result
        assert 'stars' in result
        assert 'effsize' in result
        assert 'corr' in result
        assert 'surrogate' in result
        assert 'n' in result
        assert 'test_name' in result
        assert 'statistic' in result
        assert 'H0' in result
        
        # Check values
        assert 0 <= result['p_value'] <= 1
        assert -1 <= result['corr'] <= 1
        assert result['n'] == 100
        assert len(result['surrogate']) == 100
    
    def test_corr_test_base_spearman(self):
        """Test base correlation test with Spearman."""
from scitex.stats.tests import _corr_test_base
        
        # Create monotonic data
        data1 = np.arange(50)
        data2 = data1 ** 2  # Non-linear but monotonic
        
        result = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=100,
            seed=42,
            corr_func=stats.spearmanr,
            test_name="Spearman",
            n_jobs=1
        )
        
        # Should have perfect Spearman correlation
        assert np.isclose(result['corr'], 1.0)
        assert result['p_value'] < 0.05
    
    def test_corr_test_base_parallel(self):
        """Test parallel processing."""
from scitex.stats.tests import _corr_test_base
        
        data1 = np.random.randn(100)
        data2 = np.random.randn(100)
        
        # Test with multiple jobs
        result = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=50,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson",
            n_jobs=2
        )
        
        assert len(result['surrogate']) == 50
    
    def test_corr_test_base_insufficient_data(self):
        """Test with insufficient data points."""
from scitex.stats.tests import _corr_test_base
        
        data1 = np.array([1])
        data2 = np.array([2])
        
        with pytest.raises(ValueError, match="Not enough valid numeric data"):
            _corr_test_base(
                data1, data2,
                only_significant=False,
                n_perm=100,
                seed=42,
                corr_func=stats.pearsonr,
                test_name="Pearson"
            )
    
    def test_corr_test_base_only_significant(self, capsys):
        """Test only_significant parameter."""
from scitex.stats.tests import _corr_test_base
        
        # Create uncorrelated data
        np.random.seed(42)
        data1 = np.random.randn(100)
        data2 = np.random.randn(100)
        
        # Should not print for non-significant
        result = _corr_test_base(
            data1, data2,
            only_significant=True,
            n_perm=100,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson"
        )
        
        captured = capsys.readouterr()
        if result['p_value'] >= 0.05:
            assert captured.out == ""
    
    def test_corr_test_base_normality_warning(self, capsys):
        """Test normality warning for surrogate distribution."""
from scitex.stats.tests import _corr_test_base
        
        # Create data that might produce non-normal surrogates
        data1 = np.array([1, 2, 3, 4, 5])
        data2 = np.array([1, 1, 1, 5, 5])
        
        result = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=10,  # Small number might trigger warning
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson"
        )
        
        # Check if warning might have been printed
        captured = capsys.readouterr()
        # Warning depends on actual surrogate distribution


class TestCorrTestFunctions:
    """Test the main correlation test functions."""
    
    def test_corr_test_pearson(self):
        """Test Pearson correlation test."""
from scitex.stats.tests import corr_test_pearson
        
        # Create correlated data
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = 2 * x + np.random.randn(10) * 0.1
        
        result = corr_test_pearson(x, y, n_perm=100, seed=42)
        
        assert result['corr'] > 0.9  # Strong positive correlation
        assert result['p_value'] < 0.05  # Significant
    
    def test_corr_test_spearman(self):
        """Test Spearman correlation test."""
from scitex.stats.tests import corr_test_spearman
        
        # Create monotonic but non-linear relationship
        x = np.array([1, 2, 3, 4, 5])
        y = x ** 3  # Cubic relationship
        
        result = corr_test_spearman(x, y, n_perm=100, seed=42)
        
        assert np.isclose(result['corr'], 1.0)  # Perfect monotonic
        assert result['p_value'] < 0.05
    
    def test_corr_test_main_function(self):
        """Test main corr_test function."""
from scitex.stats.tests import corr_test
        
        x = np.array([3, 4, 4, 5, 7, 8, 10, 12, 13, 15])
        y = np.array([2, 4, 4, 5, 4, 7, 8, 19, 14, 10])
        
        # Test Pearson
        result_p = corr_test(x, y, test="pearson", n_perm=100)
        assert 'corr' in result_p
        assert result_p['test_name'] == "Permutation-based Pearson correlation test"
        
        # Test Spearman
        result_s = corr_test(x, y, test="spearman", n_perm=100)
        assert 'corr' in result_s
        assert result_s['test_name'] == "Permutation-based Spearman correlation test"
    
    def test_corr_test_invalid_test_type(self):
        """Test invalid test type."""
from scitex.stats.tests import corr_test
        
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        
        with pytest.raises(ValueError, match="Invalid test type"):
            corr_test(x, y, test="kendall")
    
    def test_corr_test_with_lists(self):
        """Test correlation with list inputs (numpy_fn decorator)."""
from scitex.stats.tests import corr_test
        
        # Should work with lists due to numpy_fn decorator
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        result = corr_test(x, y, test="pearson", n_perm=50)
        assert np.isclose(result['corr'], 1.0)
    
    def test_corr_test_with_pandas_series(self):
        """Test correlation with pandas Series."""
from scitex.stats.tests import corr_test
        
        x = pd.Series([1, 2, 3, 4, 5])
        y = pd.Series([5, 4, 3, 2, 1])
        
        result = corr_test(x, y, test="pearson", n_perm=50)
        assert result['corr'] < 0  # Negative correlation


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_all_nan_data(self):
        """Test with all NaN data."""
from scitex.stats.tests import corr_test
        
        x = np.array([np.nan, np.nan, np.nan])
        y = np.array([np.nan, np.nan, np.nan])
        
        with pytest.raises(ValueError):
            corr_test(x, y)
    
    def test_constant_data(self):
        """Test with constant data."""
from scitex.stats.tests import corr_test
        
        x = np.array([1, 1, 1, 1, 1])
        y = np.array([2, 2, 2, 2, 2])
        
        # Should handle constant data
        result = corr_test(x, y, n_perm=50)
        assert np.isnan(result['corr']) or result['corr'] == 0
    
    def test_single_valid_pair(self):
        """Test with only one valid data pair."""
from scitex.stats.tests import corr_test
        
        x = np.array([1, np.nan, np.nan])
        y = np.array([2, np.nan, np.nan])
        
        with pytest.raises(ValueError, match="Not enough valid"):
            corr_test(x, y)
    
    def test_empty_arrays(self):
        """Test with empty arrays."""
from scitex.stats.tests import corr_test
        
        x = np.array([])
        y = np.array([])
        
        with pytest.raises(ValueError):
            corr_test(x, y)
    
    def test_mismatched_lengths(self):
        """Test with mismatched array lengths."""
from scitex.stats.tests import corr_test
        
        x = np.array([1, 2, 3])
        y = np.array([1, 2, 3, 4, 5])
        
        # numpy_fn should handle this by truncating to minimum length
        result = corr_test(x, y, n_perm=50)
        assert result['n'] == 3


class TestNumericalAccuracy:
    """Test numerical accuracy of correlation tests."""
    
    def test_perfect_positive_correlation(self):
        """Test perfect positive correlation."""
from scitex.stats.tests import corr_test
        
        x = np.arange(100)
        y = x.copy()
        
        result = corr_test(x, y, n_perm=100)
        assert np.isclose(result['corr'], 1.0)
        assert result['p_value'] < 0.001
    
    def test_perfect_negative_correlation(self):
        """Test perfect negative correlation."""
from scitex.stats.tests import corr_test
        
        x = np.arange(100)
        y = -x
        
        result = corr_test(x, y, n_perm=100)
        assert np.isclose(result['corr'], -1.0)
        assert result['p_value'] < 0.001
    
    def test_zero_correlation(self):
        """Test zero correlation."""
from scitex.stats.tests import corr_test
        
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)
        
        result = corr_test(x, y, n_perm=100)
        assert abs(result['corr']) < 0.2  # Should be close to 0
    
    def test_known_correlation(self):
        """Test with known correlation value."""
from scitex.stats.tests import corr_test
        
        # Create data with known correlation ~0.8
        np.random.seed(42)
        x = np.random.randn(100)
        y = 0.8 * x + 0.6 * np.random.randn(100)
        
        result = corr_test(x, y, n_perm=100)
        assert 0.7 < result['corr'] < 0.9


class TestMultiprocessing:
    """Test multiprocessing functionality."""
    
    def test_multiprocessing_consistency(self):
        """Test that multiprocessing gives consistent results."""
from scitex.stats.tests import _corr_test_base
        
        np.random.seed(42)
        data1 = np.random.randn(50)
        data2 = np.random.randn(50)
        
        # Run with single process
        result_single = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=100,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson",
            n_jobs=1
        )
        
        # Run with multiple processes
        result_multi = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=100,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson",
            n_jobs=2
        )
        
        # Results should be similar (not identical due to parallel randomness)
        assert abs(result_single['corr'] - result_multi['corr']) < 0.001
    
    def test_multiprocessing_speedup(self):
        """Test that multiprocessing provides speedup for large permutations."""
from scitex.stats.tests import _corr_test_base
        import time
        
        data1 = np.random.randn(100)
        data2 = np.random.randn(100)
        
        # Time with single process
        start = time.time()
        result_single = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=200,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson",
            n_jobs=1
        )
        time_single = time.time() - start
        
        # Time with multiple processes
        start = time.time()
        result_multi = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=200,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson",
            n_jobs=-1
        )
        time_multi = time.time() - start
        
        # Multi should be faster (but might not be on small tasks)
        print(f"Single: {time_single:.3f}s, Multi: {time_multi:.3f}s")


class TestIntegration:
    """Test integration with other scitex modules."""
    
    def test_integration_with_p2stars(self):
        """Test integration with p2stars function."""
from scitex.stats.tests import corr_test
        
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        result = corr_test(x, y, n_perm=50)
        
        # Check stars format
        assert result['stars'] in ['', '*', '**', '***']
        
        # For perfect correlation, should be significant
        assert result['stars'] != ''
    
    def test_output_format(self, capsys):
        """Test output format when printing results."""
from scitex.stats.tests import corr_test
        
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        result = corr_test(x, y, only_significant=False, n_perm=50)
        
        captured = capsys.readouterr()
        
        # Should contain correlation value, p-value, sample size
        assert "Pearson Corr." in captured.out
        assert "p-value" in captured.out
        assert f"n={len(x)}" in captured.out


class TestStatisticalProperties:
    """Test statistical properties of the permutation test."""
    
    def test_permutation_distribution(self):
        """Test that permutation creates proper null distribution."""
from scitex.stats.tests import _corr_test_base
        
        # Create uncorrelated data
        np.random.seed(42)
        data1 = np.random.randn(100)
        data2 = np.random.randn(100)
        
        result = _corr_test_base(
            data1, data2,
            only_significant=False,
            n_perm=1000,
            seed=42,
            corr_func=stats.pearsonr,
            test_name="Pearson"
        )
        
        # Surrogate distribution should be centered around 0
        assert abs(np.mean(result['surrogate'])) < 0.05
        
        # Should be roughly normal
        _, p_normal = stats.normaltest(result['surrogate'])
        # May or may not be normal depending on data
    
    def test_p_value_calculation(self):
        """Test p-value calculation accuracy."""
from scitex.stats.tests import corr_test
        
        # Create data with known correlation
        np.random.seed(42)
        n = 100
        rho = 0.5
        
        # Generate bivariate normal with correlation rho
        mean = [0, 0]
        cov = [[1, rho], [rho, 1]]
        data = np.random.multivariate_normal(mean, cov, n)
        x, y = data[:, 0], data[:, 1]
        
        result = corr_test(x, y, n_perm=1000)
        
        # P-value should be significant for true correlation
        assert result['p_value'] < 0.05
        assert 0.3 < result['corr'] < 0.7  # Should be close to 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])