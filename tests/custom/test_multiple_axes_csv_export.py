#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 20:30:00"
# File: test_multiple_axes_csv_export.py

"""
Test script to demonstrate the issue with export_as_csv for multiple axes.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex.plt as mplt
import scitex.io

# Create output directory if it doesn't exist
output_dir = "./test_multiple_axes_export_out"
os.makedirs(output_dir, exist_ok=True)

# Case 1: Single axis case (should work fine)
print("Testing single axis case...")
fig, ax = mplt.subplots(figsize=(8, 6))
ax.plot(np.arange(5), np.random.rand(5), id="line1")
ax.scatter(np.arange(5), np.random.rand(5), id="scatter1")
ax.bar(np.arange(3), np.random.rand(3), id="bar1")

# Save figure and CSV
scitex.io.save(fig, f"{output_dir}/single_axis.png")
csv_df = fig.export_as_csv()
print(f"Single axis CSV shape: {csv_df.shape}")
print(f"Single axis CSV columns: {csv_df.columns.tolist()}")
csv_df.to_csv(f"{output_dir}/single_axis.csv", index=False)

# Case 2: Multiple axes in grid (2x2)
print("\nTesting multiple axes case (2x2 grid)...")
fig, axes = mplt.subplots(2, 2, figsize=(12, 10))

# Plot different things on each axis
axes[0, 0].plot(np.arange(5), np.random.rand(5), id="line_00")
axes[0, 1].scatter(np.arange(5), np.random.rand(5), id="scatter_01")
axes[1, 0].bar(np.arange(3), np.random.rand(3), id="bar_10")
axes[1, 1].hist(np.random.randn(100), bins=10, id="hist_11")

# Save figure and CSV
scitex.io.save(fig, f"{output_dir}/multiple_axes_grid.png")
csv_df = fig.export_as_csv()
print(f"Multiple axes CSV shape: {csv_df.shape}")
if not csv_df.empty:
    print(f"Multiple axes CSV columns: {csv_df.columns.tolist()}")
    csv_df.to_csv(f"{output_dir}/multiple_axes_grid.csv", index=False)
else:
    print("Multiple axes CSV is empty!")

# Case 3: Different types of plots in a 1x3 grid
print("\nTesting different plot types in 1x3 grid...")
fig, axes = mplt.subplots(1, 3, figsize=(15, 5))

# Different data lengths to test handling variable sized arrays
axes[0].plot(np.arange(5), np.sin(np.arange(5)), id="sin_plot")
axes[1].bar(['A', 'B', 'C', 'D'], np.random.rand(4), id="categories")
axes[2].boxplot([np.random.randn(10), np.random.randn(15), np.random.randn(20)], id="boxplots")

# Save figure and CSV
scitex.io.save(fig, f"{output_dir}/three_different_plots.png")
csv_df = fig.export_as_csv()
print(f"Different plots CSV shape: {csv_df.shape}")
if not csv_df.empty:
    print(f"Different plots CSV columns: {csv_df.columns.tolist()}")
    csv_df.to_csv(f"{output_dir}/three_different_plots.csv", index=False)
else:
    print("Different plots CSV is empty!")

print("\nDone! Check the output in:", output_dir)