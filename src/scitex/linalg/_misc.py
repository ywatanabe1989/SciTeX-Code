#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2023-03-17 21:30:11 (ywatanabe)"

import numpy as np
import sympy
from scipy.linalg import norm


def cosine(v1, v2):
    if np.isnan(v1).any():
        return np.nan
    if np.isnan(v2).any():
        return np.nan
    return np.dot(v1, v2) / (norm(v1) * norm(v2))


def nannorm(v, axis=-1):
    if np.isnan(v).any():
        return np.nan
    else:
        return norm(v, axis=axis)


def rebase_a_vec(v, v_base):
    def production_vector(v1, v0):
        """
        production_vector(np.array([3,4]), np.array([10,0])) # np.array([3, 0])
        """
        return norm(v1) * cosine(v1, v0) * v0 / norm(v0)

    if np.isnan(v).any():
        return np.nan
    if np.isnan(v_base).any():
        return np.nan
    v_prod = production_vector(v, v_base)
    sign = np.sign(cosine(v, v_base))
    return sign * norm(v_prod)


def three_line_lengths_to_coords(aa, bb, cc):
    """
    O, A, B = three_line_lengths_to_coords(2, np.sqrt(3), 1)
    print(O, A, B)
    """

    # Definition
    a1 = sympy.Symbol("a1")
    b1 = sympy.Symbol("b1")
    b2 = sympy.Symbol("b2")

    a1 = aa
    # b1 = bb

    # Calculates
    cos = (aa**2 + bb**2 - cc**2) / (2 * aa * bb)
    sin = np.sqrt(1 - cos**2)
    S1 = 1 / 2 * aa * bb * sin
    S2 = 1 / 2 * aa * b2

    # Solves
    b2 = sympy.solve(S1 - S2)[0]
    b1 = bb * cos

    # tan1 = b2 / b1
    # tan2 = sin/cos

    # b1 = sympy.solve(tan1-tan2)[0]
    O = (0, 0, 0)
    A = (a1, 0, 0)
    B = (b1, b2, 0)

    return O, A, B
