#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 04:04:31 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_squeeze_space.py

import re


def squeeze_spaces(string, pattern=" +", repl=" "):
    """Replace multiple occurrences of a pattern in a string with a single replacement.

    Parameters
    ----------
    string : str
        The input string to be processed.
    pattern : str, optional
        The regular expression pattern to match (default is " +", which matches one or more spaces).
    repl : str or callable, optional
        The replacement string or function (default is " ", a single space).

    Returns
    -------
    str
        The processed string with pattern occurrences replaced.

    Example
    -------
    >>> squeeze_spaces("Hello   world")
    'Hello world'
    >>> squeeze_spaces("a---b--c-d", pattern="-+", repl="-")
    'a-b-c-d'
    """
    return re.sub(pattern, repl, string)


# EOF
