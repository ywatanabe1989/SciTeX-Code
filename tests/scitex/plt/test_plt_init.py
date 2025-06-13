#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 04:15:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/test___init__.py

"""Comprehensive tests for scitex.plt module initialization and matplotlib compatibility."""

import pytest
import sys
import importlib
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock, call
import warnings
import numpy as np
import io
import contextlib


class TestPltModuleImports:
    """Test basic imports and module structure."""
    
    def test_module_imports_successfully(self):
        """Test that scitex.plt module can be imported."""
        import scitex.plt
        assert scitex.plt is not None
        
    def test_submodule_imports(self):
        """Test that submodules are imported correctly."""
        import scitex.plt
        
        # Check required imports
        assert hasattr(scitex.plt, 'subplots')
        assert hasattr(scitex.plt, 'ax')
        assert hasattr(scitex.plt, 'color')
        assert hasattr(scitex.plt, 'close')
        assert hasattr(scitex.plt, 'tpl')
        assert hasattr(scitex.plt, 'enhanced_colorbar')
        
    def test_module_attributes(self):
        """Test module attributes."""
        import scitex.plt
        
        assert hasattr(scitex.plt, '__FILE__')
        assert hasattr(scitex.plt, '__DIR__')
        assert scitex.plt.__FILE__ == "./src/scitex/plt/__init__.py"
        
    def test_matplotlib_import(self):
        """Test that matplotlib is properly imported as _counter_part."""
        import scitex.plt
        
        # Check internal reference to matplotlib
        assert hasattr(scitex.plt, '_counter_part')
        assert scitex.plt._counter_part is plt


class TestMatplotlibCompatibility:
    """Test matplotlib compatibility features."""
    
    def test_getattr_fallback(self):
        """Test __getattr__ fallback to matplotlib.pyplot."""
        import scitex.plt
        
        # Test accessing matplotlib functions through scitex.plt
        assert hasattr(scitex.plt, 'plot')  # matplotlib function
        assert hasattr(scitex.plt, 'scatter')  # matplotlib function
        assert hasattr(scitex.plt, 'xlabel')  # matplotlib function
        
        # These should be the same as matplotlib's
        assert scitex.plt.plot is plt.plot
        assert scitex.plt.scatter is plt.scatter
        assert scitex.plt.xlabel is plt.xlabel
        
    def test_getattr_special_handling(self):
        """Test special handling in __getattr__ for enhanced functions."""
        import scitex.plt
        
        # Test close returns scitex version
        close_func = getattr(scitex.plt, 'close')
        assert close_func is scitex.plt.close
        
        # Test tight_layout returns enhanced version
        tight_layout_func = getattr(scitex.plt, 'tight_layout')
        assert tight_layout_func is scitex.plt.tight_layout
        
        # Test colorbar returns enhanced version
        colorbar_func = getattr(scitex.plt, 'colorbar')
        assert colorbar_func is scitex.plt.enhanced_colorbar
        
    def test_getattr_nonexistent(self):
        """Test __getattr__ raises AttributeError for nonexistent attributes."""
        import scitex.plt
        
        with pytest.raises(AttributeError) as exc_info:
            scitex.plt.nonexistent_function
            
        assert "has attribute 'nonexistent_function'" in str(exc_info.value)
        
    def test_dir_function(self):
        """Test __dir__ returns combined attributes."""
        import scitex.plt
        
        dir_result = dir(scitex.plt)
        
        # Should include local attributes
        assert 'subplots' in dir_result
        assert 'ax' in dir_result
        assert 'color' in dir_result
        assert 'close' in dir_result
        assert 'tpl' in dir_result
        
        # Should include matplotlib attributes
        assert 'plot' in dir_result
        assert 'scatter' in dir_result
        assert 'figure' in dir_result
        assert 'xlabel' in dir_result
        
        # Should be sorted
        assert dir_result == sorted(dir_result)
        
    def test_compatibility_check(self):
        """Test that scitex.plt is compatible with matplotlib.pyplot."""
        import scitex.plt
        
        # Get all matplotlib.pyplot attributes
        pyplot_attrs = set(dir(plt))
        
        # Get all scitex.plt attributes
        scitex_attrs = set(dir(scitex.plt))
        
        # All pyplot attributes should be accessible through scitex.plt
        for attr in pyplot_attrs:
            if not attr.startswith('_'):  # Skip private attributes
                assert hasattr(scitex.plt, attr), f"Missing matplotlib attribute: {attr}"


