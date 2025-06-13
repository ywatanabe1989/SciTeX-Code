#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 09:24:00 (ywatanabe)"
# File: ./tests/scitex/path/test__split_comprehensive.py

"""Comprehensive tests for scitex.path._split path splitting functionality."""

import pytest
import os
from pathlib import Path


class TestSplitImport:
    """Test import functionality."""

    def test_import_split(self):
        """Test that split function can be imported."""
from scitex.path import split
        assert callable(split)


class TestSplitBasicFunctionality:
    """Test basic split functionality."""

    def test_split_basic_file(self):
        """Test splitting a basic file path."""
from scitex.path import split
        
        fpath = "data/test.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "test"
        assert ext == ".txt"

    def test_split_nested_path(self):
        """Test splitting a deeply nested path."""
from scitex.path import split
        
        fpath = "home/user/documents/projects/file.py"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "home/user/documents/projects/"
        assert fname == "file"
        assert ext == ".py"

    def test_split_root_file(self):
        """Test splitting a file in root directory."""
from scitex.path import split
        
        fpath = "file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "/"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_no_extension(self):
        """Test splitting a file without extension."""
from scitex.path import split
        
        fpath = "data/filename"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "filename"
        assert ext == ""

    def test_split_hidden_file(self):
        """Test splitting a hidden file (starting with dot)."""
from scitex.path import split
        
        fpath = "home/user/.bashrc"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "home/user/"
        assert fname == ".bashrc"
        assert ext == ""

    def test_split_multiple_extensions(self):
        """Test splitting file with multiple extensions."""
from scitex.path import split
        
        fpath = "data/archive.tar.gz"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "archive.tar"
        assert ext == ".gz"


class TestSplitSpecialCases:
    """Test special cases and edge conditions."""

    def test_split_empty_string(self):
        """Test splitting empty string."""
from scitex.path import split
        
        fpath = ""
        dirname, fname, ext = split(fpath)
        
        assert dirname == "/"
        assert fname == ""
        assert ext == ""

    def test_split_only_directory(self):
        """Test splitting path that ends with directory separator."""
from scitex.path import split
        
        fpath = "data/subdir/"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/subdir/"
        assert fname == ""
        assert ext == ""

    def test_split_only_extension(self):
        """Test splitting file that is only an extension."""
from scitex.path import split
        
        fpath = "data/.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == ".txt"  # os.path.splitext treats .txt as filename, not extension
        assert ext == ""

    def test_split_dot_in_filename(self):
        """Test splitting file with dots in filename."""
from scitex.path import split
        
        fpath = "data/file.name.with.dots.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "file.name.with.dots"
        assert ext == ".txt"

    def test_split_no_directory(self):
        """Test splitting just a filename."""
from scitex.path import split
        
        fpath = "simple.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "/"
        assert fname == "simple"
        assert ext == ".txt"


class TestSplitAbsolutePaths:
    """Test split with absolute paths."""

    def test_split_absolute_unix_path(self):
        """Test splitting absolute Unix path."""
from scitex.path import split
        
        fpath = "/home/user/documents/file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "/home/user/documents/"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_absolute_root_file(self):
        """Test splitting file in absolute root."""
from scitex.path import split
        
        fpath = "/file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "//"  # Function adds "/" to os.path.dirname result
        assert fname == "file"
        assert ext == ".txt"


class TestSplitRelativePaths:
    """Test split with relative paths."""

    def test_split_current_directory(self):
        """Test splitting path in current directory."""
from scitex.path import split
        
        fpath = "./file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "./"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_parent_directory(self):
        """Test splitting path in parent directory."""
from scitex.path import split
        
        fpath = "../data/file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "../data/"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_nested_relative(self):
        """Test splitting nested relative path."""
from scitex.path import split
        
        fpath = "../../parent/child/file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "../../parent/child/"
        assert fname == "file"
        assert ext == ".txt"


class TestSplitFileTypes:
    """Test split with various file types."""

    def test_split_image_files(self):
        """Test splitting image file paths."""
from scitex.path import split
        
        test_cases = [
            ("images/photo.jpg", "images/", "photo", ".jpg"),
            ("pics/image.png", "pics/", "image", ".png"),
            ("graphics/vector.svg", "graphics/", "vector", ".svg"),
            ("raw/picture.tiff", "raw/", "picture", ".tiff")
        ]
        
        for fpath, exp_dir, exp_name, exp_ext in test_cases:
            dirname, fname, ext = split(fpath)
            assert dirname == exp_dir
            assert fname == exp_name
            assert ext == exp_ext

    def test_split_code_files(self):
        """Test splitting code file paths."""
from scitex.path import split
        
        test_cases = [
            ("src/main.py", "src/", "main", ".py"),
            ("lib/utils.js", "lib/", "utils", ".js"),
            ("cpp/program.cpp", "cpp/", "program", ".cpp"),
            ("java/App.java", "java/", "App", ".java")
        ]
        
        for fpath, exp_dir, exp_name, exp_ext in test_cases:
            dirname, fname, ext = split(fpath)
            assert dirname == exp_dir
            assert fname == exp_name
            assert ext == exp_ext

    def test_split_document_files(self):
        """Test splitting document file paths."""
