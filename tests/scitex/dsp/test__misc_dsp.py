#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 12:51:31 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__misc.py

import pytest
import numpy as np
import torch
from scitex.dsp import ensure_3d


class TestMisc:
    """Test cases for miscellaneous DSP functions."""

    def test_import(self):
        """Test that ensure_3d can be imported."""
        assert callable(ensure_3d)

    def test_ensure_3d_1d_numpy(self):
        """Test ensure_3d with 1D numpy array."""
        x_1d = np.array([1, 2, 3, 4, 5])
        result = ensure_3d(x_1d)

        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 1, 5)
        assert np.array_equal(result[0, 0], x_1d)

    def test_ensure_3d_2d_numpy(self):
        """Test ensure_3d with 2D numpy array."""
        x_2d = np.array([[1, 2, 3], [4, 5, 6]])
        result = ensure_3d(x_2d)

        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 1, 3)
        assert np.array_equal(result[:, 0, :], x_2d)

    def test_ensure_3d_3d_numpy(self):
        """Test ensure_3d with 3D numpy array (should remain unchanged)."""
        x_3d = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        result = ensure_3d(x_3d)

        assert isinstance(result, np.ndarray)
        assert result.shape == x_3d.shape
        assert np.array_equal(result, x_3d)

    def test_ensure_3d_1d_torch(self):
        """Test ensure_3d with 1D torch tensor."""
        x_1d = torch.tensor([1, 2, 3, 4, 5])
        result = ensure_3d(x_1d)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (1, 1, 5)
        assert torch.equal(result[0, 0], x_1d)

    def test_ensure_3d_2d_torch(self):
        """Test ensure_3d with 2D torch tensor."""
        x_2d = torch.tensor([[1, 2, 3], [4, 5, 6]])
        result = ensure_3d(x_2d)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (2, 1, 3)
        assert torch.equal(result[:, 0, :], x_2d)

    def test_ensure_3d_3d_torch(self):
        """Test ensure_3d with 3D torch tensor (should remain unchanged)."""
        x_3d = torch.tensor([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        result = ensure_3d(x_3d)

        assert isinstance(result, torch.Tensor)
        assert result.shape == x_3d.shape
        assert torch.equal(result, x_3d)

    def test_ensure_3d_empty_1d(self):
        """Test ensure_3d with empty 1D array."""
        x_empty = np.array([])
        result = ensure_3d(x_empty)

        assert result.shape == (1, 1, 0)

    def test_ensure_3d_dtype_preservation(self):
        """Test that ensure_3d preserves data types."""
        # Test different numpy dtypes
        for dtype in [np.float32, np.float64, np.int32, np.int64]:
            x = np.array([1, 2, 3], dtype=dtype)
            result = ensure_3d(x)
            assert result.dtype == dtype

        # Test torch dtypes
        for dtype in [torch.float32, torch.float64, torch.int32, torch.int64]:
            x = torch.tensor([1, 2, 3], dtype=dtype)
            result = ensure_3d(x)
            assert result.dtype == dtype

    def test_ensure_3d_device_preservation(self):
        """Test that ensure_3d preserves torch device."""
        if torch.cuda.is_available():
            x_gpu = torch.tensor([1, 2, 3]).cuda()
            result = ensure_3d(x_gpu)
            assert result.is_cuda
            assert result.device == x_gpu.device

    def test_ensure_3d_contiguity(self):
        """Test that ensure_3d output is contiguous."""
        # Numpy
        x_np = np.array([1, 2, 3, 4])
        result_np = ensure_3d(x_np)
        assert result_np.flags["C_CONTIGUOUS"]

        # Torch
        x_torch = torch.tensor([1, 2, 3, 4])
        result_torch = ensure_3d(x_torch)
        assert result_torch.is_contiguous()

    def test_ensure_3d_large_array(self):
        """Test ensure_3d with large array."""
        large_1d = np.random.randn(10000)
        result = ensure_3d(large_1d)

        assert result.shape == (1, 1, 10000)
        assert np.array_equal(result[0, 0], large_1d)

    def test_ensure_3d_batch_processing(self):
        """Test ensure_3d preserves batch dimension correctly."""
        batch_size = 16
        seq_len = 100
        x_2d = np.random.randn(batch_size, seq_len)
        result = ensure_3d(x_2d)

        assert result.shape == (batch_size, 1, seq_len)
        # Check that each batch is preserved
        for i in range(batch_size):
            assert np.array_equal(result[i, 0], x_2d[i])

    def test_ensure_3d_gradient_preservation(self):
        """Test that ensure_3d preserves gradients for torch tensors."""
        x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
        result = ensure_3d(x)

        assert result.requires_grad

        # Test gradient flow
        loss = result.sum()
        loss.backward()
        assert x.grad is not None
        assert torch.all(x.grad == 1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
