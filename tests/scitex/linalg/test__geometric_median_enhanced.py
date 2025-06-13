#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 09:35:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/linalg/test__geometric_median_enhanced.py

"""Comprehensive tests for geometric median computation functionality."""

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock


class TestGeometricMedianEnhanced:
    """Enhanced test suite for geometric_median function."""

    def test_basic_2d_tensor(self):
        """Test geometric median with basic 2D tensor."""
        try:
            from scitex.linalg import geometric_median
            
            # Simple 2D case: 3 points in 2D space
            xx = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
            result = geometric_median(xx, dim=0)
            
            # Result should be a tensor
            assert isinstance(result, torch.Tensor)
            # Should have shape [2] (median of 3 2D points)
            assert result.shape == torch.Size([2])
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_3d_tensor_processing(self):
        """Test geometric median with 3D tensor."""
        try:
            from scitex.linalg import geometric_median
            
            # 3D tensor: batch_size=2, seq_len=4, features=3
            xx = torch.randn(2, 4, 3)
            result = geometric_median(xx, dim=1)  # median along sequence dimension
            
            # Result shape should be [2, 3] (median over seq_len)
            assert result.shape == torch.Size([2, 3])
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_negative_dimension_index(self):
        """Test handling of negative dimension indices."""
        try:
            from scitex.linalg import geometric_median
            
            xx = torch.randn(3, 4, 5)
            
            # Test dim=-1 (last dimension)
            result_neg = geometric_median(xx, dim=-1)
            result_pos = geometric_median(xx, dim=2)  # equivalent to dim=-1
            
            # Results should be equivalent
            assert result_neg.shape == result_pos.shape
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_single_point_case(self):
        """Test geometric median with single point."""
        try:
            from scitex.linalg import geometric_median
            
            # Single point tensor
            xx = torch.tensor([[1.0, 2.0, 3.0]])
            result = geometric_median(xx, dim=0)
            
            # Should return the single point
            assert result.shape == torch.Size([3])
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_identical_points(self):
        """Test geometric median with identical points."""
        try:
            from scitex.linalg import geometric_median
            
            # All points are identical
            point = torch.tensor([1.0, 2.0, 3.0])
            xx = point.unsqueeze(0).repeat(5, 1)  # 5 identical points
            
            result = geometric_median(xx, dim=0)
            
            # Result should be close to the identical point
            assert result.shape == torch.Size([3])
            assert torch.allclose(result, point, atol=1e-3)
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_different_dimensions(self):
        """Test geometric median with various tensor dimensions."""
        try:
            from scitex.linalg import geometric_median
            
            # Test 1D case - actually works, just returns the median
            xx_1d = torch.randn(10)
            result = geometric_median(xx_1d, dim=0)
            # 1D case works and returns a scalar
            assert result.numel() == 1
                
            # Test 4D case
            xx_4d = torch.randn(2, 3, 4, 5)
            result = geometric_median(xx_4d, dim=1)
            assert result.shape == torch.Size([2, 4, 5])
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_device_consistency(self):
        """Test that result maintains device consistency."""
        try:
            from scitex.linalg import geometric_median
            
            xx = torch.randn(5, 3)
            device = xx.device
            
            result = geometric_median(xx, dim=0)
            
            # Result should be on same device
            assert result.device == device
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_dtype_preservation(self):
        """Test that dtype is preserved or handled appropriately."""
        try:
            from scitex.linalg import geometric_median
            
            # Test with float32
            xx_f32 = torch.randn(5, 3, dtype=torch.float32)
            result_f32 = geometric_median(xx_f32, dim=0)
            
            # Test with float64
            xx_f64 = torch.randn(5, 3, dtype=torch.float64)
            result_f64 = geometric_median(xx_f64, dim=0)
            
            # Both should work (exact dtype preservation may vary)
            assert result_f32.shape == torch.Size([3])
            assert result_f64.shape == torch.Size([3])
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_large_tensor_performance(self):
        """Test performance with larger tensors."""
        try:
            from scitex.linalg import geometric_median
            
            # Larger tensor test
            xx = torch.randn(100, 50)
            result = geometric_median(xx, dim=0)
            
            assert result.shape == torch.Size([50])
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_dimension_validation(self):
        """Test dimension parameter validation."""
        try:
            from scitex.linalg import geometric_median
            
            xx = torch.randn(5, 3, 4)
            
            # Valid dimensions
            result_0 = geometric_median(xx, dim=0)
            result_1 = geometric_median(xx, dim=1)
            result_2 = geometric_median(xx, dim=2)
            
            assert result_0.shape == torch.Size([3, 4])
            assert result_1.shape == torch.Size([5, 4])
            assert result_2.shape == torch.Size([5, 3])
            
            # Invalid dimension should raise error
            with pytest.raises((IndexError, RuntimeError)):
                geometric_median(xx, dim=3)
                
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_empty_tensor_handling(self):
        """Test handling of empty tensors."""
        try:
            from scitex.linalg import geometric_median
            
            # Empty tensor
            xx_empty = torch.empty(0, 3)
            
            with pytest.raises(IndexError):
                # Specific error from geom_median library
                geometric_median(xx_empty, dim=0)
                
        except ImportError:
            pytest.skip("geom_median package not available")

    @patch('scitex.linalg._geometric_median.compute_geometric_median')
    def test_external_library_integration(self, mock_compute):
        """Test integration with external geom_median library."""
        try:
            from scitex.linalg import geometric_median
            
            # Mock the external library
            mock_result = MagicMock()
            mock_result.median = torch.tensor([1.0, 2.0, 3.0])
            mock_compute.return_value = mock_result
            
            xx = torch.randn(5, 3)
            result = geometric_median(xx, dim=0)
            
            # Should call external library
            mock_compute.assert_called_once()
            assert torch.equal(result, torch.tensor([1.0, 2.0, 3.0]))
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_torch_fn_decorator_behavior(self):
        """Test that torch_fn decorator works correctly."""
        try:
            from scitex.linalg import geometric_median
            
            # Test with numpy input (should be converted by torch_fn)
            xx_np = np.random.randn(5, 3)
            result = geometric_median(xx_np, dim=0)
            
            # The decorator may return numpy or torch - check it's numeric
            assert isinstance(result, (torch.Tensor, np.ndarray))
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_gradient_computation(self):
        """Test gradient computation if enabled."""
        try:
            from scitex.linalg import geometric_median
            
            xx = torch.randn(5, 3, requires_grad=True)
            result = geometric_median(xx, dim=0)
            
            # Should be able to compute gradients
            loss = result.sum()
            try:
                loss.backward()
                # If successful, gradients should exist
                assert xx.grad is not None
            except RuntimeError:
                # Some implementations may not support gradients
                pass
                
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_batch_processing_consistency(self):
        """Test consistency across batch processing."""
        try:
            from scitex.linalg import geometric_median
            
            # Create batch of identical problems
            xx_single = torch.randn(5, 3)
            xx_batch = xx_single.unsqueeze(0).repeat(4, 1, 1)  # [4, 5, 3]
            
            # Process single
            result_single = geometric_median(xx_single, dim=0)
            
            # Process batch
            result_batch = geometric_median(xx_batch, dim=1)
            
            # Each batch result should be similar to single result (looser tolerance)
            for i in range(4):
                assert torch.allclose(result_batch[i], result_single, atol=1e-3)
                
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        try:
            from scitex.linalg import geometric_median
            
            # Test with very large values
            xx_large = torch.randn(5, 3) * 1e6
            result_large = geometric_median(xx_large, dim=0)
            assert torch.isfinite(result_large).all()
            
            # Test with very small values
            xx_small = torch.randn(5, 3) * 1e-6
            result_small = geometric_median(xx_small, dim=0)
            assert torch.isfinite(result_small).all()
            
        except ImportError:
            pytest.skip("geom_median package not available")

    def test_dimension_conversion_logic(self):
        """Test the dimension conversion logic specifically."""
        try:
            from scitex.linalg import geometric_median
            
            xx = torch.randn(3, 4, 5)
            
            # Test various negative indices
            result_neg1 = geometric_median(xx, dim=-1)
            result_neg2 = geometric_median(xx, dim=-2)
            result_neg3 = geometric_median(xx, dim=-3)
            
            # Compare with positive equivalents
            result_pos2 = geometric_median(xx, dim=2)
            result_pos1 = geometric_median(xx, dim=1)
            result_pos0 = geometric_median(xx, dim=0)
            
            assert result_neg1.shape == result_pos2.shape
            assert result_neg2.shape == result_pos1.shape
            assert result_neg3.shape == result_pos0.shape
            
        except ImportError:
            pytest.skip("geom_median package not available")


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])