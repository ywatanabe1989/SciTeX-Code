#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-09-26 07:22:18 (ywatanabe)"
# /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/pd/_from_xyz.py

import pandas as pd
import numpy as np


def from_xyz(data_frame, x=None, y=None, z=None, square=False):
    """
    Convert a DataFrame with 'x', 'y', 'z' format into a heatmap DataFrame.

    Example
    -------
    import pandas as pd
    data = pd.DataFrame({
        'col1': ['A', 'B', 'C', 'A'],
        'col2': ['X', 'Y', 'Z', 'Y'],
        'p_val': [0.01, 0.05, 0.001, 0.1]
    })
    data = data.rename(columns={"col1": "x", "col2": "y", "p_val": "z"})
    result = from_xyz(data)
    print(result)

    Parameters
    ----------
    data_frame : pandas.DataFrame
        Input DataFrame with columns for x, y, and z values.
    x : str, optional
        Name of the column to use as x-axis. Defaults to 'x'.
    y : str, optional
        Name of the column to use as y-axis. Defaults to 'y'.
    z : str, optional
        Name of the column to use as z-values. Defaults to 'z'.
    square : bool, optional
        If True, force the output to be a square matrix. Defaults to False.

    Returns
    -------
    pandas.DataFrame
        A DataFrame in heatmap/pivot format.
    """
    x = x or "x"
    y = y or "y"
    z = z or "z"

    heatmap = pd.pivot_table(data_frame, values=z, index=y, columns=x, aggfunc="first")

    if square:
        # Make it square by including all unique labels
        all_labels = sorted(set(heatmap.index) | set(heatmap.columns))
        heatmap = heatmap.reindex(index=all_labels, columns=all_labels)

    heatmap = heatmap.fillna(0)

    return heatmap


if __name__ == "__main__":
    np.random.seed(42)
    stats = pd.DataFrame(
        {
            "col1": np.random.choice(["A", "B", "C"], 100),
            "col2": np.random.choice(["X", "Y", "Z"], 100),
            "p_val": np.random.rand(100),
        }
    )
    stats = stats.rename(columns={"col1": "x", "col2": "y", "p_val": "z"})
    result = from_xyz(stats)
    print(result)
