#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-06 10:00:00 (ywatanabe)"
# File: ./examples/scitex_demo_simple.py

"""
Functionalities:
- Simple demonstration of core SciTeX functionality
- Shows basic usage patterns without complex dependencies

Example usage:
$ python ./examples/scitex_demo_simple.py

Input:
- None (generates synthetic data)

Output:
- Console output showing results
- ./examples/scitex_demo_simple_out/: Directory containing outputs
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import numpy as np
import pandas as pd
import scitex

def main():
    # Initialize SciTeX
    CONFIG, sys_out, sys_err, plt, CC = scitex.gen.start(
        sys=sys,
        verbose=True,
        seed=42
    )
    
    print("=== SciTeX Simple Demo ===")
    print(f"Log directory: {CONFIG.SDIR}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Experiment ID: {CONFIG.ID}")
    
    # 1. Data Generation
    print("\n1. Generating sample data...")
    # Create a simple signal
    fs = 1000  # Sampling frequency
    t = np.linspace(0, 1, fs)
    signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)
    signal += 0.1 * np.random.randn(len(t))  # Add noise
    
    # Create a DataFrame
    df = pd.DataFrame({
        'time': t,
        'signal': signal,
        'group': np.random.choice(['A', 'B'], len(t))
    })
    
    print(f"   Generated signal with {len(signal)} samples")
    print(f"   DataFrame shape: {df.shape}")
    
    # 2. Signal Processing
    print("\n2. Processing signal...")
    # Apply bandpass filter
    filtered_signal = scitex.dsp.filt.bandpass(signal, fs, bands=[[5, 20]])
    # Convert to numpy and squeeze extra dimensions
    filtered_signal = np.array(filtered_signal).squeeze()
    print(f"   Applied bandpass filter (5-20 Hz)")
    
    # Compute PSD
    psd_values, freqs = scitex.dsp.psd(signal, fs)
    # Convert to numpy and squeeze
    psd_values = np.array(psd_values).squeeze()
    freqs = np.array(freqs).squeeze()
    print(f"   Computed PSD with {len(freqs)} frequency bins")
    
    # 3. Plotting
    print("\n3. Creating visualizations...")
    fig, axes = scitex.plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot original vs filtered signal
    axes[0].plot(t[:200], signal[:200], label='Original', alpha=0.7)
    axes[0].plot(t[:200], filtered_signal[:200], label='Filtered (5-20 Hz)', alpha=0.7)
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Signal Comparison')
    axes[0].legend()
    
    # Plot PSD
    axes[1].plot(freqs[freqs < 100], psd_values[freqs < 100])
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Power')
    axes[1].set_title('Power Spectral Density')
    axes[1].set_xlim(0, 100)
    
    # Apply tight layout
    fig.tight_layout()
    
    # 4. Save outputs using absolute paths temporarily
    print("\n4. Saving outputs...")
    output_dir = os.path.join(os.getcwd(), "examples", "scitex_demo_simple_out")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save figure
    fig_path = os.path.join(output_dir, "signal_analysis.png")
    fig.savefig(fig_path)
    print(f"   Saved figure to: {fig_path}")
    
    # Save data as CSV
    csv_path = os.path.join(output_dir, "processed_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"   Saved data to: {csv_path}")
    
    # Save numpy array
    np_path = os.path.join(output_dir, "filtered_signal.npy")
    np.save(np_path, filtered_signal)
    print(f"   Saved array to: {np_path}")
    
    # 5. Statistical summary
    print("\n5. Statistical Summary:")
    print(f"   Original signal - Mean: {np.mean(signal):.4f}, Std: {np.std(signal):.4f}")
    print(f"   Filtered signal - Mean: {np.mean(filtered_signal):.4f}, Std: {np.std(filtered_signal):.4f}")
    print(f"   Peak frequency: {freqs[np.argmax(psd_values)]:.1f} Hz")
    
    # 6. Using pandas utilities
    print("\n6. Data manipulation with scitex.pd:")
    # Force to DataFrame
    df_forced = scitex.pd.force_df(df)
    print(f"   Forced DataFrame shape: {df_forced.shape}")
    
    # Find indices
    indices_A = scitex.pd.find_indi(df, conditions={'group': 'A'})
    print(f"   Found {len(indices_A)} samples in group A")
    
    print("\n=== Demo Complete ===")
    print(f"All outputs saved to: {output_dir}")
    
    # Close SciTeX
    scitex.gen.close(CONFIG)

if __name__ == "__main__":
    main()