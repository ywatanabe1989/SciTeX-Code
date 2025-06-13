#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:00:00 (claude)"
# File: ./tests/scitex/gen/test__type.py

"""
Comprehensive tests for scitex.gen._type module.

This module tests:
- var_info function for various data types
- ArrayLike type alias usage
- Edge cases and error handling
"""

import pytest
import numpy as np
import pandas as pd
import torch
import xarray as xr
from typing import get_args

from scitex.gen import ArrayLike, var_info


class TestArrayLikeTypeAlias:
    """Test the ArrayLike type alias definition."""

    def test_arraylike_types(self):
        """Test that ArrayLike includes all expected types."""

        expected_types = (
            list,
            tuple,
            np.ndarray,
            pd.Series,
            pd.DataFrame,
            xr.DataArray,
            torch.Tensor,
        )
        actual_types = get_args(ArrayLike)

        assert set(actual_types) == set(expected_types)
        assert len(actual_types) == 7


class TestVarInfoBasicTypes:
    """Test var_info with basic Python types."""

    def test_int(self):
        """Test var_info with integer."""

        result = var_info(42)
        assert result["type"] == "int"
        assert "length" not in result
        assert "shape" not in result
        assert "dimensions" not in result

    def test_float(self):
        """Test var_info with float."""

        result = var_info(3.14)
        assert result["type"] == "float"
        assert "length" not in result

    def test_string(self):
        """Test var_info with string."""

        result = var_info("hello")
        assert result["type"] == "str"
        assert result["length"] == 5
        assert "shape" not in result

    def test_list(self):
        """Test var_info with simple list."""

        result = var_info([1, 2, 3])
        assert result["type"] == "list"
        assert result["length"] == 3
        assert "shape" not in result
        assert "dimensions" not in result

    def test_tuple(self):
        """Test var_info with tuple."""

        result = var_info((1, 2, 3))
        assert result["type"] == "tuple"
        assert result["length"] == 3
        assert "shape" not in result

    def test_dict(self):
        """Test var_info with dictionary."""

        result = var_info({"a": 1, "b": 2})
        assert result["type"] == "dict"
        assert result["length"] == 2
        assert "shape" not in result

    def test_set(self):
        """Test var_info with set."""

        result = var_info({1, 2, 3})
        assert result["type"] == "set"
        assert result["length"] == 3
        assert "shape" not in result

    def test_none(self):
        """Test var_info with None."""

        result = var_info(None)
        assert result["type"] == "NoneType"
        assert "length" not in result


class TestVarInfoNestedLists:
    """Test var_info with nested list structures."""

    def test_2d_list(self):
        """Test var_info with 2D list."""

        data = [[1, 2, 3], [4, 5, 6]]
        result = var_info(data)

        assert result["type"] == "list"
        assert result["length"] == 2
        assert result["shape"] == (2, 3)
        assert result["dimensions"] == 2

    def test_3d_list(self):
        """Test var_info with 3D list."""

        data = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        result = var_info(data)

        assert result["type"] == "list"
        assert result["length"] == 2
        assert result["shape"] == (2, 2, 2)
        assert result["dimensions"] == 3

    def test_jagged_list(self):
        """Test var_info with jagged list (inconsistent dimensions)."""

        data = [[1, 2], [3, 4, 5]]  # Different lengths
        result = var_info(data)

        assert result["type"] == "list"
        assert result["length"] == 2
        assert result["shape"] == (2, 2)  # Uses first element's length
        assert result["dimensions"] == 2

    def test_empty_nested_list(self):
        """Test var_info with empty nested list."""

        data = [[]]
        result = var_info(data)

        assert result["type"] == "list"
        assert result["length"] == 1
        assert result["shape"] == (1, 0)
        assert result["dimensions"] == 2


class TestVarInfoNumPy:
    """Test var_info with NumPy arrays."""

    def test_numpy_1d(self):
        """Test var_info with 1D numpy array."""

        data = np.array([1, 2, 3, 4, 5])
        result = var_info(data)

        assert result["type"] == "ndarray"
        assert result["length"] == 5
        assert result["shape"] == (5,)
        assert result["dimensions"] == 1

    def test_numpy_2d(self):
        """Test var_info with 2D numpy array."""

        data = np.array([[1, 2], [3, 4], [5, 6]])
        result = var_info(data)

        assert result["type"] == "ndarray"
        assert result["length"] == 3
        assert result["shape"] == (3, 2)
        assert result["dimensions"] == 2

    def test_numpy_3d(self):
        """Test var_info with 3D numpy array."""

        data = np.zeros((2, 3, 4))
        result = var_info(data)

        assert result["type"] == "ndarray"
        assert result["length"] == 2
        assert result["shape"] == (2, 3, 4)
        assert result["dimensions"] == 3

    def test_numpy_scalar(self):
        """Test var_info with numpy scalar."""

        data = np.float32(3.14)
        result = var_info(data)

        assert result["type"] == "float32"
        assert result["shape"] == ()
        assert result["dimensions"] == 0


