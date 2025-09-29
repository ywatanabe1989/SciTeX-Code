#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 11:05:00 (ywatanabe)"
# File: ./src/scitex/str/_factor_out_digits.py

"""
Functionality:
    Factor out common powers of 10 from numerical data for cleaner axis labels
Input:
    Numerical data (list, array, or individual numbers)
Output:
    Factored values and the common factor for display
Prerequisites:
    numpy
"""

import numpy as np
from typing import Union, List, Tuple, Optional


def factor_out_digits(
    values: Union[List, np.ndarray, float, int],
    precision: int = 2,
    min_factor_power: int = 3,
    return_latex: bool = True,
    return_unicode: bool = False
) -> Tuple[Union[List, np.ndarray, float], str]:
    """
    Factor out common powers of 10 from numerical values for cleaner scientific notation.
    
    Parameters
    ----------
    values : Union[List, np.ndarray, float, int]
        Numerical values to factor
    precision : int, optional
        Number of decimal places in factored values, by default 2
    min_factor_power : int, optional
        Minimum power of 10 to factor out, by default 3
    return_latex : bool, optional
        Return factor string in LaTeX format, by default True
    return_unicode : bool, optional
        Return factor string with Unicode superscripts, by default False
        
    Returns
    -------
    Tuple[Union[List, np.ndarray, float], str]
        Tuple of (factored_values, factor_string)
        
    Examples
    --------
    >>> factor_out_digits([1000, 2000, 3000])
    ([1.0, 2.0, 3.0], '$\\times 10^{3}$')
    
    >>> factor_out_digits([0.001, 0.002, 0.003])
    ([1.0, 2.0, 3.0], '$\\times 10^{-3}$')
    
    >>> factor_out_digits([1.5e6, 2.3e6, 4.1e6])
    ([1.5, 2.3, 4.1], '$\\times 10^{6}$')
    """
    # Convert to numpy array for easier processing
    if np.isscalar(values):
        values_array = np.array([values])
        is_scalar = True
    else:
        values_array = np.array(values)
        is_scalar = False
    
    # Remove zeros and handle special cases
    non_zero_values = values_array[values_array != 0]
    if len(non_zero_values) == 0:
        return values, ""
    
    # Find the common order of magnitude
    log_values = np.log10(np.abs(non_zero_values))
    common_power = int(np.floor(np.mean(log_values)))
    
    # Only factor out if the power is significant enough
    if abs(common_power) < min_factor_power:
        return values, ""
    
    # Calculate factored values
    factor = 10 ** common_power
    factored_values = values_array / factor
    
    # Round to specified precision
    factored_values = np.round(factored_values, precision)
    
    # Generate factor string
    factor_string = _format_factor_string(common_power, return_latex, return_unicode)
    
    # Return in original format
    if is_scalar:
        return float(factored_values[0]), factor_string
    else:
        if isinstance(values, list):
            return factored_values.tolist(), factor_string
        else:
            return factored_values, factor_string


def auto_factor_axis(
    ax, 
    axis: str = 'both',
    precision: int = 2,
    min_factor_power: int = 3,
    return_latex: bool = True,
    return_unicode: bool = False,
    label_offset: Tuple[float, float] = (0.02, 0.98)
) -> None:
    """
    Automatically factor out common powers of 10 from axis tick labels.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to modify
    axis : str, optional
        Which axis to factor ('x', 'y', or 'both'), by default 'both'
    precision : int, optional
        Number of decimal places in factored values, by default 2
    min_factor_power : int, optional
        Minimum power of 10 to factor out, by default 3
    return_latex : bool, optional
        Use LaTeX format for factor string, by default True
    return_unicode : bool, optional
        Use Unicode superscripts for factor string, by default False
    label_offset : Tuple[float, float], optional
        Position for factor label as (x, y) in axes coordinates, by default (0.02, 0.98)
        
    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1000, 2000, 3000], [0.001, 0.002, 0.003])
    >>> auto_factor_axis(ax, axis='both')
    """
    if axis in ['x', 'both']:
        _factor_single_axis(ax, 'x', precision, min_factor_power, 
                           return_latex, return_unicode, label_offset)
    
    if axis in ['y', 'both']:
        _factor_single_axis(ax, 'y', precision, min_factor_power, 
                           return_latex, return_unicode, label_offset)


