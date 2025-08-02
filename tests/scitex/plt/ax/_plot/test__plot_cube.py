#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 10:31:25 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_cube.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_cube.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
from scitex.plt.ax._plot import plot_cube


class TestPlotCube:
    def setup_method(self):
        # Create output directory if it doesn't exist
        self.out_dir = __file__.replace(".py", "_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def save_test_figure(self, fig, method_name):
        """Helper method to save figure using method name"""
        from scitex.io import save

        spath = f"./{os.path.basename(__file__).replace('.py', '')}_{method_name}.jpg"
        save(fig, spath)
        # Check saved file
        actual_spath = os.path.join(self.out_dir, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    def test_plot_cube_creates_12_edges(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        r1 = [0, 1]
        r2 = [0, 1]
        r3 = [0, 1]
        plot_cube(ax, r1, r2, r3)
        ax.set_title("3D Cube with 12 Edges")

        # Save figure
        self.save_test_figure(fig, "test_plot_cube_creates_12_edges")

        # Clean up
        plt.close(fig)

    def test_plot_cube_with_custom_color(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        r1 = [0, 1]
        r2 = [0, 1]
        r3 = [0, 1]
        plot_cube(ax, r1, r2, r3, c="red")
        ax.set_title("3D Cube with Custom Color")

        # Save figure
        self.save_test_figure(fig, "test_plot_cube_with_custom_color")

        # Clean up
        plt.close(fig)

    def test_plot_cube_with_custom_alpha(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        r1 = [0, 1]
        r2 = [0, 1]
        r3 = [0, 1]
        plot_cube(ax, r1, r2, r3, alpha=0.5)
        ax.set_title("3D Cube with Custom Alpha")

        # Save figure
        self.save_test_figure(fig, "test_plot_cube_with_custom_alpha")

        # Clean up
        plt.close(fig)

    def test_plot_cube_savefig(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        ax = plot_cube(ax, [0, 1], [0, 1], [0, 1], c="red")
        ax.set_title("3D Cube Plot")

        # Saving
        from scitex.io import save

        spath = f"./{os.path.basename(__file__)}.jpg"
        save(fig, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

        # Clean up
        plt.close(fig)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_cube.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 15:21:37 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_cube.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_plot/_plot_cube.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from itertools import combinations, product
# 
# import numpy as np
# 
# 
# def plot_cube(ax, xlim, ylim, zlim, c="blue", alpha=1.0):
#     """
#     Plot a 3D cube on the given axis.
# 
#     Args:
#         ax: Matplotlib 3D axis
#         xlim: Range for x-axis as a tuple (min, max)
#         ylim: Range for y-axis as a tuple (min, max)
#         zlim: Range for z-axis as a tuple (min, max)
#         c: Color of the cube edges (default: 'blue')
#         alpha: Transparency of the cube edges (default: 1.0)
# 
#     Returns:
#         Matplotlib axis with the cube plotted
#     """
#     # Validate inputs
#     assert hasattr(ax, "plot3D"), "The axis must be a 3D axis with plot3D method"
#     assert len(xlim) == 2, "xlim must be a tuple of (min, max)"
#     assert len(ylim) == 2, "ylim must be a tuple of (min, max)"
#     assert len(zlim) == 2, "zlim must be a tuple of (min, max)"
#     assert xlim[0] < xlim[1], "xlim[0] must be less than xlim[1]"
#     assert ylim[0] < ylim[1], "ylim[0] must be less than ylim[1]"
#     assert zlim[0] < zlim[1], "zlim[0] must be less than zlim[1]"
# 
#     # Get all corners of the cube
#     corners = np.array(list(product(xlim, ylim, zlim)))
# 
#     # Draw edges between corners
#     for start, end in combinations(corners, 2):
#         # Check if the points form an edge (differ in exactly one dimension)
#         if np.sum(np.abs(start - end)) == xlim[1] - xlim[0]:
#             ax.plot3D(*zip(start, end), c=c, linewidth=3, alpha=alpha)
#         if np.sum(np.abs(start - end)) == ylim[1] - ylim[0]:
#             ax.plot3D(*zip(start, end), c=c, linewidth=3, alpha=alpha)
#         if np.sum(np.abs(start - end)) == zlim[1] - zlim[0]:
#             ax.plot3D(*zip(start, end), c=c, linewidth=3, alpha=alpha)
# 
#     return ax
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_plot/_plot_cube.py
# --------------------------------------------------------------------------------
