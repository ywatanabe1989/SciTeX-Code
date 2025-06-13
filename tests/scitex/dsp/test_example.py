import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex


class TestCalcNormResampleFiltHilbert:
    """Test calc_norm_resample_filt_hilbert function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.example, "calc_norm_resample_filt_hilbert")

    def test_basic_functionality(self):
        """Test basic functionality with demo signal."""
        # Generate demo signal
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=2, fs=1000, sig_type="chirp")
        
        # Apply function
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )
        
        # Check output structure
        assert isinstance(sigs, pd.DataFrame)
        assert sigs.index.name == "index"
        assert len(sigs.columns) > 10  # Should have multiple processing steps

    def test_output_columns(self):
        """Test that all expected columns are present."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=512)
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )
        
        expected_cols = [
            "orig",
            "z_normed",
            "minmax_normed",
            "resampled",
            "gaussian_noise_added",
            "white_noise_added",
            "pink_noise_added",
            "brown_noise_added",
            "hilbert_amp",
            "hilbert_pha"
        ]
        
        for col in expected_cols:
            assert any(col in c for c in sigs.columns), f"Missing column: {col}"

    def test_signal_shapes(self):
        """Test that signal shapes are preserved correctly."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=1024)
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )
        
        # Original signal shape
        orig_shape = sigs["orig"][0].shape
        
        # Most signals should preserve shape
        for col in ["z_normed", "minmax_normed", "hilbert_amp", "hilbert_pha"]:
            sig, _, _ = sigs[col]
            assert sig.shape == orig_shape, f"{col} shape mismatch"

    def test_resampling_shape(self):
        """Test resampled signal has correct shape."""
        src_fs = 1024
        tgt_fs = 512  # Default target in example
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=src_fs)
        
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )
        
        # Check resampled signal
        resampled_sig, resampled_tt, resampled_fs = sigs["resampled"]
        
        # Time dimension should be halved
        expected_samples = xx.shape[-1] // (src_fs // tgt_fs)
        assert resampled_sig.shape[-1] == expected_samples
        assert len(resampled_tt) == expected_samples
        assert resampled_fs == tgt_fs

    def test_tensorpac_signal(self):
        """Test handling of tensorpac signal type."""
        # Create 3D signal to simulate tensorpac
        xx_3d = np.random.randn(2, 10, 1000, 2)  # Extra dimension
        tt = np.linspace(0, 1, 1000)
        fs = 1000
        
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx_3d, tt, fs, sig_type="tensorpac", verbose=False
        )
        
        # Should extract first component
        assert sigs["orig"][0].shape == (2, 10, 1000)

    def test_filtering_parameters(self):
        """Test that filtering uses correct parameters."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=1000)
        
        # These are hardcoded in the example
        LOW_HZ = 20
        HIGH_HZ = 50
        
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )
        
        # Check column names contain correct frequencies
        bandpass_cols = [c for c in sigs.columns if "bandpass" in c]
        assert len(bandpass_cols) == 1
        assert f"{LOW_HZ}" in bandpass_cols[0]
        assert f"{HIGH_HZ}" in bandpass_cols[0]

    def test_verbose_output(self, capsys):
        """Test verbose output."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=0.5, fs=512)
        
        # With verbose=True
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=True
        )
        
        captured = capsys.readouterr()
        assert "Index" in captured.out or "index" in captured.out
        assert len(captured.out) > 0


class TestPlotSignals:
    """Test plot_signals function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.example, "plot_signals")

    @pytest.fixture
    def sample_sigs(self):
        """Create sample signals DataFrame for testing."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=512)
        return scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )

    def test_basic_plotting(self, sample_sigs):
        """Test basic plotting functionality."""
        fig = scitex.dsp.example.plot_signals(plt, sample_sigs, "chirp")
        
        # Check figure properties
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == len(sample_sigs.columns)
        assert fig._suptitle is not None
        assert fig._suptitle.get_text() == "chirp"

    def test_axes_properties(self, sample_sigs):
        """Test axes properties are set correctly."""
        fig = scitex.dsp.example.plot_signals(plt, sample_sigs, "test_signal")
        
        # Check all axes
        for ax in fig.axes:
            # Should have legend
            assert ax.get_legend() is not None
            
            # Should have data
            assert len(ax.lines) > 0
            
            # Should have xlim set
            xlim = ax.get_xlim()
            assert xlim[0] < xlim[1]

    def test_hilbert_amp_overlay(self, sample_sigs):
        """Test that hilbert_amp axis shows original signal too."""
        fig = scitex.dsp.example.plot_signals(plt, sample_sigs, "chirp")
        
        # Find hilbert_amp axis
        hilbert_ax = None
        for ax, col in zip(fig.axes, sample_sigs.columns):
            if col == "hilbert_amp":
                hilbert_ax = ax
                break
        
        assert hilbert_ax is not None
        # Should have 2 lines (original + hilbert)
        assert len(hilbert_ax.lines) == 2

    @pytest.mark.parametrize("sig_type", ["uniform", "gauss", "chirp"])
    def test_different_signal_types(self, sig_type):
        """Test plotting with different signal types."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=0.5, fs=256, sig_type=sig_type)
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type=sig_type, verbose=False
        )
        
        fig = scitex.dsp.example.plot_signals(plt, sigs, sig_type)
        
        assert fig._suptitle.get_text() == sig_type
        plt.close(fig)


