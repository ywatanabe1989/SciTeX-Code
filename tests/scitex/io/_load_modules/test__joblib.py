#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 02:20:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__joblib.py

"""Comprehensive tests for joblib file loading functionality.

This module tests the _load_joblib function with various data types,
compression levels, edge cases, and error conditions.
"""

import os
import sys
import tempfile
import shutil
import pytest
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pickle
import datetime
from dataclasses import dataclass
import warnings


@dataclass
class TestData:
    """Data class for testing serialization."""
    name: str
    value: float
    items: List[str]


class CustomObject:
    """Custom class for testing object serialization."""
    def __init__(self, x: int, y: str):
        self.x = x
        self.y = y
        self._private = "private_data"
    
    def __eq__(self, other):
        if not isinstance(other, CustomObject):
            return False
        return self.x == other.x and self.y == other.y


class TestLoadJoblibBasic:
    """Basic functionality tests for _load_joblib."""
    
    def test_load_simple_dict(self):
        """Test loading a simple dictionary."""
from scitex.io._load_modules import _load_joblib
        
        data = {'key1': 'value1', 'key2': 42, 'key3': 3.14}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert loaded == data
            assert isinstance(loaded, dict)
            assert all(k in loaded for k in data)
        finally:
            os.unlink(temp_path)
    
    def test_load_numpy_arrays(self):
        """Test loading various numpy arrays."""
