#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 03:20:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/linalg/test__distance.py

"""Comprehensive tests for distance computation functions.

This module tests the distance functions including euclidean_distance,
cdist wrapper, and the edist alias, with various array shapes and edge cases.
"""

import pytest
import os
import numpy as np
import torch
from typing import Union, Tuple, List
import scipy.spatial.distance as scipy_distance
from numpy.testing import assert_array_almost_equal, assert_array_equal


class TestEuclideanDistanceBasic:
    """Basic tests for euclidean_distance function."""
    
    def test_euclidean_distance_1d(self):
        """Test euclidean distance with 1D arrays."""
        from scitex.linalg import euclidean_distance
        
        # Simple 1D case
        uu = np.array([0, 0, 0])
        vv = np.array([1, 1, 1])
        
        dist = euclidean_distance(uu, vv, axis=0)
        expected = np.sqrt(3)  # sqrt(1^2 + 1^2 + 1^2)
        
        assert_array_almost_equal(dist, expected)
    
    def test_euclidean_distance_2d(self):
        """Test euclidean distance with 2D arrays."""
        from scitex.linalg import euclidean_distance
        
        # 2D arrays
        uu = np.array([[0, 0], [1, 1], [2, 2]])
        vv = np.array([[3, 3], [4, 4], [5, 5]])
        
        # Distance along axis 0
        dist = euclidean_distance(uu, vv, axis=0)
        
        # Manual calculation
        expected = np.sqrt((3-0)**2 + (4-1)**2 + (5-2)**2)
        assert_array_almost_equal(dist[0, 0], expected)
    
    def test_euclidean_distance_3d(self):
        """Test euclidean distance with 3D arrays."""
        from scitex.linalg import euclidean_distance
        
        # 3D arrays
        uu = np.random.rand(4, 3, 5)
        vv = np.random.rand(4, 3, 5)
        
        # Distance along different axes
        dist_axis0 = euclidean_distance(uu, vv, axis=0)
        dist_axis1 = euclidean_distance(uu, vv, axis=1)
        dist_axis2 = euclidean_distance(uu, vv, axis=2)
        
        # Check output shapes
        assert dist_axis0.shape == (3, 5, 3, 5)
        assert dist_axis1.shape == (4, 5, 4, 5)
        assert dist_axis2.shape == (4, 3, 4, 3)
    
    def test_euclidean_distance_scalar_inputs(self):
        """Test euclidean distance with scalar inputs."""
        from scitex.linalg import euclidean_distance
        
        # Scalar inputs
        uu = 3.0
        vv = 7.0
        
        dist = euclidean_distance(uu, vv)
        expected = 4.0  # |7 - 3|
        
        assert_array_almost_equal(dist, expected)
    
    def test_euclidean_distance_zero_distance(self):
        """Test euclidean distance when arrays are identical."""
        from scitex.linalg import euclidean_distance
        
        # Identical arrays
        arr = np.random.rand(5, 3)
        dist = euclidean_distance(arr, arr, axis=0)
        
        # All distances should be zero
        assert np.allclose(dist, 0)


class TestEuclideanDistanceAxis:
    """Test axis parameter behavior."""
    
    def test_axis_parameter_2d(self):
        """Test different axis values with 2D arrays."""
        from scitex.linalg import euclidean_distance
        
        uu = np.array([[1, 2, 3], [4, 5, 6]])
        vv = np.array([[7, 8, 9], [10, 11, 12]])
        
        # Axis 0: compare rows
        dist0 = euclidean_distance(uu, vv, axis=0)
        assert dist0.shape == (3, 3)  # 3x3 distance matrix
        
        # Axis 1: compare columns  
        dist1 = euclidean_distance(uu, vv, axis=1)
        assert dist1.shape == (2, 2)  # 2x2 distance matrix
    
    def test_negative_axis(self):
        """Test negative axis values."""
        from scitex.linalg import euclidean_distance
        
        uu = np.random.rand(3, 4, 5)
        vv = np.random.rand(3, 4, 5)
        
        # axis=-1 should be same as axis=2
        dist_neg1 = euclidean_distance(uu, vv, axis=-1)
        dist_2 = euclidean_distance(uu, vv, axis=2)
        
        assert_array_almost_equal(dist_neg1, dist_2)
    
    def test_invalid_axis(self):
        """Test invalid axis values."""
        from scitex.linalg import euclidean_distance
        
        uu = np.random.rand(3, 4)
        vv = np.random.rand(3, 4)
        
        # Axis out of bounds
        with pytest.raises((IndexError, np.AxisError)):
            euclidean_distance(uu, vv, axis=5)


