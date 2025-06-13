#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 20:12:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/__init__.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/__init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Adjust
from ._style._add_marginal_ax import add_marginal_ax
from ._style._add_panel import add_panel, panel
from ._style._extend import extend
from ._style._force_aspect import force_aspect
from ._style._format_label import format_label
from ._style._hide_spines import hide_spines
from ._style._show_spines import (
    show_spines,
    show_all_spines,
    show_classic_spines,
    show_box_spines,
    toggle_spines,
    scientific_spines,
    clean_spines,
)
from ._style._map_ticks import map_ticks
from ._style._rotate_labels import rotate_labels
from ._style._sci_note import sci_note
from ._style._set_n_ticks import set_n_ticks
from ._style._set_size import set_size
from ._style._set_supxyt import set_supxyt
from ._style._set_ticks import set_ticks
from ._style._set_xyt import set_xyt
from ._style._shift import shift
from ._style._share_axes import (
    get_global_xlim,
    get_global_ylim,
    set_xlims,
    set_ylims,
    sharex,
    sharexy,
    sharey,
)
from ._style._set_log_scale import (
    set_log_scale,
    smart_log_limits,
    add_log_scale_indicator,
)

# Plot
from ._plot._plot_heatmap import plot_heatmap
from ._plot._plot_circular_hist import plot_circular_hist
from ._plot._plot_conf_mat import plot_conf_mat
from ._plot._plot_cube import plot_cube
from ._plot._plot_ecdf import plot_ecdf
from ._plot._plot_fillv import plot_fillv
from ._plot._plot_violin import plot_violin
from ._plot._plot_image import plot_image
from ._plot._plot_joyplot import plot_joyplot
from ._plot._plot_raster import plot_raster
from ._plot._plot_rectangle import plot_rectangle
from ._plot._plot_scatter_hist import plot_scatter_hist
from ._plot._plot_shaded_line import plot_shaded_line
from ._plot._plot_statistical_shaded_line import (
    plot_line,
    plot_mean_std,
    plot_mean_ci,
    plot_median_iqr,
)


# ################################################################################
# # For Matplotlib Compatibility
# ################################################################################
# import matplotlib.pyplot.axis as counter_part
# _local_module_attributes = list(globals().keys())
# print(_local_module_attributes)

# def __getattr__(name):
#     """
#     Fallback to fetch attributes from matplotlib.pyplot
#     if they are not defined directly in this module.
#     """
#     try:
#         # Get the attribute from matplotlib.pyplot
#         return getattr(counter_part, name)
#     except AttributeError:
#         # Raise the standard error if not found in pyplot either
#         raise AttributeError(
#             f"module '{__name__}' nor matplotlib.pyplot has attribute '{name}'"
#         ) from None

# def __dir__():
#     """
#     Provide combined directory for tab completion, including
#     attributes from this module and matplotlib.pyplot.
#     """
#     # Get attributes defined explicitly in this module
#     local_attrs = set(_local_module_attributes)
#     # Get attributes from matplotlib.pyplot
#     pyplot_attrs = set(dir(counter_part))
#     # Return the sorted union
#     return sorted(local_attrs.union(pyplot_attrs))

# """
# import matplotlib.pyplot as plt
# import scitex.plt as mplt

# print(set(dir(mplt.ax)) - set(dir(plt.axis)))
# """

# EOF
