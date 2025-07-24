#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 21:00:00 (Claude)"
# File: /tests/scitex/gen/test__symlog.py

import pytest
import numpy as np
from scitex.gen import symlog


class TestSymlog:
    """Test cases for symmetric log transformation function."""

    def test_symlog_zero(self):
        """Test symlog with zero input."""
        result = symlog(0)
        assert result == 0

        # Array of zeros
        result_array = symlog(np.array([0, 0, 0]))
        np.testing.assert_array_equal(result_array, np.array([0, 0, 0]))

    def test_symlog_positive_values(self):
        """Test symlog with positive values."""
        # Small value < linthresh
        result = symlog(0.5, linthresh=1.0)
        expected = np.log1p(0.5 / 1.0)
        assert np.isclose(result, expected)

        # Value equal to linthresh
        result = symlog(1.0, linthresh=1.0)
        expected = np.log1p(1.0)
        assert np.isclose(result, expected)

        # Large value > linthresh
        result = symlog(10.0, linthresh=1.0)
        expected = np.log1p(10.0)
        assert np.isclose(result, expected)

    def test_symlog_negative_values(self):
        """Test symlog with negative values."""
        # Small negative value
        result = symlog(-0.5, linthresh=1.0)
        expected = -np.log1p(0.5)
        assert np.isclose(result, expected)

        # Large negative value
        result = symlog(-10.0, linthresh=1.0)
        expected = -np.log1p(10.0)
        assert np.isclose(result, expected)

    def test_symlog_symmetry(self):
        """Test that symlog is symmetric around zero."""
        values = np.array([0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
        pos_results = symlog(values)
        neg_results = symlog(-values)

        # Should be equal in magnitude but opposite in sign
        np.testing.assert_allclose(pos_results, -neg_results)

    def test_symlog_array_input(self):
        """Test symlog with array inputs."""
        x = np.array([-10, -1, -0.1, 0, 0.1, 1, 10])
        result = symlog(x)

        # Check shape preserved
        assert result.shape == x.shape

        # Check zero stays zero
        assert result[3] == 0

        # Check symmetry
        np.testing.assert_allclose(result[0:3], -result[6:3:-1])

    def test_symlog_different_linthresh(self):
        """Test symlog with different linear threshold values."""
        x = np.array([0.5, 1.0, 2.0, 5.0])

        # Smaller linthresh makes transformation more aggressive
        result_small = symlog(x, linthresh=0.1)
        result_large = symlog(x, linthresh=10.0)

        # With smaller linthresh, values should be larger (more log-like)
        assert np.all(result_small > result_large)

    def test_symlog_preserves_sign(self):
        """Test that symlog preserves the sign of input values."""
        x = np.array([-5, -2, -1, -0.5, 0, 0.5, 1, 2, 5])
        result = symlog(x)

        # Signs should match
        np.testing.assert_array_equal(np.sign(x), np.sign(result))

    def test_symlog_monotonic(self):
        """Test that symlog is monotonically increasing."""
        x = np.linspace(-10, 10, 100)
        result = symlog(x)

        # Check that differences are all positive (monotonic increasing)
        differences = np.diff(result)
        assert np.all(differences > 0)

    def test_symlog_edge_cases(self):
        """Test symlog with edge cases."""
        # Very small positive and negative values
        tiny = 1e-10
        result_pos = symlog(tiny)
        result_neg = symlog(-tiny)
        assert result_pos > 0
        assert result_neg < 0
        assert np.isclose(result_pos, -result_neg)

        # Very large values
        large = 1e10
        result_pos = symlog(large)
        result_neg = symlog(-large)
        assert result_pos > 0
        assert result_neg < 0

    def test_symlog_nan_handling(self):
        """Test symlog behavior with NaN values."""
        x = np.array([1.0, np.nan, -1.0])
        result = symlog(x)

        assert not np.isnan(result[0])
        assert np.isnan(result[1])
        assert not np.isnan(result[2])

    def test_symlog_inf_handling(self):
        """Test symlog behavior with infinite values."""
        result_pos_inf = symlog(np.inf)
        result_neg_inf = symlog(-np.inf)

        assert result_pos_inf == np.inf
        assert result_neg_inf == -np.inf

    def test_symlog_linthresh_validation(self):
        """Test symlog with different linthresh edge cases."""
        x = np.array([1.0, 2.0, 3.0])

        # Very small linthresh
        result = symlog(x, linthresh=1e-10)
        assert np.all(np.isfinite(result))

        # Zero linthresh should work but might cause division issues
        with np.errstate(divide="ignore"):
            result = symlog(x, linthresh=0)
            # Should handle gracefully, likely returning inf
            assert np.all(result == np.inf)

    def test_symlog_dtype_preservation(self):
        """Test that symlog preserves appropriate data types."""
        # Float32 input
        x_f32 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        result_f32 = symlog(x_f32)
        assert result_f32.dtype == np.float32

        # Float64 input
        x_f64 = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        result_f64 = symlog(x_f64)
        assert result_f64.dtype == np.float64

    @pytest.mark.parametrize(
        "x,linthresh,expected_sign",
        [
            (5.0, 1.0, 1),
            (-5.0, 1.0, -1),
            (0.0, 1.0, 0),
            (0.1, 0.1, 1),
            (-0.1, 0.1, -1),
        ],
    )
    def test_symlog_parametrized(self, x, linthresh, expected_sign):
        """Parametrized test for various inputs."""
        result = symlog(x, linthresh)
        assert np.sign(result) == expected_sign

        # For non-zero values, check magnitude
        if x != 0:
            expected_magnitude = np.log1p(abs(x) / linthresh)
            assert np.isclose(abs(result), expected_magnitude)

    def test_symlog_scalar_vs_array(self):
        """Test that scalar and array inputs give consistent results."""
        scalar_result = symlog(5.0, linthresh=2.0)
        array_result = symlog(np.array([5.0]), linthresh=2.0)

        assert np.isclose(scalar_result, array_result[0])

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_symlog.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-07-06 07:16:38 (ywatanabe)"
# # ./src/scitex/gen/_symlog.py
# 
# import numpy as np
# 
# 
# def symlog(x, linthresh=1.0):
#     """
#     Apply a symmetric log transformation to the input data.
# 
#     Parameters
#     ----------
#     x : array-like
#         Input data to be transformed.
#     linthresh : float, optional
#         Range within which the transformation is linear. Defaults to 1.0.
# 
#     Returns
#     -------
#     array-like
#         Symmetrically transformed data.
#     """
#     sign_x = np.sign(x)
#     abs_x = np.abs(x)
#     return sign_x * (np.log1p(abs_x / linthresh))

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_symlog.py
# --------------------------------------------------------------------------------
