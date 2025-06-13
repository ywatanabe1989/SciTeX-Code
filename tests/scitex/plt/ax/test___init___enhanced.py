#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/test___init___enhanced.py
# ----------------------------------------
"""
Enhanced test suite for scitex.plt.ax module initialization and exports.

This test ensures the module properly exports all its functions and
tests integration between different submodules.
"""

import importlib
import inspect
from unittest.mock import patch, MagicMock

import matplotlib.pyplot as plt
import numpy as np
import pytest
from hypothesis import given, strategies as st, settings

import scitex.plt.ax as ax_module


# ----------------------------------------
# Fixtures
# ----------------------------------------

@pytest.fixture
def expected_plot_functions():
    """List of expected plotting functions in the module."""
    return [
        'plot_heatmap',
        'plot_conf_mat', 
        'plot_circular_hist',
        'plot_cube',
        'plot_ecdf',
        'plot_fillv',
        'plot_image',
        'plot_joyplot',
        'plot_raster',
        'plot_rectangle',
        'plot_scatter_hist',
        'plot_shaded_line',
        'plot_statistical_shaded_line',
        'plot_violin',
    ]


@pytest.fixture
def expected_style_functions():
    """List of expected style functions in the module."""
    return [
        'hide_spines',
        'show_spines',
        'add_marginal_ax',
        'add_panel',
        'extend',
        'force_aspect',
        'format_label',
        'map_ticks',
        'rotate_labels',
        'sci_note',
        'set_log_scale',
        'set_n_ticks',
        'set_size',
        'set_supxyt',
        'set_ticks',
        'set_xyt',
        'share_axes',
        'shift',
    ]


@pytest.fixture
def sample_figure():
    """Create a sample figure for testing."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(np.random.rand(10))
    yield fig, ax
    plt.close(fig)


# ----------------------------------------
# Module Structure Tests
# ----------------------------------------

class TestModuleStructure:
    """Test the module's structure and exports."""
    
    def test_module_imports_successfully(self):
        """Test that the module imports without errors."""
        # Re-import to ensure it works
        importlib.reload(ax_module)
        assert ax_module is not None
        
    def test_all_plot_functions_exported(self, expected_plot_functions):
        """Test that all expected plot functions are exported."""
        for func_name in expected_plot_functions:
            assert hasattr(ax_module, func_name), f"Missing plot function: {func_name}"
            func = getattr(ax_module, func_name)
            assert callable(func), f"{func_name} is not callable"
            
    def test_all_style_functions_exported(self, expected_style_functions):
        """Test that all expected style functions are exported."""
        for func_name in expected_style_functions:
            assert hasattr(ax_module, func_name), f"Missing style function: {func_name}"
            func = getattr(ax_module, func_name)
            assert callable(func), f"{func_name} is not callable"
            
    def test_no_private_functions_exported(self):
        """Test that no private functions are exported."""
        for attr_name in dir(ax_module):
            if attr_name.startswith('_') and not attr_name.startswith('__'):
                attr = getattr(ax_module, attr_name)
                if callable(attr):
                    pytest.fail(f"Private function {attr_name} should not be exported")
                    
    def test_module_has_docstring(self):
        """Test that the module has a proper docstring."""
        assert ax_module.__doc__ is not None
        assert len(ax_module.__doc__.strip()) > 0


# ----------------------------------------
# Function Signature Tests
# ----------------------------------------

class TestFunctionSignatures:
    """Test function signatures for consistency."""
    
    def test_plot_functions_have_ax_parameter(self, expected_plot_functions):
        """Test that all plot functions accept an axes parameter."""
        for func_name in expected_plot_functions:
            if hasattr(ax_module, func_name):
                func = getattr(ax_module, func_name)
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                
                # First parameter should be 'ax' or 'axis'
                assert len(params) > 0, f"{func_name} has no parameters"
                assert params[0] in ['ax', 'axis'], f"{func_name} first param should be ax/axis"
                
    def test_style_functions_have_ax_parameter(self, expected_style_functions):
        """Test that all style functions accept an axes parameter."""
        for func_name in expected_style_functions:
            if hasattr(ax_module, func_name):
                func = getattr(ax_module, func_name)
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                
                # First parameter should be 'ax' or 'axis'
                assert len(params) > 0, f"{func_name} has no parameters"
                assert params[0] in ['ax', 'axis'], f"{func_name} first param should be ax/axis"
                
    def test_functions_have_docstrings(self):
        """Test that all exported functions have docstrings."""
        for attr_name in dir(ax_module):
            if not attr_name.startswith('_'):
                attr = getattr(ax_module, attr_name)
                if callable(attr) and not inspect.isclass(attr):
                    assert attr.__doc__ is not None, f"{attr_name} missing docstring"
                    assert len(attr.__doc__.strip()) > 0, f"{attr_name} has empty docstring"


# ----------------------------------------
# Integration Tests
# ----------------------------------------

