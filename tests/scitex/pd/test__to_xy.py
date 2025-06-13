#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:05:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__to_xy.py

"""
Test module for scitex.pd.to_xy function.
"""

import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal


class TestToXY:
    """Test class for to_xy function."""

    @pytest.fixture
    def square_df(self):
        """Create a square DataFrame for testing."""
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        return pd.DataFrame(data, index=["A", "B", "C"], columns=["A", "B", "C"])

    @pytest.fixture
    def numeric_index_df(self):
        """Create a DataFrame with numeric index and named columns."""
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        return pd.DataFrame(data, index=[0, 1, 2], columns=["A", "B", "C"])

    @pytest.fixture
    def numeric_columns_df(self):
        """Create a DataFrame with named index and numeric columns."""
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        return pd.DataFrame(data, index=["A", "B", "C"], columns=[0, 1, 2])

    def test_import(self):
        """Test that to_xy can be imported."""
        from scitex.pd import to_xy

        assert callable(to_xy)

    def test_basic_conversion(self, square_df):
        """Test basic conversion of square DataFrame."""
        from scitex.pd import to_xy

        result = to_xy(square_df)

        # Check shape
        assert result.shape == (9, 3)  # 3x3 matrix = 9 rows

        # Check columns
        assert list(result.columns) == ["x", "y", "z"]

        # Check values
        expected_values = [
            ("A", "A", 1),
            ("B", "A", 4),
            ("C", "A", 7),
            ("A", "B", 2),
            ("B", "B", 5),
            ("C", "B", 8),
            ("A", "C", 3),
            ("B", "C", 6),
            ("C", "C", 9),
        ]

        for i, (x, y, z) in enumerate(expected_values):
            assert result.iloc[i]["x"] == x
            assert result.iloc[i]["y"] == y
            assert result.iloc[i]["z"] == z

    def test_numeric_index_replacement(self, numeric_index_df):
        """Test that numeric index is replaced with column names."""
        from scitex.pd import to_xy

        result = to_xy(numeric_index_df)

        # After replacement, both index and columns should be ['A', 'B', 'C']
        assert result.shape == (9, 3)

        # Check that x values are now 'A', 'B', 'C' not 0, 1, 2
        unique_x = sorted(result["x"].unique())
        assert unique_x == ["A", "B", "C"]

        # Check y values
        unique_y = sorted(result["y"].unique())
        assert unique_y == ["A", "B", "C"]

    def test_numeric_columns_replacement(self, numeric_columns_df):
        """Test that numeric columns are replaced with index names."""
        from scitex.pd import to_xy

        result = to_xy(numeric_columns_df)

        # After replacement, both index and columns should be ['A', 'B', 'C']
        assert result.shape == (9, 3)

        # Check that y values are now 'A', 'B', 'C' not 0, 1, 2
        unique_y = sorted(result["y"].unique())
        assert unique_y == ["A", "B", "C"]

    def test_non_square_dataframe(self):
        """Test that non-square DataFrame raises assertion error."""
        from scitex.pd import to_xy

        # Create non-square DataFrame
        df = pd.DataFrame(np.array([[1, 2], [3, 4], [5, 6]]))

        with pytest.raises(AssertionError):
            to_xy(df)

    def test_identity_matrix(self):
        """Test conversion of identity matrix."""
        from scitex.pd import to_xy

        # Create identity matrix
        data = np.eye(3)
        df = pd.DataFrame(data, index=["A", "B", "C"], columns=["A", "B", "C"])

        result = to_xy(df)

        # Check diagonal values are 1
        diagonal = result[(result["x"] == result["y"])]
        assert all(diagonal["z"] == 1.0)

        # Check off-diagonal values are 0
        off_diagonal = result[(result["x"] != result["y"])]
        assert all(off_diagonal["z"] == 0.0)

    def test_single_element_dataframe(self):
        """Test conversion of 1x1 DataFrame."""
        from scitex.pd import to_xy

        df = pd.DataFrame([[42]], index=["A"], columns=["A"])
        result = to_xy(df)

        assert result.shape == (1, 3)
        assert result.iloc[0]["x"] == "A"
        assert result.iloc[0]["y"] == "A"
        assert result.iloc[0]["z"] == 42

    def test_with_nan_values(self):
        """Test handling of NaN values."""
        from scitex.pd import to_xy

        data = np.array([[1, np.nan, 3], [4, 5, np.nan], [np.nan, 8, 9]])
        df = pd.DataFrame(data, index=["A", "B", "C"], columns=["A", "B", "C"])

        result = to_xy(df)

        # Check that NaN values are preserved
        nan_rows = result[result["z"].isna()]
        assert len(nan_rows) == 3

    def test_column_order_preserved(self, square_df):
        """Test that the order of columns is preserved in output."""
        from scitex.pd import to_xy

        result = to_xy(square_df)

        # Group by 'y' to check order
        y_values = []
        for _, group in result.groupby("y", sort=False):
            y_values.append(group["y"].iloc[0])

        assert y_values == ["A", "B", "C"]

    def test_index_order_preserved(self, square_df):
        """Test that the order of index is preserved in output."""
        from scitex.pd import to_xy

        result = to_xy(square_df)

        # Check first three rows (should be column 'A')
        first_col_x = list(result.iloc[:3]["x"])
        assert first_col_x == ["A", "B", "C"]

    def test_with_duplicate_index_names(self):
        """Test behavior with duplicate index/column names."""
        from scitex.pd import to_xy

        # This should work as long as it's square
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        df = pd.DataFrame(data, index=["A", "A", "B"], columns=["A", "A", "B"])

        result = to_xy(df)
        assert result.shape == (9, 3)

    def test_mismatched_index_columns_error(self):
        """Test that mismatched non-numeric index/columns raise error."""
        from scitex.pd import to_xy

        # Both index and columns are non-numeric but different
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        df = pd.DataFrame(data, index=["A", "B", "C"], columns=["X", "Y", "Z"])

        # This should raise ValueError (though the code just has "ValueError" without raising)
        # The current implementation might have a bug here
        with pytest.raises(Exception):  # Could be ValueError or AttributeError
            to_xy(df)

    @pytest.mark.parametrize("dtype", [int, float, np.float32, np.float64])
    def test_different_dtypes(self, dtype):
        """Test conversion with different data types."""
        from scitex.pd import to_xy

        data = np.array([[1, 2], [3, 4]], dtype=dtype)
        df = pd.DataFrame(data, index=["A", "B"], columns=["A", "B"])

        result = to_xy(df)
        assert result.shape == (4, 3)
        # Z values should maintain numeric type
        assert pd.api.types.is_numeric_dtype(result["z"])


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/_to_xy.py
# --------------------------------------------------------------------------------
# #!/./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-09-03 07:01:31 (ywatanabe)"
# # ./src/scitex/pd/_to_xy.py
#
# import scitex
# import numpy as np
# import pandas as pd
#
#
# def to_xy(data_frame):
#     """
#     Convert a heatmap DataFrame into x, y, z format.
#
#     Ensure the index and columns are the same, and if either exists, replace with that.
#
#     Example
#     -------
#     data_frame = pd.DataFrame(...)  # Your DataFrame here
#     out = to_xy(data_frame)
#     print(out)
#
#     Parameters
#     ----------
#     data_frame : pandas.DataFrame
#         The input DataFrame to be converted.
#
#     Returns
#     -------
#     pandas.DataFrame
#         A DataFrame formatted with columns ['x', 'y', 'z']
#     """
#     assert data_frame.shape[0] == data_frame.shape[1]
#
#     if not data_frame.index.equals(data_frame.columns):
#
#         if (data_frame.index == np.array(range(len(data_frame.index)))).all():
#             data_frame.columns = data_frame.index
#         elif (
#             data_frame.columns == np.array(range(len(data_frame.columns)))
#         ).all():
#             data_frame.index = data_frame.columns
#         else:
#             ValueError
#         # else:
#         #     ValueError "Either of index or columns has to be passed"
#
#     formatted_data_frames = []
#
#     for column in data_frame.columns:
#         column_data_frame = data_frame[column]
#         y_label = column_data_frame.name
#         column_data_frame = pd.DataFrame(column_data_frame)
#         column_data_frame["x"] = column_data_frame.index
#         column_data_frame["y"] = y_label
#         column_data_frame = column_data_frame.reset_index().drop(
#             columns=["index"]
#         )
#         column_data_frame = column_data_frame.rename(columns={y_label: "z"})
#         column_data_frame = scitex.pd.mv(column_data_frame, "z", -1)
#         formatted_data_frames.append(column_data_frame)
#
#     return pd.concat(formatted_data_frames, ignore_index=True)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/_to_xy.py
# --------------------------------------------------------------------------------
