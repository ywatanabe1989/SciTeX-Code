#!/./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-09-28 11:17:22 (ywatanabe)"
# ./src/scitex/pd/_to_xyz.py

import scitex
import numpy as np
import pandas as pd


def to_xyz(data_frame):
    """
    Convert a DataFrame into x, y, z format (long format).

    Transforms a DataFrame from wide format (matrix/heatmap) to long format
    where each value becomes a row with x (row index), y (column name),
    and z (value) columns.

    Example
    -------
    data_frame = pd.DataFrame(...)  # Your DataFrame here
    out = to_xyz(data_frame)
    print(out)

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The input DataFrame to be converted.

    Returns
    -------
    pandas.DataFrame
        A DataFrame formatted with columns ['x', 'y', 'z']
    """
    x_name = data_frame.index.name or "x"
    y_name = data_frame.columns.name or "y"

    formatted_data_frames = []

    for column in data_frame.columns:
        column_data_frame = data_frame[column]
        formatted_data = pd.DataFrame(
            {
                x_name: column_data_frame.index,
                y_name: column,
                "z": column_data_frame.values,
            }
        )
        formatted_data_frames.append(formatted_data)

    result = pd.concat(formatted_data_frames, ignore_index=True)

    # Ensure column order is x, y, z
    col_order = [x_name, y_name, "z"]
    result = result[col_order]

    return result


# def to_xyz(data_frame):
#     """
#     Convert a heatmap DataFrame into x, y, z format.

#     Ensure the index and columns are the same, and if either exists, replace with that.

#     Example
#     -------
#     data_frame = pd.DataFrame(...)  # Your DataFrame here
#     out = to_xy(data_frame)
#     print(out)

#     Parameters
#     ----------
#     data_frame : pandas.DataFrame
#         The input DataFrame to be converted.

#     Returns
#     -------
#     pandas.DataFrame
#         A DataFrame formatted with columns ['x', 'y', 'z']
#     """
#     assert data_frame.shape[0] == data_frame.shape[1]

#     if not data_frame.index.equals(data_frame.columns):

#         if (data_frame.index == np.array(range(len(data_frame.index)))).all():
#             data_frame.columns = data_frame.index
#         elif (
#             data_frame.columns == np.array(range(len(data_frame.columns)))
#         ).all():
#             data_frame.index = data_frame.columns
#         else:
#             raise ValueError("Either index or columns must be a range of integers")

#     formatted_data_frames = []

#     for column in data_frame.columns:
#         column_data_frame = data_frame[column]
#         y_label = column_data_frame.name
#         column_data_frame = pd.DataFrame(column_data_frame)
#         column_data_frame["x"] = column_data_frame.index
#         column_data_frame["y"] = y_label
#         column_data_frame = column_data_frame.reset_index().drop(
#             columns=["index"]
#         )
#         column_data_frame = column_data_frame.rename(columns={y_label: "z"})
#         column_data_frame = scitex.pd.mv(column_data_frame, "z", -1)
#         formatted_data_frames.append(column_data_frame)

#     return pd.concat(formatted_data_frames, ignore_index=True)
