#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-05 07:45:00 (ywatanabe)"
# File: ./tests/scitex/plt/ax/_style/test__show_spines.py

"""
Functionality:
    Comprehensive tests for _show_spines module
Input:
    Various matplotlib axes configurations and spine parameters
Output:
    Test results validating spine visibility control functionality
Prerequisites:
    pytest, matplotlib, scitex
"""

import pytest
import matplotlib.pyplot as plt
import matplotlib.axes
import numpy as np
from unittest.mock import Mock, patch

# Import the functions to test
import scitex


class TestShowSpines:
    """Test the main show_spines function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        # Start with all spines hidden (common scitex default)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_show_all_spines_default(self):
        """Test showing all spines with default parameters."""
        result = scitex.plt.ax.show_spines(self.ax)
        
        assert result is self.ax
        assert self.ax.spines['top'].get_visible()
        assert self.ax.spines['bottom'].get_visible()
        assert self.ax.spines['left'].get_visible()
        assert self.ax.spines['right'].get_visible()
    
    def test_show_selective_spines(self):
        """Test showing only specific spines."""
        scitex.plt.ax.show_spines(self.ax, top=False, right=False, bottom=True, left=True)
        
        assert not self.ax.spines['top'].get_visible()
        assert self.ax.spines['bottom'].get_visible()
        assert self.ax.spines['left'].get_visible()
        assert not self.ax.spines['right'].get_visible()
    
    def test_spine_width_setting(self):
        """Test setting custom spine width."""
        width = 2.5
        scitex.plt.ax.show_spines(self.ax, spine_width=width)
        
        for spine in self.ax.spines.values():
            assert spine.get_linewidth() == width
    
    def test_spine_color_setting(self):
        """Test setting custom spine color."""
        color = 'red'
        scitex.plt.ax.show_spines(self.ax, spine_color=color)
        
        # matplotlib converts colors to RGBA tuples
        expected_rgba = (1.0, 0.0, 0.0, 1.0)  # red in RGBA
        for spine in self.ax.spines.values():
            assert spine.get_edgecolor() == expected_rgba
    
    def test_combined_styling(self):
        """Test combining width and color settings."""
        width, color = 1.8, 'blue'
        scitex.plt.ax.show_spines(self.ax, spine_width=width, spine_color=color)
        
        expected_rgba = (0.0, 0.0, 1.0, 1.0)  # blue in RGBA
        for spine in self.ax.spines.values():
            assert spine.get_linewidth() == width
            assert spine.get_edgecolor() == expected_rgba
    
    def test_tick_positioning_bottom_only(self):
        """Test tick positioning when only bottom spine is shown."""
        scitex.plt.ax.show_spines(self.ax, top=False, bottom=True, left=False, right=False)
        
        # Should position ticks on bottom only
        assert self.ax.xaxis.get_ticks_position() == 'bottom'
    
    def test_tick_positioning_top_only(self):
        """Test tick positioning when only top spine is shown."""
        scitex.plt.ax.show_spines(self.ax, top=True, bottom=False, left=False, right=False)
        
        assert self.ax.xaxis.get_ticks_position() == 'top'
    
    def test_tick_positioning_both_horizontal(self):
        """Test tick positioning when both horizontal spines are shown."""
        scitex.plt.ax.show_spines(self.ax, top=True, bottom=True, left=False, right=False)
        
        # When both spines are shown, matplotlib might use 'default' instead of 'both'
        tick_pos = self.ax.xaxis.get_ticks_position()
        assert tick_pos in ['both', 'default']
    
    def test_tick_positioning_left_only(self):
        """Test tick positioning when only left spine is shown."""
        scitex.plt.ax.show_spines(self.ax, top=False, bottom=False, left=True, right=False)
        
        assert self.ax.yaxis.get_ticks_position() == 'left'
    
    def test_tick_positioning_right_only(self):
        """Test tick positioning when only right spine is shown."""
        scitex.plt.ax.show_spines(self.ax, top=False, bottom=False, left=False, right=True)
        
        assert self.ax.yaxis.get_ticks_position() == 'right'
    
    def test_tick_positioning_both_vertical(self):
        """Test tick positioning when both vertical spines are shown."""
        scitex.plt.ax.show_spines(self.ax, top=False, bottom=False, left=True, right=True)
        
        # When both spines are shown, matplotlib might use 'default' instead of 'both'
        tick_pos = self.ax.yaxis.get_ticks_position()
        assert tick_pos in ['both', 'default']
    
    def test_ticks_disabled(self):
        """Test behavior when ticks are disabled."""
        original_x_pos = self.ax.xaxis.get_ticks_position()
        original_y_pos = self.ax.yaxis.get_ticks_position()
        
        scitex.plt.ax.show_spines(self.ax, ticks=False)
        
        # Tick positions should not be modified when ticks=False
        assert self.ax.xaxis.get_ticks_position() == original_x_pos
        assert self.ax.yaxis.get_ticks_position() == original_y_pos
    
    def test_restore_defaults_disabled(self):
        """Test behavior when restore_defaults is disabled."""
        scitex.plt.ax.show_spines(self.ax, restore_defaults=False)
        
        # Should still show spines but not modify tick settings
        assert all(spine.get_visible() for spine in self.ax.spines.values())
    
    def test_labels_functionality(self):
        """Test label restoration functionality."""
        # Set some data to generate ticks
        self.ax.plot([1, 2, 3], [1, 4, 2])
        
        scitex.plt.ax.show_spines(self.ax, labels=True)
        
        # Should have tick labels
        xticks = self.ax.get_xticks()
        yticks = self.ax.get_yticks()
        assert len(xticks) > 0
        assert len(yticks) > 0


class TestScitexAxisWrapperCompatibility:
    """Test compatibility with scitex AxisWrapper objects."""
    
    def setup_method(self):
        """Set up test fixtures with mock AxisWrapper."""
        self.fig, self.ax = plt.subplots()
        
        # Create a mock AxisWrapper that has _axis_mpl attribute
        self.mock_wrapper = Mock()
        self.mock_wrapper._axis_mpl = self.ax
        self.mock_wrapper.__class__.__name__ = 'AxisWrapper'
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_axis_wrapper_handling(self):
        """Test that function works with scitex AxisWrapper objects."""
        result = scitex.plt.ax.show_spines(self.mock_wrapper)
        
        # Should return the underlying matplotlib axis
        assert result is self.ax
        # All spines should be visible
        assert all(spine.get_visible() for spine in self.ax.spines.values())
    
    def test_invalid_axis_type(self):
        """Test error handling for invalid axis types."""
        with pytest.raises(AssertionError, match="First argument must be a matplotlib axis"):
            scitex.plt.ax.show_spines("not_an_axis")
    
    def test_none_axis(self):
        """Test error handling for None axis."""
        with pytest.raises(AssertionError, match="First argument must be a matplotlib axis"):
            scitex.plt.ax.show_spines(None)


class TestShowAllSpines:
    """Test the show_all_spines convenience function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_show_all_spines_basic(self):
        """Test basic show_all_spines functionality."""
        result = scitex.plt.ax.show_all_spines(self.ax)
        
        assert result is self.ax
        assert all(spine.get_visible() for spine in self.ax.spines.values())
    
    def test_show_all_spines_with_styling(self):
        """Test show_all_spines with styling parameters."""
        width, color = 2.0, 'green'
        scitex.plt.ax.show_all_spines(self.ax, spine_width=width, spine_color=color)
        
        expected_rgba = (0.0, 0.5019607843137255, 0.0, 1.0)  # green in RGBA
        for spine in self.ax.spines.values():
            assert spine.get_visible()
            assert spine.get_linewidth() == width
            assert spine.get_edgecolor() == expected_rgba
    
    def test_show_all_spines_no_ticks(self):
        """Test show_all_spines without ticks."""
        scitex.plt.ax.show_all_spines(self.ax, ticks=False)
        
        assert all(spine.get_visible() for spine in self.ax.spines.values())
    
    def test_show_all_spines_no_labels(self):
        """Test show_all_spines without labels."""
        scitex.plt.ax.show_all_spines(self.ax, labels=False)
        
        assert all(spine.get_visible() for spine in self.ax.spines.values())


