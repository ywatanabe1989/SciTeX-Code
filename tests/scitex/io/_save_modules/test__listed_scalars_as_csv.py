#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01"
# File: test__save_listed_scalars_as_csv.py

"""Tests for the _save_listed_scalars_as_csv function in scitex.io module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import numpy as np
import pandas as pd
import pytest


class TestSaveListedScalarsBasic:
    """Test basic functionality of saving listed scalars."""

    def test_save_simple_scalars(self, tmp_path):
        """Test saving a simple list of scalars."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.234, 2.345, 3.456, 4.567]
        output_file = tmp_path / "scalars.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        # Check file exists
        assert output_file.exists()

        # Load and verify
        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 4
        assert df.columns[0] == "_"  # Default column name

        # Check values are rounded to 3 decimal places by default
        assert df.iloc[0, 0] == 1.234
        assert df.iloc[1, 0] == 2.345

    def test_custom_column_name(self, tmp_path):
        """Test saving with custom column name."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [10, 20, 30]
        output_file = tmp_path / "custom_col.csv"

        _save_listed_scalars_as_csv(
            scalars, str(output_file), column_name="measurements"
        )

        df = pd.read_csv(output_file, index_col=0)
        assert df.columns[0] == "measurements"

    def test_custom_index(self, tmp_path):
        """Test saving with custom index."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.1, 2.2, 3.3]
        indices = ["exp1", "exp2", "exp3"]
        output_file = tmp_path / "custom_index.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file), indi_suffix=indices)

        df = pd.read_csv(output_file, index_col=0)
        assert list(df.index) == indices


class TestSaveListedScalarsRounding:
    """Test rounding functionality."""

    def test_default_rounding(self, tmp_path):
        """Test default rounding to 3 decimal places."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.23456789, 2.34567890, 3.45678901]
        output_file = tmp_path / "rounding_default.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        # Should be rounded to 3 decimal places
        assert df.iloc[0, 0] == 1.235
        assert df.iloc[1, 0] == 2.346
        assert df.iloc[2, 0] == 3.457

    def test_custom_rounding(self, tmp_path):
        """Test custom rounding."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.23456789, 2.34567890]

        # Test different rounding values
        for round_val in [0, 1, 2, 5]:
            output_file = tmp_path / f"round_{round_val}.csv"
            _save_listed_scalars_as_csv(scalars, str(output_file), round=round_val)

            df = pd.read_csv(output_file, index_col=0)

            if round_val == 0:
                assert df.iloc[0, 0] == 1.0
            elif round_val == 1:
                assert df.iloc[0, 0] == 1.2
            elif round_val == 2:
                assert df.iloc[0, 0] == 1.23
            elif round_val == 5:
                assert df.iloc[0, 0] == 1.23457

    def test_no_rounding_integers(self, tmp_path):
        """Test that integers are preserved."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1, 2, 3, 4, 5]
        output_file = tmp_path / "integers.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        # Integers should remain as floats but with .0
        assert all(df.iloc[:, 0] == scalars)


class TestSaveListedScalarsOptions:
    """Test various options."""

    def test_overwrite_true(self, tmp_path):
        """Test overwrite=True moves existing file."""
from scitex.io import _save_listed_scalars_as_csv

        output_file = tmp_path / "overwrite.csv"
        output_file.write_text("existing data")

        scalars = [1, 2, 3]

        with patch("scitex.io._save_listed_scalars_as_csv._mv_to_tmp") as mock_mv:
            _save_listed_scalars_as_csv(scalars, str(output_file), overwrite=True)

            mock_mv.assert_called_once_with(str(output_file), L=2)

    def test_verbose_output(self, tmp_path, capsys):
        """Test verbose output."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.1, 2.2]
        output_file = tmp_path / "verbose.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file), verbose=True)

        captured = capsys.readouterr()
        assert f"Saved to: {output_file}" in captured.out

    def test_append_behavior(self, tmp_path):
        """Test behavior when file exists and overwrite=False."""
