#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test__cache.py

"""Tests for the cache function in scitex.io module."""

import os
import pickle
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest


class TestCacheBasic:
    """Test basic cache functionality."""

    def test_cache_save_and_load(self, tmp_path, monkeypatch):
        """Test saving and loading variables with cache."""
        # Patch the cache directory to use tmp_path
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Define variables
            var1 = "test_string"
            var2 = 42
            var3 = [1, 2, 3, 4, 5]

            # Save to cache
            result = cache("test_id", "var1", "var2", "var3")
            assert result == (var1, var2, var3)

            # Check cache file exists
            cache_file = tmp_path / ".cache" / "your_app_name" / "test_id.pkl"
            assert cache_file.exists()

            # Delete variables and load from cache
            del var1, var2, var3
            var1, var2, var3 = cache("test_id", "var1", "var2", "var3")

            assert var1 == "test_string"
            assert var2 == 42
            assert var3 == [1, 2, 3, 4, 5]

    def test_cache_with_numpy_array(self, tmp_path):
        """Test caching numpy arrays."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Create numpy arrays
            arr1 = np.ones((3, 3))
            arr2 = np.random.rand(10, 5)
            arr3 = np.array([1, 2, 3, 4, 5])

            # Save to cache
            result = cache("numpy_test", "arr1", "arr2", "arr3")

            # Delete and reload
            del arr1, arr2, arr3
            arr1, arr2, arr3 = cache("numpy_test", "arr1", "arr2", "arr3")

            assert np.array_equal(arr1, np.ones((3, 3)))
            assert arr2.shape == (10, 5)
            assert np.array_equal(arr3, np.array([1, 2, 3, 4, 5]))

    def test_cache_overwrites_existing(self, tmp_path):
        """Test that cache overwrites existing cached data."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # First save
            var1 = "original"
            cache("overwrite_test", "var1")

            # Update and save again
            var1 = "updated"
            cache("overwrite_test", "var1")

            # Load and verify
            del var1
            (var1,) = cache("overwrite_test", "var1")
            assert var1 == "updated"


class TestCacheErrorHandling:
    """Test error handling in cache function."""

    def test_cache_missing_file_error(self, tmp_path):
        """Test error when cache file doesn't exist and variables not defined."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Try to load non-existent cache without variables defined
            with pytest.raises(ValueError, match="Cache file not found"):
                cache("nonexistent_id", "var1", "var2")

    def test_cache_partial_variables_defined(self, tmp_path):
        """Test behavior when only some variables are defined."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Define all variables and cache
            var1 = "test"
            var2 = 100
            var3 = [1, 2, 3]
            cache("partial_test", "var1", "var2", "var3")

            # Delete some variables
            del var2, var3
            # var1 is still defined, but we're asking for all three

            # Should load from cache since not all are defined
            var1_loaded, var2_loaded, var3_loaded = cache(
                "partial_test", "var1", "var2", "var3"
            )
            assert var1_loaded == "test"
            assert var2_loaded == 100
            assert var3_loaded == [1, 2, 3]


class TestCacheAdvanced:
    """Test advanced cache scenarios."""

    def test_cache_complex_objects(self, tmp_path):
        """Test caching complex Python objects."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Complex objects
            dict_var = {"a": 1, "b": [2, 3], "c": {"nested": True}}
            set_var = {1, 2, 3, 4, 5}
            tuple_var = (1, "two", 3.0, [4, 5])

            # Cache them
            cache("complex_test", "dict_var", "set_var", "tuple_var")

            # Delete and reload
            del dict_var, set_var, tuple_var
            dict_var, set_var, tuple_var = cache(
                "complex_test", "dict_var", "set_var", "tuple_var"
            )

            assert dict_var == {"a": 1, "b": [2, 3], "c": {"nested": True}}
            assert set_var == {1, 2, 3, 4, 5}
            assert tuple_var == (1, "two", 3.0, [4, 5])

    def test_cache_multiple_ids(self, tmp_path):
        """Test using multiple cache IDs."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Save different data with different IDs
            data1 = "first"
            cache("id1", "data1")

            data1 = "second"  # Reuse variable name
            cache("id2", "data1")

            # Load from different caches
            del data1
            (result1,) = cache("id1", "data1")
            assert result1 == "first"

            (result2,) = cache("id2", "data1")
            assert result2 == "second"

    def test_cache_directory_creation(self, tmp_path):
        """Test that cache creates necessary directories."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Ensure cache directory doesn't exist initially
            cache_dir = tmp_path / ".cache" / "your_app_name"
            assert not cache_dir.exists()

            # Use cache
            var1 = "test"
            cache("dir_test", "var1")

            # Check directory was created
            assert cache_dir.exists()
            assert cache_dir.is_dir()

    def test_cache_single_variable(self, tmp_path):
        """Test caching a single variable."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Single variable
            important_data = {"key": "value", "number": 42}

            # Cache it
            (result,) = cache("single_var", "important_data")
            assert result == important_data

            # Delete and reload
            del important_data
            (important_data,) = cache("single_var", "important_data")
            assert important_data == {"key": "value", "number": 42}


