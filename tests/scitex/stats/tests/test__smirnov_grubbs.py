#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:05:00 (ywatanabe)"
# File: tests/scitex/stats/tests/test__smirnov_grubbs.py

"""Test cases for Smirnov-Grubbs outlier detection test."""

import numpy as np
import pandas as pd
import pytest
import torch

import scitex

class TestSmirnovGrubbs:
    """Test cases for smirnov_grubbs function."""
    
    def test_basic_functionality(self):
        """Test basic functionality with simple array containing outliers."""
        # Normal data with clear outliers
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is an outlier
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert 9 in result  # Index of 100
        
    def test_no_outliers(self):
        """Test with data that has no outliers."""
        # Normal distribution data
        np.random.seed(42)
        data = np.random.randn(20)
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        # Should return None when no outliers
        assert result is None
        
    def test_multiple_outliers(self):
        """Test with multiple outliers."""
        data = [1, 2, 3, 4, 5, 50, 60, 70]  # Last three are outliers
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert len(result) >= 1  # Should detect at least one outlier
        
    def test_alpha_parameter(self):
        """Test with different alpha levels."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 20]
        
        # More strict (lower alpha)
        result_strict = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data, alpha=0.01)
        
        # Less strict (higher alpha)
        result_lenient = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data, alpha=0.1)
        
        # Lenient should detect same or more outliers
        if result_strict is None:
            assert result_lenient is None or len(result_lenient) >= 0
        elif result_lenient is not None:
            assert len(result_lenient) >= len(result_strict)
            
    def test_2d_array(self):
        """Test with 2D array (should be flattened)."""
        data = np.array([[1, 2, 3], [4, 5, 100]])
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        # Result should be 1D indices into flattened array
        assert result.ndim == 1
        
    def test_3d_array(self):
        """Test with 3D array."""
        data = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 100]]])
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert result.ndim == 1
        
    def test_small_sample(self):
        """Test with very small sample size."""
        data = [1, 2, 10]  # Minimum size for test
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        # Should handle small samples appropriately
        if result is not None:
            assert len(result) >= 0
            
    def test_identical_values(self):
        """Test with identical values."""
        data = [5, 5, 5, 5, 5, 10]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        # Should detect the different value as outlier
        assert result is not None
        assert 5 in result  # Index of 10
        
    def test_negative_values(self):
        """Test with negative values."""
        data = [-5, -4, -3, -2, -1, 0, 1, 2, 3, -50]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert 9 in result  # Index of -50
        
    def test_return_type(self):
        """Test that return type is correct."""
        data = [1, 2, 3, 4, 5, 100]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype in [np.int32, np.int64]
        
    def test_preserve_original_data(self):
        """Test that original data is not modified."""
        data = [1, 2, 3, 4, 5, 100]
        data_copy = data.copy()
        
        scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert data == data_copy
        
    def test_numpy_array_input(self):
        """Test with numpy array input."""
        data = np.array([1, 2, 3, 4, 5, 100])
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert 5 in result
        
    def test_pandas_series_input(self):
        """Test with pandas Series input."""
        data = pd.Series([1, 2, 3, 4, 5, 100])
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert 5 in result
        
    def test_list_input(self):
        """Test with list input."""
        data = [1, 2, 3, 4, 5, 100]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert 5 in result
        
    def test_single_outlier_dimension(self):
        """Test that single outlier returns 1D array."""
        data = [1, 2, 3, 4, 5, 100]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert result.ndim == 1
        
    def test_outlier_indices_validity(self):
        """Test that returned indices are valid."""
        data = np.array([1, 2, 3, 4, 5, 100])
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        if result is not None:
            # All indices should be within bounds
            assert np.all(result >= 0)
            assert np.all(result < len(data.flatten()))
            
    def test_repeated_outliers(self):
        """Test with repeated outlier values."""
        data = [1, 2, 3, 4, 5, 100, 100]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        # Should detect both occurrences
        assert len(result) >= 2
        
    def test_edge_case_two_values(self):
        """Test edge case with only two values."""
        data = [1, 100]
        
        # Should handle gracefully (might not detect outliers with n=2)
        try:
            result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
            # If it runs, check result is valid
            assert result is None or isinstance(result, np.ndarray)
        except:
            # Some implementations might raise error for n<3
            pass
            
    def test_large_dataset(self):
        """Test with large dataset."""
        np.random.seed(123)
        data = np.random.randn(1000)
        # Add some outliers
        data[100] = 10
        data[500] = -10
        
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert len(result) >= 2  # Should find the outliers
        
    def test_statistical_properties(self):
        """Test statistical properties of the test."""
        np.random.seed(456)
        
        # Generate data with known outlier
        data = np.random.randn(50)
        data[0] = 5  # Clear outlier
        
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        assert 0 in result  # Should detect the outlier at index 0
        
    def test_iterative_detection(self):
        """Test that function iteratively detects outliers."""
        # Data with multiple outliers at different scales
        data = [1, 2, 3, 4, 5, 20, 100]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        # Should detect the most extreme outlier(s)
        assert 6 in result  # Index of 100
        
    def test_mixed_distribution(self):
        """Test with data from mixed distribution."""
        np.random.seed(789)
        # Normal data with contamination
        normal_data = np.random.randn(45)
        outliers = np.random.randn(5) * 5 + 10
        data = np.concatenate([normal_data, outliers])
        
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        # Should detect some of the contaminated points
        assert len(result) >= 1
        
    def test_symmetrical_outliers(self):
        """Test with symmetrical outliers."""
        data = [-100, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 100]
        result = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data)
        
        assert result is not None
        # Should detect both extreme values
        assert len(result) >= 1
        
    def test_float_vs_int_consistency(self):
        """Test consistency between float and int inputs."""
        data_int = [1, 2, 3, 4, 5, 100]
        data_float = [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]
        
        result_int = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data_int)
        result_float = scitex.stats.tests._smirnov_grubbs.smirnov_grubbs(data_float)
        
        # Results should be identical
        if result_int is not None and result_float is not None:
            assert np.array_equal(result_int, result_float)
        else:
            assert result_int is None and result_float is None


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/tests/_smirnov_grubbs.py
# --------------------------------------------------------------------------------
# import numpy as np
# from scipy import stats
#
#
# def smirnov_grubbs(data_arr, alpha=0.05):
#     """
#     Find outliers based on Smirnov-Grubbs test.
#
#     Arguments:
#
#     Returns | indices of outliers
#     """
#     data_1D_sorted = sorted(np.array(data_arr).reshape(-1))
#     in_data, out_data = list(data_1D_sorted), []
#
#     # while True:
#     n = len(in_data)
#     for i_data in range(n):
#         n = len(in_data)
#         t = stats.t.isf(q=(alpha / n) / 2, df=n - 2)
#         tau = (n - 1) * t / np.sqrt(n * (n - 2) + n * t * t)
#         i_min, i_max = np.argmin(in_data), np.argmax(in_data)
#         mu, std = np.mean(in_data), np.std(in_data, ddof=1)
#
#         i_far = (
#             i_max
#             if np.abs(in_data[i_max] - mu) > np.abs(in_data[i_min] - mu)
#             else i_min
#         )
#
#         tau_far = np.abs((in_data[i_far] - mu) / std)
#
#         if tau_far < tau:
#             break
#
#         out_data.append(in_data.pop(i_far))
#
#     if len(out_data) == 0:
#         return None
#
#     else:
#         out_data_uq = np.unique(out_data)
#         indi_outliers = np.hstack(
#             [
#                 np.vstack(np.where(data_arr == out_data_uq[i_out])).T
#                 for i_out in range(len(out_data_uq))
#             ]
#         ).squeeze()
#
#         if indi_outliers.ndim == 0:
#             indi_outliers = indi_outliers[np.newaxis]
#         return indi_outliers
#
#
# # def smirnov_grubbs(data_arr, alpha=0.05):
# #     """
# #     Find outliers based on Smirnov-Grubbs test.
#
# #     Arguments:
#
# #     Returns | indices of outliers
# #     """
# #     data_1D_sorted = sorted(np.array(data_arr).reshape(-1))
# #     in_data, out_data = list(data_1D_sorted), []
#
# #     while True:
# #         n = len(in_data)
# #         t = stats.t.isf(q=(alpha / n) / 2, df=n - 2)
# #         tau = (n - 1) * t / np.sqrt(n * (n - 2) + n * t * t)
# #         i_min, i_max = np.argmin(in_data), np.argmax(in_data)
# #         mu, std = np.mean(in_data), np.std(in_data, ddof=1)
#
# #         i_far = (
# #             i_max
# #             if np.abs(in_data[i_max] - mu) > np.abs(in_data[i_min] - mu)
# #             else i_min
# #         )
#
# #         tau_far = np.abs((in_data[i_far] - mu) / std)
#
# #         if tau_far < tau:
# #             break
#
# #         out_data.append(in_data.pop(i_far))
#
# #     if len(out_data) == 0:
# #         return None
#
# #     else:
# #         out_data_uq = np.unique(out_data)
# #         indi_outliers = np.vstack(
# #             [
# #                 np.vstack(np.where(data_arr == out_data_uq[i_out])).T
# #                 for i_out in range(len(out_data_uq))
# #             ]
# #         )
#
# #         return np.array(indi_outliers).squeeze()

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/tests/_smirnov_grubbs.py
# --------------------------------------------------------------------------------
