#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 11:15:00 (ywatanabe)"
# File: ./src/scitex/plt/ax/_style/_show_spines.py

"""
Functionality:
    Show spines for matplotlib axes with intuitive API
Input:
    Matplotlib axes object and spine visibility parameters
Output:
    Axes with specified spines made visible
Prerequisites:
    matplotlib
"""

import matplotlib
from typing import Union, List


def show_spines(
    axis,
    top: bool = True,
    bottom: bool = True,
    left: bool = True,
    right: bool = True,
    ticks: bool = True,
    labels: bool = True,
    restore_defaults: bool = True,
    spine_width: float = None,
    spine_color: str = None
):
    """
    Shows the specified spines of a matplotlib Axes object and optionally restores ticks and labels.

    This function provides the intuitive counterpart to hide_spines. It's especially useful when
    you have spines hidden by default (as in scitex configuration) and want to selectively show them
    for clearer scientific plots or specific visualization needs.

    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The Axes object for which the spines will be shown.
    top : bool, optional
        If True, shows the top spine. Defaults to True.
    bottom : bool, optional
        If True, shows the bottom spine. Defaults to True.
    left : bool, optional
        If True, shows the left spine. Defaults to True.
    right : bool, optional
        If True, shows the right spine. Defaults to True.
    ticks : bool, optional
        If True, restores ticks on the shown spines' axes. Defaults to True.
    labels : bool, optional
        If True, restores labels on the shown spines' axes. Defaults to True.
    restore_defaults : bool, optional
        If True, restores default tick positions and labels. Defaults to True.
    spine_width : float, optional
        Width of the spines to show. If None, uses matplotlib default.
    spine_color : str, optional
        Color of the spines to show. If None, uses matplotlib default.

    Returns
    -------
    matplotlib.axes.Axes
        The modified Axes object with the specified spines shown.

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> # Show only bottom and left spines (classic scientific plot style)
    >>> show_spines(ax, top=False, right=False)
    >>> plt.show()

    >>> # Show all spines with custom styling
    >>> show_spines(ax, spine_width=1.5, spine_color='black')
    >>> plt.show()

    >>> # Show spines but without ticks/labels (for clean overlay plots)
    >>> show_spines(ax, ticks=False, labels=False)
    >>> plt.show()

    Notes
    -----
    This function is designed to work seamlessly with scitex plotting where spines are hidden
    by default. It provides an intuitive API for showing spines without needing to remember
    that hide_spines(top=False, right=False) shows top and right spines.
    """
    # Handle both matplotlib axes and scitex AxisWrapper
    if hasattr(axis, '_axis_mpl'):
        # This is an scitex AxisWrapper, get the underlying matplotlib axis
        axis = axis._axis_mpl
    
    assert isinstance(
        axis, matplotlib.axes._axes.Axes
    ), "First argument must be a matplotlib axis or scitex AxisWrapper"

    # Define which spines to show
    spine_settings = {
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right
    }

    for spine_name, should_show in spine_settings.items():
        # Set spine visibility
        axis.spines[spine_name].set_visible(should_show)
        
        if should_show:
            # Set spine width if specified
            if spine_width is not None:
                axis.spines[spine_name].set_linewidth(spine_width)
            
            # Set spine color if specified
            if spine_color is not None:
                axis.spines[spine_name].set_color(spine_color)

    # Restore ticks if requested
    if ticks and restore_defaults:
        # Determine tick positions based on which spines are shown
        if bottom and not top:
            axis.xaxis.set_ticks_position('bottom')
        elif top and not bottom:
            axis.xaxis.set_ticks_position('top')
        elif bottom and top:
            axis.xaxis.set_ticks_position('both')
        
        if left and not right:
            axis.yaxis.set_ticks_position('left')
        elif right and not left:
            axis.yaxis.set_ticks_position('right')
        elif left and right:
            axis.yaxis.set_ticks_position('both')

    # Restore labels if requested and restore_defaults is True
    if labels and restore_defaults:
        # Only restore if we haven't explicitly hidden them
        # This preserves any custom tick labels that might have been set
        current_xticks = axis.get_xticks()
        current_yticks = axis.get_yticks()
        
        if len(current_xticks) > 0 and (bottom or top):
            # Generate default labels for x-axis
            if not hasattr(axis, '_original_xticklabels'):
                axis.set_xticks(current_xticks)
        
        if len(current_yticks) > 0 and (left or right):
            # Generate default labels for y-axis  
            if not hasattr(axis, '_original_yticklabels'):
                axis.set_yticks(current_yticks)

    return axis


