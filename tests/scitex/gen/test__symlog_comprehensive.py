#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 21:10:00 (claude)"
# File: ./tests/scitex/gen/test__symlog_comprehensive.py

"""Comprehensive tests for symlog function to improve coverage."""

import pytest
import numpy as np
import sys
import os

# Add src to path for standalone execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from scitex.gen import symlog


class TestSymlogBasic:
    """Basic tests for symlog function."""
    
    def test_symlog_positive_values(self):
        """Test symlog with positive values."""
        # Small positive values
        assert symlog(0.5) == pytest.approx(np.log1p(0.5))
        assert symlog(1.0) == pytest.approx(np.log1p(1.0))
        assert symlog(2.0) == pytest.approx(np.log1p(2.0))
        
        # Large positive values
        assert symlog(10.0) == pytest.approx(np.log1p(10.0))
        assert symlog(100.0) == pytest.approx(np.log1p(100.0))
        assert symlog(1000.0) == pytest.approx(np.log1p(1000.0))
    
    def test_symlog_negative_values(self):
        """Test symlog with negative values (symmetric property)."""
        # Should be negative of positive transformation
        assert symlog(-0.5) == pytest.approx(-np.log1p(0.5))
        assert symlog(-1.0) == pytest.approx(-np.log1p(1.0))
        assert symlog(-2.0) == pytest.approx(-np.log1p(2.0))
        assert symlog(-10.0) == pytest.approx(-np.log1p(10.0))
    
    def test_symlog_zero(self):
        """Test symlog at zero."""
        assert symlog(0.0) == 0.0
        assert symlog(-0.0) == 0.0  # Negative zero
    
    def test_symlog_symmetry(self):
        """Test that symlog is symmetric around zero."""
        values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0]
        for val in values:
            assert symlog(val) == pytest.approx(-symlog(-val))


class TestSymlogWithLinthresh:
    """Test symlog with different linthresh values."""
    
    def test_linthresh_default(self):
        """Test default linthresh=1.0."""
        x = 5.0
        expected = np.log1p(5.0 / 1.0)
        assert symlog(x) == pytest.approx(expected)
    
    def test_linthresh_custom(self):
        """Test custom linthresh values."""
        x = 10.0
        
        # linthresh = 2.0
        expected = np.log1p(10.0 / 2.0)
        assert symlog(x, linthresh=2.0) == pytest.approx(expected)
        
        # linthresh = 0.5
        expected = np.log1p(10.0 / 0.5)
        assert symlog(x, linthresh=0.5) == pytest.approx(expected)
        
        # linthresh = 10.0
        expected = np.log1p(10.0 / 10.0)
        assert symlog(x, linthresh=10.0) == pytest.approx(expected)
    
    def test_linthresh_small(self):
        """Test with very small linthresh."""
        x = 1.0
        # Small linthresh amplifies the transformation
        assert symlog(x, linthresh=0.01) > symlog(x, linthresh=1.0)
        assert symlog(x, linthresh=0.001) > symlog(x, linthresh=0.01)
    
    def test_linthresh_large(self):
        """Test with very large linthresh."""
        x = 1.0
        # Large linthresh dampens the transformation
        assert symlog(x, linthresh=100.0) < symlog(x, linthresh=1.0)
        assert symlog(x, linthresh=1000.0) < symlog(x, linthresh=100.0)
    
    def test_linthresh_edge_cases(self):
        """Test edge cases for linthresh."""
        # Very small linthresh with large x
        assert np.isfinite(symlog(1000.0, linthresh=1e-10))
        
        # Very large linthresh with small x
        result = symlog(0.001, linthresh=1e10)
        assert np.isfinite(result)
        assert abs(result) < 1e-10  # Should be very close to 0


class TestSymlogArrays:
    """Test symlog with array inputs."""
    
    def test_1d_array(self):
        """Test with 1D numpy array."""
        x = np.array([-5, -2, -1, 0, 1, 2, 5])
        result = symlog(x)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        assert result[3] == 0.0  # Zero remains zero
        
        # Check symmetry
        assert result[0] == pytest.approx(-result[-1])
        assert result[1] == pytest.approx(-result[-2])
        assert result[2] == pytest.approx(-result[-3])
    
    def test_2d_array(self):
        """Test with 2D numpy array."""
        x = np.array([[-2, -1, 0], [1, 2, 3]])
        result = symlog(x)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        assert result[0, 2] == 0.0  # Zero element
        
        # Check individual elements
        assert result[0, 0] == pytest.approx(-symlog(2))
        assert result[1, 2] == pytest.approx(symlog(3))
    
    def test_3d_array(self):
        """Test with 3D numpy array."""
        x = np.random.randn(2, 3, 4)
        result = symlog(x)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
    
    def test_array_with_custom_linthresh(self):
        """Test array input with custom linthresh."""
        x = np.array([0.1, 1.0, 10.0, 100.0])
        linthresh = 5.0
        result = symlog(x, linthresh=linthresh)
        
        for i, val in enumerate(x):
            expected = np.sign(val) * np.log1p(np.abs(val) / linthresh)
            assert result[i] == pytest.approx(expected)


