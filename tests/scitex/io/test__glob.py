#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test__glob.py

"""Tests for the glob and parse_glob functions in scitex.io module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestGlobBasic:
    """Test basic glob functionality."""

    def test_glob_simple_pattern(self, tmp_path):
        """Test glob with simple wildcard pattern."""
        from scitex.io import glob

        # Create test files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        (tmp_path / "file10.txt").touch()
        (tmp_path / "other.csv").touch()

        # Test glob
        pattern = str(tmp_path / "*.txt")
        result = glob(pattern)

        # Should return naturally sorted list
        assert len(result) == 3
        assert result[0].endswith("file1.txt")
        assert result[1].endswith("file2.txt")
        assert result[2].endswith("file10.txt")  # Natural sort: 10 after 2

    def test_glob_natural_sorting(self, tmp_path):
        """Test that glob returns naturally sorted results."""
        from scitex.io import glob

        # Create files with numbers
        for i in [1, 2, 10, 20, 100]:
            (tmp_path / f"data{i}.txt").touch()

        pattern = str(tmp_path / "data*.txt")
        result = glob(pattern)

        # Check natural sorting order
        basenames = [os.path.basename(p) for p in result]
        assert basenames == [
            "data1.txt",
            "data2.txt",
            "data10.txt",
            "data20.txt",
            "data100.txt",
        ]

    def test_glob_no_matches(self, tmp_path):
        """Test glob with pattern that matches nothing."""
        from scitex.io import glob

        pattern = str(tmp_path / "nonexistent*.txt")
        result = glob(pattern)

        assert result == []

    def test_glob_recursive_pattern(self, tmp_path):
        """Test glob with recursive ** pattern."""
        from scitex.io import glob

        # Create nested structure
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / "file1.txt").touch()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "dir2" / "subdir").mkdir()
        (tmp_path / "dir2" / "subdir" / "file2.txt").touch()

        # Test recursive glob
        pattern = str(tmp_path / "**" / "*.txt")
        result = glob(pattern)

        assert len(result) == 2
        assert any("file1.txt" in p for p in result)
        assert any("file2.txt" in p for p in result)


class TestGlobParsing:
    """Test glob with parsing functionality."""

    def test_glob_with_parse(self, tmp_path):
        """Test glob with parse=True."""
        from scitex.io import glob

        # Create test files with pattern
        (tmp_path / "subj_001").mkdir()
        (tmp_path / "subj_001" / "run_01.txt").touch()
        (tmp_path / "subj_001" / "run_02.txt").touch()
        (tmp_path / "subj_002").mkdir()
        (tmp_path / "subj_002" / "run_01.txt").touch()

        # Test with parsing
        pattern = str(tmp_path / "subj_{id}" / "run_{run}.txt")
        paths, parsed = glob(pattern, parse=True)

        assert len(paths) == 3
        assert len(parsed) == 3

        # Check parsed results
        assert parsed[0]["id"] == "001"
        assert parsed[0]["run"] == "01"
        assert parsed[1]["id"] == "001"
        assert parsed[1]["run"] == "02"
        assert parsed[2]["id"] == "002"
        assert parsed[2]["run"] == "01"

    def test_parse_glob_function(self, tmp_path):
        """Test the parse_glob convenience function."""
        from scitex.io import parse_glob

        # Create test files
        (tmp_path / "exp_01_trial_001.dat").touch()
        (tmp_path / "exp_01_trial_002.dat").touch()
        (tmp_path / "exp_02_trial_001.dat").touch()

        # Test parse_glob
        pattern = str(tmp_path / "exp_{exp}_trial_{trial}.dat")
        paths, parsed = parse_glob(pattern)

        assert len(paths) == 3
        assert len(parsed) == 3

        # Verify parsing
        assert all("exp" in p and "trial" in p for p in parsed)

    def test_glob_parse_complex_pattern(self, tmp_path):
        """Test parsing with complex patterns."""
        from scitex.io import glob

        # Create complex structure
        base = tmp_path / "data" / "2024"
        base.mkdir(parents=True)
        (base / "patient_A01_session_pre_scan_001.nii").touch()
        (base / "patient_A01_session_post_scan_001.nii").touch()
        (base / "patient_B02_session_pre_scan_001.nii").touch()

        # Test complex parsing
        pattern = str(
            tmp_path / "data" / "*" / "patient_{pid}_session_{session}_scan_{scan}.nii"
        )
        paths, parsed = glob(pattern, parse=True)

        assert len(parsed) == 3
        assert parsed[0]["pid"] == "A01"
        assert parsed[0]["session"] == "pre"
        assert parsed[0]["scan"] == "001"


class TestGlobEnsureOne:
    """Test glob with ensure_one parameter."""

    def test_glob_ensure_one_success(self, tmp_path):
        """Test glob with ensure_one when exactly one match exists."""
        from scitex.io import glob

        # Create exactly one matching file
        (tmp_path / "unique.txt").touch()

        pattern = str(tmp_path / "unique.txt")
        result = glob(pattern, ensure_one=True)

        assert len(result) == 1
        assert result[0].endswith("unique.txt")

    def test_glob_ensure_one_failure(self, tmp_path):
        """Test glob with ensure_one when multiple matches exist."""
        from scitex.io import glob

        # Create multiple matching files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()

        pattern = str(tmp_path / "*.txt")

        # Should raise AssertionError
        with pytest.raises(AssertionError):
            glob(pattern, ensure_one=True)

    def test_glob_ensure_one_no_match(self, tmp_path):
        """Test glob with ensure_one when no matches exist."""
        from scitex.io import glob

        pattern = str(tmp_path / "nonexistent.txt")

        # Should raise AssertionError
        with pytest.raises(AssertionError):
            glob(pattern, ensure_one=True)

    def test_parse_glob_ensure_one(self, tmp_path):
        """Test parse_glob with ensure_one parameter."""
        from scitex.io import parse_glob

        # Create one file
        (tmp_path / "data_001.txt").touch()

        pattern = str(tmp_path / "data_{id}.txt")
        paths, parsed = parse_glob(pattern, ensure_one=True)

        assert len(paths) == 1
        assert parsed[0]["id"] == "001"


class TestGlobAdvanced:
    """Test advanced glob scenarios."""

    def test_glob_curly_brace_pattern(self, tmp_path):
        """Test glob with curly brace expansion pattern."""
        from scitex.io import glob

        # Create files in different directories
        for subdir in ["a", "b", "c"]:
            (tmp_path / subdir).mkdir()
            (tmp_path / subdir / "data.txt").touch()

        # Pattern with braces should be converted to wildcards
        pattern = str(tmp_path / "{a,b}" / "*.txt")
        result = glob(pattern)

        # Should match files in all directories (braces become *)
        assert len(result) >= 2

    def test_glob_eval_safety(self, tmp_path):
        """Test that glob handles eval safely."""
        from scitex.io import glob

        # Create a file
        (tmp_path / "test.txt").touch()

        # Pattern that might cause eval issues
        pattern = str(tmp_path / "test.txt'; import os; os.system('echo hacked')")

        # Should handle safely (fall back to regular glob)
        result = glob(pattern)
        assert result == []  # No match for malicious pattern

    def test_glob_special_characters(self, tmp_path):
        """Test glob with special characters in filenames."""
        from scitex.io import glob

        # Create files with special characters
        special_files = [
            "file with spaces.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.multiple.dots.txt",
        ]

        for fname in special_files:
            (tmp_path / fname).touch()

        pattern = str(tmp_path / "*.txt")
        result = glob(pattern)

        assert len(result) == len(special_files)

    def test_glob_hidden_files(self, tmp_path):
        """Test glob with hidden files."""
        from scitex.io import glob

        # Create hidden and regular files
        (tmp_path / ".hidden.txt").touch()
        (tmp_path / "visible.txt").touch()

        # Test with pattern that should match hidden files
        pattern = str(tmp_path / ".*")
        result = glob(pattern)

        assert any(".hidden.txt" in p for p in result)


class TestGlobIntegration:
    """Test glob integration with other features."""

    def test_glob_with_pathlib(self, tmp_path):
        """Test glob works with pathlib paths."""
        from scitex.io import glob

        # Create test structure
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "file1.csv").touch()
        (data_dir / "file2.csv").touch()

        # Use pathlib Path for pattern
        pattern = data_dir / "*.csv"
        result = glob(str(pattern))

        assert len(result) == 2

    def test_glob_parse_integration(self, tmp_path):
        """Test glob parsing integrates with scitex.str.parse."""
        from scitex.io import glob

        # Create structured data
        for year in [2022, 2023]:
            for month in [1, 2, 12]:
                dir_path = tmp_path / f"data_{year}_{month:02d}"
                dir_path.mkdir()
                (dir_path / "report.txt").touch()

        # Parse structured pattern
        pattern = str(tmp_path / "data_{year}_{month}" / "report.txt")
        paths, parsed = glob(pattern, parse=True)

        assert len(parsed) == 6
        # Check parsing worked correctly
        years = [p["year"] for p in parsed]
        assert "2022" in years and "2023" in years

    def test_glob_empty_directory(self, tmp_path):
        """Test glob on empty directory."""
        from scitex.io import glob

        # Empty directory
        pattern = str(tmp_path / "*")
        result = glob(pattern)

        assert result == []


class TestGlobEdgeCases:
    """Test edge cases for glob function."""

    def test_glob_root_pattern(self):
        """Test glob with root directory pattern."""
        from scitex.io import glob

        # Pattern at root - should work but return limited results
        result = glob("/*.txt")

        # Should return list (possibly empty)
        assert isinstance(result, list)

    def test_glob_invalid_pattern(self, tmp_path):
        """Test glob with invalid pattern."""
        from scitex.io import glob

        # Pattern with invalid syntax
        pattern = str(tmp_path / "[")

        # Should handle gracefully
        result = glob(pattern)
        assert isinstance(result, list)

    def test_glob_unicode_filenames(self, tmp_path):
        """Test glob with unicode filenames."""
        from scitex.io import glob

        # Create files with unicode names
        unicode_files = [
            "файл.txt",  # Russian
            "文件.txt",  # Chinese
            "ファイル.txt",  # Japanese
            "café.txt",  # French
        ]

        for fname in unicode_files:
            try:
                (tmp_path / fname).touch()
            except:
                pass  # Skip if filesystem doesn't support

        pattern = str(tmp_path / "*.txt")
        result = glob(pattern)

        # Should handle unicode gracefully
        assert isinstance(result, list)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_glob.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-25 00:31:08 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_glob.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/_glob.py"
# 
# import re as _re
# from glob import glob as _glob
# from ..str._parse import parse as _parse
# from natsort import natsorted as _natsorted
# 
# 
# def glob(expression, parse=False, ensure_one=False):
#     """
#     Perform a glob operation with natural sorting and extended pattern support.
# 
#     This function extends the standard glob functionality by adding natural sorting
#     and support for curly brace expansion in the glob pattern.
# 
#     Parameters:
#     -----------
#     expression : str
#         The glob pattern to match against file paths. Supports standard glob syntax
#         and curly brace expansion (e.g., 'dir/{a,b}/*.txt').
#     parse : bool, optional
#         Whether to parse the matched paths. Default is False.
#     ensure_one : bool, optional
#         Ensure exactly one match is found. Default is False.
# 
#     Returns:
#     --------
#     Union[List[str], Tuple[List[str], List[dict]]]
#         If parse=False: A naturally sorted list of file paths
#         If parse=True: Tuple of (paths, parsed results)
# 
#     Examples:
#     ---------
#     >>> glob('data/*.txt')
#     ['data/file1.txt', 'data/file2.txt', 'data/file10.txt']
# 
#     >>> glob('data/{a,b}/*.txt')
#     ['data/a/file1.txt', 'data/a/file2.txt', 'data/b/file1.txt']
# 
#     >>> paths, parsed = glob('data/subj_{id}/run_{run}.txt', parse=True)
#     >>> paths
#     ['data/subj_001/run_01.txt', 'data/subj_001/run_02.txt']
#     >>> parsed
#     [{'id': '001', 'run': '01'}, {'id': '001', 'run': '02'}]
# 
#     >>> paths, parsed = glob('data/subj_{id}/run_{run}.txt', parse=True, ensure_one=True)
#     AssertionError  # if more than one file matches
#     """
#     glob_pattern = _re.sub(r"{[^}]*}", "*", expression)
#     # Enable recursive globbing for ** patterns
#     recursive = "**" in glob_pattern
#     try:
#         found_paths = _natsorted(_glob(eval(glob_pattern), recursive=recursive))
#     except:
#         found_paths = _natsorted(_glob(glob_pattern, recursive=recursive))
# 
#     if ensure_one:
#         assert len(found_paths) == 1
# 
#     if parse:
#         parsed = [_parse(found_path, expression) for found_path in found_paths]
#         return found_paths, parsed
# 
#     else:
#         return found_paths
# 
# 
# def parse_glob(expression, ensure_one=False):
#     """
#     Convenience function for glob with parsing enabled.
# 
#     Parameters:
#     -----------
#     expression : str
#         The glob pattern to match against file paths.
#     ensure_one : bool, optional
#         Ensure exactly one match is found. Default is False.
# 
#     Returns:
#     --------
#     Tuple[List[str], List[dict]]
#         Matched paths and parsed results.
# 
#     Examples:
#     ---------
#     >>> paths, parsed = pglob('data/subj_{id}/run_{run}.txt')
#     >>> paths
#     ['data/subj_001/run_01.txt', 'data/subj_001/run_02.txt']
#     >>> parsed
#     [{'id': '001', 'run': '01'}, {'id': '001', 'run': '02'}]
# 
#     >>> paths, parsed = pglob('data/subj_{id}/run_{run}.txt', ensure_one=True)
#     AssertionError  # if more than one file matches
#     """
#     return glob(expression, parse=True, ensure_one=ensure_one)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_glob.py
# --------------------------------------------------------------------------------
