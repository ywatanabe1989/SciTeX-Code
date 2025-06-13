#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 12:45:00 (ywatanabe)"
# File: ./tests/scitex/path/test__get_spath.py

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
import shutil


def test_get_spath_default():
    """Test get_spath with default arguments."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            # Mock the stack to avoid issues with __file__
            mock_stack.return_value = [None, MagicMock(filename='/test/path/script.py')]
            mock_split.return_value = ('/test/path/', 'test_file', '.py')
            
            # Patch __file__ in the module
            with patch('scitex.path._get_spath.__file__', '/test/path/module.py'):
                result = get_spath()
                
                assert isinstance(result, str)
                assert result.endswith('test_file/.')
                mock_split.assert_called()


def test_get_spath_with_filename():
    """Test get_spath with specific filename."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/path/', 'module', '.py')
            
            with patch('scitex.path._get_spath.__file__', '/test/path/module.py'):
                result = get_spath('output.txt')
                
                assert result.endswith('module/output.txt')


def test_get_spath_makedirs_false():
    """Test get_spath without creating directories."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            with patch('os.makedirs') as mock_makedirs:
                mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
                mock_split.return_value = ('/test/', 'file', '.py')
                
                with patch('scitex.path._get_spath.__file__', '/test/module.py'):
                    result = get_spath(makedirs=False)
                    
                    # makedirs should not be called when makedirs=False
                    mock_makedirs.assert_not_called()


def test_get_spath_makedirs_true():
    """Test get_spath with directory creation."""
from scitex.path import get_spath
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test_module.py')
        
        with patch('scitex.path._get_spath.split') as mock_split:
            with patch('inspect.stack') as mock_stack:
                mock_stack.return_value = [None, MagicMock(filename=test_file)]
                
                # Return proper split values
                def split_side_effect(path):
                    if path == test_file:
                        return (tmpdir + '/', 'test_module', '.py')
                    else:
                        # For the spath
                        dir_part = os.path.dirname(path)
                        if not dir_part.endswith('/'):
                            dir_part += '/'
                        return (dir_part, os.path.basename(path), '')
                
                mock_split.side_effect = split_side_effect
                
                with patch('scitex.path._get_spath.__file__', test_file):
                    result = get_spath('subdir/output.txt', makedirs=True)
                    
                    # Check that the subdirectory was created
                    expected_dir = os.path.join(tmpdir, 'test_module', 'subdir')
                    assert os.path.exists(expected_dir)


def test_get_spath_ipython_environment():
    """Test get_spath in iPython environment."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            with patch.dict(os.environ, {'USER': 'testuser'}):
                mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
                mock_split.return_value = ('/test/', 'file', '.py')
                
                # Simulate ipython environment
                with patch('scitex.path._get_spath.__file__', '/path/to/ipython/module.py'):
                    result = get_spath()
                    
                    assert isinstance(result, str)
                    # Should still work even in ipython context


def test_get_spath_nested_directory():
    """Test get_spath with nested directory in filename."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._get_spath.__file__', '/test/module.py'):
                result = get_spath('subdir1/subdir2/file.txt')
                
                assert result.endswith('module/subdir1/subdir2/file.txt')


def test_get_spath_absolute_path_input():
    """Test get_spath with absolute path as input."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._get_spath.__file__', '/test/module.py'):
                # Even with absolute path, it should be treated as relative to module dir
                result = get_spath('/absolute/path/file.txt')
                
                assert result.endswith('module//absolute/path/file.txt')


def test_get_spath_empty_filename():
    """Test get_spath with empty filename."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._get_spath.__file__', '/test/module.py'):
                result = get_spath('')
                
                assert result.endswith('module/')


def test_get_spath_with_dot_directories():
    """Test get_spath with dot directories in path."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._get_spath.__file__', '/test/module.py'):
                result = get_spath('./relative/path.txt')
                
                assert result.endswith('module/./relative/path.txt')


def test_get_spath_with_parent_directory():
    """Test get_spath with parent directory notation."""
from scitex.path import get_spath
    
    with patch('scitex.path._get_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._get_spath.__file__', '/test/module.py'):
                result = get_spath('../sibling/file.txt')
                
                assert result.endswith('module/../sibling/file.txt')


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_get_spath.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 20:51:29 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_get_spath.py
#
# import inspect
# import os
#
# from ._split import split
#
#
# def get_spath(sfname=".", makedirs=False):
#
#     # if __IPYTHON__:
#     #     THIS_FILE = f'/tmp/{os.getenv("USER")}.py'
#     # else:
#     #     THIS_FILE = inspect.stack()[1].filename
#
#     THIS_FILE = inspect.stack()[1].filename
#     if "ipython" in __file__:  # for ipython
#         THIS_FILE = f'/tmp/{os.getenv("USER")}.py'
#
#     ## spath
#     fpath = __file__
#     fdir, fname, _ = split(fpath)
#     sdir = fdir + fname + "/"
#     spath = sdir + sfname
#
#     if makedirs:
#         os.makedirs(split(spath)[0], exist_ok=True)
#
#     return spath
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_get_spath.py
# --------------------------------------------------------------------------------
