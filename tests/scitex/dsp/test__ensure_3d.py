#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:45:00 (ywatanabe)"
# File: ./tests/scitex/dsp/test__ensure_3d.py

"""
Test module for scitex.dsp.ensure_3d function.
"""

import pytest
import numpy as np
import torch


class TestEnsure3D:
    """Test class for ensure_3d function."""

    def test_import(self):
        """Test that ensure_3d can be imported."""
        from scitex.dsp import ensure_3d

        assert callable(ensure_3d)

    def test_1d_to_3d_numpy(self):
        """Test converting 1D numpy array to 3D."""
        from scitex.dsp import ensure_3d

        # 1D input (seq_len,)
        x_1d = np.array([1, 2, 3, 4, 5])
        result = ensure_3d(x_1d)

        # Should become (1, 1, seq_len)
        assert result.shape == (1, 1, 5)
        assert np.array_equal(result[0, 0], x_1d)

    def test_2d_to_3d_numpy(self):
        """Test converting 2D numpy array to 3D."""
        from scitex.dsp import ensure_3d

        # 2D input (batch_size, seq_len)
        x_2d = np.array([[1, 2, 3], [4, 5, 6]])
        result = ensure_3d(x_2d)

        # Should become (batch_size, 1, seq_len)
        assert result.shape == (2, 1, 3)
        assert np.array_equal(result[:, 0, :], x_2d)

    def test_3d_unchanged_numpy(self):
        """Test that 3D numpy array remains unchanged."""
        from scitex.dsp import ensure_3d

        # 3D input (batch_size, n_channels, seq_len)
        x_3d = np.random.rand(4, 3, 100)
        result = ensure_3d(x_3d)

        # Should remain the same
        assert result.shape == x_3d.shape
        assert np.array_equal(result, x_3d)

    def test_1d_to_3d_torch(self):
        """Test converting 1D torch tensor to 3D."""
        from scitex.dsp import ensure_3d

        # 1D input (seq_len,)
        x_1d = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        result = ensure_3d(x_1d)

        # Should become (1, 1, seq_len)
        assert isinstance(result, torch.Tensor)
        assert result.shape == (1, 1, 5)
        assert torch.equal(result[0, 0], x_1d)

    def test_2d_to_3d_torch(self):
        """Test converting 2D torch tensor to 3D."""
        from scitex.dsp import ensure_3d

        # 2D input (batch_size, seq_len)
        x_2d = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        result = ensure_3d(x_2d)

        # Should become (batch_size, 1, seq_len)
        assert isinstance(result, torch.Tensor)
        assert result.shape == (2, 1, 3)
        assert torch.equal(result[:, 0, :], x_2d)

    def test_3d_unchanged_torch(self):
        """Test that 3D torch tensor remains unchanged."""
        from scitex.dsp import ensure_3d

        # 3D input (batch_size, n_channels, seq_len)
        x_3d = torch.randn(4, 3, 100)
        result = ensure_3d(x_3d)

        # Should remain the same
        assert result.shape == x_3d.shape
        assert torch.equal(result, x_3d)

    def test_empty_arrays(self):
        """Test handling of empty arrays."""
        from scitex.dsp import ensure_3d

        # Empty 1D
        x_empty_1d = np.array([])
        result = ensure_3d(x_empty_1d)
        assert result.shape == (1, 1, 0)

        # Empty 2D
        x_empty_2d = np.array([[], []])
        result = ensure_3d(x_empty_2d)
        assert result.shape[1] == 1  # Added channel dimension

    def test_single_element(self):
        """Test handling of single element arrays."""
        from scitex.dsp import ensure_3d

        # Single element 1D
        x_single = np.array([42])
        result = ensure_3d(x_single)
        assert result.shape == (1, 1, 1)
        assert result[0, 0, 0] == 42

    def test_large_arrays(self):
        """Test with large arrays."""
        from scitex.dsp import ensure_3d

        # Large 1D array
        x_large_1d = np.random.rand(10000)
        result = ensure_3d(x_large_1d)
        assert result.shape == (1, 1, 10000)

        # Large 2D array
        x_large_2d = np.random.rand(100, 1000)
        result = ensure_3d(x_large_2d)
        assert result.shape == (100, 1, 1000)

    def test_dtype_preservation(self):
        """Test that data types are preserved."""
        from scitex.dsp import ensure_3d

        # Test different dtypes
        for dtype in [np.float32, np.float64, np.int32, np.int64]:
            x = np.array([1, 2, 3], dtype=dtype)
            result = ensure_3d(x)
            assert result.dtype == dtype

    def test_torch_device_preservation(self):
        """Test that torch device is preserved."""
        from scitex.dsp import ensure_3d

        if torch.cuda.is_available():
            # Test GPU tensor
            x_gpu = torch.tensor([1.0, 2.0, 3.0]).cuda()
            result = ensure_3d(x_gpu)
            assert result.is_cuda
            assert result.device == x_gpu.device

        # Test CPU tensor
        x_cpu = torch.tensor([1.0, 2.0, 3.0])
        result = ensure_3d(x_cpu)
        assert result.device.type == "cpu"

    def test_gradient_preservation(self):
        """Test that gradients are preserved for torch tensors."""
        from scitex.dsp import ensure_3d

        # Create tensor with gradient
        x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
        result = ensure_3d(x)

        assert result.requires_grad

        # Test gradient flow
        loss = result.sum()
        loss.backward()
        assert x.grad is not None

    @pytest.mark.parametrize(
        "shape,expected",
        [
            ((5,), (1, 1, 5)),  # 1D
            ((3, 10), (3, 1, 10)),  # 2D
            ((2, 4, 8), (2, 4, 8)),  # 3D
        ],
    )
    def test_various_shapes(self, shape, expected):
        """Test various input shapes."""
        from scitex.dsp import ensure_3d

        x = np.ones(shape)
        result = ensure_3d(x)
        assert result.shape == expected

    def test_list_input(self):
        """Test that list input is handled properly."""
        from scitex.dsp import ensure_3d

        # List input should be converted to array first
        x_list = [1, 2, 3, 4, 5]
        result = ensure_3d(x_list)

        # Should work like 1D array
        assert result.shape == (1, 1, 5)
        assert np.array_equal(result[0, 0], x_list)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_ensure_3d.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-05 01:03:47 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/_ensure_3d.py
# 
# from ..decorators import signal_fn
# 
# 
# @signal_fn
# def ensure_3d(x):
#     if x.ndim == 1:  # assumes (seq_len,)
#         x = x.unsqueeze(0).unsqueeze(0)
#     elif x.ndim == 2:  # assumes (batch_siize, seq_len)
#         x = x.unsqueeze(1)
#     return x
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/_ensure_3d.py
# --------------------------------------------------------------------------------
