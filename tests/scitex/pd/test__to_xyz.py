#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:10:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__to_xyz.py

"""
Test module for scitex.pd.to_xyz function.
"""

import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal


class TestToXYZ:
    """Test class for to_xyz function."""

    @pytest.fixture
    def rectangular_df(self):
        """Create a rectangular DataFrame for testing."""
        data = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
        return pd.DataFrame(data, index=["A", "B", "C"], columns=["W", "X", "Y", "Z"])

    @pytest.fixture
    def named_axes_df(self):
        """Create a DataFrame with named index and columns."""
        data = np.array([[1, 2], [3, 4]])
        df = pd.DataFrame(data, index=["row1", "row2"], columns=["col1", "col2"])
        df.index.name = "rows"
        df.columns.name = "cols"
        return df

    @pytest.fixture
    def numeric_df(self):
        """Create a DataFrame with numeric index and columns."""
        data = np.array([[10, 20, 30], [40, 50, 60]])
        return pd.DataFrame(data)

    def test_import(self):
        """Test that to_xyz can be imported."""
        from scitex.pd import to_xyz

        assert callable(to_xyz)

    def test_basic_conversion(self, rectangular_df):
        """Test basic conversion of rectangular DataFrame."""
        from scitex.pd import to_xyz

        result = to_xyz(rectangular_df)

        # Check shape: 3 rows × 4 columns = 12 rows
        assert result.shape == (12, 3)

        # Check columns (should be 'x', 'y', 'z' when no names)
        assert list(result.columns) == ["x", "y", "z"]

        # Check first few values
        expected_first_rows = [
            ("A", "W", 1),
            ("B", "W", 5),
            ("C", "W", 9),
            ("A", "X", 2),
            ("B", "X", 6),
            ("C", "X", 10),
        ]

        for i, (x, y, z) in enumerate(expected_first_rows[:6]):
            assert result.iloc[i]["x"] == x
            assert result.iloc[i]["y"] == y
            assert result.iloc[i]["z"] == z

    def test_named_axes(self, named_axes_df):
        """Test conversion with named index and columns."""
        from scitex.pd import to_xyz

        result = to_xyz(named_axes_df)

        # Check column names use the axis names
        assert list(result.columns) == ["rows", "cols", "z"]

        # Check values
        assert result.shape == (4, 3)
        expected_values = [
            ("row1", "col1", 1),
            ("row2", "col1", 3),
            ("row1", "col2", 2),
            ("row2", "col2", 4),
        ]

        for i, (row, col, z) in enumerate(expected_values):
            assert result.iloc[i]["rows"] == row
            assert result.iloc[i]["cols"] == col
            assert result.iloc[i]["z"] == z

    def test_numeric_indices(self, numeric_df):
        """Test conversion with numeric index and columns."""
        from scitex.pd import to_xyz

        result = to_xyz(numeric_df)

        # Should have default column names
        assert list(result.columns) == ["x", "y", "z"]

        # Check shape
        assert result.shape == (6, 3)  # 2×3 = 6 rows

        # Check that numeric indices are preserved
        assert result["x"].iloc[0] == 0
        assert result["y"].iloc[0] == 0
        assert result["z"].iloc[0] == 10

    def test_single_column_dataframe(self):
        """Test conversion of single column DataFrame."""
        from scitex.pd import to_xyz

        df = pd.DataFrame({"A": [1, 2, 3]}, index=["x1", "x2", "x3"])
        result = to_xyz(df)

        assert result.shape == (3, 3)
        assert list(result["x"]) == ["x1", "x2", "x3"]
        assert list(result["y"]) == ["A", "A", "A"]
        assert list(result["z"]) == [1, 2, 3]

    def test_single_row_dataframe(self):
        """Test conversion of single row DataFrame."""
        from scitex.pd import to_xyz

        df = pd.DataFrame([[1, 2, 3]], columns=["A", "B", "C"], index=["row1"])
        result = to_xyz(df)

        assert result.shape == (3, 3)
        assert list(result["x"]) == ["row1", "row1", "row1"]
        assert list(result["y"]) == ["A", "B", "C"]
        assert list(result["z"]) == [1, 2, 3]

    def test_with_nan_values(self):
        """Test handling of NaN values."""
        from scitex.pd import to_xyz

        df = pd.DataFrame(
            {"A": [1, np.nan, 3], "B": [np.nan, 5, 6], "C": [7, 8, np.nan]},
            index=["X", "Y", "Z"],
        )

        result = to_xyz(df)

        # NaN values should be preserved
        assert result.shape == (9, 3)
        nan_count = result["z"].isna().sum()
        assert nan_count == 3

    def test_empty_dataframe(self):
        """Test conversion of empty DataFrame."""
        from scitex.pd import to_xyz

        # Empty DataFrame
        df = pd.DataFrame()
        result = to_xyz(df)
        assert result.empty

        # DataFrame with structure but no data
        df = pd.DataFrame(columns=["A", "B"], index=[])
        result = to_xyz(df)
        assert result.empty
        assert list(result.columns) == ["x", "y", "z"]

    def test_column_order(self, rectangular_df):
        """Test that columns are processed in order."""
        from scitex.pd import to_xyz

        result = to_xyz(rectangular_df)

        # Group by y and check order
        y_values = result["y"].unique()
        assert list(y_values) == ["W", "X", "Y", "Z"]

    def test_index_preservation(self):
        """Test that index values are preserved correctly."""
        from scitex.pd import to_xyz

        # Create DataFrame with string index
        df = pd.DataFrame(
            {"col1": [100, 200], "col2": [300, 400]}, index=["first", "second"]
        )

        result = to_xyz(df)

        # Check that index values appear in x column
        x_values = sorted(result["x"].unique())
        assert x_values == ["first", "second"]

    def test_mixed_types(self):
        """Test conversion with mixed data types."""
        from scitex.pd import to_xyz

        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "str_col": ["a", "b", "c"],
            },
            index=["r1", "r2", "r3"],
        )

        result = to_xyz(df)

        assert result.shape == (9, 3)
        # Check that different types are preserved in z column
        int_vals = result[result["y"] == "int_col"]["z"].tolist()
        assert int_vals == [1, 2, 3]

        str_vals = result[result["y"] == "str_col"]["z"].tolist()
        assert str_vals == ["a", "b", "c"]

    def test_multiindex_not_supported(self):
        """Test behavior with MultiIndex (current implementation doesn't handle specially)."""
        from scitex.pd import to_xyz

        # Create DataFrame with MultiIndex
        arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
        index = pd.MultiIndex.from_arrays(arrays, names=["first", "second"])
        df = pd.DataFrame({"col": [10, 20, 30, 40]}, index=index)

        result = to_xyz(df)
        # MultiIndex becomes tuples in the result
        assert result.shape == (4, 3)
        assert isinstance(result["first"].iloc[0], tuple)

    def test_datetime_index(self):
        """Test conversion with datetime index."""
        from scitex.pd import to_xyz

        dates = pd.date_range("2021-01-01", periods=3)
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}, index=dates)

        result = to_xyz(df)

        assert result.shape == (6, 3)
        # Check that datetime values are preserved
        assert pd.api.types.is_datetime64_any_dtype(result["x"])

    @pytest.mark.parametrize("nrows,ncols", [(1, 10), (10, 1), (5, 5), (3, 7)])
    def test_various_shapes(self, nrows, ncols):
        """Test conversion with various DataFrame shapes."""
        from scitex.pd import to_xyz

        data = np.arange(nrows * ncols).reshape(nrows, ncols)
        df = pd.DataFrame(data)

        result = to_xyz(df)
        assert result.shape == (nrows * ncols, 3)
        assert len(result["z"]) == nrows * ncols

    def test_no_square_requirement(self):
        """Test that to_xyz doesn't require square DataFrame (unlike to_xy)."""
        from scitex.pd import to_xyz

        # Non-square DataFrame should work fine
        df = pd.DataFrame(np.arange(12).reshape(3, 4))
        result = to_xyz(df)
        assert result.shape == (12, 3)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/_to_xyz.py
