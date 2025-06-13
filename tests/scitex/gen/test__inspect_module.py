#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 21:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__inspect_module.py

"""Tests for inspect_module function."""

import types
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from scitex.gen import inspect_module
from scitex.gen._inspect_module import _print_module_contents


# Mock module for testing
class MockClass:
    """Mock class for testing."""

    pass


def mock_function():
    """Mock function for testing."""
    pass


class TestInspectModule:
    """Test cases for inspect_module function."""

    def test_basic_module_inspection(self):
        """Test basic module inspection with actual module."""
        # Test with types module (small and stable)
        result = inspect_module("types", max_depth=1, root_only=True)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert all(
            col in result.columns for col in ["Type", "Name", "Docstring", "Depth"]
        )

    def test_module_string_import(self):
        """Test module inspection with string module name."""
        result = inspect_module("sys", max_depth=0)

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1  # At least the module itself
        assert result.iloc[0]["Type"] == "M"
        assert "sys" in result.iloc[0]["Name"]

    def test_import_error_handling(self):
        """Test handling of import errors."""
        # Use a module name that definitely doesn't exist
        result = inspect_module("this_module_definitely_does_not_exist_12345")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert all(
            col in result.columns for col in ["Type", "Name", "Docstring", "Depth"]
        )

    def test_max_depth_limiting(self):
        """Test that max_depth properly limits recursion."""
        # Create nested module structure
        module = types.ModuleType("test_module")
        submodule = types.ModuleType("submodule")
        subsubmodule = types.ModuleType("subsubmodule")

        module.submodule = submodule
        submodule.subsubmodule = subsubmodule

        # Test with max_depth=1
        result = inspect_module(module, max_depth=1)

        # Should have module and submodule, but not subsubmodule
        names = result["Name"].tolist()
        assert any("test_module" in name for name in names)
        assert any("submodule" in name and "subsubmodule" not in name for name in names)

    def test_visited_tracking(self):
        """Test that visited set prevents infinite recursion."""
        # Create circular reference
        module1 = types.ModuleType("module1")
        module2 = types.ModuleType("module2")
        module1.module2 = module2
        module2.module1 = module1

        # Should not cause infinite recursion
        result = inspect_module(module1, max_depth=5)

        assert isinstance(result, pd.DataFrame)
        # Each module should appear only once
        module_names = [n for n in result["Name"] if n in ["module1", "module2"]]
        assert len(set(module_names)) == len(module_names)

    def test_docstring_inclusion(self):
        """Test docstring inclusion/exclusion."""
        module = types.ModuleType("test_module")
        module.__doc__ = "Module docstring"
        module.test_function = lambda: None
        module.test_function.__doc__ = "Function docstring"

        # Test with docstring=True
        result_with_docs = inspect_module(module, docstring=True)
        # Test with docstring=False
        result_without_docs = inspect_module(module, docstring=False)

        # With docstrings should have non-empty docstring column
        assert any(result_with_docs["Docstring"].str.contains("docstring", na=False))
        # Without docstrings should have empty docstring column
        assert all(result_without_docs["Docstring"] == "")

    def test_column_selection(self):
        """Test custom column selection."""
        module = types.ModuleType("test_module")

        # Test with custom columns
        result = inspect_module(module, columns=["Type", "Name"])

        assert list(result.columns) == ["Type", "Name"]
        assert "Docstring" not in result.columns
        assert "Depth" not in result.columns

    def test_type_detection(self):
        """Test correct type detection for different objects."""
        module = types.ModuleType("test_module")
        module.test_function = mock_function
        module.TestClass = MockClass
        module.submodule = types.ModuleType("submodule")

        result = inspect_module(module)

        # Check types
        types_dict = dict(zip(result["Name"], result["Type"]))
        assert any(v == "M" for v in types_dict.values())  # Module
        assert any(v == "F" for v in types_dict.values())  # Function
        assert any(v == "C" for v in types_dict.values())  # Class

    def test_private_member_filtering(self):
        """Test that private members (starting with _) are filtered out."""
        module = types.ModuleType("test_module")
        module.public_function = lambda: None
        module._private_function = lambda: None
        module.__very_private = lambda: None

        result = inspect_module(module)

        names = result["Name"].tolist()
        assert any("public_function" in name for name in names)
        assert not any("_private_function" in name for name in names)
        assert not any("__very_private" in name for name in names)

    def test_root_only_filtering(self):
        """Test root_only parameter filters nested modules."""
        module = types.ModuleType("test_module")
        module.level1 = types.ModuleType("level1")
        module.level1.level2 = types.ModuleType("level2")

        # Test with root_only=True
        result = inspect_module(module, root_only=True, max_depth=3)

        # Count dots in names - root level should have at most 1 dot
        for name in result["Name"]:
            assert name.count(".") <= 1

    def test_drop_duplicates(self):
        """Test duplicate removal functionality."""
        # Create module with duplicate names
        module = types.ModuleType("test_module")

        # Add functions that will result in duplicates when processed
        module.func1 = lambda: None
        module.func2 = lambda: None

        # Get result with drop_duplicates=True (default)
        result_dedup = inspect_module(module, drop_duplicates=True)

        # Get result with drop_duplicates=False
        result_with_dup = inspect_module(module, drop_duplicates=False)

        # The deduplicated result should have unique names
        assert result_dedup["Name"].nunique() == len(result_dedup)

    def test_exception_handling_in_processing(self):
        """Test exception handling during module processing."""
        module = types.ModuleType("test_module")
        # Add an object that raises exception when inspected
        module.bad_obj = MagicMock()
        module.bad_obj.__name__ = property(lambda x: 1 / 0)  # Raises ZeroDivisionError

        # Should handle exception gracefully
        result = inspect_module(module)

        assert isinstance(result, pd.DataFrame)

    @patch("builtins.print")
    def test_print_output_parameter(self, mock_print):
        """Test print_output parameter."""
        module = types.ModuleType("test_module")
        module.test_func = lambda: None

        # Test with print_output=True
        inspect_module(module, print_output=True, tree=True)

        # Should have called print
        assert mock_print.called

    def test_version_handling(self):
        """Test handling of module version attribute."""
        module = types.ModuleType("test_module")
        module.__version__ = "1.2.3"

        result = inspect_module(module, docstring=True)

        # Module entry should include version
        module_entry = result[result["Type"] == "M"].iloc[0]
        assert "v1.2.3" in module_entry["Docstring"]

    def test_depth_tracking(self):
        """Test that depth is correctly tracked."""
        # Create a simple module structure for predictable testing
        module = types.ModuleType("test_module")
        module.test_function = lambda: None
        module.TestClass = type("TestClass", (), {})

        result = inspect_module(module, max_depth=2)

        # Check that we have the expected entries
        assert len(result) >= 1  # At least the module itself

        # Check depths are assigned correctly
        depth_dict = dict(zip(result["Name"], result["Depth"]))

        # Root module should be at depth 0
        assert any(
            name.endswith("test_module") and depth == 0
            for name, depth in depth_dict.items()
        )

    @patch("warnings.filterwarnings")
    def test_warning_suppression(self, mock_filter):
        """Test warning suppression with skip_depwarnings."""
        # Test with skip_depwarnings=True
        inspect_module("sys", skip_depwarnings=True)

        # Should have filtered warnings
        assert mock_filter.called
        calls = mock_filter.call_args_list
        assert any("DeprecationWarning" in str(call) for call in calls)
        assert any("UserWarning" in str(call) for call in calls)


