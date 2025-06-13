#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 22:01:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_violin.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_plot/_plot_violin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from ....plt.utils import assert_valid_axis


def plot_violin(
    ax,
    data_list,
    labels=None,
    colors=None,
    half=False,
    **kwargs,
):
    """
    Plot a violin plot using seaborn.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
        The axes to plot on
    data_list : list
        List of arrays to plot as violins
    labels : list, optional
        Labels for each array in data_list
    colors : list, optional
        Colors for each violin
    half : bool, optional
        If True, plots only the left half of the violins, default False
    **kwargs
        Additional keyword arguments passed to seaborn.violinplot

    Returns
    -------
    ax : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
        The axes object with the plot
    """
    # Convert list-style data to DataFrame
    all_values = []
    all_groups = []

    for idx, values in enumerate(data_list):
        all_values.extend(values)
        group_label = labels[idx] if labels and idx < len(labels) else f"x {idx}"
        all_groups.extend([group_label] * len(values))

    # Create DataFrame
    df = pd.DataFrame({"x": all_groups, "y": all_values})

    # Setup colors if provided
    if colors:
        if isinstance(colors, list):
            kwargs["palette"] = {
                group: color
                for group, color in zip(set(all_groups), colors[: len(set(all_groups))])
            }
        else:
            kwargs["palette"] = colors

    # Call seaborn-based function
    return sns_plot_violin(ax, data=df, x="x", y="y", hue="x", half=half, **kwargs)


def sns_plot_violin(ax, data=None, x=None, y=None, hue=None, half=False, **kwargs):
    """
    Plot a violin plot with option for half violins.
    Parameters
    ----------
    ax : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
        The axes to plot on
    data : DataFrame
        The dataframe containing the data
    x : str
        Column name for x-axis variable
    y : str
        Column name for y-axis variable
    hue : str, optional
        Column name for hue variable
    half : bool, optional
        If True, plots only the left half of the violins, default False
    **kwargs
        Additional keyword arguments passed to seaborn.violinplot
    Returns
    -------
    ax : matplotlib.axes.Axes or scitex.plt._subplots.AxisWrapper
        The axes object with the plot
    """
    assert_valid_axis(ax, "First argument must be a matplotlib axis or scitex axis wrapper")

    if not half:
        # Standard violin plot
        return sns.violinplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)

    # Create a copy of the dataframe to avoid modifying the original
    df = data.copy()

    # If no hue provided, create default hue
    if hue is None:
        df["_hue"] = "default"
        hue = "_hue"

    # Add fake hue for the right side
    df["_fake_hue"] = df[hue] + "_right"

    # Adjust hue_order and palette if provided
    if "hue_order" in kwargs:
        kwargs["hue_order"] = kwargs["hue_order"] + [
            h + "_right" for h in kwargs["hue_order"]
        ]
    else:
        kwargs["hue_order"] = []
        for group in df[x].unique().tolist():
            kwargs["hue_order"].append(group)
            kwargs["hue_order"].append(group + "_right")

    if "palette" in kwargs:
        palette = kwargs["palette"]
        if isinstance(palette, dict):
            kwargs["palette"] = {
                **palette,
                **{k + "_right": v for k, v in palette.items()},
            }
        elif isinstance(palette, list):
            kwargs["palette"] = palette + palette

    # Conc left and right
    df_left = df[[x, y]]
    df_right = df[["_fake_hue", y]].rename(columns={"_fake_hue": x})
    df_right[y] = [np.nan for _ in range(len(df_right))]
    df_conc = pd.concat([df_left, df_right], axis=0, ignore_index=True)
    df_conc = df_conc.sort_values(x)

    # Plot
    sns.violinplot(data=df_conc, x=x, y=y, hue="x", split=True, ax=ax, **kwargs)

    # Remove right half of violins
    for collection in ax.collections:
        if isinstance(collection, plt.matplotlib.collections.PolyCollection):
            collection.set_clip_path(None)

    # Adjust legend
    if ax.legend_ is not None:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])

    return ax


# def _plot_half_violin(ax, data=None, x=None, y=None, hue=None, **kwargs):

#     assert isinstance(
#         ax, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis"

#     # Prepare data
#     df = data.copy()
#     if hue is None:
#         df["_hue"] = "default"
#         hue = "_hue"

#     # Add fake hue for the right side
#     df["_fake_hue"] = df[hue] + "_right"

#     # Adjust hue_order and palette if provided
#     if "hue_order" in kwargs:
#         kwargs["hue_order"] = kwargs["hue_order"] + [
#             h + "_right" for h in kwargs["hue_order"]
#         ]

