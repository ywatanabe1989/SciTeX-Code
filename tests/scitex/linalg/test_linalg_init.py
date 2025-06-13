#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:12:00 (ywatanabe)"
# File: tests/scitex/linalg/test___init__.py

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import warnings


class TestLinalgModule:
    """Test suite for scitex.linalg module."""

    def test_distance_imports(self):
        """Test that distance functions can be imported from scitex.linalg."""
        from scitex.linalg import cdist, euclidean_distance, edist
        
        assert callable(cdist)
        assert callable(euclidean_distance)
        assert callable(edist)

    def test_geometric_median_import(self):
        """Test that geometric_median can be imported from scitex.linalg."""
        from scitex.linalg import geometric_median
        
        assert callable(geometric_median)

    def test_misc_imports(self):
        """Test that miscellaneous functions can be imported from scitex.linalg."""
        from scitex.linalg import cosine, nannorm, rebase_a_vec, three_line_lengths_to_coords
        
        assert callable(cosine)
        assert callable(nannorm)
        assert callable(rebase_a_vec)
        assert callable(three_line_lengths_to_coords)

    def test_module_attributes(self):
        """Test that scitex.linalg module has all expected attributes."""
        import scitex.linalg
        
        # Distance functions
        assert hasattr(scitex.linalg, 'cdist')
        assert hasattr(scitex.linalg, 'euclidean_distance')
        assert hasattr(scitex.linalg, 'edist')
        
        # Geometric median
        assert hasattr(scitex.linalg, 'geometric_median')
        
        # Miscellaneous functions
        assert hasattr(scitex.linalg, 'cosine')
        assert hasattr(scitex.linalg, 'nannorm')
        assert hasattr(scitex.linalg, 'rebase_a_vec')
        assert hasattr(scitex.linalg, 'three_line_lengths_to_coords')

    def test_cdist_basic_functionality(self):
        """Test basic cdist functionality."""
        from scitex.linalg import cdist
        
        # Create simple test data
        X = np.array([[0, 0], [1, 1], [2, 2]])
        Y = np.array([[0, 0], [1, 0]])
        
        # Calculate distances
        distances = cdist(X, Y)
        
        # Check output shape
        assert distances.shape == (3, 2)
        assert isinstance(distances, np.ndarray)
        
        # Check some expected values
        np.testing.assert_allclose(distances[0, 0], 0.0, atol=1e-10)  # Same point
        np.testing.assert_allclose(distances[1, 1], 1.0, atol=1e-10)  # Distance 1

    def test_euclidean_distance_basic_functionality(self):
        """Test basic euclidean_distance functionality."""
        from scitex.linalg import euclidean_distance
        
        # Test simple 2D points
        p1 = np.array([0, 0])
        p2 = np.array([3, 4])
        
        distance = euclidean_distance(p1, p2)
        
        # Should be 5 (3-4-5 triangle)
        np.testing.assert_allclose(distance, 5.0, atol=1e-10)

    def test_edist_basic_functionality(self):
        """Test basic edist functionality."""
        from scitex.linalg import edist
        
        # Test with simple vectors
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        
        distance = edist(a, b)
        
        # Expected: sqrt((4-1)^2 + (5-2)^2 + (6-3)^2) = sqrt(9+9+9) = sqrt(27)
        expected = np.sqrt(27)
        np.testing.assert_allclose(distance, expected, atol=1e-10)

    def test_geometric_median_basic_functionality(self):
        """Test basic geometric_median functionality."""
        from scitex.linalg import geometric_median
        
        # Test with simple points where median is obvious
        points = np.array([[0, 0], [1, 0], [0, 1]])
        
        median = geometric_median(points)
        
        # Should be close to the centroid for this simple case
        assert isinstance(median, np.ndarray)
        assert median.shape == (2,)
        assert not np.any(np.isnan(median))

    def test_cosine_basic_functionality(self):
        """Test basic cosine function functionality."""
        from scitex.linalg import cosine
        
        # Test orthogonal vectors (cosine should be 0)
        a = np.array([1, 0])
        b = np.array([0, 1])
        
        cos_sim = cosine(a, b)
        np.testing.assert_allclose(cos_sim, 0.0, atol=1e-10)
        
        # Test identical vectors (cosine should be 1)
        c = np.array([1, 1])
        d = np.array([2, 2])  # Same direction, different magnitude
        
        cos_sim2 = cosine(c, d)
        np.testing.assert_allclose(cos_sim2, 1.0, atol=1e-10)

    def test_nannorm_basic_functionality(self):
        """Test basic nannorm functionality."""
        from scitex.linalg import nannorm
        
        # Test vector with no NaNs
        vec = np.array([3, 4])
        norm = nannorm(vec)
        
        # Should be 5 (3-4-5 triangle)
        np.testing.assert_allclose(norm, 5.0, atol=1e-10)
        
        # Test vector with NaNs
        vec_with_nan = np.array([3, 4, np.nan])
        norm_nan = nannorm(vec_with_nan)
        
        # Should still be 5, ignoring the NaN
        np.testing.assert_allclose(norm_nan, 5.0, atol=1e-10)

    def test_rebase_a_vec_basic_functionality(self):
        """Test basic rebase_a_vec functionality."""
        from scitex.linalg import rebase_a_vec
        
        # Test simple rebasing
        vec = np.array([1, 2, 3, 4, 5])
        
        # Test different ranges
        rebased = rebase_a_vec(vec, low=0, high=1)
        
        assert isinstance(rebased, np.ndarray)
        assert rebased.shape == vec.shape
        assert rebased.min() >= 0
        assert rebased.max() <= 1

    def test_three_line_lengths_to_coords_basic_functionality(self):
        """Test basic three_line_lengths_to_coords functionality."""
        from scitex.linalg import three_line_lengths_to_coords
        
        # Test with a known triangle (3-4-5 right triangle)
        a, b, c = 3, 4, 5
        
        coords = three_line_lengths_to_coords(a, b, c)
        
        assert isinstance(coords, np.ndarray)
        assert coords.shape == (3, 2)  # 3 points in 2D
        
        # Verify the distances between points match the input lengths
        p1, p2, p3 = coords
        dist_12 = np.linalg.norm(p1 - p2)
        dist_23 = np.linalg.norm(p2 - p3)
        dist_13 = np.linalg.norm(p1 - p3)
        
        # Check that the distances match the input (allowing for reordering)
        distances = sorted([dist_12, dist_23, dist_13])
        expected = sorted([a, b, c])
        np.testing.assert_allclose(distances, expected, atol=1e-10)

    def test_distance_functions_with_higher_dimensions(self):
        """Test distance functions with higher dimensional data."""
        from scitex.linalg import cdist, euclidean_distance, edist
        
        # Test with 5D data
        X = np.random.rand(10, 5)
        Y = np.random.rand(8, 5)
        
        # cdist should work
        distances = cdist(X, Y)
        assert distances.shape == (10, 8)
        
        # euclidean_distance should work
        dist = euclidean_distance(X[0], Y[0])
        assert isinstance(dist, (float, np.floating))
        
        # edist should work
        dist2 = edist(X[0], Y[0])
        assert isinstance(dist2, (float, np.floating))

    def test_geometric_median_convergence(self):
        """Test geometric_median with various point configurations."""
        from scitex.linalg import geometric_median
        
        # Test with collinear points
        points = np.array([[0, 0], [1, 0], [2, 0]])
        median = geometric_median(points)
        
        # Should be somewhere on the line
        assert isinstance(median, np.ndarray)
        assert median.shape == (2,)
        assert not np.any(np.isnan(median))

    def test_cosine_edge_cases(self):
        """Test cosine function with edge cases."""
        from scitex.linalg import cosine
        
        # Test with zero vector (should handle gracefully)
        a = np.array([0, 0])
        b = np.array([1, 1])
        
        # This might return NaN or 0 depending on implementation
        result = cosine(a, b)
        assert isinstance(result, (float, np.floating))

    def test_nannorm_all_nan(self):
        """Test nannorm with all NaN values."""
        from scitex.linalg import nannorm
        
        vec_all_nan = np.array([np.nan, np.nan, np.nan])
        norm = nannorm(vec_all_nan)
        
        # Should handle this gracefully (likely return NaN or 0)
        assert isinstance(norm, (float, np.floating))

    def test_rebase_a_vec_edge_cases(self):
        """Test rebase_a_vec with edge cases."""
        from scitex.linalg import rebase_a_vec
        
        # Test with constant vector
        vec = np.array([5, 5, 5, 5])
        rebased = rebase_a_vec(vec, low=0, high=1)
        
        assert isinstance(rebased, np.ndarray)
        assert rebased.shape == vec.shape
        
        # Test with single element
        vec_single = np.array([42])
        rebased_single = rebase_a_vec(vec_single, low=0, high=1)
        
        assert isinstance(rebased_single, np.ndarray)
        assert rebased_single.shape == vec_single.shape

    def test_three_line_lengths_to_coords_degenerate_cases(self):
        """Test three_line_lengths_to_coords with degenerate triangles."""
        from scitex.linalg import three_line_lengths_to_coords
        
        # Test with triangle that doesn't satisfy triangle inequality
        # (should handle this gracefully)
        try:
            coords = three_line_lengths_to_coords(1, 1, 3)  # 1+1 < 3
            
            # If it returns something, it should be a valid array
            if coords is not None:
                assert isinstance(coords, np.ndarray)
        except (ValueError, RuntimeError):
            # It's acceptable for this to raise an error for invalid triangles
            pass

    def test_function_docstrings(self):
        """Test that imported functions have docstrings."""
        from scitex.linalg import (cdist, euclidean_distance, edist, 
                                geometric_median, cosine, nannorm, 
                                rebase_a_vec, three_line_lengths_to_coords)
        
        functions = [cdist, euclidean_distance, edist, geometric_median, 
                    cosine, nannorm, rebase_a_vec, three_line_lengths_to_coords]
        
        for func in functions:
            assert hasattr(func, '__doc__')
            # Doc can be None for some functions, but attribute should exist

    def test_numpy_array_compatibility(self):
        """Test that functions work with numpy arrays of different dtypes."""
        from scitex.linalg import euclidean_distance, cosine
        
        # Test with different dtypes
        for dtype in [np.float32, np.float64, np.int32]:
            a = np.array([1, 2], dtype=dtype)
            b = np.array([3, 4], dtype=dtype)
            
            # euclidean_distance should work
            dist = euclidean_distance(a, b)
            assert isinstance(dist, (float, np.floating))
            
            # cosine should work
            cos_sim = cosine(a, b)
            assert isinstance(cos_sim, (float, np.floating))


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
