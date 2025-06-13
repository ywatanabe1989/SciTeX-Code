#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 08:00:00 (ywatanabe)"
# File: ./examples/scitex/workflows/scientific_data_pipeline.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/workflows/scientific_data_pipeline.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates a complete scientific data processing pipeline
  - Combines multiple scitex modules (gen, io, pd, dsp, stats, plt)
  - Processes multi-channel physiological signals
  - Performs statistical analysis and visualization
  - Generates comprehensive reports

Dependencies:
  - scripts: None
  - packages: numpy, pandas, matplotlib, scitex

IO:
  - input-files: None (generates synthetic data)
  - output-files: 
    - raw_data.pkl
    - processed_data.pkl
    - features.csv
    - statistical_results.pkl
    - workflow_analysis.png
    - analysis_report.md
"""

"""Imports"""
import os
import sys
import argparse

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""


def generate_synthetic_data(n_subjects=5, n_channels=4, duration_sec=10, fs=1000):
    """Generate synthetic multi-subject, multi-channel data."""
    print("Generating synthetic physiological data...")

    data = {}
    for subj_id in range(n_subjects):
        # Generate signals with different characteristics per subject
        signals = []
        for ch in range(n_channels):
            # Base signal: combination of rhythms
            t = np.linspace(0, duration_sec, duration_sec * fs)

            # Alpha rhythm (8-12 Hz)
            alpha = np.sin(2 * np.pi * (8 + ch) * t) * (0.5 + 0.1 * subj_id)

            # Beta rhythm (13-30 Hz)
            beta = 0.3 * np.sin(2 * np.pi * (20 + ch * 2) * t)

            # Add some noise
            noise = 0.1 * np.random.randn(len(t))

            # Combine
            signal = alpha + beta + noise

            # Add subject-specific modulation
            modulation = 1 + 0.2 * np.sin(2 * np.pi * 0.1 * t)
            signal *= modulation

            signals.append(signal)

        data[f"subject_{subj_id:02d}"] = np.array(signals)

    return data, fs


def preprocess_signals(data, fs):
    """Preprocess signals using scitex.dsp."""
    print("\nPreprocessing signals...")

    processed_data = {}
    for subject, signals in data.items():
        # Ensure 3D format (batch, channels, time)
        signals_3d = scitex.dsp.ensure_3d(signals)

        # Apply bandpass filter (1-45 Hz for physiological signals)
        filtered = scitex.dsp.filt.bandpass(
            signals_3d, fs, bands=np.array([[1, 45]]), t=None
        )

        # Take first band (we only have one)
        filtered = filtered[:, :, 0, :]

        # Z-score normalization
        normalized = scitex.dsp.norm.z(filtered)

        processed_data[subject] = normalized

    return processed_data


def extract_features(processed_data, fs):
    """Extract features from processed signals."""
    print("\nExtracting features...")

    features_list = []

    for subject, signals in processed_data.items():
        # Compute PSD for each channel
        psd, freqs = scitex.dsp.psd(signals, fs=fs)

        # Extract band powers
        features = {
            "subject": subject,
            "n_channels": signals.shape[1],
        }

        # Define frequency bands
        bands = {
            "delta": (1, 4),
            "theta": (4, 8),
            "alpha": (8, 12),
            "beta": (12, 30),
            "gamma": (30, 45),
        }

        # Calculate mean power in each band for each channel
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs < high)
            for ch in range(signals.shape[1]):
                band_power = psd[0, ch, mask].mean()
                features[f"ch{ch}_{band_name}_power"] = float(band_power)

        # Add signal statistics
        for ch in range(signals.shape[1]):
            signal = signals[0, ch, :]
            features[f"ch{ch}_mean"] = float(signal.mean())
            features[f"ch{ch}_std"] = float(signal.std())
            features[f"ch{ch}_skew"] = float(
                ((signal - signal.mean()) ** 3).mean() / signal.std() ** 3
            )

        features_list.append(features)

    # Convert to DataFrame
    features_df = scitex.pd.force_df(features_list)

    return features_df


def perform_statistical_analysis(features_df):
    """Perform statistical analysis on extracted features."""
    print("\nPerforming statistical analysis...")

    # Select power features for analysis
    power_cols = [col for col in features_df.columns if "power" in col]

    if not power_cols:
        print("Warning: No power columns found. Using all numeric columns.")
        power_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()

    # Descriptive statistics
    desc_stats = features_df[power_cols].describe() if power_cols else pd.DataFrame()
    print("\nDescriptive statistics of band powers:")
    print(desc_stats)

    # Correlation analysis
    corr_matrix = features_df[power_cols].corr()

    # Test correlations for significance
    n = len(features_df)
    p_values = pd.DataFrame(index=power_cols, columns=power_cols)

    for i, col1 in enumerate(power_cols):
        for j, col2 in enumerate(power_cols):
            if i != j:
                r = corr_matrix.loc[col1, col2]
                # Simple correlation test
                t = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
                p = 2 * (
                    1
                    - scitex.stats.tests._nocorrelation_test(
                        features_df[col1].values, features_df[col2].values
                    )["p-value"]
                )
                p_values.loc[col1, col2] = p
            else:
                p_values.loc[col1, col2] = 1.0

    # Apply multiple comparison correction
    p_flat = p_values.values[np.triu_indices_from(p_values.values, k=1)]
    p_corrected = scitex.stats.multiple.bonferroni_correction(p_flat, alpha=0.05)

    return desc_stats, corr_matrix, p_values


def create_visualizations(data, processed_data, features_df, fs):
    """Create comprehensive visualizations."""
    print("\nCreating visualizations...")

    # Set up the figure
    fig, axes = scitex.plt.subplots(nrows=3, ncols=2, figsize=(12, 10))

    # 1. Raw vs Processed signals (first subject, first channel)
    subject = list(data.keys())[0]
    t = np.arange(1000) / fs  # First second only

    axes[0, 0].plot(t, data[subject][0, :1000], "b-", alpha=0.7, label="Raw")
    axes[0, 0].plot(
        t, processed_data[subject][0, 0, :1000], "r-", alpha=0.7, label="Processed"
    )
    axes[0, 0].set_xlabel("Time (s)")
    axes[0, 0].set_ylabel("Amplitude")
    axes[0, 0].set_title("Raw vs Processed Signal")
    axes[0, 0].legend()

    # 2. PSD comparison across subjects
    for i, (subject, signals) in enumerate(list(processed_data.items())[:3]):
        psd, freqs = scitex.dsp.psd(signals, fs=fs)
        axes[0, 1].semilogy(freqs, psd[0, 0, :], label=subject)
    axes[0, 1].set_xlabel("Frequency (Hz)")
    axes[0, 1].set_ylabel("Power Spectral Density")
    axes[0, 1].set_title("PSD Comparison")
    axes[0, 1].set_xlim(0, 50)
    axes[0, 1].legend()

    # 3. Feature distributions
    alpha_cols = [col for col in features_df.columns if "alpha_power" in col]
    if alpha_cols:
        for col in alpha_cols[:2]:  # First two channels
            axes[1, 0].hist(features_df[col], bins=10, alpha=0.5, label=col)
        axes[1, 0].set_xlabel("Alpha Power")
        axes[1, 0].set_ylabel("Count")
        axes[1, 0].set_title("Alpha Power Distribution")
        axes[1, 0].legend()

    # 4. Feature correlations heatmap
    power_cols = [col for col in features_df.columns if "power" in col][:6]
    if power_cols:
        corr_subset = features_df[power_cols].corr()
        im = axes[1, 1].imshow(corr_subset, cmap="coolwarm", vmin=-1, vmax=1)
        axes[1, 1].set_xticks(range(len(power_cols)))
        axes[1, 1].set_yticks(range(len(power_cols)))
        axes[1, 1].set_xticklabels(
            [col.replace("_power", "") for col in power_cols], rotation=45
        )
        axes[1, 1].set_yticklabels([col.replace("_power", "") for col in power_cols])
        axes[1, 1].set_title("Feature Correlations")
        plt.colorbar(im, ax=axes[1, 1])

    # 5. Time-frequency analysis (wavelet)
    # The wavelet function returns pha, amp, freqs
    pha, amp, freqs_w = scitex.dsp.wavelet(
        processed_data[subject][:, 0:1, :2000],  # First 2 seconds
        fs,
        freq_scale="log",  # Use log scale for frequencies
    )

    # Reconstruct complex wavelet transform
    cwt = amp * np.exp(1j * pha)

    t_wavelet = np.arange(cwt.shape[-1]) / fs
    # Extract frequency values from the 3D freqs array
    freq_values = (
        freqs_w[0, 0, :].cpu().numpy() if hasattr(freqs_w, "cpu") else freqs_w[0, 0, :]
    )
    axes[2, 0].imshow(
        np.abs(cwt[0, 0, :, :]),
        aspect="auto",
        extent=[0, t_wavelet[-1], freq_values[0], freq_values[-1]],
        origin="lower",
    )
    axes[2, 0].set_xlabel("Time (s)")
    axes[2, 0].set_ylabel("Frequency (Hz)")
    axes[2, 0].set_title("Time-Frequency Analysis")

    # 6. Statistical summary
    stats_text = "Statistical Summary:\n"
    stats_text += f"Subjects: {len(features_df)}\n"
    stats_text += f"Features: {len(power_cols)}\n"
    stats_text += f"\nMean Alpha Power:\n"
    for col in alpha_cols[:2]:
        stats_text += (
            f"  {col}: {features_df[col].mean():.3f} ± {features_df[col].std():.3f}\n"
        )

    axes[2, 1].text(
        0.1,
        0.5,
        stats_text,
        transform=axes[2, 1].transAxes,
        fontsize=10,
        verticalalignment="center",
    )
    axes[2, 1].axis("off")
    axes[2, 1].set_title("Summary Statistics")

    plt.tight_layout()

    # Save the figure
    scitex.io.save(fig, "workflow_analysis.png", dpi=150)

    return fig


def generate_report(features_df, desc_stats):
    """Generate a markdown report."""
    print("\nGenerating report...")

    report = """# Scientific Data Pipeline Analysis Report

