#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 06:07:01 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/scitex/decorators/test__numpy_fn.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/decorators/test__numpy_fn.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch
from scitex.decorators import numpy_fn


@pytest.fixture
def test_data():
    """Create test data for tests."""
    return {
        "list": [1.0, 2.0, 3.0],
        "numpy": np.array([1.0, 2.0, 3.0]),
        "pandas_series": pd.Series([1.0, 2.0, 3.0]),
        "pandas_df": pd.DataFrame({"col1": [1.0, 2.0, 3.0]}),
        "torch": torch.tensor([1.0, 2.0, 3.0]),
    }


def test_numpy_fn_with_list_input(test_data):
    """Test numpy_fn with list input."""

    @numpy_fn
    def dummy_function(arr):
        # Check that input is indeed a numpy array
        assert isinstance(arr, np.ndarray)
        return arr + 1.0

    # Input is a list, output should be list
    with patch(
        "scitex.decorators.to_numpy",
        return_value=([np.array([1.0, 2.0, 3.0])], {}),
    ):
        result = dummy_function(test_data["list"])
        assert isinstance(result, list)
        assert result == [2.0, 3.0, 4.0]


def test_numpy_fn_with_numpy_input(test_data):
    """Test numpy_fn with numpy input."""

    @numpy_fn
    def dummy_function(arr):
        assert isinstance(arr, np.ndarray)
        return arr * 2.0

    # Input is numpy, output should be numpy
    with patch(
        "scitex.decorators.to_numpy",
        return_value=([np.array([1.0, 2.0, 3.0])], {}),
    ):
        result = dummy_function(test_data["numpy"])
        assert isinstance(result, np.ndarray)
        np.testing.assert_allclose(result, np.array([2.0, 4.0, 6.0]))


def test_numpy_fn_with_torch_input(test_data):
    """Test numpy_fn with torch tensor input."""

    @numpy_fn
    def dummy_function(arr):
        assert isinstance(arr, np.ndarray)
        return arr * 3.0

    # Mock to_numpy to return appropriate values
    with patch(
        "scitex.decorators.to_numpy",
        return_value=([np.array([1.0, 2.0, 3.0])], {}),
    ):
        # Mock torch.tensor for return conversion
        with patch("torch.tensor", return_value=torch.tensor([3.0, 6.0, 9.0])):
            result = dummy_function(test_data["torch"])
            assert isinstance(result, torch.Tensor)
            torch.testing.assert_close(result, torch.tensor([3.0, 6.0, 9.0]))


def test_numpy_fn_nested_decorator(test_data):
    """Test nested decorator behavior with numpy_fn."""

    # Create a dummy decorator to simulate nesting
    def dummy_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set nested context
            wrapper._current_decorator = "dummy_decorator"
            return func(*args, **kwargs)

        wrapper._is_wrapper = True
        return wrapper

    # Apply both decorators (nested)
    @numpy_fn
    @dummy_decorator
    def nested_function(arr):
        # In nested mode, the type should pass through unchanged from dummy_decorator
        assert not isinstance(arr, np.ndarray)
        return arr

    with patch("scitex.decorators._numpy_fn.is_nested_decorator", return_value=True):
        # Input list should stay as list due to nested context
        result = nested_function(test_data["list"])
        assert isinstance(result, list)
        assert result == test_data["list"]


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_numpy_fn.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 15:29:53 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_numpy_fn.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/decorators/_numpy_fn.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import numpy as np
# import pandas as pd
# import torch
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_numpy_fn.py"
#
# from functools import wraps
# from typing import Any as _Any
# from typing import Callable
#
# from ._converters import _return_always, is_nested_decorator, to_numpy
#
#
# def numpy_fn(func: Callable) -> Callable:
#     @wraps(func)
#     def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
#         # Skip conversion if already in a nested decorator context
#         if is_nested_decorator():
#             results = func(*args, **kwargs)
#             return results
#
#         # Set the current decorator context
#         wrapper._current_decorator = "numpy_fn"
#
#         # Store original object for type preservation
#         original_object = args[0] if args else None
#
#         converted_args, converted_kwargs = to_numpy(
#             *args, return_fn=_return_always, **kwargs
#         )
#
#         # Assertion to ensure all args are converted to numpy arrays
#         for arg_index, arg in enumerate(converted_args):
#             assert isinstance(
#                 arg, np.ndarray
#             ), f"Argument {arg_index} not converted to numpy array: {type(arg)}"
#
#         results = func(*converted_args, **converted_kwargs)
#
#         # Convert results back to original input types
#         if isinstance(results, np.ndarray):
#             if original_object is not None:
#                 if isinstance(original_object, list):
#                     return results.tolist()
#                 elif isinstance(original_object, torch.Tensor):
#                     return torch.tensor(results)
#                 elif isinstance(original_object, pd.DataFrame):
#                     return pd.DataFrame(results)
#                 elif isinstance(original_object, pd.Series):
#                     return pd.Series(results)
#             return results
#
#         return results
#
#     # Mark as a wrapper for detection
#     wrapper._is_wrapper = True
#     wrapper._decorator_type = "numpy_fn"
#     return wrapper
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_numpy_fn.py
# --------------------------------------------------------------------------------


def test_numpy_fn_with_nested_lists():
    """Test numpy_fn with nested lists."""
    @numpy_fn
    def dummy_function(arr):
        assert isinstance(arr, np.ndarray)
        return arr

    # Test nested list conversion
    nested_list = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    result = dummy_function(nested_list)
    assert isinstance(result, list)  # Should return as list to preserve type


def test_numpy_fn_preserves_scalars():
    """Test that numpy_fn preserves scalar arguments."""
    @numpy_fn
    def dummy_function(arr, alpha=1.0, beta=2, gamma=True, delta="test"):
        assert isinstance(arr, np.ndarray)
        assert isinstance(alpha, float)
        assert isinstance(beta, int)
        assert isinstance(gamma, bool)
        assert isinstance(delta, str)
        return alpha, beta, gamma, delta

    result = dummy_function([1, 2, 3])
    assert result == (1.0, 2, True, "test")


def test_numpy_fn_preserves_dimension_tuples():
    """Test that numpy_fn preserves dimension tuples."""
    @numpy_fn
    def dummy_function(arr, dim):
        assert isinstance(arr, np.ndarray)
        assert isinstance(dim, tuple)
        assert all(isinstance(d, int) for d in dim)
        return dim

    dim = (1, 2, 3)
    result = dummy_function(np.random.randn(4, 5, 6, 7), dim=dim)
    assert result == dim


def test_numpy_fn_with_mixed_types():
    """Test numpy_fn with mixed argument types."""
    @numpy_fn
    def dummy_function(data, scalar_val, string_val, dim):
        assert isinstance(data, np.ndarray)
        assert isinstance(scalar_val, int)
        assert isinstance(string_val, str) 
        assert isinstance(dim, tuple)
        return data.shape

    result = dummy_function([[1, 2, 3]], 42, "test", (0, 1))
    assert result == (1, 3)


def test_numpy_fn_handles_empty_lists():
    """Test numpy_fn with empty lists."""
    @numpy_fn
    def dummy_function(arr):
        return arr

    result = dummy_function([])
    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_numpy_fn_with_none_values():
    """Test numpy_fn handles None values correctly."""
    @numpy_fn  
    def dummy_function(arr, optional=None):
        assert isinstance(arr, np.ndarray)
        assert optional is None
        return arr

    result = dummy_function([1, 2, 3], optional=None)
    assert isinstance(result, list)
