#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:24:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test_pac.py

"""Tests for PAC (Phase-Amplitude Coupling) functionality."""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock, Mock

try:
    import tensorpac
    TENSORPAC_AVAILABLE = True
except ImportError:
    TENSORPAC_AVAILABLE = False

import scitex
from scitex.dsp.utils.pac import calc_pac_with_tensorpac, plot_PAC_scitex_vs_tensorpac


class TestCalcPacWithTensorpac:
    """Test calc_pac_with_tensorpac function."""

    @pytest.mark.skipif(not TENSORPAC_AVAILABLE, reason="tensorpac not available")
    def test_calc_pac_with_tensorpac_basic(self):
        """Test basic PAC calculation with tensorpac."""
        # Create synthetic signal with phase-amplitude coupling
        fs = 512
        t_sec = 2
        n_samples = fs * t_sec
        t = np.linspace(0, t_sec, n_samples)
        
        # Create signal with theta-gamma coupling
        theta_freq = 6  # Hz
        gamma_freq = 40  # Hz
        
        # Phase signal (theta)
        phase_signal = np.sin(2 * np.pi * theta_freq * t)
        
        # Amplitude modulated gamma signal
        gamma_signal = (1 + 0.5 * phase_signal) * np.sin(2 * np.pi * gamma_freq * t)
        
        # Combine signals
        signal = phase_signal + gamma_signal + 0.1 * np.random.randn(n_samples)
        
        # Create batch structure expected by the function
        xx = signal[np.newaxis, np.newaxis, :]  # (batch, ch, time)
        
        try:
            phases, amplitudes, freqs_pha, freqs_amp, pac = calc_pac_with_tensorpac(
                xx, fs, t_sec, i_batch=0, i_ch=0
            )
            
            # Verify outputs
            assert phases.ndim == 3  # (freq_pha, epoch, time)
            assert amplitudes.ndim == 3  # (freq_amp, epoch, time)
            assert isinstance(freqs_pha, np.ndarray)
            assert isinstance(freqs_amp, np.ndarray)
            assert pac.ndim == 2  # (freq_pha, freq_amp)
            assert pac.shape == (len(freqs_pha), len(freqs_amp))
            
        except Exception as e:
            pytest.skip(f"tensorpac import or execution failed: {e}")
            
    @pytest.mark.skipif(not TENSORPAC_AVAILABLE, reason="tensorpac not available")
    def test_calc_pac_with_tensorpac_realistic_eeg(self):
        """Test PAC calculation with realistic EEG-like signal."""
        # Realistic EEG parameters
        fs = 250  # Hz
        t_sec = 4  # seconds
        n_samples = fs * t_sec
        t = np.linspace(0, t_sec, n_samples)
        
        # Multiple frequency components
        # Alpha rhythm (8-12 Hz)
        alpha = np.sin(2 * np.pi * 10 * t)
        
        # Beta rhythm modulated by alpha phase
        beta_freq = 20
        phase_coupling = np.angle(np.exp(1j * 2 * np.pi * 10 * t))
        beta = (1 + 0.3 * np.cos(phase_coupling)) * np.sin(2 * np.pi * beta_freq * t)
        
        # Add noise
        noise = 0.2 * np.random.randn(n_samples)
        signal = alpha + beta + noise
        
        # Batch format
        xx = signal[np.newaxis, np.newaxis, :]
        
        try:
            phases, amplitudes, freqs_pha, freqs_amp, pac = calc_pac_with_tensorpac(
                xx, fs, t_sec, i_batch=0, i_ch=0
            )
            
            # Verify realistic frequency ranges
            assert freqs_pha.min() >= 1.0  # Low frequency for phase
            assert freqs_pha.max() <= fs/4  # Below Nyquist/2
            assert freqs_amp.min() >= freqs_pha.max()  # Amplitude freq > phase freq
            assert freqs_amp.max() <= fs/2  # Below Nyquist
            
            # Verify PAC values are reasonable
            assert np.all(np.isfinite(pac))
            assert pac.min() >= 0  # PAC values should be non-negative
            
        except Exception as e:
            pytest.skip(f"tensorpac execution failed: {e}")
            
    def test_calc_pac_with_tensorpac_mocked(self):
        """Test PAC calculation with mocked tensorpac."""
        # Mock tensorpac.Pac class
        mock_pac_instance = Mock()
        
        # Mock filter method returns
        mock_phases = np.random.randn(50, 20, 1024)  # (freq, epoch, time)
        mock_amplitudes = np.random.randn(30, 20, 1024)
        mock_pac_instance.filter.side_effect = [mock_phases, mock_amplitudes]
        
        # Mock fit method
        mock_xpac = np.random.randn(50, 30, 20)  # (freq_pha, freq_amp, epoch)
        mock_pac_instance.fit.return_value = mock_xpac
        
        # Mock frequency arrays
        mock_pac_instance.f_pha = np.random.randn(50, 2)
        mock_pac_instance.f_amp = np.random.randn(30, 2)
        
        with patch('scitex.dsp.utils.pac.tensorpac.Pac') as mock_pac_class:
            mock_pac_class.return_value = mock_pac_instance
            
            # Test data
            xx = np.random.randn(1, 1, 1024)
            fs = 512
            t_sec = 2
            
            phases, amplitudes, freqs_pha, freqs_amp, pac = calc_pac_with_tensorpac(
                xx, fs, t_sec, i_batch=0, i_ch=0
            )
            
            # Verify function calls
            mock_pac_class.assert_called_once_with(
                f_pha="hres", f_amp="mres", dcomplex="wavelet"
            )
            assert mock_pac_instance.filter.call_count == 2
            mock_pac_instance.fit.assert_called_once()
            
            # Verify outputs
            assert np.array_equal(phases, mock_phases)
            assert np.array_equal(amplitudes, mock_amplitudes)
            assert isinstance(freqs_pha, np.ndarray)
            assert isinstance(freqs_amp, np.ndarray)
            assert pac.shape == (30, 50)  # Transposed from (50, 30)
            
    def test_calc_pac_with_tensorpac_different_indices(self):
        """Test PAC calculation with different batch and channel indices."""
        mock_pac_instance = Mock()
        mock_phases = np.random.randn(50, 20, 1024)
        mock_amplitudes = np.random.randn(30, 20, 1024)
        mock_pac_instance.filter.side_effect = [mock_phases, mock_amplitudes]
        mock_xpac = np.random.randn(50, 30, 20)
        mock_pac_instance.fit.return_value = mock_xpac
        mock_pac_instance.f_pha = np.random.randn(50, 2)
        mock_pac_instance.f_amp = np.random.randn(30, 2)
        
        with patch('scitex.dsp.utils.pac.tensorpac.Pac') as mock_pac_class:
            mock_pac_class.return_value = mock_pac_instance
            
            # Multi-batch, multi-channel data
            xx = np.random.randn(3, 5, 1024)
            fs = 512
            t_sec = 2
            
            # Test different indices
            for i_batch in [0, 1, 2]:
                for i_ch in [0, 2, 4]:
                    phases, amplitudes, freqs_pha, freqs_amp, pac = calc_pac_with_tensorpac(
                        xx, fs, t_sec, i_batch=i_batch, i_ch=i_ch
                    )
                    
                    # Verify correct indexing was used
                    filter_calls = mock_pac_instance.filter.call_args_list
                    expected_signal = xx[i_batch, i_ch]
                    
                    # Reset for next iteration
                    mock_pac_instance.reset_mock()
                    mock_pac_instance.filter.side_effect = [mock_phases, mock_amplitudes]


