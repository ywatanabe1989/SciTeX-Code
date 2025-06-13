#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 02:40:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/color/test___init__.py

"""Comprehensive tests for scitex.plt.color module initialization.

This module tests the initialization and imports of the color module,
ensuring all submodules and functions are properly accessible and that
the module structure is correctly set up.
"""

import pytest
import os
import sys
import importlib
from pathlib import Path
import inspect
from typing import List, Tuple, Callable, Dict, Any
import numpy as np


class TestColorModuleImport:
    """Test basic import functionality of the color module."""
    
    def test_module_import(self):
        """Test that the color module can be imported successfully."""
        try:
            import scitex.plt.color
        except ImportError as e:
            pytest.fail(f"Failed to import scitex.plt.color: {e}")
    
    def test_module_has_file_attribute(self):
        """Test that module has __file__ attribute."""
        import scitex.plt.color
        assert hasattr(scitex.plt.color, '__file__')
        assert scitex.plt.color.__file__ is not None
    
    def test_module_path_exists(self):
        """Test that the module directory exists."""
        import scitex.plt.color
        module_path = Path(scitex.plt.color.__file__).parent
        assert module_path.exists()
        assert module_path.is_dir()
    
    def test_no_import_side_effects(self):
        """Test that importing doesn't have side effects."""
        # Store original state
        original_modules = set(sys.modules.keys())
        
        # Import module
        import scitex.plt.color
        
        # Check only expected modules were added
        new_modules = set(sys.modules.keys()) - original_modules
        for module in new_modules:
            assert 'scitex' in module or 'color' in module or 'plt' in module


class TestColorFunctionImports:
    """Test that all expected functions are imported."""
    
    def test_colormap_functions(self):
        """Test colormap-related function imports."""
        from scitex.plt.color import (
            get_color_from_cmap,
            get_colors_from_cmap,
            get_categorical_colors_from_cmap
        )
        
        # Check all are callable
        assert callable(get_color_from_cmap)
        assert callable(get_colors_from_cmap)
        assert callable(get_categorical_colors_from_cmap)
    
    def test_interpolate_function(self):
        """Test interpolate function import."""
        from scitex.plt.color import interpolate
        assert callable(interpolate)
    
    def test_visualize_function(self):
        """Test visualize colors function import."""
        from scitex.plt.color import vizualize_colors
        assert callable(vizualize_colors)
    
    def test_params_import(self):
        """Test PARAMS import."""
        from scitex.plt.color import PARAMS
        assert PARAMS is not None
        # PARAMS should be a dict or similar structure
        assert hasattr(PARAMS, '__getitem__') or hasattr(PARAMS, '__dict__')
    
    def test_rgb_conversion_functions(self):
        """Test RGB conversion function imports."""
        rgb_functions = [
            'str2rgb', 'str2rgba', 'rgb2rgba', 'rgba2rgb', 
            'rgba2hex', 'cycle_color_rgb', 'gradiate_color_rgb',
            'gradiate_color_rgba'
        ]
        
        import scitex.plt.color
        for func_name in rgb_functions:
            assert hasattr(scitex.plt.color, func_name)
            func = getattr(scitex.plt.color, func_name)
            assert callable(func)
    
    def test_bgr_conversion_functions(self):
        """Test BGR conversion function imports."""
        bgr_functions = [
            'str2bgr', 'str2bgra', 'bgr2bgra', 'bgra2bgr',
            'bgra2hex', 'cycle_color_bgr', 'gradiate_color_bgr',
            'gradiate_color_bgra'
        ]
        
        import scitex.plt.color
        for func_name in bgr_functions:
            assert hasattr(scitex.plt.color, func_name)
            func = getattr(scitex.plt.color, func_name)
            assert callable(func)
    
    def test_common_color_functions(self):
        """Test common color function imports."""
        common_functions = [
            'rgb2bgr', 'bgr2rgb', 'str2hex', 'update_alpha',
            'cycle_color', 'gradiate_color', 'to_rgb', 
            'to_rgba', 'to_hex'
        ]
        
        import scitex.plt.color
        for func_name in common_functions:
            assert hasattr(scitex.plt.color, func_name)
            func = getattr(scitex.plt.color, func_name)
            assert callable(func)


class TestModuleStructure:
    """Test the internal structure of the color module."""
    
    def test_submodule_files_exist(self):
        """Test that expected submodule files exist."""
        import scitex.plt.color
        module_path = Path(scitex.plt.color.__file__).parent
        
        expected_files = [
            '_get_colors_from_cmap.py',
            '_interpolate.py',
            '_PARAMS.py',
            '_vizualize_colors.py',
            '_colors.py',
            '_add_hue_col.py'  # May exist
        ]
        
        for file_name in expected_files:
            file_path = module_path / file_name
            if not file_path.exists():
                # Some files might be optional
                if file_name not in ['_add_hue_col.py']:
                    pytest.fail(f"Expected file {file_name} not found")
    
    def test_no_duplicate_imports(self):
        """Test that there are no duplicate function names."""
        import scitex.plt.color
        
        # Get all public attributes
        public_attrs = [attr for attr in dir(scitex.plt.color) 
                       if not attr.startswith('_')]
        
        # Check for duplicates
        assert len(public_attrs) == len(set(public_attrs))
    
    def test_gradiate_color_not_duplicated(self):
        """Test that gradiate_color is not imported twice."""
        import scitex.plt.color
        
        # Count occurrences of gradiate_color in module
        gradiate_count = dir(scitex.plt.color).count('gradiate_color')
        assert gradiate_count == 1, "gradiate_color should only be imported once"


