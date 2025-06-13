#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:10:00 (ywatanabe)"
# File: ./tests/scitex/utils/test__compress_hdf5.py

"""
Functionality:
    * Tests HDF5 file compression functionality
    * Validates compression levels and file integrity
    * Tests chunked processing for large datasets
Input:
    * Test HDF5 files with various data types
Output:
    * Test results
Prerequisites:
    * pytest
    * h5py
    * numpy
"""

import os
import tempfile
import h5py
import numpy as np
import pytest
from unittest.mock import patch, mock_open
from scitex.utils import compress_hdf5


class TestCompressHDF5:
    """Test cases for HDF5 compression functionality."""

    @pytest.fixture
    def sample_h5_file(self):
        """Create a sample HDF5 file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as tmp:
            filename = tmp.name
        
        with h5py.File(filename, 'w') as f:
            # Add file attributes
            f.attrs['title'] = 'Test HDF5 File'
            f.attrs['version'] = 1.0
            
            # Create datasets with different sizes
            f.create_dataset('small_data', data=np.random.random((100, 50)))
            f.create_dataset('medium_data', data=np.random.random((1000, 100)))
            
            # Create dataset with attributes
            dset = f.create_dataset('data_with_attrs', data=np.random.random((10, 10)))
            dset.attrs['description'] = 'Test dataset'
            dset.attrs['units'] = 'meters'
            
            # Create groups
            grp = f.create_group('test_group')
            grp.attrs['group_attr'] = 'test_value'
            grp.create_dataset('nested_data', data=np.arange(50))
        
        yield filename
        os.unlink(filename)

    def test_compress_hdf5_basic(self, sample_h5_file):
        """Test basic HDF5 compression functionality."""
        with tempfile.NamedTemporaryFile(suffix='.compressed.h5', delete=False) as tmp:
            output_file = tmp.name
        
        try:
            result = compress_hdf5(sample_h5_file, output_file)
            
            assert result == output_file
            assert os.path.exists(output_file)
            
            # Verify compressed file structure
            with h5py.File(output_file, 'r') as f:
                assert 'small_data' in f
                assert 'medium_data' in f
                assert 'data_with_attrs' in f
                assert 'test_group' in f
                assert 'test_group/nested_data' in f
                
                # Check file attributes
                assert f.attrs['title'] == 'Test HDF5 File'
                assert f.attrs['version'] == 1.0
                
                # Check dataset attributes
                assert f['data_with_attrs'].attrs['description'] == 'Test dataset'
                assert f['data_with_attrs'].attrs['units'] == 'meters'
                
                # Check group attributes
                assert f['test_group'].attrs['group_attr'] == 'test_value'
        
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_compress_hdf5_auto_output_name(self, sample_h5_file):
        """Test automatic output filename generation."""
        result = compress_hdf5(sample_h5_file)
        
        expected_output = sample_h5_file.replace('.h5', '.compressed.h5')
        assert result == expected_output
        assert os.path.exists(expected_output)
        
        os.unlink(expected_output)

    def test_compress_hdf5_compression_levels(self, sample_h5_file):
        """Test different compression levels."""
        outputs = []
        
        try:
            # Test different compression levels
            for level in [1, 5, 9]:
                with tempfile.NamedTemporaryFile(suffix=f'.level{level}.h5', delete=False) as tmp:
                    output_file = tmp.name
                    outputs.append(output_file)
                
                result = compress_hdf5(sample_h5_file, output_file, compression_level=level)
                assert result == output_file
                assert os.path.exists(output_file)
                
                # Verify file is readable and has correct compression
                with h5py.File(output_file, 'r') as f:
                    # Check that datasets have compression
                    for name in ['small_data', 'medium_data']:
                        assert f[name].compression == 'gzip'
                        assert f[name].compression_opts == level
        
        finally:
            for output_file in outputs:
                if os.path.exists(output_file):
                    os.unlink(output_file)

    @patch('builtins.print')
    def test_compress_hdf5_large_dataset_chunking(self, mock_print, sample_h5_file):
        """Test chunked processing for large datasets."""
        # Create a file with a large dataset
        large_file = sample_h5_file.replace('.h5', '_large.h5')
        
        try:
            with h5py.File(large_file, 'w') as f:
                # Create dataset larger than 10M elements to trigger chunking
                large_data = np.random.random((15000000,))  # > 10M elements
                f.create_dataset('large_data', data=large_data)
            
            with tempfile.NamedTemporaryFile(suffix='.compressed.h5', delete=False) as tmp:
                output_file = tmp.name
            
            result = compress_hdf5(large_file, output_file)
            
            # Verify chunked processing was triggered
            mock_print.assert_any_call(f"Compressing {large_file} to {output_file}")
            
            # Verify the large dataset was copied correctly
            with h5py.File(output_file, 'r') as f:
                assert 'large_data' in f
                assert f['large_data'].shape == (15000000,)
            
            os.unlink(output_file)
        
        finally:
            if os.path.exists(large_file):
                os.unlink(large_file)

    def test_compress_hdf5_data_integrity(self, sample_h5_file):
        """Test that data integrity is preserved during compression."""
        with tempfile.NamedTemporaryFile(suffix='.compressed.h5', delete=False) as tmp:
            output_file = tmp.name
        
        try:
            # Get original data
            with h5py.File(sample_h5_file, 'r') as f:
                original_small = f['small_data'][()]
                original_medium = f['medium_data'][()]
                original_nested = f['test_group/nested_data'][()]
            
            # Compress
            compress_hdf5(sample_h5_file, output_file)
            
            # Verify data integrity
            with h5py.File(output_file, 'r') as f:
                compressed_small = f['small_data'][()]
                compressed_medium = f['medium_data'][()]
                compressed_nested = f['test_group/nested_data'][()]
                
                np.testing.assert_array_equal(original_small, compressed_small)
                np.testing.assert_array_equal(original_medium, compressed_medium)
                np.testing.assert_array_equal(original_nested, compressed_nested)
        
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_compress_hdf5_nonexistent_file(self):
        """Test handling of nonexistent input file."""
        nonexistent_file = '/path/to/nonexistent/file.h5'
        
        with pytest.raises(OSError):
            compress_hdf5(nonexistent_file)

    @patch('builtins.print')
    def test_compress_hdf5_progress_messages(self, mock_print, sample_h5_file):
        """Test that progress messages are printed correctly."""
        with tempfile.NamedTemporaryFile(suffix='.compressed.h5', delete=False) as tmp:
            output_file = tmp.name
        
        try:
            compress_hdf5(sample_h5_file, output_file)
            
            # Check compression start message
            mock_print.assert_any_call(f"Compressing {sample_h5_file} to {output_file}")
            
            # Check completion message (should contain size info)
            completion_calls = [call for call in mock_print.call_args_list 
                              if 'Compression complete' in str(call)]
            assert len(completion_calls) > 0
        
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
