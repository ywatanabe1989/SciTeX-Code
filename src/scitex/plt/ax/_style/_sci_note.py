#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 11:58:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_sci_note.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_style/_sci_note.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import numpy as np


class OOMFormatter(matplotlib.ticker.ScalarFormatter):
    """Custom formatter for scientific notation with fixed order of magnitude.

    A matplotlib formatter that allows you to specify a fixed exponent for
    scientific notation, rather than letting matplotlib choose it automatically.
    Useful when you want consistent notation across multiple plots or specific
    exponent values.

    Parameters
    ----------
    order : int or None, optional
        Fixed order of magnitude (exponent) to use. If None, calculated
        automatically. Default is None.
    fformat : str, optional
        Format string for the mantissa. Default is "%1.1f".
    offset : bool, optional
        Whether to use offset notation. Default is True.
    mathText : bool, optional
        Whether to use mathtext rendering. Default is True.

    Attributes
    ----------
    order : int or None
        The fixed order of magnitude to use.
    fformat : str
        Format string for displaying numbers.

    Examples
    --------
    >>> # Force all labels to use 10^3 notation
    >>> formatter = OOMFormatter(order=3, fformat="%1.2f")
    >>> ax.xaxis.set_major_formatter(formatter)

    >>> # Use 10^-6 for microvolts
    >>> formatter = OOMFormatter(order=-6, fformat="%1.1f")
    >>> ax.yaxis.set_major_formatter(formatter)

    See Also
    --------
    matplotlib.ticker.ScalarFormatter : Base formatter class
    sci_note : Convenience function using this formatter
    """

    def __init__(self, order=None, fformat="%1.1f", offset=True, mathText=True):
        self.order = order
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(
            self, useOffset=offset, useMathText=mathText
        )

    def _set_order_of_magnitude(self):
        if self.order is not None:
            self.orderOfMagnitude = self.order
        else:
            super()._set_order_of_magnitude()

    def _set_format(self, vmin=None, vmax=None):
        self.format = self.fformat
        if self._useMathText:
            self.format = r"$\mathdefault{%s}$" % self.format


def sci_note(
    ax,
    fformat="%1.1f",
    x=False,
    y=False,
    scilimits=(-3, 3),
    order_x=None,
    order_y=None,
    pad_x=-22,
    pad_y=-20,
):
    """
    Apply scientific notation to axis with optional manual order of magnitude.

    Parameters:
    -----------
    ax : matplotlib Axes
        The axes to apply scientific notation to
    fformat : str
        Format string for tick labels
    x, y : bool
        Whether to apply to x or y axis
    scilimits : tuple
        Scientific notation limits
    order_x, order_y : int or None
        Manual order of magnitude (exponent). If None, calculated automatically
    pad_x, pad_y : int
        Padding for the axis labels
    """
    if x:
        # Calculate order if not specified
        if order_x is None:
            order_x = np.floor(np.log10(np.max(np.abs(ax.get_xlim())) + 1e-5))

        ax.xaxis.set_major_formatter(OOMFormatter(order=int(order_x), fformat=fformat))
        ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
        ax.xaxis.labelpad = pad_x
        shift_x = (ax.get_xlim()[0] - ax.get_xlim()[1]) * 0.01
        ax.xaxis.get_offset_text().set_position((shift_x, 0))

    if y:
        # Calculate order if not specified
        if order_y is None:
            order_y = np.floor(np.log10(np.max(np.abs(ax.get_ylim())) + 1e-5))

        ax.yaxis.set_major_formatter(OOMFormatter(order=int(order_y), fformat=fformat))
        ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
        ax.yaxis.labelpad = pad_y
        shift_y = (ax.get_ylim()[0] - ax.get_ylim()[1]) * 0.01
        ax.yaxis.get_offset_text().set_position((0, shift_y))

    return ax


# import matplotlib
# import numpy as np


# class OOMFormatter(matplotlib.ticker.ScalarFormatter):
#     def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
#         self.order = order
#         self.fformat = fformat
#         matplotlib.ticker.ScalarFormatter.__init__(
#             self, useOffset=offset, useMathText=mathText
#         )

#     def _set_order_of_magnitude(self):
#         self.orderOfMagnitude = self.order

#     def _set_format(self, vmin=None, vmax=None):
#         self.format = self.fformat
#         if self._useMathText:
#             self.format = r"$\mathdefault{%s}$" % self.format


