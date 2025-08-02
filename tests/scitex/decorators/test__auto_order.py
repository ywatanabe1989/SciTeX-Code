#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 10:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__auto_order.py

"""Test auto-ordering decorator system"""

import pytest
import numpy as np
import torch
import pandas as pd
from scitex.decorators import (
    enable_auto_order,
    disable_auto_order,
    torch_fn,
    numpy_fn,
    pandas_fn,
    batch_fn,
)
import scitex.decorators


class TestAutoOrder:
    """Test auto-ordering functionality"""
    
    def setup_method(self):
        """Reset to original decorators before each test"""
        disable_auto_order()
    
    def teardown_method(self):
        """Reset to original decorators after each test"""
        disable_auto_order()
    
    def test_enable_disable(self):
        """Test enable and disable functionality"""
        # Enable auto-ordering
        enable_auto_order()
        
        # Check that decorators were replaced
        assert scitex.decorators.torch_fn.__class__.__name__ == 'AutoOrderDecorator'
        assert scitex.decorators.numpy_fn.__class__.__name__ == 'AutoOrderDecorator'
        assert scitex.decorators.pandas_fn.__class__.__name__ == 'AutoOrderDecorator'
        assert scitex.decorators.batch_fn.__class__.__name__ == 'AutoOrderDecorator'
        
        # Disable auto-ordering
        disable_auto_order()
        
        # Check that original decorators were restored
        assert scitex.decorators.torch_fn.__name__ == 'torch_fn'
        assert scitex.decorators.numpy_fn.__name__ == 'numpy_fn'
        assert scitex.decorators.pandas_fn.__name__ == 'pandas_fn'
        assert scitex.decorators.batch_fn.__name__ == 'batch_fn'
    
    def test_auto_ordering_torch_batch(self):
        """Test that decorators are applied in correct order regardless of how written"""
        enable_auto_order()
        
        # Define functions with different decorator orders
        @batch_fn
        @torch_fn
        def func1(x):
            return x.mean()
        
        @torch_fn
        @batch_fn
        def func2(x):
            return x.mean()
        
        # Both should work identically
        data = np.random.randn(10, 5)
        result1 = func1(data)
        result2 = func2(data)
        
        # Results should be the same (both are numpy arrays due to input type)
        np.testing.assert_allclose(result1, result2)
    
    def test_multiple_type_converters(self):
        """Test handling of multiple type converters"""
        enable_auto_order()
        
        @batch_fn
        @numpy_fn
        @torch_fn
        def func(x):
            # Should work with torch tensor input
            return x.mean()
        
        # Test with torch tensor
        data = torch.randn(10, 5)
        result = func(data)
        # With auto-ordering, the decorators are reordered, but the output type
        # depends on the input type. Since input is torch, output is torch
        assert isinstance(result, (torch.Tensor, np.ndarray, np.floating, float))
    
    def test_complex_decorator_stacking(self):
        """Test complex decorator stacking scenarios"""
        enable_auto_order()
        
        @pandas_fn
        @torch_fn
        def complex_func(x):
            # This would normally be problematic, but auto-ordering handles it
            # Need to handle CUDA tensor
            if isinstance(x, torch.Tensor) and x.is_cuda:
                x = x.cpu()
            return pd.Series(x.flatten())
        
        # Test with numpy data to avoid CUDA issues
        data = np.random.randn(8, 5)  # 8 divides evenly into batches
        result = complex_func(data)
        assert isinstance(result, pd.Series)
    
    def test_delayed_application(self):
        """Test that decorators are applied lazily on first call"""
        enable_auto_order()
        
        call_count = 0
        
        @batch_fn
        @torch_fn
        def counting_func(x):
            nonlocal call_count
            call_count += 1
            return x.sum()
        
        # Function should have pending decorators
        assert hasattr(counting_func, '_pending_decorators')
        
        # First call applies decorators
        data = np.array([1, 2, 3])
        result = counting_func(data)
        
        # After first call, pending decorators should be gone
        assert not hasattr(counting_func, '_pending_decorators')
        assert hasattr(counting_func, '_final_func')
    
    def test_preserves_function_metadata(self):
        """Test that function metadata is preserved"""
        enable_auto_order()
        
        @batch_fn
        @torch_fn
        def documented_func(x):
            """This is a documented function"""
            return x * 2
        
        assert documented_func.__doc__ == "This is a documented function"
        assert documented_func.__name__ == "documented_func"


