#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 12:48:00 (ywatanabe)"
# File: ./tests/scitex/ai/sk/test__to_sktime.py

"""Tests for scitex.ai.sk._to_sktime module."""

import pytest
import numpy as np
import pandas as pd
import torch
from scitex.ai.sk import to_sktime_df


class TestToSktimeDf:
    """Test suite for to_sktime_df function."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        n_samples, n_chs, seq_len = 10, 3, 50
        return {
            'numpy': np.random.rand(n_samples, n_chs, seq_len),
            'torch': torch.rand(n_samples, n_chs, seq_len),
            'shape': (n_samples, n_chs, seq_len)
        }

    def test_numpy_input(self, sample_data):
        """Test conversion with numpy array input."""
        X_np = sample_data['numpy']
        result = to_sktime_df(X_np)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == sample_data['shape'][0]
        assert all(isinstance(result.iloc[i, 0], pd.Series) for i in range(result.shape[0]))

    def test_torch_input(self, sample_data):
        """Test conversion with torch tensor input."""
        X_torch = sample_data['torch']
        result = to_sktime_df(X_torch)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == sample_data['shape'][0]
        assert all(isinstance(result.iloc[i, 0], pd.Series) for i in range(result.shape[0]))

    def test_dataframe_passthrough(self):
        """Test that DataFrame input is returned as-is."""
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        result = to_sktime_df(df)
        
        assert result is df
        assert isinstance(result, pd.DataFrame)

    def test_invalid_input_type(self):
        """Test error handling for invalid input types."""
        with pytest.raises(ValueError, match="Input X must be"):
            to_sktime_df([1, 2, 3])  # List input
            
        with pytest.raises(ValueError, match="Input X must be"):
            to_sktime_df("invalid")  # String input

    def test_output_structure(self, sample_data):
        """Test the structure of the output DataFrame."""
        X = sample_data['numpy']
        n_samples, n_chs, seq_len = sample_data['shape']
        result = to_sktime_df(X)
        
        # Check DataFrame shape
        assert result.shape == (n_samples, 1)
        
        # Check each cell contains a Series of Series
        for i in range(n_samples):
            cell = result.iloc[i, 0]
            assert isinstance(cell, pd.Series)
            assert len(cell) == n_chs
            
            # Check each dimension
            for j in range(n_chs):
                dim_series = cell.iloc[j]
                assert isinstance(dim_series, pd.Series)
                assert len(dim_series) == seq_len
                assert dim_series.name == f"dim_{j}"

    def test_data_type_conversion(self):
        """Test that data is converted to float64."""
        X = np.array([[[1, 2, 3], [4, 5, 6]]], dtype=np.int32)
        result = to_sktime_df(X)
        
        # Check that the data has been converted to float64
        first_series = result.iloc[0, 0].iloc[0]
        assert first_series.dtype == np.float64

    def test_empty_input(self):
        """Test handling of empty arrays."""
        # Empty array with correct dimensions
        X = np.array([]).reshape(0, 3, 50)
        result = to_sktime_df(X)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == 0

    def test_single_sample(self):
        """Test conversion with a single sample."""
        X = np.random.rand(1, 5, 100)
        result = to_sktime_df(X)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (1, 1)
        assert len(result.iloc[0, 0]) == 5

    def test_large_dataset(self):
        """Test conversion with a larger dataset."""
        X = np.random.rand(100, 64, 1000)
        result = to_sktime_df(X)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (100, 1)
        
        # Check first and last samples
        assert len(result.iloc[0, 0]) == 64
        assert len(result.iloc[-1, 0]) == 64
        assert len(result.iloc[0, 0].iloc[0]) == 1000

    def test_dimension_names(self, sample_data):
        """Test that dimension names are correctly assigned."""
        X = sample_data['numpy']
        n_chs = sample_data['shape'][1]
        result = to_sktime_df(X)
        
        first_sample = result.iloc[0, 0]
        for i in range(n_chs):
            assert first_sample.iloc[i].name == f"dim_{i}"

    def test_torch_gradient_preservation(self):
        """Test that torch tensors don't lose gradient information."""
        X = torch.rand(5, 3, 20, requires_grad=True)
        # Should not raise an error even with gradients
        result = to_sktime_df(X)
        assert isinstance(result, pd.DataFrame)

    def test_different_shapes(self):
        """Test conversion with various input shapes."""
        shapes = [
            (5, 1, 100),   # Single channel
            (10, 10, 10),  # Square dimensions
            (1, 1, 1000),  # Single sample, single channel
            (50, 2, 5),    # Many samples, few timepoints
        ]
        
        for shape in shapes:
            X = np.random.rand(*shape)
            result = to_sktime_df(X)
            assert result.shape == (shape[0], 1)
            assert len(result.iloc[0, 0]) == shape[1]

    @pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64])
    def test_various_dtypes(self, dtype):
        """Test conversion with various numpy dtypes."""
        X = np.random.rand(5, 3, 20).astype(dtype)
        result = to_sktime_df(X)
        
        assert isinstance(result, pd.DataFrame)
        # All values should be float64 after conversion
        first_series = result.iloc[0, 0].iloc[0]
        assert first_series.dtype == np.float64

    def test_nan_handling(self):
        """Test handling of NaN values."""
        X = np.random.rand(5, 3, 20)
        X[0, 0, :5] = np.nan
        
        result = to_sktime_df(X)
        first_dim_series = result.iloc[0, 0].iloc[0]
        
        # Check that NaN values are preserved
        assert np.isnan(first_dim_series.iloc[:5]).all()
        assert not np.isnan(first_dim_series.iloc[5:]).any()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
