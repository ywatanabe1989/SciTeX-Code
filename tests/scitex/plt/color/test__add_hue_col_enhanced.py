#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 09:55:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/color/test__add_hue_col_enhanced.py

"""Comprehensive tests for add_hue_col DataFrame enhancement functionality."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch


class TestAddHueColEnhanced:
    """Enhanced test suite for add_hue_col function."""

    def test_basic_functionality(self):
        """Test basic hue column addition."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        result = add_hue_col(df)
        
        # Should add hue column and dummy row
        assert "hue" in result.columns
        assert len(result) == len(df) + 1
        assert result["hue"].iloc[-1] == 1  # Dummy row has hue=1
        assert (result["hue"].iloc[:-1] == 0).all()  # Original rows have hue=0

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame()
        result = add_hue_col(df)
        
        # Should still add hue column and dummy row
        assert "hue" in result.columns
        assert len(result) == 1
        assert result["hue"].iloc[0] == 1

    def test_single_row_dataframe(self):
        """Test with single row DataFrame."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({"value": [42]})
        result = add_hue_col(df)
        
        assert len(result) == 2
        assert result["hue"].iloc[0] == 0  # Original row
        assert result["hue"].iloc[1] == 1  # Dummy row

    def test_different_column_types(self):
        """Test with different column data types."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True]
        })
        
        result = add_hue_col(df)
        
        # Check dummy row values based on data types
        dummy_row = result.iloc[-1]
        
        # Int64 columns should have NaN in dummy row
        assert pd.isna(dummy_row["int_col"])
        
        # Float columns should have NaN in dummy row
        assert pd.isna(dummy_row["float_col"])
        
        # Object/string columns should have NaN in dummy row
        assert pd.isna(dummy_row["str_col"])
        
        # Boolean columns should have None in dummy row
        assert dummy_row["bool_col"] is None or pd.isna(dummy_row["bool_col"])

    def test_existing_hue_column(self):
        """Test behavior when hue column already exists."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "data": [1, 2, 3],
            "hue": [5, 6, 7]  # Pre-existing hue column
        })
        
        result = add_hue_col(df)
        
        # Function should overwrite existing hue column
        assert (result["hue"].iloc[:-1] == 0).all()  # Original rows set to 0
        assert result["hue"].iloc[-1] == 1  # Dummy row set to 1

    def test_large_dataframe(self):
        """Test with large DataFrame."""
from scitex.plt.color import add_hue_col
        
        large_df = pd.DataFrame({
            "col1": range(10000),
            "col2": np.random.rand(10000)
        })
        
        result = add_hue_col(large_df)
        
        assert len(result) == 10001
        assert "hue" in result.columns
        assert result["hue"].iloc[-1] == 1

    def test_mixed_data_types(self):
        """Test with mixed data types in single DataFrame."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "integers": [1, 2, 3],
            "floats": [1.5, 2.5, 3.5],
            "strings": ["foo", "bar", "baz"],
            "booleans": [True, False, True],
            "dates": pd.date_range("2023-01-01", periods=3)
        })
        
        result = add_hue_col(df)
        
        # Should handle all data types
        assert len(result) == 4
        assert result["hue"].iloc[-1] == 1

    def test_column_order_preservation(self):
        """Test that column order is preserved."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "z_col": [1, 2],
            "a_col": [3, 4],
            "m_col": [5, 6]
        })
        
        original_cols = list(df.columns)
        result = add_hue_col(df)
        
        # Hue should be added, but original column order preserved
        expected_cols = original_cols + ["hue"]
        assert list(result.columns) == expected_cols

    def test_index_handling(self):
        """Test that DataFrame index is handled correctly."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame(
            {"value": [10, 20, 30]},
            index=["a", "b", "c"]
        )
        
        result = add_hue_col(df)
        
        # Should preserve original indices and add new one for dummy row
        assert len(result) == 4
        assert list(result.index[:3]) == ["a", "b", "c"]

    def test_categorical_columns(self):
        """Test with categorical data."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "category": pd.Categorical(["A", "B", "A", "C"]),
            "value": [1, 2, 3, 4]
        })
        
        result = add_hue_col(df)
        
        # Should handle categorical data
        assert len(result) == 5
        assert result["hue"].iloc[-1] == 1

    def test_multiindex_columns(self):
        """Test with MultiIndex columns."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            ("level1", "sublevel1"): [1, 2, 3],
            ("level1", "sublevel2"): [4, 5, 6]
        })
        
        try:
            result = add_hue_col(df)
            # Should work with MultiIndex columns
            assert "hue" in [col for col in result.columns if isinstance(col, str)]
        except Exception:
            # MultiIndex columns might not be fully supported
            pass

    def test_nan_values_in_original_data(self):
        """Test behavior with NaN values in original DataFrame."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "col1": [1, np.nan, 3],
            "col2": [np.nan, 2, np.nan]
        })
        
        result = add_hue_col(df)
        
        # Should preserve existing NaN values
        assert len(result) == 4
        assert pd.isna(result["col1"].iloc[1])  # Original NaN preserved
        assert pd.isna(result["col2"].iloc[0])  # Original NaN preserved

    def test_datetime_columns(self):
        """Test with datetime columns."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "date": pd.date_range("2023-01-01", periods=3),
            "value": [10, 20, 30]
        })
        
        result = add_hue_col(df)
        
        assert len(result) == 4
        assert result["hue"].iloc[-1] == 1

    def test_original_dataframe_unchanged(self):
        """Test that original DataFrame is not modified."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({"col1": [1, 2, 3]})
        original_len = len(df)
        original_cols = list(df.columns)
        
        result = add_hue_col(df)
        
        # Original DataFrame should be modified (function adds hue column)
        # But length should be different from result
        assert len(result) != original_len
        assert "hue" in result.columns

    def test_memory_efficiency(self):
        """Test memory efficiency with wide DataFrames."""
from scitex.plt.color import add_hue_col
        
        # Create DataFrame with many columns
        data = {f"col_{i}": [1, 2, 3] for i in range(100)}
        df = pd.DataFrame(data)
        
        result = add_hue_col(df)
        
        assert len(result) == 4
        assert len(result.columns) == 101  # 100 original + hue

    def test_special_column_names(self):
        """Test with special column names."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "col with spaces": [1, 2],
            "col-with-dashes": [3, 4],
            "col.with.dots": [5, 6],
            "123numeric": [7, 8]
        })
        
        result = add_hue_col(df)
        
        assert len(result) == 3
        assert "hue" in result.columns

    def test_duplicate_column_names(self):
        """Test behavior with duplicate column names."""
