#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 17:45:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/color/test__colors.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/color/test__colors.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from unittest.mock import patch

from scitex.plt.color import (
    bgr2bgra,
    bgr2rgb,
    bgra2bgr,
    bgra2hex,
    bgra2rgba,
    cycle_color,
    cycle_color_bgr,
    cycle_color_rgb,
    gradiate_color_bgr,
    gradiate_color_bgra,
    gradiate_color_rgb,
    gradiate_color_rgba,
    rgb2bgr,
    rgb2rgba,
    rgba2bgra,
    rgba2hex,
    rgba2rgb,
    str2bgr,
    str2bgra,
    str2hex,
    str2rgb,
    str2rgba,
    update_alpha,
)
from scitex.plt.color import PARAMS


def test_str2rgb():
    assert str2rgb("red") == PARAMS["RGB"]["red"]
    assert str2rgb("blue") == PARAMS["RGB"]["blue"]


def test_str2rgba():
    red_rgb = PARAMS["RGB"]["red"]
    expected = [val / 255 for val in red_rgb]
    expected.append(1.0)
    expected = [round(val, 2) for val in expected]
    result = str2rgba("red")
    assert result == expected


def test_rgb2rgba():
    rgb = [255, 0, 0]
    expected = [1.0, 0.0, 0.0, 1.0]
    assert rgb2rgba(rgb) == expected

    rgb = [255, 128, 0]
    expected = [1.0, 0.5, 0.0, 0.7]
    assert rgb2rgba(rgb, alpha=0.7) == expected


def test_rgba2rgb():
    rgba = [1.0, 0.5, 0.0, 0.7]
    expected = [255.0, 127.5, 0.0]
    assert rgba2rgb(rgba) == expected


def test_rgba2hex():
    rgba = [255, 128, 0, 0.5]
    expected = "#ff8000" + hex(int(0.5 * 255))[2:].zfill(2)
    assert rgba2hex(rgba) == expected


