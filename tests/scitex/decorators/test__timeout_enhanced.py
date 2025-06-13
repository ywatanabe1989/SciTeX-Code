#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 21:30:00 (claude)"
# File: ./tests/scitex/decorators/test__timeout_enhanced.py

"""Comprehensive tests for timeout decorator."""

import pytest
import time
import sys
import os
from multiprocessing import Queue

# Add src to path for standalone execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from scitex.decorators import timeout


class TestTimeoutBasic:
    """Basic tests for timeout decorator."""
    
    def test_function_completes_within_timeout(self):
        """Test function that completes before timeout."""
        @timeout(seconds=2)
        def quick_function():
            time.sleep(0.1)
            return "completed"
        
        result = quick_function()
        assert result == "completed"
    
    def test_function_exceeds_timeout(self):
        """Test function that exceeds timeout."""
        @timeout(seconds=0.1)
        def slow_function():
            time.sleep(1)
            return "should not complete"
        
        with pytest.raises(TimeoutError):
            slow_function()
    
    def test_custom_error_message(self):
        """Test custom error message on timeout."""
        custom_message = "Custom timeout error"
        
        @timeout(seconds=0.1, error_message=custom_message)
        def slow_function():
            time.sleep(1)
        
        with pytest.raises(TimeoutError, match=custom_message):
            slow_function()
    
    def test_immediate_return(self):
        """Test function that returns immediately."""
        @timeout(seconds=1)
        def instant_function():
            return 42
        
        result = instant_function()
        assert result == 42


class TestTimeoutWithArguments:
    """Test timeout with functions that have arguments."""
    
    def test_function_with_args(self):
        """Test decorated function with positional arguments."""
        @timeout(seconds=1)
        def add(a, b):
            return a + b
        
        result = add(5, 3)
        assert result == 8
    
    def test_function_with_kwargs(self):
        """Test decorated function with keyword arguments."""
        @timeout(seconds=1)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        result = greet("Alice", greeting="Hi")
        assert result == "Hi, Alice!"
    
    def test_function_with_mixed_args(self):
        """Test decorated function with mixed arguments."""
        @timeout(seconds=1)
        def calculate(x, y, operation="+", precision=2):
            if operation == "+":
                result = x + y
            elif operation == "*":
                result = x * y
            else:
                result = 0
            return round(result, precision)
        
        assert calculate(3.14, 2.86) == 6.0
        assert calculate(2.5, 4, operation="*") == 10.0
        assert calculate(1.234, 5.678, precision=3) == 6.912


class TestTimeoutReturnValues:
    """Test timeout with different return value types."""
    
    def test_return_none(self):
        """Test function that returns None."""
        @timeout(seconds=1)
        def return_none():
            return None
        
        result = return_none()
        assert result is None
    
    def test_return_list(self):
        """Test function that returns a list."""
        @timeout(seconds=1)
        def return_list():
            return [1, 2, 3, 4, 5]
        
        result = return_list()
        assert result == [1, 2, 3, 4, 5]
    
    def test_return_dict(self):
        """Test function that returns a dictionary."""
        @timeout(seconds=1)
        def return_dict():
            return {"key": "value", "number": 42}
        
        result = return_dict()
        assert result == {"key": "value", "number": 42}
    
    def test_return_tuple(self):
        """Test function that returns a tuple."""
        @timeout(seconds=1)
        def return_tuple():
            return (1, "two", 3.0)
        
        result = return_tuple()
        assert result == (1, "two", 3.0)
    
    def test_return_object(self):
        """Test function that returns a custom object."""
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        @timeout(seconds=1)
        def return_object():
            return CustomObject(42)
        
        result = return_object()
        assert isinstance(result, CustomObject)
        assert result.value == 42


class TestTimeoutEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_zero_timeout(self):
        """Test with zero timeout (should fail immediately)."""
        @timeout(seconds=0)
        def any_function():
            return "result"
        
        # Zero timeout might fail even for instant functions due to process overhead
        with pytest.raises(TimeoutError):
            any_function()
    
    def test_negative_timeout(self):
        """Test with negative timeout."""
        @timeout(seconds=-1)
        def function():
            return "result"
        
        # Negative timeout behaves like zero timeout
        with pytest.raises(TimeoutError):
            function()
    
    def test_very_long_timeout(self):
        """Test with very long timeout."""
        @timeout(seconds=3600)  # 1 hour
        def quick_function():
            return "done"
        
        result = quick_function()
        assert result == "done"
    
    def test_function_raises_exception(self):
        """Test function that raises an exception."""
        @timeout(seconds=1)
        def failing_function():
            raise ValueError("Internal error")
        
        # The exception should propagate through the timeout wrapper
        with pytest.raises(Exception):  # Could be ValueError or other due to multiprocessing
            failing_function()
    
    def test_recursive_function(self):
        """Test recursive function with timeout."""
        @timeout(seconds=1)
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        
        # Should complete for small values
        assert factorial(5) == 120
        
        # Large recursion might timeout
        @timeout(seconds=0.1)
        def deep_recursion(n):
            if n <= 0:
                return 0
            time.sleep(0.01)  # Simulate work
            return 1 + deep_recursion(n - 1)
        
        with pytest.raises(TimeoutError):
            deep_recursion(100)


