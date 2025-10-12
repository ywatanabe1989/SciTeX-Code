#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-21 01:52:22 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_export_as_csv.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings

import numpy as np
import pandas as pd
from scitex.pd import to_xyz

from ._export_as_csv_formatters import (_format_annotate, _format_bar,
                                        _format_barh, _format_boxplot,
                                        _format_contour, _format_errorbar,
                                        _format_eventplot, _format_fill,
                                        _format_fill_between, _format_hist,
                                        _format_imshow, _format_imshow2d,
                                        _format_plot, _format_plot_box,
                                        _format_plot_conf_mat,
                                        _format_plot_ecdf, _format_plot_fillv,
                                        _format_plot_heatmap,
                                        _format_plot_image,
                                        _format_plot_joyplot, _format_plot_kde,
                                        _format_plot_line,
                                        _format_plot_mean_ci,
                                        _format_plot_mean_std,
                                        _format_plot_median_iqr,
                                        _format_plot_raster,
                                        _format_plot_rectangle,
                                        _format_plot_scatter,
                                        _format_plot_scatter_hist,
                                        _format_plot_shaded_line,
                                        _format_plot_violin, _format_scatter,
                                        _format_sns_barplot,
                                        _format_sns_boxplot,
                                        _format_sns_heatmap,
                                        _format_sns_histplot,
                                        _format_sns_jointplot,
                                        _format_sns_kdeplot,
                                        _format_sns_lineplot,
                                        _format_sns_pairplot,
                                        _format_sns_scatterplot,
                                        _format_sns_stripplot,
                                        _format_sns_swarmplot,
                                        _format_sns_violinplot, _format_text,
                                        _format_violin, _format_violinplot)


def _to_numpy(data):
    """Convert various data types to numpy array.

    Handles torch tensors, pandas Series/DataFrame, and other array-like objects.

    Parameters
    ----------
    data : array-like
        Data to convert to numpy array

    Returns
    -------
    numpy.ndarray
        Data as numpy array
    """
    if hasattr(data, "numpy"):  # torch tensor
        return (
            data.detach().numpy() if hasattr(data, "detach") else data.numpy()
        )
    elif hasattr(data, "values"):  # pandas series/dataframe
        return data.values
    else:
        return np.asarray(data)


def export_as_csv(history_records):
    """Convert plotting history records to a combined DataFrame suitable for CSV export.

    Args:
        history_records (dict): Dictionary of plotting records.

    Returns:
        pd.DataFrame: Combined DataFrame containing all plotting data.

    Raises:
        ValueError: If no plotting records are found or they cannot be combined.
    """
    if len(history_records) <= 0:
        warnings.warn("Plotting records not found. Cannot export empty data.")
        return pd.DataFrame()  # Return empty DataFrame instead of None

    dfs = []
    for record in list(history_records.values()):
        try:
            formatted_df = format_record(record)
            if formatted_df is not None and not formatted_df.empty:
                dfs.append(formatted_df)
        except Exception as e:
            warnings.warn(f"Failed to format record {record[0]}: {e}")

    # If no valid dataframes were created, return an empty one
    if not dfs:
        warnings.warn("No valid data found to export.")
        return pd.DataFrame()

    try:
        # Reset index for each dataframe to avoid alignment issues
        dfs_reset = [df.reset_index(drop=True) for df in dfs]
        df = pd.concat(dfs_reset, axis=1)
        return df
    except Exception as e:
        warnings.warn(f"Failed to combine plotting records: {e}")
        # Return a DataFrame with metadata about what records were attempted
        meta_df = pd.DataFrame(
            {
                "record_id": [r[0] for r in history_records.values()],
                "method": [r[1] for r in history_records.values()],
                "has_data": [
                    "Yes" if r[2] and r[2] != {} else "No"
                    for r in history_records.values()
                ],
            }
        )
        return meta_df


