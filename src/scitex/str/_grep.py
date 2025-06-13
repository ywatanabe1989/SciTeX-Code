#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 04:05:41 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_grep.py

import re


def grep(str_list, search_key):
    """Search for a key in a list of strings and return matching items.

    Parameters
    ----------
    str_list : list of str
        The list of strings to search through.
    search_key : str
        The key to search for in the strings.

    Returns
    -------
    list
        A list of strings from str_list that contain the search_key.

    Example
    -------
    >>> grep(['apple', 'banana', 'cherry'], 'a')
    ['apple', 'banana']
    >>> grep(['cat', 'dog', 'elephant'], 'e')
    ['elephant']
    """
    """
    Example:
        str_list = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
        search_key = 'orange'
        print(grep(str_list, search_key))
        # ([1, 5], ['orange', 'orange_juice'])
    """
    matched_keys = []
    indi = []
    for ii, string in enumerate(str_list):
        m = re.search(search_key, string)
        if m is not None:
            matched_keys.append(string)
            indi.append(ii)
    return indi, matched_keys


# EOF
