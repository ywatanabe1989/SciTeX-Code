#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:52:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__hdf5.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__hdf5.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for HDF5 saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False

    from scitex.io._save_modules import save_hdf5, _save_hdf5_group


@pytest.mark.skipif(not HDF5_AVAILABLE, reason="h5py not installed")
class TestSaveHDF5:
    """Test suite for save_hdf5 function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.hdf5")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_arrays(self):
        """Test saving simple arrays"""
        data = {
            "array1": np.array([1, 2, 3, 4, 5]),
            "array2": np.array([[1, 2], [3, 4], [5, 6]])
        }
        save_hdf5(data, self.test_file)
        
        assert os.path.exists(self.test_file)
        with h5py.File(self.test_file, "r") as f:
            assert "array1" in f
            assert "array2" in f
            np.testing.assert_array_equal(f["array1"][:], data["array1"])
            np.testing.assert_array_equal(f["array2"][:], data["array2"])

    def test_save_different_dtypes(self):
        """Test saving arrays with different data types"""
        data = {
            "int8": np.array([1, 2, 3], dtype=np.int8),
            "int32": np.array([1, 2, 3], dtype=np.int32),
            "float32": np.array([1.1, 2.2, 3.3], dtype=np.float32),
            "float64": np.array([1.1, 2.2, 3.3], dtype=np.float64),
            "bool": np.array([True, False, True]),
            "complex": np.array([1+2j, 3+4j], dtype=np.complex128)
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            for key, arr in data.items():
                np.testing.assert_array_equal(f[key][:], arr)
                assert f[key].dtype == arr.dtype

    def test_save_large_arrays(self):
        """Test saving large arrays"""
        data = {
            "large_1d": np.random.randn(1000000),
            "large_2d": np.random.randn(1000, 1000),
            "large_3d": np.random.randn(100, 100, 100)
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            for key, arr in data.items():
                assert f[key].shape == arr.shape
                # Sample check for large arrays
                np.testing.assert_array_almost_equal(f[key][:10], arr[:10])

    def test_save_with_compression(self):
        """Test saving with compression"""
        data = {
            "compressed": np.random.randn(1000, 1000)
        }
        save_hdf5(data, self.test_file, compression="gzip", compression_opts=9)
        
        # Check file exists and data is correct
        with h5py.File(self.test_file, "r") as f:
            np.testing.assert_array_almost_equal(f["compressed"][:], data["compressed"])
            # Check compression is applied
            assert f["compressed"].compression == "gzip"
            assert f["compressed"].compression_opts == 9

    def test_save_with_chunks(self):
        """Test saving with chunked storage"""
        data = {
            "chunked": np.random.randn(1000, 1000)
        }
        save_hdf5(data, self.test_file, chunks=(100, 100))
        
        with h5py.File(self.test_file, "r") as f:
            assert f["chunked"].chunks == (100, 100)
            np.testing.assert_array_almost_equal(f["chunked"][:], data["chunked"])

    def test_save_string_arrays(self):
        """Test saving string arrays"""
        data = {
            "strings": np.array(["hello", "world", "test"], dtype='S10'),
            "unicode": np.array(["hello", "world", "test"])
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            # String comparison might need decoding
            loaded_strings = f["strings"][:]
            if loaded_strings.dtype.kind == 'S':
                loaded_strings = np.char.decode(loaded_strings)
            # Compare as strings
            for i, s in enumerate(["hello", "world", "test"]):
                assert str(loaded_strings[i]).strip() == s

    def test_save_structured_array(self):
        """Test saving structured array"""
        dt = np.dtype([("name", "U10"), ("age", "i4"), ("weight", "f4")])
        data = {
            "structured": np.array(
                [("Alice", 25, 55.0), ("Bob", 30, 75.5)], 
                dtype=dt
            )
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            loaded = f["structured"][:]
            np.testing.assert_array_equal(loaded, data["structured"])

    def test_save_empty_arrays(self):
        """Test saving empty arrays"""
        data = {
            "empty_1d": np.array([]),
            "empty_2d": np.array([]).reshape(0, 5),
            "empty_3d": np.array([]).reshape(0, 0, 0)
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            for key, arr in data.items():
                assert f[key].shape == arr.shape
                assert f[key].size == 0

    def test_save_hdf5_group(self):
        """Test saving data to specific group"""
        data1 = {"array1": np.array([1, 2, 3]), "meta1": "test"}
        data2 = {"array2": np.array([4, 5, 6]), "meta2": "test2"}
        
        _save_hdf5_group(data1, self.test_file, "group1")
        _save_hdf5_group(data2, self.test_file, "group2")
        
        with h5py.File(self.test_file, "r") as f:
            assert "group1" in f
            assert "group2" in f
            np.testing.assert_array_equal(f["group1/array1"][:], data1["array1"])
            np.testing.assert_array_equal(f["group2/array2"][:], data2["array2"])
            assert f["group1"].attrs["meta1"] == "test"
            assert f["group2"].attrs["meta2"] == "test2"

    def test_overwrite_group(self):
        """Test overwriting existing group"""
        data1 = {"array": np.array([1, 2, 3])}
        data2 = {"array": np.array([4, 5, 6])}
        
        _save_hdf5_group(data1, self.test_file, "group1")
        _save_hdf5_group(data2, self.test_file, "group1")  # Overwrite
        
        with h5py.File(self.test_file, "r") as f:
            # Should have new data
            np.testing.assert_array_equal(f["group1/array"][:], data2["array"])

    def test_save_multidimensional_data(self):
        """Test saving various dimensional data"""
        data = {
            "1d": np.arange(10),
            "2d": np.arange(20).reshape(4, 5),
            "3d": np.arange(60).reshape(3, 4, 5),
            "4d": np.arange(120).reshape(2, 3, 4, 5),
            "5d": np.arange(240).reshape(2, 3, 4, 5, 2)
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            for key, arr in data.items():
                np.testing.assert_array_equal(f[key][:], arr)

    def test_save_with_fletcher32(self):
        """Test saving with fletcher32 checksum"""
        data = {"checksummed": np.random.randn(100, 100)}
        save_hdf5(data, self.test_file, fletcher32=True)
        
        with h5py.File(self.test_file, "r") as f:
            assert f["checksummed"].fletcher32

    def test_save_with_shuffle_filter(self):
        """Test saving with shuffle filter for better compression"""
        data = {"shuffled": np.random.randn(100, 100)}
        save_hdf5(data, self.test_file, shuffle=True, compression="gzip")
        
        with h5py.File(self.test_file, "r") as f:
            assert f["shuffled"].shuffle
            assert f["shuffled"].compression == "gzip"

    def test_save_dataset_with_attributes(self):
        """Test that attributes are preserved with _save_hdf5_group"""
        data = {
            "data": np.array([1, 2, 3]),
            "description": "Test dataset",
            "version": 1.0,
            "metadata": {"key": "value"}
        }
        
        _save_hdf5_group(data, self.test_file, "test_group")
        
        with h5py.File(self.test_file, "r") as f:
            np.testing.assert_array_equal(f["test_group/data"][:], data["data"])
            assert f["test_group"].attrs["description"] == "Test dataset"
            assert f["test_group"].attrs["version"] == 1.0

    def test_save_ragged_arrays(self):
        """Test saving ragged arrays as separate datasets"""
        # HDF5 doesn't support ragged arrays directly
        data = {
            "arr1": np.array([1, 2, 3]),
            "arr2": np.array([4, 5]),
            "arr3": np.array([6, 7, 8, 9])
        }
        save_hdf5(data, self.test_file)
        
        with h5py.File(self.test_file, "r") as f:
            assert len(f["arr1"]) == 3
            assert len(f["arr2"]) == 2
            assert len(f["arr3"]) == 4


# EOF
