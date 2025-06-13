#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 17:01:23 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_printc.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/str/_printc.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 03:47:51 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_printc.py

from ._color_text import color_text
from pprint import pprint as _pprint


def printc(message, c="blue", char="-", n=40):
    """Print a message surrounded by a character border.

    This function prints a given message surrounded by a border made of
    a specified character. The border can be colored if desired.

    Parameters
    ----------
    message : str
        The message to be printed inside the border.
    char : str, optional
        The character used to create the border (default is "-").
    n : int, optional
        The width of the border (default is 40).
    c : str, optional
        The color of the border. Can be 'red', 'green', 'yellow', 'blue',
        'magenta', 'cyan', 'white', or 'grey' (default is None, which means no color).

    Returns
    -------
    None

    Example
    -------
    >>> print_block("Hello, World!", char="*", n=20, c="blue")
    ********************
    * Hello, World!    *
    ********************

    Note: The actual output will be in green color.
    """
    border = char * n
    text = f"\n{border}\n{message}\n{border}\n"
    if c is not None:
        text = color_text(text, c)

    print(text)


# EOF
