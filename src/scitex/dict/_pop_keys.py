#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 12:40:04 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dict/_pop_keys.py

import numpy as np


def pop_keys(keys_list, keys_to_pop):
    """Remove specified keys from a list of keys.

    Parameters
    ----------
    keys_list : list
        The original list of keys.
    keys_to_pop : list
        The list of keys to remove from keys_list.

    Returns
    -------
    list
        A new list with the specified keys removed.

    Example
    -------
    >>> keys_list = ['a', 'b', 'c', 'd', 'e', 'bde']
    >>> keys_to_pop = ['b', 'd']
    >>> pop_keys(keys_list, keys_to_pop)
    ['a', 'c', 'e', 'bde']
    """
    indi_to_remain = [k not in keys_to_pop for k in keys_list]
    keys_remainded_list = list(np.array(keys_list)[list(indi_to_remain)])
    return keys_remainded_list


# EOF
