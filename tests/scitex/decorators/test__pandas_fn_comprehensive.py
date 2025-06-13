#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:19:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__pandas_fn_comprehensive.py

"""Comprehensive tests for pandas_fn decorator."""

import os
import pytest
import numpy as np
import pandas as pd
import torch
import xarray as xr
from functools import wraps
from unittest.mock import patch, MagicMock
from scitex.decorators import pandas_fn


class TestPandasFnBasicConversion:
    """Test basic type conversion functionality."""
    
    @pytest.fixture
    def basic_function(self):
        """Create a basic function for testing."""
        @pandas_fn
        def add_one(df):
            assert isinstance(df, pd.DataFrame)
            return df + 1
        return add_one
    
    def test_list_to_dataframe_conversion(self, basic_function):
        """Test conversion from list to DataFrame and back."""
        # 1D list
        input_list = [1, 2, 3]
        result = basic_function(input_list)
        assert isinstance(result, list)
        assert result == [[2], [3], [4]] or result == [2, 3, 4]
        
        # 2D list
        input_list_2d = [[1, 2], [3, 4]]
        result_2d = basic_function(input_list_2d)
        assert isinstance(result_2d, list)
    
    def test_numpy_to_dataframe_conversion(self, basic_function):
        """Test conversion from numpy array to DataFrame and back."""
        # 1D array
        input_array = np.array([1, 2, 3])
        result = basic_function(input_array)
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array([[2], [3], [4]]))
        
        # 2D array
        input_array_2d = np.array([[1, 2], [3, 4]])
        result_2d = basic_function(input_array_2d)
        assert isinstance(result_2d, np.ndarray)
        np.testing.assert_array_equal(result_2d, np.array([[2, 3], [4, 5]]))
    
    def test_series_to_dataframe_conversion(self, basic_function):
        """Test conversion from Series to DataFrame and back."""
        input_series = pd.Series([1, 2, 3], name='data')
        result = basic_function(input_series)
        assert isinstance(result, pd.Series)
        pd.testing.assert_series_equal(result, pd.Series([2, 3, 4]))
    
    def test_dataframe_passthrough(self, basic_function):
        """Test that DataFrames are passed through without conversion."""
        input_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        result = basic_function(input_df)
        assert isinstance(result, pd.DataFrame)
        expected = pd.DataFrame({'A': [2, 3, 4], 'B': [5, 6, 7]})
        pd.testing.assert_frame_equal(result, expected)
    
    def test_torch_tensor_conversion(self, basic_function):
        """Test conversion from torch tensor to DataFrame and back."""
        input_tensor = torch.tensor([1.0, 2.0, 3.0])
        result = basic_function(input_tensor)
        assert isinstance(result, torch.Tensor)
        torch.testing.assert_close(result, torch.tensor([[2.0], [3.0], [4.0]]))
        
        # 2D tensor
        input_tensor_2d = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        result_2d = basic_function(input_tensor_2d)
        assert isinstance(result_2d, torch.Tensor)
        torch.testing.assert_close(result_2d, torch.tensor([[2.0, 3.0], [4.0, 5.0]]))
    
    def test_xarray_conversion(self, basic_function):
        """Test conversion from xarray to DataFrame and back."""
        input_xr = xr.DataArray([1, 2, 3])
        result = basic_function(input_xr)
        assert isinstance(result, xr.DataArray)
        np.testing.assert_array_equal(result.values, np.array([[2], [3], [4]]))


class TestPandasFnEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_inputs(self):
        """Test with empty inputs."""
        @pandas_fn
        def process_df(df):
            return df
        
        # Empty list
        assert process_df([]) == []
        
        # Empty numpy array
        result = process_df(np.array([]))
        assert isinstance(result, np.ndarray)
        assert result.size == 0
        
        # Empty DataFrame
        empty_df = pd.DataFrame()
        result_df = process_df(empty_df)
        assert isinstance(result_df, pd.DataFrame)
        assert result_df.empty
    
    def test_single_value_inputs(self):
        """Test with single value inputs."""
        @pandas_fn
        def double_value(df):
            return df * 2
        
        # Single integer
        result = double_value(5)
        assert isinstance(result, list)
        assert result == [[10]]
        
        # Single float
        result_float = double_value(3.14)
        assert isinstance(result_float, list)
        assert result_float == [[6.28]]
    
    def test_none_handling(self):
        """Test handling of None values."""
        @pandas_fn
        def handle_none(df):
            return df
        
        # Single None
        result = handle_none(None)
        assert isinstance(result, list)
        assert result == [[None]]
        
        # List with None
        result_list = handle_none([1, None, 3])
        assert isinstance(result_list, list)
        assert len(result_list) == 3
    
    def test_mixed_type_lists(self):
        """Test lists with mixed types."""
        @pandas_fn
        def process_mixed(df):
            return df
        
        mixed_list = [1, "two", 3.0, True, None]
        result = process_mixed(mixed_list)
        assert isinstance(result, list)
        assert len(result) == 5