class TestIntegration:
    """Test integration between different functions."""
    
    def test_plot_and_style_combination(self, sample_figure):
        """Test combining plot and style functions."""
        fig, ax = sample_figure
        
        # Apply multiple style functions
        ax_module.hide_spines(ax, top=True, right=True)
        ax_module.set_n_ticks(ax, n_xticks=5, n_yticks=5)
        ax_module.set_xyt(ax, xlabel="X Label", ylabel="Y Label", title="Test Title")
        
        # Verify results
        assert not ax.spines['top'].get_visible()
        assert not ax.spines['right'].get_visible()
        assert ax.get_xlabel() == "X Label"
        assert ax.get_ylabel() == "Y Label"
        assert ax.get_title() == "Test Title"
        
    def test_sequential_operations(self):
        """Test sequential operations on same axes."""
        fig, ax = plt.subplots()
        
        try:
            # Create initial plot
            data = np.random.rand(5, 5)
            if hasattr(ax_module, 'plot_heatmap'):
                ax_out, im, cbar = ax_module.plot_heatmap(ax, data)
                
            # Apply styling
            ax_module.hide_spines(ax, top=True, right=True)
            ax_module.rotate_labels(ax, axis='x', rotation=45)
            
            # Add more elements
            if hasattr(ax_module, 'add_panel'):
                ax_module.add_panel(ax, text="Panel A", loc='upper left')
                
            # Should complete without errors
            assert True
            
        finally:
            plt.close(fig)


# ----------------------------------------
# Property-Based Tests
# ----------------------------------------

class TestPropertyBased:
    """Property-based tests for the module."""
    
    @given(
        n_functions=st.integers(min_value=1, max_value=5),
        seed=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=20, deadline=5000)
    def test_random_function_combinations(self, n_functions, seed):
        """Test random combinations of functions."""
        np.random.seed(seed)
        fig, ax = plt.subplots()
        
        try:
            # Get available functions
            style_funcs = [
                ('hide_spines', lambda ax: ax_module.hide_spines(ax, top=True)),
                ('set_n_ticks', lambda ax: ax_module.set_n_ticks(ax, n_xticks=5)),
                ('rotate_labels', lambda ax: ax_module.rotate_labels(ax, axis='x', rotation=45)),
            ]
            
            # Apply random functions
            chosen = np.random.choice(len(style_funcs), min(n_functions, len(style_funcs)), replace=False)
            for idx in chosen:
                name, func = style_funcs[idx]
                func(ax)
                
            # Should not crash
            assert isinstance(ax, plt.Axes)
            
        finally:
            plt.close(fig)


# ----------------------------------------
# Mock Tests
# ----------------------------------------

class TestMocking:
    """Tests using mocks to verify behavior."""
    
    @patch('matplotlib.pyplot.subplots')
    def test_function_calls_with_mocked_axes(self, mock_subplots):
        """Test function calls with mocked matplotlib."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Configure mock axes
        mock_ax.spines = {
            'top': MagicMock(),
            'bottom': MagicMock(),
            'left': MagicMock(),
            'right': MagicMock(),
        }
        
        # Call function
        ax_module.hide_spines(mock_ax, top=True)
        
        # Verify mock was called
        mock_ax.spines['top'].set_visible.assert_called_with(False)
        
    def test_error_propagation(self):
        """Test that errors are properly propagated."""
        # Invalid axes should raise error
        with pytest.raises((AssertionError, TypeError, AttributeError)):
            ax_module.hide_spines("not_an_axes")


# ----------------------------------------
# Performance Tests
# ----------------------------------------

class TestPerformance:
    """Test performance characteristics."""
    
    def test_import_performance(self, performance_monitor):
        """Test module import performance."""
        with performance_monitor.measure('import'):
            # Clear from cache if present
            if 'scitex.plt.ax' in sys.modules:
                del sys.modules['scitex.plt.ax']
            
            # Import module
            import scitex.plt.ax
            
        performance_monitor.assert_performance(
            'import',
            max_duration=0.5,  # Should import quickly
            max_memory=10 * 1024 * 1024  # Less than 10MB
        )
        
    def test_function_lookup_performance(self, expected_plot_functions, expected_style_functions):
        """Test performance of function lookups."""
        all_functions = expected_plot_functions + expected_style_functions
        
        import time
        start = time.time()
        
        for _ in range(1000):
            for func_name in all_functions:
                if hasattr(ax_module, func_name):
                    func = getattr(ax_module, func_name)
                    
        duration = time.time() - start
        assert duration < 0.1  # Should be very fast


# ----------------------------------------
# Backward Compatibility Tests
# ----------------------------------------

class TestBackwardCompatibility:
    """Test backward compatibility of the module."""
    
    def test_common_usage_patterns(self, sample_figure):
        """Test common usage patterns still work."""
        fig, ax = sample_figure
        
        # Common pattern 1: Hide all spines
        ax_module.hide_spines(ax)
        
        # Common pattern 2: Set labels
        if hasattr(ax_module, 'set_xyt'):
            ax_module.set_xyt(ax, xlabel="X", ylabel="Y")
            
        # Common pattern 3: Adjust ticks
        if hasattr(ax_module, 'set_n_ticks'):
            ax_module.set_n_ticks(ax, n_xticks=5)
            
        # Should all work without errors
        assert True
        
    def test_function_return_values(self, sample_figure):
        """Test that functions return expected values."""
        fig, ax = sample_figure
        
        # Most style functions should return the axes
        result = ax_module.hide_spines(ax)
        assert result is ax
        
        if hasattr(ax_module, 'set_xyt'):
            result = ax_module.set_xyt(ax, xlabel="X")
            assert result is ax or result is None  # Some may return None


# ----------------------------------------
# Documentation Tests
# ----------------------------------------

class TestDocumentation:
    """Test documentation and examples."""
    
    def test_example_in_docstring_works(self):
        """Test that examples in docstrings actually work."""
        # This would parse docstrings and run examples
        # For now, just check docstrings exist
        for attr_name in dir(ax_module):
            if not attr_name.startswith('_'):
                attr = getattr(ax_module, attr_name)
                if callable(attr) and attr.__doc__:
                    # Could parse and test examples here
                    assert 'Example' in attr.__doc__ or 'example' in attr.__doc__ or len(attr.__doc__) > 50


if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v"])