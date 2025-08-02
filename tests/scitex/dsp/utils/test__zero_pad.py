#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:30:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test__zero_pad.py

"""Tests for zero padding utilities."""

import os
import pytest
import numpy as np
import torch
from unittest.mock import patch


def test_zero_pad_1d_basic():
    """Test basic 1D zero padding."""
    from scitex.dsp.utils import _zero_pad_1d
    
    x = torch.tensor([1, 2, 3])
    result = _zero_pad_1d(x, 7)
    
    # Should be padded to length 7
    assert len(result) == 7
    # Original values should be preserved in the center
    assert torch.equal(result[2:5], x)
    # Padding should be zeros
    assert torch.equal(result[:2], torch.zeros(2))
    assert torch.equal(result[5:], torch.zeros(2))


def test_zero_pad_1d_even_padding():
    """Test 1D zero padding with even padding."""
    from scitex.dsp.utils import _zero_pad_1d
    
    x = torch.tensor([1, 2])
    result = _zero_pad_1d(x, 6)
    
    # Should be padded to length 6
    assert len(result) == 6
    # 4 zeros to add, 2 on each side
    assert torch.equal(result[2:4], x)
    assert torch.equal(result[:2], torch.zeros(2))
    assert torch.equal(result[4:], torch.zeros(2))


def test_zero_pad_1d_odd_padding():
    """Test 1D zero padding with odd padding."""
    from scitex.dsp.utils import _zero_pad_1d
    
    x = torch.tensor([1, 2])
    result = _zero_pad_1d(x, 5)
    
    # Should be padded to length 5
    assert len(result) == 5
    # 3 zeros to add, 1 left, 2 right (left gets less)
    assert torch.equal(result[1:3], x)
    assert torch.equal(result[:1], torch.zeros(1))
    assert torch.equal(result[3:], torch.zeros(2))


def test_zero_pad_1d_no_padding_needed():
    """Test 1D zero padding when no padding is needed."""
    from scitex.dsp.utils import _zero_pad_1d
    
    x = torch.tensor([1, 2, 3, 4, 5])
    result = _zero_pad_1d(x, 5)
    
    # Should be unchanged
    assert torch.equal(result, x)


def test_zero_pad_1d_numpy_input():
    """Test 1D zero padding with numpy input."""
    from scitex.dsp.utils import _zero_pad_1d
    
    x = np.array([1, 2, 3])
    result = _zero_pad_1d(x, 7)
    
    # Should be a torch tensor
    assert isinstance(result, torch.Tensor)
    assert len(result) == 7
    # Original values should be preserved
    assert torch.equal(result[2:5], torch.tensor([1, 2, 3]))


def test_zero_pad_basic():
    """Test basic zero padding of multiple tensors."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1, 2, 3])
    x2 = torch.tensor([4, 5])
    x3 = torch.tensor([6, 7, 8, 9])
    
    result = zero_pad([x1, x2, x3])
    
    # Should stack into a tensor of shape (3, 4)
    assert result.shape == (3, 4)
    
    # Check first tensor (length 3 -> 4)
    assert torch.equal(result[0], torch.tensor([0, 1, 2, 3]))
    
    # Check second tensor (length 2 -> 4)
    assert torch.equal(result[1], torch.tensor([1, 4, 5, 0]))
    
    # Check third tensor (length 4 -> 4, no padding)
    assert torch.equal(result[2], torch.tensor([6, 7, 8, 9]))


def test_zero_pad_mixed_inputs():
    """Test zero padding with mixed input types."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1, 2, 3])  # torch tensor
    x2 = np.array([4, 5])         # numpy array
    x3 = [6, 7, 8, 9, 10]         # list
    
    result = zero_pad([x1, x2, x3])
    
    # Should stack into a tensor of shape (3, 5)
    assert result.shape == (3, 5)
    assert isinstance(result, torch.Tensor)
    
    # Check that all data is preserved correctly
    assert torch.equal(result[0], torch.tensor([1, 1, 2, 3, 0]))  # 1 left, 1 right padding
    assert torch.equal(result[1], torch.tensor([1, 1, 4, 5, 0]))  # 1 left, 1 right padding
    assert torch.equal(result[2], torch.tensor([6, 7, 8, 9, 10])) # no padding


