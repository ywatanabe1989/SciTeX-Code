#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:53:35 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/path/test__find.py

"""
Tests for find functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import os
import fnmatch
import tempfile
import shutil

from scitex.path import find_git_root, find_dir, find_file, _find


class TestFindGitRoot:
    """Test find_git_root function."""
    
    def test_find_git_root_success(self):
        """Test successful git root finding."""
        mock_repo = Mock()
        mock_repo.working_tree_dir = "/home/user/my_project"
        
        with patch('git.Repo', return_value=mock_repo) as mock_git:
            result = find_git_root()
            
            mock_git.assert_called_once_with(".", search_parent_directories=True)
            assert result == "/home/user/my_project"
    
    def test_find_git_root_no_repo(self):
        """Test when no git repository is found."""
        import git
        
        with patch('git.Repo', side_effect=git.InvalidGitRepositoryError("Not a git repo")):
            with pytest.raises(git.InvalidGitRepositoryError):
                find_git_root()
    
    def test_find_git_root_nested_directory(self):
        """Test finding git root from nested directory."""
        mock_repo = Mock()
        mock_repo.working_tree_dir = "/home/user/project"
        
        with patch('git.Repo', return_value=mock_repo) as mock_git:
            # Even from nested directory, should find root
            result = find_git_root()
            
            # search_parent_directories=True ensures it searches upward
            assert mock_git.call_args[1]['search_parent_directories'] is True
            assert result == "/home/user/project"


class TestFindDir:
    """Test find_dir function."""
    
    def test_find_dir_calls_find_with_correct_params(self):
        """Test that find_dir calls _find with type='d'."""
        with patch('scitex.path._find._find', return_value=["/path/to/dir"]) as mock_find:
            result = find_dir("/root", "test_*")
            
            mock_find.assert_called_once_with("/root", type="d", exp="test_*")
            assert result == ["/path/to/dir"]
    
    def test_find_dir_with_pattern(self):
        """Test finding directories with pattern."""
        expected_dirs = ["/root/test_dir1", "/root/sub/test_dir2"]
        
        with patch('scitex.path._find._find', return_value=expected_dirs):
            result = find_dir("/root", "test_*")
            assert result == expected_dirs


class TestFindFile:
    """Test find_file function."""
    
    def test_find_file_calls_find_with_correct_params(self):
        """Test that find_file calls _find with type='f'."""
        with patch('scitex.path._find._find', return_value=["/path/to/file.txt"]) as mock_find:
            result = find_file("/root", "*.txt")
            
            mock_find.assert_called_once_with("/root", type="f", exp="*.txt")
            assert result == ["/path/to/file.txt"]
    
    def test_find_file_with_pattern(self):
        """Test finding files with pattern."""
        expected_files = ["/root/test.txt", "/root/sub/data.txt"]
        
        with patch('scitex.path._find._find', return_value=expected_files):
            result = find_file("/root", "*.txt")
            assert result == expected_files


class TestFind:
    """Test _find function."""
    
    def test_find_files_only(self):
        """Test finding files only."""
        mock_walk = [
            ("/root", ["dir1", "dir2"], ["file1.txt", "file2.py"]),
            ("/root/dir1", [], ["file3.txt"]),
            ("/root/dir2", [], ["file4.py"])
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                result = _find("/root", type="f", exp="*.txt")
                
                expected = ["/root/file1.txt", "/root/dir1/file3.txt"]
                assert result == expected
    
    def test_find_directories_only(self):
        """Test finding directories only."""
        mock_walk = [
            ("/root", ["test_dir1", "test_dir2", "other_dir"], ["file1.txt"]),
            ("/root/test_dir1", ["sub_test"], []),
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isdir', return_value=True):
                result = _find("/root", type="d", exp="test_*")
                
                expected = ["/root/test_dir1", "/root/test_dir2", "/root/test_dir1/sub_test"]
                assert result == expected
    
    def test_find_all_types(self):
        """Test finding both files and directories."""
        mock_walk = [
            ("/root", ["test_dir"], ["test_file.txt"]),
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                with patch('os.path.isdir', return_value=True):
                    result = _find("/root", type=None, exp="test_*")
                    
                    expected = ["/root/test_file.txt", "/root/test_dir"]
                    assert sorted(result) == sorted(expected)
    
    def test_find_with_string_exp(self):
        """Test that string expression is converted to list."""
        mock_walk = [("/root", [], ["test.txt"])]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                result = _find("/root", type="f", exp="*.txt")
                assert len(result) == 1
    
    def test_find_with_list_exp(self):
        """Test finding with multiple patterns."""
        mock_walk = [
            ("/root", [], ["test.txt", "data.csv", "script.py"])
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                result = _find("/root", type="f", exp=["*.txt", "*.csv"])
                
                expected = ["/root/test.txt", "/root/data.csv"]
                assert sorted(result) == sorted(expected)
    
    def test_find_excludes_special_directories(self):
        """Test that /lib/, /env/, and /build/ directories are excluded."""
        mock_walk = [
            ("/root", ["normal", "lib", "env", "build"], []),
            ("/root/normal", [], ["file.txt"]),
            ("/root/lib", [], ["lib_file.txt"]),
            ("/root/env", [], ["env_file.txt"]),
            ("/root/build", [], ["build_file.txt"]),
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                result = _find("/root", type="f", exp="*.txt")
                
                # Only file from normal directory should be included
                assert result == ["/root/normal/file.txt"]
    
    def test_find_excludes_paths_containing_keywords(self):
        """Test exclusion of paths containing /lib/, /env/, /build/."""
        mock_walk = [
            ("/root", ["mylib", "project"], []),
            ("/root/mylib/src", [], ["file.txt"]),  # Contains /lib/
            ("/root/project", [], ["main.py"]),
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                result = _find("/root", type="f", exp="*")
                
                # Only project/main.py should be included
                assert len(result) == 1
                assert "/root/project/main.py" in result
    
    def test_find_empty_directory(self):
        """Test finding in empty directory."""
        mock_walk = [("/root", [], [])]
        
        with patch('os.walk', return_value=mock_walk):
            result = _find("/root", type="f", exp="*")
            assert result == []
    
    def test_find_no_matches(self):
        """Test when no files match the pattern."""
        mock_walk = [
            ("/root", [], ["file.txt", "data.csv"])
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                result = _find("/root", type="f", exp="*.py")
                assert result == []
    
    def test_find_complex_pattern(self):
        """Test with complex fnmatch patterns."""
        mock_walk = [
            ("/root", [], ["test_1.txt", "test_2.txt", "test_abc.txt", "data.txt"])
        ]
        
        with patch('os.walk', return_value=mock_walk):
            with patch('os.path.isfile', return_value=True):
                # Find files matching test_[0-9].txt
                result = _find("/root", type="f", exp="test_[0-9].txt")
                
                expected = ["/root/test_1.txt", "/root/test_2.txt"]
                assert sorted(result) == sorted(expected)
    
    def test_find_type_validation(self):
        """Test type validation for files vs directories."""
        mock_walk = [
            ("/root", ["dir1"], ["file1.txt"])
        ]
        
        with patch('os.walk', return_value=mock_walk):
            # When looking for files, directories should be excluded
            with patch('os.path.isfile', side_effect=lambda p: "file" in p):
                result = _find("/root", type="f", exp="*")
                assert all("file" in p for p in result)
                assert not any("dir" in p for p in result)
            
            # When looking for directories, files should be excluded
            with patch('os.path.isdir', side_effect=lambda p: "dir" in p):
                result = _find("/root", type="d", exp="*")
                assert all("dir" in p for p in result)
                assert not any("file" in p for p in result)


class TestFindIntegration:
    """Integration tests using temporary directories."""
    
    def test_find_real_files(self):
        """Test with real temporary files and directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test structure
            os.makedirs(os.path.join(tmpdir, "subdir"))
            os.makedirs(os.path.join(tmpdir, "test_dir"))
            os.makedirs(os.path.join(tmpdir, "lib"))  # Should be excluded
            
            # Create files
            open(os.path.join(tmpdir, "test.txt"), 'w').close()
            open(os.path.join(tmpdir, "data.csv"), 'w').close()
            open(os.path.join(tmpdir, "subdir", "test.py"), 'w').close()
            open(os.path.join(tmpdir, "lib", "excluded.txt"), 'w').close()
            
            # Test finding txt files
            txt_files = _find(tmpdir, type="f", exp="*.txt")
            assert len(txt_files) == 1
            assert any("test.txt" in f for f in txt_files)
            assert not any("excluded.txt" in f for f in txt_files)
            
            # Test finding directories
            dirs = _find(tmpdir, type="d", exp="test_*")
            assert len(dirs) == 1
            assert any("test_dir" in d for d in dirs)
            
            # Test finding all files
            all_files = _find(tmpdir, type="f", exp="*")
            assert len(all_files) == 3  # test.txt, data.csv, test.py (not excluded.txt)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_find.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 19:53:58 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/path/_find.py
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-17 09:34:43"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
# 
# """
# This script does XYZ.
# """
# 
# import fnmatch
# import os
# import sys
# 
# import scitex
# 
# 
# # Functions
# def find_git_root():
#     import git
# 
#     repo = git.Repo(".", search_parent_directories=True)
#     return repo.working_tree_dir
# 
# 
# def find_dir(root_dir, exp):
#     return _find(root_dir, type="d", exp=exp)
# 
# 
# def find_file(root_dir, exp):
#     return _find(root_dir, type="f", exp=exp)
# 
# 
# def _find(rootdir, type="f", exp=["*"]):
#     """
#     Mimicks the Unix find command.
# 
#     Example:
#         # rootdir =
#         # type = 'f'  # 'f' for files, 'd' for directories, None for both
#         # exp = '*.txt'  # Pattern to match, or None to match all
#         find('/path/to/search', "f", "*.txt")
#     """
#     if isinstance(exp, str):
#         exp = [exp]
# 
#     matches = []
#     for _exp in exp:
#         for root, dirs, files in os.walk(rootdir):
#             # Depending on the type, choose the list to iterate over
#             if type == "f":  # Files only
#                 names = files
#             elif type == "d":  # Directories only
#                 names = dirs
#             else:  # All entries
#                 names = files + dirs
# 
#             for name in names:
#                 # Construct the full path
#                 path = os.path.join(root, name)
# 
#                 # If an _exp is provided, use fnmatch to filter names
#                 if _exp and not fnmatch.fnmatch(name, _exp):
#                     continue
# 
#                 # If type is set, ensure the type matches
#                 if type == "f" and not os.path.isfile(path):
#                     continue
#                 if type == "d" and not os.path.isdir(path):
#                     continue
# 
#                 exclude_keys = ["/lib/", "/env/", "/build/"]
#                 if not any(ek in path for ek in exclude_keys):
#                     matches.append(path)
# 
#                 # for ek in exclude_keys:
#                 #     if ek in path:
#                 #         path = None
#                 #         break
# 
#                 # if path is not None:
#                 #     # Add the matching path to the results
#                 #     matches.append(path)
# 
#     return matches
# 
# 
# if __name__ == "__main__":
#     # Import matplotlib only when running as script
#     try:
#         import matplotlib.pyplot as plt
#     except ImportError:
#         plt = None
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
# /ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/path/_find.py
# """
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/path/_find.py
# --------------------------------------------------------------------------------
