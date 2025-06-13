#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test__ensure_even_len.py

"""Tests for ensure_even_len function."""

import os
import pytest
import numpy as np
import torch


def test_ensure_even_len_already_even():
    """Test ensure_even_len with already even length."""
from scitex.dsp.utils import ensure_even_len
    
    # Test 1D tensor with even length
    x = torch.randn(100)  # Even length
    result = ensure_even_len(x)
    
    # Should remain unchanged
    assert torch.equal(result, x)
    assert result.shape == x.shape
    assert result.shape[-1] % 2 == 0


def test_ensure_even_len_odd_to_even():
    """Test ensure_even_len with odd length."""
from scitex.dsp.utils import ensure_even_len
    
    # Test 1D tensor with odd length
    x = torch.randn(101)  # Odd length
    result = ensure_even_len(x)
    
    # Should remove last element
    assert result.shape == (100,)
    assert result.shape[-1] % 2 == 0
    assert torch.equal(result, x[:-1])


def test_ensure_even_len_2d_tensor():
    """Test ensure_even_len with 2D tensor."""
from scitex.dsp.utils import ensure_even_len
    
    # Test 2D tensor with odd last dimension
    x = torch.randn(10, 101)  # (batch, odd_seq_len)
    result = ensure_even_len(x)
    
    # Should remove last element from last dimension
    assert result.shape == (10, 100)
    assert result.shape[-1] % 2 == 0
    assert torch.equal(result, x[:, :-1])


def test_ensure_even_len_3d_tensor():
    """Test ensure_even_len with 3D tensor."""
from scitex.dsp.utils import ensure_even_len
    
    # Test 3D tensor with odd last dimension
    x = torch.randn(5, 8, 99)  # (batch, channels, odd_seq_len)
    result = ensure_even_len(x)
    
    # Should remove last element from last dimension
    assert result.shape == (5, 8, 98)
    assert result.shape[-1] % 2 == 0
    assert torch.equal(result, x[:, :, :-1])


def test_ensure_even_len_4d_tensor():
    """Test ensure_even_len with 4D tensor."""
from scitex.dsp.utils import ensure_even_len
    
    # Test 4D tensor with odd last dimension
    x = torch.randn(2, 3, 4, 51)  # Odd last dimension
    result = ensure_even_len(x)
    
    # Should remove last element from last dimension
    assert result.shape == (2, 3, 4, 50)
    assert result.shape[-1] % 2 == 0
    assert torch.equal(result, x[:, :, :, :-1])


def test_ensure_even_len_numpy_array():
    """Test ensure_even_len with numpy arrays."""
from scitex.dsp.utils import ensure_even_len
    
    # Test with numpy array
    x = np.random.randn(101)  # Odd length
    result = ensure_even_len(x)
    
    # Should work with numpy arrays
    assert result.shape == (100,)
    assert result.shape[-1] % 2 == 0
    assert np.array_equal(result, x[:-1])


def test_ensure_even_len_preserves_dtype():
    """Test that ensure_even_len preserves data type."""
from scitex.dsp.utils import ensure_even_len
    
    # Test different dtypes
    dtypes = [torch.float32, torch.float64, torch.int32, torch.int64]
    
    for dtype in dtypes:
        x = torch.randn(101).to(dtype)
        result = ensure_even_len(x)
        assert result.dtype == dtype


def test_ensure_even_len_preserves_device():
    """Test that ensure_even_len preserves device."""
from scitex.dsp.utils import ensure_even_len
    
    # Test CPU tensor
    x_cpu = torch.randn(101)
    result_cpu = ensure_even_len(x_cpu)
    assert result_cpu.device == x_cpu.device
    
    # Test CUDA tensor if available
    if torch.cuda.is_available():
        x_cuda = torch.randn(101).cuda()
        result_cuda = ensure_even_len(x_cuda)
        assert result_cuda.device == x_cuda.device


def test_ensure_even_len_preserves_requires_grad():
    """Test that ensure_even_len preserves gradient tracking."""
from scitex.dsp.utils import ensure_even_len
    
    # Test with requires_grad=True
    x = torch.randn(101, requires_grad=True)
    result = ensure_even_len(x)
    assert result.requires_grad == x.requires_grad
    
    # Test with requires_grad=False
    x = torch.randn(101, requires_grad=False)
    result = ensure_even_len(x)
    assert result.requires_grad == x.requires_grad


def test_ensure_even_len_gradient_flow():
    """Test that gradients flow through ensure_even_len."""
from scitex.dsp.utils import ensure_even_len
    
    x = torch.randn(101, requires_grad=True)
    result = ensure_even_len(x)
    
    # Compute a loss and backpropagate
    loss = result.sum()
    loss.backward()
    
    # Original tensor should have gradients
    assert x.grad is not None
    # First 100 elements should have gradients, last element should not
    assert torch.equal(x.grad[:100], torch.ones(100))
    assert x.grad[100] == 0  # Last element should have zero gradient


def test_ensure_even_len_small_tensors():
    """Test ensure_even_len with small tensors."""
from scitex.dsp.utils import ensure_even_len
    
    # Test length 1 (odd)
    x1 = torch.tensor([5.0])
    result1 = ensure_even_len(x1)
    assert result1.shape == (0,)  # Should become empty
    
    # Test length 2 (even)
    x2 = torch.tensor([1.0, 2.0])
    result2 = ensure_even_len(x2)
    assert torch.equal(result2, x2)  # Should remain unchanged
    
    # Test length 3 (odd)
    x3 = torch.tensor([1.0, 2.0, 3.0])
    result3 = ensure_even_len(x3)
    assert torch.equal(result3, torch.tensor([1.0, 2.0]))


