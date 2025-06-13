#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 07:10:00 (Claude)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/examples/scitex/io/basic_file_operations.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/io/basic_file_operations.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates loading various file formats with scitex.io.load
  - Shows saving data with automatic directory creation using scitex.io.save
  - Works with NumPy arrays, DataFrames, JSON, YAML, text files
  - Demonstrates compressed data storage and collections
  - Saves all outputs in the scitex-managed output directory

Dependencies:
  - scripts:
    - None
  - packages:
    - numpy
    - pandas
    - scitex
IO:
  - input-files:
    - None

  - output-files:
    - arrays/random_data.npy
    - dataframes/timeseries.csv
    - configs/experiment_config.json
    - configs/experiment_config.yaml
    - arrays/compressed_data.npz
    - reports/experiment_report.txt
    - reports/experiment_report.md
    - very/deep/nested/directory/structure/data.json
    - collections/all_dataframes.csv
"""

"""Imports"""
import argparse

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""


def main(args):
    """Demonstrate basic file I/O operations."""

    print("=== SciTeX I/O Examples ===\n")

    # 1. Working with NumPy arrays
    print("1. NumPy Arrays")
    arr = np.random.randn(100, 50)
    scitex.io.save(arr, "arrays/random_data.npy")
    print(f"   Created array shape: {arr.shape}")

    # 2. Working with DataFrames
    print("\n2. Pandas DataFrames")
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=100),
            "value": np.random.randn(100),
            "category": np.random.choice(["A", "B", "C"], 100),
        }
    )
    scitex.io.save(df, "dataframes/timeseries.csv", index=False)
    print(f"   Created DataFrame shape: {df.shape}")

    # 3. Working with dictionaries/JSON
    print("\n3. Dictionaries and JSON")
    config = {
        "experiment": {
            "name": "test_run",
            "seed": 42,
            "parameters": {"learning_rate": 0.001, "batch_size": 32},
        },
        "data": {"train_size": 0.8, "val_size": 0.1, "test_size": 0.1},
    }
    scitex.io.save(config, "configs/experiment_config.json")
    scitex.io.save(config, "configs/experiment_config.yaml")
    print(f"   Saved config with {len(config)} top-level keys")

    # 4. Working with compressed numpy arrays
    print("\n4. Compressed NumPy Arrays")
    data_dict = {
        "features": np.random.randn(1000, 128),
        "labels": np.random.randint(0, 10, 1000),
        "metadata": np.array(["sample_" + str(i) for i in range(1000)]),
    }
    scitex.io.save(data_dict, "arrays/compressed_data.npz")
    print(f"   Saved {len(data_dict)} arrays in compressed format")

    # 5. Working with text files
    print("\n5. Text Files")
    report = """Experiment Report
==================

Date: 2025-05-30
Model: SciTeX Example  
Results: Success

This is a sample report demonstrating text file handling.
"""
    scitex.io.save(report, "reports/experiment_report.txt")
    scitex.io.save(report, "reports/experiment_report.md")
    print(f"   Saved text report with {len(report.splitlines())} lines")

    # 6. Demonstrating automatic directory creation
    print("\n6. Automatic Directory Creation")
    nested_data = {"deep": {"nested": {"structure": "works"}}}
    scitex.io.save(nested_data, "very/deep/nested/directory/structure/data.json")
    print("   Created nested directory structure automatically")

    # 7. Working with lists of dataframes
    print("\n7. Lists and Collections")
    df_list = [
        pd.DataFrame({"x": np.random.randn(10), "y": np.random.randn(10)})
        for _ in range(5)
    ]
    # Save as concatenated CSV
    scitex.io.save(df_list, "collections/all_dataframes.csv")
    print(f"   Saved {len(df_list)} DataFrames as single CSV")

    # 8. Demonstrate loading files back
    print("\n8. Loading Files Back")
    # Get the actual output directory from scitex
    base_dir = CONFIG.SDIR if "CONFIG" in globals() else "./basic_file_operations_out"

    # List files created
    print(f"\n✅ All examples completed successfully!")
    print(f"📁 Files saved to scitex-managed output directory")
    print(f"   Output directory: {base_dir}")

    # Show directory structure
    print(f"\n📂 Directory structure created:")
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:5]:  # Show first 5 files
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... and {len(files)-5} more files")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(
        description="Basic file I/O operations with scitex.io"
    )
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, np, pd, scitex, os

    import sys
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
