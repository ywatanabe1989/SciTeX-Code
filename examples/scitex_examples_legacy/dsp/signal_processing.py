#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 Current"
# File: ./examples/scitex/dsp/signal_processing.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/dsp/signal_processing.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates signal processing capabilities
  - Shows filtering, spectral analysis, and PAC

Dependencies:
  - packages: numpy, matplotlib, scitex

IO:
  - output-files: output/signals/*.pkl, output/plots/*.png, output/reports/*.md
"""

"""Imports"""
import os
import sys
import argparse
import numpy as np


def generate_synthetic_signals():
    """Generate synthetic neural-like signals for demonstration"""
    import scitex

    print("\n" + "=" * 50)
    print("1. Generating Synthetic Signals")
    print("=" * 50)

    # Parameters
    fs = 1000  # Sampling frequency (Hz)
    duration = 5  # Duration (seconds)
    t = np.arange(0, duration, 1 / fs)

    # Create a complex signal with multiple frequency components
    # Theta (4-8 Hz)
    theta = 2 * np.sin(2 * np.pi * 6 * t)

    # Alpha (8-12 Hz)
    alpha = 1.5 * np.sin(2 * np.pi * 10 * t)

    # Beta (12-30 Hz)
    beta = 0.8 * np.sin(2 * np.pi * 20 * t)

    # Gamma (30-100 Hz) - modulated by theta phase
    theta_3d = scitex.dsp.ensure_3d(theta)
    theta_phase = np.angle(scitex.dsp.hilbert(theta_3d)[0][0, 0, :])
    gamma_amplitude = 0.5 * (1 + 0.5 * np.sin(theta_phase))
    gamma = gamma_amplitude * np.sin(2 * np.pi * 50 * t)

    # Combine signals and add noise
    signal = theta + alpha + beta + gamma
    noise = 0.5 * np.random.randn(len(t))
    noisy_signal = signal + noise

    # Create multi-channel data (simulate 4 channels)
    multi_channel = np.array(
        [
            noisy_signal,
            0.8 * noisy_signal + 0.2 * np.random.randn(len(t)),
            0.7 * noisy_signal + 0.3 * np.random.randn(len(t)),
            0.9 * noisy_signal + 0.1 * np.random.randn(len(t)),
        ]
    )

    print(f"Generated signal shape: {noisy_signal.shape}")
    print(f"Multi-channel shape: {multi_channel.shape}")
    print(f"Sampling rate: {fs} Hz")
    print(f"Duration: {duration} seconds")

    # Save raw signals
    scitex.io.save(
        {
            "time": t,
            "clean_signal": signal,
            "noisy_signal": noisy_signal,
            "multi_channel": multi_channel,
            "fs": fs,
        },
        "signals/synthetic_signals.pkl",
    )

    return t, signal, noisy_signal, multi_channel, fs


def demonstrate_filtering(signal, fs):
    """Demonstrate various filtering operations"""
    import scitex
    import matplotlib.pyplot as plt

    print("\n" + "=" * 50)
    print("2. Signal Filtering")
    print("=" * 50)

    # Ensure signal is 3D for scitex.dsp functions
    signal_3d = scitex.dsp.ensure_3d(signal)  # Shape: (1, 1, n_samples)

    # Bandpass filter for alpha band (8-12 Hz)
    alpha_filtered = scitex.dsp.filt.bandpass(
        signal_3d, fs=fs, bands=[[8, 12]]  # 2D array for batch dimension
    )

    # Lowpass filter (remove high frequencies)
    lowpass_filtered = scitex.dsp.filt.lowpass(
        signal_3d, fs=fs, cutoffs_hz=np.array([30])  # Must be array
    )

    # Highpass filter (remove low frequencies)
    highpass_filtered = scitex.dsp.filt.highpass(
        signal_3d,
        fs=fs,
        cutoffs_hz=np.array([1]),  # Must be array, and parameter name is cutoffs_hz
    )

    # Create figure showing filtering effects
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    fig.suptitle("Signal Filtering Examples")

    # Plot original
    axes[0].plot(signal[:1000])  # First second
    axes[0].set_title("Original Signal")
    axes[0].set_ylabel("Amplitude")

    # Plot alpha band
    axes[1].plot(alpha_filtered[0, 0, :1000])
    axes[1].set_title("Alpha Band (8-12 Hz)")
    axes[1].set_ylabel("Amplitude")

    # Plot lowpass
    axes[2].plot(lowpass_filtered[0, 0, :1000])
    axes[2].set_title("Lowpass Filtered (< 30 Hz)")
    axes[2].set_ylabel("Amplitude")

    # Plot highpass
    axes[3].plot(highpass_filtered[0, 0, :1000])
    axes[3].set_title("Highpass Filtered (> 1 Hz)")
    axes[3].set_ylabel("Amplitude")
    axes[3].set_xlabel("Time (ms)")

    plt.tight_layout()
    scitex.io.save(fig, "plots/filtering_examples.png")
    plt.close()

    print("Filtered signals saved to plots/filtering_examples.png")

    return alpha_filtered[0, 0, :]


def demonstrate_psd_analysis(signal, fs):
    """Power Spectral Density analysis"""
    import scitex
    import matplotlib.pyplot as plt

    print("\n" + "=" * 50)
    print("3. Power Spectral Density (PSD)")
    print("=" * 50)

    # Calculate PSD
    signal_3d = scitex.dsp.ensure_3d(signal)
    psd, freqs = scitex.dsp.psd(signal_3d, fs=fs)  # Returns psd first, then freqs

    # Plot PSD
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(freqs, psd[0, 0, :])
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power Spectral Density")
    ax.set_title("Power Spectral Density")
    ax.set_xlim([0, 100])
    ax.grid(True, alpha=0.3)

    # Mark frequency bands
    bands = {
        "Delta": (0.5, 4),
        "Theta": (4, 8),
        "Alpha": (8, 12),
        "Beta": (12, 30),
        "Gamma": (30, 100),
    }

    for i, (band, (low, high)) in enumerate(bands.items()):
        ax.axvspan(low, high, alpha=0.2, color=f"C{i}", label=band)

    ax.legend()
    scitex.io.save(fig, "plots/psd_analysis.png")
    plt.close()

    print("PSD analysis saved to plots/psd_analysis.png")

    # Calculate band powers
    band_powers = {}
    for band, (low, high) in bands.items():
        mask = (freqs >= low) & (freqs < high)
        band_powers[band] = float(
            np.mean(psd[0, 0, mask])
        )  # Convert to Python float for JSON

    print("\nBand Powers:")
    for band, power in band_powers.items():
        print(f"  {band}: {power:.2e}")

    scitex.io.save(band_powers, "analysis/band_powers.json")

    return freqs, psd


def demonstrate_wavelet_analysis(signal, fs):
    """Wavelet analysis for time-frequency representation"""
    import scitex
    import matplotlib.pyplot as plt

    print("\n" + "=" * 50)
    print("4. Wavelet Analysis")
    print("=" * 50)

    # Prepare signal
    signal_3d = scitex.dsp.ensure_3d(signal)

    # Compute wavelet transform
    # Note: wavelet function automatically generates frequencies up to Nyquist
    pha, amp, freqs = scitex.dsp.wavelet(
        signal_3d,
        fs=fs,
        freq_scale="log",  # 'linear' or 'log'
        out_scale="linear",  # 'linear' or 'log'
    )

    # Reconstruct complex wavelet transform for visualization
    cwt = amp * np.exp(1j * pha)

    # Extract power
    power = np.abs(cwt) ** 2

    # Plot time-frequency representation
    fig, ax = plt.subplots(figsize=(12, 8))

    # Take first 2 seconds for clarity
    time_mask = slice(0, 2 * fs)
    t = np.arange(power.shape[-1]) / fs

    # Get frequency array from first batch/channel
    freq_array = (
        freqs[0, 0, :].cpu().numpy() if hasattr(freqs, "cpu") else freqs[0, 0, :]
    )

    # Only plot frequencies up to 80 Hz
    freq_mask = freq_array <= 80

    im = ax.contourf(
        t[time_mask],
        freq_array[freq_mask],
        power[0, 0, freq_mask, :][:, time_mask],
        levels=20,
        cmap="viridis",
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("Wavelet Time-Frequency Representation")
    ax.set_yscale("log")

    plt.colorbar(im, ax=ax, label="Power")
    scitex.io.save(fig, "plots/wavelet_analysis.png")
    plt.close()

    print("Wavelet analysis saved to plots/wavelet_analysis.png")

    return cwt


def demonstrate_hilbert_transform(signal, fs):
    """Hilbert transform for instantaneous phase and amplitude"""
    import scitex
    import matplotlib.pyplot as plt

    print("\n" + "=" * 50)
    print("5. Hilbert Transform")
    print("=" * 50)

    # Filter signal to alpha band
    signal_3d = scitex.dsp.ensure_3d(signal)
    alpha_signal = scitex.dsp.filt.bandpass(signal_3d, fs=fs, bands=[[8, 12]])

    # Ensure alpha_signal is 3D and extract first trial/channel
    if alpha_signal.ndim == 2 and alpha_signal.shape[0] == 1:
        # Shape is (1, timepoints), reshape to (1, 1, timepoints)
        alpha_signal = alpha_signal[np.newaxis, :, :]

    # Compute Hilbert transform
    phase, amplitude = scitex.dsp.hilbert(alpha_signal)

    # Plot results
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle("Hilbert Transform Analysis (Alpha Band)")

    # Time window for visualization
    t = np.arange(1000) / fs  # First second

    # Get the signal for plotting (handle different shapes)
    # Squeeze unnecessary dimensions and get first 1000 samples
    alpha_signal_squeezed = np.squeeze(alpha_signal)
    amplitude_squeezed = np.squeeze(amplitude)
    phase_squeezed = np.squeeze(phase)

    # Ensure we have at least 1D
    if alpha_signal_squeezed.ndim == 0:
        alpha_signal_squeezed = alpha_signal_squeezed.reshape(1)
        amplitude_squeezed = amplitude_squeezed.reshape(1)
        phase_squeezed = phase_squeezed.reshape(1)

    # Get first 1000 samples
    plot_signal = alpha_signal_squeezed[:1000]
    plot_amplitude = amplitude_squeezed[:1000]
    plot_phase = phase_squeezed[:1000]

    # Original signal
    axes[0].plot(t, plot_signal, "b-")
    axes[0].set_ylabel("Signal")
    axes[0].set_title("Filtered Signal (8-12 Hz)")

    # Instantaneous amplitude
    axes[1].plot(t, plot_amplitude, "r-")
    axes[1].set_ylabel("Amplitude")
    axes[1].set_title("Instantaneous Amplitude")

    # Instantaneous phase
    axes[2].plot(t, plot_phase, "g-")
    axes[2].set_ylabel("Phase (rad)")
    axes[2].set_xlabel("Time (s)")
    axes[2].set_title("Instantaneous Phase")
    axes[2].set_ylim([-np.pi, np.pi])

    plt.tight_layout()
    scitex.io.save(fig, "plots/hilbert_transform.png")
    plt.close()

    print("Hilbert transform analysis saved to plots/hilbert_transform.png")

    return phase, amplitude


def demonstrate_pac_analysis(signal, fs):
    """Phase-Amplitude Coupling (PAC) analysis"""
    import scitex
    import matplotlib.pyplot as plt

    print("\n" + "=" * 50)
    print("6. Phase-Amplitude Coupling (PAC)")
    print("=" * 50)

    # Prepare signal
    signal_3d = scitex.dsp.ensure_3d(signal)

    # Calculate PAC between theta phase and gamma amplitude
    pac_value = scitex.dsp.pac(
        signal_3d,
        fs=fs,
        pha_start_hz=4,  # Theta start
        pha_end_hz=8,  # Theta end
        pha_n_bands=1,  # Just one band
        amp_start_hz=30,  # Gamma start
        amp_end_hz=80,  # Gamma end
        amp_n_bands=1,  # Just one band
    )

    # pac_value might be a tuple or array, handle accordingly
    if isinstance(pac_value, tuple):
        pac_val = pac_value[0]
    else:
        pac_val = pac_value

    # Squeeze and get scalar value
    pac_val = np.squeeze(pac_val)
    if hasattr(pac_val, "item"):
        pac_val = pac_val.item()

    print(f"PAC value (Theta-Gamma): {pac_val:.4f}")

    # Calculate PAC matrix across multiple frequency pairs
    phase_bands = [(4, 8), (8, 12), (12, 20)]  # Theta, Alpha, Beta
    amp_bands = [(30, 50), (50, 80), (80, 100)]  # Low, Mid, High Gamma

    pac_matrix = np.zeros((len(phase_bands), len(amp_bands)))

    for i, (p_start, p_end) in enumerate(phase_bands):
        for j, (a_start, a_end) in enumerate(amp_bands):
            pac_result = scitex.dsp.pac(
                signal_3d,
                fs=fs,
                pha_start_hz=p_start,
                pha_end_hz=p_end,
                pha_n_bands=1,
                amp_start_hz=a_start,
                amp_end_hz=a_end,
                amp_n_bands=1,
            )
            # Handle pac_result which might be a tuple or array
            if isinstance(pac_result, tuple):
                pac_res = pac_result[0]
            else:
                pac_res = pac_result

            # Squeeze and get scalar value
            pac_res = np.squeeze(pac_res)
            if hasattr(pac_res, "item"):
                pac_res = pac_res.item()

            pac_matrix[i, j] = pac_res

    # Plot PAC matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(pac_matrix, cmap="hot", aspect="auto")

    # Labels
    phase_labels = ["Theta\n(4-8 Hz)", "Alpha\n(8-12 Hz)", "Beta\n(12-20 Hz)"]
    amp_labels = [
        "Low Gamma\n(30-50 Hz)",
        "Mid Gamma\n(50-80 Hz)",
        "High Gamma\n(80-100 Hz)",
    ]

    ax.set_xticks(range(len(amp_labels)))
    ax.set_xticklabels(amp_labels, rotation=45, ha="right")
    ax.set_yticks(range(len(phase_labels)))
    ax.set_yticklabels(phase_labels)

    ax.set_xlabel("Amplitude Frequency")
    ax.set_ylabel("Phase Frequency")
    ax.set_title("Phase-Amplitude Coupling Matrix")

    # Add colorbar
    plt.colorbar(im, ax=ax, label="PAC Strength (MI)")

    # Add values to cells
    for i in range(len(phase_bands)):
        for j in range(len(amp_bands)):
            text = ax.text(
                j,
                i,
                f"{pac_matrix[i, j]:.3f}",
                ha="center",
                va="center",
                color="white" if pac_matrix[i, j] > 0.01 else "black",
            )

    plt.tight_layout()
    scitex.io.save(fig, "plots/pac_analysis.png")
    plt.close()

    print("PAC analysis saved to plots/pac_analysis.png")

    return pac_matrix


def demonstrate_multi_channel_processing(multi_channel, fs):
    """Processing multi-channel data"""
    import scitex
    import matplotlib.pyplot as plt

    print("\n" + "=" * 50)
    print("7. Multi-Channel Processing")
    print("=" * 50)

    # Ensure correct shape (n_channels, 1, n_samples)
    n_channels, n_samples = multi_channel.shape
    multi_3d = multi_channel.reshape(n_channels, 1, n_samples)

    # Apply common average reference
    referenced = scitex.dsp.reference.common_average(multi_3d)

    # Calculate channel-wise PSD
    freqs, psds = scitex.dsp.psd(referenced, fs=fs)

    # Plot multi-channel PSD
    fig, ax = plt.subplots(figsize=(10, 6))

    # Handle different output shapes for freqs
    if freqs.ndim == 3:
        # Extract 1D frequency array from 3D shape
        freq_1d = freqs[0, 0, :]
    elif freqs.ndim == 2:
        freq_1d = freqs[0, :]
    else:
        freq_1d = freqs

    # Handle different PSD output shapes
    if psds.ndim == 3:
        # Shape is (n_channels, 1, n_freqs)
        for ch in range(n_channels):
            ax.semilogy(freq_1d, psds[ch, 0, :], label=f"Channel {ch+1}")
    elif psds.ndim == 2:
        # Shape is (n_channels, n_freqs)
        for ch in range(n_channels):
            ax.semilogy(freq_1d, psds[ch, :], label=f"Channel {ch+1}")
    else:
        # Single channel
        ax.semilogy(freq_1d, psds, label="Channel 1")

    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power Spectral Density")
    ax.set_title("Multi-Channel PSD Comparison")
    ax.set_xlim([0, 100])
    ax.legend()
    ax.grid(True, alpha=0.3)

    scitex.io.save(fig, "plots/multichannel_psd.png")
    plt.close()

    print("Multi-channel analysis saved to plots/multichannel_psd.png")

    return referenced


def demonstrate_advanced_features(signal, fs):
    """Advanced DSP features"""
    import scitex

    print("\n" + "=" * 50)
    print("8. Advanced Features")
    print("=" * 50)

    # Signal resampling
    new_fs = 250  # Downsample to 250 Hz
    signal_3d = scitex.dsp.ensure_3d(signal)
    resampled = scitex.dsp.resample(signal_3d, src_fs=fs, tgt_fs=new_fs)

    print(f"Original shape: {signal_3d.shape}")
    print(f"Resampled shape: {resampled.shape}")
    print(f"Original fs: {fs} Hz, New fs: {new_fs} Hz")

    # Signal normalization
    normalized = scitex.dsp.norm(signal_3d, axis=-1)

    # Modulation index calculation
    # Get phase and amplitude for specific bands
    phase_signal = scitex.dsp.filt.bandpass(signal_3d, fs=fs, bands=[[4, 8]])
    amp_signal = scitex.dsp.filt.bandpass(signal_3d, fs=fs, bands=[[30, 80]])

    phase, _ = scitex.dsp.hilbert(phase_signal)
    _, amplitude = scitex.dsp.hilbert(amp_signal)

    mi = scitex.dsp.modulation_index(phase[0, 0, :], amplitude[0, 0, :], n_bins=18)
    print(f"Modulation Index: {mi:.4f}")

    # Save processed signals
    scitex.io.save(
        {"resampled": resampled, "normalized": normalized, "modulation_index": mi},
        "signals/advanced_features.pkl",
    )

    return resampled, normalized, mi


"""Functions & Classes"""


def main(args):
    """Run all DSP demonstrations"""
    import scitex

    print("\nSciTeX DSP Module Demonstration")
    print("=============================")

    # Generate signals
    t, clean_signal, noisy_signal, multi_channel, fs = generate_synthetic_signals()

    # Run demonstrations
    alpha_filtered = demonstrate_filtering(noisy_signal, fs)
    freqs, psd = demonstrate_psd_analysis(noisy_signal, fs)
    cwt = demonstrate_wavelet_analysis(noisy_signal, fs)
    phase, amplitude = demonstrate_hilbert_transform(noisy_signal, fs)
    pac_matrix = demonstrate_pac_analysis(clean_signal, fs)  # Use clean for better PAC
    referenced = demonstrate_multi_channel_processing(multi_channel, fs)
    resampled, normalized, mi = demonstrate_advanced_features(noisy_signal, fs)

    # Create summary report
    report = f"""
# SciTeX DSP Module - Example Summary

## Generated Outputs:

### Signals:
- synthetic_signals.pkl: Raw generated signals
- advanced_features.pkl: Processed signal examples

### Plots:
- filtering_examples.png: Comparison of different filters
- psd_analysis.png: Power spectral density with frequency bands
- wavelet_analysis.png: Time-frequency representation
- hilbert_transform.png: Instantaneous phase and amplitude
- pac_analysis.png: Phase-amplitude coupling matrix
- multichannel_psd.png: Multi-channel spectral comparison

### Analysis:
- band_powers.json: Power in each frequency band

## Key Functions Demonstrated:

1. **Filtering**:
   - bandpass(): Extract specific frequency bands
   - lowpass(): Remove high frequencies
   - highpass(): Remove low frequencies

2. **Spectral Analysis**:
   - psd(): Power spectral density estimation
   - wavelet(): Time-frequency decomposition

3. **Phase Analysis**:
   - hilbert(): Extract instantaneous phase and amplitude
   - pac(): Phase-amplitude coupling
   - modulation_index(): Quantify phase-amplitude relationships

4. **Signal Processing**:
   - ensure_3d(): Format signals for processing
   - resample(): Change sampling rate
   - norm(): Normalize signals
   - reference(): Apply referencing to multi-channel data

## Applications:
- EEG/MEG analysis
- Neural oscillation studies
- Signal quality assessment
- Cross-frequency coupling analysis
- Time-frequency visualization
"""

    scitex.io.save(report, "reports/dsp_examples_summary.md")
    print("\n" + "=" * 50)
    print("Summary report saved to: output/reports/dsp_examples_summary.md")
    print("All outputs saved to: output/")
    print("=" * 50)

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="DSP module examples")
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    # Start scitex framework
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    # Main
    exit_status = main(args)

    # Close the scitex framework
    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
