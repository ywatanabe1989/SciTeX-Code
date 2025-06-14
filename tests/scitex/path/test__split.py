#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:10:00 (ywatanabe)"
# File: ./tests/scitex/path/test__split.py

import pytest
import os
from pathlib import Path


def test_split_basic():
    """Test split with basic file path."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path/to/file.txt')
    
    assert dirname == '/path/to/'
    assert fname == 'file'
    assert ext == '.txt'


def test_split_relative_path():
    """Test split with relative path."""
    from scitex.path import split
    
    dirname, fname, ext = split('../data/01/day1/split_octave/2kHz_mat/tt8-2.mat')
    
    assert dirname == '../data/01/day1/split_octave/2kHz_mat/'
    assert fname == 'tt8-2'
    assert ext == '.mat'


def test_split_no_extension():
    """Test split with file without extension."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path/to/README')
    
    assert dirname == '/path/to/'
    assert fname == 'README'
    assert ext == ''


def test_split_multiple_dots():
    """Test split with filename containing multiple dots."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path/to/file.backup.tar.gz')
    
    assert dirname == '/path/to/'
    assert fname == 'file.backup.tar'
    assert ext == '.gz'


def test_split_hidden_file():
    """Test split with hidden file (starting with dot)."""
    from scitex.path import split
    
    dirname, fname, ext = split('/home/user/.bashrc')
    
    assert dirname == '/home/user/'
    assert fname == '.bashrc'
    assert ext == ''


def test_split_hidden_file_with_extension():
    """Test split with hidden file that has extension."""
    from scitex.path import split
    
    dirname, fname, ext = split('/home/user/.config.yaml')
    
    assert dirname == '/home/user/'
    assert fname == '.config'
    assert ext == '.yaml'


def test_split_root_directory():
    """Test split with file in root directory."""
    from scitex.path import split
    
    dirname, fname, ext = split('/file.txt')
    
    assert dirname == '/'
    assert fname == 'file'
    assert ext == '.txt'


def test_split_current_directory():
    """Test split with file in current directory."""
    from scitex.path import split
    
    dirname, fname, ext = split('file.txt')
    
    assert dirname == '/'  # When no directory, returns '/'
    assert fname == 'file'
    assert ext == '.txt'


def test_split_trailing_slash():
    """Test split with path ending in slash (directory)."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path/to/directory/')
    
    assert dirname == '/path/to/directory/'
    assert fname == ''
    assert ext == ''


def test_split_windows_path():
    """Test split with Windows-style path."""
    from scitex.path import split
    
    # Note: os.path handles this based on the OS
    if os.name == 'nt':
        dirname, fname, ext = split('C:\\Users\\user\\file.txt')
        assert dirname == 'C:\\Users\\user\\'
        assert fname == 'file'
        assert ext == '.txt'
    else:
        # On Unix, backslashes are part of filename
        dirname, fname, ext = split('C:\\Users\\user\\file.txt')
        # Behavior depends on OS


def test_split_empty_path():
    """Test split with empty path."""
    from scitex.path import split
    
    dirname, fname, ext = split('')
    
    assert dirname == '/'
    assert fname == ''
    assert ext == ''


def test_split_special_characters():
    """Test split with special characters in filename."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path/to/file[with]special(chars).txt')
    
    assert dirname == '/path/to/'
    assert fname == 'file[with]special(chars)'
    assert ext == '.txt'


def test_split_unicode_characters():
    """Test split with unicode characters."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path/to/ファイル.txt')
    
    assert dirname == '/path/to/'
    assert fname == 'ファイル'
    assert ext == '.txt'


def test_split_spaces_in_path():
    """Test split with spaces in path and filename."""
    from scitex.path import split
    
    dirname, fname, ext = split('/path with spaces/file name.txt')
    
    assert dirname == '/path with spaces/'
    assert fname == 'file name'
    assert ext == '.txt'


def test_split_double_extension():
    """Test split behavior with double extensions."""
    from scitex.path import split
    
    # Only the last extension is considered
    dirname, fname, ext = split('/path/to/archive.tar.gz')
    
    assert dirname == '/path/to/'
    assert fname == 'archive.tar'
    assert ext == '.gz'


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_split.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 16:18:06 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_split.py
#
# import os
#
# def split(fpath):
#     """Split a file path to (1) the directory path, (2) the file name, and (3) the file extention
#     Example:
#         dirname, fname, ext = split('../data/01/day1/split_octave/2kHz_mat/tt8-2.mat')
#         print(dirname) # '../data/01/day1/split_octave/2kHz_mat/'
#         print(fname) # 'tt8-2'
#         print(ext) # '.mat'
#     """
#     dirname = os.path.dirname(fpath) + "/"
#     base = os.path.basename(fpath)
#     fname, ext = os.path.splitext(base)
#     return dirname, fname, ext
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_split.py
# --------------------------------------------------------------------------------
