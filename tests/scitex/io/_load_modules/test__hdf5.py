#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:50:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__hdf5.py

"""
Comprehensive tests for HDF5 file loading functionality.

Tests cover:
- Basic HDF5 file loading with various data types
- Complex nested group structures
- Different numpy data types and conversions
- Pickled object storage and retrieval
- String/bytes conversion testing
- Attributes and metadata handling
- Large dataset processing
- Error conditions and edge cases
- Performance considerations for scientific computing
"""

import os
import sys
import pickle
import tempfile
import pytest
import numpy as np
import h5py
from unittest.mock import Mock, patch, MagicMock


class TestLoadHDF5:
    """Test suite for _load_hdf5 function."""

    def test_basic_hdf5_loading(self):
        """Test loading basic HDF5 file with simple datasets."""
        from scitex.io._load_modules import _load_hdf5
        
        # Create test data
        data = {'array': np.random.rand(10, 20), 'scalar': 42}
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                hf.create_dataset('array', data=data['array'])
                hf.create_dataset('scalar', data=data['scalar'])
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            assert 'array' in loaded_data
            assert 'scalar' in loaded_data
            np.testing.assert_array_almost_equal(loaded_data['array'], data['array'])
            assert loaded_data['scalar'] == 42
        finally:
            os.unlink(temp_path)

    def test_hdf5_extension_validation(self):
        """Test that function validates .hdf5 and .h5 extensions."""
        from scitex.io._load_modules import _load_hdf5
        
        invalid_extensions = [
            "file.txt",
            "file.json",
            "file.mat",
            "file.npz",
            "file.pickle",
            "file.h5.bak",
            "file.hdf5.old",
            "file"  # No extension
        ]
        
        for invalid_path in invalid_extensions:
            with pytest.raises(ValueError, match="File must have .hdf5 or .h5 extension"):
                _load_hdf5(invalid_path)

    def test_group_structures(self):
        """Test loading HDF5 files with nested group structures."""
        from scitex.io._load_modules import _load_hdf5
        
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                # Create nested groups
                grp1 = hf.create_group('experiment')
                grp2 = grp1.create_group('trial_1')
                grp3 = grp1.create_group('trial_2')
                
                # Add datasets at different levels
                hf.create_dataset('metadata', data=np.array([1, 2, 3]))
                grp1.create_dataset('conditions', data=np.array(['A', 'B', 'C'], dtype='S1'))
                grp2.create_dataset('data', data=np.ones((5, 5)))
                grp3.create_dataset('data', data=np.zeros((3, 3)))
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Check nested structure
            assert 'metadata' in loaded_data
            assert 'experiment' in loaded_data
            assert isinstance(loaded_data['experiment'], dict)
            assert 'trial_1' in loaded_data['experiment']
            assert 'trial_2' in loaded_data['experiment']
            assert 'data' in loaded_data['experiment']['trial_1']
            assert 'data' in loaded_data['experiment']['trial_2']
            
            # Verify data content
            np.testing.assert_array_equal(loaded_data['metadata'], [1, 2, 3])
            np.testing.assert_array_equal(loaded_data['experiment']['trial_1']['data'], np.ones((5, 5)))
            np.testing.assert_array_equal(loaded_data['experiment']['trial_2']['data'], np.zeros((3, 3)))
            
        finally:
            os.unlink(temp_path)

    def test_numpy_data_types(self):
        """Test loading various numpy data types and conversions."""
        from scitex.io._load_modules import _load_hdf5
        
        # Create data with different numpy types
        test_data = {
            'int8': np.int8(42),
            'int16': np.int16(1000),
            'int32': np.int32(100000),
            'int64': np.int64(10000000000),
            'uint8': np.uint8(255),
            'uint16': np.uint16(65535),
            'float32': np.float32(3.14159),
            'float64': np.float64(2.71828),
            'complex64': np.complex64(1 + 2j),
            'complex128': np.complex128(3 + 4j),
            'bool_true': np.bool_(True),
            'bool_false': np.bool_(False),
            'array_int': np.array([1, 2, 3, 4, 5], dtype=np.int32),
            'array_float': np.array([1.1, 2.2, 3.3], dtype=np.float64),
            'multidim_array': np.random.rand(3, 4, 5).astype(np.float32)
        }
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                for key, value in test_data.items():
                    hf.create_dataset(key, data=value)
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Test scalar integer conversions
            assert isinstance(loaded_data['int8'], int)
            assert loaded_data['int8'] == 42
            assert isinstance(loaded_data['int64'], int)
            assert loaded_data['int64'] == 10000000000
            
            # Test scalar float conversions
            assert isinstance(loaded_data['float32'], float)
            assert abs(loaded_data['float32'] - 3.14159) < 1e-5
            assert isinstance(loaded_data['float64'], float)
            assert abs(loaded_data['float64'] - 2.71828) < 1e-10
            
            # Test boolean conversions
            assert isinstance(loaded_data['bool_true'], bool)
            assert loaded_data['bool_true'] is True
            assert isinstance(loaded_data['bool_false'], bool)
            assert loaded_data['bool_false'] is False
            
            # Test array preservation
            np.testing.assert_array_equal(loaded_data['array_int'], [1, 2, 3, 4, 5])
            np.testing.assert_array_almost_equal(loaded_data['array_float'], [1.1, 2.2, 3.3])
            assert loaded_data['multidim_array'].shape == (3, 4, 5)
            
        finally:
            os.unlink(temp_path)

    def test_string_and_bytes_handling(self):
        """Test loading and conversion of string and bytes data."""
        from scitex.io._load_modules import _load_hdf5
        
        # Test data with strings and bytes
        string_data = "Hello, HDF5 World! 🌍"
        bytes_data = string_data.encode('utf-8')
        unicode_string = "测试中文 العربية Русский"
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                # Store bytes that should be converted to string
                hf.create_dataset('bytes_to_string', data=bytes_data)
                
                # Store unicode string
                hf.create_dataset('unicode_string', data=unicode_string)
                
                # Store array of strings
                string_array = np.array(['apple', 'banana', 'cherry'], dtype='S10')
                hf.create_dataset('string_array', data=string_array)
                
                # Store variable length strings
                vlen_string = h5py.special_dtype(vlen=str)
                hf.create_dataset('vlen_string', data=['variable', 'length', 'strings'], dtype=vlen_string)
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Test bytes to string conversion
            assert isinstance(loaded_data['bytes_to_string'], str)
            assert loaded_data['bytes_to_string'] == string_data
            
            # Test unicode string preservation
            assert loaded_data['unicode_string'] == unicode_string
            
            # Test string arrays
            assert 'string_array' in loaded_data
            assert 'vlen_string' in loaded_data
            
        finally:
            os.unlink(temp_path)

    def test_pickled_objects(self):
        """Test loading pickled objects stored in HDF5."""
        from scitex.io._load_modules import _load_hdf5
        
        # Create complex Python objects to pickle
        test_objects = {
            'list': [1, 2, 3, 'hello', [4, 5]],
            'dict': {'key1': 'value1', 'key2': 42, 'nested': {'a': 1}},
            'set': {1, 2, 3, 4, 5},
            'tuple': (1, 'two', 3.0, [4, 5])
        }
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                for key, obj in test_objects.items():
                    # Pickle and store as void array (np.void)
                    pickled_data = pickle.dumps(obj)
                    void_data = np.void(pickled_data)
                    hf.create_dataset(f'pickled_{key}', data=void_data)
                    
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Verify pickled objects are correctly unpickled
            assert loaded_data['pickled_list'] == [1, 2, 3, 'hello', [4, 5]]
            assert loaded_data['pickled_dict'] == {'key1': 'value1', 'key2': 42, 'nested': {'a': 1}}
            assert loaded_data['pickled_set'] == {1, 2, 3, 4, 5}
            assert loaded_data['pickled_tuple'] == (1, 'two', 3.0, [4, 5])
            
        finally:
            os.unlink(temp_path)

    def test_large_datasets(self):
        """Test loading large datasets for performance validation."""
        from scitex.io._load_modules import _load_hdf5
        
        # Create large arrays for performance testing
        large_1d = np.random.rand(1000000)  # 1M elements
        large_2d = np.random.rand(1000, 1000)  # 1M elements in 2D
        large_3d = np.random.randint(0, 255, size=(100, 100, 100), dtype=np.uint8)  # 1M bytes
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                hf.create_dataset('large_1d', data=large_1d, compression='gzip')
                hf.create_dataset('large_2d', data=large_2d, compression='lzf')
                hf.create_dataset('large_3d', data=large_3d)
                
                # Add chunked dataset
                hf.create_dataset('chunked', data=np.ones((500, 500)), chunks=True)
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Verify large datasets are loaded correctly
            assert loaded_data['large_1d'].shape == (1000000,)
            assert loaded_data['large_2d'].shape == (1000, 1000)
            assert loaded_data['large_3d'].shape == (100, 100, 100)
            assert loaded_data['chunked'].shape == (500, 500)
            
            # Verify data integrity for smaller sample
            np.testing.assert_array_equal(loaded_data['large_1d'][:100], large_1d[:100])
            np.testing.assert_array_equal(loaded_data['large_2d'][:10, :10], large_2d[:10, :10])
            np.testing.assert_array_equal(loaded_data['chunked'], np.ones((500, 500)))
            
        finally:
            os.unlink(temp_path)

    def test_attributes_and_metadata(self):
        """Test handling of HDF5 attributes and metadata."""
        from scitex.io._load_modules import _load_hdf5
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                # Create datasets with attributes
                dataset = hf.create_dataset('data', data=np.random.rand(10, 10))
                dataset.attrs['units'] = 'volts'
                dataset.attrs['sampling_rate'] = 1000.0
                dataset.attrs['channels'] = ['Ch1', 'Ch2', 'Ch3']
                
                # Create group with attributes
                grp = hf.create_group('experiment')
                grp.attrs['date'] = '2023-01-01'
                grp.attrs['researcher'] = 'Dr. Smith'
                grp.create_dataset('results', data=[1, 2, 3, 4, 5])
                
                # File-level attributes
                hf.attrs['version'] = '1.0'
                hf.attrs['description'] = 'Test experiment data'
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Verify main data structure is loaded
            assert 'data' in loaded_data
            assert 'experiment' in loaded_data
            assert loaded_data['data'].shape == (10, 10)
            assert 'results' in loaded_data['experiment']
            
            # Note: Attributes are not currently loaded by the function
            # This test verifies the function handles files with attributes gracefully
            
        finally:
            os.unlink(temp_path)

    def test_empty_groups_and_datasets(self):
        """Test handling of empty groups and datasets."""
        from scitex.io._load_modules import _load_hdf5
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                # Create empty group
                empty_group = hf.create_group('empty_group')
                
                # Create group with empty dataset
                grp = hf.create_group('group_with_empty')
                grp.create_dataset('empty_array', data=np.array([]))
                grp.create_dataset('empty_2d', shape=(0, 5))
                
                # Non-empty data for comparison
                hf.create_dataset('normal_data', data=[1, 2, 3])
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Verify structure is preserved
            assert 'empty_group' in loaded_data
            assert isinstance(loaded_data['empty_group'], dict)
            assert len(loaded_data['empty_group']) == 0
            
            assert 'group_with_empty' in loaded_data
            assert 'empty_array' in loaded_data['group_with_empty']
            assert 'empty_2d' in loaded_data['group_with_empty']
            
            # Verify empty arrays
            assert loaded_data['group_with_empty']['empty_array'].size == 0
            assert loaded_data['group_with_empty']['empty_2d'].shape == (0, 5)
            
            # Verify normal data still works
            np.testing.assert_array_equal(loaded_data['normal_data'], [1, 2, 3])
            
        finally:
            os.unlink(temp_path)

    def test_error_handling(self):
        """Test error handling for various failure conditions."""
        from scitex.io._load_modules import _load_hdf5
        
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            _load_hdf5('nonexistent_file.hdf5')
        
        # Test with corrupted file (create invalid HDF5)
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            f.write(b'This is not a valid HDF5 file')
            temp_path = f.name
        
        try:
            with pytest.raises((OSError, ValueError)):
                _load_hdf5(temp_path)
        finally:
            os.unlink(temp_path)

    def test_scientific_computing_scenarios(self):
        """Test real-world scientific computing scenarios."""
        from scitex.io._load_modules import _load_hdf5
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                # Simulate neuroimaging data structure
                neuro_group = hf.create_group('neuroimaging')
                neuro_group.create_dataset('bold_signal', data=np.random.rand(100, 64, 64, 32))  # 4D fMRI
                neuro_group.create_dataset('brain_mask', data=np.random.randint(0, 2, (64, 64, 32), dtype=bool))
                neuro_group.create_dataset('voxel_coordinates', data=np.random.rand(1000, 3))
                
                # Simulate time series data
                timeseries_group = hf.create_group('timeseries')
                timeseries_group.create_dataset('timestamps', data=np.linspace(0, 10, 1000))
                timeseries_group.create_dataset('eeg_channels', data=np.random.rand(1000, 64))
                timeseries_group.create_dataset('channel_names', data=[f'Ch{i:02d}' for i in range(64)])
                
                # Simulate experimental parameters
                params_group = hf.create_group('parameters')
                params_group.create_dataset('sampling_rate', data=1000.0)
                params_group.create_dataset('stimulus_times', data=[1.0, 3.5, 6.2, 8.9])
                params_group.create_dataset('condition_labels', data=['rest', 'task', 'rest', 'task'])
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Verify neuroimaging data
            assert 'neuroimaging' in loaded_data
            assert loaded_data['neuroimaging']['bold_signal'].shape == (100, 64, 64, 32)
            assert loaded_data['neuroimaging']['brain_mask'].dtype == bool
            assert loaded_data['neuroimaging']['voxel_coordinates'].shape == (1000, 3)
            
            # Verify time series data  
            assert 'timeseries' in loaded_data
            assert loaded_data['timeseries']['timestamps'].shape == (1000,)
            assert loaded_data['timeseries']['eeg_channels'].shape == (1000, 64)
            assert len(loaded_data['timeseries']['channel_names']) == 64
            
            # Verify parameters
            assert 'parameters' in loaded_data
            assert loaded_data['parameters']['sampling_rate'] == 1000.0
            assert len(loaded_data['parameters']['stimulus_times']) == 4
            
        finally:
            os.unlink(temp_path)

    def test_edge_cases_and_corner_cases(self):
        """Test edge cases and corner case scenarios."""
        from scitex.io._load_modules import _load_hdf5
        
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                # Very deep nesting
                deep_group = hf
                for i in range(10):
                    deep_group = deep_group.create_group(f'level_{i}')
                deep_group.create_dataset('deep_data', data=[42])
                
                # Unicode group and dataset names
                unicode_group = hf.create_group('测试组')
                unicode_group.create_dataset('数据集', data=np.array([1, 2, 3]))
                
                # Special characters in names
                special_group = hf.create_group('group-with_special.chars')
                special_group.create_dataset('data@#$%', data=[1, 2, 3])
                
                # Very large single value
                hf.create_dataset('huge_number', data=np.float64(1e308))
                
                # Very small single value
                hf.create_dataset('tiny_number', data=np.float64(1e-308))
                
                # NaN and infinity values
                hf.create_dataset('nan_value', data=np.nan)
                hf.create_dataset('inf_value', data=np.inf)
                hf.create_dataset('neg_inf_value', data=-np.inf)
                
            temp_path = f.name
        
        try:
            loaded_data = _load_hdf5(temp_path)
            
            # Test deep nesting
            current_level = loaded_data
            for i in range(10):
                assert f'level_{i}' in current_level
                current_level = current_level[f'level_{i}']
            assert current_level['deep_data'][0] == 42
            
            # Test unicode names
            assert '测试组' in loaded_data
            assert '数据集' in loaded_data['测试组']
            
            # Test special characters
            assert 'group-with_special.chars' in loaded_data
            assert 'data@#$%' in loaded_data['group-with_special.chars']
            
            # Test extreme values
            assert loaded_data['huge_number'] == 1e308
            assert loaded_data['tiny_number'] == 1e-308
            assert np.isnan(loaded_data['nan_value'])
            assert np.isinf(loaded_data['inf_value'])
            assert np.isinf(loaded_data['neg_inf_value']) and loaded_data['neg_inf_value'] < 0
            
        finally:
            os.unlink(temp_path)

    def test_integration_with_main_load_function(self):
        """Test integration with main scitex.io.load function."""
        try:
            import scitex
            
            # Create test HDF5 file
            with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
                with h5py.File(f.name, 'w') as hf:
                    hf.create_dataset('test_data', data=np.array([1, 2, 3, 4, 5]))
                    grp = hf.create_group('test_group')
                    grp.create_dataset('nested_data', data=np.ones((3, 3)))
                temp_path = f.name
            
            try:
                # Test loading through main interface
                loaded_data = scitex.io.load(temp_path)
                
                # Verify functionality
                assert 'test_data' in loaded_data
                assert 'test_group' in loaded_data
                np.testing.assert_array_equal(loaded_data['test_data'], [1, 2, 3, 4, 5])
                np.testing.assert_array_equal(loaded_data['test_group']['nested_data'], np.ones((3, 3)))
                
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            pytest.skip("SciTeX not available for integration testing")

    def test_kwargs_forwarding(self):
        """Test that kwargs are properly handled."""
        from scitex.io._load_modules import _load_hdf5
        
        # Create test file
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as f:
            with h5py.File(f.name, 'w') as hf:
                hf.create_dataset('data', data=[1, 2, 3])
            temp_path = f.name
        
        try:
            # Test that kwargs don't cause errors (even though they may not be used)
            loaded_data = _load_hdf5(temp_path, some_unused_kwarg=True, another_kwarg='test')
            
            # Verify data is still loaded correctly
            assert 'data' in loaded_data
            np.testing.assert_array_equal(loaded_data['data'], [1, 2, 3])
            
        finally:
            os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_hdf5.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-07-12 07:04:14 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_hdf5.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/io/_load_modules/_hdf5.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import time
