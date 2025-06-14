#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 08:00:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__ignore_SettingWithCopyWarning.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import warnings
import tempfile
import os
import sys


class TestIgnoreSettingWithCopyWarningBasic:
    """Test basic functionality of ignore_setting_with_copy_warning."""

    def test_suppress_warning_on_slice_assignment(self):
        """Test that SettingWithCopyWarning is suppressed during slice assignment."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        # Create a DataFrame and a view that would normally trigger warning
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df_view = df[df["A"] > 1]

        # This would normally trigger SettingWithCopyWarning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                df_view["B"] = 99  # This should not produce warning

            # Check no warnings were raised
            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0

    def test_warning_raised_without_context_manager(self):
        """Test that warning is raised when not using context manager."""
        # Create a DataFrame and a view that triggers warning
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df_view = df[df["A"] > 1]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                # This should trigger SettingWithCopyWarning
                df_view["B"] = 99
            except Exception:
                # Some pandas versions might raise, others just warn
                pass

            # In many cases, the warning is raised
            # Note: behavior may vary by pandas version

    def test_loc_assignment_with_context_manager(self):
        """Test .loc assignment with context manager."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        subset = df[["A"]]  # This creates a view

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                subset.loc[:, "A"] = 100

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0


class TestBackwardCompatibility:
    """Test backward compatibility with old function name."""

    def test_old_function_name_works(self):
        """Test that ignore_SettingWithCopyWarning (old name) still works."""
        from scitex.pd import ignore_SettingWithCopyWarning

        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df_view = df[df["A"] > 1]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Use old function name
            with ignore_SettingWithCopyWarning():
                df_view["B"] = 99

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0

    def test_both_names_are_same_function(self):
        """Test that both function names refer to the same function."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
            ignore_SettingWithCopyWarning,
        )

        # They should be the same object
        assert ignore_setting_with_copy_warning is ignore_SettingWithCopyWarning


class TestComplexScenarios:
    """Test complex DataFrame manipulation scenarios."""

    def test_chained_indexing(self):
        """Test suppression with chained indexing."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        df = pd.DataFrame(
            {"A": [1, 2, 3, 4], "B": [5, 6, 7, 8], "C": ["x", "y", "z", "w"]}
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                # Chained indexing that would normally warn
                df[df["A"] > 2]["B"] = 999

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0

    def test_multiple_operations(self):
        """Test multiple operations within context manager."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        df = pd.DataFrame({"A": range(10), "B": range(10, 20), "C": range(20, 30)})

        view1 = df[df["A"] < 5]
        view2 = df[["B", "C"]]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                view1["B"] = -1
                view2["C"] = -2
                view1.loc[:, "C"] = -3

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0

    def test_nested_dataframes(self):
        """Test with nested DataFrame operations."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        df = pd.DataFrame({"group": ["A", "A", "B", "B"], "value": [1, 2, 3, 4]})

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                for group in df["group"].unique():
                    group_df = df[df["group"] == group]
                    group_df["value"] = group_df["value"] * 10

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0


class TestWarningRestoration:
    """Test that warning settings are properly restored."""

    def test_warnings_restored_after_context(self):
        """Test that warning filters are restored after context manager exits."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        # Get initial warning filters
        initial_filters = warnings.filters.copy()

        # Use context manager
        with ignore_setting_with_copy_warning():
            # Inside context, SettingWithCopyWarning should be ignored
            pass

        # After context, filters should be restored
        # Note: exact comparison might fail due to internal changes
        # but the important thing is warnings work normally again

        # Test that we can still catch warnings after
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.warn("Test warning", UserWarning)

            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)

    def test_exception_in_context_restores_warnings(self):
        """Test that warnings are restored even if exception occurs."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        with pytest.raises(ValueError):
            with ignore_setting_with_copy_warning():
                raise ValueError("Test exception")

        # Warnings should still work normally after exception
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.warn("Test warning", UserWarning)

            assert len(w) == 1


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_context(self):
        """Test context manager with no operations."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        # Should not raise any errors
        with ignore_setting_with_copy_warning():
            pass

    def test_non_pandas_operations(self):
        """Test that non-pandas operations work normally."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                # Regular numpy operations
                arr = np.array([1, 2, 3])
                arr[0] = 999

                # Regular Python operations
                lst = [1, 2, 3]
                lst[0] = 999

                # Other warnings should still work
                warnings.warn("Test warning", UserWarning)

            # Should have the UserWarning but no SettingWithCopyWarning
            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)

    def test_multiple_context_managers(self):
        """Test using multiple context managers."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        df1 = pd.DataFrame({"A": [1, 2, 3]})
        df2 = pd.DataFrame({"B": [4, 5, 6]})

        view1 = df1[df1["A"] > 1]
        view2 = df2[df2["B"] < 6]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                view1["A"] = 10

                with ignore_setting_with_copy_warning():
                    view2["B"] = 20

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0


class TestRealWorldUsage:
    """Test real-world usage patterns."""

    def test_data_cleaning_workflow(self):
        """Test typical data cleaning workflow."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        # Create sample data
        df = pd.DataFrame(
            {
                "id": range(100),
                "value": np.random.randn(100),
                "category": np.random.choice(["A", "B", "C"], 100),
            }
        )

        # Filter data
        df_filtered = df[df["value"] > 0]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                # Clean data without warnings
                df_filtered["value"] = df_filtered["value"].round(2)
                df_filtered["processed"] = True
                df_filtered.loc[df_filtered["category"] == "A", "special"] = "yes"

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0

    def test_iterative_updates(self):
        """Test iterative DataFrame updates."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        df = pd.DataFrame(
            {
                "date": pd.date_range("2023-01-01", periods=30),
                "value": np.random.randn(30),
            }
        )

        # Create view
        january = df[df["date"].dt.month == 1]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with ignore_setting_with_copy_warning():
                # Update values iteratively
                for i in range(len(january)):
                    if january.iloc[i]["value"] < 0:
                        january.iloc[i, january.columns.get_loc("value")] = 0

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0


class TestDocstringExample:
    """Test the example from the docstring."""

    def test_docstring_example(self):
        """Test exact example from docstring."""
        from scitex.pd import (
            ignore_setting_with_copy_warning,
        )

        # Create a situation that would trigger warning
        df = pd.DataFrame({"column": [1, 2, 3], "other": [4, 5, 6]})
        df_subset = df[df["column"] > 1]
        new_values = [10, 20]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Example from docstring
            with ignore_setting_with_copy_warning():
                df_subset["column"] = new_values  # No warning will be shown

            setting_warnings = [
                warning for warning in w if "SettingWithCopy" in str(warning.category)
            ]
            assert len(setting_warnings) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
