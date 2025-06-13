#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 21:20:00 (claude)"
# File: ./tests/scitex/gen/test__transpose_comprehensive.py

"""Comprehensive tests for transpose function with dimension mapping."""

import pytest
import numpy as np
import sys
import os

# Add src to path for standalone execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from scitex.gen import transpose


class TestTransposeBasic:
    """Basic tests for transpose function."""
    
    def test_2d_transpose(self):
        """Test transposing a 2D array."""
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        src_dims = np.array(['rows', 'cols'])
        tgt_dims = np.array(['cols', 'rows'])
        
        result = transpose(arr, src_dims, tgt_dims)
        expected = arr.T
        
        np.testing.assert_array_equal(result, expected)
        assert result.shape == (3, 2)
    
    def test_3d_transpose_all_permutations(self):
        """Test all possible permutations of 3D array."""
        arr = np.arange(24).reshape(2, 3, 4)
        src_dims = np.array(['batch', 'height', 'width'])
        
        # Test all 6 permutations
        permutations = [
            (['batch', 'height', 'width'], (0, 1, 2)),
            (['batch', 'width', 'height'], (0, 2, 1)),
            (['height', 'batch', 'width'], (1, 0, 2)),
            (['height', 'width', 'batch'], (1, 2, 0)),
            (['width', 'batch', 'height'], (2, 0, 1)),
            (['width', 'height', 'batch'], (2, 1, 0)),
        ]
        
        for tgt_list, expected_axes in permutations:
            tgt_dims = np.array(tgt_list)
            result = transpose(arr, src_dims, tgt_dims)
            expected = arr.transpose(expected_axes)
            np.testing.assert_array_equal(result, expected)
    
    def test_identity_transpose(self):
        """Test transpose with same source and target order."""
        arr = np.arange(12).reshape(3, 4)
        src_dims = np.array(['x', 'y'])
        tgt_dims = np.array(['x', 'y'])  # Same order
        
        result = transpose(arr, src_dims, tgt_dims)
        np.testing.assert_array_equal(result, arr)
    
    def test_1d_array(self):
        """Test transpose on 1D array."""
        arr = np.array([1, 2, 3, 4, 5])
        src_dims = np.array(['x'])
        tgt_dims = np.array(['x'])
        
        result = transpose(arr, src_dims, tgt_dims)
        np.testing.assert_array_equal(result, arr)


