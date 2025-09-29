#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__force_aspect.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__force_aspect.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._style import force_aspect

matplotlib.use("Agg")  # Use non-GUI backend for testing


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        # Create an image with known dimensions
        data = np.random.rand(10, 20)  # Height x Width
        self.im = self.ax.imshow(data, extent=[0, 20, 0, 10])  # Width x Height

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test with default aspect (aspect=1)
        ax = force_aspect(self.ax)

        # Get the current aspect ratio
        current_aspect = self.ax.get_aspect()

        # With aspect=1, it should set aspect to ratio of width/height (20/10 = 2) divided by 1
        # So aspect should be 2
        assert np.isclose(current_aspect, 2.0, rtol=1e-2)

    def test_custom_aspect(self):
        # Test with custom aspect = 2
        ax = force_aspect(self.ax, aspect=2)

        # Get the current aspect ratio
        current_aspect = self.ax.get_aspect()

        # With aspect=2, it should set aspect to ratio of width/height (20/10 = 2) divided by 2
        # So aspect should be 1
        assert np.isclose(current_aspect, 1.0, rtol=1e-2)

    def test_no_images(self):
        # Test with no images on the axes
        empty_ax = self.fig.add_subplot(122)

        # Should raise IndexError as the function tries to access im[0]
        with pytest.raises(IndexError):
            force_aspect(empty_ax)

    def test_with_multiple_images(self):
        # Add another image with different dimensions
        second_data = np.random.rand(5, 10)  # Height x Width
        second_im = self.ax.imshow(second_data, extent=[0, 10, 0, 5])  # Width x Height

        # The function should use the first image from get_images()
        ax = force_aspect(self.ax)

        # Get the current aspect ratio
        current_aspect = self.ax.get_aspect()

        # Should still be using the first image (20/10 = 2)
        assert np.isclose(current_aspect, 2.0, rtol=1e-2)

    def test_with_negative_extent(self):
        # Create an image with negative extent
        neg_data = np.random.rand(10, 20)  # Height x Width
        neg_ax = self.fig.add_subplot(133)
        neg_im = neg_ax.imshow(neg_data, extent=[-20, 0, -10, 0])  # Width x Height

        # Test force_aspect
        neg_ax = force_aspect(neg_ax)

        # Should handle negative extent correctly, absolute value is used
        current_aspect = neg_ax.get_aspect()
        assert np.isclose(current_aspect, 2.0, rtol=1e-2)

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        self.ax.set_title("Force Aspect Ratio")
        force_aspect(self.ax, aspect=1.0)

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
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_force_aspect.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 09:00:52 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_force_aspect.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_style/_force_aspect.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import matplotlib
# from ....plt.utils import assert_valid_axis
# 
# 
# def force_aspect(axis, aspect=1):
#     """
#     Forces aspect ratio of an axis based on the extent of the image.
#     
#     Arguments:
#         axis (matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper): The axis to adjust.
#         aspect (float, optional): The aspect ratio to apply. Defaults to 1.
#         
#     Returns:
#         matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper: The axis with adjusted aspect ratio.
#     """
#     assert_valid_axis(axis, "First argument must be a matplotlib axis or scitex axis wrapper")
# 
#     im = axis.get_images()
# 
#     extent = im[0].get_extent()
# 
#     axis.set_aspect(abs((extent[1] - extent[0]) / (extent[3] - extent[2])) / aspect)
#     return axis
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_force_aspect.py
# --------------------------------------------------------------------------------
