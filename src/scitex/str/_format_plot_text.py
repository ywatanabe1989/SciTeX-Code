#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 11:08:00 (ywatanabe)"
# File: ./src/scitex/str/_format_plot_text.py

"""
Functionality:
    Format text for scientific plots with proper capitalization and unit handling
    Includes LaTeX fallback mechanisms for robust rendering
Input:
    Text strings with optional units
Output:
    Properly formatted strings for scientific plots with LaTeX fallback
Prerequisites:
    matplotlib, _latex_fallback module (for LaTeX fallback)
"""

import re
from typing import Union, Tuple, Optional

try:
    from ._latex_fallback import safe_latex_render, latex_fallback_decorator
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False
    # Define dummy decorator if fallback not available
    def latex_fallback_decorator(fallback_strategy="auto", preserve_math=True):
        def decorator(func):
            return func
        return decorator
    
    def safe_latex_render(text, fallback_strategy="auto", preserve_math=True):
        return text


@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
def format_plot_text(
    text: str,
    capitalize: bool = True,
    unit_style: str = "parentheses",
    latex_math: bool = True,
    scientific_notation: bool = True,
    enable_fallback: bool = True,
    replace_underscores: bool = True
) -> str:
    """
    Format text for scientific plots with proper conventions and LaTeX fallback.
    
    Parameters
    ----------
    text : str
        Input text to format
    capitalize : bool, optional
        Whether to capitalize the first letter, by default True
    unit_style : str, optional
        Unit bracket style: "parentheses" (), "brackets" [], or "auto", by default "parentheses"
    latex_math : bool, optional
        Whether to enable LaTeX math formatting, by default True
    scientific_notation : bool, optional
        Whether to format scientific notation properly, by default True
    enable_fallback : bool, optional
        Whether to enable LaTeX fallback mechanisms, by default True
    replace_underscores : bool, optional
        Whether to replace underscores with spaces, by default True
        
    Returns
    -------
    str
        Formatted text ready for matplotlib with automatic LaTeX fallback
        
    Examples
    --------
    >>> format_plot_text("time (s)")
    'Time (s)'
    
    >>> format_plot_text("voltage [V]", unit_style="brackets")
    'Voltage [V]'
    
    >>> format_plot_text("frequency in Hz", unit_style="auto")
    'Frequency (Hz)'
    
    >>> format_plot_text("signal_power_db")
    'Signal Power Db'
    
    >>> format_plot_text(r"$\alpha$ decay")  # Falls back if LaTeX fails
    'α decay'
    
    Notes
    -----
    If LaTeX rendering fails, this function automatically falls back to 
    mathtext or unicode alternatives while preserving scientific formatting.
    """
    if not text or not isinstance(text, str):
        return text
    
    # Handle LaTeX math sections (preserve them)
    latex_sections = []
    text_working = text
    
    if latex_math:
        # Extract and preserve LaTeX math
        latex_pattern = r'\$[^$]+\$'
        latex_matches = re.findall(latex_pattern, text)
        for i, match in enumerate(latex_matches):
            placeholder = f"__LATEX_{i}__"
            latex_sections.append(match)
            text_working = text_working.replace(match, placeholder, 1)
    
    # Replace underscores with spaces (before unit formatting)
    if replace_underscores:
        text_working = _replace_underscores(text_working)
    
    # Format units
    text_working = _format_units(text_working, unit_style)
    
    # Capitalize first letter (excluding LaTeX)
    if capitalize:
        text_working = _capitalize_text(text_working)
    
    # Handle scientific notation
    if scientific_notation:
        text_working = _format_scientific_notation(text_working)
    
    # Restore LaTeX sections with fallback handling
    for i, latex_section in enumerate(latex_sections):
        placeholder = f"__LATEX_{i}__"
        if enable_fallback and FALLBACK_AVAILABLE:
            # Apply fallback to LaTeX sections
            safe_latex = safe_latex_render(latex_section, preserve_math=True)
            text_working = text_working.replace(placeholder, safe_latex)
        else:
            text_working = text_working.replace(placeholder, latex_section)
    
    return text_working


@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
def format_axis_label(
    label: str,
    unit: Optional[str] = None,
    unit_style: str = "parentheses",
    capitalize: bool = True,
    latex_math: bool = True,
    enable_fallback: bool = True,
    replace_underscores: bool = True
) -> str:
    """
    Format axis labels with proper unit handling.
    
    Parameters
    ----------
    label : str
        The variable name or description
    unit : Optional[str], optional
        The unit string, by default None
    unit_style : str, optional
        Unit bracket style, by default "parentheses"
    capitalize : bool, optional
        Whether to capitalize, by default True
    latex_math : bool, optional
        Whether to enable LaTeX math, by default True
    enable_fallback : bool, optional
        Whether to enable LaTeX fallback mechanisms, by default True
    replace_underscores : bool, optional
        Whether to replace underscores with spaces, by default True
        
    Returns
    -------
    str
        Formatted axis label with automatic LaTeX fallback
        
    Examples
    --------
    >>> format_axis_label("time", "s")
    'Time (s)'
    
    >>> format_axis_label("voltage", "V", unit_style="brackets")
    'Voltage [V]'
    
    >>> format_axis_label("temperature", "°C")
    'Temperature (°C)'
    
    >>> format_axis_label("signal_power", "dB")
    'Signal Power (dB)'
    """
    if unit:
        if unit_style == "brackets":
            full_text = f"{label} [{unit}]"
        else:  # parentheses
            full_text = f"{label} ({unit})"
    else:
        full_text = label
    
    return format_plot_text(full_text, capitalize, unit_style, latex_math, scientific_notation=True, enable_fallback=enable_fallback, replace_underscores=replace_underscores)


