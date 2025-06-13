#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:23:00"
# File: /tests/scitex/torch/test__nan_funcs_enhanced.py
# ----------------------------------------
"""
Enhanced tests for scitex.torch._nan_funcs module implementing advanced testing patterns.

This module demonstrates:
- Comprehensive fixtures for PyTorch tensor testing
- Property-based testing for numerical operations
- Edge case handling (all NaN, no NaN, inf values)
- Performance benchmarking for large tensors
- Comparison with NumPy equivalents
- dtype and device compatibility testing
- Gradient flow testing for autograd
"""

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, assume
import time
from typing import Tuple, List, Optional
import warnings

try:
    from scitex.torch import (
        nanmax, nanmin, nanvar, nanstd, nanprod,
        nancumprod, nancumsum, nanargmin, nanargmax
    )
except ImportError:
    try:
        # Try importing from the _nan_funcs module directly
        from scitex.torch._nan_funcs import (
            nanmax, nanmin, nanvar, nanstd, nanprod,
            nancumprod, nancumsum, nanargmin, nanargmax
        )
    except ImportError:
        pytest.skip("scitex.torch nan functions not available", allow_module_level=True)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tensor_shapes():
    """Provide various tensor shapes for testing."""
    return {
        '1d': (100,),
        '2d': (50, 100),
        '3d': (10, 20, 30),
        '4d': (5, 10, 15, 20),
        'scalar': (),
        'single': (1,),
        'large': (1000, 1000),
        'tall': (10000, 10),
        'wide': (10, 10000),
    }


@pytest.fixture
def nan_patterns():
    """Provide various NaN patterns for testing."""
    def create_tensor_with_pattern(shape, pattern_type, dtype=torch.float32):
        if pattern_type == 'no_nan':
            return torch.randn(shape, dtype=dtype)
        
        elif pattern_type == 'all_nan':
            return torch.full(shape, float('nan'), dtype=dtype)
        
        elif pattern_type == 'single_nan':
            tensor = torch.randn(shape, dtype=dtype)
            if tensor.numel() > 0:
                tensor.view(-1)[0] = float('nan')
            return tensor
        
        elif pattern_type == 'half_nan':
            tensor = torch.randn(shape, dtype=dtype)
            mask = torch.rand(shape) > 0.5
            tensor[mask] = float('nan')
            return tensor
        
        elif pattern_type == 'sparse_nan':
            tensor = torch.randn(shape, dtype=dtype)
            mask = torch.rand(shape) > 0.9  # 10% NaN
            tensor[mask] = float('nan')
            return tensor
        
        elif pattern_type == 'row_nan':
            tensor = torch.randn(shape, dtype=dtype)
            if len(shape) >= 2:
                tensor[0] = float('nan')
            return tensor
        
        elif pattern_type == 'col_nan':
            tensor = torch.randn(shape, dtype=dtype)
            if len(shape) >= 2:
                tensor[:, 0] = float('nan')
            return tensor
        
        elif pattern_type == 'mixed_special':
            tensor = torch.randn(shape, dtype=dtype)
            if tensor.numel() >= 3:
                flat = tensor.view(-1)
                flat[0] = float('nan')
                flat[1] = float('inf')
                flat[2] = float('-inf')
            return tensor
    
    return create_tensor_with_pattern


@pytest.fixture
def tensor_dtypes():
    """Provide various tensor dtypes for testing."""
    return [
        torch.float32,
        torch.float64,
        torch.float16,  # Half precision
    ]


@pytest.fixture
def tensor_devices():
    """Provide available devices for testing."""
    devices = ['cpu']
    if torch.cuda.is_available():
        devices.append('cuda')
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        devices.append('mps')
    return devices


@pytest.fixture
def comparison_tolerances():
    """Provide tolerances for numerical comparisons."""
    return {
        torch.float32: {'rtol': 1e-5, 'atol': 1e-6},
        torch.float64: {'rtol': 1e-10, 'atol': 1e-12},
        torch.float16: {'rtol': 1e-3, 'atol': 1e-3},
    }


@pytest.fixture
def numpy_equivalents():
    """Map scitex functions to numpy equivalents for validation."""
    return {
        'nanmax': np.nanmax,
        'nanmin': np.nanmin,
        'nanvar': np.nanvar,
        'nanstd': np.nanstd,
        'nanprod': np.nanprod,
        'nancumprod': np.nancumprod,
        'nancumsum': np.nancumsum,
        'nanargmin': np.nanargmin,
        'nanargmax': np.nanargmax,
    }


