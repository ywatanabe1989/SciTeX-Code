#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:45 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__sci_note.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__sci_note.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import pytest
from scitex.plt.ax._style import OOMFormatter, sci_note


class TestSciNote:

    @pytest.fixture
    def setup_axes(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([0, 1000], [0, 2000])
        return fig, ax

    def test_oom_formatter_creation(self):
        formatter = OOMFormatter(order=3, fformat="%.2f")
        assert formatter.order == 3
        assert formatter.fformat == "%.2f"

    # def test_oom_formatter_order_setting(self):
    #     # Only test explicit order setting since auto requires an axis
    #     formatter = OOMFormatter(order=4)
    #     # Mock the parent method to avoid the call to super()
    #     formatter.orderOfMagnitude = None
    #     formatter._set_order_of_magnitude()
    #     assert formatter.orderOfMagnitude == 4

    def test_oom_formatter_format_setting(self):
        formatter = OOMFormatter(fformat="%.3f", mathText=True)
        formatter._set_format()
        assert formatter.format == r"$\mathdefault{%.3f}$"

        formatter_no_math = OOMFormatter(fformat="%.3f", mathText=False)
        formatter_no_math._set_format()
        assert formatter_no_math.format == "%.3f"

    def test_sci_note_x_axis(self, setup_axes):
        _, ax = setup_axes
        ax = sci_note(ax, x=True)

        assert isinstance(ax.xaxis.get_major_formatter(), OOMFormatter)
        assert ax.xaxis.labelpad == -22

    def test_sci_note_y_axis(self, setup_axes):
        _, ax = setup_axes
        ax = sci_note(ax, y=True)

        assert isinstance(ax.yaxis.get_major_formatter(), OOMFormatter)
        assert ax.yaxis.labelpad == -20

    def test_sci_note_both_axes(self, setup_axes):
        _, ax = setup_axes
        ax = sci_note(ax, x=True, y=True)

        assert isinstance(ax.xaxis.get_major_formatter(), OOMFormatter)
        assert isinstance(ax.yaxis.get_major_formatter(), OOMFormatter)

    def test_sci_note_custom_order(self, setup_axes):
        _, ax = setup_axes
        ax = sci_note(ax, x=True, y=True, order_x=5, order_y=6)

        # Get formatters from the axes
        xformatter = ax.xaxis.get_major_formatter()
        yformatter = ax.yaxis.get_major_formatter()

        # Check order was set correctly
        assert xformatter.order == 5
        assert yformatter.order == 6

    def test_sci_note_custom_format(self, setup_axes):
        _, ax = setup_axes
        custom_format = "%.4f"
        ax = sci_note(ax, x=True, y=True, fformat=custom_format)

        xformatter = ax.xaxis.get_major_formatter()
        yformatter = ax.yaxis.get_major_formatter()

        assert xformatter.fformat == custom_format
        assert yformatter.fformat == custom_format

    def test_sci_note_custom_padding(self, setup_axes):
        _, ax = setup_axes
        ax = sci_note(ax, x=True, y=True, pad_x=-10, pad_y=-15)

        assert ax.xaxis.labelpad == -10
        assert ax.yaxis.labelpad == -15

    def test_savefig(self, setup_axes):
        from scitex.io import save

        # Main test functionality
        fig, ax = setup_axes
        ax = sci_note(ax, x=True, y=True, fformat="%1.2f")

        # Saving
        spath = f"{os.path.basename(__file__)}.jpg"
        save(fig, spath)

        # Check saved file existence
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    # @check_figures_equal(extensions=["png"])
    # def test_sci_note_visual_output(self, fig_test, fig_ref):
    #     # Create identical data for both figures
    #     data_x = np.array([0, 10000])
    #     data_y = np.array([0, 20000])

    #     # Test figure with sci_note
    #     ax_test = fig_test.subplots()
    #     ax_test.plot(data_x, data_y)
    #     # Set both x and y limits exactly to ensure consistency
    #     ax_test.set_xlim(0, 10000)
    #     ax_test.set_ylim(0, 20000)
    #     sci_note(ax_test, x=True, y=True)

    #     # Reference figure with manually configured similar settings
    #     ax_ref = fig_ref.subplots()
    #     ax_ref.plot(data_x, data_y)
    #     # Set identical limits
    #     ax_ref.set_xlim(0, 10000)
    #     ax_ref.set_ylim(0, 20000)
    #     # Calculate the same orders of magnitude
    #     order_x = int(
    #         np.floor(np.log10(np.max(np.abs(ax_ref.get_xlim())) + 1e-5))
    #     )
    #     order_y = int(
    #         np.floor(np.log10(np.max(np.abs(ax_ref.get_ylim())) + 1e-5))
    #     )
    #     # Apply them manually
    #     ax_ref.xaxis.set_major_formatter(
    #         matplotlib.ticker.ScalarFormatter(useMathText=True)
    #     )
    #     ax_ref.yaxis.set_major_formatter(
    #         matplotlib.ticker.ScalarFormatter(useMathText=True)
    #     )
    #     ax_ref.ticklabel_format(style="sci", scilimits=(-3, 3), axis="both")

    #     # Ensure matching appearance
    #     fig_test.tight_layout()
    #     fig_ref.tight_layout()
    #     ax_ref.ticklabel_format(style="sci", scilimits=(-3, 3), axis="both")


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_sci_note.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 11:58:58 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_sci_note.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_style/_sci_note.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib
# import numpy as np
#
#
# class OOMFormatter(matplotlib.ticker.ScalarFormatter):
#     def __init__(
#         self, order=None, fformat="%1.1f", offset=True, mathText=True
#     ):
#         self.order = order
#         self.fformat = fformat
#         matplotlib.ticker.ScalarFormatter.__init__(
#             self, useOffset=offset, useMathText=mathText
#         )
#
#     def _set_order_of_magnitude(self):
#         if self.order is not None:
#             self.orderOfMagnitude = self.order
#         else:
#             super()._set_order_of_magnitude()
#
#     def _set_format(self, vmin=None, vmax=None):
#         self.format = self.fformat
#         if self._useMathText:
#             self.format = r"$\mathdefault{%s}$" % self.format
#
#
# def sci_note(
#     ax,
#     fformat="%1.1f",
#     x=False,
#     y=False,
#     scilimits=(-3, 3),
#     order_x=None,
#     order_y=None,
#     pad_x=-22,
#     pad_y=-20,
# ):
#     """
#     Apply scientific notation to axis with optional manual order of magnitude.
#
#     Parameters:
#     -----------
#     ax : matplotlib Axes
#         The axes to apply scientific notation to
#     fformat : str
#         Format string for tick labels
#     x, y : bool
#         Whether to apply to x or y axis
#     scilimits : tuple
#         Scientific notation limits
#     order_x, order_y : int or None
#         Manual order of magnitude (exponent). If None, calculated automatically
#     pad_x, pad_y : int
#         Padding for the axis labels
#     """
#     if x:
#         # Calculate order if not specified
#         if order_x is None:
#             order_x = np.floor(np.log10(np.max(np.abs(ax.get_xlim())) + 1e-5))
#
#         ax.xaxis.set_major_formatter(
#             OOMFormatter(order=int(order_x), fformat=fformat)
#         )
#         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
#         ax.xaxis.labelpad = pad_x
#         shift_x = (ax.get_xlim()[0] - ax.get_xlim()[1]) * 0.01
#         ax.xaxis.get_offset_text().set_position((shift_x, 0))
#
#     if y:
#         # Calculate order if not specified
#         if order_y is None:
#             order_y = np.floor(np.log10(np.max(np.abs(ax.get_ylim())) + 1e-5))
#
#         ax.yaxis.set_major_formatter(
#             OOMFormatter(order=int(order_y), fformat=fformat)
#         )
#         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
#         ax.yaxis.labelpad = pad_y
#         shift_y = (ax.get_ylim()[0] - ax.get_ylim()[1]) * 0.01
#         ax.yaxis.get_offset_text().set_position((0, shift_y))
#
#     return ax
#
#
# # import matplotlib
# # import numpy as np
#
#
# # class OOMFormatter(matplotlib.ticker.ScalarFormatter):
# #     def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
# #         self.order = order
# #         self.fformat = fformat
# #         matplotlib.ticker.ScalarFormatter.__init__(
# #             self, useOffset=offset, useMathText=mathText
# #         )
#
# #     def _set_order_of_magnitude(self):
# #         self.orderOfMagnitude = self.order
#
# #     def _set_format(self, vmin=None, vmax=None):
# #         self.format = self.fformat
# #         if self._useMathText:
# #             self.format = r"$\mathdefault{%s}$" % self.format
#
#
# # def sci_note(ax, fformat="%1.1f", x=False, y=False, scilimits=(-3, 3)):
# #     order_x = 0
# #     order_y = 0
#
# #     if x:
# #         order_x = np.floor(np.log10(np.max(np.abs(ax.get_xlim())) + 1e-5))
# #         ax.xaxis.set_major_formatter(
# #             OOMFormatter(order=int(order_x), fformat=fformat)
# #         )
# #         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
# #         ax.xaxis.labelpad = -22
# #         shift_x = (ax.get_xlim()[0] - ax.get_xlim()[1]) * 0.01
# #         ax.xaxis.get_offset_text().set_position((shift_x, 0))
#
# #     if y:
# #         order_y = np.floor(np.log10(np.max(np.abs(ax.get_ylim())) + 1e-5))
# #         ax.yaxis.set_major_formatter(
# #             OOMFormatter(order=int(order_y), fformat=fformat)
# #         )
# #         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
# #         ax.yaxis.labelpad = -20
# #         shift_y = (ax.get_ylim()[0] - ax.get_ylim()[1]) * 0.01
# #         ax.yaxis.get_offset_text().set_position((0, shift_y))
#
# #     return ax
#
#
# # # class OOMFormatter(matplotlib.ticker.ScalarFormatter):
# # #     def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
# # #         self.order = order
# # #         self.fformat = fformat
# # #         matplotlib.ticker.ScalarFormatter.__init__(
# # #             self, useOffset=offset, useMathText=mathText
# # #         )
#
# # #     def _set_order_of_magnitude(self):
# # #         self.orderOfMagnitude = self.order
#
# # #     def _set_format(self, vmin=None, vmax=None):
# # #         self.format = self.fformat
# # #         if self._useMathText:
# # #             self.format = r"$\mathdefault{%s}$" % self.format
#
#
# # # def sci_note(ax, fformat="%1.1f", x=False, y=False, scilimits=(-3, 3)):
# # #     order_x = 0
# # #     order_y = 0
#
# # #     if x:
# # #         order_x = np.floor(np.log10(np.max(np.abs(ax.get_xlim())) + 1e-5))
# # #         ax.xaxis.set_major_formatter(
# # #             OOMFormatter(order=int(order_x), fformat=fformat)
# # #         )
# # #         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
#
# # #     if y:
# # #         order_y = np.floor(np.log10(np.max(np.abs(ax.get_ylim()) + 1e-5)))
# # #         ax.yaxis.set_major_formatter(
# # #             OOMFormatter(order=int(order_y), fformat=fformat)
# # #         )
# # #         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
#
# # #     return ax
#
#
# # # #!/usr/bin/env python3
#
#
# # # import matplotlib
#
#
# # # class OOMFormatter(matplotlib.ticker.ScalarFormatter):
# # #     # https://stackoverflow.com/questions/42656139/set-scientific-notation-with-fixed-exponent-and-significant-digits-for-multiple
# # #     # def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
# # #     def __init__(self, order=0, fformat="%1.0d", offset=True, mathText=True):
# # #         self.oom = order
# # #         self.fformat = fformat
# # #         matplotlib.ticker.ScalarFormatter.__init__(
# # #             self, useOffset=offset, useMathText=mathText
# # #         )
#
# # #     def _set_order_of_magnitude(self):
# # #         self.orderOfMagnitude = self.oom
#
# # #     def _set_format(self, vmin=None, vmax=None):
# # #         self.format = self.fformat
# # #         if self._useMathText:
# # #             self.format = r"$\mathdefault{%s}$" % self.format
#
#
# # # def sci_note(
# # #     ax,
# # #     order,
# # #     fformat="%1.0d",
# # #     x=False,
# # #     y=False,
# # #     scilimits=(-3, 3),
# # # ):
# # #     """
# # #     Change the expression of the x- or y-axis to the scientific notation like *10^3
# # #     , where 3 is the first argument, order.
#
# # #     Example:
# # #         order = 4 # 10^4
# # #         ax = sci_note(
# # #                  ax,
# # #                  order,
# # #                  fformat="%1.0d",
# # #                  x=True,
# # #                  y=False,
# # #                  scilimits=(-3, 3),
# # #     """
#
# # #     if x == True:
# # #         ax.xaxis.set_major_formatter(
# # #             OOMFormatter(order=order, fformat=fformat)
# # #         )
# # #         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
# # #     if y == True:
# # #         ax.yaxis.set_major_formatter(
# # #             OOMFormatter(order=order, fformat=fformat)
# # #         )
# # #         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
#
# # #     return ax
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_sci_note.py
# --------------------------------------------------------------------------------
