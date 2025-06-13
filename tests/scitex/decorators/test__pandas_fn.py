#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 15:59:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/decorators/test__pandas_fn.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/decorators/test__pandas_fn.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from functools import wraps
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch
import xarray as xr
from scitex.decorators import pandas_fn


@pytest.fixture
def test_data():
    """Create test data for tests."""
    return {
        "list": [1.0, 2.0, 3.0],
        "numpy": np.array([1.0, 2.0, 3.0]),
        "pandas_series": pd.Series([1.0, 2.0, 3.0]),
        "pandas_df": pd.DataFrame({"col1": [1.0, 2.0, 3.0]}),
        "torch": torch.tensor([1.0, 2.0, 3.0]),
        "xarray": xr.DataArray([1.0, 2.0, 3.0]),
    }


def test_pandas_fn_with_list_input(test_data):
    """Test pandas_fn with list input."""

    @pandas_fn
    def dummy_function(df):
        # Check that input is indeed a DataFrame
        assert isinstance(df, pd.DataFrame)
        return df + 1.0

    # Input is a list, output should be list
    result = dummy_function(test_data["list"])
    assert isinstance(result, list)
    assert result == [[2.0], [3.0], [4.0]] or result == [2.0, 3.0, 4.0]


def test_pandas_fn_with_df_input(test_data):
    """Test pandas_fn with DataFrame input."""

    @pandas_fn
    def dummy_function(df):
        assert isinstance(df, pd.DataFrame)
        return df * 2.0

    # Input is DataFrame, output should be DataFrame
    result = dummy_function(test_data["pandas_df"])
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, pd.DataFrame({"col1": [2.0, 4.0, 6.0]}))


def test_pandas_fn_with_numpy_input(test_data):
    """Test pandas_fn with numpy input."""

    @pandas_fn
    def dummy_function(df):
        assert isinstance(df, pd.DataFrame)
        return df * 3.0

    # Input is numpy, output should be numpy
    result = dummy_function(test_data["numpy"])
    assert isinstance(result, np.ndarray)
    np.testing.assert_allclose(result, np.array([[3.0], [6.0], [9.0]]))


def test_pandas_fn_nested_decorator(test_data):
    """Test nested decorator behavior with pandas_fn."""

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
    @pandas_fn
    @dummy_decorator
    def nested_function(arr):
        # In nested mode, the type should pass through unchanged from dummy_decorator
        assert not isinstance(arr, pd.DataFrame)
        return arr

    with patch("scitex.decorators._pandas_fn.is_nested_decorator", return_value=True):
        # Input series should stay as series due to nested context
        result = nested_function(test_data["pandas_series"])
        assert isinstance(result, pd.Series)
        pd.testing.assert_series_equal(result, test_data["pandas_series"])


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_pandas_fn.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 15:44:00 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_pandas_fn.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/decorators/_pandas_fn.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_pandas_fn.py"
#
# from functools import wraps
# from typing import Any as _Any
# from typing import Callable
#
# import numpy as np
# import pandas as pd
# import torch
# import xarray as xr
#
# from ._converters import is_nested_decorator
#
#
# def pandas_fn(func: Callable) -> Callable:
#     @wraps(func)
#     def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
#         # Skip conversion if already in a nested decorator context
#         if is_nested_decorator():
#             results = func(*args, **kwargs)
#             return results
#
#         # Set the current decorator context
#         wrapper._current_decorator = "pandas_fn"
#
#         # Store original object for type preservation
#         original_object = args[0] if args else None
#
#         # Convert args to pandas DataFrames
#         def to_pandas(data):
#             if isinstance(data, pd.DataFrame):
#                 return data
#             elif isinstance(data, pd.Series):
#                 return pd.DataFrame(data)
#             elif isinstance(data, np.ndarray):
#                 return pd.DataFrame(data)
#             elif isinstance(data, list):
#                 return pd.DataFrame(data)
#             elif isinstance(data, torch.Tensor):
#                 return pd.DataFrame(data.detach().cpu().numpy())
#             elif isinstance(data, xr.DataArray):
#                 return pd.DataFrame(data.values)
#             else:
#                 return pd.DataFrame([data])
#
#         converted_args = [to_pandas(arg) for arg in args]
#         converted_kwargs = {k: to_pandas(v) for k, v in kwargs.items()}
#
#         # Assertion to ensure all args are converted to pandas DataFrames
#         for arg_index, arg in enumerate(converted_args):
#             assert isinstance(
#                 arg, pd.DataFrame
#             ), f"Argument {arg_index} not converted to DataFrame: {type(arg)}"
#
#         results = func(*converted_args, **converted_kwargs)
#
#         # Convert results back to original input types
#         if isinstance(results, pd.DataFrame):
#             if original_object is not None:
#                 if isinstance(original_object, list):
#                     return results.values.tolist()
#                 elif isinstance(original_object, np.ndarray):
#                     return results.values
#                 elif isinstance(original_object, torch.Tensor):
#                     return torch.tensor(results.values)
#                 elif isinstance(original_object, pd.Series):
#                     return (
#                         pd.Series(results.iloc[:, 0])
#                         if results.shape[1] > 0
#                         else pd.Series()
#                     )
#                 elif isinstance(original_object, xr.DataArray):
#                     return xr.DataArray(results.values)
#             return results
#
#         return results
#
#     # Mark as a wrapper for detection
#     wrapper._is_wrapper = True
#     wrapper._decorator_type = "pandas_fn"
#     return wrapper
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_pandas_fn.py
# --------------------------------------------------------------------------------
