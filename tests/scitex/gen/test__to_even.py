#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 19:45:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/gen/test__to_even.py

import pytest
import numpy as np
import sys
import math
import decimal
from typing import Union
from unittest.mock import patch, MagicMock
import warnings
from scitex.gen import to_even


class TestToEvenBasicFunctionality:
    """Test basic functionality of the to_even function."""

    def test_odd_integers(self):
        """Test conversion of odd integers to even."""
        assert to_even(1) == 0
        assert to_even(3) == 2
        assert to_even(5) == 4
        assert to_even(7) == 6
        assert to_even(99) == 98
        assert to_even(1001) == 1000

    def test_even_integers(self):
        """Test that even integers remain unchanged."""
        assert to_even(0) == 0
        assert to_even(2) == 2
        assert to_even(4) == 4
        assert to_even(6) == 6
        assert to_even(100) == 100
        assert to_even(1000) == 1000

    def test_negative_integers(self):
        """Test conversion of negative integers."""
        assert to_even(-1) == -2
        assert to_even(-2) == -2
        assert to_even(-3) == -4
        assert to_even(-4) == -4
        assert to_even(-99) == -100

    def test_floats(self):
        """Test conversion of float values."""
        assert to_even(3.7) == 2
        assert to_even(4.9) == 4
        assert to_even(5.1) == 4
        assert to_even(6.0) == 6
        assert to_even(2.3) == 2
        assert to_even(1.9) == 0

    def test_negative_floats(self):
        """Test conversion of negative float values."""
        assert to_even(-1.5) == -2
        assert to_even(-2.3) == -4
        assert to_even(-3.7) == -4
        assert to_even(-4.1) == -6

    def test_edge_cases(self):
        """Test edge cases and special values."""
        assert to_even(0) == 0
        assert to_even(0.0) == 0
        assert to_even(0.1) == 0
        assert to_even(-0.1) == -2

    def test_large_numbers(self):
        """Test with large numbers."""
        assert to_even(1000000) == 1000000
        assert to_even(1000001) == 1000000
        assert to_even(999999) == 999998
        assert to_even(1234567) == 1234566

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            (1, 0),
            (2, 2),
            (3.5, 2),
            (4.5, 4),
            (-1, -2),
            (-2, -2),
            (0, 0),
        ],
    )
    def test_parametrized(self, input_val, expected):
        """Parametrized test for various inputs."""
        assert to_even(input_val) == expected


class TestToEvenNumericTypes:
    """Test to_even with various numeric types."""
    
    def test_numpy_integers(self):
        """Test with numpy integer types."""
        assert to_even(np.int8(5)) == 4
        assert to_even(np.int16(7)) == 6
        assert to_even(np.int32(9)) == 8
        assert to_even(np.int64(11)) == 10
        assert to_even(np.uint8(13)) == 12
        assert to_even(np.uint16(15)) == 14
        assert to_even(np.uint32(17)) == 16
        assert to_even(np.uint64(19)) == 18
    
    def test_numpy_floats(self):
        """Test with numpy float types."""
        assert to_even(np.float16(3.5)) == 2
        assert to_even(np.float32(5.7)) == 4
        assert to_even(np.float64(7.9)) == 6
        if hasattr(np, 'float128'):
            assert to_even(np.float128(9.1)) == 8
    
    def test_numpy_arrays(self):
        """Test with numpy arrays (should work on scalar elements)."""
        # Single element arrays
        assert to_even(np.array(5)) == 4
        assert to_even(np.array(6)) == 6
        assert to_even(np.array([7])[0]) == 6
        assert to_even(np.array([8])[0]) == 8
    
    def test_python_numeric_types(self):
        """Test with various Python numeric types."""
        # Complex numbers should raise TypeError when converted to int
        with pytest.raises(TypeError):
            to_even(complex(5, 0))
        
        # Boolean values
        assert to_even(True) == 0  # True -> 1 -> 0
        assert to_even(False) == 0  # False -> 0 -> 0
        
        # Decimal
        assert to_even(decimal.Decimal('5.5')) == 4
        assert to_even(decimal.Decimal('6.0')) == 6
        assert to_even(decimal.Decimal('-3.7')) == -4


class TestToEvenEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_numbers(self):
        """Test with very large numbers."""
        assert to_even(10**18 + 1) == 10**18
        assert to_even(10**18) == 10**18
        assert to_even(2**31 - 1) == 2**31 - 2  # Max 32-bit int - 1
        assert to_even(2**31) == 2**31
        assert to_even(2**63 - 1) == 2**63 - 2  # Max 64-bit int - 1
    
    def test_very_small_negative_numbers(self):
        """Test with very small negative numbers."""
        assert to_even(-10**18 - 1) == -10**18 - 2
        assert to_even(-10**18) == -10**18
        assert to_even(-2**31 + 1) == -2**31
        assert to_even(-2**31) == -2**31
        assert to_even(-2**63 + 1) == -2**63
    
    def test_near_zero_values(self):
        """Test values very close to zero."""
        assert to_even(0.0001) == 0
        assert to_even(0.9999) == 0
        assert to_even(-0.0001) == -2
        assert to_even(-0.9999) == -2
        assert to_even(1e-10) == 0
        assert to_even(-1e-10) == -2
    
    def test_infinity_and_nan(self):
        """Test with infinity and NaN values."""
        # Positive infinity
        with pytest.raises(OverflowError):
            to_even(float('inf'))
        
        # Negative infinity
        with pytest.raises(OverflowError):
            to_even(float('-inf'))
        
        # NaN
        with pytest.raises(ValueError):
            to_even(float('nan'))
    
    def test_special_float_values(self):
        """Test special floating point values."""
        # Subnormal numbers
        assert to_even(sys.float_info.min) == 0
        assert to_even(-sys.float_info.min) == -2
        
        # Maximum float - Python can actually convert this to int
        # The result should be a very large even integer
        result = to_even(sys.float_info.max)
        assert isinstance(result, int)
        assert result % 2 == 0  # Should be even
        # Test actual overflow with infinity
        with pytest.raises(OverflowError):
            to_even(float('inf'))


class TestToEvenMathematicalProperties:
    """Test mathematical properties of the to_even function."""
    
    def test_idempotence(self):
        """Test that applying to_even twice gives the same result."""
        values = [1, 2, 3, 4, 5, -1, -2, -3, 3.5, -3.5]
        for val in values:
            result1 = to_even(val)
            result2 = to_even(result1)
            assert result1 == result2
    
    def test_monotonicity(self):
        """Test that to_even preserves order (is monotonic)."""
        values = [-10, -5, -1, 0, 1, 5, 10]
        results = [to_even(v) for v in values]
        assert all(results[i] <= results[i+1] for i in range(len(results)-1))
    
    def test_distance_property(self):
        """Test that result is at most 1 unit away from input."""
        values = [1, 2, 3, 4, 5, -1, -2, -3, 3.5, -3.5, 7.9, -7.9]
        for val in values:
            result = to_even(val)
            assert abs(int(val) - result) <= 1
    
    def test_parity_property(self):
        """Test that result is always even."""
        values = list(range(-100, 101)) + [x/10 for x in range(-100, 101)]
        for val in values:
            result = to_even(val)
            assert result % 2 == 0
    
    def test_floor_relationship(self):
        """Test relationship with floor function."""
        values = [3.2, 3.7, 4.0, 4.5, -3.2, -3.7, -4.0, -4.5]
        for val in values:
            result = to_even(val)
            floor_val = math.floor(val)
            if floor_val % 2 == 0:
                assert result == floor_val
            else:
                assert result == floor_val - 1


class TestToEvenErrorHandling:
    """Test error handling and invalid inputs."""
    
    def test_non_numeric_types(self):
        """Test with non-numeric types."""
        # Strings that can't be converted to numbers
        with pytest.raises((TypeError, ValueError)):
            to_even("hello")
        
        with pytest.raises(TypeError):
            to_even([1, 2, 3])
        
        with pytest.raises(TypeError):
            to_even({1: 2})
        
        with pytest.raises(TypeError):
            to_even(None)
    
    def test_string_numbers(self):
        """Test with string representations of numbers."""
        # The implementation uses math.floor() which raises TypeError for strings
        with pytest.raises(TypeError):
            to_even("5")
        
        with pytest.raises(TypeError):
            to_even("5.5")
    
    def test_custom_objects(self):
        """Test with custom objects."""
        class CustomNumber:
            def __init__(self, value):
                self.value = value
            
            def __int__(self):
                return int(self.value)
        
        # Should work if object implements __int__
        assert to_even(CustomNumber(5)) == 4
        assert to_even(CustomNumber(6)) == 6
        
        # Object without __int__
        class BadObject:
            pass
        
        with pytest.raises(TypeError):
            to_even(BadObject())


