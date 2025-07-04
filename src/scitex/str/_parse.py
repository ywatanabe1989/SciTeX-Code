#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-16 17:11:15 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_parse.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/str/_parse.py"

import re
from typing import Dict, Union

from ..dict._DotDict import DotDict as _DotDict


def parse(
    input_str_or_pattern: str, pattern_or_input_str: str
) -> Union[Dict[str, Union[str, int]], str]:
    """
    Bidirectional parser that attempts parsing in both directions.

    Parameters
    ----------
    input_str_or_pattern : str
        Either the input string to parse or the pattern
    pattern_or_input_str : str
        Either the pattern to match against or the input string

    Returns
    -------
    Union[Dict[str, Union[str, int]], str]
        Parsed dictionary or formatted string

    Raises
    ------
    ValueError
        If parsing fails in both directions

    Examples
    --------
    >>> # Forward parsing
    >>> parse("./data/Patient_23_002", "./data/Patient_{id}")
    {'id': '23_002'}

    >>> # Reverse parsing
    >>> parse("./data/Patient_{id}", "./data/Patient_23_002")
    {'id': '23_002'}
    """
    # try:
    #     parsed = _parse(input_str_or_pattern, pattern_or_input_str)
    #     if parsed:
    #         return parsed
    # except Exception as e:
    #     print(e)

    # try:
    #     parsed = _parse(pattern_or_input_str, input_str_or_pattern)
    #     if parsed:
    #         return parsed
    # except Exception as e:
    #     print(e)
    errors = []

    # Try first direction
    try:
        result = _parse(input_str_or_pattern, pattern_or_input_str)
        if result:
            return result
    except ValueError as e:
        errors.append(str(e))
        # logging.warning(f"First attempt failed: {e}")

    # Try reverse direction
    try:
        result = _parse(pattern_or_input_str, input_str_or_pattern)
        if result:
            return result
    except ValueError as e:
        errors.append(str(e))
        # logging.warning(f"Second attempt failed: {e}")

    raise ValueError(f"Parsing failed in both directions: {' | '.join(errors)}")


def _parse(string: str, expression: str) -> Dict[str, Union[str, int]]:
    """
    Parse a string based on a given expression pattern.

    Parameters
    ----------
    string : str
        The string to parse
    expression : str
        The expression pattern to match against the string

    Returns
    -------
    Dict[str, Union[str, int]]
        A dictionary containing parsed information

    Raises
    ------
    ValueError
        If the string format does not match the given expression
        If duplicate placeholders have inconsistent values

    Example
    -------
    >>> string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_12_02_00.mat"
    >>> expression = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
    >>> parse_str(string, expression)
    # {'patient_id': '23_002', 'YYYY': 2010, 'MM': 7, 'DD': 31, 'HH': 12, 'mm': 2}

    # Inconsistent version
    >>> string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_99_02_00.mat"
    >>> expression = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
    >>> parse_str(string, expression)
    # ValueError: Inconsistent values for placeholder 'HH'
    """

    # Formatting
    string = string.replace("/./", "/")
    expression = expression.replace('f"', "").replace('"', "")

    placeholders = re.findall(r"{(\w+)}", expression)
    pattern = re.sub(r"{(\w+)}", "([^/]+)", expression)
    match = re.match(pattern, string)

    if not match:
        raise ValueError(
            f"String format does not match expression: {string} vs {expression}"
        )
        # logging.warning(f"String format does not match the given expression. \nString input: {string}\nExpression: {expression}")
        # return {}

    groups = match.groups()
    result = {}

    for placeholder, value in zip(placeholders, groups):
        if placeholder in result and result[placeholder] != value:
            raise ValueError(f"Inconsistent values for placeholder '{placeholder}'")
        result[placeholder] = value

    return _DotDict(result)


if __name__ == "__main__":
    string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_12_02_00.mat"
    expression = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
    results = parse(string, expression)
    print(results)

    # Inconsistent version
    string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_99_99_00.mat"
    expression = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
    results = parse(string, expression)  # this should raise error
    print(results)


# EOF
