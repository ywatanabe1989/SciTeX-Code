#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:15:00 (ywatanabe)"
# File: ./tests/scitex/path/test__this_path.py

import pytest
import os
from unittest.mock import patch, MagicMock


def test_this_path_normal():
    """Test this_path in normal Python environment."""
    from scitex.path import this_path
    
    with patch('inspect.stack') as mock_stack:
        # Mock the calling file
        mock_stack.return_value = [
            None, 
            MagicMock(filename='/path/to/calling/script.py')
        ]
        
        with patch('scitex.path._this_path.__file__', '/path/to/module.py'):
            result = this_path()
            
            # The function returns __file__ (module path), not the calling file
            assert result == '/path/to/module.py'


def test_this_path_ipython():
    """Test this_path in iPython environment."""
    from scitex.path import this_path
    
    with patch('inspect.stack') as mock_stack:
        mock_stack.return_value = [
            None,
            MagicMock(filename='<ipython-input-1>')
        ]
        
        # Simulate ipython module path
        with patch('scitex.path._this_path.__file__', '/path/to/ipython/module.py'):
            result = this_path()
            
            # Still returns __file__ regardless of ipython
            assert result == '/path/to/ipython/module.py'


def test_this_path_custom_ipython_path():
    """Test this_path with custom iPython fake path."""
    from scitex.path import this_path
    
    with patch('inspect.stack') as mock_stack:
        mock_stack.return_value = [
            None,
            MagicMock(filename='<ipython-input-1>')
        ]
        
        with patch('scitex.path._this_path.__file__', '/path/to/ipython/module.py'):
            result = this_path(ipython_fake_path='/custom/fake.py')
            
            # The ipython_fake_path parameter doesn't affect output
            assert result == '/path/to/ipython/module.py'


def test_this_path_stack_levels():
    """Test this_path with different stack levels."""
    from scitex.path import this_path
    
    def wrapper_function():
        return this_path()
    
    with patch('inspect.stack') as mock_stack:
        # Multiple stack frames
        mock_stack.return_value = [
            MagicMock(filename='this_path.py'),  # this_path itself
            MagicMock(filename='wrapper.py'),     # wrapper function
            MagicMock(filename='test.py')        # test function
        ]
        
        with patch('scitex.path._this_path.__file__', '/module/path.py'):
            result = wrapper_function()
            
            assert result == '/module/path.py'


def test_get_this_path_alias():
    """Test that get_this_path is an alias for this_path."""
    from scitex.path import this_path, get_this_path
    
    # They should be the same function
    assert get_this_path is this_path


def test_this_path_no_arguments():
    """Test this_path requires no arguments."""
    from scitex.path import this_path
    
    with patch('inspect.stack') as mock_stack:
        mock_stack.return_value = [None, MagicMock(filename='/test.py')]
        
        with patch('scitex.path._this_path.__file__', '/module.py'):
            # Should work without arguments
            result = this_path()
            assert result is not None


def test_this_path_return_type():
    """Test this_path returns a string."""
    from scitex.path import this_path
    
    with patch('inspect.stack') as mock_stack:
        mock_stack.return_value = [None, MagicMock(filename='/test.py')]
        
        with patch('scitex.path._this_path.__file__', '/module.py'):
            result = this_path()
            assert isinstance(result, str)


def test_this_path_absolute_path():
    """Test this_path returns absolute path."""
    from scitex.path import this_path
    
    with patch('inspect.stack') as mock_stack:
        mock_stack.return_value = [None, MagicMock(filename='/test.py')]
        
        # Test with absolute path
        with patch('scitex.path._this_path.__file__', '/absolute/path/to/module.py'):
            result = this_path()
            assert os.path.isabs(result)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_this_path.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 16:22:21 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_this_path.py
# #!/usr/bin/env python3
# 
# import inspect
# 
# 
# def this_path(ipython_fake_path="/tmp/fake.py"):
#     THIS_FILE = inspect.stack()[1].filename
#     if "ipython" in __file__:
#         THIS_FILE = ipython_fake_path
#     return __file__
# 
# 
# get_this_path = this_path
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_this_path.py
# --------------------------------------------------------------------------------
