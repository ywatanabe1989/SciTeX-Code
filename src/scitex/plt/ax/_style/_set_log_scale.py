#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 11:10:00 (ywatanabe)"
# File: ./src/scitex/plt/ax/_style/_set_log_scale.py

"""
Functionality:
    Set logarithmic scale with proper minor ticks for scientific plots
Input:
    Matplotlib axes object and scale parameters
Output:
    Axes with properly configured logarithmic scale
Prerequisites:
    matplotlib, numpy
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LogFormatter, NullFormatter
from typing import Union, Optional, List


def set_log_scale(
    ax,
    axis: str = 'both',
    base: Union[int, float] = 10,
    show_minor_ticks: bool = True,
    minor_tick_length: float = 2.0,
    major_tick_length: float = 4.0,
    minor_tick_width: float = 0.5,
    major_tick_width: float = 0.8,
    grid: bool = False,
    minor_grid: bool = False,
    grid_alpha: float = 0.3,
    minor_grid_alpha: float = 0.15,
    format_minor_labels: bool = False,
    scientific_notation: bool = True
) -> object:
    """
    Set logarithmic scale with comprehensive minor tick support.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to modify
    axis : str, optional
        Which axis to set: 'x', 'y', or 'both', by default 'both'
    base : Union[int, float], optional
        Logarithmic base, by default 10
    show_minor_ticks : bool, optional
        Whether to show minor ticks, by default True
    minor_tick_length : float, optional
        Length of minor ticks in points, by default 2.0
    major_tick_length : float, optional
        Length of major ticks in points, by default 4.0
    minor_tick_width : float, optional
        Width of minor ticks in points, by default 0.5
    major_tick_width : float, optional
        Width of major ticks in points, by default 0.8
    grid : bool, optional
        Whether to show major grid lines, by default False
    minor_grid : bool, optional
        Whether to show minor grid lines, by default False
    grid_alpha : float, optional
        Alpha for major grid lines, by default 0.3
    minor_grid_alpha : float, optional
        Alpha for minor grid lines, by default 0.15
    format_minor_labels : bool, optional
        Whether to show labels on minor ticks, by default False
    scientific_notation : bool, optional
        Whether to use scientific notation for labels, by default True
        
    Returns
    -------
    matplotlib.axes.Axes
        The modified axes object
        
    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> ax.semilogy([1, 10, 100, 1000], [1, 2, 3, 4])
    >>> set_log_scale(ax, axis='y', show_minor_ticks=True, grid=True)
    """
    
    if axis in ['x', 'both']:
        _configure_log_axis(ax, 'x', base, show_minor_ticks, 
                           minor_tick_length, major_tick_length,
                           minor_tick_width, major_tick_width,
                           grid, minor_grid, grid_alpha, minor_grid_alpha,
                           format_minor_labels, scientific_notation)
    
    if axis in ['y', 'both']:
        _configure_log_axis(ax, 'y', base, show_minor_ticks,
                           minor_tick_length, major_tick_length, 
                           minor_tick_width, major_tick_width,
                           grid, minor_grid, grid_alpha, minor_grid_alpha,
                           format_minor_labels, scientific_notation)
    
    return ax


def _configure_log_axis(
    ax, axis_name: str, base: Union[int, float], show_minor_ticks: bool,
    minor_tick_length: float, major_tick_length: float,
    minor_tick_width: float, major_tick_width: float,
    grid: bool, minor_grid: bool, grid_alpha: float, minor_grid_alpha: float,
    format_minor_labels: bool, scientific_notation: bool
) -> None:
    """Configure a single axis for logarithmic scale."""
    
    # Set the logarithmic scale
    if axis_name == 'x':
        ax.set_xscale('log', base=base)
        axis_obj = ax.xaxis
        tick_params_kwargs = {'axis': 'x'}
    else:  # y-axis
        ax.set_yscale('log', base=base)
        axis_obj = ax.yaxis
        tick_params_kwargs = {'axis': 'y'}
    
    # Configure major ticks
    major_locator = LogLocator(base=base, numticks=12)
    axis_obj.set_major_locator(major_locator)
    
    # Configure major tick formatting
    if scientific_notation:
        major_formatter = LogFormatter(base=base, labelOnlyBase=False)
    else:
        major_formatter = LogFormatter(base=base, labelOnlyBase=True)
    axis_obj.set_major_formatter(major_formatter)
    
    # Configure minor ticks
    if show_minor_ticks:
        # Create minor tick positions
        minor_locator = LogLocator(base=base, subs='all', numticks=100)
        axis_obj.set_minor_locator(minor_locator)
        
        # Format minor tick labels
        if format_minor_labels:
            minor_formatter = LogFormatter(base=base, labelOnlyBase=False)
        else:
            minor_formatter = NullFormatter()  # No labels on minor ticks
        axis_obj.set_minor_formatter(minor_formatter)
        
        # Set minor tick appearance
        ax.tick_params(
            which='minor',
            length=minor_tick_length,
            width=minor_tick_width,
            **tick_params_kwargs
        )
    
    # Set major tick appearance
    ax.tick_params(
        which='major',
        length=major_tick_length,
        width=major_tick_width,
        **tick_params_kwargs
    )
    
    # Configure grid
    if grid or minor_grid:
        ax.grid(True, which='major', alpha=grid_alpha if grid else 0)
        if minor_grid and show_minor_ticks:
            ax.grid(True, which='minor', alpha=minor_grid_alpha)


def smart_log_limits(
    data: Union[List, np.ndarray],
    axis: str = 'y',
    base: Union[int, float] = 10,
    padding_factor: float = 0.1,
    min_decades: int = 1
) -> tuple:
    """
    Calculate smart logarithmic axis limits based on data.
    
    Parameters
    ----------
    data : Union[List, np.ndarray]
        Data values to calculate limits from
    axis : str, optional
        Axis name for reference, by default 'y'
    base : Union[int, float], optional
        Logarithmic base, by default 10
    padding_factor : float, optional
        Padding as fraction of data range, by default 0.1
    min_decades : int, optional
        Minimum number of decades to show, by default 1
        
    Returns
    -------
    tuple
        (lower_limit, upper_limit)
        
    Examples
    --------
    >>> smart_log_limits([1, 10, 100, 1000])
    (0.1, 10000.0)
    """
    data_array = np.array(data)
    positive_data = data_array[data_array > 0]
    
    if len(positive_data) == 0:
        return 1, base**min_decades
    
    data_min = np.min(positive_data)
    data_max = np.max(positive_data)
    
    # Calculate log range
    log_min = np.log(data_min) / np.log(base)
    log_max = np.log(data_max) / np.log(base)
    log_range = log_max - log_min
    
    # Ensure minimum range
    if log_range < min_decades:
        log_center = (log_min + log_max) / 2
        log_min = log_center - min_decades / 2
        log_max = log_center + min_decades / 2
        log_range = min_decades
    
    # Add padding
    padding = log_range * padding_factor
    log_min_padded = log_min - padding
    log_max_padded = log_max + padding
    
    # Convert back to linear scale
    lower_limit = base ** log_min_padded
    upper_limit = base ** log_max_padded
    
    return lower_limit, upper_limit


def add_log_scale_indicator(
    ax,
    axis: str = 'y',
    base: Union[int, float] = 10,
    position: str = 'auto',
    fontsize: Union[str, int] = 'small',
    color: str = 'gray',
    alpha: float = 0.7
) -> None:
    """
    Add a log scale indicator to the plot.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object
    axis : str, optional
        Which axis has log scale, by default 'y'
    base : Union[int, float], optional
        Logarithmic base, by default 10
    position : str, optional
        Position of indicator: 'auto', 'top-left', 'top-right', 'bottom-left', 'bottom-right', by default 'auto'
    fontsize : Union[str, int], optional
        Font size for indicator, by default 'small'
    color : str, optional
        Color of indicator text, by default 'gray'
    alpha : float, optional
        Alpha transparency, by default 0.7
        
    Examples
    --------
    >>> add_log_scale_indicator(ax, axis='y', base=10)
    """
    # Determine position
    if position == 'auto':
        if axis == 'y':
            position = 'top-left'
        else:
            position = 'bottom-right'
    
    # Position mapping
    positions = {
        'top-left': (0.05, 0.95),
        'top-right': (0.95, 0.95),
        'bottom-left': (0.05, 0.05),
        'bottom-right': (0.95, 0.05)
    }
    
    x_pos, y_pos = positions.get(position, (0.05, 0.95))
    
    # Create indicator text
    if base == 10:
        indicator_text = f"Log₁₀ scale ({axis}-axis)"
    else:
        indicator_text = f"Log_{{{base}}} scale ({axis}-axis)"
    
    # Add text
    ax.text(x_pos, y_pos, indicator_text,
           transform=ax.transAxes,
           fontsize=fontsize,
           color=color,
           alpha=alpha,
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))


# EOF