#     if "palette" in kwargs:
#         palette = kwargs["palette"]
#         if isinstance(palette, dict):
#             kwargs["palette"] = {
#                 **palette,
#                 **{k + "_right": v for k, v in palette.items()},
#             }
#         elif isinstance(palette, list):
#             kwargs["palette"] = palette + palette

#     # Plot
#     sns.violinplot(
#         data=df, x=x, y=y, hue="_fake_hue", split=True, ax=ax, **kwargs
#     )

#     # Remove right half of violins
#     for collection in ax.collections:
#         if isinstance(collection, plt.matplotlib.collections.PolyCollection):
#             collection.set_clip_path(None)

#     # Adjust legend
#     if ax.legend_ is not None:
#         handles, labels = ax.get_legend_handles_labels()
#         ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])

#     return ax

# import matplotlib
# import matplotlib.pyplot as plt
# import seaborn as sns

# def plot_violin_half(ax, data=None, x=None, y=None, hue=None, **kwargs):
#     """
#     Plot a half violin plot (showing only the left side of violins).

#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The axes to plot on
#     data : DataFrame
#         The dataframe containing the data
#     x : str
#         Column name for x-axis variable
#     y : str
#         Column name for y-axis variable
#     hue : str, optional
#         Column name for hue variable
#     **kwargs
#         Additional keyword arguments passed to seaborn.violinplot

#     Returns
#     -------
#     ax : matplotlib.axes.Axes
#         The axes object with the plot
#     """
#     assert isinstance(
#         ax, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis"

#     # Prepare data
#     df = data.copy()
#     if hue is None:
#         df["_hue"] = "default"
#         hue = "_hue"

#     # Add fake hue for the right side
#     df["_fake_hue"] = df[hue] + "_right"

#     # Adjust hue_order and palette if provided
#     if "hue_order" in kwargs:
#         kwargs["hue_order"] = kwargs["hue_order"] + [
#             h + "_right" for h in kwargs["hue_order"]
#         ]
#     if "palette" in kwargs:
#         palette = kwargs["palette"]
#         if isinstance(palette, dict):
#             kwargs["palette"] = {
#                 **palette,
#                 **{k + "_right": v for k, v in palette.items()},
#             }
#         elif isinstance(palette, list):
#             kwargs["palette"] = palette + palette

#     # Plot
#     sns.violinplot(
#         data=df, x=x, y=y, hue="_fake_hue", split=True, ax=ax, **kwargs
#     )

#     # Remove right half of violins
#     for collection in ax.collections:
#         if isinstance(collection, matplotlib.collections.PolyCollection):
#             collection.set_clip_path(None)

#     # Adjust legend
#     if ax.legend_ is not None:
#         handles, labels = ax.get_legend_handles_labels()
#         ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])

#     return ax


## Probably working
def half_violin(ax, data=None, x=None, y=None, hue=None, **kwargs):
    # Prepare data
    df = data.copy()
    if hue is None:
        df["_hue"] = "default"
        hue = "_hue"

    # Add fake hue for the right side
    df["_fake_hue"] = df[hue] + "_right"

    # Adjust hue_order and palette if provided
    if "hue_order" in kwargs:
        kwargs["hue_order"] = kwargs["hue_order"] + [
            h + "_right" for h in kwargs["hue_order"]
        ]

    if "palette" in kwargs:
        palette = kwargs["palette"]
        if isinstance(palette, dict):
            kwargs["palette"] = {
                **palette,
                **{k + "_right": v for k, v in palette.items()},
            }
        elif isinstance(palette, list):
            kwargs["palette"] = palette + palette

    # Plot
    sns.violinplot(data=df, x=x, y=y, hue="_fake_hue", split=True, ax=ax, **kwargs)

    # Remove right half of violins
    for collection in ax.collections:
        if isinstance(collection, plt.matplotlib.collections.PolyCollection):
            collection.set_clip_path(None)

    # Adjust legend
    if ax.legend_ is not None:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])

    return ax


# import scitex
# import numpy as np
# fig, ax = scitex.plt.subplots()
# # Test with list data
# data_list = [
#     np.random.normal(0, 1, 100),
#     np.random.normal(2, 1.5, 100),
#     np.random.normal(5, 0.8, 100),
# ]
# labels = ["x A", "x B", "x C"]
# colors = ["red", "blue", "green"]
# half = True
# ax = half_violin(
#     ax, data_list, x=""
# )

# EOF
