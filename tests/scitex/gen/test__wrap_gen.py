#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:10:00 (claude)"
# File: ./tests/scitex/gen/test__wrap.py

"""
Comprehensive tests for scitex.gen._wrap module.

This module tests:
- wrap decorator functionality
- Function metadata preservation
- Argument passing
- Return value handling
- Edge cases
"""

import pytest
import functools
from types import FunctionType

from scitex.gen import wrap



class TestWrapBasicFunctionality:
    """Test basic wrap decorator functionality."""

    def test_wrap_simple_function(self):
        """Test wrap decorator on a simple function."""

        @wrap
        def add(a, b):
            """Add two numbers."""
            return a + b

        result = add(2, 3)
        assert result == 5

    def test_wrap_preserves_function_name(self):
        """Test that wrap preserves function name."""

        @wrap
        def my_function():
            """Test function."""
            pass

        assert my_function.__name__ == "my_function"

    def test_wrap_preserves_docstring(self):
        """Test that wrap preserves docstring."""

        @wrap
        def documented_function():
            """This is a test docstring."""
            pass

        assert documented_function.__doc__ == "This is a test docstring."

    def test_wrap_preserves_module(self):
        """Test that wrap preserves module attribute."""

        def original_function():
            pass

        wrapped = wrap(original_function)
        assert wrapped.__module__ == original_function.__module__

    def test_wrap_is_function(self):
        """Test that wrapped result is still a function."""

        @wrap
        def test_func():
            pass

        assert isinstance(test_func, FunctionType)
        assert callable(test_func)


class TestWrapArgumentHandling:
    """Test wrap decorator with various argument patterns."""

    def test_wrap_no_arguments(self):
        """Test wrap with function taking no arguments."""

        @wrap
        def no_args():
            return 42

        assert no_args() == 42

    def test_wrap_positional_arguments(self):
        """Test wrap with positional arguments."""

        @wrap
        def positional(a, b, c):
            return a + b + c

        assert positional(1, 2, 3) == 6

    def test_wrap_keyword_arguments(self):
        """Test wrap with keyword arguments."""

        @wrap
        def keywords(x=1, y=2, z=3):
            return x * y * z

        assert keywords() == 6
        assert keywords(x=2) == 12
        assert keywords(x=2, y=3) == 18
        assert keywords(x=2, y=3, z=4) == 24

    def test_wrap_mixed_arguments(self):
        """Test wrap with mixed positional and keyword arguments."""

        @wrap
        def mixed(a, b, c=3, d=4):
            return a + b + c + d

        assert mixed(1, 2) == 10
        assert mixed(1, 2, 5) == 12
        assert mixed(1, 2, c=5, d=6) == 14

    def test_wrap_args_kwargs(self):
        """Test wrap with *args and **kwargs."""

        @wrap
        def var_args(*args, **kwargs):
            return sum(args) + sum(kwargs.values())

        assert var_args(1, 2, 3) == 6
        assert var_args(1, 2, x=3, y=4) == 10
        assert var_args() == 0

    def test_wrap_complex_signature(self):
        """Test wrap with complex function signature."""

        @wrap
        def complex_sig(a, b, *args, x=1, y=2, **kwargs):
            return a + b + sum(args) + x + y + sum(kwargs.values())

        assert complex_sig(10, 20) == 33
        assert complex_sig(10, 20, 30, 40) == 103
        assert complex_sig(10, 20, x=5, y=6) == 41
        assert complex_sig(10, 20, 30, x=5, y=6, z=7) == 78


class TestWrapReturnValues:
    """Test wrap decorator with various return value types."""

    def test_wrap_return_none(self):
        """Test wrap with function returning None."""

        @wrap
        def return_none():
            pass

        assert return_none() is None

    def test_wrap_return_single_value(self):
        """Test wrap with function returning single value."""

        @wrap
        def return_int():
            return 42

        assert return_int() == 42

    def test_wrap_return_tuple(self):
        """Test wrap with function returning tuple."""

        @wrap
        def return_tuple():
            return 1, 2, 3

        result = return_tuple()
        assert result == (1, 2, 3)

    def test_wrap_return_list(self):
        """Test wrap with function returning list."""

        @wrap
        def return_list():
            return [1, 2, 3]

        result = return_list()
        assert result == [1, 2, 3]

    def test_wrap_return_dict(self):
        """Test wrap with function returning dict."""

        @wrap
        def return_dict():
            return {"a": 1, "b": 2}

        result = return_dict()
        assert result == {"a": 1, "b": 2}

    def test_wrap_return_object(self):
        """Test wrap with function returning custom object."""

        class CustomObject:
            def __init__(self, value):
                self.value = value

        @wrap
        def return_object():
            return CustomObject(42)

        result = return_object()
        assert isinstance(result, CustomObject)
        assert result.value == 42


