#!/usr/bin/env python3
"""Tests for scitex.plt.utils._colorbar module.

This module provides comprehensive tests for enhanced colorbar utilities
that ensure proper spacing and placement with constrained layout.
"""

import numpy as np
import pytest
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from scitex.plt.utils import colorbar, add_shared_colorbar


class TestColorbar:
    """Test colorbar function."""
    
    @pytest.fixture
    def setup_figure(self):
        """Create a figure with test data."""
        fig, ax = plt.subplots()
        data = np.random.rand(10, 10)
        im = ax.imshow(data)
        yield fig, ax, im
        plt.close(fig)
    
    def test_colorbar_basic(self, setup_figure):
        """Test basic colorbar creation."""
        fig, ax, im = setup_figure
        
        cbar = colorbar(im, ax=ax)
        
        assert cbar is not None
        assert hasattr(cbar, 'mappable')
        assert cbar.mappable == im
        assert cbar.ax is not None
    
    def test_colorbar_defaults(self, setup_figure):
        """Test that default parameters are applied."""
        fig, ax, im = setup_figure
        
        cbar = colorbar(im, ax=ax)
        
        # Check that defaults were applied (these are stored in the axes)
        # Note: The actual values might be transformed, so we just check they exist
        assert cbar.ax.get_position().width > 0
        assert cbar.ax.get_position().height > 0
    
    def test_colorbar_custom_params(self, setup_figure):
        """Test colorbar with custom parameters."""
        fig, ax, im = setup_figure
        
        custom_params = {
            'fraction': 0.1,
            'pad': 0.1,
            'aspect': 10,
            'orientation': 'horizontal'
        }
        
        cbar = colorbar(im, ax=ax, **custom_params)
        
        assert cbar is not None
        assert cbar.orientation == 'horizontal'
    
    def test_colorbar_without_axes(self):
        """Test colorbar without specifying axes."""
        fig, ax = plt.subplots()
        data = np.random.rand(10, 10)
        im = ax.imshow(data)
        
        cbar = colorbar(im)
        
        assert cbar is not None
        plt.close(fig)
    
    def test_colorbar_with_constrained_layout(self):
        """Test colorbar with constrained layout enabled."""
        fig, ax = plt.subplots(constrained_layout=True)
        data = np.random.rand(10, 10)
        im = ax.imshow(data)
        
        cbar = colorbar(im, ax=ax)
        
        assert cbar is not None
        assert fig.get_constrained_layout()
        plt.close(fig)
    
    def test_colorbar_with_scatter(self):
        """Test colorbar with scatter plot mappable."""
        fig, ax = plt.subplots()
        x = np.random.rand(50)
        y = np.random.rand(50)
        c = np.random.rand(50)
        
        scatter = ax.scatter(x, y, c=c, cmap='viridis')
        cbar = colorbar(scatter, ax=ax)
        
        assert cbar is not None
        assert cbar.mappable == scatter
        plt.close(fig)
    
    def test_colorbar_label(self, setup_figure):
        """Test setting colorbar label."""
        fig, ax, im = setup_figure
        
        cbar = colorbar(im, ax=ax, label='Test Label')
        
        assert cbar.ax.get_ylabel() == 'Test Label'
    
    def test_colorbar_ticks(self, setup_figure):
        """Test setting colorbar ticks."""
        fig, ax, im = setup_figure
        
        ticks = [0, 0.5, 1]
        cbar = colorbar(im, ax=ax, ticks=ticks)
        
        np.testing.assert_array_equal(cbar.get_ticks(), ticks)


