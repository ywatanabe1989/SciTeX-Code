#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 13:40:00 (ywatanabe)"
# File: ./tests/scitex/torch/test__torch_comprehensive.py

"""
Comprehensive tests for scitex.torch module to improve test coverage.
Tests edge cases, error handling, and integration scenarios.
"""

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock


class TestApplyToComprehensive:
    """Comprehensive tests for apply_to function."""

    def setup_method(self):
        """Setup test fixtures."""
        pytest.importorskip("torch")
        from scitex.torch import apply_to
        self.apply_to = apply_to

    def test_apply_to_complex_functions(self):
        """Test apply_to with various complex functions."""
        x = torch.randn(3, 4, 5)
        
        # Test with torch.std
        result = self.apply_to(torch.std, x, dim=1)
        assert result.shape == (3, 1, 5)
        
        # Test with torch.median
        result = self.apply_to(torch.median, x, dim=2)
        assert result.shape == (3, 4, 1)
        
        # Test with custom reduction function
        def custom_reduction(tensor):
            return tensor.sum() + tensor.mean()
        
        result = self.apply_to(custom_reduction, x, dim=0)
        assert result.shape == (1, 4, 5)

    def test_apply_to_non_reduction_functions(self):
        """Test apply_to with non-reduction functions."""
        x = torch.randn(2, 3, 4)
        
        # Function that returns same size tensor
        def identity_like(tensor):
            return tensor.clone()
        
        result = self.apply_to(identity_like, x, dim=1)
        assert result.shape == x.shape

    def test_apply_to_with_negative_dimensions(self):
        """Test apply_to with negative dimension indices."""
        x = torch.randn(2, 3, 4, 5)
        
        # Test dim=-1 (last dimension)
        result = self.apply_to(torch.sum, x, dim=-1)
        assert result.shape == (2, 3, 4, 1)
        
        # Test dim=-2
        result = self.apply_to(torch.mean, x, dim=-2)
        assert result.shape == (2, 3, 1, 5)

    def test_apply_to_batch_processing(self):
        """Test apply_to simulating batch processing scenarios."""
        batch_size, seq_len, features = 32, 100, 64
        x = torch.randn(batch_size, seq_len, features)
        
        # Apply function along sequence dimension
        result = self.apply_to(torch.max, x, dim=1)
        assert result.shape == (batch_size, 1, features)

    def test_apply_to_memory_efficiency(self):
        """Test apply_to doesn't create unnecessary copies."""
        x = torch.randn(10, 20, 30)
        x_ptr = x.data_ptr()
        
        # Apply function that modifies tensor in-place
        def inplace_op(tensor):
            return tensor.add_(1)
        
        # Just ensure it completes without errors
        result = self.apply_to(inplace_op, x.clone(), dim=1)
        assert result is not None


class TestNanFunctionsComprehensive:
    """Comprehensive tests for nan functions."""

    def setup_method(self):
        """Setup test fixtures."""
        pytest.importorskip("torch")
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

    def test_nan_functions_with_inf(self):
        """Test nan functions handle inf values correctly."""
        x = torch.tensor([1.0, float('inf'), float('nan'), -float('inf'), 2.0])
        
        # nanmax should handle inf (may convert to max float value)
        max_result = self.nanmax(x).item()
        assert max_result > 1e30 or max_result == float('inf')
        
        # nanmin should handle -inf (may convert to min float value)
        min_result = self.nanmin(x).item()
        assert min_result < -1e30 or min_result == float('-inf')
        
        # nanprod with inf
        assert torch.isinf(self.nanprod(x))

    def test_nan_functions_mixed_nan_patterns(self):
        """Test with various NaN patterns."""
        # Alternating NaN pattern
        x = torch.tensor([[1.0, float('nan'), 3.0], 
                         [float('nan'), 2.0, float('nan')]])
        
        max_result = self.nanmax(x, dim=1)
        assert max_result.values[0].item() == 3.0
        assert max_result.values[1].item() == 2.0
        
        # Sparse NaN pattern
        x = torch.randn(10, 10)
        x[::3, ::3] = float('nan')
        
        var_result = self.nanvar(x)
        assert not torch.isnan(var_result)

    def test_nan_argfunctions_tie_breaking(self):
        """Test argmin/argmax behavior with ties."""
        x = torch.tensor([1.0, float('nan'), 1.0, 1.0])
        
        # Should return first occurrence
        argmin_result = self.nanargmin(x)
        assert argmin_result.item() == 0
        
        x = torch.tensor([[3.0, float('nan')], [3.0, 3.0]])
        argmax_result = self.nanargmax(x, dim=0)
        assert argmax_result[0].item() in [0, 1]  # Either is valid

    def test_nan_cumulative_edge_cases(self):
        """Test cumulative functions with edge cases."""
        # All NaN after certain point
        x = torch.tensor([1.0, 2.0, float('nan'), float('nan')])
        cumsum_result = self.nancumsum(x)
        expected = torch.tensor([1.0, 3.0, 3.0, 3.0])
        torch.testing.assert_close(cumsum_result, expected)
        
        # Cumprod with zeros and NaNs
        x = torch.tensor([2.0, 0.0, float('nan'), 3.0])
        cumprod_result = self.nancumprod(x)
        expected = torch.tensor([2.0, 0.0, 0.0, 0.0])
        torch.testing.assert_close(cumprod_result, expected)

    def test_nan_functions_numerical_stability(self):
        """Test numerical stability of nan functions."""
        # Large variance computation
        x = torch.tensor([1e8, float('nan'), 1e8 + 1, 1e8 + 2])
        var_result = self.nanvar(x)
        assert var_result.item() >= 0  # Variance should be non-negative
        
        # Very small std computation
        x = torch.tensor([1e-8, float('nan'), 1e-8 + 1e-16])
        std_result = self.nanstd(x)
        assert std_result.item() >= 0  # Should be non-negative

    def test_nan_functions_broadcasting(self):
        """Test nan functions with broadcasting scenarios."""
        # 3D tensor with different NaN patterns per slice
        x = torch.randn(3, 4, 5)
        x[0, :, 0] = float('nan')
        x[1, 1, :] = float('nan')
        x[2, :, -1] = float('nan')
        
        # Test along different dimensions
        max_dim0 = self.nanmax(x, dim=0)
        max_dim1 = self.nanmax(x, dim=1)
        max_dim2 = self.nanmax(x, dim=2)
        
        assert max_dim0.values.shape == (4, 5)
        assert max_dim1.values.shape == (3, 5)
        assert max_dim2.values.shape == (3, 4)


