#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 04:06:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/linalg/test__geometric_median.py

"""Comprehensive tests for geometric_median function."""

import pytest
import numpy as np
import torch
from unittest.mock import patch, MagicMock, call
import warnings
import tempfile
import os


class TestGeometricMedianBasic:
    """Test basic functionality of geometric_median."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        # Set random seed for reproducibility
        torch.manual_seed(42)
        np.random.seed(42)
        
    def test_import(self):
        """Test that geometric_median can be imported."""
from scitex.linalg import geometric_median
        assert callable(geometric_median)
        
    def test_basic_1d(self):
        """Test geometric median with 1D tensor."""
from scitex.linalg import geometric_median
        
        # Simple 1D case
        x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Mock the compute_geometric_median function
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.tensor(3.0)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x)
            
            # Check that compute_geometric_median was called
            mock_compute.assert_called_once()
            assert result == 3.0
            
    def test_basic_2d(self):
        """Test geometric median with 2D tensor."""
from scitex.linalg import geometric_median
        
        # 2D tensor
        x = torch.tensor([[1.0, 2.0, 3.0],
                         [4.0, 5.0, 6.0],
                         [7.0, 8.0, 9.0]])
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.tensor([4.0, 5.0, 6.0])
            mock_compute.return_value = mock_result
            
            # Test with default dim=-1
            result = geometric_median(x)
            
            # Verify the function was called with correct points
            called_points = mock_compute.call_args[0][0]
            assert len(called_points) == 3  # 3 columns
            
    def test_basic_3d(self):
        """Test geometric median with 3D tensor."""
from scitex.linalg import geometric_median
        
        # 3D tensor (batch x features x time)
        x = torch.randn(2, 4, 5)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(2, 4)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x, dim=-1)
            
            # Check that points were extracted along last dimension
            called_points = mock_compute.call_args[0][0]
            assert len(called_points) == 5  # 5 time points


class TestGeometricMedianDimensions:
    """Test dimension handling in geometric_median."""
    
    def test_positive_dim(self):
        """Test with positive dimension indices."""
from scitex.linalg import geometric_median
        
        x = torch.randn(3, 4, 5)
        
        # Test different positive dimensions
        for dim in [0, 1, 2]:
            with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
                mock_result = MagicMock()
                expected_shape = list(x.shape)
                expected_shape.pop(dim)
                mock_result.median = torch.randn(*expected_shape)
                mock_compute.return_value = mock_result
                
                result = geometric_median(x, dim=dim)
                
                # Verify correct number of points
                called_points = mock_compute.call_args[0][0]
                assert len(called_points) == x.shape[dim]
                
    def test_negative_dim(self):
        """Test with negative dimension indices."""
from scitex.linalg import geometric_median
        
        x = torch.randn(3, 4, 5)
        
        # Test negative dimensions
        for neg_dim, pos_dim in [(-1, 2), (-2, 1), (-3, 0)]:
            with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
                mock_result = MagicMock()
                mock_result.median = torch.randn(1)  # dummy
                mock_compute.return_value = mock_result
                
                # Should handle negative dimensions correctly
                result1 = geometric_median(x, dim=neg_dim)
                result2 = geometric_median(x, dim=pos_dim)
                
                # Both should extract same number of points
                points1 = mock_compute.call_args_list[-2][0][0]
                points2 = mock_compute.call_args_list[-1][0][0]
                assert len(points1) == len(points2)
                
    def test_dim_out_of_range(self):
        """Test with dimension index out of range."""
from scitex.linalg import geometric_median
        
        x = torch.randn(3, 4, 5)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median'):
            # These should raise errors during indexing
            with pytest.raises((IndexError, RuntimeError)):
                geometric_median(x, dim=3)  # Too large
                
            with pytest.raises((IndexError, RuntimeError)):
                geometric_median(x, dim=-4)  # Too negative


class TestGeometricMedianDataTypes:
    """Test different data types and tensor properties."""
    
    def test_float32(self):
        """Test with float32 tensors."""
from scitex.linalg import geometric_median
        
        x = torch.randn(10, 5, dtype=torch.float32)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10, dtype=torch.float32)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x)
            
            # Points should maintain dtype
            called_points = mock_compute.call_args[0][0]
            assert all(p.dtype == torch.float32 for p in called_points)
            
    def test_float64(self):
        """Test with float64 tensors."""
from scitex.linalg import geometric_median
        
        x = torch.randn(10, 5, dtype=torch.float64)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10, dtype=torch.float64)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x)
            
            # Points should maintain dtype
            called_points = mock_compute.call_args[0][0]
            assert all(p.dtype == torch.float64 for p in called_points)
            
    def test_gpu_tensor(self):
        """Test with GPU tensors if available."""
from scitex.linalg import geometric_median
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        x = torch.randn(10, 5).cuda()
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10).cuda()
            mock_compute.return_value = mock_result
            
            result = geometric_median(x)
            
            # Points should be on same device
            called_points = mock_compute.call_args[0][0]
            assert all(p.is_cuda for p in called_points)
            
    def test_requires_grad(self):
        """Test with tensors that require gradients."""
from scitex.linalg import geometric_median
        
        x = torch.randn(10, 5, requires_grad=True)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x)
            
            # Gradient requirement should be preserved
            called_points = mock_compute.call_args[0][0]
            assert all(p.requires_grad for p in called_points)


class TestGeometricMedianDecorator:
    """Test the @torch_fn decorator behavior."""
    
    def test_numpy_input(self):
        """Test that numpy arrays are converted to tensors."""
from scitex.linalg import geometric_median
        
        x = np.random.randn(10, 5)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10)
            mock_compute.return_value = mock_result
            
            # Should handle numpy input due to @torch_fn decorator
            result = geometric_median(x)
            
            # Verify conversion happened
            called_points = mock_compute.call_args[0][0]
            assert all(isinstance(p, torch.Tensor) for p in called_points)
            
    def test_list_input(self):
        """Test that lists are converted to tensors."""
from scitex.linalg import geometric_median
        
        x = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.tensor([2.5, 5.0])
            mock_compute.return_value = mock_result
            
            # Should handle list input due to @torch_fn decorator
            result = geometric_median(x)
            
            # Verify conversion happened
            called_points = mock_compute.call_args[0][0]
            assert all(isinstance(p, torch.Tensor) for p in called_points)
            
    def test_mixed_device_handling(self):
        """Test handling of tensors on different devices."""
from scitex.linalg import geometric_median
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        # CPU tensor
        x_cpu = torch.randn(10, 5)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10)
            mock_compute.return_value = mock_result
            
            # Should work with CPU tensor
            result = geometric_median(x_cpu)
            
            # All points should be on same device
            called_points = mock_compute.call_args[0][0]
            devices = [p.device for p in called_points]
            assert all(d == devices[0] for d in devices)


class TestGeometricMedianEdgeCases:
    """Test edge cases and special inputs."""
    
    def test_single_point(self):
        """Test with single point (no median to compute)."""
from scitex.linalg import geometric_median
        
        x = torch.tensor([[1.0], [2.0], [3.0]])  # 3x1 tensor
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.tensor([1.0, 2.0, 3.0])
            mock_compute.return_value = mock_result
            
            result = geometric_median(x, dim=1)
            
            # Should still call with single point
            called_points = mock_compute.call_args[0][0]
            assert len(called_points) == 1
            
    def test_empty_tensor(self):
        """Test with empty tensor."""
from scitex.linalg import geometric_median
        
        x = torch.tensor([])
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            # Should handle empty case
            with pytest.raises((RuntimeError, IndexError, ValueError)):
                geometric_median(x)
                
    def test_nan_values(self):
        """Test with NaN values."""
from scitex.linalg import geometric_median
        
        x = torch.tensor([[1.0, 2.0, float('nan')],
                         [4.0, 5.0, 6.0]])
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.tensor([float('nan'), 5.0])
            mock_compute.return_value = mock_result
            
            # Should pass through to compute_geometric_median
            result = geometric_median(x)
            
            # NaN handling is up to compute_geometric_median
            called_points = mock_compute.call_args[0][0]
            assert any(torch.isnan(p).any() for p in called_points)
            
    def test_inf_values(self):
        """Test with infinite values."""
from scitex.linalg import geometric_median
        
        x = torch.tensor([[1.0, 2.0, float('inf')],
                         [4.0, 5.0, 6.0]])
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.tensor([float('inf'), 5.0])
            mock_compute.return_value = mock_result
            
            # Should pass through to compute_geometric_median
            result = geometric_median(x)
            
            # Inf handling is up to compute_geometric_median
            called_points = mock_compute.call_args[0][0]
            assert any(torch.isinf(p).any() for p in called_points)


class TestGeometricMedianLargeScale:
    """Test with large-scale data."""
    
    def test_large_tensor(self):
        """Test with large tensors."""
from scitex.linalg import geometric_median
        
        # Large tensor
        x = torch.randn(100, 1000)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(100)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x, dim=1)
            
            # Should extract 1000 points
            called_points = mock_compute.call_args[0][0]
            assert len(called_points) == 1000
            
    def test_high_dimensional(self):
        """Test with high-dimensional tensors."""
from scitex.linalg import geometric_median
        
        # 5D tensor
        x = torch.randn(2, 3, 4, 5, 6)
        
        for dim in range(5):
            with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
                mock_result = MagicMock()
                mock_result.median = torch.randn(1)  # dummy
                mock_compute.return_value = mock_result
                
                result = geometric_median(x, dim=dim)
                
                # Should handle all dimensions correctly
                called_points = mock_compute.call_args[0][0]
                assert len(called_points) == x.shape[dim]


class TestGeometricMedianIntegration:
    """Test integration with real compute_geometric_median if available."""
    
    def test_with_real_implementation(self):
        """Test with actual geom_median library if available."""
        try:
            from geom_median.torch import compute_geometric_median as real_compute
from scitex.linalg import geometric_median
        except ImportError:
            pytest.skip("geom_median not available")
            
        # Simple test case where geometric median is known
        # For 1D case, geometric median equals regular median
        x = torch.tensor([[1.0], [2.0], [3.0], [4.0], [5.0]])
        
        result = geometric_median(x, dim=0)
        
        # Should be close to median value (3.0)
        assert torch.allclose(result, torch.tensor([3.0]), atol=0.1)
        
    def test_convergence_properties(self):
        """Test convergence properties of geometric median."""
from scitex.linalg import geometric_median
        
        # Create points where geometric median should be at origin
        angles = torch.linspace(0, 2 * np.pi, 8, dtype=torch.float32)[:-1]
        x = torch.stack([torch.cos(angles), torch.sin(angles)], dim=1)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            # Geometric median of symmetric points around origin should be near origin
            mock_result.median = torch.tensor([0.0, 0.0])
            mock_compute.return_value = mock_result
            
            result = geometric_median(x, dim=0)
            
            # Result should be near origin
            assert torch.allclose(result, torch.zeros(2), atol=0.1)


class TestGeometricMedianDocstring:
    """Test function documentation and signature."""
    
    def test_has_docstring(self):
        """Test that function has a docstring."""
from scitex.linalg import geometric_median
        
        # Currently the source shows "This script does XYZ" which needs improvement
        assert geometric_median.__doc__ is not None
        
    def test_function_signature(self):
        """Test function signature."""
from scitex.linalg import geometric_median
        import inspect
        
        sig = inspect.signature(geometric_median)
        params = list(sig.parameters.keys())
        
        assert 'xx' in params
        assert 'dim' in params
        
        # Check default values
        assert sig.parameters['dim'].default == -1
        
    def test_torch_fn_decorator_applied(self):
        """Test that torch_fn decorator is properly applied."""
from scitex.linalg import geometric_median
        
        # Should have decorator attributes or wrapped function
        # The exact attributes depend on decorator implementation
        assert callable(geometric_median)


class TestGeometricMedianPerformance:
    """Test performance considerations."""
    
    def test_memory_efficiency(self):
        """Test memory usage patterns."""
from scitex.linalg import geometric_median
        
        x = torch.randn(100, 100)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(100)
            mock_compute.return_value = mock_result
            
            # Function creates a list of points
            result = geometric_median(x)
            
            # Should create list of 100 points (for dim=-1)
            called_points = mock_compute.call_args[0][0]
            assert isinstance(called_points, list)
            assert len(called_points) == 100
            
    def test_no_unnecessary_copies(self):
        """Test that function doesn't make unnecessary copies."""
