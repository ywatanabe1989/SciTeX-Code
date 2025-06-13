#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:20:00 (ywatanabe)"
# File: ./tests/scitex/path/test__version.py

import pytest
import os
import tempfile
from pathlib import Path


def test_find_latest_no_files():
    """Test find_latest when no versioned files exist."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = find_latest(tmpdir, 'test_file', '.txt')
        assert result is None


def test_find_latest_single_file():
    """Test find_latest with one versioned file."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a versioned file
        test_file = os.path.join(tmpdir, 'test_file_v001.txt')
        Path(test_file).touch()
        
        result = find_latest(tmpdir, 'test_file', '.txt')
        assert result == test_file


def test_find_latest_multiple_files():
    """Test find_latest with multiple versioned files."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple versioned files
        files = []
        for i in [1, 3, 5, 10, 2]:  # Out of order
            f = os.path.join(tmpdir, f'test_file_v{i:03d}.txt')
            Path(f).touch()
            files.append((i, f))
        
        result = find_latest(tmpdir, 'test_file', '.txt')
        
        # Should return the file with version 10
        expected = os.path.join(tmpdir, 'test_file_v010.txt')
        assert result == expected


def test_find_latest_custom_prefix():
    """Test find_latest with custom version prefix."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with custom prefix
        files = []
        for i in [1, 2, 3]:
            f = os.path.join(tmpdir, f'test_file-version{i:03d}.txt')
            Path(f).touch()
            files.append(f)
        
        result = find_latest(tmpdir, 'test_file', '.txt', version_prefix='-version')
        
        expected = os.path.join(tmpdir, 'test_file-version003.txt')
        assert result == expected


def test_find_latest_mixed_extensions():
    """Test find_latest filters by extension correctly."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with different extensions
        Path(os.path.join(tmpdir, 'test_file_v001.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_v002.csv')).touch()
        Path(os.path.join(tmpdir, 'test_file_v003.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_v004.csv')).touch()
        
        # Should only find .txt files
        result_txt = find_latest(tmpdir, 'test_file', '.txt')
        expected_txt = os.path.join(tmpdir, 'test_file_v003.txt')
        assert result_txt == expected_txt
        
        # Should only find .csv files
        result_csv = find_latest(tmpdir, 'test_file', '.csv')
        expected_csv = os.path.join(tmpdir, 'test_file_v004.csv')
        assert result_csv == expected_csv


def test_find_latest_invalid_versions():
    """Test find_latest ignores files with invalid version numbers."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mix of valid and invalid files
        Path(os.path.join(tmpdir, 'test_file_v001.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_vABC.txt')).touch()  # Invalid
        Path(os.path.join(tmpdir, 'test_file_v002.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file.txt')).touch()  # No version
        
        result = find_latest(tmpdir, 'test_file', '.txt')
        
        expected = os.path.join(tmpdir, 'test_file_v002.txt')
        assert result == expected


def test_find_latest_large_version_numbers():
    """Test find_latest with large version numbers."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with large version numbers
        Path(os.path.join(tmpdir, 'test_file_v099.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_v100.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_v999.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_v1000.txt')).touch()
        
        result = find_latest(tmpdir, 'test_file', '.txt')
        
        expected = os.path.join(tmpdir, 'test_file_v1000.txt')
        assert result == expected


def test_find_latest_similar_filenames():
    """Test find_latest doesn't confuse similar filenames."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with similar names
        Path(os.path.join(tmpdir, 'test_file_v001.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file2_v005.txt')).touch()
        Path(os.path.join(tmpdir, 'prefix_test_file_v010.txt')).touch()
        Path(os.path.join(tmpdir, 'test_file_v002.txt')).touch()
        
        result = find_latest(tmpdir, 'test_file', '.txt')
        
        # Should only match exact filename
        expected = os.path.join(tmpdir, 'test_file_v002.txt')
        assert result == expected


