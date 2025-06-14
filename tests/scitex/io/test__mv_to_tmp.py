#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test__mv_to_tmp.py

"""Tests for scitex.io._mv_to_tmp module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestMvToTmpBasic:
    """Test basic move to tmp functionality."""

    def test_move_simple_file(self):
        """Test moving a simple file to /tmp."""
        from scitex.io import _mv_to_tmp

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            # Mock shutil.move to avoid actual file operations in /tmp
            with patch("shutil.move") as mock_move:
                with patch("builtins.print") as mock_print:
                    _mv_to_tmp(test_file)

                    # Verify move was called with correct paths
                    expected_target = "/tmp/test.txt"
                    mock_move.assert_called_once_with(test_file, expected_target)
                    mock_print.assert_called_once_with(f"Moved to: {expected_target}")

    def test_move_with_custom_level(self):
        """Test moving file with custom directory level parameter."""
        from scitex.io import _mv_to_tmp

        test_path = "/home/user/documents/project/data/file.csv"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print") as mock_print:
                # Test with L=3 (should take last 3 path components)
                _mv_to_tmp(test_path, L=3)

                expected_target = "/tmp/project-data-file.csv"
                mock_move.assert_called_once_with(test_path, expected_target)
                mock_print.assert_called_once_with(f"Moved to: {expected_target}")

    def test_move_nested_path_default_level(self):
        """Test moving file from nested path with default L=2."""
        from scitex.io import _mv_to_tmp

        test_path = "/path/to/deep/folder/structure/myfile.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print") as mock_print:
                _mv_to_tmp(test_path)

                # Default L=2 takes last 2 components
                expected_target = "/tmp/structure-myfile.txt"
                mock_move.assert_called_once_with(test_path, expected_target)

    def test_move_short_path(self):
        """Test moving file with path shorter than L parameter."""
        from scitex.io import _mv_to_tmp

        test_path = "file.txt"  # Only 1 component

        with patch("shutil.move") as mock_move:
            with patch("builtins.print") as mock_print:
                _mv_to_tmp(test_path, L=3)  # L larger than path components

                # Should handle gracefully
                expected_target = "/tmp/file.txt"
                mock_move.assert_called_once_with(test_path, expected_target)


class TestMvToTmpErrorHandling:
    """Test error handling scenarios."""

    def test_move_fails_silently(self):
        """Test that move failures are handled silently."""
        from scitex.io import _mv_to_tmp

        test_path = "/nonexistent/file.txt"

        with patch("shutil.move", side_effect=FileNotFoundError("File not found")):
            # Should not raise exception due to try/except
            _mv_to_tmp(test_path)  # Should complete without error

    def test_permission_error_handled(self):
        """Test handling of permission errors."""
        from scitex.io import _mv_to_tmp

        test_path = "/root/protected/file.txt"

        with patch("shutil.move", side_effect=PermissionError("Permission denied")):
            # Should not raise exception
            _mv_to_tmp(test_path)  # Should complete without error

    def test_invalid_path_handled(self):
        """Test handling of invalid paths."""
        from scitex.io import _mv_to_tmp

        # Test with None
        _mv_to_tmp(None)  # Should not crash

        # Test with empty string
        _mv_to_tmp("")  # Should not crash

        # Test with integer
        _mv_to_tmp(123)  # Should not crash

    def test_target_exists_error(self):
        """Test when target file already exists in /tmp."""
        from scitex.io import _mv_to_tmp

        test_path = "/home/user/file.txt"

        with patch("shutil.move", side_effect=OSError("Target exists")):
            # Should handle silently
            _mv_to_tmp(test_path)  # Should complete without error


class TestMvToTmpPathHandling:
    """Test various path format handling."""

    def test_windows_style_path(self):
        """Test handling Windows-style paths."""
        from scitex.io import _mv_to_tmp

        # Windows path with backslashes
        test_path = r"C:\Users\Documents\file.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print"):
                _mv_to_tmp(test_path)

                # The function uses "/" split, so Windows paths won't split properly
                # This is a limitation of the current implementation
                mock_move.assert_called_once()

    def test_path_with_spaces(self):
        """Test paths containing spaces."""
        from scitex.io import _mv_to_tmp

        test_path = "/home/user/my documents/important file.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print") as mock_print:
                _mv_to_tmp(test_path)

                expected_target = "/tmp/my documents-important file.txt"
                mock_move.assert_called_once_with(test_path, expected_target)

    def test_path_with_special_characters(self):
        """Test paths with special characters."""
        from scitex.io import _mv_to_tmp

        test_path = "/data/files/report_2024-01-01.csv"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print"):
                _mv_to_tmp(test_path)

                expected_target = "/tmp/files-report_2024-01-01.csv"
                mock_move.assert_called_once_with(test_path, expected_target)

    def test_relative_path(self):
        """Test with relative paths."""
        from scitex.io import _mv_to_tmp

        test_path = "./data/file.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print"):
                _mv_to_tmp(test_path)

                expected_target = "/tmp/data-file.txt"
                mock_move.assert_called_once_with(test_path, expected_target)


class TestMvToTmpLevelParameter:
    """Test the L parameter functionality in detail."""

    def test_various_L_values(self):
        """Test different L values with same path."""
        from scitex.io import _mv_to_tmp

        test_path = "/a/b/c/d/e/file.txt"

        test_cases = [
            (1, "/tmp/file.txt"),
            (2, "/tmp/e-file.txt"),
            (3, "/tmp/d-e-file.txt"),
            (4, "/tmp/c-d-e-file.txt"),
            (5, "/tmp/b-c-d-e-file.txt"),
            (10, "/tmp/a-b-c-d-e-file.txt"),  # L larger than path depth
        ]

        for L, expected_target in test_cases:
            with patch("shutil.move") as mock_move:
                with patch("builtins.print"):
                    _mv_to_tmp(test_path, L=L)
                    mock_move.assert_called_once_with(test_path, expected_target)

    def test_L_zero(self):
        """Test with L=0 (edge case)."""
        from scitex.io import _mv_to_tmp

        test_path = "/path/to/file.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print"):
                _mv_to_tmp(test_path, L=0)

                # With L=0, should result in empty selection
                expected_target = "/tmp/"
                mock_move.assert_called_once_with(test_path, expected_target)

    def test_negative_L(self):
        """Test with negative L value (edge case)."""
        from scitex.io import _mv_to_tmp

        test_path = "/path/to/file.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print"):
                # Negative L might cause unexpected slicing behavior
                _mv_to_tmp(test_path, L=-1)
                mock_move.assert_called_once()


class TestMvToTmpIntegration:
    """Test integration scenarios."""

    def test_actual_file_move(self, tmp_path):
        """Test with actual file operations (not to real /tmp)."""
        from scitex.io import _mv_to_tmp

        # Create test file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        test_file = source_dir / "test.txt"
        test_file.write_text("content")

        # Create mock /tmp directory
        mock_tmp = tmp_path / "mock_tmp"
        mock_tmp.mkdir()

        # Patch to use mock_tmp instead of /tmp
        with patch("shutil.move") as mock_move:

            def mock_move_impl(src, dst):
                # Simulate actual move
                dst_path = dst.replace("/tmp", str(mock_tmp))
                Path(dst_path).write_text(Path(src).read_text())
                Path(src).unlink()

            mock_move.side_effect = mock_move_impl

            with patch("builtins.print"):
                _mv_to_tmp(str(test_file))

            # Verify file was "moved"
            assert not test_file.exists()
            mock_move.assert_called_once()

    def test_unicode_filename(self):
        """Test with Unicode filenames."""
        from scitex.io import _mv_to_tmp

        test_path = "/home/user/文档/ファイル.txt"

        with patch("shutil.move") as mock_move:
            with patch("builtins.print"):
                _mv_to_tmp(test_path)

                expected_target = "/tmp/文档-ファイル.txt"
                mock_move.assert_called_once_with(test_path, expected_target)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
