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

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_hdf5.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-07-14 05:28:34 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save_modules/_hdf5.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/io/_save_modules/_hdf5.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import fcntl
# import pickle
# import shutil
# import tempfile
# import time
# 
# import h5py
# import numpy as np
# 
# 
# class SWMRFile:
#     """Context manager for SWMR-enabled HDF5 files."""
# 
#     def __init__(self, filepath, mode="r", swmr=True, timeout=300):
#         self.filepath = filepath
#         self.mode = mode
#         self.swmr = swmr
#         self.timeout = timeout
#         self.file = None
#         self.temp_file = None
# 
#     def __enter__(self):
#         start_time = time.time()
# 
#         while time.time() - start_time < self.timeout:
#             try:
#                 if self.mode in ["w", "w-"]:
#                     # For write mode, create new file
#                     self.file = h5py.File(
#                         self.filepath, self.mode, libver="latest"
#                     )
#                     if self.swmr:
#                         self.file.swmr_mode = True
#                     return self.file
# 
#                 elif self.mode == "a":
#                     # For append mode, handle SWMR carefully
#                     if os.path.exists(self.filepath):
#                         # Try to open in read mode first to check SWMR status
#                         try:
#                             with h5py.File(self.filepath, "r") as test_file:
#                                 is_swmr = test_file.swmr_mode
#                         except:
#                             is_swmr = False
# 
#                         if is_swmr:
#                             # File is in SWMR mode, we need to copy and modify
#                             self.temp_file = tempfile.NamedTemporaryFile(
#                                 delete=False, suffix=".h5"
#                             )
#                             shutil.copy2(self.filepath, self.temp_file.name)
#                             self.file = h5py.File(
#                                 self.temp_file.name, "r+", libver="latest"
#                             )
#                         else:
#                             # Normal append mode
#                             self.file = h5py.File(
#                                 self.filepath, "r+", libver="latest"
#                             )
#                             if self.swmr:
#                                 self.file.swmr_mode = True
#                     else:
#                         # Create new file
#                         self.file = h5py.File(
#                             self.filepath, "w", libver="latest"
#                         )
#                         if self.swmr:
#                             self.file.swmr_mode = True
#                     return self.file
# 
#                 elif self.mode == "r":
#                     # Read mode with SWMR
#                     self.file = h5py.File(
#                         self.filepath, "r", libver="latest", swmr=True
#                     )
#                     return self.file
# 
#             except (OSError, IOError) as e:
#                 if "Resource temporarily unavailable" in str(e):
#                     time.sleep(
#                         0.1 * (2 ** min(5, (time.time() - start_time) / 10))
#                     )
#                 else:
#                     raise
# 
#         raise TimeoutError(
#             f"Could not open {self.filepath} within {self.timeout} seconds"
#         )
# 
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.file:
#             self.file.close()
# 
#         # If we used a temp file, move it back
#         if self.temp_file and exc_type is None:
#             shutil.move(self.temp_file.name, self.filepath)
#         elif self.temp_file:
#             os.unlink(self.temp_file.name)
# 
# 
# def _save_hdf5(
#     obj,
#     spath,
#     key=None,
#     override=False,
#     swmr=True,
#     compression="gzip",
#     compression_opts=4,
#     max_retries=10,
#     **kwargs,
# ):
#     """
#     HDF5 save function with SWMR support for HPC environments.
# 
#     Parameters:
#     -----------
#     obj : dict or any
#         Object to save
#     spath : str
#         Path to HDF5 file
#     key : str, optional
#         Key/group path within HDF5 file
#     override : bool
#         Whether to override existing keys
#     swmr : bool
#         Enable SWMR mode (default: True)
#     compression : str
#         Compression algorithm (default: 'gzip')
#     compression_opts : int
#         Compression level (default: 4)
#     max_retries : int
#         Maximum number of retry attempts
#     """
#     if not isinstance(obj, dict):
#         obj = {"data": obj}
# 
#     # Ensure directory exists
#     os.makedirs(os.path.dirname(spath) or ".", exist_ok=True)
# 
#     # Lock file for coordination
#     lock_file = f"{spath}.lock"
# 
#     for attempt in range(max_retries):
#         try:
#             # Use file locking for write coordination
#             with open(lock_file, "w") as lock_fd:
#                 fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
# 
#                 try:
#                     mode = "a" if os.path.exists(spath) else "w"
# 
#                     with SWMRFile(spath, mode, swmr=swmr) as h5_file:
#                         if key:
#                             # Check if key exists
#                             if key in h5_file and not override:
#                                 return
# 
#                             if key in h5_file and override:
#                                 del h5_file[key]
# 
#                             # Create group structure
#                             parts = [p for p in key.split("/") if p]
#                             current_group = h5_file
# 
#                             for part in parts[:-1]:
#                                 if part:
#                                     current_group = (
#                                         current_group.require_group(part)
#                                     )
# 
#                             final_key = parts[-1] if parts else ""
#                             if final_key:
#                                 target_group = current_group.create_group(
#                                     final_key
#                                 )
#                             else:
#                                 target_group = current_group
#                         else:
#                             target_group = h5_file
# 
#                         # Save datasets with chunking for large arrays
#                         for dataset_name, data in obj.items():
#                             _save_dataset(
#                                 target_group,
#                                 dataset_name,
#                                 data,
#                                 compression,
#                                 compression_opts,
#                                 **kwargs,
#                             )
# 
#                         # Flush to ensure data is written
#                         h5_file.flush()
# 
#                 finally:
#                     fcntl.flock(lock_fd, fcntl.LOCK_UN)
# 
#                 return  # Success
# 
#         except (OSError, IOError) as e:
#             if attempt < max_retries - 1:
#                 time.sleep(0.1 * (2**attempt))
#             else:
#                 raise
# 
#     raise RuntimeError(
#         f"Failed to save to {spath} after {max_retries} attempts"
#     )
# 
# 
# def _save_dataset(group, name, data, compression, compression_opts, **kwargs):
#     """Save a single dataset with appropriate settings."""
#     try:
#         if isinstance(data, str):
#             group.create_dataset(name, data=data, dtype=h5py.string_dtype())
# 
#         elif hasattr(data, "__array__"):
#             # NumPy arrays and array-like objects
#             data_array = np.asarray(data)
# 
#             # Determine chunk size for large arrays
#             chunks = None
#             if data_array.size > 1000:
#                 chunks = True  # Let h5py auto-determine chunks
# 
#             # Check if we should use compression
#             use_compression = compression if data_array.size > 100 else None
# 
#             group.create_dataset(
#                 name,
#                 data=data_array,
#                 compression=use_compression,
#                 compression_opts=compression_opts if use_compression else None,
#                 chunks=chunks,
#                 **kwargs,
#             )
# 
#         elif isinstance(data, (list, tuple)) and len(data) > 0:
#             # Try to convert to array
#             try:
#                 data_array = np.asarray(data)
#                 if data_array.dtype != np.object_:
#                     group.create_dataset(name, data=data_array)
#                 else:
#                     # Pickle complex objects
#                     pickled_data = pickle.dumps(data)
#                     group.create_dataset(name, data=np.void(pickled_data))
#             except:
#                 # Pickle if conversion fails
#                 pickled_data = pickle.dumps(data)
#                 group.create_dataset(name, data=np.void(pickled_data))
# 
#         else:
#             # For all other types, try direct save or pickle
#             try:
#                 group.create_dataset(name, data=data)
#             except:
#                 pickled_data = pickle.dumps(data)
#                 group.create_dataset(name, data=np.void(pickled_data))
# 
#     except Exception as e:
#         print(f"Warning: Could not save dataset '{name}': {e}")
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_hdf5.py
# --------------------------------------------------------------------------------
