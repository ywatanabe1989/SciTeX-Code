#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-29 12:02:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_set_n_ticks.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/ax/_set_n_ticks.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib


def set_n_ticks(
    ax,
    n_xticks=4,
    n_yticks=4,
):
    """
    Example:
        ax = set_n_ticks(ax)
    """

    if n_xticks is not None:
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(n_xticks))

    if n_yticks is not None:
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(n_yticks))

    # Force the figure to redraw to reflect changes
    ax.figure.canvas.draw()

    return ax


# EOF
