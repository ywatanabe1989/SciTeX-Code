#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:36:00"
# File: /examples/sns_lineplot_export_for_sigmaplot.py
# ----------------------------------------
"""
Example of exporting sns_lineplot data to CSV for SigmaPlot.

This demonstrates:
1. Creating plots with sns_lineplot
2. Exporting the plotted data to CSV
3. Formatting data for SigmaPlot compatibility
4. Creating separate data files for each condition/group
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scitex.plt as mplt
import scitex.io as mio


def create_time_series_data():
    """Create sample time series data with error bars."""
    np.random.seed(42)
    
    # Experimental parameters
    time_points = np.array([0, 1, 2, 4, 8, 12, 24, 48])  # hours
    conditions = ['Control', 'Treatment A', 'Treatment B']
    n_replicates = 6
    
    data_list = []
    
    for condition in conditions:
        for replicate in range(n_replicates):
            # Generate condition-specific response curves
            if condition == 'Control':
                baseline = 100
                response = baseline + np.random.normal(0, 5, len(time_points))
            elif condition == 'Treatment A':
                baseline = 100
                # Exponential decay
                response = baseline * np.exp(-0.05 * time_points) + np.random.normal(0, 4, len(time_points))
            else:  # Treatment B
                baseline = 100
                # Linear increase
                response = baseline + 2 * time_points + np.random.normal(0, 6, len(time_points))
            
            for t, val in zip(time_points, response):
                data_list.append({
                    'Time_hr': t,
                    'Response': val,
                    'Condition': condition,
                    'Replicate': replicate + 1
                })
    
    return pd.DataFrame(data_list)


def export_for_sigmaplot_format1(df, output_prefix='sigmaplot'):
    """
    Export data in SigmaPlot Format 1: Wide format with columns for each condition.
    
    This format is ideal for creating line plots with error bars in SigmaPlot.
    Each condition gets its own column, with replicates in rows.
    """
    # Pivot data to wide format
    pivot_df = df.pivot_table(
        values='Response',
        index=['Time_hr', 'Replicate'],
        columns='Condition',
        aggfunc='first'
    ).reset_index()
    
    # Sort by time and replicate
    pivot_df = pivot_df.sort_values(['Time_hr', 'Replicate'])
    
    # Save to CSV
    filename = f'{output_prefix}_wide_format.csv'
    pivot_df.to_csv(filename, index=False)
    print(f"Saved wide format to: {filename}")
    
    # Also create a summary table with mean ± SEM
    summary_df = df.groupby(['Time_hr', 'Condition'])['Response'].agg([
        ('Mean', 'mean'),
        ('SEM', lambda x: x.sem()),
        ('SD', 'std'),
        ('N', 'count')
    ]).reset_index()
    
    # Pivot summary to wide format
    summary_pivot = summary_df.pivot_table(
        values=['Mean', 'SEM', 'SD', 'N'],
        index='Time_hr',
        columns='Condition'
    )
    
    # Flatten column names
    summary_pivot.columns = ['_'.join(col).strip() for col in summary_pivot.columns.values]
    summary_pivot = summary_pivot.reset_index()
    
    summary_filename = f'{output_prefix}_summary_stats.csv'
    summary_pivot.to_csv(summary_filename, index=False)
    print(f"Saved summary statistics to: {summary_filename}")
    
    return pivot_df, summary_pivot


def export_for_sigmaplot_format2(df, output_prefix='sigmaplot'):
    """
    Export data in SigmaPlot Format 2: XY pairs for each condition.
    
    This format creates separate X,Y column pairs for each condition,
    which is useful for scatter plots or when conditions have different X values.
    """
    conditions = df['Condition'].unique()
    
    # Create a dictionary to hold data for each condition
    xy_data = {}
    max_rows = 0
    
    for condition in conditions:
        cond_data = df[df['Condition'] == condition].copy()
        
        # Get unique time points and their mean responses
        time_response = cond_data.groupby('Time_hr')['Response'].agg(['mean', 'sem']).reset_index()
        
        # Store X, Y, and error data
        xy_data[f'{condition}_X'] = time_response['Time_hr'].values
        xy_data[f'{condition}_Y'] = time_response['mean'].values
        xy_data[f'{condition}_Error'] = time_response['sem'].values
        
        max_rows = max(max_rows, len(time_response))
    
    # Pad shorter arrays with NaN to match length
    for key in xy_data:
        if len(xy_data[key]) < max_rows:
            xy_data[key] = np.pad(xy_data[key], 
                                  (0, max_rows - len(xy_data[key])), 
                                  constant_values=np.nan)
    
    # Create DataFrame
    xy_df = pd.DataFrame(xy_data)
    
    # Save to CSV
    xy_filename = f'{output_prefix}_xy_pairs.csv'
    xy_df.to_csv(xy_filename, index=False)
    print(f"Saved XY pairs format to: {xy_filename}")
    
    return xy_df


def plot_and_export_with_scitex(df):
    """Create plot with SciTeX and export the data."""
    # Create SciTeX figure
    fig, ax = mplt.subplots(figsize=(10, 6))
    
    # Plot with sns_lineplot
    ax.sns_lineplot(
        data=df,
        x='Time_hr',
        y='Response',
        hue='Condition',
        errorbar='se',
        markers=True,
        markersize=8,
        linewidth=2.5,
        err_style='bars',
        err_kws={'capsize': 5},
        palette='Set1'
    )
    
    # Customize plot
    ax.set_xlabel('Time (hours)', fontsize=12)
    ax.set_ylabel('Response Level', fontsize=12)
    ax.set_title('Time Course Analysis', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Save plot
    fig.save('sns_lineplot_for_sigmaplot.png')
    
    # Export the plotted data using SciTeX export functionality
    exported_df = mplt.export_as_csv(fig.history)
    
    # Save the exported data
    exported_df.to_csv('scitex_exported_plot_data.csv', index=False)
    print(f"Saved SciTeX exported data to: scitex_exported_plot_data.csv")
    print(f"Exported columns: {list(exported_df.columns)}")
    
    return fig, exported_df


def create_sigmaplot_ready_files(df):
    """
    Create multiple file formats optimized for different SigmaPlot workflows.
    """
    # 1. Individual condition files (easiest for SigmaPlot)
    conditions = df['Condition'].unique()
    
    for condition in conditions:
        cond_data = df[df['Condition'] == condition]
        
        # Pivot so each replicate is a column
        replicate_df = cond_data.pivot(
            index='Time_hr',
            columns='Replicate',
            values='Response'
        )
        
        # Add column headers that SigmaPlot likes
        replicate_df.columns = [f'Rep_{i}' for i in replicate_df.columns]
        replicate_df.index.name = 'Time_hr'
        replicate_df = replicate_df.reset_index()
        
        # Save each condition separately
        filename = f'sigmaplot_{condition.replace(" ", "_")}.csv'
        replicate_df.to_csv(filename, index=False)
        print(f"Saved {condition} data to: {filename}")
    
    # 2. Create a master file with all raw data (long format)
    # This is useful for SigmaPlot's statistical analysis features
    raw_filename = 'sigmaplot_raw_data_long.csv'
    df.to_csv(raw_filename, index=False)
    print(f"Saved raw data (long format) to: {raw_filename}")
    
    # 3. Create grouped means file
    means_df = df.groupby(['Time_hr', 'Condition']).agg({
        'Response': ['mean', 'sem', 'std', 'count']
    }).reset_index()
    
    # Flatten column names
    means_df.columns = ['Time_hr', 'Condition', 'Mean', 'SEM', 'SD', 'N']
    
    means_filename = 'sigmaplot_grouped_means.csv'
    means_df.to_csv(means_filename, index=False)
    print(f"Saved grouped means to: {means_filename}")
    
    return means_df


def create_sigmaplot_template_file():
    """
    Create a template file with instructions for SigmaPlot users.
    """
    template_content = """SigmaPlot Data Import Instructions
