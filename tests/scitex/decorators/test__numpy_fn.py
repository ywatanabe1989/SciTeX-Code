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
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_numpy_fn.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 15:29:53 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_numpy_fn.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/decorators/_numpy_fn.py"
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
#         # Skip strict assertion for certain types that may not convert to arrays
#         # Instead, convert what we can and pass through what we can't
#         validated_args = []
#         for arg_index, arg in enumerate(converted_args):
#             if isinstance(arg, np.ndarray):
#                 validated_args.append(arg)
#             elif isinstance(arg, (int, float, str, type(None))):
#                 # Pass through scalars and strings unchanged
#                 validated_args.append(arg)
#             elif isinstance(arg, list) and all(isinstance(item, np.ndarray) for item in arg):
#                 # List of arrays - pass through as is
#                 validated_args.append(arg)
#             else:
#                 # Try one more conversion attempt
#                 try:
#                     validated_args.append(np.array(arg))
#                 except:
#                     # If all else fails, pass through unchanged
#                     validated_args.append(arg)
# 
#         results = func(*validated_args, **converted_kwargs)
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
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_numpy_fn.py
# --------------------------------------------------------------------------------
