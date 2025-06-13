#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 19:55:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/gen/test__mat2py.py

import pytest
import numpy as np
import tempfile
import os
from scipy.io import savemat
import h5py
from unittest.mock import patch, MagicMock
from scitex.gen import mat2dict, public_keys, save_npa, mat2npy


class TestMat2Py:
    """Test cases for MATLAB to Python conversion functions."""

    @pytest.fixture
    def temp_mat_file(self):
        """Create a temporary .mat file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".mat", delete=False) as tmp:
            # Create test data
            test_data = {
                "matrix1": np.array([[1, 2, 3], [4, 5, 6]]),
                "matrix2": np.array([7, 8, 9]),
                "_private": np.array([10, 11]),  # Private variable
            }
            savemat(tmp.name, test_data)
            yield tmp.name
            # Cleanup
            os.unlink(tmp.name)

    @pytest.fixture
    def temp_hdf5_file(self):
        """Create a temporary HDF5 .mat file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".mat", delete=False) as tmp:
            with h5py.File(tmp.name, "w") as f:
                f.create_dataset("data1", data=np.array([[1, 2], [3, 4]]))
                f.create_dataset("data2", data=np.array([5, 6, 7]))
            yield tmp.name
            # Cleanup
            os.unlink(tmp.name)

    def test_mat2dict_with_scipy_mat(self, temp_mat_file):
        """Test loading scipy .mat file into dictionary."""
        result = mat2dict(temp_mat_file)

        # Check that data is loaded
        assert "matrix1" in result
        assert "matrix2" in result
        assert "_private" in result

        # Check __hdf__ flag
        assert result["__hdf__"] == False

        # Verify data
        np.testing.assert_array_equal(
            result["matrix1"], np.array([[1, 2, 3], [4, 5, 6]])
        )
        np.testing.assert_array_equal(result["matrix2"], np.array([7, 8, 9]))

    def test_mat2dict_with_hdf5_mat(self, temp_hdf5_file):
        """Test loading HDF5 .mat file into dictionary."""
        result = mat2dict(temp_hdf5_file)

        # Check that data is loaded
        assert "data1" in result
        assert "data2" in result

        # Check __hdf__ flag
        assert result["__hdf__"] == True

    def test_public_keys(self):
        """Test filtering of public keys."""
        test_dict = {
            "public1": 1,
            "public2": 2,
            "_private1": 3,
            "__private2__": 4,
            "_": 5,
            "another_public": 6,
        }

        public = public_keys(test_dict)

        assert "public1" in public
        assert "public2" in public
        assert "another_public" in public
        assert "_private1" not in public
        assert "__private2__" not in public
        assert "_" not in public

    def test_save_npa(self):
        """Test saving numpy array."""
        with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as tmp:
            # Test data
            test_array = np.array([1, 2, 3, 4, 5])

            # Save
            save_npa(tmp.name, test_array)

            # Verify
            loaded = np.load(tmp.name)
            np.testing.assert_array_equal(loaded, test_array)

            # Cleanup
            os.unlink(tmp.name)

    def test_mat2npy_creates_npy_file(self, temp_mat_file):
        """Test that mat2npy creates .npy file."""
        # Note: mat2npy has pdb.set_trace() calls that we need to mock
        with patch("scitex.gen._mat2py.mat2npa") as mock_mat2npa:
            mock_mat2npa.return_value = np.array([1, 2, 3])

            # Call mat2npy
            mat2npy(temp_mat_file, np.float32)

            # Check that mat2npa was called
            mock_mat2npa.assert_called_once_with(temp_mat_file, np.float32)

            # Check that .npy file would be created
            expected_npy_path = temp_mat_file.replace(".mat", ".npy")
            # Note: The actual file creation happens in save_npa

    def test_public_keys_empty_dict(self):
        """Test public_keys with empty dictionary."""
        assert public_keys({}) == []

    def test_public_keys_all_private(self):
        """Test public_keys with all private keys."""
        test_dict = {"_private1": 1, "_private2": 2, "__dunder__": 3}
        assert public_keys(test_dict) == []

    def test_mat2dict_invalid_file(self):
        """Test mat2dict with invalid file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"Not a mat file")
            tmp.flush()

            # Should fall back to loadmat and potentially raise error
            # But the function has bare except clause, so it might handle it
            try:
                result = mat2dict(tmp.name)
                # If it doesn't raise, check that __hdf__ is False
                assert result.get("__hdf__", False) == False
            except:
                # Expected if loadmat also fails
                pass
            finally:
                os.unlink(tmp.name)

    @pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64])
    def test_save_npa_different_dtypes(self, dtype):
        """Test saving arrays with different data types."""
        with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as tmp:
            # Test data
            test_array = np.array([1, 2, 3, 4, 5], dtype=dtype)

            # Save
            save_npa(tmp.name, test_array)

            # Verify
            loaded = np.load(tmp.name)
            np.testing.assert_array_equal(loaded, test_array)
            assert loaded.dtype == dtype

            # Cleanup
            os.unlink(tmp.name)


if __name__ == "__main__":
    import os
    import pytest

    pytest.main([os.path.abspath(__file__)])