class TestToEvenPerformance:
    """Test performance characteristics of to_even."""
    
    def test_performance_consistency(self):
        """Test that performance is consistent across input values."""
        import time
        
        # Test with different magnitudes
        test_values = [1, 100, 10000, 1000000]
        times = []
        
        for val in test_values:
            start = time.perf_counter()
            for _ in range(10000):
                to_even(val)
            end = time.perf_counter()
            times.append(end - start)
        
        # Check that times don't vary by more than 50%
        max_time = max(times)
        min_time = min(times)
        assert max_time < min_time * 1.5
    
    def test_batch_operations(self):
        """Test performance with batch operations."""
        # Create test data
        values = list(range(1000))
        
        # Time the operation
        import time
        start = time.perf_counter()
        results = [to_even(v) for v in values]
        end = time.perf_counter()
        
        # Verify results
        assert len(results) == len(values)
        assert all(r % 2 == 0 for r in results)
        
        # Performance should be reasonable (< 0.1 seconds for 1000 values)
        assert end - start < 0.1


class TestToEvenAlgorithmVerification:
    """Verify the algorithm implementation."""
    
    def test_algorithm_formula(self):
        """Test that the algorithm follows the formula: int(n) - (int(n) % 2)."""
        test_values = [0, 1, 2, 3, 4, 5, -1, -2, -3, -4, 3.5, -3.5, 7.9, -7.9]
        
        for val in test_values:
            expected = int(val) - (int(val) % 2)
            assert to_even(val) == expected
    
    def test_modulo_behavior(self):
        """Test understanding of modulo with negative numbers."""
        # Python's modulo with negative numbers
        assert (-1) % 2 == 1  # Not -1
        assert (-3) % 2 == 1
        assert (-2) % 2 == 0
        assert (-4) % 2 == 0
        
        # Verify to_even handles this correctly
        assert to_even(-1) == -1 - 1  # -2
        assert to_even(-3) == -3 - 1  # -4
        assert to_even(-2) == -2 - 0  # -2
        assert to_even(-4) == -4 - 0  # -4


class TestToEvenDocumentation:
    """Test documentation and examples."""
    
    def test_docstring_examples(self):
        """Test examples from the docstring."""
        # From docstring:
        # >>> to_even(5)
        # 4
        assert to_even(5) == 4
        
        # >>> to_even(6)
        # 6
        assert to_even(6) == 6
        
        # >>> to_even(3.7)
        # 2
        assert to_even(3.7) == 2
    
    def test_function_signature(self):
        """Test function signature and attributes."""
        import inspect
        
        # Check function exists and is callable
        assert callable(to_even)
        
        # Check signature
        sig = inspect.signature(to_even)
        params = list(sig.parameters.keys())
        assert len(params) == 1
        assert params[0] == 'n'
        
        # Check docstring exists
        assert to_even.__doc__ is not None
        assert "Convert a number to the nearest even number" in to_even.__doc__


class TestToEvenIntegration:
    """Test integration with other parts of the system."""
    
    def test_import_from_package(self):
        """Test different import methods."""
        # Direct import
        from scitex.gen import to_even as to_even1
        
        # Import module then access
        import scitex.gen
        to_even2 = scitex.gen.to_even
        
        # Both should be the same function
        assert to_even1 is to_even2
        
        # Both should work correctly
        assert to_even1(5) == 4
        assert to_even2(5) == 4
    
    def test_with_other_gen_functions(self):
        """Test interaction with other gen module functions."""
        # Test with to_odd if it exists
        try:
            from scitex.gen import to_odd
            # to_even and to_odd should have complementary behavior
            for val in [1, 2, 3, 4, 5, 6]:
                even_result = to_even(val)
                assert even_result % 2 == 0
                # If to_odd exists, verify relationship
                odd_result = to_odd(val)
                assert odd_result % 2 == 1
                assert abs(even_result - odd_result) == 1
        except ImportError:
            # to_odd might not exist, that's okay
            pass
    
    def test_type_consistency(self):
        """Test that return type is always int."""
        test_inputs = [
            1, 2, 3.5, 4.5, -1, -2.5,
            np.float32(5.5), np.int64(6),
            True, False,
            decimal.Decimal('7.5')
        ]
        
        for inp in test_inputs:
            result = to_even(inp)
            assert isinstance(result, int)
            assert not isinstance(result, bool)  # bool is subclass of int


