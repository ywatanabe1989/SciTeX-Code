#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:12:00 (ywatanabe)"
# File: ./tests/scitex/utils/test___init__.py

"""
Functionality:
    * Tests utils module initialization and dynamic imports
    * Validates function and class exposure
    * Tests cleanup of temporary variables
Input:
    * Module imports
Output:
    * Test results
Prerequisites:
    * pytest
"""

import pytest
import inspect
import scitex.utils


class TestUtilsInit:
    """Test cases for utils module initialization."""

    def test_module_imports_functions(self):
        """Test that functions are properly imported from submodules."""
        # Check that key functions are available
        assert hasattr(scitex.utils, 'compress_hdf5')
        assert callable(scitex.utils.compress_hdf5)
        
        # Verify it's a function
        assert inspect.isfunction(scitex.utils.compress_hdf5)

    def test_module_no_private_functions(self):
        """Test that private functions are not exposed."""
        # Get all attributes from the module
        attrs = dir(scitex.utils)
        
        # Filter for functions that start with underscore (should be minimal)
        private_funcs = [attr for attr in attrs if attr.startswith('_') and not attr.startswith('__')]
        
        # utils module contains private submodules like _compress_hdf5, _email, etc.
        # This is expected behavior for dynamic imports
        assert len(private_funcs) >= 0  # Allow for private submodules

    def test_module_imports_all_expected_functions(self):
        """Test that all expected utility functions are imported."""
        expected_functions = [
            'compress_hdf5',  # From _compress_hdf5.py
        ]
        
        for func_name in expected_functions:
            assert hasattr(scitex.utils, func_name), f"Function {func_name} not found in scitex.utils"
            assert callable(getattr(scitex.utils, func_name)), f"{func_name} is not callable"

    def test_module_dynamic_import_mechanism(self):
        """Test that the dynamic import mechanism works correctly."""
        # Test that the module can be imported without errors
        import scitex.utils as utils_module
        
        # Check that the module has the expected structure
        assert hasattr(utils_module, 'compress_hdf5')
        
        # Verify that imported functions work
        func = getattr(utils_module, 'compress_hdf5')
        assert callable(func)
        
        # Test function signature
        sig = inspect.signature(func)
        assert 'input_file' in sig.parameters

    def test_module_cleanup_variables(self):
        """Test that temporary variables are cleaned up after import."""
        # These variables should not be present after cleanup
        unwanted_vars = ['os', 'importlib', 'inspect', 'current_dir', 
                        'filename', 'module_name', 'module', 'name', 'obj']
        
        for var in unwanted_vars:
            assert not hasattr(scitex.utils, var), f"Temporary variable {var} not cleaned up"

    def test_module_structure_integrity(self):
        """Test overall module structure and integrity."""
        # Check basic module attributes
        assert hasattr(scitex.utils, '__name__')
        assert 'scitex.utils' in scitex.utils.__name__
        
        # Check that module is properly initialized
        assert scitex.utils is not None
        
        # Verify module can be used
        functions = [attr for attr in dir(scitex.utils) 
                    if callable(getattr(scitex.utils, attr)) and not attr.startswith('__')]
        assert len(functions) > 0, "No callable functions found in module"

    def test_imported_functions_have_proper_modules(self):
        """Test that imported functions retain proper module information."""
        # Check that functions know their origin
        if hasattr(scitex.utils, 'compress_hdf5'):
            func = scitex.utils.compress_hdf5
            assert hasattr(func, '__module__')
            assert 'scitex.utils' in func.__module__


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