class TestEnhancedClose:
    """Test enhanced close functionality."""
    
    def test_enhanced_close_patched(self):
        """Test that matplotlib's close is patched."""
        import scitex.plt
        
        # Check that close was patched
        assert plt.close != scitex.plt._original_close
        assert plt.close is scitex.plt._enhanced_close
        
    def test_enhanced_close_no_args(self):
        """Test enhanced close with no arguments."""
        import scitex.plt
        
        with patch.object(scitex.plt, '_original_close') as mock_close:
            plt.close()
            mock_close.assert_called_once_with()
            
    def test_enhanced_close_regular_figure(self):
        """Test enhanced close with regular matplotlib figure."""
        import scitex.plt
        
        fig = MagicMock()
        
        with patch.object(scitex.plt, '_original_close') as mock_close:
            plt.close(fig)
            mock_close.assert_called_once_with(fig)
            
    def test_enhanced_close_figwrapper(self):
        """Test enhanced close with FigWrapper object."""
        import scitex.plt
        
        # Create mock FigWrapper
        fig_wrapper = MagicMock()
        fig_wrapper._fig_mpl = True
        fig_wrapper.figure = MagicMock()
        
        with patch.object(scitex.plt, '_original_close') as mock_close:
            plt.close(fig_wrapper)
            # Should close the underlying figure
            mock_close.assert_called_once_with(fig_wrapper.figure)
            
    def test_enhanced_close_integration(self):
        """Test enhanced close in real scenario."""
        import scitex.plt
        
        # Create a real figure
        fig = plt.figure()
        
        # Close it
        plt.close(fig)
        
        # Figure should be closed
        assert not plt.fignum_exists(fig.number)


class TestEnhancedTightLayout:
    """Test enhanced tight_layout functionality."""
    
    def test_tight_layout_patched(self):
        """Test that matplotlib's tight_layout is patched."""
        import scitex.plt
        
        # Check that tight_layout was patched
        assert plt.tight_layout != scitex.plt._original_tight_layout
        assert plt.tight_layout is scitex.plt.tight_layout
        
    def test_tight_layout_normal_case(self):
        """Test tight_layout in normal case."""
        import scitex.plt
        
        fig = MagicMock()
        fig.get_constrained_layout.return_value = False
        
        with patch('matplotlib.pyplot.gcf', return_value=fig):
            with patch.object(scitex.plt, '_original_tight_layout') as mock_tight:
                plt.tight_layout()
                mock_tight.assert_called_once()
                
    def test_tight_layout_with_constrained_layout(self):
        """Test tight_layout when figure uses constrained_layout."""
        import scitex.plt
        
        fig = MagicMock()
        fig.get_constrained_layout.return_value = True
        
        with patch('matplotlib.pyplot.gcf', return_value=fig):
            with patch.object(scitex.plt, '_original_tight_layout') as mock_tight:
                plt.tight_layout()
                # Should not call original tight_layout
                mock_tight.assert_not_called()
                
    def test_tight_layout_warning_suppression(self):
        """Test that tight_layout suppresses specific warnings."""
        import scitex.plt
        
        fig = MagicMock()
        fig.get_constrained_layout.return_value = False
        
        # Create a warning scenario
        def mock_tight_with_warning(*args, **kwargs):
            warnings.warn("This figure includes Axes that are not compatible with tight_layout")
            
        with patch('matplotlib.pyplot.gcf', return_value=fig):
            with patch.object(scitex.plt, '_original_tight_layout', side_effect=mock_tight_with_warning):
                # Should not raise warning
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    plt.tight_layout()
                    
                    # No warnings should be recorded
                    assert len(w) == 0
                    
    def test_tight_layout_fallback_to_constrained(self):
        """Test fallback to constrained_layout when tight_layout fails."""
        import scitex.plt
        
        fig = MagicMock()
        fig.get_constrained_layout.return_value = False
        
        with patch('matplotlib.pyplot.gcf', return_value=fig):
            with patch.object(scitex.plt, '_original_tight_layout', side_effect=Exception("Layout failed")):
                # Should try to set constrained_layout
                plt.tight_layout()
                
                fig.set_constrained_layout.assert_called_once_with(True)
                fig.set_constrained_layout_pads.assert_called_once()
                
    def test_tight_layout_complete_failure(self):
        """Test when both tight_layout and constrained_layout fail."""
        import scitex.plt
        
        fig = MagicMock()
        fig.get_constrained_layout.return_value = False
        fig.set_constrained_layout.side_effect = Exception("Constrained layout failed")
        
        with patch('matplotlib.pyplot.gcf', return_value=fig):
            with patch.object(scitex.plt, '_original_tight_layout', side_effect=Exception("Layout failed")):
                # Should not raise exception
                plt.tight_layout()
                
                # Both methods should have been tried
                fig.set_constrained_layout.assert_called_once()