class TestVarInfoPandas:
    """Test var_info with Pandas objects."""

    def test_pandas_series(self):
        """Test var_info with pandas Series."""

        data = pd.Series([1, 2, 3, 4, 5])
        result = var_info(data)

        assert result["type"] == "Series"
        assert result["length"] == 5
        assert result["shape"] == (5,)
        assert result["dimensions"] == 1

    def test_pandas_dataframe(self):
        """Test var_info with pandas DataFrame."""

        data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        result = var_info(data)

        assert result["type"] == "DataFrame"
        assert result["length"] == 3
        assert result["shape"] == (3, 2)
        assert result["dimensions"] == 2

    def test_pandas_empty_dataframe(self):
        """Test var_info with empty DataFrame."""

        data = pd.DataFrame()
        result = var_info(data)

        assert result["type"] == "DataFrame"
        assert result["length"] == 0
        assert result["shape"] == (0, 0)
        assert result["dimensions"] == 2


class TestVarInfoPyTorch:
    """Test var_info with PyTorch tensors."""

    def test_torch_1d(self):
        """Test var_info with 1D torch tensor."""

        data = torch.tensor([1, 2, 3, 4, 5])
        result = var_info(data)

        assert result["type"] == "Tensor"
        assert result["length"] == 5
        assert result["shape"] == torch.Size([5])
        assert result["dimensions"] == 1

    def test_torch_2d(self):
        """Test var_info with 2D torch tensor."""

        data = torch.zeros(3, 4)
        result = var_info(data)

        assert result["type"] == "Tensor"
        assert result["length"] == 3
        assert result["shape"] == torch.Size([3, 4])
        assert result["dimensions"] == 2

    def test_torch_4d(self):
        """Test var_info with 4D torch tensor (common in CNN)."""

        data = torch.randn(16, 3, 224, 224)  # Batch, channels, height, width
        result = var_info(data)

        assert result["type"] == "Tensor"
        assert result["length"] == 16
        assert result["shape"] == torch.Size([16, 3, 224, 224])
        assert result["dimensions"] == 4


class TestVarInfoXArray:
    """Test var_info with xarray objects."""

    def test_xarray_dataarray(self):
        """Test var_info with xarray DataArray."""

        data = xr.DataArray(np.random.randn(2, 3, 4), dims=["x", "y", "z"])
        result = var_info(data)

        assert result["type"] == "DataArray"
        assert result["length"] == 2
        assert result["shape"] == (2, 3, 4)
        assert result["dimensions"] == 3

    def test_xarray_with_coords(self):
        """Test var_info with xarray DataArray with coordinates."""

        data = xr.DataArray(
            np.random.randn(3, 4),
            coords={"x": [1, 2, 3], "y": [10, 20, 30, 40]},
            dims=["x", "y"],
        )
        result = var_info(data)

        assert result["type"] == "DataArray"
        assert result["length"] == 3
        assert result["shape"] == (3, 4)
        assert result["dimensions"] == 2


class TestVarInfoEdgeCases:
    """Test var_info with edge cases."""

    def test_empty_list(self):
        """Test var_info with empty list."""

        result = var_info([])
        assert result["type"] == "list"
        assert result["length"] == 0
        assert "shape" not in result
        assert "dimensions" not in result

    def test_custom_object(self):
        """Test var_info with custom object."""

        class CustomObject:
            def __len__(self):
                return 42

        obj = CustomObject()
        result = var_info(obj)

        assert result["type"] == "CustomObject"
        assert result["length"] == 42
        assert "shape" not in result

    def test_generator(self):
        """Test var_info with generator."""

        gen = (x for x in range(5))
        result = var_info(gen)

        assert result["type"] == "generator"
        assert "length" not in result  # Generators don't have __len__
        assert "shape" not in result

    def test_mixed_nested_list(self):
        """Test var_info with mixed nested structures."""

        data = [[1, 2], "string", [3, 4]]  # Mixed types
        result = var_info(data)

        assert result["type"] == "list"
        assert result["length"] == 3
        # Should handle gracefully, only checking first element
        assert "shape" in result
        assert result["shape"] == (3, 2)


class TestVarInfoIntegration:
    """Integration tests for var_info function."""

    def test_documentation_example(self):
        """Test the example from the docstring."""

        data = np.array([[1, 2], [3, 4]])
        info = var_info(data)

        assert info["type"] == "ndarray"
        assert info["length"] == 2
        assert info["shape"] == (2, 2)
        assert info["dimensions"] == 2

    def test_multiple_calls(self):
        """Test multiple calls with different types."""

        # Should handle different types without state issues
        result1 = var_info([1, 2, 3])
        result2 = var_info(np.array([1, 2, 3]))
        result3 = var_info("string")

        assert result1["type"] == "list"
        assert result2["type"] == "ndarray"
        assert result3["type"] == "str"

    @pytest.mark.parametrize(
        "data,expected_type,has_shape",
        [
            ([1, 2, 3], "list", False),
            (np.array([1, 2, 3]), "ndarray", True),
            (pd.Series([1, 2, 3]), "Series", True),
            (torch.tensor([1, 2, 3]), "Tensor", True),
            ("test", "str", False),
            (42, "int", False),
        ],
    )
    def test_parametrized_types(self, data, expected_type, has_shape):
        """Test var_info with various types using parametrization."""

        result = var_info(data)
        assert result["type"] == expected_type
        assert ("shape" in result) == has_shape


if __name__ == "__main__":
    # Run specific test file
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