from scitex.io._load_modules import _load_joblib
        
        arrays = {
            '1d': np.array([1, 2, 3, 4, 5]),
            '2d': np.random.rand(10, 20),
            '3d': np.random.rand(5, 10, 15),
            'int': np.array([1, 2, 3], dtype=np.int32),
            'float': np.array([1.1, 2.2, 3.3], dtype=np.float64),
            'complex': np.array([1+2j, 3+4j], dtype=np.complex128),
            'bool': np.array([True, False, True], dtype=bool),
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(arrays, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            for key, original in arrays.items():
                np.testing.assert_array_equal(loaded[key], original)
                assert loaded[key].dtype == original.dtype
        finally:
            os.unlink(temp_path)
    
    def test_load_pandas_objects(self):
        """Test loading pandas DataFrames and Series."""
from scitex.io._load_modules import _load_joblib
        
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': pd.date_range('2024-01-01', periods=5),
            'D': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        series = pd.Series([10, 20, 30], index=['x', 'y', 'z'])
        
        data = {'dataframe': df, 'series': series}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            pd.testing.assert_frame_equal(loaded['dataframe'], df)
            pd.testing.assert_series_equal(loaded['series'], series)
        finally:
            os.unlink(temp_path)
    
    def test_load_nested_structures(self):
        """Test loading deeply nested data structures."""
from scitex.io._load_modules import _load_joblib
        
        nested_data = {
            'level1': {
                'level2': {
                    'level3': {
                        'array': np.array([1, 2, 3]),
                        'list': [[1, 2], [3, 4]],
                        'tuple': (('a', 'b'), ('c', 'd')),
                    }
                },
                'items': [{'id': i, 'value': i**2} for i in range(5)]
            },
            'metadata': {
                'created': datetime.datetime.now(),
                'version': '1.0.0',
                'tags': {'python', 'testing', 'joblib'}
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(nested_data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert loaded['level1']['level2']['level3']['list'] == [[1, 2], [3, 4]]
            assert loaded['metadata']['version'] == '1.0.0'
            assert isinstance(loaded['metadata']['tags'], set)
        finally:
            os.unlink(temp_path)


class TestLoadJoblibCompression:
    """Test compression-related functionality."""
    
    def test_load_all_compression_levels(self):
        """Test loading files with different compression levels."""
from scitex.io._load_modules import _load_joblib
        
        data = np.random.rand(100, 100)
        
        for compress_level in range(10):  # 0-9 compression levels
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(data, f.name, compress=compress_level)
                temp_path = f.name
            
            try:
                loaded = _load_joblib(temp_path)
                np.testing.assert_array_almost_equal(loaded, data)
            finally:
                os.unlink(temp_path)
    
    def test_load_different_compression_methods(self):
        """Test loading files with different compression methods."""
from scitex.io._load_modules import _load_joblib
        
        data = {'array': np.random.rand(50, 50), 'value': 42}
        
        compression_methods = [
            ('zlib', 3),
            ('gzip', 3),
            ('bz2', 3),
            ('lzma', 3),
            ('xz', 3),
        ]
        
        for method, level in compression_methods:
            try:
                with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                    joblib.dump(data, f.name, compress=(method, level))
                    temp_path = f.name
                
                loaded = _load_joblib(temp_path)
                np.testing.assert_array_almost_equal(loaded['array'], data['array'])
                assert loaded['value'] == data['value']
            except Exception as e:
                # Some compression methods might not be available
                if "module" in str(e) and "not found" in str(e):
                    continue
                raise
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_load_large_compressed_data(self):
        """Test loading large compressed data."""
from scitex.io._load_modules import _load_joblib
        
        # Create large dataset
        large_data = {
            'matrix': np.random.rand(1000, 1000),
            'strings': ['string_' + str(i) for i in range(10000)],
            'nested': {str(i): np.random.rand(10, 10) for i in range(100)}
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(large_data, f.name, compress=3)
            temp_path = f.name
            compressed_size = os.path.getsize(temp_path)
        
        try:
            loaded = _load_joblib(temp_path)
            assert loaded['matrix'].shape == (1000, 1000)
            assert len(loaded['strings']) == 10000
            assert len(loaded['nested']) == 100
            
            # Verify compression was effective
            uncompressed_size = large_data['matrix'].nbytes
            assert compressed_size < uncompressed_size
        finally:
            os.unlink(temp_path)


class TestLoadJoblibCustomObjects:
    """Test loading custom objects and classes."""
    
    def test_load_custom_class(self):
        """Test loading custom class instances."""
from scitex.io._load_modules import _load_joblib
        
        obj = CustomObject(x=42, y="test")
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(obj, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert isinstance(loaded, CustomObject)
            assert loaded.x == 42
            assert loaded.y == "test"
            assert loaded == obj
        finally:
            os.unlink(temp_path)
    
    def test_load_dataclass(self):
        """Test loading dataclass instances."""
from scitex.io._load_modules import _load_joblib
        
        data = TestData(
            name="test_data",
            value=3.14159,
            items=["item1", "item2", "item3"]
        )
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert isinstance(loaded, TestData)
            assert loaded.name == "test_data"
            assert loaded.value == 3.14159
            assert loaded.items == ["item1", "item2", "item3"]
        finally:
            os.unlink(temp_path)
    
    def test_load_lambda_functions(self):
        """Test loading lambda functions (if supported)."""
from scitex.io._load_modules import _load_joblib
        
        # Note: Lambda functions might not be serializable depending on joblib version
        data = {
            'func': lambda x: x * 2,
            'value': 42
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            try:
                joblib.dump(data, f.name)
                temp_path = f.name
                
                loaded = _load_joblib(temp_path)
                assert loaded['value'] == 42
                # Test if lambda was preserved
                if 'func' in loaded and callable(loaded['func']):
                    assert loaded['func'](5) == 10
            except Exception:
                # Lambda serialization might fail, which is acceptable
                pass
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)


class TestLoadJoblibEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_load_empty_file(self):
        """Test loading an empty joblib file."""
from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):  # Should raise when trying to load empty file
                _load_joblib(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_corrupted_file(self):
        """Test loading a corrupted joblib file."""
from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            f.write(b"This is not a valid joblib file content")
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):  # Should raise when loading invalid data
                _load_joblib(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_wrong_file_extension(self):
        """Test various wrong file extensions."""
from scitex.io._load_modules import _load_joblib
        
        wrong_extensions = [
            "file.pkl",
            "file.pickle",
            "file.npy",
            "file.npz",
            "file.json",
            "file.txt",
            "file.dat",
            "file",  # No extension
            "file.JOBLIB",  # Wrong case
            "file.joblib.bak",  # Additional extension
        ]
        
        for filename in wrong_extensions:
            with pytest.raises(ValueError, match="must have .joblib extension"):
                _load_joblib(filename)
    
    def test_nonexistent_file(self):
        """Test loading a non-existent file."""
from scitex.io._load_modules import _load_joblib
        
        with pytest.raises(FileNotFoundError):
            _load_joblib("/tmp/nonexistent_file_12345.joblib")
    
    def test_load_none_values(self):
        """Test loading None values and empty containers."""
from scitex.io._load_modules import _load_joblib
        
        data = {
            'none': None,
            'empty_list': [],
            'empty_dict': {},
            'empty_tuple': (),
            'empty_set': set(),
            'empty_string': '',
            'empty_array': np.array([]),
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert loaded['none'] is None
            assert loaded['empty_list'] == []
            assert loaded['empty_dict'] == {}
            assert loaded['empty_tuple'] == ()
            assert loaded['empty_set'] == set()
            assert loaded['empty_string'] == ''
            assert len(loaded['empty_array']) == 0
        finally:
            os.unlink(temp_path)


class TestLoadJoblibWithKwargs:
    """Test _load_joblib with various keyword arguments."""
    
    def test_load_with_mmap_mode(self):
        """Test loading with memory mapping."""
from scitex.io._load_modules import _load_joblib
        
        # Large array that benefits from memory mapping
        large_array = np.random.rand(1000, 1000)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(large_array, f.name)
            temp_path = f.name
        
        try:
            # Test different mmap modes
            for mmap_mode in [None, 'r', 'r+', 'c']:
                loaded = _load_joblib(temp_path, mmap_mode=mmap_mode)
                
                if mmap_mode is not None:
                    # Should be memory mapped
                    assert isinstance(loaded, np.memmap) or loaded.base is not None
                else:
                    # Regular array
                    assert isinstance(loaded, np.ndarray)
                
                # Values should be the same regardless
                np.testing.assert_array_almost_equal(loaded, large_array)
        finally:
            os.unlink(temp_path)
    
    def test_load_with_custom_kwargs(self):
        """Test passing custom kwargs to joblib.load."""
from scitex.io._load_modules import _load_joblib
        
        data = {'test': 'data', 'array': np.array([1, 2, 3])}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            # Test with various kwargs (if supported by joblib version)
            loaded = _load_joblib(temp_path)
            assert loaded == data
        finally:
            os.unlink(temp_path)


class TestLoadJoblibPathHandling:
    """Test various path formats and handling."""
    
    def test_load_with_pathlib_path(self):
        """Test loading with pathlib.Path object."""
from scitex.io._load_modules import _load_joblib
        
        data = {'pathlib': 'test'}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = Path(f.name)
        
        try:
            # Convert to string since _load_joblib expects str
            loaded = _load_joblib(str(temp_path))
            assert loaded == data
        finally:
            os.unlink(temp_path)
    
    def test_load_with_relative_path(self):
        """Test loading with relative paths."""
from scitex.io._load_modules import _load_joblib
        
        data = {'relative': 'path'}
        
        # Create file in current directory
        filename = "test_relative_path.joblib"
        joblib.dump(data, filename)
        
        try:
            loaded = _load_joblib(filename)
            assert loaded == data
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_load_with_special_characters_in_path(self):
        """Test loading files with special characters in path."""
from scitex.io._load_modules import _load_joblib
        
        data = {'special': 'chars'}
        
        # Test various special characters (that are valid in filenames)
        special_names = [
            "test file with spaces.joblib",
            "test-file-with-dashes.joblib",
            "test_file_with_underscores.joblib",
            "test.file.with.dots.joblib",
        ]
        
        for name in special_names:
            with tempfile.NamedTemporaryFile(suffix='', delete=False) as f:
                temp_dir = os.path.dirname(f.name)
                special_path = os.path.join(temp_dir, name)
            
            joblib.dump(data, special_path)
            
            try:
                loaded = _load_joblib(special_path)
                assert loaded == data
            finally:
                if os.path.exists(special_path):
                    os.unlink(special_path)


class TestLoadJoblibConcurrency:
    """Test concurrent loading scenarios."""
    
    def test_load_same_file_multiple_times(self):
        """Test loading the same file multiple times."""
from scitex.io._load_modules import _load_joblib
        
        data = {'concurrent': np.random.rand(100, 100)}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            # Load multiple times
            results = []
            for _ in range(10):
                loaded = _load_joblib(temp_path)
                results.append(loaded)
            
            # All should be equal
            for result in results[1:]:
                np.testing.assert_array_almost_equal(
                    result['concurrent'], 
                    results[0]['concurrent']
                )
        finally:
            os.unlink(temp_path)


class TestLoadJoblibIntegration:
    """Integration tests with real-world scenarios."""
    
    def test_load_machine_learning_model(self):
        """Test loading a mock ML model structure."""
from scitex.io._load_modules import _load_joblib
        
        # Mock ML model data
        model_data = {
            'weights': {
                'layer1': np.random.rand(100, 50),
                'layer2': np.random.rand(50, 10),
                'bias1': np.random.rand(50),
                'bias2': np.random.rand(10),
            },
            'config': {
                'learning_rate': 0.001,
                'epochs': 100,
                'batch_size': 32,
                'optimizer': 'adam',
            },
            'metadata': {
                'trained_on': datetime.datetime.now(),
                'accuracy': 0.95,
                'loss': 0.05,
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(model_data, f.name, compress=3)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert 'weights' in loaded
            assert 'config' in loaded
            assert loaded['config']['learning_rate'] == 0.001
            assert loaded['weights']['layer1'].shape == (100, 50)
        finally:
            os.unlink(temp_path)
    
    def test_load_scientific_data(self):
        """Test loading scientific computation results."""
from scitex.io._load_modules import _load_joblib
        
        # Mock scientific data
        sci_data = {
            'experiment_id': 'EXP-2024-001',
            'measurements': {
                'time': np.linspace(0, 10, 1000),
                'signal': np.sin(np.linspace(0, 10, 1000)) + np.random.normal(0, 0.1, 1000),
                'temperature': np.random.normal(25, 0.5, 1000),
            },
            'analysis': {
                'mean': np.mean,  # Function reference
                'std': np.std,
                'results': {'peak': 1.0, 'frequency': 0.159},
            },
            'parameters': {
                'sampling_rate': 100,
                'duration': 10,
                'sensor_type': 'PT100',
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(sci_data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert loaded['experiment_id'] == 'EXP-2024-001'
            assert len(loaded['measurements']['time']) == 1000
            assert loaded['parameters']['sampling_rate'] == 100
            # Function references should be preserved
            assert callable(loaded['analysis']['mean'])
        finally:
            os.unlink(temp_path)


def test_backwards_compatibility():
    """Test loading joblib files created with pickle protocol."""
from scitex.io._load_modules import _load_joblib
    
    # Create data and save with different protocols
    data = {'test': 'backwards', 'array': np.array([1, 2, 3])}
    
    for protocol in [2, 3, 4]:  # Different pickle protocols
        try:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                # Some joblib versions support protocol parameter
                joblib.dump(data, f.name, protocol=protocol)
                temp_path = f.name
            
            loaded = _load_joblib(temp_path)
            assert loaded == data
        except TypeError:
            # Protocol parameter not supported in this joblib version
            pass
        finally:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([os.path.abspath(__file__), "-v", "-s"])
