#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 00:53:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/color/_vizualize_colors.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/color/_vizualize_colors.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import numpy as np


def vizualize_colors(colors):

    def gen_rand_sample(size=100):
        x = np.linspace(-1, 1, size)
        y = np.random.normal(size=size)
        s = np.random.randn(size)
        return x, y, s

    from .. import subplots as scitex_plt_subplots

    fig, ax = scitex_plt_subplots()

    for ii, (color_str, rgba) in enumerate(colors.items()):
        xx, yy, ss = gen_rand_sample()

        # # Box color plot
        # ax.plot_rectangle(
        #     xx=ii, yy=0, width=1, height=1, color=rgba, label=color_str
        # )

        # Line plot
        ax.plot_shaded_line(xx, yy - ss, yy, yy + ss, color=rgba, label=color_str)

        # # Scatter plot
        # axes[2].scatter(xx, yy, color=rgba, label=color_str)

        # # KDE plot
        # axes[3].plot_kde(yy, color=rgba, label=color_str)

    # for ax in axes.flat:
    #     # ax.axis("off")
    #     ax.legend()

    ax.legend()
    # plt.tight_layout()
    # plt.show()
    return fig, ax


# EOF
