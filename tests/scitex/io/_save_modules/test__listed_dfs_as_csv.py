#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01"
# File: test__save_listed_dfs_as_csv.py

"""Tests for the _save_listed_dfs_as_csv function in scitex.io module."""

import csv
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import numpy as np
import pandas as pd
import pytest


class TestSaveListedDfsBasic:
    """Test basic functionality of saving listed DataFrames."""

    def test_save_single_dataframe(self, tmp_path):
        """Test saving a single DataFrame in a list."""
        from scitex.io import _save_listed_dfs_as_csv

        # Create test DataFrame
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})

        output_file = tmp_path / "single_df.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        # Check file was created
        assert output_file.exists()

        # Read and verify content
        with open(output_file, "r") as f:
            content = f.read()
            assert "0" in content  # Default suffix
            assert "A,B" in content  # Headers
            assert "1,a" in content  # Data

    def test_save_multiple_dataframes(self, tmp_path):
        """Test saving multiple DataFrames."""
        from scitex.io import _save_listed_dfs_as_csv

        # Create test DataFrames
        df1 = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
        df2 = pd.DataFrame({"P": [5, 6], "Q": [7, 8]})
        df3 = pd.DataFrame({"M": [9], "N": [10]})

        output_file = tmp_path / "multiple_dfs.csv"

        _save_listed_dfs_as_csv([df1, df2, df3], str(output_file))

        # Read and check structure
        with open(output_file, "r") as f:
            content = f.read()

            # Check all DataFrames are present with separators
            assert "0" in content  # First suffix
            assert "1" in content  # Second suffix
            assert "2" in content  # Third suffix
            assert "X,Y" in content
            assert "P,Q" in content
            assert "M,N" in content

    def test_custom_suffixes(self, tmp_path):
        """Test saving with custom suffixes."""
        from scitex.io import _save_listed_dfs_as_csv

        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = pd.DataFrame({"B": [3, 4]})

        output_file = tmp_path / "custom_suffix.csv"
        suffixes = ["experiment_1", "experiment_2"]

        _save_listed_dfs_as_csv([df1, df2], str(output_file), indi_suffix=suffixes)

        with open(output_file, "r") as f:
            content = f.read()
            assert "experiment_1" in content
            assert "experiment_2" in content


class TestSaveListedDfsOptions:
    """Test various options for saving DataFrames."""

    def test_overwrite_true(self, tmp_path):
        """Test overwrite=True moves existing file."""
        from scitex.io import _save_listed_dfs_as_csv

        output_file = tmp_path / "overwrite_test.csv"

        # Create existing file
        output_file.write_text("existing content")

        df = pd.DataFrame({"A": [1, 2]})

        with patch("scitex.io._save_listed_dfs_as_csv._mv_to_tmp") as mock_mv:
            _save_listed_dfs_as_csv([df], str(output_file), overwrite=True)

            # Should call mv_to_tmp
            mock_mv.assert_called_once_with(str(output_file), L=2)

    def test_verbose_output(self, tmp_path, capsys):
        """Test verbose output."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame({"A": [1]})
        output_file = tmp_path / "verbose_test.csv"

        _save_listed_dfs_as_csv([df], str(output_file), verbose=True)

        captured = capsys.readouterr()
        assert f"Saved to: {output_file}" in captured.out

    def test_append_mode(self, tmp_path):
        """Test that function appends to existing file."""
        from scitex.io import _save_listed_dfs_as_csv

        output_file = tmp_path / "append_test.csv"

        # First save
        df1 = pd.DataFrame({"A": [1, 2]})
        _save_listed_dfs_as_csv([df1], str(output_file))

        # Second save without overwrite
        df2 = pd.DataFrame({"B": [3, 4]})
        _save_listed_dfs_as_csv([df2], str(output_file), overwrite=False)

        # Both should be in file
        with open(output_file, "r") as f:
            content = f.read()
            assert "A" in content  # From first save
            assert "B" in content  # From second save


class TestSaveListedDfsDataTypes:
    """Test saving different types of DataFrames."""

    def test_empty_dataframe(self, tmp_path):
        """Test saving empty DataFrame."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame()
        output_file = tmp_path / "empty_df.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        assert output_file.exists()
        # Should still have suffix row
        with open(output_file, "r") as f:
            content = f.read()
            assert "0" in content

    def test_mixed_dtypes(self, tmp_path):
        """Test DataFrames with mixed data types."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "str_col": ["a", "b", "c"],
                "bool_col": [True, False, True],
                "datetime_col": pd.date_range("2024-01-01", periods=3),
            }
        )

        output_file = tmp_path / "mixed_types.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        # Verify all columns are saved
        content = pd.read_csv(output_file, skiprows=1)  # Skip suffix row
        assert len(content.columns) == 6  # Including index

    def test_dataframe_with_nan(self, tmp_path):
        """Test DataFrame containing NaN values."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame({"A": [1, np.nan, 3], "B": ["x", "y", None]})

        output_file = tmp_path / "nan_df.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        assert output_file.exists()
        # CSV should handle NaN/None appropriately

    def test_dataframe_with_multiindex(self, tmp_path):
        """Test DataFrame with MultiIndex."""
        from scitex.io import _save_listed_dfs_as_csv

        # Create MultiIndex DataFrame
        arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
        index = pd.MultiIndex.from_arrays(arrays, names=["letter", "number"])
        df = pd.DataFrame({"value": [10, 20, 30, 40]}, index=index)

        output_file = tmp_path / "multiindex_df.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        assert output_file.exists()
        # MultiIndex should be preserved in CSV format


