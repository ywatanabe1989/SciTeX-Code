#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate example plots for scitex.plt documentation."""

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

def generate_basic_plots():
    """Generate basic plot examples."""
    print("Generating basic plots...")
    
    # 1. Basic line plot with tracking
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label='sin(x)', id='sin_wave')
    ax.plot(x, np.cos(x), label='cos(x)', id='cos_wave')
    ax.set_xyt(x='X-axis', y='Y-axis', t='Basic Line Plot with Tracking')
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
    ax.set_xyt(x='X values', y='Y values', t='Scatter Plot with Colors')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "02_scatter_plot.png"))
    plt.close()
    
    # 3. Bar plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    errors = [5, 3, 4, 2, 4]
    ax.bar(categories, values, yerr=errors, capsize=5, id='bar_data')
    ax.set_xyt(x='Categories', y='Values', t='Bar Plot with Error Bars')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "03_bar_plot.png"))
    plt.close()
    
    # 4. Histogram
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    data = np.random.normal(100, 15, 1000)
    ax.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black', id='hist_data')
    ax.set_xyt(x='Value', y='Frequency', t='Histogram')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "04_histogram.png"))
    plt.close()
    
    # 5. Box plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    data = [np.random.normal(100, std, 100) for std in [10, 15, 20, 25]]
    ax.boxplot(data, labels=['Group 1', 'Group 2', 'Group 3', 'Group 4'], id='box_data')
    ax.set_xyt(x='Groups', y='Values', t='Box Plot')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "05_boxplot.png"))
    plt.close()

def generate_advanced_plots():
    """Generate advanced plot examples."""
    print("Generating advanced plots...")
    
    # 6. Heatmap
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    data = np.random.randn(10, 12)
    ax.plot_heatmap(data, cmap='coolwarm', id='heatmap_data')
    ax.set_xyt(x='Columns', y='Rows', t='Heatmap Example')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "06_heatmap.png"))
    plt.close()
    
    # 7. Statistical plot - mean with std
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    x = np.linspace(0, 10, 20)
    n_trials = 50
    data = np.array([np.sin(x) + np.random.randn(len(x)) * 0.3 for _ in range(n_trials)])
    ax.plot_mean_std(x, data, color='blue', alpha=0.3, id='mean_std_data')
    ax.set_xyt(x='X-axis', y='Y-axis', t='Mean ± Standard Deviation')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "07_mean_std_plot.png"))
    plt.close()
    
    # 8. Violin plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    data = [np.random.normal(loc, 1, 100) for loc in [0, 1, 2, 1.5]]
    ax.plot_violin(data, positions=[1, 2, 3, 4], id='violin_data')
    ax.set_xyt(x='Groups', y='Values', t='Violin Plot')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "08_violin_plot.png"))
    plt.close()
    
    # 9. Fill between (shaded area)
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    lower = y - 0.2
    upper = y + 0.2
    ax.plot(x, y, 'b-', label='Mean', id='mean_line')
    ax.fill_between(x, lower, upper, alpha=0.3, label='Confidence', id='confidence_band')
    ax.set_xyt(x='X-axis', y='Y-axis', t='Fill Between Example')
    ax.legend()
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "09_fill_between.png"))
    plt.close()
    
    # 10. ECDF plot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    data = np.random.normal(0, 1, 1000)
    ax.plot_ecdf(data, id='ecdf_data')
    ax.set_xyt(x='Value', y='Cumulative Probability', t='Empirical CDF')
    ax.grid(True, alpha=0.3)
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "10_ecdf_plot.png"))
    plt.close()

