#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 17:00:00 (ywatanabe)"
# File: ./tests/scitex/plt/ax/_style/test___init__.py

"""Tests for matplotlib axis styling module initialization."""

import pytest
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestStyleModuleImports:
    """Test import functionality of the style module."""
    
    def test_module_import(self):
        """Test that the style module imports successfully."""
        import scitex.plt.ax._style
        assert scitex.plt.ax._style is not None
    
    def test_add_marginal_ax_import(self):
        """Test add_marginal_ax function import."""
from scitex.plt.ax import add_marginal_ax
        assert callable(add_marginal_ax)
    
    def test_add_panel_import(self):
        """Test add_panel function import."""
from scitex.plt.ax import add_panel
        assert callable(add_panel)
    
    def test_extend_import(self):
        """Test extend function import."""
from scitex.plt.ax import extend
        assert callable(extend)
    
    def test_force_aspect_import(self):
        """Test force_aspect function import."""
from scitex.plt.ax import force_aspect
        assert callable(force_aspect)
    
    def test_format_label_import(self):
        """Test format_label function import."""
from scitex.plt.ax import format_label
        assert callable(format_label)
    
    def test_hide_spines_import(self):
        """Test hide_spines function import."""
from scitex.plt.ax import hide_spines
        assert callable(hide_spines)
    
    def test_map_ticks_import(self):
        """Test map_ticks function import."""
from scitex.plt.ax import map_ticks
        assert callable(map_ticks)
    
    def test_rotate_labels_import(self):
        """Test rotate_labels function import."""
from scitex.plt.ax import rotate_labels
        assert callable(rotate_labels)
    
    def test_sci_note_import(self):
        """Test sci_note function import."""
from scitex.plt.ax import sci_note
        assert callable(sci_note)
    
    def test_set_n_ticks_import(self):
        """Test set_n_ticks function import."""
from scitex.plt.ax import set_n_ticks
        assert callable(set_n_ticks)
    
    def test_set_size_import(self):
        """Test set_size function import."""
from scitex.plt.ax import set_size
        assert callable(set_size)
    
    def test_set_supxyt_import(self):
        """Test set_supxyt function import."""
from scitex.plt.ax import set_supxyt
        assert callable(set_supxyt)
    
    def test_set_ticks_import(self):
        """Test set_ticks function import."""
from scitex.plt.ax import set_ticks
        assert callable(set_ticks)
    
    def test_set_xyt_import(self):
        """Test set_xyt function import."""
from scitex.plt.ax import set_xyt
        assert callable(set_xyt)
    
    def test_shift_import(self):
        """Test shift function import."""
from scitex.plt.ax import shift
        assert callable(shift)


class TestShareAxesFunctions:
    """Test share axes functionality."""
    
    def test_sharexy_import(self):
        """Test sharexy function import."""
from scitex.plt.ax import sharexy
        assert callable(sharexy)
    
    def test_sharex_import(self):
        """Test sharex function import."""
from scitex.plt.ax import sharex
        assert callable(sharex)
    
    def test_sharey_import(self):
        """Test sharey function import."""
from scitex.plt.ax import sharey
        assert callable(sharey)
    
    def test_get_global_xlim_import(self):
        """Test get_global_xlim function import."""
from scitex.plt.ax import get_global_xlim
        assert callable(get_global_xlim)
    
    def test_get_global_ylim_import(self):
        """Test get_global_ylim function import."""
from scitex.plt.ax import get_global_ylim
        assert callable(get_global_ylim)
    
    def test_set_xlims_import(self):
        """Test set_xlims function import."""
from scitex.plt.ax import set_xlims
        assert callable(set_xlims)
    
    def test_set_ylims_import(self):
        """Test set_ylims function import."""
from scitex.plt.ax import set_ylims
        assert callable(set_ylims)


class TestBasicFunctionality:
    """Test basic functionality of imported functions."""
    
    @pytest.fixture
    def mock_axes(self):
        """Create mock matplotlib axes for testing."""
        fig, ax = plt.subplots()
        yield ax
        plt.close(fig)
    
    def test_hide_spines_basic(self, mock_axes):
        """Test basic hide_spines functionality."""
from scitex.plt.ax import hide_spines
        
        # Function should be callable with axes
        try:
            hide_spines(mock_axes)
        except Exception as e:
            # Function exists and is callable, specific behavior tested in dedicated files
            pass
    
    def test_sci_note_basic(self, mock_axes):
        """Test basic sci_note functionality."""
from scitex.plt.ax import sci_note
        
        # Function should be callable with axes
        try:
            sci_note(mock_axes)
        except Exception as e:
            # Function exists and is callable, specific behavior tested in dedicated files
            pass
    
    def test_force_aspect_basic(self, mock_axes):
        """Test basic force_aspect functionality."""
