#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-07-06 07:16:38 (ywatanabe)"
# ./src/scitex/gen/_symlog.py

import numpy as np


def symlog(x, linthresh=1.0):
    """
    Apply a symmetric log transformation to the input data.

    Parameters
    ----------
    x : array-like
        Input data to be transformed.
    linthresh : float, optional
        Range within which the transformation is linear. Defaults to 1.0.

    Returns
    -------
    array-like
        Symmetrically transformed data.
    """
    sign_x = np.sign(x)
    abs_x = np.abs(x)
    return sign_x * (np.log1p(abs_x / linthresh))
