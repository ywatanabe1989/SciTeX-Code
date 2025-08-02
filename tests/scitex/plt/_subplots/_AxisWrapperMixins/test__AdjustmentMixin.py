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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_AxisWrapperMixins/_AdjustmentMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-07 15:49:20 (ywatanabe)"
# # File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_AdjustmentMixin.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/_subplots/_AxisWrapperMixins/_AdjustmentMixin.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from typing import List, Optional, Union
# 
# from ....plt import ax as ax_module
# 
# 
# class AdjustmentMixin:
#     """Mixin class for matplotlib axis adjustments."""
# 
#     def rotate_labels(
#         self,
#         x: float = 30,
#         y: float = 30,
#         x_ha: str = "right",
#         y_ha: str = "center",
#     ) -> None:
#         self._axis_mpl = ax_module.rotate_labels(
#             self._axis_mpl, x=x, y=y, x_ha=x_ha, y_ha=y_ha
#         )
# 
#     def legend(self, loc: str = "upper left", **kwargs) -> None:
#         """Places legend at specified location, with support for outside positions.
# 
#         Parameters
#         ----------
#         loc : str
#             Legend position. Standard matplotlib positions plus:
#             - "outer": Automatically place legend outside plot area (right side)
#             - "separate": Save legend as a separate figure file
#             - upper/lower/center variants: e.g. "upper right out", "lower left out"
#             - directional shortcuts: "right", "left", "upper", "lower"
#             - center variants: "center right out", "center left out"
#             - alternative formats: "right upper out", "left lower out" etc.
#         **kwargs : dict
#             Additional keyword arguments passed to legend()
#             For "separate": can include 'filename' (default: 'legend.png')
#         """
#         import matplotlib.pyplot as plt
#         
#         # Handle special cases
#         if loc == "outer":
#             # Place legend outside on the right, adjusting figure to make room
#             legend = self._axis_mpl.legend(
#                 loc='center left', 
#                 bbox_to_anchor=(1.02, 0.5),
#                 **kwargs
#             )
#             # Adjust figure to prevent legend cutoff
#             if hasattr(self, '_figure_wrapper') and self._figure_wrapper:
#                 self._figure_wrapper._fig_mpl.tight_layout()
#                 self._figure_wrapper._fig_mpl.subplots_adjust(right=0.85)
#             return legend
#             
#         elif loc == "separate":
#             # Set flag to save legend separately when figure is saved
#             import warnings
#             
#             handles, labels = self._axis_mpl.get_legend_handles_labels()
#             if not handles:
#                 warnings.warn("No legend handles found. Create plots with labels first.")
#                 return None
#             
#             # Store legend params for later use during save
#             fig = self._axis_mpl.get_figure()
#             if not hasattr(fig, '_separate_legend_params'):
#                 fig._separate_legend_params = []
#             
#             # Extract separate-specific kwargs
#             figsize = kwargs.pop('figsize', (4, 3))
#             dpi = kwargs.pop('dpi', 150)
#             frameon = kwargs.pop('frameon', True)
#             fancybox = kwargs.pop('fancybox', True)
#             shadow = kwargs.pop('shadow', True)
#             
#             # Store parameters for this axes
#             # Include axis index or name for unique filenames
#             axis_id = None
#             
#             # Try to find axis index in parent figure
#             try:
#                 fig_axes = fig.get_axes()
#                 for idx, ax in enumerate(fig_axes):
#                     if ax is self._axis_mpl:
#                         axis_id = f"ax_{idx:02d}"
#                         break
#             except:
#                 pass
#             
#             # If not found, try subplot spec
#             if axis_id is None and hasattr(self._axis_mpl, 'get_subplotspec'):
#                 try:
#                     spec = self._axis_mpl.get_subplotspec()
#                     if spec is not None:
#                         # Get grid shape and position
#                         gridspec = spec.get_gridspec()
#                         nrows, ncols = gridspec.get_geometry()
#                         rowspan = spec.rowspan
#                         colspan = spec.colspan
#                         # Calculate flat index from row/col position
#                         row_start = rowspan.start if hasattr(rowspan, 'start') else rowspan
#                         col_start = colspan.start if hasattr(colspan, 'start') else colspan
#                         flat_idx = row_start * ncols + col_start
#                         axis_id = f"ax_{flat_idx:02d}"
#                 except:
#                     pass
#             
#             # Fallback to sequential numbering
#             if axis_id is None:
#                 axis_id = f"ax_{len(fig._separate_legend_params):02d}"
#                 
#             fig._separate_legend_params.append({
#                 'axis': self._axis_mpl,
#                 'axis_id': axis_id,
#                 'handles': handles,
#                 'labels': labels,
#                 'figsize': figsize,
#                 'dpi': dpi,
#                 'frameon': frameon,
#                 'fancybox': fancybox,
#                 'shadow': shadow,
#                 'kwargs': kwargs
#             })
#             
#             # Remove legend from main figure immediately
#             if self._axis_mpl.get_legend():
#                 self._axis_mpl.get_legend().remove()
#             
#             return None
# 
#         # Original outside positions
#         outside_positions = {
#             # Upper right variants
#             "upper right out": ("center left", (1.15, 0.85)),
#             "right upper out": ("center left", (1.15, 0.85)),
#             # Center right variants
#             "center right out": ("center left", (1.15, 0.5)),
#             "right out": ("center left", (1.15, 0.5)),
#             "right": ("center left", (1.05, 0.5)),
#             # Lower right variants
#             "lower right out": ("center left", (1.15, 0.15)),
#             "right lower out": ("center left", (1.15, 0.15)),
#             # Upper left variants
#             "upper left out": ("center right", (-0.25, 0.85)),
#             "left upper out": ("center right", (-0.25, 0.85)),
#             # Center left variants
#             "center left out": ("center right", (-0.25, 0.5)),
#             "left out": ("center right", (-0.25, 0.5)),
#             "left": ("center right", (-0.15, 0.5)),
#             # Lower left variants
#             "lower left out": ("center right", (-0.25, 0.15)),
#             "left lower out": ("center right", (-0.25, 0.15)),
#             # Upper center variants
#             "upper center out": ("lower center", (0.5, 1.25)),
#             "upper out": ("lower center", (0.5, 1.25)),
#             # Lower center variants
#             "lower center out": ("upper center", (0.5, -0.25)),
#             "lower out": ("upper center", (0.5, -0.25)),
#         }
# 
#         if loc in outside_positions:
#             location, bbox = outside_positions[loc]
#             return self._axis_mpl.legend(loc=location, bbox_to_anchor=bbox, **kwargs)
#         return self._axis_mpl.legend(loc=loc, **kwargs)
# 
#     def set_xyt(
#         self,
#         x: Optional[str] = None,
#         y: Optional[str] = None,
#         t: Optional[str] = None,
#         format_labels: bool = True,
#     ) -> None:
#         self._axis_mpl = ax_module.set_xyt(
#             self._axis_mpl,
#             x=x,
#             y=y,
#             t=t,
#             format_labels=format_labels,
#         )
# 
#     def set_xytc(
#         self,
#         x: Optional[str] = None,
#         y: Optional[str] = None,
#         t: Optional[str] = None,
#         c: Optional[str] = None,
#         format_labels: bool = True,
#     ) -> None:
#         """Set xlabel, ylabel, title, and caption for automatic saving.
# 
#         Parameters
#         ----------
#         x : str, optional
#             X-axis label
#         y : str, optional
#             Y-axis label
#         t : str, optional
#             Title
#         c : str, optional
#             Caption to be saved automatically with scitex.io.save()
#         format_labels : bool, optional
#             Whether to apply automatic formatting, by default True
#         """
#         self._axis_mpl = ax_module.set_xytc(
#             self._axis_mpl,
#             x=x,
#             y=y,
#             t=t,
#             c=c,
#             format_labels=format_labels,
#         )
# 
#         # Store caption in this wrapper for easy access
#         if c is not False and c is not None:
#             self._scitex_caption = c
# 
#     def set_supxyt(
#         self,
#         xlabel: Optional[str] = None,
#         ylabel: Optional[str] = None,
#         title: Optional[str] = None,
#         format_labels: bool = True,
#     ) -> None:
#         self._axis_mpl = ax_module.set_supxyt(
#             self._axis_mpl,
#             xlabel=xlabel,
#             ylabel=ylabel,
#             title=title,
#             format_labels=format_labels,
#         )
# 
#     def set_supxytc(
#         self,
#         xlabel: Optional[str] = None,
#         ylabel: Optional[str] = None,
#         title: Optional[str] = None,
#         caption: Optional[str] = None,
#         format_labels: bool = True,
#     ) -> None:
#         """Set figure-level xlabel, ylabel, title, and caption for automatic saving.
# 
#         Parameters
#         ----------
#         xlabel : str, optional
#             Figure-level X-axis label
#         ylabel : str, optional
#             Figure-level Y-axis label
#         title : str, optional
#             Figure-level title (suptitle)
#         caption : str, optional
#             Figure-level caption to be saved automatically with scitex.io.save()
#         format_labels : bool, optional
#             Whether to apply automatic formatting, by default True
#         """
#         self._axis_mpl = ax_module.set_supxytc(
#             self._axis_mpl,
#             xlabel=xlabel,
#             ylabel=ylabel,
#             title=title,
#             caption=caption,
#             format_labels=format_labels,
#         )
# 
#         # Store figure-level caption for easy access
#         if caption is not False and caption is not None:
#             fig = self._axis_mpl.get_figure()
#             fig._scitex_main_caption = caption
# 
#     def set_meta(
#         self,
#         caption=None,
#         methods=None,
#         stats=None,
#         keywords=None,
#         experimental_details=None,
#         journal_style=None,
#         significance=None,
#         **kwargs
#     ) -> None:
#         """Set comprehensive scientific metadata with YAML export capability.
# 
#         Parameters
#         ----------
#         caption : str, optional
#             Figure caption text
#         methods : str, optional
#             Experimental methods description
#         stats : str, optional
#             Statistical analysis details
#         keywords : List[str], optional
#             Keywords for categorization
#         experimental_details : Dict[str, Any], optional
#             Structured experimental parameters
#         journal_style : str, optional
#             Target journal style
#         significance : str, optional
#             Significance statement
#         **kwargs : additional metadata
#             Any additional metadata fields
#         """
#         self._axis_mpl = ax_module.set_meta(
#             self._axis_mpl,
#             caption=caption,
#             methods=methods,
#             stats=stats,
#             keywords=keywords,
#             experimental_details=experimental_details,
#             journal_style=journal_style,
#             significance=significance,
#             **kwargs
#         )
# 
#     def set_figure_meta(
#         self,
#         caption=None,
#         methods=None,
#         stats=None,
#         significance=None,
#         funding=None,
#         conflicts=None,
#         data_availability=None,
#         **kwargs
#     ) -> None:
#         """Set figure-level metadata for multi-panel figures.
# 
#         Parameters
#         ----------
#         caption : str, optional
#             Figure-level caption
#         methods : str, optional
#             Overall experimental methods
#         stats : str, optional
#             Overall statistical approach
#         significance : str, optional
#             Significance and implications
#         funding : str, optional
#             Funding acknowledgments
#         conflicts : str, optional
#             Conflict of interest statement
#         data_availability : str, optional
#             Data availability statement
#         **kwargs : additional metadata
#             Any additional figure-level metadata
#         """
#         self._axis_mpl = ax_module.set_figure_meta(
#             self._axis_mpl,
#             caption=caption,
#             methods=methods,
#             stats=stats,
#             significance=significance,
#             funding=funding,
#             conflicts=conflicts,
#             data_availability=data_availability,
#             **kwargs
#         )
# 
#     def set_ticks(
#         self,
#         xvals: Optional[List[Union[int, float]]] = None,
#         xticks: Optional[List[str]] = None,
#         yvals: Optional[List[Union[int, float]]] = None,
#         yticks: Optional[List[str]] = None,
#     ) -> None:
#         self._axis_mpl = ax_module.set_ticks(
#             self._axis_mpl,
#             xvals=xvals,
#             xticks=xticks,
#             yvals=yvals,
#             yticks=yticks,
#         )
# 
#     def set_n_ticks(self, n_xticks: int = 4, n_yticks: int = 4) -> None:
#         self._axis_mpl = ax_module.set_n_ticks(
#             self._axis_mpl, n_xticks=n_xticks, n_yticks=n_yticks
#         )
# 
#     def hide_spines(
#         self,
#         top: bool = True,
#         bottom: bool = False,
#         left: bool = False,
#         right: bool = True,
#         ticks: bool = False,
#         labels: bool = False,
#     ) -> None:
#         self._axis_mpl = ax_module.hide_spines(
#             self._axis_mpl,
#             top=top,
#             bottom=bottom,
#             left=left,
#             right=right,
#             ticks=ticks,
#             labels=labels,
#         )
# 
#     def extend(self, x_ratio: float = 1.0, y_ratio: float = 1.0) -> None:
#         self._axis_mpl = ax_module.extend(
#             self._axis_mpl, x_ratio=x_ratio, y_ratio=y_ratio
#         )
# 
#     def shift(self, dx: float = 0, dy: float = 0) -> None:
#         self._axis_mpl = ax_module.shift(self._axis_mpl, dx=dx, dy=dy)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/_subplots/_AxisWrapperMixins/_AdjustmentMixin.py
# --------------------------------------------------------------------------------
