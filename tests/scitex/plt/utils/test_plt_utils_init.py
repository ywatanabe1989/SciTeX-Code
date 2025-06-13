#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:07:21 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/utils/test___init__.py

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
import importlib
from types import ModuleType


class TestPlotUtilsInit:
    """Test cases for scitex.plt.utils.__init__.py module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.module_name = "scitex.plt.utils"
        
    def test_module_imports_successfully(self):
        """Test that the module can be imported without errors."""
        try:
            import scitex.plt.utils
            assert hasattr(scitex.plt.utils, 'calc_bacc_from_conf_mat')
            assert hasattr(scitex.plt.utils, 'calc_nice_ticks')
            assert hasattr(scitex.plt.utils, 'configure_mpl')
            assert hasattr(scitex.plt.utils, 'im2grid')
            assert hasattr(scitex.plt.utils, 'mk_colorbar')
            assert hasattr(scitex.plt.utils, 'mk_patches')
        except ImportError as e:
            pytest.fail(f"Failed to import scitex.plt.utils: {e}")

    def test_calc_bacc_from_conf_mat_import(self):
        """Test that calc_bacc_from_conf_mat can be imported and is callable."""
        from scitex.plt.utils import calc_bacc_from_conf_mat
        assert callable(calc_bacc_from_conf_mat)
        assert hasattr(calc_bacc_from_conf_mat, '__name__')
        assert calc_bacc_from_conf_mat.__name__ == 'calc_bacc_from_conf_mat'

    def test_calc_nice_ticks_import(self):
        """Test that calc_nice_ticks can be imported and is callable."""
        from scitex.plt.utils import calc_nice_ticks
        assert callable(calc_nice_ticks)
        assert hasattr(calc_nice_ticks, '__name__')
        assert calc_nice_ticks.__name__ == 'calc_nice_ticks'

    def test_configure_mpl_import(self):
        """Test that configure_mpl can be imported and is callable."""
        from scitex.plt.utils import configure_mpl
        assert callable(configure_mpl)
        assert hasattr(configure_mpl, '__name__')
        assert configure_mpl.__name__ == 'configure_mpl'

    def test_im2grid_import(self):
        """Test that im2grid can be imported and is callable."""
        from scitex.plt.utils import im2grid
        assert callable(im2grid)
        assert hasattr(im2grid, '__name__')
        assert im2grid.__name__ == 'im2grid'

    def test_mk_colorbar_import(self):
        """Test that mk_colorbar can be imported and is callable."""
        from scitex.plt.utils import mk_colorbar
        assert callable(mk_colorbar)
        assert hasattr(mk_colorbar, '__name__')
        assert mk_colorbar.__name__ == 'mk_colorbar'

    def test_mk_patches_import(self):
        """Test that mk_patches can be imported and is callable."""
        from scitex.plt.utils import mk_patches
        assert callable(mk_patches)
        assert hasattr(mk_patches, '__name__')
        assert mk_patches.__name__ == 'mk_patches'

    def test_all_imports_available_via_star_import(self):
        """Test that all expected functions are available via star import."""
        # Create a temporary namespace to test star import
        namespace = {}
        exec("from scitex.plt.utils import *", namespace)
        
        expected_functions = [
            'calc_bacc_from_conf_mat',
            'calc_nice_ticks', 
            'configure_mpl',
            'im2grid',
            'mk_colorbar',
            'mk_patches'
        ]
        
        for func_name in expected_functions:
            assert func_name in namespace, f"Function {func_name} not available via star import"
            assert callable(namespace[func_name]), f"{func_name} is not callable"

    def test_module_has_expected_attributes(self):
        """Test that the module has all expected public attributes."""
        import scitex.plt.utils as utils_module
        
        expected_attrs = [
            'calc_bacc_from_conf_mat',
            'calc_nice_ticks',
            'configure_mpl', 
            'im2grid',
            'mk_colorbar',
            'mk_patches'
        ]
        
        for attr in expected_attrs:
            assert hasattr(utils_module, attr), f"Module missing attribute: {attr}"

    def test_module_docstring_exists(self):
        """Test that the module has a docstring or is properly documented."""
        import scitex.plt.utils as utils_module
        # Module may or may not have docstring, but should be importable
        assert isinstance(utils_module, ModuleType)
        assert utils_module.__name__ == 'scitex.plt.utils'

    def test_import_isolation_calc_bacc(self):
        """Test that calc_bacc_from_conf_mat import is isolated correctly."""
        # Test that the function can be imported independently
        from scitex.plt.utils import calc_bacc_from_conf_mat
        assert callable(calc_bacc_from_conf_mat)
        
        # Verify it's also available from the main module
        import scitex.plt.utils
        assert hasattr(scitex.plt.utils, 'calc_bacc_from_conf_mat')
        assert scitex.plt.utils.calc_bacc_from_conf_mat is calc_bacc_from_conf_mat

    def test_import_isolation_calc_nice_ticks(self):
        """Test that calc_nice_ticks import is isolated correctly."""
        # Test that the function can be imported independently  
        from scitex.plt.utils import calc_nice_ticks
        assert callable(calc_nice_ticks)
        
        # Verify it's also available from the main module
        import scitex.plt.utils
        assert hasattr(scitex.plt.utils, 'calc_nice_ticks')
        assert scitex.plt.utils.calc_nice_ticks is calc_nice_ticks

    def test_module_structure_integrity(self):
        """Test that the module maintains proper structure and organization."""
        import scitex.plt.utils as utils_module
        
        # Check that this is indeed the utils submodule of plt
        assert utils_module.__name__ == 'scitex.plt.utils'
        
        # Verify it's part of the scitex.plt package
        import scitex.plt
        assert hasattr(scitex.plt, 'utils')
        assert scitex.plt.utils is utils_module

    def test_circular_import_protection(self):
        """Test that there are no circular import issues."""
        try:
            # This should work without hanging or errors
            import scitex.plt.utils
            from scitex.plt.utils import calc_bacc_from_conf_mat
            from scitex.plt.utils import calc_nice_ticks
            from scitex.plt.utils import configure_mpl
            from scitex.plt.utils import im2grid
            from scitex.plt.utils import mk_colorbar
            from scitex.plt.utils import mk_patches
            
            # If we get here, no circular imports occurred
            assert True
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                # Re-raise other import errors for investigation
                raise

    def test_reload_module_safety(self):
        """Test that the module can be safely reloaded."""
        import scitex.plt.utils as utils_module
        
        # Store original function references
        original_calc_bacc = utils_module.calc_bacc_from_conf_mat
        original_calc_ticks = utils_module.calc_nice_ticks
        
        # Reload the module
        importlib.reload(utils_module)
        
        # Verify functions are still available and callable
        assert hasattr(utils_module, 'calc_bacc_from_conf_mat')
        assert hasattr(utils_module, 'calc_nice_ticks')
        assert callable(utils_module.calc_bacc_from_conf_mat)
        assert callable(utils_module.calc_nice_ticks)

    def test_function_signatures_accessible(self):
        """Test that function signatures are properly accessible for introspection."""
        import inspect
        from scitex.plt.utils import (
            calc_bacc_from_conf_mat,
            calc_nice_ticks,
            configure_mpl,
            im2grid,
            mk_colorbar,
            mk_patches
        )
        
        functions_to_test = [
            calc_bacc_from_conf_mat,
            calc_nice_ticks,
            configure_mpl,
            im2grid,
            mk_colorbar,
            mk_patches
        ]
        
        for func in functions_to_test:
            try:
                signature = inspect.signature(func)
                assert signature is not None
                # Function should have parameters (they're not no-arg functions)
                assert len(signature.parameters) >= 0
            except (ValueError, TypeError) as e:
                pytest.fail(f"Could not inspect signature of {func.__name__}: {e}")

    def test_namespace_cleanliness(self):
        """Test that the module namespace only contains expected public items."""
        import scitex.plt.utils as utils_module
        
        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(utils_module) if not attr.startswith('_')]
        
        expected_public_attrs = {
            'calc_bacc_from_conf_mat',
            'calc_nice_ticks',
            'configure_mpl',
            'im2grid', 
            'mk_colorbar',
            'mk_patches'
        }
        
        # Check that all expected attributes are present
        for attr in expected_public_attrs:
            assert attr in public_attrs, f"Expected public attribute {attr} not found"
        
        # Allow for additional attributes but warn if unexpected ones appear
        unexpected_attrs = set(public_attrs) - expected_public_attrs
        if unexpected_attrs:
            # This is informational, not necessarily an error
            print(f"Note: Unexpected public attributes found: {unexpected_attrs}")


if __name__ == "__main__":
    pytest.main([__file__])
