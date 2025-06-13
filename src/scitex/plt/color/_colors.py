#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 12:19:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/colors/_colors.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/colors/_colors.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.colors as _colors
import numpy as np

from ...decorators._deprecated import deprecated
from ._PARAMS import PARAMS

# RGB
# ------------------------------


def str2rgb(c):
    return PARAMS["RGB"][c]


def str2rgba(c, alpha=1.0):
    rgba = rgb2rgba(PARAMS["RGB"][c])
    rgba[-1] = alpha
    return rgba


def rgb2rgba(rgb, alpha=1.0, round=2):
    rgb = np.array(rgb).astype(float)
    rgb /= 255
    return [*rgb.round(round), alpha]


def rgba2rgb(rgba):
    rgba = np.array(rgba).astype(float)
    rgb = (rgba[:3] * 255).clip(0, 255)
    return rgb.round(2).tolist()


def rgba2hex(rgba):
    return "#{:02x}{:02x}{:02x}{:02x}".format(
        int(rgba[0]), int(rgba[1]), int(rgba[2]), int(rgba[3] * 255)
    )


def cycle_color_rgb(i_color, colors=None):
    if colors is None:
        colors = list(PARAMS["RGB"].keys())
    n_colors = len(colors)
    return colors[i_color % n_colors]


def gradiate_color_rgb(rgb_or_rgba, n=5):

    # Separate RGB and alpha if present
    if len(rgb_or_rgba) == 4:  # RGBA format
        rgb = rgb_or_rgba[:3]
        alpha = rgb_or_rgba[3]
        has_alpha = True
    else:  # RGB format
        rgb = rgb_or_rgba
        alpha = None
        has_alpha = False

    # Scale RGB values to 0-1 range if they're in 0-255 range
    if any(val > 1 for val in rgb):
        rgb = [val / 255 for val in rgb]

    rgb_hsv = _colors.rgb_to_hsv(np.array(rgb))

    gradient = []
    for step in range(n):
        color_hsv = [
            rgb_hsv[0],
            rgb_hsv[1],
            rgb_hsv[2] * (1.0 - (step / n)),
        ]
        color_rgb = [int(v * 255) for v in _colors.hsv_to_rgb(color_hsv)]

        if has_alpha:
            gradient.append(rgb2rgba(color_rgb, alpha=alpha))
        else:
            gradient.append(color_rgb)

    return gradient


def gradiate_color_rgba(rgb_or_rgba, n=5):
    return gradiate_color_rgb(rgb_or_rgba, n)


# BGRA
# ------------------------------
def str2bgr(c):
    return rgb2bgr(str2rgb(c))


def str2bgra(c, alpha=1.0):
    return rgba2bgra(str2rgba(c))


def bgr2bgra(bgra, alpha=1.0, round=2):
    return rgb2rgba(bgra, alpha=alpha, round=round)


def bgra2bgr(bgra):
    return rgba2rgb(bgra)


def bgra2hex(bgra):
    """Convert BGRA color format to hex format."""
    rgba = bgra2rgba(bgra)
    return rgba2hex(rgba)


def cycle_color_bgr(i_color, colors=None):
    rgb_color = str2rgb(cycle_color(i_color, colors=colors))
    return rgb2bgr(rgb_color)


def gradiate_color_bgr(bgr_or_bgra, n=5):
    rgb_or_rgba = (
        bgr2rgb(bgr_or_bgra) if len(bgr_or_bgra) == 3 else bgra2rgba(bgr_or_bgra)
    )
    rgb_gradient = gradiate_color_rgb(rgb_or_rgba, n)
    return [
        rgb2bgr(color) if len(color) == 3 else rgba2bgra(color)
        for color in rgb_gradient
    ]


def gradiate_color_bgra(bgra, n=5):
    return gradiate_color_bgr(bgra, n)


# Common
# ------------------------------
def bgr2rgb(bgr):
    """Convert BGR color format to RGB format."""
    return [bgr[2], bgr[1], bgr[0]]


def rgb2bgr(rgb):
    """Convert RGB color format to BGR format."""
    return [rgb[2], rgb[1], rgb[0]]


def bgra2rgba(bgra):
    """Convert BGRA color format to RGBA format."""
    return [bgra[2], bgra[1], bgra[0], bgra[3]]


def rgba2bgra(rgba):
    """Convert RGBA color format to BGRA format."""
    return [rgba[2], rgba[1], rgba[0], rgba[3]]


def str2hex(c):
    return PARAMS["HEX"][c]


def update_alpha(rgba, alpha):
    rgba_list = list(rgba)
    rgba_list[-1] = alpha
    return rgba_list


def cycle_color(i_color, colors=None):
    return cycle_color_rgb(i_color, colors=colors)


# Deprecated
# ------------------------------
@deprecated("Use str2rgb instead")
def to_rgb(c):
    return str2rgb(c)


@deprecated("use str2rgba instewad")
def to_rgba(c, alpha=1.0):
    return str2rgba(c, alpha=alpha)


@deprecated("use str2hex instead")
def to_hex(c):
    return PARAMS["HEX"][c]


@deprecated("use gradiate_color_rgb/rgba/bgr/bgra instead")
def gradiate_color(rgb_or_rgba, n=5):
    return gradiate_color_rgb(rgb_or_rgba, n)


if __name__ == "__main__":
    c = "blue"
    print(to_rgb(c))
    print(to_rgba(c))
    print(to_hex(c))
    print(cycle_color(1))

# EOF
