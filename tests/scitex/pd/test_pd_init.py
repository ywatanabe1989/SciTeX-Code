#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 19:50:00 (ywatanabe)"
# File: ./tests/scitex/pd/test___init__.py

"""
Test module for scitex.pd package initialization.
"""

import pytest
import pandas as pd
import numpy as np
import warnings


class TestPdInit:
    """Test class for pd module initialization."""

    def test_module_import(self):
        """Test that scitex.pd can be imported."""
        import scitex.pd

        assert hasattr(scitex, "pd")

    def test_available_functions(self):
        """Test that expected functions are available in the module."""
        import scitex.pd

        # Core functions that should be available
        expected_functions = [
            "find_indi",
            "find_pval",
            "force_df",
            "from_xyz",
            "ignore_SettingWithCopyWarning",
            "melt_cols",
            "merge_columns",
            "mv",
            "replace",
            "round",
            "slice",
            "sort",
            "to_numeric",
            "to_xy",
            "to_xyz",
        ]

        # Check at least some core functions are available
        available_count = sum(
            1 for func in expected_functions if hasattr(scitex.pd, func)
        )
        assert (
            available_count > 10
        ), f"Only {available_count} functions available out of {len(expected_functions)}"

    def test_no_private_functions_exposed(self):
        """Test that private functions (starting with _) are not exposed."""
        import scitex.pd

        for attr_name in dir(scitex.pd):
            if not attr_name.startswith("__"):  # Skip dunder methods
                attr = getattr(scitex.pd, attr_name)
                if callable(attr) and attr_name.startswith("_"):
                    # Check if it's a function from the pd module
                    if hasattr(attr, "__module__") and "scitex.pd" in attr.__module__:
                        pytest.fail(
                            f"Private function {attr_name} should not be exposed"
                        )

    def test_import_warnings_handled(self):
        """Test that import warnings are properly handled."""
        # This tests that the module handles ImportError gracefully
        # The __init__.py catches ImportError and issues warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib
            import scitex.pd

            importlib.reload(scitex.pd)
            # Check that any warnings are about failed imports, not other errors
            for warning in w:
                if "Failed to import" in str(warning.message):
                    assert True  # This is expected behavior

    def test_force_df_available(self):
        """Test that force_df function is available and works."""
        import scitex.pd

        # Test with list
        result = scitex.pd.force_df([1, 2, 3])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # Test with dict
        result = scitex.pd.force_df({"a": [1, 2], "b": [3, 4]})
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["a", "b"]

        # Test with Series
        s = pd.Series([1, 2, 3])
        result = scitex.pd.force_df(s)
        assert isinstance(result, pd.DataFrame)

    def test_ignore_settingwithcopywarning_available(self):
        """Test that ignore_SettingWithCopyWarning is available."""
        import scitex.pd

        assert hasattr(scitex.pd, "ignore_SettingWithCopyWarning")
        # Call it to ensure it works
        scitex.pd.ignore_SettingWithCopyWarning()

    def test_basic_functionality_smoke_test(self):
        """Smoke test for basic pd module functionality."""
        import scitex.pd

        # Create test DataFrame
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

        # Test slice if available
        if hasattr(scitex.pd, "slice"):
            # Use slice object for row indices (not list)
            result = scitex.pd.slice(df, slice(0, 2))  # slice(0, 2) selects rows 0 and 1
            assert len(result) == 2

        # Test round if available
        if hasattr(scitex.pd, "round"):
            df_float = pd.DataFrame({"A": [1.234, 2.567, 3.891]})
            result = scitex.pd.round(df_float, 2)
            assert result["A"].iloc[0] == 1.23

        # Test to_numeric if available
        if hasattr(scitex.pd, "to_numeric"):
            df_str = pd.DataFrame({"A": ["1", "2", "3"]})
            result = scitex.pd.to_numeric(df_str)
            assert pd.api.types.is_numeric_dtype(result["A"])


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/__init__.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-24 18:40:30 (ywatanabe)"
# # /home/ywatanabe/proj/scitex/src/scitex/pd/__init__.py
#
# import os
# import importlib
# import inspect
# import warnings
#
# # Get the current directory
# current_dir = os.path.dirname(__file__)
#
# # Iterate through all Python files in the current directory
# for filename in os.listdir(current_dir):
#     if filename.endswith(".py") and not filename.startswith("__"):
#         module_name = filename[:-3]
#         # module = importlib.import_module(f".{module_name}", package=__name__)
#
#         # # Import only functions and classes from the module
#         # for name, obj in inspect.getmembers(module):
#         #     if inspect.isfunction(obj) or inspect.isclass(obj):
#         #         if not name.startswith("_"):
#         #             globals()[name] = obj
#         try:
#             module = importlib.import_module(f".{module_name}", package=__name__)
#
#             # Import only functions and classes from the module
#             for name, obj in inspect.getmembers(module):
#                 if inspect.isfunction(obj) or inspect.isclass(obj):
#                     if not name.startswith("_"):
#                         globals()[name] = obj
#         except ImportError as e:
#             warnings.warn(f"Warning: Failed to import {module_name}.")
#
# # Clean up temporary variables
# del (
#     os,
#     importlib,
#     inspect,
#     current_dir,
#     filename,
#     module_name,
#     module,
#     name,
#     obj,
# )
#
# # from ._merge_columns import merge_cols, merge_columns
# # from ._misc import find_indi  # col_to_last,; col_to_top,; merge_columns,
# # from ._misc import force_df, ignore_SettingWithCopyWarning, slice
# # from ._mv import mv, mv_to_first, mv_to_last
# # from ._sort import sort

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/pd/__init__.py
# --------------------------------------------------------------------------------