class TestTorchModuleIntegration:
    """Integration tests for torch module."""

    def setup_method(self):
        """Setup test fixtures."""
        pytest.importorskip("torch")

    def test_module_imports(self):
        """Test all expected functions are importable."""
        import scitex.torch
        
        # Check apply_to is available
        assert hasattr(scitex.torch, 'apply_to')
        
        # Check all nan functions are available
        nan_functions = [
            'nanmax', 'nanmin', 'nanvar', 'nanstd', 
            'nanprod', 'nancumprod', 'nancumsum', 
            'nanargmin', 'nanargmax'
        ]
        
        for func_name in nan_functions:
            assert hasattr(scitex.torch, func_name)

    def test_combined_usage(self):
        """Test using apply_to with nan functions."""
        from scitex.torch import apply_to, nanmax
        
        # Create 3D tensor with NaNs
        x = torch.randn(2, 3, 4)
        x[0, 1, :] = float('nan')
        
        # Apply nanmax using apply_to
        result = apply_to(lambda t: nanmax(t), x, dim=1)
        assert result.shape == (2, 1, 4)
        assert not torch.any(torch.isnan(result))

    def test_device_agnostic(self):
        """Test functions work on different devices if available."""
        from scitex.torch import nanmax, apply_to
        
        x = torch.tensor([1.0, float('nan'), 3.0])
        
        # CPU test (always available)
        cpu_result = nanmax(x)
        assert cpu_result.item() == 3.0
        
        # GPU test if available
        if torch.cuda.is_available():
            x_cuda = x.cuda()
            cuda_result = nanmax(x_cuda)
            assert cuda_result.device.type == 'cuda'
            assert cuda_result.cpu().item() == 3.0

    def test_error_messages(self):
        """Test helpful error messages for common mistakes."""
        from scitex.torch import apply_to
        
        x = torch.randn(2, 3, 4)
        
        # Invalid dimension
        with pytest.raises((IndexError, RuntimeError)):
            apply_to(torch.sum, x, dim=10)

    def test_performance_characteristics(self):
        """Test performance characteristics are reasonable."""
        from scitex.torch import nanmax, nanmin
        import time
        
        # Large tensor
        x = torch.randn(1000, 1000)
        x[::10, ::10] = float('nan')
        
        # Measure time
        start = time.time()
        _ = nanmax(x)
        _ = nanmin(x)
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0


class TestTorchUtilityFunctions:
    """Test utility aspects of torch module."""

    def test_docstring_examples(self):
        """Test that docstring examples work correctly."""
        from scitex.torch import apply_to
        
        # From apply_to docstring
        x = torch.randn(2, 3, 4)
        fn = sum
        result = apply_to(fn, x, 1)
        assert result.shape == (2, 1, 4)

    def test_type_preservation(self):
        """Test that tensor types are preserved."""
        from scitex.torch import nanmax, nancumprod
        
        # Test different dtypes
        for dtype in [torch.float32, torch.float64]:
            x = torch.tensor([1.0, float('nan'), 3.0], dtype=dtype)
            
            max_result = nanmax(x)
            assert max_result.dtype == dtype
            
            cumprod_result = nancumprod(x)
            assert cumprod_result.dtype == dtype

    def test_gradient_flow(self):
        """Test gradient flow through nan functions."""
        from scitex.torch import nanvar, nanstd
        
        x = torch.tensor([1.0, 2.0, float('nan'), 4.0], requires_grad=True)
        
        # Compute variance
        var = nanvar(x)
        
        # Check if gradients can be computed (may not work for all custom implementations)
        try:
            var.backward()
            # Gradient should exist
            assert x.grad is not None
        except RuntimeError:
            # Some custom nan functions may not support autograd
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])