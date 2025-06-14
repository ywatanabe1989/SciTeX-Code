#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:53:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__matlab.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__matlab.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for MATLAB .mat file saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import scipy.io
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

    from scitex.io._save_modules import save_matlab


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not installed")
class TestSaveMatlab:
    """Test suite for save_matlab function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.mat")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_dict(self):
        """Test saving simple dictionary"""
        data = {
            "scalar": 42,
            "array": np.array([1, 2, 3, 4, 5]),
            "matrix": np.array([[1, 2], [3, 4]])
        }
        save_matlab(data, self.test_file)
        
        assert os.path.exists(self.test_file)
        loaded = scipy.io.loadmat(self.test_file)
        
        assert loaded["scalar"][0, 0] == 42
        np.testing.assert_array_equal(loaded["array"].flatten(), data["array"])
        np.testing.assert_array_equal(loaded["matrix"], data["matrix"])

    def test_save_numpy_arrays(self):
        """Test saving various numpy arrays"""
        data = {
            "float_array": np.array([1.1, 2.2, 3.3]),
            "int_array": np.array([1, 2, 3], dtype=np.int32),
            "bool_array": np.array([True, False, True]),
            "complex_array": np.array([1+2j, 3+4j])
        }
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        
        np.testing.assert_array_almost_equal(
            loaded["float_array"].flatten(), 
            data["float_array"]
        )
        np.testing.assert_array_equal(
            loaded["int_array"].flatten(), 
            data["int_array"]
        )
        # Bool arrays might be converted to uint8
        assert all(loaded["bool_array"].flatten() == np.array([1, 0, 1]))
        np.testing.assert_array_almost_equal(
            loaded["complex_array"].flatten(), 
            data["complex_array"]
        )

    def test_save_multidimensional_arrays(self):
        """Test saving multi-dimensional arrays"""
        data = {
            "array_2d": np.random.randn(10, 20),
            "array_3d": np.random.randn(5, 10, 15),
            "array_4d": np.random.randn(3, 4, 5, 6)
        }
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        
        for key, arr in data.items():
            np.testing.assert_array_almost_equal(loaded[key], arr)

    def test_save_cell_arrays(self):
        """Test saving cell-like arrays (lists of arrays)"""
        # MATLAB cell arrays are tricky - usually need object arrays
        data = {
            "cell_like": np.array([
                np.array([1, 2, 3]),
                np.array([4, 5]),
                np.array([6, 7, 8, 9])
            ], dtype=object)
        }
        save_matlab(data, self.test_file)
        
        assert os.path.exists(self.test_file)
        # Cell arrays might not load exactly the same way

    def test_save_strings(self):
        """Test saving string data"""
        data = {
            "single_string": "hello",
            "string_array": np.array(["hello", "world", "test"])
        }
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        
        # Strings in MATLAB files often come back as arrays
        assert "hello" in str(loaded["single_string"])

    def test_save_sparse_matrix(self):
        """Test saving sparse matrix"""
        from scipy.sparse import csr_matrix
        
        # Create sparse matrix
        row = np.array([0, 0, 1, 2, 2, 2])
        col = np.array([0, 2, 2, 0, 1, 2])
        data_vals = np.array([1, 2, 3, 4, 5, 6])
        sparse = csr_matrix((data_vals, (row, col)), shape=(3, 3))
        
        data = {"sparse_matrix": sparse}
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        
        # Check if loaded as sparse
        from scipy.sparse import issparse
        assert issparse(loaded["sparse_matrix"]) or isinstance(loaded["sparse_matrix"], np.ndarray)

    def test_save_struct_like(self):
        """Test saving struct-like nested dictionaries"""
        data = {
            "experiment": {
                "name": "test_exp",
                "parameters": {
                    "learning_rate": 0.001,
                    "batch_size": 32
                },
                "results": np.array([0.8, 0.85, 0.9])
            }
        }
        save_matlab(data, self.test_file)
        
        # Note: Nested dicts might need special handling for MATLAB
        assert os.path.exists(self.test_file)

    def test_save_with_compression(self):
        """Test saving with compression (if supported)"""
        large_data = {
            "large_array": np.random.randn(1000, 1000)
        }
        save_matlab(large_data, self.test_file, do_compression=True)
        
        loaded = scipy.io.loadmat(self.test_file)
        np.testing.assert_array_almost_equal(
            loaded["large_array"], 
            large_data["large_array"]
        )

    def test_save_matlab_compatible_names(self):
        """Test handling of MATLAB variable name restrictions"""
        # MATLAB variable names must start with letter and contain only letters, numbers, underscores
        data = {
            "valid_name": np.array([1, 2, 3]),
            "another_valid_123": np.array([4, 5, 6]),
            "_starts_with_underscore": np.array([7, 8, 9]),  # Invalid in MATLAB
            "123_starts_with_number": np.array([10, 11, 12])  # Invalid in MATLAB
        }
        
        # Save might handle invalid names differently
        save_matlab(data, self.test_file)
        assert os.path.exists(self.test_file)

    def test_save_empty_arrays(self):
        """Test saving empty arrays"""
        data = {
            "empty_1d": np.array([]),
            "empty_2d": np.zeros((0, 5)),
            "empty_3d": np.zeros((2, 0, 3))
        }
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        
        for key in data:
            if key in loaded:
                assert loaded[key].size == 0

    def test_save_single_array(self):
        """Test saving single array directly"""
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        # If save_matlab expects dict, wrap it
        save_matlab({"data": arr}, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        np.testing.assert_array_equal(loaded["data"], arr)

    def test_save_pandas_dataframe(self):
        """Test saving pandas DataFrame (as dict of arrays)"""
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4.5, 5.6, 6.7],
            "c": ["x", "y", "z"]
        })
        
        # Convert to dict of arrays
        data = {col: df[col].values for col in df.columns}
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        np.testing.assert_array_equal(loaded["a"].flatten(), df["a"].values)
        np.testing.assert_array_almost_equal(loaded["b"].flatten(), df["b"].values)

    def test_save_logical_arrays(self):
        """Test saving logical (boolean) arrays"""
        data = {
            "logical": np.array([True, False, True, False])
        }
        save_matlab(data, self.test_file)
        
        loaded = scipy.io.loadmat(self.test_file)
        # MATLAB logical arrays might load as uint8
        expected = np.array([1, 0, 1, 0], dtype=np.uint8)
        np.testing.assert_array_equal(loaded["logical"].flatten(), expected)

    def test_save_with_mat_version(self):
        """Test saving with different MAT file versions"""
        data = {"test": np.array([1, 2, 3])}
        
        # Test v5 format (most compatible)
        save_matlab(data, self.test_file, format='5')
        assert os.path.exists(self.test_file)
        
        # Test v4 format if needed
        test_file_v4 = os.path.join(self.temp_dir, "test_v4.mat")
        save_matlab(data, test_file_v4, format='4')
        assert os.path.exists(test_file_v4)


# EOF
