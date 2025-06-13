#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:24:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test_filter.py

"""Tests for filter functionality."""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
from scipy.signal import freqz

import scitex
from scitex.dsp.utils.filter import design_filter, plot_filter_responses


class TestDesignFilter:
    """Test design_filter function."""

    def test_design_filter_lowpass(self):
        """Test lowpass filter design."""
        sig_len = 1000
        fs = 250
        low_hz = 30.0
        
        filter_coeffs = design_filter(sig_len, fs, low_hz=low_hz)
        
        assert isinstance(filter_coeffs, np.ndarray)
        assert len(filter_coeffs) > 0
        assert filter_coeffs.dtype in [np.float32, np.float64]
        
    def test_design_filter_highpass(self):
        """Test highpass filter design."""
        sig_len = 1000
        fs = 250
        high_hz = 70.0
        
        filter_coeffs = design_filter(sig_len, fs, high_hz=high_hz)
        
        assert isinstance(filter_coeffs, np.ndarray)
        assert len(filter_coeffs) > 0
        assert filter_coeffs.dtype in [np.float32, np.float64]
        
    def test_design_filter_bandpass(self):
        """Test bandpass filter design."""
        sig_len = 1000
        fs = 250
        low_hz = 8.0
        high_hz = 30.0
        
        filter_coeffs = design_filter(sig_len, fs, low_hz=low_hz, high_hz=high_hz)
        
        assert isinstance(filter_coeffs, np.ndarray)
        assert len(filter_coeffs) > 0
        assert filter_coeffs.dtype in [np.float32, np.float64]
        
    def test_design_filter_bandstop(self):
        """Test bandstop filter design."""
        sig_len = 1000
        fs = 250
        low_hz = 48.0
        high_hz = 52.0
        
        filter_coeffs = design_filter(
            sig_len, fs, low_hz=low_hz, high_hz=high_hz, is_bandstop=True
        )
        
        assert isinstance(filter_coeffs, np.ndarray)
        assert len(filter_coeffs) > 0
        assert filter_coeffs.dtype in [np.float32, np.float64]
        
    def test_design_filter_real_eeg_scenario(self):
        """Test filter design with realistic EEG parameters."""
        # Realistic EEG preprocessing scenario
        fs = 250  # Hz
        sig_len_sec = 4  # seconds
        sig_len = fs * sig_len_sec
        
        # Alpha band filter (8-12 Hz)
        alpha_filter = design_filter(sig_len, fs, low_hz=8.0, high_hz=12.0)
        
        # Beta band filter (13-30 Hz)
        beta_filter = design_filter(sig_len, fs, low_hz=13.0, high_hz=30.0)
        
        # Line noise notch filter (48-52 Hz)
        notch_filter = design_filter(
            sig_len, fs, low_hz=48.0, high_hz=52.0, is_bandstop=True
        )
        
        for filt in [alpha_filter, beta_filter, notch_filter]:
            assert isinstance(filt, np.ndarray)
            assert len(filt) > 0
            assert filt.dtype in [np.float32, np.float64]
            
    def test_design_filter_cycle_parameter(self):
        """Test different cycle parameter values."""
        sig_len = 1000
        fs = 250
        low_hz = 10.0
        
        for cycle in [1, 3, 5]:
            filter_coeffs = design_filter(sig_len, fs, low_hz=low_hz, cycle=cycle)
            assert isinstance(filter_coeffs, np.ndarray)
            assert len(filter_coeffs) > 0
            
    def test_design_filter_frequency_response(self):
        """Test filter frequency response characteristics."""
        sig_len = 2000
        fs = 500
        low_hz = 10.0
        high_hz = 50.0
        
        # Design bandpass filter
        bp_filter = design_filter(sig_len, fs, low_hz=low_hz, high_hz=high_hz)
        
        # Compute frequency response
        w, h = freqz(bp_filter, worN=1024, fs=fs)
        magnitude_db = 20 * np.log10(np.abs(h) + 1e-10)
        
        # Check passband has higher magnitude than stopband
        passband_idx = (w >= low_hz) & (w <= high_hz)
        stopband_low_idx = w < low_hz * 0.5
        stopband_high_idx = w > high_hz * 1.5
        
        if np.any(passband_idx) and np.any(stopband_low_idx):
            passband_mean = np.mean(magnitude_db[passband_idx])
            stopband_mean = np.mean(magnitude_db[stopband_low_idx])
            assert passband_mean > stopband_mean
            
    def test_design_filter_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very short signal
        short_filter = design_filter(sig_len=100, fs=250, low_hz=10.0)
        assert isinstance(short_filter, np.ndarray)
        assert len(short_filter) <= 100
        
        # High sampling rate
        high_fs_filter = design_filter(sig_len=1000, fs=2000, low_hz=100.0)
        assert isinstance(high_fs_filter, np.ndarray)
        
        # Low frequency cutoff
        low_freq_filter = design_filter(sig_len=2000, fs=250, low_hz=1.0)
        assert isinstance(low_freq_filter, np.ndarray)
        
    def test_design_filter_parameter_validation(self):
        """Test parameter validation and error handling."""
        sig_len = 1000
        fs = 250
        
        # Test missing parameters
        with pytest.raises(Exception):  # Should raise FilterParameterError
            design_filter(sig_len, fs)
            
        # Test negative frequencies
        with pytest.raises(Exception):
            design_filter(sig_len, fs, low_hz=-10.0)
            
        with pytest.raises(Exception):
            design_filter(sig_len, fs, high_hz=-10.0)
            
        # Test invalid frequency order
        with pytest.raises(Exception):
            design_filter(sig_len, fs, low_hz=50.0, high_hz=10.0)
            
    def test_design_filter_numpy_conversion(self):
        """Test numpy_fn decorator behavior."""
        # Test with different input types
        filter1 = design_filter(1000, 250, low_hz=10.0)
        filter2 = design_filter(1000.0, 250.0, low_hz=10.0)
        filter3 = design_filter(np.array([1000]), np.array([250]), low_hz=np.array([10.0]))
        
        for filt in [filter1, filter2, filter3]:
            assert isinstance(filt, np.ndarray)
            assert len(filt) > 0