class TestSaveListedDfsFormatting:
    """Test CSV formatting details."""

    def test_separator_rows(self, tmp_path):
        """Test that empty separator rows are added between DataFrames."""
        from scitex.io import _save_listed_dfs_as_csv

        df1 = pd.DataFrame({"A": [1]})
        df2 = pd.DataFrame({"B": [2]})

        output_file = tmp_path / "separator_test.csv"

        _save_listed_dfs_as_csv([df1, df2], str(output_file))

        with open(output_file, "r") as f:
            lines = f.readlines()

        # Should have empty lines between DataFrames
        empty_lines = [i for i, line in enumerate(lines) if line.strip() == ""]
        assert len(empty_lines) >= 2  # At least one after each DataFrame

    def test_index_preserved(self, tmp_path):
        """Test that DataFrame index is preserved."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame({"A": [1, 2, 3]}, index=["row1", "row2", "row3"])
        df.index.name = "custom_index"

        output_file = tmp_path / "index_test.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        with open(output_file, "r") as f:
            content = f.read()
            assert "custom_index" in content
            assert "row1" in content

    def test_headers_preserved(self, tmp_path):
        """Test that column headers are preserved."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame({"Column One": [1, 2], "Column Two": [3, 4]})

        output_file = tmp_path / "header_test.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        with open(output_file, "r") as f:
            content = f.read()
            assert "Column One" in content
            assert "Column Two" in content