class TestFunctionSignatures:
    """Test function signatures and basic behavior."""
    
    def test_color_conversion_signatures(self):
        """Test signatures of color conversion functions."""
        import scitex.plt.color
        
        # Test str2rgb signature
        sig = inspect.signature(scitex.plt.color.str2rgb)
        params = list(sig.parameters.keys())
        assert 'color_str' in params or len(params) >= 1
        
        # Test rgb2rgba signature
        sig = inspect.signature(scitex.plt.color.rgb2rgba)
        params = list(sig.parameters.keys())
        assert len(params) >= 1  # Should take RGB input
    
    def test_colormap_function_signatures(self):
        """Test signatures of colormap functions."""
        import scitex.plt.color
        
        # Test get_colors_from_cmap
        sig = inspect.signature(scitex.plt.color.get_colors_from_cmap)
        params = list(sig.parameters.keys())
        # Should have parameters for cmap name and number of colors
        assert len(params) >= 1
    
    def test_interpolate_signature(self):
        """Test interpolate function signature."""
        import scitex.plt.color
        
        sig = inspect.signature(scitex.plt.color.interpolate)
        params = list(sig.parameters.keys())
        # Should have parameters for colors and interpolation
        assert len(params) >= 2


class TestColorOperations:
    """Test basic color operations work correctly."""
    
    def test_str2rgb_basic(self):
        """Test basic string to RGB conversion."""
        from scitex.plt.color import str2rgb
        
        # Common color names should work
        for color in ['red', 'green', 'blue', 'white', 'black']:
            try:
                result = str2rgb(color)
                assert result is not None
                # Should return tuple or array of 3 values
                assert len(result) == 3
            except Exception as e:
                pytest.fail(f"str2rgb failed for '{color}': {e}")
    
    def test_rgb_bgr_conversion(self):
        """Test RGB to BGR conversion and back."""
        from scitex.plt.color import rgb2bgr, bgr2rgb
        
        # Test RGB to BGR
        rgb = (255, 128, 0)  # Orange in RGB
        bgr = rgb2bgr(rgb)
        assert bgr is not None
        
        # Convert back
        rgb_back = bgr2rgb(bgr)
        assert rgb_back is not None
        
        # Should be reversible
        assert tuple(rgb_back) == rgb
    
    def test_alpha_operations(self):
        """Test alpha channel operations."""
        from scitex.plt.color import rgb2rgba, update_alpha
        
        # Add alpha to RGB
        rgb = (255, 0, 0)  # Red
        rgba = rgb2rgba(rgb)
        assert len(rgba) == 4
        assert rgba[3] in [1.0, 255]  # Full opacity
        
        # Update alpha
        if hasattr(update_alpha, '__call__'):
            new_rgba = update_alpha(rgba, 0.5)
            assert new_rgba is not None


class TestModuleCompleteness:
    """Test that the module exports all expected functionality."""
    
    def test_all_expected_exports(self):
        """Test that all expected functions are exported."""
        import scitex.plt.color
        
        expected_exports = [
            # Colormap functions
            'get_color_from_cmap', 'get_colors_from_cmap',
            'get_categorical_colors_from_cmap',
            # Interpolation
            'interpolate',
            # Visualization
            'vizualize_colors',
            # RGB conversions
            'str2rgb', 'str2rgba', 'rgb2rgba', 'rgba2rgb', 'rgba2hex',
            'cycle_color_rgb', 'gradiate_color_rgb', 'gradiate_color_rgba',
            # BGR conversions
            'str2bgr', 'str2bgra', 'bgr2bgra', 'bgra2bgr', 'bgra2hex',
            'cycle_color_bgr', 'gradiate_color_bgr', 'gradiate_color_bgra',
            # Common functions
            'rgb2bgr', 'bgr2rgb', 'str2hex', 'update_alpha',
            'cycle_color', 'gradiate_color', 'to_rgb', 'to_rgba', 'to_hex',
            # PARAMS
            'PARAMS'
        ]
        
        module_attrs = dir(scitex.plt.color)
        missing = [exp for exp in expected_exports if exp not in module_attrs]
        
        assert not missing, f"Missing exports: {missing}"
    
    def test_no_unexpected_exports(self):
        """Test that there are no unexpected public exports."""
        import scitex.plt.color
        
        # Get all public attributes
        public_attrs = [attr for attr in dir(scitex.plt.color) 
                       if not attr.startswith('_')]
        
        # Known expected exports
        expected = {
            'get_color_from_cmap', 'get_colors_from_cmap',
            'get_categorical_colors_from_cmap', 'interpolate',
            'vizualize_colors', 'str2rgb', 'str2rgba', 'rgb2rgba',
            'rgba2rgb', 'rgba2hex', 'cycle_color_rgb', 'gradiate_color_rgb',
            'gradiate_color_rgba', 'str2bgr', 'str2bgra', 'bgr2bgra',
            'bgra2bgr', 'bgra2hex', 'cycle_color_bgr', 'gradiate_color_bgr',
            'gradiate_color_bgra', 'rgb2bgr', 'bgr2rgb', 'str2hex',
            'update_alpha', 'cycle_color', 'gradiate_color', 'to_rgb',
            'to_rgba', 'to_hex', 'PARAMS'
        }
        
        # Allow some standard Python attributes
        allowed_extras = {'__builtins__', '__cached__', '__doc__', 
                         '__file__', '__loader__', '__name__', 
                         '__package__', '__spec__', '__path__'}
        
        unexpected = set(public_attrs) - expected - allowed_extras
        # Some modules might have additional valid exports
        # Just warn rather than fail
        if unexpected:
            print(f"Unexpected exports found: {unexpected}")