class TestSymlogSpecialValues:
    """Test symlog with special values."""
    
    def test_infinity(self):
        """Test with infinity values."""
        assert symlog(np.inf) == np.inf
        assert symlog(-np.inf) == -np.inf
        
        # With custom linthresh
        assert symlog(np.inf, linthresh=10.0) == np.inf
        assert symlog(-np.inf, linthresh=0.1) == -np.inf
    
    def test_nan(self):
        """Test with NaN values."""
        assert np.isnan(symlog(np.nan))
        assert np.isnan(symlog(np.nan, linthresh=2.0))
    
    def test_very_small_values(self):
        """Test with very small values near machine epsilon."""
        eps = np.finfo(float).eps
        
        # Should handle without overflow/underflow
        result = symlog(eps)
        assert np.isfinite(result)
        assert result > 0
        
        result = symlog(-eps)
        assert np.isfinite(result)
        assert result < 0
    
    def test_very_large_values(self):
        """Test with very large values."""
        large = 1e100
        result = symlog(large)
        assert np.isfinite(result)
        assert result > 0
        
        # Should maintain symmetry
        assert symlog(-large) == pytest.approx(-result)


class TestSymlogMathematicalProperties:
    """Test mathematical properties of symlog."""
    
    def test_monotonicity(self):
        """Test that symlog is monotonically increasing."""
        x = np.linspace(-10, 10, 100)
        y = symlog(x)
        
        # Check that differences are all positive
        assert np.all(np.diff(y) > 0)
    
    def test_linear_region(self):
        """Test behavior in the linear region."""
        # For small x relative to linthresh, should be approximately linear
        linthresh = 1.0
        small_x = np.linspace(-0.1, 0.1, 10)
        result = symlog(small_x, linthresh=linthresh)
        
        # In linear region, symlog(x) ≈ x/linthresh
        expected = small_x / linthresh
        np.testing.assert_allclose(result, expected, rtol=0.1)
    
    def test_derivative_continuity(self):
        """Test that the transformation is smooth."""
        # Check smoothness around x=0
        x = np.array([-1e-6, -1e-7, 0, 1e-7, 1e-6])
        y = symlog(x)
        
        # Should not have jumps
        assert np.all(np.isfinite(y))
        assert np.all(np.abs(np.diff(y)) < 1)
    
    def test_inverse_relationship(self):
        """Test properties related to inverse (though symlog doesn't have simple inverse)."""
        # For large x, symlog(x) ≈ sign(x) * log(|x|/linthresh)
        x = 1000.0
        linthresh = 1.0
        result = symlog(x, linthresh)
        
        # Should be close to log(x/linthresh) for large x
        expected = np.log(x / linthresh)
        assert abs(result - expected) < 0.1  # Within reasonable tolerance


class TestSymlogUseCases:
    """Test common use cases for symlog."""
    
    def test_data_with_outliers(self):
        """Test with data containing outliers."""
        # Data with normal values and outliers
        data = np.array([0.1, 0.5, 1.0, 2.0, 100.0, 1000.0])
        result = symlog(data)
        
        # Should compress the range of outliers
        assert np.all(np.isfinite(result))
        assert result[-1] < 10 * result[0]  # Outlier compressed
    
    def test_mixed_sign_data(self):
        """Test with data having both positive and negative values."""
        data = np.array([-1000, -10, -1, -0.1, 0, 0.1, 1, 10, 1000])
        result = symlog(data)
        
        # Should handle all values smoothly
        assert np.all(np.isfinite(result))
        assert result[4] == 0  # Zero maps to zero
        
        # Check symmetry
        for i in range(4):
            assert result[i] == pytest.approx(-result[-(i+1)])
    
    @pytest.mark.parametrize("linthresh", [0.1, 0.5, 1.0, 2.0, 10.0])
    def test_different_scales(self, linthresh):
        """Test symlog with different scale parameters."""
        x = np.array([0, 0.5, 1, 2, 5, 10, 50, 100])
        result = symlog(x, linthresh=linthresh)
        
        # All results should be finite
        assert np.all(np.isfinite(result))
        
        # Zero should always map to zero
        assert result[0] == 0
        
        # Should be monotonic
        assert np.all(np.diff(result) >= 0)


class TestSymlogEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_array(self):
        """Test with empty array."""
        x = np.array([])
        result = symlog(x)
        assert isinstance(result, np.ndarray)
        assert result.shape == (0,)
    
    def test_scalar_vs_array(self):
        """Test that scalar and single-element array give same result."""
        scalar_result = symlog(5.0)
        array_result = symlog(np.array([5.0]))[0]
        assert scalar_result == pytest.approx(array_result)
    
    def test_dtype_preservation(self):
        """Test that dtype is preserved appropriately."""
        # Float32
        x_f32 = np.array([1, 2, 3], dtype=np.float32)
        result_f32 = symlog(x_f32)
        assert result_f32.dtype == np.float32
        
        # Float64
        x_f64 = np.array([1, 2, 3], dtype=np.float64)
        result_f64 = symlog(x_f64)
        assert result_f64.dtype == np.float64
        
        # Integer input should produce float output
        x_int = np.array([1, 2, 3], dtype=np.int32)
        result_int = symlog(x_int)
        assert np.issubdtype(result_int.dtype, np.floating)
    
    def test_negative_linthresh(self):
        """Test behavior with negative linthresh (might be undefined)."""
        # Using absolute value of linthresh would be reasonable
        x = 5.0
        result1 = symlog(x, linthresh=2.0)
        result2 = symlog(x, linthresh=-2.0)
        
        # Behavior depends on implementation, but should be finite
        assert np.isfinite(result2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])