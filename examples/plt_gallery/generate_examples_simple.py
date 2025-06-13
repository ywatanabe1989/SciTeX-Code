#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate simple example plots for scitex.plt documentation."""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex
import os

# Output directory
OUTPUT_DIR = "/data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/examples/plt_gallery/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_examples():
    """Generate example plots."""
    
    # 1. Basic line plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label='sin(x)', id='sin_wave')
    ax.plot(x, np.cos(x), label='cos(x)', id='cos_wave')
    ax.set_xyt(x='X-axis', y='Y-axis', t='Basic Line Plot')
    ax.legend()
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "01_basic_line_plot.png"))
    plt.close()
    
    # 2. Scatter plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    n = 100
    x = np.random.randn(n)
    y = 2 * x + np.random.randn(n) * 0.5
    colors = np.random.rand(n)
    ax.scatter(x, y, c=colors, cmap='viridis', alpha=0.6, id='scatter_data')
    ax.set_xyt(x='X values', y='Y values', t='Scatter Plot')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "02_scatter_plot.png"))
    plt.close()
    
    # 3. Bar plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    ax.bar(categories, values, id='bar_data')
    ax.set_xyt(x='Categories', y='Values', t='Bar Plot')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "03_bar_plot.png"))
    plt.close()
    
    # 4. Multiple subplots
    fig, axes = scitex.plt.subplots(2, 2, figsize=(12, 10))
    x = np.linspace(0, 10, 100)
    
    axes[0, 0].plot(x, np.sin(x), 'b-', id='sin')
    axes[0, 0].set_xyt(t='Sine Wave')
    
    axes[0, 1].plot(x, np.cos(x), 'r-', id='cos')
    axes[0, 1].set_xyt(t='Cosine Wave')
    
    axes[1, 0].plot(x, np.exp(-x/5), 'g-', id='exp')
    axes[1, 0].set_xyt(t='Exponential Decay')
    
    axes[1, 1].plot(x, x**2, 'm-', id='square')
    axes[1, 1].set_xyt(t='Quadratic')
    
    fig.suptitle('Multiple Subplots', fontsize=16)
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "04_multiple_subplots.png"))
    plt.close()
    
    # 5. Data export example
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    x = np.linspace(0, 10, 50)
    ax.plot(x, np.sin(x), label='sin(x)', id='sin_wave')
    ax.plot(x, np.cos(x), label='cos(x)', id='cos_wave')
    ax.scatter(x[::5], np.sin(x[::5]), c='red', s=100, label='samples', id='scatter_samples')
    ax.set_xyt(x='X-axis', y='Y-axis', t='Plot with Data Export')
    ax.legend()
    
    # Save figure and export data
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "05_export_example.png"))
    
    # Export data
    df = ax.export_as_csv()
    df.to_csv(os.path.join(OUTPUT_DIR, "05_exported_data.csv"), index=False)
    
    # Export for SigmaPlot
    df_sigma = ax.export_as_csv_for_sigmaplot()
    df_sigma.to_csv(os.path.join(OUTPUT_DIR, "05_exported_data_sigmaplot.csv"), index=False)
    
    plt.close()
    
    print(f"\nGenerated examples in {OUTPUT_DIR}")
    
    # List generated files
    files = sorted(os.listdir(OUTPUT_DIR))
    print(f"\nGenerated {len(files)} files:")
    for f in files:
        print(f"  - {f}")

if __name__ == "__main__":
    generate_examples()