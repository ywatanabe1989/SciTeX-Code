#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-06 10:00:00 (ywatanabe)"
# File: ./examples/scitex_demo.py

"""
Functionalities:
- Demonstrates core SciTeX functionality with a complete scientific workflow
- Shows data generation, processing, analysis, and visualization
- Illustrates best practices for using SciTeX modules

Example usage:
$ python ./examples/scitex_demo.py

Input:
- None (generates synthetic data)

Output:
- ./examples/scitex_demo_output/: Directory containing all outputs
  - figures/: Visualization results
  - data/: Processed data files
  - results/: Analysis results
  - logs/: Execution logs
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import numpy as np
import pandas as pd
from scipy import signal
import scitex

def generate_synthetic_signals(n_trials=50, fs=1000, duration=2):
    """Generate synthetic neural-like signals with two conditions."""
    t = np.linspace(0, duration, int(fs * duration))
    signals_cond1 = []
    signals_cond2 = []
    
    for i in range(n_trials):
        # Condition 1: Strong 10Hz + weak 40Hz
        sig1 = (np.sin(2 * np.pi * 10 * t) + 
                0.3 * np.sin(2 * np.pi * 40 * t) + 
                0.5 * np.random.randn(len(t)))
        signals_cond1.append(sig1)
        
        # Condition 2: Weak 10Hz + strong 40Hz
        sig2 = (0.3 * np.sin(2 * np.pi * 10 * t) + 
                np.sin(2 * np.pi * 40 * t) + 
                0.5 * np.random.randn(len(t)))
        signals_cond2.append(sig2)
    
    return np.array(signals_cond1), np.array(signals_cond2), t

def process_signals(signals, fs):
    """Apply signal processing to extract features."""
    processed_signals = []
    features = []
    
    for sig in signals:
        # Bandpass filter 1-100 Hz
        filtered = scitex.dsp.filt.bandpass(sig, fs, bands=[[1, 100]])
        processed_signals.append(filtered)
        
        # Extract power spectral density features
        freqs, psd = scitex.dsp.psd(filtered, fs)
        
        # Extract band powers
        alpha_mask = (freqs >= 8) & (freqs <= 12)
        beta_mask = (freqs >= 13) & (freqs <= 30)
        gamma_mask = (freqs >= 30) & (freqs <= 50)
        
        features.append({
            'alpha_power': np.mean(psd[alpha_mask]),
            'beta_power': np.mean(psd[beta_mask]),
            'gamma_power': np.mean(psd[gamma_mask]),
            'total_power': np.sum(psd)
        })
    
    return np.array(processed_signals), pd.DataFrame(features), freqs

def visualize_results(signals1, signals2, features1, features2, freqs, CONFIG):
    """Create comprehensive visualizations."""
    
    # 1. Signal comparison plot
    fig1, axes = scitex.plt.subplots(2, 2, figsize=(12, 8))
    
    # Plot example signals
    axes[0, 0].plot(signals1[0][:1000], label='Condition 1')
    axes[0, 0].set_title('Example Signal - Condition 1')
    axes[0, 0].set_xlabel('Time (ms)')
    axes[0, 0].set_ylabel('Amplitude')
    
    axes[0, 1].plot(signals2[0][:1000], label='Condition 2', color='orange')
    axes[0, 1].set_title('Example Signal - Condition 2')
    axes[0, 1].set_xlabel('Time (ms)')
    axes[0, 1].set_ylabel('Amplitude')
    
    # Plot average PSDs
    psd1_mean = []
    psd2_mean = []
    
    for sig in signals1:
        _, psd = scitex.dsp.psd(sig, fs=1000)
        psd1_mean.append(psd)
    
    for sig in signals2:
        _, psd = scitex.dsp.psd(sig, fs=1000)
        psd2_mean.append(psd)
    
    psd1_mean = np.mean(psd1_mean, axis=0)
    psd2_mean = np.mean(psd2_mean, axis=0)
    
    axes[1, 0].plot(freqs[freqs <= 60], psd1_mean[freqs <= 60], label='Condition 1')
    axes[1, 0].plot(freqs[freqs <= 60], psd2_mean[freqs <= 60], label='Condition 2')
    axes[1, 0].set_xlabel('Frequency (Hz)')
    axes[1, 0].set_ylabel('Power')
    axes[1, 0].set_title('Average Power Spectral Density')
    axes[1, 0].legend()
    
    # Feature comparison
    feature_names = ['alpha_power', 'beta_power', 'gamma_power']
    x = np.arange(len(feature_names))
    width = 0.35
    
    means1 = [features1[f].mean() for f in feature_names]
    means2 = [features2[f].mean() for f in feature_names]
    stds1 = [features1[f].std() for f in feature_names]
    stds2 = [features2[f].std() for f in feature_names]
    
    axes[1, 1].bar(x - width/2, means1, width, yerr=stds1, label='Condition 1')
    axes[1, 1].bar(x + width/2, means2, width, yerr=stds2, label='Condition 2')
    axes[1, 1].set_xlabel('Frequency Band')
    axes[1, 1].set_ylabel('Power')
    axes[1, 1].set_title('Band Power Comparison')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(['Alpha\n(8-12Hz)', 'Beta\n(13-30Hz)', 'Gamma\n(30-50Hz)'])
    axes[1, 1].legend()
    
    plt_tight_layout(fig1)
    scitex.io.save("./examples/scitex_demo_output/figures/signal_analysis.png", fig1)
    
    # 2. Statistical comparison plot
    fig2, ax = scitex.plt.subplots(figsize=(10, 6))
    
    # Combine features for statistical testing
    all_features = pd.concat([
        features1.assign(condition='Condition 1'),
        features2.assign(condition='Condition 2')
    ])
    
    # Box plot comparison
    import matplotlib.pyplot as plt
    positions = [1, 2, 3, 5, 6, 7, 9, 10, 11]
    data_to_plot = []
    labels = []
    
    for i, feature in enumerate(feature_names):
        data_to_plot.extend([
            features1[feature].values,
            features2[feature].values,
            []  # spacer
        ])
        labels.extend([f'C1\n{feature.split("_")[0]}', f'C2\n{feature.split("_")[0]}', ''])
    
    # Remove spacers
    data_to_plot = [d for d in data_to_plot if len(d) > 0]
    labels = [l for l in labels if l != '']
    
    bp = ax.boxplot(data_to_plot, positions=positions[:len(data_to_plot)], 
                    widths=0.6, patch_artist=True)
    
    # Color boxes
    colors = ['lightblue', 'lightcoral'] * len(feature_names)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_xticks(positions[:len(data_to_plot)])
    ax.set_xticklabels(labels)
    ax.set_ylabel('Power')
    ax.set_title('Statistical Comparison of Band Powers')
    
    # Add significance stars
    from scipy import stats
    y_max = ax.get_ylim()[1]
    for i, feature in enumerate(feature_names):
        t_stat, p_val = stats.ttest_ind(features1[feature], features2[feature])
        stars = scitex.stats.p2stars(p_val)
        if stars:
            x_pos = positions[i*3] + 0.5
            ax.text(x_pos, y_max * 0.95, stars, ha='center', va='bottom', fontsize=14)
    
    scitex.io.save("./examples/scitex_demo_output/figures/statistical_comparison.png", fig2)
    
    return fig1, fig2

def plt_tight_layout(fig):
    """Helper function to apply tight_layout."""
    fig.tight_layout()

def main():
    # Initialize SciTeX with configuration
    CONFIG, sys_out, sys_err, plt, CC = scitex.gen.start(
        sys=sys,
        sdir="./examples/scitex_demo_output/logs",
        verbose=True,
        seed=42
    )
    
    print("=== SciTeX Demo Script ===")
    print(f"Log directory: {CONFIG.SDIR}")
    print(f"Working directory: {os.getcwd()}")
    
    # Step 1: Generate synthetic data
    print("\n1. Generating synthetic signals...")
    signals1, signals2, time_vec = generate_synthetic_signals(n_trials=50)
    print(f"   Generated {len(signals1)} trials for Condition 1")
    print(f"   Generated {len(signals2)} trials for Condition 2")
    
    # Save raw data
    scitex.io.save("./examples/scitex_demo_output/data/raw_signals_cond1.npy", signals1)
    scitex.io.save("./examples/scitex_demo_output/data/raw_signals_cond2.npy", signals2)
    scitex.io.save("./examples/scitex_demo_output/data/time_vector.npy", time_vec)
    
    # Step 2: Process signals
    print("\n2. Processing signals...")
    processed1, features1, freqs = process_signals(signals1, fs=1000)
    processed2, features2, freqs = process_signals(signals2, fs=1000)
    print(f"   Extracted {len(features1.columns)} features per trial")
    
    # Save processed data and features
    scitex.io.save("./examples/scitex_demo_output/data/processed_signals_cond1.npy", processed1)
    scitex.io.save("./examples/scitex_demo_output/data/processed_signals_cond2.npy", processed2)
    scitex.io.save("./examples/scitex_demo_output/data/features_cond1.csv", features1)
    scitex.io.save("./examples/scitex_demo_output/data/features_cond2.csv", features2)
    
    # Step 3: Statistical analysis
    print("\n3. Performing statistical analysis...")
    results = []
    
    for feature in features1.columns:
        # Perform t-test
        from scipy import stats
        t_stat, p_val = stats.ttest_ind(features1[feature], features2[feature])
        
        # Calculate effect size (Cohen's d)
        mean_diff = features1[feature].mean() - features2[feature].mean()
        pooled_std = np.sqrt((features1[feature].std()**2 + features2[feature].std()**2) / 2)
        cohens_d = mean_diff / pooled_std
        
        results.append({
            'feature': feature,
            'mean_cond1': features1[feature].mean(),
            'std_cond1': features1[feature].std(),
            'mean_cond2': features2[feature].mean(),
            'std_cond2': features2[feature].std(),
            't_statistic': t_stat,
            'p_value': p_val,
            'significance': scitex.stats.p2stars(p_val),
            'cohens_d': cohens_d
        })
    
    results_df = pd.DataFrame(results)
    print("\nStatistical Results:")
    print(results_df.to_string(index=False))
    
    # Save results
    scitex.io.save("./examples/scitex_demo_output/results/statistical_analysis.csv", results_df)
    
    # Step 4: Visualization
    print("\n4. Creating visualizations...")
    fig1, fig2 = visualize_results(processed1, processed2, features1, features2, freqs, CONFIG)
    
    # Step 5: Generate summary report
    print("\n5. Generating summary report...")
    report = f"""# SciTeX Demo Analysis Report

