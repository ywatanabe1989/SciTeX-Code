#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:40:00"
# File: monitor.py

"""
Real-time performance monitoring for SciTeX.
"""

import time
import threading
from collections import deque, defaultdict
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import warnings


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    timestamp: float
    function: str
    duration: float
    memory_delta: Optional[float] = None
    args_size: Optional[int] = None
    result_size: Optional[int] = None
    exception: Optional[str] = None


class PerformanceMonitor:
    """
    Monitor performance metrics for SciTeX functions.
    
    Example
    -------
    >>> monitor = PerformanceMonitor()
    >>> monitor.start()
    >>> # Your code here
    >>> stats = monitor.get_stats()
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = deque(maxlen=max_history)
        self.function_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0
        })
        self.is_monitoring = False
        self._lock = threading.Lock()
        
        # Alerts configuration
        self.alerts = {
            'slow_function': 1.0,  # Alert if function takes > 1s
            'memory_spike': 100,   # Alert if memory increases > 100MB
            'error_rate': 0.1      # Alert if error rate > 10%
        }
        self.alert_callbacks = []
    
    def start(self):
        """Start monitoring."""
        self.is_monitoring = True
    
    def stop(self):
        """Stop monitoring."""
        self.is_monitoring = False
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric."""
        if not self.is_monitoring:
            return
        
        with self._lock:
            self.metrics.append(metric)
            
            # Update function statistics
            stats = self.function_stats[metric.function]
            stats['count'] += 1
            stats['total_time'] += metric.duration
            stats['min_time'] = min(stats['min_time'], metric.duration)
            stats['max_time'] = max(stats['max_time'], metric.duration)
            
            if metric.exception:
                stats['errors'] += 1
            
            # Check alerts
            self._check_alerts(metric)
    
    def _check_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts."""
        alerts_triggered = []
        
        # Slow function alert
        if metric.duration > self.alerts['slow_function']:
            alerts_triggered.append({
                'type': 'slow_function',
                'function': metric.function,
                'duration': metric.duration,
                'threshold': self.alerts['slow_function']
            })
        
        # Memory spike alert
        if metric.memory_delta and metric.memory_delta > self.alerts['memory_spike']:
            alerts_triggered.append({
                'type': 'memory_spike',
                'function': metric.function,
                'delta': metric.memory_delta,
                'threshold': self.alerts['memory_spike']
            })
        
        # Error rate alert
        stats = self.function_stats[metric.function]
        if stats['count'] > 10:  # Only check after sufficient calls
            error_rate = stats['errors'] / stats['count']
            if error_rate > self.alerts['error_rate']:
                alerts_triggered.append({
                    'type': 'high_error_rate',
                    'function': metric.function,
                    'rate': error_rate,
                    'threshold': self.alerts['error_rate']
                })
        
        # Trigger callbacks
        for alert in alerts_triggered:
            for callback in self.alert_callbacks:
                callback(alert)
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def get_stats(self, function: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Parameters
        ----------
        function : str, optional
            Specific function to get stats for
            
        Returns
        -------
        dict
            Performance statistics
        """
        with self._lock:
            if function:
                stats = self.function_stats.get(function, {})
                if stats and stats['count'] > 0:
                    return {
                        'function': function,
                        'count': stats['count'],
                        'total_time': stats['total_time'],
                        'avg_time': stats['total_time'] / stats['count'],
                        'min_time': stats['min_time'],
                        'max_time': stats['max_time'],
                        'error_rate': stats['errors'] / stats['count']
                    }
                return {}
            else:
                # Return all stats
                all_stats = {}
                for func, stats in self.function_stats.items():
                    if stats['count'] > 0:
                        all_stats[func] = {
                            'count': stats['count'],
                            'avg_time': stats['total_time'] / stats['count'],
                            'min_time': stats['min_time'],
                            'max_time': stats['max_time'],
                            'error_rate': stats['errors'] / stats['count']
                        }
                return all_stats
    
    def get_recent_metrics(self, n: int = 100) -> List[PerformanceMetric]:
        """Get n most recent metrics."""
        with self._lock:
            return list(self.metrics)[-n:]
    
    def save_metrics(self, path: str):
        """Save metrics to file."""
        with self._lock:
            data = {
                'metrics': [
                    {
                        'timestamp': m.timestamp,
                        'function': m.function,
                        'duration': m.duration,
                        'memory_delta': m.memory_delta,
                        'args_size': m.args_size,
                        'result_size': m.result_size,
                        'exception': m.exception
                    }
                    for m in self.metrics
                ],
                'stats': dict(self.function_stats)
            }
        
        Path(path).write_text(json.dumps(data, indent=2))
    
    def load_metrics(self, path: str):
        """Load metrics from file."""
        data = json.loads(Path(path).read_text())
        
        with self._lock:
            self.metrics.clear()
            for m in data['metrics']:
                self.metrics.append(PerformanceMetric(**m))
            
            self.function_stats.clear()
            self.function_stats.update(data['stats'])
    
    def clear(self):
        """Clear all metrics."""
        with self._lock:
            self.metrics.clear()
            self.function_stats.clear()


