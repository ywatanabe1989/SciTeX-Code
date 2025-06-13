#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 20:48:00"
# File: /tests/scitex/io/test__io_benchmarks.py
# ----------------------------------------
"""
Performance benchmark tests for scitex.io module.

These tests measure and track performance characteristics:
- File I/O speed for different formats
- Memory usage patterns
- Scaling behavior with data size
- Compression effectiveness
"""

import os
import sys
import time
import pytest
import numpy as np
import pandas as pd
import tempfile
import psutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))
import scitex


@pytest.mark.benchmark
class TestIOPerformance:
    """Benchmark tests for I/O operations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temp directory for benchmarks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture(scope="class")
    def benchmark_datasets(self):
        """Generate datasets of various sizes for benchmarking."""
        return {
            'tiny': np.random.rand(10, 10),           # ~800 bytes
            'small': np.random.rand(100, 100),        # ~80 KB
            'medium': np.random.rand(1000, 100),      # ~800 KB
            'large': np.random.rand(1000, 1000),      # ~8 MB
            'xlarge': np.random.rand(5000, 1000),     # ~40 MB
            'huge': np.random.rand(10000, 1000),      # ~80 MB
        }
    
    # --- Format Comparison Benchmarks ---
    @pytest.mark.parametrize("size_name,expected_range", [
        ('tiny', (0.001, 0.01)),     # 1-10ms
        ('small', (0.001, 0.05)),    # 1-50ms
        ('medium', (0.01, 0.1)),     # 10-100ms
        ('large', (0.05, 0.5)),      # 50-500ms
        ('xlarge', (0.2, 2.0)),      # 200ms-2s
    ])
    def test_numpy_save_performance(self, benchmark_datasets, temp_dir, size_name, expected_range):
        """Benchmark numpy array saving performance."""
        data = benchmark_datasets[size_name]
        path = os.path.join(temp_dir, f'bench_{size_name}.npy')
        
        # Warm up
        scitex.io.save(data, path, verbose=False)
        
        # Benchmark
        times = []
        for _ in range(5):
            start = time.time()
            scitex.io.save(data, path, verbose=False)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        assert expected_range[0] <= avg_time <= expected_range[1], \
            f"Save time {avg_time:.3f}s outside expected range {expected_range}"
    
    def test_format_performance_comparison(self, temp_dir):
        """Compare performance across different file formats."""
        # Test data
        data_array = np.random.rand(1000, 100)
        data_df = pd.DataFrame(data_array)
        data_dict = {'array': data_array, 'metadata': {'shape': data_array.shape}}
        
        results = {}
        
        # Test different formats
        test_cases = [
            (data_array, 'array.npy', 'numpy'),
            (data_dict, 'dict.npz', 'numpy_compressed'),
            (data_df, 'df.csv', 'csv'),
            (data_dict, 'dict.json', 'json'),
            (data_dict, 'dict.pkl', 'pickle'),
        ]
        
        for data, filename, format_name in test_cases:
            path = os.path.join(temp_dir, filename)
            
            # Time save operation
            start = time.time()
            scitex.io.save(data, path, verbose=False)
            save_time = time.time() - start
            
            # Time load operation
            start = time.time()
            loaded = scitex.io.load(path)
            load_time = time.time() - start
            
            # Get file size
            file_size = os.path.getsize(path) / 1024  # KB
            
            results[format_name] = {
                'save_time': save_time,
                'load_time': load_time,
                'file_size_kb': file_size,
                'efficiency': file_size / (save_time + load_time)  # KB/s
            }
        
        # Assert numpy is fastest for array data
        assert results['numpy']['save_time'] < results['csv']['save_time']
        assert results['numpy']['load_time'] < results['csv']['load_time']
    
    # --- Memory Usage Benchmarks ---
    def test_memory_usage_large_files(self, temp_dir):
        """Test memory usage patterns with large files."""
        process = psutil.Process()
        
        # Create large dataset (100MB)
        large_data = np.random.rand(5000, 2500)
        expected_size = large_data.nbytes / 1024 / 1024  # MB
        
        path = os.path.join(temp_dir, 'large_memory_test.npy')
        
        # Measure memory before save
        memory_before = process.memory_info().rss / 1024 / 1024
        
        # Save data
        scitex.io.save(large_data, path, verbose=False)
        
        # Measure memory after save
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_increase = memory_after - memory_before
        
        # Memory increase should be minimal (not holding duplicate in memory)
        assert memory_increase < expected_size * 0.5, \
            f"Memory increased by {memory_increase}MB, expected < {expected_size * 0.5}MB"
        
        # Clean up reference
        del large_data
        
        # Test loading memory usage
        memory_before_load = process.memory_info().rss / 1024 / 1024
        loaded = scitex.io.load(path)
        memory_after_load = process.memory_info().rss / 1024 / 1024
        
        load_memory_increase = memory_after_load - memory_before_load
        assert load_memory_increase < expected_size * 1.5, \
            f"Loading increased memory by {load_memory_increase}MB"
    
    # --- Scaling Behavior ---
    def test_linear_scaling_behavior(self, temp_dir):
        """Test that I/O operations scale linearly with data size."""
        sizes = [100, 500, 1000, 2000, 4000]
        times = []
        
        for size in sizes:
            data = np.random.rand(size, size)
            path = os.path.join(temp_dir, f'scale_{size}.npy')
            
            # Measure time
            start = time.time()
            scitex.io.save(data, path, verbose=False)
            save_time = time.time() - start
            
            times.append(save_time)
            
            # Clean up to avoid running out of space
            os.unlink(path)
        
        # Check if scaling is approximately linear
        # Time should roughly double when data size quadruples
        for i in range(1, len(sizes)):
            size_ratio = (sizes[i] * sizes[i]) / (sizes[i-1] * sizes[i-1])
            time_ratio = times[i] / times[i-1]
            
            # Allow some deviation from perfect linear scaling
            assert 0.5 * size_ratio <= time_ratio <= 2.0 * size_ratio, \
                f"Non-linear scaling: size increased {size_ratio}x, time increased {time_ratio}x"
    
    # --- Compression Benchmarks ---
    def test_compression_effectiveness(self, temp_dir):
        """Test compression ratios and performance for different data types."""
        test_cases = [
            # (data, description, expected_compression_ratio)
            (np.zeros((1000, 1000)), "zeros", 0.001),  # Should compress very well
            (np.ones((1000, 1000)), "ones", 0.001),    # Should compress very well
            (np.random.rand(1000, 1000), "random", 0.9),  # Poor compression
            (np.repeat(np.arange(1000), 1000).reshape(1000, 1000), "repeated", 0.1),  # Good compression
        ]
        
        results = []
        
        for data, desc, expected_ratio in test_cases:
            # Save uncompressed
            path_raw = os.path.join(temp_dir, f'{desc}_raw.npy')
            start = time.time()
            scitex.io.save(data, path_raw, verbose=False)
            time_raw = time.time() - start
            size_raw = os.path.getsize(path_raw)
            
            # Save compressed
            path_compressed = os.path.join(temp_dir, f'{desc}_compressed.npz')
            start = time.time()
            scitex.io.save({'data': data}, path_compressed, compress=True, verbose=False)
            time_compressed = time.time() - start
            size_compressed = os.path.getsize(path_compressed)
            
            compression_ratio = size_compressed / size_raw
            
            results.append({
                'data_type': desc,
                'size_raw_mb': size_raw / 1024 / 1024,
                'size_compressed_mb': size_compressed / 1024 / 1024,
                'compression_ratio': compression_ratio,
                'time_raw': time_raw,
                'time_compressed': time_compressed,
                'time_overhead': time_compressed / time_raw
            })
            
            # Verify compression effectiveness
            assert compression_ratio <= expected_ratio * 2, \
                f"{desc} data compressed poorly: {compression_ratio:.3f} vs expected {expected_ratio}"
        
        return results
    
    # --- Concurrent I/O Performance ---
    def test_concurrent_io_performance(self, temp_dir):
        """Test performance under concurrent I/O load."""
        import threading
        import queue
        
        num_threads = 4
        operations_per_thread = 10
        data_size = (100, 100)
        
        times_queue = queue.Queue()
        
        def worker(thread_id):
            thread_times = []
            for i in range(operations_per_thread):
                data = np.random.rand(*data_size)
                path = os.path.join(temp_dir, f'thread_{thread_id}_file_{i}.npy')
                
                start = time.time()
                scitex.io.save(data, path, verbose=False)
                thread_times.append(time.time() - start)
            
            times_queue.put(thread_times)
        
        # Run concurrent operations
        start_total = time.time()
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        total_time = time.time() - start_total
        
        # Collect all times
        all_times = []
        while not times_queue.empty():
            all_times.extend(times_queue.get())
        
        # Calculate statistics
        avg_time = np.mean(all_times)
        max_time = np.max(all_times)
        total_ops = num_threads * operations_per_thread
        
        # Performance should not degrade too much under concurrent load
        sequential_estimate = avg_time * total_ops
        parallel_speedup = sequential_estimate / total_time
        
        assert parallel_speedup > 0.5, \
            f"Poor parallel performance: {parallel_speedup:.2f}x speedup with {num_threads} threads"
    
    # --- CSV Performance Optimization ---
    @pytest.mark.parametrize("rows,cols", [
        (100, 10),
        (1000, 10),
        (1000, 100),
        (10000, 10),
    ])
    def test_csv_performance_by_shape(self, temp_dir, rows, cols):
        """Test CSV I/O performance for different shapes."""
        df = pd.DataFrame(np.random.rand(rows, cols))
        path = os.path.join(temp_dir, f'perf_{rows}x{cols}.csv')
        
        # Benchmark save
        save_times = []
        for _ in range(3):
            start = time.time()
            scitex.io.save(df, path, verbose=False)
            save_times.append(time.time() - start)
        
        # Benchmark load
        load_times = []
        for _ in range(3):
            start = time.time()
            loaded = scitex.io.load(path)
            load_times.append(time.time() - start)
        
        avg_save = np.mean(save_times)
        avg_load = np.mean(load_times)
        
        # Performance expectations (rough guidelines)
        cells = rows * cols
        expected_save_time = cells * 1e-6  # ~1 microsecond per cell
        expected_load_time = cells * 2e-6  # ~2 microseconds per cell
        
        # Allow 10x margin for CI environments
        assert avg_save < expected_save_time * 10, \
            f"CSV save too slow: {avg_save:.3f}s for {cells} cells"
        assert avg_load < expected_load_time * 10, \
            f"CSV load too slow: {avg_load:.3f}s for {cells} cells"
    
    # --- Performance Regression Tests ---
    def test_performance_regression_suite(self, temp_dir, benchmark_datasets):
        """Comprehensive performance regression test suite."""
        baseline_performance = {
            # Format: (operation, size) -> expected_time_seconds
            ('save_npy', 'small'): 0.01,
            ('save_npy', 'medium'): 0.05,
            ('save_npy', 'large'): 0.5,
            ('save_csv', 'small'): 0.02,
            ('save_csv', 'medium'): 0.1,
            ('save_json', 'small'): 0.01,
            ('load_npy', 'small'): 0.005,
            ('load_npy', 'medium'): 0.02,
            ('load_csv', 'small'): 0.02,
        }
        
        tolerance = 5.0  # Allow 5x slower than baseline (for CI environments)
        
        results = {}
        
        for (operation, size), expected_time in baseline_performance.items():
            if size not in benchmark_datasets:
                continue
                
            data = benchmark_datasets[size]
            
            if 'npy' in operation:
                path = os.path.join(temp_dir, f'regression_{size}.npy')
                test_data = data
            elif 'csv' in operation:
                path = os.path.join(temp_dir, f'regression_{size}.csv')
                test_data = pd.DataFrame(data[:100, :10])  # Smaller for CSV
            elif 'json' in operation:
                path = os.path.join(temp_dir, f'regression_{size}.json')
                test_data = {'data': data[:10, :10].tolist()}  # Much smaller for JSON
            else:
                continue
            
            if operation.startswith('save'):
                start = time.time()
                scitex.io.save(test_data, path, verbose=False)
                actual_time = time.time() - start
            else:  # load operation
                # Ensure file exists
                if not os.path.exists(path):
                    scitex.io.save(test_data, path, verbose=False)
                
                start = time.time()
                loaded = scitex.io.load(path)
                actual_time = time.time() - start
            
            results[f"{operation}_{size}"] = actual_time
            
            # Check against baseline
            assert actual_time < expected_time * tolerance, \
                f"{operation} {size}: {actual_time:.3f}s exceeds baseline {expected_time}s by >{tolerance}x"
        
        return results


# --- Performance Tracking Decorator ---
def track_performance(func):
    """Decorator to track and report performance metrics."""
    def wrapper(*args, **kwargs):
        import gc
        gc.collect()  # Clean up before measurement
        
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024
        
        print(f"\nPerformance Report for {func.__name__}:")
        print(f"  Duration: {end_time - start_time:.3f}s")
        print(f"  Memory used: {end_memory - start_memory:.1f}MB")
        print(f"  Final memory: {end_memory:.1f}MB")
        
        return result
    
    return wrapper


# Run with: pytest -m benchmark tests/scitex/io/test__io_benchmarks.py
# For detailed output: pytest -v -s -m benchmark tests/scitex/io/test__io_benchmarks.py

# EOF