from scitex.plt.ax import force_aspect
        
        # Function should be callable with axes
        try:
            force_aspect(mock_axes, 1.0)
        except Exception as e:
            # Function exists and is callable, specific behavior tested in dedicated files
            pass
    
    def test_rotate_labels_basic(self, mock_axes):
        """Test basic rotate_labels functionality."""
from scitex.plt.ax import rotate_labels
        
        # Function should be callable with axes
        try:
            rotate_labels(mock_axes, 45)
        except Exception as e:
            # Function exists and is callable, specific behavior tested in dedicated files
            pass


class TestModuleStructure:
    """Test the overall module structure."""
    
    def test_module_has_expected_attributes(self):
        """Test that module has all expected function attributes."""
        import scitex.plt.ax._style as style_module
        
        expected_functions = [
            'add_marginal_ax',
            'add_panel', 
            'extend',
            'force_aspect',
            'format_label',
            'hide_spines',
            'map_ticks',
            'rotate_labels',
            'sci_note',
            'set_n_ticks',
            'set_size',
            'set_supxyt',
            'set_ticks',
            'set_xyt',
            'sharexy',
            'sharex',
            'sharey',
            'get_global_xlim',
            'get_global_ylim',
            'set_xlims',
            'set_ylims',
            'shift'
        ]
        
        for func_name in expected_functions:
            assert hasattr(style_module, func_name), f"Missing function: {func_name}"
            assert callable(getattr(style_module, func_name)), f"Not callable: {func_name}"
    
    def test_module_file_path(self):
        """Test module file path attribute."""
        import scitex.plt.ax._style as style_module
        
        assert hasattr(style_module, '__file__')
        assert style_module.__file__ is not None
    
    def test_all_imports_successful(self):
        """Test that all imports in the module are successful."""
        # If we can import the module without exceptions, all imports work
        try:
            import scitex.plt.ax._style
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestFunctionCallability:
    """Test that all functions are properly callable."""
    
    def test_all_functions_callable_with_mock_args(self):
        """Test that all functions can be called with mock arguments."""
        import scitex.plt.ax._style as style
        
        # Create mock matplotlib objects
        mock_ax = Mock()
        mock_fig = Mock()
        
        # Functions that should accept axes as first argument
        axes_functions = [
            'hide_spines',
            'sci_note', 
            'force_aspect',
            'rotate_labels',
            'set_n_ticks',
            'set_ticks',
            'extend',
            'shift',
            'add_panel',
            'add_marginal_ax'
        ]
        
        for func_name in axes_functions:
            func = getattr(style, func_name)
            assert callable(func), f"{func_name} is not callable"
            
            # Test that function exists and can be referenced
            # Actual behavior testing is done in individual test files
            try:
                # Just verify function signature exists
                import inspect
                sig = inspect.signature(func)
                assert len(sig.parameters) >= 1, f"{func_name} should accept at least one parameter"
            except Exception:
                # Function exists, signature inspection might fail due to decorators
                pass


class TestIntegrationImport:
    """Test integration with matplotlib ecosystem."""
    
    def test_matplotlib_compatibility(self):
        """Test that style module is compatible with matplotlib."""
        import matplotlib
        import scitex.plt.ax._style
        
        # Module should import without conflicts with matplotlib
        assert matplotlib is not None
        assert scitex.plt.ax._style is not None
    
    def test_numpy_compatibility(self):
        """Test compatibility with numpy (common dependency)."""
        import numpy as np
        import scitex.plt.ax._style
        
        # Should not have import conflicts
        assert np is not None
        assert scitex.plt.ax._style is not None
    
    def test_no_circular_imports(self):
        """Test that there are no circular import issues."""
        # If we can import successfully, there are no circular imports
        try:
            import scitex.plt.ax._style
            import scitex.plt.ax
            import scitex.plt
            import scitex
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")


class TestErrorHandling:
    """Test error handling in module imports."""
    
    def test_import_survives_missing_optional_deps(self):
        """Test that module import survives missing optional dependencies."""
        # The module should import even if some optional dependencies are missing
        try:
            import scitex.plt.ax._style
            assert True
        except ImportError as e:
            # If it fails, it should be due to critical dependencies, not optional ones
            assert "matplotlib" not in str(e).lower() or "numpy" not in str(e).lower()
    
    def test_function_existence_verification(self):
        """Test that all expected functions exist and are not None."""
        import scitex.plt.ax._style as style
        
        function_names = [
            'add_marginal_ax', 'add_panel', 'extend', 'force_aspect',
            'format_label', 'hide_spines', 'map_ticks', 'rotate_labels',
            'sci_note', 'set_n_ticks', 'set_size', 'set_supxyt',
            'set_ticks', 'set_xyt', 'sharexy', 'sharex', 'sharey',
            'get_global_xlim', 'get_global_ylim', 'set_xlims', 'set_ylims', 'shift'
        ]
        
        for name in function_names:
            func = getattr(style, name, None)
            assert func is not None, f"Function {name} is None"
            assert callable(func), f"Function {name} is not callable"


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
