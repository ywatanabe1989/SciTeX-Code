#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/conftest_enhanced.py
# ----------------------------------------
"""
Enhanced pytest fixtures for scitex.plt.ax module testing.

This file provides comprehensive fixtures for testing plotting functions,
including sample data, figure management, performance monitoring, and
integration helpers.
"""

import os
import shutil
import tempfile
import time
import tracemalloc
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from hypothesis import strategies as st


# ----------------------------------------
# Configuration
# ----------------------------------------

# Set non-interactive backend for testing
matplotlib.use('Agg')

# Ensure reproducibility
np.random.seed(42)


# ----------------------------------------
# Data Generation Fixtures
# ----------------------------------------

@pytest.fixture
def sample_1d_data():
    """Provide various 1D data arrays for testing."""
    return {
        'simple': np.array([1, 2, 3, 4, 5]),
        'large': np.random.randn(1000),
        'periodic': np.sin(np.linspace(0, 4*np.pi, 100)),
        'noisy': np.random.randn(100) + np.linspace(0, 10, 100),
        'categorical': np.array(['A', 'B', 'C', 'A', 'B', 'C']),
        'with_nans': np.array([1, 2, np.nan, 4, 5]),
        'with_infs': np.array([1, np.inf, 3, -np.inf, 5]),
        'empty': np.array([]),
        'single': np.array([42]),
        'binary': np.array([0, 1, 0, 1, 1, 0]),
        'sorted': np.arange(50),
        'reversed': np.arange(50)[::-1],
    }


@pytest.fixture
def sample_2d_data():
    """Provide various 2D data arrays for testing."""
    return {
        'small': np.array([[1, 2], [3, 4]]),
        'medium': np.random.randn(10, 10),
        'large': np.random.randn(100, 100),
        'correlation': np.corrcoef(np.random.randn(5, 20)),
        'confusion_matrix': np.array([[85, 15], [10, 90]]),
        'heatmap': np.random.rand(20, 30),
        'image': np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8),
        'sparse': np.zeros((50, 50)),
        'diagonal': np.diag(np.arange(10)),
        'symmetric': lambda: (lambda x: x + x.T)(np.random.randn(10, 10)),
        'with_pattern': np.outer(np.sin(np.linspace(0, np.pi, 50)), 
                                np.cos(np.linspace(0, np.pi, 50))),
    }


@pytest.fixture
def sample_3d_data():
    """Provide various 3D data arrays for testing."""
    return {
        'simple': np.random.randn(5, 10, 15),
        'image_stack': np.random.randint(0, 255, (10, 64, 64), dtype=np.uint8),
        'time_series': np.random.randn(100, 5, 3),  # time x channels x features
        'volume': np.random.rand(20, 20, 20),
    }


@pytest.fixture
def sample_time_series():
    """Provide time series data for testing."""
    n_points = 1000
    t = np.linspace(0, 10, n_points)
    
    return {
        'time': t,
        'sine': np.sin(2 * np.pi * t),
        'cosine': np.cos(2 * np.pi * t),
        'noisy_sine': np.sin(2 * np.pi * t) + 0.1 * np.random.randn(n_points),
        'multi_freq': (np.sin(2 * np.pi * t) + 
                      0.5 * np.sin(10 * np.pi * t) + 
                      0.2 * np.sin(50 * np.pi * t)),
        'trend': t + 0.5 * np.random.randn(n_points),
        'seasonal': np.sin(2 * np.pi * t) + 0.1 * t,
        'multiple': np.column_stack([
            np.sin(2 * np.pi * t),
            np.cos(2 * np.pi * t),
            np.sin(4 * np.pi * t)
        ]),
    }


@pytest.fixture
def sample_statistical_data():
    """Provide statistical data for testing."""
    n_samples = 100
    
    return {
        'normal': np.random.normal(0, 1, n_samples),
        'uniform': np.random.uniform(-1, 1, n_samples),
        'exponential': np.random.exponential(1, n_samples),
        'bimodal': np.concatenate([
            np.random.normal(-2, 0.5, n_samples//2),
            np.random.normal(2, 0.5, n_samples//2)
        ]),
        'outliers': np.concatenate([
            np.random.normal(0, 1, int(n_samples * 0.95)),
            np.random.normal(0, 10, int(n_samples * 0.05))
        ]),
        'groups': {
            'A': np.random.normal(0, 1, n_samples),
            'B': np.random.normal(1, 1.5, n_samples),
            'C': np.random.normal(-0.5, 0.8, n_samples),
        },
        'paired': np.column_stack([
            np.random.normal(0, 1, n_samples),
            np.random.normal(0, 1, n_samples) + 0.5
        ]),
    }


@pytest.fixture
def sample_dataframes():
    """Provide pandas DataFrames for testing."""
    n_rows = 50
    
    return {
        'simple': pd.DataFrame({
            'x': np.arange(n_rows),
            'y': np.random.randn(n_rows),
        }),
        'multivariate': pd.DataFrame({
            'A': np.random.randn(n_rows),
            'B': np.random.randn(n_rows),
            'C': np.random.randn(n_rows),
            'category': np.random.choice(['X', 'Y', 'Z'], n_rows),
        }),
        'time_series': pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='H'),
            'value': np.cumsum(np.random.randn(n_rows)),
            'volume': np.random.randint(0, 100, n_rows),
        }),
        'wide': pd.DataFrame(
            np.random.randn(20, 100),
            columns=[f'feature_{i}' for i in range(100)]
        ),
    }


