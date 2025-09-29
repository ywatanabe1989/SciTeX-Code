#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:20:00 (claude)"
# File: ./tests/scitex/gen/test__to_odd.py

"""
Comprehensive tests for scitex.gen._to_odd module.

This module tests:
- to_odd function with various numeric inputs
- Edge cases and special values
- Type handling
"""

import pytest
import numpy as np

from scitex.gen import to_odd



class TestToOddBasic:
    """Test basic to_odd functionality."""

    def test_even_integers(self):
        """Test conversion of even integers to odd."""

        assert to_odd(2) == 1
        assert to_odd(4) == 3
        assert to_odd(6) == 5
        assert to_odd(8) == 7
        assert to_odd(10) == 9
        assert to_odd(100) == 99

    def test_odd_integers(self):
        """Test that odd integers remain unchanged."""

        assert to_odd(1) == 1
        assert to_odd(3) == 3
        assert to_odd(5) == 5
        assert to_odd(7) == 7
        assert to_odd(9) == 9
        assert to_odd(99) == 99

    def test_zero(self):
        """Test conversion of zero."""

        # 0 is even, so should become -1
        assert to_odd(0) == -1

    def test_negative_even(self):
        """Test conversion of negative even integers."""

        assert to_odd(-2) == -3
        assert to_odd(-4) == -5
        assert to_odd(-6) == -7
        assert to_odd(-8) == -9

    def test_negative_odd(self):
        """Test that negative odd integers remain unchanged."""

        assert to_odd(-1) == -1
        assert to_odd(-3) == -3
        assert to_odd(-5) == -5
        assert to_odd(-7) == -7
        assert to_odd(-9) == -9


class TestToOddFloats:
    """Test to_odd with floating point numbers."""

    def test_float_truncation(self):
        """Test that floats are truncated, not rounded."""

        # Positive floats
        assert to_odd(5.1) == 5
        assert to_odd(5.5) == 5
        assert to_odd(5.9) == 5
        assert to_odd(6.1) == 5
        assert to_odd(6.5) == 5
        assert to_odd(6.9) == 5

    def test_float_even_base(self):
        """Test floats with even integer part."""

        assert to_odd(4.1) == 3
        assert to_odd(4.5) == 3
        assert to_odd(4.9) == 3
        assert to_odd(8.3) == 7

    def test_negative_floats(self):
        """Test negative floats."""

        assert to_odd(-5.1) == -5
        assert to_odd(-5.5) == -5
        assert to_odd(-5.9) == -5
        assert to_odd(-6.1) == -7
        assert to_odd(-6.5) == -7
        assert to_odd(-6.9) == -7

    def test_documentation_examples(self):
        """Test examples from the docstring."""

        assert to_odd(6) == 5
        assert to_odd(7) == 7
        assert to_odd(5.8) == 5


class TestToOddEdgeCases:
    """Test edge cases for to_odd function."""

    def test_large_numbers(self):
        """Test with very large numbers."""

        assert to_odd(1000000) == 999999
        assert to_odd(1000001) == 1000001
        assert to_odd(10**9) == 10**9 - 1
        assert to_odd(10**9 + 1) == 10**9 + 1

    def test_special_floats(self):
        """Test with special float values."""

        # Very small positive numbers should become -1
        assert to_odd(0.1) == -1
        assert to_odd(0.5) == -1
        assert to_odd(0.9) == -1

        # Very small negative numbers
        assert to_odd(-0.1) == -1
        assert to_odd(-0.5) == -1
        assert to_odd(-0.9) == -1

    def test_numpy_types(self):
        """Test with NumPy numeric types."""

        # NumPy integers
        assert to_odd(np.int32(6)) == 5
        assert to_odd(np.int64(7)) == 7
        assert to_odd(np.int16(8)) == 7

        # NumPy floats
        assert to_odd(np.float32(6.5)) == 5
        assert to_odd(np.float64(7.9)) == 7

    def test_boolean_inputs(self):
        """Test with boolean inputs (which convert to 0/1)."""

        assert to_odd(True) == 1  # True -> 1 (already odd)
        assert to_odd(False) == -1  # False -> 0 -> -1


