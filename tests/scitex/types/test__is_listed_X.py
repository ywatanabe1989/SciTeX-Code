#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 14:00:00 (claude)"
# File: ./tests/scitex/types/test__is_listed_X.py
# ----------------------------------------

"""
Comprehensive test suite for scitex.types._is_listed_X module.

This module tests the is_listed_X function which validates whether an object
is a list where all elements are of specified types.

Test Structure:
- Basic functionality tests
- Type validation tests  
- Edge case handling
- Error handling and robustness
- Performance considerations
"""

import pytest
import numpy as np
from src.scitex.types._is_listed_X import is_listed_X


class TestIsListedX:
    """Test cases for the is_listed_X function."""
    
    def test_function_exists(self):
        """Test that the is_listed_X function exists and is callable."""
        assert callable(is_listed_X), "is_listed_X should be callable"
    
    def test_simple_integer_list(self):
        """Test with simple integer list."""
        obj = [1, 2, 3, 4, 5]
        assert is_listed_X(obj, int) == True
        
    def test_simple_string_list(self):
        """Test with simple string list."""
        obj = ["a", "b", "c"]
        assert is_listed_X(obj, str) == True
        
    def test_simple_float_list(self):
        """Test with simple float list."""
        obj = [1.0, 2.5, 3.14]
        assert is_listed_X(obj, float) == True
        
    def test_mixed_type_list_single_type(self):
        """Test mixed type list against single type (should fail)."""
        obj = [1, "a", 3.0]
        assert is_listed_X(obj, int) == False
        assert is_listed_X(obj, str) == False
        assert is_listed_X(obj, float) == False
        
    def test_multiple_allowed_types_tuple(self):
        """Test with multiple allowed types as tuple."""
        # All integers - should work with tuple containing int
        obj = [1, 2, 3]
        assert is_listed_X(obj, (int, float)) == True
        
        # All floats - should work with tuple containing float
        obj = [1.0, 2.5, 3.14]
        assert is_listed_X(obj, (int, float)) == True
        
        # Mixed types - should fail because not all elements are the same type
        obj = [1, 2.5, 3]
        assert is_listed_X(obj, (int, float)) == False
        
    def test_multiple_allowed_types_list(self):
        """Test with multiple allowed types as list."""
        # All integers - should work with list containing int
        obj = [1, 2, 3]
        assert is_listed_X(obj, [int, float]) == True
        
        # All floats - should work with list containing float
        obj = [1.0, 2.5, 3.14]
        assert is_listed_X(obj, [int, float]) == True
        
        # Mixed types - should fail because not all elements are the same type
        obj = [1, 2.5, 3]
        assert is_listed_X(obj, [int, float]) == False
        
    def test_empty_list(self):
        """Test with empty list."""
        obj = []
        # Empty list should return True for any type since all elements satisfy condition
        assert is_listed_X(obj, int) == True
        assert is_listed_X(obj, str) == True
        assert is_listed_X(obj, (int, float)) == True
        
    def test_non_list_objects(self):
        """Test with non-list objects."""
        assert is_listed_X("not a list", int) == False
        assert is_listed_X(123, int) == False
        assert is_listed_X({"a": 1}, int) == False
        assert is_listed_X((1, 2, 3), int) == False  # tuple, not list
        assert is_listed_X(np.array([1, 2, 3]), int) == False  # numpy array, not list
        
    def test_nested_lists(self):
        """Test with nested lists."""
        obj = [[1, 2], [3, 4]]
        assert is_listed_X(obj, list) == True
        assert is_listed_X(obj, int) == False
        
    def test_list_with_none_values(self):
        """Test list containing None values."""
        obj = [1, None, 3]
        assert is_listed_X(obj, int) == False
        # Mixed int and None - should fail because not all are same type
        assert is_listed_X(obj, (int, type(None))) == False
        
        # All None values - should work
        obj = [None, None, None]
        assert is_listed_X(obj, (int, type(None))) == True
        assert is_listed_X(obj, type(None)) == True
        
    def test_complex_types(self):
        """Test with complex Python types."""
        obj = [complex(1, 2), complex(3, 4)]
        assert is_listed_X(obj, complex) == True
        assert is_listed_X(obj, int) == False
        
    def test_bool_type_inheritance(self):
        """Test boolean type (which inherits from int in Python)."""
        obj = [True, False, True]
        assert is_listed_X(obj, bool) == True
        # Note: bool is subclass of int, so this should also be True
        assert is_listed_X(obj, int) == True
        
    def test_numpy_types(self):
        """Test with numpy numeric types."""
        obj = [np.int32(1), np.int32(2), np.int32(3)]
        assert is_listed_X(obj, np.int32) == True
        # Test compatibility with standard int
        assert is_listed_X(obj, int) == False  # numpy types are not standard int
        
    def test_custom_class_instances(self):
        """Test with custom class instances."""
        class CustomClass:
            def __init__(self, value):
                self.value = value
                
        obj1 = CustomClass(1)
        obj2 = CustomClass(2)
        obj = [obj1, obj2]
        
        assert is_listed_X(obj, CustomClass) == True
        assert is_listed_X(obj, int) == False
        
    def test_exception_handling(self):
        """Test exception handling with problematic inputs."""
        # Test with None as obj
        assert is_listed_X(None, int) == False
        
        # Test with unhashable types that might cause issues
        class ProblematicClass:
            def __hash__(self):
                raise TypeError("Unhashable type")
                
        problematic_obj = ProblematicClass()
        obj = [problematic_obj]
        
        # Should handle exceptions gracefully
        result = is_listed_X(obj, ProblematicClass)
        assert isinstance(result, (bool, np.bool_))  # Should return boolean, not raise exception
        
    def test_large_list_performance(self):
        """Test performance with large list."""
        obj = list(range(1000))  # Large list of integers
        assert is_listed_X(obj, int) == True
        assert is_listed_X(obj, str) == False
        
    def test_mixed_numeric_types(self):
        """Test with mixed numeric types."""
        obj = [1, 2.0, 3]
        # Mixed int and float - should fail because not all are same type
        assert is_listed_X(obj, (int, float)) == False
        assert is_listed_X(obj, int) == False  # contains float
        assert is_listed_X(obj, float) == False  # contains int
        
        # Test all same type but with multiple allowed
        obj = [1, 2, 3]  # all int
        assert is_listed_X(obj, (int, float)) == True
        obj = [1.0, 2.0, 3.0]  # all float
        assert is_listed_X(obj, (int, float)) == True
        
    def test_string_variations(self):
        """Test with different string types."""
        obj = ["hello", "world", "test"]
        assert is_listed_X(obj, str) == True
        assert is_listed_X(obj, bytes) == False
        
    def test_bytes_objects(self):
        """Test with bytes objects."""
        obj = [b"hello", b"world"]
        assert is_listed_X(obj, bytes) == True
        assert is_listed_X(obj, str) == False
        
    def test_function_objects(self):
        """Test with function objects."""
        def func1():
            pass
            
        def func2():
            pass
            
        obj = [func1, func2]
        assert is_listed_X(obj, type(func1)) == True
        
    def test_edge_case_single_element(self):
        """Test with single element lists."""
        assert is_listed_X([1], int) == True
        assert is_listed_X([1], str) == False
        assert is_listed_X(["a"], str) == True
        assert is_listed_X(["a"], int) == False
        
    def test_return_type_validation(self):
        """Test that function always returns boolean."""
        test_cases = [
            ([1, 2, 3], int),
            (["a", "b"], str),
            ([1, "a"], int),
            (None, int),
            ("not_a_list", str),
            ([], int)
        ]
        
        for obj, types in test_cases:
            result = is_listed_X(obj, types)
            assert isinstance(result, (bool, np.bool_)), f"Expected bool, got {type(result)} for {obj}, {types}"

    def test_docstring_examples(self):
        """Test examples from the function's docstring."""
        obj = [3, 2, 1, 5]
        assert is_listed_X(obj, int) == True
        assert is_listed_X(obj, (int, float)) == True
        assert is_listed_X(obj, str) == False


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