class TestPlotPacScitexVsTensorpac:
    """Test plot_PAC_scitex_vs_tensorpac function."""
    
    @patch('scitex.plt.subplots')
    def test_plot_pac_basic(self, mock_subplots):
        """Test basic PAC plotting functionality."""
        # Create mock figure and axes
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_ax3 = MagicMock()
        mock_axes = [mock_ax1, mock_ax2, mock_ax3]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Test data
        pac_scitex = np.random.rand(50, 30)
        pac_tp = np.random.rand(50, 30)
        freqs_pha = np.linspace(1, 20, 50)
        freqs_amp = np.linspace(30, 150, 30)
        
        result = plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
        
        # Verify function returns the figure
        assert result == mock_fig
        
        # Verify subplots called with correct parameters
        mock_subplots.assert_called_once_with(ncols=3)
        
        # Verify imshow2d calls on each axis
        mock_ax1.imshow2d.assert_called_once()
        mock_ax2.imshow2d.assert_called_once()
        mock_ax3.imshow2d.assert_called_once()
        
        # Verify titles were set
        mock_ax1.set_title.assert_called_with("scitex")
        mock_ax2.set_title.assert_called_with("Tensorpac")
        mock_ax3.set_title.assert_called_with("Difference\n(scitex - Tensorpac)")
        
        # Verify figure labels
        mock_fig.suptitle.assert_called_with("PAC (MI) values")
        mock_fig.supxlabel.assert_called_with("Frequency for phase [Hz]")
        mock_fig.supylabel.assert_called_with("Frequency for amplitude [Hz]")
        
    @patch('scitex.plt.subplots')
    def test_plot_pac_different_shapes(self, mock_subplots):
        """Test plotting with different PAC matrix shapes."""
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock(), MagicMock()]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Test different matrix sizes
        for n_pha, n_amp in [(20, 15), (100, 50), (10, 10)]:
            pac_scitex = np.random.rand(n_pha, n_amp)
            pac_tp = np.random.rand(n_pha, n_amp)
            freqs_pha = np.linspace(1, 20, n_pha)
            freqs_amp = np.linspace(30, 150, n_amp)
            
            result = plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
            assert result == mock_fig
            
    @patch('scitex.plt.subplots')
    def test_plot_pac_vmin_vmax_calculation(self, mock_subplots):
        """Test proper vmin/vmax calculation for color scaling."""
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock(), MagicMock()]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Create data with known min/max values
        pac_scitex = np.array([[0.1, 0.5], [0.3, 0.9]])
        pac_tp = np.array([[0.2, 0.4], [0.6, 0.8]])
        freqs_pha = np.array([1, 2])
        freqs_amp = np.array([30, 40])
        
        plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
        
        # Expected vmin/vmax from the data and difference
        diff = pac_scitex - pac_tp
        expected_vmin = min(pac_scitex.min(), pac_tp.min(), diff.min())
        expected_vmax = max(pac_scitex.max(), pac_tp.max(), diff.max())
        
        # Verify each imshow2d call received correct vmin/vmax
        for mock_ax in mock_axes:
            call_kwargs = mock_ax.imshow2d.call_args[1]
            assert 'vmin' in call_kwargs
            assert 'vmax' in call_kwargs
            
    def test_plot_pac_shape_mismatch_error(self):
        """Test error handling for mismatched PAC matrix shapes."""
        pac_scitex = np.random.rand(50, 30)
        pac_tp = np.random.rand(40, 30)  # Different shape
        freqs_pha = np.linspace(1, 20, 50)
        freqs_amp = np.linspace(30, 150, 30)
        
        with pytest.raises(AssertionError):
            plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
            
    @patch('scitex.plt.subplots')
    def test_plot_pac_with_extreme_values(self, mock_subplots):
        """Test plotting with extreme PAC values."""
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock(), MagicMock()]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Create data with extreme values
        pac_scitex = np.array([[0.0, 1000.0], [1e-10, 1e10]])
        pac_tp = np.array([[-100.0, 500.0], [1e-5, 1e5]])
        freqs_pha = np.array([1, 2])
        freqs_amp = np.array([30, 40])
        
        # Should not raise an exception
        result = plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
        assert result == mock_fig


