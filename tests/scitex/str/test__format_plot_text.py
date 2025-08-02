#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-05 12:05:00 (ywatanabe)"
# File: ./tests/scitex/str/test__format_plot_text.py

import pytest
try:
    # Try importing from public API first
    from scitex.str import (
        format_plot_text,
        format_axis_label,
        format_title,
        check_unit_consistency,
        axis_label,
        title,
        scientific_text,
    )
except ImportError:
    # Fall back to module imports
    from scitex.str._format_plot_text import (
        format_plot_text,
        format_axis_label,
        format_title,
        check_unit_consistency,
        axis_label,
        title,
        scientific_text,
    )

# Import private functions directly
from scitex.str._format_plot_text import (
    _format_units,
    _capitalize_text,
    _format_scientific_notation,
    _normalize_unit,
)


class TestFormatPlotText:
    """Test cases for format_plot_text function."""

    def test_basic_capitalization(self):
        """Test basic text capitalization."""
        result = format_plot_text("time")
        assert result == "Time"

    def test_disable_capitalization(self):
        """Test disabling capitalization."""
        result = format_plot_text("time", capitalize=False)
        assert result == "time"

    def test_units_parentheses(self):
        """Test units with parentheses style."""
        result = format_plot_text("time (s)")
        assert result == "Time (s)"

    def test_units_brackets(self):
        """Test units with brackets style."""
        result = format_plot_text("voltage [V]", unit_style="brackets")
        assert result == "Voltage [V]"

    def test_units_auto_conversion_in(self):
        """Test auto-detection of 'in Hz' style units."""
        result = format_plot_text("frequency in Hz", unit_style="auto")
        assert result == "Frequency (Hz)"

    def test_units_auto_conversion_brackets(self):
        """Test auto-detection of bracket units."""
        result = format_plot_text("voltage [V]", unit_style="auto")
        assert result == "Voltage (V)"

    def test_latex_preservation(self):
        """Test LaTeX math preservation with fallback."""
        result = format_plot_text("signal $\\alpha$ value", latex_math=True)
        # In environments where LaTeX is unavailable, fallback to Unicode
        assert result in ["Signal $\\alpha$ value", "Signal α value"]

    def test_multiple_latex_sections(self):
        """Test multiple LaTeX sections with fallback."""
        result = format_plot_text("$\\alpha$ and $\\beta$ values", latex_math=True)
        # In environments where LaTeX is unavailable, fallback to Unicode
        assert result in ["$\\alpha$ and $\\beta$ values", "α and β values"]

    def test_scientific_notation_formatting(self):
        """Test scientific notation formatting."""
        result = format_plot_text("value 1e-3", scientific_notation=True)
        assert result == "Value 1×10^{-3}"

    def test_scientific_notation_disabled(self):
        """Test scientific notation disabled."""
        result = format_plot_text("value 1e-3", scientific_notation=False)
        assert result == "Value 1e-3"

    def test_empty_string(self):
        """Test empty string input."""
        result = format_plot_text("")
        assert result == ""

    def test_none_input(self):
        """Test None input."""
        result = format_plot_text(None)
        assert result is None

    def test_non_string_input(self):
        """Test non-string input."""
        result = format_plot_text(123)
        assert result == 123

    def test_complex_text_with_all_features(self):
        """Test complex text with all formatting features."""
        text = "frequency $\\omega$ in Hz with 1e6 samples"
        result = format_plot_text(text, unit_style="auto")
        assert "Frequency" in result
        # LaTeX fallback: $\omega$ → ω in constrained environments
        assert ("$\\omega$" in result) or ("ω" in result)
        assert "(Hz)" in result
        assert "1×10^{6}" in result

    def test_special_characters_capitalization(self):
        """Test capitalization with special characters."""
        result = format_plot_text("(time)")
        assert result == "(Time)"

    def test_unicode_units(self):
        """Test Unicode characters in units."""
        result = format_plot_text("temperature (°C)")
        assert result == "Temperature (°C)"


