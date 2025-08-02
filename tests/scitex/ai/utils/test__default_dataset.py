#!/usr/bin/env python3
"""Tests for scitex.ai.utils._default_dataset module.

This module provides comprehensive tests for the DefaultDataset class,
which is used for creating PyTorch datasets from arrays with optional
transformations.
"""

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader

from scitex.ai.utils import DefaultDataset


class TestDefaultDataset:
    """Test DefaultDataset class functionality."""

    def test_initialization_single_array(self):
        """Test initialization with single array."""
        X = np.random.rand(100, 10)
        ds = DefaultDataset([X])
        assert len(ds) == 100
        assert ds.transform is None
        assert ds.arrs_list == [X]
        assert ds.arrs == [X]  # Check alias

    def test_initialization_multiple_arrays(self):
        """Test initialization with multiple arrays."""
        n = 50
        X = np.random.rand(n, 19, 1000)
        T = np.random.randint(0, 4, size=(n, 1))
        S = np.random.randint(0, 999, size=(n, 1))
        
        ds = DefaultDataset([X, T, S])
        assert len(ds) == n
        assert len(ds.arrs_list) == 3

    def test_getitem_single_array(self):
        """Test __getitem__ with single array."""
        X = np.random.rand(10, 5)
        ds = DefaultDataset([X])
        
        # Get first item
        item = ds[0]
        assert len(item) == 1
        assert np.array_equal(item[0], X[0])
        
        # Get last item
        item = ds[9]
        assert np.array_equal(item[0], X[9])

    def test_getitem_multiple_arrays(self):
        """Test __getitem__ with multiple arrays."""
        n = 20
        X = np.random.rand(n, 10)
        T = np.random.randint(0, 4, size=(n,))
        S = np.random.randint(0, 999, size=(n,))
        
        ds = DefaultDataset([X, T, S])
        
        # Check first item
        item = ds[0]
        assert len(item) == 3
        assert np.array_equal(item[0], X[0])
        assert item[1] == T[0]
        assert item[2] == S[0]

    def test_transform_application(self):
        """Test that transform is applied only to first array."""
        def double_transform(x):
            return x * 2
        
        X = np.ones((10, 5))
        T = np.ones((10,))
        
        ds = DefaultDataset([X, T], transform=double_transform)
        
        item = ds[0]
        # First array should be transformed
        assert np.allclose(item[0], 2.0)
        # Second array should not be transformed
        assert item[1] == 1.0

    def test_transform_preserves_dtype(self):
        """Test that transform preserves original dtype."""
        def add_noise(x):
            return x + np.random.randn(*x.shape) * 0.01
        
        X = np.ones((10, 5), dtype=np.float32)
        ds = DefaultDataset([X], transform=add_noise)
        
        item = ds[0]
        assert item[0].dtype == np.float32

    def test_zero_length_arrays_assertion(self):
        """Test that arrays with zero length raise assertion error."""
        X = np.array([])  # Empty array
        
        with pytest.raises(AssertionError):
            DefaultDataset([X])

    def test_different_dtypes(self):
        """Test dataset with arrays of different dtypes."""
        X = np.random.rand(10, 5).astype(np.float32)
        T = np.random.randint(0, 4, size=(10,)).astype(np.int64)
        S = np.random.rand(10).astype(np.float64)
        
        ds = DefaultDataset([X, T, S])
        item = ds[0]
        
        assert item[0].dtype == np.float32
        assert item[1].dtype == np.int64
        assert item[2].dtype == np.float64

    def test_empty_arrays_list_error(self):
        """Test that empty arrays list raises appropriate error."""
        with pytest.raises(IndexError):
            DefaultDataset([])

    def test_mismatched_lengths_not_validated(self):
        """Test that arrays with different lengths are not validated at init.
        
        Note: The current implementation doesn't validate that all arrays
        have the same length, which could be a potential bug.
        """
        X = np.random.rand(10, 5)
        T = np.random.rand(8)  # Different length
        
        # This actually doesn't raise an error in current implementation
        ds = DefaultDataset([X, T])
        assert len(ds) == 10  # Uses length of first array

    def test_dataloader_compatibility(self):
        """Test compatibility with PyTorch DataLoader."""
        n = 100
        X = np.random.rand(n, 10)
        T = np.random.randint(0, 4, size=(n,))
        
        ds = DefaultDataset([X, T])
        loader = DataLoader(ds, batch_size=16, shuffle=True)
        
        # Check that we can iterate through loader
        batch_count = 0
        for batch in loader:
            batch_count += 1
            assert len(batch) == 2  # X and T
            assert batch[0].shape[0] <= 16  # Batch size
            assert batch[1].shape[0] <= 16
        
        # Should have correct number of batches
        expected_batches = (n + 15) // 16  # Ceiling division
        assert batch_count == expected_batches

    def test_indexing_bounds(self):
        """Test indexing boundary conditions."""
        X = np.random.rand(10, 5)
        ds = DefaultDataset([X])
        
        # Valid indices
        assert ds[0] is not None
        assert ds[9] is not None
        
        # Invalid indices should raise IndexError
        with pytest.raises(IndexError):
            ds[10]
        
        with pytest.raises(IndexError):
            ds[-11]

    def test_negative_indexing(self):
        """Test negative indexing support."""
        X = np.random.rand(10, 5)
        ds = DefaultDataset([X])
        
        # Negative indexing should work
        last_item = ds[-1]
        assert np.array_equal(last_item[0], X[-1])
        
        first_item = ds[-10]
        assert np.array_equal(first_item[0], X[0])

    def test_complex_transform(self):
        """Test with more complex transform function."""
        def normalize_transform(x):
            mean = x.mean()
            std = x.std()
            return (x - mean) / (std + 1e-8)
        
        X = np.random.rand(20, 10) * 100 + 50
        ds = DefaultDataset([X], transform=normalize_transform)
        
        item = ds[0]
        transformed = normalize_transform(X[0].astype(np.float64)).astype(X.dtype)
        assert np.allclose(item[0], transformed)

    def test_multidimensional_arrays(self):
        """Test with various multidimensional array shapes."""
        # 3D array (e.g., time series with channels)
        X_3d = np.random.rand(50, 19, 1000)
        # 2D array (e.g., features)
        X_2d = np.random.rand(50, 100)
        # 1D array (e.g., labels)
        T_1d = np.random.randint(0, 4, size=(50,))
        
        ds = DefaultDataset([X_3d, X_2d, T_1d])
        
        item = ds[0]
        assert item[0].shape == (19, 1000)
        assert item[1].shape == (100,)
        assert isinstance(item[2], (int, np.integer))

    def test_example_from_docstring(self):
        """Test the exact example given in the docstring."""
        n = 1024
        n_chs = 19
        X = np.random.rand(n, n_chs, 1000)
        T = np.random.randint(0, 4, size=(n, 1))
        S = np.random.randint(0, 999, size=(n, 1))
        Sr = np.random.randint(0, 4, size=(n, 1))
        
        arrs_list = [X, T, S, Sr]
        transform = None
        ds = DefaultDataset(arrs_list, transform=transform)
        
        assert len(ds) == 1024
        
        # Check that items are retrieved correctly
        item = ds[0]
        assert len(item) == 4
        assert item[0].shape == (n_chs, 1000)
        assert item[1].shape == (1,)
        assert item[2].shape == (1,)
        assert item[3].shape == (1,)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/utils/_default_dataset.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# 
