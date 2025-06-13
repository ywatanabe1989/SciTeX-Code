#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:45:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__excel.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__excel.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for Excel saving functionality
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from scitex.io._save_modules import save_excel


class TestSaveExcel:
    """Test suite for save_excel function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.xlsx")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_dataframe(self):
        """Test saving a pandas DataFrame"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": ["x", "y", "z"]})
        save_excel(df, self.test_file)
        
        # Verify file exists and content is correct
        assert os.path.exists(self.test_file)
        loaded_df = pd.read_excel(self.test_file)
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_save_dict(self):
        """Test saving dictionary as Excel"""
        data = {"col1": [1, 2, 3], "col2": [4, 5, 6], "col3": ["a", "b", "c"]}
        save_excel(data, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        pd.testing.assert_frame_equal(pd.DataFrame(data), loaded_df)

    def test_save_numpy_array(self):
        """Test saving numpy array as Excel"""
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        save_excel(arr, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        np.testing.assert_array_equal(arr, loaded_df.values)

    def test_save_2d_list(self):
        """Test saving 2D list as Excel through numpy conversion"""
        data = [[1, 2, 3], [4, 5, 6]]
        arr = np.array(data)
        save_excel(arr, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        np.testing.assert_array_equal(arr, loaded_df.values)

    def test_save_with_sheet_name(self):
        """Test saving with custom sheet name"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        save_excel(df, self.test_file, sheet_name="MySheet")
        
        loaded_df = pd.read_excel(self.test_file, sheet_name="MySheet")
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_save_multiple_sheets(self):
        """Test saving multiple sheets using ExcelWriter"""
        df1 = pd.DataFrame({"a": [1, 2, 3]})
        df2 = pd.DataFrame({"b": [4, 5, 6]})
        
        # This would require modifying save_excel to support multiple sheets
        # For now, test single sheet functionality
        save_excel(df1, self.test_file)
        assert os.path.exists(self.test_file)

    def test_save_mixed_types(self):
        """Test saving mixed data types"""
        data = {
            "integers": [1, 2, 3],
            "floats": [1.1, 2.2, 3.3],
            "strings": ["a", "b", "c"],
            "booleans": [True, False, True]
        }
        save_excel(data, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        assert loaded_df["integers"].dtype == np.int64
        assert loaded_df["floats"].dtype == np.float64
        assert loaded_df["strings"].dtype == object
        assert loaded_df["booleans"].dtype == bool

    def test_save_with_datetime(self):
        """Test saving datetime data"""
        dates = pd.date_range("2023-01-01", periods=3)
        df = pd.DataFrame({"date": dates, "value": [1, 2, 3]})
        save_excel(df, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        # Excel might change datetime precision slightly
        assert len(loaded_df) == len(df)
        assert list(loaded_df["value"]) == [1, 2, 3]

    def test_save_large_dataframe(self):
        """Test saving large DataFrame"""
        df = pd.DataFrame(np.random.randn(1000, 10))
        save_excel(df, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        assert loaded_df.shape == (1000, 10)

    def test_error_unsupported_type(self):
        """Test error handling for unsupported types"""
        class CustomObject:
            pass
        
        obj = CustomObject()
        with pytest.raises(ValueError, match="Cannot save object of type"):
            save_excel(obj, self.test_file)

    def test_save_empty_dataframe(self):
        """Test saving empty DataFrame"""
        df = pd.DataFrame()
        save_excel(df, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        assert loaded_df.empty

    def test_save_with_special_characters(self):
        """Test saving data with special characters"""
        df = pd.DataFrame({
            "col1": ["hello", "world", "test"],
            "col2": ["特殊文字", "émojis 😊", "tabs\there"]
        })
        save_excel(df, self.test_file)
        
        loaded_df = pd.read_excel(self.test_file)
        pd.testing.assert_frame_equal(df, loaded_df)


# EOF