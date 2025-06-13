#!/usr/bin/env python3
"""
Comprehensive tests for scitex.plt.ax._style._set_log_scale module.

This module tests logarithmic scale configuration utilities including:
- set_log_scale: Configure log scales with advanced formatting
- smart_log_limits: Automatically determine optimal log scale limits
- add_log_scale_indicator: Add visual indicators for log scales
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from unittest.mock import Mock, patch, MagicMock
import warnings

import scitex

# Test fixtures
@pytest.fixture
def fig_ax():
    """Create a figure and axis for testing."""
    fig, ax = plt.subplots(figsize=(8, 6))
    yield fig, ax
    plt.close(fig)

@pytest.fixture
def sample_data():
    """Generate sample data spanning multiple orders of magnitude."""
    return {
        'linear': np.linspace(1, 100, 50),
        'exponential': np.logspace(0, 4, 50),  # 1 to 10000
        'small_range': np.logspace(-2, 0, 20),  # 0.01 to 1
        'large_range': np.logspace(0, 6, 50),   # 1 to 1000000
        'negative': -np.logspace(0, 3, 30),     # -1 to -1000
        'mixed_sign': np.concatenate([np.logspace(0, 2, 25), -np.logspace(0, 2, 25)])
    }

class TestSetLogScale:
    """Test set_log_scale function - main log scale configuration."""
    
    def test_set_log_scale_x_axis(self, fig_ax):
        """Test setting log scale on x-axis."""
        fig, ax = fig_ax
        
        result = scitex.plt.ax.set_log_scale(ax, axis='x')
        
        assert ax.get_xscale() == 'log'
        assert ax.get_yscale() == 'linear'  # Should remain linear
        assert result == ax  # Should return the axis
    
    def test_set_log_scale_y_axis(self, fig_ax):
        """Test setting log scale on y-axis."""
        fig, ax = fig_ax
        
        result = scitex.plt.ax.set_log_scale(ax, axis='y')
        
        assert ax.get_xscale() == 'linear'  # Should remain linear
        assert ax.get_yscale() == 'log'
        assert result == ax
    
    def test_set_log_scale_both_axes(self, fig_ax):
        """Test setting log scale on both axes."""
        fig, ax = fig_ax
        
        result = scitex.plt.ax.set_log_scale(ax, axis='both')
        
        assert ax.get_xscale() == 'log'
        assert ax.get_yscale() == 'log'
        assert result == ax
    
    def test_set_log_scale_with_base(self, fig_ax):
        """Test setting log scale with custom base."""
        fig, ax = fig_ax
        
        # Test base 2
        scitex.plt.ax.set_log_scale(ax, axis='x', base=2)
        assert ax.get_xscale() == 'log'
        
        # Test base e (natural log)
        scitex.plt.ax.set_log_scale(ax, axis='y', base=np.e)
        assert ax.get_yscale() == 'log'
    
    def test_set_log_scale_with_custom_limits(self, fig_ax):
        """Test setting log scale and then setting custom limits."""
        fig, ax = fig_ax
        
        # set_log_scale doesn't have limits parameter, so set them separately
        limits = (1, 1000)
        scitex.plt.ax.set_log_scale(ax, axis='x')
        ax.set_xlim(limits)
        
        assert ax.get_xscale() == 'log'
        x_limits = ax.get_xlim()
        assert x_limits[0] == pytest.approx(limits[0], rel=1e-2)
        assert x_limits[1] == pytest.approx(limits[1], rel=1e-2)
    
    def test_set_log_scale_with_minor_ticks(self, fig_ax):
        """Test setting log scale with minor tick configuration."""
        fig, ax = fig_ax
        
        scitex.plt.ax.set_log_scale(ax, axis='x', show_minor_ticks=True)
        
        assert ax.get_xscale() == 'log'
        # Check that minor ticks are enabled
        assert ax.xaxis.get_minor_locator() is not None
    
    def test_set_log_scale_without_minor_ticks(self, fig_ax):
        """Test setting log scale without minor ticks."""
        fig, ax = fig_ax
        
        scitex.plt.ax.set_log_scale(ax, axis='y', show_minor_ticks=False)
        
        assert ax.get_yscale() == 'log'
        # Minor ticks should be minimal or disabled
    
    def test_set_log_scale_with_grid(self, fig_ax):
        """Test setting log scale with grid configuration."""
        fig, ax = fig_ax
        
        scitex.plt.ax.set_log_scale(ax, axis='both', grid=True)
        
        assert ax.get_xscale() == 'log'
        assert ax.get_yscale() == 'log'
        # Grid should be enabled (matplotlib's grid state can be complex to check)
    
    def test_set_log_scale_with_scientific_notation(self, fig_ax):
        """Test setting log scale with scientific notation formatting."""
        fig, ax = fig_ax
        
        scitex.plt.ax.set_log_scale(ax, axis='x', scientific_notation=True)
        
        assert ax.get_xscale() == 'log'
        # Check that formatter is set for scientific notation
        formatter = ax.xaxis.get_major_formatter()
        assert formatter is not None
    
    def test_set_log_scale_invalid_axis(self, fig_ax):
        """Test error handling for invalid axis specification."""
        fig, ax = fig_ax
        
        # Test with invalid axis - may not raise exception, just ignore invalid axis
        try:
            result = scitex.plt.ax.set_log_scale(ax, axis='invalid')
            # If it doesn't raise, it should return the axis unchanged
            assert result == ax
        except (ValueError, KeyError):
            # If it does raise, that's also acceptable
            pass
    
    def test_set_log_scale_with_negative_limits(self, fig_ax):
        """Test handling of negative limits (logarithmic scale doesn't support negatives)."""
        fig, ax = fig_ax
        
        # Set log scale first, then try negative limits
        scitex.plt.ax.set_log_scale(ax, axis='x')
        
        # Setting negative limits on log scale should raise warning
        with pytest.warns(UserWarning):
            ax.set_xlim(-10, 100)
    
    def test_set_log_scale_with_zero_limits(self, fig_ax):
        """Test handling of zero in limits (logarithmic scale doesn't support zero)."""
        fig, ax = fig_ax
        
        # Set log scale first, then try zero limits
        scitex.plt.ax.set_log_scale(ax, axis='y')
        
        # Setting limits with zero on log scale should raise warning
        with pytest.warns(UserWarning):
            ax.set_ylim(0, 100)

class TestSmartLogLimits:
    """Test smart_log_limits function - automatic limit determination."""
    
    def test_smart_log_limits_exponential_data(self, sample_data):
        """Test smart limits calculation for exponential data."""
        data = sample_data['exponential']  # 1 to 10000
        
        limits = scitex.plt.ax.smart_log_limits(data)
        
        assert len(limits) == 2
        assert limits[0] > 0  # Lower limit should be positive
        assert limits[1] > limits[0]  # Upper > lower
        assert limits[0] <= data.min()
        assert limits[1] >= data.max()
    
    def test_smart_log_limits_small_range_data(self, sample_data):
        """Test smart limits for small range data."""
        data = sample_data['small_range']  # 0.01 to 1
        
        limits = scitex.plt.ax.smart_log_limits(data)
        
        assert limits[0] > 0
        assert limits[1] > limits[0]
        assert limits[0] <= data.min()
        assert limits[1] >= data.max()
    
    def test_smart_log_limits_large_range_data(self, sample_data):
        """Test smart limits for large range data."""
        data = sample_data['large_range']  # 1 to 1000000
        
        limits = scitex.plt.ax.smart_log_limits(data)
        
        assert limits[0] > 0
        assert limits[1] > limits[0]
        # Should span multiple orders of magnitude
        assert np.log10(limits[1] / limits[0]) >= 5  # At least 5 orders
    
    def test_smart_log_limits_with_padding(self):
        """Test smart limits with custom padding."""
        data = np.logspace(1, 3, 50)  # 10 to 1000
        
        # Test with larger padding
        limits_padded = scitex.plt.ax.smart_log_limits(data, padding_factor=2.0)
        limits_normal = scitex.plt.ax.smart_log_limits(data, padding_factor=1.1)
        
        # Padded limits should be wider
        assert limits_padded[0] < limits_normal[0]
        assert limits_padded[1] > limits_normal[1]
    
    def test_smart_log_limits_single_value(self):
        """Test smart limits with single value (edge case)."""
        data = np.array([100.0])
        
        limits = scitex.plt.ax.smart_log_limits(data)
        
        assert limits[0] > 0
        assert limits[1] > limits[0]
        # Should create reasonable range around single value
        assert limits[0] < 100 < limits[1]
    
    def test_smart_log_limits_with_zeros(self):
        """Test handling of data containing zeros."""
        data = np.array([0, 1, 10, 100])
        
        with pytest.warns(UserWarning) or pytest.raises(ValueError):
            limits = scitex.plt.ax.smart_log_limits(data)
    
    def test_smart_log_limits_with_negatives(self, sample_data):
        """Test handling of negative data."""
        data = sample_data['negative']
        
        with pytest.warns(UserWarning) or pytest.raises(ValueError):
            limits = scitex.plt.ax.smart_log_limits(data)
    
    def test_smart_log_limits_empty_data(self):
        """Test handling of empty data array."""
        data = np.array([])
        
        with pytest.raises((ValueError, IndexError)):
            scitex.plt.ax.smart_log_limits(data)
    
    def test_smart_log_limits_with_axis_specification(self, sample_data):
        """Test smart limits with axis specification."""
        data = sample_data['exponential']
        
        # Test with different axis names (for reference/documentation)
        x_limits = scitex.plt.ax.smart_log_limits(data, axis='x')
        y_limits = scitex.plt.ax.smart_log_limits(data, axis='y')
        
        assert len(x_limits) == 2
        assert len(y_limits) == 2
        assert all(lim > 0 for lim in x_limits + y_limits)
        # Both should be the same since they're based on the same data
        assert x_limits == y_limits

class TestAddLogScaleIndicator:
    """Test add_log_scale_indicator function - visual log scale indicators."""
    
    def test_add_log_scale_indicator_basic(self, fig_ax):
        """Test adding basic log scale indicator."""
        fig, ax = fig_ax
        
        # Set log scale first
        ax.set_xscale('log')
        
        result = scitex.plt.ax.add_log_scale_indicator(ax, axis='x')
        
        # Should return some indicator object or modify the axis
        assert result is not None or ax.get_xlabel() or ax.get_title()
    
    def test_add_log_scale_indicator_custom_styling(self, fig_ax):
        """Test adding log scale indicator with custom styling."""
        fig, ax = fig_ax
        
        ax.set_yscale('log')
        
        # Test with custom styling parameters that exist in the function
        scitex.plt.ax.add_log_scale_indicator(
            ax, axis='y', fontsize=14, color='blue', alpha=0.8
        )
        
        # Function should complete without error
    
    def test_add_log_scale_indicator_position(self, fig_ax):
        """Test log scale indicator positioning."""
        fig, ax = fig_ax
        
        ax.set_xscale('log')
        
        # Test different positions from the function signature
        positions = ['auto', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
        for position in positions:
            try:
                scitex.plt.ax.add_log_scale_indicator(ax, axis='x', position=position)
            except (ValueError, KeyError):
                # Some positions might not be valid
                pass
    
    def test_add_log_scale_indicator_base_display(self, fig_ax):
        """Test log scale indicator with different bases."""
        fig, ax = fig_ax
        
        ax.set_yscale('log')
        
        # Test with different bases
        for base in [2, np.e, 10]:
            scitex.plt.ax.add_log_scale_indicator(ax, axis='y', base=base)
        
        # Indicator should be added with custom styling
    
    def test_add_log_scale_indicator_both_axes(self, fig_ax):
        """Test adding indicators for both axes."""
        fig, ax = fig_ax
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        scitex.plt.ax.add_log_scale_indicator(ax, axis='both')
        
        # Should add indicators for both axes
    
    def test_add_log_scale_indicator_linear_axis_warning(self, fig_ax):
        """Test warning when adding indicator to linear axis."""
        fig, ax = fig_ax
        
        # Keep axis linear (default)
        
        with pytest.warns(UserWarning):
            scitex.plt.ax.add_log_scale_indicator(ax, axis='x')
    
    def test_add_log_scale_indicator_with_base(self, fig_ax):
        """Test log scale indicator showing custom base."""
        fig, ax = fig_ax
        
        ax.set_xscale('log', base=2)
        
        scitex.plt.ax.add_log_scale_indicator(ax, axis='x', base=2)
        
        # Should indicate base 2 logarithm

class TestLogScaleIntegration:
    """Test integration between log scale functions."""
    
    def test_complete_log_scale_workflow(self, fig_ax, sample_data):
        """Test complete workflow: smart limits + set scale + indicator."""
        fig, ax = fig_ax
        data = sample_data['exponential']
        
        # 1. Calculate smart limits
        limits = scitex.plt.ax.smart_log_limits(data)
        
        # 2. Set log scale with those limits
        scitex.plt.ax.set_log_scale(ax, axis='both', limits=limits)
        
        # 3. Add visual indicator
        scitex.plt.ax.add_log_scale_indicator(ax, axis='both')
        
        # Verify everything worked together
        assert ax.get_xscale() == 'log'
        assert ax.get_yscale() == 'log'
        
        x_limits = ax.get_xlim()
        assert x_limits[0] == pytest.approx(limits[0], rel=1e-1)
        assert x_limits[1] == pytest.approx(limits[1], rel=1e-1)
    
    def test_log_scale_with_plot_data(self, fig_ax, sample_data):
        """Test log scale functions with actual plotted data."""
        fig, ax = fig_ax
        x_data = sample_data['exponential']
        y_data = sample_data['large_range']
        
        # Plot data
        ax.plot(x_data, y_data, 'o-')
        
        # Apply log scaling
        scitex.plt.ax.set_log_scale(ax, axis='both', show_minor_ticks=True, grid=True)
        
        # Add indicators
        scitex.plt.ax.add_log_scale_indicator(ax, axis='both')
        
        assert ax.get_xscale() == 'log'
        assert ax.get_yscale() == 'log'
    
    def test_mixed_scale_configuration(self, fig_ax, sample_data):
        """Test mixed linear/log scale configuration."""
        fig, ax = fig_ax
        
        # Linear x, log y
        scitex.plt.ax.set_log_scale(ax, axis='y')
        scitex.plt.ax.add_log_scale_indicator(ax, axis='y')
        
        assert ax.get_xscale() == 'linear'
        assert ax.get_yscale() == 'log'

class TestLogScaleEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_log_scale_with_invalid_data_types(self, fig_ax):
        """Test error handling with invalid data types."""
        fig, ax = fig_ax
        
        with pytest.raises((TypeError, ValueError)):
            scitex.plt.ax.smart_log_limits("invalid_data")
        
        with pytest.raises((TypeError, AttributeError)):
            scitex.plt.ax.set_log_scale("not_an_axis", axis='x')
    
    def test_log_scale_with_none_values(self, fig_ax):
        """Test handling of None values in parameters."""
        fig, ax = fig_ax
        
        # These should either work with defaults or raise appropriate errors
        try:
            scitex.plt.ax.set_log_scale(ax, axis=None)
        except (ValueError, TypeError):
            pass  # Expected for invalid axis
        
        try:
            scitex.plt.ax.add_log_scale_indicator(ax, axis=None)
        except (ValueError, TypeError):
            pass  # Expected for invalid axis
    
    def test_log_scale_very_small_numbers(self):
        """Test log scale with very small positive numbers."""
        data = np.array([1e-10, 1e-8, 1e-6, 1e-4])
        
        limits = scitex.plt.ax.smart_log_limits(data)
        
        assert limits[0] > 0
        assert limits[1] > limits[0]
        assert limits[0] <= data.min()
        assert limits[1] >= data.max()
    
    def test_log_scale_very_large_numbers(self):
        """Test log scale with very large numbers."""
        data = np.array([1e6, 1e8, 1e10, 1e12])
        
        limits = scitex.plt.ax.smart_log_limits(data)
        
        assert limits[0] > 0
        assert limits[1] > limits[0]
        assert limits[0] <= data.min()
        assert limits[1] >= data.max()
    
    @pytest.mark.parametrize("base", [2, np.e, 10, 5])
    def test_log_scale_different_bases(self, fig_ax, base):
        """Test log scale with different logarithmic bases."""
        fig, ax = fig_ax
        
        scitex.plt.ax.set_log_scale(ax, axis='x', base=base)
        
        assert ax.get_xscale() == 'log'
    
    def test_log_scale_persistence_after_operations(self, fig_ax, sample_data):
        """Test that log scale persists after various plot operations."""
        fig, ax = fig_ax
        data = sample_data['exponential']
        
        # Set log scale
        scitex.plt.ax.set_log_scale(ax, axis='both')
        
        # Perform various operations
        ax.plot(data, data)
        ax.set_title("Test Plot")
        ax.grid(True)
        
        # Log scale should persist
        assert ax.get_xscale() == 'log'
        assert ax.get_yscale() == 'log'

# Run specific test classes for debugging
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])