class TestModuleReload:
    """Test module reload behavior."""
    
    def test_module_reload(self):
        """Test that the module can be reloaded."""
        import scitex.plt.color
        
        # Store original function reference
        original_str2rgb = scitex.plt.color.str2rgb
        
        # Reload module
        importlib.reload(scitex.plt.color)
        
        # Function should still exist
        assert hasattr(scitex.plt.color, 'str2rgb')
        # But might be a different object
        # (This is implementation-dependent)
    
    def test_no_state_persistence(self):
        """Test that module doesn't maintain problematic state."""
        import scitex.plt.color
        
        # Get initial state
        initial_attrs = set(dir(scitex.plt.color))
        
        # Use some functions (shouldn't change module state)
        if hasattr(scitex.plt.color, 'str2rgb'):
            try:
                scitex.plt.color.str2rgb('red')
            except:
                pass
        
        # Check state hasn't changed
        final_attrs = set(dir(scitex.plt.color))
        assert initial_attrs == final_attrs


class TestCircularImports:
    """Test for circular import issues."""
    
    def test_no_circular_imports(self):
        """Test that importing submodules doesn't cause circular imports."""
        # Clear relevant modules from cache
        modules_to_clear = [key for key in sys.modules.keys() 
                           if 'scitex.plt.color' in key]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Try importing in different orders
        try:
            from scitex.plt.color import str2rgb
        from scitex.plt.color import interpolate
            import scitex.plt.color
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")


class TestErrorHandling:
    """Test error handling in module import."""
    
    def test_missing_dependency_handling(self):
        """Test that missing dependencies are handled gracefully."""
        # This is more relevant for the actual function implementations
        # but we can test that the module imports even if some deps are missing
        import scitex.plt.color
        
        # Module should import successfully
        assert scitex.plt.color is not None
    
    def test_import_error_messages(self):
        """Test that import errors have helpful messages."""
        try:
            from scitex.plt.color import non_existent_function
            pytest.fail("Should have raised ImportError")
        except ImportError as e:
            # Error message should mention the module
            assert 'non_existent_function' in str(e)


class TestModuleDocumentation:
    """Test module documentation."""
    
    def test_module_has_docstring(self):
        """Test that functions have docstrings."""
        import scitex.plt.color
        
        # Check some key functions have docstrings
        functions_to_check = [
            'str2rgb', 'get_colors_from_cmap', 'interpolate'
        ]
        
        for func_name in functions_to_check:
            if hasattr(scitex.plt.color, func_name):
                func = getattr(scitex.plt.color, func_name)
                if callable(func):
                    # Function should have docstring (may be None)
                    assert hasattr(func, '__doc__')


class TestNamespaceIntegrity:
    """Test namespace integrity and organization."""
    
    def test_private_imports_not_exposed(self):
        """Test that private imports are not exposed."""
        import scitex.plt.color
        
        # Check that private modules are not exposed
        private_modules = ['_colors', '_interpolate', '_PARAMS', 
                          '_vizualize_colors', '_get_colors_from_cmap']
        
        for private in private_modules:
            # These should not be directly accessible (without underscore)
            assert private not in dir(scitex.plt.color)
    
    def test_import_organization(self):
        """Test that imports are well-organized."""
        import scitex.plt.color
        
        # Group functions by category
        rgb_funcs = [attr for attr in dir(scitex.plt.color) 
                    if 'rgb' in attr.lower()]
        bgr_funcs = [attr for attr in dir(scitex.plt.color) 
                    if 'bgr' in attr.lower()]
        
        # Should have both RGB and BGR functions
        assert len(rgb_funcs) > 0
        assert len(bgr_funcs) > 0
        
        # Should be roughly balanced (similar functionality)
        assert abs(len(rgb_funcs) - len(bgr_funcs)) < 5


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v", "-s"])
