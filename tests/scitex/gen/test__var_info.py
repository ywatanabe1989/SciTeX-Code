import numpy as np
import pandas as pd
import pytest
import torch
import xarray as xr

from scitex.gen import var_info


class TestVarInfoBasicTypes:
    """Test var_info with basic Python types."""

    def test_integer(self):
        """Test var_info with integer."""
        result = var_info(42)
        assert result == {"type": "int"}

    def test_float(self):
        """Test var_info with float."""
        result = var_info(3.14)
        assert result == {"type": "float"}

    def test_string(self):
        """Test var_info with string."""
        result = var_info("hello")
        assert result == {"type": "str", "length": 5}

    def test_boolean(self):
        """Test var_info with boolean."""
        result = var_info(True)
        assert result == {"type": "bool"}

    def test_none(self):
        """Test var_info with None."""
        result = var_info(None)
        assert result == {"type": "NoneType"}

    def test_dict(self):
        """Test var_info with dictionary."""
        result = var_info({"a": 1, "b": 2})
        assert result == {"type": "dict", "length": 2}

    def test_set(self):
        """Test var_info with set."""
        result = var_info({1, 2, 3})
        assert result == {"type": "set", "length": 3}

    def test_tuple(self):
        """Test var_info with tuple."""
        result = var_info((1, 2, 3))
        assert result == {"type": "tuple", "length": 3}


class TestVarInfoLists:
    """Test var_info with list structures."""

    def test_empty_list(self):
        """Test var_info with empty list."""
        result = var_info([])
        assert result == {"type": "list", "length": 0}

    def test_flat_list(self):
        """Test var_info with flat list."""
        result = var_info([1, 2, 3, 4])
        assert result == {"type": "list", "length": 4}

    def test_nested_list_2d(self):
        """Test var_info with 2D nested list."""
        data = [[1, 2, 3], [4, 5, 6]]
        result = var_info(data)
        assert result == {"type": "list", "length": 2, "shape": (2, 3), "dimensions": 2}

    def test_nested_list_3d(self):
        """Test var_info with 3D nested list."""
        data = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        result = var_info(data)
        assert result == {
            "type": "list",
            "length": 2,
            "shape": (2, 2, 2),
            "dimensions": 3,
        }

    def test_irregular_nested_list(self):
        """Test var_info with irregular nested list."""
        # Only checks first element's shape
        data = [[1, 2, 3], [4, 5]]  # Irregular
        result = var_info(data)
        assert result == {
            "type": "list",
            "length": 2,
            "shape": (2, 3),  # Uses first element's length
            "dimensions": 2,
        }

    def test_mixed_type_list(self):
        """Test var_info with mixed type list."""
        data = [1, "hello", 3.14, [1, 2]]
        result = var_info(data)
        assert result == {"type": "list", "length": 4}


class TestVarInfoNumPy:
    """Test var_info with NumPy arrays."""

    def test_numpy_1d(self):
        """Test var_info with 1D NumPy array."""
        arr = np.array([1, 2, 3, 4])
        result = var_info(arr)
        assert result == {
            "type": "ndarray",
            "length": 4,
            "shape": (4,),
            "dimensions": 1,
        }

    def test_numpy_2d(self):
        """Test var_info with 2D NumPy array."""
        arr = np.array([[1, 2], [3, 4]])
        result = var_info(arr)
        assert result == {
            "type": "ndarray",
            "length": 2,
            "shape": (2, 2),
            "dimensions": 2,
        }

    def test_numpy_3d(self):
        """Test var_info with 3D NumPy array."""
        arr = np.zeros((2, 3, 4))
        result = var_info(arr)
        assert result == {
            "type": "ndarray",
            "length": 2,
            "shape": (2, 3, 4),
            "dimensions": 3,
        }

    def test_numpy_scalar(self):
        """Test var_info with NumPy scalar."""
        scalar = np.int64(42)
        result = var_info(scalar)
        assert result == {"type": "int64", "shape": (), "dimensions": 0}


