#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 18:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_export_as_csv_formatters/_format_imshow.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pandas as pd

def _format_imshow(id, tracked_dict, kwargs):
    """Format data from an imshow call."""

    if tracked_dict.get("image_df") is not None:
        return tracked_dict.get("image_df")

    # # Placeholder implementation
    # # Imshow displays an image (2D array)
    # if len(args) >= 1:
    #     img = args[0]

    #     # Convert 2D image to long format
    #     if isinstance(img, np.ndarray) and img.ndim == 2:
    #         rows, cols = img.shape
    #         row_indices, col_indices = np.meshgrid(
    #             range(rows), range(cols), indexing="ij"
    #         )

    #         df = pd.DataFrame(
    #             {
    #                 f"{id}_imshow_row": row_indices.flatten(),
    #                 f"{id}_imshow_col": col_indices.flatten(),
    #                 f"{id}_imshow_value": img.flatten(),
    #             }
    #         )
    #         return df

    #     # Handle RGB/RGBA images
    #     elif isinstance(img, np.ndarray) and img.ndim == 3:
    #         rows, cols, channels = img.shape
    #         row_indices, col_indices = np.meshgrid(
    #             range(rows), range(cols), indexing="ij"
    #         )

    #         data = {
    #             f"{id}_imshow_row": row_indices.flatten(),
    #             f"{id}_imshow_col": col_indices.flatten(),
    #         }

    #         # Add channel data
    #         for c in range(channels):
    #             data[f"{id}_imshow_channel{c}"] = img[:, :, c].flatten()

    #         return pd.DataFrame(data)
    # return pd.DataFrame()