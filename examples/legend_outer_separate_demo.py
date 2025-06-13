#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:39:00"
# File: /examples/legend_outer_separate_demo.py
# ----------------------------------------
"""
Demonstration of the new legend placement features in SciTeX.

This example shows:
1. ax.legend("outer") - Places legend outside plot area without overlap
2. ax.legend("separate") - Saves legend as a separate figure file
3. Combining both features with real data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex.plt as mplt


def example_legend_outer():
    """Demonstrate ax.legend('outer') functionality."""
    print("Example 1: Using ax.legend('outer')")
    print("-" * 40)
    
    # Create sample data
    x = np.linspace(0, 10, 100)
    
    # Create figure
    fig, ax = mplt.subplots(figsize=(8, 6))
    
    # Plot multiple lines
    for i in range(5):
        y = np.sin(x + i * np.pi/4) + i * 0.2
        ax.plot(x, y, label=f'Signal {i+1}: φ={i*45}°', linewidth=2)
    
    # Set labels
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Multiple Signals with Phase Shifts')
    ax.grid(True, alpha=0.3)
    
    # Use the new "outer" option - legend will be placed outside without overlap
    ax.legend("outer")
    
    # Save the figure
    fig.save('example_legend_outer.png')
    print("Saved: example_legend_outer.png")
    
    plt.close()


def example_legend_separate():
    """Demonstrate ax.legend('separate') functionality."""
    print("\nExample 2: Using ax.legend('separate')")
    print("-" * 40)
    
    # Create sample data
    categories = ['Method A', 'Method B', 'Method C', 'Method D']
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    
    # Generate random performance data
    np.random.seed(42)
    data = np.random.rand(len(categories), len(metrics)) * 0.3 + 0.6
    
    # Create figure
    fig, ax = mplt.subplots(figsize=(10, 6))
    
    # Create grouped bar plot
    x = np.arange(len(metrics))
    width = 0.2
    
    for i, (category, values) in enumerate(zip(categories, data)):
        offset = (i - len(categories)/2 + 0.5) * width
        ax.bar(x + offset, values, width, label=category, alpha=0.8)
    
    # Customize plot
    ax.set_xlabel('Metrics')
    ax.set_ylabel('Score')
    ax.set_title('Performance Comparison of Different Methods')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1)
    ax.grid(True, axis='y', alpha=0.3)
    
    # Save legend as separate file with custom filename
    ax.legend("separate", filename="performance_legend.png", ncol=2)
    
    # Save the main plot (legend won't appear on it)
    fig.save('example_performance_comparison.png')
    print("Saved: example_performance_comparison.png")
    print("Saved: performance_legend.png (legend only)")
    
    plt.close()


def example_combined_usage():
    """Demonstrate combined usage with real scientific data."""
    print("\nExample 3: Combined usage with time series data")
    print("-" * 40)
    
    # Create time series data
    time = np.linspace(0, 100, 500)
    
    # Simulate experimental conditions
    conditions = {
        'Control': {
            'mean': 50,
            'amplitude': 5,
            'frequency': 0.1,
            'noise': 2
        },
        'Treatment A (Low Dose)': {
            'mean': 45,
            'amplitude': 8,
            'frequency': 0.15,
            'noise': 2.5
        },
        'Treatment A (High Dose)': {
            'mean': 40,
            'amplitude': 10,
            'frequency': 0.2,
            'noise': 3
        },
        'Treatment B': {
            'mean': 55,
            'amplitude': 3,
            'frequency': 0.08,
            'noise': 1.5
        },
        'Combined A+B': {
            'mean': 42,
            'amplitude': 12,
            'frequency': 0.18,
            'noise': 3.5
        }
    }
    
    # Create figure with two subplots
    fig, (ax1, ax2) = mplt.subplots(nrows=2, ncols=1, figsize=(12, 10), sharex=True)
    
    # Plot raw data on first subplot
    for name, params in conditions.items():
        signal = (params['mean'] + 
                 params['amplitude'] * np.sin(2 * np.pi * params['frequency'] * time) +
                 np.random.normal(0, params['noise'], len(time)))
        
        # Apply smoothing
        from scipy.ndimage import gaussian_filter1d
        smoothed = gaussian_filter1d(signal, sigma=5)
        
        # Plot raw data
        ax1.plot(time, signal, alpha=0.3, linewidth=0.5)
        ax1.plot(time, smoothed, label=name, linewidth=2)
    
    ax1.set_ylabel('Response Level')
    ax1.set_title('Time Series Response - Raw and Smoothed Data')
    ax1.grid(True, alpha=0.3)
    
    # First legend - placed outside
    ax1.legend("outer", title="Experimental Conditions")
    
    # Calculate and plot derivatives on second subplot
    for name, params in conditions.items():
        signal = (params['mean'] + 
                 params['amplitude'] * np.sin(2 * np.pi * params['frequency'] * time) +
                 np.random.normal(0, params['noise'], len(time)))
        smoothed = gaussian_filter1d(signal, sigma=5)
        
        # Calculate derivative
        derivative = np.gradient(smoothed, time)
        
        ax2.plot(time, derivative, label=name, linewidth=2)
    
    ax2.set_xlabel('Time (minutes)')
    ax2.set_ylabel('Rate of Change')
    ax2.set_title('First Derivative of Response')
    ax2.grid(True, alpha=0.3)
    
    # Second legend - save separately with custom styling
    ax2.legend("separate", 
               filename="time_series_legend.png",
               ncol=2,
               title="Experimental Conditions",
               frameon=True,
               fancybox=True,
               shadow=True,
               title_fontsize=14,
               fontsize=12)
    
    # Save the complete figure
    fig.save('example_time_series_analysis.png')
    print("Saved: example_time_series_analysis.png")
    print("Saved: time_series_legend.png (shared legend)")
    
    plt.close()


def example_legend_customization():
    """Show various legend customization options."""
    print("\nExample 4: Legend customization options")
    print("-" * 40)
    
    # Create data
    x = np.linspace(0, 2*np.pi, 100)
    
    fig, axes = mplt.subplots(nrows=2, ncols=2, figsize=(12, 10))
    axes = axes.flatten()
    
    # Different legend placements
    placements = [
        ("outer", {}),
        ("upper right out", {}),
        ("lower center out", {"ncol": 3}),
        ("separate", {"filename": "custom_legend.png", "figsize": (6, 2)})
    ]
    
    for ax, (placement, kwargs) in zip(axes, placements):
        # Create plots
        ax.plot(x, np.sin(x), 'b-', label='sin(x)', linewidth=2)
        ax.plot(x, np.cos(x), 'r--', label='cos(x)', linewidth=2)
        ax.plot(x, np.sin(2*x), 'g-.', label='sin(2x)', linewidth=2)
        ax.plot(x, np.cos(2*x), 'm:', label='cos(2x)', linewidth=2)
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'Legend: {placement}')
        ax.grid(True, alpha=0.3)
        
        # Apply legend with placement
        ax.legend(placement, **kwargs)
    
    fig.tight_layout()
    fig.save('example_legend_placements.png')
    print("Saved: example_legend_placements.png")
    print("Saved: custom_legend.png (from bottom-right subplot)")
    
    plt.close()


if __name__ == "__main__":
    print("SciTeX Legend Features Demonstration")
    print("=" * 60)
    print("\nNew features:")
    print("1. ax.legend('outer') - Automatically places legend outside plot")
    print("2. ax.legend('separate') - Saves legend as separate image file")
    print("\n")
    
    # Run examples
    example_legend_outer()
    example_legend_separate()
    example_combined_usage()
    example_legend_customization()
    
    print("\n" + "=" * 60)
    print("All examples completed! Check the generated PNG files.")
    print("\nKey advantages:")
    print("- 'outer': No manual bbox_to_anchor calculations needed")
    print("- 'outer': Automatic figure adjustment to prevent cutoff")
    print("- 'separate': Easy legend extraction for presentations/papers")
    print("- 'separate': Shared legends for multi-panel figures")

# EOF