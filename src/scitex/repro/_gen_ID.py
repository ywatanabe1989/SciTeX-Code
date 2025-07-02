#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 17:53:38 (ywatanabe)"
# File: ./scitex_repo/src/scitex/repro/_gen_ID.py

import random as _random
import string as _string
from datetime import datetime as _datetime


def gen_id(time_format="%YY-%mM-%dD-%Hh%Mm%Ss", N=8):
    """Generate a unique identifier with timestamp and random characters.

    Creates a unique ID by combining a formatted timestamp with random
    alphanumeric characters. Useful for creating unique experiment IDs,
    run identifiers, or temporary file names.

    Parameters
    ----------
    time_format : str, optional
        Format string for timestamp portion. Default is "%YY-%mM-%dD-%Hh%Mm%Ss"
        which produces "2025Y-05M-31D-12h30m45s" format.
    N : int, optional
        Number of random characters to append. Default is 8.

    Returns
    -------
    str
        Unique identifier in format "{timestamp}_{random_chars}"

    Examples
    --------
    >>> id1 = gen_id()
    >>> print(id1)
    '2025Y-05M-31D-12h30m45s_a3Bc9xY2'

    >>> id2 = gen_id(time_format="%Y%m%d", N=4)
    >>> print(id2)
    '20250531_xY9a'

    >>> # For experiment tracking
    >>> exp_id = gen_id()
    >>> save_path = f"results/experiment_{exp_id}.pkl"
    """
    now_str = _datetime.now().strftime(time_format)
    rand_str = "".join(
        [_random.choice(_string.ascii_letters + _string.digits) for i in range(N)]
    )
    return now_str + "_" + rand_str


# Backward compatibility
gen_ID = gen_id  # Deprecated: use gen_id instead

# EOF
