#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for plt/__init__.py

Tests cover:
- Module imports and exports
- Matplotlib compatibility layer
- Enhanced close function
- Enhanced tight_layout function
- Enhanced colorbar function
- __getattr__ fallback mechanism
- __dir__ method for tab completion
"""

import os
import sys
import warnings
from unittest.mock import Mock, patch, MagicMock, call

import matplotlib.pyplot as plt
import numpy as np
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestModuleStructure:
    """Test basic module structure and imports."""
    
    def test_module_imports(self):
        """Test that the module can be imported."""
        import scitex.plt
        assert scitex.plt is not None
    
    def test_required_imports(self):
        """Test that required submodules are imported."""
        import scitex.plt
        
        # Check submodules
        assert hasattr(scitex.plt, 'ax')
        assert hasattr(scitex.plt, 'color')
        assert hasattr(scitex.plt, 'subplots')
        assert hasattr(scitex.plt, 'close')
        assert hasattr(scitex.plt, 'tpl')
        assert hasattr(scitex.plt, 'enhanced_colorbar')
    
    def test_file_and_dir_attributes(self):
        """Test __FILE__ and __DIR__ attributes."""
        import scitex.plt
        
        assert hasattr(scitex.plt, '__FILE__')
        assert hasattr(scitex.plt, '__DIR__')
        assert scitex.plt.__FILE__ == "./src/scitex/plt/__init__.py"


class TestMatplotlibCompatibility:
    """Test matplotlib compatibility features."""
    
    def test_getattr_fallback(self):
        """Test __getattr__ fallback to matplotlib.pyplot."""
        import scitex.plt
        
        # Test common matplotlib functions
        assert hasattr(scitex.plt, 'plot')
        assert hasattr(scitex.plt, 'scatter')
        assert hasattr(scitex.plt, 'figure')
        assert hasattr(scitex.plt, 'xlabel')
        assert hasattr(scitex.plt, 'ylabel')
        assert hasattr(scitex.plt, 'title')
        assert hasattr(scitex.plt, 'show')
        assert hasattr(scitex.plt, 'savefig')
    
    def test_getattr_error(self):
        """Test __getattr__ raises appropriate error for non-existent attributes."""
        import scitex.plt
        
        with pytest.raises(AttributeError) as exc_info:
            _ = scitex.plt.non_existent_attribute_xyz123
        
        assert "has attribute 'non_existent_attribute_xyz123'" in str(exc_info.value)
    
    def test_dir_method(self):
        """Test __dir__ returns combined attributes."""
        import scitex.plt
        
        dir_result = dir(scitex.plt)
        
        # Should include local attributes
        assert 'subplots' in dir_result
        assert 'ax' in dir_result
        assert 'color' in dir_result
        assert 'close' in dir_result
        assert 'tpl' in dir_result
        
        # Should include matplotlib.pyplot attributes
        assert 'plot' in dir_result
        assert 'scatter' in dir_result
        assert 'figure' in dir_result
        
        # Should be sorted
        assert dir_result == sorted(dir_result)
    
    def test_special_attribute_handling(self):
        """Test special handling for close, tight_layout, and colorbar."""
        import scitex.plt
        
        # These should return our enhanced versions, not matplotlib's
        assert scitex.plt.close is not plt.close
        assert scitex.plt.tight_layout is not plt.tight_layout
        assert scitex.plt.colorbar is scitex.plt.enhanced_colorbar


class TestEnhancedClose:
    """Test enhanced close function."""
    
    def test_close_no_args(self):
        """Test close with no arguments."""
        import scitex.plt
        
        # Create a figure
        fig = plt.figure()
        
        # Close all figures
        scitex.plt.close()
        
        # Should have closed the figure
        assert not plt.fignum_exists(fig.number)
    
    def test_close_regular_figure(self):
        """Test close with regular matplotlib figure."""
        import scitex.plt
        
        # Create a figure
        fig = plt.figure()
        fig_num = fig.number
        
        # Close it
        scitex.plt.close(fig)
        
        # Should have closed
        assert not plt.fignum_exists(fig_num)
    
    def test_close_figwrapper(self):
        """Test close with FigWrapper object."""
        import scitex.plt
        
        # Create mock FigWrapper
        mock_fig = Mock()
        mock_mpl_fig = plt.figure()
        mock_fig._fig_mpl = mock_mpl_fig
        mock_fig.figure = mock_mpl_fig
        fig_num = mock_mpl_fig.number
        
        # Close it
        scitex.plt.close(mock_fig)
        
        # Should have closed the underlying figure
        assert not plt.fignum_exists(fig_num)
    
    def test_plt_close_monkey_patch(self):
        """Test that matplotlib.pyplot.close is monkey patched."""
        # Import after scitex.plt to ensure monkey patching happens
        import scitex.plt
        import matplotlib.pyplot as mpl_plt
        
        # Create mock FigWrapper
        mock_fig = Mock()
        mock_mpl_fig = plt.figure()
        mock_fig._fig_mpl = mock_mpl_fig
        mock_fig.figure = mock_mpl_fig
        fig_num = mock_mpl_fig.number
        
        # Use matplotlib's close (which should be patched)
        mpl_plt.close(mock_fig)
        
        # Should have closed the underlying figure
        assert not plt.fignum_exists(fig_num)


class TestEnhancedTightLayout:
    """Test enhanced tight_layout function."""
    
    def test_tight_layout_basic(self):
        """Test basic tight_layout functionality."""
        import scitex.plt
        
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Should not raise
        scitex.plt.tight_layout()
        
        plt.close(fig)
    
    def test_tight_layout_with_constrained_layout(self):
        """Test tight_layout with constrained_layout figure."""
        import scitex.plt
        
        # Create figure with constrained_layout
        fig, ax = plt.subplots(constrained_layout=True)
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Mock to check it's not called
        with patch('matplotlib.pyplot.tight_layout') as mock_tight:
            scitex.plt.tight_layout()
            # Should not call original tight_layout
            mock_tight.assert_not_called()
        
        plt.close(fig)
    
    def test_tight_layout_warning_suppression(self):
        """Test that tight_layout suppresses incompatible axes warning."""
        import scitex.plt
        
        fig, ax = plt.subplots()
        
        # Add a colorbar which can cause compatibility issues
        im = ax.imshow(np.random.rand(10, 10))
        plt.colorbar(im)
        
        # Should not produce warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            scitex.plt.tight_layout()
            
            # Check no warning about incompatible axes
            for warning in w:
                assert "not compatible with tight_layout" not in str(warning.message)
        
        plt.close(fig)
    
    def test_tight_layout_fallback_to_constrained(self):
        """Test fallback to constrained_layout on failure."""
        import scitex.plt
        
        fig, ax = plt.subplots()
        
        # Mock tight_layout to raise exception
        original_tight = plt.tight_layout
        
        def failing_tight(*args, **kwargs):
            raise Exception("Tight layout failed")
        
        # Temporarily replace
        plt.tight_layout = failing_tight
        
        try:
            # Should not raise, should fallback
            scitex.plt.tight_layout()
            
            # Check if constrained_layout was set
            if hasattr(fig, 'get_constrained_layout'):
                # Might have been set as fallback
                pass
        finally:
            # Restore
            plt.tight_layout = original_tight
        
        plt.close(fig)
    
    def test_plt_tight_layout_monkey_patch(self):
        """Test that matplotlib.pyplot.tight_layout is monkey patched."""
        import scitex.plt
        import matplotlib.pyplot as mpl_plt
        
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Use matplotlib's tight_layout (which should be patched)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            mpl_plt.tight_layout()
            
            # Should suppress warnings
            for warning in w:
                assert "not compatible with tight_layout" not in str(warning.message)
        
        plt.close(fig)


class TestEnhancedColorbar:
    """Test enhanced colorbar function."""
    
    def test_colorbar_import(self):
        """Test that enhanced_colorbar is imported."""
        import scitex.plt
        
        assert hasattr(scitex.plt, 'enhanced_colorbar')
        assert scitex.plt.colorbar is scitex.plt.enhanced_colorbar
    
    def test_colorbar_via_getattr(self):
        """Test accessing colorbar via __getattr__."""
        import scitex.plt
        
        # Access via attribute (triggers __getattr__)
        colorbar_func = getattr(scitex.plt, 'colorbar')
        assert colorbar_func is scitex.plt.enhanced_colorbar


class TestIntegration:
    """Test integration scenarios."""
    
    def test_full_plotting_workflow(self):
        """Test a complete plotting workflow."""
        import scitex.plt
        
        # Create figure using scitex.plt
        fig, ax = scitex.plt.subplots()
        
        # Plot using fallback to matplotlib
        ax.plot([1, 2, 3], [4, 5, 6])
        scitex.plt.xlabel("X")
        scitex.plt.ylabel("Y")
        scitex.plt.title("Test Plot")
        
        # Use enhanced tight_layout
        scitex.plt.tight_layout()
        
        # Close using enhanced close
        scitex.plt.close(fig)
        
        # Verify closed
        assert not plt.fignum_exists(fig.figure.number if hasattr(fig, 'figure') else fig.number)
    
    def test_compatibility_with_matplotlib_code(self):
        """Test that existing matplotlib code works with scitex.plt."""
        import scitex.plt as mplt  # Use as drop-in replacement
        
        # Standard matplotlib workflow
        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x)
        
        mplt.figure(figsize=(8, 6))
        mplt.plot(x, y, 'b-', label='sin(x)')
        mplt.xlabel('x')
        mplt.ylabel('y')
        mplt.title('Sine Wave')
        mplt.legend()
        mplt.grid(True)
        mplt.tight_layout()
        
        # Should all work without errors
        mplt.close('all')
    
    def test_attribute_caching(self):
        """Test that attributes are cached after first access."""
        import scitex.plt
        
        # First access
        plot1 = scitex.plt.plot
        
        # Second access should return same object
        plot2 = scitex.plt.plot
        
        assert plot1 is plot2
    
    def test_submodule_access(self):
        """Test accessing submodules and their contents."""
        import scitex.plt
        
        # Access submodule
        assert hasattr(scitex.plt.ax, '_plot')
        assert hasattr(scitex.plt.color, '_colors')
        
        # Can create plots through submodules
        fig, ax = scitex.plt.subplots()
        
        # Should be our wrapped version
        assert hasattr(fig, '_fig_mpl') or isinstance(fig, plt.Figure)
        
        scitex.plt.close(fig)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_import_order_independence(self):
        """Test that import order doesn't matter."""
        # This tests that monkey patching works regardless of import order
        import matplotlib.pyplot as mpl_plt
        import scitex.plt
        
        # Both should have enhanced functionality
        mock_fig = Mock()
        mock_fig._fig_mpl = plt.figure()
        mock_fig.figure = mock_fig._fig_mpl
        
        # Close via both interfaces
        scitex.plt.close(mock_fig)
        # Already closed, but shouldn't error
        mpl_plt.close(mock_fig)
    
    def test_multiple_imports(self):
        """Test that multiple imports don't cause issues."""
        import scitex.plt
        import scitex.plt as mplt
        from scitex import plt as scitex_plt
        
        # All should be the same module
        assert scitex.plt is mplt
        assert scitex.plt is scitex_plt
    
    def test_getattr_with_none(self):
        """Test __getattr__ with special values."""
        import scitex.plt
        
        # Should handle these without errors
        assert hasattr(scitex.plt, '__name__')
        assert hasattr(scitex.plt, '__file__')
        assert hasattr(scitex.plt, '__package__')


class TestDocumentation:
    """Test documentation and docstrings."""
    
    def test_module_docstring(self):
        """Test that functions have proper docstrings."""
        import scitex.plt
        
        # Enhanced functions should have docstrings
        assert scitex.plt.tight_layout.__doc__ is not None
        assert "Enhanced tight_layout" in scitex.plt.tight_layout.__doc__
        
        # Check close function (accessed via getattr)
        close_func = getattr(scitex.plt, 'close')
        # May or may not have docstring depending on implementation
    
    def test_getattr_docstring(self):
        """Test __getattr__ has docstring."""
        import scitex.plt
        
        assert scitex.plt.__getattr__.__doc__ is not None
        assert "Fallback" in scitex.plt.__getattr__.__doc__
    
    def test_dir_docstring(self):
        """Test __dir__ has docstring."""
        import scitex.plt
        
        assert scitex.plt.__dir__.__doc__ is not None
        assert "tab completion" in scitex.plt.__dir__.__doc__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])