def test_zero_pad_single_tensor():
    """Test zero padding with single tensor."""
    from scitex.dsp.utils import zero_pad
    
    x = torch.tensor([1, 2, 3, 4])
    result = zero_pad([x])
    
    # Should have shape (1, 4)
    assert result.shape == (1, 4)
    assert torch.equal(result[0], x)


def test_zero_pad_empty_list():
    """Test zero padding with empty list."""
    from scitex.dsp.utils import zero_pad
    
    with pytest.raises(ValueError):
        zero_pad([])


def test_zero_pad_different_dimensions():
    """Test zero padding with different stacking dimensions."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1, 2])
    x2 = torch.tensor([3, 4, 5])
    
    # Test dim=0 (default)
    result_dim0 = zero_pad([x1, x2], dim=0)
    assert result_dim0.shape == (2, 3)
    
    # Test dim=1 (should give same result for this case)
    result_dim1 = zero_pad([x1, x2], dim=1)
    assert result_dim1.shape == (2, 3)


def test_zero_pad_preserve_dtype():
    """Test that zero padding preserves data types."""
    from scitex.dsp.utils import zero_pad
    
    # Test different dtypes
    dtypes = [torch.float32, torch.float64, torch.int32, torch.int64]
    
    for dtype in dtypes:
        x1 = torch.tensor([1, 2], dtype=dtype)
        x2 = torch.tensor([3, 4, 5], dtype=dtype)
        
        result = zero_pad([x1, x2])
        assert result.dtype == dtype


def test_zero_pad_preserve_device():
    """Test that zero padding preserves device."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1, 2])
    x2 = torch.tensor([3, 4, 5])
    
    result = zero_pad([x1, x2])
    assert result.device == x1.device
    
    # Test CUDA if available
    if torch.cuda.is_available():
        x1_cuda = x1.cuda()
        x2_cuda = x2.cuda()
        result_cuda = zero_pad([x1_cuda, x2_cuda])
        assert result_cuda.device == x1_cuda.device


def test_zero_pad_large_size_difference():
    """Test zero padding with large size differences."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1])              # length 1
    x2 = torch.tensor(list(range(100))) # length 100
    
    result = zero_pad([x1, x2])
    
    assert result.shape == (2, 100)
    # x1 should be heavily padded
    assert result[0, 49] == 1  # Should be in the middle
    assert torch.sum(result[0] == 0) == 99  # 99 zeros
    # x2 should be unchanged
    assert torch.equal(result[1], x2)


def test_zero_pad_real_signal_example():
    """Test zero padding with realistic signal processing example."""
    from scitex.dsp.utils import zero_pad
    
    # Simulate different length EEG trials
    fs = 250  # Hz
    trial1 = torch.sin(2 * np.pi * 10 * torch.linspace(0, 1, fs))      # 1 second
    trial2 = torch.sin(2 * np.pi * 10 * torch.linspace(0, 1.5, int(fs * 1.5)))  # 1.5 seconds
    trial3 = torch.sin(2 * np.pi * 10 * torch.linspace(0, 2, fs * 2))  # 2 seconds
    
    trials = [trial1, trial2, trial3]
    result = zero_pad(trials)
    
    # Should be padded to longest trial (2 seconds = 500 samples)
    assert result.shape == (3, 500)
    
    # Check that original signals are preserved (approximately)
    # Due to padding, signals should be centered
    for i, trial in enumerate(trials):
        # Find where the non-zero (non-padded) values are
        non_zero_mask = torch.abs(result[i]) > 1e-6
        non_zero_indices = torch.where(non_zero_mask)[0]
        start_idx = non_zero_indices[0]
        end_idx = non_zero_indices[-1] + 1
        
        # Extract the non-padded part
        extracted = result[i, start_idx:end_idx]
        
        # Should match original (with some tolerance for floating point)
        assert extracted.shape == trial.shape
        assert torch.allclose(extracted, trial, atol=1e-6)


def test_zero_pad_gradient_flow():
    """Test that gradients flow through zero padding."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1.0, 2.0], requires_grad=True)
    x2 = torch.tensor([3.0, 4.0, 5.0], requires_grad=True)
    
    result = zero_pad([x1, x2])
    loss = result.sum()
    loss.backward()
    
    # Both input tensors should have gradients
    assert x1.grad is not None
    assert x2.grad is not None
    assert torch.equal(x1.grad, torch.ones_like(x1))
    assert torch.equal(x2.grad, torch.ones_like(x2))