=====================================

This dataset contains time course data with three conditions.
The data has been exported in multiple formats for your convenience.

Files included:
--------------
1. sigmaplot_wide_format.csv
   - Wide format with all conditions in columns
   - Best for: Line plots with multiple series

2. sigmaplot_xy_pairs.csv
   - X,Y pairs for each condition
   - Best for: Scatter plots or when X values differ

3. sigmaplot_Control.csv, sigmaplot_Treatment_A.csv, sigmaplot_Treatment_B.csv
   - Individual files for each condition
   - Best for: Creating plots one condition at a time

4. sigmaplot_summary_stats.csv
   - Pre-calculated means, SEM, SD, and N
   - Best for: Quick plotting without calculating stats

5. sigmaplot_raw_data_long.csv
   - All raw data in long format
   - Best for: Statistical analysis in SigmaPlot

To create a line plot with error bars in SigmaPlot:
--------------------------------------------------
1. Open sigmaplot_wide_format.csv
2. Select columns for one condition (e.g., all 'Control' columns)
3. Create Graph > Line Plot > Simple Error Bars
4. Repeat for other conditions

To perform statistical analysis:
-------------------------------
1. Open sigmaplot_raw_data_long.csv
2. Use Statistics > ANOVA > Two Way Repeated Measures
3. Set 'Time_hr' as within-subject factor
4. Set 'Condition' as between-subject factor

