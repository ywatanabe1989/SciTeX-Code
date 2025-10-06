#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 22:55:11 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/str/__init__.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex str module."""

from ._clean_path import clean_path
from ._color_text import color_text, ct
from ._decapitalize import decapitalize
from ._factor_out_digits import (
    auto_factor_axis,
    factor_out_digits,
    smart_tick_formatter,
)
from ._format_plot_text import (
    axis_label,
    check_unit_consistency,
    format_axis_label,
    format_plot_text,
    format_title,
    scientific_text,
    title,
)
from ._grep import grep
from ._latex import (
    add_hat_in_latex_style,
    hat_latex_style,
    latex_style,
    safe_add_hat_in_latex_style,
    safe_to_latex_style,
    to_latex_style,
)
from ._latex_fallback import (
    LaTeXFallbackError,
    check_latex_capability,
    disable_latex_fallback,
    enable_latex_fallback,
    get_fallback_mode,
    get_latex_status,
    latex_fallback_decorator,
    latex_to_mathtext,
    latex_to_unicode,
    logger,
    reset_latex_cache,
    safe_latex_render,
    set_fallback_mode,
)
from ._mask_api import mask_api
from ._mask_api_key import mask_api
from ._parse import parse
from ._print_block import printc
from ._print_debug import print_debug
from ._printc import printc
from ._readable_bytes import readable_bytes
from ._remove_ansi import remove_ansi
from ._replace import replace
from ._search import search
from ._squeeze_space import squeeze_spaces

__all__ = [
    "LaTeXFallbackError",
    "add_hat_in_latex_style",
    "auto_factor_axis",
    "axis_label",
    "check_latex_capability",
    "check_unit_consistency",
    "clean_path",
    "color_text",
    "ct",
    "decapitalize",
    "disable_latex_fallback",
    "enable_latex_fallback",
    "factor_out_digits",
    "format_axis_label",
    "format_plot_text",
    "format_title",
    "get_fallback_mode",
    "get_latex_status",
    "grep",
    "hat_latex_style",
    "latex_fallback_decorator",
    "latex_style",
    "latex_to_mathtext",
    "latex_to_unicode",
    "logger",
    "mask_api",
    "parse",
    "print_debug",
    "printc",
    "readable_bytes",
    "remove_ansi",
    "replace",
    "reset_latex_cache",
    "safe_add_hat_in_latex_style",
    "safe_latex_render",
    "safe_to_latex_style",
    "scientific_text",
    "search",
    "set_fallback_mode",
    "smart_tick_formatter",
    "squeeze_spaces",
    "title",
    "to_latex_style",
]

# EOF
