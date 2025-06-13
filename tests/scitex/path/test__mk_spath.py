#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:00:00 (ywatanabe)"
# File: ./tests/scitex/path/test__mk_spath.py

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
import shutil


def test_mk_spath_default():
    """Test mk_spath with default arguments."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            # Mock the stack to simulate calling from a script
            mock_stack.return_value = [None, MagicMock(filename='/test/path/script.py')]
            mock_split.return_value = ('/test/path/', 'module', '.py')
            
            # Patch __file__ in the module
            with patch('scitex.path._mk_spath.__file__', '/test/path/module.py'):
                result = mk_spath('output.txt')
                
                assert isinstance(result, str)
                assert result.endswith('module/output.txt')
                mock_split.assert_called()


def test_mk_spath_with_subdirectory():
    """Test mk_spath with subdirectory in filename."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._mk_spath.__file__', '/test/module.py'):
                result = mk_spath('subdir/output.txt')
                
                assert result.endswith('module/subdir/output.txt')


def test_mk_spath_makedirs_false():
    """Test mk_spath without creating directories."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            with patch('os.makedirs') as mock_makedirs:
                mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
                mock_split.return_value = ('/test/', 'module', '.py')
                
                with patch('scitex.path._mk_spath.__file__', '/test/module.py'):
                    result = mk_spath('output.txt', makedirs=False)
                    
                    # makedirs should not be called
                    mock_makedirs.assert_not_called()


def test_mk_spath_makedirs_true():
    """Test mk_spath with directory creation."""
    from scitex.path import mk_spath
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test_module.py')
        
        with patch('scitex.path._mk_spath.split') as mock_split:
            with patch('inspect.stack') as mock_stack:
                mock_stack.return_value = [None, MagicMock(filename=test_file)]
                
                # Define split behavior
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
                
                with patch('scitex.path._mk_spath.__file__', test_file):
                    result = mk_spath('subdir/output.txt', makedirs=True)
                    
                    # Check that directory was created
                    expected_dir = os.path.join(tmpdir, 'test_module', 'subdir')
                    assert os.path.exists(expected_dir)


def test_mk_spath_ipython_environment():
    """Test mk_spath in iPython environment."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            with patch.dict(os.environ, {'USER': 'testuser'}):
                mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
                mock_split.return_value = ('/test/', 'module', '.py')
                
                # Simulate ipython environment
                with patch('scitex.path._mk_spath.__file__', '/path/to/ipython/module.py'):
                    result = mk_spath('output.txt')
                    
                    assert isinstance(result, str)
                    # Should handle ipython case


def test_mk_spath_empty_filename():
    """Test mk_spath with empty filename."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._mk_spath.__file__', '/test/module.py'):
                result = mk_spath('')
                
                assert result.endswith('module/')


def test_mk_spath_multiple_levels():
    """Test mk_spath with multiple directory levels."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._mk_spath.__file__', '/test/module.py'):
                result = mk_spath('level1/level2/level3/output.txt')
                
                assert result.endswith('module/level1/level2/level3/output.txt')


def test_mk_spath_with_extension():
    """Test mk_spath with various file extensions."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._mk_spath.__file__', '/test/module.py'):
                # Test various extensions
                for ext in ['.txt', '.csv', '.json', '.tar.gz']:
                    result = mk_spath(f'output{ext}')
                    assert result.endswith(f'module/output{ext}')


def test_mk_spath_absolute_path():
    """Test mk_spath behavior with absolute path input."""
    from scitex.path import mk_spath
    
    with patch('scitex.path._mk_spath.split') as mock_split:
        with patch('inspect.stack') as mock_stack:
            mock_stack.return_value = [None, MagicMock(filename='/test/script.py')]
            mock_split.return_value = ('/test/', 'module', '.py')
            
            with patch('scitex.path._mk_spath.__file__', '/test/module.py'):
                # Even with absolute path, it gets appended
                result = mk_spath('/absolute/path/file.txt')
                
                assert result.endswith('module//absolute/path/file.txt')


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_mk_spath.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 20:59:46 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_mk_spath.py
#
# import inspect
# import os
#
# from ._split import split
#
#
#
# def mk_spath(sfname, makedirs=False):
#     """
#     Create a save path based on the calling script's location.
#
#     Parameters:
#     -----------
#     sfname : str
#         The name of the file to be saved.
#     makedirs : bool, optional
#         If True, create the directory structure for the save path. Default is False.
#
#     Returns:
#     --------
#     str
#         The full save path for the file.
#
#     Example:
#     --------
#     >>> import scitex.io._path as path
#     >>> spath = path.mk_spath('output.txt', makedirs=True)
#     >>> print(spath)
#     '/path/to/current/script/output.txt'
#     """
#     THIS_FILE = inspect.stack()[1].filename
#     if "ipython" in __file__:  # for ipython
#         THIS_FILE = f'/tmp/fake-{os.getenv("USER")}.py'
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
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_mk_spath.py
# --------------------------------------------------------------------------------
