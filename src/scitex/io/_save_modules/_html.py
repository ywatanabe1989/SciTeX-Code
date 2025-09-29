#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:45:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/io/_save_modules/_html.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/io/_save_modules/_html.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
HTML saving functionality for scitex.io.save
"""

import plotly


def save_html(obj, spath, **kwargs):
    """Handle HTML file saving (primarily for Plotly figures).
    
    Parameters
    ----------
    obj : plotly.graph_objs.Figure or str
        Plotly figure object or HTML string to save
    spath : str
        Path where HTML file will be saved
    **kwargs
        Additional keyword arguments passed to plotly.io.write_html()
        
    Notes
    -----
    - Primarily designed for saving Plotly interactive figures
    - Can also save raw HTML strings
    """
    if hasattr(obj, 'write_html'):
        # Plotly figure object
        obj.write_html(spath, **kwargs)
    elif isinstance(obj, str):
        # Raw HTML string
        with open(spath, 'w') as f:
            f.write(obj)
    else:
        # Try to convert to HTML using plotly
        plotly.io.write_html(obj, spath, **kwargs)


# EOF