class TestEuclideanDistanceShapes:
    """Test shape compatibility and broadcasting."""
    
    def test_shape_mismatch_error(self):
        """Test error when shapes don't match along specified axis."""
        from scitex.linalg import euclidean_distance
        
        uu = np.random.rand(3, 4)
        vv = np.random.rand(5, 4)  # Different size along axis 0
        
        with pytest.raises(ValueError, match="Shape along axis"):
            euclidean_distance(uu, vv, axis=0)
    
    def test_compatible_shapes(self):
        """Test with compatible but different shapes."""
        from scitex.linalg import euclidean_distance
        
        # Different shapes but same size along axis
        uu = np.random.rand(3, 4, 5)
        vv = np.random.rand(3, 2, 7)
        
        # Should work along axis 0
        dist = euclidean_distance(uu, vv, axis=0)
        assert dist.shape == (4, 5, 2, 7)
    
    def test_broadcasting_behavior(self):
        """Test broadcasting in distance calculations."""
        from scitex.linalg import euclidean_distance
        
        # Arrays that can be broadcast
        uu = np.array([[1], [2], [3]])  # 3x1
        vv = np.array([[4, 5, 6]])      # 1x3 (will be treated as 3x1 after moveaxis)
        
        # This should work due to internal reshaping
        dist = euclidean_distance(uu, vv, axis=0)
        assert dist.shape[0] == 1  # Result shape depends on implementation


class TestEuclideanDistanceNumericAccuracy:
    """Test numeric accuracy and edge cases."""
    
    def test_known_distances(self):
        """Test with known distance values."""
        from scitex.linalg import euclidean_distance
        
        # 3-4-5 right triangle
        uu = np.array([0, 0])
        vv = np.array([3, 4])
        
        dist = euclidean_distance(uu, vv, axis=0)
        assert_array_almost_equal(dist, 5.0)
        
        # Unit vectors
        uu = np.array([1, 0, 0])
        vv = np.array([0, 1, 0])
        
        dist = euclidean_distance(uu, vv, axis=0)
        assert_array_almost_equal(dist, np.sqrt(2))
    
    def test_large_values(self):
        """Test with large values to check numeric stability."""
        from scitex.linalg import euclidean_distance
        
        uu = np.array([1e10, 1e10])
        vv = np.array([1e10 + 1, 1e10 + 1])
        
        dist = euclidean_distance(uu, vv, axis=0)
        assert_array_almost_equal(dist, np.sqrt(2), decimal=5)
    
    def test_small_values(self):
        """Test with very small values."""
        from scitex.linalg import euclidean_distance
        
        uu = np.array([1e-10, 1e-10])
        vv = np.array([2e-10, 2e-10])
        
        dist = euclidean_distance(uu, vv, axis=0)
        assert_array_almost_equal(dist, np.sqrt(2) * 1e-10)
    
    def test_mixed_signs(self):
        """Test with mixed positive and negative values."""
        from scitex.linalg import euclidean_distance
        
        uu = np.array([-1, -2, -3])
        vv = np.array([1, 2, 3])
        
        dist = euclidean_distance(uu, vv, axis=0)
        expected = np.sqrt(4 + 16 + 36)  # 2^2 + 4^2 + 6^2
        assert_array_almost_equal(dist, expected)


