#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:45:00"
# File: benchmark_example.py

"""
Example of using the SciTeX benchmarking suite.
"""

import numpy as np
import scitex as stx
from scitex.benchmark import (
    benchmark_function,
    compare_implementations,
    BenchmarkSuite,
    track_performance,
    start_monitoring,
    stop_monitoring,
    get_performance_stats,
    profile_function,
    get_profile_report
)


# Example 1: Benchmark a single function
def example_benchmark_single():
    """Benchmark a single function."""
    print("=== Single Function Benchmark ===")
    
    # Define a function to benchmark
    def matrix_multiply(size=1000):
        A = np.random.randn(size, size)
        B = np.random.randn(size, size)
        return np.dot(A, B)
    
    # Benchmark it
    result = benchmark_function(
        matrix_multiply,
        args=(),
        kwargs={'size': 500},
        iterations=5,
        warmup=1,
        input_size='500x500'
    )
    
    print(f"Result: {result}")
    print(f"Average time: {result.mean_time:.3f}s ± {result.std_time:.3f}s")


# Example 2: Compare implementations
def example_compare_implementations():
    """Compare different implementations."""
    print("\n\n=== Implementation Comparison ===")
    
    # Different ways to normalize data
    def normalize_v1(data):
        return (data - np.mean(data)) / np.std(data)
    
    def normalize_v2(data):
        mean = data.mean()
        std = data.std()
        return (data - mean) / std
    
    def normalize_v3(data):
        # Using SciTeX
        return stx.gen.to_z(data)
    
    # Test data generator
    def get_test_data():
        data = np.random.randn(10000, 100)
        return (data,), {}
    
    # Compare
    results = compare_implementations(
        implementations={
            'numpy_functions': normalize_v1,
            'cached_mean_std': normalize_v2,
            'scitex': normalize_v3
        },
        test_data_generator=get_test_data,
        iterations=10
    )
    
    print(results)


# Example 3: Benchmark suite
def example_benchmark_suite():
    """Create and run a benchmark suite."""
    print("\n\n=== Benchmark Suite ===")
    
    suite = BenchmarkSuite("Data Processing")
    
    # Add benchmarks
    def load_test_gen():
        import tempfile
        data = np.random.randn(1000, 100)
        with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
            np.save(f.name, data)
            return (f.name,), {}
    
    suite.add_benchmark(
        stx.io.load,
        load_test_gen,
        "file_loading",
        sizes=['small', 'medium', 'large']
    )
    
    # Run suite
    results = suite.run(iterations=5, verbose=True)
    print("\nResults:")
    print(results)


# Example 4: Performance monitoring
@track_performance
def slow_function(n=1000000):
    """A function we want to monitor."""
    total = 0
    for i in range(n):
        total += i ** 2
    return total


@track_performance
def fast_function(n=1000):
    """A faster function."""
    return sum(i ** 2 for i in range(n))


def example_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n\n=== Performance Monitoring ===")
    
    # Start monitoring
    start_monitoring()
    
    # Call functions multiple times
    for i in range(5):
        slow_function(1000000)
        fast_function(10000)
    
    # Get statistics
    stats = get_performance_stats()
    
    print("\nPerformance Statistics:")
    for func, data in stats.items():
        print(f"\n{func}:")
        print(f"  Calls: {data['count']}")
        print(f"  Avg time: {data['avg_time']:.3f}s")
        print(f"  Min/Max: {data['min_time']:.3f}s / {data['max_time']:.3f}s")
    
    stop_monitoring()


# Example 5: Profiling
@profile_function
def complex_calculation(n=1000):
    """Function with multiple operations to profile."""
    # Data generation
    data = np.random.randn(n, n)
    
    # Normalization
    normalized = (data - data.mean()) / data.std()
    
    # Matrix operations
    result = np.dot(normalized, normalized.T)
    
    # Eigenvalue decomposition
    eigenvalues = np.linalg.eigvals(result)
    
    return eigenvalues


def example_profiling():
    """Demonstrate function profiling."""
    print("\n\n=== Function Profiling ===")
    
    # Call the profiled function
    for i in range(3):
        _ = complex_calculation(500)
    
    # Get profile report
    report = get_profile_report()
    
    print("\nProfile Report:")
    for func_name, data in report.items():
        print(f"\n{func_name}:")
        print(f"  Total calls: {data['call_count']}")
        print(f"  Total time: {data['total_time']:.3f}s")
        print(f"  Avg time: {data['avg_time']:.3f}s")


def main():
    """Run all examples."""
    print("SciTeX Benchmarking Examples")
    print("=" * 50)
    
    example_benchmark_single()
    example_compare_implementations()
    example_benchmark_suite()
    example_performance_monitoring()
    example_profiling()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    main()