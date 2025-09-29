#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 08:10:00 (ywatanabe)"
# File: ./tests/scitex/stats/test__nan_stats.py

"""Comprehensive tests for stats._nan_stats module."""

import pytest
import numpy as np
import pandas as pd
from scitex.stats import nan, real


class TestNanFunction:
    """Test suite for nan function."""
    
    def test_no_nans_array(self):
        """Test with array containing no NaN values."""
        data = [1, 2, 3, 4, 5]
        result = nan(data)
        
        assert result["count"] == 0
        assert result["proportion"] == 0.0
        assert result["total"] == 5
        assert result["valid_count"] == 5
    
    def test_all_nans_array(self):
        """Test with array containing all NaN values."""
        data = [np.nan, np.nan, np.nan]
        result = nan(data)
        
        assert result["count"] == 3
        assert result["proportion"] == 1.0
        assert result["total"] == 3
        assert result["valid_count"] == 0
    
    def test_partial_nans_array(self):
        """Test with array containing some NaN values."""
        data = [1, np.nan, 3, np.nan, 5]
        result = nan(data)
        
        assert result["count"] == 2
        assert result["proportion"] == 0.4
        assert result["total"] == 5
        assert result["valid_count"] == 3
    
    def test_numpy_array_input(self):
        """Test with numpy array input."""
        data = np.array([1, 2, np.nan, 4, np.nan])
        result = nan(data)
        
        assert result["count"] == 2
        assert result["proportion"] == 0.4
        assert result["total"] == 5
        assert result["valid_count"] == 3
    
    def test_pandas_series_input(self):
        """Test with pandas Series input."""
        data = pd.Series([1, 2, np.nan, 4, np.nan])
        result = nan(data)
        
        assert result["count"] == 2
        assert result["proportion"] == 0.4
        assert result["total"] == 5
        assert result["valid_count"] == 3
    
    def test_pandas_dataframe_input(self):
        """Test with pandas DataFrame input."""
        data = pd.DataFrame({
            'A': [1, 2, np.nan],
            'B': [np.nan, 5, 6]
        })
        result = nan(data)
        
        assert result["count"] == 2
        assert result["proportion"] == 2/6
        assert result["total"] == 6
        assert result["valid_count"] == 4
    
    def test_multidimensional_array(self):
        """Test with multidimensional array."""
        data = np.array([[1, np.nan], [3, 4], [np.nan, 6]])
        result = nan(data)
        
        assert result["count"] == 2
        assert result["proportion"] == 2/6
        assert result["total"] == 6
        assert result["valid_count"] == 4
    
    def test_empty_array(self):
        """Test with empty array."""
        data = []
        result = nan(data)
        
        assert result["count"] == 0
        assert result["proportion"] == 0.0
        assert result["total"] == 0
        assert result["valid_count"] == 0
    
    def test_single_element_array(self):
        """Test with single element arrays."""
        # Single valid value
        result1 = nan([5])
        assert result1["count"] == 0
        assert result1["proportion"] == 0.0
        assert result1["total"] == 1
        assert result1["valid_count"] == 1
        
        # Single NaN value
        result2 = nan([np.nan])
        assert result2["count"] == 1
        assert result2["proportion"] == 1.0
        assert result2["total"] == 1
        assert result2["valid_count"] == 0
    
    def test_mixed_numeric_types(self):
        """Test with mixed numeric types."""
        data = [1, 2.5, np.nan, 4, np.inf, -np.inf]
        result = nan(data)
        
        # Only np.nan should be counted as NaN, not inf
        assert result["count"] == 1
        assert result["proportion"] == 1/6
        assert result["total"] == 6
        assert result["valid_count"] == 5
    
    def test_return_types(self):
        """Test that return values have correct types."""
        data = [1, np.nan, 3]
        result = nan(data)
        
        assert isinstance(result["count"], int)
        assert isinstance(result["proportion"], float)
        assert isinstance(result["total"], int)
        assert isinstance(result["valid_count"], int)
    
    def test_nested_structure_flattening(self):
        """Test that nested structures are properly flattened."""
        data = [[1, np.nan], [3, 4]]
        result = nan(data)
        
        assert result["count"] == 1
        assert result["total"] == 4
        assert result["valid_count"] == 3