class TestVarInfoPandas:
    """Test var_info with Pandas objects."""

    def test_pandas_series(self):
        """Test var_info with Pandas Series."""
        series = pd.Series([1, 2, 3, 4])
        result = var_info(series)
        assert result == {"type": "Series", "length": 4, "shape": (4,), "dimensions": 1}

    def test_pandas_dataframe(self):
        """Test var_info with Pandas DataFrame."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = var_info(df)
        assert result == {
            "type": "DataFrame",
            "length": 3,  # Number of rows
            "shape": (3, 2),
            "dimensions": 2,
        }

    def test_empty_dataframe(self):
        """Test var_info with empty DataFrame."""
        df = pd.DataFrame()
        result = var_info(df)
        assert result == {
            "type": "DataFrame",
            "length": 0,
            "shape": (0, 0),
            "dimensions": 2,
        }


class TestVarInfoXArray:
    """Test var_info with xarray objects."""

    def test_xarray_dataarray(self):
        """Test var_info with xarray DataArray."""
        data = xr.DataArray(
            np.random.randn(2, 3),
            dims=["x", "y"],
            coords={"x": [1, 2], "y": [10, 20, 30]},
        )
        result = var_info(data)
        assert result == {
            "type": "DataArray",
            "length": 2,
            "shape": (2, 3),
            "dimensions": 2,
        }

    def test_xarray_1d(self):
        """Test var_info with 1D xarray."""
        data = xr.DataArray([1, 2, 3, 4], dims=["time"])
        result = var_info(data)
        assert result == {
            "type": "DataArray",
            "length": 4,
            "shape": (4,),
            "dimensions": 1,
        }


class TestVarInfoTorch:
    """Test var_info with PyTorch tensors."""

    def test_torch_1d(self):
        """Test var_info with 1D torch tensor."""
        tensor = torch.tensor([1, 2, 3, 4])
        result = var_info(tensor)
        assert result == {
            "type": "Tensor",
            "length": 4,
            "shape": torch.Size([4]),
            "dimensions": 1,
        }

    def test_torch_2d(self):
        """Test var_info with 2D torch tensor."""
        tensor = torch.zeros(3, 4)
        result = var_info(tensor)
        assert result == {
            "type": "Tensor",
            "length": 3,
            "shape": torch.Size([3, 4]),
            "dimensions": 2,
        }

    def test_torch_4d(self):
        """Test var_info with 4D torch tensor (common in CNNs)."""
        tensor = torch.randn(16, 3, 224, 224)  # batch, channels, height, width
        result = var_info(tensor)
        assert result == {
            "type": "Tensor",
            "length": 16,
            "shape": torch.Size([16, 3, 224, 224]),
            "dimensions": 4,
        }


class TestVarInfoEdgeCases:
    """Test var_info with edge cases."""

    def test_custom_class(self):
        """Test var_info with custom class."""

        class MyClass:
            pass

        obj = MyClass()
        result = var_info(obj)
        assert result == {"type": "MyClass"}

    def test_function(self):
        """Test var_info with function."""

        def my_func():
            pass

        result = var_info(my_func)
        assert result == {"type": "function"}

    def test_lambda(self):
        """Test var_info with lambda."""
        f = lambda x: x + 1
        result = var_info(f)
        assert result == {"type": "function"}

    def test_generator(self):
        """Test var_info with generator."""
        gen = (x for x in range(10))
        result = var_info(gen)
        assert result["type"] == "generator"
        # Generators don't have length
        assert "length" not in result

    def test_bytes(self):
        """Test var_info with bytes."""
        data = b"hello"
        result = var_info(data)
        assert result == {"type": "bytes", "length": 5}

    def test_range(self):
        """Test var_info with range object."""
        r = range(10)
        result = var_info(r)
        assert result == {"type": "range", "length": 10}


class TestVarInfoIntegration:
    """Integration tests for var_info."""

    def test_docstring_example(self):
        """Test the example from the docstring."""
        data = np.array([[1, 2], [3, 4]])
        info = var_info(data)
        assert info == {
            "type": "ndarray",
            "length": 2,
            "shape": (2, 2),
            "dimensions": 2,
        }

    def test_complex_nested_structure(self):
        """Test with complex nested data structure."""
        data = {
            "arrays": [np.array([1, 2, 3]), np.array([[1, 2], [3, 4]])],
            "tensors": torch.tensor([1.0, 2.0, 3.0]),
            "df": pd.DataFrame({"a": [1, 2], "b": [3, 4]}),
        }

        result = var_info(data)
        assert result == {"type": "dict", "length": 3}

        # Check individual components
        assert var_info(data["arrays"][0])["shape"] == (3,)
        assert var_info(data["tensors"])["shape"] == torch.Size([3])
        assert var_info(data["df"])["shape"] == (2, 2)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_var_info.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 00:35:31 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_var_info.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_var_info.py"
#
# from typing import Any, Union
# import numpy as np
# import pandas as pd
# import torch
# import xarray as xr
#
# ArrayLike = Union[list, tuple, np.ndarray, pd.Series, pd.DataFrame, xr.DataArray, torch.Tensor]
#
# def var_info(variable: Any) -> dict:
#     """Returns type and structural information about a variable.
#
#     Example
#     -------
#     >>> data = np.array([[1, 2], [3, 4]])
#     >>> info = var_info(data)
#     >>> print(info)
#     {
#         'type': 'numpy.ndarray',
#         'length': 2,
#         'shape': (2, 2),
#         'dimensions': 2
#     }
#
#     Parameters
#     ----------
#     variable : Any
#         Variable to inspect.
#
#     Returns
#     -------
#     dict
#         Dictionary containing variable information.
#     """
#     info = {'type': type(variable).__name__}
#
#     # Length check
#     if hasattr(variable, '__len__'):
#         info['length'] = len(variable)
#
#     # Shape check for array-like objects
#     if isinstance(variable, (np.ndarray, pd.DataFrame, pd.Series,
#                            xr.DataArray, torch.Tensor)):
#         info['shape'] = variable.shape
#         info['dimensions'] = len(variable.shape)
#
#     # Special handling for nested lists
#     elif isinstance(variable, list):
#         if variable and isinstance(variable[0], list):
#             depth = 1
#             current = variable
#             shape = [len(variable)]
#             while current and isinstance(current[0], list):
#                 shape.append(len(current[0]))
#                 current = current[0]
#                 depth += 1
#             info['shape'] = tuple(shape)
#             info['dimensions'] = depth
#
#     return info
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_var_info.py
# --------------------------------------------------------------------------------