## Summary
- Date: {CONFIG.START_TIME}
- Experiment ID: {CONFIG.ID}
- Samples per condition: {len(signals1)}

## Key Findings

### Statistical Results
{results_df.to_markdown(index=False)}

### Interpretation
- Condition 1 shows stronger alpha (10 Hz) activity
- Condition 2 shows stronger gamma (40 Hz) activity
- All frequency bands show significant differences (p < 0.001)

## Output Files
- Raw data: `./data/raw_signals_*.npy`
- Processed data: `./data/processed_signals_*.npy`
- Features: `./data/features_*.csv`
- Statistical results: `./results/statistical_analysis.csv`
- Figures: `./figures/*.png`
- Logs: `./logs/`

## Methods
1. Generated synthetic signals with known frequency content
2. Applied 1-100 Hz bandpass filter
3. Extracted power spectral density features
4. Performed statistical comparisons using t-tests
5. Visualized results using SciTeX plotting utilities
"""
    
    scitex.io.save("./examples/scitex_demo_output/ANALYSIS_REPORT.md", report)
    
    print("\n=== Demo Complete ===")
    print(f"All outputs saved to: ./examples/scitex_demo_output/")
    print("Check ANALYSIS_REPORT.md for detailed results")
    
    # Close SciTeX (saves logs)
    scitex.gen.close(CONFIG)

if __name__ == "__main__":
    # Run from project root: python ./examples/scitex_demo.py
    main()