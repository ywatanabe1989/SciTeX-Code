#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 17:44:32 (ywatanabe)"
# File: ./scitex_repo/src/scitex/reproduce/_gen_timestamp.py

from datetime import datetime as _datetime


def gen_timestamp():
    """Generate a timestamp string for file naming.

    Returns a timestamp in the format YYYY-MMDD-HHMM, suitable for
    creating unique filenames or version identifiers.

    Returns
    -------
    str
        Timestamp string in format "YYYY-MMDD-HHMM"

    Examples
    --------
    >>> timestamp = gen_timestamp()
    >>> print(timestamp)
    '2025-0531-1230'

    >>> filename = f"experiment_{gen_timestamp()}.csv"
    >>> print(filename)
    'experiment_2025-0531-1230.csv'
    """
    return _datetime.now().strftime("%Y-%m%d-%H%M")


timestamp = gen_timestamp

# EOF