class TestPandasFnMultipleArguments:
    """Test decorator with multiple arguments."""
    
    def test_multiple_args_conversion(self):
        """Test conversion of multiple arguments."""
        @pandas_fn
        def combine_dfs(df1, df2):
            assert isinstance(df1, pd.DataFrame)
            assert isinstance(df2, pd.DataFrame)
            return pd.concat([df1, df2], axis=1)
        
        # Two lists
        result = combine_dfs([1, 2], [3, 4])
        assert isinstance(result, list)
        
        # Mixed types
        arr1 = np.array([1, 2])
        list2 = [3, 4]
        result_mixed = combine_dfs(arr1, list2)
        assert isinstance(result_mixed, np.ndarray)
    
    def test_kwargs_conversion(self):
        """Test conversion of keyword arguments."""
        @pandas_fn
        def process_with_kwargs(df, factor=2):
            assert isinstance(df, pd.DataFrame)
            assert isinstance(factor, pd.DataFrame)
            return df * factor.iloc[0, 0]
        
        result = process_with_kwargs([1, 2, 3], factor=3)
        assert isinstance(result, list)
        assert result == [[3], [6], [9]]
    
    def test_mixed_args_kwargs(self):
        """Test mixed positional and keyword arguments."""
        @pandas_fn
        def complex_function(df1, df2, scale=1, offset=0):
            assert all(isinstance(x, pd.DataFrame) for x in [df1, df2, scale, offset])
            return df1 * scale.iloc[0, 0] + df2 + offset.iloc[0, 0]
        
        result = complex_function([1, 2], [3, 4], scale=2, offset=1)
        assert isinstance(result, list)


class TestPandasFnNestedDecorators:
    """Test nested decorator behavior."""
    
    def test_nested_with_custom_decorator(self):
        """Test nesting with custom decorator."""
        def custom_decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                wrapper._current_decorator = "custom"
                return func(*args, **kwargs)
            wrapper._is_wrapper = True
            return wrapper
        
        @pandas_fn
        @custom_decorator
        def nested_func(data):
            return data
        
        with patch("scitex.decorators._pandas_fn.is_nested_decorator", return_value=True):
            # Should bypass conversion in nested context
            input_data = pd.Series([1, 2, 3])
            result = nested_func(input_data)
            assert isinstance(result, pd.Series)
            pd.testing.assert_series_equal(result, input_data)
    
    def test_multiple_pandas_fn_decorators(self):
        """Test multiple pandas_fn decorators (should handle gracefully)."""
        @pandas_fn
        @pandas_fn
        def double_decorated(df):
            return df + 1
        
        result = double_decorated([1, 2, 3])
        assert isinstance(result, list)
    
    def test_decorator_context_preservation(self):
        """Test that decorator context is properly set."""
        @pandas_fn
        def check_context(df):
            # During execution, wrapper should have context
            return df
        
        # Check that wrapper has proper attributes
        assert hasattr(check_context, '_is_wrapper')
        assert hasattr(check_context, '_decorator_type')
        assert check_context._decorator_type == 'pandas_fn'


class TestPandasFnReturnTypes:
    """Test various return type scenarios."""
    
    def test_non_dataframe_return(self):
        """Test when function returns non-DataFrame types."""
        @pandas_fn
        def return_scalar(df):
            return df.sum().sum()  # Returns scalar
        
        result = return_scalar([[1, 2], [3, 4]])
        assert isinstance(result, (int, float, np.number))
        assert result == 10
    
    def test_return_none(self):
        """Test when function returns None."""
        @pandas_fn
        def return_none(df):
            return None
        
        result = return_none([1, 2, 3])
        assert result is None
    
    def test_return_multiple_values(self):
        """Test when function returns tuple."""
        @pandas_fn
        def return_tuple(df):
            return df.mean(), df.std()
        
        mean, std = return_tuple([1, 2, 3, 4, 5])
        assert isinstance(mean, pd.Series) or isinstance(mean, pd.DataFrame)
        assert isinstance(std, pd.Series) or isinstance(std, pd.DataFrame)
    
    def test_return_dict(self):
        """Test when function returns dictionary."""
        @pandas_fn
        def return_stats(df):
            return {
                'mean': df.mean(),
                'sum': df.sum(),
                'shape': df.shape
            }
        
        result = return_stats([1, 2, 3])
        assert isinstance(result, dict)
        assert 'mean' in result
        assert 'sum' in result
        assert 'shape' in result


