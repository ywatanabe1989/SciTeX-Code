#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-11 03:50:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__ci.py

"""Comprehensive tests for confidence interval calculation function.

This module tests the ci() function which calculates 95% confidence intervals
for data arrays using the formula: CI = 1.96 * std / sqrt(n)
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import warnings
from typing import Union, List, Optional
import scipy.stats as stats

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

    from scitex.gen import ci


class TestConfidenceIntervalBasic:
    """Basic functionality tests for confidence interval calculation."""

    def test_ci_basic_1d(self):
        """Test CI calculation on 1D array."""
        # Create data with known properties
        data = np.array([1, 2, 3, 4, 5])
        result = ci(data)

        # CI = 1.96 * std / sqrt(n)
        expected_std = np.std(data)
        expected_ci = 1.96 * expected_std / np.sqrt(5)

        assert np.isclose(result, expected_ci)

    def test_ci_with_nan(self):
        """Test CI calculation with NaN values."""
        data = np.array([1, 2, np.nan, 4, 5, np.nan])
        result = ci(data)

        # Only non-NaN values should be used
        valid_data = data[~np.isnan(data)]
        expected_std = np.std(valid_data)
        expected_ci = 1.96 * expected_std / np.sqrt(len(valid_data))

        assert np.isclose(result, expected_ci)

    def test_ci_all_nan(self):
        """Test CI calculation when all values are NaN."""
        data = np.array([np.nan, np.nan, np.nan])

        # Should handle gracefully (likely return NaN or raise)
        with pytest.warns(RuntimeWarning):  # Division by zero warning
            result = ci(data)
            assert np.isnan(result) or np.isinf(result)

    def test_ci_single_value(self):
        """Test CI calculation with single value."""
        data = np.array([5.0])
        result = ci(data)

        # Standard deviation of single value is 0
        # CI = 1.96 * 0 / sqrt(1) = 0
        assert result == 0.0

    def test_ci_constant_values(self):
        """Test CI calculation with constant values."""
        data = np.array([3.0, 3.0, 3.0, 3.0])
        result = ci(data)

        # Standard deviation of constant values is 0
        assert result == 0.0

    def test_ci_2d_array_no_axis(self):
        """Test CI calculation on 2D array without specifying axis."""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        result = ci(data)

        # Should compute CI over all elements
        flat_data = data.flatten()
        expected_std = np.std(flat_data)
        expected_ci = 1.96 * expected_std / np.sqrt(len(flat_data))

        assert np.isclose(result, expected_ci)

    def test_ci_2d_array_axis_0(self):
        """Test CI calculation along axis 0 - Note: axis doesn't work properly with NaN filtering."""
        # The current implementation flattens data after NaN filtering,
        # so axis parameter doesn't work as expected for 2D arrays
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Without NaN values, the function still flattens the data
        result = ci(data, axis=0)

        # Result is scalar because data[indi] flattens the array
        assert np.isscalar(result)

    def test_ci_2d_array_axis_limitation(self):
        """Test that axis parameter has limitations due to implementation."""
        # The implementation uses xx[indi] which flattens the array
        # This is a known limitation of the current implementation
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # When axis=1 is specified on flattened data, it raises error
        from numpy.exceptions import AxisError

        with pytest.raises(AxisError):
            ci(data, axis=1)

    def test_ci_mixed_nan_2d(self):
        """Test CI with NaN values in 2D array."""
        data = np.array([[1, np.nan, 3], [4, 5, np.nan], [7, 8, 9]])
        result = ci(data)

        # Should only use non-NaN values
        valid_data = data[~np.isnan(data)]
        expected_ci = 1.96 * np.std(valid_data) / np.sqrt(len(valid_data))

        assert np.isclose(result, expected_ci)

    def test_ci_negative_values(self):
        """Test CI calculation with negative values."""
        data = np.array([-2, -1, 0, 1, 2])
        result = ci(data)

        # CI should still be positive (it's a measure of spread)
        assert result > 0

        expected_std = np.std(data)
        expected_ci = 1.96 * expected_std / np.sqrt(5)
        assert np.isclose(result, expected_ci)

    def test_ci_large_sample(self):
        """Test CI calculation with large sample."""
        np.random.seed(42)
        data = np.random.normal(100, 15, 1000)
        result = ci(data)

        # For large samples, CI should be relatively small
        expected_ci = 1.96 * np.std(data) / np.sqrt(1000)
        assert np.isclose(result, expected_ci, rtol=1e-5)

    def test_ci_empty_array(self):
        """Test CI calculation with empty array."""
        data = np.array([])

        # Should handle empty array gracefully
        with pytest.warns(RuntimeWarning):  # Mean of empty slice warning
            result = ci(data)
            assert np.isnan(result)

    @pytest.mark.parametrize("confidence", [0.90, 0.95, 0.99])
    def test_ci_different_confidence_levels(self, confidence):
        """Test that current implementation uses 95% confidence (z=1.96)."""
        data = np.array([1, 2, 3, 4, 5])
        result = ci(data)

        # Current implementation uses fixed 1.96 (95% confidence)
        expected_ci = 1.96 * np.std(data) / np.sqrt(5)
        assert np.isclose(result, expected_ci)

    def test_ci_dtype_preservation(self):
        """Test that CI preserves appropriate data type."""
        # Test with float32
        data_f32 = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        result_f32 = ci(data_f32)
        assert isinstance(result_f32, (np.floating, float))

        # Test with int
        data_int = np.array([1, 2, 3, 4, 5], dtype=np.int32)
        result_int = ci(data_int)
        assert isinstance(result_int, (np.floating, float))  # Should be float


