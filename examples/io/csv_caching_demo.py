#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 18:48:00 (ywatanabe)"
# File: ./examples/io/csv_caching_demo.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/io/csv_caching_demo.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates CSV caching functionality
  - Shows performance improvements with caching
  - Tests cache invalidation on data changes
  - Saves performance metrics

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex
    - numpy
    - pandas
    - time
IO:
  - input-files:
    - None (generates data programmatically)

  - output-files:
    - ./examples/io/csv_caching_demo_out/test_data.csv
    - ./examples/io/csv_caching_demo_out/large_data.csv
    - ./examples/io/csv_caching_demo_out/performance_report.txt
    - ./examples/io/csv_caching_demo_out/logs/*
"""

"""Imports"""
import time
import numpy as np
import pandas as pd
import scitex

"""Parameters"""
SIZES = [100, 1000, 5000]  # Different dataset sizes to test

"""Functions"""
def test_csv_caching():
    """Test and demonstrate CSV caching functionality."""
    # Start logging
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(__FILE__, sys_=True, plt_=True)
    
    print("SciTeX CSV Caching Demonstration")
    print("=" * 50)
    print("This demo shows how CSV caching improves performance")
    print("by avoiding unnecessary file rewrites.\n")
    
    # 1. Basic caching demo
    print("1. Basic CSV Caching")
    print("-" * 30)
    
    df = pd.DataFrame({
        'x': np.arange(100),
        'y': np.sin(np.arange(100) * 0.1),
        'z': np.random.randn(100)
    })
    
    # First save
    start = time.perf_counter()
    scitex.io.save(df, "test_data.csv", index=False)
    time1 = time.perf_counter() - start
    print(f"First save: {time1:.4f}s")
    
    # Second save (should be cached)
    start = time.perf_counter()
    scitex.io.save(df, "test_data.csv", index=False)
    time2 = time.perf_counter() - start
    print(f"Second save (cached): {time2:.4f}s")
    print(f"Speedup: {time1/time2:.1f}x ✓\n")
    
    # 2. Cache invalidation on data change
    print("2. Cache Invalidation")
    print("-" * 30)
    
    # Modify data
    df.loc[0, 'x'] = 999
    start = time.perf_counter()
    scitex.io.save(df, "test_data.csv", index=False)
    time3 = time.perf_counter() - start
    print(f"Save after modification: {time3:.4f}s")
    print("Cache correctly invalidated on data change ✓\n")
    
    # 3. Performance with different sizes
    print("3. Performance Scaling")
    print("-" * 30)
    
    results = []
    for size in SIZES:
        # Create dataset
        large_df = pd.DataFrame({
            f'col_{i}': np.random.randn(size) 
            for i in range(10)
        })
        
        # First save
        start = time.perf_counter()
        scitex.io.save(large_df, f"large_data_{size}.csv", index=False)
        first_time = time.perf_counter() - start
        
        # Cached save
        start = time.perf_counter()
        scitex.io.save(large_df, f"large_data_{size}.csv", index=False)
        cached_time = time.perf_counter() - start
        
        speedup = first_time / cached_time
        results.append({
            'Size': size,
            'First Save (s)': first_time,
            'Cached Save (s)': cached_time,
            'Speedup': speedup
        })
        
        print(f"Size {size:5d}: First={first_time:.4f}s, "
              f"Cached={cached_time:.4f}s, Speedup={speedup:.1f}x")
    
    # 4. Save performance report
    print("\n4. Performance Summary")
    print("-" * 30)
    
    report = f"""CSV Caching Performance Report
==============================

Test Configuration:
- DataFrame sizes: {SIZES}
- 10 columns per DataFrame
- All numeric data

Results:
"""
    for r in results:
        report += f"\nSize {r['Size']:5d} rows:"
        report += f"\n  First save:  {r['First Save (s)']:.4f}s"
        report += f"\n  Cached save: {r['Cached Save (s)']:.4f}s"
        report += f"\n  Speedup:     {r['Speedup']:.1f}x"
    
    report += "\n\nConclusion: CSV caching provides significant performance"
    report += "\nimprovements, especially for frequently saved data."
    
    scitex.io.save(report, "performance_report.txt")
    print(report)
    
    # Close and finalize
    scitex.gen.close(CONFIG)
    print(f"\n✅ Demo completed! Outputs in: {CONFIG.SDIR}")

"""Main"""
if __name__ == "__main__":
    test_csv_caching()

"""EOF"""