from scitex.io import _save_listed_scalars_as_csv

        output_file = tmp_path / "append.csv"

        # First save
        scalars1 = [1, 2, 3]
        _save_listed_scalars_as_csv(scalars1, str(output_file))

        # Second save without overwrite
        scalars2 = [4, 5, 6]
        _save_listed_scalars_as_csv(scalars2, str(output_file), overwrite=False)

        # Second save should overwrite (not append)
        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 3  # Only second set
        assert df.iloc[0, 0] == 4


class TestSaveListedScalarsDataTypes:
    """Test different data types."""

    def test_mixed_numeric_types(self, tmp_path):
        """Test mixed numeric types."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [
            1,  # int
            2.5,  # float
            np.int32(3),  # numpy int
            np.float64(4.5),  # numpy float
            5.0,  # float
        ]

        output_file = tmp_path / "mixed_types.csv"
        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 5
        assert list(df.iloc[:, 0]) == [1.0, 2.5, 3.0, 4.5, 5.0]

    def test_numpy_array_input(self, tmp_path):
        """Test with numpy array input."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = np.array([1.1, 2.2, 3.3, 4.4])
        output_file = tmp_path / "numpy_input.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 4
        np.testing.assert_array_almost_equal(df.iloc[:, 0].values, scalars, decimal=3)

    def test_negative_values(self, tmp_path):
        """Test with negative values."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [-1.234, -2.345, 0, 1.234, 2.345]
        output_file = tmp_path / "negative.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert df.iloc[0, 0] == -1.234
        assert df.iloc[1, 0] == -2.345
        assert df.iloc[2, 0] == 0

    def test_very_large_values(self, tmp_path):
        """Test with very large values."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1e10, 1e-10, 1e20, 1e-20]
        output_file = tmp_path / "large_values.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file), round=20)

        df = pd.read_csv(output_file, index_col=0)
        assert df.iloc[0, 0] == 1e10
        assert df.iloc[1, 0] == pytest.approx(1e-10)


class TestSaveListedScalarsEdgeCases:
    """Test edge cases."""

    def test_empty_list(self, tmp_path):
        """Test saving empty list."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = []
        output_file = tmp_path / "empty.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 0
        assert df.columns[0] == "_"

    def test_single_scalar(self, tmp_path):
        """Test saving single scalar."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [42.123456]
        output_file = tmp_path / "single.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 1
        assert df.iloc[0, 0] == 42.123

    def test_nan_values(self, tmp_path):
        """Test with NaN values."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.0, np.nan, 3.0, np.nan, 5.0]
        output_file = tmp_path / "nan_values.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 5
        assert df.iloc[0, 0] == 1.0
        assert pd.isna(df.iloc[1, 0])
        assert df.iloc[2, 0] == 3.0

    def test_inf_values(self, tmp_path):
        """Test with infinity values."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.0, np.inf, -np.inf, 2.0]
        output_file = tmp_path / "inf_values.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert df.iloc[0, 0] == 1.0
        assert np.isinf(df.iloc[1, 0])
        assert np.isinf(df.iloc[2, 0])
        assert df.iloc[3, 0] == 2.0


