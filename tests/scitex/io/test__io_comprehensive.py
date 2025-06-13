#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 11:00:00 (Claude)"
# File: /tests/scitex/io/test__io_comprehensive.py

"""
Comprehensive tests for scitex.io module core functions.
Tests load/save functionality with various file formats.
"""

import os
import sys
import json
import yaml
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import pickle
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex.io


class TestLoadSaveRoundtrip:
    """Test load/save roundtrip for various data types and formats."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    @pytest.fixture
    def sample_data(self):
        """Create various types of sample data for testing."""
        return {
            "dict": {
                "string": "test",
                "integer": 42,
                "float": 3.14,
                "list": [1, 2, 3],
                "nested": {"a": 1, "b": 2},
            },
            "list": [1, 2, 3, 4, 5],
            "numpy_array": np.array([[1, 2, 3], [4, 5, 6]]),
            "pandas_df": pd.DataFrame(
                {"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [1.1, 2.2, 3.3]}
            ),
            "string": "Hello, SciTeX!\nMultiline text.",
            "number": 42.5,
        }

    def test_pickle_roundtrip(self, temp_dir, sample_data):
        """Test save/load roundtrip with pickle format."""
        for name, data in sample_data.items():
            # Arrange
            file_path = os.path.join(temp_dir, f"{name}.pkl")

            # Act
            scitex.io.save(data, file_path)
            loaded = scitex.io.load(file_path)

            # Assert
            if isinstance(data, np.ndarray):
                np.testing.assert_array_equal(loaded, data)
            elif isinstance(data, pd.DataFrame):
                pd.testing.assert_frame_equal(loaded, data)
            else:
                assert loaded == data
            assert os.path.exists(file_path)

    def test_numpy_roundtrip(self, temp_dir):
        """Test save/load roundtrip with numpy format."""
        # Arrange
        data = np.random.randn(10, 5)
        npy_path = os.path.join(temp_dir, "array.npy")
        npz_path = os.path.join(temp_dir, "arrays.npz")

        # Test .npy
        scitex.io.save(data, npy_path)
        loaded_npy = scitex.io.load(npy_path)
        np.testing.assert_array_equal(loaded_npy, data)

        # Test .npz with multiple arrays
        data_dict = {"arr1": data, "arr2": data * 2}
        scitex.io.save(data_dict, npz_path)
        loaded_npz = scitex.io.load(npz_path)

        assert set(loaded_npz.keys()) == set(data_dict.keys())
        for key in data_dict:
            np.testing.assert_array_equal(loaded_npz[key], data_dict[key])

    def test_json_roundtrip(self, temp_dir):
        """Test save/load roundtrip with JSON format."""
        # Arrange
        data = {
            "name": "test",
            "values": [1, 2, 3, 4.5],
            "nested": {"a": 1, "b": "two"},
        }
        json_path = os.path.join(temp_dir, "data.json")

        # Act
        scitex.io.save(data, json_path)
        loaded = scitex.io.load(json_path)

        # Assert
        assert loaded == data

        # Verify it's valid JSON
        with open(json_path, "r") as f:
            json.load(f)  # Should not raise

    def test_yaml_roundtrip(self, temp_dir):
        """Test save/load roundtrip with YAML format."""
        # Arrange
        data = {
            "config": {"learning_rate": 0.001, "batch_size": 32, "epochs": 100},
            "paths": ["./data", "./models", "./results"],
        }
        yaml_path = os.path.join(temp_dir, "config.yaml")

        # Act
        scitex.io.save(data, yaml_path)
        loaded = scitex.io.load(yaml_path)

        # Assert
        assert loaded == data

    def test_csv_roundtrip(self, temp_dir):
        """Test save/load roundtrip with CSV format."""
        # Arrange
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "name": ["Alice", "Bob", "Charlie", "David"],
                "score": [95.5, 87.3, 92.1, 88.9],
            }
        )
        csv_path = os.path.join(temp_dir, "data.csv")

        # Act
        scitex.io.save(df, csv_path)
        loaded = scitex.io.load(csv_path)

        # Assert
        pd.testing.assert_frame_equal(loaded, df)

    def test_text_roundtrip(self, temp_dir):
        """Test save/load roundtrip with text files."""
        # Arrange
        text = "Line 1\nLine 2\nLine 3\n"
        txt_path = os.path.join(temp_dir, "text.txt")

        # Act
        scitex.io.save(text, txt_path)
        loaded = scitex.io.load(txt_path)

        # Assert
        assert loaded == text

    def test_excel_roundtrip(self, temp_dir):
        """Test save/load roundtrip with Excel format."""
        # Arrange
        df = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=5),
                "Value": [10, 20, 30, 40, 50],
                "Category": ["A", "B", "A", "B", "A"],
            }
        )
        excel_path = os.path.join(temp_dir, "data.xlsx")

        # Act
        scitex.io.save(df, excel_path)
        loaded = scitex.io.load(excel_path)

        # Assert
        pd.testing.assert_frame_equal(loaded, df)

    def test_hdf5_roundtrip(self, temp_dir):
        """Test save/load roundtrip with HDF5 format."""
        # Arrange
        data = {
            "array": np.random.randn(100, 50),
            "metadata": {"experiment": "test", "version": 1},
        }
        h5_path = os.path.join(temp_dir, "data.h5")

        # Act
        scitex.io.save(data, h5_path)
        loaded = scitex.io.load(h5_path)

        # Assert
        np.testing.assert_array_equal(loaded["array"], data["array"])
        assert loaded["metadata"] == data["metadata"]


class TestLoadFunctionality:
    """Test specific load functionality and edge cases."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises((FileNotFoundError, IOError)):
            scitex.io.load("nonexistent_file.pkl")

    def test_load_with_glob_pattern(self, temp_dir):
        """Test loading files with glob pattern."""
        # Create multiple files
        for i in range(3):
            data = {"index": i, "value": i * 10}
            scitex.io.save(data, os.path.join(temp_dir, f"data_{i}.json"))

        # Load with pattern
        pattern = os.path.join(temp_dir, "data_*.json")
        loaded = scitex.io.load(pattern)

        # Should return a list of loaded data
        assert isinstance(loaded, list)
        assert len(loaded) == 3
        assert all(isinstance(item, dict) for item in loaded)

    def test_load_compressed_files(self, temp_dir):
        """Test loading compressed files."""
        # Test gzip compressed pickle
        import gzip

        data = {"test": "data", "values": [1, 2, 3]}
        pkl_gz_path = os.path.join(temp_dir, "data.pkl.gz")

        with gzip.open(pkl_gz_path, "wb") as f:
            pickle.dump(data, f)

        loaded = scitex.io.load(pkl_gz_path)
        assert loaded == data

    def test_load_with_encoding(self, temp_dir):
        """Test loading text files with different encodings."""
        # Create file with specific encoding
        text = "Testing encoding: αβγδε"
        txt_path = os.path.join(temp_dir, "utf8_text.txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Load should handle encoding properly
        loaded = scitex.io.load(txt_path)
        assert loaded == text


class TestSaveFunctionality:
    """Test specific save functionality and edge cases."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_save_creates_directories(self, temp_dir):
        """Test that save creates parent directories if they don't exist."""
        # Arrange
        data = {"test": "data"}
        nested_path = os.path.join(temp_dir, "nested", "dirs", "data.pkl")

        # Act
        scitex.io.save(data, nested_path)

        # Assert
        assert os.path.exists(nested_path)
        loaded = scitex.io.load(nested_path)
        assert loaded == data

    def test_save_overwrites_existing(self, temp_dir):
        """Test that save overwrites existing files."""
        # Arrange
        file_path = os.path.join(temp_dir, "data.json")
        data1 = {"version": 1}
        data2 = {"version": 2}

        # Act
        scitex.io.save(data1, file_path)
        scitex.io.save(data2, file_path)  # Overwrite

        # Assert
        loaded = scitex.io.load(file_path)
        assert loaded == data2
        assert loaded["version"] == 2

    def test_save_with_compression(self, temp_dir):
        """Test saving with compression."""
        # Large data that benefits from compression
        data = np.random.randn(1000, 100)

        # Save compressed
        npz_path = os.path.join(temp_dir, "compressed.npz")
        scitex.io.save(data, npz_path)

        # Verify it's compressed by checking file size
        uncompressed_size = data.nbytes
        compressed_size = os.path.getsize(npz_path)
        assert compressed_size < uncompressed_size

        # Verify data integrity
        loaded = scitex.io.load(npz_path)
        np.testing.assert_array_equal(loaded, data)

    def test_save_complex_pandas_dataframe(self, temp_dir):
        """Test saving complex pandas DataFrames."""
        # Create DataFrame with various dtypes
        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "str_col": ["a", "b", "c"],
                "datetime_col": pd.date_range("2023-01-01", periods=3),
                "category_col": pd.Categorical(["cat1", "cat2", "cat1"]),
            }
        )

        # Test different formats
        for ext in [".pkl", ".csv", ".xlsx"]:
            file_path = os.path.join(temp_dir, f"complex_df{ext}")
            scitex.io.save(df, file_path)
            loaded = scitex.io.load(file_path)

            # CSV and Excel might lose some type information
            if ext in [".csv", ".xlsx"]:
                # Just check shape and general content
                assert loaded.shape == df.shape
                # For Excel, check that categorical values are preserved (even if dtype changes)
                if ext == ".xlsx":
                    assert (
                        loaded["category_col"].tolist() == df["category_col"].tolist()
                    )
            else:
                pd.testing.assert_frame_equal(loaded, df)