class TestPlotWavelet:
    """Test plot_wavelet function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.example, "plot_wavelet")

    @pytest.fixture
    def sample_sigs(self):
        """Create sample signals DataFrame for testing."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=512)
        return scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )

    def test_basic_wavelet_plot(self, sample_sigs):
        """Test basic wavelet plotting functionality."""
        fig = scitex.dsp.example.plot_wavelet(
            plt, sample_sigs, "orig", "chirp"
        )
        
        # Should have 2 subplots
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 2

    def test_wavelet_plot_structure(self, sample_sigs):
        """Test wavelet plot has correct structure."""
        fig = scitex.dsp.example.plot_wavelet(
            plt, sample_sigs, "z_normed", "test"
        )
        
        # First axis: signal
        ax0 = fig.axes[0]
        assert len(ax0.lines) > 0
        assert ax0.get_ylabel() == "Voltage"
        
        # Second axis: spectrogram
        ax1 = fig.axes[1]
        assert len(ax1.images) > 0  # Should have imshow
        assert ax1.get_ylabel() == "Frequency [Hz]"
        assert ax1.yaxis_inverted()  # Should be inverted

    @pytest.mark.parametrize("sig_col", ["orig", "z_normed", "bandpass_filted (20 - 50 Hz)"])
    def test_different_signal_columns(self, sample_sigs, sig_col):
        """Test wavelet plot with different signal columns."""
        if sig_col not in sample_sigs.columns:
            # Find a bandpass column
            for col in sample_sigs.columns:
                if "bandpass" in col:
                    sig_col = col
                    break
        
        fig = scitex.dsp.example.plot_wavelet(
            plt, sample_sigs, sig_col, "test"
        )
        
        assert fig is not None
        plt.close(fig)


class TestPlotPSD:
    """Test plot_psd function."""

    def test_import(self):
        """Test function can be imported."""
        assert hasattr(scitex.dsp.example, "plot_psd")

    @pytest.fixture
    def sample_sigs(self):
        """Create sample signals DataFrame for testing."""
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=512)
        return scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, sig_type="chirp", verbose=False
        )

    def test_basic_psd_plot(self, sample_sigs):
        """Test basic PSD plotting functionality."""
        fig = scitex.dsp.example.plot_psd(
            plt, sample_sigs, "orig", "chirp"
        )
        
        # Should have 2 subplots
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 2

    def test_psd_plot_structure(self, sample_sigs):
        """Test PSD plot has correct structure."""
        fig = scitex.dsp.example.plot_psd(
            plt, sample_sigs, "minmax_normed", "test"
        )
        
        # First axis: signal
        ax0 = fig.axes[0]
        assert len(ax0.lines) > 0
        assert ax0.get_xlabel() == "Time [s]"
        assert ax0.get_ylabel() == "Voltage"
        
        # Second axis: PSD
        ax1 = fig.axes[1]
        assert len(ax1.lines) > 0
        assert ax1.get_xlabel() == "Frequency [Hz]"
        assert ax1.get_ylabel() == "Power [uV^2 / Hz]"
        assert ax1.get_yscale() == "log"  # Should be log scale

    def test_psd_with_filtered_signal(self, sample_sigs):
        """Test PSD plot with filtered signal."""
        # Find a filtered signal column
        filtered_col = None
        for col in sample_sigs.columns:
            if "filted" in col:
                filtered_col = col
                break
        
        assert filtered_col is not None
        
        fig = scitex.dsp.example.plot_psd(
            plt, sample_sigs, filtered_col, "filtered"
        )
        
        assert fig._suptitle.get_text() == "filtered"
        plt.close(fig)