def test_ensure_even_len_empty_tensor():
    """Test ensure_even_len with empty tensor."""
from scitex.dsp.utils import ensure_even_len
    
    x = torch.empty(0)
    result = ensure_even_len(x)
    
    # Empty tensor has even length (0), should remain unchanged
    assert torch.equal(result, x)
    assert result.shape == (0,)


def test_ensure_even_len_consistency():
    """Test that ensure_even_len is consistent across calls."""
from scitex.dsp.utils import ensure_even_len
    
    x = torch.randn(101)
    
    # Multiple calls should produce identical results
    result1 = ensure_even_len(x)
    result2 = ensure_even_len(x)
    
    assert torch.equal(result1, result2)


def test_ensure_even_len_real_signal_example():
    """Test ensure_even_len with realistic signal processing example."""
from scitex.dsp.utils import ensure_even_len
    
    # Simulate EEG signal with odd number of samples
    fs = 250  # Hz
    duration = 2.001  # Slightly over 2 seconds to get odd samples
    n_samples = int(fs * duration)  # Should be 501 (odd)
    
    # Create a sine wave signal
    t = torch.linspace(0, duration, n_samples)
    signal = torch.sin(2 * np.pi * 10 * t)  # 10 Hz sine wave
    
    assert signal.shape[-1] % 2 == 1  # Should be odd
    
    result = ensure_even_len(signal)
    
    # Should now have even length
    assert result.shape[-1] % 2 == 0
    assert result.shape[-1] == 500  # One less than original
    
    # Signal should be preserved except for last sample
    assert torch.allclose(result, signal[:-1])


def test_ensure_even_len_multichannel_signal():
    """Test ensure_even_len with multi-channel signals."""
from scitex.dsp.utils import ensure_even_len
    
    # Simulate multi-channel EEG data
    n_channels = 64
    n_samples = 1001  # Odd number of samples
    
    signal = torch.randn(n_channels, n_samples)
    result = ensure_even_len(signal)
    
    # Should preserve channel dimension, make samples even
    assert result.shape == (n_channels, 1000)
    assert result.shape[-1] % 2 == 0
    assert torch.equal(result, signal[:, :-1])


def test_ensure_even_len_batch_processing():
    """Test ensure_even_len with batch of signals."""
from scitex.dsp.utils import ensure_even_len
    
    # Simulate batch of signals
    batch_size = 32
    n_channels = 16
    n_samples = 999  # Odd number of samples
    
    signals = torch.randn(batch_size, n_channels, n_samples)
    result = ensure_even_len(signals)
    
    # Should preserve batch and channel dimensions, make samples even
    assert result.shape == (batch_size, n_channels, 998)
    assert result.shape[-1] % 2 == 0
    assert torch.equal(result, signals[:, :, :-1])


def test_ensure_even_len_fft_compatibility():
    """Test ensure_even_len for FFT preprocessing."""
from scitex.dsp.utils import ensure_even_len
    
    # Create a signal that needs to be even for FFT
    signal = torch.randn(1023)  # Odd length
    
    # Ensure even length for FFT
    even_signal = ensure_even_len(signal)
    
    # Should now be compatible with FFT requirements
    assert even_signal.shape[-1] % 2 == 0
    assert even_signal.shape[-1] == 1022
    
    # Should be able to compute FFT without issues
    fft_result = torch.fft.fft(even_signal)
    assert fft_result.shape == even_signal.shape


def test_ensure_even_len_memory_view():
    """Test that ensure_even_len returns a view when possible."""
from scitex.dsp.utils import ensure_even_len
    
    # For even length, should return the same tensor (view)
    x_even = torch.randn(100)
    result_even = ensure_even_len(x_even)
    assert result_even is x_even  # Should be the same object
    
    # For odd length, should return a new view (slice)
    x_odd = torch.randn(101)
    result_odd = ensure_even_len(x_odd)
    assert result_odd is not x_odd  # Should be different objects
    assert result_odd.data_ptr() == x_odd.data_ptr()  # But same underlying data


def test_ensure_even_len_different_shapes():
    """Test ensure_even_len with various tensor shapes."""
from scitex.dsp.utils import ensure_even_len
    
    # Test various shapes where last dimension is odd
    shapes = [
        (101,),           # 1D
        (10, 101),        # 2D
        (5, 8, 101),      # 3D
        (2, 3, 4, 101),   # 4D
        (2, 2, 2, 2, 101) # 5D
    ]
    
    for shape in shapes:
        x = torch.randn(shape)
        result = ensure_even_len(x)
        
        # Last dimension should be reduced by 1
        expected_shape = list(shape)
        expected_shape[-1] -= 1
        
        assert result.shape == tuple(expected_shape)
        assert result.shape[-1] % 2 == 0


def test_ensure_even_len_integration_test():
    """Integration test for ensure_even_len in signal processing pipeline."""
from scitex.dsp.utils import ensure_even_len
    
    # Simulate a complete signal processing pipeline
    
    # 1. Generate raw signal with odd length
    fs = 1000
    t = torch.linspace(0, 2.001, 2001)  # Odd number of samples
    signal = torch.sin(2 * np.pi * 50 * t) + 0.1 * torch.randn(2001)
    
    # 2. Ensure even length for downstream processing
    even_signal = ensure_even_len(signal)
    assert even_signal.shape[-1] % 2 == 0
    
    # 3. Apply windowing (requires even length)
    window = torch.hann_window(even_signal.shape[-1])
    windowed_signal = even_signal * window
    
    # 4. Compute FFT (works better with even lengths)
    fft_result = torch.fft.fft(windowed_signal)
    
    # 5. Verify the pipeline worked
    assert fft_result.shape == windowed_signal.shape
    assert torch.all(torch.isfinite(fft_result))


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
