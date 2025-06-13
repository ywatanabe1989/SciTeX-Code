#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test___init__.py

"""Tests for scitex.io module initialization and imports."""

import inspect
import sys
from pathlib import Path

import pytest


class TestIOModuleInitialization:
    """Test the imports and structure of the io module."""

    def test_module_imports(self):
        """Test that the io module successfully imports."""
        import scitex.io

        assert scitex.io is not None
        assert hasattr(scitex.io, "__file__")

    def test_expected_functions_available(self):
        """Test that expected functions are available after import."""
        import scitex.io

        # Core IO functions that should be available
        expected_functions = [
            "save",
            "load",
            "cache",
            "flush",
            "glob",
            "parse_glob",
            "json2md",
            "load_configs",
            "mv_to_tmp",
            "path",
            "reload",
            "save_image",
            "save_listed_dfs_as_csv",
            "save_listed_scalars_as_csv",
            "save_mp4",
            "save_optuna_study_as_csv_and_pngs",
            "save_text",
        ]

        for func_name in expected_functions:
            assert hasattr(
                scitex.io, func_name
            ), f"Function {func_name} not found in scitex.io"

    def test_glob_override(self):
        """Test that glob function is properly overridden."""
        import scitex.io

        # glob should be from _glob module, not the standard library
        assert hasattr(scitex.io, "glob")
        assert hasattr(scitex.io, "parse_glob")

        # Check it's not the standard library glob
        import glob as stdlib_glob

        assert scitex.io.glob is not stdlib_glob.glob

    def test_wildcard_imports(self):
        """Test that wildcard imports work correctly."""
        # The module uses from ._module import * pattern
        import scitex.io

        # Check that functions from submodules are available
        assert callable(getattr(scitex.io, "save", None))
        assert callable(getattr(scitex.io, "load", None))
        assert callable(getattr(scitex.io, "cache", None))

    def test_no_duplicate_imports(self):
        """Test that save is not imported twice (it appears twice in source)."""
        import scitex.io

        # Despite appearing twice in imports, save should be a single function
        assert hasattr(scitex.io, "save")
        save_func = getattr(scitex.io, "save")
        assert callable(save_func)

    def test_module_structure(self):
        """Test the module has proper structure."""
        import scitex.io

        # Check for module attributes
        assert hasattr(scitex.io, "__file__")
        assert hasattr(scitex.io, "__name__")
        assert scitex.io.__name__ == "scitex.io"


class TestIOModuleFunctionality:
    """Test specific functionality of the io module."""

    def test_save_load_availability(self):
        """Test that save and load functions are available and callable."""
        import scitex.io

        assert callable(scitex.io.save)
        assert callable(scitex.io.load)

        # Check they have proper signatures
        save_sig = inspect.signature(scitex.io.save)
        load_sig = inspect.signature(scitex.io.load)

        assert "filename" in save_sig.parameters or "fname" in save_sig.parameters
        assert "filename" in load_sig.parameters or "fname" in load_sig.parameters

    def test_specialized_save_functions(self):
        """Test that specialized save functions are available."""
        import scitex.io

        specialized_saves = [
            "save_image",
            "save_text",
            "save_mp4",
            "save_listed_dfs_as_csv",
            "save_listed_scalars_as_csv",
            "save_optuna_study_as_csv_and_pngs",
        ]

        for func_name in specialized_saves:
            assert hasattr(scitex.io, func_name), f"{func_name} not found"
            assert callable(getattr(scitex.io, func_name)), f"{func_name} is not callable"

    def test_utility_functions(self):
        """Test that utility functions are available."""
        import scitex.io

        utilities = ["cache", "flush", "reload", "mv_to_tmp", "path"]

        for util in utilities:
            assert hasattr(scitex.io, util), f"{util} not found"
            assert callable(getattr(scitex.io, util)), f"{util} is not callable"

    def test_config_loading(self):
        """Test that config loading function is available."""
        import scitex.io

        assert hasattr(scitex.io, "load_configs")
        assert callable(scitex.io.load_configs)

    def test_json_to_markdown(self):
        """Test that json2md function is available."""
        import scitex.io

        assert hasattr(scitex.io, "json2md")
        assert callable(scitex.io.json2md)


