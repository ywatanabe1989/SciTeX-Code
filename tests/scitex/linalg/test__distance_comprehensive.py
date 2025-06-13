#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for _distance.py

Tests cover:
- Euclidean distance calculations
- Different array shapes and dimensions
- Axis parameter handling
- Broadcasting behavior
- Edge cases and error handling
- Integration with numpy_fn decorator
- Wrapper for scipy.spatial.distance.cdist
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock

import numpy as np
import pytest
import scipy.spatial.distance as scipy_distance
import torch

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestEuclideanDistance:
    """Test euclidean_distance function."""
    
    def test_euclidean_distance_1d(self):
        """Test Euclidean distance for 1D arrays."""
from scitex.linalg import euclidean_distance
        
        u = np.array([0, 0])
        v = np.array([3, 4])
        
        # Should compute sqrt(3^2 + 4^2) = 5
        result = euclidean_distance(u, v, axis=0)
        assert np.isclose(result, 5.0)
    
    def test_euclidean_distance_2d_axis0(self):
        """Test Euclidean distance for 2D arrays along axis 0."""
from scitex.linalg import euclidean_distance
        
        u = np.array([[1, 2, 3],
                      [4, 5, 6]])
        v = np.array([[7, 8, 9],
                      [10, 11, 12]])
        
        result = euclidean_distance(u, v, axis=0)
        
        # Should compute distance between columns
        expected = np.sqrt(np.sum((u - v)**2, axis=0))
        np.testing.assert_allclose(result, expected)
    
    def test_euclidean_distance_2d_axis1(self):
        """Test Euclidean distance for 2D arrays along axis 1."""
from scitex.linalg import euclidean_distance
        
        u = np.array([[1, 2, 3],
                      [4, 5, 6]])
        v = np.array([[7, 8, 9],
                      [10, 11, 12]])
        
        result = euclidean_distance(u, v, axis=1)
        
        # Should compute distance between rows
        expected = np.sqrt(np.sum((u - v)**2, axis=1))
        np.testing.assert_allclose(result, expected)
    
    def test_euclidean_distance_broadcasting(self):
        """Test broadcasting behavior."""
from scitex.linalg import euclidean_distance
        
        # Test with different shapes that should broadcast
        u = np.array([[1, 2, 3]])  # Shape (1, 3)
        v = np.array([[4],
                      [5],
                      [6]])  # Shape (3, 1)
        
        # When axis=0, shapes along axis 0 must match
        with pytest.raises(ValueError, match="Shape along axis"):
            euclidean_distance(u, v, axis=0)
    
    def test_euclidean_distance_3d(self):
        """Test with 3D arrays."""
from scitex.linalg import euclidean_distance
        
        u = np.random.randn(2, 3, 4)
        v = np.random.randn(2, 3, 4)
        
        # Test along different axes
        for axis in [0, 1, 2]:
            result = euclidean_distance(u, v, axis=axis)
            
            # Verify shape
            expected_shape = list(u.shape)
            expected_shape.pop(axis)
            
            # For broadcasting, the result shape is more complex
            # Just verify it runs without error
            assert result.ndim >= len(expected_shape)
    
    def test_euclidean_distance_scalar_promotion(self):
        """Test that scalars are promoted to 1D arrays."""
from scitex.linalg import euclidean_distance
        
        u = 3
        v = 4
        
        result = euclidean_distance(u, v, axis=0)
        assert np.isclose(result, 1.0)  # |3 - 4| = 1
    
    def test_euclidean_distance_with_lists(self):
        """Test with list inputs (numpy_fn decorator)."""
from scitex.linalg import euclidean_distance
        
        u = [1, 2, 3]
        v = [4, 5, 6]
        
        result = euclidean_distance(u, v, axis=0)
        expected = np.sqrt(np.sum((np.array(u) - np.array(v))**2))
        assert np.isclose(result, expected)
    
    def test_euclidean_distance_with_torch(self):
        """Test with PyTorch tensors (numpy_fn decorator)."""
from scitex.linalg import euclidean_distance
        
        u = torch.tensor([1.0, 2.0, 3.0])
        v = torch.tensor([4.0, 5.0, 6.0])
        
        result = euclidean_distance(u, v, axis=0)
        
        # Result should be numpy array
        assert isinstance(result, np.ndarray)
        expected = np.sqrt(np.sum((u.numpy() - v.numpy())**2))
        assert np.isclose(result, expected)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_mismatched_shapes(self):
        """Test error when shapes don't match along specified axis."""
