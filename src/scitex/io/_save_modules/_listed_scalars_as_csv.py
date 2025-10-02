#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 14:53:11 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save_modules/_save_listed_scalars_as_csv.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-11-02 21:26:48 (ywatanabe)"

import numpy as np
import pandas as pd

from .._mv_to_tmp import _mv_to_tmp



def _save_listed_scalars_as_csv(
    listed_scalars,
    spath_csv,
    column_name="_",
    indi_suffix=None,
    round=3,
    overwrite=False,
    verbose=False,
):
    """Puts to df and save it as csv"""

    if overwrite == True:
        _mv_to_tmp(spath_csv, L=2)
    indi_suffix = np.arange(len(listed_scalars)) if indi_suffix is None else indi_suffix
    df = pd.DataFrame(
        {"{}".format(column_name): listed_scalars}, index=indi_suffix
    ).round(round)
    df.to_csv(spath_csv)
    if verbose:
        print("\nSaved to: {}\n".format(spath_csv))

# EOF
