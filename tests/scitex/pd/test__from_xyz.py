#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 10:30:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__from_xyz.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.pd import from_xyz


class TestBasicFunctionality:
    """Test basic functionality of from_xyz."""

    def test_simple_xyz_conversion(self):
        """Test basic x, y, z conversion to pivot table."""
        data = pd.DataFrame(
            {"x": ["A", "B", "C", "A"], "y": ["X", "Y", "Z", "Y"], "z": [1, 2, 3, 4]}
        )
        result = from_xyz(data)

        assert isinstance(result, pd.DataFrame)
        assert "A" in result.columns
        assert "X" in result.index
        assert result.loc["Y", "A"] == 4
        assert result.loc["Y", "B"] == 2
        assert result.loc["Z", "C"] == 3

    def test_custom_column_names(self):
        """Test with custom column names."""
        data = pd.DataFrame(
            {"col1": ["A", "B", "C"], "col2": ["X", "Y", "Z"], "values": [10, 20, 30]}
        )
        result = from_xyz(data, x="col1", y="col2", z="values")

        assert result.loc["X", "A"] == 10
        assert result.loc["Y", "B"] == 20
        assert result.loc["Z", "C"] == 30

    def test_missing_values_filled_with_zero(self):
        """Test that missing values are filled with 0."""
        data = pd.DataFrame({"x": ["A", "B"], "y": ["X", "Y"], "z": [1, 2]})
        result = from_xyz(data)

        # Check that non-existent combinations are 0
        assert result.loc["X", "B"] == 0
        assert result.loc["Y", "A"] == 0

    def test_duplicate_xy_pairs(self):
        """Test handling of duplicate x,y pairs (uses first value)."""
        data = pd.DataFrame(
            {"x": ["A", "A", "A"], "y": ["X", "X", "X"], "z": [1, 2, 3]}
        )
        result = from_xyz(data)

        # Should use first value due to aggfunc='first'
        assert result.loc["X", "A"] == 1


class TestSquareMatrix:
    """Test square matrix functionality."""

    def test_square_false_default(self):
        """Test that square=False produces non-square matrix by default."""
        data = pd.DataFrame(
            {"x": ["A", "B", "C"], "y": ["X", "Y", "Y"], "z": [1, 2, 3]}
        )
        result = from_xyz(data, square=False)

        # Should have 2 rows (X, Y) and 3 columns (A, B, C)
        assert result.shape == (2, 3)
        assert list(result.index) == ["X", "Y"]
        assert list(result.columns) == ["A", "B", "C"]

    def test_square_true_creates_square_matrix(self):
        """Test that square=True creates a square matrix."""
        data = pd.DataFrame(
            {"x": ["A", "B", "C"], "y": ["X", "Y", "Y"], "z": [1, 2, 3]}
        )
        result = from_xyz(data, square=True)

        # Should create square matrix with all unique labels
        all_labels = ["A", "B", "C", "X", "Y"]
        assert result.shape == (5, 5)
        assert list(result.index) == all_labels
        assert list(result.columns) == all_labels

    def test_square_with_identical_labels(self):
        """Test square matrix when x and y have same labels."""
        data = pd.DataFrame(
            {"x": ["A", "B", "C", "A"], "y": ["B", "C", "A", "C"], "z": [1, 2, 3, 4]}
        )
        result = from_xyz(data, square=True)

        # Should be 3x3 matrix
        assert result.shape == (3, 3)
        assert set(result.index) == set(result.columns) == {"A", "B", "C"}
        assert result.loc["B", "A"] == 1
        assert result.loc["C", "B"] == 2
        assert result.loc["A", "C"] == 3
        assert result.loc["C", "A"] == 4