def show_all_spines(
    axis,
    spine_width: float = None,
    spine_color: str = None,
    ticks: bool = True,
    labels: bool = True
):
    """
    Convenience function to show all spines with optional styling.
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The Axes object to modify.
    spine_width : float, optional
        Width of all spines.
    spine_color : str, optional
        Color of all spines.
    ticks : bool, optional
        Whether to show ticks. Defaults to True.
    labels : bool, optional
        Whether to show labels. Defaults to True.
        
    Returns
    -------
    matplotlib.axes.Axes
        The modified Axes object.
        
    Examples
    --------
    >>> show_all_spines(ax, spine_width=1.2, spine_color='gray')
    """
    return show_spines(
        axis,
        top=True, bottom=True, left=True, right=True,
        ticks=ticks, labels=labels,
        spine_width=spine_width, spine_color=spine_color
    )


def show_classic_spines(
    axis,
    spine_width: float = None,
    spine_color: str = None,
    ticks: bool = True,
    labels: bool = True
):
    """
    Show only bottom and left spines (classic scientific plot style).
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The Axes object to modify.
    spine_width : float, optional
        Width of the spines.
    spine_color : str, optional
        Color of the spines.
    ticks : bool, optional
        Whether to show ticks. Defaults to True.
    labels : bool, optional
        Whether to show labels. Defaults to True.
        
    Returns
    -------
    matplotlib.axes.Axes
        The modified Axes object.
        
    Examples
    --------
    >>> show_classic_spines(ax)  # Shows only bottom and left spines
    """
    return show_spines(
        axis,
        top=False, bottom=True, left=True, right=False,
        ticks=ticks, labels=labels,
        spine_width=spine_width, spine_color=spine_color
    )


def show_box_spines(
    axis,
    spine_width: float = None,
    spine_color: str = None,
    ticks: bool = True,
    labels: bool = True
):
    """
    Show all four spines to create a box around the plot.
    
    This is an alias for show_all_spines but with more descriptive naming
    for when you specifically want a boxed appearance.
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The Axes object to modify.
    spine_width : float, optional
        Width of the box spines.
    spine_color : str, optional
        Color of the box spines.
    ticks : bool, optional
        Whether to show ticks. Defaults to True.
    labels : bool, optional
        Whether to show labels. Defaults to True.
        
    Returns
    -------
    matplotlib.axes.Axes
        The modified Axes object.
        
    Examples
    --------
    >>> show_box_spines(ax, spine_width=1.0, spine_color='black')
    """
    return show_all_spines(axis, spine_width, spine_color, ticks, labels)


def toggle_spines(
    axis,
    top: bool = None,
    bottom: bool = None,
    left: bool = None,
    right: bool = None
):
    """
    Toggle the visibility of spines (show if hidden, hide if shown).
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The Axes object to modify.
    top : bool, optional
        If specified, sets top spine visibility. If None, toggles current state.
    bottom : bool, optional
        If specified, sets bottom spine visibility. If None, toggles current state.
    left : bool, optional
        If specified, sets left spine visibility. If None, toggles current state.
    right : bool, optional
        If specified, sets right spine visibility. If None, toggles current state.
        
    Returns
    -------
    matplotlib.axes.Axes
        The modified Axes object.
        
    Examples
    --------
    >>> toggle_spines(ax)  # Toggles all spines
    >>> toggle_spines(ax, top=True, right=True)  # Shows top and right, toggles others
    """
    spine_names = ['top', 'bottom', 'left', 'right']
    spine_params = [top, bottom, left, right]
    
    for spine_name, param in zip(spine_names, spine_params):
        if param is None:
            # Toggle current state
            current_state = axis.spines[spine_name].get_visible()
            axis.spines[spine_name].set_visible(not current_state)
        else:
            # Set specific state
            axis.spines[spine_name].set_visible(param)
    
    return axis


# Convenient aliases for common use cases
def scientific_spines(axis, **kwargs):
    """Alias for show_classic_spines - shows only bottom and left spines."""
    return show_classic_spines(axis, **kwargs)


def clean_spines(axis, **kwargs):
    """Alias for showing no spines - useful for overlay plots or clean visualizations."""
    return show_spines(axis, top=False, bottom=False, left=False, right=False, **kwargs)


# EOF