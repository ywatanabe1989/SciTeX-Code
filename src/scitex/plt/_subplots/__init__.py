#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 05:22:40 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/_subplots/__init__.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_subplots/__init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Import export_as_csv module functions
from ._export_as_csv import export_as_csv, format_record

# Import formatters for backward compatibility
from ._export_as_csv_formatters import (
    _format_plot_kde,
    _format_plot_line,
    _format_plot_conf_mat,
    _format_plot_mean_std,
    _format_plot_ecdf,
    _format_plot_raster,
    _format_plot_joyplot,
    _format_plot,
    _format_scatter,
    _format_bar,
    _format_hist,
    _format_boxplot,
    _format_errorbar,
    _format_fill_between,
    _format_imshow,
    _format_violin,
    _format_sns_boxplot,
)

# import importlib
# import inspect

# # Get the current directory
# current_dir = os.path.dirname(__file__)

# # Iterate through all Python files in the current directory
# for filename in os.listdir(current_dir):
#     if filename.endswith(".py") and not filename.startswith("__"):
#         module_name = filename[:-3]  # Remove .py extension
#         module = importlib.import_module(f".{module_name}", package=__name__)

#         # Import only functions and classes from the module
#         for name, obj in inspect.getmembers(module):
#             if inspect.isfunction(obj) or inspect.isclass(obj):
#                 if not name.startswith("_"):
#                     globals()[name] = obj

# # Clean up temporary variables
# del (
#     os,
#     importlib,
#     inspect,
#     current_dir,
#     filename,
#     module_name,
#     module,
#     name,
#     obj,
# )

# ################################################################################
# # For Matplotlib Compatibility
# ################################################################################
# import matplotlib.pyplot.subplots as counter_part

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


"""
import matplotlib.pyplot as plt
import scitex.plt as mplt

print(set(dir(mplt.subplots)) - set(dir(plt.subplots)))
"""

# EOF
