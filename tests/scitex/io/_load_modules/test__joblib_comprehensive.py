#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:06:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__joblib_comprehensive.py

"""Comprehensive tests for joblib file loading functionality."""

import os
import tempfile
import pytest
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
import pickle
import gzip
import warnings


class TestLoadJoblibBasic:
    """Test basic joblib loading functionality."""
    
    def test_load_simple_objects(self):
        """Test loading various simple Python objects."""
        from scitex.io._load_modules import _load_joblib
        
        test_objects = [
            42,
            3.14159,
            "hello world",
            True,
            None,
            [1, 2, 3],
            {"a": 1, "b": 2},
            {1, 2, 3},
            (1, 2, 3)
        ]
        
        for obj in test_objects:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(obj, f.name)
                temp_path = f.name
            
            try:
                loaded = _load_joblib(temp_path)
                assert loaded == obj
            finally:
                os.unlink(temp_path)
    
    def test_load_numpy_arrays(self):
        """Test loading various numpy array types."""
        from scitex.io._load_modules import _load_joblib
        
        arrays = [
            np.array([1, 2, 3]),
            np.array([[1, 2], [3, 4]]),
            np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]),
            np.array([1.0, 2.0, 3.0]),
            np.array([True, False, True]),
            np.array(['a', 'b', 'c']),
            np.array([1 + 2j, 3 + 4j])
        ]
        
        for arr in arrays:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(arr, f.name)
                temp_path = f.name
            
            try:
                loaded = _load_joblib(temp_path)
                np.testing.assert_array_equal(loaded, arr)
            finally:
                os.unlink(temp_path)
    
    def test_load_pandas_objects(self):
        """Test loading pandas DataFrames and Series."""
        from scitex.io._load_modules import _load_joblib
        
        # Create test DataFrame
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c'],
            'C': [1.1, 2.2, 3.3]
        })
        
        # Create test Series
        series = pd.Series([1, 2, 3], name='test_series')
        
        for obj in [df, series]:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(obj, f.name)
                temp_path = f.name
            
            try:
                loaded = _load_joblib(temp_path)
                if isinstance(obj, pd.DataFrame):
                    pd.testing.assert_frame_equal(loaded, obj)
                else:
                    pd.testing.assert_series_equal(loaded, obj)
            finally:
                os.unlink(temp_path)
    
    def test_load_nested_structures(self):
        """Test loading complex nested data structures."""
        from scitex.io._load_modules import _load_joblib
        
        complex_data = {
            'arrays': {
                '1d': np.array([1, 2, 3]),
                '2d': np.array([[1, 2], [3, 4]]),
                '3d': np.random.rand(2, 3, 4)
            },
            'lists': [[1, 2], [3, [4, 5]]],
            'mixed': {
                'df': pd.DataFrame({'A': [1, 2, 3]}),
                'array': np.array([1.0, 2.0]),
                'scalar': 42
            },
            'metadata': {
                'version': '1.0',
                'created': '2025-06-10',
                'params': {'alpha': 0.1, 'beta': 0.9}
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(complex_data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            
            # Verify structure
            assert 'arrays' in loaded
            assert 'lists' in loaded
            assert 'mixed' in loaded
            assert 'metadata' in loaded
            
            # Verify nested content
            np.testing.assert_array_equal(loaded['arrays']['1d'], complex_data['arrays']['1d'])
            pd.testing.assert_frame_equal(loaded['mixed']['df'], complex_data['mixed']['df'])
            assert loaded['metadata']['params']['alpha'] == 0.1
        finally:
            os.unlink(temp_path)


class TestLoadJoblibCompression:
    """Test joblib compression features."""
    
    def test_compression_levels(self):
        """Test different compression levels."""
        from scitex.io._load_modules import _load_joblib
        
        # Large data for compression testing
        large_data = np.random.rand(1000, 1000)
        
        compression_levels = [0, 1, 3, 6, 9]
        
        for level in compression_levels:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(large_data, f.name, compress=level)
                temp_path = f.name
            
            try:
                loaded = _load_joblib(temp_path)
                np.testing.assert_array_almost_equal(loaded, large_data)
            finally:
                os.unlink(temp_path)
    
    def test_compression_methods(self):
        """Test different compression methods."""
        from scitex.io._load_modules import _load_joblib
        
        data = np.random.rand(100, 100)
        
        # Different compression formats
        compression_methods = [
            ('zlib', 3),
            ('gzip', 3),
            ('bz2', 3),
            ('lzma', 3),
            ('xz', 3)
        ]
        
        for method, level in compression_methods:
            try:
                with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                    joblib.dump(data, f.name, compress=(method, level))
                    temp_path = f.name
                
                loaded = _load_joblib(temp_path)
                np.testing.assert_array_almost_equal(loaded, data)
            except Exception as e:
                # Some compression methods might not be available
                if "module" in str(e).lower():
                    pytest.skip(f"Compression method {method} not available")
                else:
                    raise
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


class TestLoadJoblibPaths:
    """Test different path types and formats."""
    
    def test_pathlib_path(self):
        """Test loading with pathlib.Path object."""
        from scitex.io._load_modules import _load_joblib
        
        data = {"test": "data"}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = Path(f.name)
        
        try:
            loaded = _load_joblib(temp_path)
            assert loaded == data
        finally:
            temp_path.unlink()
    
    def test_relative_path(self):
        """Test loading with relative path."""
        from scitex.io._load_modules import _load_joblib
        
        data = [1, 2, 3, 4, 5]
        
        # Create file in current directory
        filename = "test_temp.joblib"
        joblib.dump(data, filename)
        
        try:
            loaded = _load_joblib(filename)
            assert loaded == data
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_absolute_path(self):
        """Test loading with absolute path."""
        from scitex.io._load_modules import _load_joblib
        
        data = np.array([1, 2, 3])
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            abs_path = os.path.abspath(f.name)
        
        try:
            loaded = _load_joblib(abs_path)
            np.testing.assert_array_equal(loaded, data)
        finally:
            os.unlink(abs_path)
    
    def test_path_with_spaces(self):
        """Test loading file with spaces in path."""
        from scitex.io._load_modules import _load_joblib
        
        data = {"key": "value"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path_with_spaces = os.path.join(tmpdir, "test file with spaces.joblib")
            joblib.dump(data, path_with_spaces)
            
            loaded = _load_joblib(path_with_spaces)
            assert loaded == data
    
    def test_path_with_special_characters(self):
        """Test loading file with special characters in path."""
        from scitex.io._load_modules import _load_joblib
        
        data = [1, 2, 3]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use safe special characters
            special_path = os.path.join(tmpdir, "test-file_2025.joblib")
            joblib.dump(data, special_path)
            
            loaded = _load_joblib(special_path)
            assert loaded == data


class TestLoadJoblibErrors:
    """Test error handling and edge cases."""
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        from scitex.io._load_modules import _load_joblib
        
        with pytest.raises(FileNotFoundError):
            _load_joblib("non_existent_file.joblib")
    
    def test_invalid_extension(self):
        """Test various invalid file extensions."""
        from scitex.io._load_modules import _load_joblib
        
        invalid_extensions = ['.pkl', '.pickle', '.npy', '.txt', '.json', '']
        
        for ext in invalid_extensions:
            with pytest.raises(ValueError, match="extension"):
                _load_joblib(f"file{ext}")
    
    def test_corrupted_file(self):
        """Test handling of corrupted joblib file."""
        from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            # Write garbage data
            f.write(b"This is not a valid joblib file content")
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):  # Could be various exceptions
                _load_joblib(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_file(self):
        """Test handling of empty file."""
        from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            # Create empty file
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):
                _load_joblib(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_permission_denied(self):
        """Test handling of permission denied error."""
        from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump({"test": "data"}, f.name)
            temp_path = f.name
        
        try:
            # Change permissions to read-only
            os.chmod(temp_path, 0o000)
            
            with pytest.raises(PermissionError):
                _load_joblib(temp_path)
        finally:
            # Restore permissions and delete
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)
    
    def test_wrong_format_file(self):
        """Test loading file saved with pickle instead of joblib."""
        from scitex.io._load_modules import _load_joblib
        
        data = {"test": "data"}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            # Save with pickle instead of joblib
            with open(f.name, 'wb') as pf:
                pickle.dump(data, pf)
            temp_path = f.name
        
        try:
            # Depending on implementation, might work or fail
            loaded = _load_joblib(temp_path)
            # If it loads successfully, verify data
            if loaded:
                assert loaded == data
        except Exception:
            # Expected if strict joblib format checking
            pass
        finally:
            os.unlink(temp_path)


class TestLoadJoblibLargeData:
    """Test handling of large data files."""
    
    def test_large_array(self):
        """Test loading very large numpy array."""
        from scitex.io._load_modules import _load_joblib
        
        # Create large array (adjust size based on available memory)
        large_array = np.random.rand(1000, 1000)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(large_array, f.name, compress=3)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            np.testing.assert_array_almost_equal(loaded, large_array, decimal=5)
        finally:
            os.unlink(temp_path)
    
    def test_many_small_objects(self):
        """Test loading file with many small objects."""
        from scitex.io._load_modules import _load_joblib
        
        # Create many small objects
        data = {f"key_{i}": np.random.rand(10) for i in range(1000)}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(data, f.name)
            temp_path = f.name
        
        try:
            loaded = _load_joblib(temp_path)
            assert len(loaded) == 1000
            assert all(f"key_{i}" in loaded for i in range(1000))
        finally:
            os.unlink(temp_path)


class TestLoadJoblibCompatibility:
    """Test compatibility with different joblib versions and settings."""
    
    def test_mmap_mode(self):
        """Test loading with memory mapping."""
        from scitex.io._load_modules import _load_joblib
        
        # Large array for mmap testing
        large_array = np.random.rand(500, 500)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(large_array, f.name)
            temp_path = f.name
        
        try:
            # Note: _load_joblib might not support mmap_mode parameter
            # This tests basic loading which should work regardless
            loaded = _load_joblib(temp_path)
            np.testing.assert_array_almost_equal(loaded, large_array)
        finally:
            os.unlink(temp_path)
    
    def test_protocol_versions(self):
        """Test loading files saved with different pickle protocols."""
        from scitex.io._load_modules import _load_joblib
        
        data = {"test": np.array([1, 2, 3])}
        
        # Test different pickle protocols (if supported by joblib.dump)
        for protocol in [2, 3, 4]:
            try:
                with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                    # Try to specify protocol if supported
                    try:
                        joblib.dump(data, f.name, protocol=protocol)
                    except TypeError:
                        # If protocol parameter not supported, use default
                        joblib.dump(data, f.name)
                    temp_path = f.name
                
                loaded = _load_joblib(temp_path)
                assert loaded["test"].tolist() == [1, 2, 3]
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


class TestLoadJoblibIntegration:
    """Integration tests with other scitex.io functionality."""
    
    @patch('scitex.io._load_modules._joblib.joblib.load')
    def test_joblib_load_called(self, mock_load):
        """Test that joblib.load is called correctly."""
        from scitex.io._load_modules import _load_joblib
        
        mock_load.return_value = {"mocked": "data"}
        
        result = _load_joblib("test.joblib")
        
        mock_load.assert_called_once_with("test.joblib")
        assert result == {"mocked": "data"}
    
    def test_round_trip_consistency(self):
        """Test saving and loading maintains data integrity."""
        from scitex.io._load_modules import _load_joblib
        
        # Various data types for round-trip testing
        test_cases = [
            np.random.rand(50, 50),
            pd.DataFrame(np.random.rand(100, 5), columns=list('ABCDE')),
            {"nested": {"data": [1, 2, 3], "array": np.eye(3)}},
            [np.array([1, 2]), np.array([3, 4]), np.array([5, 6])]
        ]
        
        for original_data in test_cases:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(original_data, f.name)
                temp_path = f.name
            
            try:
                loaded_data = _load_joblib(temp_path)
                
                if isinstance(original_data, np.ndarray):
                    np.testing.assert_array_almost_equal(loaded_data, original_data)
                elif isinstance(original_data, pd.DataFrame):
                    pd.testing.assert_frame_equal(loaded_data, original_data)
                elif isinstance(original_data, dict):
                    assert loaded_data.keys() == original_data.keys()
                elif isinstance(original_data, list):
                    assert len(loaded_data) == len(original_data)
            finally:
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])