class TestConfidenceIntervalStatistical:
    """Statistical correctness tests for CI calculation."""
    
    def test_ci_normal_distribution(self):
        """Test CI for normally distributed data."""
        np.random.seed(42)
        # Generate data from known distribution
        true_mean = 50
        true_std = 10
        n_samples = 100
        
        data = np.random.normal(true_mean, true_std, n_samples)
        result = ci(data)
        
        # Theoretical CI for sample
        theoretical_ci = 1.96 * true_std / np.sqrt(n_samples)
        empirical_ci = 1.96 * np.std(data) / np.sqrt(n_samples)
        
        # Should be close to empirical calculation
        assert np.isclose(result, empirical_ci)
        
        # Should be reasonably close to theoretical
        assert abs(result - theoretical_ci) < theoretical_ci * 0.2  # Within 20%
    
    def test_ci_confidence_level_interpretation(self):
        """Test interpretation of 95% confidence interval."""
        np.random.seed(42)
        true_mean = 100
        true_std = 15
        n_samples = 30
        
        # Generate many samples and check CI coverage
        n_simulations = 1000
        ci_contains_mean = 0
        
        for _ in range(n_simulations):
            sample = np.random.normal(true_mean, true_std, n_samples)
            sample_mean = np.mean(sample)
            sample_ci = ci(sample)
            
            # Check if true mean is within CI of sample mean
            if abs(sample_mean - true_mean) <= sample_ci:
                ci_contains_mean += 1
        
        # Should be approximately 95%
        coverage = ci_contains_mean / n_simulations
        assert 0.93 < coverage < 0.97  # Allow some variance
    
    def test_ci_vs_standard_error(self):
        """Test relationship between CI and standard error."""
        data = np.array([10, 12, 14, 16, 18, 20])
        
        result = ci(data)
        
        # Standard error
        se = np.std(data) / np.sqrt(len(data))
        
        # CI should be 1.96 * SE for 95% confidence
        assert np.isclose(result, 1.96 * se)
    
    def test_ci_sample_size_effect(self):
        """Test effect of sample size on CI width."""
        np.random.seed(42)
        base_data = np.random.normal(50, 10, 1000)
        
        # Test different sample sizes
        sample_sizes = [10, 50, 100, 500]
        ci_values = []
        
        for n in sample_sizes:
            sample = base_data[:n]
            ci_values.append(ci(sample))
        
        # CI should decrease with increasing sample size
        for i in range(len(ci_values) - 1):
            assert ci_values[i] > ci_values[i + 1]
        
        # Should follow 1/sqrt(n) relationship approximately
        for i, n in enumerate(sample_sizes):
            expected_ratio = np.sqrt(sample_sizes[0] / n)
            actual_ratio = ci_values[0] / ci_values[i]
            assert abs(actual_ratio - expected_ratio) < 0.3  # Rough approximation