@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
def format_title(
    title: str,
    subtitle: Optional[str] = None,
    capitalize: bool = True,
    latex_math: bool = True,
    enable_fallback: bool = True,
    replace_underscores: bool = True
) -> str:
    """
    Format plot titles with proper conventions.
    
    Parameters
    ----------
    title : str
        Main title text
    subtitle : Optional[str], optional
        Subtitle text, by default None
    capitalize : bool, optional
        Whether to capitalize, by default True
    latex_math : bool, optional
        Whether to enable LaTeX math, by default True
    enable_fallback : bool, optional
        Whether to enable LaTeX fallback mechanisms, by default True
    replace_underscores : bool, optional
        Whether to replace underscores with spaces, by default True
        
    Returns
    -------
    str
        Formatted title with automatic LaTeX fallback
        
    Examples
    --------
    >>> format_title("neural spike analysis")
    'Neural Spike Analysis'
    
    >>> format_title("data analysis", "preliminary results")
    'Data Analysis\\nPreliminary Results'
    
    >>> format_title("signal_processing_results")
    'Signal Processing Results'
    """
    formatted_title = format_plot_text(title, capitalize, latex_math=latex_math, 
                                      enable_fallback=enable_fallback, 
                                      replace_underscores=replace_underscores)
    
    if subtitle:
        formatted_subtitle = format_plot_text(subtitle, capitalize, latex_math=latex_math,
                                            enable_fallback=enable_fallback,
                                            replace_underscores=replace_underscores)
        return f"{formatted_title}\\n{formatted_subtitle}"
    
    return formatted_title


def check_unit_consistency(
    x_unit: Optional[str] = None,
    y_unit: Optional[str] = None,
    operation: str = "none"
) -> Tuple[bool, str]:
    """
    Check unit consistency for mathematical operations.
    
    Parameters
    ----------
    x_unit : Optional[str], optional
        X-axis unit, by default None
    y_unit : Optional[str], optional
        Y-axis unit, by default None
    operation : str, optional
        Mathematical operation: "add", "subtract", "multiply", "divide", "none", by default "none"
        
    Returns
    -------
    Tuple[bool, str]
        (is_consistent, expected_result_unit)
        
    Examples
    --------
    >>> check_unit_consistency("m", "s", "divide")
    (True, 'm/s')
    
    >>> check_unit_consistency("m", "m", "add")
    (True, 'm')
    
    >>> check_unit_consistency("m", "kg", "add")
    (False, 'Units incompatible for addition')
    """
    if not x_unit or not y_unit:
        return True, x_unit or y_unit or ""
    
    # Normalize units
    x_norm = _normalize_unit(x_unit)
    y_norm = _normalize_unit(y_unit)
    
    if operation in ["add", "subtract"]:
        if x_norm == y_norm:
            return True, x_unit
        else:
            return False, f"Units incompatible for {operation}"
    
    elif operation == "multiply":
        if x_norm == "1" or y_norm == "1":  # dimensionless
            return True, x_unit if x_norm != "1" else y_unit
        else:
            return True, f"{x_unit}·{y_unit}"
    
    elif operation == "divide":
        if y_norm == "1":  # dividing by dimensionless
            return True, x_unit
        elif x_norm == y_norm:
            return True, "1"  # dimensionless
        else:
            return True, f"{x_unit}/{y_unit}"
    
    return True, ""


