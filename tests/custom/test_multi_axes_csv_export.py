#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import scitex
import scitex.plt as mplt

# Function to verify if the CSV was exported successfully
def check_csv_export(path):
    # Check if CSV was exported
    csv_path = path.replace(".png", ".csv")
    # Check in the expected directory (./png/)
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"\nCSV export found: {csv_path}")
        print(f"CSV columns: {df.columns.tolist()}")
        return True
    else:
        print(f"\nCSV export NOT found in expected location: {csv_path}")
        
        # Check in the output directory structure created by scitex.io.save
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "test_multi_axes_csv_export_out")
        alt_csv_path = os.path.join(output_dir, "csv", os.path.basename(csv_path))
        if os.path.exists(alt_csv_path):
            try:
                df = pd.read_csv(alt_csv_path)
                if not df.empty:
                    print(f"CSV export found in alternate location: {alt_csv_path}")
                    print(f"CSV columns: {df.columns.tolist()}")
                    return True
                else:
                    print(f"CSV file exists at {alt_csv_path} but is empty")
            except Exception as e:
                print(f"Error reading CSV at {alt_csv_path}: {e}")
        
        return False

# Create output directory
os.makedirs("./png", exist_ok=True)

print("Testing single axis case...")
# Create a figure with a single axis
fig1, ax1 = mplt.subplots(figsize=(8, 6))

# Generate and plot data
x = np.linspace(0, 10, 100)
ax1.plot(x, np.sin(x), id="single_sine")

# Save the figure
save_path1 = "./png/single_axis_test.png"
scitex.io.save(fig1, save_path1)

# Check if CSV was exported
single_axis_success = check_csv_export(save_path1)

print("\nTesting multiple axes case...")
# Create a figure with multiple axes (3 rows)
fig2, axes2 = mplt.subplots(nrows=3, figsize=(8, 10))

# Add debug output to understand the structure
print(f"Type of axes2: {type(axes2)}")
print(f"Shape of axes2: {axes2.shape if hasattr(axes2, 'shape') else 'N/A'}")
print(f"Has track attribute: {hasattr(axes2[0], 'track')}")
print(f"Has _ax_history: {hasattr(axes2[0], '_ax_history')}")

# Generate and plot different data on each axis
# Ensure tracking is explicitly enabled
for i, ax in enumerate(axes2):
    ax.track = True  # Explicitly enable tracking
    ax.plot(x, np.sin(x + i*np.pi/3), id=f"multi_sine_{i}")
    ax.set_title(f"Plot {i+1}")
    
    # Debug - check if history is being recorded
    if hasattr(ax, '_ax_history'):
        print(f"Axis {i} has {len(ax._ax_history)} tracked items")

# Save the figure
save_path2 = "./png/multi_axes_test.png"
scitex.io.save(fig2, save_path2)

# Check if CSV was exported
multi_axes_success = check_csv_export(save_path2)

print("\nTesting grid of axes case with the new implementation...")
# Create a figure with a grid of axes (2x2)
fig3, axes3 = mplt.subplots(nrows=2, ncols=2, figsize=(12, 10))

# Add debug output
print(f"Type of axes3: {type(axes3)}")
print(f"Shape of axes3: {axes3.shape if hasattr(axes3, 'shape') else 'N/A'}")
print(f"Has track attribute (0,0): {hasattr(axes3[0, 0], 'track')}")
print(f"Has _ax_history (0,0): {hasattr(axes3[0, 0], '_ax_history')}")

# Generate and plot different data on each axis
# We'll use different plotting functions to test various formatters

# Top left - sine wave
axes3[0, 0].track = True  # Explicitly enable tracking
axes3[0, 0].plot(x, np.sin(x), id="grid_sine")
axes3[0, 0].set_title("Sine Wave")
if hasattr(axes3[0, 0], '_ax_history'):
    print(f"Axis [0,0] has {len(axes3[0, 0]._ax_history)} tracked items")

# Top right - cosine wave with scatter points
axes3[0, 1].track = True  # Explicitly enable tracking
axes3[0, 1].plot(x, np.cos(x), id="grid_cosine")
axes3[0, 1].scatter(x[::10], np.cos(x[::10]), color='red', id="grid_cosine_points")
axes3[0, 1].set_title("Cosine Wave with Points")
if hasattr(axes3[0, 1], '_ax_history'):
    print(f"Axis [0,1] has {len(axes3[0, 1]._ax_history)} tracked items")

# Bottom left - histogram
axes3[1, 0].track = True  # Explicitly enable tracking
axes3[1, 0].hist(np.random.normal(0, 1, 1000), bins=30, id="grid_hist")
axes3[1, 0].set_title("Normal Distribution")
if hasattr(axes3[1, 0], '_ax_history'):
    print(f"Axis [1,0] has {len(axes3[1, 0]._ax_history)} tracked items")

# Bottom right - bar chart
axes3[1, 1].track = True  # Explicitly enable tracking
categories = ['A', 'B', 'C', 'D', 'E']
values = np.random.randint(1, 10, size=len(categories))
axes3[1, 1].bar(categories, values, id="grid_bars")
axes3[1, 1].set_title("Bar Chart")
if hasattr(axes3[1, 1], '_ax_history'):
    print(f"Axis [1,1] has {len(axes3[1, 1]._ax_history)} tracked items")

# Save the figure
save_path3 = "./png/grid_axes_test.png"
scitex.io.save(fig3, save_path3)

# Check if CSV was exported
grid_axes_success = check_csv_export(save_path3)

# Report summary of results
print("\nSummary:")
print(f"Single axis CSV export: {'Success' if single_axis_success else 'Failed'}")
print(f"Multiple axes CSV export: {'Success' if multi_axes_success else 'Failed'}")
print(f"Grid axes CSV export: {'Success' if grid_axes_success else 'Failed'}")

# Check actual output directory
print("\nFinding actual output files:")
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                         "test_multi_axes_csv_export_out")
if os.path.exists(output_dir):
    print(f"Output directory: {output_dir}")
    print("Files in output directory:")
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"- {file_path}")
    
    # Check content of CSV files
    csv_files = [os.path.join(root, file) for root, _, files in os.walk(output_dir) 
                for file in files if file.endswith('.csv')]
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            print(f"\nContents of {csv_file}:")
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
else:
    print(f"Output directory does not exist: {output_dir}")