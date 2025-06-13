#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 18:03:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/color/test__add_hue_col.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/color/test__add_hue_col.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd
import pytest


def test_add_hue_appends_dummy_row():
    import pandas as pd
from scitex.plt.color import add_hue_col

    df = pd.DataFrame({"col1": [1, 2]})
    df2 = add_hue_col(df)
    assert "hue" in df2.columns
    assert df2["hue"].iloc[-1] == 1
    assert len(df2) == len(df) + 1


def test_add_hue_col_basic():
    """Test basic functionality of add_hue_col."""
from scitex.plt.color import add_hue_col
    
    # Create simple dataframe
    df = pd.DataFrame({
        "a": [1, 2, 3],
        "b": [4, 5, 6]
    })
    
    result = add_hue_col(df)
    
    # Check that hue column was added
    assert "hue" in result.columns
    
    # Check that original rows have hue=0
    assert all(result["hue"].iloc[:-1] == 0)
    
    # Check that dummy row has hue=1
    assert result["hue"].iloc[-1] == 1
    
    # Check that length increased by 1
    assert len(result) == len(df) + 1


def test_add_hue_col_different_dtypes():
    """Test with different data types."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({
        "int_col": [1, 2, 3],
        "float_col": [1.1, 2.2, 3.3],
        "str_col": ["a", "b", "c"],
        "bool_col": [True, False, True]
    })
    
    result = add_hue_col(df)
    
    # Check dummy row values
    dummy_row = result.iloc[-1]
    assert pd.isna(dummy_row["int_col"])
    assert pd.isna(dummy_row["float_col"])
    assert pd.isna(dummy_row["str_col"])
    # Boolean column gets None which becomes NaN
    assert pd.isna(dummy_row["bool_col"])
    assert dummy_row["hue"] == 1


def test_add_hue_col_empty_dataframe():
    """Test with empty dataframe."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame()
    result = add_hue_col(df)
    
    # Should have hue column and one row
    assert "hue" in result.columns
    assert len(result) == 1
    assert result["hue"].iloc[0] == 1


def test_add_hue_col_single_row():
    """Test with single row dataframe."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({"x": [10], "y": [20]})
    result = add_hue_col(df)
    
    assert len(result) == 2
    assert result["hue"].iloc[0] == 0
    assert result["hue"].iloc[1] == 1


def test_add_hue_col_existing_hue_column():
    """Test behavior when dataframe already has hue column."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({
        "col1": [1, 2, 3],
        "hue": [10, 20, 30]  # Existing hue column
    })
    
    result = add_hue_col(df)
    
    # Original hue values should be overwritten with 0
    assert all(result["hue"].iloc[:-1] == 0)
    assert result["hue"].iloc[-1] == 1


def test_add_hue_col_nan_values():
    """Test with dataframe containing NaN values."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({
        "a": [1, np.nan, 3],
        "b": [np.nan, 2, np.nan]
    })
    
    result = add_hue_col(df)
    
    # Check that original NaN values are preserved
    assert pd.isna(result["a"].iloc[1])
    assert pd.isna(result["b"].iloc[0])
    assert pd.isna(result["b"].iloc[2])
    
    # Check dummy row
    assert pd.isna(result["a"].iloc[-1])
    assert pd.isna(result["b"].iloc[-1])
    assert result["hue"].iloc[-1] == 1


def test_add_hue_col_categorical_data():
    """Test with categorical data."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({
        "cat_col": pd.Categorical(["A", "B", "A", "C"])
    })
    
    result = add_hue_col(df)
    
    assert len(result) == 5
    assert result["hue"].iloc[-1] == 1


def test_add_hue_col_datetime_data():
    """Test with datetime data."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({
        "date_col": pd.date_range("2023-01-01", periods=3)
    })
    
    result = add_hue_col(df)
    
    assert len(result) == 4
    assert result["hue"].iloc[-1] == 1
    # Datetime columns aren't explicitly handled, so behavior may vary
    # Just check that function doesn't crash


def test_add_hue_col_mixed_types():
    """Test with mixed numeric and non-numeric types."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({
        "num": [1, 2, 3],
        "text": ["x", "y", "z"],
        "mixed": [1, "two", 3.0]
    })
    
    result = add_hue_col(df)
    
    assert len(result) == 4
    assert all(result["hue"].iloc[:-1] == 0)
    assert result["hue"].iloc[-1] == 1


