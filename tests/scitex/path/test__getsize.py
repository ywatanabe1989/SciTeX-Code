#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 19:54:02 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/path/test__getsize.py

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


def test_getsize_existing_file():
    """Test getsize with existing file."""
    from scitex.path import getsize
    
    # Create temporary file with known content
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        content = "Hello, World!"
        f.write(content)
        temp_path = f.name
    
    try:
        size = getsize(temp_path)
        assert size == len(content.encode())
        assert isinstance(size, int)
    finally:
        os.unlink(temp_path)


def test_getsize_empty_file():
    """Test getsize with empty file."""
    from scitex.path import getsize
    
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
    
    try:
        size = getsize(temp_path)
        assert size == 0
    finally:
        os.unlink(temp_path)


def test_getsize_large_file():
    """Test getsize with larger file."""
    from scitex.path import getsize
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        # Write 1MB of data
        data = b'x' * (1024 * 1024)
        f.write(data)
        temp_path = f.name
    
    try:
        size = getsize(temp_path)
        assert size == 1024 * 1024
    finally:
        os.unlink(temp_path)


def test_getsize_nonexistent_file():
    """Test getsize with non-existent file."""
    from scitex.path import getsize
    
    nonexistent_path = "/path/that/does/not/exist/file.txt"
    size = getsize(nonexistent_path)
    assert np.isnan(size)


def test_getsize_directory():
    """Test getsize with directory."""
    from scitex.path import getsize
    
    with tempfile.TemporaryDirectory() as temp_dir:
        size = getsize(temp_dir)
        # Directory size varies by filesystem
        assert isinstance(size, int)
        assert size >= 0


def test_getsize_symlink():
    """Test getsize with symlink."""
    from scitex.path import getsize
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Symlink target content")
        target_path = f.name
    
    with tempfile.TemporaryDirectory() as temp_dir:
        symlink_path = os.path.join(temp_dir, "symlink")
        
        try:
            os.symlink(target_path, symlink_path)
            
            # getsize should return size of symlink itself, not target
            size = getsize(symlink_path)
            assert isinstance(size, int)
            assert size > 0
        finally:
            os.unlink(target_path)


def test_getsize_pathlib_path():
    """Test getsize with pathlib.Path object."""
    from scitex.path import getsize
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Pathlib test")
        temp_path = Path(f.name)
    
    try:
        size = getsize(temp_path)
        assert size == len("Pathlib test".encode())
    finally:
        os.unlink(str(temp_path))


def test_getsize_binary_file():
    """Test getsize with binary file."""
    from scitex.path import getsize
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        binary_data = bytes(range(256))
        f.write(binary_data)
        temp_path = f.name
    
    try:
        size = getsize(temp_path)
        assert size == 256
    finally:
        os.unlink(temp_path)


def test_getsize_unicode_filename():
    """Test getsize with unicode filename."""
    from scitex.path import getsize
    
    with tempfile.TemporaryDirectory() as temp_dir:
        unicode_path = os.path.join(temp_dir, "文件名.txt")
        
        with open(unicode_path, 'w', encoding='utf-8') as f:
            f.write("Unicode filename test")
        
        size = getsize(unicode_path)
        assert size == len("Unicode filename test".encode('utf-8'))


def test_getsize_permission_error():
    """Test getsize with permission error."""
    from scitex.path import getsize
    
    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                getsize("/restricted/file")


def test_getsize_special_files():
    """Test getsize with special files like /dev/null."""
    from scitex.path import getsize
    
    if os.path.exists("/dev/null"):
        size = getsize("/dev/null")
        assert size == 0


def test_getsize_relative_path():
    """Test getsize with relative path."""
    from scitex.path import getsize
    
    current_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        try:
            # Create file with relative path
            with open("relative_test.txt", 'w') as f:
                f.write("Relative path test")
            
            size = getsize("relative_test.txt")
            assert size == len("Relative path test".encode())
        finally:
            os.chdir(current_dir)


def test_getsize_spaces_in_path():
    """Test getsize with spaces in path."""
    from scitex.path import getsize
    
    with tempfile.TemporaryDirectory() as temp_dir:
        path_with_spaces = os.path.join(temp_dir, "file with spaces.txt")
        
        with open(path_with_spaces, 'w') as f:
            f.write("Spaces in filename")
        
        size = getsize(path_with_spaces)
        assert size == len("Spaces in filename".encode())


def test_getsize_empty_string():
    """Test getsize with empty string path."""
    from scitex.path import getsize
    
    size = getsize("")
    assert np.isnan(size)


def test_getsize_none_path():
    """Test getsize with None path."""
    from scitex.path import getsize
    
    with pytest.raises(TypeError):
        getsize(None)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_getsize.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 19:54:02 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_getsize.py
# 
# import os
# 
# import numpy as np
# 
# 
# def getsize(path):
#     if os.path.exists(path):
#         return os.path.getsize(path)
#     else:
#         return np.nan
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_getsize.py
# --------------------------------------------------------------------------------
