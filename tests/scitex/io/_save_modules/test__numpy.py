#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:46:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__numpy.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__numpy.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for NumPy saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from scitex.io._save_modules import save_numpy


class TestSaveNumpy:
    """Test suite for save_numpy function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_npy = os.path.join(self.temp_dir, "test.npy")
        self.test_file_npz = os.path.join(self.temp_dir, "test.npz")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_numpy_array_npy(self):
        """Test saving numpy array as .npy"""
        arr = np.array([1, 2, 3, 4, 5])
        save_numpy(arr, self.test_file_npy)
        
        assert os.path.exists(self.test_file_npy)
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_numpy_array_npz(self):
        """Test saving numpy array as .npz"""
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        save_numpy(arr, self.test_file_npz)
        
        assert os.path.exists(self.test_file_npz)
        loaded = np.load(self.test_file_npz)
        np.testing.assert_array_equal(arr, loaded["arr_0"])

    def test_save_dict_npz(self):
        """Test saving dictionary of arrays as .npz"""
        data = {
            "array1": np.array([1, 2, 3]),
            "array2": np.array([[4, 5], [6, 7]]),
            "array3": np.array([1.1, 2.2, 3.3])
        }
        save_numpy(data, self.test_file_npz)
        
        loaded = np.load(self.test_file_npz)
        for key in data:
            np.testing.assert_array_equal(data[key], loaded[key])

    def test_save_list_as_array(self):
        """Test saving list as numpy array"""
        lst = [1, 2, 3, 4, 5]
        save_numpy(lst, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(np.array(lst), loaded)

    def test_save_2d_list(self):
        """Test saving 2D list"""
        lst = [[1, 2, 3], [4, 5, 6]]
        save_numpy(lst, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(np.array(lst), loaded)

    def test_save_multidimensional_array(self):
        """Test saving multi-dimensional array"""
        arr = np.random.randn(10, 20, 30)
        save_numpy(arr, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_compressed(self):
        """Test saving with compression"""
        arr = np.random.randn(1000, 1000)
        save_numpy(arr, self.test_file_npz, compress=True)
        
        assert os.path.exists(self.test_file_npz)
        loaded = np.load(self.test_file_npz)
        np.testing.assert_array_almost_equal(arr, loaded["arr_0"])

    def test_save_different_dtypes(self):
        """Test saving arrays with different data types"""
        arrays = {
            "int8": np.array([1, 2, 3], dtype=np.int8),
            "int32": np.array([1, 2, 3], dtype=np.int32),
            "float32": np.array([1.1, 2.2, 3.3], dtype=np.float32),
            "float64": np.array([1.1, 2.2, 3.3], dtype=np.float64),
            "bool": np.array([True, False, True]),
            "complex": np.array([1+2j, 3+4j, 5+6j])
        }
        save_numpy(arrays, self.test_file_npz)
        
        loaded = np.load(self.test_file_npz)
        for key, arr in arrays.items():
            np.testing.assert_array_equal(arr, loaded[key])
            assert arr.dtype == loaded[key].dtype

    def test_save_structured_array(self):
        """Test saving structured array"""
        dt = np.dtype([("name", "U10"), ("age", "i4"), ("weight", "f4")])
        arr = np.array([("Alice", 25, 55.0), ("Bob", 30, 75.5)], dtype=dt)
        save_numpy(arr, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_pandas_dataframe(self):
        """Test saving pandas DataFrame as numpy array"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        save_numpy(df.values, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(df.values, loaded)

    def test_save_sparse_array(self):
        """Test saving sparse array (converted to dense)"""
        arr = np.zeros((100, 100))
        arr[10, 20] = 1.0
        arr[50, 60] = 2.0
        save_numpy(arr, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_empty_array(self):
        """Test saving empty array"""
        arr = np.array([])
        save_numpy(arr, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        assert loaded.size == 0

    def test_save_scalar(self):
        """Test saving scalar value"""
        scalar = np.float64(3.14159)
        save_numpy(scalar, self.test_file_npy)
        
        loaded = np.load(self.test_file_npy)
        assert loaded.item() == pytest.approx(3.14159)

    def test_save_with_allow_pickle(self):
        """Test saving object arrays with pickle"""
        arr = np.array([{"a": 1}, {"b": 2}], dtype=object)
        save_numpy(arr, self.test_file_npy, allow_pickle=True)
        
        loaded = np.load(self.test_file_npy, allow_pickle=True)
        assert len(loaded) == 2
        assert loaded[0] == {"a": 1}

    def test_error_invalid_extension(self):
        """Test error for invalid file extension"""
        arr = np.array([1, 2, 3])
        with pytest.raises(ValueError):
            save_numpy(arr, os.path.join(self.temp_dir, "test.txt"))


# EOF