def _factor_single_axis(
    ax, 
    axis_name: str,
    precision: int,
    min_factor_power: int,
    return_latex: bool,
    return_unicode: bool,
    label_offset: Tuple[float, float]
) -> None:
    """Factor out digits from a single axis."""
    # Get current tick values
    if axis_name == 'x':
        tick_values = ax.get_xticks()
        set_ticks = ax.set_xticks
        set_ticklabels = ax.set_xticklabels
        label_x, label_y = label_offset[0], 0.02
    else:  # y-axis
        tick_values = ax.get_yticks()
        set_ticks = ax.set_yticks
        set_ticklabels = ax.set_yticklabels
        label_x, label_y = 0.02, label_offset[1]
    
    # Factor out common digits
    factored_ticks, factor_string = factor_out_digits(
        tick_values, precision, min_factor_power, return_latex, return_unicode
    )
    
    # Apply factored labels if factor was found
    if factor_string:
        set_ticks(tick_values)
        set_ticklabels([f"{val:.{precision}f}" for val in factored_ticks])
        
        # Add factor label
        ax.text(label_x, label_y, factor_string, 
               transform=ax.transAxes, 
               fontsize='small',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))


def _format_factor_string(
    power: int, 
    latex: bool = True, 
    unicode_sup: bool = False
) -> str:
    """
    Format the factor string for display.
    
    Parameters
    ----------
    power : int
        The power of 10
    latex : bool, optional
        Use LaTeX formatting, by default True
    unicode_sup : bool, optional
        Use Unicode superscripts, by default False
        
    Returns
    -------
    str
        Formatted factor string
    """
    if latex:
        return f"$\\times 10^{{{power}}}$"
    elif unicode_sup:
        # Unicode superscript mapping
        superscripts = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '-': '⁻', '+': '⁺'
        }
        power_str = str(power)
        unicode_power = ''.join(superscripts.get(char, char) for char in power_str)
        return f"×10{unicode_power}"
    else:
        return f"×10^{power}"


def smart_tick_formatter(
    values: Union[List, np.ndarray],
    max_ticks: int = 6,
    factor_out: bool = True,
    precision: int = 2,
    min_factor_power: int = 3,
    return_latex: bool = True
) -> Tuple[Union[List, np.ndarray], List[str], str]:
    """
    Smart tick formatter that combines nice tick selection with factor-out-digits.
    
    Parameters
    ----------
    values : Union[List, np.ndarray]
        Data values to create ticks for
    max_ticks : int, optional
        Maximum number of ticks, by default 6
    factor_out : bool, optional
        Whether to factor out common powers of 10, by default True
    precision : int, optional
        Number of decimal places, by default 2
    min_factor_power : int, optional
        Minimum power to factor out, by default 3
    return_latex : bool, optional
        Use LaTeX format, by default True
        
    Returns
    -------
    Tuple[Union[List, np.ndarray], List[str], str]
        (tick_positions, tick_labels, factor_string)
        
    Examples
    --------
    >>> smart_tick_formatter([1000, 1500, 2000, 2500, 3000])
    ([1000, 1500, 2000, 2500, 3000], ['1.0', '1.5', '2.0', '2.5', '3.0'], '$\\times 10^{3}$')
    """
    values_array = np.array(values)
    
    # Create nice tick positions
    from matplotlib.ticker import MaxNLocator
    locator = MaxNLocator(nbins=max_ticks, prune='both')
    tick_positions = locator.tick_values(values_array.min(), values_array.max())
    
    # Factor out common digits if requested
    if factor_out:
        factored_ticks, factor_string = factor_out_digits(
            tick_positions, precision, min_factor_power, return_latex
        )
        tick_labels = [f"{val:.{precision}f}".rstrip('0').rstrip('.') 
                      for val in factored_ticks]
    else:
        tick_labels = [f"{val:.{precision}f}".rstrip('0').rstrip('.') 
                      for val in tick_positions]
        factor_string = ""
    
    return tick_positions, tick_labels, factor_string


# EOF