class TestConfidenceIntervalEdgeCases:
    """Edge case tests for CI calculation."""
    
    def test_ci_infinite_values(self):
        """Test CI with infinite values."""
        data = np.array([1, 2, np.inf, 4, 5])
        
        # Should handle infinity (likely return nan or inf)
        result = ci(data)
        assert np.isnan(result) or np.isinf(result)
    
    def test_ci_very_large_values(self):
        """Test CI with very large values."""
        data = np.array([1e15, 2e15, 3e15, 4e15, 5e15])
        result = ci(data)
        
        # Should compute correctly even with large values
        expected_std = np.std(data)
        expected_ci = 1.96 * expected_std / np.sqrt(5)
        
        assert np.isclose(result, expected_ci, rtol=1e-10)
    
    def test_ci_very_small_values(self):
        """Test CI with very small values."""
        data = np.array([1e-15, 2e-15, 3e-15, 4e-15, 5e-15])
        result = ci(data)
        
        # Should compute correctly even with small values
        expected_std = np.std(data)
        expected_ci = 1.96 * expected_std / np.sqrt(5)
        
        assert np.isclose(result, expected_ci, rtol=1e-10)
    
    def test_ci_mixed_finite_infinite(self):
        """Test CI with mix of finite and infinite values."""
        data = np.array([1, 2, np.inf, 4, -np.inf, 6])
        
        result = ci(data)
        assert np.isnan(result) or np.isinf(result)
    
    def test_ci_near_zero_variance(self):
        """Test CI with near-zero variance."""
        # Values very close but not identical
        data = np.array([1.0, 1.0 + 1e-15, 1.0 - 1e-15, 1.0 + 2e-15])
        result = ci(data)
        
        # Should be very small but not exactly zero
        assert result > 0
        assert result < 1e-10
    
    def test_ci_alternating_pattern(self):
        """Test CI with alternating positive/negative values."""
        data = np.array([1, -1, 1, -1, 1, -1, 1, -1])
        result = ci(data)
        
        # Mean is 0 but variance is high
        expected_std = np.std(data)
        expected_ci = 1.96 * expected_std / np.sqrt(8)
        
        assert np.isclose(result, expected_ci)


class TestConfidenceIntervalRobustness:
    """Robustness tests for CI calculation."""
    
    def test_ci_outliers_effect(self):
        """Test effect of outliers on CI."""
        # Normal data
        normal_data = np.array([10, 11, 12, 13, 14, 15, 16])
        normal_ci = ci(normal_data)
        
        # Data with outlier
        outlier_data = np.array([10, 11, 12, 13, 14, 15, 100])
        outlier_ci = ci(outlier_data)
        
        # CI should be much larger with outlier
        assert outlier_ci > normal_ci * 3
    
    def test_ci_data_ordering(self):
        """Test that data ordering doesn't affect CI."""
        data = np.array([1, 5, 3, 9, 2, 7, 4, 8, 6])
        
        # Original
        result1 = ci(data)
        
        # Sorted
        result2 = ci(np.sort(data))
        
        # Reversed
        result3 = ci(data[::-1])
        
        # Random permutation
        np.random.seed(42)
        shuffled = data.copy()
        np.random.shuffle(shuffled)
        result4 = ci(shuffled)
        
        # All should be identical
        assert np.isclose(result1, result2)
        assert np.isclose(result1, result3)
        assert np.isclose(result1, result4)
    
    def test_ci_numerical_stability(self):
        """Test numerical stability with extreme scales."""
        # Very large scale
        large_scale = np.array([1e10, 2e10, 3e10, 4e10, 5e10])
        large_ci = ci(large_scale)
        
        # Normalized version
        normalized = large_scale / 1e10
        normalized_ci = ci(normalized)
        
        # Should scale linearly
        assert np.isclose(large_ci / 1e10, normalized_ci, rtol=1e-10)
    
    def test_ci_precision_loss(self):
        """Test for precision loss with many similar values."""
        # Many values close to 1
        data = np.ones(1000) + np.random.randn(1000) * 1e-10
        result = ci(data)
        
        # Should handle precision correctly
        assert result > 0
        assert result < 1e-8