# from torch.utils.data import Dataset
# import numpy as np
# 
# 
# class DefaultDataset(Dataset):
#     """
#     Apply transform for the first element of arrs_list
# 
#     Example:
#         n = 1024
#         n_chs = 19
#         X = np.random.rand(n, n_chs, 1000)
#         T = np.random.randint(0, 4, size=(n, 1))
#         S = np.random.randint(0, 999, size=(n, 1))
#         Sr = np.random.randint(0, 4, size=(n, 1))
# 
#         arrs_list = [X, T, S, Sr]
#         transform = None
#         ds = _DefaultDataset(arrs_list, transform=transform)
#         len(ds) # 1024
#     """
# 
#     def __init__(self, arrs_list, transform=None):
#         self.arrs_list = arrs_list
#         self.arrs = arrs_list  # alias
# 
#         assert np.all([len(arr) for arr in arrs_list])
# 
#         self.length = len(arrs_list[0])
#         self.transform = transform
# 
#     def __len__(self):
#         return self.length
# 
#     def __getitem__(self, idx):
#         arrs_list_idx = [arr[idx] for arr in self.arrs_list]
# 
#         # Here, you might want to transform, or apply DA on X as a numpy array
#         if self.transform:
#             dtype_orig = arrs_list_idx[0].dtype
#             arrs_list_idx[0] = self.transform(
#                 arrs_list_idx[0].astype(np.float64)
#             ).astype(dtype_orig)
#         return arrs_list_idx

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/utils/_default_dataset.py
# --------------------------------------------------------------------------------