# def sci_note(ax, fformat="%1.1f", x=False, y=False, scilimits=(-3, 3)):
#     order_x = 0
#     order_y = 0

#     if x:
#         order_x = np.floor(np.log10(np.max(np.abs(ax.get_xlim())) + 1e-5))
#         ax.xaxis.set_major_formatter(
#             OOMFormatter(order=int(order_x), fformat=fformat)
#         )
#         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
#         ax.xaxis.labelpad = -22
#         shift_x = (ax.get_xlim()[0] - ax.get_xlim()[1]) * 0.01
#         ax.xaxis.get_offset_text().set_position((shift_x, 0))

#     if y:
#         order_y = np.floor(np.log10(np.max(np.abs(ax.get_ylim())) + 1e-5))
#         ax.yaxis.set_major_formatter(
#             OOMFormatter(order=int(order_y), fformat=fformat)
#         )
#         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
#         ax.yaxis.labelpad = -20
#         shift_y = (ax.get_ylim()[0] - ax.get_ylim()[1]) * 0.01
#         ax.yaxis.get_offset_text().set_position((0, shift_y))

#     return ax


# # class OOMFormatter(matplotlib.ticker.ScalarFormatter):
# #     def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
# #         self.order = order
# #         self.fformat = fformat
# #         matplotlib.ticker.ScalarFormatter.__init__(
# #             self, useOffset=offset, useMathText=mathText
# #         )

# #     def _set_order_of_magnitude(self):
# #         self.orderOfMagnitude = self.order

# #     def _set_format(self, vmin=None, vmax=None):
# #         self.format = self.fformat
# #         if self._useMathText:
# #             self.format = r"$\mathdefault{%s}$" % self.format


# # def sci_note(ax, fformat="%1.1f", x=False, y=False, scilimits=(-3, 3)):
# #     order_x = 0
# #     order_y = 0

# #     if x:
# #         order_x = np.floor(np.log10(np.max(np.abs(ax.get_xlim())) + 1e-5))
# #         ax.xaxis.set_major_formatter(
# #             OOMFormatter(order=int(order_x), fformat=fformat)
# #         )
# #         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)

# #     if y:
# #         order_y = np.floor(np.log10(np.max(np.abs(ax.get_ylim()) + 1e-5)))
# #         ax.yaxis.set_major_formatter(
# #             OOMFormatter(order=int(order_y), fformat=fformat)
# #         )
# #         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)

# #     return ax


# # #!/usr/bin/env python3


# # import matplotlib


# # class OOMFormatter(matplotlib.ticker.ScalarFormatter):
# #     # https://stackoverflow.com/questions/42656139/set-scientific-notation-with-fixed-exponent-and-significant-digits-for-multiple
# #     # def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
# #     def __init__(self, order=0, fformat="%1.0d", offset=True, mathText=True):
# #         self.oom = order
# #         self.fformat = fformat
# #         matplotlib.ticker.ScalarFormatter.__init__(
# #             self, useOffset=offset, useMathText=mathText
# #         )

# #     def _set_order_of_magnitude(self):
# #         self.orderOfMagnitude = self.oom

# #     def _set_format(self, vmin=None, vmax=None):
# #         self.format = self.fformat
# #         if self._useMathText:
# #             self.format = r"$\mathdefault{%s}$" % self.format


# # def sci_note(
# #     ax,
# #     order,
# #     fformat="%1.0d",
# #     x=False,
# #     y=False,
# #     scilimits=(-3, 3),
# # ):
# #     """
# #     Change the expression of the x- or y-axis to the scientific notation like *10^3
# #     , where 3 is the first argument, order.

# #     Example:
# #         order = 4 # 10^4
# #         ax = sci_note(
# #                  ax,
# #                  order,
# #                  fformat="%1.0d",
# #                  x=True,
# #                  y=False,
# #                  scilimits=(-3, 3),
# #     """

# #     if x == True:
# #         ax.xaxis.set_major_formatter(
# #             OOMFormatter(order=order, fformat=fformat)
# #         )
# #         ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
# #     if y == True:
# #         ax.yaxis.set_major_formatter(
# #             OOMFormatter(order=order, fformat=fformat)
# #         )
# #         ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)

# #     return ax

# EOF