class TestTimeoutProcessBehavior:
    """Test multiprocessing behavior of timeout."""
    
    def test_process_cleanup(self):
        """Test that processes are properly cleaned up."""
        @timeout(seconds=0.1)
        def infinite_loop():
            while True:
                time.sleep(0.01)
        
        with pytest.raises(TimeoutError):
            infinite_loop()
        
        # Process should be terminated, not left running
        # (Hard to test directly, but no zombie processes should remain)
    
    def test_shared_state_isolation(self):
        """Test that decorated functions are isolated."""
        global_var = []
        
        @timeout(seconds=1)
        def modify_global():
            global_var.append(1)  # This won't affect the parent process
            return len(global_var)
        
        result = modify_global()
        # The global in parent process should be unchanged
        assert len(global_var) == 0
        # But the function in subprocess saw its modification
        assert result == 1
    
    def test_large_return_value(self):
        """Test with large return values (queue limitations)."""
        @timeout(seconds=2)
        def return_large_data():
            # Return a moderately large object
            return list(range(100000))
        
        result = return_large_data()
        assert len(result) == 100000
        assert result[0] == 0
        assert result[-1] == 99999


class TestTimeoutDecorator:
    """Test decorator behavior and syntax."""
    
    def test_decorator_without_parentheses(self):
        """Test that decorator requires parentheses."""
        # This would not work as intended:
        # @timeout  # Missing parentheses
        # def function():
        #     return 42
        
        # The correct usage requires parentheses
        @timeout()  # Uses default seconds=10
        def function():
            return 42
        
        # This should work with default timeout
        result = function()
        assert result == 42
    
    def test_multiple_decorations(self):
        """Test function with multiple timeout decorations."""
        # Only the innermost decorator should apply
        @timeout(seconds=2)
        @timeout(seconds=0.1)  # This one applies
        def function():
            time.sleep(0.5)
            return "done"
        
        with pytest.raises(TimeoutError):
            function()
    
    def test_class_method_decoration(self):
        """Test decorating class methods."""
        class MyClass:
            @timeout(seconds=1)
            def instance_method(self, value):
                return value * 2
            
            @classmethod
            @timeout(seconds=1)
            def class_method(cls, value):
                return value * 3
            
            @staticmethod
            @timeout(seconds=1)
            def static_method(value):
                return value * 4
        
        obj = MyClass()
        assert obj.instance_method(5) == 10
        assert MyClass.class_method(5) == 15
        assert MyClass.static_method(5) == 20


class TestTimeoutRealWorld:
    """Test real-world scenarios."""
    
    def test_io_bound_operation(self):
        """Test I/O bound operation with timeout."""
        @timeout(seconds=1)
        def simulate_io():
            # Simulate I/O with sleep
            time.sleep(0.1)
            return "data"
        
        result = simulate_io()
        assert result == "data"
    
    def test_cpu_bound_operation(self):
        """Test CPU bound operation with timeout."""
        @timeout(seconds=1)
        def compute_intensive():
            # Simple CPU-bound task
            result = 0
            for i in range(1000000):
                result += i
            return result
        
        result = compute_intensive()
        assert result == sum(range(1000000))
    
    def test_network_simulation(self):
        """Test simulated network operation with timeout."""
        @timeout(seconds=0.5, error_message="Network timeout")
        def fetch_data(delay=0.1):
            time.sleep(delay)  # Simulate network delay
            return {"status": "success", "data": [1, 2, 3]}
        
        # Fast network
        result = fetch_data(0.1)
        assert result["status"] == "success"
        
        # Slow network
        with pytest.raises(TimeoutError, match="Network timeout"):
            fetch_data(1.0)
    
    @pytest.mark.parametrize("sleep_time,timeout_val,should_complete", [
        (0.1, 1.0, True),
        (0.5, 1.0, True),
        (1.5, 1.0, False),
        (0.01, 0.1, True),
        (0.2, 0.1, False),
    ])
    def test_parametrized_timeouts(self, sleep_time, timeout_val, should_complete):
        """Test various timeout scenarios with parameters."""
        @timeout(seconds=timeout_val)
        def timed_function():
            time.sleep(sleep_time)
            return "completed"
        
        if should_complete:
            result = timed_function()
            assert result == "completed"
        else:
            with pytest.raises(TimeoutError):
                timed_function()


class TestTimeoutConcurrency:
    """Test concurrent timeout operations."""
    
    def test_sequential_timeouts(self):
        """Test multiple sequential timeout operations."""
        @timeout(seconds=1)
        def operation(n):
            time.sleep(0.1)
            return n * 2
        
        results = []
        for i in range(5):
            results.append(operation(i))
        
        assert results == [0, 2, 4, 6, 8]
    
    def test_nested_timeout_calls(self):
        """Test nested functions with timeouts."""
        @timeout(seconds=1)
        def inner_function(x):
            time.sleep(0.1)
            return x + 1
        
        @timeout(seconds=2)
        def outer_function(x):
            result = inner_function(x)
            return result * 2
        
        final_result = outer_function(5)
        assert final_result == 12  # (5 + 1) * 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])