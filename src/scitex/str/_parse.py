#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-16 10:14:44 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/str/_parse.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/str/_parse.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re
from typing import Dict, Union

from ..dict._DotDict import DotDict as _DotDict


def parse(
    string_or_fstring: str, fstring_or_string: str
) -> Union[Dict[str, Union[str, int]], str]:
    """
    Bidirectional parser that attempts parsing in both directions.

    Parameters
    ----------
    string_or_fstring : str
        Either the input string to parse or the pattern
    fstring_or_string : str
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
    #     parsed = _parse(string_or_fstring, fstring_or_string)
    #     if parsed:
    #         return parsed
    # except Exception as e:
    #     print(e)

    # try:
    #     parsed = _parse(fstring_or_string, string_or_fstring)
    #     if parsed:
    #         return parsed
    # except Exception as e:
    #     print(e)
    errors = []

    # Try first direction
    try:
        result = _parse(string_or_fstring, fstring_or_string)
        if result:
            return result
    except ValueError as e:
        errors.append(str(e))
        # logging.warning(f"First attempt failed: {e}")

    # Try reverse direction
    try:
        result = _parse(fstring_or_string, string_or_fstring)
        if result:
            return result
    except ValueError as e:
        errors.append(str(e))
        # logging.warning(f"Second attempt failed: {e}")

    raise ValueError(
        f"Parsing failed in both directions: {' | '.join(errors)}"
    )


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
    """
    # Clean up inputs
    string = string.replace("/./", "/")
    expression = expression.strip()
    if expression.startswith('f"') and expression.endswith('"'):
        expression = expression[2:-1]
    elif expression.startswith('"') and expression.endswith('"'):
        expression = expression[1:-1]
    elif expression.startswith("'") and expression.endswith("'"):
        expression = expression[1:-1]

    # Remove format specifiers from placeholders
    expression_clean = re.sub(r"{(\w+):[^}]+}", r"{\1}", expression)

    # Extract placeholder names
    placeholders = re.findall(r"{(\w+)}", expression_clean)

    # Create regex pattern
    pattern = re.sub(r"{(\w+)}", r"([^/]+)", expression_clean)

    match = re.match(pattern, string)

    if not match:
        raise ValueError(
            f"String format does not match expression: {string} vs {expression}"
        )

    groups = match.groups()
    result = {}

    for placeholder, value in zip(placeholders, groups):
        if placeholder in result and result[placeholder] != value:
            raise ValueError(
                f"Inconsistent values for placeholder '{placeholder}'"
            )

        # Try to convert to int if it looks like a number
        if value.lstrip("-").isdigit():
            result[placeholder] = int(value)
        else:
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