# ----------------------------------------
# Figure Management Fixtures
# ----------------------------------------

@pytest.fixture
def fig_ax():
    """Create a single figure and axes, cleaned up after test."""
    fig, ax = plt.subplots(figsize=(8, 6))
    yield fig, ax
    plt.close(fig)


@pytest.fixture
def multi_axes():
    """Create multiple axes configurations."""
    configs = {
        '2x2': plt.subplots(2, 2, figsize=(10, 8)),
        '3x1': plt.subplots(3, 1, figsize=(8, 10)),
        '1x3': plt.subplots(1, 3, figsize=(12, 4)),
        'mixed': plt.subplots(2, 3, figsize=(12, 8)),
    }
    
    yield configs
    
    # Cleanup
    for fig, axes in configs.values():
        plt.close(fig)


@pytest.fixture
def fig_3d():
    """Create a 3D axes for testing."""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    yield fig, ax
    plt.close(fig)


@pytest.fixture
def clean_figure():
    """Ensure all figures are closed before and after test."""
    plt.close('all')
    yield
    plt.close('all')


# ----------------------------------------
# Style and Appearance Fixtures
# ----------------------------------------

@pytest.fixture
def color_palettes():
    """Provide various color palettes for testing."""
    return {
        'basic': ['red', 'green', 'blue'],
        'mpl_cycle': plt.rcParams['axes.prop_cycle'].by_key()['color'],
        'seaborn': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'grayscale': ['#000000', '#404040', '#808080', '#bfbfbf', '#ffffff'],
        'rainbow': plt.cm.rainbow(np.linspace(0, 1, 7)),
        'diverging': plt.cm.RdBu(np.linspace(0, 1, 11)),
        'sequential': plt.cm.viridis(np.linspace(0, 1, 9)),
    }


@pytest.fixture
def line_styles():
    """Provide various line styles for testing."""
    return {
        'solid': '-',
        'dashed': '--',
        'dotted': ':',
        'dashdot': '-.',
        'custom': (0, (5, 2, 1, 2)),  # Custom dash pattern
    }


@pytest.fixture
def marker_styles():
    """Provide various marker styles for testing."""
    return ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x']


# ----------------------------------------
# Mock and Patch Fixtures
# ----------------------------------------

@pytest.fixture
def mock_save():
    """Mock the scitex.io.save function."""
    with patch('scitex.io.save') as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def mock_plt_show():
    """Mock plt.show to prevent display during tests."""
    with patch('matplotlib.pyplot.show') as mock:
        yield mock


@pytest.fixture
def mock_file_system(tmp_path):
    """Create a mock file system with test files."""
    # Create directory structure
    (tmp_path / 'data').mkdir()
    (tmp_path / 'figures').mkdir()
    (tmp_path / 'results').mkdir()
    
    # Create some test files
    (tmp_path / 'data' / 'test.csv').write_text('x,y\n1,2\n3,4\n')
    (tmp_path / 'data' / 'test.npy').touch()
    
    yield tmp_path


# ----------------------------------------
# Performance Monitoring Fixtures
# ----------------------------------------

@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            
        @contextmanager
        def measure(self, name):
            start_time = time.time()
            tracemalloc.start()
            start_memory = tracemalloc.get_traced_memory()[0]
            
            yield
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            self.metrics[name] = {
                'duration': time.time() - start_time,
                'memory_used': current - start_memory,
                'memory_peak': peak,
            }
            
        def get_metrics(self):
            return self.metrics
            
        def assert_performance(self, name, max_duration=None, max_memory=None):
            """Assert performance constraints."""
            if name not in self.metrics:
                raise ValueError(f"No metrics recorded for '{name}'")
                
            metrics = self.metrics[name]
            if max_duration and metrics['duration'] > max_duration:
                raise AssertionError(
                    f"{name} took {metrics['duration']:.3f}s, "
                    f"expected < {max_duration}s"
                )
            if max_memory and metrics['memory_used'] > max_memory:
                raise AssertionError(
                    f"{name} used {metrics['memory_used']/1e6:.1f}MB, "
                    f"expected < {max_memory/1e6:.1f}MB"
                )
    
    return PerformanceMonitor()


