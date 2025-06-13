#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test__path.py

"""Tests for scitex.io._path module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestFindTheGitRootDir:
    """Test git root directory finding functionality."""

    def test_find_git_root_in_repo(self):
        """Test finding git root in a git repository."""
        from scitex.io import find_the_git_root_dir

        # Mock git.Repo
        with patch("git.Repo") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.working_tree_dir = "/path/to/git/root"
            mock_repo_class.return_value = mock_repo

            result = find_the_git_root_dir()

            assert result == "/path/to/git/root"
            mock_repo_class.assert_called_once_with(".", search_parent_directories=True)

    def test_find_git_root_not_in_repo(self):
        """Test behavior when not in a git repository."""
        from scitex.io import find_the_git_root_dir

        # Mock git.Repo to raise exception
        with patch("git.Repo") as mock_repo_class:
            import git

            mock_repo_class.side_effect = git.exc.InvalidGitRepositoryError(
                "Not a git repo"
            )

            with pytest.raises(git.exc.InvalidGitRepositoryError):
                find_the_git_root_dir()


class TestSplitFpath:
    """Test file path splitting functionality."""

    def test_split_fpath_basic(self):
        """Test basic file path splitting."""
        from scitex.io import split_fpath

        fpath = "/home/user/data/file.txt"
        dirname, fname, ext = split_fpath(fpath)

        assert dirname == "/home/user/data/"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_fpath_complex_extension(self):
        """Test splitting with complex extensions."""
        from scitex.io import split_fpath

        # Double extension (only last one is considered extension)
        fpath = "/path/to/archive.tar.gz"
        dirname, fname, ext = split_fpath(fpath)

        assert dirname == "/path/to/"
        assert fname == "archive.tar"
        assert ext == ".gz"

    def test_split_fpath_no_extension(self):
        """Test splitting file with no extension."""
        from scitex.io import split_fpath

        fpath = "/path/to/README"
        dirname, fname, ext = split_fpath(fpath)

        assert dirname == "/path/to/"
        assert fname == "README"
        assert ext == ""

    def test_split_fpath_root_file(self):
        """Test splitting file in root directory."""
        from scitex.io import split_fpath

        fpath = "/file.txt"
        dirname, fname, ext = split_fpath(fpath)

        assert dirname == "/"
        assert fname == "file"
        assert ext == ".txt"

    def test_split_fpath_relative_path(self):
        """Test splitting relative path."""
        from scitex.io import split_fpath

        fpath = "../data/01/day1/split_octave/2kHz_mat/tt8-2.mat"
        dirname, fname, ext = split_fpath(fpath)

        assert dirname == "../data/01/day1/split_octave/2kHz_mat/"
        assert fname == "tt8-2"
        assert ext == ".mat"

    def test_split_fpath_hidden_file(self):
        """Test splitting hidden file."""
        from scitex.io import split_fpath

        fpath = "/home/user/.config"
        dirname, fname, ext = split_fpath(fpath)

        assert dirname == "/home/user/"
        assert fname == ".config"
        assert ext == ""


class TestTouch:
    """Test file touch functionality."""

    def test_touch_creates_new_file(self, tmp_path):
        """Test that touch creates a new file."""
        from scitex.io import touch

        test_file = tmp_path / "new_file.txt"
        assert not test_file.exists()

        touch(str(test_file))

        assert test_file.exists()
        assert test_file.is_file()

    def test_touch_updates_existing_file(self, tmp_path):
        """Test that touch updates modification time of existing file."""
        from scitex.io import touch
        import time

        test_file = tmp_path / "existing.txt"
        test_file.write_text("content")

        # Get initial modification time
        initial_mtime = os.path.getmtime(test_file)

        # Wait a bit to ensure time difference
        time.sleep(0.1)

        # Touch the file
        touch(str(test_file))

        # Check modification time updated
        new_mtime = os.path.getmtime(test_file)
        assert new_mtime > initial_mtime

        # Content should remain unchanged
        assert test_file.read_text() == "content"

    def test_touch_nested_directory(self, tmp_path):
        """Test touch with nested directory path."""
        from scitex.io import touch

        nested_dir = tmp_path / "level1" / "level2"
        nested_dir.mkdir(parents=True)

        test_file = nested_dir / "file.txt"
        touch(str(test_file))

        assert test_file.exists()


class TestFind:
    """Test find functionality."""

    def test_find_files_only(self, tmp_path):
        """Test finding files only."""
        from scitex.io import find

        # Create test structure
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").touch()

        # Find all files
        results = find(str(tmp_path), type="f", exp="*.txt")

        assert len(results) == 3
        assert all(r.endswith(".txt") for r in results)

    def test_find_directories_only(self, tmp_path):
        """Test finding directories only."""
        from scitex.io import find

        # Create test structure
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "dir1" / "subdir").mkdir()
        (tmp_path / "file.txt").touch()

        # Find all directories
        results = find(str(tmp_path), type="d", exp="*")

        assert len(results) == 3
        assert all(os.path.isdir(r) for r in results)

    def test_find_with_pattern(self, tmp_path):
        """Test finding with specific pattern."""
        from scitex.io import find

        # Create mixed files
        (tmp_path / "test1.py").touch()
        (tmp_path / "test2.py").touch()
        (tmp_path / "data.txt").touch()
        (tmp_path / "script.sh").touch()

        # Find only Python files
        results = find(str(tmp_path), type="f", exp="*.py")

        assert len(results) == 2
        assert all(r.endswith(".py") for r in results)

    def test_find_multiple_patterns(self, tmp_path):
        """Test finding with multiple patterns."""
        from scitex.io import find

        # Create various files
        (tmp_path / "test.py").touch()
        (tmp_path / "data.txt").touch()
        (tmp_path / "image.jpg").touch()

        # Find Python and text files
        results = find(str(tmp_path), type="f", exp=["*.py", "*.txt"])

        assert len(results) == 2
        assert any(r.endswith(".py") for r in results)
        assert any(r.endswith(".txt") for r in results)

    def test_find_all_types(self, tmp_path):
        """Test finding both files and directories."""
        from scitex.io import find

        # Create mixed structure
        (tmp_path / "file.txt").touch()
        (tmp_path / "directory").mkdir()

        # Find all (type=None)
        results = find(str(tmp_path), type=None, exp="*")

        assert len(results) == 2

    def test_find_recursive(self, tmp_path):
        """Test recursive finding."""
        from scitex.io import find

        # Create nested structure
        (tmp_path / "level1").mkdir()
        (tmp_path / "level1" / "level2").mkdir()
        (tmp_path / "level1" / "level2" / "deep.txt").touch()
        (tmp_path / "shallow.txt").touch()

        # Find should be recursive by default
        results = find(str(tmp_path), type="f", exp="*.txt")

        assert len(results) == 2
        assert any("deep.txt" in r for r in results)
        assert any("shallow.txt" in r for r in results)


class TestFindLatest:
    """Test find_latest functionality."""

    def test_find_latest_basic(self, tmp_path):
        """Test finding latest version of file."""
        from scitex.io import find_latest

        # Create versioned files
        (tmp_path / "report_v1.txt").touch()
        (tmp_path / "report_v2.txt").touch()
        (tmp_path / "report_v10.txt").touch()
        (tmp_path / "report_v3.txt").touch()

        result = find_latest(str(tmp_path), "report", ".txt")

        assert result is not None
        assert result.endswith("report_v10.txt")

    def test_find_latest_custom_prefix(self, tmp_path):
        """Test finding latest with custom version prefix."""
        from scitex.io import find_latest

        # Create files with custom prefix
        (tmp_path / "data-ver1.csv").touch()
        (tmp_path / "data-ver2.csv").touch()
        (tmp_path / "data-ver5.csv").touch()

        result = find_latest(str(tmp_path), "data", ".csv", version_prefix="-ver")

        assert result is not None
        assert result.endswith("data-ver5.csv")

    def test_find_latest_no_matches(self, tmp_path):
        """Test when no matching files exist."""
        from scitex.io import find_latest

        # Create non-matching files
        (tmp_path / "other.txt").touch()
        (tmp_path / "report.txt").touch()  # No version number

        result = find_latest(str(tmp_path), "report", ".txt")

        assert result is None

    def test_find_latest_special_characters(self, tmp_path):
        """Test with special characters in filename."""
        from scitex.io import find_latest

        # Create files with special characters
        (tmp_path / "data.backup_v1.tar.gz").touch()
        (tmp_path / "data.backup_v2.tar.gz").touch()

        result = find_latest(str(tmp_path), "data.backup", ".tar.gz")

        assert result is not None
        assert result.endswith("data.backup_v2.tar.gz")

    def test_find_latest_zero_padding(self, tmp_path):
        """Test with zero-padded version numbers."""
        from scitex.io import find_latest

        # Create files with zero-padded versions
        (tmp_path / "doc_v001.pdf").touch()
        (tmp_path / "doc_v002.pdf").touch()
        (tmp_path / "doc_v010.pdf").touch()

        result = find_latest(str(tmp_path), "doc", ".pdf")

        assert result is not None
        assert result.endswith("doc_v010.pdf")


class TestPathIntegration:
    """Test integration scenarios."""

    def test_combined_workflow(self, tmp_path):
        """Test a combined workflow using multiple functions."""
        from scitex.io import touch, find, split_fpath

        # Create test structure
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Touch some files
        files = ["analysis_v1.py", "analysis_v2.py", "readme.txt"]
        for f in files:
            touch(str(data_dir / f))

        # Find Python files
        py_files = find(str(data_dir), type="f", exp="*.py")
        assert len(py_files) == 2

        # Split paths
        for py_file in py_files:
            dirname, fname, ext = split_fpath(py_file)
            assert ext == ".py"
            assert "analysis" in fname

    def test_unicode_handling(self, tmp_path):
        """Test handling of Unicode in paths."""
        from scitex.io import touch, find, split_fpath

        # Create file with Unicode name
        unicode_file = tmp_path / "文档_v1.txt"
        touch(str(unicode_file))

        # Find and verify
        results = find(str(tmp_path), type="f", exp="*.txt")
        assert len(results) == 1

        # Split path
        dirname, fname, ext = split_fpath(results[0])
        assert "文档_v1" in fname
        assert ext == ".txt"


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
