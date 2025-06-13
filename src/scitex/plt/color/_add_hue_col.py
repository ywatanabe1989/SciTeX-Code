#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 18:02:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/color/_add_hue_col.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/color/_add_hue_col.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np
import pandas as pd


def add_hue_col(df):
    df["hue"] = 0
    dummy_row = pd.DataFrame(
        columns=df.columns,
        data=np.array([np.nan for _ in df.columns]).reshape(1, -1),
    )
    dummy_row = {}
    for col in df.columns:
        dtype = df[col].dtype
        if dtype is np.dtype(object):
            dummy_row[col] = np.nan
        if dtype is np.dtype(float):
            dummy_row[col] = np.nan
        if dtype is np.dtype(np.int64):
            dummy_row[col] = np.nan
        if dtype is np.dtype(bool):
            dummy_row[col] = None

    dummy_row = pd.DataFrame(pd.Series(dummy_row)).T

    dummy_row["hue"] = 1
    df_added = pd.concat([df, dummy_row], axis=0)
    return df_added


# EOF