class TestToEvenRobustness:
    """Test robustness and edge cases."""
    
    def test_thread_safety(self):
        """Test basic thread safety (function should be stateless)."""
        import threading
        results = []
        
        def worker(value):
            result = to_even(value)
            results.append((value, result))
        
        threads = []
        test_values = list(range(100))
        
        for val in test_values:
            t = threading.Thread(target=worker, args=(val,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all results are correct
        assert len(results) == len(test_values)
        for val, result in results:
            expected = int(val) - (int(val) % 2)
            assert result == expected
    
    def test_repeated_calls(self):
        """Test repeated calls with same and different values."""
        # Same value repeatedly
        for _ in range(100):
            assert to_even(5) == 4
            assert to_even(6) == 6
        
        # Different values
        for i in range(100):
            result = to_even(i)
            assert result % 2 == 0
            assert result <= i
            assert i - result <= 1
    
    def test_memory_efficiency(self):
        """Test that function doesn't leak memory."""
        import gc
        
        # Get initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Call function many times
        for i in range(1000):
            to_even(i)
        
        # Check object count hasn't grown significantly
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Allow some growth for test infrastructure
        assert final_objects - initial_objects < 100

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_to_even.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 23:40:12 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_to_even.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_to_even.py"
# 
# 
# def to_even(n):
#     """Convert a number to the nearest even number less than or equal to itself.
# 
#     Parameters
#     ----------
#     n : int or float
#         The input number to be converted.
# 
#     Returns
#     -------
#     int
#         The nearest even number less than or equal to the input.
# 
#     Example
#     -------
#     >>> to_even(5)
#     4
#     >>> to_even(6)
#     6
#     >>> to_even(3.7)
#     2
#     >>> to_even(-2.3)
#     -4
#     >>> to_even(-0.1)
#     -2
#     """
#     import math
#     
#     # Handle integers directly to avoid float conversion issues with large numbers
#     # Note: bool is a subclass of int, so we need to exclude it
#     if isinstance(n, int) and not isinstance(n, bool):
#         if n % 2 == 0:
#             return int(n)  # Ensure we return int, not bool
#         else:
#             return int(n - 1)  # Ensure we return int, not bool
#     
#     # Handle special float values
#     if isinstance(n, float):
#         if math.isnan(n):
#             raise ValueError("Cannot convert NaN to even")
#         if math.isinf(n):
#             raise OverflowError("Cannot convert infinity to even")
#         # Python can actually convert sys.float_info.max to int, so we don't need this check
#         # Only infinity truly can't be converted
#     
#     # Try to handle custom objects with __int__ (but not float types)
#     if hasattr(n, '__int__') and not isinstance(n, (float, bool)):
#         try:
#             n_int = int(n)
#             if n_int % 2 == 0:
#                 return int(n_int)
#             else:
#                 return int(n_int - 1)
#         except:
#             pass
#     
#     # Check for string type explicitly - raise TypeError
#     if isinstance(n, str):
#         raise TypeError(f"must be real number, not {type(n).__name__}")
#     
#     # Convert to float for all other cases
#     try:
#         n_float = float(n)
#     except (TypeError, ValueError):
#         raise TypeError(f"must be real number, not {type(n).__name__}")
#     
#     # Use floor for float values
#     floored = int(math.floor(n_float))
#     
#     # If odd, subtract 1 to get the next lower even number
#     if floored % 2 != 0:
#         return int(floored - 1)  # Ensure we return int, not bool
#     return int(floored)  # Ensure we return int, not bool
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_to_even.py
# --------------------------------------------------------------------------------
