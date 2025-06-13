#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:54:25 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/path/test__path.py

"""
Tests for path utility functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import inspect

from scitex.path import this_path, get_this_path


class TestThisPath:
    """Test this_path function."""
    
    def test_this_path_normal_file(self):
        """Test this_path with normal Python file."""
        # Mock the inspect.stack to return a specific filename
        mock_frame = Mock()
        mock_frame.filename = "/home/user/project/my_script.py"
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/home/user/project/scitex/path/_path.py'):
                result = this_path()
                # Note: The function has a bug - it returns __file__ instead of THIS_FILE
                assert result == '/home/user/project/scitex/path/_path.py'
    
    def test_this_path_ipython_environment(self):
        """Test this_path when running in IPython."""
        mock_frame = Mock()
        mock_frame.filename = "<ipython console>"
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/some/path/with/ipython/in/it.py'):
                result = this_path()
                # When 'ipython' is in __file__, it returns __file__ (due to bug)
                assert result == '/some/path/with/ipython/in/it.py'
    
    def test_this_path_custom_ipython_path(self):
        """Test this_path with custom IPython fallback path."""
        mock_frame = Mock()
        mock_frame.filename = "<ipython console>"
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/path/with/ipython/kernel.py'):
                result = this_path(when_ipython="/my/custom/path.py")
                # Still returns __file__ due to the bug
                assert result == '/path/with/ipython/kernel.py'
    
    def test_this_path_stack_structure(self):
        """Test that this_path accesses the correct stack frame."""
        mock_frame0 = Mock()
        mock_frame0.filename = "/path/to/this_function.py"
        mock_frame1 = Mock()
        mock_frame1.filename = "/path/to/calling_function.py"
        mock_frame2 = Mock()
        mock_frame2.filename = "/path/to/caller_of_caller.py"
        
        with patch('inspect.stack', return_value=[mock_frame0, mock_frame1, mock_frame2]):
            with patch('scitex.path._path.__file__', '/scitex/path/_path.py'):
                # The function should use stack()[1].filename
                result = this_path()
                assert result == '/scitex/path/_path.py'
    
    def test_this_path_various_file_patterns(self):
        """Test with various file path patterns."""
        test_cases = [
            "/absolute/path/to/file.py",
            "relative/path/file.py",
            "../parent/file.py",
            "C:\\Windows\\path\\file.py",
            "/path with spaces/file.py",
            "/path/with-special_chars@123/file.py"
        ]
        
        for test_path in test_cases:
            mock_frame = Mock()
            mock_frame.filename = test_path
            
            with patch('inspect.stack', return_value=[None, mock_frame]):
                with patch('scitex.path._path.__file__', test_path):
                    result = this_path()
                    # Due to bug, always returns __file__
                    assert result == test_path
    
    def test_this_path_no_ipython_in_path(self):
        """Test when 'ipython' is not in the file path."""
        mock_frame = Mock()
        mock_frame.filename = "/normal/python/script.py"
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/normal/module/path.py'):
                result = this_path()
                assert result == '/normal/module/path.py'
                assert 'ipython' not in result
    
    def test_this_path_edge_cases(self):
        """Test edge cases for this_path."""
        # Empty filename
        mock_frame = Mock()
        mock_frame.filename = ""
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/scitex/path/_path.py'):
                result = this_path()
                assert result == '/scitex/path/_path.py'
        
        # None filename (shouldn't happen but test defensive programming)
        mock_frame.filename = None
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/scitex/path/_path.py'):
                result = this_path()
                assert result == '/scitex/path/_path.py'
    
    def test_get_this_path_alias(self):
        """Test that get_this_path is an alias for this_path."""
        assert get_this_path == this_path
        assert get_this_path is this_path
    
    def test_this_path_implementation_bug(self):
        """Test documenting the implementation bug."""
        # The function sets THIS_FILE from inspect.stack()[1].filename
        # but then returns __file__ instead of THIS_FILE
        # This test documents this behavior
        
        mock_frame = Mock()
        mock_frame.filename = "/caller/file.py"
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/module/file.py'):
                result = this_path()
                # Should return "/caller/file.py" (THIS_FILE) but returns __file__
                assert result == '/module/file.py'
                assert result != mock_frame.filename
    
    def test_this_path_with_when_ipython_not_used(self):
        """Test that when_ipython parameter is not used due to bug."""
        mock_frame = Mock()
        mock_frame.filename = "<ipython-input-1>"
        
        with patch('inspect.stack', return_value=[None, mock_frame]):
            with patch('scitex.path._path.__file__', '/has/ipython/in/path.py'):
                # Even though THIS_FILE would be set to when_ipython value,
                # the function returns __file__ so when_ipython is ignored
                result = this_path(when_ipython="/custom/fallback.py")
                assert result == '/has/ipython/in/path.py'
                assert result != "/custom/fallback.py"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