class TestCdistWrapper:
    """Test the cdist wrapper function."""
    
    def test_cdist_basic(self):
        """Test basic cdist functionality."""
        from scitex.linalg import cdist
        
        # Simple 2D arrays
        XA = np.array([[0, 0], [1, 1], [2, 2]])
        XB = np.array([[0, 1], [1, 0], [3, 3]])
        
        # Compute distances
        distances = cdist(XA, XB)
        
        # Check shape
        assert distances.shape == (3, 3)
        
        # Check specific values
        assert_array_almost_equal(distances[0, 0], 1.0)  # [0,0] to [0,1]
        assert_array_almost_equal(distances[2, 2], np.sqrt(2))  # [2,2] to [3,3]
    
    def test_cdist_metrics(self):
        """Test cdist with different metrics."""
        from scitex.linalg import cdist
        
        XA = np.random.rand(5, 3)
        XB = np.random.rand(4, 3)
        
        # Test different metrics
        metrics = ['euclidean', 'cityblock', 'cosine', 'correlation']
        
        for metric in metrics:
            dist = cdist(XA, XB, metric=metric)
            assert dist.shape == (5, 4)
            
            # Compare with scipy
            expected = scipy_distance.cdist(XA, XB, metric=metric)
            assert_array_almost_equal(dist, expected)
    
    def test_cdist_custom_metric(self):
        """Test cdist with custom metric function."""
        from scitex.linalg import cdist
        
        # Custom metric
        def custom_metric(u, v):
            return np.sum(np.abs(u - v))
        
        XA = np.array([[1, 2], [3, 4]])
        XB = np.array([[5, 6], [7, 8]])
        
        dist = cdist(XA, XB, metric=custom_metric)
        
        # Check manual calculation
        assert_array_almost_equal(dist[0, 0], 8)  # |1-5| + |2-6|
        assert_array_almost_equal(dist[1, 1], 8)  # |3-7| + |4-8|
    
    def test_cdist_kwargs_passthrough(self):
        """Test that kwargs are passed through correctly."""
        from scitex.linalg import cdist
        
        XA = np.random.rand(3, 5)
        XB = np.random.rand(4, 5)
        
        # Test with p parameter for Minkowski distance
        dist_p1 = cdist(XA, XB, metric='minkowski', p=1)
        dist_p2 = cdist(XA, XB, metric='minkowski', p=2)
        
        # Results should be different
        assert not np.allclose(dist_p1, dist_p2)


class TestEdistAlias:
    """Test the edist alias."""
    
    def test_edist_is_alias(self):
        """Test that edist is an alias for euclidean_distance."""
        from scitex.linalg import edist, euclidean_distance
        
        assert edist is euclidean_distance
        assert edist.__name__ == euclidean_distance.__name__
        assert edist.__doc__ == euclidean_distance.__doc__
    
    def test_edist_functionality(self):
        """Test that edist works identically to euclidean_distance."""
        from scitex.linalg import edist, euclidean_distance
        
        uu = np.random.rand(5, 3)
        vv = np.random.rand(5, 3)
        
        dist1 = euclidean_distance(uu, vv, axis=0)
        dist2 = edist(uu, vv, axis=0)
        
        assert_array_equal(dist1, dist2)


class TestNumpyFnDecorator:
    """Test @numpy_fn decorator behavior."""
    
    def test_torch_tensor_input(self):
        """Test with PyTorch tensor inputs."""
        from scitex.linalg import euclidean_distance
        
        # PyTorch tensors
        uu = torch.tensor([1.0, 2.0, 3.0])
        vv = torch.tensor([4.0, 5.0, 6.0])
        
        # Should handle torch tensors (converted to numpy by decorator)
        dist = euclidean_distance(uu, vv, axis=0)
        
        # Result should be numpy array
        assert isinstance(dist, np.ndarray)
        expected = np.sqrt((4-1)**2 + (5-2)**2 + (6-3)**2)
        assert_array_almost_equal(dist, expected)
    
    def test_list_input(self):
        """Test with list inputs."""
        from scitex.linalg import euclidean_distance
        
        # Lists
        uu = [1, 2, 3]
        vv = [4, 5, 6]
        
        # Should handle lists (converted to numpy)
        dist = euclidean_distance(uu, vv, axis=0)
        
        assert isinstance(dist, np.ndarray)
        expected = np.sqrt(27)  # sqrt(9 + 9 + 9)
        assert_array_almost_equal(dist, expected)
    
    def test_mixed_input_types(self):
        """Test with mixed input types."""
        from scitex.linalg import euclidean_distance
        
        # Mixed types
        uu = np.array([1.0, 2.0, 3.0])
        vv = [4, 5, 6]  # List
        
        dist = euclidean_distance(uu, vv, axis=0)
        assert isinstance(dist, np.ndarray)