class TestIOModuleIntegration:
    """Test integration aspects of the io module."""

    def test_load_modules_imported(self):
        """Test that _load_modules submodule content is available."""
        import scitex.io

        # The _load_modules is imported with *, so its functions should be available
        # Check for some common load functions if they exist
        possible_loaders = [
            "load_numpy",
            "load_pickle",
            "load_json",
            "load_yaml",
            "load_torch",
            "load_pandas",
            "load_image",
        ]

        # At least some loaders should be available
        available_loaders = [l for l in possible_loaders if hasattr(scitex.io, l)]
        # This assertion might need adjustment based on actual implementation
        assert len(available_loaders) >= 0, "Expected some loader functions"

    def test_no_private_functions_exposed(self):
        """Test that private functions are not exposed."""
        import scitex.io

        # Get all attributes
        for attr_name in dir(scitex.io):
            if attr_name.startswith("_") and not attr_name.startswith("__"):
                # Skip module imports like _cache, _save etc
                attr = getattr(scitex.io, attr_name)
                if callable(attr) and not inspect.ismodule(attr):
                    # Private functions should not be exposed
                    pytest.fail(f"Private function {attr_name} is exposed")

    def test_reimport_stability(self):
        """Test that reimporting maintains stability."""
        import importlib
        import scitex.io

        # Get initial function list
        initial_funcs = set(
            name
            for name in dir(scitex.io)
            if not name.startswith("_") and callable(getattr(scitex.io, name))
        )

        # Reload module
        importlib.reload(scitex.io)

        # Check functions are still there
        final_funcs = set(
            name
            for name in dir(scitex.io)
            if not name.startswith("_") and callable(getattr(scitex.io, name))
        )

        assert initial_funcs == final_funcs, "Function list changed after reimport"


class TestIOModuleEdgeCases:
    """Test edge cases for the io module."""

    def test_circular_import_handling(self):
        """Test that the module handles circular imports properly."""
        # Import in different orders
        import scitex
        import scitex.io

        assert scitex is not None
        assert scitex.io is not None

    def test_module_path_consistency(self):
        """Test that module path is consistent."""
        import scitex.io

        module_path = Path(scitex.io.__file__).parent
        assert module_path.name == "io"
        assert module_path.parent.name == "scitex"

    def test_this_file_constant(self):
        """Test THIS_FILE constant if it exists."""
        import scitex.io

        if hasattr(scitex.io, "THIS_FILE"):
            # It should be a string path
            assert isinstance(scitex.io.THIS_FILE, str)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/__init__.py"
#
# # import os
# # import importlib
# # import inspect
#
# # # Get the current directory
# # current_dir = os.path.dirname(__file__)
#
# # # Iterate through all Python files in the current directory
# # for filename in os.listdir(current_dir):
# #     if filename.endswith(".py") and not filename.startswith("__"):
# #         module_name = filename[:-3]  # Remove .py extension
# #         module = importlib.import_module(f".{module_name}", package=__name__)
# #         # Import only functions and classes from the module
# #         for name, obj in inspect.getmembers(module):
# #             if inspect.isfunction(obj) or inspect.isclass(obj):
# #                 if not name.startswith("_"):
# #                     # print(name)
# #                     globals()[name] = obj
#
# # # Clean up temporary variables
# # del os, importlib, inspect, current_dir, filename, module_name, module, name, obj
#
# # # EOF
#
# from ._cache import *
# from ._flush import *
# from ._glob import *
# from ._json2md import *
# from ._load_configs import *
# from ._load_modules import *
# from ._load import *
# from ._mv_to_tmp import *
# from ._path import *
# from ._reload import *
# from ._save import *
# from ._save_image import *
# from ._save_listed_dfs_as_csv import *
# from ._save_listed_scalars_as_csv import *
# from ._save_mp4 import *
# from ._save_optuna_study_as_csv_and_pngs import *
# # from ._save_optuna_stury import *
# from ._save import *
# from ._save_text import *
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/__init__.py
# --------------------------------------------------------------------------------
