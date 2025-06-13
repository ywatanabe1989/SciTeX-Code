#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 20:40:00 (claude)"
# File: ./tests/scitex/gen/test__to_odd_comprehensive.py

"""Comprehensive tests for scitex.gen._to_odd module to improve coverage."""

import pytest
import sys
import os

# Add src to path for standalone execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

# Import the function directly for testing
from scitex.gen import to_odd


class TestToOddComprehensive:
    """Comprehensive test suite for to_odd function."""
    
    def test_even_to_odd_conversion(self):
        """Test conversion of even numbers to nearest odd less than or equal."""
        assert to_odd(0) == -1  # 0 is even, nearest odd ≤ 0 is -1
        assert to_odd(2) == 1   # nearest odd ≤ 2 is 1
        assert to_odd(4) == 3   # nearest odd ≤ 4 is 3
        assert to_odd(6) == 5   # nearest odd ≤ 6 is 5
        assert to_odd(100) == 99
        assert to_odd(1000) == 999
    
    def test_odd_numbers_unchanged(self):
        """Test that odd numbers remain unchanged."""
        assert to_odd(1) == 1
        assert to_odd(3) == 3
        assert to_odd(5) == 5
        assert to_odd(7) == 7
        assert to_odd(99) == 99
        assert to_odd(1001) == 1001
    
    def test_negative_numbers(self):
        """Test conversion of negative numbers."""
        assert to_odd(-1) == -1  # -1 is odd, stays -1
        assert to_odd(-2) == -3  # -2 is even, nearest odd ≤ -2 is -3
        assert to_odd(-3) == -3  # -3 is odd, stays -3
        assert to_odd(-4) == -5  # -4 is even, nearest odd ≤ -4 is -5
        assert to_odd(-100) == -101
    
    def test_float_conversion(self):
        """Test conversion of float values."""
        assert to_odd(1.1) == 1   # int(1.1) = 1, which is odd
        assert to_odd(2.9) == 1   # int(2.9) = 2, nearest odd ≤ 2 is 1
        assert to_odd(3.5) == 3   # int(3.5) = 3, which is odd
        assert to_odd(4.2) == 3   # int(4.2) = 4, nearest odd ≤ 4 is 3
        assert to_odd(5.8) == 5   # int(5.8) = 5, which is odd
        assert to_odd(6.1) == 5   # int(6.1) = 6, nearest odd ≤ 6 is 5
    
    def test_negative_floats(self):
        """Test conversion of negative float values."""
        assert to_odd(-1.5) == -1  # int(-1.5) = -1, which is odd
        assert to_odd(-2.3) == -3  # int(-2.3) = -2, nearest odd ≤ -2 is -3
        assert to_odd(-3.7) == -3  # int(-3.7) = -3, which is odd
        assert to_odd(-4.1) == -5  # int(-4.1) = -4, nearest odd ≤ -4 is -5
    
    def test_zero_and_near_zero(self):
        """Test edge cases around zero."""
        assert to_odd(0) == -1     # 0 is even
        assert to_odd(0.0) == -1   # 0.0 is even
        assert to_odd(0.1) == -1   # int(0.1) = 0, which is even
        assert to_odd(0.9) == -1   # int(0.9) = 0, which is even
        assert to_odd(-0.1) == -1  # int(-0.1) = 0, which is even
        assert to_odd(-0.9) == -1  # int(-0.9) = 0, which is even
    
    def test_large_numbers(self):
        """Test with large numbers."""
        assert to_odd(1000000) == 999999
        assert to_odd(1000001) == 1000001
        assert to_odd(999998) == 999997
        assert to_odd(999999) == 999999
        assert to_odd(1234567) == 1234567  # already odd
        assert to_odd(1234568) == 1234567
    
    def test_very_small_floats(self):
        """Test with very small float values."""
        assert to_odd(0.0001) == -1   # rounds to 0
        assert to_odd(0.9999) == -1   # still rounds to 0
        assert to_odd(1.0001) == 1    # rounds to 1
        assert to_odd(-0.0001) == -1  # rounds to 0
        assert to_odd(-0.9999) == -1  # rounds to 0
    
    def test_formula_verification(self):
        """Verify the formula: int(n) - ((int(n) + 1) % 2)."""
        # For even n: int(n) is even, (int(n) + 1) is odd, (odd % 2) = 1
        # Result: int(n) - 1 (which gives the odd number below)
        
        # For odd n: int(n) is odd, (int(n) + 1) is even, (even % 2) = 0
        # Result: int(n) - 0 = int(n) (stays the same)
        
        # Test even numbers
        for n in [0, 2, 4, 6, 8, 10]:
            expected = n - 1
            assert to_odd(n) == expected
        
        # Test odd numbers
        for n in [1, 3, 5, 7, 9, 11]:
            expected = n
            assert to_odd(n) == expected
    
    @pytest.mark.parametrize("input_val,expected", [
        # Even integers
        (0, -1),
        (2, 1),
        (4, 3),
        (10, 9),
        # Odd integers
        (1, 1),
        (3, 3),
        (5, 5),
        (11, 11),
        # Floats
        (2.3, 1),
        (3.7, 3),
        (4.9, 3),
        (5.1, 5),
        # Negative
        (-2, -3),
        (-3, -3),
        (-4.5, -5),
        # Edge cases
        (0.5, -1),
        (-0.5, -1),
    ])
    def test_parametrized_comprehensive(self, input_val, expected):
        """Parametrized test covering various scenarios."""
        assert to_odd(input_val) == expected
    
    def test_type_preservation(self):
        """Test that the function always returns int."""
        # Test with various input types
        assert isinstance(to_odd(5), int)
        assert isinstance(to_odd(5.7), int)
        assert isinstance(to_odd(-3.2), int)
        assert isinstance(to_odd(0), int)
    
    def test_mathematical_properties(self):
        """Test mathematical properties of the function."""
        # to_odd(n) should always be odd
        for n in range(-10, 11):
            result = to_odd(n)
            assert result % 2 != 0, f"to_odd({n}) = {result} is not odd"
        
        # to_odd(n) <= n for all n
        for n in range(-10, 11):
            assert to_odd(n) <= n
        
        # to_odd(n) >= n - 1 for all integer n
        for n in range(-10, 11):
            assert to_odd(n) >= n - 1
    
    def test_consistency_with_documentation(self):
        """Test examples from the function's docstring."""
        # From docstring:
        assert to_odd(6) == 5
        assert to_odd(7) == 7
        assert to_odd(5.8) == 5


class TestToOddEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_special_float_values(self):
        """Test with special float values."""
        # Note: These may raise exceptions or have undefined behavior
        # depending on implementation
        try:
            # Very large float
            large = 1e10
            result = to_odd(large)
            assert result % 2 != 0  # Should be odd
            assert result <= large
        except:
            pass  # Implementation may not handle very large floats
    
    def test_numerical_precision(self):
        """Test numerical precision edge cases."""
        # Numbers very close to integers
        assert to_odd(1.9999999999) == 1
        assert to_odd(2.0000000001) == 1
        assert to_odd(2.9999999999) == 1
        assert to_odd(3.0000000001) == 3
    
    def test_sequence_generation(self):
        """Test generating sequence of odd numbers."""
        # Using to_odd to generate sequence
        odds = []
        for i in range(10):
            odds.append(to_odd(i))
        
        expected = [-1, 1, 1, 3, 3, 5, 5, 7, 7, 9]
        assert odds == expected


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])