# 
# import h5py
# import numpy as np
# 
# from .._save_modules._hdf5 import SWMRFile
# 
# 
# def _load_hdf5(lpath, key=None, swmr=True, max_retries=10, **kwargs):
#     """Load HDF5 file with SWMR support."""
#     for attempt in range(max_retries):
#         try:
#             with SWMRFile(lpath, "r", swmr=swmr) as h5_file:
#                 if key:
#                     if key not in h5_file:
#                         return None
#                     target = h5_file[key]
#                 else:
#                     target = h5_file
# 
#                 # Load data recursively
#                 return _load_h5_object(target)
# 
#         except (OSError, IOError) as e:
#             if attempt < max_retries - 1:
#                 time.sleep(0.1 * (2**attempt))
#             else:
#                 raise
# 
#     return None
# 
# 
# def _load_h5_object(h5_obj):
#     """Recursively load HDF5 object."""
#     if isinstance(h5_obj, h5py.Group):
#         result = {}
#         # Load datasets
#         for key in h5_obj.keys():
#             result[key] = _load_h5_object(h5_obj[key])
#         # Load attributes
#         for key in h5_obj.attrs.keys():
#             result[f"_attr_{key}"] = h5_obj.attrs[key]
#         return result
# 
#     elif isinstance(h5_obj, h5py.Dataset):
#         data = h5_obj[()]
# 
#         # Handle different data types
#         if isinstance(data, bytes):
#             return data.decode("utf-8")
#         elif isinstance(data, np.void):
#             # Unpickle data
#             import pickle
# 
#             return pickle.loads(data.tobytes())
#         else:
#             return data
#     else:
#         return h5_obj
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_hdf5.py
# --------------------------------------------------------------------------------
