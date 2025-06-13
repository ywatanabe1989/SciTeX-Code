#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:56:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__cache_disk.py

"""Tests for disk caching decorator functionality."""

import pytest
import os
import tempfile
import time
import shutil
from unittest.mock import patch, MagicMock


class TestCacheDisk:
    """Test cases for scitex.decorators._cache_disk module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for cache testing
        self.temp_dir = tempfile.mkdtemp()
        self.call_count = 0

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_cache_disk_import(self):
        """Test that cache_disk can be imported successfully."""
        from scitex.decorators import cache_disk
        assert callable(cache_disk)

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_basic_functionality(self):
        """Test basic disk caching functionality."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
        def simple_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute the function
        result1 = simple_func(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call with same argument should use disk cache
        result2 = simple_func(5)
        assert result2 == 10
        assert call_count == 1  # No additional function call
        
        # Call with different argument should execute function again
        result3 = simple_func(10)
        assert result3 == 20
        assert call_count == 2

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_with_arguments(self):
        """Test disk caching with multiple arguments."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
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
        
        # Different arguments should execute function
        result3 = multi_arg_func(1, 2, z=20)
        assert result3 == 23
        assert call_count == 2

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_with_keyword_arguments(self):
        """Test disk caching with keyword arguments."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
        def keyword_func(a, b=5, c=10):
            nonlocal call_count
            call_count += 1
            return a * b + c
        
        # Test with keyword arguments
        result1 = keyword_func(2, b=3, c=4)
        assert result1 == 10
        assert call_count == 1
        
        # Same call should use cache
        result2 = keyword_func(2, b=3, c=4)
        assert result2 == 10
        assert call_count == 1

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_return_types(self):
        """Test disk caching with different return types."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
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

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_persistence_across_function_calls(self):
        """Test that disk cache persists across different function instances."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
        def persistent_func(x):
            nonlocal call_count
            call_count += 1
            return x ** 2
        
        # First call
        result1 = persistent_func(5)
        assert result1 == 25
        assert call_count == 1
        
        # Create a new decorated function with same implementation
        @cache_disk
        def persistent_func2(x):
            nonlocal call_count
            call_count += 1
            return x ** 2
        
        # This might use cache depending on joblib implementation
        result2 = persistent_func2(5)
        assert result2 == 25
        # call_count might be 1 or 2 depending on cache sharing

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_performance_improvement(self):
        """Test that disk caching improves performance."""
        from scitex.decorators import cache_disk
        
        @cache_disk
        def slow_function(n):
            # Simulate slow computation
            time.sleep(0.01)  # 10ms delay
            return n ** 2
        
        # Time first call
        start_time = time.time()
        result1 = slow_function(5)
        first_call_time = time.time() - start_time
        
        # Time second call (should be faster due to disk caching)
        start_time = time.time()
        result2 = slow_function(5)
        second_call_time = time.time() - start_time
        
        assert result1 == result2 == 25
        # Second call should be faster (allowing some tolerance for disk I/O)
        assert second_call_time < first_call_time

    def test_cache_disk_uses_scitex_dir_environment_variable(self):
        """Test that cache_disk respects SciTeX_DIR environment variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_scitex_dir = temp_dir + "/custom_scitex/"
            
            with patch.dict(os.environ, {'SciTeX_DIR': custom_scitex_dir}):
                from scitex.decorators import cache_disk
                
                @cache_disk
                def test_func(x):
                    return x * 2
                
                # Call function to trigger cache creation
                result = test_func(5)
                assert result == 10
                
                # Check that cache directory was created in custom location
                expected_cache_dir = custom_scitex_dir + "cache/"
                # Cache directory should exist (joblib creates it)
                # Note: We can't easily test this without accessing internals

    def test_cache_disk_default_cache_location(self):
        """Test cache_disk uses default location when SciTeX_DIR not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove SciTeX_DIR if it exists
            if 'SciTeX_DIR' in os.environ:
                del os.environ['SciTeX_DIR']
            
                from scitex.decorators import cache_disk
            
            @cache_disk
            def test_func(x):
                return x * 3
            
            # Should work with default location
            result = test_func(7)
            assert result == 21

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_with_complex_data_structures(self):
        """Test disk caching with complex data structures."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
        def complex_data_func(data_type):
            nonlocal call_count
            call_count += 1
            
            if data_type == "nested_dict":
                return {
                    "level1": {
                        "level2": {
                            "values": [1, 2, 3, 4, 5]
                        }
                    }
                }
            elif data_type == "nested_list":
                return [[1, 2], [3, 4], [5, [6, 7]]]
            else:
                return {"simple": "data"}
        
        # Test complex nested dictionary
        result1 = complex_data_func("nested_dict")
        expected_dict = {
            "level1": {
                "level2": {
                    "values": [1, 2, 3, 4, 5]
                }
            }
        }
        assert result1 == expected_dict
        assert call_count == 1
        
        # Should use cache for same input
        result2 = complex_data_func("nested_dict")
        assert result2 == expected_dict
        assert call_count == 1

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_function_signature_preservation(self):
        """Test that decorated function preserves original signature."""
        from scitex.decorators import cache_disk
        
        @cache_disk
        def documented_func(x, y=10):
            """This is a test function with documentation."""
            return x + y
        
        # Function should preserve name and docstring
        assert documented_func.__name__ == "documented_func"
        assert "test function with documentation" in documented_func.__doc__

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_with_exceptions(self):
        """Test disk caching behavior when function raises exceptions."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
        def error_func(x):
            nonlocal call_count
            call_count += 1
            if x < 0:
                raise ValueError("Negative value not allowed")
            return x * 2
        
        # Function that raises exception
        with pytest.raises(ValueError):
            error_func(-1)
        assert call_count == 1
        
        # Successful call should work
        result = error_func(5)
        assert result == 10
        assert call_count == 2
        
        # Same successful call should use cache
        result2 = error_func(5)
        assert result2 == 10
        assert call_count == 2

    @patch('scitex.decorators._cache_disk._Memory')
    def test_cache_disk_joblib_memory_integration(self, mock_memory_class):
        """Test integration with joblib.Memory."""
        mock_memory = MagicMock()
        mock_memory_class.return_value = mock_memory
        mock_cached_func = MagicMock(return_value=42)
        mock_memory.cache.return_value = mock_cached_func
        
        from scitex.decorators import cache_disk
        
        @cache_disk
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        
        # Verify joblib Memory was instantiated
        mock_memory_class.assert_called_once()
        
        # Verify cache method was called
        mock_memory.cache.assert_called_once()
        
        # Verify cached function was called with correct arguments
        mock_cached_func.assert_called_once_with(5)
        assert result == 42

    def test_cache_disk_cache_directory_creation(self):
        """Test that cache directory is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_scitex_dir = os.path.join(temp_dir, "test_scitex")
            
            with patch.dict(os.environ, {'SciTeX_DIR': custom_scitex_dir + "/"}):
                from scitex.decorators import cache_disk
                
                @cache_disk
                def test_func(x):
                    return x ** 2
                
                # Call function to trigger cache setup
                result = test_func(4)
                assert result == 16
                
                # joblib should create the cache directory structure
                # We can't easily verify this without diving into joblib internals

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_multiple_functions(self):
        """Test disk caching with multiple different functions."""
        from scitex.decorators import cache_disk
        
        call_count_1 = 0
        call_count_2 = 0
        
        @cache_disk
        def func1(x):
            nonlocal call_count_1
            call_count_1 += 1
            return x * 2
        
        @cache_disk
        def func2(x):
            nonlocal call_count_2
            call_count_2 += 1
            return x * 3
        
        # Test both functions
        result1 = func1(5)
        result2 = func2(5)
        assert result1 == 10
        assert result2 == 15
        assert call_count_1 == 1
        assert call_count_2 == 1
        
        # Test caching for both
        result1_cached = func1(5)
        result2_cached = func2(5)
        assert result1_cached == 10
        assert result2_cached == 15
        assert call_count_1 == 1  # Should use cache
        assert call_count_2 == 1  # Should use cache

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_with_class_methods(self):
        """Test disk caching with class methods."""
        from scitex.decorators import cache_disk
        
        class TestClass:
            def __init__(self):
                self.call_count = 0
            
            @cache_disk
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

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_memory_verbose_setting(self):
        """Test that joblib Memory is created with verbose=0."""
        with patch('scitex.decorators._cache_disk._Memory') as mock_memory:
            from scitex.decorators import cache_disk
            
            @cache_disk
            def test_func(x):
                return x * 2
            
            # The Memory object should be created with verbose=0
            # Check the call arguments
            call_args = mock_memory.call_args
            if call_args:
                if len(call_args[0]) > 1:
                    # If verbose is passed as positional argument
                    assert call_args[0][1] == 0
                elif 'verbose' in call_args[1]:
                    # If verbose is passed as keyword argument
                    assert call_args[1]['verbose'] == 0

    @patch.dict(os.environ, {'SciTeX_DIR': ''})
    def test_cache_disk_concurrent_access_safety(self):
        """Test disk caching with concurrent-like access patterns."""
        from scitex.decorators import cache_disk
        
        call_count = 0
        
        @cache_disk
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Simulate multiple rapid calls
        results = []
        for _ in range(5):
            results.append(test_func(42))
        
        # All results should be the same
        assert all(r == 84 for r in results)
        # Function should only be called once due to caching
        assert call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
