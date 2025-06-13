#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 19:08:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/linalg/test__misc_comprehensive.py

"""Comprehensive tests for miscellaneous linear algebra functions."""

import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import sympy
from scipy.linalg import norm


class TestCosineFunction:
    """Test cases for cosine similarity function."""
    
    def test_import(self):
        """Test that cosine function can be imported."""
from scitex.linalg import cosine
        assert callable(cosine)
    
    def test_orthogonal_vectors(self):
        """Test cosine of orthogonal vectors."""
from scitex.linalg import cosine
        
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        
        result = cosine(v1, v2)
        assert np.isclose(result, 0.0)
    
    def test_parallel_vectors(self):
        """Test cosine of parallel vectors."""
from scitex.linalg import cosine
        
        v1 = np.array([1, 2, 3])
        v2 = np.array([2, 4, 6])  # Same direction, different magnitude
        
        result = cosine(v1, v2)
        assert np.isclose(result, 1.0)
    
    def test_opposite_vectors(self):
        """Test cosine of opposite vectors."""
from scitex.linalg import cosine
        
        v1 = np.array([1, 2, 3])
        v2 = np.array([-1, -2, -3])
        
        result = cosine(v1, v2)
        assert np.isclose(result, -1.0)
    
    def test_arbitrary_angle(self):
        """Test cosine of vectors at 45 degrees."""
from scitex.linalg import cosine
        
        v1 = np.array([1, 0])
        v2 = np.array([1, 1])  # 45 degrees from v1
        
        result = cosine(v1, v2)
        expected = 1 / np.sqrt(2)  # cos(45°)
        assert np.isclose(result, expected)
    
    def test_nan_handling_first_vector(self):
        """Test NaN handling in first vector."""
from scitex.linalg import cosine
        
        v1 = np.array([1, np.nan, 3])
        v2 = np.array([4, 5, 6])
        
        result = cosine(v1, v2)
        assert np.isnan(result)
    
    def test_nan_handling_second_vector(self):
        """Test NaN handling in second vector."""
from scitex.linalg import cosine
        
        v1 = np.array([1, 2, 3])
        v2 = np.array([4, np.nan, 6])
        
        result = cosine(v1, v2)
        assert np.isnan(result)
    
    def test_nan_handling_both_vectors(self):
        """Test NaN handling in both vectors."""
from scitex.linalg import cosine
        
        v1 = np.array([np.nan, 2, 3])
        v2 = np.array([4, np.nan, 6])
        
        result = cosine(v1, v2)
        assert np.isnan(result)
    
    def test_zero_vector(self):
        """Test cosine with zero vector."""
from scitex.linalg import cosine
        
        v1 = np.array([0, 0, 0])
        v2 = np.array([1, 2, 3])
        
        # Should handle division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            result = cosine(v1, v2)
            assert np.isnan(result) or np.isinf(result)
    
    def test_unit_vectors(self):
        """Test cosine with unit vectors."""
from scitex.linalg import cosine
        
        v1 = np.array([1, 0, 0])
        v2 = np.array([0.6, 0.8, 0])  # 3-4-5 triangle
        
        result = cosine(v1, v2)
        assert np.isclose(result, 0.6)
    
    def test_high_dimensional_vectors(self):
        """Test cosine with high-dimensional vectors."""
from scitex.linalg import cosine
        
        np.random.seed(42)
        v1 = np.random.randn(100)
        v2 = np.random.randn(100)
        
        result = cosine(v1, v2)
        assert -1 <= result <= 1  # Cosine similarity bounds


class TestNannormFunction:
    """Test cases for nannorm function."""
    
    def test_import(self):
        """Test that nannorm function can be imported."""
from scitex.linalg import nannorm
        assert callable(nannorm)
    
    def test_basic_norm(self):
        """Test basic norm calculation without NaN."""
from scitex.linalg import nannorm
        
        v = np.array([3, 4])
        result = nannorm(v)
        assert np.isclose(result, 5.0)  # 3-4-5 triangle
    
    def test_with_nan(self):
        """Test norm calculation with NaN values."""
