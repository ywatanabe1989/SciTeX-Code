#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-16 12:30:15 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_plotly.py

import plotly


def _save_plotly_html(obj, spath):
    """
    Save a Plotly figure as an HTML file.
    
    Parameters
    ----------
    obj : plotly.graph_objs.Figure
        The Plotly figure to save.
    spath : str
        Path where the HTML file will be saved.
        
    Returns
    -------
    None
    """
    if isinstance(obj, plotly.graph_objs.Figure):
        obj.write_html(file=spath)
    else:
        raise TypeError("Object must be a plotly.graph_objs.Figure")