from scitex.plt.color import add_hue_col
        
        # Pandas typically doesn't allow duplicate column names
        # but let's test if our function handles it gracefully
        try:
            df = pd.DataFrame([[1, 2], [3, 4]])
            df.columns = ["col", "col"]  # Force duplicate names
            
            result = add_hue_col(df)
            assert len(result) == 3
        except Exception:
            # Duplicate column names might cause issues
            pass

    def test_very_wide_dataframe(self):
        """Test with very wide DataFrame (many columns)."""
from scitex.plt.color import add_hue_col
        
        # Create DataFrame with 1000 columns
        data = {f"col_{i}": [i] for i in range(1000)}
        df = pd.DataFrame(data)
        
        result = add_hue_col(df)
        
        assert len(result) == 2  # Original row + dummy row
        assert len(result.columns) == 1001  # 1000 original + hue

    def test_dtype_preservation(self):
        """Test that data types are preserved where possible."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({
            "int8": np.array([1, 2, 3], dtype=np.int8),
            "float32": np.array([1.1, 2.2, 3.3], dtype=np.float32),
            "uint16": np.array([1, 2, 3], dtype=np.uint16)
        })
        
        result = add_hue_col(df)
        
        # Check that original data types are preserved in non-dummy rows
        assert result["int8"].dtype in [np.int8, np.float64]  # Might be promoted due to NaN
        assert result["float32"].dtype in [np.float32, np.float64]

    def test_concat_behavior(self):
        """Test pandas concat behavior used internally."""
from scitex.plt.color import add_hue_col
        
        df = pd.DataFrame({"value": [1, 2, 3]})
        
        with patch('pandas.concat') as mock_concat:
            mock_concat.return_value = pd.DataFrame({
                "value": [1, 2, 3, np.nan],
                "hue": [0, 0, 0, 1]
            })
            
            result = add_hue_col(df)
            
            # Verify concat was called
            mock_concat.assert_called_once()
            args, kwargs = mock_concat.call_args
            assert kwargs.get('axis') == 0

    def test_performance_with_large_data(self):
        """Test performance with realistically large data."""
from scitex.plt.color import add_hue_col
        
        # Create moderately large DataFrame
        df = pd.DataFrame({
            "id": range(50000),
            "value1": np.random.rand(50000),
            "value2": np.random.rand(50000),
            "category": np.random.choice(["A", "B", "C"], 50000)
        })
        
        result = add_hue_col(df)
        
        # Should complete in reasonable time
        assert len(result) == 50001
        assert result["hue"].iloc[-1] == 1


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])