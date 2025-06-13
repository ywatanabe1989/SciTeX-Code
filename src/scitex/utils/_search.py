#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 13:01:38 (ywatanabe)"
# File: ./scitex_repo/src/scitex/utils/_search.py

import numpy as np
import re
from collections import abc

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import xarray as xr
except ImportError:
    xr = None

try:
    from natsort import natsorted
except ImportError:
    # Fallback to regular sorted if natsort not available
    def natsorted(iterable):
        return sorted(iterable)


def search(
    patterns, strings, only_perfect_match=False, as_bool=False, ensure_one=False
):
    """Search for patterns in strings using regular expressions.

    Parameters
    ----------
    patterns : str or list of str
        The pattern(s) to search for. Can be a single string or a list of strings.
    strings : str or list of str
        The string(s) to search in. Can be a single string or a list of strings.
    only_perfect_match : bool, optional
        If True, only exact matches are considered (default is False).
    as_bool : bool, optional
        If True, return a boolean array instead of indices (default is False).
    ensure_one : bool, optional
        If True, ensures only one match is found (default is False).

    Returns
    -------
    tuple
        A tuple containing two elements:
        - If as_bool is False: (list of int, list of str)
          The first element is a list of indices where matches were found.
          The second element is a list of matched strings.
        - If as_bool is True: (numpy.ndarray of bool, list of str)
          The first element is a boolean array indicating matches.
          The second element is a list of matched strings.

    Example
    -------
    >>> patterns = ['orange', 'banana']
    >>> strings = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
    >>> search(patterns, strings)
    ([1, 4, 5], ['orange', 'banana', 'orange_juice'])

    >>> patterns = 'orange'
    >>> strings = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
    >>> search(patterns, strings)
    ([1, 5], ['orange', 'orange_juice'])
    """

    def to_list(string_or_pattern):
        # Check for numpy arrays first
        if isinstance(string_or_pattern, np.ndarray):
            return string_or_pattern.tolist()
        
        # Check for pandas types if pandas is available
        if pd is not None:
            if isinstance(string_or_pattern, (pd.Series, pd.Index)):
                return string_or_pattern.tolist()
        
        # Check for xarray types if xarray is available
        if xr is not None:
            if isinstance(string_or_pattern, xr.DataArray):
                return string_or_pattern.tolist()
        
        # Check for other iterables
        if isinstance(string_or_pattern, abc.KeysView):
            return list(string_or_pattern)
        elif not isinstance(string_or_pattern, (list, tuple)):
            return [string_or_pattern]
        return string_or_pattern

    patterns = to_list(patterns)
    strings = to_list(strings)

    indices_matched = []
    for pattern in patterns:
        for index_str, string in enumerate(strings):
            if only_perfect_match:
                if pattern == string:
                    indices_matched.append(index_str)
            else:
                if re.search(pattern, string):
                    indices_matched.append(index_str)

    indices_matched = natsorted(indices_matched)
    keys_matched = list(np.array(strings)[indices_matched])

    if ensure_one:
        assert (
            len(indices_matched) == 1
        ), "Expected exactly one match, but found {}".format(len(indices_matched))

    if as_bool:
        bool_matched = np.zeros(len(strings), dtype=bool)
        bool_matched[np.unique(indices_matched)] = True
        return bool_matched, keys_matched
    else:
        return indices_matched, keys_matched


# EOF
