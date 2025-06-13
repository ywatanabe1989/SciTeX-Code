#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 04:00:36 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_color_text.py


def color_text(text, c="green"):
    """Apply ANSI color codes to text.

    Parameters
    ----------
    text : str
        The text to be colored.
    c : str, optional
        The color to apply. Available colors are 'red', 'green', 'yellow',
        'blue', 'magenta', 'cyan', 'white', and 'grey' (default is "green").

    Returns
    -------
    str
        The input text with ANSI color codes applied.

    Example
    -------
    >>> print(color_text("Hello, World!", "blue"))
    # This will print "Hello, World!" in blue text
    """
    ANSI_COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "grey": "\033[90m",
        "gray": "\033[90m",
        "reset": "\033[0m",
    }
    ANSI_COLORS["tra"] = ANSI_COLORS["white"]
    ANSI_COLORS["val"] = ANSI_COLORS["green"]
    ANSI_COLORS["tes"] = ANSI_COLORS["red"]

    start_code = ANSI_COLORS.get(c, ANSI_COLORS["reset"])
    end_code = ANSI_COLORS["reset"]
    return f"{start_code}{text}{end_code}"


ct = color_text


# EOF
