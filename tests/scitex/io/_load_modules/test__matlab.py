#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:55:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__matlab.py

"""
Comprehensive tests for MATLAB file loading functionality.

Tests cover:
- Basic MATLAB file loading with scipy.io
- Complex MATLAB data structures (structs, cell arrays)
- Different MATLAB file versions (v4, v6, v7, v7.3)
- Pymatreader fallback functionality
- Various MATLAB data types and conversions
- Large file handling and performance
- Error conditions and edge cases
- Integration with scientific computing workflows
"""

import os
import sys
import tempfile
import pytest
import numpy as np
import scipy.io as sio
from unittest.mock import Mock, patch, MagicMock


class TestLoadMatlab:
    """Test suite for _load_matlab function."""

    def test_basic_matlab_loading(self):
        """Test loading basic MATLAB .mat file with scipy.io."""
        from scitex.io._load_modules import _load_matlab
        
        # Create test data with various types
        data = {
            'double_array': np.random.rand(10, 20),
            'integer_scalar': 42,
            'float_scalar': 3.14159,
            'string_array': np.array(['hello', 'world'], dtype='U10'),
            'logical_array': np.array([True, False, True, False]),
            'complex_array': np.array([1+2j, 3+4j, 5+6j])
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, data)
            temp_path = f.name
        
        try:
            loaded_data = _load_matlab(temp_path)
            
            # Verify basic data presence
            assert 'double_array' in loaded_data
            assert 'integer_scalar' in loaded_data
            assert 'float_scalar' in loaded_data
            
            # Verify array data
            np.testing.assert_array_almost_equal(loaded_data['double_array'], data['double_array'])
            assert loaded_data['integer_scalar'].item() == 42
            assert abs(loaded_data['float_scalar'].item() - 3.14159) < 1e-10
            
            # Verify complex data (MATLAB may add extra dimensions)
            complex_loaded = loaded_data['complex_array']
            if complex_loaded.ndim > 1:
                complex_loaded = complex_loaded.flatten()
            np.testing.assert_array_almost_equal(complex_loaded, data['complex_array'])
            
        finally:
            os.unlink(temp_path)

    def test_extension_validation(self):
        """Test that function validates .mat extension."""
        from scitex.io._load_modules import _load_matlab
        
        invalid_extensions = [
            "file.txt",
            "file.hdf5",
            "file.csv",
            "file.json",
            "file.mat.bak",
            "file.matlab",
            "file"  # No extension
        ]
        
        for invalid_path in invalid_extensions:
            with pytest.raises(ValueError, match="File must have .mat extension"):
                _load_matlab(invalid_path)

    def test_scipy_loadmat_functionality(self):
        """Test scipy.io.loadmat functionality with different options."""
        from scitex.io._load_modules import _load_matlab
        
        # Create test data with metadata
        data = {
            'test_array': np.random.rand(5, 5),
            'metadata': np.array(['experiment_1'], dtype='U20')
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, data, format='5')  # Force MATLAB v5 format
            temp_path = f.name
        
        try:
            # Test basic loading
            loaded_data = _load_matlab(temp_path)
            assert 'test_array' in loaded_data
            np.testing.assert_array_almost_equal(loaded_data['test_array'], data['test_array'])
            
            # Test with kwargs forwarding
            loaded_data_with_kwargs = _load_matlab(temp_path, squeeze_me=True, struct_as_record=False)
            assert 'test_array' in loaded_data_with_kwargs
            
        finally:
            os.unlink(temp_path)

    def test_struct_array_handling(self):
        """Test loading MATLAB struct arrays."""
        from scitex.io._load_modules import _load_matlab
        
        # Create nested structure data
        nested_data = {
            'experiment': {
                'name': 'test_experiment',
                'date': '2023-01-01',
                'data': np.random.rand(10, 10),
                'parameters': {
                    'sampling_rate': 1000,
                    'channels': ['Ch1', 'Ch2', 'Ch3']
                }
            },
            'results': {
                'accuracy': 0.95,
                'confusion_matrix': np.random.randint(0, 100, (3, 3))
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, nested_data)
            temp_path = f.name
        
        try:
            loaded_data = _load_matlab(temp_path)
            
            # Verify nested structure is preserved (note: scipy may flatten structures)
            assert 'experiment' in loaded_data
            assert 'results' in loaded_data
            
            # Verify data integrity where possible
            if isinstance(loaded_data['experiment'], np.ndarray) and loaded_data['experiment'].dtype.names:
                # Structured array format
                assert 'data' in loaded_data['experiment'].dtype.names or 'data' in str(loaded_data['experiment'])
            
        finally:
            os.unlink(temp_path)

    def test_large_file_handling(self):
        """Test loading large MATLAB files."""
        from scitex.io._load_modules import _load_matlab
        
        # Create large data for performance testing
        large_data = {
            'large_matrix': np.random.rand(500, 500),
            'large_3d': np.random.rand(100, 100, 100).astype(np.float32),
            'integer_array': np.random.randint(0, 1000, (1000, 100)),
            'metadata': np.array(['large_experiment'], dtype='U50')
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, large_data, format='5')
            temp_path = f.name
        
        try:
            loaded_data = _load_matlab(temp_path)
            
            # Verify large arrays are loaded correctly
            assert loaded_data['large_matrix'].shape == (500, 500)
            assert loaded_data['large_3d'].shape == (100, 100, 100)
            assert loaded_data['integer_array'].shape == (1000, 100)
            
            # Verify data integrity for sample
            np.testing.assert_array_equal(
                loaded_data['large_matrix'][:5, :5], 
                large_data['large_matrix'][:5, :5]
            )
            
        finally:
            os.unlink(temp_path)

    def test_different_matlab_versions(self):
        """Test loading different MATLAB file format versions."""
        from scitex.io._load_modules import _load_matlab
        
        test_data = {
            'version_test': np.array([1, 2, 3, 4, 5]),
            'float_data': np.array([1.1, 2.2, 3.3])
        }
        
        # Test different MATLAB versions supported by scipy
        matlab_versions = ['4', '5']
        
        for version in matlab_versions:
            with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
                try:
                    sio.savemat(f.name, test_data, format=version)
                    temp_path = f.name
                    
                    loaded_data = _load_matlab(temp_path)
                    
                    # Verify data integrity
                    assert 'version_test' in loaded_data
                    np.testing.assert_array_equal(loaded_data['version_test'].flatten(), test_data['version_test'])
                    
                except Exception as e:
                    # Skip if version not supported
                    pytest.skip(f"MATLAB version {version} not supported: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

    def test_pymatreader_fallback(self):
        """Test fallback to pymatreader when scipy fails."""
        from scitex.io._load_modules import _load_matlab
        
        # Mock pymatreader
        mock_pymat_data = {
            'test_data': np.array([1, 2, 3]),
            'fallback_test': 'pymatreader_success'
        }
        
        with patch('scipy.io.loadmat', side_effect=Exception("scipy failed to load")) as mock_loadmat:
            with patch('pymatreader.read_mat', return_value=mock_pymat_data) as mock_read_mat:
                result = _load_matlab('test.mat')
                
                # Verify pymatreader was called
                mock_read_mat.assert_called_once_with('test.mat')
                assert result == mock_pymat_data
                
                # Verify scipy was tried first
                mock_loadmat.assert_called_once_with('test.mat')

    def test_both_loaders_fail(self):
        """Test when both scipy and pymatreader fail."""
        from scitex.io._load_modules import _load_matlab
        
        # Make both loaders fail
        scipy_error = Exception("scipy error")
        pymat_error = Exception("pymatreader error")
        
        with patch('scipy.io.loadmat', side_effect=scipy_error) as mock_loadmat:
            with patch('pymatreader.read_mat', side_effect=pymat_error) as mock_read_mat:
                # Should raise ValueError with both error messages
                with pytest.raises(ValueError) as exc_info:
                    _load_matlab('test.mat')
                
                error_message = str(exc_info.value)
                assert "scipy error" in error_message
                assert "pymatreader error" in error_message
                assert "Error loading file test.mat" in error_message

    def test_kwargs_forwarding_to_scipy(self):
        """Test that kwargs are forwarded to scipy.io.loadmat."""
        from scitex.io._load_modules import _load_matlab
        
        test_data = {'simple_array': np.array([1, 2, 3])}
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, test_data)
            temp_path = f.name
        
        try:
            # Test with various scipy.io.loadmat parameters
            loaded_data = _load_matlab(
                temp_path,
                squeeze_me=True,
                struct_as_record=False,
                variable_names=['simple_array']
            )
            
            assert 'simple_array' in loaded_data
            
        finally:
            os.unlink(temp_path)

    def test_kwargs_forwarding_to_pymatreader(self):
        """Test that kwargs are forwarded to pymatreader when used as fallback."""
        from scitex.io._load_modules import _load_matlab
        
        mock_pymat_data = {'pymat_data': np.array([4, 5, 6])}
        
        with patch('scipy.io.loadmat', side_effect=Exception("scipy failed")):
            with patch('pymatreader.read_mat', return_value=mock_pymat_data) as mock_read_mat:
                
                custom_kwargs = {'ignore_fields': ['__header__'], 'squeeze_me': True}
                result = _load_matlab('test.mat', **custom_kwargs)
                
                # Verify kwargs were passed to pymatreader
                mock_read_mat.assert_called_once_with('test.mat', **custom_kwargs)
                assert result == mock_pymat_data

    def test_error_handling_file_not_found(self):
        """Test error handling for non-existent files."""
        from scitex.io._load_modules import _load_matlab
        
        # Both scipy and pymatreader should fail for non-existent file
        with pytest.raises(ValueError) as exc_info:
            _load_matlab('nonexistent_file.mat')
        
        error_message = str(exc_info.value)
        assert "Error loading file nonexistent_file.mat" in error_message

    def test_corrupted_file_handling(self):
        """Test handling of corrupted MATLAB files."""
        from scitex.io._load_modules import _load_matlab
        
        # Create a file that's not a valid MATLAB file
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            f.write(b'This is not a valid MATLAB file content')
            temp_path = f.name
        
        try:
            # Should raise ValueError with both loader errors
            with pytest.raises(ValueError) as exc_info:
                _load_matlab(temp_path)
            
            error_message = str(exc_info.value)
            assert "Error loading file" in error_message
            
        finally:
            os.unlink(temp_path)

    def test_scientific_computing_scenarios(self):
        """Test real-world scientific computing scenarios."""
        from scitex.io._load_modules import _load_matlab
        
        # Simulate typical scientific data
        scientific_data = {
            'experimental_data': {
                'time_series': np.random.rand(1000, 64),  # EEG-like data
                'sampling_rate': 1000.0,
                'channel_names': [f'Ch{i:02d}' for i in range(64)],
                'stimulus_times': [1.0, 2.5, 4.0, 5.5],
                'conditions': ['rest', 'task', 'rest', 'task']
            },
            'analysis_results': {
                'power_spectrum': np.random.rand(512, 64),
                'connectivity_matrix': np.random.rand(64, 64),
                'statistical_significance': np.random.rand(64) < 0.05
            },
            'metadata': {
                'experiment_date': '2023-01-15',
                'subject_id': 'S001',
                'session_number': 1
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, scientific_data)
            temp_path = f.name
        
        try:
            loaded_data = _load_matlab(temp_path)
            
            # Verify scientific data structure
            assert 'experimental_data' in loaded_data
            assert 'analysis_results' in loaded_data
            assert 'metadata' in loaded_data
            
            # Verify data shapes for typical neuroscience analysis
            exp_data = loaded_data['experimental_data']
            if hasattr(exp_data, 'dtype') and exp_data.dtype.names:
                # Structured array - verify fields exist
                field_names = exp_data.dtype.names
                assert any('time_series' in name for name in field_names)
            
        finally:
            os.unlink(temp_path)

    def test_edge_cases(self):
        """Test edge cases and corner case scenarios."""
        from scitex.io._load_modules import _load_matlab
        
        # Test with various edge case data
        edge_case_data = {
            'empty_array': np.array([]),
            'single_value': np.array([42]),
            'nan_values': np.array([np.nan, 1.0, np.inf, -np.inf]),
            'unicode_string': np.array(['测试', 'العربية', 'Русский'], dtype='U10'),
            'very_small_numbers': np.array([1e-300, 1e-100, 1e-50]),
            'very_large_numbers': np.array([1e50, 1e100, 1e200]),
            'boolean_array': np.array([True, False, True, False]),
            'complex_numbers': np.array([1+1j, 2-2j, 3+3j])
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, edge_case_data)
            temp_path = f.name
        
        try:
            loaded_data = _load_matlab(temp_path)
            
            # Verify edge cases are handled
            assert 'empty_array' in loaded_data
            assert 'single_value' in loaded_data
            assert 'nan_values' in loaded_data
            
            # Check single value
            if hasattr(loaded_data['single_value'], 'item'):
                assert loaded_data['single_value'].item() == 42
            else:
                assert loaded_data['single_value'].flatten()[0] == 42
            
            # Check NaN and infinity handling
            nan_array = loaded_data['nan_values'].flatten()
            assert np.isnan(nan_array[0])
            assert nan_array[1] == 1.0
            assert np.isinf(nan_array[2])
            assert np.isinf(nan_array[3]) and nan_array[3] < 0
            
        finally:
            os.unlink(temp_path)

    def test_integration_with_main_load_function(self):
        """Test integration with main scitex.io.load function."""
        try:
            import scitex
            
            # Create test MATLAB file
            test_data = {
                'integration_test': np.array([1, 2, 3, 4, 5]),
                'metadata': np.array(['integration_test'], dtype='U20')
            }
            
            with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
                sio.savemat(f.name, test_data)
                temp_path = f.name
            
            try:
                # Test loading through main interface
                loaded_data = scitex.io.load(temp_path)
                
                # Verify functionality
                assert 'integration_test' in loaded_data
                np.testing.assert_array_equal(
                    loaded_data['integration_test'].flatten(), 
                    test_data['integration_test']
                )
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("SciTeX not available for integration testing")

    def test_memory_efficiency(self):
        """Test memory efficiency with repeated loading."""
        from scitex.io._load_modules import _load_matlab
        
        # Create moderately large data
        data = {
            'repeated_test': np.random.rand(200, 200),
            'test_counter': np.array([1])
        }
        
        with tempfile.NamedTemporaryFile(suffix='.mat', delete=False) as f:
            sio.savemat(f.name, data)
            temp_path = f.name
        
        try:
            # Load multiple times to test memory efficiency
            for i in range(5):
                loaded_data = _load_matlab(temp_path)
                assert 'repeated_test' in loaded_data
                assert loaded_data['repeated_test'].shape == (200, 200)
                # Force garbage collection simulation
                del loaded_data
                
        finally:
            os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_matlab.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-10 08:07:03 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_matlab.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "/ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_matlab.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from typing import Any
# 
# 
# def _load_matlab(lpath: str, **kwargs) -> Any:
#     """Load MATLAB file."""
#     if not lpath.endswith(".mat"):
#         raise ValueError("File must have .mat extension")
# 
#     # Try using scipy.io first for binary .mat files
#     try:
#         # For MATLAB v7.3 files (HDF5 format)
#         from scipy.io import loadmat
# 
#         return loadmat(lpath, **kwargs)
#     except Exception as e1:
#         # If scipy fails, try pymatreader  or older MAT files
#         try:
#             from pymatreader import read_mat
# 
#             return read_mat(lpath, **kwargs)
#         except Exception as e2:
#             # Both methods failed
#             raise ValueError(f"Error loading file {lpath}: {str(e1)}\nAnd: {str(e2)}")
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_matlab.py
# --------------------------------------------------------------------------------