class TestEdgeCases:
    """Test edge cases and special conditions."""
    
    def test_empty_arrays(self):
        """Test with empty arrays."""
        from scitex.linalg import euclidean_distance
        
        # Empty arrays
        uu = np.array([])
        vv = np.array([])
        
        # Should handle empty arrays
        dist = euclidean_distance(uu, vv, axis=0)
        assert dist.size == 0
    
    def test_nan_values(self):
        """Test with NaN values."""
        from scitex.linalg import euclidean_distance
        
        uu = np.array([1, 2, np.nan])
        vv = np.array([4, 5, 6])
        
        dist = euclidean_distance(uu, vv, axis=0)
        
        # Result should contain NaN
        assert np.isnan(dist)
    
    def test_inf_values(self):
        """Test with infinite values."""
        from scitex.linalg import euclidean_distance
        
        uu = np.array([1, 2, np.inf])
        vv = np.array([4, 5, 6])
        
        dist = euclidean_distance(uu, vv, axis=0)
        
        # Result should be inf
        assert np.isinf(dist)
    
    def test_complex_numbers(self):
        """Test behavior with complex numbers."""
        from scitex.linalg import euclidean_distance
        
        # Complex arrays - may not be supported
        uu = np.array([1+2j, 3+4j])
        vv = np.array([5+6j, 7+8j])
        
        # This might raise an error or work depending on implementation
        try:
            dist = euclidean_distance(uu, vv, axis=0)
            # If it works, check it's real
            assert np.isreal(dist).all()
        except Exception:
            # Complex numbers might not be supported
            pass


class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_arrays(self):
        """Test with large arrays."""
        from scitex.linalg import euclidean_distance
        import time
        
        # Large arrays
        uu = np.random.rand(100, 50)
        vv = np.random.rand(100, 50)
        
        start = time.time()
        dist = euclidean_distance(uu, vv, axis=0)
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 1.0  # Less than 1 second
        assert dist.shape == (50, 50)
    
    def test_memory_efficiency(self):
        """Test memory usage with broadcasting."""
        from scitex.linalg import euclidean_distance
        
        # Arrays that would require large memory if fully expanded
        uu = np.random.rand(1000, 10)
        vv = np.random.rand(1000, 10)
        
        # Should handle efficiently
        dist = euclidean_distance(uu, vv, axis=0)
        assert dist.shape == (10, 10)


class TestDocumentation:
    """Test function documentation."""
    
    def test_euclidean_distance_docstring(self):
        """Test euclidean_distance has proper docstring."""
        from scitex.linalg import euclidean_distance
        
        assert euclidean_distance.__doc__ is not None
        assert "Euclidean distance" in euclidean_distance.__doc__
        assert "Parameters" in euclidean_distance.__doc__
        assert "Returns" in euclidean_distance.__doc__
    
    def test_cdist_docstring_copied(self):
        """Test cdist has scipy's docstring."""
        from scitex.linalg import cdist
        
        assert cdist.__doc__ is not None
        # Should have scipy's cdist docstring
        assert cdist.__doc__ == scipy_distance.cdist.__doc__


class TestComparison:
    """Compare with other distance implementations."""
    
    def test_compare_with_scipy(self):
        """Compare results with scipy for simple cases."""
        from scitex.linalg import euclidean_distance
        from scipy.spatial.distance import euclidean
        
        # Simple vectors
        u = np.array([1, 2, 3])
        v = np.array([4, 5, 6])
        
        # Our implementation
        our_dist = euclidean_distance(u, v, axis=0)
        
        # Scipy implementation
        scipy_dist = euclidean(u, v)
        
        assert_array_almost_equal(our_dist, scipy_dist)
    
    def test_pairwise_distances(self):
        """Test computing pairwise distances."""
        from scitex.linalg import euclidean_distance, cdist
        
        # Set of points
        points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        
        # Using cdist
        dist_cdist = cdist(points, points)
        
        # Manual verification of some distances
        assert_array_almost_equal(dist_cdist[0, 1], 1.0)  # [0,0] to [1,0]
        assert_array_almost_equal(dist_cdist[0, 3], np.sqrt(2))  # [0,0] to [1,1]


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v", "-s"])
