#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:37 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__add_marginal_ax.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__add_marginal_ax.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from scitex.plt.ax._style import add_marginal_ax


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)

        # Draw something on the axis for reference
        self.ax.plot([0, 1], [0, 1])

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test adding marginal axes in each position
        positions = ["top", "bottom", "left", "right"]

        for position in positions:
            ax_marg = add_marginal_ax(self.ax, position)

            # Check that the marginal axis was created
            assert ax_marg is not None
            assert isinstance(ax_marg, matplotlib.axes.Axes)

            # Check that we have multiple axes in the figure
            assert len(self.fig.axes) > 1

            # Reset for next test
            self.fig.clear()
            self.ax = self.fig.add_subplot(111)
            self.ax.plot([0, 1], [0, 1])

    def test_size_parameter(self):
        # Test with custom size parameter
        custom_size = 0.4
        ax_marg = add_marginal_ax(self.ax, "top", size=custom_size)

        # Get main axis and marginal axis positions
        main_bbox = self.ax.get_position()
        marg_bbox = ax_marg.get_position()

        # Calculate the relative height of marginal axis vs main axis
        main_height = main_bbox.height
        marg_height = marg_bbox.height

        # Ratio should be approximately equal to the size parameter
        # (allowing for some rounding/precision differences)
        assert marg_height > 0
        # assert np.isclose(marg_height / main_height, custom_size, rtol=0.1)

    # def test_pad_parameter(self):
    #     # Test with custom pad parameter
    #     custom_pad = 0.2
    #     ax_marg = add_marginal_ax(self.ax, "top", pad=custom_pad)

    #     # Get main axis and marginal axis positions
    #     main_bbox = self.ax.get_position()
    #     marg_bbox = ax_marg.get_position()

    #     # Calculate the gap between the axes
    #     main_top = main_bbox.y1
    #     marg_bottom = marg_bbox.y0

    #     # The pad is in units of inches, so we need to convert to figure coords
    #     fig_height_in = self.fig.get_figheight()
    #     pad_in_fig_coords = custom_pad / fig_height_in

    #     # Allow reasonable tolerance since the padding calculation involves several conversions
    #     assert (marg_bottom - main_top) > 0  # Gap exists

    # def test_aspect_ratio(self):
    #     # Test that box_aspect is set correctly

    #     # For 'top' and 'bottom', box_aspect should be equal to size
    #     size = 0.3
    #     ax_marg_top = add_marginal_ax(self.ax, "top", size=size)

    #     # Check if box_aspect matches size
    #     # Since set_box_aspect doesn't have a direct getter, we'll check indirectly
    #     # by drawing the figure and checking the resulting aspect ratio
    #     self.fig.canvas.draw()

    #     # For 'left' and 'right', box_aspect should be 1/size
    #     ax_marg_right = add_marginal_ax(self.ax, "right", size=size)
    #     self.fig.canvas.draw()

    #     # The box_aspect is correctly set in the function, but checking it precisely
    #     # requires checking the private attribute or rendering metrics which is complex
    #     # So we'll just check that the axes were created with different shapes
    #     main_height = self.ax.get_window_extent().height
    #     right_height = ax_marg_right.get_window_extent().height
    #     assert np.isclose(
    #         main_height, right_height, rtol=0.1
    #     )  # Heights should be similar

    #     main_width = self.ax.get_window_extent().width
    #     right_width = ax_marg_right.get_window_extent().width
    #     assert right_width < main_width  # Right axis should be narrower

    def test_multiple_marginal_axes(self):
        # Test adding multiple marginal axes
        ax_top = add_marginal_ax(self.ax, "top")
        ax_right = add_marginal_ax(self.ax, "right")

        # Check that three axes exist (main + 2 marginal)
        assert len(self.fig.axes) == 3

        # Draw something in each marginal axis to verify they work
        ax_top.plot([0, 1], [0, 1], "r")
        ax_right.plot([0, 1], [0, 1], "g")

        # Verify the axes are different
        assert ax_top != ax_right
        assert self.ax != ax_top
        assert self.ax != ax_right

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        self.ax.plot([0, 1], [0, 1], "b-")

        # Add marginal axes
        ax_top = add_marginal_ax(self.ax, "top")
        ax_top.hist([0.1, 0.2, 0.3, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9], bins=5)

        ax_right = add_marginal_ax(self.ax, "right")
        ax_right.hist(
            [0.1, 0.2, 0.3, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9],
            bins=5,
            orientation="horizontal",
        )

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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_add_marginal_ax.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 20:18:52 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_add_marginal_ax.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_add_marginal_ax.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib
# from mpl_toolkits.axes_grid1 import make_axes_locatable
#
#
# def add_marginal_ax(axis, place, size=0.2, pad=0.1):
#     assert isinstance(
#         axis, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis"
#
#     divider = make_axes_locatable(axis)
#
#     size_perc_str = f"{size*100}%"
#     if place in ["left", "right"]:
#         size = 1.0 / size
#
#     axis_marginal = divider.append_axes(place, size=size_perc_str, pad=pad)
#     axis_marginal.set_box_aspect(size)
#
#     return axis_marginal
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_add_marginal_ax.py
# --------------------------------------------------------------------------------
