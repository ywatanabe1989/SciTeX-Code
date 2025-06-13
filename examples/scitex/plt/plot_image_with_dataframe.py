#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 23:32:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/examples/scitex/plt/plot_image_with_dataframe.py
# ----------------------------------------
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
import scitex

# ----------------------------------------
# Demo: plot_image with DataFrame (current behavior vs desired)
# ----------------------------------------

def demonstrate_plot_image_with_dataframe():
    """Demonstrate how plot_image currently handles DataFrames and what could be improved."""
    
    # Create a sample DataFrame with meaningful indices and columns
    # This could represent a correlation matrix, comodulogram, etc.
    frequencies_phase = [2, 4, 8, 16, 32]
    frequencies_amp = [30, 50, 70, 90, 110]
    
    # Create sample PAC data
    data = np.random.rand(len(frequencies_phase), len(frequencies_amp))
    
    # Create DataFrame with meaningful labels
    df = pd.DataFrame(
        data,
        index=frequencies_phase,
        columns=frequencies_amp
    )
    df.index.name = 'Phase Frequency (Hz)'
    df.columns.name = 'Amplitude Frequency (Hz)'
    
    print("Original DataFrame:")
    print(df)
    print()
    
    # Create figure
    fig, axes = scitex.plt.subplots(ncols=3, figsize=(15, 5))
    
    # 1. Current behavior - array only
    ax1 = axes[0]
    ax1.plot_image(df.values, cbar_label='PAC Strength')
    ax1.set_xyt('X index', 'Y index', 'Current: Array values only')
    
    # 2. What happens if we pass DataFrame directly
    ax2 = axes[1]
    try:
        # This will convert to array internally
        ax2.plot_image(df, cbar_label='PAC Strength')
        ax2.set_xyt('X index', 'Y index', 'DataFrame → Array (labels lost)')
    except Exception as e:
        ax2.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_xyt('', '', 'DataFrame not supported')
    
    # 3. Desired behavior - preserve DataFrame labels
    ax3 = axes[2]
    # Manually set tick labels to show what could be done automatically
    im = ax3.plot_image(df.values, cbar_label='PAC Strength')
    
    # Set tick positions and labels based on DataFrame
    ax3._axis_mpl.set_xticks(range(len(df.columns)))
    ax3._axis_mpl.set_xticklabels(df.columns)
    ax3._axis_mpl.set_yticks(range(len(df.index)))
    ax3._axis_mpl.set_yticklabels(df.index)
    
    ax3.set_xyt(
        df.columns.name or 'Columns',
        df.index.name or 'Index', 
        'Desired: Preserve DataFrame labels'
    )
    
    fig.suptitle('plot_image with DataFrame: Current vs Desired Behavior')
    
    # Save figure
    output_path = "plot_image_dataframe_demo.png"
    scitex.io.save(fig, output_path)
    print(f"\nFigure saved to: {output_path}")
    
    # Show what could be enhanced
    print("\nSuggested enhancement for plot_image:")
    print("1. Accept DataFrame input directly")
    print("2. Automatically use index/columns as tick labels")
    print("3. Use index.name/columns.name as axis labels")
    print("4. Preserve this information in CSV export")
    
    return fig

def show_enhanced_plot_image_usage():
    """Show how an enhanced plot_image could work with DataFrames."""
    
    print("\n" + "="*60)
    print("Enhanced plot_image API (proposed):")
    print("="*60)
    
    print("""
    # Create correlation matrix DataFrame
    data = pd.DataFrame(np.random.randn(10, 10))
    data.columns = [f'Feature {i}' for i in range(10)]
    data.index = data.columns
    corr_matrix = data.corr()
    
    # Current way (labels lost):
    ax.plot_image(corr_matrix.values)
    
    # Proposed enhancement:
    ax.plot_image(corr_matrix)  # Automatically uses DataFrame labels
    
    # Would automatically:
    # - Use DataFrame index as y-axis tick labels
    # - Use DataFrame columns as x-axis tick labels  
    # - Use index.name as y-axis label
    # - Use columns.name as x-axis label
    # - Include this metadata in CSV export for reproducibility
    """)
    
    # Create actual example
    data = pd.DataFrame(np.random.randn(5, 5))
    data.columns = [f'Feature {i}' for i in range(5)]
    data.index = data.columns
    corr_matrix = data.corr()
    corr_matrix.index.name = 'Features'
    corr_matrix.columns.name = 'Features'
    
    fig, ax = scitex.plt.subplots()
    
    # Current workaround
    ax.plot_image(corr_matrix.values, cmap='coolwarm', vmin=-1, vmax=1)
    ax._axis_mpl.set_xticks(range(len(corr_matrix.columns)))
    ax._axis_mpl.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
    ax._axis_mpl.set_yticks(range(len(corr_matrix.index)))
    ax._axis_mpl.set_yticklabels(corr_matrix.index)
    ax.set_xyt('Features', 'Features', 'Correlation Matrix (manual labels)')
    
    output_path = "correlation_matrix_demo.png"
    scitex.io.save(fig, output_path)
    print(f"\nCorrelation matrix saved to: {output_path}")
    
    return fig

if __name__ == "__main__":
    # Run demonstrations
    fig1 = demonstrate_plot_image_with_dataframe()
    fig2 = show_enhanced_plot_image_usage()
    
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    print("Currently, plot_image does NOT handle DataFrame index/columns.")
    print("The DataFrame is converted to a numpy array, losing all labels.")
    print("This could be enhanced to preserve and use DataFrame metadata.")
    print("\nFor now, users need to manually set tick labels as shown above.")