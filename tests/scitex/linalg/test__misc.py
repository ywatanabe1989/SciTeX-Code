#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 04:18:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/linalg/test__misc.py

"""Comprehensive tests for miscellaneous linear algebra functions."""

import pytest
import numpy as np
from scipy.linalg import norm
import sympy
from unittest.mock import patch, MagicMock
import warnings
import math


class TestCosineFunction:
    """Test the cosine similarity function."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        np.random.seed(42)
        
    def test_cosine_basic(self):
        """Test basic cosine similarity calculation."""
        from scitex.linalg import cosine
        
        # Parallel vectors (cosine = 1)
        v1 = np.array([1, 0, 0])
        v2 = np.array([2, 0, 0])
        assert np.isclose(cosine(v1, v2), 1.0)
        
        # Orthogonal vectors (cosine = 0)
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        assert np.isclose(cosine(v1, v2), 0.0)
        
        # Opposite vectors (cosine = -1)
        v1 = np.array([1, 0, 0])
        v2 = np.array([-1, 0, 0])
        assert np.isclose(cosine(v1, v2), -1.0)
        
    def test_cosine_arbitrary_angle(self):
        """Test cosine with arbitrary angles."""
        from scitex.linalg import cosine
        
        # 45 degree angle
        v1 = np.array([1, 0])
        v2 = np.array([1, 1])
        expected = 1 / np.sqrt(2)  # cos(45°)
        assert np.isclose(cosine(v1, v2), expected)
        
        # 60 degree angle
        v1 = np.array([1, 0])
        v2 = np.array([1, np.sqrt(3)])
        expected = 0.5  # cos(60°)
        assert np.isclose(cosine(v1, v2), expected)
        
    def test_cosine_with_nan(self):
        """Test cosine behavior with NaN values."""
        from scitex.linalg import cosine
        
        # NaN in first vector
        v1 = np.array([1, np.nan, 0])
        v2 = np.array([1, 1, 1])
        assert np.isnan(cosine(v1, v2))
        
        # NaN in second vector
        v1 = np.array([1, 1, 1])
        v2 = np.array([1, np.nan, 0])
        assert np.isnan(cosine(v1, v2))
        
        # NaN in both vectors
        v1 = np.array([np.nan, 1, 0])
        v2 = np.array([1, np.nan, 0])
        assert np.isnan(cosine(v1, v2))
        
    def test_cosine_different_dimensions(self):
        """Test cosine with vectors of different lengths."""
        from scitex.linalg import cosine
        
        # 2D vectors
        v1 = np.array([3, 4])
        v2 = np.array([4, 3])
        result = cosine(v1, v2)
        expected = (3*4 + 4*3) / (5 * 5)  # 24/25
        assert np.isclose(result, expected)
        
        # 3D vectors
        v1 = np.array([1, 2, 2])
        v2 = np.array([2, 1, 2])
        result = cosine(v1, v2)
        expected = (1*2 + 2*1 + 2*2) / (3 * 3)  # 8/9
        assert np.isclose(result, expected)
        
    def test_cosine_zero_vector(self):
        """Test cosine with zero vectors."""
        from scitex.linalg import cosine
        
        v1 = np.array([0, 0, 0])
        v2 = np.array([1, 1, 1])
        
        # This will cause division by zero
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = cosine(v1, v2)
            # Result should be NaN or inf
            assert np.isnan(result) or np.isinf(result)
            
    def test_cosine_normalization_invariance(self):
        """Test that cosine is invariant to vector magnitude."""
        from scitex.linalg import cosine
        
        v1 = np.array([1, 2, 3])
        v2 = np.array([4, 5, 6])
        
        # Scale vectors
        v1_scaled = v1 * 10
        v2_scaled = v2 * 0.1
        
        result1 = cosine(v1, v2)
        result2 = cosine(v1_scaled, v2_scaled)
        
        assert np.isclose(result1, result2)


class TestNannormFunction:
    """Test the nannorm function."""
    
    def test_nannorm_basic(self):
        """Test basic norm calculation."""
        from scitex.linalg import nannorm
        
        # Simple vectors
        v = np.array([3, 4])
        assert np.isclose(nannorm(v), 5)
        
        v = np.array([1, 0, 0])
        assert np.isclose(nannorm(v), 1)
        
        v = np.array([1, 1, 1])
        assert np.isclose(nannorm(v), np.sqrt(3))
        
    def test_nannorm_with_nan(self):
        """Test nannorm behavior with NaN values."""
        from scitex.linalg import nannorm
        
        # Vector with NaN
        v = np.array([1, np.nan, 3])
        assert np.isnan(nannorm(v))
        
        # All NaN
        v = np.array([np.nan, np.nan, np.nan])
        assert np.isnan(nannorm(v))
        
    def test_nannorm_multidimensional(self):
        """Test nannorm with multidimensional arrays."""
        from scitex.linalg import nannorm
        
        # 2D array
        v = np.array([[1, 2, 3],
                      [4, 5, 6]])
        
        # Norm along last axis (default)
        result = nannorm(v, axis=-1)
        expected = np.array([np.sqrt(14), np.sqrt(77)])
        np.testing.assert_allclose(result, expected)
        
        # Norm along first axis
        result = nannorm(v, axis=0)
        expected = np.array([np.sqrt(17), np.sqrt(29), np.sqrt(45)])
        np.testing.assert_allclose(result, expected)
        
    def test_nannorm_empty_array(self):
        """Test nannorm with empty arrays."""
        from scitex.linalg import nannorm
        
        v = np.array([])
        result = nannorm(v)
        assert result == 0.0
        
    def test_nannorm_single_element(self):
        """Test nannorm with single element."""
        from scitex.linalg import nannorm
        
        v = np.array([5])
        assert nannorm(v) == 5
        
        v = np.array([-5])
        assert nannorm(v) == 5


class TestRebaseVecFunction:
    """Test the rebase_a_vec function."""
    
    def test_rebase_vec_basic(self):
        """Test basic vector rebasing."""
        from scitex.linalg import rebase_a_vec
        
        # Project along x-axis
        v = np.array([3, 4])
        v_base = np.array([1, 0])
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 3)  # x-component
        
        # Project along y-axis
        v = np.array([3, 4])
        v_base = np.array([0, 1])
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 4)  # y-component
        
    def test_rebase_vec_diagonal(self):
        """Test rebasing along diagonal."""
        from scitex.linalg import rebase_a_vec
        
        v = np.array([2, 2])
        v_base = np.array([1, 1])
        
        # Length of projection should be full length since parallel
        result = rebase_a_vec(v, v_base)
        expected = np.sqrt(8)  # Length of v
        assert np.isclose(result, expected)
        
    def test_rebase_vec_negative_projection(self):
        """Test rebasing with negative projection."""
        from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 0])
        v_base = np.array([-1, 0])
        
        # Opposite direction
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, -1)
        
    def test_rebase_vec_with_nan(self):
        """Test rebase_a_vec with NaN values."""
        from scitex.linalg import rebase_a_vec
        
        # NaN in v
        v = np.array([np.nan, 1])
        v_base = np.array([1, 0])
        assert np.isnan(rebase_a_vec(v, v_base))
        
        # NaN in v_base
        v = np.array([1, 1])
        v_base = np.array([np.nan, 0])
        assert np.isnan(rebase_a_vec(v, v_base))
        
    def test_rebase_vec_orthogonal(self):
        """Test rebasing orthogonal vectors."""
        from scitex.linalg import rebase_a_vec
        
        v = np.array([0, 1])
        v_base = np.array([1, 0])
        
        # Orthogonal vectors have zero projection
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 0)
        
    def test_rebase_vec_3d(self):
        """Test rebasing in 3D space."""
        from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 1, 1])
        v_base = np.array([1, 0, 0])
        
        # Projection onto x-axis
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 1)
        
    def test_rebase_vec_production_vector(self):
        """Test the internal production_vector function."""
        from scitex.linalg import rebase_a_vec
        
        # Test example from docstring
        v = np.array([3, 4])
        v_base = np.array([10, 0])
        
        # This tests the projection formula
        result = rebase_a_vec(v, v_base)
        assert np.isclose(result, 3)  # x-component only


class TestThreeLineLengthsToCoords:
    """Test the three_line_lengths_to_coords function."""
    
    def test_basic_triangle(self):
        """Test basic triangle construction."""
        from scitex.linalg import three_line_lengths_to_coords
        
        # Right triangle: 3-4-5
        O, A, B = three_line_lengths_to_coords(3, 4, 5)
        
        # Check coordinates
        assert O == (0, 0, 0)
        assert A == (3, 0, 0)
        
        # B should form a right triangle
        # Distance OB should be 4
        assert np.isclose(np.linalg.norm(np.array(B) - np.array(O)), 4)
        
        # Distance AB should be 5
        assert np.isclose(np.linalg.norm(np.array(B) - np.array(A)), 5)
        
    def test_equilateral_triangle(self):
        """Test equilateral triangle."""
        from scitex.linalg import three_line_lengths_to_coords
        
        # All sides equal
        side = 2
        O, A, B = three_line_lengths_to_coords(side, side, side)
        
        assert O == (0, 0, 0)
        assert A == (side, 0, 0)
        
        # Check B forms equilateral triangle
        B_array = np.array(B)
        assert np.isclose(B_array[0], 1)  # x-coordinate
        assert np.isclose(B_array[1], np.sqrt(3))  # y-coordinate
        assert B_array[2] == 0  # z-coordinate
        
    def test_docstring_example(self):
        """Test the example from docstring."""
        from scitex.linalg import three_line_lengths_to_coords
        
        O, A, B = three_line_lengths_to_coords(2, np.sqrt(3), 1)
        
        # This forms a specific triangle
        assert O == (0, 0, 0)
        assert A == (2, 0, 0)
        
        # Verify distances
        assert np.isclose(np.linalg.norm(np.array(B) - np.array(O)), np.sqrt(3))
        assert np.isclose(np.linalg.norm(np.array(B) - np.array(A)), 1)
        
    def test_degenerate_triangle(self):
        """Test degenerate triangle (invalid side lengths)."""
        from scitex.linalg import three_line_lengths_to_coords
        
        # Triangle inequality violated (one side too long)
        # This should produce NaN or complex values in calculation
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                O, A, B = three_line_lengths_to_coords(1, 1, 3)
                # Check if B has NaN or complex components
                B_array = np.array(B)
                assert np.any(np.isnan(B_array)) or np.any(np.iscomplex(B_array))
            except (ValueError, RuntimeError):
                # Some configurations might raise errors
                pass
                
    def test_zero_length_side(self):
        """Test with zero-length side."""
        from scitex.linalg import three_line_lengths_to_coords
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                O, A, B = three_line_lengths_to_coords(1, 1, 0)
                # B should coincide with A
                assert np.allclose(A, B, rtol=1e-10)
            except (ZeroDivisionError, ValueError):
                # Division by zero is expected
                pass
                
    def test_isosceles_triangle(self):
        """Test isosceles triangle."""
        from scitex.linalg import three_line_lengths_to_coords
        
        # Two equal sides
        O, A, B = three_line_lengths_to_coords(3, 3, 4)
        
        assert O == (0, 0, 0)
        assert A == (3, 0, 0)
        
        # Verify the triangle properties
        OB_dist = np.linalg.norm(np.array(B) - np.array(O))
        AB_dist = np.linalg.norm(np.array(B) - np.array(A))
        
        assert np.isclose(OB_dist, 3)
        assert np.isclose(AB_dist, 4)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_cosine_empty_vectors(self):
        """Test cosine with empty vectors."""
        from scitex.linalg import cosine
        
        v1 = np.array([])
        v2 = np.array([])
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = cosine(v1, v2)
            # Empty dot product is 0, but norms are also 0
            assert np.isnan(result) or np.isinf(result)
            
    def test_nannorm_complex_numbers(self):
        """Test nannorm with complex numbers."""
        from scitex.linalg import nannorm
        
        v = np.array([3+4j, 0])
        result = nannorm(v)
        assert np.isclose(result, 5)  # |3+4j| = 5
        
    def test_rebase_vec_zero_base(self):
        """Test rebase_a_vec with zero base vector."""
        from scitex.linalg import rebase_a_vec
        
        v = np.array([1, 2, 3])
        v_base = np.array([0, 0, 0])
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = rebase_a_vec(v, v_base)
            assert np.isnan(result) or np.isinf(result)


class TestNumericalStability:
    """Test numerical stability of functions."""
    
    def test_cosine_large_values(self):
        """Test cosine with very large values."""
        from scitex.linalg import cosine
        
        v1 = np.array([1e100, 2e100])
        v2 = np.array([3e100, 4e100])
        
        # Should still work due to normalization
        result = cosine(v1, v2)
        expected = (3 + 8) / (np.sqrt(5) * np.sqrt(25))
        assert np.isclose(result, expected)
        
    def test_cosine_small_values(self):
        """Test cosine with very small values."""
        from scitex.linalg import cosine
        
        v1 = np.array([1e-100, 2e-100])
        v2 = np.array([3e-100, 4e-100])
        
        result = cosine(v1, v2)
        expected = (3 + 8) / (np.sqrt(5) * np.sqrt(25))
        assert np.isclose(result, expected)
        
    def test_nannorm_overflow(self):
        """Test nannorm with values that might overflow."""
        from scitex.linalg import nannorm
        
        v = np.array([1e200, 1e200])
        result = nannorm(v)
        
        # Should handle large values
        assert result > 0
        assert not np.isnan(result)


class TestIntegration:
    """Test integration between functions."""
    
    def test_cosine_and_rebase_consistency(self):
        """Test consistency between cosine and rebase_a_vec."""
        from scitex.linalg import cosine, rebase_a_vec
        
        v = np.array([3, 4])
        v_base = np.array([1, 0])
        
        # cosine * |v| should relate to projection
        cos_angle = cosine(v, v_base)
        v_norm = np.linalg.norm(v)
        expected_projection = cos_angle * v_norm
        
        actual_projection = rebase_a_vec(v, v_base)
        
        assert np.isclose(expected_projection, actual_projection)
        
    def test_triangle_and_vectors(self):
        """Test triangle construction with vector operations."""
        from scitex.linalg import three_line_lengths_to_coords, cosine
        
        O, A, B = three_line_lengths_to_coords(3, 4, 5)
        
        # Convert to vectors
        OA = np.array(A) - np.array(O)
        OB = np.array(B) - np.array(O)
        
        # Check angle using cosine
        cos_angle = cosine(OA, OB)
        
        # For 3-4-5 triangle, angle at O should be 90 degrees
        # Actually, let's calculate the expected angle
        # Using law of cosines: c² = a² + b² - 2ab*cos(C)
        # 5² = 3² + 4² - 2*3*4*cos(angle)
        # 25 = 9 + 16 - 24*cos(angle)
        # cos(angle) = 0
        assert np.isclose(cos_angle, 0, atol=1e-10)


class TestDocstringExamples:
    """Test examples provided in docstrings."""
    
    def test_production_vector_example(self):
        """Test the production_vector example from rebase_a_vec docstring."""
        from scitex.linalg import rebase_a_vec
        
        # The docstring mentions:
        # production_vector(np.array([3,4]), np.array([10,0])) # np.array([3, 0])
        
        v = np.array([3, 4])
        v_base = np.array([10, 0])
        
        result = rebase_a_vec(v, v_base)
        # The projection of [3,4] onto [10,0] (x-axis) should have magnitude 3
        assert np.isclose(result, 3)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/linalg/_misc.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-03-17 21:30:11 (ywatanabe)"
# 
# import numpy as np
# import sympy
# from scipy.linalg import norm
# 
# 
# def cosine(v1, v2):
#     if np.isnan(v1).any():
#         return np.nan
#     if np.isnan(v2).any():
#         return np.nan
#     return np.dot(v1, v2) / (norm(v1) * norm(v2))
# 
# 
# def nannorm(v, axis=-1):
#     if np.isnan(v).any():
#         return np.nan
#     else:
#         return norm(v, axis=axis)
# 
# 
# def rebase_a_vec(v, v_base):
#     def production_vector(v1, v0):
#         """
#         production_vector(np.array([3,4]), np.array([10,0])) # np.array([3, 0])
#         """
#         return norm(v1) * cosine(v1, v0) * v0 / norm(v0)
# 
#     if np.isnan(v).any():
#         return np.nan
#     if np.isnan(v_base).any():
#         return np.nan
#     v_prod = production_vector(v, v_base)
#     sign = np.sign(cosine(v, v_base))
#     return sign * norm(v_prod)
# 
# 
# def three_line_lengths_to_coords(aa, bb, cc):
#     """
#     O, A, B = three_line_lengths_to_coords(2, np.sqrt(3), 1)
#     print(O, A, B)
#     """
# 
#     # Definition
#     a1 = sympy.Symbol("a1")
#     b1 = sympy.Symbol("b1")
#     b2 = sympy.Symbol("b2")
# 
#     a1 = aa
#     # b1 = bb
# 
#     # Calculates
#     cos = (aa**2 + bb**2 - cc**2) / (2 * aa * bb)
#     sin = np.sqrt(1 - cos**2)
#     S1 = 1 / 2 * aa * bb * sin
#     S2 = 1 / 2 * aa * b2
# 
#     # Solves
#     b2 = sympy.solve(S1 - S2)[0]
#     b1 = bb * cos
# 
#     # tan1 = b2 / b1
#     # tan2 = sin/cos
# 
#     # b1 = sympy.solve(tan1-tan2)[0]
#     O = (0, 0, 0)
#     A = (a1, 0, 0)
#     B = (b1, b2, 0)
# 
#     return O, A, B

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/linalg/_misc.py
# --------------------------------------------------------------------------------