class TestPrintModuleContents:
    """Test cases for _print_module_contents function."""

    @patch("builtins.print")
    def test_tree_printing(self, mock_print):
        """Test tree structure printing."""
        df = pd.DataFrame(
            {
                "Type": ["M", "F", "C"],
                "Name": ["module", "module.func", "module.Class"],
                "Docstring": ["", " - A function", " - A class"],
                "Depth": [0, 1, 1],
            }
        )

        _print_module_contents(df)

        # Check print was called
        assert mock_print.called

        # Check output contains tree characters
        printed_strings = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("├──" in s or "└──" in s for s in printed_strings)
        assert any("(M)" in s for s in printed_strings)
        assert any("(F)" in s for s in printed_strings)
        assert any("(C)" in s for s in printed_strings)

    @patch("builtins.print")
    def test_tree_structure_depth(self, mock_print):
        """Test tree structure with multiple depths."""
        df = pd.DataFrame(
            {
                "Type": ["M", "M", "F"],
                "Name": ["a", "a.b", "a.b.c"],
                "Docstring": ["", "", ""],
                "Depth": [0, 1, 2],
            }
        )

        _print_module_contents(df)

        # Verify print was called
        assert mock_print.called

        # Check output has tree structure elements
        printed_strings = [str(call[0][0]) for call in mock_print.call_args_list]
        # Should have tree characters
        assert any("├──" in s or "└──" in s or "│" in s for s in printed_strings)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