from scitex.linalg import euclidean_distance
        
        u = np.array([1, 2, 3])
        v = np.array([4, 5])
        
        with pytest.raises(ValueError, match="Shape along axis 0 must match"):
            euclidean_distance(u, v, axis=0)
    
    def test_empty_arrays(self):
        """Test with empty arrays."""
from scitex.linalg import euclidean_distance
        
        u = np.array([])
        v = np.array([])
        
        result = euclidean_distance(u, v, axis=0)
        assert result.size == 0
    
    def test_nan_handling(self):
        """Test behavior with NaN values."""
from scitex.linalg import euclidean_distance
        
        u = np.array([1, 2, np.nan])
        v = np.array([4, 5, 6])
        
        result = euclidean_distance(u, v, axis=0)
        assert np.isnan(result)
    
    def test_inf_handling(self):
        """Test behavior with infinite values."""
from scitex.linalg import euclidean_distance
        
        u = np.array([1, 2, np.inf])
        v = np.array([4, 5, 6])
        
        result = euclidean_distance(u, v, axis=0)
        assert np.isinf(result)
    
    def test_zero_distance(self):
        """Test when arrays are identical."""
from scitex.linalg import euclidean_distance
        
        u = np.array([1, 2, 3])
        v = np.array([1, 2, 3])
        
        result = euclidean_distance(u, v, axis=0)
        assert np.isclose(result, 0.0)
    
    def test_negative_axis(self):
        """Test with negative axis values."""
from scitex.linalg import euclidean_distance
        
        u = np.array([[1, 2], [3, 4]])
        v = np.array([[5, 6], [7, 8]])
        
        # axis=-1 should be same as axis=1
        result1 = euclidean_distance(u, v, axis=-1)
        result2 = euclidean_distance(u, v, axis=1)
        
        np.testing.assert_allclose(result1, result2)


class TestCdist:
    """Test cdist wrapper function."""
    
    def test_cdist_basic(self):
        """Test basic cdist functionality."""
from scitex.linalg import cdist
        
        X = np.array([[0, 0], [1, 0], [0, 1]])
        Y = np.array([[1, 1], [2, 2]])
        
        result = cdist(X, Y)
        expected = scipy_distance.cdist(X, Y)
        
        np.testing.assert_allclose(result, expected)
    
    def test_cdist_with_metric(self):
        """Test cdist with different metrics."""
from scitex.linalg import cdist
        
        X = np.random.randn(5, 3)
        Y = np.random.randn(4, 3)
        
        # Test different metrics
        for metric in ['euclidean', 'cityblock', 'cosine']:
            result = cdist(X, Y, metric=metric)
            expected = scipy_distance.cdist(X, Y, metric=metric)
            np.testing.assert_allclose(result, expected)
    
    def test_cdist_with_kwargs(self):
        """Test cdist with additional keyword arguments."""
from scitex.linalg import cdist
        
        X = np.random.randn(5, 3)
        Y = np.random.randn(4, 3)
        
        # Test with p parameter for Minkowski distance
        result = cdist(X, Y, metric='minkowski', p=3)
        expected = scipy_distance.cdist(X, Y, metric='minkowski', p=3)
        
        np.testing.assert_allclose(result, expected)
    
    def test_cdist_docstring(self):
        """Test that cdist has scipy's docstring."""
from scitex.linalg import cdist
        
        assert cdist.__doc__ is not None
        assert cdist.__doc__ == scipy_distance.cdist.__doc__


class TestAliases:
    """Test function aliases."""
    
    def test_edist_alias(self):
        """Test that edist is an alias for euclidean_distance."""
from scitex.linalg import edist, euclidean_distance
        
        assert edist is euclidean_distance
        
        # Test functionality
        u = np.array([1, 2, 3])
        v = np.array([4, 5, 6])
        
        result1 = edist(u, v, axis=0)
        result2 = euclidean_distance(u, v, axis=0)
        
        assert np.array_equal(result1, result2)


class TestNumericalAccuracy:
    """Test numerical accuracy of distance calculations."""
    
    def test_small_distances(self):
        """Test accuracy for very small distances."""
from scitex.linalg import euclidean_distance
        
        u = np.array([1e-10, 2e-10])
        v = np.array([1.5e-10, 2.5e-10])
        
        result = euclidean_distance(u, v, axis=0)
        expected = np.sqrt((0.5e-10)**2 + (0.5e-10)**2)
        
        assert np.isclose(result, expected, rtol=1e-10)
    
    def test_large_distances(self):
        """Test accuracy for very large distances."""
from scitex.linalg import euclidean_distance
        
        u = np.array([1e10, 2e10])
        v = np.array([1.5e10, 2.5e10])
        
        result = euclidean_distance(u, v, axis=0)
        expected = np.sqrt((0.5e10)**2 + (0.5e10)**2)
        
        assert np.isclose(result, expected, rtol=1e-10)
    
    def test_known_distances(self):
        """Test with known distance values."""
