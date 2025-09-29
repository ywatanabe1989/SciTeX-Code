#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 01:00:00 (Claude)"
# File: /tests/scitex/io/test__load.py

import os
import json
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

import scitex.io


class TestLoad:
    """Test cases for scitex.io.load function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_load_json(self, temp_dir):
        """Test loading JSON files."""
        # Arrange
        test_data = {"name": "test", "value": 42, "array": [1, 2, 3]}
        json_path = os.path.join(temp_dir, "test.json")
        with open(json_path, "w") as f:
            json.dump(test_data, f)

        # Act
        loaded_data = scitex.io.load(json_path)

        # Assert
        assert loaded_data == test_data
        assert isinstance(loaded_data, dict)

    def test_load_yaml(self, temp_dir):
        """Test loading YAML files."""
        # Arrange
        yaml_content = """
name: test
value: 42
array:
  - 1
  - 2
  - 3
"""
        yaml_path = os.path.join(temp_dir, "test.yaml")
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

        # Act
        loaded_data = scitex.io.load(yaml_path)

        # Assert
        assert loaded_data["name"] == "test"
        assert loaded_data["value"] == 42
        assert loaded_data["array"] == [1, 2, 3]

    def test_load_csv(self, temp_dir):
        """Test loading CSV files."""
        # Arrange
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [1.1, 2.2, 3.3]})
        csv_path = os.path.join(temp_dir, "test.csv")
        df.to_csv(csv_path, index=False)

        # Act
        loaded_df = scitex.io.load(csv_path)

        # Assert
        assert isinstance(loaded_df, pd.DataFrame)
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_load_numpy(self, temp_dir):
        """Test loading NumPy array files."""
        # Arrange
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        npy_path = os.path.join(temp_dir, "test.npy")
        np.save(npy_path, arr)

        # Act
        loaded_arr = scitex.io.load(npy_path)

        # Assert
        assert isinstance(loaded_arr, np.ndarray)
        np.testing.assert_array_equal(loaded_arr, arr)

    def test_load_txt(self, temp_dir):
        """Test loading text files."""
        # Arrange
        text_content = "Hello\nWorld\nTest"
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write(text_content)

        # Act
        loaded_text = scitex.io.load(txt_path)

        # Assert - text loader returns list of lines by default
        assert loaded_text == ["Hello", "World", "Test"]

    def test_load_markdown(self, temp_dir):
        """Test loading markdown files."""
        # Arrange
        md_content = "# Header\n\nThis is a **test** markdown file."
        md_path = os.path.join(temp_dir, "test.md")
        with open(md_path, "w") as f:
            f.write(md_content)

        # Act
        loaded_md = scitex.io.load(md_path)

        # Assert
        assert "Header" in loaded_md
        assert "test" in loaded_md

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        # Arrange
        fake_path = "/path/to/nonexistent/file.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            scitex.io.load(fake_path)

    def test_load_with_extension_no_dot(self, temp_dir):
        """Test loading a file without extension."""
        # Arrange
        text_content = "File without extension"
        no_ext_path = os.path.join(temp_dir, "testfile")
        with open(no_ext_path, "w") as f:
            f.write(text_content)

        # Act
        loaded_text = scitex.io.load(no_ext_path)

        # Assert - no extension files are loaded as text (returns list)
        assert loaded_text == ["File without extension"]

    def test_load_pickle(self, temp_dir):
        """Test loading pickle files."""
        # Arrange
        import pickle

        test_obj = {"key": "value", "list": [1, 2, 3], "nested": {"a": 1}}
        pkl_path = os.path.join(temp_dir, "test.pkl")
        with open(pkl_path, "wb") as f:
            pickle.dump(test_obj, f)

        # Act
        loaded_obj = scitex.io.load(pkl_path)

        # Assert
        assert loaded_obj == test_obj

    def test_load_excel(self, temp_dir):
        """Test loading Excel files."""
        # Arrange
        df = pd.DataFrame({"Col1": [1, 2, 3], "Col2": ["x", "y", "z"]})
        excel_path = os.path.join(temp_dir, "test.xlsx")
        df.to_excel(excel_path, index=False)

        # Act
        loaded_df = scitex.io.load(excel_path)

        # Assert
        assert isinstance(loaded_df, pd.DataFrame)
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_load_tsv(self, temp_dir):
        """Test loading TSV files."""
        # Arrange
        df = pd.DataFrame({"A": [10, 20, 30], "B": ["foo", "bar", "baz"]})
        tsv_path = os.path.join(temp_dir, "test.tsv")
        df.to_csv(tsv_path, sep="\t", index=False)

        # Act
        loaded_df = scitex.io.load(tsv_path)

        # Assert
        assert isinstance(loaded_df, pd.DataFrame)
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_load_relative_paths(self, temp_dir):
        """Test that relative paths like ./file.txt work correctly."""
        # Arrange
        text_content = "Relative path test"
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write(text_content)

        # Test with ./relative path from temp_dir  
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            relative_path = "./test.txt"
            
            # Act
            loaded_text = scitex.io.load(relative_path)
            
            # Assert - text files return list of lines
            assert loaded_text == ["Relative path test"]
        finally:
            os.chdir(original_cwd)

    def test_load_symlink(self, temp_dir):
        """Test loading files through symlinks."""
        # Arrange
        text_content = "Symlink test content"
        
        # Create source file in subdirectory
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)
        source_path = os.path.join(source_dir, "original.txt")
        with open(source_path, "w") as f:
            f.write(text_content)
        
        # Create symlink
        symlink_path = os.path.join(temp_dir, "link.txt")
        os.symlink(os.path.relpath(source_path, temp_dir), symlink_path)
        
        # Act
        loaded_text = scitex.io.load(symlink_path)
        
        # Assert - text files return list of lines
        assert loaded_text == ["Symlink test content"]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

