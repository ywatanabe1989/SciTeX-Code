#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
import numpy as np
import pandas as pd
import torch
from scitex.ai.utils import format_samples_for_sktime
from scitex.ai.utils._format_samples_for_sktime import _format_a_sample_for_sktime


class TestFormatSamplesForSktime:
    """Test suite for sktime format conversion functions."""
    
    def test_format_single_sample_basic(self):
        """Test formatting a single sample with basic dimensions."""
        x = np.random.rand(3, 100)  # 3 channels, 100 time points
        result = _format_a_sample_for_sktime(x)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert all(f"dim_{i}" in result.index for i in range(3))
        
    def test_format_single_sample_values(self):
        """Test that values are correctly preserved in formatting."""
        x = np.array([[1, 2, 3], [4, 5, 6]])  # 2 channels, 3 time points
        result = _format_a_sample_for_sktime(x)
        
        assert isinstance(result["dim_0"], pd.Series)
        assert list(result["dim_0"].values) == [1, 2, 3]
        assert list(result["dim_1"].values) == [4, 5, 6]
        
    def test_format_multiple_samples_numpy(self):
        """Test formatting multiple samples from numpy array."""
        X = np.random.rand(10, 5, 50)  # 10 samples, 5 channels, 50 time points
        result = format_samples_for_sktime(X)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10
        assert result.shape == (10, 5)
        
    def test_format_multiple_samples_torch(self):
        """Test formatting multiple samples from torch tensor."""
        X = torch.randn(20, 3, 100)  # 20 samples, 3 channels, 100 time points
        result = format_samples_for_sktime(X)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 20
        assert result.shape == (20, 3)
        
    def test_torch_to_numpy_conversion(self):
        """Test that torch tensors are correctly converted to numpy."""
        X_torch = torch.randn(5, 2, 30, dtype=torch.float32)
        X_numpy = X_torch.numpy()
        
        result_torch = format_samples_for_sktime(X_torch)
        result_numpy = format_samples_for_sktime(X_numpy)
        
        pd.testing.assert_frame_equal(result_torch, result_numpy)
        
    def test_float64_conversion(self):
        """Test that data is converted to float64."""
        X = np.random.rand(5, 3, 20).astype(np.float32)
        result = format_samples_for_sktime(X)
        
        # Check that all series have float64 dtype
        for col in result.columns:
            for idx in result.index:
                assert result.loc[idx, col].dtype == np.float64
                
    def test_single_channel_data(self):
        """Test formatting with single channel data."""
        X = np.random.rand(15, 1, 200)  # Single channel
        result = format_samples_for_sktime(X)
        
        assert result.shape == (15, 1)
        assert "dim_0" in result.columns
        
    def test_large_number_of_channels(self):
        """Test formatting with many channels."""
        n_channels = 100
        X = np.random.rand(5, n_channels, 50)
        result = format_samples_for_sktime(X)
        
        assert result.shape == (5, n_channels)
        assert all(f"dim_{i}" in result.columns for i in range(n_channels))
        
    def test_varying_sequence_lengths_same_shape(self):
        """Test that function works with consistent sequence lengths."""
        X = np.random.rand(8, 4, 150)
        result = format_samples_for_sktime(X)
        
        # All time series should have same length
        for idx in result.index:
            for col in result.columns:
                assert len(result.loc[idx, col]) == 150
                
    def test_empty_data_handling(self):
        """Test handling of empty data arrays."""
        X = np.array([]).reshape(0, 5, 100)  # 0 samples
        result = format_samples_for_sktime(X)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        
    def test_single_sample_3d_array(self):
        """Test formatting a single sample in 3D array format."""
        X = np.random.rand(1, 3, 50)  # 1 sample, 3 channels, 50 time points
        result = format_samples_for_sktime(X)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.shape == (1, 3)
        
    def test_dimension_names_consistency(self):
        """Test that dimension names are consistent across samples."""
        X = np.random.rand(10, 7, 30)
        result = format_samples_for_sktime(X)
        
        expected_columns = [f"dim_{i}" for i in range(7)]
        assert list(result.columns) == expected_columns
        
    def test_preserves_data_integrity(self):
        """Test that data values are preserved exactly."""
        X = np.arange(24).reshape(2, 3, 4).astype(np.float64)
        result = format_samples_for_sktime(X)
        
        # Check first sample
        assert list(result.loc[0, "dim_0"].values) == [0, 1, 2, 3]
        assert list(result.loc[0, "dim_1"].values) == [4, 5, 6, 7]
        assert list(result.loc[0, "dim_2"].values) == [8, 9, 10, 11]
        
        # Check second sample
        assert list(result.loc[1, "dim_0"].values) == [12, 13, 14, 15]
        
    def test_with_nan_values(self):
        """Test handling of NaN values in the data."""
        X = np.random.rand(5, 2, 25)
        X[0, 0, 5] = np.nan
        X[2, 1, 10:15] = np.nan
        
        result = format_samples_for_sktime(X)
        
        assert np.isnan(result.loc[0, "dim_0"].iloc[5])
        assert np.all(np.isnan(result.loc[2, "dim_1"].iloc[10:15]))
        
    def test_with_inf_values(self):
        """Test handling of infinite values in the data."""
        X = np.random.rand(3, 2, 20)
        X[1, 0, 0] = np.inf
        X[2, 1, -1] = -np.inf
        
        result = format_samples_for_sktime(X)
        
        assert np.isinf(result.loc[1, "dim_0"].iloc[0])
        assert np.isinf(result.loc[2, "dim_1"].iloc[-1])
        
    def test_series_naming_in_single_sample(self):
        """Test that series within samples have correct names."""
        x = np.random.rand(4, 30)
        result = _format_a_sample_for_sktime(x)
        
        for i in range(4):
            assert result[f"dim_{i}"].name == f"dim_{i}"
            
    def test_dataframe_index_range(self):
        """Test that DataFrame has correct index range."""
        n_samples = 25
        X = np.random.rand(n_samples, 5, 40)
        result = format_samples_for_sktime(X)
        
        assert list(result.index) == list(range(n_samples))
        
    def test_torch_cuda_tensor_handling(self):
        """Test handling of CUDA tensors (if available)."""
        if torch.cuda.is_available():
            X = torch.randn(10, 3, 50).cuda()
            # Should work after moving to CPU
            X_cpu = X.cpu()
            result = format_samples_for_sktime(X_cpu)
            
            assert isinstance(result, pd.DataFrame)
            assert result.shape == (10, 3)
            
    def test_memory_efficiency_check(self):
        """Test that function handles large arrays efficiently."""
        # Create a moderately large array
        X = np.random.rand(100, 10, 1000)
        
        # This should complete without memory errors
        result = format_samples_for_sktime(X)
        
        assert result.shape == (100, 10)
        # Verify a few random elements
        assert len(result.loc[50, "dim_5"]) == 1000


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
