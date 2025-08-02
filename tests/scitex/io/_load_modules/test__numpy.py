#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:26:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__numpy.py

"""Tests for NumPy file loading functionality.

This module tests the _load_npy function and its helpers from scitex.io._load_modules._numpy,
which handle loading NPY and NPZ files with proper handling of single vs multiple arrays.
"""

import os
import tempfile
import pytest
import numpy as np


def test_load_npy_basic():
    """Test loading a basic NPY file."""
    from scitex.io._load_modules import _load_npy
    
    # Create test data
    test_array = np.array([1, 2, 3, 4, 5])
    
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
        np.save(f.name, test_array)
        temp_path = f.name
    
    try:
        loaded_array = _load_npy(temp_path)
        np.testing.assert_array_equal(loaded_array, test_array)
    finally:
        os.unlink(temp_path)


def test_load_npy_multidimensional():
    """Test loading multidimensional arrays."""
    from scitex.io._load_modules import _load_npy
    
    # Test 2D array
    test_array_2d = np.random.rand(10, 20)
    
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
        np.save(f.name, test_array_2d)
        temp_path = f.name
    
    try:
        loaded_array = _load_npy(temp_path)
        np.testing.assert_array_almost_equal(loaded_array, test_array_2d)
        assert loaded_array.shape == (10, 20)
    finally:
        os.unlink(temp_path)
    
    # Test 3D array
    test_array_3d = np.random.rand(5, 10, 15)
    
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
        np.save(f.name, test_array_3d)
        temp_path = f.name
    
    try:
        loaded_array = _load_npy(temp_path)
        np.testing.assert_array_almost_equal(loaded_array, test_array_3d)
        assert loaded_array.shape == (5, 10, 15)
    finally:
        os.unlink(temp_path)


def test_load_npz_single_array():
    """Test loading NPZ file with single array (backward compatibility)."""
    from scitex.io._load_modules import _load_npy
    
    test_array = np.array([[1, 2, 3], [4, 5, 6]])
    
    with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
        np.savez(f.name, test_array)  # Saves as 'arr_0'
        temp_path = f.name
    
    try:
        # Should return the array directly, not the NpzFile object
        loaded_array = _load_npy(temp_path)
        np.testing.assert_array_equal(loaded_array, test_array)
        assert isinstance(loaded_array, np.ndarray)
    finally:
        os.unlink(temp_path)


def test_load_npz_multiple_arrays():
    """Test loading NPZ file with multiple arrays."""
    from scitex.io._load_modules import _load_npy
    
    array1 = np.array([1, 2, 3])
    array2 = np.array([[4, 5], [6, 7]])
    array3 = np.random.rand(3, 4, 5)
    
    with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
        np.savez(f.name, first=array1, second=array2, third=array3)
        temp_path = f.name
    
    try:
        loaded_data = _load_npy(temp_path)
        
        # Should return NpzFile object when multiple arrays
        assert hasattr(loaded_data, 'files')
        assert set(loaded_data.files) == {'first', 'second', 'third'}
        
        # Verify individual arrays
        np.testing.assert_array_equal(loaded_data['first'], array1)
        np.testing.assert_array_equal(loaded_data['second'], array2)
        np.testing.assert_array_almost_equal(loaded_data['third'], array3)
    finally:
        os.unlink(temp_path)


def test_load_npy_with_objects():
    """Test loading NPY file with Python objects (using pickle)."""
    from scitex.io._load_modules import _load_npy
    
    # Create array with Python objects
    test_data = np.array([{'key': 'value'}, [1, 2, 3], 'string'], dtype=object)
    
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
        np.save(f.name, test_data)
        temp_path = f.name
    
    try:
        loaded_data = _load_npy(temp_path)
        assert loaded_data[0] == {'key': 'value'}
        assert loaded_data[1] == [1, 2, 3]
        assert loaded_data[2] == 'string'
    finally:
        os.unlink(temp_path)


def test_load_npy_invalid_extension():
    """Test that loading non-numpy file raises ValueError."""
    from scitex.io._load_modules import _load_npy
    
    with pytest.raises(ValueError, match="File must have .npy or .npz extension"):
        _load_npy("test.txt")
    
    with pytest.raises(ValueError, match="File must have .npy or .npz extension"):
        _load_npy("/path/to/file.mat")


def test_load_npy_nonexistent_file():
    """Test loading a nonexistent file."""
    from scitex.io._load_modules import _load_npy
    
    with pytest.raises(FileNotFoundError):
        _load_npy("/nonexistent/path/file.npy")


def test_load_npy_structured_array():
    """Test loading structured arrays."""
    from scitex.io._load_modules import _load_npy
    
    # Create structured array
    dt = np.dtype([('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])
    structured_array = np.array([
        ('Alice', 25, 55.5),
        ('Bob', 30, 70.2),
        ('Charlie', 35, 80.1)
    ], dtype=dt)
    
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
        np.save(f.name, structured_array)
        temp_path = f.name
    
    try:
        loaded_array = _load_npy(temp_path)
        np.testing.assert_array_equal(loaded_array, structured_array)
        assert loaded_array.dtype == dt
    finally:
        os.unlink(temp_path)


def test_load_npz_compressed():
    """Test loading compressed NPZ files."""
    from scitex.io._load_modules import _load_npy
    
    # Create large array for compression benefit
    large_array = np.random.rand(1000, 1000)
    
    with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
        np.savez_compressed(f.name, data=large_array)
        temp_path = f.name
    
    try:
        loaded_data = _load_npy(temp_path)
        np.testing.assert_array_almost_equal(loaded_data['data'], large_array)
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_numpy.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:55:44 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_modules/_numpy.py
# 
# from typing import Any
# 
# import numpy as np
# 
# 
# def _load_npy(lpath: str, **kwargs) -> Any:
#     """Load NPY or NPZ file."""
#     if lpath.endswith(".npy"):
#         return __load_npy(lpath, **kwargs)
#     elif lpath.endswith(".npz"):
#         return __load_npz(lpath, **kwargs)
#     raise ValueError("File must have .npy or .npz extension")
# 
# 
# def __load_npy(lpath: str, **kwargs) -> Any:
#     """Load NPY file."""
#     return np.load(lpath, allow_pickle=True, **kwargs)
# 
# 
# def __load_npz(lpath: str, **kwargs) -> Any:
#     """Load NPZ file."""
#     obj = np.load(lpath, allow_pickle=True)
# 
#     # Check if it's a single array saved with default key
#     if len(obj.files) == 1 and obj.files[0] == "arr_0":
#         # Return the single array directly for backward compatibility
#         return obj["arr_0"]
# 
#     # Return the NpzFile object so users can access arrays by key
#     # This preserves the dictionary-like interface
#     return obj
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_numpy.py
# --------------------------------------------------------------------------------