def generate_subplot_examples():
    """Generate subplot examples."""
    print("Generating subplot examples...")
    
    # 11. Multiple subplots
    fig, axes = scitex.plt.subplots(2, 2, figsize=(12, 10))
    x = np.linspace(0, 10, 100)
    
    # Plot different functions
    axes[0, 0].plot(x, np.sin(x), 'b-', id='sin')
    axes[0, 0].set_xyt(t='Sine Wave')
    
    axes[0, 1].plot(x, np.cos(x), 'r-', id='cos')
    axes[0, 1].set_xyt(t='Cosine Wave')
    
    axes[1, 0].plot(x, np.exp(-x/5), 'g-', id='exp')
    axes[1, 0].set_xyt(t='Exponential Decay')
    
    axes[1, 1].plot(x, x**2, 'm-', id='square')
    axes[1, 1].set_xyt(t='Quadratic')
    
    fig.suptitle('Multiple Subplots Example', fontsize=16)
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "11_multiple_subplots.png"))
    plt.close()
    
    # 12. Shared axes
    fig, axes = scitex.plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    t = np.linspace(0, 2*np.pi, 200)
    
    axes[0].plot(t, np.sin(t), id='signal1')
    axes[0].set_ylabel('Signal 1')
    
    axes[1].plot(t, np.sin(2*t), id='signal2')
    axes[1].set_ylabel('Signal 2')
    
    axes[2].plot(t, np.sin(3*t), id='signal3')
    axes[2].set_ylabel('Signal 3')
    axes[2].set_xlabel('Time (s)')
    
    fig.suptitle('Shared X-axis Example', fontsize=14)
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "12_shared_axes.png"))
    plt.close()

def generate_seaborn_examples():
    """Generate seaborn integration examples."""
    print("Generating seaborn examples...")
    
    # 13. Seaborn barplot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    df = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'] * 3,
        'value': np.random.randn(12) + [1, 2, 3, 4] * 3,
        'group': ['X', 'X', 'X', 'X', 'Y', 'Y', 'Y', 'Y', 'Z', 'Z', 'Z', 'Z']
    })
    ax.sns_barplot(data=df, x='category', y='value', hue='group', id='sns_bar')
    ax.set_xyt(x='Category', y='Value', t='Seaborn Bar Plot')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "13_seaborn_barplot.png"))
    plt.close()
    
    # 14. Seaborn violinplot
    fig, ax = scitex.plt.subplots(figsize=(8, 6))
    ax.sns_violinplot(data=df, x='category', y='value', id='sns_violin')
    ax.set_xyt(t='Seaborn Violin Plot')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "14_seaborn_violinplot.png"))
    plt.close()

def generate_color_examples():
    """Generate color utility examples."""
    print("Generating color examples...")
    
    # 15. Color palette visualization
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    
    # Get colors from colormap
    colors = scitex.plt.color.get_colors_from_cmap(8, cmap='viridis')
    
    # Plot bars with different colors
    x = np.arange(len(colors))
    heights = np.random.rand(len(colors)) + 0.5
    bars = ax.bar(x, heights, color=colors, id='color_bars')
    
    ax.set_xyt(x='Color Index', y='Value', t='Colors from Colormap')
    ax.set_xticks(x)
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "15_colormap_example.png"))
    plt.close()
    
    # 16. Color interpolation
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    
    # Interpolate between colors
    start_colors = ['red', 'blue', 'green']
    interpolated = scitex.plt.color.interpolate(start_colors, 20)
    
    # Create color patches
    for i, color in enumerate(interpolated):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=color))
    
    ax.set_xlim(0, len(interpolated))
    ax.set_ylim(0, 1)
    ax.set_xyt(t='Color Interpolation Example')
    ax.set_aspect('equal')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "16_color_interpolation.png"))
    plt.close()