def test_cycle_color_rgb():
    mock_colors = ["red", "green", "blue"]

    with patch.dict(
        PARAMS["RGB"],
        {"red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255]},
    ):
        assert cycle_color_rgb(0, colors=mock_colors) == "red"
        assert cycle_color_rgb(1, colors=mock_colors) == "green"
        assert cycle_color_rgb(2, colors=mock_colors) == "blue"
        assert cycle_color_rgb(3, colors=mock_colors) == "red"


def test_gradiate_color_rgb():
    rgb = [255, 0, 0]
    result = gradiate_color_rgb(rgb, n=3)

    assert len(result) == 3
    assert result[0][0] > result[1][0] > result[2][0]


def test_gradiate_color_rgba():
    rgba = [255, 0, 0, 0.8]
    result = gradiate_color_rgba(rgba, n=3)

    assert len(result) == 3
    for color in result:
        assert len(color) == 4
        assert color[3] == 0.8


def test_str2bgr():
    rgb = PARAMS["RGB"]["red"]
    expected = [rgb[2], rgb[1], rgb[0]]
    assert str2bgr("red") == expected


def test_str2bgra():
    red_rgb = PARAMS["RGB"]["red"]
    rgba = [val / 255 for val in red_rgb]
    rgba.append(1.0)
    rgba = [round(val, 2) for val in rgba]
    expected = [rgba[2], rgba[1], rgba[0], rgba[3]]
    result = str2bgra("red")
    assert result == expected


def test_bgr2bgra():
    bgr = [0, 0, 255]
    expected = [0.0, 0.0, 1.0, 1.0]
    assert bgr2bgra(bgr) == expected


def test_bgra2bgr():
    bgra = [0, 0.5, 1.0, 0.7]
    expected = [0.0, 127.5, 255.0]
    assert bgra2bgr(bgra) == expected


def test_bgra2hex():
    bgra = [0, 128, 255, 0.5]
    expected = "#ff8000" + hex(int(0.5 * 255))[2:].zfill(2)
    assert bgra2hex(bgra) == expected


def test_cycle_color_bgr():
    mock_colors = ["red", "green", "blue"]

    with patch.dict(
        PARAMS["RGB"],
        {"red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255]},
    ):
        assert cycle_color_bgr(0, colors=mock_colors) == [0, 0, 255]
        assert cycle_color_bgr(1, colors=mock_colors) == [0, 255, 0]
        assert cycle_color_bgr(2, colors=mock_colors) == [255, 0, 0]


def test_gradiate_color_bgr():
    bgr = [0, 0, 255]
    result = gradiate_color_bgr(bgr, n=3)

    assert len(result) == 3
    assert result[0][2] > result[1][2] > result[2][2]


def test_gradiate_color_bgra():
    bgra = [0, 0, 255, 0.8]
    result = gradiate_color_bgra(bgra, n=3)

    assert len(result) == 3
    for color in result:
        assert len(color) == 4
        assert color[3] == 0.8


def test_bgr2rgb():
    bgr = [0, 128, 255]
    expected = [255, 128, 0]
    assert bgr2rgb(bgr) == expected


def test_rgb2bgr():
    rgb = [255, 128, 0]
    expected = [0, 128, 255]
    assert rgb2bgr(rgb) == expected


def test_bgra2rgba():
    bgra = [0, 128, 255, 0.5]
    expected = [255, 128, 0, 0.5]
    assert bgra2rgba(bgra) == expected


def test_rgba2bgra():
    rgba = [255, 128, 0, 0.5]
    expected = [0, 128, 255, 0.5]
    assert rgba2bgra(rgba) == expected


def test_str2hex():
    assert str2hex("red") == PARAMS["HEX"]["red"]
    assert str2hex("blue") == PARAMS["HEX"]["blue"]


def test_update_alpha():
    rgba = [1.0, 0.5, 0.0, 0.3]
    expected = [1.0, 0.5, 0.0, 0.8]
    assert update_alpha(rgba, 0.8) == expected


def test_cycle_color():
    mock_colors = ["red", "green", "blue"]

    with patch.dict(
        PARAMS["RGB"],
        {"red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255]},
    ):
        assert cycle_color(0, colors=mock_colors) == "red"
        assert cycle_color(1, colors=mock_colors) == "green"
        assert cycle_color(2, colors=mock_colors) == "blue"
        assert cycle_color(3, colors=mock_colors) == "red"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/color/_colors.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 12:19:50 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/colors/_colors.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/colors/_colors.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import matplotlib.colors as _colors
# import numpy as np
# 
# from ...decorators._deprecated import deprecated
# from ._PARAMS import PARAMS
# 
# # RGB
# # ------------------------------
# 
# 
# def str2rgb(c):
#     return PARAMS["RGB"][c]
# 
# 
# def str2rgba(c, alpha=1.0):
#     rgba = rgb2rgba(PARAMS["RGB"][c])
#     rgba[-1] = alpha
#     return rgba
# 
# 
# def rgb2rgba(rgb, alpha=1.0, round=2):
#     rgb = np.array(rgb).astype(float)
#     rgb /= 255
#     return [*rgb.round(round), alpha]
# 
# 
# def rgba2rgb(rgba):
#     rgba = np.array(rgba).astype(float)
#     rgb = (rgba[:3] * 255).clip(0, 255)
#     return rgb.round(2).tolist()
# 
# 
# def rgba2hex(rgba):
#     return "#{:02x}{:02x}{:02x}{:02x}".format(
#         int(rgba[0]), int(rgba[1]), int(rgba[2]), int(rgba[3] * 255)
#     )
# 
# 
# def cycle_color_rgb(i_color, colors=None):
#     if colors is None:
#         colors = list(PARAMS["RGB"].keys())
#     n_colors = len(colors)
#     return colors[i_color % n_colors]
# 
# 
# def gradiate_color_rgb(rgb_or_rgba, n=5):
# 
#     # Separate RGB and alpha if present
#     if len(rgb_or_rgba) == 4:  # RGBA format
#         rgb = rgb_or_rgba[:3]
#         alpha = rgb_or_rgba[3]
#         has_alpha = True
#     else:  # RGB format
#         rgb = rgb_or_rgba
#         alpha = None
#         has_alpha = False
# 
#     # Scale RGB values to 0-1 range if they're in 0-255 range
#     if any(val > 1 for val in rgb):
#         rgb = [val / 255 for val in rgb]
# 
#     rgb_hsv = _colors.rgb_to_hsv(np.array(rgb))
# 
#     gradient = []
#     for step in range(n):
#         color_hsv = [
#             rgb_hsv[0],
#             rgb_hsv[1],
#             rgb_hsv[2] * (1.0 - (step / n)),
#         ]
#         color_rgb = [int(v * 255) for v in _colors.hsv_to_rgb(color_hsv)]
# 
#         if has_alpha:
#             gradient.append(rgb2rgba(color_rgb, alpha=alpha))
#         else:
#             gradient.append(color_rgb)
# 
#     return gradient
# 
# 
# def gradiate_color_rgba(rgb_or_rgba, n=5):
#     return gradiate_color_rgb(rgb_or_rgba, n)
# 
# 
# # BGRA
# # ------------------------------
# def str2bgr(c):
#     return rgb2bgr(str2rgb(c))
# 
# 
# def str2bgra(c, alpha=1.0):
#     return rgba2bgra(str2rgba(c))
# 
# 
# def bgr2bgra(bgra, alpha=1.0, round=2):
#     return rgb2rgba(bgra, alpha=alpha, round=round)
# 
# 
# def bgra2bgr(bgra):
#     return rgba2rgb(bgra)
# 
# 
# def bgra2hex(bgra):
#     """Convert BGRA color format to hex format."""
#     rgba = bgra2rgba(bgra)
#     return rgba2hex(rgba)
# 
# 
# def cycle_color_bgr(i_color, colors=None):
#     rgb_color = str2rgb(cycle_color(i_color, colors=colors))
#     return rgb2bgr(rgb_color)
# 
# 
# def gradiate_color_bgr(bgr_or_bgra, n=5):
#     rgb_or_rgba = (
#         bgr2rgb(bgr_or_bgra) if len(bgr_or_bgra) == 3 else bgra2rgba(bgr_or_bgra)
#     )
#     rgb_gradient = gradiate_color_rgb(rgb_or_rgba, n)
#     return [
#         rgb2bgr(color) if len(color) == 3 else rgba2bgra(color)
#         for color in rgb_gradient
#     ]
# 
# 
# def gradiate_color_bgra(bgra, n=5):
#     return gradiate_color_bgr(bgra, n)
# 
# 
# # Common
# # ------------------------------
# def bgr2rgb(bgr):
#     """Convert BGR color format to RGB format."""
#     return [bgr[2], bgr[1], bgr[0]]
# 
# 
# def rgb2bgr(rgb):
#     """Convert RGB color format to BGR format."""
#     return [rgb[2], rgb[1], rgb[0]]
# 
# 
# def bgra2rgba(bgra):
#     """Convert BGRA color format to RGBA format."""
#     return [bgra[2], bgra[1], bgra[0], bgra[3]]
# 
# 
# def rgba2bgra(rgba):
#     """Convert RGBA color format to BGRA format."""
#     return [rgba[2], rgba[1], rgba[0], rgba[3]]
# 
# 
# def str2hex(c):
#     return PARAMS["HEX"][c]
# 
# 
# def update_alpha(rgba, alpha):
#     rgba_list = list(rgba)
#     rgba_list[-1] = alpha
#     return rgba_list
# 
# 
# def cycle_color(i_color, colors=None):
#     return cycle_color_rgb(i_color, colors=colors)
# 
# 
# # Deprecated
# # ------------------------------
# @deprecated("Use str2rgb instead")
# def to_rgb(c):
#     return str2rgb(c)
# 
# 
# @deprecated("use str2rgba instewad")
# def to_rgba(c, alpha=1.0):
#     return str2rgba(c, alpha=alpha)
# 
# 
# @deprecated("use str2hex instead")
# def to_hex(c):
#     return PARAMS["HEX"][c]
# 
# 
# @deprecated("use gradiate_color_rgb/rgba/bgr/bgra instead")
# def gradiate_color(rgb_or_rgba, n=5):
#     return gradiate_color_rgb(rgb_or_rgba, n)
# 
# 
# if __name__ == "__main__":
#     c = "blue"
#     print(to_rgb(c))
#     print(to_rgba(c))
#     print(to_hex(c))
#     print(cycle_color(1))
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/color/_colors.py
# --------------------------------------------------------------------------------