class TestConfidenceIntervalDataTypes:
    """Test CI with different data types and structures."""
    
    def test_ci_integer_array(self):
        """Test CI with integer arrays."""
        data = np.array([10, 20, 30, 40, 50], dtype=np.int32)
        result = ci(data)
        
        # Should work and return float
        assert isinstance(result, (float, np.floating))
        assert result > 0
    
    def test_ci_boolean_array(self):
        """Test CI with boolean arrays."""
        data = np.array([True, False, True, True, False, True, False])
        result = ci(data)
        
        # Should treat as 0s and 1s
        numeric_data = data.astype(float)
        expected_ci = 1.96 * np.std(numeric_data) / np.sqrt(len(data))
        
        assert np.isclose(result, expected_ci)
    
    def test_ci_mixed_types_error(self):
        """Test CI with mixed types (should convert or error)."""
        # NumPy will try to find common type
        data = np.array([1, 2.5, 3, 4.5, 5])
        result = ci(data)
        
        # Should work with implicit conversion
        assert result > 0
    
    @pytest.mark.skipif(not HAS_PANDAS, reason="pandas not available")
    def test_ci_pandas_series(self):
        """Test CI with pandas Series."""
        data = pd.Series([1, 2, 3, 4, 5, np.nan, 7, 8, 9])
        
        # Convert to numpy array for CI calculation
        result = ci(data.values)
        
        # Should handle NaN correctly
        valid_data = data.dropna().values
        expected_ci = 1.96 * np.std(valid_data) / np.sqrt(len(valid_data))
        
        assert np.isclose(result, expected_ci)
    
    @pytest.mark.skipif(not HAS_TORCH, reason="torch not available")
    def test_ci_torch_tensor(self):
        """Test CI with PyTorch tensors."""
        data = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Convert to numpy for CI calculation
        result = ci(data.numpy())
        
        expected_ci = 1.96 * np.std(data.numpy()) / np.sqrt(5)
        assert np.isclose(result, expected_ci)


class TestConfidenceIntervalMultidimensional:
    """Test CI with multidimensional arrays."""
    
    def test_ci_3d_array(self):
        """Test CI with 3D array."""
        data = np.random.randn(4, 5, 6)
        result = ci(data)
        
        # Current implementation flattens the array
        flat_data = data.flatten()
        expected_ci = 1.96 * np.std(flat_data) / np.sqrt(len(flat_data))
        
        assert np.isclose(result, expected_ci)
    
    def test_ci_high_dimensional(self):
        """Test CI with high-dimensional array."""
        data = np.random.randn(2, 3, 4, 5, 6)
        result = ci(data)
        
        # Should handle by flattening
        flat_data = data.flatten()
        expected_ci = 1.96 * np.std(flat_data) / np.sqrt(len(flat_data))
        
        assert np.isclose(result, expected_ci)
    
    def test_ci_ragged_array_limitation(self):
        """Test CI with ragged arrays (not directly supported)."""
        # Create list of arrays with different lengths
        data = [np.array([1, 2, 3]), np.array([4, 5]), np.array([6, 7, 8, 9])]
        
        # Would need to concatenate first
        concatenated = np.concatenate(data)
        result = ci(concatenated)
        
        assert result > 0