class TestSaveListedScalarsErrorHandling:
    """Test error handling."""

    def test_mismatched_index_length(self, tmp_path):
        """Test when index length doesn't match scalars length."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1, 2, 3]
        indices = ["a", "b"]  # Too short
        output_file = tmp_path / "mismatch.csv"

        # Should raise error during DataFrame creation
        with pytest.raises(ValueError):
            _save_listed_scalars_as_csv(scalars, str(output_file), indi_suffix=indices)

    def test_non_numeric_values(self, tmp_path):
        """Test behavior with non-numeric values."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1, 2, "three", 4]  # String in numeric list
        output_file = tmp_path / "non_numeric.csv"

        # May raise during rounding
        with pytest.raises((TypeError, ValueError)):
            _save_listed_scalars_as_csv(scalars, str(output_file))

    def test_permission_error(self):
        """Test handling permission errors."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1, 2, 3]
        output_file = "/root/protected.csv"

        with pytest.raises(PermissionError):
            _save_listed_scalars_as_csv(scalars, output_file)


class TestSaveListedScalarsIntegration:
    """Test integration scenarios."""

    def test_large_dataset(self, tmp_path):
        """Test with large number of scalars."""
from scitex.io import _save_listed_scalars_as_csv

        # Create 10000 random scalars
        np.random.seed(42)
        scalars = np.random.randn(10000).tolist()
        output_file = tmp_path / "large_dataset.csv"

        _save_listed_scalars_as_csv(scalars, str(output_file))

        df = pd.read_csv(output_file, index_col=0)
        assert len(df) == 10000

        # Check some statistics are preserved
        assert abs(np.mean(df.iloc[:, 0]) - np.mean(scalars)) < 0.01

    def test_scientific_data_workflow(self, tmp_path):
        """Test typical scientific data workflow."""
from scitex.io import _save_listed_scalars_as_csv

        # Simulate experimental measurements
        measurements = [
            23.456789,  # Trial 1
            24.123456,  # Trial 2
            23.987654,  # Trial 3
            24.345678,  # Trial 4
            23.876543,  # Trial 5
        ]

        trial_names = [f"trial_{i+1}" for i in range(5)]

        output_file = tmp_path / "experiment_results.csv"

        _save_listed_scalars_as_csv(
            measurements,
            str(output_file),
            column_name="temperature_C",
            indi_suffix=trial_names,
            round=2,
            verbose=False,
        )

        # Verify saved data
        df = pd.read_csv(output_file, index_col=0)
        assert df.columns[0] == "temperature_C"
        assert list(df.index) == trial_names
        assert df.iloc[0, 0] == 23.46  # Rounded to 2 decimal places

    def test_round_trip_preservation(self, tmp_path):
        """Test that data can be recovered accurately."""
from scitex.io import _save_listed_scalars_as_csv

        # Original data with specific precision
        original = [1.234, 2.345, 3.456, 4.567, 5.678]
        output_file = tmp_path / "round_trip.csv"

        # Save with sufficient precision
        _save_listed_scalars_as_csv(original, str(output_file), round=3)

        # Load back
        df = pd.read_csv(output_file, index_col=0)
        recovered = df.iloc[:, 0].tolist()

        # Check values match to saved precision
        for orig, recov in zip(original, recovered):
            assert abs(orig - recov) < 0.001

    def test_unicode_column_name(self, tmp_path):
        """Test with Unicode column name."""
from scitex.io import _save_listed_scalars_as_csv

        scalars = [1.1, 2.2, 3.3]
        output_file = tmp_path / "unicode.csv"

        _save_listed_scalars_as_csv(
            scalars,
            str(output_file),
            column_name="温度測定",  # Japanese for "temperature measurement"
        )

        df = pd.read_csv(output_file, index_col=0, encoding="utf-8")
        assert df.columns[0] == "温度測定"


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 21:26:48 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_save_listed_scalars_as_csv.py
#
# import numpy as np
# import pandas as pd
# from ._mv_to_tmp import _mv_to_tmp
#
# def _save_listed_scalars_as_csv(
#     listed_scalars,
#     spath_csv,
#     column_name="_",
#     indi_suffix=None,
#     round=3,
#     overwrite=False,
#     verbose=False,
# ):
#     """Puts to df and save it as csv"""
#
#     if overwrite == True:
#         _mv_to_tmp(spath_csv, L=2)
#     indi_suffix = (
#         np.arange(len(listed_scalars)) if indi_suffix is None else indi_suffix
#     )
#     df = pd.DataFrame(
#         {"{}".format(column_name): listed_scalars}, index=indi_suffix
#     ).round(round)
#     df.to_csv(spath_csv)
#     if verbose:
#         print("\nSaved to: {}\n".format(spath_csv))
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_listed_scalars_as_csv.py
# --------------------------------------------------------------------------------