class TestToOddConsecutive:
    """Test to_odd with consecutive inputs."""

    def test_consecutive_integers(self):
        """Test pattern with consecutive integers."""

        results = [to_odd(i) for i in range(10)]
        expected = [-1, 1, 1, 3, 3, 5, 5, 7, 7, 9]
        assert results == expected

    def test_consecutive_negative(self):
        """Test pattern with consecutive negative integers."""

        results = [to_odd(i) for i in range(-5, 6)]
        expected = [-5, -5, -3, -3, -1, -1, 1, 1, 3, 3, 5]
        assert results == expected

    def test_sequence_properties(self):
        """Test mathematical properties of the conversion."""

        # Property: result is always odd
        for n in range(-20, 21):
            result = to_odd(n)
            assert result % 2 != 0, f"to_odd({n})={result} is not odd"

        # Property: result <= input
        for n in range(-20, 21):
            result = to_odd(n)
            assert result <= n, f"to_odd({n})={result} is greater than input"

        # Property: difference is at most 1
        for n in range(-20, 21):
            result = to_odd(n)
            assert n - result <= 1, f"to_odd({n})={result} differs by more than 1"


class TestToOddParameterized:
    """Parametrized tests for comprehensive coverage."""

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            (0, -1),
            (1, 1),
            (2, 1),
            (3, 3),
            (4, 3),
            (5, 5),
            (-1, -1),
            (-2, -3),
            (-3, -3),
            (-4, -5),
            (10.7, 9),
            (-10.7, -11),
            (0.5, -1),
            (-0.5, -1),
        ],
    )
    def test_various_inputs(self, input_val, expected):
        """Test to_odd with various inputs using parametrization."""

        assert to_odd(input_val) == expected

    @pytest.mark.parametrize("n", range(-100, 101, 10))
    def test_even_conversion_pattern(self, n):
        """Test that even numbers are converted correctly."""

        if n % 2 == 0:
            # Even numbers should become n-1
            assert to_odd(n) == n - 1
        else:
            # Odd numbers should stay the same
            assert to_odd(n) == n


class TestToOddTypeHandling:
    """Test type handling and conversions."""

    def test_string_numeric(self):
        """Test behavior with numeric strings (should raise error)."""

        # String inputs should cause TypeError in int()
        with pytest.raises(TypeError):
            to_odd("5")

        with pytest.raises(TypeError):
            to_odd("5.5")

    def test_none_input(self):
        """Test behavior with None input."""

        with pytest.raises(TypeError):
            to_odd(None)

    def test_complex_numbers(self):
        """Test behavior with complex numbers."""

        # Complex numbers don't support int() conversion
        with pytest.raises(TypeError):
            to_odd(3 + 4j)

    def test_infinity(self):
        """Test behavior with infinity."""

        # Infinity can't be converted to int
        with pytest.raises((ValueError, OverflowError)):
            to_odd(float("inf"))

        with pytest.raises((ValueError, OverflowError)):
            to_odd(float("-inf"))

    def test_nan(self):
        """Test behavior with NaN."""

        # NaN can't be converted to int
        with pytest.raises(ValueError):
            to_odd(float("nan"))


class TestToOddIntegration:
    """Integration tests for to_odd function."""

    def test_with_array_processing(self):
        """Test using to_odd with array processing."""

        # Process array of values
        inputs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        results = [to_odd(x) for x in inputs]
        expected = [1, 1, 3, 3, 5, 5, 7, 7, 9, 9]
        assert results == expected

    def test_with_numpy_vectorize(self):
        """Test using to_odd with numpy vectorize."""

        # Vectorize the function
        vec_to_odd = np.vectorize(to_odd)

        # Test on array
        inputs = np.array([1, 2, 3, 4, 5, 6])
        results = vec_to_odd(inputs)
        expected = np.array([1, 1, 3, 3, 5, 5])

        assert np.array_equal(results, expected)

    def test_use_case_kernel_sizes(self):
        """Test realistic use case: ensuring odd kernel sizes."""

        # Common in image processing where kernels need odd sizes
        kernel_sizes = [3, 4, 5, 6, 7, 8, 9]
        odd_sizes = [to_odd(k) for k in kernel_sizes]

        # All should be odd
        assert all(s % 2 != 0 for s in odd_sizes)
        # Should preserve odd sizes
        assert odd_sizes == [3, 3, 5, 5, 7, 7, 9]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_to_odd.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 23:40:22 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_to_odd.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_to_odd.py"
# 
# 
# def to_odd(n):
#     """Convert a number to the nearest odd number less than or equal to itself.
# 
#     Parameters
#     ----------
#     n : int or float
#         The input number to be converted.
# 
#     Returns
#     -------
#     int
#         The nearest odd number less than or equal to the input.
# 
#     Example
#     -------
#     >>> to_odd(6)
#     5
#     >>> to_odd(7)
#     7
#     >>> to_odd(5.8)
#     5
#     """
#     return int(n) - ((int(n) + 1) % 2)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_to_odd.py
# --------------------------------------------------------------------------------