class TestConfidenceIntervalComparison:
    """Compare CI implementation with other methods."""
    
    def test_ci_vs_scipy_sem(self):
        """Compare with scipy's standard error of mean."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
        our_ci = ci(data)
        
        # scipy SEM * 1.96 should equal our CI
        scipy_sem = stats.sem(data, nan_policy='omit')
        scipy_ci = 1.96 * scipy_sem
        
        assert np.isclose(our_ci, scipy_ci)
    
    def test_ci_bootstrap_comparison(self):
        """Compare with bootstrap confidence interval."""
        np.random.seed(42)
        data = np.random.normal(50, 10, 30)
        
        our_ci = ci(data)
        
        # Simple bootstrap CI
        n_bootstrap = 1000
        bootstrap_means = []
        for _ in range(n_bootstrap):
            resample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(resample))
        
        # 95% percentile interval width
        bootstrap_ci_lower = np.percentile(bootstrap_means, 2.5)
        bootstrap_ci_upper = np.percentile(bootstrap_means, 97.5)
        bootstrap_ci_width = (bootstrap_ci_upper - bootstrap_ci_lower) / 2
        
        # Should be in same ballpark
        assert abs(our_ci - bootstrap_ci_width) < our_ci * 0.3  # Within 30%


class TestConfidenceIntervalApplications:
    """Test CI in practical applications."""
    
    def test_ci_time_series(self):
        """Test CI for time series data."""
        # Simulate time series with trend
        t = np.linspace(0, 10, 100)
        signal = 10 + 2 * t + np.random.randn(100) * 3
        
        # Calculate CI for detrended data
        detrended = signal - np.polyval(np.polyfit(t, signal, 1), t)
        result = ci(detrended)
        
        # Should give reasonable CI for noise level
        assert 0.5 < result < 1.5  # Rough expectation
    
    def test_ci_grouped_data(self):
        """Test CI calculation for grouped data."""
        # Simulate grouped data
        group1 = np.random.normal(50, 5, 30)
        group2 = np.random.normal(55, 5, 30)
        group3 = np.random.normal(60, 5, 30)
        
        # Calculate CI for each group
        ci1 = ci(group1)
        ci2 = ci(group2)
        ci3 = ci(group3)
        
        # Should be similar since same variance and sample size
        assert abs(ci1 - ci2) < 1.0
        assert abs(ci2 - ci3) < 1.0
    
    def test_ci_measurement_error(self):
        """Test CI for repeated measurements."""
        # Simulate repeated measurements with error
        true_value = 25.0
        measurement_error = 0.5
        n_measurements = 20
        
        measurements = true_value + np.random.normal(0, measurement_error, n_measurements)
        result = ci(measurements)
        
        # CI should reflect measurement precision
        expected_ci = 1.96 * measurement_error / np.sqrt(n_measurements)
        assert abs(result - expected_ci) < expected_ci * 0.3  # Within 30%


class TestConfidenceIntervalPerformance:
    """Performance tests for CI calculation."""
    
    def test_ci_large_array_performance(self):
        """Test CI performance with large arrays."""
        import time
        
        # Large array
        data = np.random.randn(1_000_000)
        
        start_time = time.time()
        result = ci(data)
        end_time = time.time()
        
        # Should be fast
        assert end_time - start_time < 0.1  # Less than 100ms
        assert result > 0
    
    def test_ci_many_nan_performance(self):
        """Test CI performance with many NaN values."""
        import time
        
        # Array with 90% NaN values
        data = np.random.randn(100_000)
        nan_mask = np.random.rand(100_000) < 0.9
        data[nan_mask] = np.nan
        
        start_time = time.time()
        result = ci(data)
        end_time = time.time()
        
        # Should still be reasonably fast
        assert end_time - start_time < 0.1  # Less than 100ms
        assert result > 0
    
    def test_ci_repeated_calls(self):
        """Test performance of repeated CI calculations."""
        import time
        
        data = np.random.randn(1000)
        
        start_time = time.time()
        for _ in range(10000):
            _ = ci(data)
        end_time = time.time()
        
        # Should handle many calls efficiently
        avg_time = (end_time - start_time) / 10000
        assert avg_time < 0.0001  # Less than 0.1ms per call


class TestConfidenceIntervalValidation:
    """Validation tests for CI calculation."""
    
    def test_ci_mathematical_properties(self):
        """Test mathematical properties of CI."""
        data = np.random.randn(100)
        result = ci(data)
        
        # CI should be non-negative
        assert result >= 0
        
        # CI should be finite for finite data
        assert np.isfinite(result)
        
        # CI should be less than range of data (for reasonable sample)
        data_range = np.ptp(data)
        assert result < data_range
    
    def test_ci_invariance_properties(self):
        """Test invariance properties of CI."""
        data = np.array([1, 2, 3, 4, 5])
        
        # Translation invariance (CI shouldn't change with shift)
        ci_original = ci(data)
        ci_shifted = ci(data + 100)
        assert np.isclose(ci_original, ci_shifted)
        
        # Scale equivariance (CI should scale with data)
        ci_scaled = ci(data * 10)
        assert np.isclose(ci_scaled, ci_original * 10)
    
    def test_ci_consistency_across_versions(self):
        """Test that CI calculation is consistent."""
        # Fixed data for consistency check
        data = np.array([2.5, 3.7, 1.2, 4.8, 3.3, 2.9, 4.1, 3.5, 2.7, 3.9])
        result = ci(data)
        
        # Expected value calculated manually
        std_val = np.std(data)
        n = len(data)
        expected = 1.96 * std_val / np.sqrt(n)
        
        assert np.isclose(result, expected, rtol=1e-10)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_ci.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-06-04 06:55:56 (ywatanabe)"
# # /home/ywatanabe/proj/scitex/src/scitex/gen/_ci.py
# 
# 
# import numpy as np
# 
# 
# def ci(xx, axis=None):
#     indi = ~np.isnan(xx)
#     return 1.96 * (xx[indi]).std(axis=axis) / np.sqrt(indi.sum())

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_ci.py
# --------------------------------------------------------------------------------
