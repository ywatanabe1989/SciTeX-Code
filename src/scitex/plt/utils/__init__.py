#!/usr/bin/env python3
"""Scitex utils module."""

from ._calc_bacc_from_conf_mat import calc_bacc_from_conf_mat
from ._calc_nice_ticks import calc_nice_ticks
from ._close import close
from ._colorbar import add_shared_colorbar, colorbar
from ._configure_mpl import configure_mpl
from ._histogram_utils import HistogramBinManager, histogram_bin_manager
from ._im2grid import im2grid
from ._is_valid_axis import assert_valid_axis, is_valid_axis
from ._mk_colorbar import mk_colorbar
from ._mk_patches import mk_patches
from ._scientific_captions import ScientificCaption, add_figure_caption, add_panel_captions, caption_manager, create_figure_list, cross_ref, enhance_scitex_save_with_captions, export_captions, quick_caption, save_with_caption
from ._scitex_config import SciTeXConfig, configure_scitex_ecosystem, get_scitex_config

__all__ = [
    "HistogramBinManager",
    "SciTeXConfig",
    "ScientificCaption",
    "add_figure_caption",
    "add_panel_captions",
    "add_shared_colorbar",
    "assert_valid_axis",
    "calc_bacc_from_conf_mat",
    "calc_nice_ticks",
    "caption_manager",
    "close",
    "colorbar",
    "configure_mpl",
    "configure_scitex_ecosystem",
    "create_figure_list",
    "cross_ref",
    "enhance_scitex_save_with_captions",
    "export_captions",
    "get_scitex_config",
    "histogram_bin_manager",
    "im2grid",
    "is_valid_axis",
    "mk_colorbar",
    "mk_patches",
    "quick_caption",
    "save_with_caption",
]
