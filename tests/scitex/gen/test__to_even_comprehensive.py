#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:25:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__to_even_comprehensive.py

"""Comprehensive tests for to_even function."""

import pytest
import numpy as np
import math
import decimal
from fractions import Fraction
from scitex.gen import to_even


class TestToEvenBasicIntegers:
    """Test basic integer conversions."""
    
    def test_odd_positive_integers(self):
        """Test conversion of odd positive integers."""
        test_cases = [
            (1, 0),
            (3, 2),
            (5, 4),
            (7, 6),
            (9, 8),
            (11, 10),
            (99, 98),
            (101, 100),
            (999, 998),
            (1001, 1000),
            (9999, 9998)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_even_positive_integers(self):
        """Test that even positive integers remain unchanged."""
        test_cases = [0, 2, 4, 6, 8, 10, 100, 1000, 9998, 10000]
        
        for val in test_cases:
            assert to_even(val) == val
    
    def test_odd_negative_integers(self):
        """Test conversion of odd negative integers."""
        test_cases = [
            (-1, -2),
            (-3, -4),
            (-5, -6),
            (-7, -8),
            (-9, -10),
            (-99, -100),
            (-999, -1000),
            (-9999, -10000)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_even_negative_integers(self):
        """Test that even negative integers remain unchanged."""
        test_cases = [-2, -4, -6, -8, -10, -100, -1000, -9998, -10000]
        
        for val in test_cases:
            assert to_even(val) == val
    
    def test_zero(self):
        """Test that zero remains zero."""
        assert to_even(0) == 0
        assert to_even(-0) == 0  # -0 is same as 0 in Python


class TestToEvenFloats:
    """Test float conversions."""
    
    def test_positive_floats_between_integers(self):
        """Test positive floats between integers."""
        test_cases = [
            (0.1, 0),
            (0.5, 0),
            (0.9, 0),
            (1.1, 0),
            (1.5, 0),
            (1.9, 0),
            (2.1, 2),
            (2.5, 2),
            (2.9, 2),
            (3.1, 2),
            (3.5, 2),
            (3.9, 2),
            (4.1, 4),
            (4.5, 4),
            (4.9, 4)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_negative_floats_between_integers(self):
        """Test negative floats between integers."""
        test_cases = [
            (-0.1, -2),
            (-0.5, -2),
            (-0.9, -2),
            (-1.1, -2),
            (-1.5, -2),
            (-1.9, -2),
            (-2.1, -4),
            (-2.5, -4),
            (-2.9, -4),
            (-3.1, -4),
            (-3.5, -4),
            (-3.9, -4)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_floats_exactly_integers(self):
        """Test floats that are exactly integers."""
        test_cases = [
            (1.0, 0),
            (2.0, 2),
            (3.0, 2),
            (4.0, 4),
            (-1.0, -2),
            (-2.0, -2),
            (-3.0, -4),
            (-4.0, -4)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_very_small_floats(self):
        """Test very small float values."""
        test_cases = [
            (0.0001, 0),
            (0.00001, 0),
            (1e-10, 0),
            (1e-100, 0),
            (-0.0001, -2),
            (-0.00001, -2),
            (-1e-10, -2),
            (-1e-100, -2)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected


class TestToEvenSpecialValues:
    """Test special numeric values."""
    
    def test_infinity(self):
        """Test infinity values."""
        # Positive infinity
        result = to_even(float('inf'))
        assert math.isinf(result) or isinstance(result, (int, float))
        
        # Negative infinity
        result = to_even(float('-inf'))
        assert math.isinf(result) or isinstance(result, (int, float))
    
    def test_nan(self):
        """Test NaN values."""
        result = to_even(float('nan'))
        # Could return NaN or raise exception
        assert math.isnan(result) or isinstance(result, (int, float))
    
    def test_numpy_values(self):
        """Test with numpy numeric types."""
        test_cases = [
            (np.int8(3), 2),
            (np.int16(5), 4),
            (np.int32(7), 6),
            (np.int64(9), 8),
            (np.float32(3.5), 2),
            (np.float64(5.7), 4)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_numpy_special_values(self):
        """Test numpy special values."""
        # Test numpy infinity
        result = to_even(np.inf)
        assert np.isinf(result) or isinstance(result, (int, float))
        
        # Test numpy nan
        result = to_even(np.nan)
        assert np.isnan(result) or isinstance(result, (int, float))


class TestToEvenEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_numbers(self):
        """Test with very large numbers."""
        test_cases = [
            (10**6, 10**6),           # 1 million (even)
            (10**6 + 1, 10**6),       # 1 million + 1 (odd)
            (10**9, 10**9),           # 1 billion (even)
            (10**9 + 1, 10**9),       # 1 billion + 1 (odd)
            (10**12 - 1, 10**12 - 2), # 1 trillion - 1 (odd)
            (10**15 + 1, 10**15),     # 1 quadrillion + 1 (odd)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_near_zero_values(self):
        """Test values very close to zero."""
        test_cases = [
            (0.1, 0),
            (0.01, 0),
            (0.001, 0),
            (0.0001, 0),
            (-0.1, -2),
            (-0.01, -2),
            (-0.001, -2),
            (-0.0001, -2)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_boundary_crossings(self):
        """Test values at integer boundaries."""
        # Just below even integers
        assert to_even(1.9999999) == 0
        assert to_even(3.9999999) == 2
        assert to_even(-1.0000001) == -2
        assert to_even(-3.0000001) == -4
        
        # Just above even integers  
        assert to_even(2.0000001) == 2
        assert to_even(4.0000001) == 4
        assert to_even(-2.0000001) == -4
        assert to_even(-4.0000001) == -6
    
    def test_precision_limits(self):
        """Test floating point precision limits."""
        # Very close to integers
        assert to_even(1 + 1e-15) == 0
        assert to_even(2 + 1e-15) == 2
        assert to_even(3 - 1e-15) == 2
        assert to_even(4 - 1e-15) == 4


class TestToEvenTypeHandling:
    """Test handling of different numeric types."""
    
    def test_boolean_values(self):
        """Test boolean values (True=1, False=0)."""
        assert to_even(True) == 0   # True is 1, which becomes 0
        assert to_even(False) == 0  # False is 0, which stays 0
    
    def test_decimal_type(self):
        """Test with decimal.Decimal type."""
        from decimal import Decimal
        
        test_cases = [
            (Decimal('1'), 0),
            (Decimal('2'), 2),
            (Decimal('3.5'), 2),
            (Decimal('4.7'), 4),
            (Decimal('-1.5'), -2),
            (Decimal('-2.3'), -4)
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_fraction_type(self):
        """Test with fractions.Fraction type."""
        test_cases = [
            (Fraction(1, 1), 0),      # 1
            (Fraction(3, 1), 2),      # 3
            (Fraction(5, 2), 2),      # 2.5
            (Fraction(7, 2), 2),      # 3.5
            (Fraction(-3, 2), -2),    # -1.5
            (Fraction(-5, 2), -4)     # -2.5
        ]
        
        for input_val, expected in test_cases:
            assert to_even(input_val) == expected
    
    def test_complex_numbers(self):
        """Test behavior with complex numbers."""
        # Should either handle real part or raise TypeError
        try:
            result = to_even(3 + 4j)
            # If it works, it might use real part
            assert result == 2
        except (TypeError, AttributeError):
            # Expected if complex numbers not supported
            pass


class TestToEvenAlgorithmicProperties:
    """Test algorithmic properties of to_even."""
    
    def test_idempotence(self):
        """Test that applying to_even twice gives same result."""
        test_values = [1, 2, 3, 4, 5, -1, -2, -3, 3.5, -2.7]
        
        for val in test_values:
            once = to_even(val)
            twice = to_even(once)
            assert once == twice
    
    def test_monotonicity(self):
        """Test monotonic property: if a < b, then to_even(a) <= to_even(b)."""
        test_pairs = [
            (1, 2),
            (1.5, 2.5),
            (3, 5),
            (-5, -3),
            (-2.5, -1.5),
            (0, 1),
            (-1, 0)
        ]
        
        for a, b in test_pairs:
            assert to_even(a) <= to_even(b)
    
    def test_distance_to_nearest_even(self):
        """Test that result is always within 2 of input."""
        test_values = [1, 3, 5, 7, 1.5, 3.7, -1, -3.5]
        
        for val in test_values:
            result = to_even(val)
            distance = abs(result - val)
            assert distance <= 2
    
    def test_sign_preservation_pattern(self):
        """Test sign behavior patterns."""
        # Positive values stay non-negative
        positive_values = [0.1, 1, 1.5, 2, 3, 4.5]
        for val in positive_values:
            assert to_even(val) >= 0
        
        # Negative values stay non-positive
        negative_values = [-0.1, -1, -1.5, -2, -3, -4.5]
        for val in negative_values:
            assert to_even(val) <= 0


class TestToEvenParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("input_val,expected", [
        # Positive integers
        (1, 0), (2, 2), (3, 2), (4, 4), (5, 4),
        # Negative integers
        (-1, -2), (-2, -2), (-3, -4), (-4, -4), (-5, -6),
        # Positive floats
        (0.5, 0), (1.5, 0), (2.5, 2), (3.5, 2), (4.5, 4),
        # Negative floats
        (-0.5, -2), (-1.5, -2), (-2.5, -4), (-3.5, -4), (-4.5, -6),
        # Edge cases
        (0, 0), (0.0, 0), (-0.0, 0),
        # Large numbers
        (999, 998), (1000, 1000), (1001, 1000),
        (-999, -1000), (-1000, -1000), (-1001, -1002)
    ])
    def test_comprehensive_values(self, input_val, expected):
        """Comprehensive parametrized test."""
        assert to_even(input_val) == expected
    
    @pytest.mark.parametrize("offset", [0.1, 0.5, 0.9])
    def test_float_offsets(self, offset):
        """Test consistent behavior with different decimal offsets."""
        # Positive offsets from odd numbers
        assert to_even(1 + offset) == 0
        assert to_even(3 + offset) == 2
        assert to_even(5 + offset) == 4
        
        # Positive offsets from even numbers
        assert to_even(2 + offset) == 2
        assert to_even(4 + offset) == 4
        assert to_even(6 + offset) == 6
        
        # Negative offsets
        assert to_even(-1 - offset) == -2
        assert to_even(-3 - offset) == -4
        assert to_even(-2 - offset) == -4


class TestToEvenPerformance:
    """Test performance characteristics."""
    
    def test_large_array_processing(self):
        """Test with large arrays of values."""
        # Create large array
        values = list(range(10000))
        
        # Process all values
        results = [to_even(v) for v in values]
        
        # Verify some results
        assert results[0] == 0
        assert results[1] == 0
        assert results[2] == 2
        assert results[999] == 998
        assert results[1000] == 1000
    
    def test_repeated_calls(self):
        """Test repeated calls with same values."""
        # Should handle repeated calls efficiently
        value = 12345
        
        results = []
        for _ in range(100):
            results.append(to_even(value))
        
        # All results should be the same
        assert all(r == 12344 for r in results)


class TestToEvenErrorHandling:
    """Test error handling and invalid inputs."""
    
    def test_string_input(self):
        """Test with string input."""
        with pytest.raises((TypeError, ValueError)):
            to_even("5")
    
    def test_none_input(self):
        """Test with None input."""
        with pytest.raises((TypeError, AttributeError)):
            to_even(None)
    
    def test_list_input(self):
        """Test with list input."""
        with pytest.raises((TypeError, ValueError)):
            to_even([1, 2, 3])
    
    def test_dict_input(self):
        """Test with dictionary input."""
        with pytest.raises((TypeError, ValueError)):
            to_even({"value": 5})
    
    def test_custom_object(self):
        """Test with custom object."""
        class CustomNumber:
            def __init__(self, value):
                self.value = value
            
            def __int__(self):
                return self.value
        
        # If object has __int__, it might work
        try:
            result = to_even(CustomNumber(5))
            assert result == 4
        except (TypeError, AttributeError):
            # Expected if custom objects not supported
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])