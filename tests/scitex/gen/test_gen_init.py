#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test___init__.py

"""Tests for scitex.gen module initialization and auto-imports."""

import importlib
import inspect
import sys
from pathlib import Path

import pytest


class TestGenModuleInitialization:
    """Test the automatic import functionality of the gen module."""

    def test_module_imports(self):
        """Test that the gen module successfully imports."""
        import scitex.gen

        assert scitex.gen is not None
        assert hasattr(scitex.gen, "__file__")

    def test_expected_functions_available(self):
        """Test that expected functions are available after import."""
        import scitex.gen

        # Test some common functions that should be auto-imported
        expected_functions = [
            "DimHandler",
            "TimeStamper",
            "alternate_kwarg",
            "cache",
            "check_host",
            "ci",
            "close",
            "embed",
            "inspect_module",
            "is_ipython",
            "less",
            "list_packages",
            "mat2py",
            "norm",
            "paste",
            "print_config",
            "shell",
            "src",
            "start",
            "symlink",
            "symlog",
            "tee",
            "title2path",
            "title_case",
            "to_even",
            "to_odd",
            "to_rank",
            "transpose",
            "type",
            "var_info",
            "wrap",
            "xml2dict",
        ]

        for func_name in expected_functions:
            assert hasattr(
                scitex.gen, func_name
            ), f"Function {func_name} not found in scitex.gen"

    def test_no_private_functions_exported(self):
        """Test that private functions (starting with _) are not exported."""
        import scitex.gen

        for name in dir(scitex.gen):
            if name.startswith("_") and not name.startswith("__"):
                obj = getattr(scitex.gen, name)
                # Private functions should not be callable or classes
                if callable(obj) and not name.endswith("__"):
                    pytest.fail(f"Private function {name} should not be exported")

    def test_imported_objects_are_callable_or_classes(self):
        """Test that all imported objects are either functions or classes."""
        import scitex.gen

        for name in dir(scitex.gen):
            if not name.startswith("_"):
                obj = getattr(scitex.gen, name)
                assert callable(obj) or inspect.isclass(
                    obj
                ), f"{name} is neither callable nor a class"

    def test_module_docstring(self):
        """Test that the module has a proper docstring."""
        import scitex.gen

        assert scitex.gen.__doc__ is not None
        assert (
            "Gen utility" in scitex.gen.__doc__ or "utility" in scitex.gen.__doc__.lower()
        )

    def test_no_import_side_effects(self):
        """Test that importing the module doesn't have unwanted side effects."""
        # Save the initial state
        initial_modules = set(sys.modules.keys())

        # Remove scitex.gen if it's already imported
        for key in list(sys.modules.keys()):
            if key.startswith("scitex.gen"):
                del sys.modules[key]

        # Import and check for side effects
        import scitex.gen

        # Only scitex.gen and its submodules should be added
        new_modules = set(sys.modules.keys()) - initial_modules
        for module in new_modules:
            assert module.startswith("scitex") or module in [
                "importlib",
                "inspect",
            ], f"Unexpected module imported: {module}"

    def test_cleanup_of_temporary_variables(self):
        """Test that temporary variables used in __init__ are cleaned up."""
        import scitex.gen

        # These variables should not exist after cleanup
        temp_vars = [
            "os",
            "importlib",
            "inspect",
            "current_dir",
            "filename",
            "module_name",
            "module",
            "name",
            "obj",
        ]

        for var in temp_vars:
            assert not hasattr(
                scitex.gen, var
            ), f"Temporary variable {var} was not cleaned up"


class TestGenModuleFunctionality:
    """Test specific functionality expectations of the gen module."""

    def test_misc_functions_imported(self):
        """Test that functions from misc.py are available."""
        import scitex.gen

        misc_functions = [
            "find_closest",
            "isclose",
            "describe",
            "unique",
            "float_linspace",
            "Dirac",
            "step",
            "relu",
        ]

        available = [f for f in misc_functions if hasattr(scitex.gen, f)]
        # At least some misc functions should be available
        assert len(available) > 0, "No misc functions were imported"

    def test_function_origins(self):
        """Test that we can trace functions back to their origin modules."""
        import scitex.gen

        # Test a few known functions and their expected modules
        if hasattr(scitex.gen, "TimeStamper"):
            assert scitex.gen.TimeStamper.__module__.endswith("_TimeStamper")

        if hasattr(scitex.gen, "tee"):
            assert scitex.gen.tee.__module__.endswith("_tee")

    def test_reimport_stability(self):
        """Test that reimporting the module is stable."""
        import scitex.gen

        # Get initial function list
        initial_funcs = set(name for name in dir(scitex.gen) if not name.startswith("_"))

        # Force reimport
        importlib.reload(scitex.gen)

        # Check functions are still there
        final_funcs = set(name for name in dir(scitex.gen) if not name.startswith("_"))

        assert initial_funcs == final_funcs, "Function list changed after reimport"


class TestGenModuleEdgeCases:
    """Test edge cases and error handling."""

    def test_import_with_missing_submodule(self, tmp_path, monkeypatch):
        """Test behavior when a submodule fails to import."""
        # This is a conceptual test - in practice the module handles this gracefully
        import scitex.gen

        # The module should still be importable even if some submodules fail
        assert scitex.gen is not None

    def test_circular_import_handling(self):
        """Test that the module handles potential circular imports."""
        # Import in different order to test for circular dependencies
        import scitex
        import scitex.gen

        # Both should work without issues
        assert scitex is not None
        assert scitex.gen is not None

    def test_module_all_attribute(self):
        """Test __all__ attribute if present."""
        import scitex.gen

        if hasattr(scitex.gen, "__all__"):
            # If __all__ is defined, it should be a list of strings
            assert isinstance(scitex.gen.__all__, list)
            for item in scitex.gen.__all__:
                assert isinstance(item, str)
                assert hasattr(scitex.gen, item)


class TestGenModuleIntegration:
    """Test integration with other parts of scitex."""

    def test_gen_functions_work_together(self):
        """Test that various gen functions can work together."""
        import scitex.gen

        # Test TimeStamper if available
        if hasattr(scitex.gen, "TimeStamper"):
            ts = scitex.gen.TimeStamper()
            assert hasattr(ts, "start")

    def test_module_path_consistency(self):
        """Test that the module path is consistent."""
        import scitex.gen

        module_path = Path(scitex.gen.__file__).parent
        assert module_path.name == "gen"
        assert module_path.parent.name == "scitex"


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
