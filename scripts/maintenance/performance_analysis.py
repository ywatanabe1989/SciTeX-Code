#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 04:15:00"
# File: performance_analysis.py

"""
Performance analysis script for SciTeX codebase.
Identifies slow functions and performance bottlenecks.
"""

import sys
import os
import time
import cProfile
import pstats
import io
from pathlib import Path
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import various scitex modules
import scitex as stx


def profile_io_operations():
    """Profile I/O operations."""
    print("\n=== Profiling I/O Operations ===")
    
    # Create test data
    data = np.random.randn(1000, 100)
    df = pd.DataFrame(data, columns=[f'col_{i}' for i in range(100)])
    
    # Profile save operations
    pr = cProfile.Profile()
    pr.enable()
    
    # Test various save formats
    test_dir = Path('.dev/perf_test')
    test_dir.mkdir(exist_ok=True)
    
    stx.io.save(data, test_dir / 'test_data.npy')
    stx.io.save(df, test_dir / 'test_data.csv')
    stx.io.save(df, test_dir / 'test_data.pkl')
    stx.io.save({'data': data.tolist()}, test_dir / 'test_data.json')  # Convert to list for JSON
    
    pr.disable()
    
    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())
    
    # Profile load operations
    pr = cProfile.Profile()
    pr.enable()
    
    # Test various load formats
    _ = stx.io.load(test_dir / 'test_data.npy')
    _ = stx.io.load(test_dir / 'test_data.csv')
    _ = stx.io.load(test_dir / 'test_data.pkl')
    _ = stx.io.load(test_dir / 'test_data.json')
    
    pr.disable()
    
    print("\n=== Load Operations ===")
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())


def profile_gen_operations():
    """Profile gen module operations."""
    print("\n=== Profiling Gen Operations ===")
    
    # Create test data
    data = np.random.randn(10000, 50)
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Test normalization operations
    for _ in range(100):
        _ = stx.gen.to_z(data)
        _ = stx.gen.to_01(data)
        _ = stx.gen.to_even(5)
        _ = stx.gen.to_odd(6)
    
    # Test timestamp operations
    for _ in range(1000):
        _ = stx.gen.timestamp()
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())


def profile_stats_operations():
    """Profile stats module operations."""
    print("\n=== Profiling Stats Operations ===")
    
    # Create test data
    x = np.random.randn(1000)
    y = np.random.randn(1000)
    groups = np.random.randint(0, 3, 1000)
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Test various statistical operations
    for _ in range(50):
        _ = stx.stats.describe(x)
        _ = stx.stats.corr_test(x, y)
        _ = stx.stats.brunner_munzel_test(x[:500], x[500:])
        _ = stx.stats.multicompair(x, groups)
    
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())


def identify_slow_imports():
    """Identify slow module imports."""
    print("\n=== Analyzing Import Times ===")
    
    modules_to_test = [
        'scitex.io',
        'scitex.gen',
        'scitex.plt',
        'scitex.stats',
        'scitex.pd',
        'scitex.ai',
        'scitex.dsp',
        'scitex.path',
    ]
    
    import_times = {}
    
    for module in modules_to_test:
        # Remove from sys.modules if already imported
        if module in sys.modules:
            del sys.modules[module]
        
        start = time.time()
        try:
            __import__(module)
            import_time = time.time() - start
            import_times[module] = import_time
            print(f"{module}: {import_time:.3f}s")
        except ImportError as e:
            print(f"{module}: Failed to import - {e}")
    
    # Sort by import time
    sorted_times = sorted(import_times.items(), key=lambda x: x[1], reverse=True)
    print("\nSlowest imports:")
    for module, import_time in sorted_times[:5]:
        print(f"  {module}: {import_time:.3f}s")


def analyze_memory_usage():
    """Analyze memory usage of common operations."""
    print("\n=== Analyzing Memory Usage ===")
    
    import tracemalloc
    
    # Test data sizes
    sizes = [100, 1000, 10000]
    
    for size in sizes:
        print(f"\nData size: {size}x{size}")
        
        # Start tracing
        tracemalloc.start()
        
        # Create data
        data = np.random.randn(size, size)
        
        # Perform operations
        normalized = stx.gen.to_z(data)
        df = pd.DataFrame(normalized)
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        tracemalloc.stop()


def find_expensive_functions():
    """Find the most expensive functions across modules."""
    print("\n=== Finding Expensive Functions ===")
    
    # Create comprehensive test
    pr = cProfile.Profile()
    pr.enable()
    
    # Run various operations
    data = np.random.randn(1000, 100)
    df = pd.DataFrame(data)
    
    # I/O operations
    test_dir = Path('.dev/perf_test')
    test_dir.mkdir(exist_ok=True)
    stx.io.save(df, test_dir / 'temp.csv')
    _ = stx.io.load(test_dir / 'temp.csv')
    
    # Gen operations
    _ = stx.gen.to_z(data)
    _ = stx.gen.to_01(data)
    
    # Stats operations
    _ = stx.stats.describe(data[:, 0])
    
    # Path operations
    _ = stx.path.find("*.py", "src", max_depth=2)
    
    pr.disable()
    
    # Get top 30 most expensive functions
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    
    stats_output = s.getvalue()
    print(stats_output)
    
    # Save detailed report
    with open('.dev/performance_report.txt', 'w') as f:
        f.write(stats_output)
    
    print("\nDetailed report saved to .dev/performance_report.txt")


def suggest_optimizations():
    """Suggest specific optimizations based on profiling."""
    print("\n=== Optimization Suggestions ===")
    
    suggestions = []
    
    # Check for repeated calculations
    print("\n1. Checking for repeated calculations...")
    
    # Test gen.to_z with caching potential
    data = np.random.randn(1000, 100)
    
    start = time.time()
    for _ in range(10):
        _ = stx.gen.to_z(data)
    no_cache_time = time.time() - start
    
    print(f"   10x gen.to_z without caching: {no_cache_time:.3f}s")
    suggestions.append({
        'function': 'gen.to_z',
        'issue': 'No caching for repeated calls with same data',
        'suggestion': 'Add @cache decorator for pure functions',
        'potential_speedup': '10x for repeated calls'
    })
    
    # Check for inefficient algorithms
    print("\n2. Checking algorithm efficiency...")
    
    # Test stats operations
    x = np.random.randn(10000)
    y = np.random.randn(10000)
    
    start = time.time()
    _ = stx.stats.corr_test(x, y)
    corr_time = time.time() - start
    
    if corr_time > 0.1:
        suggestions.append({
            'function': 'stats.corr_test',
            'issue': 'Slow correlation computation',
            'suggestion': 'Use numpy.corrcoef instead of manual calculation',
            'potential_speedup': '5x'
        })
    
    # Check for unnecessary file I/O
    print("\n3. Checking I/O patterns...")
    
    # Test repeated loads
    test_dir = Path('.dev/perf_test')
    test_dir.mkdir(exist_ok=True)
    cache_file = test_dir / 'test_cache.npy'
    stx.io.save(data, cache_file)
    
    start = time.time()
    for _ in range(5):
        _ = stx.io.load(cache_file)
    io_time = time.time() - start
    
    print(f"   5x repeated loads: {io_time:.3f}s")
    suggestions.append({
        'function': 'io.load',
        'issue': 'No caching for recently loaded files',
        'suggestion': 'Implement LRU cache for file loads',
        'potential_speedup': '100x for repeated loads'
    })
    
    # Print suggestions
    print("\n=== Optimization Recommendations ===")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['function']}")
        print(f"   Issue: {suggestion['issue']}")
        print(f"   Suggestion: {suggestion['suggestion']}")
        print(f"   Potential speedup: {suggestion['potential_speedup']}")
    
    # Save suggestions
    with open('.dev/optimization_suggestions.txt', 'w') as f:
        for suggestion in suggestions:
            f.write(f"{suggestion['function']}\n")
            f.write(f"  Issue: {suggestion['issue']}\n")
            f.write(f"  Suggestion: {suggestion['suggestion']}\n")
            f.write(f"  Potential speedup: {suggestion['potential_speedup']}\n\n")


def main():
    """Run all performance analyses."""
    print("SciTeX Performance Analysis")
    print("=" * 60)
    
    # Create .dev directory if it doesn't exist
    os.makedirs('.dev', exist_ok=True)
    
    # Run analyses
    identify_slow_imports()
    profile_io_operations()
    profile_gen_operations()
    profile_stats_operations()
    analyze_memory_usage()
    find_expensive_functions()
    suggest_optimizations()
    
    # Cleanup
    import shutil
    if Path('.dev/perf_test').exists():
        shutil.rmtree('.dev/perf_test')
    if Path('.dev/performance_analysis_out').exists():
        shutil.rmtree('.dev/performance_analysis_out')
    
    print("\n" + "=" * 60)
    print("Performance analysis complete!")
    print("Check .dev/performance_report.txt for detailed results")
    print("Check .dev/optimization_suggestions.txt for recommendations")


if __name__ == "__main__":
    main()