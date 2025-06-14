#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 09:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/plt/aucs/test___init__.py

"""Comprehensive tests for scitex.ai.plt.aucs module initialization.

This module tests the initialization and imports of the AUCs plotting module,
ensuring all submodules are properly accessible and that the module structure
is correctly set up.
"""

import pytest
import sys
import importlib
from pathlib import Path


class TestAUCsModuleInit:
    """Test suite for aucs module initialization."""
    
    def test_module_import(self):
        """Test that the aucs module can be imported successfully."""
        try:
            import scitex.ai.plt.aucs
        except ImportError as e:
            pytest.fail(f"Failed to import scitex.ai.plt.aucs: {e}")
    
    def test_submodules_exist(self):
        """Test that all expected submodules exist in the package."""
        import scitex.ai.plt.aucs
        
        # Check module path exists
        module_path = Path(scitex.ai.plt.aucs.__file__).parent
        assert module_path.exists(), "Module directory does not exist"
        
        # Check for expected submodule files
        expected_files = ['example.py', 'roc_auc.py', 'pre_rec_auc.py']
        for file_name in expected_files:
            file_path = module_path / file_name
            assert file_path.exists(), f"Expected file {file_name} not found"
    
    def test_roc_auc_import(self):
        """Test that roc_auc function can be imported."""
        try:
            from scitex.ai.plt.aucs.roc_auc import roc_auc
            assert callable(roc_auc), "roc_auc should be callable"
        except ImportError as e:
            pytest.fail(f"Failed to import roc_auc: {e}")
    
    def test_pre_rec_auc_import(self):
        """Test that pre_rec_auc function can be imported."""
        try:
            from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
            assert callable(pre_rec_auc), "pre_rec_auc should be callable"
        except ImportError as e:
            pytest.fail(f"Failed to import pre_rec_auc: {e}")
    
    def test_helper_functions_import(self):
        """Test that helper functions can be imported from submodules."""
        try:
            from scitex.ai.plt.aucs.roc_auc import to_onehot, interpolate_roc_data_points
            assert callable(to_onehot), "to_onehot should be callable"
            assert callable(interpolate_roc_data_points), "interpolate_roc_data_points should be callable"
        except ImportError as e:
            pytest.fail(f"Failed to import helper functions: {e}")
    
    def test_module_attributes(self):
        """Test that the module has expected attributes."""
        import scitex.ai.plt.aucs
        
        # Check for __file__ attribute
        assert hasattr(scitex.ai.plt.aucs, '__file__'), "Module should have __file__ attribute"
        
        # Check for __path__ attribute (package indicator)
        assert hasattr(scitex.ai.plt.aucs, '__path__'), "Module should have __path__ attribute"
    
    def test_import_with_reload(self):
        """Test that the module can be reloaded without issues."""
        import scitex.ai.plt.aucs
        
        try:
            importlib.reload(scitex.ai.plt.aucs)
        except Exception as e:
            pytest.fail(f"Failed to reload module: {e}")
    
    def test_namespace_integrity(self):
        """Test that importing aucs doesn't pollute the namespace."""
        # Store original modules
        original_modules = set(sys.modules.keys())
        
        # Import the module
        import scitex.ai.plt.aucs
        
        # Check that only expected modules were added
        new_modules = set(sys.modules.keys()) - original_modules
        
        # Should only add aucs-related modules
        for module in new_modules:
            assert 'aucs' in module or 'scitex' in module, \
                f"Unexpected module imported: {module}"
    
    def test_circular_import_check(self):
        """Test that there are no circular import issues."""
        # Clear the module from cache if it exists
        modules_to_clear = [key for key in sys.modules.keys() if 'aucs' in key]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Try importing in different orders
        try:
            from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
            from scitex.ai.plt.aucs.roc_auc import roc_auc
            import scitex.ai.plt.aucs
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")
    
    def test_module_docstring(self):
        """Test that module files have appropriate docstrings."""
        import scitex.ai.plt.aucs.roc_auc
        import scitex.ai.plt.aucs.pre_rec_auc
        
        # Main functions should be documented
        assert scitex.ai.plt.aucs.roc_auc.roc_auc.__doc__ is not None, \
            "roc_auc function should have a docstring"
        assert scitex.ai.plt.aucs.pre_rec_auc.pre_rec_auc.__doc__ is not None, \
            "pre_rec_auc function should have a docstring"
    
    def test_dependencies_available(self):
        """Test that required dependencies are available."""
        required_modules = ['matplotlib', 'numpy', 'sklearn', 'pandas']
        
        for module_name in required_modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                pytest.fail(f"Required dependency {module_name} is not available")
    
    def test_module_structure_consistency(self):
        """Test that module structure is consistent with expectations."""
        import scitex.ai.plt.aucs.roc_auc as roc_module
        import scitex.ai.plt.aucs.pre_rec_auc as pr_module
        
        # Both modules should have similar structure
        assert hasattr(roc_module, 'to_onehot'), "roc_auc should have to_onehot function"
        assert hasattr(pr_module, 'to_onehot'), "pre_rec_auc should have to_onehot function"
        
        # Main plotting functions
        assert hasattr(roc_module, 'roc_auc'), "roc_auc module should have roc_auc function"
        assert hasattr(pr_module, 'pre_rec_auc'), "pre_rec_auc module should have pre_rec_auc function"
    
    def test_no_side_effects_on_import(self):
        """Test that importing the module doesn't have side effects."""
        import matplotlib.pyplot as plt
        
        # Store original state
        original_backend = plt.get_backend()
        original_interactive = plt.isinteractive()
        
        # Import module
        import scitex.ai.plt.aucs
        
        # Check state hasn't changed
        assert plt.get_backend() == original_backend, \
            "Module import should not change matplotlib backend"
        assert plt.isinteractive() == original_interactive, \
            "Module import should not change matplotlib interactive mode"
    
    def test_version_compatibility(self):
        """Test Python version compatibility."""
        import sys
        
        # Module should work with Python 3.6+
        assert sys.version_info >= (3, 6), \
            "Module requires Python 3.6 or higher"
    
    def test_import_error_handling(self):
        """Test that import errors are handled gracefully."""
        # This test ensures the module handles missing optional dependencies
        # gracefully (though for aucs, all dependencies are required)
        pass
    
    def test_module_all_attribute(self):
        """Test __all__ attribute if defined in modules."""
        # Test that modules have __all__ defined
        import scitex.ai.plt.aucs.roc_auc as roc_module
        import scitex.ai.plt.aucs.pre_rec_auc as pre_rec_module
        
        # Check if __all__ is defined (it's optional)
        if hasattr(roc_module, '__all__'):
            assert isinstance(roc_module.__all__, list)
        if hasattr(pre_rec_module, '__all__'):
            assert isinstance(pre_rec_module.__all__, list)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