class TestShowClassicSpines:
    """Test the show_classic_spines function (scientific plot style)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_classic_spines_pattern(self):
        """Test that classic spines shows only bottom and left."""
        scitex.plt.ax.show_classic_spines(self.ax)
        
        assert not self.ax.spines['top'].get_visible()
        assert self.ax.spines['bottom'].get_visible()
        assert self.ax.spines['left'].get_visible()
        assert not self.ax.spines['right'].get_visible()
    
    def test_classic_spines_with_styling(self):
        """Test classic spines with custom styling."""
        width, color = 1.5, 'black'
        scitex.plt.ax.show_classic_spines(self.ax, spine_width=width, spine_color=color)
        
        expected_rgba = (0.0, 0.0, 0.0, 1.0)  # black in RGBA
        # Only bottom and left should be styled and visible
        assert self.ax.spines['bottom'].get_visible()
        assert self.ax.spines['left'].get_visible()
        assert self.ax.spines['bottom'].get_linewidth() == width
        assert self.ax.spines['left'].get_linewidth() == width
        assert self.ax.spines['bottom'].get_edgecolor() == expected_rgba
        assert self.ax.spines['left'].get_edgecolor() == expected_rgba
    
    def test_scientific_spines_alias(self):
        """Test that scientific_spines is an alias for show_classic_spines."""
        scitex.plt.ax.scientific_spines(self.ax)
        
        assert not self.ax.spines['top'].get_visible()
        assert self.ax.spines['bottom'].get_visible()
        assert self.ax.spines['left'].get_visible()
        assert not self.ax.spines['right'].get_visible()


class TestShowBoxSpines:
    """Test the show_box_spines function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_box_spines_all_visible(self):
        """Test that box spines shows all four spines."""
        scitex.plt.ax.show_box_spines(self.ax)
        
        assert all(spine.get_visible() for spine in self.ax.spines.values())
    
    def test_box_spines_with_styling(self):
        """Test box spines with styling."""
        width, color = 1.0, 'purple'
        scitex.plt.ax.show_box_spines(self.ax, spine_width=width, spine_color=color)
        
        expected_rgba = (0.5019607843137255, 0.0, 0.5019607843137255, 1.0)  # purple in RGBA
        for spine in self.ax.spines.values():
            assert spine.get_visible()
            assert spine.get_linewidth() == width
            assert spine.get_edgecolor() == expected_rgba