class TestSaveListedDfsErrorHandling:
    """Test error handling scenarios."""

    def test_empty_list(self, tmp_path):
        """Test saving empty list of DataFrames."""
        from scitex.io import _save_listed_dfs_as_csv

        output_file = tmp_path / "empty_list.csv"

        _save_listed_dfs_as_csv([], str(output_file))

        # Should handle gracefully, file may or may not exist

    def test_non_dataframe_in_list(self, tmp_path):
        """Test behavior with non-DataFrame objects."""
        from scitex.io import _save_listed_dfs_as_csv

        output_file = tmp_path / "non_df.csv"

        # Mix DataFrame with non-DataFrame
        df = pd.DataFrame({"A": [1, 2]})
        not_df = {"A": [1, 2]}  # Dict, not DataFrame

        # This might raise AttributeError
        with pytest.raises(AttributeError):
            _save_listed_dfs_as_csv([df, not_df], str(output_file))

    def test_mismatched_suffix_length(self, tmp_path):
        """Test when suffix list length doesn't match DataFrame list."""
        from scitex.io import _save_listed_dfs_as_csv

        df1 = pd.DataFrame({"A": [1]})
        df2 = pd.DataFrame({"B": [2]})

        output_file = tmp_path / "mismatch_suffix.csv"

        # Too few suffixes
        with pytest.raises(IndexError):
            _save_listed_dfs_as_csv(
                [df1, df2], str(output_file), indi_suffix=["only_one"]
            )

    def test_permission_error(self, tmp_path):
        """Test handling permission errors."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame({"A": [1]})

        # Try to write to protected location
        output_file = "/root/protected.csv"

        with pytest.raises(PermissionError):
            _save_listed_dfs_as_csv([df], output_file)


class TestSaveListedDfsIntegration:
    """Test integration scenarios."""

    def test_large_dataframe_list(self, tmp_path):
        """Test saving many DataFrames."""
        from scitex.io import _save_listed_dfs_as_csv

        # Create 10 DataFrames
        dfs = []
        for i in range(10):
            df = pd.DataFrame({f"col_{i}": np.random.rand(5)})
            dfs.append(df)

        output_file = tmp_path / "many_dfs.csv"

        _save_listed_dfs_as_csv(dfs, str(output_file))

        assert output_file.exists()

        # Check all DataFrames are present
        with open(output_file, "r") as f:
            content = f.read()
            for i in range(10):
                assert str(i) in content  # Suffixes
                assert f"col_{i}" in content  # Column names

    def test_round_trip(self, tmp_path):
        """Test that data can be recovered from saved file."""
        from scitex.io import _save_listed_dfs_as_csv

        # Create test data
        df1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df2 = pd.DataFrame({"X": [7, 8], "Y": [9, 10]})

        output_file = tmp_path / "round_trip.csv"

        _save_listed_dfs_as_csv(
            [df1, df2], str(output_file), indi_suffix=["first", "second"]
        )

        # Manually parse the file to recover data
        with open(output_file, "r") as f:
            lines = f.readlines()

        # Find suffix markers
        suffix_lines = []
        for i, line in enumerate(lines):
            if line.strip() in ["first", "second"]:
                suffix_lines.append(i)

        assert len(suffix_lines) == 2

    def test_unicode_content(self, tmp_path):
        """Test saving DataFrames with Unicode content."""
        from scitex.io import _save_listed_dfs_as_csv

        df = pd.DataFrame(
            {
                "language": ["English", "日本語", "Français", "中文"],
                "greeting": ["Hello", "こんにちは", "Bonjour", "你好"],
            }
        )

        output_file = tmp_path / "unicode_content.csv"

        _save_listed_dfs_as_csv([df], str(output_file))

        # Check Unicode is preserved
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "日本語" in content
            assert "こんにちは" in content


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 21:28:56 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_save_listed_dfs_as_csv.py
#
# import csv
# import numpy as np
# from ._mv_to_tmp import _mv_to_tmp
#
# def _save_listed_dfs_as_csv(
#     listed_dfs,
#     spath_csv,
#     indi_suffix=None,
#     overwrite=False,
#     verbose=False,
# ):
#     """listed_dfs:
#         [df1, df2, df3, ..., dfN]. They will be written vertically in the order.
#
#     spath_csv:
#         /hoge/fuga/foo.csv
#
#     indi_suffix:
#         At the left top cell on the output csv file, '{}'.format(indi_suffix[i])
#         will be added, where i is the index of the df.On the other hand,
#         when indi_suffix=None is passed, only '{}'.format(i) will be added.
#     """
#
#     if overwrite == True:
#         _mv_to_tmp(spath_csv, L=2)
#
#     indi_suffix = (
#         np.arange(len(listed_dfs)) if indi_suffix is None else indi_suffix
#     )
#     for i, df in enumerate(listed_dfs):
#         with open(spath_csv, mode="a") as f:
#             f_writer = csv.writer(f)
#             i_suffix = indi_suffix[i]
#             f_writer.writerow(["{}".format(indi_suffix[i])])
#         df.to_csv(spath_csv, mode="a", index=True, header=True)
#         with open(spath_csv, mode="a") as f:
#             f_writer = csv.writer(f)
#             f_writer.writerow([""])
#     if verbose:
#         print("Saved to: {}".format(spath_csv))
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_listed_dfs_as_csv.py
# --------------------------------------------------------------------------------