class TestDataTypes:
    """Test handling of different data types."""

    def test_numeric_labels(self):
        """Test with numeric x and y labels."""
        data = pd.DataFrame(
            {"x": [1, 2, 3, 1], "y": [10, 20, 30, 20], "z": [0.1, 0.2, 0.3, 0.4]}
        )
        result = from_xyz(data)

        assert result.loc[20, 1] == 0.4
        assert result.loc[20, 2] == 0.2
        assert result.loc[30, 3] == 0.3

    def test_mixed_types_labels(self):
        """Test with mixed type labels."""
        data = pd.DataFrame(
            {
                "x": [1, "B", 3.14, 1],
                "y": ["alpha", "beta", "gamma", "beta"],
                "z": [10, 20, 30, 40],
            }
        )
        result = from_xyz(data)

        assert result.loc["beta", 1] == 40
        assert result.loc["beta", "B"] == 20
        assert result.loc["gamma", 3.14] == 30

    def test_float_z_values(self):
        """Test with float z values."""
        data = pd.DataFrame(
            {"x": ["A", "B", "C"], "y": ["X", "Y", "Z"], "z": [1.5, 2.7, 3.9]}
        )
        result = from_xyz(data)

        assert result.loc["X", "A"] == 1.5
        assert result.loc["Y", "B"] == 2.7
        assert result.loc["Z", "C"] == 3.9

    def test_string_z_values(self):
        """Test with string z values."""
        data = pd.DataFrame({"x": ["A", "B"], "y": ["X", "Y"], "z": ["high", "low"]})
        result = from_xyz(data)

        assert result.loc["X", "A"] == "high"
        assert result.loc["Y", "B"] == "low"
        # Missing values should be 0, not '0'
        assert result.loc["X", "B"] == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        data = pd.DataFrame({"x": [], "y": [], "z": []})
        result = from_xyz(data)

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_single_row(self):
        """Test with single row."""
        data = pd.DataFrame({"x": ["A"], "y": ["X"], "z": [42]})
        result = from_xyz(data)

        assert result.shape == (1, 1)
        assert result.loc["X", "A"] == 42

    def test_missing_columns(self):
        """Test error when required columns are missing."""
        data = pd.DataFrame({"a": [1], "b": [2]})

        with pytest.raises(KeyError):
            from_xyz(data)  # Should fail looking for 'x', 'y', 'z'

    def test_nan_values(self):
        """Test handling of NaN values."""
        data = pd.DataFrame(
            {"x": ["A", "B", "C"], "y": ["X", "Y", "Z"], "z": [1, np.nan, 3]}
        )
        result = from_xyz(data)

        # NaN values are dropped by pivot_table, so row Y and column B don't exist
        assert result.shape == (2, 2)  # Only X,Z rows and A,C columns
        assert result.loc["X", "A"] == 1
        assert result.loc["Z", "C"] == 3
        # Check that Y row and B column don't exist
        assert "Y" not in result.index
        assert "B" not in result.columns

    def test_none_in_labels(self):
        """Test with None in x or y labels."""
        data = pd.DataFrame(
            {"x": ["A", None, "C"], "y": ["X", "Y", None], "z": [1, 2, 3]}
        )
        result = from_xyz(data)

        # None values are dropped by pivot_table
        assert result.shape == (1, 1)  # Only X,A remains
        assert result.loc["X", "A"] == 1
        # Check that rows/columns with None are excluded
        assert None not in result.index
        assert None not in result.columns
        assert "Y" not in result.index  # Row with None in x is dropped
        assert "C" not in result.columns  # Column with None in y is dropped


class TestAggregation:
    """Test aggregation behavior."""

    def test_first_aggregation(self):
        """Test that 'first' aggregation is used."""
        data = pd.DataFrame(
            {"x": ["A", "A", "A"], "y": ["X", "X", "X"], "z": [1, 2, 3]}
        )
        result = from_xyz(data)

        # Should take first value
        assert result.loc["X", "A"] == 1

    def test_multiple_duplicates(self):
        """Test with multiple duplicate x,y pairs."""
        data = pd.DataFrame(
            {
                "x": ["A", "B", "A", "B", "A"],
                "y": ["X", "Y", "X", "Y", "X"],
                "z": [1, 2, 3, 4, 5],
            }
        )
        result = from_xyz(data)

        assert result.loc["X", "A"] == 1  # First occurrence
        assert result.loc["Y", "B"] == 2  # First occurrence

    def test_order_preservation(self):
        """Test that order of first occurrence is preserved."""
        data = pd.DataFrame(
            {"x": ["C", "B", "A"], "y": ["Z", "Y", "X"], "z": [3, 2, 1]}
        )
        result = from_xyz(data)

        # Columns and index should be sorted
        assert list(result.columns) == ["A", "B", "C"]
        assert list(result.index) == ["X", "Y", "Z"]


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_statistical_pvalues_matrix(self):
        """Test creating p-value matrix from statistical tests."""
        data = pd.DataFrame(
            {
                "x": ["gene1", "gene2", "gene3", "gene1", "gene2"],
                "y": [
                    "condition1",
                    "condition1",
                    "condition1",
                    "condition2",
                    "condition2",
                ],
                "z": [0.01, 0.05, 0.001, 0.1, 0.02],
            }
        )
        result = from_xyz(data)

        assert result.shape == (2, 3)
        assert result.loc["condition1", "gene1"] == 0.01
        assert result.loc["condition1", "gene3"] == 0.001
        assert result.loc["condition2", "gene2"] == 0.02
        assert result.loc["condition2", "gene3"] == 0  # Missing combination

    def test_correlation_matrix_construction(self):
        """Test constructing correlation matrix."""
        # Upper triangle of correlation matrix
        data = pd.DataFrame(
            {
                "x": ["A", "A", "A", "B", "B", "C"],
                "y": ["A", "B", "C", "B", "C", "C"],
                "z": [1.0, 0.8, 0.6, 1.0, 0.7, 1.0],
            }
        )
        result = from_xyz(data, square=True)

        # Should create symmetric matrix
        assert result.shape == (3, 3)
        assert result.loc["A", "A"] == 1.0
        assert result.loc["B", "A"] == 0.8  # From A-B pair
        assert result.loc["C", "B"] == 0.7  # From B-C pair

    def test_contingency_table(self):
        """Test creating contingency table."""
        data = pd.DataFrame(
            {
                "x": ["Yes", "No", "Yes", "No", "Yes"],
                "y": ["Group1", "Group1", "Group2", "Group2", "Group1"],
                "z": [15, 10, 20, 5, 5],  # counts
            }
        )
        result = from_xyz(data)

        assert result.loc["Group1", "Yes"] == 15
        assert result.loc["Group1", "No"] == 10
        assert result.loc["Group2", "Yes"] == 20
        assert result.loc["Group2", "No"] == 5


