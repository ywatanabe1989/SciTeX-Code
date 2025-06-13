#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 18:50:00 (ywatanabe)"
# File: ./examples/plt/basic_plotting.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/plt/basic_plotting.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic scitex.plt functionality
  - Shows automatic figure saving and tracking
  - Creates various plot types
  - Saves all figures and data automatically

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex
    - numpy
    - matplotlib
IO:
  - input-files:
    - None (generates data programmatically)

  - output-files:
    - ./examples/plt/basic_plotting_out/figures/*.png
    - ./examples/plt/basic_plotting_out/figures/*.csv (plot data)
    - ./examples/plt/basic_plotting_out/logs/*
"""

"""Imports"""
import numpy as np
import scitex

"""Parameters"""
N_POINTS = 100
NOISE_LEVEL = 0.1

"""Functions"""
def create_plots():
    """Create various plots demonstrating scitex.plt capabilities."""
    # Start with plotting enabled
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(__FILE__, sys_=True, plt_=True)
    
    print("SciTeX Plotting Demonstration")
    print("=" * 50)
    
    # Generate demo data
    x = np.linspace(0, 4 * np.pi, N_POINTS)
    y1 = np.sin(x) + np.random.randn(N_POINTS) * NOISE_LEVEL
    y2 = np.cos(x) + np.random.randn(N_POINTS) * NOISE_LEVEL
    
    # 1. Simple line plot
    print("\n1. Creating simple line plot...")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, y1, 'b-', label='sin(x) + noise', alpha=0.7)
    ax.plot(x, y2, 'r-', label='cos(x) + noise', alpha=0.7)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Simple Line Plot Example')
    ax.legend()
    ax.grid(True, alpha=0.3)
    scitex.io.save(fig, "simple_line_plot.png")
    
    # 2. Scatter plot with color mapping
    print("2. Creating scatter plot...")
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = x  # Color by x-value
    scatter = ax.scatter(y1, y2, c=colors, cmap='viridis', alpha=0.6, s=50)
    ax.set_xlabel('sin(x) + noise')
    ax.set_ylabel('cos(x) + noise')
    ax.set_title('Scatter Plot with Color Mapping')
    plt.colorbar(scatter, ax=ax, label='X value')
    scitex.io.save(fig, "scatter_plot.png")
    
    # 3. Subplots
    print("3. Creating subplot figure...")
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle('Multiple Subplots Example', fontsize=14)
    
    # Subplot 1: Histogram
    axes[0, 0].hist(y1, bins=20, alpha=0.7, color='blue', edgecolor='black')
    axes[0, 0].set_title('Histogram of sin(x) + noise')
    axes[0, 0].set_xlabel('Value')
    axes[0, 0].set_ylabel('Count')
    
    # Subplot 2: Box plot
    axes[0, 1].boxplot([y1, y2], labels=['sin', 'cos'])
    axes[0, 1].set_title('Box Plot Comparison')
    axes[0, 1].set_ylabel('Value')
    
    # Subplot 3: Error bars
    mean_y1 = np.convolve(y1, np.ones(10)/10, mode='valid')
    std_y1 = np.array([y1[i:i+10].std() for i in range(len(mean_y1))])
    x_err = x[:len(mean_y1)]
    axes[1, 0].errorbar(x_err, mean_y1, yerr=std_y1, fmt='o-', alpha=0.7, 
                        capsize=5, label='Moving average ± std')
    axes[1, 0].set_title('Error Bar Plot')
    axes[1, 0].set_xlabel('X')
    axes[1, 0].set_ylabel('Y')
    axes[1, 0].legend()
    
    # Subplot 4: Filled area
    axes[1, 1].fill_between(x, y1-NOISE_LEVEL, y1+NOISE_LEVEL, 
                           alpha=0.3, label='sin ± noise')
    axes[1, 1].plot(x, y1, 'b-', label='sin(x)')
    axes[1, 1].set_title('Filled Area Plot')
    axes[1, 1].set_xlabel('X')
    axes[1, 1].set_ylabel('Y')
    axes[1, 1].legend()
    
    plt.tight_layout()
    scitex.io.save(fig, "subplots_example.png")
    
    # 4. Using SciTeX color scheme
    print("4. Creating plot with SciTeX colors...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Use colors from CC (color collection)
    for i, (color_name, color) in enumerate(list(CC.items())[:5]):
        y_offset = i * 0.5
        ax.plot(x, np.sin(x + i) + y_offset, color=color, 
                linewidth=2, label=color_name)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y (offset)')
    ax.set_title('SciTeX Color Scheme Example')
    ax.legend()
    ax.grid(True, alpha=0.3)
    scitex.io.save(fig, "scitex_colors.png")
    
    # 5. Heatmap
    print("5. Creating heatmap...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create 2D data
    data_2d = np.outer(np.sin(x), np.cos(x)) + np.random.randn(N_POINTS, N_POINTS) * 0.1
    im = ax.imshow(data_2d, cmap='RdBu_r', aspect='auto')
    ax.set_title('Heatmap Example')
    ax.set_xlabel('X index')
    ax.set_ylabel('Y index')
    plt.colorbar(im, ax=ax, label='Value')
    scitex.io.save(fig, "heatmap.png")
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"✓ Created 5 different plot types")
    print(f"✓ All figures automatically saved to: {CONFIG.SDIR}/figures/")
    print(f"✓ Plot data can be exported as CSV using export functionality")
    
    # Close and finalize
    scitex.gen.close(CONFIG)
    print("\n✅ Plotting demo completed successfully!")

"""Main"""
if __name__ == "__main__":
    create_plots()

"""EOF"""