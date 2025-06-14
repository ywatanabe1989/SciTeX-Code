#!/usr/bin/env python3
"""Scitex color module."""

from ._add_hue_col import add_hue_col
from ._colors import bgr2bgra, bgr2rgb, bgra2bgr, bgra2hex, bgra2rgba, cycle_color, cycle_color_bgr, cycle_color_rgb, gradiate_color, gradiate_color_bgr, gradiate_color_bgra, gradiate_color_rgb, gradiate_color_rgba, rgb2bgr, rgb2rgba, rgba2bgra, rgba2hex, rgba2rgb, str2bgr, str2bgra, str2hex, str2rgb, str2rgba, to_hex, to_rgb, to_rgba, update_alpha
from ._get_colors_from_cmap import get_categorical_colors_from_cmap, get_color_from_cmap, get_colors_from_cmap
from ._interpolate import gen_interpolate, interpolate
from ._PARAMS import PARAMS, DEF_ALPHA, RGB, RGB_NORM, RGBA, RGBA_NORM
from ._vizualize_colors import vizualize_colors

__all__ = [
    "PARAMS",
    "DEF_ALPHA",
    "RGB",
    "RGB_NORM",
    "RGBA",
    "RGBA_NORM",
    "add_hue_col",
    "bgr2bgra",
    "bgr2rgb",
    "bgra2bgr",
    "bgra2hex",
    "bgra2rgba",
    "cycle_color",
    "cycle_color_bgr",
    "cycle_color_rgb",
    "gen_interpolate",
    "get_categorical_colors_from_cmap",
    "get_color_from_cmap",
    "get_colors_from_cmap",
    "gradiate_color",
    "gradiate_color_bgr",
    "gradiate_color_bgra",
    "gradiate_color_rgb",
    "gradiate_color_rgba",
    "interpolate",
    "rgb2bgr",
    "rgb2rgba",
    "rgba2bgra",
    "rgba2hex",
    "rgba2rgb",
    "str2bgr",
    "str2bgra",
    "str2hex",
    "str2rgb",
    "str2rgba",
    "to_hex",
    "to_rgb",
    "to_rgba",
    "update_alpha",
    "vizualize_colors",
]
