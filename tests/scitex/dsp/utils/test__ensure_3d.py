#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:25:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test__ensure_3d.py

"""Tests for ensure_3d function."""

import os
import pytest
import numpy as np
import torch
from unittest.mock import patch


def test_ensure_3d_1d_input():
    """Test ensure_3d with 1D input."""
from scitex.dsp.utils import ensure_3d
    
    # Create 1D tensor (seq_len,)
    x = torch.randn(100)
    result = ensure_3d(x)
    
    # Should become (1, 1, seq_len)
    assert result.ndim == 3
    assert result.shape == (1, 1, 100)
    assert torch.equal(result.squeeze(), x)


def test_ensure_3d_2d_input():
    """Test ensure_3d with 2D input."""
from scitex.dsp.utils import ensure_3d
    
    # Create 2D tensor (batch_size, seq_len)
    x = torch.randn(32, 100)
    result = ensure_3d(x)
    
    # Should become (batch_size, 1, seq_len)
    assert result.ndim == 3
    assert result.shape == (32, 1, 100)
    assert torch.equal(result.squeeze(1), x)


def test_ensure_3d_3d_input():
    """Test ensure_3d with 3D input (should remain unchanged)."""
from scitex.dsp.utils import ensure_3d
    
    # Create 3D tensor (batch_size, n_channels, seq_len)
    x = torch.randn(32, 5, 100)
    result = ensure_3d(x)
    
    # Should remain unchanged
    assert result.ndim == 3
    assert result.shape == (32, 5, 100)
    assert torch.equal(result, x)


def test_ensure_3d_0d_input():
    """Test ensure_3d with 0D input (scalar)."""
from scitex.dsp.utils import ensure_3d
    
    # Create 0D tensor (scalar)
    x = torch.tensor(5.0)
    result = ensure_3d(x)
    
    # Should remain unchanged (not handled by function)
    assert result.ndim == 0
    assert torch.equal(result, x)


def test_ensure_3d_4d_input():
    """Test ensure_3d with 4D input (should remain unchanged)."""
from scitex.dsp.utils import ensure_3d
    
    # Create 4D tensor
    x = torch.randn(10, 5, 20, 100)
    result = ensure_3d(x)
    
    # Should remain unchanged (not handled by function)
    assert result.ndim == 4
    assert result.shape == (10, 5, 20, 100)
    assert torch.equal(result, x)


def test_ensure_3d_preserves_dtype():
    """Test that ensure_3d preserves data type."""
from scitex.dsp.utils import ensure_3d
    
    # Test different dtypes
    dtypes = [torch.float32, torch.float64, torch.int32, torch.int64]
    
    for dtype in dtypes:
        x = torch.randn(100).to(dtype)
        result = ensure_3d(x)
        assert result.dtype == dtype


def test_ensure_3d_preserves_device():
    """Test that ensure_3d preserves device."""
from scitex.dsp.utils import ensure_3d
    
    # Test CPU tensor
    x_cpu = torch.randn(100)
    result_cpu = ensure_3d(x_cpu)
    assert result_cpu.device == x_cpu.device
    
    # Test CUDA tensor if available
    if torch.cuda.is_available():
        x_cuda = torch.randn(100).cuda()
        result_cuda = ensure_3d(x_cuda)
        assert result_cuda.device == x_cuda.device


def test_ensure_3d_preserves_requires_grad():
    """Test that ensure_3d preserves gradient tracking."""
from scitex.dsp.utils import ensure_3d
    
    # Test with requires_grad=True
    x = torch.randn(100, requires_grad=True)
    result = ensure_3d(x)
    assert result.requires_grad == x.requires_grad
    
    # Test with requires_grad=False
    x = torch.randn(100, requires_grad=False)
    result = ensure_3d(x)
    assert result.requires_grad == x.requires_grad


def test_ensure_3d_gradient_flow():
    """Test that gradients flow through ensure_3d."""
from scitex.dsp.utils import ensure_3d
    
    x = torch.randn(100, requires_grad=True)
    result = ensure_3d(x)
    
    # Compute a loss and backpropagate
    loss = result.sum()
    loss.backward()
    
    # Original tensor should have gradients
    assert x.grad is not None
    assert x.grad.shape == x.shape


def test_ensure_3d_with_different_sizes():
    """Test ensure_3d with various input sizes."""
from scitex.dsp.utils import ensure_3d
    
    # Test various 1D sizes
    sizes_1d = [1, 10, 100, 1000]
    for size in sizes_1d:
        x = torch.randn(size)
        result = ensure_3d(x)
        assert result.shape == (1, 1, size)
    
    # Test various 2D sizes
    batch_sizes = [1, 5, 32]
    seq_lens = [10, 100, 1000]
    for batch_size in batch_sizes:
        for seq_len in seq_lens:
            x = torch.randn(batch_size, seq_len)
            result = ensure_3d(x)
            assert result.shape == (batch_size, 1, seq_len)


