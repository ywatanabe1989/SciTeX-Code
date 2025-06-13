#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test__reload.py

"""Tests for scitex.io._reload module."""

import importlib
import sys
import types
from unittest.mock import MagicMock, patch

import pytest


class TestReloadModule:
    """Test module reloading functionality."""

    def test_reload_module_in_sys_modules(self):
        """Test reloading a module that exists in sys.modules."""
from scitex.io import reload

        # Create a mock module
        mock_module = MagicMock(spec=types.ModuleType)
        mock_module.__name__ = "test_module"

        # Add to sys.modules
        sys.modules["test_module"] = mock_module

        try:
            with patch("importlib.reload") as mock_importlib_reload:
                with patch("builtins.print"):
                    reload(mock_module)

                    # Should have been deleted and reloaded
                    assert (
                        "test_module" not in sys.modules
                        or sys.modules["test_module"] != mock_module
                    )
                    mock_importlib_reload.assert_called()
        finally:
            # Cleanup
            if "test_module" in sys.modules:
                del sys.modules["test_module"]

    def test_reload_module_by_name(self):
        """Test reloading a module when it has __name__ attribute."""
from scitex.io import reload

        # Create a mock module with __name__
        mock_module = MagicMock()
        mock_module.__name__ = "my_module"
        sys.modules["my_module"] = mock_module

        try:
            with patch("importlib.reload") as mock_importlib_reload:
                with patch("builtins.print"):
                    reload(mock_module)

                    mock_importlib_reload.assert_called_with(sys.modules["my_module"])
        finally:
            if "my_module" in sys.modules:
                del sys.modules["my_module"]

    def test_reload_module_verbose(self):
        """Test reload with verbose output."""
from scitex.io import reload

        mock_module = MagicMock()
        mock_module.__name__ = "verbose_module"
        sys.modules["verbose_module"] = mock_module

        try:
            with patch("importlib.reload"):
                with patch("builtins.print") as mock_print:
                    reload(mock_module, verbose=True)

                    # Should print success message
                    mock_print.assert_called_with(
                        "Successfully reloaded module: verbose_module"
                    )
        finally:
            if "verbose_module" in sys.modules:
                del sys.modules["verbose_module"]


class TestReloadFunction:
    """Test function module reloading functionality."""

    def test_reload_function(self):
        """Test reloading module containing a function."""
from scitex.io import reload

        # Create a mock function with __module__ attribute
        mock_function = MagicMock()
        mock_function.__module__ = "function_module"

        # Create module for the function
        mock_module = MagicMock(spec=types.ModuleType)
        sys.modules["function_module"] = mock_module

        try:
            with patch("importlib.reload") as mock_importlib_reload:
                with patch("builtins.print"):
                    reload(mock_function)

                    mock_importlib_reload.assert_called_with(
                        sys.modules["function_module"]
                    )
        finally:
            if "function_module" in sys.modules:
                del sys.modules["function_module"]

    def test_reload_function_module_not_found(self):
        """Test reloading function when its module is not in sys.modules."""
from scitex.io import reload

        # Create mock function with module that's not loaded
        mock_function = MagicMock()
        mock_function.__module__ = "nonexistent_module"

        with patch("builtins.print") as mock_print:
            reload(mock_function)

            # Should print error message
            mock_print.assert_called_with(
                "Module nonexistent_module not found in sys.modules. Cannot reload."
            )

    def test_reload_class(self):
        """Test reloading module containing a class."""
from scitex.io import reload

        # Create a mock class with __module__ attribute
        mock_class = MagicMock()
        mock_class.__module__ = "class_module"

        # Create module for the class
        mock_module = MagicMock(spec=types.ModuleType)
        sys.modules["class_module"] = mock_module

        try:
            with patch("importlib.reload") as mock_importlib_reload:
                with patch("builtins.print"):
                    reload(mock_class)

                    mock_importlib_reload.assert_called_with(
                        sys.modules["class_module"]
                    )
        finally:
            if "class_module" in sys.modules:
                del sys.modules["class_module"]


class TestReloadErrorHandling:
    """Test error handling in reload function."""

    def test_reload_unrecognized_object(self):
        """Test reloading an object that's neither module nor function/class."""