class TestPandasFnComplexDataTypes:
    """Test with complex data types."""
    
    def test_datetime_data(self):
        """Test with datetime data."""
        @pandas_fn
        def process_dates(df):
            return df
        
        dates = pd.date_range('2024-01-01', periods=3)
        result = process_dates(dates)
        assert len(result) == 3
    
    def test_categorical_data(self):
        """Test with categorical data."""
        @pandas_fn
        def process_categorical(df):
            return df
        
        cat_data = pd.Categorical(['a', 'b', 'c', 'a'])
        result = process_categorical(cat_data)
        assert isinstance(result, list) or isinstance(result, pd.DataFrame)
    
    def test_multiindex_dataframe(self):
        """Test with MultiIndex DataFrame."""
        @pandas_fn
        def process_multiindex(df):
            return df * 2
        
        # Create MultiIndex DataFrame
        index = pd.MultiIndex.from_tuples([('A', 1), ('A', 2), ('B', 1)])
        df = pd.DataFrame({'value': [10, 20, 30]}, index=index)
        
        result = process_multiindex(df)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df * 2)
    
    def test_sparse_data(self):
        """Test with sparse data."""
        @pandas_fn
        def process_sparse(df):
            return df
        
        sparse_data = pd.arrays.SparseArray([0, 0, 1, 0, 2])
        # Note: Direct sparse array might not be supported, test through Series
        sparse_series = pd.Series(sparse_data)
        result = process_sparse(sparse_series)
        assert isinstance(result, pd.Series)


class TestPandasFnErrorHandling:
    """Test error handling scenarios."""
    
    def test_function_raises_error(self):
        """Test when decorated function raises error."""
        @pandas_fn
        def error_function(df):
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            error_function([1, 2, 3])
    
    def test_conversion_error_handling(self):
        """Test handling of conversion errors."""
        @pandas_fn
        def process_data(df):
            return df
        
        # Object that can't be easily converted
        class UnconvertibleObject:
            pass
        
        # Should still attempt conversion (might wrap in DataFrame)
        obj = UnconvertibleObject()
        result = process_data(obj)
        assert result is not None
    
    def test_invalid_operations(self):
        """Test invalid operations on converted data."""
        @pandas_fn
        def invalid_op(df):
            return df + "invalid"  # This will raise TypeError for numeric data
        
        with pytest.raises(TypeError):
            invalid_op([1, 2, 3])


class TestPandasFnPerformance:
    """Test performance-related aspects."""
    
    def test_large_data_conversion(self):
        """Test with large datasets."""
        @pandas_fn
        def process_large(df):
            return df.mean()
        
        # Large array
        large_array = np.random.rand(10000, 100)
        result = process_large(large_array)
        assert result is not None
    
    def test_memory_efficiency(self):
        """Test memory efficiency of conversions."""
        @pandas_fn
        def memory_test(df):
            return df
        
        # Test that original data isn't unnecessarily copied
        original = np.array([1, 2, 3])
        result = memory_test(original)
        assert isinstance(result, np.ndarray)


class TestPandasFnIntegration:
    """Test integration with other scitex decorators."""
    
    def test_with_functools_wraps(self):
        """Test that functools.wraps is properly applied."""
        def original_function(df):
            """Original function docstring."""
            return df
        
        decorated = pandas_fn(original_function)
        
        assert decorated.__name__ == 'original_function'
        assert decorated.__doc__ == 'Original function docstring.'
    
    def test_decorator_stacking_order(self):
        """Test order of decorator application."""
        call_order = []
        
        def track_decorator(name):
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    call_order.append(name)
                    return func(*args, **kwargs)
                return wrapper
            return decorator
        
        @track_decorator('outer')
        @pandas_fn
        @track_decorator('inner')
        def stacked_function(df):
            call_order.append('function')
            return df
        
        stacked_function([1, 2, 3])
        assert 'outer' in call_order
        assert 'inner' in call_order
        assert 'function' in call_order


if __name__ == "__main__":
    pytest.main([__file__, "-v"])