class TestWrapExceptionHandling:
    """Test wrap decorator with exception handling."""

    def test_wrap_propagates_exceptions(self):
        """Test that wrap propagates exceptions."""

        @wrap
        def raise_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            raise_error()

    def test_wrap_preserves_exception_type(self):
        """Test that wrap preserves exception types."""

        @wrap
        def raise_custom():
            class CustomError(Exception):
                pass

            raise CustomError("Custom")

        with pytest.raises(Exception) as exc_info:
            raise_custom()

        assert "Custom" in str(exc_info.value)

    def test_wrap_with_try_except(self):
        """Test wrap with function containing try-except."""

        @wrap
        def safe_divide(a, b):
            try:
                return a / b
            except ZeroDivisionError:
                return float("inf")

        assert safe_divide(10, 2) == 5
        assert safe_divide(10, 0) == float("inf")


class TestWrapNesting:
    """Test wrap decorator with nested functions and decorators."""

    def test_wrap_nested_functions(self):
        """Test wrap with nested function definitions."""

        @wrap
        def outer(x):
            def inner(y):
                return x + y

            return inner

        add_five = outer(5)
        assert add_five(3) == 8

    def test_wrap_multiple_decorators(self):
        """Test wrap with multiple decorators."""

        def double(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs) * 2

            return wrapper

        @wrap
        @double
        def get_value():
            return 10

        assert get_value() == 20

    def test_wrap_recursive_function(self):
        """Test wrap with recursive function."""

        @wrap
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        assert factorial(5) == 120
        assert factorial(0) == 1


class TestWrapEdgeCases:
    """Test wrap decorator with edge cases."""

    def test_wrap_lambda(self):
        """Test wrap with lambda function."""

        wrapped_lambda = wrap(lambda x: x * 2)
        assert wrapped_lambda(5) == 10

    def test_wrap_partial_function(self):
        """Test wrap with partial function."""

        def multiply(a, b):
            return a * b

        partial_mult = functools.partial(multiply, 10)
        wrapped_partial = wrap(partial_mult)

        assert wrapped_partial(5) == 50

    def test_wrap_class_method(self):
        """Test wrap with class method."""

        class TestClass:
            @wrap
            def method(self, x):
                return x * 2

        obj = TestClass()
        assert obj.method(5) == 10

    def test_wrap_static_method(self):
        """Test wrap with static method."""

        class TestClass:
            @staticmethod
            @wrap
            def static_method(x):
                return x * 3

        assert TestClass.static_method(5) == 15

    def test_wrap_generator_function(self):
        """Test wrap with generator function."""

        @wrap
        def count_to(n):
            for i in range(n):
                yield i

        result = list(count_to(5))
        assert result == [0, 1, 2, 3, 4]

    def test_wrap_async_function(self):
        """Test wrap with async function."""
        import asyncio

        @wrap
        async def async_add(a, b):
            return a + b

        # Test that it's still async
        assert asyncio.iscoroutinefunction(async_add)

        # Test execution
        result = asyncio.run(async_add(2, 3))
        assert result == 5


class TestWrapIntegration:
    """Integration tests for wrap decorator."""

    def test_wrap_preserves_all_metadata(self):
        """Test that wrap preserves all function metadata."""

        def original(x, y=2):
            """Original function."""
            return x + y

        original.custom_attr = "test"

        wrapped = wrap(original)

        # Check standard attributes
        assert wrapped.__name__ == original.__name__
        assert wrapped.__doc__ == original.__doc__
        assert wrapped.__module__ == original.__module__
        assert wrapped.__dict__ == original.__dict__

        # Check custom attribute
        assert hasattr(wrapped, "custom_attr")
        assert wrapped.custom_attr == "test"

    def test_wrap_idempotent(self):
        """Test that wrapping multiple times is safe."""

        def func(x):
            return x * 2

        once_wrapped = wrap(func)
        twice_wrapped = wrap(once_wrapped)

        assert once_wrapped(5) == 10
        assert twice_wrapped(5) == 10

    def test_wrap_performance(self):
        """Test that wrap doesn't significantly impact performance."""
        import time

        def simple_func(x):
            return x + 1

        wrapped_func = wrap(simple_func)

        # Test both functions work correctly
        assert simple_func(10) == 11
        assert wrapped_func(10) == 11

        # Performance should be similar (not testing exact timing due to variability)
        iterations = 10000

        # Original function timing
        start = time.time()
        for _ in range(iterations):
            simple_func(10)
        original_time = time.time() - start

        # Wrapped function timing
        start = time.time()
        for _ in range(iterations):
            wrapped_func(10)
        wrapped_time = time.time() - start

        # Wrapped should not be more than 2x slower for this simple case
        assert wrapped_time < original_time * 2


if __name__ == "__main__":
    # Run specific test file
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