def format_record(record):
    """Route record to the appropriate formatting function based on plot method.

    Args:
        record (tuple): Plotting record tuple (id, method, tracked_dict, kwargs).

    Returns:
        pd.DataFrame: Formatted data for the plot record.
    """
    id, method, tracked_dict, kwargs = record

    # Basic Matplotlib functions
    if method == "plot":
        return _format_plot(id, tracked_dict, kwargs)
    elif method == "scatter":
        return _format_scatter(id, tracked_dict, kwargs)
    elif method == "bar":
        return _format_bar(id, tracked_dict, kwargs)
    elif method == "barh":
        return _format_barh(id, tracked_dict, kwargs)
    elif method == "hist":
        return _format_hist(id, tracked_dict, kwargs)
    elif method == "boxplot":
        return _format_boxplot(id, tracked_dict, kwargs)
    elif method == "contour":
        return _format_contour(id, tracked_dict, kwargs)
    elif method == "errorbar":
        return _format_errorbar(id, tracked_dict, kwargs)
    elif method == "eventplot":
        return _format_eventplot(id, tracked_dict, kwargs)
    elif method == "fill":
        return _format_fill(id, tracked_dict, kwargs)
    elif method == "fill_between":
        return _format_fill_between(id, tracked_dict, kwargs)
    elif method == "imshow":
        return _format_imshow(id, tracked_dict, kwargs)
    elif method == "imshow2d":
        return _format_imshow2d(id, tracked_dict, kwargs)
    elif method == "violin":
        return _format_violin(id, tracked_dict, kwargs)
    elif method == "violinplot":
        return _format_violinplot(id, tracked_dict, kwargs)
    elif method == "text":
        return _format_text(id, tracked_dict, kwargs)
    elif method == "annotate":
        return _format_annotate(id, tracked_dict, kwargs)

    # Custom plotting functions
    elif method == "plot_box":
        return _format_plot_box(id, tracked_dict, kwargs)
    elif method == "plot_conf_mat":
        return _format_plot_conf_mat(id, tracked_dict, kwargs)
    elif method == "plot_ecdf":
        return _format_plot_ecdf(id, tracked_dict, kwargs)
    elif method == "plot_fillv":
        return _format_plot_fillv(id, tracked_dict, kwargs)
    elif method == "plot_heatmap":
        return _format_plot_heatmap(id, tracked_dict, kwargs)
    elif method == "plot_image":
        return _format_plot_image(id, tracked_dict, kwargs)
    elif method == "plot_joyplot":
        return _format_plot_joyplot(id, tracked_dict, kwargs)
    elif method == "plot_kde":
        return _format_plot_kde(id, tracked_dict, kwargs)
    elif method == "plot_line":
        return _format_plot_line(id, tracked_dict, kwargs)
    elif method == "plot_mean_ci":
        return _format_plot_mean_ci(id, tracked_dict, kwargs)
    elif method == "plot_mean_std":
        return _format_plot_mean_std(id, tracked_dict, kwargs)
    elif method == "plot_median_iqr":
        return _format_plot_median_iqr(id, tracked_dict, kwargs)
    elif method == "plot_raster":
        return _format_plot_raster(id, tracked_dict, kwargs)
    elif method == "plot_rectangle":
        return _format_plot_rectangle(id, tracked_dict, kwargs)
    elif method == "plot_scatter":
        return _format_plot_scatter(id, tracked_dict, kwargs)
    elif method == "plot_scatter_hist":
        return _format_plot_scatter_hist(id, tracked_dict, kwargs)
    elif method == "plot_shaded_line":
        return _format_plot_shaded_line(id, tracked_dict, kwargs)
    elif method == "plot_violin":
        return _format_plot_violin(id, tracked_dict, kwargs)

    # Seaborn functions
    elif method == "sns_barplot":
        return _format_sns_barplot(id, tracked_dict, kwargs)
    elif method == "sns_boxplot":
        return _format_sns_boxplot(id, tracked_dict, kwargs)
    elif method == "sns_heatmap":
        return _format_sns_heatmap(id, tracked_dict, kwargs)
    elif method == "sns_histplot":
        return _format_sns_histplot(id, tracked_dict, kwargs)
    elif method == "sns_jointplot":
        return _format_sns_jointplot(id, tracked_dict, kwargs)
    elif method == "sns_kdeplot":
        return _format_sns_kdeplot(id, tracked_dict, kwargs)
    elif method == "sns_lineplot":
        return _format_sns_lineplot(id, tracked_dict, kwargs)
    elif method == "sns_pairplot":
        return _format_sns_pairplot(id, tracked_dict, kwargs)
    elif method == "sns_scatterplot":
        return _format_sns_scatterplot(id, tracked_dict, kwargs)
    elif method == "sns_stripplot":
        return _format_sns_stripplot(id, tracked_dict, kwargs)
    elif method == "sns_swarmplot":
        return _format_sns_swarmplot(id, tracked_dict, kwargs)
    elif method == "sns_violinplot":
        return _format_sns_violinplot(id, tracked_dict, kwargs)
    else:
        # Unknown or unimplemented method
        raise NotImplementedError(
            f"CSV export for plot method '{method}' is not yet implemented in the scitex.plt module. "
            f"Check the feature-request-export-as-csv-functions.md for implementation status."
        )

# EOF