class TestDocstringExample:
    """Test the example from the docstring."""

    def test_docstring_example(self):
        """Test the exact example from the docstring."""
        data = pd.DataFrame(
            {
                "col1": ["A", "B", "C", "A"],
                "col2": ["X", "Y", "Z", "Y"],
                "p_val": [0.01, 0.05, 0.001, 0.1],
            }
        )
        data = data.rename(columns={"col1": "x", "col2": "y", "p_val": "z"})
        result = from_xyz(data)

        assert result.loc["X", "A"] == 0.01
        assert result.loc["Y", "B"] == 0.05
        assert result.loc["Z", "C"] == 0.001
        assert result.loc["Y", "A"] == 0.1

        # Check filled values
        assert result.loc["X", "B"] == 0
        assert result.loc["X", "C"] == 0


class TestLargeDatasets:
    """Test with larger datasets."""

    def test_large_sparse_matrix(self):
        """Test with large sparse data."""
        # Create sparse data
        np.random.seed(42)
        n_points = 1000
        x_vals = np.random.choice(list("ABCDEFGHIJ"), n_points)
        y_vals = np.random.choice(list("KLMNOPQRST"), n_points)
        z_vals = np.random.rand(n_points)

        data = pd.DataFrame({"x": x_vals, "y": y_vals, "z": z_vals})
        result = from_xyz(data)

        assert result.shape == (10, 10)  # 10 unique x and y values
        assert (result >= 0).all().all()  # All values non-negative
        assert (result <= 1).all().all()  # All values <= 1 (including fills)

    def test_performance_with_categories(self):
        """Test performance with categorical data."""
        # Using categories can improve performance
        # Create data where all combinations exist
        x_vals = []
        y_vals = []
        z_vals = []
        for x in ["A", "B", "C"]:
            for y in ["X", "Y", "Z"]:
                x_vals.extend([x] * 100)
                y_vals.extend([y] * 100)
                z_vals.extend(np.random.rand(100))
        
        data = pd.DataFrame(
            {
                "x": pd.Categorical(x_vals),
                "y": pd.Categorical(y_vals),
                "z": z_vals,
            }
        )
        result = from_xyz(data)

        assert result.shape == (3, 3)
        # All positions should have values (due to all combinations being present)
        assert (result != 0).all().all()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_from_xyz.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-09-26 07:22:18 (ywatanabe)"
# # /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/pd/_from_xyz.py
# 
# import pandas as pd
# import numpy as np
# 
# 
# def from_xyz(data_frame, x=None, y=None, z=None, square=False):
#     """
#     Convert a DataFrame with 'x', 'y', 'z' format into a heatmap DataFrame.
# 
#     Example
#     -------
#     import pandas as pd
#     data = pd.DataFrame({
#         'col1': ['A', 'B', 'C', 'A'],
#         'col2': ['X', 'Y', 'Z', 'Y'],
#         'p_val': [0.01, 0.05, 0.001, 0.1]
#     })
#     data = data.rename(columns={"col1": "x", "col2": "y", "p_val": "z"})
#     result = from_xyz(data)
#     print(result)
# 
#     Parameters
#     ----------
#     data_frame : pandas.DataFrame
#         Input DataFrame with columns for x, y, and z values.
#     x : str, optional
#         Name of the column to use as x-axis. Defaults to 'x'.
#     y : str, optional
#         Name of the column to use as y-axis. Defaults to 'y'.
#     z : str, optional
#         Name of the column to use as z-values. Defaults to 'z'.
#     square : bool, optional
#         If True, force the output to be a square matrix. Defaults to False.
# 
#     Returns
#     -------
#     pandas.DataFrame
#         A DataFrame in heatmap/pivot format.
#     """
#     x = x or "x"
#     y = y or "y"
#     z = z or "z"
# 
#     heatmap = pd.pivot_table(data_frame, values=z, index=y, columns=x, aggfunc="first")
# 
#     if square:
#         # Make it square by including all unique labels
#         all_labels = sorted(set(heatmap.index) | set(heatmap.columns))
#         heatmap = heatmap.reindex(index=all_labels, columns=all_labels)
# 
#     heatmap = heatmap.fillna(0)
# 
#     return heatmap
# 
# 
# if __name__ == "__main__":
#     np.random.seed(42)
#     stats = pd.DataFrame(
#         {
#             "col1": np.random.choice(["A", "B", "C"], 100),
#             "col2": np.random.choice(["X", "Y", "Z"], 100),
#             "p_val": np.random.rand(100),
#         }
#     )
#     stats = stats.rename(columns={"col1": "x", "col2": "y", "p_val": "z"})
#     result = from_xyz(stats)
#     print(result)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_from_xyz.py
# --------------------------------------------------------------------------------
