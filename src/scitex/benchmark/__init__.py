#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:25:00"
# File: __init__.py

"""
SciTeX Performance Benchmarking Suite

This module provides tools for benchmarking and monitoring the performance
of SciTeX functions.
"""

from .benchmark import (
    benchmark_function,
    benchmark_module,
    BenchmarkResult,
    BenchmarkSuite,
    run_all_benchmarks,
    compare_implementations
)

from .profiler import (
    profile_function,
    profile_module,
    get_profile_report
)

from .monitor import (
    PerformanceMonitor,
    track_performance,
    get_performance_stats
)

__all__ = [
    # Benchmarking
    'benchmark_function',
    'benchmark_module',
    'BenchmarkResult',
    'BenchmarkSuite',
    'run_all_benchmarks',
    'compare_implementations',
    
    # Profiling
    'profile_function',
    'profile_module',
    'get_profile_report',
    
    # Monitoring
    'PerformanceMonitor',
    'track_performance',
    'get_performance_stats'
]