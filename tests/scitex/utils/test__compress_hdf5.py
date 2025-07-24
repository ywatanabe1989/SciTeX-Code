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

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_compress_hdf5.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-10 08:26:28 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/utils/_compress_hdf5.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "/ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/utils/_compress_hdf5.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# import numpy as np
# 
# # h5py and tqdm imported in functions that need them
# 
# 
# def compress_hdf5(input_file, output_file=None, compression_level=4):
#     """
#     Compress an existing HDF5 file by reading all datasets and rewriting them with compression.
# 
#     Parameters:
#     -----------
#     input_file : str
#         Path to the input HDF5 file
#     output_file : str, optional
#         Path to the output compressed HDF5 file. If None, will use input_file + '.compressed.h5'
#     compression_level : int, optional
#         Compression level (1-9), higher means more compression but slower processing
#     """
#     # Import h5py when actually needed
#     try:
#         import h5py
#     except ImportError:
#         raise ImportError("h5py is required for HDF5 compression but not installed")
#     
#     # Import tqdm if available
#     try:
#         from tqdm import tqdm
#     except ImportError:
#         tqdm = None
#     if output_file is None:
#         base, ext = os.path.splitext(input_file)
#         output_file = f"{base}.compressed{ext}"
# 
#     print(f"Compressing {input_file} to {output_file}")
# 
#     with h5py.File(input_file, "r") as src, h5py.File(output_file, "w") as dst:
#         # Copy file attributes
#         for key, value in src.attrs.items():
#             dst.attrs[key] = value
# 
#         def copy_dataset(name, obj):
#             if isinstance(obj, h5py.Dataset):
#                 # Print progress for large datasets
#                 if len(obj.shape) > 0 and obj.shape[0] > 1000000:
#                     print(f"Processing large dataset {name} with shape {obj.shape}")
# 
#                 # Get original dataset attributes
#                 chunks = True  # Let h5py choose chunking
#                 if obj.chunks is not None:
#                     chunks = obj.chunks
# 
#                 # Create the compressed dataset
#                 compressed_data = dst.create_dataset(
#                     name,
#                     shape=obj.shape,
#                     dtype=obj.dtype,
#                     compression="gzip",
#                     compression_opts=compression_level,
#                     chunks=chunks,
#                 )
# 
#                 # Copy data and attributes
#                 if len(obj.shape) > 0 and obj.shape[0] > 10000000:
#                     # Process large datasets in chunks to avoid memory issues
#                     chunk_size = 5000000  # Adjust based on your available RAM
#                     for i in tqdm(
#                         range(0, obj.shape[0], chunk_size), desc=f"Copying {name}"
#                     ):
#                         end = min(i + chunk_size, obj.shape[0])
#                         if len(obj.shape) == 1:
#                             compressed_data[i:end] = obj[i:end]
#                         else:
#                             compressed_data[i:end, ...] = obj[i:end, ...]
#                 else:
#                     # Small enough to copy at once
#                     compressed_data[()] = obj[()]
# 
#                 # Copy dataset attributes
#                 for key, value in obj.attrs.items():
#                     compressed_data.attrs[key] = value
# 
#             elif isinstance(obj, h5py.Group):
#                 # Create group in destination file
#                 group = dst.create_group(name)
#                 # Copy group attributes
#                 for key, value in obj.attrs.items():
#                     group.attrs[key] = value
# 
#         # Process all objects in the file
#         src.visititems(copy_dataset)
# 
#     print(
#         f"Compression complete. Original size: {os.path.getsize(input_file)/1e9:.2f} GB, "
#         f"New size: {os.path.getsize(output_file)/1e9:.2f} GB"
#     )
# 
#     return output_file
# 
# 
# if __name__ == "__main__":
#     import argparse
# 
#     parser = argparse.ArgumentParser(
#         description="Compress existing HDF5 files with gzip compression"
#     )
#     parser.add_argument("input_file", help="Path to the input HDF5 file")
#     parser.add_argument(
#         "--output_file", help="Path to the output compressed HDF5 file", default=None
#     )
#     parser.add_argument(
#         "--compression", type=int, help="Compression level (1-9)", default=4
#     )
# 
#     args = parser.parse_args()
#     compress_hdf5(args.input_file, args.output_file, args.compression)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_compress_hdf5.py
# --------------------------------------------------------------------------------
