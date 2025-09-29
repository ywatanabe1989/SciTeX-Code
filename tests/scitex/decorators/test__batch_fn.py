#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 10:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/decorators/test__batch_fn.py

"""Test batch_fn decorator functionality"""

import pytest
import numpy as np
import torch
import pandas as pd
from scitex.decorators import batch_fn
from scitex.decorators import torch_fn
from scitex.decorators import numpy_fn


class TestBatchFn:
    """Test batch_fn decorator"""
    
    def test_basic_functionality(self):
        """Test basic batch processing"""
        @batch_fn
        def sum_batch(x, batch_size=4):
            return x.sum(axis=1)
        
        data = np.random.randn(10, 5)
        result = sum_batch(data, batch_size=3)
        expected = data.sum(axis=1)
        
        np.testing.assert_allclose(result, expected)
    
    def test_default_batch_size(self):
        """Test default batch_size=4"""
        call_count = 0
        
        @batch_fn
        def count_calls(x, batch_size=4):
            nonlocal call_count
            call_count += 1
            return x
        
        data = np.arange(10)
        result = count_calls(data)  # No batch_size specified
        
        # With 10 elements and batch_size=4, should have 3 calls
        assert call_count == 3
        np.testing.assert_array_equal(result, data)
    
    def test_batch_size_minus_one(self):
        """Test batch_size=-1 processes all at once"""
        call_count = 0
        
        @batch_fn
        def count_calls(x, batch_size=-1):
            nonlocal call_count
            call_count += 1
            return x
        
        data = np.arange(100)
        result = count_calls(data, batch_size=-1)
        
        # Should only call once
        assert call_count == 1
        np.testing.assert_array_equal(result, data)
    
    def test_scalar_results(self):
        """Test handling of scalar results"""
        @batch_fn
        def get_mean(x, batch_size=4):
            return np.mean(x)
        
        data = np.random.randn(10)
        result = get_mean(data, batch_size=3)
        expected = np.mean(data)
        
        np.testing.assert_allclose(result, expected)
    
    def test_tuple_results(self):
        """Test handling of tuple results"""
        @batch_fn
        def get_stats(x, batch_size=4):
            return x.mean(), x.std()
        
        data = np.random.randn(10, 5)
        mean, std = get_stats(data, batch_size=3)
        
        np.testing.assert_allclose(mean, data.mean())
        np.testing.assert_allclose(std, data.std())
    
    def test_mixed_tuple_results(self):
        """Test handling of tuples with mixed types (tensor + list)"""
        @batch_fn
        def describe_batch(x, batch_size=4):
            stats = x.mean(axis=1)
            labels = ["mean", "std", "min", "max", "q25", "q50", "q75"]  # Fixed list
            return stats, labels
        
        data = np.random.randn(10, 5)
        stats, labels = describe_batch(data, batch_size=3)
        
        expected_stats = data.mean(axis=1)
        np.testing.assert_allclose(stats, expected_stats)
        # Non-tensor elements use first batch value
        assert labels == ["mean", "std", "min", "max", "q25", "q50", "q75"]
    
    def test_torch_tensor_scalar_results(self):
        """Test handling of torch tensor scalar results"""
        @batch_fn
        @torch_fn
        def get_sum(x, batch_size=4):
            return x.sum()
        
        data = torch.randn(10)
        result = get_sum(data, batch_size=3)
        expected = data.sum()
        
        assert torch.allclose(result, expected)
    
    def test_torch_tensor_multidim_results(self):
        """Test handling of torch tensor multidimensional results"""
        @batch_fn
        @torch_fn
        def reduce_dim(x, batch_size=4):
            return x.mean(dim=1)
        
        data = torch.randn(10, 5)
        result = reduce_dim(data, batch_size=3)
        expected = data.mean(dim=1)
        
        assert torch.allclose(result, expected)
    
    def test_parameter_compatibility(self):
        """Test that batch_size is only passed to functions that accept it"""
        @batch_fn
        def no_batch_param(x):
            # This function doesn't accept batch_size
            return x.sum()
        
        data = np.random.randn(10)
        # Should work without error
        result = no_batch_param(data, batch_size=3)
        expected = data.sum()
        
        np.testing.assert_allclose(result, expected)
    
    def test_with_kwargs(self):
        """Test batch processing with additional kwargs"""
        @batch_fn
        def weighted_sum(x, weights=None, batch_size=4):
            if weights is not None:
                return (x * weights).sum(axis=1)
            return x.sum(axis=1)
        
        data = np.random.randn(10, 5)
        weights = np.random.randn(5)
        
        result = weighted_sum(data, weights=weights, batch_size=3)
        expected = (data * weights).sum(axis=1)
        
        np.testing.assert_allclose(result, expected)
    
    def test_empty_input(self):
        """Test handling of empty input"""
        @batch_fn
        def process(x, batch_size=4):
            return x * 2
        
        data = np.array([])
        result = process(data)
        
        assert len(result) == 0
    
    def test_uneven_batches(self):
        """Test handling of uneven batch sizes"""
        batch_sizes_seen = []
        
        @batch_fn
        def track_batch_size(x, batch_size=4):
            batch_sizes_seen.append(len(x))
            return x
        
        data = np.arange(10)  # 10 elements
        result = track_batch_size(data, batch_size=4)
        
        # Should see batches of size 4, 4, 2
        assert batch_sizes_seen == [4, 4, 2]
        np.testing.assert_array_equal(result, data)


