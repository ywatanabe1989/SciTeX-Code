#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 23:40:22 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_to_odd.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_to_odd.py"


def to_odd(n):
    """Convert a number to the nearest odd number less than or equal to itself.

    Parameters
    ----------
    n : int or float
        The input number to be converted.

    Returns
    -------
    int
        The nearest odd number less than or equal to the input.

    Example
    -------
    >>> to_odd(6)
    5
    >>> to_odd(7)
    7
    >>> to_odd(5.8)
    5
    """
    return int(n) - ((int(n) + 1) % 2)


# EOF