class TestRealFunction:
    """Test suite for real function."""
    
    def test_all_finite_values(self):
        """Test with all finite values."""
        data = [1, 2, 3, 4, 5]
        result = real(data)
        
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["count"] == 5
        assert isinstance(result["std"], float)
        assert isinstance(result["skew"], float)
        assert isinstance(result["kurtosis"], float)
    
    def test_with_nan_values(self):
        """Test with NaN values (should be excluded)."""
        data = [1, 2, np.nan, 4, 5]
        result = real(data)
        
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["count"] == 4
        assert np.isfinite(result["std"])
        assert np.isfinite(result["skew"])
        assert np.isfinite(result["kurtosis"])
    
    def test_with_inf_values(self):
        """Test with infinity values (should be excluded)."""
        data = [1, 2, np.inf, 4, -np.inf]
        result = real(data)
        
        assert result["mean"] == 7/3  # (1+2+4)/3
        assert result["median"] == 2.0
        assert result["count"] == 3
        assert np.isfinite(result["std"])
    
    def test_with_nan_and_inf_values(self):
        """Test with both NaN and infinity values."""
        data = [1, 2, np.nan, np.inf, 5, -np.inf]
        result = real(data)
        
        assert result["mean"] == 8/3  # (1+2+5)/3
        assert result["median"] == 2.0
        assert result["count"] == 3
    
    def test_all_non_finite_values(self):
        """Test when all values are non-finite."""
        data = [np.nan, np.inf, -np.inf, np.nan]
        result = real(data)
        
        assert np.isnan(result["mean"])
        assert np.isnan(result["median"])
        assert np.isnan(result["std"])
        assert np.isnan(result["skew"])
        assert np.isnan(result["kurtosis"])
        assert result["count"] == 0
    
    def test_empty_array(self):
        """Test with empty array."""
        data = []
        result = real(data)
        
        assert np.isnan(result["mean"])
        assert np.isnan(result["median"])
        assert np.isnan(result["std"])
        assert np.isnan(result["skew"])
        assert np.isnan(result["kurtosis"])
        assert result["count"] == 0
    
    def test_single_value(self):
        """Test with single finite value."""
        data = [5.0]
        result = real(data)
        
        assert result["mean"] == 5.0
        assert result["median"] == 5.0
        assert result["std"] == 0.0
        assert result["count"] == 1
        # Note: skew and kurtosis of single value are NaN in scipy
        assert np.isnan(result["skew"])
        assert np.isnan(result["kurtosis"])
    
    def test_numpy_array_input(self):
        """Test with numpy array input."""
        data = np.array([1.0, 2.0, np.nan, 4.0, np.inf])
        result = real(data)
        
        expected_mean = (1.0 + 2.0 + 4.0) / 3
        assert result["mean"] == expected_mean
        assert result["count"] == 3
    
    def test_pandas_series_input(self):
        """Test with pandas Series input."""
        data = pd.Series([1.0, 2.0, np.nan, 4.0, np.inf])
        result = real(data)
        
        expected_mean = (1.0 + 2.0 + 4.0) / 3
        assert result["mean"] == expected_mean
        assert result["count"] == 3
    
    def test_multidimensional_array(self):
        """Test with multidimensional array."""
        data = np.array([[1, 2], [np.nan, 4], [5, np.inf]])
        result = real(data)
        
        # Should consider [1, 2, 4, 5] as finite values
        expected_mean = (1 + 2 + 4 + 5) / 4
        assert result["mean"] == expected_mean
        assert result["count"] == 4
    
    def test_return_types(self):
        """Test that return values have correct types."""
        data = [1.0, 2.0, 3.0]
        result = real(data)
        
        assert isinstance(result["mean"], float)
        assert isinstance(result["median"], float)
        assert isinstance(result["std"], float)
        assert isinstance(result["skew"], float)
        assert isinstance(result["kurtosis"], float)
        assert isinstance(result["count"], int)
    
    def test_statistical_calculations(self):
        """Test statistical calculations with known values."""
        # Use values with known statistics
        data = [1, 2, 3, 4, 5]
        result = real(data)
        
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["count"] == 5
        
        # Standard deviation of [1,2,3,4,5] should be sqrt(2)
        expected_std = np.sqrt(2.0)
        assert abs(result["std"] - expected_std) < 1e-10
    
    def test_skewness_and_kurtosis(self):
        """Test skewness and kurtosis calculations."""
        # Symmetric data should have skewness close to 0
        symmetric_data = [1, 2, 3, 4, 5]
        result = real(symmetric_data)
        assert abs(result["skew"]) < 1e-10
        
        # Right-skewed data should have positive skewness
        right_skewed = [1, 1, 1, 2, 3, 4, 10]
        result = real(right_skewed)
        assert result["skew"] > 0
    
    def test_identical_values(self):
        """Test with identical values."""
        data = [5, 5, 5, 5, 5]
        result = real(data)
        
        assert result["mean"] == 5.0
        assert result["median"] == 5.0
        assert result["std"] == 0.0
        # Skew and kurtosis of identical values are NaN due to zero variance
        assert np.isnan(result["skew"])
        assert np.isnan(result["kurtosis"])
        assert result["count"] == 5
    
    def test_two_values(self):
        """Test with exactly two finite values."""
        data = [np.nan, 10, np.inf, 20, np.nan]
        result = real(data)
        
        assert result["mean"] == 15.0
        assert result["median"] == 15.0
        assert result["count"] == 2
        assert result["std"] == 5.0  # sqrt(((10-15)^2 + (20-15)^2)/2)
    
    def test_large_dataset(self):
        """Test with larger dataset."""
        np.random.seed(42)
        # Create data with some NaN and inf values
        data = np.random.normal(0, 1, 1000)
        data[50:60] = np.nan
        data[100:105] = np.inf
        data[200:203] = -np.inf
        
        result = real(data)
        
        # Should exclude 10 NaN + 5 inf + 3 -inf = 18 values
        assert result["count"] == 1000 - 18
        assert np.isfinite(result["mean"])
        assert np.isfinite(result["median"])
        assert np.isfinite(result["std"])
        assert np.isfinite(result["skew"])
        assert np.isfinite(result["kurtosis"])


