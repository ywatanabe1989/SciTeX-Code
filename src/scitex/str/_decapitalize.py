#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 11:25:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_decapitalize.py

"""
Functionality:
    - Converts first character of string to lowercase
Input:
    - String to be processed
Output:
    - Modified string with lowercase first character
Prerequisites:
    - None
"""


def decapitalize(input_string: str) -> str:
    """Converts first character of string to lowercase.

    Example
    -------
    >>> decapitalize("Hello")
    'hello'
    >>> decapitalize("WORLD")
    'wORLD'
    >>> decapitalize("")
    ''

    Parameters
    ----------
    input_string : str
        String to be processed

    Returns
    -------
    str
        Modified string with first character in lowercase

    Raises
    ------
    TypeError
        If input is not a string
    """
    try:
        if not isinstance(input_string, str):
            raise TypeError("Input must be a string")

        if not input_string:
            return input_string

        return input_string[0].lower() + input_string[1:]

    except Exception as error:
        raise ValueError(f"String processing failed: {str(error)}")


# EOF