def test_add_hue_col_large_dataframe():
    """Test with larger dataframe."""
from scitex.plt.color import add_hue_col
    
    n_rows = 1000
    df = pd.DataFrame({
        "col1": range(n_rows),
        "col2": np.random.randn(n_rows),
        "col3": [f"item_{i}" for i in range(n_rows)]
    })
    
    result = add_hue_col(df)
    
    assert len(result) == n_rows + 1
    assert sum(result["hue"] == 0) == n_rows
    assert sum(result["hue"] == 1) == 1


def test_add_hue_col_preserves_index():
    """Test that index handling works correctly."""
from scitex.plt.color import add_hue_col
    
    # Create dataframe with custom index
    df = pd.DataFrame({
        "value": [10, 20, 30]
    }, index=["a", "b", "c"])
    
    result = add_hue_col(df)
    
    # Check that original indices are preserved
    assert list(result.index[:-1]) == ["a", "b", "c"]
    
    # The dummy row will have a numeric index (0)
    assert result.index[-1] == 0


def test_add_hue_col_multiindex():
    """Test with MultiIndex dataframe."""
from scitex.plt.color import add_hue_col
    
    # Create MultiIndex dataframe
    index = pd.MultiIndex.from_tuples([
        ("A", 1), ("A", 2), ("B", 1), ("B", 2)
    ])
    df = pd.DataFrame({"value": [10, 20, 30, 40]}, index=index)
    
    result = add_hue_col(df)
    
    assert len(result) == 5
    assert result["hue"].iloc[-1] == 1


def test_add_hue_col_wide_dataframe():
    """Test with many columns."""
from scitex.plt.color import add_hue_col
    
    # Create dataframe with many columns
    n_cols = 50
    data = {f"col_{i}": range(5) for i in range(n_cols)}
    df = pd.DataFrame(data)
    
    result = add_hue_col(df)
    
    assert len(result.columns) == n_cols + 1  # Original columns + hue
    assert "hue" in result.columns
    assert len(result) == 6  # 5 original rows + 1 dummy


def test_add_hue_col_original_unchanged():
    """Test that original dataframe is not modified."""
from scitex.plt.color import add_hue_col
    
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    original_shape = df.shape
    original_columns = list(df.columns)
    
    result = add_hue_col(df)
    
    # Original dataframe should be unchanged
    assert df.shape == original_shape
    assert list(df.columns) == original_columns
    assert "hue" not in df.columns


def test_add_hue_col_complex_dtypes():
    """Test with complex/unsupported dtypes."""
from scitex.plt.color import add_hue_col
    
    # Create dataframe with various complex types
    df = pd.DataFrame({
        "list_col": [[1, 2], [3, 4], [5, 6]],
        "dict_col": [{"a": 1}, {"b": 2}, {"c": 3}],
        "tuple_col": [(1, 2), (3, 4), (5, 6)]
    })
    
    result = add_hue_col(df)
    
    # Function should handle these without crashing
    assert len(result) == 4
    assert result["hue"].iloc[-1] == 1


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/color/_add_hue_col.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 18:02:24 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/color/_add_hue_col.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/color/_add_hue_col.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import numpy as np
# import pandas as pd
#
#
# def add_hue_col(df):
#     df["hue"] = 0
#     dummy_row = pd.DataFrame(
#         columns=df.columns,
#         data=np.array([np.nan for _ in df.columns]).reshape(1, -1),
#     )
#     dummy_row = {}
#     for col in df.columns:
#         dtype = df[col].dtype
#         if dtype is np.dtype(object):
#             dummy_row[col] = np.nan
#         if dtype is np.dtype(float):
#             dummy_row[col] = np.nan
#         if dtype is np.dtype(np.int64):
#             dummy_row[col] = np.nan
#         if dtype is np.dtype(bool):
#             dummy_row[col] = None
#
#     dummy_row = pd.DataFrame(pd.Series(dummy_row)).T
#
#     dummy_row["hue"] = 1
#     df_added = pd.concat([df, dummy_row], axis=0)
#     return df_added
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/color/_add_hue_col.py
# --------------------------------------------------------------------------------