class TestToggleSpines:
    """Test the toggle_spines function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        # Set initial known state
        self.ax.spines['top'].set_visible(True)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(True)
        self.ax.spines['right'].set_visible(False)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_toggle_all_spines(self):
        """Test toggling all spines (None parameters)."""
        initial_states = {name: spine.get_visible() for name, spine in self.ax.spines.items()}
        
        scitex.plt.ax.toggle_spines(self.ax)
        
        for name, spine in self.ax.spines.items():
            assert spine.get_visible() == (not initial_states[name])
    
    def test_toggle_specific_spines(self):
        """Test setting specific spine states."""
        scitex.plt.ax.toggle_spines(self.ax, top=False, bottom=True)
        
        assert not self.ax.spines['top'].get_visible()
        assert self.ax.spines['bottom'].get_visible()
        # Left and right should be toggled from initial state
        assert not self.ax.spines['left'].get_visible()  # was True, now False
        assert self.ax.spines['right'].get_visible()    # was False, now True
    
    def test_toggle_mixed_parameters(self):
        """Test mixing explicit and toggle parameters."""
        scitex.plt.ax.toggle_spines(self.ax, top=True, right=False)
        
        assert self.ax.spines['top'].get_visible()      # explicitly set to True
        assert not self.ax.spines['right'].get_visible()  # explicitly set to False
        # Bottom and left should be toggled
        assert self.ax.spines['bottom'].get_visible()   # was False, now True
        assert not self.ax.spines['left'].get_visible()   # was True, now False


class TestCleanSpines:
    """Test the clean_spines function (no spines shown)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
        # Start with all spines visible
        for spine in self.ax.spines.values():
            spine.set_visible(True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_clean_spines_hides_all(self):
        """Test that clean_spines hides all spines."""
        scitex.plt.ax.clean_spines(self.ax)
        
        assert all(not spine.get_visible() for spine in self.ax.spines.values())
    
    def test_clean_spines_with_ticks_labels(self):
        """Test clean_spines with tick and label options."""
        scitex.plt.ax.clean_spines(self.ax, ticks=True, labels=True)
        
        # All spines should be hidden regardless of tick/label settings
        assert all(not spine.get_visible() for spine in self.ax.spines.values())


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_empty_axis_data(self):
        """Test behavior with axis that has no data."""
        # Should work without errors even with empty axis
        result = scitex.plt.ax.show_spines(self.ax)
        assert result is self.ax
    
    def test_axis_with_data(self):
        """Test behavior with axis containing data."""
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        self.ax.plot(x, y)
        
        result = scitex.plt.ax.show_spines(self.ax)
        assert result is self.ax
        assert all(spine.get_visible() for spine in self.ax.spines.values())
    
    def test_negative_spine_width(self):
        """Test behavior with negative spine width."""
        # Matplotlib should handle this gracefully
        scitex.plt.ax.show_spines(self.ax, spine_width=-1.0)
        
        for spine in self.ax.spines.values():
            assert spine.get_linewidth() == -1.0  # matplotlib allows negative widths
    
    def test_zero_spine_width(self):
        """Test behavior with zero spine width."""
        scitex.plt.ax.show_spines(self.ax, spine_width=0.0)
        
        for spine in self.ax.spines.values():
            assert spine.get_linewidth() == 0.0
    
    def test_invalid_color_format(self):
        """Test behavior with invalid color format."""
        # This should raise a matplotlib error
        with pytest.raises((ValueError, TypeError)):
            scitex.plt.ax.show_spines(self.ax, spine_color='invalid_color_name')
    
    def test_none_width_and_color(self):
        """Test that None values don't change existing properties."""
        # Set initial properties
        initial_width = self.ax.spines['bottom'].get_linewidth()
        initial_color = self.ax.spines['bottom'].get_edgecolor()
        
        scitex.plt.ax.show_spines(self.ax, spine_width=None, spine_color=None)
        
        # Properties should remain unchanged
        assert self.ax.spines['bottom'].get_linewidth() == initial_width
        assert self.ax.spines['bottom'].get_edgecolor() == initial_color


class TestIntegration:
    """Integration tests with realistic usage patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        plt.close(self.fig)
    
    def test_scientific_plot_workflow(self):
        """Test typical scientific plotting workflow."""
        # Generate sample data
        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x)
        self.ax.plot(x, y)
        
        # Apply scientific styling
        scitex.plt.ax.show_classic_spines(
            self.ax, 
            spine_width=1.2, 
            spine_color='black'
        )
        
        # Verify the result
        assert not self.ax.spines['top'].get_visible()
        assert self.ax.spines['bottom'].get_visible()
        assert self.ax.spines['left'].get_visible()
        assert not self.ax.spines['right'].get_visible()
        
        # Check styling
        expected_rgba = (0.0, 0.0, 0.0, 1.0)  # black in RGBA
        assert self.ax.spines['bottom'].get_linewidth() == 1.2
        assert self.ax.spines['left'].get_linewidth() == 1.2
        assert self.ax.spines['bottom'].get_edgecolor() == expected_rgba
        assert self.ax.spines['left'].get_edgecolor() == expected_rgba
    
    def test_overlay_plot_workflow(self):
        """Test workflow for overlay plots with clean spines."""
        # Create base plot
        x = np.linspace(0, 10, 50)
        y = np.exp(-x/3)
        self.ax.plot(x, y)
        
        # Apply clean styling for overlay
        scitex.plt.ax.clean_spines(self.ax, ticks=False, labels=False)
        
        # Verify clean appearance
        assert all(not spine.get_visible() for spine in self.ax.spines.values())
    
    def test_publication_ready_workflow(self):
        """Test workflow for publication-ready figures."""
        # Create sample data
        categories = ['A', 'B', 'C', 'D']
        values = [23, 45, 56, 78]
        self.ax.bar(categories, values)
        
        # Apply publication styling
        scitex.plt.ax.show_box_spines(
            self.ax,
            spine_width=0.8,
            spine_color='#333333',
            ticks=True,
            labels=True
        )
        
        # Verify box appearance
        expected_rgba = (0.2, 0.2, 0.2, 1.0)  # #333333 in RGBA
        assert all(spine.get_visible() for spine in self.ax.spines.values())
        for spine in self.ax.spines.values():
            assert spine.get_linewidth() == 0.8
            assert spine.get_edgecolor() == expected_rgba
    
    def test_toggle_workflow(self):
        """Test interactive toggle workflow."""
        # Start with default state
        initial_states = {name: spine.get_visible() for name, spine in self.ax.spines.items()}
        
        # Toggle spines multiple times
        scitex.plt.ax.toggle_spines(self.ax)
        first_toggle = {name: spine.get_visible() for name, spine in self.ax.spines.items()}
        
        scitex.plt.ax.toggle_spines(self.ax)
        second_toggle = {name: spine.get_visible() for name, spine in self.ax.spines.items()}
        
        # Should return to initial state after double toggle
        assert initial_states == second_toggle
        
        # First toggle should be opposite of initial
        for name in initial_states:
            assert first_toggle[name] == (not initial_states[name])

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_show_spines.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-06-04 11:15:00 (ywatanabe)"
# # File: ./src/scitex/plt/ax/_style/_show_spines.py
# 
# """
# Functionality:
#     Show spines for matplotlib axes with intuitive API
# Input:
#     Matplotlib axes object and spine visibility parameters
# Output:
#     Axes with specified spines made visible
# Prerequisites:
#     matplotlib
# """
# 
# import matplotlib
# from typing import Union, List
# 
# 
# def show_spines(
#     axis,
#     top: bool = True,
#     bottom: bool = True,
#     left: bool = True,
#     right: bool = True,
#     ticks: bool = True,
#     labels: bool = True,
#     restore_defaults: bool = True,
#     spine_width: float = None,
#     spine_color: str = None
# ):
#     """
#     Shows the specified spines of a matplotlib Axes object and optionally restores ticks and labels.
# 
#     This function provides the intuitive counterpart to hide_spines. It's especially useful when
#     you have spines hidden by default (as in scitex configuration) and want to selectively show them
#     for clearer scientific plots or specific visualization needs.
# 
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes
#         The Axes object for which the spines will be shown.
#     top : bool, optional
#         If True, shows the top spine. Defaults to True.
#     bottom : bool, optional
#         If True, shows the bottom spine. Defaults to True.
#     left : bool, optional
#         If True, shows the left spine. Defaults to True.
#     right : bool, optional
#         If True, shows the right spine. Defaults to True.
#     ticks : bool, optional
#         If True, restores ticks on the shown spines' axes. Defaults to True.
#     labels : bool, optional
#         If True, restores labels on the shown spines' axes. Defaults to True.
#     restore_defaults : bool, optional
#         If True, restores default tick positions and labels. Defaults to True.
#     spine_width : float, optional
#         Width of the spines to show. If None, uses matplotlib default.
#     spine_color : str, optional
#         Color of the spines to show. If None, uses matplotlib default.
# 
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The modified Axes object with the specified spines shown.
# 
#     Examples
#     --------
#     >>> fig, ax = plt.subplots()
#     >>> # Show only bottom and left spines (classic scientific plot style)
#     >>> show_spines(ax, top=False, right=False)
#     >>> plt.show()
# 
#     >>> # Show all spines with custom styling
#     >>> show_spines(ax, spine_width=1.5, spine_color='black')
#     >>> plt.show()
# 
#     >>> # Show spines but without ticks/labels (for clean overlay plots)
#     >>> show_spines(ax, ticks=False, labels=False)
#     >>> plt.show()
# 
#     Notes
#     -----
#     This function is designed to work seamlessly with scitex plotting where spines are hidden
#     by default. It provides an intuitive API for showing spines without needing to remember
#     that hide_spines(top=False, right=False) shows top and right spines.
#     """
#     # Handle both matplotlib axes and scitex AxisWrapper
#     if hasattr(axis, '_axis_mpl'):
#         # This is an scitex AxisWrapper, get the underlying matplotlib axis
#         axis = axis._axis_mpl
#     
#     assert isinstance(
#         axis, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis or scitex AxisWrapper"
# 
#     # Define which spines to show
#     spine_settings = {
#         "top": top,
#         "bottom": bottom,
#         "left": left,
#         "right": right
#     }
# 
#     for spine_name, should_show in spine_settings.items():
#         # Set spine visibility
#         axis.spines[spine_name].set_visible(should_show)
#         
#         if should_show:
#             # Set spine width if specified
#             if spine_width is not None:
#                 axis.spines[spine_name].set_linewidth(spine_width)
#             
#             # Set spine color if specified
#             if spine_color is not None:
#                 axis.spines[spine_name].set_color(spine_color)
# 
#     # Restore ticks if requested
#     if ticks and restore_defaults:
#         # Determine tick positions based on which spines are shown
#         if bottom and not top:
#             axis.xaxis.set_ticks_position('bottom')
#         elif top and not bottom:
#             axis.xaxis.set_ticks_position('top')
#         elif bottom and top:
#             axis.xaxis.set_ticks_position('both')
#         
#         if left and not right:
#             axis.yaxis.set_ticks_position('left')
#         elif right and not left:
#             axis.yaxis.set_ticks_position('right')
#         elif left and right:
#             axis.yaxis.set_ticks_position('both')
# 
#     # Restore labels if requested and restore_defaults is True
#     if labels and restore_defaults:
#         # Only restore if we haven't explicitly hidden them
#         # This preserves any custom tick labels that might have been set
#         current_xticks = axis.get_xticks()
#         current_yticks = axis.get_yticks()
#         
#         if len(current_xticks) > 0 and (bottom or top):
#             # Generate default labels for x-axis
#             if not hasattr(axis, '_original_xticklabels'):
#                 axis.set_xticks(current_xticks)
#         
#         if len(current_yticks) > 0 and (left or right):
#             # Generate default labels for y-axis  
#             if not hasattr(axis, '_original_yticklabels'):
#                 axis.set_yticks(current_yticks)
# 
#     return axis
# 
# 
# def show_all_spines(
#     axis,
#     spine_width: float = None,
#     spine_color: str = None,
#     ticks: bool = True,
#     labels: bool = True
# ):
#     """
#     Convenience function to show all spines with optional styling.
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes
#         The Axes object to modify.
#     spine_width : float, optional
#         Width of all spines.
#     spine_color : str, optional
#         Color of all spines.
#     ticks : bool, optional
#         Whether to show ticks. Defaults to True.
#     labels : bool, optional
#         Whether to show labels. Defaults to True.
#         
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The modified Axes object.
#         
#     Examples
#     --------
#     >>> show_all_spines(ax, spine_width=1.2, spine_color='gray')
#     """
#     return show_spines(
#         axis,
#         top=True, bottom=True, left=True, right=True,
#         ticks=ticks, labels=labels,
#         spine_width=spine_width, spine_color=spine_color
#     )
# 
# 
# def show_classic_spines(
#     axis,
#     spine_width: float = None,
#     spine_color: str = None,
#     ticks: bool = True,
#     labels: bool = True
# ):
#     """
#     Show only bottom and left spines (classic scientific plot style).
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes
#         The Axes object to modify.
#     spine_width : float, optional
#         Width of the spines.
#     spine_color : str, optional
#         Color of the spines.
#     ticks : bool, optional
#         Whether to show ticks. Defaults to True.
#     labels : bool, optional
#         Whether to show labels. Defaults to True.
#         
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The modified Axes object.
#         
#     Examples
#     --------
#     >>> show_classic_spines(ax)  # Shows only bottom and left spines
#     """
#     return show_spines(
#         axis,
#         top=False, bottom=True, left=True, right=False,
#         ticks=ticks, labels=labels,
#         spine_width=spine_width, spine_color=spine_color
#     )
# 
# 
# def show_box_spines(
#     axis,
#     spine_width: float = None,
#     spine_color: str = None,
#     ticks: bool = True,
#     labels: bool = True
# ):
#     """
#     Show all four spines to create a box around the plot.
#     
#     This is an alias for show_all_spines but with more descriptive naming
#     for when you specifically want a boxed appearance.
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes
#         The Axes object to modify.
#     spine_width : float, optional
#         Width of the box spines.
#     spine_color : str, optional
#         Color of the box spines.
#     ticks : bool, optional
#         Whether to show ticks. Defaults to True.
#     labels : bool, optional
#         Whether to show labels. Defaults to True.
#         
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The modified Axes object.
#         
#     Examples
#     --------
#     >>> show_box_spines(ax, spine_width=1.0, spine_color='black')
#     """
#     return show_all_spines(axis, spine_width, spine_color, ticks, labels)
# 
# 
# def toggle_spines(
#     axis,
#     top: bool = None,
#     bottom: bool = None,
#     left: bool = None,
#     right: bool = None
# ):
#     """
#     Toggle the visibility of spines (show if hidden, hide if shown).
#     
#     Parameters
#     ----------
#     axis : matplotlib.axes.Axes
#         The Axes object to modify.
#     top : bool, optional
#         If specified, sets top spine visibility. If None, toggles current state.
#     bottom : bool, optional
#         If specified, sets bottom spine visibility. If None, toggles current state.
#     left : bool, optional
#         If specified, sets left spine visibility. If None, toggles current state.
#     right : bool, optional
#         If specified, sets right spine visibility. If None, toggles current state.
#         
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The modified Axes object.
#         
#     Examples
#     --------
#     >>> toggle_spines(ax)  # Toggles all spines
#     >>> toggle_spines(ax, top=True, right=True)  # Shows top and right, toggles others
#     """
#     spine_names = ['top', 'bottom', 'left', 'right']
#     spine_params = [top, bottom, left, right]
#     
#     for spine_name, param in zip(spine_names, spine_params):
#         if param is None:
#             # Toggle current state
#             current_state = axis.spines[spine_name].get_visible()
#             axis.spines[spine_name].set_visible(not current_state)
#         else:
#             # Set specific state
#             axis.spines[spine_name].set_visible(param)
#     
#     return axis
# 
# 
# # Convenient aliases for common use cases
# def scientific_spines(axis, **kwargs):
#     """Alias for show_classic_spines - shows only bottom and left spines."""
#     return show_classic_spines(axis, **kwargs)
# 
# 
# def clean_spines(axis, **kwargs):
#     """Alias for showing no spines - useful for overlay plots or clean visualizations."""
#     return show_spines(axis, top=False, bottom=False, left=False, right=False, **kwargs)
# 
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_show_spines.py
# --------------------------------------------------------------------------------
