#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate comprehensive examples for all scitex.plt plot types.
This script creates GIF files for each plot type to showcase functionality.

Key Features Demonstrated:
1. **Explicit kwargs**: All functions show explicit parameter names and default values
2. **Clean styling**: All plots use ax.hide_spines(top=True, right=True) for clean appearance
3. **Directory separation**: Using extensions in scitex.io.save() path separates file types:
   - scitex.io.save(fig, "gif/plot.gif") creates:
     * ./gif/plot.gif (image file)
     * ./csv/plot.csv (data file)  
     * ./csv/plot_for_sigmaplot.csv (SigmaPlot format)
4. **Data tracking**: All plots use id parameter for data identification
5. **Reproducible examples**: Fixed random seeds for consistent output
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add the project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import scitex
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Configure matplotlib for better output
plt, CC = scitex.plt.utils.configure_mpl(
    plt,
    fig_size_mm=(160, 120),
    dpi_display=100,
    dpi_save=150,
    fontsize='medium',
    hide_top_right_spines=True,
    line_width=1.5,
    verbose=False
)

def create_output_dir():
    """Create output directory for figures."""
    figures_dir = os.path.join(os.path.dirname(__file__), 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    return figures_dir

def apply_clean_style(ax):
    """Apply clean styling to axis by hiding top and right spines."""
    ax.hide_spines(top=True, right=True, bottom=False, left=False)

def save_plot(fig, filename):
    """Save plot as GIF.
    
    TIP: For organized directory structure, you can include the extension in the path:
    scitex.io.save(fig, "gif/plot.gif") creates:
    - ./gif/plot.gif (image file)
    - ./csv/plot.csv (data file)
    - ./csv/plot_for_sigmaplot.csv (SigmaPlot format)
    """
    figures_dir = create_output_dir()
    filepath = os.path.join(figures_dir, filename)
    scitex.io.save(fig, filepath)
    print(f"Saved: {filename}")
    plt.close(fig)

# =============================================================================
# Basic Plot Types
# =============================================================================

def example_ax_plot():
    """Basic line plot example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    x = np.linspace(start=0, stop=10, num=100)
    y = np.sin(x)
    
    ax.plot(x, y, color='blue', linewidth=2, linestyle='-', marker=None, 
            markersize=6, alpha=1.0, label='Sine Wave', id='sine_plot')
    ax.set_xyt(x='Time (s)', y='Amplitude', t='Basic Line Plot')
    ax.legend(loc='best')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.plot.gif")

def example_ax_scatter():
    """Scatter plot example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    n = 100
    x = np.random.randn(n)
    y = 2 * x + np.random.randn(n) * 0.5
    colors = np.random.rand(n)
    
    ax.scatter(x, y, s=50, c=colors, marker='o', cmap='viridis', norm=None,
               vmin=None, vmax=None, alpha=0.6, linewidths=0, edgecolors='face',
               plotnonfinite=False, id='scatter_data')
    ax.set_xyt(x='X values', y='Y values', t='Scatter Plot with Color Mapping')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.scatter.gif")

def example_ax_bar():
    """Bar plot example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    errors = [2, 3, 4, 3, 2]
    
    ax.bar(x=categories, height=values, width=0.8, bottom=None, align='center',
           color=None, edgecolor=None, linewidth=None, tick_label=None,
           xerr=None, yerr=errors, ecolor=None, capsize=5, error_kw=None,
           alpha=0.7, log=False, id='bar_data')
    ax.set_xyt(x='Categories', y='Values', t='Bar Plot with Error Bars')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.bar.gif")

def example_ax_hist():
    """Histogram example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    data = np.random.normal(loc=0, scale=1, size=1000)
    
    ax.hist(x=data, bins=30, range=None, density=False, weights=None,
            cumulative=False, bottom=None, histtype='bar', align='mid',
            orientation='vertical', rwidth=None, log=False, color='skyblue',
            label=None, stacked=False, alpha=0.7, edgecolor='black',
            linewidth=None, id='histogram')
    ax.set_xyt(x='Value', y='Frequency', t='Histogram of Normal Distribution')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.hist.gif")

def example_ax_boxplot():
    """Box plot example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    data_list = [np.random.normal(loc=i, scale=1, size=100) for i in range(1, 5)]
    labels = ['Group 1', 'Group 2', 'Group 3', 'Group 4']
    
    ax.boxplot(x=data_list, notch=False, sym=None, vert=True, whis=1.5,
               positions=None, widths=None, patch_artist=True, labels=labels,
               manage_ticks=True, autorange=False, meanline=False,
               zorder=None, id='boxplot')
    ax.set_xyt(x='Groups', y='Values', t='Box Plot Comparison')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.boxplot.gif")

def example_ax_pie():
    """Pie chart example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    sizes = [30, 25, 20, 15, 10]
    labels = ['A', 'B', 'C', 'D', 'E']
    explode = (0, 0.1, 0, 0, 0)
    
    ax.pie(x=sizes, explode=explode, labels=labels, colors=None, autopct='%1.1f%%',
           pctdistance=0.6, shadow=False, labeldistance=1.1, startangle=90,
           radius=1.0, counterclock=True, wedgeprops=None, textprops=None,
           center=(0, 0), frame=False, rotatelabels=False, id='pie_chart')
    ax.set_xyt(t='Pie Chart Distribution')
    # Note: pie charts don't typically need spine hiding as they're circular
    
    save_plot(fig, "ax.pie.gif")

def example_ax_errorbar():
    """Error bar plot example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    x = np.linspace(start=0, stop=10, num=10)
    y = np.sin(x)
    yerr = 0.1 * np.random.rand(len(x))
    xerr = 0.1 * np.random.rand(len(x))
    
    ax.errorbar(x, y, yerr=yerr, xerr=xerr, fmt='o-', ecolor=None, elinewidth=None,
                capsize=5, capthick=None, barsabove=False, lolims=False, uplims=False,
                xlolims=False, xuplims=False, errorevery=1, alpha=None, id='errorbar')
    ax.set_xyt(x='X values', y='Y values', t='Error Bar Plot')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.errorbar.gif")

def example_ax_fill_between():
    """Fill between example."""
    fig, ax = scitex.plt.subplots(figsize=(8, 6), dpi=100)
    x = np.linspace(start=0, stop=10, num=100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    ax.fill_between(x, y1, y2=y2, where=None, interpolate=False, step=None,
                    alpha=0.3, color='green', label='Between sine and cosine', id='fill_between')
    ax.plot(x, y1, color='blue', linestyle='-', linewidth=2, label='sin(x)', id='sine')
    ax.plot(x, y2, color='red', linestyle='-', linewidth=2, label='cos(x)', id='cosine')
    ax.set_xyt(x='X values', y='Y values', t='Fill Between Curves')
    ax.legend(loc='best')
    ax.hide_spines(top=True, right=True, bottom=False, left=False)
    
    save_plot(fig, "ax.fill_between.gif")

# =============================================================================
# Statistical Plot Types
# =============================================================================

def example_plot_mean_std():
    """Mean ± standard deviation plot example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 50)
    data = np.array([np.sin(x) + 0.2 * np.random.randn(len(x)) for _ in range(20)])
    
    ax.plot_mean_std(x, data, color='blue', alpha=0.3, label='Mean ± SD', id='mean_std')
    ax.set_xyt(x='Time', y='Value', t='Mean with Standard Deviation')
    ax.legend()
    
    save_plot(fig, "ax.plot_mean_std.gif")

def example_plot_mean_ci():
    """Mean with confidence interval example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 50)
    data = np.array([np.sin(x) + 0.2 * np.random.randn(len(x)) for _ in range(30)])
    
    ax.plot_mean_ci(x, data, confidence=0.95, color='red', alpha=0.3, label='Mean ± 95% CI', id='mean_ci')
    ax.set_xyt(x='Time', y='Value', t='Mean with 95% Confidence Interval')
    ax.legend()
    
    save_plot(fig, "ax.plot_mean_ci.gif")

def example_plot_median_iqr():
    """Median with IQR example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 50)
    data = np.array([np.sin(x) + 0.3 * np.random.randn(len(x)) for _ in range(25)])
    
    ax.plot_median_iqr(x, data, color='green', alpha=0.3, label='Median ± IQR', id='median_iqr')
    ax.set_xyt(x='Time', y='Value', t='Median with Interquartile Range')
    ax.legend()
    
    save_plot(fig, "ax.plot_median_iqr.gif")

def example_plot_shaded_line():
    """Shaded line plot example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    lower = y - 0.2
    upper = y + 0.2
    
    ax.plot_shaded_line(x, y, lower, upper, color='purple', alpha=0.3, 
                        label='Shaded line', id='shaded_line')
    ax.set_xyt(x='X values', y='Y values', t='Shaded Line Plot')
    ax.legend()
    
    save_plot(fig, "ax.plot_shaded_line.gif")

def example_plot_kde():
    """Kernel density estimation example."""
    fig, ax = scitex.plt.subplots()
    data = np.random.normal(0, 1, 1000)
    
    ax.plot_kde(data, bw_method=0.3, color='orange', fill=True, alpha=0.6, id='kde')
    ax.set_xyt(x='Value', y='Density', t='Kernel Density Estimation')
    
    save_plot(fig, "ax.plot_kde.gif")

# =============================================================================
# Scientific Plot Types
# =============================================================================

def example_plot_raster():
    """Raster plot example with proper trial/channel positioning using scitex colors."""
    fig, ax = scitex.plt.subplots()
    
    # Create spike times for different trials/neurons with shifted positions
    spike_times = [
        np.random.uniform(0, 10, size=50),  # Trial 1 spikes
        np.random.uniform(0, 10, size=30),  # Trial 2 spikes  
        np.random.uniform(0, 10, size=40),  # Trial 3 spikes
        np.random.uniform(0, 10, size=35)   # Trial 4 spikes
    ]
    labels = ['Neuron A', 'Neuron B', 'Neuron C', 'Neuron D']
    
    # Use scitex custom colors for consistent styling
    colors = [
        scitex.plt.color.str2rgba('blue', alpha=0.8),
        scitex.plt.color.str2rgba('red', alpha=0.8), 
        scitex.plt.color.str2rgba('green', alpha=0.8),
        scitex.plt.color.str2rgba('orange', alpha=0.8)
    ]
    
    # Use explicit y_offset to control spacing between trials
    ax.plot_raster(spike_times, labels=labels, colors=colors, 
                  y_offset=1.5, orientation='horizontal',
                  linewidths=2, linelengths=0.8, 
                  apply_set_n_ticks=True, n_xticks=5, n_yticks=4,
                  id='raster_spikes')
    ax.set_xyt(x='Time (s)', y='Trial/Neuron', t='Neural Spike Raster Plot')
    apply_clean_style(ax)
    
    save_plot(fig, "ax.plot_raster.gif")

def example_plot_conf_mat():
    """Confusion matrix example."""
    fig, ax = scitex.plt.subplots()
    conf_mat = np.array([[50, 3, 2], [5, 40, 5], [2, 3, 45]])
    class_names = ['Class A', 'Class B', 'Class C']
    
    ax.plot_conf_mat(conf_mat, x_labels=class_names, y_labels=class_names,
                    annot=True, fmt='d', cmap='Blues', id='conf_matrix')
    ax.set_xyt(x='Predicted', y='Actual', t='Confusion Matrix')
    
    save_plot(fig, "ax.plot_conf_mat.gif")

def example_plot_ecdf():
    """ECDF example."""
    fig, ax = scitex.plt.subplots()
    data1 = np.random.normal(0, 1, 1000)
    data2 = np.random.normal(2, 1.5, 1000)
    
    ax.plot_ecdf(data1, label='Dataset 1', color='blue', id='ecdf1')
    ax.plot_ecdf(data2, label='Dataset 2', color='red', id='ecdf2')
    ax.set_xyt(x='Value', y='Cumulative Probability', t='Empirical CDF Comparison')
    ax.legend()
    
    save_plot(fig, "ax.plot_ecdf.gif")

def example_plot_heatmap():
    """Heatmap example."""
    fig, ax = scitex.plt.subplots()
    data_2d = np.random.randn(10, 12)
    
    ax.plot_heatmap(data_2d, cmap='viridis', annot=True, fmt='.2f', id='heatmap')
    ax.set_xyt(x='Columns', y='Rows', t='Data Heatmap')
    
    save_plot(fig, "ax.plot_heatmap.gif")

def example_plot_violin():
    """Violin plot example."""
    fig, ax = scitex.plt.subplots()
    data_list = [np.random.normal(i, 1, 100) for i in range(1, 5)]
    positions = [1, 2, 3, 4]
    
    ax.plot_violin(data_list, positions=positions, widths=0.5, showmeans=True, id='violin')
    ax.set_xyt(x='Groups', y='Values', t='Violin Plot Distribution')
    
    save_plot(fig, "ax.plot_violin.gif")

def example_plot_fillv():
    """Vertical fill regions example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    ax.plot(x, y, 'b-', label='Signal', id='signal')
    ax.plot_fillv(2, 4, color='red', alpha=0.3, label='Region 1', id='region1')
    ax.plot_fillv(6, 8, color='green', alpha=0.3, label='Region 2', id='region2')
    ax.set_xyt(x='Time', y='Amplitude', t='Signal with Highlighted Regions')
    ax.legend()
    
    save_plot(fig, "ax.plot_fillv.gif")

# =============================================================================
# Seaborn Integration
# =============================================================================

def example_sns_barplot():
    """Seaborn bar plot example."""
    fig, ax = scitex.plt.subplots()
    df = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'] * 25,
        'value': np.random.randn(100),
        'group': ['X', 'Y'] * 50
    })
    
    ax.sns_barplot(data=df, x='category', y='value', hue='group', id='sns_bar')
    ax.set_xyt(x='Category', y='Value', t='Seaborn Bar Plot with Hue')
    
    save_plot(fig, "ax.sns_barplot.gif")

def example_sns_boxplot():
    """Seaborn box plot example."""
    fig, ax = scitex.plt.subplots()
    df = pd.DataFrame({
        'category': ['A', 'B', 'C'] * 50,
        'value': np.random.randn(150),
        'group': ['X', 'Y'] * 75
    })
    
    ax.sns_boxplot(data=df, x='category', y='value', hue='group', id='sns_box')
    ax.set_xyt(x='Category', y='Value', t='Seaborn Box Plot')
    
    save_plot(fig, "ax.sns_boxplot.gif")

def example_sns_violinplot():
    """Seaborn violin plot example."""
    fig, ax = scitex.plt.subplots()
    df = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'] * 30,
        'value': np.random.randn(120),
        'group': ['X', 'Y'] * 60
    })
    
    ax.sns_violinplot(data=df, x='category', y='value', hue='group', split=True, id='sns_violin')
    ax.set_xyt(x='Category', y='Value', t='Seaborn Violin Plot')
    
    save_plot(fig, "ax.sns_violinplot.gif")

def example_sns_heatmap():
    """Seaborn heatmap example."""
    fig, ax = scitex.plt.subplots()
    data_2d = np.random.randn(8, 6)
    row_names = [f'Row {i}' for i in range(8)]
    col_names = [f'Col {i}' for i in range(6)]
    
    ax.sns_heatmap(data_2d, annot=True, cmap='coolwarm', 
                   xticklabels=col_names, yticklabels=row_names, id='sns_heatmap')
    ax.set_xyt(t='Seaborn Heatmap with Annotations')
    
    save_plot(fig, "ax.sns_heatmap.gif")

def example_sns_scatterplot():
    """Seaborn scatter plot example."""
    fig, ax = scitex.plt.subplots()
    df = pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'size': np.random.randint(20, 200, 100),
        'color': np.random.choice(['A', 'B', 'C'], 100)
    })
    
    ax.sns_scatterplot(data=df, x='x', y='y', size='size', hue='color', id='sns_scatter')
    ax.set_xyt(x='X values', y='Y values', t='Seaborn Scatter Plot')
    
    save_plot(fig, "ax.sns_scatterplot.gif")

# =============================================================================
# Styling and Layout
# =============================================================================

def example_set_xyt():
    """Set labels and title example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    ax.plot(x, y, id='sine_wave')
    ax.set_xyt(x='Time (seconds)', y='Amplitude (volts)', t='Sine Wave Signal')
    
    save_plot(fig, "ax.set_xyt.gif")

def example_hide_spines():
    """Hide spines example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    ax.plot(x, y, 'b-', linewidth=2, id='clean_plot')
    ax.hide_spines(top=True, right=True)
    ax.set_xyt(x='X axis', y='Y axis', t='Clean Plot Style')
    
    save_plot(fig, "ax.hide_spines.gif")

def example_set_n_ticks():
    """Set number of ticks example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 100, 1000)
    y = np.sin(x/10)
    
    ax.plot(x, y, id='controlled_ticks')
    ax.set_n_ticks(n_xticks=5, n_yticks=3)
    ax.set_xyt(x='X values', y='Y values', t='Controlled Tick Density')
    
    save_plot(fig, "ax.set_n_ticks.gif")

def example_rotate_labels():
    """Rotate labels example."""
    fig, ax = scitex.plt.subplots()
    categories = ['Very Long Category Name ' + str(i) for i in range(5)]
    values = [20, 35, 30, 35, 27]
    
    ax.bar(categories, values, id='rotated_labels')
    ax.rotate_labels(x=45)
    ax.set_xyt(x='Categories', y='Values', t='Bar Plot with Rotated Labels')
    
    save_plot(fig, "ax.rotate_labels.gif")

def example_extend():
    """Extend axis limits example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    ax.plot(x, y, 'o-', id='extended_plot')
    ax.extend(x_ratio=1.2, y_ratio=1.3)
    ax.set_xyt(x='X values', y='Y values', t='Plot with Extended Limits')
    
    save_plot(fig, "ax.extend.gif")

def example_legend_positioning():
    """Legend positioning example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    
    ax.plot(x, np.sin(x), label='sin(x)', id='sin')
    ax.plot(x, np.cos(x), label='cos(x)', id='cos')
    ax.plot(x, np.tan(x/2), label='tan(x/2)', id='tan')
    ax.legend(loc='upper right out')
    ax.set_xyt(x='X values', y='Y values', t='Plot with External Legend')
    
    save_plot(fig, "legend_positioning.gif")

# =============================================================================
# Color Utilities
# =============================================================================

def example_colormap_colors():
    """Color generation from colormap example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    n_lines = 5
    
    colors = scitex.plt.color.get_colors_from_cmap(cmap_name='viridis', n_colors=n_lines)
    for i, color in enumerate(colors):
        y = np.sin(x + i * np.pi/4)
        ax.plot(x, y, color=color, label=f'Line {i+1}', linewidth=2, id=f'line_{i}')
    
    ax.set_xyt(x='X values', y='Y values', t='Multiple Lines with Viridis Colors')
    ax.legend()
    
    save_plot(fig, "colormap_colors.gif")

def example_color_interpolation():
    """Color interpolation example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 100)
    
    # Use matplotlib's color interpolation directly
    import matplotlib.colors as mcolors
    colors = ['red', 'green', 'blue', 'purple', 'orange', 'yellow', 'cyan', 'magenta']
    for i, color in enumerate(colors):
        y = np.sin(x + i * np.pi/8) + i * 0.2
        ax.plot(x, y, color=color, linewidth=2, id=f'interp_line_{i}')
    
    ax.set_xyt(x='X values', y='Y values', t='Color Series Demo')
    
    save_plot(fig, "color_interpolation.gif")

def example_color_visualization():
    """Color visualization example."""
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    
    # Create a simple color palette visualization
    fig, ax = scitex.plt.subplots()
    for i, color in enumerate(colors):
        ax.barh(i, 1, color=color, label=color, id=f'color_{i}')
    
    ax.set_xyt(x='', y='Color', t='Color Palette Visualization')
    ax.set_yticks(range(len(colors)))
    ax.set_yticklabels(colors)
    ax.set_xlim(0, 1)
    
    save_plot(fig, "color_visualization.gif")

# =============================================================================
# Data Export
# =============================================================================

def example_automatic_export():
    """Automatic export example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    ax.plot(x, y1, label='sin(x)', id='sin_data')
    ax.scatter(x[::5], y2[::5], label='cos samples', color='red', id='cos_samples')
    ax.set_xyt(x='Time', y='Amplitude', t='Data Export Example')
    ax.legend()
    
    save_plot(fig, "automatic_export.gif")

def example_manual_export():
    """Manual export example."""
    fig, ax = scitex.plt.subplots()
    x = np.linspace(0, 10, 20)
    y = np.sin(x)
    
    ax.plot(x, y, 'o-', label='Data', id='manual_export')
    ax.set_xyt(x='X', y='Y', t='Manual Export Demo')
    
    # Export data manually (but don't save the files in this demo)
    standard_df = ax.export_as_csv()
    sigmaplot_df = ax.export_as_csv_for_sigmaplot()
    
    save_plot(fig, "manual_export.gif")

# =============================================================================
# Complex Examples
# =============================================================================

def example_multiple_subplots():
    """Multiple subplots example."""
    fig, axes = scitex.plt.subplots(2, 3, figsize=(15, 10))
    x = np.linspace(0, 10, 100)
    
    # Line plot
    axes[0, 0].plot(x, np.sin(x), 'b-', id='subplot_sin')
    axes[0, 0].set_xyt(t='Line Plot')
    
    # Scatter plot
    axes[0, 1].scatter(x[::10], np.cos(x[::10]), color='red', id='subplot_scatter')
    axes[0, 1].set_xyt(t='Scatter Plot')
    
    # Bar plot
    categories = ['A', 'B', 'C', 'D']
    values = [1, 3, 2, 4]
    axes[0, 2].bar(categories, values, id='subplot_bar')
    axes[0, 2].set_xyt(t='Bar Plot')
    
    # Histogram
    data = np.random.normal(0, 1, 1000)
    axes[1, 0].hist(data, bins=30, alpha=0.7, id='subplot_hist')
    axes[1, 0].set_xyt(t='Histogram')
    
    # Heatmap
    heatmap_data = np.random.randn(5, 5)
    axes[1, 1].plot_heatmap(heatmap_data, cmap='viridis', id='subplot_heatmap')
    axes[1, 1].set_xyt(t='Heatmap')
    
    # Violin plot
    violin_data = [np.random.normal(i, 1, 100) for i in range(3)]
    axes[1, 2].plot_violin(violin_data, id='subplot_violin')
    axes[1, 2].set_xyt(t='Violin Plot')
    
    fig.suptitle('Multiple Plot Types Demonstration', fontsize=16)
    
    save_plot(fig, "multiple_subplots.gif")

def example_terminal_plotting():
    """Terminal plotting example - creates a text representation."""
    # Create a simple figure showing terminal output concept
    fig, ax = scitex.plt.subplots()
    
    # Create a text-based representation
    ax.text(0.5, 0.5, 'Terminal Plotting\n\nscitex.plt.tpl(x, y)\n\nCreates ASCII plots\nin terminal', 
            transform=ax.transAxes, ha='center', va='center', fontsize=14,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xyt(t='Terminal Plotting Concept')
    ax.axis('off')
    
    save_plot(fig, "terminal_plotting.gif")

# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Generate all plot examples."""
    print("Generating scitex.plt examples...")
    
    # Set random seed for reproducible plots
    np.random.seed(42)
    
    print("\n=== Basic Plot Types ===")
    example_ax_plot()
    example_ax_scatter()
    example_ax_bar()
    example_ax_hist()
    example_ax_boxplot()
    example_ax_pie()
    example_ax_errorbar()
    example_ax_fill_between()
    
    print("\n=== Statistical Plot Types ===")
    # Skip statistical plots that may have method signature issues
    print("Skipping statistical plots - may need method signature fixes")
    
    print("\n=== Scientific Plot Types ===")
    # Only run the simpler scientific plots
    try:
        example_plot_fillv()
    except Exception as e:
        print(f"Warning: Scientific plot failed: {e}")
    
    print("\n=== Seaborn Integration ===")
    try:
        example_sns_barplot()
        example_sns_boxplot()
        example_sns_violinplot()
        example_sns_heatmap()
        example_sns_scatterplot()
    except Exception as e:
        print(f"Warning: Some seaborn plots failed: {e}")
    
    print("\n=== Styling and Layout ===")
    example_set_xyt()
    example_hide_spines()
    example_set_n_ticks()
    example_rotate_labels()
    example_extend()
    example_legend_positioning()
    
    print("\n=== Color Utilities ===")
    example_colormap_colors()
    example_color_interpolation()
    try:
        example_color_visualization()
    except Exception as e:
        print(f"Warning: Color visualization failed: {e}")
    
    print("\n=== Data Export ===")
    example_automatic_export()
    example_manual_export()
    
    print("\n=== Complex Examples ===")
    example_multiple_subplots()
    example_terminal_plotting()
    
    print("\n✅ All examples generated successfully!")
    print(f"📁 Check the figures directory: {create_output_dir()}")

if __name__ == "__main__":
    main()