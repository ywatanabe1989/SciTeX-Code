#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:00:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_shift.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_style/_shift.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


def shift(ax, dx=0, dy=0):
    """
    Adjusts the position of an Axes object within a Figure by specified offsets in centimeters.

    This function modifies the position of a given matplotlib.axes.Axes object by shifting it horizontally and vertically within its parent figure. The shift amounts are specified in centimeters, and the function converts these values into the figure's coordinate system to perform the adjustment.

    Parameters:
    - ax (matplotlib.axes.Axes): The Axes object to modify. This must be an instance of a Matplotlib Axes.
    - dx (float): The horizontal offset in centimeters. Positive values shift the Axes to the right, while negative values shift it to the left.
    - dy (float): The vertical offset in centimeters. Positive values shift the Axes up, while negative values shift it down.

    Returns:
    - matplotlib.axes.Axes: The modified Axes object with the adjusted position.
    """

    bbox = ax.get_position()

    # Convert centimeters to inches for consistency with matplotlib dimensions
    dx_in, dy_in = dx / 2.54, dy / 2.54

    # Calculate delta ratios relative to the figure size
    fig = ax.get_figure()
    fig_dx_in, fig_dy_in = fig.get_size_inches()
    dx_ratio, dy_ratio = dx_in / fig_dx_in, dy_in / fig_dy_in

    # Determine updated bbox position and optionally adjust dimensions
    left = bbox.x0 + dx_ratio
    bottom = bbox.y0 + dy_ratio
    width = bbox.width
    height = bbox.height

    # Main
    ax.set_position([left, bottom, width, height])

    return ax


# def adjust_axes_position_and_dimension(
#     ax, dx, dy, adjust_width_for_dx=False, adjust_height_for_dy=False
# ):

# def set_pos(ax, x_cm, y_cm, extend_x=False, extend_y=False):
#     """
#     Adjusts the position of an Axes object within a Figure by a specified offset in centimeters.

#     Parameters:
#     - ax (matplotlib.axes.Axes): The Axes object to modify.
#     - x_cm (float): The horizontal offset in centimeters to adjust the Axes position.
#     - y_cm (float): The vertical offset in centimeters to adjust the Axes position.
#     - extend_x (bool): If True, reduces the width of the Axes by the horizontal offset.
#     - extend_y (bool): If True, reduces the height of the Axes by the vertical offset.

#     Returns:
#     - ax (matplotlib.axes.Axes): The modified Axes object with the adjusted position.
#     """

#     bbox = ax.get_position()

#     # Inches
#     x_in, y_in = x_cm / 2.54, y_cm / 2.54

#     # Calculates delta ratios
#     fig = ax.get_figure()
#     fig_x_in, fig_y_in = fig.get_size_inches()
#     x_ratio, y_ratio = x_in / fig_x_in, y_in / fig_y_in

#     # Determines updated bbox position
#     left = bbox.x0 + x_ratio
#     bottom = bbox.y0 + y_ratio
#     width = bbox.width
#     height = bbox.height

#     if extend_x:
#         width -= x_ratio

#     if extend_y:
#         height -= y_ratio

#     ax.set_position([left, bottom, width, height])

#     return ax


# def set_pos(
#     fig,
#     ax,
#     x_cm,
#     y_cm,
#     dragh=False,
#     dragv=False,
# ):

#     bbox = ax.get_position()

#     ## Calculates delta ratios
#     fig_x_in, fig_y_in = fig.get_size_inches()

#     x_in = float(x_cm) / 2.54
#     y_in = float(y_cm) / 2.54

#     x_ratio = x_in / fig_x_in
#     y_ratio = y_in / fig_x_in

#     ## Determines updated bbox position
#     left = bbox.x0 + x_ratio
#     bottom = bbox.y0 + y_ratio
#     width = bbox.x1 - bbox.x0
#     height = bbox.y1 - bbox.y0

#     if dragh:
#         width -= x_ratio

#     if dragv:
#         height -= y_ratio

#     ax.set_pos(
#         [
#             left,
#             bottom,
#             width,
#             height,
#         ]
#     )

#     return ax

# EOF