def _format_units(text: str, unit_style: str) -> str:
    """Format units in text according to specified style."""
    if unit_style == "auto":
        # Auto-detect and standardize to parentheses
        # Look for common unit patterns
        unit_patterns = [
            r'\s+in\s+([A-Za-z°µ²³⁻⁺]+)',  # "in Hz", "in μV", etc.
            r'\s+\[([^\]]+)\]',  # [unit]
            r'\s+\(([^)]+)\)',   # (unit)
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, text)
            if match:
                unit = match.group(1)
                # Replace with standardized format
                text = re.sub(pattern, f' ({unit})', text)
                break
    
    elif unit_style == "brackets":
        # Convert parentheses to brackets
        text = re.sub(r'\s*\(([^)]+)\)', r' [\1]', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def _capitalize_text(text: str) -> str:
    """Capitalize the first letter of text, preserving units in parentheses/brackets."""
    if not text:
        return text
    
    # Preserve content in parentheses and brackets
    preserved_sections = []
    
    # Find and preserve parentheses content
    paren_pattern = r'(\([^)]+\))'
    paren_matches = re.findall(paren_pattern, text)
    for i, match in enumerate(paren_matches):
        placeholder = f"__PAREN_{i}__"
        preserved_sections.append((placeholder, match))
        text = text.replace(match, placeholder, 1)
    
    # Find and preserve bracket content
    bracket_pattern = r'(\[[^\]]+\])'
    bracket_matches = re.findall(bracket_pattern, text)
    for i, match in enumerate(bracket_matches):
        placeholder = f"__BRACKET_{i}__"
        preserved_sections.append((placeholder, match))
        text = text.replace(match, placeholder, 1)
    
    # Capitalize the first alphabetic character
    capitalized = False
    result = []
    for char in text:
        if not capitalized and char.isalpha():
            result.append(char.upper())
            capitalized = True
        else:
            result.append(char)
    
    text = ''.join(result)
    
    # Restore preserved sections
    for placeholder, original in preserved_sections:
        text = text.replace(placeholder, original)
    
    return text


def _format_scientific_notation(text: str) -> str:
    """Format scientific notation in text."""
    # Convert patterns like "1e-3" to "1×10⁻³" or LaTeX equivalent
    sci_pattern = r'(\d+\.?\d*)[eE]([-+]?\d+)'
    
    def replace_sci(match):
        base = match.group(1)
        exp = match.group(2)
        # Use LaTeX format
        return f"{base}×10^{{{exp}}}"
    
    return re.sub(sci_pattern, replace_sci, text)


def _replace_underscores(text: str) -> str:
    """Replace underscores with spaces and apply proper word capitalization."""
    # First, preserve content in parentheses and brackets
    preserved_sections = []
    
    # Preserve parentheses content
    paren_pattern = r'(\([^)]+\))'
    paren_matches = re.findall(paren_pattern, text)
    for i, match in enumerate(paren_matches):
        placeholder = f"|||PAREN{i}|||"
        preserved_sections.append((placeholder, match))
        text = text.replace(match, placeholder, 1)
    
    # Preserve bracket content
    bracket_pattern = r'(\[[^\]]+\])'
    bracket_matches = re.findall(bracket_pattern, text)
    for i, match in enumerate(bracket_matches):
        placeholder = f"|||BRACKET{i}|||"
        preserved_sections.append((placeholder, match))
        text = text.replace(match, placeholder, 1)
    
    # Replace underscores with spaces
    text_with_spaces = text.replace('_', ' ')
    
    # Split by spaces for word processing
    words = text_with_spaces.split(' ')
    
    # Common units that should preserve their case
    common_units = {'Hz', 'kHz', 'MHz', 'GHz', 'V', 'mV', 'uV', 'μV', 'A', 'mA', 
                    'μA', 'W', 'mW', 'dB', 'dBm', 's', 'ms', 'μs', 'ns', 'ps',
                    'K', 'C', 'F', 'rad', 'deg', 'm', 'cm', 'mm', 'μm', 'nm',
                    'kg', 'g', 'mg', 'μg', 'N', 'Pa', 'bar', 'psi', 'mol', 'M'}
    
    # Process each word
    formatted_words = []
    for word in words:
        if not word:  # Preserve empty strings (from consecutive underscores)
            formatted_words.append('')
        # Skip placeholders
        elif '|||' in word:
            formatted_words.append(word)
        # Check if word is a known unit
        elif word in common_units:
            formatted_words.append(word)
        # Preserve special cases (e.g., all caps like "DB", "ID", etc.)
        elif word.isupper() and len(word) > 1:
            formatted_words.append(word)
        # Capitalize first letter of each word
        else:
            formatted_words.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
    
    # Join with spaces
    result = ' '.join(formatted_words)
    
    # Restore preserved sections
    for placeholder, original in preserved_sections:
        result = result.replace(placeholder, original)
    
    return result


def _normalize_unit(unit: str) -> str:
    """Normalize unit string for comparison."""
    # Remove brackets/parentheses and normalize
    normalized = re.sub(r'[\[\]()]', '', unit).strip().lower()
    
    # Handle common equivalent units
    equivalents = {
        'sec': 's', 'second': 's', 'seconds': 's',
        'volt': 'V', 'volts': 'V',
        'amp': 'A', 'ampere': 'A', 'amps': 'A',
        'meter': 'm', 'meters': 'm', 'metre': 'm', 'metres': 'm',
        'gram': 'g', 'grams': 'g',
        'hertz': 'Hz', 'hz': 'Hz',
        'dimensionless': '1', 'unitless': '1', '': '1',
    }
    
    return equivalents.get(normalized, normalized)


# Convenient aliases and shortcuts
def axis_label(label: str, unit: str = None, **kwargs) -> str:
    """Convenient alias for format_axis_label."""
    return format_axis_label(label, unit, **kwargs)


def title(text: str, **kwargs) -> str:
    """Convenient alias for format_title."""
    return format_title(text, **kwargs)


def scientific_text(text: str, **kwargs) -> str:
    """Convenient alias for format_plot_text with scientific defaults."""
    return format_plot_text(text, **kwargs)


# EOF