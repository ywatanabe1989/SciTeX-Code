#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Example: Legend positioning and CSV export improvements in SciTeX
# Timestamp: "2025-06-09 21:57:00 (ywatanabe)"

"""
This example demonstrates the improved legend positioning options and
enhanced CSV export functionality for seaborn plots in SciTeX.

Key Features:
1. ax.legend("separate") - Save legend as a separate image file
2. ax.legend("outer") - Position legend outside the plot area
3. Automatic meaningful column names in CSV export for seaborn plots
"""

import pandas as pd
import numpy as np
import scitex

# Create sample data
np.random.seed(42)
n_points = 50
time = np.linspace(0, 10, n_points)
groups = ['Control', 'Treatment A', 'Treatment B']

# Generate time series data for each group
data_list = []
for i, group in enumerate(groups):
    values = np.sin(time + i * np.pi/3) + np.random.normal(0, 0.1, n_points) + i * 2
    df_group = pd.DataFrame({
        'time': time,
        'measurement': values,
        'group': group
    })
    data_list.append(df_group)

data = pd.concat(data_list, ignore_index=True)

# Example 1: Seaborn lineplot with separate legend
print("Example 1: Seaborn lineplot with separate legend file")
fig1, ax1 = scitex.plt.subplots(figsize=(8, 6))
ax1.sns_lineplot(
    data=data, 
    x='time', 
    y='measurement', 
    hue='group',
    style='group',
    markers=True,
    dashes=False
)
ax1.set_xyt('Time (s)', 'Measurement Value', 'Treatment Comparison')

# Save legend as a separate file
ax1.legend('separate', filename='treatment_comparison_legend.png')

# Export data with meaningful column names
df_export = ax1.export_as_csv()
print("\nExported column names:")
for col in df_export.columns[:6]:  # Show first 6 columns
    print(f"  - {col}")
print("  ...")

scitex.io.save(df_export, 'seaborn_lineplot_data.csv')
scitex.io.save(fig1, 'treatment_comparison.png')

# Example 2: Multiple plot types with outer legend
print("\n\nExample 2: Multiple plot types with outer legend")
fig2, ax2 = scitex.plt.subplots(figsize=(8, 6))

# Add different plot types
x = np.linspace(0, 10, 100)
ax2.plot(x, np.sin(x), label='Sine wave', linewidth=2)
ax2.plot(x, np.cos(x), label='Cosine wave', linewidth=2)
ax2.scatter(x[::10], np.sin(x[::10]), label='Sample points', s=50, alpha=0.7)
ax2.fill_between(x, np.sin(x) - 0.2, np.sin(x) + 0.2, alpha=0.3, label='Confidence band')

ax2.set_xyt('X', 'Y', 'Trigonometric Functions')

# Place legend outside the plot area
ax2.legend('outer')

scitex.io.save(fig2, 'trig_functions_outer_legend.png')

# Example 3: Seaborn boxplot with meaningful CSV export
print("\n\nExample 3: Seaborn boxplot with CSV export")
fig3, ax3 = scitex.plt.subplots(figsize=(8, 6))

# Create categorical data
categories = ['Low', 'Medium', 'High']
box_data = pd.DataFrame({
    'category': np.repeat(categories, 100),
    'value': np.concatenate([
        np.random.normal(5, 1, 100),   # Low
        np.random.normal(10, 2, 100),  # Medium
        np.random.normal(15, 1.5, 100) # High
    ]),
    'condition': np.tile(['A', 'B'] * 50, 3)
})

ax3.sns_boxplot(data=box_data, x='category', y='value', hue='condition')
ax3.set_xyt('Category', 'Value', 'Distribution by Category and Condition')

# Export will have columns like: 0_sns_boxplot_value_condition_A, etc.
df_box_export = ax3.export_as_csv()
scitex.io.save(df_box_export, 'boxplot_data.csv')
scitex.io.save(fig3, 'boxplot_comparison.png')

# Example 4: Combined legend options
print("\n\nExample 4: Legend position variations")
positions = ['upper right out', 'lower left out', 'center right out']
fig4, axes4 = scitex.plt.subplots(1, 3, figsize=(15, 4))

for ax, pos in zip(axes4, positions):
    x = np.linspace(0, 2*np.pi, 100)
    ax.plot(x, np.sin(x), label='sin(x)')
    ax.plot(x, np.cos(x), label='cos(x)')
    ax.plot(x, np.sin(2*x), label='sin(2x)')
    ax.set_title(f"Legend: '{pos}'")
    ax.legend(pos)

scitex.io.save(fig4, 'legend_position_examples.png')

print("\n\nAll examples completed!")
print("\nGenerated files:")
print("  - treatment_comparison.png (main plot)")
print("  - treatment_comparison_legend.png (separate legend)")
print("  - seaborn_lineplot_data.csv (with meaningful column names)")
print("  - trig_functions_outer_legend.png (with outer legend)")
print("  - boxplot_comparison.png")
print("  - boxplot_data.csv")
print("  - legend_position_examples.png")

# Summary of improvements
print("\n=== Summary of Improvements ===")
print("1. Legend 'separate' option:")
print("   - Saves legend as a standalone image file")
print("   - Useful for presentations and publications")
print("   - Customizable filename and DPI")
print("")
print("2. Legend 'outer' option:")
print("   - Automatically positions legend outside plot area")
print("   - Adjusts figure layout to prevent overlap")
print("   - Multiple position variants available")
print("")
print("3. Enhanced CSV export for seaborn:")
print("   - Column names include variable names from x, y, hue")
print("   - Format: {id}_{method}_{variable}_{hue}_{value}")
print("   - Makes data analysis and reimporting easier")