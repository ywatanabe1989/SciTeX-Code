#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__set_ticks.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__set_ticks.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._style import set_ticks

matplotlib.use("Agg")


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        # Create a basic plot
        xx = np.linspace(0, 10, 100)
        yy = np.sin(xx)
        self.ax.plot(xx, yy)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_set_x_ticks_basic(self):
        # Test with custom x tick locations
        x_ticks = [0, 2.5, 5, 7.5, 10]
        ax = set_x_ticks(self.ax, x_ticks=x_ticks)

        # Check that the ticks were set correctly
        assert len(ax.get_xticks()) == len(x_ticks)
        assert np.allclose(ax.get_xticks(), x_ticks)

    def test_set_y_ticks_basic(self):
        # Test with custom y tick locations
        y_ticks = [-1, -0.5, 0, 0.5, 1]
        ax = set_y_ticks(self.ax, y_ticks=y_ticks)

        # Check that the ticks were set correctly
        assert len(ax.get_yticks()) == len(y_ticks)
        assert np.allclose(ax.get_yticks(), y_ticks)

    def test_set_ticks_combined(self):
        # Test setting both x and y ticks
        x_ticks = [0, 5, 10]
        y_ticks = [-1, 0, 1]

        ax = set_ticks(self.ax, xticks=x_ticks, yticks=y_ticks)

        # Check that the ticks were set correctly
        assert np.allclose(ax.get_xticks(), x_ticks)
        assert np.allclose(ax.get_yticks(), y_ticks)

    def test_set_ticks_with_vals_and_ticks(self):
        # Test with both vals and ticks
        x_vals = np.linspace(0, 100, 11)  # [0, 10, 20, ..., 100]
        x_ticks = [0, 50, 100]

        # This should create a new mapping of the axis
        ax = set_x_ticks(self.ax, x_vals=x_vals, x_ticks=x_ticks)

        # Check the ticks after mapping
        assert len(ax.get_xticks()) > 0
        assert len(ax.get_xticklabels()) > 0

    # def test_string_ticks(self):
    #     # Test with string tick labels
    #     x_ticks = ["A", "B", "C", "D"]
    #     ax = set_x_ticks(self.ax, x_ticks=x_ticks)

    #     # Get the tick labels (need to render the figure for this)
    #     fig = ax.get_figure()
    #     fig.canvas.draw()
    #     tick_labels = [label.get_text() for label in ax.get_xticklabels()]

    #     # Check that the tick labels match
    #     assert tick_labels == x_ticks

    # def test_dict_ticks(self):
    #     # This test depends on the implementation of to_str from scitex.dict
    #     # Testing with a mock instead
    #     from unittest.mock import patch

    #     with patch("scitex.plt.ax._set_ticks.is_listed_X", return_value=True):
    #         with patch(
    #             "scitex.plt.ax._set_ticks.to_str",
    #             side_effect=lambda x, delimiter: f"formatted_{x}",
    #         ):
    #             x_ticks = [{"a": 1}, {"b": 2}]
    #             ax = set_x_ticks(self.ax, x_ticks=x_ticks)

    #             # Get the tick labels
    #             fig = ax.get_figure()
    #             fig.canvas.draw()
    #             tick_labels = [
    #                 label.get_text() for label in ax.get_xticklabels()
    #             ]

    #             # Check formatted labels (matching the mock's return value)
    #             assert "formatted_" in tick_labels[0]

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        x_ticks = [0, 2.5, 5, 7.5, 10]
        y_ticks = [-1, -0.5, 0, 0.5, 1]
        set_ticks(self.ax, xticks=x_ticks, yticks=y_ticks)

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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_set_ticks.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-27 20:04:55 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_set_ticks.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_set_ticks.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib.pyplot as plt
# import scitex
# import numpy as np
#
# from ....dict._to_str import to_str
# from ....types import is_listed_X
#
#
# def set_ticks(ax, xvals=None, xticks=None, yvals=None, yticks=None):
#     ax = set_x_ticks(ax, x_vals=xvals, x_ticks=xticks)
#     ax = set_y_ticks(ax, y_vals=yvals, y_ticks=yticks)
#     canvas_type = type(ax.figure.canvas).__name__
#     if "TkAgg" in canvas_type:
#         ax.get_figure().canvas.draw()  # Redraw the canvas once after making all updates
#     return ax
#
#
# def set_x_ticks(ax, x_vals=None, x_ticks=None):
#     """
#     Set custom tick labels on the x and y axes based on specified values and desired ticks.
#
#     Parameters:
#     - ax: The axis object to modify.
#     - x_vals: Array of x-axis values.
#     - x_ticks: List of desired tick labels on the x-axis.
#     - y_vals: Array of y-axis values.
#     - y_ticks: List of desired tick labels on the y-axis.
#
#     Example:
#         import matplotlib.pyplot as plt
#         import numpy as np
#
#         fig, axes = plt.subplots(nrows=4)
#         x = np.linspace(0, 10, 100)
#         y = np.sin(x)
#         for ax in axes:
#             ax.plot(x, y)  # Plot a sine wave
#
#         set_ticks(axes[0])  # Do nothing # OK
#         set_ticks(axes[1], x_vals=x+3) # OK
#         set_ticks(axes[2], x_ticks=[1,2])  # OK
#         set_ticks(axes[3], x_vals=x+3, x_ticks=[4,5])  # Auto-generate ticks across the range
#         fig.tight_layout()
#         plt.show()
#     """
#
#     def _avoid_overlaps(values):
#         values = np.array(values)
#         if ("int" in str(values.dtype)) or ("float" in str(values.dtype)):
#             values = values.astype(float) + np.arange(len(values)) * 1e-5
#         return values
#
#     def _set_x_vals(ax, x_vals):
#         x_vals = _avoid_overlaps(x_vals)
#         new_x_axis = np.linspace(*ax.get_xlim(), len(x_vals))
#         ax.set_xticks(new_x_axis)
#         ax.set_xticklabels([f"{xv}" for xv in x_vals])
#         return ax
#
#     def _set_x_ticks(ax, x_ticks):
#         x_ticks = np.array(x_ticks)
#         if x_ticks.dtype.kind in ["U", "S", "O"]:  # If x_ticks are strings
#             ax.set_xticks(range(len(x_ticks)))
#             ax.set_xticklabels(x_ticks)
#         else:
#             x_vals = np.array(
#                 [
#                     label.get_text().replace("−", "-")
#                     for label in ax.get_xticklabels()
#                 ]
#             )
#             x_vals = x_vals.astype(float)
#             x_indi = np.argmin(
#                 np.array(
#                     np.abs(x_vals[:, np.newaxis] - x_ticks[np.newaxis, :])
#                 ),
#                 axis=0,
#             )
#             ax.set_xticks(ax.get_xticks()[x_indi])
#             ax.set_xticklabels([f"{xt}" for xt in x_ticks])
#         return ax
#
#     x_vals_passed = x_vals is not None
#     x_ticks_passed = x_ticks is not None
#
#     if is_listed_X(x_ticks, dict):
#         x_ticks = [to_str(xt, delimiter="\n") for xt in x_ticks]
#
#     if (not x_vals_passed) and (not x_ticks_passed):
#         # Do nothing
#         pass
#
#     elif x_vals_passed and (not x_ticks_passed):
#         # Replaces the x axis to x_vals
#         x_ticks = np.linspace(x_vals[0], x_vals[-1], 4)
#         ax = _set_x_vals(ax, x_ticks)
#
#     elif (not x_vals_passed) and x_ticks_passed:
#         # Locates 'x_ticks' on the original x axis
#         ax.set_xticks(x_ticks)
#
#     elif x_vals_passed and x_ticks_passed:
#         if isinstance(x_vals, str):
#             if x_vals == "auto":
#                 x_vals = np.arange(len(x_ticks))
#
#         # Replaces the original x axis to 'x_vals' and locates the 'x_ticks' on the new axis
#         ax = _set_x_vals(ax, x_vals)
#         ax = _set_x_ticks(ax, x_ticks)
#
#     return ax
#
#
# def set_y_ticks(ax, y_vals=None, y_ticks=None):
#     """
#     Set custom tick labels on the y-axis based on specified values and desired ticks.
#
#     Parameters:
#     - ax: The axis object to modify.
#     - y_vals: Array of y-axis values where ticks should be placed.
#     - y_ticks: List of labels for ticks on the y-axis.
#
#     Example:
#         import matplotlib.pyplot as plt
#         import numpy as np
#
#         fig, ax = plt.subplots()
#         x = np.linspace(0, 10, 100)
#         y = np.sin(x)
#         ax.plot(x, y)  # Plot a sine wave
#
#         set_y_ticks(ax, y_vals=y, y_ticks=['Low', 'High'])  # Set custom y-axis ticks
#         plt.show()
#     """
#
#     def _avoid_overlaps(values):
#         values = np.array(values)
#         if ("int" in str(values.dtype)) or ("float" in str(values.dtype)):
#             values = values.astype(float) + np.arange(len(values)) * 1e-5
#         return values
#
#     def _set_y_vals(ax, y_vals):
#         y_vals = _avoid_overlaps(y_vals)
#         new_y_axis = np.linspace(*ax.get_ylim(), len(y_vals))
#         ax.set_yticks(new_y_axis)
#         ax.set_yticklabels([f"{yv:.2f}" for yv in y_vals])
#         return ax
#
#     # def _set_y_ticks(ax, y_ticks):
#     #     y_ticks = np.array(y_ticks)
#     #     y_vals = np.array(
#     #         [
#     #             label.get_text().replace("−", "-")
#     #             for label in ax.get_yticklabels()
#     #         ]
#     #     )
#     #     y_vals = y_vals.astype(float)
#     #     y_indi = np.argmin(
#     #         np.array(np.abs(y_vals[:, np.newaxis] - y_ticks[np.newaxis, :])),
#     #         axis=0,
#     #     )
#
#     #     # y_indi = [np.argmin(np.abs(y_vals - yt)) for yt in y_ticks]
#     #     ax.set_yticks(ax.get_yticks()[y_indi])
#     #     ax.set_yticklabels([f"{yt}" for yt in y_ticks])
#     #     return ax
#     def _set_y_ticks(ax, y_ticks):
#         y_ticks = np.array(y_ticks)
#         if y_ticks.dtype.kind in ["U", "S", "O"]:  # If y_ticks are strings
#             ax.set_yticks(range(len(y_ticks)))
#             ax.set_yticklabels(y_ticks)
#         else:
#             y_vals = np.array(
#                 [
#                     label.get_text().replace("−", "-")
#                     for label in ax.get_yticklabels()
#                 ]
#             )
#             y_vals = y_vals.astype(float)
#             y_indi = np.argmin(
#                 np.array(
#                     np.abs(y_vals[:, np.newaxis] - y_ticks[np.newaxis, :])
#                 ),
#                 axis=0,
#             )
#             ax.set_yticks(ax.get_yticks()[y_indi])
#             ax.set_yticklabels([f"{yt}" for yt in y_ticks])
#         return ax
#
#     y_vals_passed = y_vals is not None
#     y_ticks_passed = y_ticks is not None
#
#     if is_listed_X(y_ticks, dict):
#         y_ticks = [to_str(yt, delimiter="\n") for yt in y_ticks]
#
#     if (not y_vals_passed) and (not y_ticks_passed):
#         # Do nothing
#         pass
#
#     elif y_vals_passed and (not y_ticks_passed):
#         # Replaces the y axis to y_vals
#         ax = _set_y_vals(ax, y_vals)
#
#     elif (not y_vals_passed) and y_ticks_passed:
#         # Locates 'y_ticks' on the original y axis
#         ax.set_yticks(y_ticks)
#
#     elif y_vals_passed and y_ticks_passed:
#         # Replaces the original y axis to 'y_vals' and locates the 'y_ticks' on the new axis
#         if y_vals == "auto":
#             y_vals = np.arange(len(y_ticks))
#
#         ax = _set_y_vals(ax, y_vals)
#         ax = _set_y_ticks(ax, y_ticks)
#     return ax
#
#
# if __name__ == "__main__":
#     import scitex
#
#     xx, tt, fs = scitex.dsp.demo_sig()
#     pha, amp, freqs = scitex.dsp.wavelet(xx, fs)
#
#     i_batch, i_ch = 0, 0
#     ff = freqs[i_batch, i_ch]
#     fig, ax = scitex.plt.subplots()
#
#     ax.image2d(amp[i_batch, i_ch])
#
#     ax = set_ticks(
#         ax,
#         x_vals=tt,
#         x_ticks=[0, 1, 2, 3, 4],
#         y_vals=ff,
#         y_ticks=[0, 128, 256],
#     )
#
#     plt.show()
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_set_ticks.py
# --------------------------------------------------------------------------------
