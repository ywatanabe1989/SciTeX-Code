#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:54:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__cache_mem.py

"""Tests for memory caching decorator functionality."""

import pytest
import time
from unittest.mock import patch, MagicMock


class TestCacheMem:
    """Test cases for scitex.decorators._cache_mem module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Clear any existing cache before each test
        self.call_count = 0

    def test_cache_mem_import(self):
        """Test that cache_mem can be imported successfully."""
        from scitex.decorators import cache_mem
        assert callable(cache_mem)

    def test_cache_mem_basic_functionality(self):
        """Test basic caching functionality with simple function."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def simple_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute the function
        result1 = simple_func(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call with same argument should use cache
        result2 = simple_func(5)
        assert result2 == 10
        assert call_count == 1  # No additional function call
        
        # Call with different argument should execute function again
        result3 = simple_func(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_mem_multiple_arguments(self):
        """Test caching with multiple arguments."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def multi_arg_func(x, y, z=10):
            nonlocal call_count
            call_count += 1
            return x + y + z
        
        # Test with positional arguments
        result1 = multi_arg_func(1, 2)
        assert result1 == 13
        assert call_count == 1
        
        # Same arguments should use cache
        result2 = multi_arg_func(1, 2)
        assert result2 == 13
        assert call_count == 1
        
        # Different z value should execute function
        result3 = multi_arg_func(1, 2, z=20)
        assert result3 == 23
        assert call_count == 2
        
        # Keyword arguments should be cached separately
        result4 = multi_arg_func(1, 2, z=20)
        assert result4 == 23
        assert call_count == 2  # Should use cache

    def test_cache_mem_with_keyword_arguments(self):
        """Test caching behavior with keyword arguments."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def keyword_func(a, b=5, c=10):
            nonlocal call_count
            call_count += 1
            return a * b + c
        
        # Test different ways of calling the same function
        result1 = keyword_func(2, b=3, c=4)
        assert result1 == 10
        assert call_count == 1
        
        # Same call should use cache
        result2 = keyword_func(2, b=3, c=4)
        assert result2 == 10
        assert call_count == 1
        
        # Different order of keyword args (may create different cache entries)
        result3 = keyword_func(2, c=4, b=3)
        assert result3 == 10
        assert call_count <= 2  # May be cached or may be a new entry

    def test_cache_mem_return_types(self):
        """Test caching with different return types."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def return_various_types(type_name):
            nonlocal call_count
            call_count += 1
            
            if type_name == "list":
                return [1, 2, 3]
            elif type_name == "dict":
                return {"key": "value"}
            elif type_name == "tuple":
                return (1, 2, 3)
            elif type_name == "none":
                return None
            else:
                return type_name
        
        # Test list return
        result1 = return_various_types("list")
        assert result1 == [1, 2, 3]
        assert call_count == 1
        
        result2 = return_various_types("list")
        assert result2 == [1, 2, 3]
        assert call_count == 1  # Should use cache
        
        # Test dict return
        result3 = return_various_types("dict")
        assert result3 == {"key": "value"}
        assert call_count == 2
        
        # Test None return
        result4 = return_various_types("none")
        assert result4 is None
        assert call_count == 3
        
        result5 = return_various_types("none")
        assert result5 is None
        assert call_count == 3  # Should use cache

    def test_cache_mem_with_mutable_arguments(self):
        """Test caching behavior with mutable arguments."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def process_list(lst):
            nonlocal call_count
            call_count += 1
            return sum(lst)
        
        # Test with list argument
        list1 = [1, 2, 3]
        result1 = process_list(tuple(list1))  # Convert to tuple for hashability
        assert result1 == 6
        assert call_count == 1
        
        # Same tuple should use cache
        result2 = process_list(tuple(list1))
        assert result2 == 6
        assert call_count == 1

    def test_cache_mem_performance_improvement(self):
        """Test that caching actually improves performance."""
        from scitex.decorators import cache_mem
        
        @cache_mem
        def slow_function(n):
            # Simulate slow computation
            time.sleep(0.01)  # 10ms delay
            return n ** 2
        
        # Time first call
        start_time = time.time()
        result1 = slow_function(5)
        first_call_time = time.time() - start_time
        
        # Time second call (should be much faster due to caching)
        start_time = time.time()
        result2 = slow_function(5)
        second_call_time = time.time() - start_time
        
        assert result1 == result2 == 25
        assert second_call_time < first_call_time / 2  # Should be significantly faster

    def test_cache_mem_cache_info(self):
        """Test cache_info functionality."""
        from scitex.decorators import cache_mem
        
        @cache_mem
        def test_func(x):
            return x * 2
        
        # Check that cache_info is available
        assert hasattr(test_func, 'cache_info')
        
        # Initial cache should be empty
        info = test_func.cache_info()
        assert info.hits == 0
        assert info.misses == 0
        
        # After first call
        test_func(5)
        info = test_func.cache_info()
        assert info.hits == 0
        assert info.misses == 1
        
        # After second call with same argument
        test_func(5)
        info = test_func.cache_info()
        assert info.hits == 1
        assert info.misses == 1

    def test_cache_mem_cache_clear(self):
        """Test cache clearing functionality."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Make some calls
        test_func(5)
        test_func(5)  # Should use cache
        assert call_count == 1
        
        # Clear cache
        test_func.cache_clear()
        
        # Next call should execute function again
        test_func(5)
        assert call_count == 2

    def test_cache_mem_unlimited_size(self):
        """Test that cache has unlimited size (maxsize=None)."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x
        
        # Make many unique calls
        for i in range(1000):
            test_func(i)
        
        assert call_count == 1000
        
        # All previous calls should still be cached
        for i in range(1000):
            test_func(i)
        
        assert call_count == 1000  # No additional calls

    def test_cache_mem_exception_handling(self):
        """Test caching behavior when function raises exceptions."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def error_func(x):
            nonlocal call_count
            call_count += 1
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        # Function that raises exception
        with pytest.raises(ValueError):
            error_func(-1)
        assert call_count == 1
        
        # Exception should not be cached (function should be called again)
        with pytest.raises(ValueError):
            error_func(-1)
        assert call_count == 2
        
        # Successful call should be cached
        result = error_func(5)
        assert result == 10
        assert call_count == 3
        
        result2 = error_func(5)
        assert result2 == 10
        assert call_count == 3  # Should use cache

    def test_cache_mem_with_class_methods(self):
        """Test caching with class methods."""
        from scitex.decorators import cache_mem
        
        class TestClass:
            def __init__(self):
                self.call_count = 0
            
            @cache_mem
            def cached_method(self, x):
                self.call_count += 1
                return x * 2
        
        obj = TestClass()
        
        # First call
        result1 = obj.cached_method(5)
        assert result1 == 10
        assert obj.call_count == 1
        
        # Second call should use cache
        result2 = obj.cached_method(5)
        assert result2 == 10
        assert obj.call_count == 1

    def test_cache_mem_function_attributes(self):
        """Test that decorated function preserves important attributes."""
        from scitex.decorators import cache_mem
        
        @cache_mem
        def documented_func(x):
            """This is a test function."""
            return x
        
        # Function should have cache-related attributes
        assert hasattr(documented_func, 'cache_info')
        assert hasattr(documented_func, 'cache_clear')
        assert callable(documented_func.cache_info)
        assert callable(documented_func.cache_clear)

    def test_cache_mem_is_lru_cache_wrapper(self):
        """Test that cache_mem is indeed a wrapper around lru_cache."""
        from scitex.decorators import cache_mem
        from functools import lru_cache
        
        # cache_mem should be an lru_cache with maxsize=None
        # Test by checking the actual functionality rather than object equality
        @cache_mem
        def test_func(x):
            return x * 2
        
        # Should have lru_cache attributes
        assert hasattr(test_func, 'cache_info')
        assert hasattr(test_func, 'cache_clear')
        
        # Cache info should have infinite maxsize
        info = test_func.cache_info()
        assert info.maxsize is None

    def test_cache_mem_concurrent_access(self):
        """Test caching behavior with concurrent-like access patterns."""
        from scitex.decorators import cache_mem
        
        call_count = 0
        
        @cache_mem
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Simulate multiple rapid calls
        results = []
        for _ in range(10):
            results.append(test_func(42))
        
        # All results should be the same
        assert all(r == 84 for r in results)
        # Function should only be called once
        assert call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