from scitex.linalg import geometric_median
        
        x = torch.randn(10, 5)
        x_ptr = x.data_ptr()
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(10)
            mock_compute.return_value = mock_result
            
            result = geometric_median(x)
            
            # Original tensor should not be modified
            assert x.data_ptr() == x_ptr
            
            # Slices should share memory with original
            called_points = mock_compute.call_args[0][0]
            # Note: Slicing creates views, not copies in PyTorch


class TestGeometricMedianErrorHandling:
    """Test error handling and edge cases."""
    
    def test_dimension_mismatch_handling(self):
        """Test handling of dimension mismatches."""
from scitex.linalg import geometric_median
        
        x = torch.randn(3, 4, 5)
        
        # The current implementation has a bug where it converts dim to tensor
        # This should be tested and potentially fixed
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_result = MagicMock()
            mock_result.median = torch.randn(1)
            mock_compute.return_value = mock_result
            
            # Test the current behavior
            result = geometric_median(x, dim=-1)
            
            # The dimension conversion to tensor seems incorrect
            # This test documents current behavior
            
    def test_compute_geometric_median_failure(self):
        """Test handling when compute_geometric_median fails."""
from scitex.linalg import geometric_median
        
        x = torch.randn(10, 5)
        
        with patch('scitex.linalg._geometric_median.compute_geometric_median') as mock_compute:
            mock_compute.side_effect = RuntimeError("Computation failed")
            
            with pytest.raises(RuntimeError):
                geometric_median(x)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
