#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:20:00 (ywatanabe)"
# File: ./tests/scitex/ai/sampling/test_undersample.py

"""Tests for scitex.ai.sampling.undersample module."""

import pytest
import numpy as np
import torch
import pandas as pd
from unittest.mock import patch, MagicMock
from typing import Tuple
from scitex.ai.sampling.undersample import undersample


class TestUndersample:
    """Test suite for undersample function."""

    def test_undersample_numpy_arrays(self):
        """Test undersampling with numpy arrays."""
        # Create imbalanced dataset
        X = np.array([
            [1, 2], [2, 3], [3, 4], [4, 5], [5, 6],  # Class 0 (majority)
            [6, 7], [7, 8], [8, 9], [9, 10], [10, 11],
            [11, 12], [12, 13]  # Class 1 (minority)
        ])
        y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check that classes are balanced
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert len(unique) == 2
        assert counts[0] == counts[1]  # Equal number of samples per class
        
        # Check that output types are preserved
        assert isinstance(X_resampled, np.ndarray)
        assert isinstance(y_resampled, np.ndarray)
        
        # Check shapes
        assert X_resampled.shape[1] == X.shape[1]
        assert len(X_resampled) == len(y_resampled)

    def test_undersample_with_lists(self):
        """Test undersampling with Python lists."""
        X = [
            [1, 2], [2, 3], [3, 4], [4, 5], [5, 6],
            [6, 7], [7, 8], [8, 9], [9, 10], [10, 11],
            [11, 12], [12, 13]
        ]
        y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check balance
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert counts[0] == counts[1]
        
        # RandomUnderSampler returns numpy arrays
        assert isinstance(X_resampled, np.ndarray)
        assert isinstance(y_resampled, np.ndarray)

    def test_undersample_with_torch_tensors(self):
        """Test undersampling with PyTorch tensors."""
        X = torch.tensor([
            [1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0], [5.0, 6.0],
            [6.0, 7.0], [7.0, 8.0], [8.0, 9.0], [9.0, 10.0], [10.0, 11.0],
            [11.0, 12.0], [12.0, 13.0]
        ])
        y = torch.tensor([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check balance
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert counts[0] == counts[1]
        
        # RandomUnderSampler converts to numpy
        assert isinstance(X_resampled, np.ndarray)
        assert isinstance(y_resampled, np.ndarray)

    def test_undersample_with_pandas(self):
        """Test undersampling with pandas DataFrame and Series."""
        X = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'feature2': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        })
        y = pd.Series([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check balance
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert counts[0] == counts[1]
        
        # RandomUnderSampler preserves pandas types
        assert isinstance(X_resampled, pd.DataFrame)
        assert isinstance(y_resampled, pd.Series)
        
        # Check column names are preserved
        assert list(X_resampled.columns) == list(X.columns)

    def test_undersample_random_state(self):
        """Test that random_state produces reproducible results."""
        X = np.random.rand(100, 5)
        y = np.array([0] * 80 + [1] * 20)
        
        # First run
        X_resampled1, y_resampled1 = undersample(X, y, random_state=42)
        
        # Second run with same random state
        X_resampled2, y_resampled2 = undersample(X, y, random_state=42)
        
        # Should produce identical results
        np.testing.assert_array_equal(X_resampled1, X_resampled2)
        np.testing.assert_array_equal(y_resampled1, y_resampled2)

    def test_undersample_different_random_states(self):
        """Test that different random states produce different results."""
        X = np.random.rand(100, 5)
        y = np.array([0] * 80 + [1] * 20)
        
        # First run
        X_resampled1, y_resampled1 = undersample(X, y, random_state=42)
        
        # Second run with different random state
        X_resampled2, y_resampled2 = undersample(X, y, random_state=123)
        
        # Should produce different results (very unlikely to be identical)
        assert not np.array_equal(X_resampled1, X_resampled2)

    def test_undersample_already_balanced(self):
        """Test undersampling on already balanced data."""
        X = np.array([
            [1, 2], [2, 3], [3, 4], [4, 5],
            [5, 6], [6, 7], [7, 8], [8, 9]
        ])
        y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Should return all samples since already balanced
        assert len(X_resampled) == len(X)
        assert len(y_resampled) == len(y)

    def test_undersample_multiclass(self):
        """Test undersampling with multiple classes."""
        X = np.array([
            [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7],  # Class 0
            [7, 8], [8, 9], [9, 10], [10, 11],  # Class 1
            [11, 12], [12, 13]  # Class 2
        ])
        y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check that all classes have same count (minority class count)
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert len(unique) == 3
        assert counts[0] == counts[1] == counts[2] == 2

    def test_undersample_extreme_imbalance(self):
        """Test undersampling with extreme class imbalance."""
        X = np.random.rand(1000, 10)
        y = np.array([0] * 999 + [1])  # Only 1 minority sample
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Should have 1 sample from each class
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert len(X_resampled) == 2
        assert counts[0] == counts[1] == 1

    def test_undersample_single_class_error(self):
        """Test that undersampling fails gracefully with single class."""
        X = np.array([[1, 2], [2, 3], [3, 4]])
        y = np.array([0, 0, 0])  # Only one class
        
        # Should work but return original data
        X_resampled, y_resampled = undersample(X, y)
        
        # RandomUnderSampler handles single class by returning original
        assert len(X_resampled) == len(X)
        assert len(y_resampled) == len(y)

    def test_undersample_shape_mismatch_error(self):
        """Test error handling for shape mismatch."""
        X = np.array([[1, 2], [2, 3], [3, 4]])
        y = np.array([0, 1])  # Wrong length
        
        with pytest.raises(ValueError):
            undersample(X, y)

    def test_undersample_empty_data_error(self):
        """Test error handling for empty data."""
        X = np.array([]).reshape(0, 2)
        y = np.array([])
        
        with pytest.raises(ValueError):
            undersample(X, y)

    @patch('scitex.ai.sampling.undersample.RandomUnderSampler')
    def test_undersample_calls_imblearn(self, mock_rus_class):
        """Test that function correctly calls imblearn's RandomUnderSampler."""
        # Setup mock
        mock_rus = MagicMock()
        mock_rus_class.return_value = mock_rus
        mock_rus.fit_resample.return_value = (
            np.array([[1, 2], [3, 4]]),
            np.array([0, 1])
        )
        
        # Call function
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([0, 0, 1])
        X_resampled, y_resampled = undersample(X, y, random_state=123)
        
        # Verify calls
        mock_rus_class.assert_called_once_with(random_state=123)
        mock_rus.fit_resample.assert_called_once_with(X, y)

    def test_undersample_preserves_feature_order(self):
        """Test that feature order is preserved after undersampling."""
        X = np.array([
            [1.1, 2.2, 3.3],
            [4.4, 5.5, 6.6],
            [7.7, 8.8, 9.9],
            [10.1, 11.1, 12.1]
        ])
        y = np.array([0, 0, 0, 1])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check that feature dimension is preserved
        assert X_resampled.shape[1] == X.shape[1]
        
        # Check that resampled data contains original samples
        for sample in X_resampled:
            assert any(np.allclose(sample, orig_sample) for orig_sample in X)

    def test_undersample_string_labels(self):
        """Test undersampling with string labels."""
        X = np.array([
            [1, 2], [2, 3], [3, 4], [4, 5], [5, 6],
            [6, 7], [7, 8]
        ])
        y = np.array(['cat', 'cat', 'cat', 'cat', 'cat', 'dog', 'dog'])
        
        X_resampled, y_resampled = undersample(X, y)
        
        # Check balance
        unique, counts = np.unique(y_resampled, return_counts=True)
        assert counts[0] == counts[1]
        assert set(unique) == {'cat', 'dog'}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