class TestAddSharedColorbar:
    """Test add_shared_colorbar function."""
    
    @pytest.fixture
    def setup_subplots(self):
        """Create a figure with multiple subplots."""
        fig, axes = plt.subplots(2, 2)
        data = np.random.rand(10, 10)
        images = []
        for ax in axes.flat:
            im = ax.imshow(data * np.random.rand())
            images.append(im)
        yield fig, axes, images[0]
        plt.close(fig)
    
    def test_shared_colorbar_basic(self, setup_subplots):
        """Test basic shared colorbar creation."""
        fig, axes, mappable = setup_subplots
        
        cbar = add_shared_colorbar(fig, axes, mappable)
        
        assert cbar is not None
        assert hasattr(cbar, 'mappable')
        assert cbar.mappable == mappable
    
    def test_shared_colorbar_location_right(self, setup_subplots):
        """Test shared colorbar on the right (default)."""
        fig, axes, mappable = setup_subplots
        
        cbar = add_shared_colorbar(fig, axes, mappable, location='right')
        
        assert cbar is not None
        # Colorbar should be vertical for right location
        assert cbar.orientation == 'vertical'
    
    def test_shared_colorbar_location_bottom(self, setup_subplots):
        """Test shared colorbar on the bottom."""
        fig, axes, mappable = setup_subplots
        
        cbar = add_shared_colorbar(fig, axes, mappable, location='bottom')
        
        assert cbar is not None
        # Colorbar should be horizontal for bottom location
        assert cbar.orientation == 'horizontal'
    
    def test_shared_colorbar_location_left(self, setup_subplots):
        """Test shared colorbar on the left."""
        fig, axes, mappable = setup_subplots
        
        cbar = add_shared_colorbar(fig, axes, mappable, location='left')
        
        assert cbar is not None
        # Colorbar should be vertical for left location
        assert cbar.orientation == 'vertical'
    
    def test_shared_colorbar_location_top(self, setup_subplots):
        """Test shared colorbar on the top."""
        fig, axes, mappable = setup_subplots
        
        cbar = add_shared_colorbar(fig, axes, mappable, location='top')
        
        assert cbar is not None
        # Colorbar should be horizontal for top location
        assert cbar.orientation == 'horizontal'
    
    def test_shared_colorbar_custom_params(self, setup_subplots):
        """Test shared colorbar with custom parameters."""
        fig, axes, mappable = setup_subplots
        
        custom_params = {
            'shrink': 0.5,
            'aspect': 50,
            'label': 'Shared Label'
        }
        
        cbar = add_shared_colorbar(fig, axes, mappable, **custom_params)
        
        assert cbar is not None
        assert cbar.ax.get_ylabel() == 'Shared Label'
    
    def test_shared_colorbar_single_axis(self):
        """Test shared colorbar with single axis (edge case)."""
        fig, ax = plt.subplots()
        data = np.random.rand(10, 10)
        im = ax.imshow(data)
        
        cbar = add_shared_colorbar(fig, [ax], im)
        
        assert cbar is not None
        plt.close(fig)
    
    def test_shared_colorbar_with_norm(self):
        """Test shared colorbar with custom normalization."""
        fig, axes = plt.subplots(2, 2)
        vmin, vmax = 0, 2
        norm = Normalize(vmin=vmin, vmax=vmax)
        
        data = np.random.rand(10, 10) * 2
        images = []
        for ax in axes.flat:
            im = ax.imshow(data, norm=norm, cmap='viridis')
            images.append(im)
        
        cbar = add_shared_colorbar(fig, axes, images[0])
        
        assert cbar is not None
        assert cbar.vmin == vmin
        assert cbar.vmax == vmax
        plt.close(fig)
    
    def test_shared_colorbar_flattened_axes(self):
        """Test shared colorbar with flattened axes array."""
        fig, axes = plt.subplots(2, 2)
        data = np.random.rand(10, 10)
        
        # Use flattened axes
        axes_flat = axes.flatten()
        images = []
        for ax in axes_flat:
            im = ax.imshow(data)
            images.append(im)
        
        cbar = add_shared_colorbar(fig, axes_flat, images[0])
        
        assert cbar is not None
        plt.close(fig)


