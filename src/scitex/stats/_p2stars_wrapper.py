#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-30 auto-created"
# File: ./src/scitex/stats/_p2stars_wrapper.py

"""
Wrapper for p2stars to handle array inputs and match test expectations
"""

import numpy as np
from typing import Union, List


def p2stars(
    input_data: Union[float, np.ndarray, List],
    thresholds: List[float] = None,
    symbols: List[str] = None,
) -> Union[str, List[str]]:
    """
    Wrapper for p2stars that handles array inputs and returns 'ns' for non-significant.

    Parameters
    ----------
    input_data : float, np.ndarray, or List
        P-value(s) to convert
    thresholds : List[float], optional
        Custom significance thresholds (default: [0.001, 0.01, 0.05])
    symbols : List[str], optional
        Custom symbols for each threshold (default: ['***', '**', '*'])
    """
    from ._p2stars import p2stars as _p2stars_impl

    # Handle custom thresholds/symbols
    if thresholds is not None and symbols is not None:

        def custom_p2stars(p):
            try:
                p_float = float(p)
                for threshold, symbol in zip(thresholds, symbols):
                    if p_float <= threshold:
                        return symbol
                return "ns"
            except (ValueError, TypeError):
                return "NA"

        if isinstance(input_data, (np.ndarray, list)):
            return [custom_p2stars(p) for p in input_data]
        else:
            return custom_p2stars(input_data)

    # Default behavior
    if isinstance(input_data, (np.ndarray, list)):
        return [_p2stars_impl(p, ns=True) for p in input_data]
    else:
        # Single value - use ns=True to return 'ns' instead of empty string
        return _p2stars_impl(input_data, ns=True)