def test_zero_pad_empty_tensors():
    """Test zero padding with empty tensors."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.empty(0)
    x2 = torch.tensor([1, 2, 3])
    
    result = zero_pad([x1, x2])
    
    # Should be padded to length 3
    assert result.shape == (2, 3)
    # First row should be all zeros
    assert torch.equal(result[0], torch.zeros(3))
    # Second row should be original
    assert torch.equal(result[1], x2)


def test_zero_pad_consistency():
    """Test that zero padding is consistent across calls."""
    from scitex.dsp.utils import zero_pad
    
    x1 = torch.tensor([1, 2])
    x2 = torch.tensor([3, 4, 5])
    
    result1 = zero_pad([x1, x2])
    result2 = zero_pad([x1, x2])
    
    assert torch.equal(result1, result2)


def test_zero_pad_different_numeric_types():
    """Test zero padding with different numeric types."""
    from scitex.dsp.utils import zero_pad
    
    # Test with integers
    x1 = [1, 2]
    x2 = [3, 4, 5]
    result_int = zero_pad([x1, x2])
    assert result_int.dtype in [torch.int64, torch.long]  # Default int type
    
    # Test with floats
    x1 = [1.0, 2.0]
    x2 = [3.0, 4.0, 5.0]
    result_float = zero_pad([x1, x2])
    assert result_float.dtype in [torch.float32, torch.float64]  # Default float type


def test_zero_pad_edge_cases():
    """Test zero padding edge cases."""
    from scitex.dsp.utils import zero_pad
    
    # Test with single element tensors
    x1 = torch.tensor([42])
    x2 = torch.tensor([99])
    result = zero_pad([x1, x2])
    
    assert result.shape == (2, 1)
    assert torch.equal(result, torch.tensor([[42], [99]]))


def test_zero_pad_memory_efficiency():
    """Test zero padding memory efficiency."""
    from scitex.dsp.utils import zero_pad
    
    # Create large tensors
    x1 = torch.randn(1000)
    x2 = torch.randn(1000)  # Same length, no padding needed
    
    result = zero_pad([x1, x2])
    
    # Should stack without unnecessary copying
    assert result.shape == (2, 1000)
    assert torch.equal(result[0], x1)
    assert torch.equal(result[1], x2)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/utils/_zero_pad.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-26 10:30:34 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/utils/_zero_pad.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dsp/utils/_zero_pad.py"
# 
# import numpy as np
# import torch
# import torch.nn.functional as F
# from ...decorators import torch_fn
# 
# 
# def _zero_pad_1d(x, target_length):
#     """Zero pad a 1D tensor to target length."""
#     if not isinstance(x, torch.Tensor):
#         x = torch.tensor(x)
#     padding_needed = target_length - len(x)
#     padding_left = padding_needed // 2
#     padding_right = padding_needed - padding_left
#     return F.pad(x, (padding_left, padding_right), "constant", 0)
# 
# 
# def zero_pad(xs, dim=0):
#     """Zero pad a list of arrays to the same length.
# 
#     Args:
#         xs: List of tensors or arrays
#         dim: Dimension to stack along
# 
#     Returns:
#         Stacked tensor with zero padding
#     """
#     # Convert to tensors if needed
#     tensors = []
#     for x in xs:
#         if isinstance(x, np.ndarray):
#             tensors.append(torch.tensor(x))
#         elif isinstance(x, torch.Tensor):
#             tensors.append(x)
#         else:
#             tensors.append(torch.tensor(x))
# 
#     max_len = max([len(x) for x in tensors])
#     return torch.stack([_zero_pad_1d(x, max_len) for x in tensors], dim=dim)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/utils/_zero_pad.py
# --------------------------------------------------------------------------------
