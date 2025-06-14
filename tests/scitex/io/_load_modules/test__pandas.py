#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__pandas.py

"""Tests for pandas file loading functionality.

This module tests the pandas loading functions from scitex.io._load_modules._pandas,
including _load_csv, _load_tsv, _load_excel, and _load_parquet.
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np


def test_load_csv_basic():
    """Test loading a basic CSV file."""
    from scitex.io._load_modules import _load_csv
    
    # Create sample DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': [1.1, 2.2, 3.3, 4.4, 5.5]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=True)
        temp_path = f.name
    
    try:
        # Load with default index_col=0
        loaded_df = _load_csv(temp_path)
        pd.testing.assert_frame_equal(loaded_df, df)
        
        # Load without index column
        loaded_df_no_index = _load_csv(temp_path, index_col=None)
        assert loaded_df_no_index.shape[1] == df.shape[1] + 1  # Extra column for index
    finally:
        os.unlink(temp_path)


def test_load_csv_unnamed_columns():
    """Test that unnamed columns are removed."""
    from scitex.io._load_modules import _load_csv
    
    # Create DataFrame with unnamed columns
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'Unnamed: 1': [4, 5, 6],  # This should be removed
        'B': [7, 8, 9],
        'Unnamed: 3': [10, 11, 12]  # This should be removed
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_path = f.name
    
    try:
        loaded_df = _load_csv(temp_path, index_col=None)
        
        # Check that unnamed columns are removed
        assert 'Unnamed: 1' not in loaded_df.columns
        assert 'Unnamed: 3' not in loaded_df.columns
        assert 'A' in loaded_df.columns
        assert 'B' in loaded_df.columns
        assert len(loaded_df.columns) == 2
    finally:
        os.unlink(temp_path)


def test_load_csv_with_options():
    """Test loading CSV with various pandas options."""
    from scitex.io._load_modules import _load_csv
    
    # Create CSV with various features
    data = """date,value,category
2023-01-01,100.5,A
2023-01-02,200.3,B
2023-01-03,300.1,A"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(data)
        temp_path = f.name
    
    try:
        # Load with date parsing
        loaded_df = _load_csv(temp_path, index_col=None, parse_dates=['date'])
        
        assert pd.api.types.is_datetime64_any_dtype(loaded_df['date'])
        assert loaded_df['value'].dtype == float
        assert len(loaded_df) == 3
    finally:
        os.unlink(temp_path)


def test_load_csv_invalid_extension():
    """Test that loading non-CSV file raises ValueError."""
    from scitex.io._load_modules import _load_csv
    
    with pytest.raises(ValueError, match="File must have .csv extension"):
        _load_csv("test.txt")


def test_load_tsv_basic():
    """Test loading a TSV file."""
    from scitex.io._load_modules import _load_tsv
    
    # Create sample data
    df = pd.DataFrame({
        'col1': ['a', 'b', 'c'],
        'col2': [1, 2, 3],
        'col3': [1.1, 2.2, 3.3]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
        df.to_csv(f.name, sep='\t', index=False)
        temp_path = f.name
    
    try:
        loaded_df = _load_tsv(temp_path)
        pd.testing.assert_frame_equal(loaded_df, df)
    finally:
        os.unlink(temp_path)


def test_load_tsv_invalid_extension():
    """Test that loading non-TSV file raises ValueError."""
    from scitex.io._load_modules import _load_tsv
    
    with pytest.raises(ValueError, match="File must have .tsv extension"):
        _load_tsv("test.csv")


def test_load_excel_basic():
    """Test loading an Excel file."""
    from scitex.io._load_modules import _load_excel
    
    # Skip if openpyxl not available
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not available")
    
    # Create sample DataFrame
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'Score': [85.5, 90.0, 78.5]
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df.to_excel(f.name, index=False)
        temp_path = f.name
    
    try:
        loaded_df = _load_excel(temp_path)
        pd.testing.assert_frame_equal(loaded_df, df)
    finally:
        os.unlink(temp_path)


def test_load_excel_multiple_sheets():
    """Test loading Excel file with multiple sheets."""
    from scitex.io._load_modules import _load_excel
    
    # Skip if openpyxl not available
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not available")
    
    df1 = pd.DataFrame({'A': [1, 2, 3]})
    df2 = pd.DataFrame({'B': [4, 5, 6]})
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        with pd.ExcelWriter(f.name) as writer:
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='Sheet2', index=False)
        temp_path = f.name
    
    try:
        # Load specific sheet
        loaded_df1 = _load_excel(temp_path, sheet_name='Sheet1')
        pd.testing.assert_frame_equal(loaded_df1, df1)
        
        loaded_df2 = _load_excel(temp_path, sheet_name='Sheet2')
        pd.testing.assert_frame_equal(loaded_df2, df2)
    finally:
        os.unlink(temp_path)


def test_load_excel_invalid_extension():
    """Test that loading non-Excel file raises ValueError."""
    from scitex.io._load_modules import _load_excel
    
    with pytest.raises(ValueError, match="File must have Excel extension"):
        _load_excel("test.csv")


def test_load_parquet_basic():
    """Test loading a Parquet file."""
    from scitex.io._load_modules import _load_parquet
    
    # Skip if pyarrow not available
    try:
        import pyarrow
    except ImportError:
        pytest.skip("pyarrow not available")
    
    # Create sample DataFrame with various data types
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
        'str_col': ['a', 'b', 'c', 'd', 'e'],
        'datetime_col': pd.date_range('2023-01-01', periods=5),
        'bool_col': [True, False, True, False, True]
    })
    
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
        df.to_parquet(f.name)
        temp_path = f.name
    
    try:
        loaded_df = _load_parquet(temp_path)
        pd.testing.assert_frame_equal(loaded_df, df)
        
        # Verify data types are preserved
        assert loaded_df['int_col'].dtype == df['int_col'].dtype
        assert loaded_df['float_col'].dtype == df['float_col'].dtype
        assert pd.api.types.is_datetime64_any_dtype(loaded_df['datetime_col'])
    finally:
        os.unlink(temp_path)


def test_load_parquet_invalid_extension():
    """Test that loading non-Parquet file raises ValueError."""
    from scitex.io._load_modules import _load_parquet
    
    with pytest.raises(ValueError, match="File must have .parquet extension"):
        _load_parquet("test.csv")


def test_load_csv_nonexistent_file():
    """Test loading a nonexistent CSV file."""
    from scitex.io._load_modules import _load_csv
    
    with pytest.raises(FileNotFoundError):
        _load_csv("/nonexistent/path/file.csv")


def test_load_csv_large_file():
    """Test loading a large CSV file."""
    from scitex.io._load_modules import _load_csv
    
    # Create a large DataFrame
    n_rows = 10000
    df = pd.DataFrame({
        'id': range(n_rows),
        'value': np.random.rand(n_rows),
        'category': np.random.choice(['A', 'B', 'C'], n_rows)
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_path = f.name
    
    try:
        loaded_df = _load_csv(temp_path, index_col=None)
        assert len(loaded_df) == n_rows
        assert list(loaded_df.columns) == ['id', 'value', 'category']
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