from scitex.linalg import nannorm
        
        v = np.array([3, np.nan, 4])
        result = nannorm(v)
        assert np.isnan(result)
    
    def test_zero_vector(self):
        """Test norm of zero vector."""
from scitex.linalg import nannorm
        
        v = np.array([0, 0, 0])
        result = nannorm(v)
        assert np.isclose(result, 0.0)
    
    def test_unit_vector(self):
        """Test norm of unit vector."""
from scitex.linalg import nannorm
        
        v = np.array([1, 0, 0])
        result = nannorm(v)
        assert np.isclose(result, 1.0)
    
    def test_negative_values(self):
        """Test norm with negative values."""
from scitex.linalg import nannorm
        
        v = np.array([-3, -4])
        result = nannorm(v)
        assert np.isclose(result, 5.0)
    
    def test_axis_parameter(self):
        """Test norm calculation along different axes."""
from scitex.linalg import nannorm
        
        # 2D array
        v = np.array([[3, 4], [5, 12], [8, 15]])
        
        # Norm along axis 1 (row-wise)
        result = nannorm(v, axis=1)
        expected = np.array([5, 13, 17])
        np.testing.assert_array_almost_equal(result, expected)
        
        # Norm along axis 0 (column-wise)
        result = nannorm(v, axis=0)
        expected = norm(v, axis=0)
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_multidimensional_array(self):
        """Test norm with multidimensional arrays."""
from scitex.linalg import nannorm
        
        v = np.random.randn(3, 4, 5)
        
        # Test different axes
        for axis in [0, 1, 2, -1]:
            result = nannorm(v, axis=axis)
            expected_shape = list(v.shape)
            expected_shape.pop(axis if axis >= 0 else len(expected_shape) + axis)
            assert result.shape == tuple(expected_shape)
    
    def test_partial_nan_array(self):
        """Test with array containing some NaN values."""
from scitex.linalg import nannorm
        
        v = np.array([[1, 2], [np.nan, 4], [5, 6]])
        
        # Any NaN should make result NaN
        result = nannorm(v, axis=1)
        assert not np.isnan(result[0])
        assert np.isnan(result[1])
        assert not np.isnan(result[2])


class TestRebaseAVecFunction:
    """Test cases for rebase_a_vec function."""
    
    def test_import(self):
        """Test that rebase_a_vec function can be imported."""
from scitex.linalg import rebase_a_vec
        assert callable(rebase_a_vec)
    
    def test_projection_onto_x_axis(self):
        """Test projection onto x-axis."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([3, 4])
        v_base = np.array([1, 0])  # x-axis
        
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 3.0)  # x-component
    
    def test_projection_onto_y_axis(self):
        """Test projection onto y-axis."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([3, 4])
        v_base = np.array([0, 1])  # y-axis
        
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 4.0)  # y-component
    
    def test_projection_onto_diagonal(self):
        """Test projection onto diagonal vector."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([2, 2])
        v_base = np.array([1, 1])
        
        # Projection length should be 2*sqrt(2)
        result = rebase_a_vec(v, v_base)
        expected = 2 * np.sqrt(2)
        assert np.isclose(result, expected)
    
    def test_opposite_direction_projection(self):
        """Test projection in opposite direction."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 1])
        v_base = np.array([-1, -1])
        
        result = rebase_a_vec(v, v_base)
        assert result < 0  # Negative due to opposite direction
    
    def test_orthogonal_vectors_projection(self):
        """Test projection of orthogonal vectors."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 0])
        v_base = np.array([0, 1])
        
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 0.0)
    
    def test_nan_in_vector(self):
        """Test with NaN in vector."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([np.nan, 2])
        v_base = np.array([1, 0])
        
        result = rebase_a_vec(v, v_base)
        assert np.isnan(result)
    
    def test_nan_in_base(self):
        """Test with NaN in base vector."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 2])
        v_base = np.array([np.nan, 0])
        
        result = rebase_a_vec(v, v_base)
        assert np.isnan(result)
    
    def test_zero_base_vector(self):
        """Test with zero base vector."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 2])
        v_base = np.array([0, 0])
        
        with np.errstate(divide='ignore', invalid='ignore'):
            result = rebase_a_vec(v, v_base)
            assert np.isnan(result) or np.isinf(result)
    
    def test_3d_vectors(self):
        """Test with 3D vectors."""
