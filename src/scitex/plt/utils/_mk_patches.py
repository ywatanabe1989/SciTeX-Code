#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-30 21:18:45 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_mk_patches.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_mk_patches.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.patches as mpatches


def mk_patches(colors, labels):
    """
    colors = ["red", "blue"]
    labels = ["label_1", "label_2"]
    ax.legend(handles=scitex.plt.mk_patches(colors, labels))
    """

    patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors, labels)]
    return patches


# EOF