class TestBatchFnWithOtherDecorators:
    """Test batch_fn combined with other decorators"""
    
    def test_with_torch_fn(self):
        """Test batch_fn with torch_fn"""
        @batch_fn
        @torch_fn
        def torch_mean(x, dim=None, batch_size=4):
            if dim is not None:
                return x.mean(dim=dim)
            return x.mean()
        
        data = np.random.randn(10, 5)
        result = torch_mean(data, dim=1, batch_size=3)
        expected = data.mean(axis=1)
        
        np.testing.assert_allclose(result, expected, rtol=1e-6)
    
    def test_with_numpy_fn(self):
        """Test batch_fn with numpy_fn"""
        @batch_fn
        @numpy_fn
        def numpy_std(x, axis=None, batch_size=4):
            if axis is not None:
                return x.std(axis=axis)
            return x.std()
        
        data = torch.randn(10, 5)
        result = numpy_std(data, axis=1, batch_size=3)
        expected = data.numpy().std(axis=1)
        
        np.testing.assert_allclose(result, expected, rtol=1e-6)
    
    def test_nested_decorator_context(self):
        """Test nested decorator context handling"""
        from scitex.decorators import is_nested_decorator
        
        @batch_fn
        @torch_fn
        def nested_func(x, batch_size=4):
            # Inside here, should be in nested context
            assert not is_nested_decorator()  # Should be false in final function
            return x.sum()
        
        data = torch.randn(10)
        result = nested_func(data, batch_size=3)
        assert isinstance(result, torch.Tensor)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_batch_fn.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 09:18:26 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_batch_fn.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/decorators/_batch_fn.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# from typing import Any as _Any
# 
# from functools import wraps
# from typing import Callable
# 
# import numpy as np
# import torch
# from tqdm import tqdm as _tqdm
# 
# from ._converters import is_nested_decorator
# 
# 
# def batch_fn(func: Callable) -> Callable:
#     @wraps(func)
#     def wrapper(x: _Any, *args: _Any, **kwargs: _Any) -> _Any:
#         # Skip batching if in a nested decorator context and batch_size is already set
#         if is_nested_decorator() and "batch_size" in kwargs:
#             return func(x, *args, **kwargs)
# 
#         # Set the current decorator context
#         wrapper._current_decorator = "batch_fn"
#         
#         # Mark that batch_fn has been applied
#         if not hasattr(wrapper, '_decorator_order'):
#             wrapper._decorator_order = []
#         wrapper._decorator_order.append('batch_fn')
# 
#         batch_size = int(kwargs.pop("batch_size", 4))
#         if len(x) <= batch_size:
#             # Only pass batch_size if the function accepts it
#             import inspect
#             try:
#                 sig = inspect.signature(func)
#                 if 'batch_size' in sig.parameters:
#                     return func(x, *args, **kwargs, batch_size=batch_size)
#                 else:
#                     return func(x, *args, **kwargs)
#             except:
#                 # Fallback for wrapped functions
#                 return func(x, *args, **kwargs)
# 
#         n_batches = (len(x) + batch_size - 1) // batch_size
#         results = []
# 
#         for i_batch in _tqdm(range(n_batches)):
#             start = i_batch * batch_size
#             end = min((i_batch + 1) * batch_size, len(x))
# 
#             # Only pass batch_size if the function accepts it
#             import inspect
#             try:
#                 sig = inspect.signature(func)
#                 if 'batch_size' in sig.parameters:
#                     batch_result = func(x[start:end], *args, **kwargs, batch_size=batch_size)
#                 else:
#                     batch_result = func(x[start:end], *args, **kwargs)
#             except:
#                 # Fallback for wrapped functions
#                 batch_result = func(x[start:end], *args, **kwargs)
# 
#             if isinstance(batch_result, torch.Tensor):
#                 batch_result = batch_result.cpu()
#             elif isinstance(batch_result, tuple):
#                 batch_result = tuple(
#                     val.cpu() if isinstance(val, torch.Tensor) else val
#                     for val in batch_result
#                 )
# 
#             results.append(batch_result)
# 
#         if isinstance(results[0], tuple):
#             n_vars = len(results[0])
#             combined_results = []
#             for i_var in range(n_vars):
#                 # Check if this element is stackable (tensor/array) or should be kept as-is
#                 first_elem = results[0][i_var]
#                 if isinstance(first_elem, (torch.Tensor, np.ndarray)):
#                     # Stack tensors/arrays
#                     if isinstance(first_elem, torch.Tensor):
#                         if first_elem.ndim == 0:
#                             combined = torch.stack([res[i_var] for res in results])
#                         else:
#                             combined = torch.vstack([res[i_var] for res in results])
#                     else:
#                         combined = np.vstack([res[i_var] for res in results])
#                     combined_results.append(combined)
#                 else:
#                     # For non-tensor elements (like lists), just take the first one
#                     # (assuming they're all the same across batches)
#                     combined_results.append(first_elem)
#             return tuple(combined_results)
#         elif isinstance(results[0], torch.Tensor):
#             # Check if results are 0-D tensors (scalars)
#             if results[0].ndim == 0:
#                 return torch.stack(results)
#             else:
#                 return torch.vstack(results)
#         elif isinstance(results[0], np.ndarray):
#             # Handle numpy arrays
#             if results[0].ndim == 0:
#                 return np.array(results)
#             else:
#                 return np.vstack(results)
#         elif isinstance(results[0], (int, float)):
#             # Handle scalar results
#             return np.array(results) if len(results) > 1 else results[0]
#         else:
#             # For lists and other types
#             return sum(results, [])
# 
#     # Mark as a wrapper for detection
#     wrapper._is_wrapper = True
#     wrapper._decorator_type = "batch_fn"
#     return wrapper
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_batch_fn.py
# --------------------------------------------------------------------------------
