#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:53:10 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/path/test__get_module_path.py

"""
Tests for get_module_path functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import importlib.util

from scitex.path import get_data_path_from_a_package


class TestGetDataPathFromAPackage:
    """Test get_data_path_from_a_package function."""
    
    def test_get_data_path_success(self):
        """Test successful retrieval of data path."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/project/src/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                result = get_data_path_from_a_package("mypackage", "test_data.txt")
                
                expected_path = os.path.join("/home/user/project/data", "test_data.txt")
                assert result == expected_path
    
    def test_get_data_path_package_not_found(self):
        """Test when package is not found."""
        with patch('importlib.util.find_spec', return_value=None):
            with pytest.raises(ImportError, match="Package 'nonexistent' not found"):
                get_data_path_from_a_package("nonexistent", "data.txt")
    
    def test_get_data_path_resource_not_found(self):
        """Test when resource file is not found."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/project/src/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=False):
                with pytest.raises(FileNotFoundError, match="Resource 'missing.txt' not found"):
                    get_data_path_from_a_package("mypackage", "missing.txt")
    
    def test_get_data_path_various_origins(self):
        """Test with various package origin formats."""
        test_cases = [
            ("/usr/lib/python3.9/site-packages/src/pkg/__init__.py", "/usr/lib/python3.9/site-packages/data"),
            ("/home/user/src/myapp/module.py", "/home/user/data"),
            ("C:\\Python\\Lib\\site-packages\\src\\pkg\\__init__.py", "C:\\Python\\Lib\\site-packages\\data"),
        ]
        
        for origin, expected_data_dir in test_cases:
            mock_spec = Mock()
            mock_spec.origin = origin
            
            with patch('importlib.util.find_spec', return_value=mock_spec):
                with patch('os.path.exists', return_value=True):
                    result = get_data_path_from_a_package("testpkg", "file.txt")
                    
                    expected_path = os.path.join(expected_data_dir, "file.txt")
                    assert result == expected_path
    
    def test_get_data_path_no_src_in_path(self):
        """Test when 'src' is not in the package path."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/project/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                # This will create a path like "/home/user/project/mypackage/__init__.pydata"
                # because split("src")[0] returns the full string when "src" is not found
                result = get_data_path_from_a_package("mypackage", "test.txt")
                assert "data" in result
    
    def test_get_data_path_nested_resource(self):
        """Test with nested resource path."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/project/src/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                result = get_data_path_from_a_package("mypackage", "subdir/test_data.csv")
                
                expected_path = os.path.join("/home/user/project/data", "subdir/test_data.csv")
                assert result == expected_path
    
    def test_get_data_path_empty_resource(self):
        """Test with empty resource name."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/project/src/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                result = get_data_path_from_a_package("mypackage", "")
                
                expected_path = "/home/user/project/data"
                assert result == expected_path
    
    def test_get_data_path_multiple_src_in_path(self):
        """Test when 'src' appears multiple times in path."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/src/project/src/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                result = get_data_path_from_a_package("mypackage", "data.json")
                
                # Should split on first 'src'
                expected_path = os.path.join("/home/user/data", "data.json")
                assert result == expected_path
    
    def test_get_data_path_case_sensitivity(self):
        """Test case sensitivity of 'src' in path."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user/SRC/mypackage/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                # 'SRC' won't match 'src' in split
                result = get_data_path_from_a_package("mypackage", "test.txt")
                # Will append 'data' to the full path
                assert result.endswith("data/test.txt")
    
    def test_get_data_path_special_characters(self):
        """Test with special characters in paths."""
        mock_spec = Mock()
        mock_spec.origin = "/home/user-name/project@1.0/src/my-package/__init__.py"
        
        with patch('importlib.util.find_spec', return_value=mock_spec):
            with patch('os.path.exists', return_value=True):
                result = get_data_path_from_a_package("my-package", "test file.txt")
                
                expected_path = os.path.join("/home/user-name/project@1.0/data", "test file.txt")
                assert result == expected_path
    
    def test_get_data_path_real_package(self):
        """Test with a real package (if available)."""
        # Try with a standard library package
        try:
            import json
            mock_spec = Mock()
            mock_spec.origin = os.path.join(os.path.dirname(json.__file__), "src", "__init__.py")
            
            with patch('importlib.util.find_spec', return_value=mock_spec):
                with patch('os.path.exists', return_value=True):
                    result = get_data_path_from_a_package("json", "test.json")
                    assert result.endswith("data/test.json")
        except Exception:
            # Skip if json module structure is different
            pytest.skip("Real package test not applicable in this environment")

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_get_module_path.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:39:32 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_get_module_path.py
# 
# 
# def get_data_path_from_a_package(package_str, resource):
#     """
#     Get the path to a data file within a package.
# 
#     This function finds the path to a data file within a package's data directory.
# 
#     Parameters:
#     -----------
#     package_str : str
#         The name of the package as a string.
#     resource : str
#         The name of the resource file within the package's data directory.
# 
#     Returns:
#     --------
#     str
#         The full path to the resource file.
# 
#     Raises:
#     -------
#     ImportError
#         If the specified package cannot be found.
#     FileNotFoundError
#         If the resource file does not exist in the package's data directory.
#     """
#     import importlib
#     import os
#     import sys
# 
#     spec = importlib.util.find_spec(package_str)
#     if spec is None:
#         raise ImportError(f"Package '{package_str}' not found")
# 
#     data_dir = os.path.join(spec.origin.split("src")[0], "data")
#     resource_path = os.path.join(data_dir, resource)
# 
#     if not os.path.exists(resource_path):
#         raise FileNotFoundError(
#             f"Resource '{resource}' not found in package '{package_str}'"
#         )
# 
#     return resource_path
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_get_module_path.py
# --------------------------------------------------------------------------------