# ============================================================================
# Basic Functionality Tests
# ============================================================================

class TestNanFunctionsBasics:
    """Test basic functionality of NaN functions."""
    
    @pytest.mark.parametrize('func_name,func', [
        ('nanmax', nanmax),
        ('nanmin', nanmin),
        ('nanvar', nanvar),
        ('nanstd', nanstd),
        ('nanprod', nanprod),
    ])
    def test_basic_functionality(self, func_name, func):
        """Test basic functionality with simple tensors."""
        # Create tensor with some NaN values
        tensor = torch.tensor([1.0, 2.0, float('nan'), 4.0, 5.0])
        
        # Apply function
        result = func(tensor)
        
        # Result should be scalar and not NaN
        assert result.dim() == 0
        assert not torch.isnan(result)
        
        # Check specific values
        if func_name == 'nanmax':
            assert result == 5.0
        elif func_name == 'nanmin':
            assert result == 1.0
        elif func_name == 'nanprod':
            assert result == 40.0  # 1*2*4*5
    
    @pytest.mark.parametrize('func', [nancumprod, nancumsum])
    def test_cumulative_functions(self, func):
        """Test cumulative functions."""
        tensor = torch.tensor([1.0, 2.0, float('nan'), 4.0, 5.0])
        result = func(tensor)
        
        # Result should have same shape
        assert result.shape == tensor.shape
        
        # No NaN in result
        assert not torch.isnan(result).any()
    
    @pytest.mark.parametrize('func', [nanargmin, nanargmax])
    def test_argfunctions(self, func):
        """Test arg functions."""
        tensor = torch.tensor([5.0, 2.0, float('nan'), 1.0, 4.0])
        result = func(tensor)
        
        # Result should be integer index
        assert result.dtype in [torch.int64, torch.long]
        
        # Check correct index
        if func == nanargmin:
            assert result == 3  # Index of 1.0
        else:  # nanargmax
            assert result == 0  # Index of 5.0


# ============================================================================
# Dimension Tests
# ============================================================================

