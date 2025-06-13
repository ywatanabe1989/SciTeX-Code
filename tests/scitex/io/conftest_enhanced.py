#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 20:45:00"
# File: /tests/scitex/io/conftest_enhanced.py
# ----------------------------------------
"""
Enhanced shared fixtures and configuration for io module tests.

This file provides advanced testing fixtures following best practices:
- Reusable test data generation
- Mock objects for external dependencies
- Performance testing utilities
- Resource management helpers
"""

import os
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from unittest.mock import MagicMock
import time
from contextlib import contextmanager


# --- Directory and File Management Fixtures ---
@pytest.fixture
def temp_dir():
    """Provide a temporary directory that's automatically cleaned up."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup even if test fails
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir):
    """Provide a temporary file path (file not created)."""
    def _make_temp_file(suffix=''):
        return os.path.join(temp_dir, f'test_{time.time()}{suffix}')
    return _make_temp_file


@pytest.fixture
def mock_filesystem(tmp_path):
    """Provide a mock filesystem structure for testing."""
    # Create standard directory structure
    dirs = ['input', 'output', 'cache', 'logs']
    for dir_name in dirs:
        (tmp_path / dir_name).mkdir()
    
    # Create some test files
    (tmp_path / 'input' / 'data.csv').write_text('a,b,c\n1,2,3\n')
    (tmp_path / 'input' / 'config.json').write_text('{"key": "value"}')
    
    return tmp_path


# --- Test Data Fixtures ---
@pytest.fixture
def sample_arrays():
    """Provide various NumPy arrays for testing."""
    return {
        'small_1d': np.array([1, 2, 3, 4, 5]),
        'small_2d': np.array([[1, 2], [3, 4]]),
        'large_2d': np.random.rand(1000, 100),
        'empty': np.array([]),
        'single': np.array([42]),
        'float32': np.array([1.0, 2.0, 3.0], dtype=np.float32),
        'complex': np.array([1+2j, 3+4j, 5+6j]),
        'boolean': np.array([True, False, True, False]),
        'structured': np.array([(1, 2.0, 'a'), (3, 4.0, 'b')],
                              dtype=[('x', 'i4'), ('y', 'f4'), ('z', 'U1')])
    }


@pytest.fixture
def sample_dataframes():
    """Provide various pandas DataFrames for testing."""
    return {
        'simple': pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']}),
        'large': pd.DataFrame(np.random.rand(1000, 50)),
        'empty': pd.DataFrame(),
        'single_row': pd.DataFrame({'A': [1]}),
        'mixed_types': pd.DataFrame({
            'int': [1, 2, 3],
            'float': [1.1, 2.2, 3.3],
            'string': ['a', 'b', 'c'],
            'datetime': pd.date_range('2020-01-01', periods=3),
            'category': pd.Categorical(['cat1', 'cat2', 'cat1']),
            'boolean': [True, False, True]
        }),
        'with_nan': pd.DataFrame({
            'A': [1, np.nan, 3],
            'B': ['a', 'b', None]
        }),
        'multi_index': pd.DataFrame(
            np.random.rand(6, 3),
            index=pd.MultiIndex.from_product([['A', 'B'], [1, 2, 3]]),
            columns=['X', 'Y', 'Z']
        )
    }


@pytest.fixture
def sample_dicts():
    """Provide various dictionaries for testing."""
    return {
        'simple': {'key': 'value', 'number': 42},
        'nested': {
            'level1': {
                'level2': {
                    'level3': {'data': [1, 2, 3]}
                }
            }
        },
        'mixed': {
            'string': 'hello',
            'int': 42,
            'float': 3.14,
            'list': [1, 2, 3],
            'dict': {'nested': True},
            'none': None
        },
        'empty': {},
        'unicode': {'key': 'value with émojis 🎉'},
        'special_keys': {
            'key with spaces': 'value1',
            'key-with-dashes': 'value2',
            'key.with.dots': 'value3'
        }
    }


@pytest.fixture
def sample_models():
    """Provide various model objects for testing."""
    class SimpleModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(10, 5)
    
    return {
        'tensor': torch.tensor([1, 2, 3]),
        'model': SimpleModel(),
        'state_dict': {'weights': torch.randn(10, 5), 'bias': torch.randn(5)},
        'optimizer_state': {
            'state': {},
            'param_groups': [{'lr': 0.01, 'momentum': 0.9}]
        }
    }


# --- File Format Fixtures ---
@pytest.fixture(params=[
    'npy', 'npz', 'csv', 'json', 'yaml', 'pkl', 'pth', 'txt', 'h5', 'mat'
])
def file_extension(request):
    """Parametrized fixture providing various file extensions."""
    return f'.{request.param}'


@pytest.fixture
def format_data_pairs():
    """Provide compatible data-format pairs for testing."""
    return [
        (np.array([1, 2, 3]), '.npy'),
        ({'a': np.array([1, 2])}, '.npz'),
        (pd.DataFrame({'A': [1, 2]}), '.csv'),
        ({'key': 'value'}, '.json'),
        ({'config': True}, '.yaml'),
        (['mixed', 123, {'nested': True}], '.pkl'),
        (torch.tensor([1, 2, 3]), '.pth'),
        ('Hello\nWorld', '.txt'),
    ]


# --- Mock Objects ---
@pytest.fixture
def mock_torch_save():
    """Mock torch.save for unit testing."""
    with pytest.mock.patch('torch.save') as mock:
        yield mock


@pytest.fixture
def mock_file_io():
    """Mock file I/O operations."""
    mock_open = pytest.mock.mock_open()
    with pytest.mock.patch('builtins.open', mock_open):
        yield mock_open


@pytest.fixture
def mock_os_operations():
    """Mock OS-level operations."""
    with pytest.mock.patch('os.makedirs') as mock_makedirs:
        with pytest.mock.patch('os.path.exists', return_value=True) as mock_exists:
            with pytest.mock.patch('os.chmod') as mock_chmod:
                yield {
                    'makedirs': mock_makedirs,
                    'exists': mock_exists,
                    'chmod': mock_chmod
                }


# --- Performance Testing Fixtures ---
@pytest.fixture
def benchmark_data():
    """Provide data for benchmarking tests."""
    return {
        'small': np.random.rand(10, 10),
        'medium': np.random.rand(100, 100),
        'large': np.random.rand(1000, 1000),
        'xlarge': np.random.rand(5000, 1000)
    }


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    @contextmanager
    def _monitor():
        import psutil
        import gc
        
        # Force garbage collection before test
        gc.collect()
        
        # Get initial metrics
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        metrics = {}
        yield metrics
        
        # Get final metrics
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Store metrics
        metrics['duration'] = end_time - start_time
        metrics['memory_used'] = end_memory - start_memory
        metrics['start_memory'] = start_memory
        metrics['end_memory'] = end_memory
    
    return _monitor


# --- Error Injection Fixtures ---
@pytest.fixture
def error_scenarios():
    """Provide various error scenarios for testing."""
    return {
        'disk_full': IOError("No space left on device"),
        'permission_denied': PermissionError("Permission denied"),
        'file_not_found': FileNotFoundError("No such file or directory"),
        'network_error': ConnectionError("Network is unreachable"),
        'timeout': TimeoutError("Operation timed out"),
        'memory_error': MemoryError("Unable to allocate memory"),
        'corrupt_data': ValueError("Invalid data format")
    }


@pytest.fixture
def inject_error():
    """Factory for injecting errors at specific points."""
    def _inject(target, error, when='call'):
        if when == 'call':
            target.side_effect = error
        elif when == 'first_call':
            target.side_effect = [error] + [target.return_value] * 10
        elif when == 'after_n_calls':
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count > n:
                    raise error
                return target.return_value
            call_count = 0
            n = 3
            target.side_effect = side_effect
    
    return _inject


# --- Test Markers ---
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests requiring GPU"
    )
    config.addinivalue_line(
        "markers", "network: marks tests requiring network access"
    )


# --- Hypothesis Strategies ---
try:
    from hypothesis import strategies as st
    
    # Custom strategy for file paths
    file_path_strategy = st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), 
                              whitelist_characters='_-./ '),
        min_size=1,
        max_size=50
    ).filter(lambda x: not x.startswith('/') and '..' not in x)
    
    # Custom strategy for valid DataFrames
    dataframe_strategy = st.builds(
        pd.DataFrame,
        st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.lists(st.one_of(
                st.integers(),
                st.floats(allow_nan=False),
                st.text()
            ), min_size=1, max_size=100),
            min_size=1,
            max_size=10
        )
    )
    
except ImportError:
    pass  # Hypothesis not installed


# --- Utility Functions ---
def assert_files_equal(file1, file2, format='binary'):
    """Assert two files have identical content."""
    if format == 'binary':
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            assert f1.read() == f2.read()
    else:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            assert f1.read() == f2.read()


def create_large_file(path, size_mb):
    """Create a file of specified size for testing."""
    with open(path, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))


# --- Cleanup ---
@pytest.fixture(autouse=True)
def cleanup_test_files(request):
    """Automatically cleanup any test files created."""
    test_files = []
    
    def register_cleanup(path):
        test_files.append(path)
    
    request.addfinalizer(lambda: [
        os.unlink(f) for f in test_files if os.path.exists(f)
    ])
    
    return register_cleanup


# EOF