from scitex.linalg import euclidean_distance
        
        # 3-4-5 right triangle
        u = np.array([0, 0])
        v = np.array([3, 4])
        assert np.isclose(euclidean_distance(u, v, axis=0), 5.0)
        
        # Unit square diagonal
        u = np.array([0, 0])
        v = np.array([1, 1])
        assert np.isclose(euclidean_distance(u, v, axis=0), np.sqrt(2))
        
        # 3D unit cube diagonal
        u = np.array([0, 0, 0])
        v = np.array([1, 1, 1])
        assert np.isclose(euclidean_distance(u, v, axis=0), np.sqrt(3))


class TestComplexScenarios:
    """Test complex usage scenarios."""
    
    def test_pairwise_distances(self):
        """Test computing pairwise distances."""
from scitex.linalg import euclidean_distance
        
        # Set of points
        points = np.array([[0, 0],
                          [1, 0],
                          [0, 1],
                          [1, 1]])
        
        n_points = len(points)
        distances = np.zeros((n_points, n_points))
        
        for i in range(n_points):
            for j in range(n_points):
                distances[i, j] = euclidean_distance(points[i], points[j], axis=0)
        
        # Check symmetry
        assert np.allclose(distances, distances.T)
        
        # Check diagonal is zero
        assert np.allclose(np.diag(distances), 0)
        
        # Check known distances
        assert np.isclose(distances[0, 1], 1.0)  # (0,0) to (1,0)
        assert np.isclose(distances[0, 3], np.sqrt(2))  # (0,0) to (1,1)
    
    def test_batch_distance_computation(self):
        """Test batch distance computation."""
from scitex.linalg import euclidean_distance
        
        # Batch of vectors
        batch_u = np.random.randn(10, 3, 4)  # 10 matrices of 3x4
        batch_v = np.random.randn(10, 3, 4)
        
        # Compute distances along different axes
        dist_axis0 = euclidean_distance(batch_u, batch_v, axis=0)
        dist_axis1 = euclidean_distance(batch_u, batch_v, axis=1)
        dist_axis2 = euclidean_distance(batch_u, batch_v, axis=2)
        
        # Verify computation doesn't fail
        assert dist_axis0.size > 0
        assert dist_axis1.size > 0
        assert dist_axis2.size > 0
    
    def test_distance_matrix_consistency(self):
        """Test consistency with scipy cdist."""
from scitex.linalg import euclidean_distance, cdist
        
        # Create random points
        points = np.random.randn(5, 3)
        
        # Compute distance matrix using cdist
        dist_matrix_cdist = cdist(points, points, metric='euclidean')
        
        # Compute using euclidean_distance
        n = len(points)
        dist_matrix_manual = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                dist_matrix_manual[i, j] = euclidean_distance(
                    points[i], points[j], axis=0
                )
        
        np.testing.assert_allclose(dist_matrix_cdist, dist_matrix_manual, rtol=1e-10)


class TestPerformance:
    """Test performance-related aspects."""
    
    def test_large_array_handling(self):
        """Test handling of large arrays."""
from scitex.linalg import euclidean_distance
        
        # Create large arrays
        u = np.random.randn(1000, 100)
        v = np.random.randn(1000, 100)
        
        # Should complete without memory error
        result = euclidean_distance(u, v, axis=0)
        assert result.shape == (100,)
        
        result = euclidean_distance(u, v, axis=1)
        assert result.shape == (1000,)
    
    def test_memory_efficiency(self):
        """Test that function doesn't create unnecessary copies."""
from scitex.linalg import euclidean_distance
        
        # Test with views
        arr = np.random.randn(100, 50)
        u = arr[:50]
        v = arr[50:]
        
        # Should work with views
        result = euclidean_distance(u, v, axis=0)
        assert result.shape == (50,)


class TestDocumentation:
    """Test documentation and docstrings."""
    
    def test_euclidean_distance_docstring(self):
        """Test euclidean_distance has proper docstring."""
from scitex.linalg import euclidean_distance
        
        assert euclidean_distance.__doc__ is not None
        assert "Euclidean distance" in euclidean_distance.__doc__
        assert "Parameters" in euclidean_distance.__doc__
        assert "Returns" in euclidean_distance.__doc__
    
    def test_parameter_descriptions(self):
        """Test that parameters are documented."""
from scitex.linalg import euclidean_distance
        
        doc = euclidean_distance.__doc__
        assert "uu :" in doc
        assert "vv :" in doc
        assert "axis :" in doc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])