class TestFormatAxisLabel:
    """Test cases for format_axis_label function."""

    def test_basic_label_with_unit(self):
        """Test basic label with unit."""
        result = format_axis_label("time", "s")
        assert result == "Time (s)"

    def test_label_without_unit(self):
        """Test label without unit."""
        result = format_axis_label("time")
        assert result == "Time"

    def test_label_with_brackets_style(self):
        """Test label with brackets unit style."""
        result = format_axis_label("voltage", "V", unit_style="brackets")
        assert result == "Voltage [V]"

    def test_label_with_special_unit(self):
        """Test label with special Unicode unit."""
        result = format_axis_label("temperature", "°C")
        assert result == "Temperature (°C)"

    def test_disable_capitalization(self):
        """Test axis label without capitalization."""
        result = format_axis_label("time", "s", capitalize=False)
        assert result == "time (s)"

    def test_latex_in_label(self):
        """Test LaTeX math in axis label with fallback."""
        result = format_axis_label("phase $\\phi$", "rad")
        # LaTeX fallback: $\phi$ → φ in constrained environments
        assert result in ["Phase $\\phi$ (rad)", "Phase φ (rad)"]

    def test_empty_unit(self):
        """Test empty unit string."""
        result = format_axis_label("time", "")
        assert result == "Time"

    def test_none_unit(self):
        """Test None unit."""
        result = format_axis_label("time", None)
        assert result == "Time"


class TestFormatTitle:
    """Test cases for format_title function."""

    def test_basic_title(self):
        """Test basic title formatting."""
        result = format_title("neural spike analysis")
        assert result == "Neural spike analysis"

    def test_title_with_subtitle(self):
        """Test title with subtitle."""
        result = format_title("data analysis", "preliminary results")
        assert result == "Data analysis\\nPreliminary results"

    def test_disable_capitalization(self):
        """Test title without capitalization."""
        result = format_title("neural spike analysis", capitalize=False)
        assert result == "neural spike analysis"

    def test_title_with_latex(self):
        """Test title with LaTeX math and fallback."""
        result = format_title("analysis of $\\alpha$ waves")
        # LaTeX fallback: $\alpha$ → α in constrained environments  
        assert result in ["Analysis of $\\alpha$ waves", "Analysis of α waves"]

    def test_empty_title(self):
        """Test empty title."""
        result = format_title("")
        assert result == ""

    def test_subtitle_only(self):
        """Test with subtitle but empty main title."""
        result = format_title("", "subtitle")
        assert result == "\\nSubtitle"


class TestCheckUnitConsistency:
    """Test cases for check_unit_consistency function."""

    def test_addition_same_units(self):
        """Test addition with same units."""
        consistent, result_unit = check_unit_consistency("m", "m", "add")
        assert consistent is True
        assert result_unit == "m"

    def test_addition_different_units(self):
        """Test addition with different units."""
        consistent, result_unit = check_unit_consistency("m", "kg", "add")
        assert consistent is False
        assert "incompatible" in result_unit.lower()

    def test_subtraction_same_units(self):
        """Test subtraction with same units."""
        consistent, result_unit = check_unit_consistency("V", "V", "subtract")
        assert consistent is True
        assert result_unit == "V"

    def test_multiplication_units(self):
        """Test multiplication with units."""
        consistent, result_unit = check_unit_consistency("m", "s", "multiply")
        assert consistent is True
        assert result_unit == "m·s"

    def test_multiplication_with_dimensionless(self):
        """Test multiplication with dimensionless quantity."""
        consistent, result_unit = check_unit_consistency("m", "1", "multiply")
        assert consistent is True
        assert result_unit == "m"

    def test_division_same_units(self):
        """Test division with same units."""
        consistent, result_unit = check_unit_consistency("m", "m", "divide")
        assert consistent is True
        assert result_unit == "1"

    def test_division_different_units(self):
        """Test division with different units."""
        consistent, result_unit = check_unit_consistency("m", "s", "divide")
        assert consistent is True
        assert result_unit == "m/s"

    def test_division_by_dimensionless(self):
        """Test division by dimensionless quantity."""
        consistent, result_unit = check_unit_consistency("m", "1", "divide")
        assert consistent is True
        assert result_unit == "m"

    def test_no_operation(self):
        """Test with no operation specified."""
        consistent, result_unit = check_unit_consistency("m", "s", "none")
        assert consistent is True
        assert result_unit == ""

    def test_missing_units(self):
        """Test with missing units."""
        consistent, result_unit = check_unit_consistency(None, "s", "add")
        assert consistent is True
        assert result_unit == "s"

        consistent, result_unit = check_unit_consistency("m", None, "add")
        assert consistent is True
        assert result_unit == "m"

    def test_both_units_missing(self):
        """Test with both units missing."""
        consistent, result_unit = check_unit_consistency(None, None, "add")
        assert consistent is True
        assert result_unit == ""


