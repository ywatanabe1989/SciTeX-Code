#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-09 09:05:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/etc/test_etc_performance.py
# ----------------------------------------
"""Performance benchmarks for etc module."""

import os
import sys
import time
import threading
import multiprocessing
import statistics
from unittest.mock import Mock, patch
import pytest

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

__FILE__ = "./tests/scitex/etc/test_etc_performance.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


class TestEtcPerformance:
    """Performance benchmarks for etc module functions."""

    @pytest.fixture
    def benchmark_results(self):
        """Fixture to collect benchmark results."""
        return {
            'wait_key': {},
            'count': {},
            'memory': {}
        }

    def test_wait_key_response_time(self, benchmark_results):
        """Benchmark wait_key response time to key presses."""
        from scitex.etc import wait_key
        
        response_times = []
        
        for num_keys in [10, 100, 1000]:
            keys = ['x'] * num_keys + ['q']
            
            mock_process = Mock()
            
            start_time = time.perf_counter()
            
            with patch('scitex.etc.wait_key.readchar.readchar', side_effect=keys):
                with patch('builtins.print'):
                    wait_key(mock_process)
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            response_times.append({
                'num_keys': num_keys,
                'total_time': duration,
                'time_per_key': duration / (num_keys + 1)
            })
        
        # Store results
        benchmark_results['wait_key']['response_times'] = response_times
        
        # Performance assertions
        for result in response_times:
            # Should process at least 1000 keys per second
            assert result['time_per_key'] < 0.001
            
        # Check scaling
        times = [r['time_per_key'] for r in response_times]
        # Time per key should be relatively constant (not exponential)
        assert max(times) / min(times) < 2.0

    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not installed")
    def test_wait_key_cpu_usage(self):
        """Test CPU usage during wait_key operation."""
        from scitex.etc import wait_key
        import psutil
        
        # Get current process
        process = psutil.Process()
        
        # Measure baseline CPU
        process.cpu_percent(interval=0.1)
        baseline_cpu = process.cpu_percent(interval=0.1)
        
        mock_process = Mock()
        
        # Simulate waiting with periodic key presses
        def key_generator():
            for _ in range(50):
                time.sleep(0.01)  # Simulate realistic key press intervals
                yield 'x'
            yield 'q'
        
        # Measure CPU during wait_key
        cpu_samples = []
        
        def monitor_cpu():
            while len(cpu_samples) < 5:
                cpu_samples.append(process.cpu_percent(interval=0.1))
        
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=key_generator()):
            with patch('builtins.print'):
                wait_key(mock_process)
        
        monitor_thread.join()
        
        # CPU usage should be reasonable
        avg_cpu = statistics.mean(cpu_samples)
        assert avg_cpu < 50.0  # Should not use excessive CPU

    def test_count_performance_scaling(self, benchmark_results):
        """Test count function performance with different iteration counts."""
        from scitex.etc import count
        
        scaling_results = []
        
        for iterations in [100, 1000, 10000]:
            counter = 0
            
            def mock_print(value):
                nonlocal counter
                counter = value
                if counter >= iterations:
                    raise KeyboardInterrupt()
            
            start_time = time.perf_counter()
            
            with patch('scitex.etc.wait_key.time.sleep'):  # Remove sleep for perf test
                with patch('builtins.print', side_effect=mock_print):
                    try:
                        count()
                    except KeyboardInterrupt:
                        pass
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            scaling_results.append({
                'iterations': iterations,
                'duration': duration,
                'iterations_per_second': iterations / duration
            })
        
        benchmark_results['count']['scaling'] = scaling_results
        
        # Performance assertions
        for result in scaling_results:
            # Should handle at least 10000 iterations per second
            assert result['iterations_per_second'] > 10000
        
        # Check linear scaling
        rates = [r['iterations_per_second'] for r in scaling_results]
        # Rate should be relatively constant
        assert max(rates) / min(rates) < 2.0

    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not installed")
    def test_memory_usage_stability(self):
        """Test memory usage remains stable during extended operation."""
        from scitex.etc import wait_key, count
        import psutil
        
        process = psutil.Process()
        
        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run many iterations
        mock_process = Mock()
        keys = ['x'] * 10000 + ['q']
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=keys):
            with patch('builtins.print'):
                wait_key(mock_process)
        
        # Check memory after
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - baseline_memory
        
        # Memory growth should be minimal (less than 10MB)
        assert memory_growth < 10.0

    def test_concurrent_wait_key_performance(self):
        """Test performance with multiple concurrent wait_key instances."""
        from scitex.etc import wait_key
        
        num_threads = 10
        results = []
        
        def run_wait_key(thread_id):
            mock_process = Mock()
            mock_process.id = thread_id
            
            start_time = time.perf_counter()
            
            with patch('scitex.etc.wait_key.readchar.readchar', side_effect=['a', 'b', 'c', 'q']):
                with patch('builtins.print'):
                    wait_key(mock_process)
            
            end_time = time.perf_counter()
            results.append({
                'thread_id': thread_id,
                'duration': end_time - start_time
            })
        
        # Run concurrent threads
        threads = []
        start_time = time.perf_counter()
        
        for i in range(num_threads):
            t = threading.Thread(target=run_wait_key, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        total_time = time.perf_counter() - start_time
        
        # All threads should complete
        assert len(results) == num_threads
        
        # Total time should be much less than sum of individual times
        # (indicating parallelism)
        sum_individual = sum(r['duration'] for r in results)
        assert total_time < sum_individual * 0.5

    def test_input_latency(self):
        """Test input processing latency."""
        from scitex.etc import wait_key
        
        latencies = []
        
        class LatencyMeasuringReadchar:
            def __init__(self, keys):
                self.keys = keys
                self.index = 0
                self.call_times = []
            
            def readchar(self):
                self.call_times.append(time.perf_counter())
                if self.index < len(self.keys):
                    key = self.keys[self.index]
                    self.index += 1
                    return key
                return 'q'
        
        # Test with different key sequences
        for seq_length in [10, 50, 100]:
            keys = ['x'] * seq_length
            reader = LatencyMeasuringReadchar(keys)
            
            mock_process = Mock()
            
            with patch('scitex.etc.wait_key.readchar.readchar', side_effect=reader.readchar):
                with patch('builtins.print'):
                    wait_key(mock_process)
            
            # Calculate latencies between calls
            for i in range(1, len(reader.call_times)):
                latency = reader.call_times[i] - reader.call_times[i-1]
                latencies.append(latency)
        
        # Average latency should be very low
        avg_latency = statistics.mean(latencies)
        assert avg_latency < 0.001  # Less than 1ms

    def test_count_with_real_sleep_performance(self):
        """Test count performance with actual sleep delays."""
        from scitex.etc import count
        
        # Test with very short sleep
        iteration_times = []
        
        def mock_print(value):
            iteration_times.append(time.perf_counter())
            if len(iteration_times) >= 10:
                raise KeyboardInterrupt()
        
        with patch('scitex.etc.wait_key.time.sleep', lambda x: time.sleep(0.001)):  # 1ms sleep
            with patch('builtins.print', side_effect=mock_print):
                try:
                    count()
                except KeyboardInterrupt:
                    pass
        
        # Calculate actual intervals
        intervals = []
        for i in range(1, len(iteration_times)):
            intervals.append(iteration_times[i] - iteration_times[i-1])
        
        # Intervals should be close to sleep time
        avg_interval = statistics.mean(intervals)
        assert 0.0009 < avg_interval < 0.002  # Allow some variance

    def test_termination_speed(self):
        """Test how quickly termination occurs after 'q' press."""
        from scitex.etc import wait_key
        
        termination_times = []
        
        for _ in range(10):
            mock_process = Mock()
            
            # Time from 'q' press to termination
            q_press_time = None
            terminate_time = None
            
            def mock_readchar():
                nonlocal q_press_time
                q_press_time = time.perf_counter()
                return 'q'
            
            def mock_terminate():
                nonlocal terminate_time
                terminate_time = time.perf_counter()
            
            mock_process.terminate = mock_terminate
            
            with patch('scitex.etc.wait_key.readchar.readchar', side_effect=mock_readchar):
                with patch('builtins.print'):
                    wait_key(mock_process)
            
            if q_press_time and terminate_time:
                termination_times.append(terminate_time - q_press_time)
        
        # Termination should be near-instant
        avg_termination_time = statistics.mean(termination_times)
        assert avg_termination_time < 0.001  # Less than 1ms

    def test_scalability_limits(self):
        """Test behavior at scalability limits."""
        from scitex.etc import wait_key
        
        # Test with extremely long key sequence
        mock_process = Mock()
        
        # Generate 100k keys
        huge_key_sequence = ['x'] * 100000 + ['q']
        
        start_time = time.perf_counter()
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=huge_key_sequence):
            with patch('builtins.print'):
                wait_key(mock_process)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        # Should still complete in reasonable time
        assert duration < 10.0  # Less than 10 seconds for 100k keys
        
        # Calculate throughput
        keys_per_second = 100001 / duration
        assert keys_per_second > 10000  # At least 10k keys/second

    def generate_performance_report(self, benchmark_results):
        """Generate a performance report from benchmark results."""
        report = []
        report.append("=== ETC Module Performance Report ===\n")
        
        # Wait key performance
        if 'response_times' in benchmark_results['wait_key']:
            report.append("Wait Key Response Times:")
            for result in benchmark_results['wait_key']['response_times']:
                report.append(f"  {result['num_keys']} keys: "
                            f"{result['total_time']:.4f}s total, "
                            f"{result['time_per_key']*1000:.2f}ms per key")
        
        # Count scaling
        if 'scaling' in benchmark_results['count']:
            report.append("\nCount Function Scaling:")
            for result in benchmark_results['count']['scaling']:
                report.append(f"  {result['iterations']} iterations: "
                            f"{result['duration']:.4f}s, "
                            f"{result['iterations_per_second']:.0f} iter/sec")
        
        return '\n'.join(report)


if __name__ == "__main__":
    pytest.main([__FILE__, "-v", "-s"])