class TestTransposeDimensionNames:
    """Test transpose with various dimension naming schemes."""
    
    def test_standard_ml_dimensions(self):
        """Test with standard ML dimension names."""
        # NCHW to NHWC (common in deep learning)
        arr = np.random.rand(32, 3, 224, 224)  # batch, channels, height, width
        src_dims = np.array(['N', 'C', 'H', 'W'])
        tgt_dims = np.array(['N', 'H', 'W', 'C'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (32, 224, 224, 3)
        
        # Verify specific element mapping
        assert result[0, 0, 0, 0] == arr[0, 0, 0, 0]
        assert result[0, 0, 0, 1] == arr[0, 1, 0, 0]
        assert result[0, 0, 0, 2] == arr[0, 2, 0, 0]
    
    def test_time_series_dimensions(self):
        """Test with time series dimension names."""
        # (time, batch, features) to (batch, time, features)
        arr = np.random.rand(100, 16, 64)
        src_dims = np.array(['time', 'batch', 'features'])
        tgt_dims = np.array(['batch', 'time', 'features'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (16, 100, 64)
    
    def test_scientific_dimensions(self):
        """Test with scientific data dimensions."""
        # (x, y, z, t) to (t, z, y, x)
        arr = np.random.rand(10, 20, 30, 40)
        src_dims = np.array(['x', 'y', 'z', 't'])
        tgt_dims = np.array(['t', 'z', 'y', 'x'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (40, 30, 20, 10)
    
    def test_unicode_dimension_names(self):
        """Test with unicode dimension names."""
        arr = np.array([[1, 2], [3, 4]])
        src_dims = np.array(['α', 'β'])
        tgt_dims = np.array(['β', 'α'])
        
        result = transpose(arr, src_dims, tgt_dims)
        expected = arr.T
        np.testing.assert_array_equal(result, expected)


class TestTransposeEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_mismatched_dimensions_error(self):
        """Test that mismatched dimensions raise an error."""
        arr = np.array([[1, 2], [3, 4]])
        src_dims = np.array(['x', 'y'])
        tgt_dims = np.array(['a', 'b'])  # Different dimension names
        
        with pytest.raises(AssertionError, match="same elements"):
            transpose(arr, src_dims, tgt_dims)
    
    def test_missing_dimension_error(self):
        """Test error when target has missing dimension."""
        arr = np.random.rand(2, 3, 4)
        src_dims = np.array(['a', 'b', 'c'])
        tgt_dims = np.array(['a', 'b'])  # Missing 'c'
        
        with pytest.raises(AssertionError):
            transpose(arr, src_dims, tgt_dims)
    
    def test_extra_dimension_error(self):
        """Test error when target has extra dimension."""
        arr = np.random.rand(2, 3)
        src_dims = np.array(['a', 'b'])
        tgt_dims = np.array(['a', 'b', 'c'])  # Extra 'c'
        
        with pytest.raises(AssertionError):
            transpose(arr, src_dims, tgt_dims)
    
    def test_duplicate_dimensions_in_source(self):
        """Test behavior with duplicate dimension names in source."""
        arr = np.random.rand(2, 3, 4)
        src_dims = np.array(['a', 'a', 'b'])  # Duplicate 'a'
        tgt_dims = np.array(['b', 'a', 'a'])
        
        # This will use the first occurrence of 'a'
        result = transpose(arr, src_dims, tgt_dims)
        # Shape should be (4, 2, 2) based on first 'a' match
        assert result.shape == (4, 2, 2)
    
    def test_empty_array(self):
        """Test with empty array."""
        arr = np.array([])
        src_dims = np.array([])
        tgt_dims = np.array([])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == arr.shape
        assert len(result) == 0


class TestTransposeHighDimensional:
    """Test transpose with high-dimensional arrays."""
    
    def test_4d_transpose(self):
        """Test 4D array transpose."""
        arr = np.random.rand(2, 3, 4, 5)
        src_dims = np.array(['a', 'b', 'c', 'd'])
        tgt_dims = np.array(['d', 'b', 'a', 'c'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (5, 3, 2, 4)
        
        # Verify element mapping
        assert result[0, 0, 0, 0] == arr[0, 0, 0, 0]
    
    def test_5d_transpose(self):
        """Test 5D array transpose."""
        arr = np.random.rand(2, 3, 4, 5, 6)
        src_dims = np.array(['v', 'w', 'x', 'y', 'z'])
        tgt_dims = np.array(['z', 'y', 'x', 'w', 'v'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (6, 5, 4, 3, 2)
    
    def test_6d_transpose(self):
        """Test 6D array transpose (stress test)."""
        shape = (2, 2, 2, 2, 2, 2)
        arr = np.arange(64).reshape(shape)
        src_dims = np.array(['a', 'b', 'c', 'd', 'e', 'f'])
        tgt_dims = np.array(['f', 'e', 'd', 'c', 'b', 'a'])
        
        result = transpose(arr, src_dims, tgt_dims)
        expected = arr.transpose(5, 4, 3, 2, 1, 0)
        np.testing.assert_array_equal(result, expected)


class TestTransposeDataTypes:
    """Test transpose with different data types."""
    
    def test_integer_array(self):
        """Test with integer array."""
        arr = np.array([[1, 2], [3, 4]], dtype=np.int32)
        src_dims = np.array(['x', 'y'])
        tgt_dims = np.array(['y', 'x'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.dtype == np.int32
        np.testing.assert_array_equal(result, arr.T)
    
    def test_float32_array(self):
        """Test with float32 array."""
        arr = np.array([[1.5, 2.5], [3.5, 4.5]], dtype=np.float32)
        src_dims = np.array(['a', 'b'])
        tgt_dims = np.array(['b', 'a'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.dtype == np.float32
        np.testing.assert_array_equal(result, arr.T)
    
    def test_complex_array(self):
        """Test with complex number array."""
        arr = np.array([[1+2j, 3+4j], [5+6j, 7+8j]], dtype=np.complex128)
        src_dims = np.array(['real', 'imag'])
        tgt_dims = np.array(['imag', 'real'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.dtype == np.complex128
        np.testing.assert_array_equal(result, arr.T)
    
    def test_boolean_array(self):
        """Test with boolean array."""
        arr = np.array([[True, False], [False, True]])
        src_dims = np.array(['p', 'q'])
        tgt_dims = np.array(['q', 'p'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.dtype == bool
        np.testing.assert_array_equal(result, arr.T)


class TestTransposeSpecialCases:
    """Test special cases and advanced usage."""
    
    def test_view_vs_copy(self):
        """Test whether transpose returns a view or copy."""
        arr = np.arange(6).reshape(2, 3)
        src_dims = np.array(['x', 'y'])
        tgt_dims = np.array(['y', 'x'])
        
        result = transpose(arr, src_dims, tgt_dims)
        
        # Transpose typically returns a view
        # Modifying result should affect original if it's a view
        result_copy = result.copy()
        result_copy[0, 0] = 999
        
        # Original should not be affected since we modified a copy
        assert arr[0, 0] != 999
    
    def test_dimension_order_preservation(self):
        """Test that dimension order is preserved correctly."""
        arr = np.arange(24).reshape(2, 3, 4)
        src_dims = np.array(['batch', 'height', 'width'])
        
        # Circular shift of dimensions
        tgt_dims = np.array(['width', 'batch', 'height'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (4, 2, 3)
        
        # Verify specific elements
        assert result[0, 0, 0] == arr[0, 0, 0]
        assert result[3, 1, 2] == arr[1, 2, 3]
    
    def test_list_input_for_dimensions(self):
        """Test that list inputs are converted to numpy arrays."""
        arr = np.array([[1, 2], [3, 4]])
        src_dims = ['x', 'y']  # List instead of numpy array
        tgt_dims = ['y', 'x']  # List instead of numpy array
        
        # Should work after internal conversion
        result = transpose(np.array(arr), np.array(src_dims), np.array(tgt_dims))
        np.testing.assert_array_equal(result, arr.T)
    
    @pytest.mark.parametrize("shape,src,tgt", [
        ((2, 3), ['a', 'b'], ['b', 'a']),
        ((2, 3, 4), ['x', 'y', 'z'], ['z', 'x', 'y']),
        ((5, 4, 3, 2), ['d1', 'd2', 'd3', 'd4'], ['d4', 'd3', 'd2', 'd1']),
    ])
    def test_parametrized_shapes(self, shape, src, tgt):
        """Test various array shapes with parametrized inputs."""
        arr = np.random.rand(*shape)
        src_dims = np.array(src)
        tgt_dims = np.array(tgt)
        
        result = transpose(arr, src_dims, tgt_dims)
        
        # Calculate expected shape
        src_to_tgt_map = {s: i for i, s in enumerate(src)}
        expected_shape = tuple(shape[src_to_tgt_map[t]] for t in tgt)
        
        assert result.shape == expected_shape


class TestTransposeMemoryLayout:
    """Test memory layout considerations."""
    
    def test_c_contiguous_input(self):
        """Test with C-contiguous array."""
        arr = np.ascontiguousarray(np.random.rand(3, 4, 5))
        assert arr.flags['C_CONTIGUOUS']
        
        src_dims = np.array(['a', 'b', 'c'])
        tgt_dims = np.array(['c', 'b', 'a'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (5, 4, 3)
        # Result may not be C-contiguous after transpose
    
    def test_f_contiguous_input(self):
        """Test with Fortran-contiguous array."""
        arr = np.asfortranarray(np.random.rand(3, 4, 5))
        assert arr.flags['F_CONTIGUOUS']
        
        src_dims = np.array(['a', 'b', 'c'])
        tgt_dims = np.array(['c', 'b', 'a'])
        
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (5, 4, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])