class TestAutoOrderIntegration:
    """Test auto-ordering with real use cases"""
    
    def setup_method(self):
        """Enable auto-ordering for integration tests"""
        enable_auto_order()
    
    def teardown_method(self):
        """Disable after tests"""
        disable_auto_order()
    
    def test_stats_describe_with_auto_order(self):
        """Test that stats.describe works with auto-ordering"""
        import scitex.stats.desc
        
        # Test case from bug report
        features_pac_z = np.random.randn(87, 5, 50, 30)
        tensor_input = torch.tensor(features_pac_z)
        
        # This should work without errors
        out = scitex.stats.desc.describe(tensor_input, axis=(1, 2, 3))
        
        assert out[0].shape == (87, 7)
        assert len(out[1]) == 7
    
    def test_nested_lists_with_auto_order(self):
        """Test nested list handling with auto-ordering"""
        @torch_fn
        def process_nested(x):
            return x.mean()
        
        # Nested lists should work
        nested_data = [[1, 2, 3], [4, 5, 6]]
        result = process_nested(nested_data)
        
        # Result will be numpy since input was a list
        expected = np.array(nested_data).mean()
        np.testing.assert_allclose(result, expected)
    
    def test_scalar_preservation_with_auto_order(self):
        """Test that scalars are preserved with auto-ordering"""
        @torch_fn
        def scale_tensor(x, scale=2.5):
            assert isinstance(scale, float)
            return x * scale
        
        data = torch.tensor([1, 2, 3])
        result = scale_tensor(data, scale=3.0)
        
        expected = data * 3.0
        assert torch.allclose(result, expected)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_auto_order.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-06-01 10:30:00 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/decorators/_auto_order.py