from scitex.io import reload

        # Create object without __module__ or __name__ in sys.modules
        unrecognized_obj = MagicMock()
        # Remove __module__ and __name__ if they exist
        if hasattr(unrecognized_obj, "__module__"):
            delattr(unrecognized_obj, "__module__")
        if hasattr(unrecognized_obj, "__name__"):
            delattr(unrecognized_obj, "__name__")

        with patch("builtins.print") as mock_print:
            reload(unrecognized_obj)

            # Should print error message
            mock_print.assert_called_with(
                "Provided object is neither a recognized module nor a function/class with a __module__ attribute."
            )

    def test_reload_module_not_in_sys_modules(self):
        """Test reloading when module is not in sys.modules."""
from scitex.io import reload

        mock_module = MagicMock()
        mock_module.__name__ = "missing_module"
        # Don't add to sys.modules

        with patch("builtins.print") as mock_print:
            reload(mock_module)

            # Should print error about module not found
            mock_print.assert_called_with(
                "Module missing_module not found in sys.modules. Cannot reload."
            )

    def test_reload_importlib_exception(self):
        """Test handling of exception during importlib.reload."""
from scitex.io import reload

        mock_module = MagicMock()
        mock_module.__name__ = "error_module"
        sys.modules["error_module"] = mock_module

        try:
            with patch("importlib.reload", side_effect=Exception("Reload failed")):
                with patch("builtins.print") as mock_print:
                    reload(mock_module)

                    # Should print error message
                    mock_print.assert_called_with(
                        "Failed to reload module error_module. Error: Reload failed"
                    )
        finally:
            if "error_module" in sys.modules:
                del sys.modules["error_module"]

    def test_reload_keyerror(self):
        """Test handling of KeyError during reload."""
from scitex.io import reload

        # Create a function that claims to be from a module that doesn't exist
        mock_function = MagicMock()
        mock_function.__module__ = "phantom_module"

        # Add module to sys.modules but make importlib.reload raise KeyError
        sys.modules["phantom_module"] = MagicMock()

        try:
            with patch("importlib.reload", side_effect=KeyError("phantom_module")):
                with patch("builtins.print") as mock_print:
                    reload(mock_function)

                    # Should handle KeyError gracefully
                    mock_print.assert_called_with(
                        "Module phantom_module not found in sys.modules. Cannot reload."
                    )
        finally:
            if "phantom_module" in sys.modules:
                del sys.modules["phantom_module"]


class TestReloadIntegration:
    """Test integration scenarios."""

    def test_reload_actual_module(self):
        """Test reloading an actual imported module."""
from scitex.io import reload
        import json  # Use a standard library module

        # Store original module reference
        original_json = sys.modules.get("json")

        try:
            with patch("importlib.reload") as mock_importlib_reload:
                with patch("builtins.print"):
                    reload(json)

                    # Should attempt to reload json module
                    mock_importlib_reload.assert_called()
        finally:
            # Restore original module if needed
            if original_json:
                sys.modules["json"] = original_json

    def test_reload_from_imported_function(self):
        """Test reloading from an imported function."""
from scitex.io import reload
        from os.path import join  # Import a function

        with patch("importlib.reload") as mock_importlib_reload:
            with patch("builtins.print"):
                reload(join)

                # Should reload the os.path module
                mock_importlib_reload.assert_called_with(sys.modules["posixpath"])

    def test_reload_edge_case_module_in_sys_modules_branch(self):
        """Test the first branch where module is directly in sys.modules."""
from scitex.io import reload

        # Create a module name that will trigger the first if condition
        module_name = "direct_module"
        mock_module = MagicMock(spec=types.ModuleType)
        mock_module.__name__ = module_name

        # Add the module name itself to sys.modules
        sys.modules[module_name] = mock_module

        try:
            with patch("importlib.reload") as mock_importlib_reload:
                # Pass the module name string directly
                reload(module_name)

                # Should delete and reload
                mock_importlib_reload.assert_called()
        finally:
            if module_name in sys.modules:
                del sys.modules[module_name]


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
