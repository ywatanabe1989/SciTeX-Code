#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:33 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__rotate_labels.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__rotate_labels.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from scitex.plt.ax._style import rotate_labels


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        # Create a basic plot with labels
        xx = np.linspace(0, 10, 5)
        yy = np.sin(xx)
        self.ax.plot(xx, yy)
        self.ax.set_xticks(xx)
        self.ax.set_yticks(yy)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test with default parameters
        ax = rotate_labels(self.ax)

        # Force draw to ensure labels are updated
        self.fig.canvas.draw()

        # Check x and y tick label rotations
        for label in ax.get_xticklabels():
            assert label.get_rotation() == 45
            assert label.get_ha() == "center"

        for label in ax.get_yticklabels():
            assert label.get_rotation() == 45
            assert label.get_ha() == "center"

    def test_custom_rotations(self):
        # Test with custom rotation angles
        ax = rotate_labels(self.ax, x=30, y=60)

        # Force draw to ensure labels are updated
        self.fig.canvas.draw()

        # Check custom x and y tick label rotations
        for label in ax.get_xticklabels():
            assert label.get_rotation() == 30

        for label in ax.get_yticklabels():
            assert label.get_rotation() == 60

    def test_custom_alignment(self):
        # Test with custom horizontal alignments
        ax = rotate_labels(self.ax, x_ha="left", y_ha="right")

        # Force draw to ensure labels are updated
        self.fig.canvas.draw()

        # Check custom alignments
        for label in ax.get_xticklabels():
            assert label.get_ha() == "left"

        for label in ax.get_yticklabels():
            assert label.get_ha() == "right"

    def test_rotate_x_only(self):
        # Test rotating only x labels
        ax = rotate_labels(self.ax, x=90, y=0)

        # Force draw to ensure labels are updated
        self.fig.canvas.draw()

        # Check that x labels are rotated but y labels are vertical
        for label in ax.get_xticklabels():
            assert label.get_rotation() == 90

        for label in ax.get_yticklabels():
            assert label.get_rotation() == 0

    def test_rotate_y_only(self):
        # Test rotating only y labels
        ax = rotate_labels(self.ax, x=0, y=90)

        # Force draw to ensure labels are updated
        self.fig.canvas.draw()

        # Check that y labels are rotated but x labels are horizontal
        for label in ax.get_xticklabels():
            assert label.get_rotation() == 0

        for label in ax.get_yticklabels():
            assert label.get_rotation() == 90

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        rotate_labels(self.ax, x=45, y=30)

        # Saving
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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_rotate_labels.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-27 13:24:32 (ywatanabe)"
# # /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/plt/ax/_rotate_labels.py
#
# """This script does XYZ."""
#
# """Imports"""
# def rotate_labels(ax, x=45, y=45, x_ha='center', y_ha='center'):
#     """
#     Rotate x and y axis labels of a matplotlib Axes object.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The Axes object to modify.
#     x : float, optional
#         Rotation angle for x-axis labels in degrees. Default is 45.
#     y : float, optional
#         Rotation angle for y-axis labels in degrees. Default is 45.
#     x_ha : str, optional
#         Horizontal alignment for x-axis labels. Default is 'center'.
#     y_ha : str, optional
#         Horizontal alignment for y-axis labels. Default is 'center'.
#
#     Returns
#     -------
#     matplotlib.axes.Axes
#         The modified Axes object.
#
#     Example
#     -------
#     fig, ax = plt.subplots()
#     ax.plot([1, 2, 3], [1, 2, 3])
#     rotate_labels(ax)
#     plt.show()
#     """
#     # Get current tick positions
#     xticks = ax.get_xticks()
#     yticks = ax.get_yticks()
#
#     # Set ticks explicitly
#     ax.set_xticks(xticks)
#     ax.set_yticks(yticks)
#
#     # Set labels with rotation
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=x, ha=x_ha)
#     ax.set_yticklabels(ax.get_yticklabels(), rotation=y, ha=y_ha)
#     return ax

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_rotate_labels.py
# --------------------------------------------------------------------------------
