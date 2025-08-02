#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 20:36:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_rectangle.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_rectangle.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scitex.plt.ax._plot import plot_rectangle

matplotlib.use("Agg")


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test creating a basic plot_rectangle
        xx, yy = 1.0, 2.0  # Bottom-left corner
        ww, hh = 3.0, 4.0  # Width and height

        # Add plot_rectangle to the plot
        ax = plot_rectangle(self.ax, xx, yy, ww, hh)

        # Check that a patch was added to the axis
        assert len(ax.patches) == 1

        # Check that the patch is a Rectangle with correct properties
        patch = ax.patches[0]
        assert isinstance(patch, Rectangle)
        assert patch.get_x() == xx
        assert patch.get_y() == yy
        assert patch.get_width() == ww
        assert patch.get_height() == hh

    def test_with_styling(self):
        # Test creating a plot_rectangle with custom styling
        xx, yy = 1.0, 2.0
        ww, hh = 3.0, 4.0
        color = "red"
        linewidth = 2.0
        alpha = 0.5

        # Add plot_rectangle with styling
        ax = plot_rectangle(
            self.ax,
            xx,
            yy,
            ww,
            hh,
            facecolor=color,
            linewidth=linewidth,
            alpha=alpha,
        )

        # Check that the patch has the correct styling
        patch = ax.patches[0]
        assert patch.get_facecolor()[0:3] == matplotlib.colors.to_rgb(color)
        assert patch.get_linewidth() == linewidth
        assert patch.get_alpha() == alpha

    def test_multiple_plot_rectangles(self):
        # Test adding multiple plot_rectangles
        # First plot_rectangle
        ax = plot_rectangle(self.ax, 0, 0, 1, 1, facecolor="red")

        # Second plot_rectangle
        ax = plot_rectangle(ax, 1, 1, 1, 1, facecolor="blue")

        # Third plot_rectangle
        ax = plot_rectangle(ax, 2, 2, 1, 1, facecolor="green")

        # Check that all three plot_rectangles were added
        assert len(ax.patches) == 3

        # Check colors of plot_rectangles
        assert ax.patches[0].get_facecolor()[0:3] == matplotlib.colors.to_rgb("red")
        assert ax.patches[1].get_facecolor()[0:3] == matplotlib.colors.to_rgb("blue")
        assert ax.patches[2].get_facecolor()[0:3] == matplotlib.colors.to_rgb("green")

    def test_edge_cases(self):
        # Test with zero width/height
        ax = plot_rectangle(self.ax, 0, 0, 0, 0)
        patch = ax.patches[0]
        assert patch.get_width() == 0
        assert patch.get_height() == 0

        # Test with negative width/height (will be rendered correctly by matplotlib)
        ax = plot_rectangle(self.ax, 5, 5, -1, -1)
        patch = ax.patches[1]
        assert patch.get_width() == -1
        assert patch.get_height() == -1

    def test_plot_rectangle_savefig(self):

        ax = plot_rectangle(self.ax, 0.2, 0.3, 0.5, 0.4, facecolor="blue", alpha=0.5)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # Saving
        from scitex.io import save

        spath = f"./{os.path.basename(__file__)}.jpg"
        save(self.fig, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_rectangle.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 08:45:44 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_rectangle.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_plot/_plot_rectangle.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from matplotlib.patches import Rectangle
# 
# 
# def plot_rectangle(ax, xx, yy, ww, hh, **kwargs):
#     """Add a rectangle patch to an axes.
# 
#     Convenience function for adding rectangular patches to plots, useful for
#     highlighting regions, creating box annotations, or drawing geometric shapes.
# 
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The axes to add the rectangle to.
#     xx : float
#         X-coordinate of the rectangle's bottom-left corner.
#     yy : float
#         Y-coordinate of the rectangle's bottom-left corner.
#     ww : float
#         Width of the rectangle.
#     hh : float
#         Height of the rectangle.
#     **kwargs : dict
#         Additional keyword arguments passed to matplotlib.patches.Rectangle.
#         Common options include:
#         - facecolor/fc : fill color
#         - edgecolor/ec : edge color
#         - linewidth/lw : edge line width
#         - alpha : transparency (0-1)
#         - linestyle/ls : edge line style
# 
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The axes with the rectangle added.
# 
#     Examples
#     --------
#     >>> fig, ax = plt.subplots()
#     >>> ax.plot([0, 10], [0, 10])
#     >>> # Highlight a region
#     >>> plot_rectangle(ax, 2, 3, 4, 3, facecolor='yellow', alpha=0.3)
# 
#     >>> # Draw a box annotation
#     >>> plot_rectangle(ax, 5, 5, 2, 2, facecolor='none', edgecolor='red', linewidth=2)
# 
#     >>> # Create a filled rectangle
#     >>> plot_rectangle(ax, 0, 0, 1, 1, facecolor='blue', edgecolor='black')
# 
#     See Also
#     --------
#     matplotlib.patches.Rectangle : The underlying Rectangle class
#     matplotlib.axes.Axes.add_patch : Method used to add the patch
#     """
#     ax.add_patch(Rectangle((xx, yy), ww, hh, **kwargs))
#     return ax
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_rectangle.py
# --------------------------------------------------------------------------------
