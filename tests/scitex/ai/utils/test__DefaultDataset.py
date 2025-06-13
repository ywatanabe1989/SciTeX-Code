#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
import numpy as np
import torch
from torch.utils.data import DataLoader
from scitex.ai.utils import DefaultDataset


class TestDefaultDataset:
    """Test suite for DefaultDataset class."""
    
    def test_initialization_with_single_array(self):
        """Test initialization with a single array."""
        X = np.random.rand(100, 10, 50)
        ds = DefaultDataset([X])
        assert len(ds) == 100
        assert ds.arrs_list == [X]
        assert ds.arrs == ds.arrs_list  # Check alias
        
    def test_initialization_with_multiple_arrays(self):
        """Test initialization with multiple arrays of same length."""
        n = 256
        X = np.random.rand(n, 19, 1000)
        T = np.random.randint(0, 4, size=(n, 1))
        S = np.random.randint(0, 999, size=(n, 1))
        
        ds = DefaultDataset([X, T, S])
        assert len(ds) == n
        assert len(ds.arrs_list) == 3
        
    def test_initialization_with_transform(self):
        """Test initialization with a transform function."""
        X = np.random.rand(50, 5, 100)
        transform = lambda x: x * 2.0
        
        ds = DefaultDataset([X], transform=transform)
        assert ds.transform is not None
        assert callable(ds.transform)
        
    def test_getitem_without_transform(self):
        """Test __getitem__ method without transform."""
        n = 100
        X = np.random.rand(n, 10, 50)
        Y = np.random.randint(0, 5, size=(n,))
        
        ds = DefaultDataset([X, Y])
        sample = ds[0]
        
        assert len(sample) == 2
        np.testing.assert_array_equal(sample[0], X[0])
        assert sample[1] == Y[0]
        
    def test_getitem_with_transform(self):
        """Test __getitem__ method with transform applied to first element."""
        n = 50
        X = np.random.rand(n, 5, 20).astype(np.float32)
        Y = np.random.randint(0, 3, size=(n,))
        
        transform = lambda x: x * 2.0
        ds = DefaultDataset([X, Y], transform=transform)
        
        sample = ds[10]
        expected = (X[10] * 2.0).astype(np.float32)
        np.testing.assert_allclose(sample[0], expected, rtol=1e-5)
        assert sample[1] == Y[10]
        
    def test_dtype_preservation_with_transform(self):
        """Test that dtype is preserved after transform."""
        X = np.random.rand(30, 8, 64).astype(np.float32)
        
        transform = lambda x: x + 1.0
        ds = DefaultDataset([X], transform=transform)
        
        sample = ds[0]
        assert sample[0].dtype == np.float32
        
    def test_integer_dtype_preservation(self):
        """Test integer dtype preservation with transform."""
        X = np.random.randint(0, 255, size=(20, 3, 32, 32), dtype=np.uint8)
        
        transform = lambda x: x / 255.0
        ds = DefaultDataset([X], transform=transform)
        
        sample = ds[5]
        assert sample[0].dtype == np.uint8
        
    def test_len_method(self):
        """Test __len__ method returns correct length."""
        for n in [10, 100, 1000]:
            X = np.random.rand(n, 5, 20)
            ds = DefaultDataset([X])
            assert len(ds) == n
            
    def test_empty_dataset_raises_error(self):
        """Test that empty dataset raises appropriate error."""
        with pytest.raises(IndexError):
            ds = DefaultDataset([])
            
    def test_mismatched_lengths_assertion(self):
        """Test assertion fails with arrays of different lengths."""
        X = np.random.rand(100, 10)
        Y = np.random.rand(50, 10)
        
        with pytest.raises(AssertionError):
            ds = DefaultDataset([X, Y])
            
    def test_indexing_out_of_bounds(self):
        """Test indexing beyond dataset length raises error."""
        X = np.random.rand(10, 5)
        ds = DefaultDataset([X])
        
        with pytest.raises(IndexError):
            _ = ds[10]
            
    def test_negative_indexing(self):
        """Test negative indexing works correctly."""
        n = 20
        X = np.random.rand(n, 5)
        Y = np.arange(n)
        
        ds = DefaultDataset([X, Y])
        last_sample = ds[-1]
        
        np.testing.assert_array_equal(last_sample[0], X[-1])
        assert last_sample[1] == Y[-1]
        
    def test_slice_indexing_not_supported(self):
        """Test that slice indexing raises appropriate error."""
        X = np.random.rand(100, 10)
        ds = DefaultDataset([X])
        
        with pytest.raises(TypeError):
            _ = ds[0:10]
            
    def test_dataloader_compatibility(self):
        """Test compatibility with PyTorch DataLoader."""
        n = 128
        X = np.random.rand(n, 3, 32, 32)
        Y = np.random.randint(0, 10, size=(n,))
        
        ds = DefaultDataset([X, Y])
        loader = DataLoader(ds, batch_size=16, shuffle=True)
        
        batch_count = 0
        for batch in loader:
            batch_count += 1
            assert len(batch) == 2
            assert batch[0].shape[0] <= 16
            
        assert batch_count == 8  # 128 / 16
        
    def test_transform_modifies_only_first_element(self):
        """Test that transform is applied only to the first element."""
        n = 50
        X = np.random.rand(n, 10)
        Y = np.random.rand(n, 5)
        Z = np.random.rand(n, 3)
        
        transform = lambda x: x * 0.0  # Zero out
        ds = DefaultDataset([X, Y, Z], transform=transform)
        
        sample = ds[10]
        assert np.all(sample[0] == 0.0)
        np.testing.assert_array_equal(sample[1], Y[10])
        np.testing.assert_array_equal(sample[2], Z[10])
        
    def test_complex_transform_function(self):
        """Test with more complex transform function."""
        n = 40
        X = np.random.rand(n, 1, 28, 28)
        
        def normalize_and_augment(x):
            # Normalize to [-1, 1]
            x = (x - 0.5) * 2.0
            # Add random noise
            noise = np.random.normal(0, 0.01, x.shape)
            return x + noise
        
        ds = DefaultDataset([X], transform=normalize_and_augment)
        sample = ds[0]
        
        # Check that values are roughly in [-1, 1] range
        assert sample[0].min() >= -1.5
        assert sample[0].max() <= 1.5
        
    def test_with_different_array_types(self):
        """Test with different numpy array types."""
        n = 30
        X_float64 = np.random.rand(n, 10).astype(np.float64)
        Y_int32 = np.random.randint(0, 10, size=(n,)).astype(np.int32)
        Z_bool = np.random.choice([True, False], size=(n, 5))
        
        ds = DefaultDataset([X_float64, Y_int32, Z_bool])
        sample = ds[5]
        
        assert sample[0].dtype == np.float64
        assert sample[1].dtype == np.int32
        assert sample[2].dtype == np.bool_
        
    def test_dataset_iteration(self):
        """Test iterating through entire dataset."""
        n = 25
        X = np.random.rand(n, 5)
        ds = DefaultDataset([X])
        
        count = 0
        for i in range(len(ds)):
            sample = ds[i]
            np.testing.assert_array_equal(sample[0], X[i])
            count += 1
            
        assert count == n
        
    def test_transform_with_none_returns_original(self):
        """Test that None transform returns original data."""
        X = np.random.rand(15, 7, 20)
        ds = DefaultDataset([X], transform=None)
        
        sample = ds[7]
        np.testing.assert_array_equal(sample[0], X[7])


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
