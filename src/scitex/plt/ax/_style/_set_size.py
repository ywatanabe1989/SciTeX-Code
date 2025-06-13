#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2022-12-09 13:38:11 (ywatanabe)"


def set_size(ax, w, h):
    """w, h: width, height in inches"""
    # if not ax: ax=plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w) / (r - l)
    figh = float(h) / (t - b)
    ax.figure.set_size_inches(figw, figh)
    return ax
