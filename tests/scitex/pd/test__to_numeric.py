#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:00:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__to_numeric.py

"""
Test module for scitex.pd.to_numeric function.
"""

import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal, assert_series_equal


class TestToNumeric:
    """Test class for to_numeric function."""

    @pytest.fixture
    def mixed_df(self):
        """Create a DataFrame with mixed types."""
        return pd.DataFrame(
            {
                "int_str": ["1", "2", "3", "4"],
                "float_str": ["1.5", "2.5", "3.5", "4.5"],
                "mixed": ["1", "2.5", "three", "4"],
                "pure_str": ["a", "b", "c", "d"],
                "already_int": [1, 2, 3, 4],
                "already_float": [1.1, 2.2, 3.3, 4.4],
                "with_nan": ["1", "2", np.nan, "4"],
            }
        )

    @pytest.fixture
    def datetime_df(self):
        """Create a DataFrame with datetime strings."""
        return pd.DataFrame(
            {
                "dates": ["2021-01-01", "2021-01-02", "2021-01-03"],
                "times": ["10:30:00", "11:45:00", "12:00:00"],
                "numbers": ["100", "200", "300"],
            }
        )

    def test_import(self):
        """Test that to_numeric can be imported."""
        from scitex.pd import to_numeric

        assert callable(to_numeric)

    def test_basic_conversion(self, mixed_df):
        """Test basic numeric conversion with coerce."""
        from scitex.pd import to_numeric

        result = to_numeric(mixed_df)

        # Check conversions
        assert result["int_str"].dtype in [np.int64, np.float64]
        assert result["float_str"].dtype == np.float64
        assert result["already_int"].dtype in [np.int64, np.float64]
        assert result["already_float"].dtype == np.float64

        # Check values
        assert list(result["int_str"]) == [1, 2, 3, 4]
        assert list(result["float_str"]) == [1.5, 2.5, 3.5, 4.5]

    def test_coerce_mode(self, mixed_df):
        """Test coerce mode converts invalid values to NaN."""
        from scitex.pd import to_numeric

        result = to_numeric(mixed_df, errors="coerce")

        # Mixed column should have NaN for 'three'
        assert pd.isna(result["mixed"].iloc[2])
        assert result["mixed"].iloc[0] == 1
        assert result["mixed"].iloc[1] == 2.5
        assert result["mixed"].iloc[3] == 4

        # Pure string column should be all NaN
        assert result["pure_str"].isna().all()

    def test_ignore_mode(self, mixed_df):
        """Test ignore mode leaves non-numeric columns unchanged."""
        from scitex.pd import to_numeric

        result = to_numeric(mixed_df, errors="ignore")

        # Numeric strings should be converted
        assert result["int_str"].dtype in [np.int64, np.float64]
        assert result["float_str"].dtype == np.float64

        # Pure string column should remain unchanged
        assert result["pure_str"].dtype == object
        assert list(result["pure_str"]) == ["a", "b", "c", "d"]

        # Mixed column should remain unchanged (has non-numeric values)
        assert result["mixed"].dtype == object
        assert list(result["mixed"]) == ["1", "2.5", "three", "4"]

    def test_raise_mode(self):
        """Test raise mode raises exception on invalid conversion."""
        from scitex.pd import to_numeric

        df = pd.DataFrame({"valid": ["1", "2", "3"], "invalid": ["1", "two", "3"]})

        # Should raise ValueError for invalid column
        with pytest.raises(ValueError):
            to_numeric(df, errors="raise")

    def test_with_nan_values(self, mixed_df):
        """Test handling of NaN values."""
        from scitex.pd import to_numeric

        result = to_numeric(mixed_df)

        # with_nan column should preserve NaN
        assert pd.isna(result["with_nan"].iloc[2])
        assert result["with_nan"].iloc[0] == 1
        assert result["with_nan"].iloc[1] == 2
        assert result["with_nan"].iloc[3] == 4

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        from scitex.pd import to_numeric

        df = pd.DataFrame()
        result = to_numeric(df)
        assert result.empty

        # Empty with columns
        df = pd.DataFrame(columns=["A", "B"])
        result = to_numeric(df)
        assert list(result.columns) == ["A", "B"]
        assert result.empty

    def test_single_column_dataframe(self):
        """Test with single column DataFrame."""
        from scitex.pd import to_numeric

        df = pd.DataFrame({"A": ["1", "2", "3"]})
        result = to_numeric(df)
        assert result["A"].dtype in [np.int64, np.float64]
        assert list(result["A"]) == [1, 2, 3]

    def test_scientific_notation(self):
        """Test conversion of scientific notation strings."""
        from scitex.pd import to_numeric

        df = pd.DataFrame(
            {"sci": ["1e3", "2.5e-2", "3E+4"], "normal": ["1000", "0.025", "30000"]}
        )

        result = to_numeric(df)
        assert result["sci"].iloc[0] == 1000
        assert result["sci"].iloc[1] == 0.025
        assert result["sci"].iloc[2] == 30000

    def test_boolean_strings(self):
        """Test conversion of boolean-like strings."""
        from scitex.pd import to_numeric

        df = pd.DataFrame(
            {"bool_str": ["True", "False", "True"], "bool_num": ["1", "0", "1"]}
        )

        result = to_numeric(df, errors="coerce")
        # 'True'/'False' strings should become NaN with coerce
        assert result["bool_str"].isna().all()
        # '1'/'0' should convert to numbers
        assert list(result["bool_num"]) == [1, 0, 1]

    def test_preserve_dtypes_when_possible(self):
        """Test that already numeric columns preserve their dtypes."""
        from scitex.pd import to_numeric

        df = pd.DataFrame(
            {
                "int32": pd.array([1, 2, 3], dtype="int32"),
                "float32": pd.array([1.1, 2.2, 3.3], dtype="float32"),
                "int64": pd.array([1, 2, 3], dtype="int64"),
                "float64": pd.array([1.1, 2.2, 3.3], dtype="float64"),
            }
        )

        result = to_numeric(df)
        # Types might be promoted but should remain numeric
        for col in df.columns:
            assert pd.api.types.is_numeric_dtype(result[col])

    def test_whitespace_handling(self):
        """Test handling of whitespace in numeric strings."""
        from scitex.pd import to_numeric

        df = pd.DataFrame(
            {
                "with_spaces": ["  1  ", " 2.5 ", "3", "  4.0"],
                "with_tabs": ["\t1\t", "2\t", "\t3", "4\t\t"],
            }
        )

        result = to_numeric(df)
        assert list(result["with_spaces"]) == [1, 2.5, 3, 4.0]
        assert list(result["with_tabs"]) == [1, 2, 3, 4]

    def test_currency_symbols(self):
        """Test handling of currency symbols."""
        from scitex.pd import to_numeric

        df = pd.DataFrame(
            {
                "dollars": ["$100", "$200.50", "$300"],
                "pounds": ["£100", "£200.50", "£300"],
            }
        )

        # Currency symbols should result in NaN with coerce
        result = to_numeric(df, errors="coerce")
        assert result["dollars"].isna().all()
        assert result["pounds"].isna().all()

    def test_percentage_strings(self):
        """Test handling of percentage strings."""
        from scitex.pd import to_numeric

        df = pd.DataFrame(
            {"percent": ["10%", "20.5%", "30%"], "decimal": ["0.1", "0.205", "0.3"]}
        )

        result = to_numeric(df, errors="coerce")
        # Percentage strings should become NaN
        assert result["percent"].isna().all()
        # Decimal strings should convert
        assert list(result["decimal"]) == [0.1, 0.205, 0.3]

    def test_copy_behavior(self, mixed_df):
        """Test that the function returns a copy, not modifying the original."""
        from scitex.pd import to_numeric

        original_values = mixed_df["int_str"].copy()
        result = to_numeric(mixed_df)

        # Original should be unchanged
        assert mixed_df["int_str"].dtype == object
        assert_series_equal(mixed_df["int_str"], original_values)

        # Result should be numeric
        assert result["int_str"].dtype in [np.int64, np.float64]

    @pytest.mark.parametrize("errors", ["coerce", "ignore"])
    def test_consistent_behavior(self, errors):
        """Test consistent behavior across different error modes."""
        from scitex.pd import to_numeric

        df = pd.DataFrame({"nums": ["1", "2", "3"], "mixed": ["1", "a", "3"]})

        result = to_numeric(df, errors=errors)
        # Nums column should always be converted
        assert pd.api.types.is_numeric_dtype(result["nums"])


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/_to_numeric.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-08 04:35:31 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/pd/_to_numeric.py
#
# import pandas as pd
#
#
# def to_numeric(df):
#     """Convert all possible columns in a DataFrame to numeric types.
#
#     Parameters
#     ----------
#     df : pd.DataFrame
#         Input DataFrame
#
#     Returns
#     -------
#     pd.DataFrame
#         DataFrame with numeric columns converted
#     """
#     for col in df.columns:
#         try:
#             df[col] = pd.to_numeric(df[col])
#         except (ValueError, TypeError):
#             continue
#     return df
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/_to_numeric.py
# --------------------------------------------------------------------------------
