#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-06-04 06:55:56 (ywatanabe)"
# /home/ywatanabe/proj/scitex/src/scitex/gen/_ci.py


import numpy as np


def ci(xx, axis=None):
    indi = ~np.isnan(xx)
    return 1.96 * (xx[indi]).std(axis=axis) / np.sqrt(indi.sum())