from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 2, 3])
        v_base = np.array([1, 0, 0])
        
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 1.0)  # x-component


class TestThreeLineLengthsToCoords:
    """Test cases for three_line_lengths_to_coords function."""
    
    def test_import(self):
        """Test that function can be imported."""
from scitex.linalg import three_line_lengths_to_coords
        assert callable(three_line_lengths_to_coords)
    
    def test_right_triangle(self):
        """Test with right triangle (3-4-5)."""
from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(3, 4, 5)
        
        # Check coordinates
        assert O == (0, 0, 0)
        assert A == (3, 0, 0)
        
        # Check that B forms right triangle
        # Distance OB should be 4
        ob_dist = np.sqrt(B[0]**2 + B[1]**2)
        assert np.isclose(ob_dist, 4)
        
        # Distance AB should be 5
        ab_dist = np.sqrt((B[0] - A[0])**2 + B[1]**2)
        assert np.isclose(ab_dist, 5)
    
    def test_equilateral_triangle(self):
        """Test with equilateral triangle."""
from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(1, 1, 1)
        
        assert O == (0, 0, 0)
        assert A == (1, 0, 0)
        
        # B should have x=0.5, y=sqrt(3)/2 for equilateral
        assert np.isclose(B[0], 0.5)
        assert np.isclose(B[1], np.sqrt(3)/2)
        assert B[2] == 0
    
    def test_isosceles_triangle(self):
        """Test with isosceles triangle."""
from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(2, 2, 2)
        
        # Should be scaled version of equilateral
        assert O == (0, 0, 0)
        assert A == (2, 0, 0)
        assert np.isclose(B[0], 1.0)
        assert B[1] > 0  # Positive y-coordinate
    
    def test_degenerate_triangle(self):
        """Test with degenerate triangle (straight line)."""
from scitex.linalg import three_line_lengths_to_coords
        
        # Triangle inequality violated
        with pytest.raises((ValueError, ZeroDivisionError)):
            O, A, B = three_line_lengths_to_coords(1, 2, 3)
    
    def test_example_from_docstring(self):
        """Test the example from function docstring."""
from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(2, np.sqrt(3), 1)
        
        assert O == (0, 0, 0)
        assert A == (2, 0, 0)
        
        # Verify triangle sides
        oa = np.sqrt(A[0]**2 + A[1]**2 + A[2]**2)
        ob = np.sqrt(B[0]**2 + B[1]**2 + B[2]**2)
        ab = np.sqrt((B[0]-A[0])**2 + (B[1]-A[1])**2 + (B[2]-A[2])**2)
        
        assert np.isclose(oa, 2)
        assert np.isclose(ob, np.sqrt(3))
        assert np.isclose(ab, 1)
    
    def test_all_points_in_xy_plane(self):
        """Test that all points are in xy-plane (z=0)."""
from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(5, 6, 7)
        
        assert O[2] == 0
        assert A[2] == 0
        assert B[2] == 0
    
    def test_scalene_triangle(self):
        """Test with scalene triangle."""
from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(3, 5, 7)
        
        # Verify all distances
        oa = np.sqrt(sum(x**2 for x in A))
        ob = np.sqrt(sum(x**2 for x in B))
        ab = np.sqrt(sum((B[i]-A[i])**2 for i in range(3)))
        
        assert np.isclose(oa, 3)
        assert np.isclose(ob, 5)
        assert np.isclose(ab, 7)


class TestEdgeCasesAndIntegration:
    """Test edge cases and integration between functions."""
    
    def test_cosine_with_rebase(self):
        """Test using cosine in rebase_a_vec calculation."""
from scitex.linalg import cosine, rebase_a_vec
        
        v = np.array([3, 4])
        v_base = np.array([1, 0])
        
        # Manual calculation
        cos_angle = cosine(v, v_base)
        expected = norm(v) * cos_angle
        
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, expected)
    
    def test_nannorm_edge_cases(self):
        """Test nannorm with various edge cases."""
