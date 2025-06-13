#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:18:00 (ywatanabe)"
# File: ./tests/scitex/str/test__clean_path.py

"""Tests for path cleaning functionality."""

import pytest
import os
from scitex.str import clean_path


class TestCleanPath:
    """Test cases for path cleaning functionality."""

    def test_basic_path_cleaning(self):
        """Test basic path normalization."""
        assert clean_path("/home/user/file.txt") == "/home/user/file.txt"
        assert clean_path("simple/path") == "simple/path"
        
    def test_redundant_separators(self):
        """Test removal of redundant path separators."""
        assert clean_path("path//to//file.txt") == "path/to/file.txt"
        assert clean_path("///multiple///slashes///") == "/multiple/slashes/"
        assert clean_path("path///to/file") == "path/to/file"
        
    def test_current_directory_references(self):
        """Test removal of current directory references."""
        assert clean_path("./file.txt") == "file.txt"
        assert clean_path("path/./to/file") == "path/to/file"
        assert clean_path("./path/./to/./file") == "path/to/file"
        
    def test_parent_directory_references(self):
        """Test normalization of parent directory references."""
        assert clean_path("/home/user/../file.txt") == "/home/file.txt"
        assert clean_path("path/to/../file.txt") == "path/file.txt"
        assert clean_path("path/../other/../file") == "file"
        
    def test_mixed_path_issues(self):
        """Test paths with multiple normalization issues."""
        assert clean_path("/home/user/./folder/../file.txt") == "/home/user/file.txt"
        assert clean_path("path/./to//file.txt") == "path/to/file.txt"
        assert clean_path("./path/../to//./file") == "to/file"
        
    def test_directory_paths(self):
        """Test directory path preservation."""
        assert clean_path("/home/user/") == "/home/user/"
        assert clean_path("path/to/dir/") == "path/to/dir/"
        assert clean_path("./dir/") == "dir/"
        
    def test_directory_normalization(self):
        """Test directory path normalization with issues."""
        assert clean_path("path//to//dir/") == "path/to/dir/"
        assert clean_path("path/./to/./dir/") == "path/to/dir/"
        assert clean_path("path/../dir/") == "dir/"
        
    def test_root_path(self):
        """Test root path handling."""
        assert clean_path("/") == "/"
        assert clean_path("//") == "//"
        assert clean_path("///") == "/"
        
    def test_empty_path(self):
        """Test empty path handling."""
        assert clean_path("") == "."
        assert clean_path(".") == "."
        assert clean_path("./") == "./"
        
    def test_relative_paths(self):
        """Test relative path normalization."""
        assert clean_path("../file.txt") == "../file.txt"
        assert clean_path("../../file") == "../../file"
        assert clean_path("../path/to/file") == "../path/to/file"
        
    def test_absolute_paths(self):
        """Test absolute path normalization."""
        assert clean_path("/home/user/file") == "/home/user/file"
        assert clean_path("/var/log/./messages") == "/var/log/messages"
        assert clean_path("/etc/../home/user") == "/home/user"
        
    def test_f_string_path_cleaning(self):
        """Test cleaning of f-string formatted paths."""
        assert clean_path('f"/home/user/file"') == "/home/user/file"
        assert clean_path('f"path/to/file"') == "path/to/file"
        assert clean_path('f"./relative/path"') == "relative/path"
        
    def test_complex_f_string_paths(self):
        """Test complex f-string path scenarios."""
        assert clean_path('f"/home//user/../file"') == "/home/file"
        assert clean_path('f"./path//to/./file"') == "path/to/file"
        
    def test_windows_paths(self):
        """Test Windows-style path handling."""
        # Note: os.path.normpath handles platform differences
        if os.name == 'nt':
            assert clean_path("C:\\Users\\file.txt") == "C:\\Users\\file.txt"
            assert clean_path("C:\\Users\\..\\file") == "C:\\file"
        else:
            # On Unix, backslashes are treated as regular characters
            result = clean_path("C:\\Users\\file.txt")
            assert "C:" in result and "Users" in result and "file.txt" in result
            
    def test_special_characters(self):
        """Test paths with special characters."""
        assert clean_path("/home/user/file name.txt") == "/home/user/file name.txt"
        assert clean_path("path/to/file-with-dash") == "path/to/file-with-dash"
        assert clean_path("path/to/file_with_underscore") == "path/to/file_with_underscore"
        
    def test_unicode_paths(self):
        """Test paths with unicode characters."""
        assert clean_path("/home/用户/文件.txt") == "/home/用户/文件.txt"
        assert clean_path("./пуш/к/файл") == "пуш/к/файл"
        assert clean_path("café/résumé/naïve") == "café/résumé/naïve"
        
    def test_long_paths(self):
        """Test very long path normalization."""
        long_path = "/".join(["dir"] * 50) + "/file.txt"
        normalized = clean_path(long_path)
        assert normalized == long_path
        
        long_path_with_issues = "/".join(["dir", ".", "..", "dir"] * 20) + "/file.txt"
        normalized = clean_path(long_path_with_issues)
        assert normalized.count("..") == 0
        assert normalized.count("/.") == 0
        
    def test_type_validation(self):
        """Test input type validation."""
        with pytest.raises(ValueError, match="Path cleaning failed"):
            clean_path(123)
            
        with pytest.raises(ValueError, match="Path cleaning failed"):
            clean_path(None)
            
        with pytest.raises(ValueError, match="Path cleaning failed"):
            clean_path([])
            
    def test_edge_cases(self):
        """Test edge case paths."""
        assert clean_path("...") == "..."
        assert clean_path("....") == "...."
        assert clean_path("file...txt") == "file...txt"
        
    def test_multiple_parent_references(self):
        """Test multiple consecutive parent directory references."""
        assert clean_path("../../file") == "../../file"
        assert clean_path("../../../file") == "../../../file"
        assert clean_path("path/../../file") == "../file"
        
    def test_mixed_separators(self):
        """Test paths with mixed separator styles."""
        # Test backslash and forward slash mixing
        mixed_path = "path\\to/mixed\\separators/file"
        result = clean_path(mixed_path)
        # Result depends on platform, but should be normalized
        assert "file" in result
        
    def test_symlink_like_paths(self):
        """Test paths that look like symbolic links."""
        assert clean_path("link/../target") == "target"
        assert clean_path("./link/../file") == "file"
        
    def test_network_paths(self):
        """Test network-style paths."""
        assert clean_path("//server/share/file") == "//server/share/file"
        assert clean_path("\\\\server\\share\\file") == "\\\\server\\share\\file"
        
    def test_preserve_trailing_slash_consistency(self):
        """Test that trailing slash behavior is consistent."""
        # Directory paths should preserve trailing slash
        assert clean_path("dir/").endswith("/")
        assert clean_path("./dir/").endswith("/")
        assert clean_path("path//to//dir/").endswith("/")
        
        # File paths should not have trailing slash
        assert not clean_path("file.txt").endswith("/")
        assert not clean_path("./file.txt").endswith("/")
        
    def test_error_handling(self):
        """Test error handling and exception propagation."""
        # Test with extreme inputs that might cause issues
        very_long_string = "a" * 10000
        result = clean_path(very_long_string)
        assert len(result) > 0
        
        # Test with string containing null bytes (if platform supports)
        try:
            result = clean_path("path\x00/file")
            # Some platforms may handle this, others may not
            assert isinstance(result, str)
        except ValueError:
            # Expected on platforms that don't support null bytes in paths
            pass


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