class TestPlotFilterResponses:
    """Test plot_filter_responses function."""
    
    @patch('scitex.plt.subplots')
    def test_plot_filter_responses_basic(self, mock_subplots):
        """Test basic filter response plotting."""
        # Create mock figure and axes
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_axes = [mock_ax1, mock_ax2]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Create a simple filter
        filter_coeffs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
        fs = 250
        
        result = plot_filter_responses(filter_coeffs, fs)
        
        # Verify function returns the figure
        assert result == mock_fig
        
        # Verify plotting functions were called
        mock_ax1.plot.assert_called_once()
        mock_ax2.plot.assert_called_once()
        
        # Verify titles and labels were set
        mock_ax1.set_title.assert_called_with("Impulse Responses of FIR Filter")
        mock_ax1.set_xlabel.assert_called_with("Tap Number")
        mock_ax1.set_ylabel.assert_called_with("Amplitude")
        
        mock_ax2.set_title.assert_called_with("Frequency Response of FIR Filter")
        mock_ax2.set_xlabel.assert_called_with("Frequency [Hz]")
        mock_ax2.set_ylabel.assert_called_with("Gain [dB]")
        
    @patch('scitex.plt.subplots')
    def test_plot_filter_responses_with_title(self, mock_subplots):
        """Test plotting with custom title."""
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock()]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        filter_coeffs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
        fs = 250
        title = "Test Filter"
        
        plot_filter_responses(filter_coeffs, fs, title=title)
        
        mock_fig.suptitle.assert_called_with(title)
        
    @patch('scitex.plt.subplots')
    def test_plot_filter_responses_different_worN(self, mock_subplots):
        """Test plotting with different frequency resolution."""
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock()]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        filter_coeffs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
        fs = 250
        worN = 4000
        
        plot_filter_responses(filter_coeffs, fs, worN=worN)
        
        # Verify the function completed without error
        assert mock_subplots.called
        
    def test_plot_filter_responses_real_filter(self):
        """Test plotting with real filter design."""
        # Design a real filter
        sig_len = 1000
        fs = 250
        filter_coeffs = design_filter(sig_len, fs, low_hz=10.0, high_hz=40.0)
        
        # This should not raise an exception
        try:
            with patch('scitex.plt.subplots') as mock_subplots:
                mock_fig = MagicMock()
                mock_axes = [MagicMock(), MagicMock()]
                mock_subplots.return_value = (mock_fig, mock_axes)
                
                result = plot_filter_responses(filter_coeffs, fs)
                assert result == mock_fig
        except ImportError:
            # Skip if scitex.plt is not available
            pytest.skip("scitex.plt not available")
            
    def test_plot_filter_responses_numpy_conversion(self):
        """Test numpy_fn decorator behavior in plotting."""
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = [MagicMock(), MagicMock()]
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with different input types
            filter_coeffs = [0.1, 0.2, 0.4, 0.2, 0.1]
            fs = 250.0
            
            result = plot_filter_responses(filter_coeffs, fs)
            assert result == mock_fig


class TestFilterIntegration:
    """Test integration between filter design and plotting."""
    
    def test_design_and_plot_integration(self):
        """Test complete workflow from design to plotting."""
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = [MagicMock(), MagicMock()]
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Design filter
            sig_len = 1000
            fs = 250
            filter_coeffs = design_filter(sig_len, fs, low_hz=8.0, high_hz=30.0)
            
            # Plot responses
            result = plot_filter_responses(
                filter_coeffs, fs, title="Alpha-Beta Band Filter"
            )
            
            assert result == mock_fig
            assert isinstance(filter_coeffs, np.ndarray)
            
    def test_multiple_filter_types_workflow(self):
        """Test workflow with multiple filter types."""
        sig_len = 2000
        fs = 500
        
        # Design different filter types
        filters = {
            'lowpass': design_filter(sig_len, fs, low_hz=50.0),
            'highpass': design_filter(sig_len, fs, high_hz=1.0),
            'bandpass': design_filter(sig_len, fs, low_hz=8.0, high_hz=30.0),
            'bandstop': design_filter(
                sig_len, fs, low_hz=48.0, high_hz=52.0, is_bandstop=True
            )
        }
        
        # Verify all filters were designed successfully
        for filter_type, filter_coeffs in filters.items():
            assert isinstance(filter_coeffs, np.ndarray)
            assert len(filter_coeffs) > 0
            
            # Test plotting each filter
            with patch('scitex.plt.subplots') as mock_subplots:
                mock_fig = MagicMock()
                mock_axes = [MagicMock(), MagicMock()]
                mock_subplots.return_value = (mock_fig, mock_axes)
                
                result = plot_filter_responses(
                    filter_coeffs, fs, title=f"{filter_type.title()} Filter"
                )
                assert result == mock_fig


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
