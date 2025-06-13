#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 00:10:00 (ywatanabe)"
# File: tests/scitex/str/test__format_plot_text_enhanced.py

"""
Enhanced tests for the updated format_plot_text module with underscore replacement
"""

import pytest
try:
    # Try importing from public API first
    from scitex.str import (
        format_plot_text,
        format_axis_label,
        format_title,
    )
except ImportError:
    # Fall back to module imports
    from scitex.str._format_plot_text import (
        format_plot_text,
        format_axis_label,
        format_title,
    )

# Import private functions directly
from scitex.str._format_plot_text import _replace_underscores


class TestUnderscoreReplacement:
    """Test the new underscore replacement functionality"""
    
    def test_basic_underscore_replacement(self):
        """Test basic underscore replacement"""
        assert format_plot_text("signal_power") == "Signal Power"
        assert format_plot_text("frequency_response") == "Frequency Response"
        assert format_plot_text("time_delay") == "Time Delay"
    
    def test_preserve_common_units(self):
        """Test preservation of common scientific units"""
        assert format_plot_text("signal_Hz") == "Signal Hz"
        assert format_plot_text("voltage_V") == "Voltage V"
        assert format_plot_text("time_ms") == "Time ms"
        assert format_plot_text("power_dB") == "Power dB"
        assert format_plot_text("angle_rad") == "Angle rad"
        assert format_plot_text("angle_deg") == "Angle deg"
    
    def test_preserve_acronyms(self):
        """Test preservation of all-caps acronyms"""
        assert format_plot_text("FFT_analysis") == "FFT Analysis"
        assert format_plot_text("EEG_data") == "EEG Data"
        assert format_plot_text("SNR_dB") == "SNR dB"
        assert format_plot_text("API_response") == "API Response"
        assert format_plot_text("CPU_usage") == "CPU Usage"
        assert format_plot_text("GPU_memory") == "GPU Memory"
    
    def test_mixed_case_scenarios(self):
        """Test mixed case scenarios"""
        assert format_plot_text("signal_SNR_dB") == "Signal SNR dB"
        assert format_plot_text("FFT_frequency_Hz") == "FFT Frequency Hz"
        assert format_plot_text("channel_01_EEG") == "Channel 01 EEG"
    
    def test_disable_underscore_replacement(self):
        """Test disabling underscore replacement"""
        assert format_plot_text("keep_underscores", replace_underscores=False) == "Keep_underscores"
        assert format_plot_text("DO_NOT_REPLACE", replace_underscores=False) == "DO_NOT_REPLACE"
    
    def test_empty_between_underscores(self):
        """Test handling of consecutive underscores"""
        # Note: Current implementation joins words with single spaces
        assert format_plot_text("test__double") == "Test Double"
        assert format_plot_text("test___triple") == "Test Triple"


class TestAxisLabelWithUnderscores:
    """Test axis label formatting with underscore replacement"""
    
    def test_axis_label_basic(self):
        """Test basic axis label with underscores"""
        assert format_axis_label("signal_power", "dB") == "Signal Power (dB)"
        assert format_axis_label("frequency_response", "Hz") == "Frequency Response (Hz)"
        assert format_axis_label("phase_angle", "rad") == "Phase Angle (rad)"
    
    def test_axis_label_with_units_in_name(self):
        """Test axis labels where unit is part of the name"""
        assert format_axis_label("signal_amplitude_uV") == "Signal Amplitude uV"
        assert format_axis_label("time_ms") == "Time ms"
        assert format_axis_label("frequency_Hz") == "Frequency Hz"
    
    def test_axis_label_bracket_style(self):
        """Test axis labels with bracket style"""
        assert format_axis_label("voltage_rms", "V", unit_style="brackets") == "Voltage Rms [V]"
        assert format_axis_label("current_peak", "A", unit_style="brackets") == "Current Peak [A]"
    
    def test_axis_label_disable_replacement(self):
        """Test disabling underscore replacement in axis labels"""
        result = format_axis_label("keep_underscore", "unit", replace_underscores=False)
        assert result == "Keep_underscore (unit)"