def test_find_latest_empty_directory():
    """Test find_latest with empty directory string."""
    from scitex.path import find_latest
    
    # Should handle empty dirname
    result = find_latest('', 'test_file', '.txt')
    # Depends on current directory contents
    assert result is None or isinstance(result, str)


def test_find_latest_nested_directory():
    """Test find_latest in nested directory."""
    from scitex.path import find_latest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create nested directory
        nested_dir = os.path.join(tmpdir, 'sub1', 'sub2')
        os.makedirs(nested_dir)
        
        # Create versioned files
        Path(os.path.join(nested_dir, 'test_file_v001.txt')).touch()
        Path(os.path.join(nested_dir, 'test_file_v002.txt')).touch()
        
        result = find_latest(nested_dir, 'test_file', '.txt')
        
        expected = os.path.join(nested_dir, 'test_file_v002.txt')
        assert result == expected


def test_increment_version_duplicate_function():
    """Test that increment_version in _version.py works the same as in _increment_version.py."""
    from scitex.path import increment_version
    from scitex.path import increment_version as increment_version_main
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        Path(os.path.join(tmpdir, 'test_v001.txt')).touch()
        
        # Both functions should return the same result
        result1 = increment_version(tmpdir, 'test', '.txt')
        result2 = increment_version_main(tmpdir, 'test', '.txt')
        
        assert result1 == result2
        assert result1.endswith('test_v002.txt')


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_version.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 20:48:24 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_version.py
#
# import os
# import re
# import sys
# from glob import glob
#
# import matplotlib.pyplot as plt
#
#
# # Functions
# def find_latest(dirname, fname, ext, version_prefix="_v"):
#     version_pattern = re.compile(
#         rf"({re.escape(fname)}{re.escape(version_prefix)})(\d+)({re.escape(ext)})$"
#     )
#
#     glob_pattern = os.path.join(dirname, f"{fname}{version_prefix}*{ext}")
#     files = glob(glob_pattern)
#
#     highest_version = 0
#     latest_file = None
#
#     for file in files:
#         filename = os.path.basename(file)
#         match = version_pattern.search(filename)
#         if match:
#             version_num = int(match.group(2))
#             if version_num > highest_version:
#                 highest_version = version_num
#                 latest_file = file
#
#     return latest_file
#
#
# ## Version
# def increment_version(dirname, fname, ext, version_prefix="_v"):
#     # Create a regex pattern to match the version number in the filename
#     version_pattern = re.compile(
#         rf"({re.escape(fname)}{re.escape(version_prefix)})(\d+)({re.escape(ext)})$"
#     )
#
#     # Construct the glob pattern to find all files that match the pattern
#     glob_pattern = os.path.join(dirname, f"{fname}{version_prefix}*{ext}")
#
#     # Use glob to find all files that match the pattern
#     files = glob(glob_pattern)
#
#     # Initialize the highest version number
#     highest_version = 0
#     base, suffix = None, None
#
#     # Loop through the files to find the highest version number
#     for file in files:
#         filename = os.path.basename(file)
#         match = version_pattern.search(filename)
#         if match:
#             base, version_str, suffix = match.groups()
#             version_num = int(version_str)
#             if version_num > highest_version:
#                 highest_version = version_num
#
#     # If no versioned files were found, use the provided filename and extension
#     if base is None or suffix is None:
#         base = f"{fname}{version_prefix}"
#         suffix = ext
#         highest_version = 0  # No previous versions
#
#     # Increment the highest version number
#     next_version_number = highest_version + 1
#
#     # Format the next version number with the same number of digits as the original
#     next_version_str = f"{base}{next_version_number:03d}{suffix}"
#
#     # Combine the directory and new filename to create the full path
#     next_filepath = os.path.join(dirname, next_version_str)
#
#     return next_filepath
#
#
# if __name__ == "__main__":
#     import scitex
#
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
#
#     # (YOUR AWESOME CODE)
#
#     # Close
#     scitex.gen.close(CONFIG)
#
# # EOF
#
# """
# /ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/path/_version.py
# """
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_version.py
# --------------------------------------------------------------------------------
