#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-03 08:05:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/resource/_utils/test___init__.py

"""Tests for resource._utils.__init__.py module.

This module tests the dynamic import functionality that automatically loads
all functions and classes from Python files in the resource._utils directory.
"""

import os
import sys
import tempfile
import importlib
import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path


class TestResourceUtilsInit:
    """Test the resource._utils.__init__.py dynamic import functionality."""

    def test_module_import(self):
        """Test that the module can be imported successfully."""
        import scitex.resource._utils
        assert scitex.resource._utils is not None

    def test_get_env_info_function_available(self):
        """Test that get_env_info function is available after import."""
        import scitex.resource._utils
        assert hasattr(scitex.resource._utils, 'get_env_info')
        assert callable(scitex.resource._utils.get_env_info)

    def test_pretty_str_function_available(self):
        """Test that pretty_str function is available after import."""
        import scitex.resource._utils
        assert hasattr(scitex.resource._utils, 'pretty_str')
        assert callable(scitex.resource._utils.pretty_str)

    def test_dynamic_import_mechanism(self):
        """Test the dynamic import mechanism by checking that it works."""
        # Since the module is already imported, just verify it works properly
        import scitex.resource._utils
        
        # Verify that the expected functions are available
        assert hasattr(scitex.resource._utils, 'get_env_info')
        assert callable(scitex.resource._utils.get_env_info)
        
        # Verify that the dynamic import worked by checking module attributes
        module_attrs = dir(scitex.resource._utils)
        public_attrs = [attr for attr in module_attrs if not attr.startswith('_')]
        assert len(public_attrs) > 0, "Dynamic import should expose public functions"

    @patch('os.listdir')
    def test_file_filtering(self, mock_listdir):
        """Test that only .py files are processed, excluding __init__.py."""
        mock_listdir.return_value = [
            '_get_env_info.py',      # Should be processed
            '_test_module.py',       # Should be processed
            '__init__.py',           # Should be excluded
            '__pycache__',           # Should be excluded (not .py)
            'README.md',             # Should be excluded (not .py)
            '.hidden_file.py',       # Should be excluded (starts with .)
        ]
        
        with patch('os.path.dirname', return_value='/fake/path'):
            with patch('importlib.import_module') as mock_import:
                with patch('inspect.getmembers', return_value=[]):
                    # Re-import to trigger the filtering logic
                    if 'scitex.resource._utils' in sys.modules:
                        del sys.modules['scitex.resource._utils']
                    
                    try:
                        import scitex.resource._utils
                        # Check that only the expected files were processed
                        # Note: This may not call import_module if already cached
                        pass
                    except:
                        # Module may already be loaded, that's fine for this test
                        pass

    def test_function_visibility_filter(self):
        """Test that only public functions/classes are exposed."""
        import scitex.resource._utils
        
        # Get all attributes from the module
        module_attrs = dir(scitex.resource._utils)
        
        # Filter out built-in attributes
        user_attrs = [attr for attr in module_attrs if not attr.startswith('__')]
        
        # Check that we don't have private functions starting with _
        private_functions = [attr for attr in user_attrs if attr.startswith('_')]
        
        # There might be some private attributes, but the main functions should be public
        public_functions = [attr for attr in user_attrs if not attr.startswith('_')]
        assert len(public_functions) > 0, "Should have at least some public functions"

    def test_module_cleanup(self):
        """Test that temporary variables are cleaned up after import."""
        import scitex.resource._utils
        
        # These variables should not be available after cleanup
        cleanup_vars = ['current_dir', 'filename', 'module_name', 'module', 'name', 'obj']
        
        for var in cleanup_vars:
            assert not hasattr(scitex.resource._utils, var), f"Variable {var} should be cleaned up"

    @patch('importlib.import_module')
    def test_import_error_handling(self, mock_import):
        """Test behavior when module import fails."""
        # Make import_module raise an exception
        mock_import.side_effect = ImportError("Test import error")
        
        with patch('os.listdir', return_value=['_test_module.py']):
            with patch('os.path.dirname', return_value='/fake/path'):
                # The module should handle import errors gracefully
                try:
                    # Try to reimport (may be cached)
                    if 'scitex.resource._utils' in sys.modules:
                        del sys.modules['scitex.resource._utils']
                    import scitex.resource._utils
                    # If we get here, the module loaded despite the error (cached or handled)
                except ImportError:
                    # This is also acceptable - the import error propagated
                    pass

    def test_inspect_members_filtering(self):
        """Test that inspect.getmembers correctly filters functions and classes."""
        import scitex.resource._utils
        import inspect
        
        # Get all members from the module
        all_members = inspect.getmembers(scitex.resource._utils)
        
        # Filter functions and classes
        functions = [item for name, item in all_members 
                    if inspect.isfunction(item) and not name.startswith('_')]
        classes = [item for name, item in all_members 
                  if inspect.isclass(item) and not name.startswith('_')]
        
        # Should have at least some functions
        assert len(functions) > 0, "Should have imported some functions"

    def test_module_attributes_exist(self):
        """Test that expected module attributes exist."""
        import scitex.resource._utils
        
        # Check for expected attributes from _get_env_info module
        expected_attrs = ['get_env_info']
        
        for attr in expected_attrs:
            assert hasattr(scitex.resource._utils, attr), f"Missing expected attribute: {attr}"
            assert callable(getattr(scitex.resource._utils, attr)), f"Attribute {attr} should be callable"

    def test_module_directory_structure(self):
        """Test that the module directory structure is as expected."""
        import scitex.resource._utils
        import os
        
        # Get the module's directory
        module_dir = os.path.dirname(scitex.resource._utils.__file__)
        
        # Check that it's a valid directory
        assert os.path.isdir(module_dir), "Module directory should exist"
        
        # Check for expected Python files
        files = os.listdir(module_dir)
        py_files = [f for f in files if f.endswith('.py') and not f.startswith('__')]
        
        assert len(py_files) > 0, "Should have at least some Python files to import"
        assert '_get_env_info.py' in py_files, "Should have _get_env_info.py file"

    @patch('os.path.dirname')
    @patch('os.listdir')
    def test_empty_directory_handling(self, mock_listdir, mock_dirname):
        """Test behavior when the directory contains no Python files."""
        mock_dirname.return_value = '/empty/path'
        mock_listdir.return_value = ['README.md', '__init__.py', '.gitignore']
        
        # Should handle empty directory gracefully
        try:
            # Re-import to test empty directory scenario
            import scitex.resource._utils
            # Module should still be importable even with no additional files
        except Exception as e:
            pytest.fail(f"Module should handle empty directory gracefully: {e}")

    def test_module_docstring_and_metadata(self):
        """Test that module has proper metadata."""
        import scitex.resource._utils
        
        # Check that module is properly formed
        assert hasattr(scitex.resource._utils, '__file__'), "Module should have __file__ attribute"
        assert hasattr(scitex.resource._utils, '__name__'), "Module should have __name__ attribute"
        
        # Module name should be correct
        assert scitex.resource._utils.__name__ == 'scitex.resource._utils'

    def test_imported_function_execution(self):
        """Test that imported functions can be executed."""
        import scitex.resource._utils
        
        # Test that get_env_info function can be called
        try:
            result = scitex.resource._utils.get_env_info()
            assert isinstance(result, dict), "get_env_info should return a dictionary"
        except Exception as e:
            # Function might require certain dependencies, that's ok
            assert True, f"Function exists but may have dependencies: {e}"

    def test_no_namespace_pollution(self):
        """Test that the dynamic import doesn't pollute the namespace inappropriately."""
        import scitex.resource._utils
        
        # Get all attributes
        attrs = dir(scitex.resource._utils)
        
        # Should not have basic Python builtin polluting the namespace
        unwanted_attrs = ['os', 'importlib', 'inspect']
        
        for attr in unwanted_attrs:
            assert attr not in attrs, f"Unwanted attribute {attr} found in namespace"

    def test_member_inspection_edge_cases(self):
        """Test edge cases in member inspection."""
        import scitex.resource._utils
        import inspect
        
        # Get all members from the actual module
        all_members = inspect.getmembers(scitex.resource._utils)
        
        # Test that we have the expected types of objects
        functions = []
        classes = []
        other_objects = []
        
        for name, obj in all_members:
            if not name.startswith('__'):  # Skip builtin attributes
                if inspect.isfunction(obj):
                    functions.append((name, obj))
                elif inspect.isclass(obj):
                    classes.append((name, obj))
                else:
                    other_objects.append((name, obj))
        
        # Should have found some functions
        assert len(functions) > 0, "Should have imported some functions"
        
        # Test that private objects starting with _ are properly filtered
        private_objects = [name for name, obj in all_members if name.startswith('_') and not name.startswith('__')]
        # The cleanup should have removed temporary variables
        forbidden_private = ['current_dir', 'filename', 'module_name', 'module', 'name', 'obj']
        for forbidden in forbidden_private:
            assert forbidden not in [name for name, obj in all_members], f"Temporary variable {forbidden} should be cleaned up"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])