class TestFormatUnits:
    """Test cases for _format_units function."""

    def test_auto_detect_in_pattern(self):
        """Test auto-detection of 'in Hz' pattern."""
        result = _format_units("frequency in Hz", "auto")
        assert result == "frequency (Hz)"

    def test_auto_detect_brackets(self):
        """Test auto-detection of bracket units."""
        result = _format_units("voltage [V]", "auto")
        assert result == "voltage (V)"

    def test_auto_detect_parentheses(self):
        """Test auto-detection of parentheses units."""
        result = _format_units("time (s)", "auto")
        assert result == "time (s)"

    def test_convert_to_brackets(self):
        """Test conversion to brackets style."""
        result = _format_units("time (s)", "brackets")
        assert result == "time [s]"

    def test_no_units_found(self):
        """Test text with no units."""
        result = _format_units("simple text", "auto")
        assert result == "simple text"

    def test_multiple_spaces_cleanup(self):
        """Test cleanup of multiple spaces."""
        result = _format_units("time   (s)", "auto")
        assert result == "time (s)"

    def test_unicode_units_auto(self):
        """Test Unicode units with auto detection."""
        result = _format_units("temperature in °C", "auto")
        assert result == "temperature (°C)"


class TestCapitalizeText:
    """Test cases for _capitalize_text function."""

    def test_basic_capitalization(self):
        """Test basic text capitalization."""
        result = _capitalize_text("hello")
        assert result == "Hello"

    def test_leading_non_alpha(self):
        """Test capitalization with leading non-alphabetic characters."""
        result = _capitalize_text("(time)")
        assert result == "(Time)"

    def test_numbers_and_symbols(self):
        """Test capitalization with numbers and symbols."""
        result = _capitalize_text("123abc")
        assert result == "123Abc"

    def test_empty_string(self):
        """Test empty string."""
        result = _capitalize_text("")
        assert result == ""

    def test_no_alphabetic_characters(self):
        """Test string with no alphabetic characters."""
        result = _capitalize_text("123!@#")
        assert result == "123!@#"

    def test_already_capitalized(self):
        """Test already capitalized text."""
        result = _capitalize_text("Hello")
        assert result == "Hello"


class TestFormatScientificNotation:
    """Test cases for _format_scientific_notation function."""

    def test_lowercase_e_notation(self):
        """Test lowercase 'e' scientific notation."""
        result = _format_scientific_notation("1e-3")
        assert result == "1×10^{-3}"

    def test_uppercase_e_notation(self):
        """Test uppercase 'E' scientific notation."""
        result = _format_scientific_notation("2E+5")
        assert result == "2×10^{+5}"

    def test_decimal_base(self):
        """Test decimal base in scientific notation."""
        result = _format_scientific_notation("3.14e2")
        assert result == "3.14×10^{2}"

    def test_multiple_scientific_numbers(self):
        """Test multiple scientific numbers in text."""
        result = _format_scientific_notation("values 1e-3 and 2e4")
        assert result == "values 1×10^{-3} and 2×10^{4}"

    def test_no_scientific_notation(self):
        """Test text without scientific notation."""
        result = _format_scientific_notation("normal text")
        assert result == "normal text"

    def test_embedded_in_words(self):
        """Test scientific notation embedded in longer text."""
        result = _format_scientific_notation("The value is 1.5e-6 meters")
        assert result == "The value is 1.5×10^{-6} meters"