from scitex.path import split
        
        test_cases = [
            ("docs/readme.md", "docs/", "readme", ".md"),
            ("papers/research.pdf", "papers/", "research", ".pdf"),
            ("texts/document.docx", "texts/", "document", ".docx"),
            ("sheets/data.xlsx", "sheets/", "data", ".xlsx")
        ]
        
        for fpath, exp_dir, exp_name, exp_ext in test_cases:
            dirname, fname, ext = split(fpath)
            assert dirname == exp_dir
            assert fname == exp_name
            assert ext == exp_ext


class TestSplitSpecialCharacters:
    """Test split with special characters in paths."""

    def test_split_spaces_in_path(self):
        """Test splitting paths with spaces."""
from scitex.path import split
        
        fpath = "my documents/my file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "my documents/"
        assert fname == "my file"
        assert ext == ".txt"

    def test_split_unicode_characters(self):
        """Test splitting paths with Unicode characters."""
from scitex.path import split
        
        fpath = "données/fichier_тест.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "données/"
        assert fname == "fichier_тест"
        assert ext == ".txt"

    def test_split_special_symbols(self):
        """Test splitting paths with special symbols."""
from scitex.path import split
        
        fpath = "data/file-name_v2.0.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "file-name_v2.0"
        assert ext == ".txt"

    def test_split_parentheses_brackets(self):
        """Test splitting paths with parentheses and brackets."""
from scitex.path import split
        
        fpath = "data/file(1)[copy].txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "file(1)[copy]"
        assert ext == ".txt"


class TestSplitReturnTypes:
    """Test split return types and values."""

    def test_split_return_tuple(self):
        """Test that split returns a tuple."""
from scitex.path import split
        
        result = split("data/file.txt")
        
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_split_return_strings(self):
        """Test that split returns strings."""
from scitex.path import split
        
        dirname, fname, ext = split("data/file.txt")
        
        assert isinstance(dirname, str)
        assert isinstance(fname, str)
        assert isinstance(ext, str)

    def test_split_unpacking(self):
        """Test that split can be unpacked correctly."""
from scitex.path import split
        
        # Test tuple unpacking
        result = split("data/file.txt")
        dirname, fname, ext = result
        
        assert dirname == "data/"
        assert fname == "file"
        assert ext == ".txt"


class TestSplitConsistency:
    """Test split consistency and behavior."""

    def test_split_idempotent(self):
        """Test that split is consistent for same input."""
from scitex.path import split
        
        fpath = "data/test/file.txt"
        
        result1 = split(fpath)
        result2 = split(fpath)
        
        assert result1 == result2

    def test_split_different_inputs(self):
        """Test split with various different inputs."""
from scitex.path import split
        
        test_cases = [
            "simple.txt",
            "data/file.py", 
            "/absolute/path.md",
            "./relative.json",
            "../parent/child.xml",
            "no_extension",
            ".hidden",
            "complex.tar.gz"
        ]
        
        for fpath in test_cases:
            result = split(fpath)
            assert isinstance(result, tuple)
            assert len(result) == 3
            
            dirname, fname, ext = result
            assert isinstance(dirname, str)
            assert isinstance(fname, str)
            assert isinstance(ext, str)


class TestSplitDocumentedExample:
    """Test the specific example from the function docstring."""

    def test_split_docstring_example(self):
        """Test the exact example from the function docstring."""
from scitex.path import split
        
        fpath = '../data/01/day1/split_octave/2kHz_mat/tt8-2.mat'
        dirname, fname, ext = split(fpath)
        
        # Expected results from docstring
        assert dirname == '../data/01/day1/split_octave/2kHz_mat/'
        assert fname == 'tt8-2'
        assert ext == '.mat'


class TestSplitEdgeCases:
    """Test edge cases and potential error conditions."""

    def test_split_very_long_path(self):
        """Test splitting very long path."""
from scitex.path import split
        
        # Create a very long path
        long_dir = "/".join(["very_long_directory_name"] * 20)
        fpath = f"{long_dir}/file.txt"
        
        dirname, fname, ext = split(fpath)
        
        assert dirname.endswith("/")
        assert fname == "file"
        assert ext == ".txt"

    def test_split_numeric_names(self):
        """Test splitting paths with numeric names."""
from scitex.path import split
        
        fpath = "data/123.456"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "123"
        assert ext == ".456"

    def test_split_single_character(self):
        """Test splitting single character filename."""
from scitex.path import split
        
        fpath = "data/a.b"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/"
        assert fname == "a"
        assert ext == ".b"


class TestSplitOSCompatibility:
    """Test OS compatibility aspects."""

    def test_split_forward_slashes(self):
        """Test splitting with forward slashes (Unix-style)."""
from scitex.path import split
        
        fpath = "data/subdir/file.txt"
        dirname, fname, ext = split(fpath)
        
        assert dirname == "data/subdir/"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_mixed_separators(self):
        """Test behavior with mixed path separators."""
from scitex.path import split
        
        # This tests current behavior - may vary by OS
        fpath = "data\\subdir/file.txt"
        dirname, fname, ext = split(fpath)
        
        # Behavior depends on os.path implementation
        assert isinstance(dirname, str)
        assert isinstance(fname, str) 
        assert isinstance(ext, str)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])