#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-27 13:24:32 (ywatanabe)"
# /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/plt/ax/_rotate_labels.py

"""This script does XYZ."""

"""Imports"""
import numpy as np


def rotate_labels(ax, x=45, y=45, x_ha=None, y_ha=None, x_va=None, y_va=None, 
                 auto_adjust=True, scientific_convention=True):
    """
    Rotate x and y axis labels of a matplotlib Axes object with automatic positioning.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    x : float, optional
        Rotation angle for x-axis labels in degrees. Default is 45.
    y : float, optional
        Rotation angle for y-axis labels in degrees. Default is 45.
    x_ha : str, optional
        Horizontal alignment for x-axis labels. If None, automatically determined.
    y_ha : str, optional
        Horizontal alignment for y-axis labels. If None, automatically determined.
    x_va : str, optional
        Vertical alignment for x-axis labels. If None, automatically determined.
    y_va : str, optional
        Vertical alignment for y-axis labels. If None, automatically determined.
    auto_adjust : bool, optional
        Whether to automatically adjust alignment based on rotation angle. Default is True.
    scientific_convention : bool, optional
        Whether to follow scientific plotting conventions. Default is True.

    Returns
    -------
    matplotlib.axes.Axes
        The modified Axes object.

    Example
    -------
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    rotate_labels(ax)
    plt.show()
    
    Notes
    -----
    Scientific conventions for label rotation:
    - X-axis labels: For angles 0-90°, use 'right' alignment; for 90-180°, use 'left'
    - Y-axis labels: For angles 0-90°, use 'center' alignment; adjust vertical as needed
    - Optimal readability maintained through automatic positioning
    """
    # Get current tick positions
    xticks = ax.get_xticks()
    yticks = ax.get_yticks()

    # Set ticks explicitly
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    # Auto-adjust alignment based on rotation angle and scientific conventions
    if auto_adjust:
        x_ha, x_va = _get_optimal_alignment('x', x, x_ha, x_va, scientific_convention)
        y_ha, y_va = _get_optimal_alignment('y', y, y_ha, y_va, scientific_convention)
    
    # Apply defaults if not auto-adjusting
    if x_ha is None:
        x_ha = "center"
    if y_ha is None:
        y_ha = "center"
    if x_va is None:
        x_va = "center"
    if y_va is None:
        y_va = "center"

    # Set labels with rotation and proper alignment
    ax.set_xticklabels(ax.get_xticklabels(), rotation=x, ha=x_ha, va=x_va)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=y, ha=y_ha, va=y_va)
    
    # Auto-adjust subplot parameters for better layout if needed
    if auto_adjust and scientific_convention:
        _adjust_subplot_params(ax, x, y)
    
    return ax


def _get_optimal_alignment(axis, angle, ha, va, scientific_convention):
    """
    Determine optimal alignment based on rotation angle and scientific conventions.
    
    Parameters
    ----------
    axis : str
        'x' or 'y' axis
    angle : float
        Rotation angle in degrees
    ha : str or None
        Current horizontal alignment
    va : str or None  
        Current vertical alignment
    scientific_convention : bool
        Whether to follow scientific conventions
        
    Returns
    -------
    tuple
        (horizontal_alignment, vertical_alignment)
    """
    # Normalize angle to 0-360 range
    angle = angle % 360
    
    if axis == 'x':
        if scientific_convention:
            # Scientific convention for x-axis labels
            if 0 <= angle <= 30:
                ha = ha or 'center'
                va = va or 'top'
            elif 30 < angle <= 60:
                ha = ha or 'right'
                va = va or 'top'
            elif 60 < angle <= 120:
                ha = ha or 'right'
                va = va or 'center'
            elif 120 < angle <= 150:
                ha = ha or 'right'
                va = va or 'bottom'
            elif 150 < angle <= 210:
                ha = ha or 'center'
                va = va or 'bottom'
            elif 210 < angle <= 240:
                ha = ha or 'left'
                va = va or 'bottom'
            elif 240 < angle <= 300:
                ha = ha or 'left'
                va = va or 'center'
            else:  # 300-360
                ha = ha or 'left'
                va = va or 'top'
        else:
            ha = ha or 'center'
            va = va or 'top'
            
    else:  # y-axis
        if scientific_convention:
            # Scientific convention for y-axis labels
            if 0 <= angle <= 30:
                ha = ha or 'right'
                va = va or 'center'
            elif 30 < angle <= 60:
                ha = ha or 'right'
                va = va or 'bottom'
            elif 60 < angle <= 120:
                ha = ha or 'center'
                va = va or 'bottom'
            elif 120 < angle <= 150:
                ha = ha or 'left'
                va = va or 'bottom'
            elif 150 < angle <= 210:
                ha = ha or 'left'
                va = va or 'center'
            elif 210 < angle <= 240:
                ha = ha or 'left'
                va = va or 'top'
            elif 240 < angle <= 300:
                ha = ha or 'center'
                va = va or 'top'
            else:  # 300-360
                ha = ha or 'right'
                va = va or 'top'
        else:
            ha = ha or 'center'
            va = va or 'center'
    
    return ha, va


def _adjust_subplot_params(ax, x_angle, y_angle):
    """
    Automatically adjust subplot parameters to accommodate rotated labels.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object
    x_angle : float
        X-axis rotation angle
    y_angle : float
        Y-axis rotation angle
    """
    fig = ax.get_figure()
    
    # Calculate required margins based on rotation angles
    x_margin_factor = abs(np.sin(np.radians(x_angle))) * 0.1
    y_margin_factor = abs(np.sin(np.radians(y_angle))) * 0.15
    
    # Get current subplot parameters
    try:
        subplotpars = fig.subplotpars
        current_bottom = subplotpars.bottom
        current_left = subplotpars.left
        
        # Adjust margins if they need to be increased
        new_bottom = max(current_bottom, 0.1 + x_margin_factor)
        new_left = max(current_left, 0.1 + y_margin_factor)
        
        # Only adjust if we're increasing the margins significantly
        if new_bottom > current_bottom + 0.05 or new_left > current_left + 0.05:
            fig.subplots_adjust(bottom=new_bottom, left=new_left)
    except Exception:
        # Skip adjustment if there are issues
        pass
