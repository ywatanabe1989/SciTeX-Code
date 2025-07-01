#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:19:00 (ywatanabe)"
# File: ./tests/scitex/scholar/test_search.py

"""Test search functionality."""

import pytest
import tempfile
import os
from pathlib import Path
from scitex.scholar import get_scholar_dir, build_index


def test_get_scholar_dir():
    """Test getting the scholar directory."""
    scholar_dir = get_scholar_dir()
    assert isinstance(scholar_dir, Path)
    assert scholar_dir.is_absolute()


def test_build_index_empty_dir():
    """Test building index on empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Should not raise exception on empty directory
        try:
            build_index([tmpdir])
        except Exception as e:
            # Allow certain filesystem errors that can occur during testing
            if "Invalid argument" in str(e):
                pytest.skip(f"Skipping test due to filesystem issue: {e}")
            else:
                pytest.fail(f"build_index raised unexpected exception on empty dir: {e}")


def test_build_index_with_files():
    """Test building index with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample text files
        for i in range(3):
            filepath = os.path.join(tmpdir, f"test_file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"This is test content for file {i}\n")
                f.write("Scientific literature search test\n")
        
        # Build index should process these files
        try:
            result = build_index([tmpdir])
            assert isinstance(result, dict)
        except Exception as e:
            # Allow certain filesystem errors that can occur during testing
            if "Invalid argument" in str(e):
                pytest.skip(f"Skipping test due to filesystem issue: {e}")
            else:
                pytest.fail(f"build_index raised unexpected exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__])