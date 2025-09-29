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

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/utils/filter.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-03 07:24:43 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/utils/filter.py
# 
# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.signal import firwin, freqz
# 
# from ...decorators import numpy_fn
# from ...gen._to_even import to_even
# 
# 
# @numpy_fn
# def design_filter(sig_len, fs, low_hz=None, high_hz=None, cycle=3, is_bandstop=False):
#     """
#     Designs a Finite Impulse Response (FIR) filter based on the specified parameters.
# 
#     Arguments:
#     - sig_len (int): Length of the signal for which the filter is being designed.
#     - fs (int): Sampling frequency of the signal.
#     - low_hz (float, optional): Low cutoff frequency for the filter. Required for lowpass and bandpass filters.
#     - high_hz (float, optional): High cutoff frequency for the filter. Required for highpass and bandpass filters.
#     - cycle (int, optional): Number of cycles to use in determining the filter order. Defaults to 3.
#     - is_bandstop (bool, optional): Specifies if the filter should be a bandstop filter. Defaults to False.
# 
#     Returns:
#     - The coefficients of the designed FIR filter.
# 
#     Raises:
#     - FilterParameterError: If the provided parameters are invalid.
#     """
# 
#     class FilterParameterError(Exception):
#         """Custom exception for invalid filter parameters."""
# 
#         pass
# 
#     def estimate_filter_type(low_hz=None, high_hz=None, is_bandstop=False):
#         """
#         Estimates the filter type based on the provided low and high cutoff frequencies,
#         and whether a bandstop filter is desired. Raises an exception for invalid configurations.
#         """
#         if low_hz is not None and low_hz < 0:
#             raise FilterParameterError("low_hz must be non-negative.")
#         if high_hz is not None and high_hz < 0:
#             raise FilterParameterError("high_hz must be non-negative.")
#         if low_hz is not None and high_hz is not None and low_hz >= high_hz:
#             raise FilterParameterError(
#                 "low_hz must be less than high_hz for valid configurations."
#             )
# 
#         if low_hz is not None and high_hz is not None:
#             return "bandstop" if is_bandstop else "bandpass"
#         elif low_hz is not None:
#             return "lowpass"
#         elif high_hz is not None:
#             return "highpass"
#         else:
#             raise FilterParameterError(
#                 "At least one of low_hz or high_hz must be provided."
#             )
# 
#     def determine_cutoff_frequencies(filter_mode, low_hz, high_hz):
#         if filter_mode in ["lowpass", "highpass"]:
#             cutoff = low_hz if filter_mode == "lowpass" else high_hz
#         else:  # 'bandpass' or 'bandstop'
#             cutoff = [low_hz, high_hz]
#         return cutoff
# 
#     def determine_low_freq(filter_mode, low_hz, high_hz):
#         if filter_mode in ["lowpass", "bandstop"]:
#             low_freq = low_hz
#         else:  # 'highpass' or 'bandpass'
#             low_freq = high_hz if filter_mode == "highpass" else min(low_hz, high_hz)
#         return low_freq
# 
#     def determine_order(filter_mode, fs, low_freq, sig_len, cycle):
#         order = cycle * int((fs // low_freq))
#         if 3 * order < sig_len:
#             order = (sig_len - 1) // 3
#         order = to_even(order)
#         return order
# 
#     fs = int(fs)
#     low_hz = float(low_hz) if low_hz is not None else low_hz
#     high_hz = float(high_hz) if high_hz is not None else high_hz
#     filter_mode = estimate_filter_type(low_hz, high_hz, is_bandstop)
#     cutoff = determine_cutoff_frequencies(filter_mode, low_hz, high_hz)
#     low_freq = determine_low_freq(filter_mode, low_hz, high_hz)
#     order = determine_order(filter_mode, fs, low_freq, sig_len, cycle)
#     numtaps = order + 1
# 
#     try:
#         h = firwin(
#             numtaps=numtaps,
#             cutoff=cutoff,
#             pass_zero=(filter_mode in ["highpass", "bandstop"]),
#             window="hamming",
#             fs=fs,
#             scale=True,
#         )
#     except Exception as e:
#         print(e)
#         import ipdb
# 
#         ipdb.set_trace()
# 
#     return h
# 
# 
# @numpy_fn
# def plot_filter_responses(filter, fs, worN=8000, title=None):
#     """
#     Plots the impulse and frequency response of an FIR filter using numpy arrays.
# 
#     Parameters:
#     - filter_coeffs (numpy.ndarray): The filter coefficients as a numpy array.
#     - fs (int): The sampling frequency in Hz.
#     - title (str, optional): The title of the plot. Defaults to None.
# 
#     Returns:
#     - matplotlib.figure.Figure: The figure object containing the impulse and frequency response plots.
#     """
#     import scitex
# 
#     ww, hh = freqz(filter, worN=worN, fs=fs)
# 
#     fig, axes = scitex.plt.subplots(ncols=2)
#     fig.suptitle(title)
# 
#     # Impulse Responses of FIR Filter
#     ax = axes[0]
#     ax.plot(filter)
#     ax.set_title("Impulse Responses of FIR Filter")
#     ax.set_xlabel("Tap Number")
#     ax.set_ylabel("Amplitude")
# 
#     # Frequency Response of FIR Filter
#     ax = axes[1]
#     ax.plot(ww, 20 * np.log10(abs(hh) + 1e-5))
#     ax.set_title("Frequency Response of FIR Filter")
#     ax.set_xlabel("Frequency [Hz]")
#     ax.set_ylabel("Gain [dB]")
# 
#     return fig
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     # Example usage
#     xx, tt, fs = scitex.dsp.demo_sig()
#     batch_size, n_chs, seq_len = xx.shape
# 
#     lp_filter = design_filter(seq_len, fs, low_hz=30, high_hz=None)
#     hp_filter = design_filter(seq_len, fs, low_hz=None, high_hz=70)
#     bp_filter = design_filter(seq_len, fs, low_hz=30, high_hz=70)
#     bs_filter = design_filter(seq_len, fs, low_hz=30, high_hz=70, is_bandstop=True)
# 
#     fig = plot_filter_responses(lp_filter, fs, title="Lowpass Filter")
#     fig = plot_filter_responses(hp_filter, fs, title="Highpass Filter")
#     fig = plot_filter_responses(bp_filter, fs, title="Bandpass Filter")
#     fig = plot_filter_responses(bs_filter, fs, title="Bandstop Filter")
# 
#     # Figure
#     fig, axes = plt.subplots(nrows=4, ncols=2)
# 
#     # Time domain expressions??
#     axes[0, 0].plot(lp_filter, label="Lowpass Filter")
#     axes[1, 0].plot(hp_filter, label="Highpass Filter")
#     axes[2, 0].plot(bp_filter, label="Bandpass Filter")
#     axes[3, 0].plot(bs_filter, label="Bandstop Filter")
#     # fig.suptitle("Impulse Responses of FIR Filter")
#     # fig.supxlabel("Tap Number")
#     # fig.supylabel("Amplitude")
#     # fig.show()
# 
#     # Frequency response of the filters
#     w, h_lp = freqz(lp_filter, worN=8000, fs=fs)
#     w, h_hp = freqz(hp_filter, worN=8000, fs=fs)
#     w, h_bp = freqz(bp_filter, worN=8000, fs=fs)
#     w, h_bs = freqz(bs_filter, worN=8000, fs=fs)
# 
#     # Plotting the frequency response
#     axes[0, 1].plot(w, 20 * np.log10(abs(h_lp)), label="Lowpass Filter")
#     axes[1, 1].plot(w, 20 * np.log10(abs(h_hp)), label="Highpass Filter")
#     axes[2, 1].plot(w, 20 * np.log10(abs(h_bp)), label="Bandpass Filter")
#     axes[3, 1].plot(w, 20 * np.log10(abs(h_bs)), label="Bandstop Filter")
#     # plt.title("Frequency Response of FIR Filters")
#     # plt.xlabel("Frequency (Hz)")
#     # plt.ylabel("Gain (dB)")
#     # plt.grid(True)
#     # plt.legend(loc="best")
#     # plt.show()
#     fig.tight_layout()
#     plt.show()
# 
# # @torch_fn
# # def bandpass(x, filt):
# #     assert x.ndim == 3
# #     xf = F.conv1d(
# #         x.reshape(-1, x.shape[-1]).unsqueeze(1),
# #         filt.unsqueeze(0).unsqueeze(0),
# #         padding="same",
# #     ).reshape(*x.shape)
# #     assert x.shape == xf.shape
# #     return xf
# 
# # def define_bandpass_filters(seq_len, fs, freq_bands, cycle=3):
# #     """
# #     Defines Finite Impulse Response (FIR) filters.
# #     b: The filter coefficients (or taps) of the FIR filters
# #     a: The denominator coefficients of the filter's transfer function.  However, FIR filters have a transfer function with a denominator equal to 1 (since they are all-zero filters with no poles).
# #     """
# #     # Parameters
# #     n_freqs = len(freq_bands)
# #     nyq = fs / 2.0
# 
# #     bs = []
# #     for ll, hh in freq_bands:
# #         wn = np.array([ll, hh]) / nyq
# #         order = define_fir_order(fs, seq_len, ll, cycle=cycle)
# #         bs.append(fir1(order, wn)[0])
# #     return bs
# 
# # def define_fir_order(fs, sizevec, flow, cycle=3):
# #     """
# #     Calculate filter order.
# #     """
# #     if cycle is None:
# #         filtorder = 3 * np.fix(fs / flow)
# #     else:
# #         filtorder = cycle * (fs // flow)
# 
# #         if sizevec < 3 * filtorder:
# #             filtorder = (sizevec - 1) // 3
# 
# #     return int(filtorder)
# 
# # def n_odd_fcn(f, o, w, l):
# #     """Odd case."""
# #     # Variables :
# #     b0 = 0
# #     m = np.array(range(int(l + 1)))
# #     k = m[1 : len(m)]
# #     b = np.zeros(k.shape)
# 
# #     # Run Loop :
# #     for s in range(0, len(f), 2):
# #         m = (o[s + 1] - o[s]) / (f[s + 1] - f[s])
# #         b1 = o[s] - m * f[s]
# #         b0 = b0 + (
# #             b1 * (f[s + 1] - f[s])
# #             + m / 2 * (f[s + 1] * f[s + 1] - f[s] * f[s])
# #         ) * abs(np.square(w[round((s + 1) / 2)]))
# #         b = b + (
# #             m
# #             / (4 * np.pi * np.pi)
# #             * (
# #                 np.cos(2 * np.pi * k * f[s + 1])
# #                 - np.cos(2 * np.pi * k * f[s])
# #             )
# #             / (k * k)
# #         ) * abs(np.square(w[round((s + 1) / 2)]))
# #         b = b + (
# #             f[s + 1] * (m * f[s + 1] + b1) * np.sinc(2 * k * f[s + 1])
# #             - f[s] * (m * f[s] + b1) * np.sinc(2 * k * f[s])
# #         ) * abs(np.square(w[round((s + 1) / 2)]))
# 
# #     b = np.insert(b, 0, b0)
# #     a = (np.square(w[0])) * 4 * b
# #     a[0] = a[0] / 2
# #     aud = np.flipud(a[1 : len(a)]) / 2
# #     a2 = np.insert(aud, len(aud), a[0])
# #     h = np.concatenate((a2, a[1:] / 2))
# 
# #     return h
# 
# # def n_even_fcn(f, o, w, l):
# #     """Even case."""
# #     # Variables :
# #     k = np.array(range(0, int(l) + 1, 1)) + 0.5
# #     b = np.zeros(k.shape)
# 
# #     # # Run Loop :
# #     for s in range(0, len(f), 2):
# #         m = (o[s + 1] - o[s]) / (f[s + 1] - f[s])
# #         b1 = o[s] - m * f[s]
# #         b = b + (
# #             m
# #             / (4 * np.pi * np.pi)
# #             * (
# #                 np.cos(2 * np.pi * k * f[s + 1])
# #                 - np.cos(2 * np.pi * k * f[s])
# #             )
# #             / (k * k)
# #         ) * abs(np.square(w[round((s + 1) / 2)]))
# #         b = b + (
# #             f[s + 1] * (m * f[s + 1] + b1) * np.sinc(2 * k * f[s + 1])
# #             - f[s] * (m * f[s] + b1) * np.sinc(2 * k * f[s])
# #         ) * abs(np.square(w[round((s + 1) / 2)]))
# 
# #     a = (np.square(w[0])) * 4 * b
# #     h = 0.5 * np.concatenate((np.flipud(a), a))
# 
# #     return h
# 
# # def firls(n, f, o):
# #     # Variables definition :
# #     w = np.ones(round(len(f) / 2))
# #     n += 1
# #     f /= 2
# #     lo = (n - 1) / 2
# 
# #     nodd = bool(n % 2)
# 
# #     if nodd:  # Odd case
# #         h = n_odd_fcn(f, o, w, lo)
# #     else:  # Even case
# #         h = n_even_fcn(f, o, w, lo)
# 
# #     return h
# 
# # def fir1(n, wn):
# #     # Variables definition :
# #     nbands = len(wn) + 1
# #     ff = np.array((0, wn[0], wn[0], wn[1], wn[1], 1))
# 
# #     f0 = np.mean(ff[2:4])
# #     lo = n + 1
# 
# #     mags = np.array(range(nbands)).reshape(1, -1) % 2
# #     aa = np.ravel(np.tile(mags, (2, 1)), order="F")
# 
# #     # Get filter coefficients :
# #     h = firls(lo - 1, ff, aa)
# 
# #     # Apply a window to coefficients :
# #     wind = np.hamming(lo)
# #     b = h * wind
# #     c = np.exp(-1j * 2 * np.pi * (f0 / 2) * np.array(range(lo)))
# #     b /= abs(c @ b)
# 
# #     return b, 1
# 
# # def apply_filters(x, filts):
# #     """
# #     x: (batch_size, n_chs, seq_len)
# #     filts: (n_filts, seq_len_filt)
# #     """
# #     assert x.ndims == 3
# #     assert filts.ndims == 2
# #     batch_size, n_chs, n_time = x.shape
# #     x = x.reshape(-1, x.shape[-1]).unsqueeze(1)
# #     filts = filts.unsqueeze(1)
# #     n_filts = len(filts)
# #     return F.conv1d(x, filts, padding="same").reshape(
# #         batch_size, n_chs, n_filts, n_time
# #     )
# 
# # if __name__ == "__main__":
# #     import torch
# #     import torch.nn.functional as F
# 
# #     plt, CC = scitex.plt.configure_mpl(plt)
# 
# #     # Demo Signal
# #     freqs_hz = [10, 30, 100]
# #     xx, tt, fs = scitex.dsp.demo_sig(freqs_hz=freqs_hz, sig_type="periodic")
# #     x = xx
# 
# #     seq_len = x.shape[-1]
# #     freq_bands = np.array([[20, 70], [3.0, 4.0]])
# 
# #     # Plots the figure
# #     fig, ax = scitex.plt.subplots()
# #     # ax.plot(b, label="bandpass filter")
# 
# #     # Bandpass Filtering
# #     filters = define_bandpass_filters(seq_len, fs, freq_bands, cycle=3)
# #     i_filt = 0
# #     # xf = bandpass(xx, filters[i_filt])
# 
# #     # Plots the signals
# #     fig, axes = scitex.plt.subplots(nrows=2, sharex=True, sharey=True)
# #     axes[0].plot(tt, xx[0, 0], label="orig")
# #     axes[1].plot(tt, xf[0, 0], label="orig")
# #     [ax.legend(loc="upper left") for ax in axes]
# 
# #     # Plots PSDs
# #     psd_xx, ff_xx = scitex.dsp.psd(xx.numpy(), fs)
# #     psd_xf, ff_xf = scitex.dsp.psd(xf.numpy(), fs)
# 
# #     fig, axes = scitex.plt.subplots(nrows=2, sharex=True, sharey=True)
# #     axes[0].plot(ff_xx, psd_xx[0, 0], label="orig")
# #     axes[1].plot(ff_xf, psd_xf[0, 0], label="filted")
# #     [ax.legend(loc="upper left") for ax in axes]
# #     plt.show()
# 
# #     # Multiple Filters in a parallel computation
# #     x = torch.randn(33, 32, 30)
# #     filters = torch.randn(20, 5)
# 
# #     y = apply_filters(x, filters)
# #     print(y.shape)  # (33, 32, 20, 30)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/utils/filter.py
# --------------------------------------------------------------------------------
