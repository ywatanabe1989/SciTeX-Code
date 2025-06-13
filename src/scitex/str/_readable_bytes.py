#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 04:06:54 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_readable_bytes.py


def readable_bytes(num, suffix="B"):
    """Convert a number of bytes to a human-readable format.

    Parameters
    ----------
    num : int
        The number of bytes to convert.
    suffix : str, optional
        The suffix to append to the unit (default is "B" for bytes).

    Returns
    -------
    str
        A human-readable string representation of the byte size.

    Example
    -------
    >>> readable_bytes(1024)
    '1.0 KiB'
    >>> readable_bytes(1048576)
    '1.0 MiB'
    >>> readable_bytes(1073741824)
    '1.0 GiB'
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, "Yi", suffix)


# EOF