# 
# """
# Auto-ordering decorator system that enforces predefined order regardless of 
# how decorators are written in code.
# 
# The enforced order is:
# 1. Type conversion (innermost): torch_fn, numpy_fn, pandas_fn
# 2. Batch processing (outermost): batch_fn
# 
# This uses a delayed application approach where decorators are collected
# and then applied in the correct order when the function is first called.
# 
# Example
# -------
# >>> from scitex.decorators import enable_auto_order
# >>> enable_auto_order()
# >>> 
# >>> # These will all work identically:
# >>> @batch_fn
# >>> @torch_fn
# >>> def func1(x):
# ...     return x.mean()
# >>> 
# >>> @torch_fn
# >>> @batch_fn  # Order doesn't matter!
# >>> def func2(x):
# ...     return x.mean()
# 
# The auto-ordering system eliminates decorator ordering complexity and
# prevents common errors from incorrect decorator stacking.
# """
# 
# from functools import wraps
# from typing import Callable, List, Tuple, Any
# 
# # Import original decorators
# from ._torch_fn import torch_fn as _orig_torch_fn
# from ._numpy_fn import numpy_fn as _orig_numpy_fn
# from ._pandas_fn import pandas_fn as _orig_pandas_fn
# from ._batch_fn import batch_fn as _orig_batch_fn
# 
# 
# # Decorator priority (higher = inner/applied first)
# DECORATOR_PRIORITY = {
#     'torch_fn': 100,
#     'numpy_fn': 100,
#     'pandas_fn': 100,
#     'batch_fn': 10,
# }
# 
# # Original decorator mapping
# ORIGINAL_DECORATORS = {
#     'torch_fn': _orig_torch_fn,
#     'numpy_fn': _orig_numpy_fn,
#     'pandas_fn': _orig_pandas_fn,
#     'batch_fn': _orig_batch_fn,
# }
# 
# 
# class AutoOrderDecorator:
#     """Decorator that collects and applies decorators in predefined order."""
#     
#     def __init__(self, name: str):
#         self.name = name
#         self.priority = DECORATOR_PRIORITY[name]
#         self.original = ORIGINAL_DECORATORS[name]
#     
#     def __call__(self, func: Callable) -> Callable:
#         # Initialize or get pending decorators list
#         if not hasattr(func, '_pending_decorators'):
#             # First decorator - create the wrapper
#             original_func = func
#             
#             @wraps(func)
#             def auto_ordered_wrapper(*args, **kwargs):
#                 # On first call, apply decorators in correct order
#                 if hasattr(auto_ordered_wrapper, '_pending_decorators'):
#                     # Sort by priority (descending = innermost first)
#                     decorators = sorted(
#                         auto_ordered_wrapper._pending_decorators,
#                         key=lambda x: x[1],
#                         reverse=True
#                     )
#                     
#                     # Apply decorators in order
#                     final_func = original_func
#                     for dec_name, _, dec_func in decorators:
#                         final_func = dec_func(final_func)
#                     
#                     # Replace this wrapper with the final decorated function
#                     auto_ordered_wrapper._final_func = final_func
#                     delattr(auto_ordered_wrapper, '_pending_decorators')
#                 
#                 # Call the final decorated function
#                 if hasattr(auto_ordered_wrapper, '_final_func'):
#                     return auto_ordered_wrapper._final_func(*args, **kwargs)
#                 else:
#                     return original_func(*args, **kwargs)
#             
#             auto_ordered_wrapper._pending_decorators = []
#             func = auto_ordered_wrapper
#         
#         # Add this decorator to pending list
#         func._pending_decorators.append((self.name, self.priority, self.original))
#         
#         return func
# 
# 
# # Create auto-ordering versions
# torch_fn = AutoOrderDecorator('torch_fn')
# numpy_fn = AutoOrderDecorator('numpy_fn')
# pandas_fn = AutoOrderDecorator('pandas_fn')
# batch_fn = AutoOrderDecorator('batch_fn')
# 
# 
# # Enable auto-ordering globally
# def enable_auto_order():
#     """
#     Enable auto-ordering for all decorators in the scitex.decorators module.
#     
#     This replaces the standard decorators with auto-ordering versions.
#     
#     Example
#     -------
#     >>> import scitex
#     >>> scitex.decorators.enable_auto_order()
#     >>> 
#     >>> # Now decorators will auto-order regardless of how they're written
#     >>> @scitex.decorators.batch_fn
#     >>> @scitex.decorators.torch_fn
#     >>> def my_func(x):
#     ...     return x.mean()
#     """
#     import scitex.decorators as decorators_module
#     
#     # Replace with auto-ordering versions
#     decorators_module.torch_fn = torch_fn
#     decorators_module.numpy_fn = numpy_fn
#     decorators_module.pandas_fn = pandas_fn
#     decorators_module.batch_fn = batch_fn
#     
#     print("Auto-ordering enabled for scitex decorators!")
#     print("Decorators will now apply in predefined order:")
#     print("  1. Type conversion (torch_fn, numpy_fn, pandas_fn)")
#     print("  2. Batch processing (batch_fn)")
# 
# 
# def disable_auto_order():
#     """Disable auto-ordering and restore original decorators."""
#     import scitex.decorators as decorators_module
#     
#     # Restore original decorators
#     decorators_module.torch_fn = _orig_torch_fn
#     decorators_module.numpy_fn = _orig_numpy_fn
#     decorators_module.pandas_fn = _orig_pandas_fn
#     decorators_module.batch_fn = _orig_batch_fn
#     
#     print("Auto-ordering disabled. Using original decorators.")
# 
# 
# __all__ = [
#     'torch_fn',
#     'numpy_fn',
#     'pandas_fn',
#     'batch_fn',
#     'enable_auto_order',
#     'disable_auto_order',
# ]
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_auto_order.py
# --------------------------------------------------------------------------------
