#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 17:17:05 (ywatanabe)"
# File: ./scitex_repo/src/scitex/str/_print_debug.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/str/_print_debug.py"

from ._printc import printc


def print_debug():
    """Print a prominent debug mode banner.

    Displays a highly visible yellow banner to indicate that the program
    is running in debug mode. Useful for making debug runs immediately
    distinguishable from production runs.

    The banner consists of multiple lines of exclamation marks with
    "DEBUG MODE" prominently displayed in the center.

    Examples
    --------
    >>> # At the start of debug runs
    >>> if DEBUG:
    ...     print_debug()
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!! DEBUG MODE !!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    >>> # In configuration validation
    >>> if config.debug_mode:
    ...     print_debug()
    ...     print("Debug logging enabled")

    See Also
    --------
    printc : Colored printing function used internally

    Notes
    -----
    The banner is printed in yellow color to ensure high visibility
    in terminal output.
    """
    printc(
        (
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*24} DEBUG MODE {'!'*24}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}\n"
            f"{'!'*60}"
        ),
        c="yellow",
        char="!",
        n=60,
    )


# EOF