class TestNormalizeUnit:
    """Test cases for _normalize_unit function."""

    def test_basic_normalization(self):
        """Test basic unit normalization."""
        result = _normalize_unit("seconds")
        assert result == "s"

    def test_case_insensitive(self):
        """Test case-insensitive normalization."""
        result = _normalize_unit("Volts")
        assert result == "V"

    def test_bracket_removal(self):
        """Test bracket removal."""
        result = _normalize_unit("[Hz]")
        assert result == "Hz"

    def test_parentheses_removal(self):
        """Test parentheses removal."""
        result = _normalize_unit("(meter)")
        assert result == "m"

    def test_dimensionless_units(self):
        """Test dimensionless unit normalization."""
        assert _normalize_unit("dimensionless") == "1"
        assert _normalize_unit("unitless") == "1"
        assert _normalize_unit("") == "1"

    def test_unknown_unit(self):
        """Test unknown unit (should return lowercase)."""
        result = _normalize_unit("Foobar")
        assert result == "foobar"

    def test_whitespace_handling(self):
        """Test whitespace handling."""
        result = _normalize_unit("  meters  ")
        assert result == "m"


class TestConvenienceAliases:
    """Test cases for convenience alias functions."""

    def test_axis_label_alias(self):
        """Test axis_label convenience function."""
        result = axis_label("time", "s")
        expected = format_axis_label("time", "s")
        assert result == expected

    def test_title_alias(self):
        """Test title convenience function."""
        result = title("test title")
        expected = format_title("test title")
        assert result == expected

    def test_scientific_text_alias(self):
        """Test scientific_text convenience function."""
        result = scientific_text("test 1e-3")
        expected = format_plot_text("test 1e-3")
        assert result == expected

    def test_axis_label_with_kwargs(self):
        """Test axis_label with keyword arguments."""
        result = axis_label("voltage", "V", unit_style="brackets")
        expected = format_axis_label("voltage", "V", unit_style="brackets")
        assert result == expected


class TestEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_very_long_text(self):
        """Test very long text formatting."""
        long_text = "very " * 50 + "long text with units (Hz)"
        result = format_plot_text(long_text)
        assert result.startswith("Very")
        assert "(Hz)" in result

    def test_nested_parentheses(self):
        """Test nested parentheses handling."""
        result = format_plot_text("value (test (s))")
        assert "Value" in result

    def test_mixed_latex_and_units(self):
        """Test mixed LaTeX and units with fallback."""
        text = "phase $\\phi$ (rad) with $\\omega$ frequency"
        result = format_plot_text(text)
        # LaTeX fallback: $\phi$ → φ, $\omega$ → ω in constrained environments
        assert ("$\\phi$" in result) or ("φ" in result)
        assert ("$\\omega$" in result) or ("ω" in result)
        assert "(rad)" in result

    def test_multiple_scientific_notations(self):
        """Test multiple scientific notations with units."""
        text = "range 1e-6 to 1e3 (Hz)"
        result = format_plot_text(text)
        assert "1×10^{-6}" in result
        assert "1×10^{3}" in result
        assert "(Hz)" in result

    def test_complex_unit_patterns(self):
        """Test complex unit patterns."""
        result = _format_units("power in W/m²", "auto")
        assert "(W/m²)" in result or "(W)/m²" in result  # Accept either format

    def test_unit_consistency_edge_cases(self):
        """Test unit consistency with edge cases."""
        # Test with empty strings
        consistent, unit = check_unit_consistency("", "", "add")
        assert consistent is True

        # Test with same normalized units but different strings
        consistent, unit = check_unit_consistency("seconds", "s", "add")
        assert consistent is True

    def test_error_resistance(self):
        """Test function resistance to various error conditions."""
        # Should not crash with malformed input
        try:
            format_plot_text("test $incomplete_latex")
            format_plot_text("test (incomplete_unit")
            format_plot_text("test [incomplete_unit")
        except Exception as e:
            pytest.fail(f"Function should handle malformed input gracefully: {e}")

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_format_plot_text.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2025-06-04 11:08:00 (ywatanabe)"
# # File: ./src/scitex/str/_format_plot_text.py
# 
# """
# Functionality:
#     Format text for scientific plots with proper capitalization and unit handling
#     Includes LaTeX fallback mechanisms for robust rendering
# Input:
#     Text strings with optional units
# Output:
#     Properly formatted strings for scientific plots with LaTeX fallback
# Prerequisites:
#     matplotlib, _latex_fallback module (for LaTeX fallback)
# """
# 
# import re
# from typing import Union, Tuple, Optional
# 
# try:
#     from ._latex_fallback import safe_latex_render, latex_fallback_decorator
#     FALLBACK_AVAILABLE = True
# except ImportError:
#     FALLBACK_AVAILABLE = False
#     # Define dummy decorator if fallback not available
#     def latex_fallback_decorator(fallback_strategy="auto", preserve_math=True):
#         def decorator(func):
#             return func
#         return decorator
#     
#     def safe_latex_render(text, fallback_strategy="auto", preserve_math=True):
#         return text
# 
# 
# @latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
# def format_plot_text(
#     text: str,
#     capitalize: bool = True,
#     unit_style: str = "parentheses",
#     latex_math: bool = True,
#     scientific_notation: bool = True,
#     enable_fallback: bool = True,
#     replace_underscores: bool = True
# ) -> str:
#     """
#     Format text for scientific plots with proper conventions and LaTeX fallback.
#     
#     Parameters
#     ----------
#     text : str
#         Input text to format
#     capitalize : bool, optional
#         Whether to capitalize the first letter, by default True
#     unit_style : str, optional
#         Unit bracket style: "parentheses" (), "brackets" [], or "auto", by default "parentheses"
#     latex_math : bool, optional
#         Whether to enable LaTeX math formatting, by default True
#     scientific_notation : bool, optional
#         Whether to format scientific notation properly, by default True
#     enable_fallback : bool, optional
#         Whether to enable LaTeX fallback mechanisms, by default True
#     replace_underscores : bool, optional
#         Whether to replace underscores with spaces, by default True
#         
#     Returns
#     -------
#     str
#         Formatted text ready for matplotlib with automatic LaTeX fallback
#         
#     Examples
#     --------
#     >>> format_plot_text("time (s)")
#     'Time (s)'
#     
#     >>> format_plot_text("voltage [V]", unit_style="brackets")
#     'Voltage [V]'
#     
#     >>> format_plot_text("frequency in Hz", unit_style="auto")
#     'Frequency (Hz)'
#     
#     >>> format_plot_text("signal_power_db")
#     'Signal Power Db'
#     
#     >>> format_plot_text(r"$\alpha$ decay")  # Falls back if LaTeX fails
#     'α decay'
#     
#     Notes
#     -----
#     If LaTeX rendering fails, this function automatically falls back to 
#     mathtext or unicode alternatives while preserving scientific formatting.
#     """
#     if not text or not isinstance(text, str):
#         return text
#     
#     # Handle LaTeX math sections (preserve them)
#     latex_sections = []
#     text_working = text
#     
#     if latex_math:
#         # Extract and preserve LaTeX math
#         latex_pattern = r'\$[^$]+\$'
#         latex_matches = re.findall(latex_pattern, text)
#         for i, match in enumerate(latex_matches):
#             placeholder = f"__LATEX_{i}__"
#             latex_sections.append(match)
#             text_working = text_working.replace(match, placeholder, 1)
#     
#     # Replace underscores with spaces (before unit formatting)
#     if replace_underscores:
#         text_working = _replace_underscores(text_working)
#     
#     # Format units
#     text_working = _format_units(text_working, unit_style)
#     
#     # Capitalize first letter (excluding LaTeX)
#     if capitalize:
#         text_working = _capitalize_text(text_working)
#     
#     # Handle scientific notation
#     if scientific_notation:
#         text_working = _format_scientific_notation(text_working)
#     
#     # Restore LaTeX sections with fallback handling
#     for i, latex_section in enumerate(latex_sections):
#         placeholder = f"__LATEX_{i}__"
#         if enable_fallback and FALLBACK_AVAILABLE:
#             # Apply fallback to LaTeX sections
#             safe_latex = safe_latex_render(latex_section, preserve_math=True)
#             text_working = text_working.replace(placeholder, safe_latex)
#         else:
#             text_working = text_working.replace(placeholder, latex_section)
#     
#     return text_working
# 
# 
# @latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
# def format_axis_label(
#     label: str,
#     unit: Optional[str] = None,
#     unit_style: str = "parentheses",
#     capitalize: bool = True,
#     latex_math: bool = True,
#     enable_fallback: bool = True,
#     replace_underscores: bool = True
# ) -> str:
#     """
#     Format axis labels with proper unit handling.
#     
#     Parameters
#     ----------
#     label : str
#         The variable name or description
#     unit : Optional[str], optional
#         The unit string, by default None
#     unit_style : str, optional
#         Unit bracket style, by default "parentheses"
#     capitalize : bool, optional
#         Whether to capitalize, by default True
#     latex_math : bool, optional
#         Whether to enable LaTeX math, by default True
#     enable_fallback : bool, optional
#         Whether to enable LaTeX fallback mechanisms, by default True
#     replace_underscores : bool, optional
#         Whether to replace underscores with spaces, by default True
#         
#     Returns
#     -------
#     str
#         Formatted axis label with automatic LaTeX fallback
#         
#     Examples
#     --------
#     >>> format_axis_label("time", "s")
#     'Time (s)'
#     
#     >>> format_axis_label("voltage", "V", unit_style="brackets")
#     'Voltage [V]'
#     
#     >>> format_axis_label("temperature", "°C")
#     'Temperature (°C)'
#     
#     >>> format_axis_label("signal_power", "dB")
#     'Signal Power (dB)'
#     """
#     if unit:
#         if unit_style == "brackets":
#             full_text = f"{label} [{unit}]"
#         else:  # parentheses
#             full_text = f"{label} ({unit})"
#     else:
#         full_text = label
#     
#     return format_plot_text(full_text, capitalize, unit_style, latex_math, scientific_notation=True, enable_fallback=enable_fallback, replace_underscores=replace_underscores)
# 
# 
# @latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
# def format_title(
#     title: str,
#     subtitle: Optional[str] = None,
#     capitalize: bool = True,
#     latex_math: bool = True,
#     enable_fallback: bool = True,
#     replace_underscores: bool = True
# ) -> str:
#     """
#     Format plot titles with proper conventions.
#     
#     Parameters
#     ----------
#     title : str
#         Main title text
#     subtitle : Optional[str], optional
#         Subtitle text, by default None
#     capitalize : bool, optional
#         Whether to capitalize, by default True
#     latex_math : bool, optional
#         Whether to enable LaTeX math, by default True
#     enable_fallback : bool, optional
#         Whether to enable LaTeX fallback mechanisms, by default True
#     replace_underscores : bool, optional
#         Whether to replace underscores with spaces, by default True
#         
#     Returns
#     -------
#     str
#         Formatted title with automatic LaTeX fallback
#         
#     Examples
#     --------
#     >>> format_title("neural spike analysis")
#     'Neural Spike Analysis'
#     
#     >>> format_title("data analysis", "preliminary results")
#     'Data Analysis\\nPreliminary Results'
#     
#     >>> format_title("signal_processing_results")
#     'Signal Processing Results'
#     """
#     formatted_title = format_plot_text(title, capitalize, latex_math=latex_math, 
#                                       enable_fallback=enable_fallback, 
#                                       replace_underscores=replace_underscores)
#     
#     if subtitle:
#         formatted_subtitle = format_plot_text(subtitle, capitalize, latex_math=latex_math,
#                                             enable_fallback=enable_fallback,
#                                             replace_underscores=replace_underscores)
#         return f"{formatted_title}\\n{formatted_subtitle}"
#     
#     return formatted_title
# 
# 
# def check_unit_consistency(
#     x_unit: Optional[str] = None,
#     y_unit: Optional[str] = None,
#     operation: str = "none"
# ) -> Tuple[bool, str]:
#     """
#     Check unit consistency for mathematical operations.
#     
#     Parameters
#     ----------
#     x_unit : Optional[str], optional
#         X-axis unit, by default None
#     y_unit : Optional[str], optional
#         Y-axis unit, by default None
#     operation : str, optional
#         Mathematical operation: "add", "subtract", "multiply", "divide", "none", by default "none"
#         
#     Returns
#     -------
#     Tuple[bool, str]
#         (is_consistent, expected_result_unit)
#         
#     Examples
#     --------
#     >>> check_unit_consistency("m", "s", "divide")
#     (True, 'm/s')
#     
#     >>> check_unit_consistency("m", "m", "add")
#     (True, 'm')
#     
#     >>> check_unit_consistency("m", "kg", "add")
#     (False, 'Units incompatible for addition')
#     """
#     if not x_unit or not y_unit:
#         return True, x_unit or y_unit or ""
#     
#     # Normalize units
#     x_norm = _normalize_unit(x_unit)
#     y_norm = _normalize_unit(y_unit)
#     
#     if operation in ["add", "subtract"]:
#         if x_norm == y_norm:
#             return True, x_unit
#         else:
#             return False, f"Units incompatible for {operation}"
#     
#     elif operation == "multiply":
#         if x_norm == "1" or y_norm == "1":  # dimensionless
#             return True, x_unit if x_norm != "1" else y_unit
#         else:
#             return True, f"{x_unit}·{y_unit}"
#     
#     elif operation == "divide":
#         if y_norm == "1":  # dividing by dimensionless
#             return True, x_unit
#         elif x_norm == y_norm:
#             return True, "1"  # dimensionless
#         else:
#             return True, f"{x_unit}/{y_unit}"
#     
#     return True, ""
# 
# 
# def _format_units(text: str, unit_style: str) -> str:
#     """Format units in text according to specified style."""
#     if unit_style == "auto":
#         # Auto-detect and standardize to parentheses
#         # Look for common unit patterns
#         unit_patterns = [
#             r'\s+in\s+([A-Za-z°µ²³⁻⁺]+)',  # "in Hz", "in μV", etc.
#             r'\s+\[([^\]]+)\]',  # [unit]
#             r'\s+\(([^)]+)\)',   # (unit)
#         ]
#         
#         for pattern in unit_patterns:
#             match = re.search(pattern, text)
#             if match:
#                 unit = match.group(1)
#                 # Replace with standardized format
#                 text = re.sub(pattern, f' ({unit})', text)
#                 break
#     
#     elif unit_style == "brackets":
#         # Convert parentheses to brackets
#         text = re.sub(r'\s*\(([^)]+)\)', r' [\1]', text)
#     
#     # Clean up multiple spaces
#     text = re.sub(r'\s+', ' ', text).strip()
#     
#     return text
# 
# 
# def _capitalize_text(text: str) -> str:
#     """Capitalize the first letter of text, preserving units in parentheses/brackets."""
#     if not text:
#         return text
#     
#     # Preserve content in parentheses and brackets
#     preserved_sections = []
#     
#     # Find and preserve parentheses content
#     paren_pattern = r'(\([^)]+\))'
#     paren_matches = re.findall(paren_pattern, text)
#     for i, match in enumerate(paren_matches):
#         placeholder = f"__PAREN_{i}__"
#         preserved_sections.append((placeholder, match))
#         text = text.replace(match, placeholder, 1)
#     
#     # Find and preserve bracket content
#     bracket_pattern = r'(\[[^\]]+\])'
#     bracket_matches = re.findall(bracket_pattern, text)
#     for i, match in enumerate(bracket_matches):
#         placeholder = f"__BRACKET_{i}__"
#         preserved_sections.append((placeholder, match))
#         text = text.replace(match, placeholder, 1)
#     
#     # Capitalize the first alphabetic character
#     capitalized = False
#     result = []
#     for char in text:
#         if not capitalized and char.isalpha():
#             result.append(char.upper())
#             capitalized = True
#         else:
#             result.append(char)
#     
#     text = ''.join(result)
#     
#     # Restore preserved sections
#     for placeholder, original in preserved_sections:
#         text = text.replace(placeholder, original)
#     
#     return text
# 
# 
# def _format_scientific_notation(text: str) -> str:
#     """Format scientific notation in text."""
#     # Convert patterns like "1e-3" to "1×10⁻³" or LaTeX equivalent
#     sci_pattern = r'(\d+\.?\d*)[eE]([-+]?\d+)'
#     
#     def replace_sci(match):
#         base = match.group(1)
#         exp = match.group(2)
#         # Use LaTeX format
#         return f"{base}×10^{{{exp}}}"
#     
#     return re.sub(sci_pattern, replace_sci, text)
# 
# 
# def _replace_underscores(text: str) -> str:
#     """Replace underscores with spaces and apply proper word capitalization."""
#     # First, preserve content in parentheses and brackets
#     preserved_sections = []
#     
#     # Preserve parentheses content
#     paren_pattern = r'(\([^)]+\))'
#     paren_matches = re.findall(paren_pattern, text)
#     for i, match in enumerate(paren_matches):
#         placeholder = f"|||PAREN{i}|||"
#         preserved_sections.append((placeholder, match))
#         text = text.replace(match, placeholder, 1)
#     
#     # Preserve bracket content
#     bracket_pattern = r'(\[[^\]]+\])'
#     bracket_matches = re.findall(bracket_pattern, text)
#     for i, match in enumerate(bracket_matches):
#         placeholder = f"|||BRACKET{i}|||"
#         preserved_sections.append((placeholder, match))
#         text = text.replace(match, placeholder, 1)
#     
#     # Replace underscores with spaces
#     text_with_spaces = text.replace('_', ' ')
#     
#     # Split by spaces for word processing
#     words = text_with_spaces.split(' ')
#     
#     # Common units that should preserve their case
#     common_units = {'Hz', 'kHz', 'MHz', 'GHz', 'V', 'mV', 'uV', 'μV', 'A', 'mA', 
#                     'μA', 'W', 'mW', 'dB', 'dBm', 's', 'ms', 'μs', 'ns', 'ps',
#                     'K', 'C', 'F', 'rad', 'deg', 'm', 'cm', 'mm', 'μm', 'nm',
#                     'kg', 'g', 'mg', 'μg', 'N', 'Pa', 'bar', 'psi', 'mol', 'M'}
#     
#     # Process each word
#     formatted_words = []
#     for word in words:
#         if not word:  # Preserve empty strings (from consecutive underscores)
#             formatted_words.append('')
#         # Skip placeholders
#         elif '|||' in word:
#             formatted_words.append(word)
#         # Check if word is a known unit
#         elif word in common_units:
#             formatted_words.append(word)
#         # Preserve special cases (e.g., all caps like "DB", "ID", etc.)
#         elif word.isupper() and len(word) > 1:
#             formatted_words.append(word)
#         # Capitalize first letter of each word
#         else:
#             formatted_words.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
#     
#     # Join with spaces
#     result = ' '.join(formatted_words)
#     
#     # Restore preserved sections
#     for placeholder, original in preserved_sections:
#         result = result.replace(placeholder, original)
#     
#     return result
# 
# 
# def _normalize_unit(unit: str) -> str:
#     """Normalize unit string for comparison."""
#     # Remove brackets/parentheses and normalize
#     normalized = re.sub(r'[\[\]()]', '', unit).strip().lower()
#     
#     # Handle common equivalent units
#     equivalents = {
#         'sec': 's', 'second': 's', 'seconds': 's',
#         'volt': 'V', 'volts': 'V',
#         'amp': 'A', 'ampere': 'A', 'amps': 'A',
#         'meter': 'm', 'meters': 'm', 'metre': 'm', 'metres': 'm',
#         'gram': 'g', 'grams': 'g',
#         'hertz': 'Hz', 'hz': 'Hz',
#         'dimensionless': '1', 'unitless': '1', '': '1',
#     }
#     
#     return equivalents.get(normalized, normalized)
# 
# 
# # Convenient aliases and shortcuts
# def axis_label(label: str, unit: str = None, **kwargs) -> str:
#     """Convenient alias for format_axis_label."""
#     return format_axis_label(label, unit, **kwargs)
# 
# 
# def title(text: str, **kwargs) -> str:
#     """Convenient alias for format_title."""
#     return format_title(text, **kwargs)
# 
# 
# def scientific_text(text: str, **kwargs) -> str:
#     """Convenient alias for format_plot_text with scientific defaults."""
#     return format_plot_text(text, **kwargs)
# 
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_format_plot_text.py
# --------------------------------------------------------------------------------