# --------------------------------------------------------------------------------
# #!/./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-09-28 11:17:22 (ywatanabe)"
# # ./src/scitex/pd/_to_xyz.py
#
# import scitex
# import numpy as np
# import pandas as pd
#
# def to_xyz(data_frame):
#     """
#     Convert a heatmap DataFrame into x, y, z format.
#
#     Ensure the index and columns are the same, and if either exists, replace with that.
#
#     Example
#     -------
#     data_frame = pd.DataFrame(...)  # Your DataFrame here
#     out = to_xyz(data_frame)
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
#         if np.array_equal(data_frame.index, np.arange(len(data_frame.index))):
#             data_frame.columns = data_frame.index
#         elif np.array_equal(data_frame.columns, np.arange(len(data_frame.columns))):
#             data_frame.index = data_frame.columns
#         else:
#             raise ValueError("Either index or columns must be a range of integers")
#
#     x_name = data_frame.index.name or 'x'
#     y_name = data_frame.columns.name or 'y'
#
#     formatted_data_frames = []
#
#     for column in data_frame.columns:
#         column_data_frame = data_frame[column]
#         formatted_data = pd.DataFrame({
#             x_name: column_data_frame.index,
#             y_name: column,
#             'z': column_data_frame.values
#         })
#         formatted_data_frames.append(formatted_data)
#
#     result = pd.concat(formatted_data_frames, ignore_index=True)
#     result = scitex.pd.mv(result, 'z', -1)
#
#     return result
#
# # def to_xyz(data_frame):
# #     """
# #     Convert a heatmap DataFrame into x, y, z format.
#
# #     Ensure the index and columns are the same, and if either exists, replace with that.
#
# #     Example
# #     -------
# #     data_frame = pd.DataFrame(...)  # Your DataFrame here
# #     out = to_xy(data_frame)
# #     print(out)
#
# #     Parameters
# #     ----------
# #     data_frame : pandas.DataFrame
# #         The input DataFrame to be converted.
#
# #     Returns
# #     -------
# #     pandas.DataFrame
# #         A DataFrame formatted with columns ['x', 'y', 'z']
# #     """
# #     assert data_frame.shape[0] == data_frame.shape[1]
#
# #     if not data_frame.index.equals(data_frame.columns):
#
# #         if (data_frame.index == np.array(range(len(data_frame.index)))).all():
# #             data_frame.columns = data_frame.index
# #         elif (
# #             data_frame.columns == np.array(range(len(data_frame.columns)))
# #         ).all():
# #             data_frame.index = data_frame.columns
# #         else:
# #             raise ValueError("Either index or columns must be a range of integers")
#
# #     formatted_data_frames = []
#
# #     for column in data_frame.columns:
# #         column_data_frame = data_frame[column]
# #         y_label = column_data_frame.name
# #         column_data_frame = pd.DataFrame(column_data_frame)
# #         column_data_frame["x"] = column_data_frame.index
# #         column_data_frame["y"] = y_label
# #         column_data_frame = column_data_frame.reset_index().drop(
# #             columns=["index"]
# #         )
# #         column_data_frame = column_data_frame.rename(columns={y_label: "z"})
# #         column_data_frame = scitex.pd.mv(column_data_frame, "z", -1)
# #         formatted_data_frames.append(column_data_frame)
#
# #     return pd.concat(formatted_data_frames, ignore_index=True)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/_to_xyz.py
# --------------------------------------------------------------------------------
