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
    pytest.main([__file__])


# EOF