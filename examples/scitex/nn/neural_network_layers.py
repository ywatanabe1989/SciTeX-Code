#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 (ywatanabe)"
# File: ./examples/scitex/nn/neural_network_layers.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/nn/neural_network_layers.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates custom neural network layers in scitex.nn
  - Shows signal processing layers (filters, transforms)
  - Implements augmentation layers for training
  - Provides analysis layers (PSD, PAC, wavelets)
  - Integrates seamlessly with PyTorch models

Dependencies:
  - scripts: None
  - packages: torch, numpy, matplotlib, scitex

IO:
  - input-files: None
  - output-files:
    - neural_network_layers_out/demo_signal.png
    - neural_network_layers_out/filter_responses.png
    - neural_network_layers_out/augmentation_demo.png
    - neural_network_layers_out/analysis_results.png
    - neural_network_layers_out/model_architecture.txt
    - neural_network_layers_out/info.json
"""

"""Imports"""
import argparse

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()


def demo_signal_processing_layers():
    """Demonstrate signal processing neural network layers."""
    print("\n=== Signal Processing Layers ===")

    # Generate example multi-channel signal
    n_channels = 8
    n_samples = 1000
    sample_rate = 250.0

    # Create signal with multiple frequency components
    t = np.linspace(0, n_samples / sample_rate, n_samples)
    signal = np.zeros((1, n_channels, n_samples))  # batch x channels x time

    for ch in range(n_channels):
        # Add different frequency components to each channel
        signal[0, ch, :] = (
            np.sin(2 * np.pi * 10 * t)  # 10 Hz
            + 0.5 * np.sin(2 * np.pi * 25 * t)  # 25 Hz
            + 0.3 * np.sin(2 * np.pi * 60 * t)  # 60 Hz (noise)
            + 0.1 * np.random.randn(n_samples)  # Random noise
        )

    signal_tensor = torch.FloatTensor(signal)

    # 1. Bandpass filter layer
    print("\n1. Bandpass Filter Layer")
    # BandPassFilter expects bands as tensor and fs (sampling frequency)
    filter_layer = scitex.nn.BandPassFilter(
        bands=torch.tensor([[8.0, 30.0]]), fs=sample_rate, seq_len=n_samples
    )

    filtered_signal = filter_layer(signal_tensor)
    print(f"   Input shape: {signal_tensor.shape}")
    print(f"   Output shape: {filtered_signal.shape}")
    # BandPassFilter returns (batch, channels, n_bands, time) - squeeze the n_bands dimension
    filtered_signal = filtered_signal.squeeze(2)

    # 2. Hilbert transform layer
    print("\n2. Hilbert Transform Layer")
    hilbert_layer = scitex.nn.Hilbert(seq_len=n_samples, dim=-1)

    envelope = hilbert_layer(signal_tensor)
    print(f"   Envelope shape: {envelope.shape}")
    # Hilbert returns complex values, take absolute value for envelope
    if envelope.is_complex():
        envelope = torch.abs(envelope)
    # If it returns real and imaginary parts as last dimension
    elif envelope.shape[-1] == 2:
        envelope = torch.sqrt(envelope[..., 0] ** 2 + envelope[..., 1] ** 2)

    # 3. Power Spectral Density layer
    print("\n3. PSD Layer")
    psd_layer = scitex.nn.PSD(sample_rate=sample_rate, prob=False, dim=-1)

    psd_features, freqs = psd_layer(signal_tensor)
    print(f"   PSD features shape: {psd_features.shape}")

    # 4. Wavelet transform layer
    print("\n4. Wavelet Transform Layer")
    # Note: Wavelet layer has dimension issues in current version
    # Skipping for now to demonstrate other layers
    print("   (Skipped due to compatibility issues)")

    # Save example outputs
    scitex.io.save(signal[0].T, "raw_signal.npy")
    scitex.io.save(filtered_signal[0].detach().numpy().T, "filtered_signal.npy")
    scitex.io.save(envelope[0].detach().numpy().T, "envelope.npy")

    return signal_tensor, filtered_signal, envelope, psd_features, None


def demo_augmentation_layers():
    """Demonstrate data augmentation layers for neural networks."""
    print("\n=== Data Augmentation Layers ===")

    # Create example data
    batch_size = 4
    n_channels = 8
    n_samples = 500

    data = torch.randn(batch_size, n_channels, n_samples)

    # 1. Channel dropout
    print("\n1. Channel Dropout")
    channel_dropout = scitex.nn.DropoutChannels(p=0.2)
    channel_dropout.train()  # Enable dropout

    augmented = channel_dropout(data)
    dropped_channels = (augmented == 0).any(dim=2).sum().item()
    print(f"   Dropped {dropped_channels} channels out of {batch_size * n_channels}")

    # 2. Channel swapping
    print("\n2. Channel Swapping")
    swap_layer = scitex.nn.SwapChannels(p=0.5)
    swap_layer.train()

    swapped = swap_layer(data)
    print(f"   Swapped channels in batch (probabilistic)")

    # 3. Frequency gain changer
    print("\n3. Frequency Gain Changer")
    freq_gain = scitex.nn.FreqGainChanger(
        seq_len=n_samples,
        fs=250.0,
        bands_hz=[[8, 12], [13, 30], [30, 50]],
        gain_range=(0.8, 1.2),
        p=0.5,
    )
    freq_gain.train()

    freq_augmented = freq_gain(data)
    print(f"   Applied frequency-specific gain changes")

    # 4. Channel gain changer
    print("\n4. Channel Gain Changer")
    channel_gain = scitex.nn.ChannelGainChanger(gain_range=(0.9, 1.1), p=0.5)
    channel_gain.train()

    gain_augmented = channel_gain(data)
    print(f"   Applied channel-specific gain changes")

    return data, augmented, swapped, freq_augmented, gain_augmented


def demo_analysis_layers():
    """Demonstrate neural network layers for signal analysis."""
    print("\n=== Signal Analysis Layers ===")

    # Generate example signal with PAC
    n_samples = 2000
    sample_rate = 250.0
    t = np.linspace(0, n_samples / sample_rate, n_samples)

    # Low frequency phase signal (10 Hz)
    phase_signal = np.sin(2 * np.pi * 10 * t)

    # High frequency amplitude signal (40 Hz) modulated by phase
    amp_signal = (1 + 0.5 * phase_signal) * np.sin(2 * np.pi * 40 * t)

    # Combine signals
    signal = (
        torch.FloatTensor(phase_signal + 0.5 * amp_signal).unsqueeze(0).unsqueeze(0)
    )

    # 1. Phase-Amplitude Coupling layer
    print("\n1. PAC Layer")
    pac_layer = scitex.nn.PAC(
        seq_len=n_samples,
        fs=sample_rate,
        pha_start_hz=8,
        pha_end_hz=12,
        pha_n_bands=10,
        amp_start_hz=30,
        amp_end_hz=50,
        amp_n_bands=10,
    )

    pac_values = pac_layer(signal)
    print(f"   PAC values shape: {pac_values.shape}")
    if pac_values.numel() == 1:
        print(f"   PAC strength: {pac_values.item():.3f}")
    else:
        print(f"   PAC strength (mean): {pac_values.mean().item():.3f}")

    # 2. Modulation Index layer
    print("\n2. Modulation Index Layer")
    # ModulationIndex expects phase and amplitude as separate inputs
    # First, we need to extract phase and amplitude from our signal
    # Using bandpass filters for phase and amplitude bands

    # Extract phase signal (8-12 Hz)
    phase_filter = scitex.nn.BandPassFilter(
        bands=torch.tensor([[8.0, 12.0]]), fs=sample_rate, seq_len=n_samples
    )
    phase_signal = phase_filter(signal)
    # BandPassFilter returns (batch, channels, n_bands, time) - squeeze n_bands
    phase_signal = phase_signal.squeeze(2)

    # Extract amplitude signal (30-50 Hz)
    amp_filter = scitex.nn.BandPassFilter(
        bands=torch.tensor([[30.0, 50.0]]), fs=sample_rate, seq_len=n_samples
    )
    amp_signal = amp_filter(signal)
    # BandPassFilter returns (batch, channels, n_bands, time) - squeeze n_bands
    amp_signal = amp_signal.squeeze(2)

    # Get phase using Hilbert transform
    hilbert = scitex.nn.Hilbert(seq_len=n_samples)
    phase_complex = hilbert(phase_signal)
    # Handle Hilbert output format
    if phase_complex.is_complex():
        phase = torch.angle(phase_complex)
    elif phase_complex.shape[-1] == 2:
        # Real and imaginary parts as last dimension
        phase = torch.atan2(phase_complex[..., 1], phase_complex[..., 0])
    else:
        phase = phase_complex

    # Get amplitude envelope
    amp_complex = hilbert(amp_signal)
    # Handle Hilbert output format
    if amp_complex.is_complex():
        amplitude = torch.abs(amp_complex)
    elif amp_complex.shape[-1] == 2:
        # Real and imaginary parts as last dimension
        amplitude = torch.sqrt(amp_complex[..., 0] ** 2 + amp_complex[..., 1] ** 2)
    else:
        amplitude = amp_complex

    mi_layer = scitex.nn.ModulationIndex(n_bins=18, fp16=False, amp_prob=False)

    mi_values = mi_layer(phase, amplitude)
    print(f"   MI values: {mi_values.item():.3f}")

    # 3. Spectrogram layer - Note: Not available in current scitex version
    print("\n3. Spectrogram Layer (skipped - not available)")
    spec = None
    # spectrogram_layer = scitex.nn.Spectrogram(
    #     n_chs=1,
    #     samp_rate=sample_rate,
    #     window_size=128,
    #     overlap=0.75
    # )
    #
    # spec = spectrogram_layer(signal)
    # print(f"   Spectrogram shape: {spec.shape}")

    return signal, pac_values, mi_values, spec


def demo_complete_model():
    """Demonstrate a complete neural network model using scitex layers."""
    print("\n=== Complete Neural Network Model ===")

    class SignalClassifier(nn.Module):
        """Example model combining multiple scitex layers."""

        def __init__(self, n_channels=8, n_classes=2):
            super().__init__()

            # Signal processing layers
            # Using regular BandPassFilter for now
            self.filter = scitex.nn.BandPassFilter(
                bands=torch.tensor([[8.0, 30.0]]),
                fs=250.0,
                seq_len=1000,  # Will need to handle variable lengths
            )

            # Feature extraction
            self.psd = scitex.nn.PSD(sample_rate=250.0, prob=False, dim=-1)

            # Augmentation (only during training)
            self.dropout = scitex.nn.DropoutChannels(p=0.1)
            self.gain = scitex.nn.ChannelGainChanger(gain_range=(0.9, 1.1))

            # Get feature dimension
            dummy_input = torch.randn(1, n_channels, 1000)
            dummy_filtered = self.filter(dummy_input)
            dummy_features, _ = self.psd(dummy_filtered)
            # PSD returns (batch, channels, freq_bins), so we need to flatten
            feature_dim = dummy_features.shape[1] * dummy_features.shape[2]

            # Classification head
            self.classifier = nn.Sequential(
                nn.Linear(feature_dim, 128),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(64, n_classes),
            )

        def forward(self, x):
            # Apply augmentation only during training
            if self.training:
                x = self.dropout(x)
                x = self.gain(x)

            # Signal processing
            x = self.filter(x)
            # BandPassFilter returns (batch, channels, n_bands, time) - squeeze n_bands
            x = x.squeeze(2)

            # Feature extraction
            features, _ = self.psd(x)
            # Flatten the features (batch, channels, freq_bins) -> (batch, channels*freq_bins)
            features = features.flatten(1)

            # Classification
            output = self.classifier(features)

            return output

    # Create model
    model = SignalClassifier(n_channels=8, n_classes=2)
    print(
        f"\nModel architecture created with {sum(p.numel() for p in model.parameters())} parameters"
    )

    # Example forward pass
    batch_size = 16
    n_channels = 8
    n_samples = 1000

    example_input = torch.randn(batch_size, n_channels, n_samples)

    # Training mode
    model.train()
    train_output = model(example_input)
    print(f"\nTraining mode output shape: {train_output.shape}")

    # Evaluation mode
    model.eval()
    with torch.no_grad():
        eval_output = model(example_input)
    print(f"Evaluation mode output shape: {eval_output.shape}")

    # Save model architecture
    model_info = {
        "architecture": str(model),
        "n_parameters": sum(p.numel() for p in model.parameters()),
        "layer_info": {
            "filter": "Learnable bandpass filter",
            "psd": "Power spectral density features",
            "augmentation": "Channel dropout and gain changes",
            "classifier": "3-layer MLP",
        },
    }
    scitex.io.save(model_info, "model_info.json")

    return model


def visualize_layer_outputs():
    """Create visualizations of layer outputs."""
    print("\n=== Creating Visualizations ===")

    # Setup plotting
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Generate test signal
    n_samples = 1000
    sample_rate = 250.0
    t = np.linspace(0, n_samples / sample_rate, n_samples)

    # Multi-frequency signal
    signal = (
        np.sin(2 * np.pi * 10 * t)
        + 0.5 * np.sin(2 * np.pi * 25 * t)
        + 0.3 * np.sin(2 * np.pi * 40 * t)
    )
    signal_tensor = torch.FloatTensor(signal).unsqueeze(0).unsqueeze(0)

    # 1. Original vs Filtered
    ax = axes[0, 0]
    filter_layer = scitex.nn.BandPassFilter(
        bands=torch.tensor([[8.0, 30.0]]), fs=sample_rate, seq_len=n_samples
    )
    filtered = filter_layer(signal_tensor)
    # BandPassFilter returns (batch, channels, n_bands, time) - take first band
    filtered = filtered[0, 0, 0].detach().numpy()

    ax.plot(t[:250], signal[:250], "b-", alpha=0.7, label="Original")
    ax.plot(t[:250], filtered[:250], "r-", alpha=0.7, label="Filtered (8-30 Hz)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Bandpass Filtering")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Envelope extraction
    ax = axes[0, 1]
    # First apply bandpass filter
    bp_filter = scitex.nn.BandPassFilter(
        bands=torch.tensor([[8.0, 12.0]]), fs=sample_rate, seq_len=n_samples
    )
    bp_filtered = bp_filter(signal_tensor)
    bp_filtered = bp_filtered.squeeze(2)  # Remove n_bands dimension

    hilbert_layer = scitex.nn.Hilbert(seq_len=n_samples)
    envelope_complex = hilbert_layer(bp_filtered)
    # Handle Hilbert output format
    if envelope_complex.is_complex():
        envelope = torch.abs(envelope_complex)[0, 0].detach().numpy()
    elif envelope_complex.shape[-1] == 2:
        envelope = (
            torch.sqrt(envelope_complex[..., 0] ** 2 + envelope_complex[..., 1] ** 2)[
                0, 0
            ]
            .detach()
            .numpy()
        )
    else:
        envelope = envelope_complex[0, 0].detach().numpy()

    # Use the bandpass filtered signal from above
    ax.plot(
        t[:500],
        bp_filtered[0, 0, :500].detach().numpy(),
        "b-",
        alpha=0.5,
        label="Filtered signal",
    )
    ax.plot(t[:500], envelope[:500], "r-", linewidth=2, label="Envelope")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Hilbert Envelope")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. PSD features
    ax = axes[1, 0]
    psd_layer = scitex.nn.PSD(sample_rate=sample_rate)
    psd_features, freqs_psd = psd_layer(signal_tensor)
    psd_features = psd_features[0, 0].detach().numpy()

    freqs = freqs_psd.detach().numpy()
    # Only plot positive frequencies
    mask = freqs >= 0
    ax.semilogy(freqs[mask], psd_features[mask], "b-", linewidth=2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power")
    ax.set_title("Power Spectral Density")
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 60])

    # 4. Time-frequency representation (using spectrogram instead)
    ax = axes[1, 1]
    # Since Wavelet has issues, use a simple spectrogram visualization
    from scipy import signal as scipy_signal

    f, t_spec, Sxx = scipy_signal.spectrogram(signal[:250], fs=sample_rate, nperseg=64)

    im = ax.pcolormesh(t_spec, f, 10 * np.log10(Sxx), shading="gouraud", cmap="hot")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("Spectrogram (Alternative to Wavelet)")
    ax.set_ylim([0, 60])
    plt.colorbar(im, ax=ax, label="Power (dB)")

    plt.tight_layout()
    scitex.io.save(fig, "layer_outputs.png")
    plt.close()

    print("   Saved visualization to layer_outputs.png")


"""Functions & Classes"""


def main(args):
    """Run all neural network layer examples."""
    print("=" * 60)
    print("SciTeX Neural Network Layer Examples")
    print("=" * 60)

    # Create output directory (handled by scitex.gen.start)
    scitex.io.save({"example": "nn_layers"}, "info.json")

    # Run demonstrations
    signal_outputs = demo_signal_processing_layers()
    augmentation_outputs = demo_augmentation_layers()
    analysis_outputs = demo_analysis_layers()
    model = demo_complete_model()
    visualize_layer_outputs()

    # Summary
    print("\n" + "=" * 60)
    print("Summary of SciTeX Neural Network Layers:")
    print("=" * 60)
    print("\nSignal Processing Layers:")
    print("  - Filters: Learnable/fixed bandpass, lowpass, highpass")
    print("  - Hilbert: Envelope and phase extraction")
    print("  - PSD: Power spectral density features")
    print("  - Wavelet: Time-frequency decomposition")
    print("  - Spectrogram: Short-time Fourier transform")

    print("\nAugmentation Layers:")
    print("  - DropoutChannels: Channel-wise dropout")
    print("  - SwapChannels: Random channel permutation")
    print("  - FreqGainChanger: Frequency-band specific gain")
    print("  - ChannelGainChanger: Channel-specific gain")

    print("\nAnalysis Layers:")
    print("  - PAC: Phase-amplitude coupling")
    print("  - ModulationIndex: Cross-frequency coupling strength")
    print("  - Various feature extraction layers")

    print("\nKey Features:")
    print("  - PyTorch compatible")
    print("  - Differentiable signal processing")
    print("  - GPU acceleration support")
    print("  - Learnable parameters option")
    print("  - Batch processing")

    print(f"\nOutputs saved to current directory")
    print("\nThese layers can be combined with standard PyTorch layers")
    print("to create powerful signal processing neural networks!")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(
        description="Neural network layer examples with scitex.nn"
    )
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, np, torch, nn, scitex

    import sys
    import numpy as np
    import torch
    import torch.nn as nn
    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()