def test_ensure_3d_empty_tensors():
    """Test ensure_3d with empty tensors."""
from scitex.dsp.utils import ensure_3d
    
    # Test empty 1D tensor
    x = torch.empty(0)
    result = ensure_3d(x)
    assert result.shape == (1, 1, 0)
    
    # Test empty 2D tensor
    x = torch.empty(0, 0)
    result = ensure_3d(x)
    assert result.shape == (0, 1, 0)


def test_ensure_3d_torch_fn_decorator():
    """Test that the torch_fn decorator works correctly."""
from scitex.dsp.utils import ensure_3d
    
    # Test with numpy array input (should be converted by decorator)
    x_np = np.random.randn(100)
    result = ensure_3d(x_np)
    
    # Should return a torch tensor
    assert isinstance(result, torch.Tensor)
    assert result.ndim == 3
    assert result.shape == (1, 1, 100)


def test_ensure_3d_torch_fn_with_list():
    """Test torch_fn decorator with list input."""
from scitex.dsp.utils import ensure_3d
    
    # Test with list input
    x_list = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = ensure_3d(x_list)
    
    # Should convert to tensor and ensure 3D
    assert isinstance(result, torch.Tensor)
    assert result.ndim == 3
    assert result.shape == (1, 1, 5)
    assert torch.allclose(result.squeeze(), torch.tensor(x_list))


def test_ensure_3d_real_signal_example():
    """Test ensure_3d with realistic signal processing example."""
from scitex.dsp.utils import ensure_3d
    
    # Simulate a realistic EEG signal scenario
    fs = 250  # sampling frequency
    duration = 2.0  # 2 seconds
    n_samples = int(fs * duration)
    
    # Single channel signal
    signal_1d = torch.sin(2 * np.pi * 10 * torch.linspace(0, duration, n_samples))
    result_1d = ensure_3d(signal_1d)
    assert result_1d.shape == (1, 1, n_samples)
    
    # Multi-trial signal
    n_trials = 20
    signal_2d = torch.sin(2 * np.pi * 10 * torch.linspace(0, duration, n_samples)).repeat(n_trials, 1)
    result_2d = ensure_3d(signal_2d)
    assert result_2d.shape == (n_trials, 1, n_samples)


def test_ensure_3d_consistency_across_calls():
    """Test that ensure_3d is consistent across multiple calls."""
from scitex.dsp.utils import ensure_3d
    
    x = torch.randn(100)
    
    # Multiple calls should produce identical results
    result1 = ensure_3d(x)
    result2 = ensure_3d(x)
    
    assert torch.equal(result1, result2)


def test_ensure_3d_memory_efficiency():
    """Test that ensure_3d doesn't unnecessarily copy data."""
from scitex.dsp.utils import ensure_3d
    
    # For 3D input, should return the same tensor (view)
    x = torch.randn(32, 5, 100)
    result = ensure_3d(x)
    
    # Should be the same object for 3D input
    assert result is x


def test_ensure_3d_shape_semantics():
    """Test the semantic meaning of dimensions after ensure_3d."""
from scitex.dsp.utils import ensure_3d
    
    # Test 1D: (seq_len,) -> (batch=1, channels=1, seq_len)
    seq_len = 200
    x_1d = torch.randn(seq_len)
    result_1d = ensure_3d(x_1d)
    assert result_1d.shape[0] == 1  # batch dimension
    assert result_1d.shape[1] == 1  # channel dimension  
    assert result_1d.shape[2] == seq_len  # sequence dimension
    
    # Test 2D: (batch, seq_len) -> (batch, channels=1, seq_len)
    batch_size, seq_len = 16, 200
    x_2d = torch.randn(batch_size, seq_len)
    result_2d = ensure_3d(x_2d)
    assert result_2d.shape[0] == batch_size  # batch dimension preserved
    assert result_2d.shape[1] == 1  # channel dimension added
    assert result_2d.shape[2] == seq_len  # sequence dimension preserved


def test_ensure_3d_integration_with_torch_operations():
    """Test that ensure_3d output works with common torch operations."""
from scitex.dsp.utils import ensure_3d
    
    x = torch.randn(100)
    result = ensure_3d(x)
    
    # Test common operations work on result
    assert result.mean().item() is not None
    assert result.std().item() is not None
    assert result.max().item() is not None
    assert result.min().item() is not None
    
    # Test reshaping works
    reshaped = result.view(-1)
    assert reshaped.shape == (100,)
    
    # Test slicing works
    subset = result[:, :, :50]
    assert subset.shape == (1, 1, 50)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
