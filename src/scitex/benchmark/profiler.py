#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:35:00"
# File: profiler.py

"""
Profiling tools for SciTeX performance analysis.
"""

import cProfile
import pstats
import io
from typing import Callable, Optional, Dict, Any
from functools import wraps
import time
from contextlib import contextmanager


class FunctionProfiler:
    """Profile individual function calls."""
    
    def __init__(self):
        self.profiles = {}
        self.call_counts = {}
        self.total_times = {}
    
    def profile(self, func: Callable) -> Callable:
        """
        Decorator to profile a function.
        
        Example
        -------
        >>> profiler = FunctionProfiler()
        >>> @profiler.profile
        ... def my_function(x):
        ...     return x ** 2
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create profiler for this call
            pr = cProfile.Profile()
            pr.enable()
            
            # Call function
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            pr.disable()
            
            # Store results
            func_name = func.__name__
            if func_name not in self.profiles:
                self.profiles[func_name] = []
                self.call_counts[func_name] = 0
                self.total_times[func_name] = 0.0
            
            self.profiles[func_name].append(pr)
            self.call_counts[func_name] += 1
            self.total_times[func_name] += (end_time - start_time)
            
            return result
        
        return wrapper
    
    def get_stats(self, func_name: str) -> Optional[pstats.Stats]:
        """Get profiling statistics for a function."""
        if func_name not in self.profiles:
            return None
        
        # Combine all profiles for this function
        combined = pstats.Stats(self.profiles[func_name][0])
        for pr in self.profiles[func_name][1:]:
            combined.add(pr)
        
        return combined
    
    def print_stats(self, func_name: Optional[str] = None, top_n: int = 10):
        """Print profiling statistics."""
        if func_name:
            stats = self.get_stats(func_name)
            if stats:
                print(f"\nProfile for {func_name}:")
                print(f"Total calls: {self.call_counts[func_name]}")
                print(f"Total time: {self.total_times[func_name]:.3f}s")
                print(f"Avg time per call: {self.total_times[func_name]/self.call_counts[func_name]:.3f}s")
                print("\nDetailed stats:")
                stats.sort_stats('cumulative').print_stats(top_n)
        else:
            # Print all functions
            for name in self.profiles:
                self.print_stats(name, top_n)
    
    def get_report(self) -> Dict[str, Any]:
        """Get a summary report of all profiled functions."""
        report = {}
        for func_name in self.profiles:
            stats = self.get_stats(func_name)
            
            # Get top time consumers
            s = io.StringIO()
            stats.sort_stats('cumulative').print_stats(10, s)
            
            report[func_name] = {
                'call_count': self.call_counts[func_name],
                'total_time': self.total_times[func_name],
                'avg_time': self.total_times[func_name] / self.call_counts[func_name],
                'profile': s.getvalue()
            }
        
        return report


# Global profiler instance
_global_profiler = FunctionProfiler()


def profile_function(func: Callable) -> Callable:
    """
    Decorator to profile a function using the global profiler.
    
    Example
    -------
    >>> @profile_function
    ... def my_function(x):
    ...     return sum(range(x))
    """
    return _global_profiler.profile(func)


def get_profile_report() -> Dict[str, Any]:
    """Get profiling report from global profiler."""
    return _global_profiler.get_report()


def print_profile_stats(func_name: Optional[str] = None):
    """Print profiling statistics from global profiler."""
    _global_profiler.print_stats(func_name)


@contextmanager
def profile_block(name: str):
    """
    Context manager for profiling a code block.
    
    Example
    -------
    >>> with profile_block("data_processing"):
    ...     # Some expensive operations
    ...     data = process_data()
    """
    pr = cProfile.Profile()
    pr.enable()
    start_time = time.time()
    
    try:
        yield
    finally:
        pr.disable()
        end_time = time.time()
        
        print(f"\nProfile for block '{name}':")
        print(f"Total time: {end_time - start_time:.3f}s")
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        print(s.getvalue())


def profile_module(module_name: str, pattern: str = "*") -> Dict[str, Any]:
    """
    Profile all matching functions in a module.
    
    Parameters
    ----------
    module_name : str
        Name of module to profile
    pattern : str
        Pattern to match function names
        
    Returns
    -------
    dict
        Profiling results
    """
    import importlib
    import fnmatch
    
    module = importlib.import_module(module_name)
    profiler = FunctionProfiler()
    
    # Wrap all matching functions
    wrapped_functions = []
    for name in dir(module):
        if fnmatch.fnmatch(name, pattern):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith('_'):
                # Replace with profiled version
                profiled = profiler.profile(obj)
                setattr(module, name, profiled)
                wrapped_functions.append(name)
    
    print(f"Profiling {len(wrapped_functions)} functions in {module_name}")
    print(f"Wrapped: {', '.join(wrapped_functions)}")
    print("\nRun your code now. Call get_profile_report() when done.")
    
    return profiler


class LineProfiler:
    """
    Line-by-line profiler for detailed analysis.
    
    Note: This is a simplified version. For production use,
    consider using the line_profiler package.
    """
    
    def __init__(self):
        self.timings = {}
    
    def profile_lines(self, func: Callable) -> Callable:
        """Profile a function line by line."""
        import inspect
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get source lines
            source_lines = inspect.getsourcelines(func)[0]
            line_times = {}
            
            # This is a simplified implementation
            # Real line profiling requires bytecode instrumentation
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Store timing
            func_name = func.__name__
            if func_name not in self.timings:
                self.timings[func_name] = []
            
            self.timings[func_name].append({
                'total_time': end_time - start_time,
                'source': source_lines
            })
            
            return result
        
        return wrapper
    
    def print_timings(self, func_name: str):
        """Print line timings for a function."""
        if func_name not in self.timings:
            print(f"No timings for {func_name}")
            return
        
        timing = self.timings[func_name][-1]  # Most recent
        print(f"\nLine timings for {func_name}:")
        print(f"Total time: {timing['total_time']:.3f}s")
        print("\nSource code:")
        for i, line in enumerate(timing['source']):
            print(f"{i+1:4d}: {line.rstrip()}")


# Memory profiling utilities
def get_memory_usage():
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return None


@contextmanager
def track_memory(name: str):
    """
    Track memory usage for a code block.
    
    Example
    -------
    >>> with track_memory("data_loading"):
    ...     data = load_large_dataset()
    """
    start_mem = get_memory_usage()
    
    try:
        yield
    finally:
        end_mem = get_memory_usage()
        if start_mem and end_mem:
            print(f"\nMemory usage for '{name}':")
            print(f"Start: {start_mem:.1f} MB")
            print(f"End: {end_mem:.1f} MB")
            print(f"Delta: {end_mem - start_mem:+.1f} MB")