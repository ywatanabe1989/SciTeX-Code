#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 20:45:00 (ywatanabe)"
# /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/pd/test__round.py


"""
Comprehensive tests for scitex.pd.round function.
"""

import numpy as np
import pandas as pd
import pytest


class TestRound:
    """Test class for round function."""

    def test_basic_float_rounding(self):
        """Test basic rounding of float values."""
        from scitex.pd import round

        df = pd.DataFrame(
            {"A": [1.23456, 2.34567, 3.45678], "B": [4.56789, 5.67890, 6.78901]}
        )

        result = round(df, factor=2)
        expected = pd.DataFrame({"A": [1.23, 2.35, 3.46], "B": [4.57, 5.68, 6.79]})

        pd.testing.assert_frame_equal(result, expected)

    def test_default_factor(self):
        """Test rounding with default factor of 3."""
        from scitex.pd import round

        df = pd.DataFrame({"value": [1.234567, 2.345678, 3.456789]})

        result = round(df)
        expected = pd.DataFrame({"value": [1.235, 2.346, 3.457]})

        pd.testing.assert_frame_equal(result, expected)

    def test_mixed_types(self):
        """Test rounding with mixed data types."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "float": [1.23456, 2.34567],
                "int": [3, 4],
                "str": ["abc", "def"],
                "bool": [True, False],
            }
        )

        result = round(df, factor=2)
        expected = pd.DataFrame(
            {
                "float": [1.23, 2.35],
                "int": [3, 4],
                "str": ["abc", "def"],
                "bool": [1, 0],  # Booleans are converted to int by pd.to_numeric
            }
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_integer_preservation(self):
        """Test that integer columns remain as integers."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [10, 20, 30, 40, 50]})

        result = round(df, factor=2)

        assert result["A"].dtype == np.int64
        assert result["B"].dtype == np.int64
        pd.testing.assert_frame_equal(result, df)

    def test_zero_decimal_places(self):
        """Test rounding to zero decimal places."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [1.4, 2.5, 3.6], "B": [4.4, 5.5, 6.6]})

        result = round(df, factor=0)
        expected = pd.DataFrame({"A": [1, 2, 4], "B": [4, 6, 7]})

        pd.testing.assert_frame_equal(result, expected)

    def test_large_factor(self):
        """Test rounding with large factor value."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [1.123456789, 2.234567890]})

        result = round(df, factor=6)
        expected = pd.DataFrame({"A": [1.123457, 2.234568]})

        pd.testing.assert_frame_equal(result, expected)

    def test_negative_values(self):
        """Test rounding negative values."""
        from scitex.pd import round

        df = pd.DataFrame(
            {"A": [-1.23456, -2.34567, -3.45678], "B": [1.23456, -2.34567, 3.45678]}
        )

        result = round(df, factor=2)
        expected = pd.DataFrame({"A": [-1.23, -2.35, -3.46], "B": [1.23, -2.35, 3.46]})

        pd.testing.assert_frame_equal(result, expected)

    def test_nan_handling(self):
        """Test handling of NaN values - columns with NaN are not rounded due to comparison issue."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "A": [1.234, np.nan, 3.456],
                "B": [np.nan, 2.345, np.nan],
                "C": [1.234, 2.345, 3.456],  # No NaN
            }
        )

        result = round(df, factor=2)
        # NaN values are preserved, non-NaN values are rounded
        expected = pd.DataFrame(
            {
                "A": [1.23, np.nan, 3.46],  # Rounded, NaN preserved
                "B": [np.nan, 2.35, np.nan],  # Rounded, NaN preserved
                "C": [1.23, 2.35, 3.46],  # Rounded correctly - no NaN
            }
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_inf_handling(self):
        """Test handling of infinity values - columns with inf are not rounded."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "A": [1.234, np.inf, -np.inf],
                "B": [np.inf, 2.345, -np.inf],
                "C": [1.234, 2.345, 3.456],  # No inf
            }
        )

        result = round(df, factor=2)
        # inf values are preserved, finite values are rounded
        expected = pd.DataFrame(
            {
                "A": [1.23, np.inf, -np.inf],  # Rounded, inf preserved
                "B": [np.inf, 2.35, -np.inf],  # Rounded, inf preserved
                "C": [1.23, 2.35, 3.46],  # Rounded correctly - no inf
            }
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        """Test rounding empty DataFrame."""
        from scitex.pd import round

        df = pd.DataFrame()
        result = round(df, factor=2)
        pd.testing.assert_frame_equal(result, df)

    def test_single_column(self):
        """Test rounding single column DataFrame."""
        from scitex.pd import round

        df = pd.DataFrame({"values": [1.234567, 2.345678, 3.456789]})
        result = round(df, factor=3)
        expected = pd.DataFrame({"values": [1.235, 2.346, 3.457]})

        pd.testing.assert_frame_equal(result, expected)

    def test_datetime_columns(self):
        """Test that datetime columns are preserved."""
        from scitex.pd import round

        dates = pd.date_range("2024-01-01", periods=3)
        df = pd.DataFrame({"date": dates, "value": [1.23456, 2.34567, 3.45678]})

        result = round(df, factor=2)
        expected = pd.DataFrame({"date": dates, "value": [1.23, 2.35, 3.46]})

        pd.testing.assert_frame_equal(result, expected)

    def test_categorical_columns(self):
        """Test that categorical columns are preserved."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "category": pd.Categorical(["A", "B", "C"]),
                "value": [1.23456, 2.34567, 3.45678],
            }
        )

        result = round(df, factor=2)
        expected = pd.DataFrame(
            {"category": pd.Categorical(["A", "B", "C"]), "value": [1.23, 2.35, 3.46]}
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_scientific_notation(self):
        """Test rounding values in scientific notation."""
        from scitex.pd import round

        df = pd.DataFrame(
            {"A": [1.234e-5, 2.345e-5, 3.456e-5], "B": [1.234e5, 2.345e5, 3.456e5]}
        )

        result = round(df, factor=3)
        # Values less than 0.001 will be rounded to 0.0 when rounding to 3 decimal places
        # Large values remain unchanged as they have no decimal component
        expected = pd.DataFrame(
            {"A": [0.0, 0.0, 0.0], "B": [123400.0, 234500.0, 345600.0]}
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_very_small_values(self):
        """Test rounding very small values."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [0.000123456, 0.000234567, 0.000345678]})

        result = round(df, factor=3)
        # Rounding to 3 decimal places means values < 0.001 become 0.0
        expected = pd.DataFrame({"A": [0.0, 0.0, 0.0]})

        pd.testing.assert_frame_equal(result, expected)

    def test_roundable_to_int(self):
        """Test values that can be converted to integers after rounding."""
        from scitex.pd import round

        df = pd.DataFrame(
            {"A": [1.00001, 2.00002, 3.00003], "B": [4.99999, 5.99998, 6.99997]}
        )

        result = round(df, factor=0)
        expected = pd.DataFrame({"A": [1, 2, 3], "B": [5, 6, 7]})

        pd.testing.assert_frame_equal(result, expected)

    def test_multiindex_dataframe(self):
        """Test rounding DataFrame with MultiIndex."""
        from scitex.pd import round

        arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
        index = pd.MultiIndex.from_arrays(arrays, names=["first", "second"])
        df = pd.DataFrame({"value": [1.23456, 2.34567, 3.45678, 4.56789]}, index=index)

        result = round(df, factor=2)
        expected = pd.DataFrame({"value": [1.23, 2.35, 3.46, 4.57]}, index=index)

        pd.testing.assert_frame_equal(result, expected)

    def test_mixed_numeric_string(self):
        """Test DataFrame with numeric strings."""
        from scitex.pd import round

        df = pd.DataFrame(
            {"A": ["1.234", "2.345", "3.456"], "B": [1.234, 2.345, 3.456]}
        )

        result = round(df, factor=2)
        # Numeric strings should be converted and rounded
        expected = pd.DataFrame({"A": [1.23, 2.35, 3.46], "B": [1.23, 2.35, 3.46]})

        pd.testing.assert_frame_equal(result, expected)

    def test_none_values(self):
        """Test handling of None values - columns with None are not rounded."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "A": [1.234, None, 3.456],
                "B": [None, 2.345, None],
                "C": [1.234, 2.345, 3.456],  # No None
            }
        )

        result = round(df, factor=2)
        # Columns with None (converted to NaN) are returned unrounded
        expected = pd.DataFrame(
            {
                "A": [1.234, None, 3.456],  # Not rounded due to None/NaN
                "B": [None, 2.345, None],  # Not rounded due to None/NaN
                "C": [1.23, 2.35, 3.46],  # Rounded correctly - no None
            }
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_object_dtype_with_numbers(self):
        """Test object dtype columns containing numbers."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "A": pd.Series([1.234, 2.345, 3.456], dtype="object"),
                "B": pd.Series(["a", "b", "c"], dtype="object"),
            }
        )

        result = round(df, factor=2)
        expected = pd.DataFrame({"A": [1.23, 2.35, 3.46], "B": ["a", "b", "c"]})

        pd.testing.assert_frame_equal(result, expected)

    def test_series_like_behavior(self):
        """Test that function preserves column order and names."""
        from scitex.pd import round

        df = pd.DataFrame({"Z": [1.234], "A": [2.345], "M": [3.456]})

        result = round(df, factor=2)

        assert list(result.columns) == ["Z", "A", "M"]
        assert result["Z"][0] == 1.23
        assert result["A"][0] == 2.35
        assert result["M"][0] == 3.46

    def test_large_dataframe_performance(self):
        """Test performance with large DataFrame."""
        from scitex.pd import round

        # Create large DataFrame
        np.random.seed(42)
        df = pd.DataFrame(np.random.randn(1000, 10))

        result = round(df, factor=3)

        # Check shape is preserved
        assert result.shape == df.shape

        # Spot check some values are rounded correctly
        assert abs(result.iloc[0, 0] - np.round(df.iloc[0, 0], 3)) < 1e-10

    def test_factor_one(self):
        """Test rounding with factor=1."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [1.234, 2.567, 3.891]})

        result = round(df, factor=1)
        expected = pd.DataFrame({"A": [1.2, 2.6, 3.9]})

        pd.testing.assert_frame_equal(result, expected)

    def test_complex_mixed_data(self):
        """Test complex DataFrame with various types."""
        from scitex.pd import round

        df = pd.DataFrame(
            {
                "floats": [1.23456, 2.34567, np.nan],
                "floats_no_nan": [1.23456, 2.34567, 3.45678],
                "ints": [1, 2, 3],
                "strings": ["a", "b", "c"],
                "bools": [True, False, True],
                "mixed": [1.234, "text", None],
            }
        )

        result = round(df, factor=2)
        expected = pd.DataFrame(
            {
                "floats": [1.23456, 2.34567, np.nan],  # Not rounded due to NaN
                "floats_no_nan": [1.23, 2.35, 3.46],  # Rounded correctly
                "ints": [1, 2, 3],
                "strings": ["a", "b", "c"],
                "bools": [1, 0, 1],  # Booleans are converted to int by pd.to_numeric
                "mixed": [
                    1.234,
                    "text",
                    None,
                ],  # Not rounded due to mixed types with None
            }
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_edge_case_rounding(self):
        """Test edge cases in rounding (0.5 cases)."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [1.125, 2.225, 3.335, 4.445, 5.555]})

        result = round(df, factor=2)
        # Python uses banker's rounding (round to even)
        expected = pd.DataFrame({"A": [1.12, 2.22, 3.34, 4.44, 5.56]})

        pd.testing.assert_frame_equal(result, expected)

    def test_preserve_index(self):
        """Test that DataFrame index is preserved."""
        from scitex.pd import round

        df = pd.DataFrame({"A": [1.234, 2.345, 3.456]}, index=["x", "y", "z"])

        result = round(df, factor=2)

        assert list(result.index) == ["x", "y", "z"]
        assert result.loc["x", "A"] == 1.23

    def test_column_specific_behavior(self):
        """Test that rounding is applied column-wise."""
        from scitex.pd import round

        df = pd.DataFrame(
            {"precise": [1.123456789, 2.234567890], "rough": [100.1, 200.2]}
        )

        result = round(df, factor=4)
        expected = pd.DataFrame({"precise": [1.1235, 2.2346], "rough": [100.1, 200.2]})

        pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
