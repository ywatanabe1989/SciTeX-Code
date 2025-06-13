#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 10:09:35 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/utils/_calc_bacc_from_conf_mat.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/utils/_calc_bacc_from_conf_mat.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np

from ...context import suppress_output


def calc_bacc_from_conf_mat(confusion_matrix: np.ndarray, n_round=3) -> float:
    """Calculates balanced accuracy from confusion matrix.

    Parameters
    ----------
    confusion_matrix : np.ndarray
        Confusion matrix array

    Returns
    -------
    float
        Balanced accuracy score

    Example
    -------
    >>> cm = np.array([[10, 2, 0], [1, 15, 3], [0, 2, 20]])
    >>> bacc = calc_bacc_from_conf_mat(cm, n_round=3)
    >>> print(f"Balanced Accuracy: bacc")
    Balanced Accuracy: 0.889
    """
    with suppress_output():
        try:
            per_class = np.diag(confusion_matrix) / np.nansum(confusion_matrix, axis=1)
            bacc = np.nanmean(per_class)
        except:
            bacc = np.nan
        return round(bacc, n_round)


# EOF
