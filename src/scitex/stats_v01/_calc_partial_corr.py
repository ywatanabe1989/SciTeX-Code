#!/usr/bin/env python3

import numpy as np


def calc_partial_corr(x, y, z):
    """remove the influence of the variable z from the correlation between x and y."""

    x = np.array(x).astype(np.float128)
    y = np.array(y).astype(np.float128)
    z = np.array(z).astype(np.float128)

    r_xy = np.corrcoef(x, y)[0, 1]
    r_xz = np.corrcoef(x, z)[0, 1]
    r_yz = np.corrcoef(y, z)[0, 1]
    r_xy_z = (r_xy - r_xz * r_yz) / (np.sqrt(1 - r_xz**2) * np.sqrt(1 - r_yz**2))
    return float(r_xy_z)
