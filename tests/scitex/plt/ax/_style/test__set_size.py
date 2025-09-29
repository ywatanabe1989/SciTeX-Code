#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__set_size.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__set_size.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scitex.plt.ax._style import set_size

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
        # Test setting specific dimensions
        target_width = 5.0  # inches
        target_height = 3.0  # inches

        # Set the figure to have specific subplotpars for testing
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        # Use set_size to adjust figure size
        ax = set_size(self.ax, target_width, target_height)

        # Get the figure dimensions and subplot parameters
        figsize = ax.figure.get_size_inches()
        l = ax.figure.subplotpars.left
        r = ax.figure.subplotpars.right
        t = ax.figure.subplotpars.top
        b = ax.figure.subplotpars.bottom

        # Calculate the expected figure dimensions
        expected_width = target_width / (r - l)
        expected_height = target_height / (t - b)

        # Check that figure dimensions match expected values
        assert np.isclose(figsize[0], expected_width)
        assert np.isclose(figsize[1], expected_height)

    def test_aspect_ratio(self):
        # Test maintaining a specific aspect ratio
        target_width = 4.0  # inches
        target_height = 4.0  # inches (square)

        # Use set_size to adjust figure size
        ax = set_size(self.ax, target_width, target_height)

        # Get the figure dimensions
        figsize = ax.figure.get_size_inches()

        # Check that aspect ratio is maintained
        aspect_ratio = figsize[0] / figsize[1]
        expected_aspect_ratio = 1.0  # Square

        assert np.isclose(aspect_ratio, expected_aspect_ratio, rtol=0.1)

    def test_edge_cases(self):
        # Test with very small dimensions
        ax = set_size(self.ax, 0.1, 0.1)
        figsize = ax.figure.get_size_inches()
        assert figsize[0] > 0
        assert figsize[1] > 0

        # Test with very large dimensions
        ax = set_size(self.ax, 100, 100)
        figsize = ax.figure.get_size_inches()
        assert figsize[0] > 0
        assert figsize[1] > 0

    def test_wide_figure(self):
        # Test with wide aspect ratio
        target_width = 8.0  # inches
        target_height = 2.0  # inches

        # Use set_size to adjust figure size
        ax = set_size(self.ax, target_width, target_height)

        # Get the figure dimensions
        figsize = ax.figure.get_size_inches()

        # Check that aspect ratio is correct
        aspect_ratio = figsize[0] / figsize[1]
        expected_aspect_ratio = 4.0  # Wide rectangle

        assert np.isclose(aspect_ratio, expected_aspect_ratio, rtol=0.1)

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        target_width = 4.0
        target_height = 3.0
        self.ax.plot([1, 2, 3], [1, 2, 3])
        set_size(self.ax, target_width, target_height)

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
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_set_size.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2022-12-09 13:38:11 (ywatanabe)"
# 
# 
# def set_size(ax, w, h):
#     """w, h: width, height in inches"""
#     # if not ax: ax=plt.gca()
#     l = ax.figure.subplotpars.left
#     r = ax.figure.subplotpars.right
#     t = ax.figure.subplotpars.top
#     b = ax.figure.subplotpars.bottom
#     figw = float(w) / (r - l)
#     figh = float(h) / (t - b)
#     ax.figure.set_size_inches(figw, figh)
#     return ax

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_set_size.py
# --------------------------------------------------------------------------------
