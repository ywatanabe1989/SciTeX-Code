#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 18:45:00 (ywatanabe)"
# File: ./examples/io/basic_io_operations.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/io/basic_io_operations.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic scitex.io operations
  - Shows saving and loading various data formats
  - Demonstrates automatic directory creation
  - Saves outputs to examples/io/basic_io_operations_out

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex
    - numpy
    - pandas
IO:
  - input-files:
    - None (generates data programmatically)

  - output-files:
    - ./examples/io/basic_io_operations_out/data.npy
    - ./examples/io/basic_io_operations_out/data.pkl
    - ./examples/io/basic_io_operations_out/data.csv
    - ./examples/io/basic_io_operations_out/data.json
    - ./examples/io/basic_io_operations_out/logs/*
"""

"""Imports"""
import numpy as np
import pandas as pd
import scitex

"""Parameters"""
# scitex automatically creates output directory based on script name

"""Functions"""
def demonstrate_basic_io():
    """Demonstrate basic I/O operations with scitex."""
    # Start logging
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(__FILE__, sys_=True, plt_=True)
    
    print("SciTeX I/O Basic Operations Demo")
    print("=" * 50)
    
    # 1. NumPy arrays
    print("\n1. NumPy Array I/O")
    arr = np.random.randn(100, 50)
    scitex.io.save(arr, "data.npy")
    loaded_arr = scitex.io.load("data.npy")
    print(f"  ✓ Saved and loaded NumPy array: shape={loaded_arr.shape}")
    
    # 2. Pandas DataFrames
    print("\n2. Pandas DataFrame I/O")
    df = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.choice(['X', 'Y', 'Z'], 100),
        'C': np.arange(100)
    })
    
    # Save as CSV
    scitex.io.save(df, "data.csv")
    loaded_csv = scitex.io.load("data.csv")
    print(f"  ✓ CSV: shape={loaded_csv.shape}, columns={list(loaded_csv.columns)}")
    
    # Save as pickle
    scitex.io.save(df, "data.pkl")
    loaded_pkl = scitex.io.load("data.pkl")
    print(f"  ✓ Pickle: shape={loaded_pkl.shape}")
    
    # 3. Dictionaries and JSON
    print("\n3. Dictionary/JSON I/O")
    data_dict = {
        'experiment': 'demo',
        'parameters': {'lr': 0.01, 'epochs': 100},
        'results': [0.8, 0.85, 0.9]
    }
    scitex.io.save(data_dict, "data.json")
    loaded_json = scitex.io.load("data.json")
    print(f"  ✓ JSON: keys={list(loaded_json.keys())}")
    
    # 4. Compressed formats
    print("\n4. Compressed Formats")
    # Multiple arrays in npz
    arrays = {
        'train': np.random.randn(1000, 10),
        'test': np.random.randn(200, 10),
        'labels': np.random.randint(0, 2, 1000)
    }
    scitex.io.save(arrays, "data.npz")
    loaded_npz = scitex.io.load("data.npz")
    print(f"  ✓ NPZ: arrays={list(loaded_npz.keys())}")
    
    # 5. Automatic path handling
    print("\n5. Automatic Path Handling")
    # Save to nested directory (auto-created)
    scitex.io.save(arr, "nested/dir/data.npy")
    print("  ✓ Saved to nested directory (auto-created)")
    
    # Use CONFIG.SDIR for output directory
    full_path = os.path.join(CONFIG.SDIR, "data_with_full_path.npy")
    scitex.io.save(arr, full_path)
    print(f"  ✓ Saved with full path: {full_path}")
    
    # Close and finalize
    scitex.gen.close(CONFIG)
    print("\n✅ Demo completed successfully!")
    print(f"📁 Outputs saved to: {CONFIG.SDIR}")

"""Main"""
if __name__ == "__main__":
    demonstrate_basic_io()

"""EOF"""