Data structure:
--------------
- Time points: 0, 1, 2, 4, 8, 12, 24, 48 hours
- Conditions: Control, Treatment A, Treatment B
- Replicates: 6 per condition
- Response: Measured values with condition-specific patterns
"""
    
    with open('SIGMAPLOT_README.txt', 'w') as f:
        f.write(template_content)
    
    print("Created SigmaPlot instructions file: SIGMAPLOT_README.txt")


if __name__ == "__main__":
    print("Creating and exporting sns_lineplot data for SigmaPlot...")
    print("=" * 60)
    
    # Create sample data
    df = create_time_series_data()
    print(f"\nCreated dataset with {len(df)} observations")
    print(f"Conditions: {df['Condition'].unique()}")
    print(f"Time points: {sorted(df['Time_hr'].unique())}")
    
    # Plot and export with SciTeX
    print("\n1. Creating plot with SciTeX and exporting data...")
    fig, exported_df = plot_and_export_with_scitex(df)
    
    # Export in various SigmaPlot-friendly formats
    print("\n2. Exporting data in SigmaPlot Format 1 (Wide format)...")
    wide_df, summary_df = export_for_sigmaplot_format1(df)
    
    print("\n3. Exporting data in SigmaPlot Format 2 (XY pairs)...")
    xy_df = export_for_sigmaplot_format2(df)
    
    print("\n4. Creating individual condition files...")
    means_df = create_sigmaplot_ready_files(df)
    
    print("\n5. Creating SigmaPlot instructions...")
    create_sigmaplot_template_file()
    
    print("\n" + "=" * 60)
    print("Export complete! Files created:")
    print("- sns_lineplot_for_sigmaplot.png (plot image)")
    print("- scitex_exported_plot_data.csv (SciTeX export)")
    print("- sigmaplot_wide_format.csv (wide format)")
    print("- sigmaplot_summary_stats.csv (summary statistics)")
    print("- sigmaplot_xy_pairs.csv (XY pairs)")
    print("- sigmaplot_Control.csv (Control data)")
    print("- sigmaplot_Treatment_A.csv (Treatment A data)")
    print("- sigmaplot_Treatment_B.csv (Treatment B data)")
    print("- sigmaplot_raw_data_long.csv (all raw data)")
    print("- sigmaplot_grouped_means.csv (grouped statistics)")
    print("- SIGMAPLOT_README.txt (instructions)")
    
    # Close plot
    plt.close('all')

# EOF