class TestCacheEdgeCases:
    """Test edge cases for cache function."""

    def test_cache_empty_args(self, tmp_path):
        """Test cache with no variable arguments."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Should work but cache nothing
            result = cache("empty_test")
            assert result == ()

    def test_cache_none_values(self, tmp_path):
        """Test caching None values."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            var1 = None
            var2 = "not none"
            var3 = None

            cache("none_test", "var1", "var2", "var3")

            del var1, var2, var3
            var1, var2, var3 = cache("none_test", "var1", "var2", "var3")

            assert var1 is None
            assert var2 == "not none"
            assert var3 is None

    def test_cache_special_characters_in_id(self, tmp_path):
        """Test cache with special characters in ID."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # IDs with special characters
            test_ids = [
                "test-with-dash",
                "test_with_underscore",
                "test.with.dot",
                "test@with@at",
            ]

            for test_id in test_ids:
                data = f"data_for_{test_id}"
                cache(test_id, "data")

                del data
                (data,) = cache(test_id, "data")
                assert data == f"data_for_{test_id}"


class TestCacheIntegration:
    """Test cache integration with other scitex features."""

    def test_cache_with_large_data(self, tmp_path):
        """Test caching large data structures."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            # Create large data
            large_array = np.random.rand(1000, 1000)
            large_list = list(range(10000))
            large_dict = {str(i): i for i in range(1000)}

            # Cache it
            cache("large_data", "large_array", "large_list", "large_dict")

            # Verify file was created and has reasonable size
            cache_file = tmp_path / ".cache" / "your_app_name" / "large_data.pkl"
            assert cache_file.exists()
            assert cache_file.stat().st_size > 1000  # Should be reasonably large

    def test_cache_caller_frame_access(self, tmp_path):
        """Test that cache correctly accesses caller's frame."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            from scitex.io import cache

            def inner_function():
                # Variables defined in this scope
                inner_var1 = "inner"
                inner_var2 = 123
                return cache("frame_test", "inner_var1", "inner_var2")

            # Call the function
            result = inner_function()
            assert result == ("inner", 123)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
# import sys
# from pathlib import Path
#
#
# def cache(id, *args):
#     """
#     Store or fetch data using a pickle file.
#
#     This function provides a simple caching mechanism for storing and retrieving
#     Python objects. It uses pickle to serialize the data and stores it in a file
#     with a unique identifier. If the data is already cached, it can be retrieved
#     without recomputation.
#
#     Parameters:
#     -----------
#     id : str
#         A unique identifier for the cache file.
#     *args : str
#         Variable names to be cached or loaded.
#
#     Returns:
#     --------
#     tuple
#         A tuple of cached values corresponding to the input variable names.
#
#     Raises:
#     -------
#     ValueError
#         If the cache file is not found and not all variables are defined.
#
#     Example:
#     --------
#     >>> import scitex
#     >>> import numpy as np
#     >>>
#     >>> # Variables to cache
#     >>> var1 = "x"
#     >>> var2 = 1
#     >>> var3 = np.ones(10)
#     >>>
#     >>> # Saving
#     >>> var1, var2, var3 = scitex.io.cache("my_id", "var1", "var2", "var3")
#     >>> print(var1, var2, var3)
#     >>>
#     >>> # Loading when not all variables are defined and the id exists
#     >>> del var1, var2, var3
#     >>> var1, var2, var3 = scitex.io.cache("my_id", "var1", "var2", "var3")
#     >>> print(var1, var2, var3)
#     """
#     cache_dir = Path.home() / ".cache" / "your_app_name"
#     cache_dir.mkdir(parents=True, exist_ok=True)
#     cache_file = cache_dir / f"{id}.pkl"
#
#     does_cache_file_exist = cache_file.exists()
#
#     # Get the caller's local variables
#     caller_locals = sys._getframe(1).f_locals
#     are_all_variables_defined = all(arg in caller_locals for arg in args)
#
#     if are_all_variables_defined:
#         # If all variables are defined, save them to cache and return as-is
#         data_to_cache = {arg: caller_locals[arg] for arg in args}
#         with cache_file.open("wb") as f:
#             pickle.dump(data_to_cache, f)
#         return tuple(data_to_cache.values())
#     else:
#         if does_cache_file_exist:
#             # If cache exists, load and return the values
#             with cache_file.open("rb") as f:
#                 loaded_data = pickle.load(f)
#             return tuple(loaded_data[arg] for arg in args)
#         else:
#             raise ValueError(
#                 "Cache file not found and not all variables are defined."
#             )
#
#
# # Usage example
# if __name__ == "__main__":
#     import scitex
#     import numpy as np
#
#     # Variables to cache
#     var1 = "x"
#     var2 = 1
#     var3 = np.ones(10)
#
#     # Saving
#     var1, var2, var3 = scitex.io.cache("my_id", "var1", "var2", "var3")
#     print(var1, var2, var3)
#
#     # Loading when not all variables are defined and the id exists
#     del var1, var2, var3
#     var1, var2, var3 = scitex.io.cache("my_id", "var1", "var2", "var3")
#     print(var1, var2, var3)
#

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_cache.py
# --------------------------------------------------------------------------------