def generate_special_plots():
    """Generate special plot examples."""
    print("Generating special plots...")
    
    # 17. Raster plot
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    n_trials = 20
    spike_times = [np.sort(np.random.uniform(0, 10, np.random.randint(5, 20))) 
                   for _ in range(n_trials)]
    trial_ids = [[i] * len(spikes) for i, spikes in enumerate(spike_times)]
    
    # Flatten lists
    all_spikes = np.concatenate(spike_times)
    all_trials = np.concatenate(trial_ids)
    
    ax.plot_raster(all_spikes, all_trials, id='raster_data')
    ax.set_xyt(x='Time (s)', y='Trial', t='Raster Plot Example')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "17_raster_plot.png"))
    plt.close()
    
    # 18. Confusion matrix
    fig, ax = scitex.plt.subplots(figsize=(8, 8))
    conf_mat = np.array([[50, 3, 2], [5, 40, 5], [2, 3, 45]])
    ax.plot_conf_mat(conf_mat, annot=True, fmt='d', cmap='Blues', id='conf_mat')
    ax.set_xyt(x='Predicted', y='Actual', t='Confusion Matrix')
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "18_confusion_matrix.png"))
    plt.close()
    
    # 19. Fill vertical regions
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.randn(100) * 0.1
    ax.plot(x, y, 'k-', label='Signal', id='signal')
    
    # Highlight regions
    ax.plot_fillv(2, 3, color='red', alpha=0.3, id='region1')
    ax.plot_fillv(5, 6, color='blue', alpha=0.3, id='region2')
    ax.plot_fillv(8, 9, color='green', alpha=0.3, id='region3')
    
    ax.set_xyt(x='Time', y='Amplitude', t='Vertical Fill Regions')
    ax.legend()
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "19_fill_vertical.png"))
    plt.close()
    
    # 20. Statistical shaded line plot
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    x = np.linspace(0, 10, 20)
    n_samples = 100
    
    # Generate data with different variability
    y_samples = []
    for xi in x:
        y_samples.append(np.sin(xi) + np.random.normal(0, 0.1 + 0.05 * xi, n_samples))
    
    y_samples = np.array(y_samples).T
    
    # Plot with confidence interval
    ax.plot_mean_ci(x, y_samples, confidence=0.95, color='purple', id='mean_ci')
    ax.set_xyt(x='X-axis', y='Y-axis', t='Mean with 95% Confidence Interval')
    ax.grid(True, alpha=0.3)
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "20_mean_confidence_interval.png"))
    plt.close()

def generate_style_examples():
    """Generate style customization examples."""
    print("Generating style examples...")
    
    # 21. Custom styled plot
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    ax.plot(x, y1, 'b-', linewidth=2, label='sin(x)', id='sin')
    ax.plot(x, y2, 'r--', linewidth=2, label='cos(x)', id='cos')
    
    # Apply custom styling
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    ax.set_n_ticks(n_xticks=6, n_yticks=5)
    ax.rotate_labels(x=45)
    ax.set_xyt(x='Time (s)', y='Amplitude', t='Customized Plot Style')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, linestyle=':')
    
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "21_custom_style.png"))
    plt.close()
    
    # 22. Scientific notation
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    x = np.linspace(0, 1, 100)
    y = np.exp(x) * 1e-6
    
    ax.plot(x, y, 'g-', linewidth=2, id='exp_small')
    # Use ticklabel_format instead of sci_note
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
    ax.set_xyt(x='X-axis', y='Y-axis (scientific)', t='Scientific Notation Example')
    ax.grid(True, alpha=0.3)
    
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "22_scientific_notation.png"))
    plt.close()

def generate_export_example():
    """Generate data export example."""
    print("Generating export example...")
    
    # 23. Plot with data export
    fig, ax = scitex.plt.subplots(figsize=(10, 6))
    
    # Create multiple plots
    x = np.linspace(0, 10, 50)
    ax.plot(x, np.sin(x), label='sin(x)', id='sin_wave')
    ax.plot(x, np.cos(x), label='cos(x)', id='cos_wave')
    ax.scatter(x[::5], np.sin(x[::5]), c='red', s=100, label='samples', id='scatter_samples')
    
    ax.set_xyt(x='X-axis', y='Y-axis', t='Plot with Data Export Capability')
    ax.legend()
    
    # Save figure and data
    scitex.io.save(fig, os.path.join(OUTPUT_DIR, "23_export_example.png"))
    
    # Export data
    df = ax.export_as_csv()
    df.to_csv(os.path.join(OUTPUT_DIR, "23_exported_data.csv"), index=False)
    
    # Export for SigmaPlot
    df_sigma = ax.export_as_csv_for_sigmaplot()
    df_sigma.to_csv(os.path.join(OUTPUT_DIR, "23_exported_data_sigmaplot.csv"), index=False)
    
    plt.close()

def main():
    """Generate all examples."""
    print(f"Generating scitex.plt examples in {OUTPUT_DIR}")
    
    generate_basic_plots()
    generate_advanced_plots()
    generate_subplot_examples()
    generate_seaborn_examples()
    generate_color_examples()
    generate_special_plots()
    generate_style_examples()
    generate_export_example()
    
    print("\nAll examples generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # List generated files
    files = sorted(os.listdir(OUTPUT_DIR))
    print(f"\nGenerated {len(files)} files:")
    for f in files:
        print(f"  - {f}")

if __name__ == "__main__":
    main()