class TestModuleOrganization:
    """Test module organization and structure."""
    
    def test_local_module_attributes(self):
        """Test _local_module_attributes is set correctly."""
        import scitex.plt
        
        assert hasattr(scitex.plt, '_local_module_attributes')
        assert isinstance(scitex.plt._local_module_attributes, list)
        
        # Should include our custom attributes
        local_attrs = scitex.plt._local_module_attributes
        assert 'subplots' in local_attrs or 'subplots' in globals()
        
    def test_no_import_side_effects(self):
        """Test that importing doesn't have side effects."""
        # Capture output during import
        f = io.StringIO()
        
        # Remove from cache to force fresh import
        if 'scitex.plt' in sys.modules:
            del sys.modules['scitex.plt']
            
        with contextlib.redirect_stdout(f):
            with contextlib.redirect_stderr(f):
                import scitex.plt
                
        output = f.getvalue()
        
        # Should not print anything
        assert output == ""
        
    def test_submodule_types(self):
        """Test types of imported submodules."""
        import scitex.plt
        
        # ax and color should be modules
        assert hasattr(scitex.plt.ax, '__name__')
        assert hasattr(scitex.plt.color, '__name__')
        
        # Functions should be callable
        assert callable(scitex.plt.subplots)
        assert callable(scitex.plt.close)
        assert callable(scitex.plt.tpl)
        assert callable(scitex.plt.enhanced_colorbar)


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_basic_plotting_workflow(self):
        """Test basic plotting workflow using scitex.plt."""
        import scitex.plt
        
        # Should work just like matplotlib
        fig, ax = scitex.plt.subplots()
        
        # Plot some data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        
        # Set labels (using matplotlib compatibility)
        scitex.plt.xlabel('X axis')
        scitex.plt.ylabel('Y axis')
        scitex.plt.title('Test Plot')
        
        # Close figure
        scitex.plt.close(fig)
        
    def test_enhanced_features_workflow(self):
        """Test workflow using enhanced features."""
        import scitex.plt
        
        # Create figure
        fig, ax = scitex.plt.subplots()
        
        # Add some content that might cause tight_layout issues
        im = ax.imshow(np.random.rand(10, 10))
        
        # Add colorbar using enhanced version
        cbar = scitex.plt.colorbar(im)
        
        # Use enhanced tight_layout (should handle colorbar)
        scitex.plt.tight_layout()
        
        # Close using enhanced close
        scitex.plt.close(fig)
        
    def test_module_reload(self):
        """Test that module can be reloaded."""
        import scitex.plt
        
        # Store reference to a function
        original_subplots = scitex.plt.subplots
        
        # Reload module
        importlib.reload(scitex.plt)
        
        # Should still have all functions
        assert hasattr(scitex.plt, 'subplots')
        assert hasattr(scitex.plt, 'close')
        assert hasattr(scitex.plt, 'tight_layout')
        
        # Matplotlib compatibility should still work
        assert hasattr(scitex.plt, 'plot')
        assert hasattr(scitex.plt, 'scatter')


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_attribute_error_message(self):
        """Test that AttributeError has helpful message."""
        import scitex.plt
        
        with pytest.raises(AttributeError) as exc_info:
            scitex.plt.completely_fake_function
            
        error_msg = str(exc_info.value)
        assert "module 'scitex.plt'" in error_msg
        assert "matplotlib.pyplot" in error_msg
        assert "completely_fake_function" in error_msg
        
    def test_no_attribute_leakage(self):
        """Test that private attributes aren't exposed."""
        import scitex.plt
        
        # Private attributes should not be accessible through __getattr__
        with pytest.raises(AttributeError):
            scitex.plt._some_private_attr
            
    def test_import_error_handling(self):
        """Test handling of import errors."""
        # This tests the robustness of the module structure
        import scitex.plt
        
        # Even if submodules have issues, main module should work
        assert scitex.plt is not None
        assert callable(getattr(scitex.plt, '__getattr__', None))
        assert callable(getattr(scitex.plt, '__dir__', None))


class TestPerformance:
    """Test performance-related aspects."""
    
    def test_import_time(self):
        """Test that module imports quickly."""
        import time
        
        # Remove from cache
        if 'scitex.plt' in sys.modules:
            del sys.modules['scitex.plt']
            
        start = time.time()
        import scitex.plt
        end = time.time()
        
        # Should import reasonably fast
        assert (end - start) < 2.0  # 2 seconds is generous
        
    def test_attribute_access_performance(self):
        """Test that attribute access is efficient."""
        import scitex.plt
        import time
        
        # Access matplotlib function many times
        start = time.time()
        for _ in range(1000):
            _ = scitex.plt.plot
        end = time.time()
        
        # Should be fast (caching should help)
        assert (end - start) < 0.1  # 100ms for 1000 accesses
        
    def test_dir_performance(self):
        """Test that dir() is reasonably fast."""
        import scitex.plt
        import time
        
        start = time.time()
        for _ in range(100):
            _ = dir(scitex.plt)
        end = time.time()
        
        # Should be reasonably fast
        assert (end - start) < 1.0  # 1 second for 100 calls


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
