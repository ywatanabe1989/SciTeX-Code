#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:28:00 (ywatanabe)"
# File: ./tests/scitex/torch/test__apply_to.py

"""
Functionality:
    * Tests apply_to function for applying functions along tensor dimensions
    * Validates dimension permutation and reshaping logic
    * Tests function application to tensor slices
Input:
    * PyTorch tensors and functions
Output:
    * Test results
Prerequisites:
    * pytest, torch
"""

import pytest
import torch
import numpy as np


class TestApplyTo:
    """Test cases for apply_to function."""

    def setup_method(self):
        """Setup test fixtures."""
        # Skip tests if torch not available
        pytest.importorskip("torch")
        from scitex.torch import apply_to
        self.apply_to = apply_to

    def test_apply_sum_to_last_dimension(self):
        """Test applying sum function to last dimension."""
        x = torch.randn(2, 3, 4)
        result = self.apply_to(torch.sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        
        # Check that sum was applied correctly
        expected = torch.stack([torch.sum(x[i, j, :]) for i in range(2) for j in range(3)]).reshape(2, 3, 1)
        torch.testing.assert_close(result, expected)

    def test_apply_sum_to_middle_dimension(self):
        """Test applying sum function to middle dimension."""
        x = torch.randn(2, 3, 4)
        result = self.apply_to(torch.sum, x, 1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 1, 4)
        
        # Check that sum was applied correctly
        expected = torch.stack([torch.sum(x[i, :, j]) for i in range(2) for j in range(4)]).reshape(2, 1, 4)
        torch.testing.assert_close(result, expected)

    def test_apply_mean_function(self):
        """Test applying mean function."""
        x = torch.randn(2, 3, 4)
        result = self.apply_to(torch.mean, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        
        # Check that mean was applied correctly
        expected = torch.stack([torch.mean(x[i, j, :]) for i in range(2) for j in range(3)]).reshape(2, 3, 1)
        torch.testing.assert_close(result, expected)

    def test_apply_to_1d_tensor(self):
        """Test applying function to 1D tensor."""
        x = torch.randn(5)
        result = self.apply_to(torch.sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (1,)
        
        # Check that sum was applied correctly
        expected = torch.sum(x).unsqueeze(0)
        torch.testing.assert_close(result, expected)

    def test_apply_to_2d_tensor(self):
        """Test applying function to 2D tensor."""
        x = torch.randn(3, 4)
        result = self.apply_to(torch.sum, x, 0)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (1, 4)
        
        # Check that sum was applied correctly
        expected = torch.stack([torch.sum(x[:, j]) for j in range(4)]).reshape(1, 4)
        torch.testing.assert_close(result, expected)

    def test_apply_to_4d_tensor(self):
        """Test applying function to 4D tensor."""
        x = torch.randn(2, 3, 4, 5)
        result = self.apply_to(torch.sum, x, 2)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1, 5)
        assert torch.is_tensor(result)

    def test_dimension_permutation_logic(self):
        """Test that dimension permutation works correctly."""
        x = torch.randn(2, 3, 4)
        
        # Apply to dimension 0
        result_dim0 = self.apply_to(torch.sum, x, 0)
        assert result_dim0.shape == (1, 3, 4)
        
        # Apply to dimension 1
        result_dim1 = self.apply_to(torch.sum, x, 1)
        assert result_dim1.shape == (2, 1, 4)
        
        # Apply to dimension -1 (last)
        result_dim_last = self.apply_to(torch.sum, x, -1)
        assert result_dim_last.shape == (2, 3, 1)

    def test_custom_function(self):
        """Test with custom function."""
        def custom_sum(tensor):
            return torch.sum(tensor) * 2
        
        x = torch.randn(2, 3, 4)
        result = self.apply_to(custom_sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        
        # Check that custom function was applied correctly
        expected = torch.stack([custom_sum(x[i, j, :]) for i in range(2) for j in range(3)]).reshape(2, 3, 1)
        torch.testing.assert_close(result, expected)

    def test_lambda_function(self):
        """Test with lambda function."""
        x = torch.randn(2, 3, 4)
        result = self.apply_to(lambda t: torch.sum(t), x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        assert torch.is_tensor(result)

    def test_max_function(self):
        """Test with max function that returns values and indices."""
        x = torch.randn(2, 3, 4)
        # Use torch.max directly which returns a scalar tensor for 1D input
        result = self.apply_to(torch.max, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        assert torch.is_tensor(result)

    def test_different_dtypes(self):
        """Test with different tensor dtypes."""
        # Float tensor
        x_float = torch.randn(2, 3, 4, dtype=torch.float32)
        result_float = self.apply_to(torch.sum, x_float, -1)
        assert result_float.dtype == torch.float32
        
        # Double tensor
        x_double = torch.randn(2, 3, 4, dtype=torch.float64)
        result_double = self.apply_to(torch.sum, x_double, -1)
        assert result_double.dtype == torch.float64

    def test_with_requires_grad(self):
        """Test with tensors that require gradients."""
        x = torch.randn(2, 3, 4, requires_grad=True)
        result = self.apply_to(torch.sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        assert result.requires_grad == x.requires_grad

    def test_empty_tensor_handling(self):
        """Test with edge case of very small tensors."""
        x = torch.randn(1, 1, 1)
        result = self.apply_to(torch.sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (1, 1, 1)
        assert torch.is_tensor(result)

    def test_specific_example_from_docstring(self):
        """Test the specific example given in the function docstring."""
        x = torch.randn(2, 3, 4)
        result = self.apply_to(torch.sum, x, 1)
        
        # From docstring: apply_to(sum, x, 1).shape should be (2, 1, 4)
        assert result.shape == (2, 1, 4)
        assert torch.is_tensor(result)

    def test_numerical_correctness(self):
        """Test numerical correctness with known input."""
        # Create a simple tensor where we can verify the computation
        x = torch.ones(2, 2, 2)  # All ones
        result = self.apply_to(torch.sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 2, 1)
        # Each sum should equal 2.0 (sum of 2 ones)
        expected = torch.full((2, 2, 1), 2.0)
        torch.testing.assert_close(result, expected)

    def test_zero_tensor(self):
        """Test with tensor of zeros."""
        x = torch.zeros(2, 3, 4)
        result = self.apply_to(torch.sum, x, -1)
        
        # Should reduce the applied dimension to size 1
        assert result.shape == (2, 3, 1)
        # All sums should be 0
        expected = torch.zeros(2, 3, 1)
        torch.testing.assert_close(result, expected)

    def test_device_consistency(self):
        """Test that result stays on same device as input."""
        if torch.cuda.is_available():
            x_cpu = torch.randn(2, 3, 4)
            result_cpu = self.apply_to(torch.sum, x_cpu, -1)
            assert result_cpu.device == x_cpu.device
            
            x_cuda = torch.randn(2, 3, 4, device='cuda')
            result_cuda = self.apply_to(torch.sum, x_cuda, -1)
            assert result_cuda.device == x_cuda.device
        else:
            # Test CPU only
            x = torch.randn(2, 3, 4)
            result = self.apply_to(torch.sum, x, -1)
            assert result.device == x.device

    def test_invalid_dimension(self):
        """Test with invalid dimension indices."""
        x = torch.randn(2, 3, 4)
        
        # These should either work or raise appropriate errors
        try:
            # Dimension beyond tensor dimensions
            result = self.apply_to(torch.sum, x, 10)
            assert torch.is_tensor(result)
        except (IndexError, RuntimeError):
            # This is acceptable behavior for invalid dimensions
            pass

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/torch/_apply_to.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-31 08:11:45 (ywatanabe)"
# 
# import torch
# 
# 
# def apply_to(fn, x, dim):
#     """
#     Example:
#     x = torch.randn(2, 3, 4)
#     fn = sum
#     apply_to(fn, x, 1).shape # (2, 1, 4)
#     """
#     if dim != -1:
#         dims = list(range(x.dim()))
#         dims[-1], dims[dim] = dims[dim], dims[-1]
#         x = x.permute(*dims)
# 
#     # Flatten the tensor along the time dimension
#     shape = x.shape
#     x = x.reshape(-1, shape[-1])
# 
#     # Apply the function to each slice along the time dimension
#     applied = torch.stack([fn(x_i) for x_i in torch.unbind(x, dim=0)], dim=0)
# 
#     # Reshape the tensor to its original shape (with the time dimension at the end)
#     applied = applied.reshape(*shape[:-1], -1)
# 
#     # Permute back to the original dimension order if necessary
#     if dim != -1:
#         applied = applied.permute(*dims)
# 
#     return applied

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/torch/_apply_to.py
# --------------------------------------------------------------------------------