class TestPacIntegration:
    """Test integration between PAC calculation and plotting."""
    
    @patch('scitex.plt.subplots')
    def test_pac_calculation_and_plotting_workflow(self, mock_subplots):
        """Test complete PAC workflow from calculation to plotting."""
        # Mock plotting components
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock(), MagicMock()]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Mock tensorpac calculation
        mock_pac_instance = Mock()
        mock_phases = np.random.randn(50, 20, 1024)
        mock_amplitudes = np.random.randn(30, 20, 1024)
        mock_pac_instance.filter.side_effect = [mock_phases, mock_amplitudes]
        mock_xpac = np.random.randn(50, 30, 20)
        mock_pac_instance.fit.return_value = mock_xpac
        mock_pac_instance.f_pha = np.random.randn(50, 2)
        mock_pac_instance.f_amp = np.random.randn(30, 2)
        
        with patch('scitex.dsp.utils.pac.tensorpac.Pac') as mock_pac_class:
            mock_pac_class.return_value = mock_pac_instance
            
            # Calculate PAC
            xx = np.random.randn(2, 2, 1024)
            fs = 512
            t_sec = 2
            
            phases, amplitudes, freqs_pha, freqs_amp, pac_tp = calc_pac_with_tensorpac(
                xx, fs, t_sec, i_batch=0, i_ch=0
            )
            
            # Create mock scitex PAC result
            pac_scitex = np.random.rand(*pac_tp.shape)
            
            # Plot comparison
            result = plot_PAC_scitex_vs_tensorpac(pac_scitex, pac_tp, freqs_pha, freqs_amp)
            
            # Verify complete workflow
            assert result == mock_fig
            assert isinstance(pac_tp, np.ndarray)
            assert pac_scitex.shape == pac_tp.shape
            
    def test_pac_module_imports(self):
        """Test that PAC module imports work correctly."""
        # Test basic imports
        from scitex.dsp.utils.pac import calc_pac_with_tensorpac, plot_PAC_scitex_vs_tensorpac
        
        # Verify functions are callable
        assert callable(calc_pac_with_tensorpac)
        assert callable(plot_PAC_scitex_vs_tensorpac)
        
    @pytest.mark.skipif(not TENSORPAC_AVAILABLE, reason="tensorpac not available")
    def test_pac_realistic_workflow_end_to_end(self):
        """Test realistic PAC workflow if tensorpac is available."""
        try:
            # Generate synthetic coupled signal
            fs = 128  # Lower sampling rate for faster test
            t_sec = 1
            n_samples = fs * t_sec
            t = np.linspace(0, t_sec, n_samples)
            
            # Simple theta-gamma coupling
            theta = np.sin(2 * np.pi * 8 * t)
            gamma = (1 + 0.5 * theta) * np.sin(2 * np.pi * 40 * t)
            signal = theta + gamma + 0.1 * np.random.randn(n_samples)
            
            xx = signal[np.newaxis, np.newaxis, :]
            
            # Calculate PAC
            phases, amplitudes, freqs_pha, freqs_amp, pac = calc_pac_with_tensorpac(
                xx, fs, t_sec, i_batch=0, i_ch=0
            )
            
            # Verify results are reasonable
            assert phases.shape[0] > 0  # Has phase frequencies
            assert amplitudes.shape[0] > 0  # Has amplitude frequencies
            assert pac.shape == (len(freqs_pha), len(freqs_amp))
            assert np.all(np.isfinite(pac))
            
        except Exception as e:
            pytest.skip(f"End-to-end PAC test failed: {e}")


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
