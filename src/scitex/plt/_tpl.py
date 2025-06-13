#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-31 11:58:28 (ywatanabe)"

import numpy as np
import termplotlib as tpl


def termplot(*args):
    """
    Plots given y values against x using termplotlib, or plots a single y array against its indices if x is not provided.

    Parameters:
    - *args: Accepts either one argument (y values) or two arguments (x and y values).

    Returns:
    None. Displays the plot in the terminal.
    """
    if len(args) == 1:
        y = args[0]  # [REVISED]
        x = np.arange(len(y))

    if len(args) == 2:
        x, y = args

    fig = tpl.figure()
    fig.plot(x, y)
    fig.show()