class TestSpecialCases:
    """Test special cases and edge conditions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_empty_data_handling(self, temp_dir):
        """Test handling of empty data structures."""
        test_cases = {
            "empty_dict.json": {},
            "empty_list.json": [],
            "empty_string.txt": "",
            "empty_array.npy": np.array([]),
            "empty_df.pkl": pd.DataFrame(),
        }

        for filename, data in test_cases.items():
            file_path = os.path.join(temp_dir, filename)

            # Save and load
            scitex.io.save(data, file_path)
            loaded = scitex.io.load(file_path)

            # Verify
            if isinstance(data, np.ndarray):
                np.testing.assert_array_equal(loaded, data)
            elif isinstance(data, pd.DataFrame):
                pd.testing.assert_frame_equal(loaded, data)
            else:
                assert loaded == data

    def test_large_data_handling(self, temp_dir):
        """Test handling of large data (memory efficiency)."""
        # Create large array (100MB)
        large_array = np.random.randn(2500, 5000)  # ~100MB
        file_path = os.path.join(temp_dir, "large_data.npy")

        # Save and load
        scitex.io.save(large_array, file_path)
        loaded = scitex.io.load(file_path)

        # Verify
        np.testing.assert_array_equal(loaded, large_array)

    def test_special_characters_in_path(self, temp_dir):
        """Test handling paths with special characters."""
        # Create path with spaces and special chars
        special_dir = os.path.join(temp_dir, "my data & results (2023)")
        os.makedirs(special_dir, exist_ok=True)

        data = {"test": "special path"}
        file_path = os.path.join(special_dir, "file with spaces.json")

        # Save and load
        scitex.io.save(data, file_path)
        # Note: scitex.io.save cleans paths by replacing spaces with underscores
        # So we need to load from the cleaned path
        cleaned_path = file_path.replace(" ", "_")
        loaded = scitex.io.load(cleaned_path)

        assert loaded == data

    def test_format_inference(self, temp_dir):
        """Test automatic format inference from extension."""
        data = {"test": "format inference"}

        # Test various extensions
        extensions = {".json": json, ".yaml": yaml, ".pkl": pickle, ".pickle": pickle}

        for ext, module in extensions.items():
            file_path = os.path.join(temp_dir, f"test{ext}")
            scitex.io.save(data, file_path)

            # Verify file can be loaded with native module
            with open(file_path, "rb" if ext in [".pkl", ".pickle"] else "r") as f:
                if ext in [".pkl", ".pickle"]:
                    native_load = module.load(f)
                elif ext == ".yaml":
                    native_load = module.load(f, Loader=yaml.SafeLoader)
                else:
                    native_load = module.load(f)

            # Verify scitex.io.load gives same result
            scitex_load = scitex.io.load(file_path)
            assert scitex_load == native_load


class TestGlobFunctionality:
    """Test scitex.io.glob functionality."""

    @pytest.fixture
    def temp_dir_with_files(self):
        """Create temp directory with various files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            for i in range(3):
                subdir = os.path.join(tmpdir, f"exp_{i}")
                os.makedirs(subdir)

                # Create various files
                scitex.io.save(
                    {"exp": i, "type": "config"}, os.path.join(subdir, "config.json")
                )
                scitex.io.save(np.random.randn(10, 5), os.path.join(subdir, "data.npy"))
                scitex.io.save(
                    f"Results for experiment {i}", os.path.join(subdir, "results.txt")
                )

            yield tmpdir

    def test_glob_pattern_matching(self, temp_dir_with_files):
        """Test glob pattern matching."""
        # Find all JSON files
        json_files = scitex.io.glob(os.path.join(temp_dir_with_files, "**/config.json"))
        assert len(json_files) == 3
        assert all(f.endswith("config.json") for f in json_files)

        # Find all numpy files
        npy_files = scitex.io.glob(os.path.join(temp_dir_with_files, "**/*.npy"))
        assert len(npy_files) == 3

        # Find files in specific subdirectory
        exp0_files = scitex.io.glob(os.path.join(temp_dir_with_files, "exp_0/*"))
        assert len(exp0_files) == 3

    def test_glob_with_load(self, temp_dir_with_files):
        """Test using glob results with load."""
        # Load all config files
        config_pattern = os.path.join(temp_dir_with_files, "**/config.json")
        config_files = scitex.io.glob(config_pattern)

        configs = [scitex.io.load(f) for f in config_files]
        assert len(configs) == 3
        assert all(isinstance(c, dict) for c in configs)
        assert all("exp" in c and "type" in c for c in configs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