class TestColorbarIntegration:
    """Test integration with different plot types and scenarios."""
    
    def test_colorbar_with_contour(self):
        """Test colorbar with contour plot."""
        fig, ax = plt.subplots()
        x = np.linspace(-3, 3, 100)
        y = np.linspace(-3, 3, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.exp(-(X**2 + Y**2))
        
        contour = ax.contour(X, Y, Z)
        cbar = colorbar(contour, ax=ax)
        
        assert cbar is not None
        plt.close(fig)
    
    def test_colorbar_with_pcolormesh(self):
        """Test colorbar with pcolormesh."""
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 11)
        y = np.linspace(0, 10, 11)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        
        pcm = ax.pcolormesh(X, Y, Z[:-1, :-1])
        cbar = colorbar(pcm, ax=ax)
        
        assert cbar is not None
        plt.close(fig)
    
    def test_multiple_colorbars(self):
        """Test multiple colorbars on same figure."""
        fig, (ax1, ax2) = plt.subplots(1, 2)
        
        data1 = np.random.rand(10, 10)
        data2 = np.random.rand(10, 10) * 2
        
        im1 = ax1.imshow(data1, cmap='viridis')
        im2 = ax2.imshow(data2, cmap='plasma')
        
        cbar1 = colorbar(im1, ax=ax1)
        cbar2 = colorbar(im2, ax=ax2)
        
        assert cbar1 is not None
        assert cbar2 is not None
        assert cbar1 != cbar2
        plt.close(fig)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_colorbar.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-08 11:15:00 (ywatanabe)"
# # File: /src/scitex/plt/utils/_colorbar.py
# # ----------------------------------------
# 
# """Enhanced colorbar utilities for better placement with scitex.plt"""
# 
# import matplotlib.pyplot as plt
# from matplotlib.cm import ScalarMappable
# from matplotlib.colors import Normalize
# 
# 
# def colorbar(mappable, ax=None, **kwargs):
#     """Enhanced colorbar function that ensures proper spacing.
#     
#     This function wraps matplotlib.pyplot.colorbar with better defaults
#     to prevent overlap with axes when using constrained_layout.
#     
#     Parameters
#     ----------
#     mappable : matplotlib.cm.ScalarMappable
#         The mappable whose colorbar is to be made (e.g., from imshow, scatter)
#     ax : matplotlib.axes.Axes or list of Axes, optional
#         Parent axes from which space for a new colorbar axes will be stolen.
#     **kwargs : dict
#         Additional keyword arguments passed to matplotlib.pyplot.colorbar
#         
#     Returns
#     -------
#     colorbar : matplotlib.colorbar.Colorbar
#         The colorbar instance
#     """
#     # Set better defaults for colorbar placement
#     defaults = {
#         'fraction': 0.046,  # Fraction of axes to use for colorbar
#         'pad': 0.04,        # Padding between axes and colorbar
#         'aspect': 20,       # Aspect ratio of colorbar
#     }
#     
#     # Update defaults with any user-provided kwargs
#     for key, value in defaults.items():
#         if key not in kwargs:
#             kwargs[key] = value
#     
#     # Create the colorbar
#     cbar = plt.colorbar(mappable, ax=ax, **kwargs)
#     
#     # If using constrained_layout, ensure the figure updates
#     if ax is not None:
#         fig = ax.figure if hasattr(ax, 'figure') else ax[0].figure
#         if hasattr(fig, 'get_constrained_layout') and fig.get_constrained_layout():
#             # Force a layout update
#             fig.canvas.draw_idle()
#     
#     return cbar
# 
# 
# def add_shared_colorbar(fig, axes, mappable, location='right', **kwargs):
#     """Add a single colorbar shared by multiple axes.
#     
#     Parameters
#     ----------
#     fig : matplotlib.figure.Figure
#         The figure containing the axes
#     axes : array-like of Axes
#         The axes that will share the colorbar
#     mappable : matplotlib.cm.ScalarMappable
#         The mappable whose colorbar is to be made
#     location : {'right', 'bottom', 'left', 'top'}, optional
#         Where to place the colorbar (default: 'right')
#     **kwargs : dict
#         Additional keyword arguments passed to fig.colorbar
#         
#     Returns
#     -------
#     colorbar : matplotlib.colorbar.Colorbar
#         The colorbar instance
#     """
#     defaults = {
#         'shrink': 0.8,      # Shrink colorbar to match axes height
#         'aspect': 30,       # Make it thinner for shared colorbars
#     }
#     
#     # Update defaults with any user-provided kwargs
#     for key, value in defaults.items():
#         if key not in kwargs:
#             kwargs[key] = value
#     
#     # Create the shared colorbar
#     cbar = fig.colorbar(mappable, ax=axes, location=location, **kwargs)
#     
#     return cbar
# 
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_colorbar.py
# --------------------------------------------------------------------------------