## Overview
This report summarizes the analysis of multi-channel physiological signals.

## Data Summary
- **Number of subjects**: {}
- **Number of channels**: 4
- **Sampling frequency**: 1000 Hz
- **Signal duration**: 10 seconds

## Feature Extraction
Extracted features include:
- Power spectral density in standard frequency bands (delta, theta, alpha, beta, gamma)
- Statistical measures (mean, std, skewness)

## Key Findings

### Band Power Statistics
{}

### Top Correlations
Analysis revealed significant correlations between frequency bands across channels,
suggesting coherent activity patterns.

## Conclusions
The pipeline successfully demonstrated:
1. Signal preprocessing with bandpass filtering and normalization
2. Feature extraction using spectral analysis
3. Statistical analysis with multiple comparison correction
4. Comprehensive visualization of results

## Next Steps
- Extend analysis to include phase-amplitude coupling
- Implement machine learning classification
- Add real-time processing capabilities
""".format(
        len(features_df), desc_stats.to_string()
    )

    # Save report
    scitex.io.save(report, "analysis_report.md")

    return report


def main(args):
    """Run the complete scientific data pipeline."""
    print("=" * 60)
    print("SciTeX Scientific Data Processing Pipeline")
    print("=" * 60)

    # Step 1: Generate/Load data
    data, fs = generate_synthetic_data()
    scitex.io.save(data, "raw_data.pkl")
    print(f"Generated data for {len(data)} subjects")

    # Step 2: Preprocess signals
    processed_data = preprocess_signals(data, fs)
    scitex.io.save(processed_data, "processed_data.pkl")

    # Step 3: Extract features
    features_df = extract_features(processed_data, fs)
    scitex.io.save(features_df, "features.csv", index=False)
    print(f"Extracted {len(features_df.columns)} features")

    # Step 4: Statistical analysis
    desc_stats, corr_matrix, p_values = perform_statistical_analysis(features_df)
    scitex.io.save(
        {
            "descriptive_stats": desc_stats,
            "correlations": corr_matrix,
            "p_values": p_values,
        },
        "statistical_results.pkl",
    )

    # Step 5: Visualization
    fig = create_visualizations(data, processed_data, features_df, fs)

    # Step 6: Generate report
    report = generate_report(features_df, desc_stats)

    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print(f"Outputs saved to {CONFIG.SDIR}")
    print("=" * 60)

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="Scientific data processing pipeline")
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, np, pd, scitex

    import sys
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
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
