#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-16 16:34:46 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_replace.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/str/_replace.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-16 16:30:25 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_replace.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/str/_replace.py"

from typing import Union, Dict, Optional
from ..dict import DotDict as _DotDict


def replace(
    string: str, replacements: Optional[Union[str, Dict[str, str]]] = None
) -> str:
    """Replace placeholders in the string with corresponding values from replacements.

    This function replaces placeholders in the format {key} within the input string
    with corresponding values from the replacements dictionary. If replacements is
    a string, it replaces the entire input string.

    Parameters
    ----------
    string : str
        The string containing placeholders in the format {key}
    replacements : Optional[Union[str, Dict[str, str]]], optional
        A dictionary containing key-value pairs for replacing placeholders in the string,
        or a single string to replace the entire string

    Returns
    -------
    str
        The input string with placeholders replaced by their corresponding values

    Examples
    --------
    >>> replace("Hello, {name}!", {"name": "World"})
    'Hello, World!'
    >>> replace("Original string", "New string")
    'New string'
    >>> replace("Value: {x}", {"x": "42"})
    'Value: 42'
    >>> template = "Hello, {name}! You are {age} years old."
    >>> replacements = {"name": "Alice", "age": "30"}
    >>> replace(template, replacements)
    'Hello, Alice! You are 30 years old.'
    """
    if not isinstance(string, str):
        raise TypeError("Input 'string' must be a string")

    if isinstance(replacements, str):
        return replacements

    if replacements is None:
        return string

    if not isinstance(replacements, (dict, _DotDict)):
        raise TypeError("replacements must be either a string or a dictionary")

    result = string
    for key, value in replacements.items():
        if value is not None:
            placeholder = "{" + str(key) + "}"
            result = result.replace(placeholder, str(value))

    return result


# EOF

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-16 16:30:25 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/str/_replace.py

# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/str/_replace.py"

# def replace(string, replacements):
#     """Replace placeholders in the string with corresponding values from replacements.

#     This function replaces placeholders in the format {key} within the input string
#     with corresponding values from the replacements dictionary. If replacements is
#     a string, it replaces the entire input string.

#     Parameters
#     ----------
#     string : str
#         The string containing placeholders in the format {key}.
#     replacements : dict or str, optional
#         A dictionary containing key-value pairs for replacing placeholders in the string,
#         or a single string to replace the entire string.

#     Returns
#     -------
#     str
#         The input string with placeholders replaced by their corresponding values.

#     Examples
#     --------
#     >>> replace("Hello, {name}!", {"name": "World"})
#     'Hello, World!'
#     >>> replace("Original string", "New string")
#     'New string'
#     >>> replace("Value: {x}", {"x": 42})
#     'Value: 42'
#     >>> template = "Hello, {name}! You are {age} years old."
#     >>> replacements = {"name": "Alice", "age": "30"}
#     >>> replace(template, replacements)
#     'Hello, Alice! You are 30 years old.'
#     """
#     if isinstance(replacements, str):
#         return replacements

#     if replacements is None:
#         replacements = {}

#     for k, v in replacements.items():
#         if v is not None:
#             try:
#                 string = string.replace("{" + k + "}", v)
#             except Exception as e:
#                 pass
#     return string


#

# EOF