# ----------------------------------------
# Hypothesis Strategies
# ----------------------------------------

@pytest.fixture
def hypothesis_strategies():
    """Provide common Hypothesis strategies for property testing."""
    return {
        'colors': st.sampled_from(['red', 'blue', 'green', 'black', '#FF0000']),
        'line_widths': st.floats(min_value=0.1, max_value=10.0),
        'alpha_values': st.floats(min_value=0.0, max_value=1.0),
        'fontsize': st.integers(min_value=6, max_value=24),
        'figure_size': st.tuples(
            st.integers(min_value=4, max_value=20),
            st.integers(min_value=3, max_value=15)
        ),
        'data_size': st.integers(min_value=10, max_value=1000),
        'labels': st.text(min_size=1, max_size=20),
    }


# ----------------------------------------
# Assertion Helpers
# ----------------------------------------

@pytest.fixture
def plot_assertions():
    """Provide common assertion helpers for plots."""
    class PlotAssertions:
        @staticmethod
        def assert_axes_limits(ax, xlim=None, ylim=None, tolerance=1e-6):
            """Assert axes limits are as expected."""
            if xlim:
                actual_xlim = ax.get_xlim()
                assert abs(actual_xlim[0] - xlim[0]) < tolerance
                assert abs(actual_xlim[1] - xlim[1]) < tolerance
            if ylim:
                actual_ylim = ax.get_ylim()
                assert abs(actual_ylim[0] - ylim[0]) < tolerance
                assert abs(actual_ylim[1] - ylim[1]) < tolerance
                
        @staticmethod
        def assert_labels(ax, xlabel=None, ylabel=None, title=None):
            """Assert axes labels are as expected."""
            if xlabel is not None:
                assert ax.get_xlabel() == xlabel
            if ylabel is not None:
                assert ax.get_ylabel() == ylabel
            if title is not None:
                assert ax.get_title() == title
                
        @staticmethod
        def assert_legend_exists(ax, n_entries=None):
            """Assert legend exists and has expected entries."""
            legend = ax.get_legend()
            assert legend is not None
            if n_entries is not None:
                assert len(legend.get_texts()) == n_entries
                
        @staticmethod
        def assert_n_lines(ax, n_lines):
            """Assert number of lines in plot."""
            lines = ax.get_lines()
            assert len(lines) == n_lines
            
        @staticmethod
        def assert_colorbar_exists(fig):
            """Assert figure has a colorbar."""
            # Check if any axes is a colorbar
            for ax in fig.get_axes():
                if hasattr(ax, 'colorbar') or ax.__class__.__name__ == 'Colorbar':
                    return True
            raise AssertionError("No colorbar found in figure")
    
    return PlotAssertions()


# ----------------------------------------
# Temporary Directory Management
# ----------------------------------------

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    
    yield output_dir
    
    # Optional: Keep outputs for debugging by setting env var
    if not os.environ.get('KEEP_TEST_OUTPUTS'):
        shutil.rmtree(output_dir)


# ----------------------------------------
# Integration Helpers
# ----------------------------------------

@pytest.fixture
def scitex_modules():
    """Import and provide access to scitex modules if available."""
    modules = {}
    
    try:
        import scitex
        modules['scitex'] = scitex
    except ImportError:
        pass
        
    try:
        import scitex.plt
        modules['plt'] = scitex.plt
    except ImportError:
        pass
        
    try:
        import scitex.io
        modules['io'] = scitex.io
    except ImportError:
        pass
    
    return modules


# ----------------------------------------
# Cleanup and Safety
# ----------------------------------------

@pytest.fixture(autouse=True)
def cleanup_matplotlib():
    """Automatically cleanup matplotlib state after each test."""
    yield
    plt.close('all')
    # Reset any modified rcParams
    matplotlib.rcdefaults()


if __name__ == "__main__":
    print("This is a pytest conftest file and should not be run directly.")
    print("Fixtures provided:")
    print("- sample_1d_data: Various 1D arrays")
    print("- sample_2d_data: Various 2D arrays")
    print("- sample_3d_data: Various 3D arrays")
    print("- sample_time_series: Time series data")
    print("- sample_statistical_data: Statistical distributions")
    print("- sample_dataframes: Pandas DataFrames")
    print("- fig_ax: Single figure/axes pair")
    print("- multi_axes: Multiple axes configurations")
    print("- performance_monitor: Performance measurement")
    print("- plot_assertions: Common plot assertions")
    print("... and many more!")