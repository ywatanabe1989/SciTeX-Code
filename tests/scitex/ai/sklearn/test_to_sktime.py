#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 08:00:00 (ywatanabe)"
# File: ./tests/scitex/ai/sklearn/test_to_sktime.py

"""Comprehensive tests for ai.sklearn.to_sktime module."""

import pytest
import numpy as np
import pandas as pd
import torch
from scitex.ai.sklearn.to_sktime import to_sktime_df


class TestToSktimeDf:
    """Test suite for to_sktime_df function."""
    
    @pytest.fixture
    def sample_numpy_data(self):
        """Create sample numpy array data."""
        np.random.seed(42)
        return np.random.rand(10, 3, 50)  # 10 samples, 3 channels, 50 time points
    
    @pytest.fixture
    def sample_torch_data(self, sample_numpy_data):
        """Create sample torch tensor data."""
        return torch.from_numpy(sample_numpy_data.copy())
    
    @pytest.fixture
    def sample_pandas_data(self):
        """Create sample pandas DataFrame data in sktime format."""
        data = []
        for i in range(5):
            row = []
            for j in range(2):
                row.append(pd.Series(np.random.rand(20), name=f"dim_{j}"))
            data.append(row)
        return pd.DataFrame(data, columns=[0, 1])
    
    def test_numpy_input_basic_functionality(self, sample_numpy_data):
        """Test basic functionality with numpy array input."""
        result = to_sktime_df(sample_numpy_data)
        
        # Check output type
        assert isinstance(result, pd.DataFrame)
        
        # Check dimensions
        assert len(result) == sample_numpy_data.shape[0]  # n_samples (rows)
        assert len(result.columns) == sample_numpy_data.shape[1]  # n_channels (columns)
        
        # Check first sample, first channel structure
        first_channel = result.iloc[0, 0]
        assert isinstance(first_channel, pd.Series)
        assert len(first_channel) == sample_numpy_data.shape[2]  # seq_len
        assert first_channel.name == "dim_0"
    
    def test_torch_input_basic_functionality(self, sample_torch_data):
        """Test basic functionality with torch tensor input."""
        result = to_sktime_df(sample_torch_data)
        
        # Check output type
        assert isinstance(result, pd.DataFrame)
        
        # Check dimensions match torch input
        assert len(result) == sample_torch_data.shape[0]
        assert len(result.columns) == sample_torch_data.shape[1]
        
        # Check data conversion
        first_channel = result.iloc[0, 0]
        assert isinstance(first_channel, pd.Series)
        assert len(first_channel) == sample_torch_data.shape[2]
    
    def test_pandas_input_passthrough(self, sample_pandas_data):
        """Test that pandas DataFrame input is returned as-is."""
        result = to_sktime_df(sample_pandas_data)
        
        # Should return the same object
        assert result is sample_pandas_data
    
    def test_data_type_conversion(self):
        """Test that data is converted to float64."""
        X = np.random.randint(0, 10, size=(5, 2, 10)).astype(np.int32)
        result = to_sktime_df(X)
        
        # Check that underlying data is float64
        first_channel = result.iloc[0, 0]
        assert first_channel.dtype == np.float64
    
    def test_dimension_names(self, sample_numpy_data):
        """Test that channel dimensions are properly named."""
        result = to_sktime_df(sample_numpy_data)
        
        # Check each channel in first sample
        for i in range(sample_numpy_data.shape[1]):
            channel = result.iloc[0, i]
            assert channel.name == f"dim_{i}"
    
    def test_data_preservation(self, sample_numpy_data):
        """Test that original data values are preserved."""
        result = to_sktime_df(sample_numpy_data)
        
        # Check a specific sample and channel
        sample_idx, channel_idx = 0, 0
        original_data = sample_numpy_data[sample_idx, channel_idx, :]
        converted_data = result.iloc[sample_idx, channel_idx].values
        
        np.testing.assert_array_almost_equal(original_data, converted_data)
    
    def test_multiple_samples_conversion(self):
        """Test conversion of multiple samples."""
        X = np.random.rand(20, 4, 100)
        result = to_sktime_df(X)
        
        assert len(result) == 20  # 20 samples (rows)
        assert len(result.columns) == 4  # 4 channels (columns)
        
        # Check each cell has correct structure
        for i in range(len(result)):
            for j in range(len(result.columns)):
                channel = result.iloc[i, j]
                assert isinstance(channel, pd.Series)
                assert len(channel) == 100  # 100 time points
                assert channel.name == f"dim_{j}"
    
    def test_single_sample_conversion(self):
        """Test conversion of single sample."""
        X = np.random.rand(1, 2, 30)
        result = to_sktime_df(X)
        
        assert len(result) == 1  # 1 sample
        assert len(result.columns) == 2  # 2 channels
        
        for j in range(2):
            channel = result.iloc[0, j]
            assert len(channel) == 30
            assert channel.name == f"dim_{j}"
    
    def test_single_channel_conversion(self):
        """Test conversion with single channel data."""
        X = np.random.rand(5, 1, 25)
        result = to_sktime_df(X)
        
        assert len(result) == 5  # 5 samples
        assert len(result.columns) == 1  # 1 channel
        
        for i in range(5):
            channel = result.iloc[i, 0]
            assert len(channel) == 25
            assert channel.name == "dim_0"
    
    def test_torch_tensor_conversion_types(self):
        """Test different torch tensor types."""
        # Float tensor
        X_float = torch.rand(3, 2, 10)
        result_float = to_sktime_df(X_float)
        assert isinstance(result_float, pd.DataFrame)
        assert result_float.shape == (3, 2)
        
        # Double tensor
        X_double = torch.rand(3, 2, 10, dtype=torch.double)
        result_double = to_sktime_df(X_double)
        assert isinstance(result_double, pd.DataFrame)
        
        # Check data type after conversion
        channel = result_double.iloc[0, 0]
        assert channel.dtype == np.float64
    
    def test_torch_to_numpy_conversion(self):
        """Test that torch tensors are properly converted to numpy."""
        X_torch = torch.rand(4, 3, 20)
        X_numpy = X_torch.numpy()
        
        result_torch = to_sktime_df(X_torch)
        result_numpy = to_sktime_df(X_numpy)
        
        # Results should be equivalent
        assert result_torch.shape == result_numpy.shape
        for i in range(len(result_torch)):
            for j in range(len(result_torch.columns)):
                np.testing.assert_array_almost_equal(
                    result_torch.iloc[i, j].values,
                    result_numpy.iloc[i, j].values
                )
    
    def test_invalid_input_types(self):
        """Test error handling for invalid input types."""
        # List input
        with pytest.raises(ValueError, match="Input X must be a numpy.ndarray, torch.Tensor, or pandas.DataFrame"):
            to_sktime_df([[1, 2, 3], [4, 5, 6]])
        
        # String input
        with pytest.raises(ValueError, match="Input X must be a numpy.ndarray, torch.Tensor, or pandas.DataFrame"):
            to_sktime_df("invalid")
        
        # Dictionary input
        with pytest.raises(ValueError, match="Input X must be a numpy.ndarray, torch.Tensor, or pandas.DataFrame"):
            to_sktime_df({"data": [1, 2, 3]})
    
    def test_wrong_dimensions(self):
        """Test handling of arrays with wrong dimensions."""
        # 2D array (missing channel dimension) - actually works but treats rows as samples, cols as time
        X_2d = np.random.rand(10, 50)
        result = to_sktime_df(X_2d)
        assert isinstance(result, pd.DataFrame)
        # With 2D input, it becomes (10 samples, 50 channels)
        assert result.shape == (10, 50)
    
    def test_empty_data(self):
        """Test handling of empty or zero-sized data."""
        # Empty array
        X_empty = np.array([]).reshape(0, 2, 10)
        result = to_sktime_df(X_empty)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        # Empty array results in empty DataFrame with no columns
        assert len(result.columns) == 0
        
        # Zero sequence length
        X_zero_seq = np.random.rand(3, 2, 0)
        result = to_sktime_df(X_zero_seq)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert len(result.columns) == 2
        
        # Check that channels have zero length
        for i in range(3):
            for j in range(2):
                channel = result.iloc[i, j]
                assert len(channel) == 0
    
    def test_large_data_handling(self):
        """Test handling of larger datasets."""
        # Larger dataset
        X_large = np.random.rand(100, 10, 500)
        result = to_sktime_df(X_large)
        
        assert len(result) == 100
        assert len(result.columns) == 10
        
        # Spot check a few samples
        for i in [0, 50, 99]:
            for j in [0, 5, 9]:
                channel = result.iloc[i, j]
                assert len(channel) == 500
                assert channel.name == f"dim_{j}"
    
    def test_data_consistency_across_samples(self, sample_numpy_data):
        """Test that data structure is consistent across all samples."""
        result = to_sktime_df(sample_numpy_data)
        
        n_samples, n_channels, seq_len = sample_numpy_data.shape
        
        assert result.shape == (n_samples, n_channels)
        
        for i in range(n_samples):
            for j in range(n_channels):
                channel = result.iloc[i, j]
                assert isinstance(channel, pd.Series)
                assert len(channel) == seq_len
                assert channel.name == f"dim_{j}"
    
    def test_example_from_docstring(self):
        """Test the example provided in the docstring."""
        X_np = np.random.rand(64, 160, 1024)
        sktime_df = to_sktime_df(X_np)
        
        # Check type as mentioned in docstring
        assert isinstance(sktime_df, pd.DataFrame)
        
        # Check structure
        assert len(sktime_df) == 64  # n_samples
        assert len(sktime_df.columns) == 160  # n_channels
        first_channel = sktime_df.iloc[0, 0]
        assert len(first_channel) == 1024  # seq_len
    
    def test_edge_case_single_timepoint(self):
        """Test with single time point data."""
        X = np.random.rand(5, 3, 1)
        result = to_sktime_df(X)
        
        assert len(result) == 5
        assert len(result.columns) == 3
        
        for i in range(5):
            for j in range(3):
                channel = result.iloc[i, j]
                assert len(channel) == 1
                assert channel.name == f"dim_{j}"
    
    def test_numerical_precision(self):
        """Test that numerical precision is maintained."""
        # Use specific values to test precision
        X = np.array([[[1.123456789, 2.987654321, 3.141592653]]]).astype(np.float64)
        result = to_sktime_df(X)
        
        channel = result.iloc[0, 0]
        
        # Check that precision is maintained
        expected = np.array([1.123456789, 2.987654321, 3.141592653])
        np.testing.assert_array_almost_equal(channel.values, expected, decimal=9)
    
    def test_channel_indexing_structure(self):
        """Test that channels are properly indexed in DataFrame columns."""
        X = np.random.rand(5, 4, 20)
        result = to_sktime_df(X)
        
        # Check column structure
        expected_columns = [0, 1, 2, 3]
        assert list(result.columns) == expected_columns
        
        # Check that each column contains proper channel data
        for col_idx, col in enumerate(result.columns):
            for row_idx in range(len(result)):
                channel = result.iloc[row_idx, col_idx]
                assert channel.name == f"dim_{col_idx}"
    
    def test_data_immutability(self):
        """Test that original data is not modified."""
        X_original = np.random.rand(3, 2, 10)
        X_copy = X_original.copy()
        
        result = to_sktime_df(X_original)
        
        # Original data should remain unchanged
        np.testing.assert_array_equal(X_original, X_copy)
    
    def test_memory_efficiency_large_data(self):
        """Test memory behavior with large data."""
        # This test mainly ensures the function can handle larger data
        X = np.random.rand(50, 20, 1000)
        result = to_sktime_df(X)
        
        # Should complete without memory errors
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (50, 20)
    
    def test_different_sequence_lengths_simulation(self):
        """Test behavior with different sequence lengths (simulated via different inputs)."""
        # Short sequences
        X_short = np.random.rand(3, 2, 5)
        result_short = to_sktime_df(X_short)
        assert result_short.iloc[0, 0].shape[0] == 5
        
        # Medium sequences
        X_medium = np.random.rand(3, 2, 100)
        result_medium = to_sktime_df(X_medium)
        assert result_medium.iloc[0, 0].shape[0] == 100
        
        # Long sequences
        X_long = np.random.rand(3, 2, 2000)
        result_long = to_sktime_df(X_long)
        assert result_long.iloc[0, 0].shape[0] == 2000
    
    def test_torch_gradient_tensor_handling(self):
        """Test handling of torch tensors with gradients."""
        X = torch.rand(3, 2, 10, requires_grad=True)
        result = to_sktime_df(X)
        
        # Should work without issues
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 2)
        
        # Data should be detached from gradient computation
        channel = result.iloc[0, 0]
        assert isinstance(channel, pd.Series)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])