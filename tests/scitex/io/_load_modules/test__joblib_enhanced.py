#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 09:50:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__joblib_enhanced.py

"""Comprehensive tests for joblib file loading functionality."""

import os
import tempfile
import pytest
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from unittest.mock import patch, mock_open


class TestLoadJoblibEnhanced:
    """Enhanced test suite for _load_joblib function."""

    def test_load_basic_data_types(self):
        """Test loading various basic Python data types."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {
            'int': 42,
            'float': 3.14159,
            'string': "Hello, World!",
            'list': [1, 2, 3, 'mixed', True],
            'dict': {'nested': {'key': 'value', 'number': 123}},
            'tuple': (1, 2, 3),
            'set': {1, 2, 3, 4, 5},
            'boolean': True,
            'none': None
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            loaded_data = _load_joblib(temp_path)
            
            assert loaded_data['int'] == 42
            assert loaded_data['float'] == 3.14159
            assert loaded_data['string'] == "Hello, World!"
            assert loaded_data['list'] == [1, 2, 3, 'mixed', True]
            assert loaded_data['dict']['nested']['key'] == 'value'
            assert loaded_data['tuple'] == (1, 2, 3)
            assert loaded_data['set'] == {1, 2, 3, 4, 5}
            assert loaded_data['boolean'] is True
            assert loaded_data['none'] is None
            
        finally:
            os.unlink(temp_path)

    def test_load_numpy_arrays(self):
        """Test loading NumPy arrays of various types and shapes."""
        from scitex.io._load_modules import _load_joblib
        
        test_arrays = {
            '1d_int': np.array([1, 2, 3, 4, 5]),
            '2d_float': np.random.rand(10, 5),
            '3d_complex': np.random.rand(3, 4, 5) + 1j * np.random.rand(3, 4, 5),
            'bool_array': np.array([True, False, True, False]),
            'string_array': np.array(['a', 'b', 'c']),
            'structured': np.array([(1, 'a', 2.5), (2, 'b', 3.7)], 
                                 dtype=[('id', 'i4'), ('name', 'U10'), ('value', 'f8')])
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_arrays, f.name)
            temp_path = f.name
        
        try:
            loaded_arrays = _load_joblib(temp_path)
            
            np.testing.assert_array_equal(loaded_arrays['1d_int'], test_arrays['1d_int'])
            np.testing.assert_array_almost_equal(loaded_arrays['2d_float'], test_arrays['2d_float'])
            np.testing.assert_array_almost_equal(loaded_arrays['3d_complex'], test_arrays['3d_complex'])
            np.testing.assert_array_equal(loaded_arrays['bool_array'], test_arrays['bool_array'])
            np.testing.assert_array_equal(loaded_arrays['string_array'], test_arrays['string_array'])
            np.testing.assert_array_equal(loaded_arrays['structured'], test_arrays['structured'])
            
        finally:
            os.unlink(temp_path)

    def test_load_pandas_objects(self):
        """Test loading Pandas DataFrames and Series."""
        from scitex.io._load_modules import _load_joblib
        
        # Create test DataFrame
        df = pd.DataFrame({
            'int_col': [1, 2, 3, 4, 5],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'str_col': ['a', 'b', 'c', 'd', 'e'],
            'bool_col': [True, False, True, False, True]
        })
        
        series = pd.Series([10, 20, 30, 40, 50], name='test_series')
        
        test_data = {'dataframe': df, 'series': series}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            loaded_data = _load_joblib(temp_path)
            
            pd.testing.assert_frame_equal(loaded_data['dataframe'], df)
            pd.testing.assert_series_equal(loaded_data['series'], series)
            
        finally:
            os.unlink(temp_path)

    def test_load_sklearn_models(self):
        """Test loading scikit-learn models."""
        from scitex.io._load_modules import _load_joblib
        
        # Create and train a simple model
        X = np.random.rand(100, 4)
        y = np.random.randint(0, 2, 100)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(model, f.name)
            temp_path = f.name
        
        try:
            loaded_model = _load_joblib(temp_path)
            
            # Test that the loaded model works
            predictions = loaded_model.predict(X[:5])
            assert len(predictions) == 5
            assert all(pred in [0, 1] for pred in predictions)
            
            # Test model attributes
            assert loaded_model.n_estimators == 10
            assert loaded_model.random_state == 42
            
        finally:
            os.unlink(temp_path)

    def test_load_with_compression(self):
        """Test loading compressed joblib files."""
        from scitex.io._load_modules import _load_joblib
        
        # Large data to benefit from compression
        large_data = {
            'large_array': np.random.rand(1000, 1000),
            'repeated_data': [42] * 10000
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(large_data, f.name, compress=3)
            temp_path = f.name
        
        try:
            loaded_data = _load_joblib(temp_path)
            
            np.testing.assert_array_almost_equal(
                loaded_data['large_array'], 
                large_data['large_array']
            )
            assert loaded_data['repeated_data'] == [42] * 10000
            
        finally:
            os.unlink(temp_path)

    def test_load_with_protocol_versions(self):
        """Test loading files saved with different pickle protocols."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {'test': 'protocol_version'}
        
        # Test different protocol versions
        for protocol in [2, 3, 4]:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(test_data, f.name, protocol=protocol)
                temp_path = f.name
            
            try:
                loaded_data = _load_joblib(temp_path)
                assert loaded_data['test'] == 'protocol_version'
            finally:
                os.unlink(temp_path)

    def test_load_empty_file(self):
        """Test behavior with empty joblib file."""
        from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            # Create empty joblib file
            joblib.dump(None, f.name)
            temp_path = f.name
        
        try:
            loaded_data = _load_joblib(temp_path)
            assert loaded_data is None
        finally:
            os.unlink(temp_path)

    def test_load_single_values(self):
        """Test loading single value objects."""
        from scitex.io._load_modules import _load_joblib
        
        test_values = [42, 3.14, "single_string", [1, 2, 3], True, None]
        
        for value in test_values:
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                joblib.dump(value, f.name)
                temp_path = f.name
            
            try:
                loaded_data = _load_joblib(temp_path)
                if isinstance(value, list):
                    assert loaded_data == value
                else:
                    assert loaded_data == value
            finally:
                os.unlink(temp_path)

    def test_invalid_file_extension(self):
        """Test error handling for invalid file extensions."""
        from scitex.io._load_modules import _load_joblib
        
        invalid_extensions = [
            "file.pkl",
            "file.pickle",
            "file.json",
            "file.txt",
            "file",
            "file.JOBLIB",  # Case sensitive
            "file.joblib.backup"
        ]
        
        for invalid_path in invalid_extensions:
            with pytest.raises(ValueError, match="File must have .joblib extension"):
                _load_joblib(invalid_path)

    def test_nonexistent_file(self):
        """Test error handling for nonexistent files."""
        from scitex.io._load_modules import _load_joblib
        
        with pytest.raises((FileNotFoundError, IOError)):
            _load_joblib("nonexistent_file.joblib")

    def test_corrupted_file(self):
        """Test error handling for corrupted joblib files."""
        from scitex.io._load_modules import _load_joblib
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            # Write corrupted data
            f.write(b"This is not a valid joblib file content")
            temp_path = f.name
        
        try:
            with pytest.raises((joblib.externals.loky.process_executor.TerminatedWorkerError, 
                              Exception)):  # Various pickle-related errors possible
                _load_joblib(temp_path)
        finally:
            os.unlink(temp_path)

    def test_large_file_handling(self):
        """Test handling of large files."""
        from scitex.io._load_modules import _load_joblib
        
        # Create reasonably large data (but not too large for CI)
        large_data = {
            'matrix': np.random.rand(500, 500),
            'list': list(range(100000)),
            'dict': {f'key_{i}': f'value_{i}' for i in range(10000)}
        }
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(large_data, f.name)
            temp_path = f.name
        
        try:
            loaded_data = _load_joblib(temp_path)
            
            assert loaded_data['matrix'].shape == (500, 500)
            assert len(loaded_data['list']) == 100000
            assert len(loaded_data['dict']) == 10000
            
        finally:
            os.unlink(temp_path)

    def test_file_permissions(self):
        """Test handling of file permission issues."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {'test': 'permissions'}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            # Remove read permissions
            os.chmod(temp_path, 0o000)
            
            with pytest.raises(PermissionError):
                _load_joblib(temp_path)
                
        finally:
            # Restore permissions before cleanup
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)

    def test_kwargs_passing(self):
        """Test that kwargs are passed to joblib.load."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {'test': 'kwargs'}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            # Test with mmap_mode (if supported)
            with patch('joblib.load') as mock_load:
                mock_load.return_value = test_data
                
                _load_joblib(temp_path, mmap_mode='r')
                
                # Verify joblib.load was called with kwargs
                mock_load.assert_called_once()
                args, kwargs = mock_load.call_args
                assert 'mmap_mode' in kwargs
                assert kwargs['mmap_mode'] == 'r'
                
        finally:
            os.unlink(temp_path)

    def test_file_handle_management(self):
        """Test proper file handle management."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {'test': 'file_handles'}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            # Mock to test file is properly closed
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('joblib.load', return_value=test_data):
                    _load_joblib(temp_path)
                
                # Verify file was opened and closed
                mock_file.assert_called_once_with(temp_path, 'rb')
                mock_file().__enter__.assert_called_once()
                mock_file().__exit__.assert_called_once()
                
        finally:
            os.unlink(temp_path)

    def test_unicode_filename(self):
        """Test loading from files with unicode characters in path."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {'unicode': 'test'}
        
        # Create file with unicode in name
        with tempfile.NamedTemporaryFile(suffix='_测试.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            loaded_data = _load_joblib(temp_path)
            assert loaded_data['unicode'] == 'test'
        finally:
            os.unlink(temp_path)

    def test_relative_vs_absolute_paths(self):
        """Test loading with both relative and absolute paths."""
        from scitex.io._load_modules import _load_joblib
        
        test_data = {'path': 'test'}
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(test_data, f.name)
            temp_path = f.name
        
        try:
            # Test absolute path
            loaded_data = _load_joblib(temp_path)
            assert loaded_data['path'] == 'test'
            
            # Test relative path (if possible)
            dirname = os.path.dirname(temp_path)
            basename = os.path.basename(temp_path)
            original_cwd = os.getcwd()
            
            try:
                os.chdir(dirname)
                loaded_data = _load_joblib(basename)
                assert loaded_data['path'] == 'test'
            finally:
                os.chdir(original_cwd)
                
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])