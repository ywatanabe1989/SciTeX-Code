#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:59:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__save_listed_dfs_as_csv.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__save_listed_dfs_as_csv.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for saving listed DataFrames as CSV functionality
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from scitex.io._save_modules import save_listed_dfs_as_csv


class TestSaveListedDfsAsCSV:
    """Test suite for save_listed_dfs_as_csv function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_dfs.csv")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_dataframes(self):
        """Test saving list of simple DataFrames"""
        df1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df2 = pd.DataFrame({"A": [7, 8, 9], "B": [10, 11, 12]})
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        assert os.path.exists(self.test_file)
        
        # Load and verify
        loaded = pd.read_csv(self.test_file)
        expected = pd.concat([df1, df2], ignore_index=True)
        pd.testing.assert_frame_equal(loaded, expected)

    def test_save_with_labels(self):
        """Test saving DataFrames with labels"""
        df1 = pd.DataFrame({"value": [1, 2, 3]})
        df2 = pd.DataFrame({"value": [4, 5, 6]})
        df3 = pd.DataFrame({"value": [7, 8, 9]})
        
        listed_dfs = [df1, df2, df3]
        labels = ["Group A", "Group B", "Group C"]
        
        save_listed_dfs_as_csv(listed_dfs, self.test_file, labels=labels)
        
        loaded = pd.read_csv(self.test_file)
        
        # Check that label column was added
        assert "label" in loaded.columns
        assert list(loaded["label"]) == ["Group A"]*3 + ["Group B"]*3 + ["Group C"]*3

    def test_save_empty_dataframes(self):
        """Test handling empty DataFrames"""
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame(columns=["A", "B"])  # Empty with columns
        df3 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})
        
        listed_dfs = [df1, df2, df3]
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        assert len(loaded) == 4  # df1 (2 rows) + df2 (0 rows) + df3 (2 rows)

    def test_save_different_columns(self):
        """Test saving DataFrames with different columns"""
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"B": [5, 6], "C": [7, 8]})
        df3 = pd.DataFrame({"A": [9, 10], "C": [11, 12]})
        
        listed_dfs = [df1, df2, df3]
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        
        # Should have all columns A, B, C with NaN where missing
        assert set(loaded.columns) == {"A", "B", "C"}
        assert pd.isna(loaded.iloc[2]["A"])  # df2 doesn't have column A

    def test_save_with_index(self):
        """Test saving DataFrames with meaningful index"""
        df1 = pd.DataFrame({"value": [1, 2, 3]}, index=["a", "b", "c"])
        df2 = pd.DataFrame({"value": [4, 5, 6]}, index=["d", "e", "f"])
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file, index=True)
        
        loaded = pd.read_csv(self.test_file, index_col=0)
        assert list(loaded.index) == ["a", "b", "c", "d", "e", "f"]

    def test_save_mixed_types(self):
        """Test saving DataFrames with mixed data types"""
        df1 = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True]
        })
        df2 = pd.DataFrame({
            "int_col": [4, 5, 6],
            "float_col": [4.4, 5.5, 6.6],
            "str_col": ["d", "e", "f"],
            "bool_col": [False, True, False]
        })
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        assert loaded["int_col"].dtype == np.int64
        assert loaded["float_col"].dtype == np.float64
        assert loaded["str_col"].dtype == object

    def test_save_with_datetime(self):
        """Test saving DataFrames with datetime columns"""
        dates1 = pd.date_range("2023-01-01", periods=3)
        dates2 = pd.date_range("2023-01-04", periods=3)
        
        df1 = pd.DataFrame({"date": dates1, "value": [1, 2, 3]})
        df2 = pd.DataFrame({"date": dates2, "value": [4, 5, 6]})
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        loaded = pd.read_csv(self.test_file, parse_dates=["date"])
        assert pd.api.types.is_datetime64_any_dtype(loaded["date"])

    def test_save_large_list(self):
        """Test saving large list of DataFrames"""
        listed_dfs = []
        for i in range(100):
            df = pd.DataFrame({
                "id": [i] * 10,
                "value": np.random.randn(10)
            })
            listed_dfs.append(df)
        
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        assert len(loaded) == 1000  # 100 DataFrames × 10 rows each

    def test_save_with_multiindex(self):
        """Test saving DataFrames with MultiIndex"""
        # Create MultiIndex DataFrames
        index1 = pd.MultiIndex.from_tuples([("A", 1), ("A", 2), ("B", 1)])
        df1 = pd.DataFrame({"value": [10, 20, 30]}, index=index1)
        
        index2 = pd.MultiIndex.from_tuples([("B", 2), ("C", 1), ("C", 2)])
        df2 = pd.DataFrame({"value": [40, 50, 60]}, index=index2)
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file, index=True)
        
        # MultiIndex will be flattened in CSV
        loaded = pd.read_csv(self.test_file)
        assert len(loaded) == 6

    def test_save_with_missing_values(self):
        """Test saving DataFrames with missing values"""
        df1 = pd.DataFrame({
            "A": [1, np.nan, 3],
            "B": [4, 5, np.nan]
        })
        df2 = pd.DataFrame({
            "A": [np.nan, 7, 8],
            "B": [9, np.nan, 11]
        })
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        assert pd.isna(loaded.iloc[1]["A"])
        assert pd.isna(loaded.iloc[3]["A"])

    def test_save_single_dataframe(self):
        """Test saving single DataFrame in a list"""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        save_listed_dfs_as_csv([df], self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        pd.testing.assert_frame_equal(loaded, df)

    def test_error_empty_list(self):
        """Test error handling for empty list"""
        with pytest.raises(ValueError):
            save_listed_dfs_as_csv([], self.test_file)

    def test_error_non_dataframe_items(self):
        """Test error handling for non-DataFrame items"""
        with pytest.raises(TypeError):
            save_listed_dfs_as_csv([pd.DataFrame({"A": [1]}), "not a df"], self.test_file)

    def test_save_with_custom_separator(self):
        """Test saving with custom separator"""
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})
        
        listed_dfs = [df1, df2]
        save_listed_dfs_as_csv(listed_dfs, self.test_file, sep=";")
        
        loaded = pd.read_csv(self.test_file, sep=";")
        expected = pd.concat([df1, df2], ignore_index=True)
        pd.testing.assert_frame_equal(loaded, expected)


# EOF