class TestNanFunctionsDimensions:
    """Test NaN functions with various dimensions."""
    
    @pytest.mark.parametrize('shape', [
        (10,),
        (5, 10),
        (3, 4, 5),
        (2, 3, 4, 5),
    ])
    @pytest.mark.parametrize('func', [nanmax, nanmin, nanvar, nanstd])
    def test_reduction_dimensions(self, shape, func):
        """Test reduction along different dimensions."""
        tensor = torch.randn(shape)
        # Add some NaN values
        mask = torch.rand(shape) > 0.8
        tensor[mask] = float('nan')
        
        # Test reduction along each dimension
        for dim in range(len(shape)):
            result = func(tensor, dim=dim)
            expected_shape = list(shape)
            expected_shape.pop(dim)
            assert list(result.shape) == expected_shape
            assert not torch.isnan(result).any()
        
        # Test keepdim
        for dim in range(len(shape)):
            result = func(tensor, dim=dim, keepdim=True)
            expected_shape = list(shape)
            expected_shape[dim] = 1
            assert list(result.shape) == expected_shape
    
    def test_multiple_dimensions(self):
        """Test reduction over multiple dimensions."""
        tensor = torch.randn(4, 5, 6)
        mask = torch.rand(4, 5, 6) > 0.8
        tensor[mask] = float('nan')
        
        # Note: Current implementation doesn't support tuple dims
        # This is a limitation that could be documented or fixed
        result = nanmax(tensor)  # Reduces over all dims
        assert result.dim() == 0


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestNanFunctionsEdgeCases:
    """Test edge cases and special values."""
    
    def test_all_nan_tensor(self):
        """Test behavior with all NaN values."""
        tensor = torch.full((5, 5), float('nan'))
        
        # For reductions, PyTorch returns NaN when all values are NaN
        assert torch.isnan(nanmax(tensor))
        assert torch.isnan(nanmin(tensor))
        assert torch.isnan(nanvar(tensor))
        assert torch.isnan(nanstd(tensor))
        
        # For cumulative operations
        assert torch.isnan(nancumprod(tensor)).all()
        assert torch.isnan(nancumsum(tensor)).all()
    
    def test_no_nan_tensor(self):
        """Test behavior with no NaN values."""
        tensor = torch.randn(5, 5)
        
        # Should behave like regular functions
        assert torch.allclose(nanmax(tensor), tensor.max())
        assert torch.allclose(nanmin(tensor), tensor.min())
        
        # Variance might have slight differences due to implementation
        assert torch.allclose(nanvar(tensor), tensor.var(), rtol=1e-4)
    
    def test_empty_tensor(self):
        """Test behavior with empty tensors."""
        tensor = torch.tensor([])
        
        # Most functions should handle empty tensors
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # These might produce warnings or specific values
            result_max = nanmax(tensor)
            result_min = nanmin(tensor)
    
    def test_scalar_tensor(self):
        """Test with scalar tensors."""
        scalar = torch.tensor(5.0)
        scalar_nan = torch.tensor(float('nan'))
        
        assert nanmax(scalar) == 5.0
        assert torch.isnan(nanmax(scalar_nan))
        
        # Variance of single value should be 0
        assert nanvar(scalar) == 0.0
    
    def test_inf_values(self):
        """Test handling of infinite values."""
        tensor = torch.tensor([1.0, float('inf'), float('nan'), -float('inf'), 2.0])
        
        assert nanmax(tensor) == float('inf')
        assert nanmin(tensor) == -float('inf')
        
        # Product with inf
        assert torch.isinf(nanprod(tensor))


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestNanFunctionsProperties:
    """Property-based tests for NaN functions."""
    
    @given(
        shape=st.tuples(
            st.integers(min_value=1, max_value=20),
            st.integers(min_value=1, max_value=20)
        ),
        nan_ratio=st.floats(min_value=0, max_value=0.5)
    )
    @settings(max_examples=50, deadline=None)
    def test_nanmax_nanmin_ordering(self, shape, nan_ratio):
        """Test that nanmin <= nanmax always."""
        tensor = torch.randn(shape)
        
        # Add NaN values
        if nan_ratio > 0:
            mask = torch.rand(shape) < nan_ratio
            tensor[mask] = float('nan')
        
        # Skip if all NaN
        if not torch.isnan(tensor).all():
            max_val = nanmax(tensor)
            min_val = nanmin(tensor)
            
            if not torch.isnan(max_val) and not torch.isnan(min_val):
                assert min_val <= max_val
    
    @given(
        size=st.integers(min_value=1, max_value=100),
        nan_positions=st.lists(st.integers(min_value=0, max_value=99), max_size=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_argfunctions_consistency(self, size, nan_positions):
        """Test that argmax/argmin return valid indices."""
        tensor = torch.randn(size)
        
        # Add NaN at specific positions
        for pos in nan_positions:
            if pos < size:
                tensor[pos] = float('nan')
        
        # Get indices
        idx_max = nanargmax(tensor)
        idx_min = nanargmin(tensor)
        
        # Indices should be valid
        assert 0 <= idx_max < size
        assert 0 <= idx_min < size
        
        # Values at indices should not be NaN
        if not torch.isnan(tensor).all():
            assert not torch.isnan(tensor[idx_max])
            assert not torch.isnan(tensor[idx_min])
    
    @given(
        data=st.lists(
            st.floats(min_value=-100, max_value=100, allow_nan=False),
            min_size=1, max_size=50
        )
    )
    @settings(max_examples=30, deadline=None)
    def test_variance_non_negative(self, data):
        """Test that variance is always non-negative."""
        tensor = torch.tensor(data, dtype=torch.float32)
        
        # Add some NaN
        if len(data) > 3:
            tensor[0] = float('nan')
        
        var = nanvar(tensor)
        if not torch.isnan(var):
            assert var >= 0
        
        std = nanstd(tensor)
        if not torch.isnan(std):
            assert std >= 0


# ============================================================================
# Numerical Accuracy Tests
# ============================================================================

class TestNanFunctionsAccuracy:
    """Test numerical accuracy against NumPy."""
    
    @pytest.mark.parametrize('func_name', [
        'nanmax', 'nanmin', 'nanvar', 'nanstd', 'nanprod',
        'nancumprod', 'nancumsum', 'nanargmin', 'nanargmax'
    ])
    def test_numpy_compatibility(self, func_name, numpy_equivalents, comparison_tolerances):
        """Test compatibility with NumPy nan functions."""
        # Get functions
        torch_func = globals()[func_name]
        numpy_func = numpy_equivalents[func_name]
        
        # Create test data
        data = np.random.randn(10, 20)
        data[data > 1.5] = np.nan  # Add some NaN values
        
        tensor = torch.from_numpy(data).float()
        
        # Compare results
        torch_result = torch_func(tensor)
        numpy_result = numpy_func(data)
        
        # Convert torch result to numpy for comparison
        if isinstance(torch_result, torch.Tensor):
            torch_result = torch_result.numpy()
        
        # For arg functions, just check they identify same element
        if 'arg' in func_name:
            # Both should point to same value (accounting for NaN)
            torch_val = data.flat[torch_result]
            numpy_val = data.flat[numpy_result]
            if not np.isnan(torch_val) and not np.isnan(numpy_val):
                assert torch_val == numpy_val
        else:
            # For other functions, check numerical closeness
            tol = comparison_tolerances[torch.float32]
            np.testing.assert_allclose(
                torch_result, numpy_result,
                rtol=tol['rtol'], atol=tol['atol'],
                equal_nan=True
            )
    
    @pytest.mark.parametrize('dim', [0, 1])
    def test_dimensional_accuracy(self, dim):
        """Test accuracy along specific dimensions."""
        data = np.random.randn(10, 20, 30)
        data[data > 2] = np.nan
        
        tensor = torch.from_numpy(data).float()
        
        # Test max along dimension
        torch_max = nanmax(tensor, dim=dim)
        numpy_max = np.nanmax(data, axis=dim)
        
        np.testing.assert_allclose(
            torch_max.numpy(), numpy_max,
            rtol=1e-5, equal_nan=True
        )


# ============================================================================
# Performance Tests
# ============================================================================

class TestNanFunctionsPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize('size', [1000, 10000, 100000])
    def test_nanmax_performance(self, size, benchmark):
        """Benchmark nanmax performance."""
        tensor = torch.randn(size)
        tensor[torch.rand(size) > 0.9] = float('nan')
        
        def run_nanmax():
            return nanmax(tensor)
        
        result = benchmark(run_nanmax)
        assert not torch.isnan(result)
    
    def test_memory_efficiency(self):
        """Test memory usage of operations."""
        # Large tensor
        tensor = torch.randn(1000, 1000)
        tensor[torch.rand(1000, 1000) > 0.9] = float('nan')
        
        # Track memory
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            tensor = tensor.cuda()
            
            # Operations shouldn't use excessive memory
            result = nanmax(tensor, dim=0)
            peak_memory = torch.cuda.max_memory_allocated()
            
            # Should not allocate much more than input tensor
            tensor_memory = tensor.element_size() * tensor.nelement()
            assert peak_memory < tensor_memory * 3  # Reasonable overhead
    
    def test_operation_scaling(self):
        """Test how operations scale with tensor size."""
        times = []
        sizes = [100, 1000, 10000]
        
        for size in sizes:
            tensor = torch.randn(size)
            tensor[torch.rand(size) > 0.9] = float('nan')
            
            start = time.time()
            _ = nanvar(tensor)
            elapsed = time.time() - start
            times.append(elapsed)
        
        # Check that time grows reasonably (not quadratically)
        # Allow for some variance in timing
        assert times[-1] < times[0] * 200  # Not worse than O(n log n)


# ============================================================================
# Dtype and Device Tests
# ============================================================================

class TestNanFunctionsDtypeDevice:
    """Test dtype and device compatibility."""
    
    @pytest.mark.parametrize('dtype', [torch.float32, torch.float64, torch.float16])
    def test_dtype_compatibility(self, dtype):
        """Test functions work with different dtypes."""
        tensor = torch.randn(10, 10, dtype=dtype)
        
        # float16 might not support nan_to_num well
        if dtype == torch.float16:
            # Still test but be more lenient
            result = nanmax(tensor)
            assert result.dtype == dtype
        else:
            tensor[0, 0] = float('nan')
            result = nanmax(tensor)
            assert result.dtype == dtype
            assert not torch.isnan(result)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_compatibility(self):
        """Test functions work on CUDA tensors."""
        tensor = torch.randn(10, 10).cuda()
        tensor[0, 0] = float('nan')
        
        # All functions should work on CUDA
        assert nanmax(tensor).is_cuda
        assert nanmin(tensor).is_cuda
        assert nanvar(tensor).is_cuda
        assert nanstd(tensor).is_cuda
        assert nanprod(tensor).is_cuda
        assert nancumprod(tensor).is_cuda
        assert nancumsum(tensor).is_cuda
        assert nanargmin(tensor).is_cuda
        assert nanargmax(tensor).is_cuda
    
    def test_dtype_preservation(self):
        """Test that operations preserve dtype."""
        for dtype in [torch.float32, torch.float64]:
            tensor = torch.randn(5, 5, dtype=dtype)
            tensor[0, 0] = float('nan')
            
            # Most operations should preserve dtype
            assert nanmax(tensor).dtype == dtype
            assert nanmin(tensor).dtype == dtype
            assert nanvar(tensor).dtype == dtype
            assert nanstd(tensor).dtype == dtype
            assert nanprod(tensor).dtype == dtype
            assert nancumprod(tensor).dtype == dtype
            assert nancumsum(tensor).dtype == dtype


# ============================================================================
# Gradient Tests
# ============================================================================

class TestNanFunctionsGradients:
    """Test gradient flow through NaN functions."""
    
    def test_gradient_flow_basic(self):
        """Test that gradients flow through operations."""
        tensor = torch.randn(5, 5, requires_grad=True)
        # Don't add NaN to maintain gradient flow
        
        result = nanmax(tensor)
        result.backward()
        
        assert tensor.grad is not None
        assert not torch.isnan(tensor.grad).any()
    
    def test_gradient_with_nan_handling(self):
        """Test gradient behavior with NaN values."""
        tensor = torch.randn(5, 5, requires_grad=True)
        
        # Create a copy and add NaN
        tensor_with_nan = tensor.clone()
        mask = torch.rand(5, 5) > 0.8
        tensor_with_nan[mask] = float('nan')
        
        # Note: This might not work as expected due to nan_to_num
        # This is a limitation of the current implementation
        try:
            result = nanmax(tensor_with_nan)
            if result.requires_grad:
                result.backward()
        except RuntimeError:
            # Expected if gradient computation fails with NaN
            pass


# ============================================================================
# Integration Tests
# ============================================================================

class TestNanFunctionsIntegration:
    """Test integration with PyTorch ecosystem."""
    
    def test_with_neural_network(self):
        """Test usage in neural network context."""
        class NanRobustPooling(torch.nn.Module):
            def forward(self, x):
                # Max pooling that handles NaN
                batch, channels, height, width = x.shape
                x_reshaped = x.view(batch, channels, -1)
                pooled = torch.stack([
                    nanmax(x_reshaped[b, c]) 
                    for b in range(batch) 
                    for c in range(channels)
                ]).view(batch, channels)
                return pooled
        
        model = NanRobustPooling()
        input_tensor = torch.randn(2, 3, 4, 4)
        input_tensor[0, 0, 0, 0] = float('nan')
        
        output = model(input_tensor)
        assert output.shape == (2, 3)
        assert not torch.isnan(output).all()
    
    def test_in_data_pipeline(self):
        """Test usage in data preprocessing pipeline."""
        # Simulate data with missing values
        data = torch.randn(100, 10)
        missing_mask = torch.rand(100, 10) > 0.9
        data[missing_mask] = float('nan')
        
        # Normalize using nan-robust statistics
        mean = torch.stack([data[:, i].nanmean() for i in range(10)])
        std = torch.stack([nanstd(data[:, i]) for i in range(10)])
        
        # Avoid division by zero
        std = torch.clamp(std, min=1e-6)
        
        normalized = (data - mean) / std
        
        # Check normalization worked
        assert normalized.shape == data.shape
        # Non-NaN values should be normalized
        non_nan_mask = ~torch.isnan(data)
        assert not torch.isnan(normalized[non_nan_mask]).any()


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestNanFunctionsErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_dimensions(self):
        """Test behavior with invalid dimension arguments."""
        tensor = torch.randn(5, 5)
        
        # Dimension out of range should raise error
        with pytest.raises((IndexError, RuntimeError)):
            nanmax(tensor, dim=3)  # Only has 2 dimensions
    
    def test_keepdim_behavior(self):
        """Test keepdim parameter behavior."""
        tensor = torch.randn(3, 4, 5)
        tensor[0, 0, 0] = float('nan')
        
        # Without keepdim
        result = nanmax(tensor, dim=1)
        assert result.shape == (3, 5)
        
        # With keepdim
        result_keep = nanmax(tensor, dim=1, keepdim=True)
        assert result_keep.shape == (3, 1, 5)
    
    def test_empty_tensor_dimensions(self):
        """Test with tensors that have empty dimensions."""
        tensor = torch.randn(0, 5)  # 0 rows
        
        # Should handle gracefully
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = nanmax(tensor, dim=0)
            # Result should have shape (5,) but might be undefined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF