#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:30:00"
# File: benchmark.py

"""
Core benchmarking functionality for SciTeX.
"""

import time
import numpy as np
import pandas as pd
from typing import Callable, Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import inspect
import gc
import os
from pathlib import Path


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    function_name: str
    module: str
    mean_time: float
    std_time: float
    min_time: float
    max_time: float
    iterations: int
    input_size: Optional[str] = None
    memory_usage: Optional[float] = None
    notes: Optional[str] = None
    
    def __str__(self):
        return (f"{self.function_name}: {self.mean_time:.3f}s ± {self.std_time:.3f}s "
                f"(n={self.iterations})")
    
    def to_dict(self):
        """Convert to dictionary for easy serialization."""
        return {
            'function': self.function_name,
            'module': self.module,
            'mean_time': self.mean_time,
            'std_time': self.std_time,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'iterations': self.iterations,
            'input_size': self.input_size,
            'memory_usage': self.memory_usage,
            'notes': self.notes
        }


def benchmark_function(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    iterations: int = 10,
    warmup: int = 2,
    input_size: Optional[str] = None,
    measure_memory: bool = False
) -> BenchmarkResult:
    """
    Benchmark a single function.
    
    Parameters
    ----------
    func : Callable
        Function to benchmark
    args : tuple
        Arguments to pass to function
    kwargs : dict
        Keyword arguments to pass to function
    iterations : int
        Number of benchmark iterations
    warmup : int
        Number of warmup iterations
    input_size : str, optional
        Description of input size
    measure_memory : bool
        Whether to measure memory usage
        
    Returns
    -------
    BenchmarkResult
        Benchmark results
    """
    if kwargs is None:
        kwargs = {}
    
    # Warmup runs
    for _ in range(warmup):
        _ = func(*args, **kwargs)
    
    # Garbage collection before timing
    gc.collect()
    
    # Timing runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        _ = func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)
    
    times = np.array(times)
    
    # Get function info
    module = inspect.getmodule(func).__name__ if inspect.getmodule(func) else 'unknown'
    
    # Memory measurement (simplified)
    memory_usage = None
    if measure_memory:
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except:
            pass
    
    return BenchmarkResult(
        function_name=func.__name__,
        module=module,
        mean_time=np.mean(times),
        std_time=np.std(times),
        min_time=np.min(times),
        max_time=np.max(times),
        iterations=iterations,
        input_size=input_size,
        memory_usage=memory_usage
    )


def compare_implementations(
    implementations: Dict[str, Callable],
    test_data_generator: Callable[[], Tuple[tuple, dict]],
    iterations: int = 10,
    sizes: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compare multiple implementations of the same functionality.
    
    Parameters
    ----------
    implementations : dict
        Dictionary mapping implementation names to functions
    test_data_generator : callable
        Function that returns (args, kwargs) for testing
    iterations : int
        Number of iterations per implementation
    sizes : list, optional
        List of input sizes to test
        
    Returns
    -------
    pd.DataFrame
        Comparison results
    """
    results = []
    
    for name, func in implementations.items():
        # Generate test data
        args, kwargs = test_data_generator()
        
        # Benchmark
        result = benchmark_function(
            func,
            args=args,
            kwargs=kwargs,
            iterations=iterations
        )
        
        results.append({
            'implementation': name,
            'mean_time': result.mean_time,
            'std_time': result.std_time,
            'speedup': 1.0  # Will calculate relative to baseline
        })
    
    df = pd.DataFrame(results)
    
    # Calculate speedup relative to first implementation
    baseline_time = df.iloc[0]['mean_time']
    df['speedup'] = baseline_time / df['mean_time']
    
    return df


class BenchmarkSuite:
    """Collection of benchmarks for a module or set of functions."""
    
    def __init__(self, name: str):
        self.name = name
        self.benchmarks = []
        self.results = []
    
    def add_benchmark(
        self,
        func: Callable,
        test_data_generator: Callable[[], Tuple[tuple, dict]],
        name: Optional[str] = None,
        sizes: Optional[List[str]] = None
    ):
        """Add a benchmark to the suite."""
        self.benchmarks.append({
            'func': func,
            'data_gen': test_data_generator,
            'name': name or func.__name__,
            'sizes': sizes or ['default']
        })
    
    def run(self, iterations: int = 10, verbose: bool = True) -> pd.DataFrame:
        """Run all benchmarks in the suite."""
        results = []
        
        for benchmark in self.benchmarks:
            if verbose:
                print(f"Running benchmark: {benchmark['name']}")
            
            for size in benchmark['sizes']:
                # Generate test data
                args, kwargs = benchmark['data_gen']()
                
                # Run benchmark
                result = benchmark_function(
                    benchmark['func'],
                    args=args,
                    kwargs=kwargs,
                    iterations=iterations,
                    input_size=size
                )
                
                result_dict = result.to_dict()
                result_dict['size'] = size
                results.append(result_dict)
                
                if verbose:
                    print(f"  {size}: {result}")
        
        self.results = pd.DataFrame(results)
        return self.results
    
    def save_results(self, path: str):
        """Save benchmark results to CSV."""
        if self.results is not None:
            self.results.to_csv(path, index=False)
    
    def compare_with_baseline(self, baseline_path: str) -> pd.DataFrame:
        """Compare current results with baseline."""
        baseline = pd.read_csv(baseline_path)
        
        # Merge on function name and size
        comparison = pd.merge(
            self.results,
            baseline,
            on=['function', 'size'],
            suffixes=('_current', '_baseline')
        )
        
        # Calculate speedup
        comparison['speedup'] = (
            comparison['mean_time_baseline'] / 
            comparison['mean_time_current']
        )
        
        return comparison


def benchmark_module(module_name: str, pattern: str = "test_*") -> BenchmarkSuite:
    """
    Create a benchmark suite for all matching functions in a module.
    
    Parameters
    ----------
    module_name : str
        Name of module to benchmark
    pattern : str
        Pattern to match function names
        
    Returns
    -------
    BenchmarkSuite
        Suite containing all matching benchmarks
    """
    import importlib
    import fnmatch
    
    module = importlib.import_module(module_name)
    suite = BenchmarkSuite(module_name)
    
    # Find all matching functions
    for name in dir(module):
        if fnmatch.fnmatch(name, pattern):
            func = getattr(module, name)
            if callable(func):
                # Create simple test data generator
                def data_gen():
                    return (), {}
                
                suite.add_benchmark(func, data_gen, name)
    
    return suite


# Pre-defined benchmark suites for common SciTeX modules
def create_io_benchmark_suite() -> BenchmarkSuite:
    """Create benchmark suite for I/O operations."""
    import tempfile
    import numpy as np
    
    suite = BenchmarkSuite("IO Operations")
    
    # Benchmark numpy file loading
    def numpy_data_gen():
        data = np.random.randn(1000, 1000)
        with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
            np.save(f.name, data)
            return (f.name,), {}
    
    import scitex.io
    suite.add_benchmark(
        scitex.io.load,
        numpy_data_gen,
        "load_numpy",
        sizes=['1MB', '10MB', '100MB']
    )
    
    return suite


def create_stats_benchmark_suite() -> BenchmarkSuite:
    """Create benchmark suite for statistics operations."""
    import numpy as np
    
    suite = BenchmarkSuite("Statistics Operations")
    
    # Benchmark correlation
    def corr_data_gen():
        x = np.random.randn(1000)
        y = x + np.random.randn(1000) * 0.5
        return (x, y), {'n_perm': 1000}
    
    import scitex.stats
    suite.add_benchmark(
        scitex.stats.corr_test,
        corr_data_gen,
        "correlation_test",
        sizes=['1000_samples', '10000_samples']
    )
    
    return suite


def run_all_benchmarks(output_dir: str = "./benchmark_results") -> Dict[str, pd.DataFrame]:
    """
    Run all pre-defined benchmark suites.
    
    Parameters
    ----------
    output_dir : str
        Directory to save results
        
    Returns
    -------
    dict
        Dictionary mapping suite names to results
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    suites = {
        'io': create_io_benchmark_suite(),
        'stats': create_stats_benchmark_suite(),
    }
    
    results = {}
    for name, suite in suites.items():
        print(f"\nRunning {name} benchmarks...")
        df = suite.run()
        
        # Save results
        suite.save_results(output_path / f"{name}_benchmark.csv")
        results[name] = df
    
    # Create summary
    summary = []
    for name, df in results.items():
        summary.append({
            'suite': name,
            'functions': len(df['function'].unique()),
            'mean_time': df['mean_time'].mean(),
            'total_time': df['mean_time'].sum()
        })
    
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(output_path / "benchmark_summary.csv", index=False)
    
    print(f"\nBenchmark results saved to {output_path}")
    return results