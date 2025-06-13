#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 18:22:00 (ywatanabe)"
# File: ./examples/scitex_io_example.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scitex_io_example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates scitex.io module capabilities
  - Shows file I/O operations for various formats
  - Demonstrates CSV caching functionality
  - Saves outputs to examples_output directory

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex
    - numpy
    - pandas
    - matplotlib
IO:
  - input-files:
    - None (generates data programmatically)

  - output-files:
    - ./examples_output/io_demo/sample_data.csv
    - ./examples_output/io_demo/sample_data.npy
    - ./examples_output/io_demo/sample_data.pkl
    - ./examples_output/io_demo/sample_data.json
    - ./examples_output/io_demo/sample_plot.png
    - ./examples_output/io_demo/performance_results.txt
"""

"""Imports"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex

"""Parameters"""
OUTPUT_DIR = "./examples_output/io_demo"
scitex.io.makedirs(OUTPUT_DIR, exist_ok=True)

"""Main Script"""
def main():
    print("SciTeX I/O Module Demonstration")
    print("=" * 50)
    
    # 1. Basic Data I/O
    print("\n1. Basic Data I/O Operations")
    print("-" * 30)
    
    # Create sample data
    data_dict = {
        'x': np.arange(100),
        'y': np.sin(np.arange(100) * 0.1),
        'z': np.random.randn(100)
    }
    df = pd.DataFrame(data_dict)
    
    # Save in various formats
    formats = {
        'csv': f"{OUTPUT_DIR}/sample_data.csv",
        'npy': f"{OUTPUT_DIR}/sample_data.npy",
        'pkl': f"{OUTPUT_DIR}/sample_data.pkl",
        'json': f"{OUTPUT_DIR}/sample_data.json",
        'xlsx': f"{OUTPUT_DIR}/sample_data.xlsx"
    }
    
    for fmt, path in formats.items():
        if fmt == 'npy':
            scitex.io.save(df.values, path)
        else:
            scitex.io.save(df, path)
        print(f"  ✓ Saved as {fmt}: {os.path.basename(path)}")
    
    # Load and verify
    print("\n  Loading and verifying:")
    for fmt, path in formats.items():
        loaded = scitex.io.load(path)
        if fmt == 'npy':
            print(f"  ✓ Loaded {fmt}: shape={loaded.shape}")
        elif fmt in ['csv', 'xlsx']:
            print(f"  ✓ Loaded {fmt}: shape={loaded.shape}, columns={list(loaded.columns)}")
        else:
            print(f"  ✓ Loaded {fmt}: type={type(loaded).__name__}")
    
    # 2. CSV Caching Demonstration
    print("\n\n2. CSV Caching Performance")
    print("-" * 30)
    
    # Create a larger dataset for performance testing
    large_df = pd.DataFrame({
        f'col_{i}': np.random.randn(1000) 
        for i in range(10)
    })
    csv_path = f"{OUTPUT_DIR}/cached_data.csv"
    
    # First save (no cache)
    start = time.perf_counter()
    scitex.io.save(large_df, csv_path, index=False)
    first_time = time.perf_counter() - start
    print(f"  First save: {first_time:.4f} seconds")
    
    # Second save (with cache - should skip)
    start = time.perf_counter()
    scitex.io.save(large_df, csv_path, index=False)
    second_time = time.perf_counter() - start
    print(f"  Second save (cached): {second_time:.4f} seconds")
    print(f"  Speedup: {first_time/second_time:.1f}x")
    
    # Modify data and save (should update)
    large_df.iloc[0, 0] = 999
    start = time.perf_counter()
    scitex.io.save(large_df, csv_path, index=False)
    third_time = time.perf_counter() - start
    print(f"  Third save (modified): {third_time:.4f} seconds")
    
    # 3. Image I/O
    print("\n\n3. Image I/O Operations")
    print("-" * 30)
    
    # Create a simple plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(data_dict['x'], data_dict['y'], 'b-', label='sin(x)')
    ax.scatter(data_dict['x'][::10], data_dict['z'][::10], 
               c='red', alpha=0.5, label='random')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('SciTeX I/O Example Plot')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Save plot
    img_path = f"{OUTPUT_DIR}/sample_plot.png"
    scitex.io.save(fig, img_path)
    print(f"  ✓ Saved plot: {os.path.basename(img_path)}")
    plt.close(fig)
    
    # 4. Advanced Features
    print("\n\n4. Advanced I/O Features")
    print("-" * 30)
    
    # Compressed formats
    compressed_data = {
        'array1': np.random.randn(100, 50),
        'array2': np.random.randn(50, 100),
        'metadata': {'created': '2025-06-07', 'version': '1.0'}
    }
    
    # Save compressed numpy
    npz_path = f"{OUTPUT_DIR}/compressed_data.npz"
    scitex.io.save(compressed_data, npz_path)
    print(f"  ✓ Saved compressed: {os.path.basename(npz_path)}")
    
    # Load and verify
    loaded_npz = scitex.io.load(npz_path)
    print(f"  ✓ Loaded arrays: {list(loaded_npz.keys())}")
    
    # Save nested structure as JSON
    nested_data = {
        'experiment': {
            'name': 'SciTeX Demo',
            'parameters': {'learning_rate': 0.01, 'epochs': 100},
            'results': {'accuracy': 0.95, 'loss': 0.05}
        }
    }
    json_path = f"{OUTPUT_DIR}/nested_data.json"
    scitex.io.save(nested_data, json_path)
    print(f"  ✓ Saved nested JSON: {os.path.basename(json_path)}")
    
    # 5. Performance Summary
    print("\n\n5. Performance Summary")
    print("-" * 30)
    
    summary = f"""CSV Caching Performance Results:
    - First save: {first_time:.4f}s
    - Cached save: {second_time:.4f}s (speedup: {first_time/second_time:.1f}x)
    - Modified save: {third_time:.4f}s
    
Note: CSV caching automatically detects identical content and skips rewriting,
providing significant performance improvements for repeated saves."""
    
    summary_path = f"{OUTPUT_DIR}/performance_results.txt"
    scitex.io.save(summary, summary_path)
    print(summary)
    
    print(f"\n✅ All outputs saved to: {OUTPUT_DIR}")
    print("Example completed successfully!")

if __name__ == "__main__":
    main()

"""EOF"""