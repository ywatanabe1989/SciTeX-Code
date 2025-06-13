#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:32:00"
# File: /examples/sns_lineplot_with_separate_legend.py
# ----------------------------------------
"""
Example of using sns_lineplot with SciTeX and saving legend separately.

This demonstrates:
1. Using the new sns_lineplot method
2. Creating plots with multiple lines using hue
3. Extracting and saving legends separately
4. Different legend placement options
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scitex.plt as mplt


def create_sample_data():
    """Create sample time series data for demonstration."""
    np.random.seed(42)
    
    # Create time series data with multiple conditions
    time_points = np.arange(0, 100)
    conditions = ['Control', 'Treatment A', 'Treatment B']
    subjects = ['S1', 'S2', 'S3', 'S4', 'S5']
    
    data_list = []
    for condition in conditions:
        for subject in subjects:
            # Generate data with condition-specific trends
            if condition == 'Control':
                trend = 0.05
                noise_level = 2
            elif condition == 'Treatment A':
                trend = 0.1
                noise_level = 2.5
            else:  # Treatment B
                trend = -0.02
                noise_level = 3
            
            values = 10 + trend * time_points + np.random.normal(0, noise_level, len(time_points))
            
            for t, val in zip(time_points, values):
                data_list.append({
                    'Time': t,
                    'Value': val,
                    'Condition': condition,
                    'Subject': subject
                })
    
    df = pd.DataFrame(data_list)
    return df


def example_basic_sns_lineplot():
    """Basic example of sns_lineplot with separate legend."""
    # Create data
    df = create_sample_data()
    
    # Create SciTeX figure
    fig, ax = mplt.subplots(figsize=(10, 6))
    
    # Use sns_lineplot to plot with confidence intervals
    ax.sns_lineplot(
        data=df,
        x='Time',
        y='Value',
        hue='Condition',
        errorbar='ci',
        linewidth=2.5,
        palette='Set2'
    )
    
    # Customize plot
    ax.set_xlabel('Time (minutes)', fontsize=12)
    ax.set_ylabel('Measurement Value', fontsize=12)
    ax.set_title('Time Series Analysis with Confidence Intervals', fontsize=14)
    
    # Get the legend from the matplotlib axis
    legend = ax._axis_mpl.get_legend()
    
    # Save the complete plot
    fig.save('sns_lineplot_with_legend.png')
    
    # Extract and save legend separately
    if legend:
        # Method 1: Create new figure for legend
        fig_legend = plt.figure(figsize=(3, 2))
        handles = legend.legendHandles
        labels = [t.get_text() for t in legend.get_texts()]
        fig_legend.legend(handles, labels, loc='center', title='Condition',
                         frameon=True, fancybox=True, shadow=True)
        fig_legend.savefig('sns_lineplot_legend_only.png', dpi=150, bbox_inches='tight')
        plt.close(fig_legend)
        
        # Remove legend from original plot
        legend.remove()
    
    # Save plot without legend
    fig.save('sns_lineplot_without_legend.png')
    
    plt.close('all')


def example_multiple_variables():
    """Example with multiple variables using sns_lineplot."""
    # Create more complex data
    np.random.seed(42)
    
    # Simulate sensor data
    time = np.linspace(0, 10, 200)
    data_list = []
    
    sensors = ['Sensor A', 'Sensor B', 'Sensor C']
    locations = ['Location 1', 'Location 2']
    
    for sensor in sensors:
        for location in locations:
            # Different patterns for each sensor/location combination
            if sensor == 'Sensor A':
                base_signal = np.sin(2 * np.pi * time)
            elif sensor == 'Sensor B':
                base_signal = np.cos(2 * np.pi * time) * 0.8
            else:
                base_signal = np.sin(2 * np.pi * time) * np.exp(-time/5)
            
            # Location affects amplitude
            if location == 'Location 1':
                signal = base_signal * 1.2 + np.random.normal(0, 0.1, len(time))
            else:
                signal = base_signal * 0.8 + np.random.normal(0, 0.15, len(time))
            
            for t, val in zip(time, signal):
                data_list.append({
                    'Time': t,
                    'Signal': val,
                    'Sensor': sensor,
                    'Location': location
                })
    
    df = pd.DataFrame(data_list)
    
    # Create figure with subplots
    fig, axes = mplt.subplots(nrows=2, ncols=1, figsize=(12, 10), sharex=True)
    
    # Plot 1: All sensors at Location 1
    location1_data = df[df['Location'] == 'Location 1']
    axes[0].sns_lineplot(
        data=location1_data,
        x='Time',
        y='Signal',
        hue='Sensor',
        linewidth=2,
        palette='viridis'
    )
    axes[0].set_title('Sensor Readings at Location 1')
    axes[0].set_ylabel('Signal Amplitude')
    
    # Plot 2: All sensors at Location 2
    location2_data = df[df['Location'] == 'Location 2']
    axes[1].sns_lineplot(
        data=location2_data,
        x='Time',
        y='Signal',
        hue='Sensor',
        linewidth=2,
        palette='viridis'
    )
    axes[1].set_title('Sensor Readings at Location 2')
    axes[1].set_xlabel('Time (seconds)')
    axes[1].set_ylabel('Signal Amplitude')
    
    # Save full figure
    fig.save('sns_lineplot_multiple_panels.png')
    
    # Extract legends and create a combined legend figure
    fig_legend = plt.figure(figsize=(4, 2))
    
    # Get handles and labels from first subplot (same for both)
    handles, labels = axes[0]._axis_mpl.get_legend_handles_labels()
    
    # Create horizontal legend
    legend = fig_legend.legend(handles, labels, 
                              loc='center', 
                              ncol=3,
                              title='Sensors',
                              frameon=True,
                              fancybox=True,
                              shadow=True)
    
    fig_legend.savefig('sns_lineplot_combined_legend.png', dpi=150, bbox_inches='tight')
    
    # Remove legends from subplots
    for ax in axes:
        if ax._axis_mpl.get_legend():
            ax._axis_mpl.get_legend().remove()
    
    # Save plots without legends
    fig.save('sns_lineplot_multiple_panels_no_legend.png')
    
    plt.close('all')


def example_sns_lineplot_with_style():
    """Example using both hue and style parameters."""
    # Create data with two grouping variables
    np.random.seed(42)
    
    conditions = ['Healthy', 'Disease']
    treatments = ['Placebo', 'Drug A', 'Drug B']
    time_points = np.arange(0, 24, 2)  # 0 to 24 hours, every 2 hours
    
    data_list = []
    for condition in conditions:
        for treatment in treatments:
            for replicate in range(5):  # 5 replicates per group
                # Generate response curves
                if condition == 'Healthy':
                    if treatment == 'Placebo':
                        response = 100 + np.random.normal(0, 5, len(time_points))
                    elif treatment == 'Drug A':
                        response = 100 - 2 * time_points + np.random.normal(0, 6, len(time_points))
                    else:  # Drug B
                        response = 100 - 1.5 * time_points + np.random.normal(0, 5, len(time_points))
                else:  # Disease
                    if treatment == 'Placebo':
                        response = 80 + np.random.normal(0, 8, len(time_points))
                    elif treatment == 'Drug A':
                        response = 80 + 1.5 * time_points + np.random.normal(0, 7, len(time_points))
                    else:  # Drug B
                        response = 80 + 0.5 * time_points + np.random.normal(0, 6, len(time_points))
                
                for t, val in zip(time_points, response):
                    data_list.append({
                        'Time': t,
                        'Response': val,
                        'Condition': condition,
                        'Treatment': treatment,
                        'Replicate': f'R{replicate}'
                    })
    
    df = pd.DataFrame(data_list)
    
    # Create figure
    fig, ax = mplt.subplots(figsize=(12, 8))
    
    # Use sns_lineplot with both hue and style
    ax.sns_lineplot(
        data=df,
        x='Time',
        y='Response',
        hue='Treatment',
        style='Condition',
        markers=True,
        dashes=True,
        linewidth=2.5,
        markersize=8,
        errorbar='se',  # Standard error
        palette='deep'
    )
    
    # Customize plot
    ax.set_xlabel('Time (hours)', fontsize=14)
    ax.set_ylabel('Response Level', fontsize=14)
    ax.set_title('Treatment Response Over Time by Condition', fontsize=16)
    ax.grid(True, alpha=0.3)
    
    # Save with legend
    fig.save('sns_lineplot_hue_style_with_legend.png')
    
    # Create custom legend figure with better organization
    fig_legend = plt.figure(figsize=(6, 3))
    
    # Get the current legend
    legend = ax._axis_mpl.get_legend()
    
    if legend:
        # Extract all handles and labels
        handles = legend.legendHandles
        labels = [t.get_text() for t in legend.get_texts()]
        
        # Create organized legend with two columns
        # First column for treatments, second for conditions
        fig_legend.legend(handles[:len(treatments)], labels[:len(treatments)], 
                         loc='upper left', 
                         bbox_to_anchor=(0.1, 0.9),
                         title='Treatment',
                         frameon=True)
        
        fig_legend.legend(handles[len(treatments):], labels[len(treatments):], 
                         loc='upper right',
                         bbox_to_anchor=(0.9, 0.9),
                         title='Condition',
                         frameon=True)
        
        fig_legend.suptitle('Legend', fontsize=14, y=0.98)
        fig_legend.savefig('sns_lineplot_organized_legend.png', dpi=150, bbox_inches='tight')
        
        # Remove legend from main plot
        legend.remove()
    
    # Save without legend
    fig.save('sns_lineplot_hue_style_no_legend.png')
    
    plt.close('all')


if __name__ == "__main__":
    print("Demonstrating sns_lineplot with separate legend saving...")
    
    # Set style for all plots
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.2)
    
    print("1. Basic sns_lineplot with confidence intervals")
    example_basic_sns_lineplot()
    
    print("2. Multiple variables with panel plots")
    example_multiple_variables()
    
    print("3. Using hue and style parameters")
    example_sns_lineplot_with_style()
    
    print("\nCompleted! Check the generated PNG files.")
    print("\nKey features demonstrated:")
    print("- sns_lineplot with error bars (CI, SE)")
    print("- Multiple grouping variables (hue, style)")
    print("- Saving legends separately")
    print("- Creating organized multi-column legends")

# EOF