class TestExampleIntegration:
    """Test the full example workflow."""

    def test_full_workflow(self, tmp_path):
        """Test the complete example workflow."""
        # Set up parameters
        T_SEC = 0.5  # Short for testing
        SIG_TYPES = ["chirp", "gauss"]
        SRC_FS = 512
        
        # Configure matplotlib
        plt.style.use('default')
        CC = {"blue": "blue", "red": "red"}  # Simple color config
        
        # Run workflow
        for sig_type in SIG_TYPES:
            # Generate signal
            xx, tt, fs = scitex.dsp.demo_sig(
                t_sec=T_SEC, fs=SRC_FS, sig_type=sig_type
            )
            
            # Process signal
            sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
                xx, tt, fs, sig_type, verbose=False
            )
            
            # Test plotting functions
            fig1 = scitex.dsp.example.plot_signals(plt, sigs, sig_type)
            assert fig1 is not None
            plt.close(fig1)
            
            # Test wavelet and PSD for one column
            fig2 = scitex.dsp.example.plot_wavelet(plt, sigs, "orig", sig_type)
            assert fig2 is not None
            plt.close(fig2)
            
            fig3 = scitex.dsp.example.plot_psd(plt, sigs, "orig", sig_type)
            assert fig3 is not None
            plt.close(fig3)

    def test_parameter_dependencies(self):
        """Test that hardcoded parameters work correctly."""
        # These are defined in the example
        LOW_HZ = 20
        HIGH_HZ = 50
        SIGMA = 10
        TGT_FS = 512
        
        xx, tt, fs = scitex.dsp.demo_sig(t_sec=1, fs=1024)
        sigs = scitex.dsp.example.calc_norm_resample_filt_hilbert(
            xx, tt, fs, "chirp", verbose=False
        )
        
        # Check resampling target
        assert sigs["resampled"][2] == TGT_FS
        
        # Check filter parameters in column names
        bandpass_col = [c for c in sigs.columns if "bandpass" in c][0]
        assert str(LOW_HZ) in bandpass_col
        assert str(HIGH_HZ) in bandpass_col
        
        # Check gaussian filter sigma
        gauss_col = [c for c in sigs.columns if "gauss" in c and "sigma" in c][0]
        assert str(SIGMA) in gauss_col


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/dsp/example.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-06 01:36:18 (ywatanabe)"
#
# import matplotlib
#
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
# import pandas as pd
#
#
# # Functions
# def calc_norm_resample_filt_hilbert(xx, tt, fs, sig_type, verbose=True):
#     sigs = {"index": ("signal", "time", "fs")}  # Collector
#
#     if sig_type == "tensorpac":
#         xx = xx[:, :, 0]
#
#     sigs[f"orig"] = (xx, tt, fs)
#
#     # Normalization
#     sigs["z_normed"] = (scitex.dsp.norm.z(xx), tt, fs)
#     sigs["minmax_normed"] = (scitex.dsp.norm.minmax(xx), tt, fs)
#
#     # Resampling
#     sigs["resampled"] = (
#         scitex.dsp.resample(xx, fs, TGT_FS),
#         tt[:: int(fs / TGT_FS)],
#         TGT_FS,
#     )
#
#     # Noise injection
#     sigs["gaussian_noise_added"] = (scitex.dsp.add_noise.gauss(xx), tt, fs)
#     sigs["white_noise_added"] = (scitex.dsp.add_noise.white(xx), tt, fs)
#     sigs["pink_noise_added"] = (scitex.dsp.add_noise.pink(xx), tt, fs)
#     sigs["brown_noise_added"] = (scitex.dsp.add_noise.brown(xx), tt, fs)
#
#     # Filtering
#     sigs[f"bandpass_filted ({LOW_HZ} - {HIGH_HZ} Hz)"] = (
#         scitex.dsp.filt.bandpass(xx, fs, low_hz=LOW_HZ, high_hz=HIGH_HZ),
#         tt,
#         fs,
#     )
#
#     sigs[f"bandstop_filted ({LOW_HZ} - {HIGH_HZ} Hz)"] = (
#         scitex.dsp.filt.bandstop(xx, fs, low_hz=LOW_HZ, high_hz=HIGH_HZ),
#         tt,
#         fs,
#     )
#     sigs[f"bandstop_gauss (sigma = {SIGMA})"] = (
#         scitex.dsp.filt.gauss(xx, sigma=SIGMA),
#         tt,
#         fs,
#     )
#
#     # Hilbert Transformation
#     pha, amp = scitex.dsp.hilbert(xx)
#     sigs["hilbert_amp"] = (amp, tt, fs)
#     sigs["hilbert_pha"] = (pha, tt, fs)
#
#     sigs = pd.DataFrame(sigs).set_index("index")
#
#     if verbose:
#         print(sigs.index)
#         print(sigs.columns)
#
#     return sigs
# ... (truncated for brevity)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/dsp/example.py
# --------------------------------------------------------------------------------
