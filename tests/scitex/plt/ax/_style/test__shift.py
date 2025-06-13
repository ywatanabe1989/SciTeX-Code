#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__shift.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__shift.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._style import shift

matplotlib.use("Agg")


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Basic test case
        original_bbox = self.ax.get_position()

        # Shift 1 inch (2.54 cm) right and up
        shifted_ax = shift(self.ax, dx=2.54, dy=2.54)

        # Get new position
        new_bbox = shifted_ax.get_position()

        # Calculate expected change in position
        fig_width_in, fig_height_in = self.fig.get_size_inches()
        expected_dx_ratio = (2.54 / 2.54) / fig_width_in
        expected_dy_ratio = (2.54 / 2.54) / fig_height_in

        # Check that the ax was shifted correctly
        assert np.isclose(new_bbox.x0, original_bbox.x0 + expected_dx_ratio)
        assert np.isclose(new_bbox.y0, original_bbox.y0 + expected_dy_ratio)

        # Check that width and height are unchanged
        assert np.isclose(new_bbox.width, original_bbox.width)
        assert np.isclose(new_bbox.height, original_bbox.height)

    def test_edge_cases(self):
        # Test with zero shift
        original_bbox = self.ax.get_position()
        shifted_ax = shift(self.ax, dx=0, dy=0)
        new_bbox = shifted_ax.get_position()

        assert np.isclose(new_bbox.x0, original_bbox.x0)
        assert np.isclose(new_bbox.y0, original_bbox.y0)

        # Test with negative shift
        original_bbox = self.ax.get_position()
        shifted_ax = shift(self.ax, dx=-1.27, dy=-1.27)
        new_bbox = shifted_ax.get_position()

        fig_width_in, fig_height_in = self.fig.get_size_inches()
        expected_dx_ratio = (-1.27 / 2.54) / fig_width_in
        expected_dy_ratio = (-1.27 / 2.54) / fig_height_in

        assert np.isclose(new_bbox.x0, original_bbox.x0 + expected_dx_ratio)
        assert np.isclose(new_bbox.y0, original_bbox.y0 + expected_dy_ratio)

    def test_error_handling(self):
        # Test with invalid input types
        with pytest.raises(TypeError):
            shift(self.ax, dx="invalid", dy=0)

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        original_bbox = self.ax.get_position()
        shifted_ax = shift(self.ax, dx=1.27, dy=1.27)

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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_shift.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 09:00:54 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_shift.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_style/_shift.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# def shift(ax, dx=0, dy=0):
#     """
#     Adjusts the position of an Axes object within a Figure by specified offsets in centimeters.
#
#     This function modifies the position of a given matplotlib.axes.Axes object by shifting it horizontally and vertically within its parent figure. The shift amounts are specified in centimeters, and the function converts these values into the figure's coordinate system to perform the adjustment.
#
#     Parameters:
#     - ax (matplotlib.axes.Axes): The Axes object to modify. This must be an instance of a Matplotlib Axes.
#     - dx (float): The horizontal offset in centimeters. Positive values shift the Axes to the right, while negative values shift it to the left.
#     - dy (float): The vertical offset in centimeters. Positive values shift the Axes up, while negative values shift it down.
#
#     Returns:
#     - matplotlib.axes.Axes: The modified Axes object with the adjusted position.
#     """
#
#     bbox = ax.get_position()
#
#     # Convert centimeters to inches for consistency with matplotlib dimensions
#     dx_in, dy_in = dx / 2.54, dy / 2.54
#
#     # Calculate delta ratios relative to the figure size
#     fig = ax.get_figure()
#     fig_dx_in, fig_dy_in = fig.get_size_inches()
#     dx_ratio, dy_ratio = dx_in / fig_dx_in, dy_in / fig_dy_in
#
#     # Determine updated bbox position and optionally adjust dimensions
#     left = bbox.x0 + dx_ratio
#     bottom = bbox.y0 + dy_ratio
#     width = bbox.width
#     height = bbox.height
#
#     # Main
#     ax.set_position([left, bottom, width, height])
#
#     return ax
#
#
# # def adjust_axes_position_and_dimension(
# #     ax, dx, dy, adjust_width_for_dx=False, adjust_height_for_dy=False
# # ):
#
# # def set_pos(ax, x_cm, y_cm, extend_x=False, extend_y=False):
# #     """
# #     Adjusts the position of an Axes object within a Figure by a specified offset in centimeters.
#
# #     Parameters:
# #     - ax (matplotlib.axes.Axes): The Axes object to modify.
# #     - x_cm (float): The horizontal offset in centimeters to adjust the Axes position.
# #     - y_cm (float): The vertical offset in centimeters to adjust the Axes position.
# #     - extend_x (bool): If True, reduces the width of the Axes by the horizontal offset.
# #     - extend_y (bool): If True, reduces the height of the Axes by the vertical offset.
#
# #     Returns:
# #     - ax (matplotlib.axes.Axes): The modified Axes object with the adjusted position.
# #     """
#
# #     bbox = ax.get_position()
#
# #     # Inches
# #     x_in, y_in = x_cm / 2.54, y_cm / 2.54
#
# #     # Calculates delta ratios
# #     fig = ax.get_figure()
# #     fig_x_in, fig_y_in = fig.get_size_inches()
# #     x_ratio, y_ratio = x_in / fig_x_in, y_in / fig_y_in
#
# #     # Determines updated bbox position
# #     left = bbox.x0 + x_ratio
# #     bottom = bbox.y0 + y_ratio
# #     width = bbox.width
# #     height = bbox.height
#
# #     if extend_x:
# #         width -= x_ratio
#
# #     if extend_y:
# #         height -= y_ratio
#
# #     ax.set_position([left, bottom, width, height])
#
# #     return ax
#
#
# # def set_pos(
# #     fig,
# #     ax,
# #     x_cm,
# #     y_cm,
# #     dragh=False,
# #     dragv=False,
# # ):
#
# #     bbox = ax.get_position()
#
# #     ## Calculates delta ratios
# #     fig_x_in, fig_y_in = fig.get_size_inches()
#
# #     x_in = float(x_cm) / 2.54
# #     y_in = float(y_cm) / 2.54
#
# #     x_ratio = x_in / fig_x_in
# #     y_ratio = y_in / fig_x_in
#
# #     ## Determines updated bbox position
# #     left = bbox.x0 + x_ratio
# #     bottom = bbox.y0 + y_ratio
# #     width = bbox.x1 - bbox.x0
# #     height = bbox.y1 - bbox.y0
#
# #     if dragh:
# #         width -= x_ratio
#
# #     if dragv:
# #         height -= y_ratio
#
# #     ax.set_pos(
# #         [
# #             left,
# #             bottom,
# #             width,
# #             height,
# #         ]
# #     )
#
# #     return ax
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_shift.py
# --------------------------------------------------------------------------------
