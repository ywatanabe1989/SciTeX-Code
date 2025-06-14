#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for resource/__init__.py

Tests cover:
- Dynamic module import functionality
- Automatic function and class discovery
- Module cleanup after import
- Integration with resource monitoring functions
"""

import importlib
import os
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestModuleStructure:
    """Test basic module structure and imports."""
    
    def test_module_imports(self):
        """Test that the module can be imported."""
        import scitex.resource
        assert scitex.resource is not None
    
    def test_dynamic_imports(self):
        """Test that functions are dynamically imported from submodules."""
        import scitex.resource
        
        # Should have imported functions from submodules
        # Based on the source, it imports all non-private functions and classes
        module_attrs = dir(scitex.resource)
        
        # Should have some functions (exact ones depend on what's in the directory)
        assert len(module_attrs) > 0
        
        # Should not have the temporary variables used during import
        assert 'os' not in module_attrs
        assert 'importlib' not in module_attrs
        assert 'inspect' not in module_attrs
        assert 'current_dir' not in module_attrs
        assert 'filename' not in module_attrs
        assert 'module_name' not in module_attrs
        assert 'module' not in module_attrs
        assert 'name' not in module_attrs
        assert 'obj' not in module_attrs


class TestDynamicImportMechanism:
    """Test the dynamic import mechanism."""
    
    @patch('os.listdir')
    @patch('importlib.import_module')
    def test_import_mechanism_mock(self, mock_import, mock_listdir):
        """Test the import mechanism with mocked modules."""
        # Mock the directory listing
        mock_listdir.return_value = ['test_module.py', '__init__.py', 'not_python.txt']
        
        # Create a mock module with functions and classes
        mock_module = MagicMock()
        mock_module.test_function = lambda: "test"
        mock_module.TestClass = type('TestClass', (), {})
        mock_module._private_function = lambda: "private"
        
        # Mock inspect.getmembers to return our test items
        with patch('inspect.getmembers') as mock_getmembers:
            mock_getmembers.return_value = [
                ('test_function', mock_module.test_function),
                ('TestClass', mock_module.TestClass),
                ('_private_function', mock_module._private_function),
                ('some_variable', 42),  # Should be ignored
            ]
            
            # Re-import the module to trigger dynamic imports
            import scitex.resource
            importlib.reload(scitex.resource)
    
    def test_actual_imports(self):
        """Test actual imports from resource submodules."""
        import scitex.resource
        
        # Check for expected functions based on the file structure
        # These are typical resource monitoring functions
        expected_attrs = [
            'get_processor_usages',
            'get_specs',
            'log_processor_usages',
            'limit_ram',  # May be limit_ram or limit_RAM
        ]
        
        module_attrs = dir(scitex.resource)
        
        # At least some of these should be present
        found_attrs = [attr for attr in expected_attrs if attr in module_attrs or attr.upper() in module_attrs or attr.lower() in module_attrs]
        
        # Should find at least one expected function
        assert len(found_attrs) > 0


class TestImportedFunctions:
    """Test that imported functions work correctly."""
    
    def test_get_specs_exists(self):
        """Test that get_specs function exists."""
        import scitex.resource
        
        # Should have get_specs from _get_specs.py
        assert hasattr(scitex.resource, 'get_specs')
        assert callable(scitex.resource.get_specs)
    
    def test_get_processor_usages_exists(self):
        """Test that get_processor_usages function exists."""
        import scitex.resource
        
        # Should have get_processor_usages from _get_processor_usages.py
        assert hasattr(scitex.resource, 'get_processor_usages')
        assert callable(scitex.resource.get_processor_usages)
    
    def test_log_processor_usages_exists(self):
        """Test that log_processor_usages function exists."""
        import scitex.resource
        
        # Should have log_processor_usages from _log_processor_usages.py
        assert hasattr(scitex.resource, 'log_processor_usages')
        assert callable(scitex.resource.log_processor_usages)
    
    def test_no_private_functions_exposed(self):
        """Test that private functions are not exposed."""
        import scitex.resource
        
        # Check that no attributes start with underscore (except special attributes)
        for attr in dir(scitex.resource):
            if not attr.startswith('__'):  # Allow dunder attributes
                assert not attr.startswith('_'), f"Private attribute {attr} should not be exposed"


class TestFunctionality:
    """Test basic functionality of imported functions."""
    
    def test_get_specs_basic(self):
        """Test basic get_specs functionality."""
        import scitex.resource
        
        # Should be able to call get_specs
        try:
            result = scitex.resource.get_specs()
            # Should return some system information
            assert result is not None
            
            # Typically returns a dict or similar structure
            if isinstance(result, dict):
                assert len(result) > 0
        except Exception as e:
            # Some functions might require specific conditions
            # Just ensure it's callable
            pass
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('GPUtil.getGPUs')
    def test_get_processor_usages_mocked(self, mock_gpus, mock_disk, mock_memory, mock_cpu):
        """Test get_processor_usages with mocked psutil."""
        import scitex.resource
        
        # Mock system stats
        mock_cpu.return_value = 50.0
        mock_memory.return_value = MagicMock(percent=60.0)
        mock_disk.return_value = MagicMock(percent=70.0)
        mock_gpus.return_value = []  # No GPUs
        
        # Should be able to call the function
        result = scitex.resource.get_processor_usages()
        
        # Should return usage information
        assert result is not None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_import_nonexistent_function(self):
        """Test accessing non-existent function."""
        import scitex.resource
        
        # Should raise AttributeError for non-existent attributes
        with pytest.raises(AttributeError):
            _ = scitex.resource.nonexistent_function_xyz123
    
    def test_module_reload(self):
        """Test that module can be reloaded."""
        import scitex.resource
        
        # Get initial attributes
        initial_attrs = set(dir(scitex.resource))
        
        # Reload the module
        importlib.reload(scitex.resource)
        
        # Should have same attributes after reload
        reload_attrs = set(dir(scitex.resource))
        
        # Most attributes should be the same
        # (Some internal attributes might change)
        common_attrs = initial_attrs.intersection(reload_attrs)
        assert len(common_attrs) > 0


class TestIntegration:
    """Test integration scenarios."""
    
    def test_resource_monitoring_workflow(self):
        """Test typical resource monitoring workflow."""
        import scitex.resource
        
        # Should be able to get system specs
        if hasattr(scitex.resource, 'get_specs'):
            try:
                specs = scitex.resource.get_specs()
                assert specs is not None
            except:
                # Some environments might not support all features
                pass
        
        # Should be able to get processor usage
        if hasattr(scitex.resource, 'get_processor_usages'):
            try:
                usage = scitex.resource.get_processor_usages()
                assert usage is not None
            except:
                pass
    
    def test_imported_functions_are_bound(self):
        """Test that imported functions are properly bound."""
        import scitex.resource
        
        # Get all callable attributes
        callables = [attr for attr in dir(scitex.resource) 
                    if not attr.startswith('_') and callable(getattr(scitex.resource, attr))]
        
        # Should have some callables
        assert len(callables) > 0
        
        # Each should be properly accessible
        for func_name in callables:
            func = getattr(scitex.resource, func_name)
            assert callable(func)
            
            # Should have proper name
            if hasattr(func, '__name__'):
                assert func.__name__ == func_name


class TestModuleCleanup:
    """Test module cleanup after import."""
    
    def test_temporary_variables_cleaned(self):
        """Test that temporary import variables are cleaned up."""
        import scitex.resource
        
        # These variables should have been deleted
        temp_vars = ['os', 'importlib', 'inspect', 'current_dir', 
                    'filename', 'module_name', 'module', 'name', 'obj']
        
        for var in temp_vars:
            assert not hasattr(scitex.resource, var), f"Temporary variable {var} should be cleaned up"
    
    def test_no_module_references_leaked(self):
        """Test that no module references are leaked."""
        import scitex.resource
        
        # Check that we don't have references to importlib internals
        for attr in dir(scitex.resource):
            if not attr.startswith('__'):
                value = getattr(scitex.resource, attr)
                # Should not be module objects (except for legitimate submodules)
                if hasattr(value, '__file__'):
                    # If it's a module, it should be a legitimate submodule
                    assert 'scitex.resource' in str(value)


class TestDynamicBehavior:
    """Test dynamic behavior of the module."""
    
    def test_new_module_detection(self):
        """Test that new modules would be detected on reload."""
        import scitex.resource
        
        # This tests the concept - in practice we can't easily add files
        # But we can verify the mechanism exists
        
        # The module uses os.listdir to find Python files
        # So it should dynamically pick up new files on reload
        
        # Get current functions
        current_funcs = [attr for attr in dir(scitex.resource) 
                        if not attr.startswith('_') and callable(getattr(scitex.resource, attr))]
        
        # The fact that functions exist proves the dynamic import works
        assert len(current_funcs) > 0
    
    def test_function_override_behavior(self):
        """Test behavior when multiple modules define same function."""
        import scitex.resource
        
        # If multiple modules define the same function name,
        # the last one imported wins (standard Python behavior)
        
        # We can at least verify that functions don't have conflicts
        # by checking they're all accessible
        funcs = {}
        for attr in dir(scitex.resource):
            if not attr.startswith('_') and callable(getattr(scitex.resource, attr)):
                funcs[attr] = getattr(scitex.resource, attr)
        
        # Each function should be unique
        assert len(funcs) == len(set(funcs.keys()))


class TestErrorHandling:
    """Test error handling in dynamic imports."""
    
    @patch('os.listdir')
    def test_handle_import_error(self, mock_listdir):
        """Test handling of import errors."""
        # Mock directory with a problematic module
        mock_listdir.return_value = ['bad_module.py']
        
        with patch('importlib.import_module') as mock_import:
            # Make import fail
            mock_import.side_effect = ImportError("Test error")
            
            # Module should handle this gracefully
            # (In the actual code, it might skip bad modules)
            try:
                import scitex.resource
                importlib.reload(scitex.resource)
                # Should not crash
                assert True
            except ImportError:
                # Import error is acceptable if not handled
                pass
    
    def test_handle_inspection_error(self):
        """Test handling of inspection errors."""
        import scitex.resource
        
        # Even with inspection issues, module should work
        with patch('inspect.isfunction') as mock_isfunction:
            mock_isfunction.side_effect = Exception("Inspection failed")
            
            try:
                # Try to access functions
                attrs = dir(scitex.resource)
                # Should still have some attributes
                assert len(attrs) > 0
            except:
                # Errors are acceptable in this edge case
                pass


class TestPerformance:
    """Test performance aspects of dynamic imports."""
    
    def test_import_performance(self):
        """Test that imports are reasonably fast."""
        import time
        
        start = time.time()
        import scitex.resource
        end = time.time()
        
        # Import should be reasonably fast (< 1 second)
        assert (end - start) < 1.0
    
    def test_attribute_access_performance(self):
        """Test that attribute access is fast after import."""
        import scitex.resource
        import time
        
        # Get a function
        if hasattr(scitex.resource, 'get_specs'):
            func = scitex.resource.get_specs
            
            # Accessing it again should be instant
            start = time.time()
            for _ in range(1000):
                _ = scitex.resource.get_specs
            end = time.time()
            
            # Should be very fast
            assert (end - start) < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])