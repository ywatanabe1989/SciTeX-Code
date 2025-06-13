#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 23:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/_AxisWrapperMixins/test__AdjustmentMixin.py
# ----------------------------------------
import os
import sys
import tempfile
import pytest
import numpy as np
import matplotlib.pyplot as plt

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../src')))

import scitex


class TestAdjustmentMixin:
    """Test suite for AdjustmentMixin functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a simple figure with data
        self.fig, self.ax = scitex.plt.subplots()
        self.x = np.linspace(0, 10, 100)
        self.y1 = np.sin(self.x)
        self.y2 = np.cos(self.x)
        
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
        
    def test_legend_standard_positions(self):
        """Test standard legend positioning."""
        # Plot some data
        self.ax.plot(self.x, self.y1, label='sin(x)')
        self.ax.plot(self.x, self.y2, label='cos(x)')
        
        # Test standard position
        self.ax.legend('upper right')
        assert self.ax._axis_mpl.get_legend() is not None
        
    def test_legend_outside_positions(self):
        """Test outside legend positioning."""
        # Plot some data
        self.ax.plot(self.x, self.y1, label='sin(x)')
        self.ax.plot(self.x, self.y2, label='cos(x)')
        
        # Test various outside positions
        outside_positions = [
            'upper right out', 'right upper out',
            'center right out', 'right out', 'right',
            'lower right out', 'right lower out',
            'upper left out', 'left upper out',
            'center left out', 'left out', 'left',
            'lower left out', 'left lower out',
            'upper center out', 'upper out',
            'lower center out', 'lower out'
        ]
        
        for pos in outside_positions:
            self.ax.legend(pos)
            legend = self.ax._axis_mpl.get_legend()
            assert legend is not None, f"Legend not created for position: {pos}"
            
    def test_legend_separate_single_plot(self):
        """Test separate legend saving for single plot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Plot some data
            self.ax.plot(self.x, self.y1, label='sin(x)')
            self.ax.plot(self.x, self.y2, label='cos(x)')
            
            # Use separate legend
            self.ax.legend("separate")
            
            # Legend should be removed from main figure
            assert self.ax._axis_mpl.get_legend() is None
            
            # Check that legend params are stored on figure
            assert hasattr(self.fig._fig_mpl, '_separate_legend_params')
            assert len(self.fig._fig_mpl._separate_legend_params) == 1
            
            # Save the figure
            output_path = os.path.join(tmpdir, "test_plot.png")
            scitex.io.save(self.fig, output_path)
            
            # Check that both files exist
            assert os.path.exists(output_path)
            # For single subplot, the legend is saved with ax_00 suffix
            legend_path = os.path.join(tmpdir, "test_plot_ax_00_legend.png")
            assert os.path.exists(legend_path)
            
    def test_legend_separate_multiple_subplots(self):
        """Test separate legend saving for multiple subplots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create figure with multiple subplots
            fig, axes = scitex.plt.subplots(nrows=2, ncols=2)
            
            # Plot data on each subplot with separate legends
            for i, ax in enumerate(axes.flat):
                x = np.linspace(0, 10, 100)
                ax.plot(x, np.sin(x + i), label=f'sin(x+{i})')
                ax.plot(x, np.cos(x + i), label=f'cos(x+{i})')
                ax.legend("separate")
                
            # Save the figure
            output_path = os.path.join(tmpdir, "multi_plot.png")
            scitex.io.save(fig, output_path)
            
            # Check that main file exists
            assert os.path.exists(output_path)
            
            # Check that legend files exist for each subplot
            # The axis IDs are formatted as ax_00, ax_01, ax_02, ax_03
            expected_legend_files = [
                "multi_plot_ax_00_legend.png",
                "multi_plot_ax_01_legend.png", 
                "multi_plot_ax_02_legend.png",
                "multi_plot_ax_03_legend.png"
            ]
            for legend_file in expected_legend_files:
                legend_path = os.path.join(tmpdir, legend_file)
                assert os.path.exists(legend_path), f"Legend file missing: {legend_path}"
                
    def test_legend_separate_gif_format(self):
        """Test separate legend saving with GIF format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Plot some data
            self.ax.plot(self.x, self.y1, label='sin(x)')
            self.ax.plot(self.x, self.y2, label='cos(x)')
            
            # Use separate legend
            self.ax.legend("separate")
            
            # Save as GIF
            output_path = os.path.join(tmpdir, "test_plot.gif")
            scitex.io.save(self.fig, output_path)
            
            # Check that both files exist
            assert os.path.exists(output_path)
            # For single subplot, the legend is saved with ax_00 suffix
            legend_path = os.path.join(tmpdir, "test_plot_ax_00_legend.gif")
            assert os.path.exists(legend_path)
            
    def test_rotate_labels(self):
        """Test label rotation functionality."""
        # Set some tick labels
        self.ax._axis_mpl.set_xticks([0, 5, 10])
        self.ax._axis_mpl.set_xticklabels(['start', 'middle', 'end'])
        self.ax._axis_mpl.set_yticks([0, 0.5, 1])
        self.ax._axis_mpl.set_yticklabels(['low', 'mid', 'high'])
        
        # Rotate labels
        self.ax.rotate_labels(x=45, y=30)
        
        # Check that labels are rotated
        for label in self.ax._axis_mpl.get_xticklabels():
            assert label.get_rotation() == 45
            
    def test_set_xyt(self):
        """Test setting axis labels and title."""
        self.ax.set_xyt(x='X-axis', y='Y-axis', t='Test Title')
        
        assert self.ax._axis_mpl.get_xlabel() == 'X-axis'
        assert self.ax._axis_mpl.get_ylabel() == 'Y-axis'
        assert self.ax._axis_mpl.get_title() == 'Test Title'
        
    def test_set_n_ticks(self):
        """Test setting number of ticks."""
        self.ax.plot(self.x, self.y1)
        self.ax.set_n_ticks(n_xticks=5, n_yticks=3)
        
        # Check approximate number of ticks (matplotlib may adjust)
        # The function tries to set approximately n ticks, but matplotlib
        # may choose different numbers based on nice tick values
        xticks = self.ax._axis_mpl.get_xticks()
        yticks = self.ax._axis_mpl.get_yticks()
        # Allow more flexibility in the tick count
        assert len(xticks) >= 3 and len(xticks) <= 8
        assert len(yticks) >= 2 and len(yticks) <= 5
        
    def test_hide_spines(self):
        """Test hiding spines."""
        # Hide all spines
        self.ax.hide_spines(top=True, bottom=True, left=True, right=True)
        
        # Check that spines are hidden
        for spine in ['top', 'bottom', 'left', 'right']:
            assert not self.ax._axis_mpl.spines[spine].get_visible()
            
    def test_extend(self):
        """Test extending axis position (not limits)."""
        # The extend method modifies the axis position in the figure, not the data limits
        self.ax.plot([0, 1], [0, 1])
        
        # Get original position
        original_pos = self.ax._axis_mpl.get_position()
        original_width = original_pos.width
        original_height = original_pos.height
        
        # Extend by 20%
        self.ax.extend(x_ratio=1.2, y_ratio=1.2)
        
        # Get new position
        new_pos = self.ax._axis_mpl.get_position()
        new_width = new_pos.width
        new_height = new_pos.height
        
        # Check that axis size is extended
        assert abs(new_width - original_width * 1.2) < 0.01
        assert abs(new_height - original_height * 1.2) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