class TestTitleWithUnderscores:
    """Test title formatting with underscore replacement"""
    
    def test_title_basic(self):
        """Test basic title with underscores"""
        assert format_title("signal_processing_results") == "Signal Processing Results"
        assert format_title("frequency_domain_analysis") == "Frequency Domain Analysis"
        assert format_title("time_series_visualization") == "Time Series Visualization"
    
    def test_title_with_subtitle(self):
        """Test title with subtitle containing underscores"""
        result = format_title("main_analysis", "preliminary_results")
        assert result == "Main Analysis\\nPreliminary Results"
        
        result = format_title("FFT_analysis", "power_spectrum_dB")
        assert result == "FFT Analysis\\nPower Spectrum dB"
    
    def test_title_with_mixed_elements(self):
        """Test titles with mixed acronyms and units"""
        assert format_title("EEG_FFT_analysis_Hz") == "EEG FFT Analysis Hz"
        assert format_title("API_response_time_ms") == "API Response Time ms"
    
    def test_title_disable_replacement(self):
        """Test disabling underscore replacement in titles"""
        result = format_title("keep_underscores_here", replace_underscores=False)
        assert result == "Keep_underscores_here"


class TestReplaceUnderscoresHelper:
    """Test the _replace_underscores helper function directly"""
    
    def test_basic_replacement(self):
        """Test basic underscore replacement"""
        assert _replace_underscores("hello_world") == "Hello World"
        assert _replace_underscores("one_two_three") == "One Two Three"
    
    def test_unit_preservation(self):
        """Test that units are preserved"""
        assert _replace_underscores("value_Hz") == "Value Hz"
        assert _replace_underscores("power_dB") == "Power dB"
        assert _replace_underscores("time_ms") == "Time ms"
        assert _replace_underscores("voltage_mV") == "Voltage mV"
        assert _replace_underscores("current_μA") == "Current μA"
    
    def test_acronym_preservation(self):
        """Test that acronyms are preserved"""
        assert _replace_underscores("FFT") == "FFT"
        assert _replace_underscores("EEG") == "EEG"
        assert _replace_underscores("API") == "API"
        assert _replace_underscores("CPU") == "CPU"
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert _replace_underscores("") == ""
        assert _replace_underscores("_") == " "
        assert _replace_underscores("__") == "  "
        assert _replace_underscores("_start") == " Start"
        assert _replace_underscores("end_") == "End "


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    def test_dataframe_column_names(self):
        """Test formatting of typical DataFrame column names"""
        columns = [
            ("time_ms", "Time ms"),
            ("signal_amplitude_uV", "Signal Amplitude uV"),
            ("frequency_Hz", "Frequency Hz"),
            ("phase_angle_deg", "Phase Angle deg"),
            ("power_spectral_density_dB", "Power Spectral Density dB"),
            ("EEG_channel_01", "EEG Channel 01"),
            ("FFT_magnitude", "FFT Magnitude"),
        ]
        
        for input_text, expected in columns:
            assert format_plot_text(input_text) == expected
    
    def test_scientific_plot_labels(self):
        """Test common scientific plot labels"""
        labels = [
            ("normalized_power_spectrum", "Normalized Power Spectrum"),
            ("cross_correlation_coefficient", "Cross Correlation Coefficient"),
            ("signal_to_noise_ratio_dB", "Signal To Noise Ratio dB"),
            ("peak_to_peak_amplitude_mV", "Peak To Peak Amplitude mV"),
            ("RMS_voltage_V", "RMS Voltage V"),
        ]
        
        for input_text, expected in labels:
            assert format_plot_text(input_text) == expected
    
    def test_with_units_auto_detection(self):
        """Test with auto unit detection"""
        # Note: When replace_underscores is True, "in" becomes "In" before unit detection
        assert format_plot_text("frequency in Hz", unit_style="auto") == "Frequency In Hz"
        assert format_plot_text("voltage_in_V", unit_style="auto") == "Voltage In V"
        assert format_plot_text("time [ms]", unit_style="auto") == "Time (ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF