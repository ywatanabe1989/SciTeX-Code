#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:30:00"
# File: /examples/save_legend_separately.py
# ----------------------------------------
"""
Example of saving legends separately from the main plot.

This demonstrates how to:
1. Create a plot with legend
2. Extract the legend
3. Save the legend as a separate image
4. Save the plot without legend
"""

import matplotlib.pyplot as plt
import numpy as np
import scitex.plt as mplt


def save_legend_separately_basic():
    """Basic example of saving legend separately using matplotlib."""
    # Create sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.cos(x)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot data with labels
    line1 = ax.plot(x, y1, label='sin(x)', linewidth=2)
    line2 = ax.plot(x, y2, label='cos(x)', linewidth=2)
    line3 = ax.plot(x, y3, label='sin(x)cos(x)', linewidth=2)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Trigonometric Functions')
    
    # Create legend
    legend = ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Save the full figure with legend
    fig.savefig('plot_with_legend.png', dpi=150, bbox_inches='tight')
    
    # Method 1: Save legend only by creating a new figure
    def export_legend(legend, filename="legend.png"):
        fig_legend = legend.figure
        fig_legend.canvas.draw()
        bbox = legend.get_window_extent().transformed(fig_legend.dpi_scale_trans.inverted())
        fig_legend.savefig(filename, dpi=150, bbox_inches=bbox)
    
    export_legend(legend, "legend_only_method1.png")
    
    # Method 2: Create a separate figure just for the legend
    fig_legend = plt.figure(figsize=(3, 2))
    handles, labels = ax.get_legend_handles_labels()
    fig_legend.legend(handles, labels, loc='center', frameon=True, fancybox=True, shadow=True)
    fig_legend.savefig('legend_only_method2.png', dpi=150, bbox_inches='tight')
    
    # Method 3: Remove legend and save plot without it
    legend.remove()
    fig.savefig('plot_without_legend.png', dpi=150, bbox_inches='tight')
    
    plt.close('all')


def save_legend_separately_scitex():
    """Example using SciTeX plotting framework."""
    # Create sample data
    x = np.linspace(0, 10, 100)
    data = {
        'sin(x)': np.sin(x),
        'cos(x)': np.cos(x),
        'sin(x)cos(x)': np.sin(x) * np.cos(x),
    }
    
    # Create SciTeX figure
    fig, ax = mplt.subplots(figsize=(8, 6))
    
    # Plot data
    for label, y in data.items():
        ax.plot(x, y, label=label, linewidth=2)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Trigonometric Functions')
    
    # Create legend on the axis
    legend = ax._axis_mpl.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Save full plot
    fig.save('scitex_plot_with_legend.png')
    
    # Extract and save legend separately
    def save_legend_from_axis(ax_mpl, filename):
        """Save legend from matplotlib axis."""
        handles, labels = ax_mpl.get_legend_handles_labels()
        if handles:
            fig_leg = plt.figure(figsize=(3, 2))
            legend = fig_leg.legend(handles, labels, loc='center', 
                                   frameon=True, fancybox=True, shadow=True)
            fig_leg.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close(fig_leg)
    
    save_legend_from_axis(ax._axis_mpl, 'scitex_legend_only.png')
    
    # Remove legend and save plot without it
    if legend:
        legend.remove()
    fig.save('scitex_plot_without_legend.png')
    
    plt.close('all')


def save_legend_outside_plot():
    """Example of placing legend outside the plot area."""
    # Create sample data
    x = np.linspace(0, 10, 100)
    
    # Create plot with more lines
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i in range(5):
        y = np.sin(x + i * np.pi/4)
        ax.plot(x, y, label=f'sin(x + {i}π/4)', linewidth=2)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Phase-shifted Sine Waves')
    
    # Place legend outside the plot area
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Save with tight layout to include the legend
    fig.savefig('plot_with_outside_legend.png', dpi=150, bbox_inches='tight')
    
    # Create a horizontal legend below the plot
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    for i in range(5):
        y = np.sin(x + i * np.pi/4)
        ax2.plot(x, y, label=f'sin(x + {i}π/4)', linewidth=2)
    
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.set_title('Phase-shifted Sine Waves')
    
    # Place legend below the plot
    ax2.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=5)
    
    fig2.savefig('plot_with_bottom_legend.png', dpi=150, bbox_inches='tight')
    
    plt.close('all')


def advanced_legend_extraction():
    """Advanced example with custom legend styling and extraction."""
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot different types of data
    x = np.linspace(0, 10, 100)
    
    # Lines
    ax.plot(x, np.sin(x), 'b-', linewidth=2, label='Line plot')
    
    # Scatter
    ax.scatter(x[::10], np.cos(x[::10]), c='red', s=100, label='Scatter plot', alpha=0.6)
    
    # Bar (simplified)
    bar_x = np.arange(5)
    ax.bar(bar_x, np.random.rand(5), width=0.5, alpha=0.5, label='Bar plot')
    
    # Create custom legend elements
    custom_lines = [
        Line2D([0], [0], color='blue', linewidth=2),
        Line2D([0], [0], marker='o', color='red', linewidth=0, markersize=10, alpha=0.6),
        mpatches.Rectangle((0, 0), 1, 1, facecolor='C0', alpha=0.5)
    ]
    custom_labels = ['Line plot', 'Scatter plot', 'Bar plot']
    
    # Create main plot
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Mixed Plot Types')
    ax.set_xlim(0, 10)
    
    # Create legend figure with custom elements
    fig_legend = plt.figure(figsize=(4, 3))
    legend = fig_legend.legend(custom_lines, custom_labels, 
                              loc='center', 
                              title='Plot Types',
                              frameon=True, 
                              fancybox=True, 
                              shadow=True,
                              fontsize=12,
                              title_fontsize=14)
    
    # Save legend
    fig_legend.savefig('custom_legend_only.png', dpi=150, bbox_inches='tight')
    
    # Save plot without legend
    fig.savefig('plot_without_custom_legend.png', dpi=150, bbox_inches='tight')
    
    plt.close('all')


if __name__ == "__main__":
    print("Demonstrating different ways to save legends separately...")
    
    # Run examples
    print("1. Basic legend extraction")
    save_legend_separately_basic()
    
    print("2. SciTeX framework legend extraction")
    save_legend_separately_scitex()
    
    print("3. Legend placement outside plot")
    save_legend_outside_plot()
    
    print("4. Advanced custom legend")
    advanced_legend_extraction()
    
    print("\nCompleted! Check the generated PNG files.")

# EOF