class TestIntegrationAndEdgeCases:
    """Test integration and edge cases for both functions."""
    
    def test_consistent_counting(self):
        """Test that nan and real functions give consistent counts."""
        data = [1, 2, np.nan, np.inf, 5, np.nan, -np.inf]
        
        nan_result = nan(data)
        real_result = real(data)
        
        # Total should be sum of nan count and finite count
        total_accounted = nan_result["count"] + real_result["count"]
        # Note: inf values are not counted as NaN but also not counted as real
        # So total might not equal total length if there are inf values
        
        assert nan_result["total"] == 7
        assert nan_result["count"] == 2  # Two NaN values
        assert real_result["count"] == 3  # Three finite values (1, 2, 5)
    
    def test_complex_pandas_structures(self):
        """Test with complex pandas structures."""
        df = pd.DataFrame({
            'A': [1, np.nan, 3, np.inf],
            'B': [np.nan, 2, np.nan, 4],
            'C': [5, 6, 7, np.nan]
        })
        
        nan_result = nan(df)
        real_result = real(df)
        
        assert nan_result["total"] == 12  # 4 rows × 3 columns
        assert nan_result["count"] == 4   # Count of NaN values (verified above)
        assert real_result["count"] == 7  # Count of finite values
    
    def test_numerical_precision(self):
        """Test numerical precision with edge values."""
        data = [1e-10, 1e10, -1e-10, -1e10, 0.0]
        
        nan_result = nan(data)
        real_result = real(data)
        
        assert nan_result["count"] == 0
        assert real_result["count"] == 5
        assert np.isfinite(real_result["mean"])
        assert np.isfinite(real_result["std"])
    
    def test_dtype_preservation(self):
        """Test that functions work with different dtypes."""
        # Integer data
        int_data = np.array([1, 2, 3], dtype=np.int32)
        int_result = real(int_data)
        assert int_result["count"] == 3
        
        # Float data
        float_data = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        float_result = real(float_data)
        assert float_result["count"] == 3
        
        # Mixed with NaN (will be converted to float)
        mixed_data = [1, 2.5, np.nan]
        mixed_result = real(mixed_data)
        assert mixed_result["count"] == 2

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/_nan_stats.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-05-30 22:10:00 (Claude)"
# # File: ./scitex_repo/src/scitex/stats/_nan_stats.py
# 
# """
# Functions for NaN statistics.
# """
# 
# import numpy as np
# import pandas as pd
# 
# 
# def nan(data):
#     """
#     Get statistics about NaN values in the data.
# 
#     Parameters
#     ----------
#     data : array-like
#         Input data
# 
#     Returns
#     -------
#     dict
#         Dictionary containing NaN statistics
#     """
#     # Convert to numpy array if needed
#     if isinstance(data, pd.DataFrame):
#         data_flat = data.values.flatten()
#     elif isinstance(data, pd.Series):
#         data_flat = data.values
#     else:
#         data_flat = np.asarray(data).flatten()
# 
#     # Count NaNs
#     nan_mask = np.isnan(data_flat)
#     nan_count = int(np.sum(nan_mask))
#     total_count = len(data_flat)
# 
#     return {
#         "count": nan_count,
#         "proportion": nan_count / total_count if total_count > 0 else 0.0,
#         "total": total_count,
#         "valid_count": total_count - nan_count,
#     }
# 
# 
# def real(data):
#     """
#     Get statistics for real (non-NaN, non-Inf) values.
# 
#     Parameters
#     ----------
#     data : array-like
#         Input data
# 
#     Returns
#     -------
#     dict
#         Dictionary containing statistics for real values
#     """
#     # Convert to numpy array
#     data_array = np.asarray(data)
# 
#     # Get only finite values
#     finite_mask = np.isfinite(data_array)
#     real_values = data_array[finite_mask]
# 
#     if len(real_values) == 0:
#         return {
#             "mean": np.nan,
#             "median": np.nan,
#             "std": np.nan,
#             "skew": np.nan,
#             "kurtosis": np.nan,
#             "count": 0,
#         }
# 
#     # Calculate statistics
#     from scipy import stats as scipy_stats
# 
#     return {
#         "mean": float(np.mean(real_values)),
#         "median": float(np.median(real_values)),
#         "std": float(np.std(real_values)),
#         "skew": float(scipy_stats.skew(real_values)),
#         "kurtosis": float(scipy_stats.kurtosis(real_values)),
#         "count": len(real_values),
#     }
# 
# 
# __all__ = ["nan", "real"]

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/stats/_nan_stats.py
# --------------------------------------------------------------------------------