from scitex.linalg import nannorm
        
        # Empty array
        with pytest.raises(ValueError):
            nannorm(np.array([]))
        
        # Single element
        result = nannorm(np.array([5]))
        assert np.isclose(result, 5.0)
        
        # All NaN
        result = nannorm(np.array([np.nan, np.nan]))
        assert np.isnan(result)
    
    def test_vector_operations_consistency(self):
        """Test consistency between vector operations."""
from scitex.linalg import cosine, nannorm, rebase_a_vec
        
        # Create test vectors
        v1 = np.array([1, 0, 0])
        v2 = np.array([1, 1, 0])
        
        # Test relationships
        cos_val = cosine(v1, v2)
        norm_v1 = nannorm(v1)
        norm_v2 = nannorm(v2)
        
        # Cauchy-Schwarz inequality: |cos| <= 1
        assert abs(cos_val) <= 1.0
        
        # Dot product formula
        dot_product = cos_val * norm_v1 * norm_v2
        assert np.isclose(dot_product, np.dot(v1, v2))
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
from scitex.linalg import cosine, nannorm
        
        # Very small values
        v_small = np.array([1e-10, 1e-10])
        result = nannorm(v_small)
        assert result > 0  # Should not underflow to zero
        
        # Very large values
        v_large = np.array([1e10, 1e10])
        result = nannorm(v_large)
        assert not np.isinf(result)  # Should not overflow
        
        # Mixed scales
        v1 = np.array([1e-5, 1e-5])
        v2 = np.array([1e5, 1e5])
        cos_result = cosine(v1, v2)
        assert np.isclose(cos_result, 1.0)  # Parallel vectors


class TestPerformance:
    """Test performance aspects of the functions."""
    
    def test_large_vector_cosine(self):
        """Test cosine with large vectors."""
from scitex.linalg import cosine
        
        np.random.seed(42)
        v1 = np.random.randn(10000)
        v2 = np.random.randn(10000)
        
        result = cosine(v1, v2)
        assert -1 <= result <= 1
    
    def test_batch_nannorm(self):
        """Test nannorm with batch processing."""
from scitex.linalg import nannorm
        
        # Large batch of vectors
        vectors = np.random.randn(1000, 100)
        
        # Compute norms along axis 1
        results = nannorm(vectors, axis=1)
        assert results.shape == (1000,)
        assert np.all(results >= 0)  # All norms non-negative
    
    def test_repeated_calculations(self):
        """Test repeated calculations for consistency."""
from scitex.linalg import three_line_lengths_to_coords
        
        # Same input should give same output
        results = []
        for _ in range(10):
            O, A, B = three_line_lengths_to_coords(3, 4, 5)
            results.append((O, A, B))
        
        # All results should be identical
        for i in range(1, 10):
            assert results[i] == results[0]


class TestDocumentation:
    """Test documentation and examples."""
    
    def test_production_vector_example(self):
        """Test the production_vector example from comments."""
from scitex.linalg import rebase_a_vec
        
        # From the comment: production_vector(np.array([3,4]), np.array([10,0])) # np.array([3, 0])
        v = np.array([3, 4])
        v_base = np.array([10, 0])
        
        result = rebase_a_vec(v, v_base)
        # The projection of [3,4] onto [10,0] (x-axis) should give magnitude 3
        assert np.isclose(result, 3.0)
    
    def test_function_signatures(self):
        """Test that functions have expected signatures."""
from scitex.linalg import cosine, nannorm, rebase_a_vec, three_line_lengths_to_coords
        import inspect
        
        # Check cosine
        sig = inspect.signature(cosine)
        assert len(sig.parameters) == 2
        
        # Check nannorm
        sig = inspect.signature(nannorm)
        params = list(sig.parameters.keys())
        assert 'v' in params
        assert 'axis' in params
        
        # Check rebase_a_vec
        sig = inspect.signature(rebase_a_vec)
        assert len(sig.parameters) == 2
        
        # Check three_line_lengths_to_coords
        sig = inspect.signature(three_line_lengths_to_coords)
        assert len(sig.parameters) == 3


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])