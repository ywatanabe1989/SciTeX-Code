#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:30:00 (ywatanabe)"
# File: ./tests/scitex/torch/test__nan_funcs.py

"""
Functionality:
    * Tests NaN-handling functions for PyTorch tensors
    * Validates numerical correctness against PyTorch reference implementations
    * Tests edge cases and different tensor shapes/dtypes
Input:
    * PyTorch tensors with NaN values
Output:
    * Test results
Prerequisites:
    * pytest, torch
"""

import pytest
import torch
import numpy as np


class TestNanFunctions:
    """Test cases for NaN-handling functions."""

    def setup_method(self):
        """Setup test fixtures."""
        # Skip tests if torch not available
        pytest.importorskip("torch")
        
        # Import all nan functions
        from scitex.torch import (
            nanmax, nanmin, nanvar, nanstd, nanprod, 
            nancumprod, nancumsum, nanargmin, nanargmax
        )
        
        self.nanmax = nanmax
        self.nanmin = nanmin
        self.nanvar = nanvar
        self.nanstd = nanstd
        self.nanprod = nanprod
        self.nancumprod = nancumprod
        self.nancumsum = nancumsum
        self.nanargmin = nanargmin
        self.nanargmax = nanargmax

    def test_nanmax_basic(self):
        """Test nanmax with basic tensor."""
        # Tensor with NaN values
        x = torch.tensor([1.0, float('nan'), 3.0, 2.0])
        result = self.nanmax(x)
        
        assert result == 3.0
        assert torch.is_tensor(result)

    def test_nanmax_with_dim(self):
        """Test nanmax with specified dimension."""
        x = torch.tensor([[1.0, float('nan')], [3.0, 2.0]])
        result = self.nanmax(x, dim=0)
        
        assert result.values.shape == (2,)
        assert result.values[0] == 3.0  # max of [1.0, 3.0]
        assert result.values[1] == 2.0  # max of [nan, 2.0]

    def test_nanmax_keepdim(self):
        """Test nanmax with keepdim=True."""
        x = torch.tensor([[1.0, float('nan')], [3.0, 2.0]])
        result = self.nanmax(x, dim=0, keepdim=True)
        
        assert result.values.shape == (1, 2)

    def test_nanmin_basic(self):
        """Test nanmin with basic tensor."""
        x = torch.tensor([1.0, float('nan'), 3.0, 2.0])
        result = self.nanmin(x)
        
        assert result.item() == 1.0

    def test_nanmin_with_dim(self):
        """Test nanmin with specified dimension."""
        x = torch.tensor([[1.0, float('nan')], [3.0, 2.0]])
        result = self.nanmin(x, dim=1)
        
        assert result.values.shape == (2,)
        assert result.values[0] == 1.0  # min of [1.0, nan]
        assert result.values[1] == 2.0  # min of [3.0, 2.0]

    def test_nanvar_basic(self):
        """Test nanvar computation."""
        x = torch.tensor([1.0, 2.0, float('nan'), 4.0])
        result = self.nanvar(x)
        
        # Should compute variance of [1.0, 2.0, 4.0]
        assert torch.is_tensor(result)
        # Expected variance of [1, 2, 4] with mean 7/3
        expected_vals = torch.tensor([1.0, 2.0, 4.0])
        expected_var = torch.var(expected_vals, unbiased=False)
        assert torch.allclose(result, expected_var, atol=1e-5)

    def test_nanvar_with_dim(self):
        """Test nanvar with dimension."""
        x = torch.tensor([[1.0, float('nan')], [2.0, 3.0]])
        result = self.nanvar(x, dim=0)
        
        assert result.shape == (2,)
        assert torch.is_tensor(result)

    def test_nanstd_basic(self):
        """Test nanstd computation."""
        x = torch.tensor([1.0, 2.0, float('nan'), 4.0])
        result = self.nanstd(x)
        
        # Should be sqrt of nanvar
        var_result = self.nanvar(x)
        expected = torch.sqrt(var_result)
        assert torch.allclose(result, expected, atol=1e-5)

    def test_nanstd_with_dim_keepdim(self):
        """Test nanstd with dimension and keepdim."""
        x = torch.tensor([[1.0, float('nan')], [2.0, 3.0]])
        result = self.nanstd(x, dim=1, keepdim=True)
        
        assert result.shape == (2, 1)

    def test_nanprod_basic(self):
        """Test nanprod computation."""
        x = torch.tensor([2.0, float('nan'), 3.0, 4.0])
        result = self.nanprod(x)
        
        # Should compute product of [2.0, 1.0, 3.0, 4.0] = 24.0
        # (NaN replaced with 1.0)
        assert result == 24.0

    def test_nanprod_with_dim(self):
        """Test nanprod with dimension."""
        x = torch.tensor([[2.0, float('nan')], [3.0, 4.0]])
        result = self.nanprod(x, dim=0)
        
        assert result.shape == (2,)
        assert result[0] == 6.0  # 2.0 * 3.0
        assert result[1] == 4.0  # nan->1.0 * 4.0

    def test_nancumprod_basic(self):
        """Test nancumprod computation."""
        x = torch.tensor([2.0, float('nan'), 3.0])
        result = self.nancumprod(x, dim=0)
        
        # Should be [2.0, 2.0, 6.0] (nan treated as 1.0)
        assert result.shape == x.shape
        assert result[0] == 2.0
        assert result[1] == 2.0  # 2.0 * 1.0
        assert result[2] == 6.0  # 2.0 * 1.0 * 3.0

    def test_nancumsum_basic(self):
        """Test nancumsum computation."""
        x = torch.tensor([1.0, float('nan'), 3.0])
        result = self.nancumsum(x, dim=0)
        
        # Should be [1.0, 1.0, 4.0] (nan treated as 0.0)
        assert result.shape == x.shape
        assert result[0] == 1.0
        assert result[1] == 1.0  # 1.0 + 0.0
        assert result[2] == 4.0  # 1.0 + 0.0 + 3.0

    def test_nancumsum_with_dim_keepdim(self):
        """Test nancumsum with dimension and keepdim."""
        x = torch.tensor([[1.0, float('nan')], [2.0, 3.0]])
        result = self.nancumsum(x, dim=1, keepdim=True)
        
        assert result.shape == (2, 2)

    def test_nanargmin_basic(self):
        """Test nanargmin computation."""
        x = torch.tensor([3.0, float('nan'), 1.0, 2.0])
        result = self.nanargmin(x)
        
        # Should find index of minimum non-NaN value (1.0 at index 2)
        assert result == 2

    def test_nanargmin_with_dim(self):
        """Test nanargmin with dimension."""
        x = torch.tensor([[3.0, float('nan')], [1.0, 2.0]])
        result = self.nanargmin(x, dim=0)
        
        assert result.shape == (2,)
        assert result[0] == 1  # min of [3.0, 1.0] is at index 1
        assert result[1] == 1  # min of [nan, 2.0] is at index 1

    def test_nanargmax_basic(self):
        """Test nanargmax computation."""
        x = torch.tensor([3.0, float('nan'), 1.0, 5.0])
        result = self.nanargmax(x)
        
        # Should find index of maximum non-NaN value (5.0 at index 3)
        assert result == 3

    def test_nanargmax_with_dim_keepdim(self):
        """Test nanargmax with dimension and keepdim."""
        x = torch.tensor([[3.0, float('nan')], [1.0, 2.0]])
        result = self.nanargmax(x, dim=1, keepdim=True)
        
        assert result.shape == (2, 1)

    def test_all_nan_tensor(self):
        """Test functions with all-NaN tensor."""
        x = torch.tensor([float('nan'), float('nan')])
        
        # These should handle all-NaN gracefully
        max_result = self.nanmax(x)
        min_result = self.nanmin(x)
        var_result = self.nanvar(x)
        std_result = self.nanstd(x)
        
        # Results might be NaN or extreme values
        assert torch.is_tensor(max_result)
        assert torch.is_tensor(min_result)
        assert torch.is_tensor(var_result)
        assert torch.is_tensor(std_result)

    def test_no_nan_tensor(self):
        """Test functions with no NaN values."""
        x = torch.tensor([1.0, 2.0, 3.0, 4.0])
        
        # Should behave like regular torch functions
        max_result = self.nanmax(x)
        min_result = self.nanmin(x)
        prod_result = self.nanprod(x)
        
        assert max_result.item() == 4.0
        assert min_result.item() == 1.0
        assert prod_result.item() == 24.0

    def test_different_dtypes(self):
        """Test with different tensor dtypes."""
        for dtype in [torch.float32, torch.float64]:
            x = torch.tensor([1.0, float('nan'), 3.0], dtype=dtype)
            
            max_result = self.nanmax(x)
            min_result = self.nanmin(x)
            var_result = self.nanvar(x)
            
            assert max_result.dtype == dtype
            assert min_result.dtype == dtype
            assert var_result.dtype == dtype

    def test_multidimensional_tensors(self):
        """Test with multidimensional tensors."""
        # 3D tensor
        x = torch.randn(2, 3, 4)
        x[0, 1, :] = float('nan')  # Make some values NaN
        
        # Test different dimensions
        for dim in [0, 1, 2, None]:
            max_result = self.nanmax(x, dim=dim)
            min_result = self.nanmin(x, dim=dim)
            
            if dim is not None:
                assert torch.is_tensor(max_result.values)
                assert torch.is_tensor(min_result.values)
            else:
                assert torch.is_tensor(max_result)
                assert torch.is_tensor(min_result)

    def test_cumulative_functions_multidim(self):
        """Test cumulative functions with multidimensional tensors."""
        x = torch.tensor([[1.0, float('nan')], [2.0, 3.0]])
        
        cumprod_result = self.nancumprod(x, dim=0)
        cumsum_result = self.nancumsum(x, dim=1)
        
        assert cumprod_result.shape == x.shape
        assert cumsum_result.shape == x.shape

    def test_edge_case_single_element(self):
        """Test with single element tensors."""
        x_val = torch.tensor([5.0])
        x_nan = torch.tensor([float('nan')])
        
        # Valid single element
        assert self.nanmax(x_val).item() == 5.0
        assert self.nanmin(x_val).item() == 5.0
        assert self.nanprod(x_val).item() == 5.0
        
        # NaN single element
        max_nan = self.nanmax(x_nan)
        min_nan = self.nanmin(x_nan)
        prod_nan = self.nanprod(x_nan)
        
        assert torch.is_tensor(max_nan)
        assert torch.is_tensor(min_nan)
        assert torch.is_tensor(prod_nan)

    def test_empty_tensor_handling(self):
        """Test with empty tensors."""
        x = torch.tensor([])
        
        try:
            max_result = self.nanmax(x)
            min_result = self.nanmin(x)
            # Should either work or raise appropriate error
            assert torch.is_tensor(max_result)
            assert torch.is_tensor(min_result)
        except (RuntimeError, ValueError):
            # Empty tensor operations might raise errors
            pass

    def test_large_tensor_performance(self):
        """Test with larger tensors for performance validation."""
        x = torch.randn(100, 100)
        # Randomly set some values to NaN
        nan_mask = torch.rand(100, 100) < 0.1
        x[nan_mask] = float('nan')
        
        # Should complete without issues
        max_result = self.nanmax(x)
        var_result = self.nanvar(x)
        cumprod_result = self.nancumprod(x, dim=0)
        
        assert torch.is_tensor(max_result)
        assert torch.is_tensor(var_result)
        assert cumprod_result.shape == x.shape

    def test_grad_compatibility(self):
        """Test compatibility with gradient computation."""
        x = torch.tensor([1.0, float('nan'), 3.0], requires_grad=True)
        
        # Test that functions work with grad-enabled tensors
        var_result = self.nanvar(x)
        std_result = self.nanstd(x)
        
        assert torch.is_tensor(var_result)
        assert torch.is_tensor(std_result)
        # Gradient tracking should be preserved where possible
        assert var_result.requires_grad
        assert std_result.requires_grad

    def test_device_consistency(self):
        """Test that operations preserve device placement."""
        if torch.cuda.is_available():
            x_cuda = torch.tensor([1.0, float('nan'), 3.0], device='cuda')
            result_cuda = self.nanvar(x_cuda)
            assert result_cuda.device.type == 'cuda'
        
        # CPU test
        x_cpu = torch.tensor([1.0, float('nan'), 3.0])
        result_cpu = self.nanvar(x_cpu)
        assert result_cpu.device.type == 'cpu'

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/torch/_nan_funcs.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-28 19:38:19 (ywatanabe)"
# # /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/torch/_nan_funcs.py
# 
# import torch as _torch
# 
# 
# # https://github.com/pytorch/pytorch/issues/61474
# def nanmax(tensor, dim=None, keepdim=False):
#     min_value = _torch.finfo(tensor.dtype).min
#     if dim is None:
#         output = tensor.nan_to_num(min_value).max()
#     else:
#         output = tensor.nan_to_num(min_value).max(dim=dim, keepdim=keepdim)
#     return output
# 
# 
# def nanmin(tensor, dim=None, keepdim=False):
#     max_value = _torch.finfo(tensor.dtype).max
#     if dim is None:
#         output = tensor.nan_to_num(max_value).min()
#     else:
#         output = tensor.nan_to_num(max_value).min(dim=dim, keepdim=keepdim)
#     return output
# 
# 
# def nanvar(tensor, dim=None, keepdim=False):
#     tensor_mean = tensor.nanmean(dim=dim, keepdim=True)
#     output = (tensor - tensor_mean).square().nanmean(dim=dim, keepdim=keepdim)
#     return output
# 
# 
# def nanstd(tensor, dim=None, keepdim=False):
#     output = nanvar(tensor, dim=dim, keepdim=keepdim)
#     output = output.sqrt()
#     return output
# 
# 
# def nanprod(tensor, dim=None, keepdim=False):
#     if dim is None:
#         output = tensor.nan_to_num(1).prod()
#     else:
#         output = tensor.nan_to_num(1).prod(dim=dim, keepdim=keepdim)
#     return output
# 
# 
# def nancumprod(tensor, dim=None, keepdim=False):
#     if dim is None:
#         dim = 0  # Default to first dimension for cumulative operations
#     output = tensor.nan_to_num(1).cumprod(dim=dim)
#     return output
# 
# 
# def nancumsum(tensor, dim=None, keepdim=False):
#     if dim is None:
#         dim = 0  # Default to first dimension for cumulative operations
#     output = tensor.nan_to_num(0).cumsum(dim=dim)
#     return output
# 
# 
# def nanargmin(tensor, dim=None, keepdim=False):
#     max_value = _torch.finfo(tensor.dtype).max
#     if dim is None:
#         output = tensor.nan_to_num(max_value).argmin()
#     else:
#         output = tensor.nan_to_num(max_value).argmin(dim=dim, keepdim=keepdim)
#     return output
# 
# 
# def nanargmax(tensor, dim=None, keepdim=False):
#     min_value = _torch.finfo(tensor.dtype).min
#     if dim is None:
#         output = tensor.nan_to_num(min_value).argmax()
#     else:
#         output = tensor.nan_to_num(min_value).argmax(dim=dim, keepdim=keepdim)
#     return output

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/torch/_nan_funcs.py
# --------------------------------------------------------------------------------