# Global monitor instance
_global_monitor = PerformanceMonitor()


def track_performance(func: Callable) -> Callable:
    """
    Decorator to track function performance.
    
    Example
    -------
    >>> @track_performance
    ... def my_function(x):
    ...     return x ** 2
    """
    from functools import wraps
    import sys
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _global_monitor.is_monitoring:
            return func(*args, **kwargs)
        
        # Get memory before (if available)
        try:
            import psutil
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024
        except:
            mem_before = None
        
        # Time the function
        start_time = time.time()
        exception = None
        result = None
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            exception = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            # Get memory after
            mem_delta = None
            if mem_before is not None:
                try:
                    mem_after = process.memory_info().rss / 1024 / 1024
                    mem_delta = mem_after - mem_before
                except:
                    pass
            
            # Estimate sizes
            args_size = None
            result_size = None
            try:
                args_size = sys.getsizeof(args) + sys.getsizeof(kwargs)
                if result is not None:
                    result_size = sys.getsizeof(result)
            except:
                pass
            
            # Record metric
            metric = PerformanceMetric(
                timestamp=start_time,
                function=func.__name__,
                duration=duration,
                memory_delta=mem_delta,
                args_size=args_size,
                result_size=result_size,
                exception=exception
            )
            
            _global_monitor.record_metric(metric)
        
        return result
    
    return wrapper


def start_monitoring():
    """Start global performance monitoring."""
    _global_monitor.start()


def stop_monitoring():
    """Stop global performance monitoring."""
    _global_monitor.stop()


def get_performance_stats(function: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics from global monitor."""
    return _global_monitor.get_stats(function)


def set_performance_alerts(**thresholds):
    """
    Set performance alert thresholds.
    
    Parameters
    ----------
    slow_function : float
        Alert if function takes longer than this (seconds)
    memory_spike : float
        Alert if memory increases by more than this (MB)
    error_rate : float
        Alert if error rate exceeds this (0-1)
    """
    _global_monitor.alerts.update(thresholds)


def add_performance_alert_handler(handler: Callable[[Dict[str, Any]], None]):
    """
    Add a handler for performance alerts.
    
    Example
    -------
    >>> def alert_handler(alert):
    ...     print(f"ALERT: {alert['type']} in {alert['function']}")
    >>> add_performance_alert_handler(alert_handler)
    """
    _global_monitor.add_alert_callback(handler)


# Default alert handler
def _default_alert_handler(alert: Dict[str, Any]):
    """Default handler that prints warnings."""
    if alert['type'] == 'slow_function':
        warnings.warn(
            f"Slow function: {alert['function']} took {alert['duration']:.2f}s "
            f"(threshold: {alert['threshold']}s)"
        )
    elif alert['type'] == 'memory_spike':
        warnings.warn(
            f"Memory spike: {alert['function']} increased memory by {alert['delta']:.1f}MB "
            f"(threshold: {alert['threshold']}MB)"
        )
    elif alert['type'] == 'high_error_rate':
        warnings.warn(
            f"High error rate: {alert['function']} has {alert['rate']:.1%} error rate "
            f"(threshold: {alert['threshold']:.1%})"
        )


# Register default handler
add_performance_alert_handler(_default_alert_handler)