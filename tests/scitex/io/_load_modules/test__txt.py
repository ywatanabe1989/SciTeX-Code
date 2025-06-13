#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:30:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__txt.py

"""Tests for text file loading functionality.

This module tests the _load_txt function from scitex.io._load_modules._txt,
which handles loading text files with various encodings and formats.
"""

import os
import tempfile
import warnings
import pytest


def test_load_txt_basic():
    """Test loading a basic text file."""
from scitex.io._load_modules import _load_txt
    
    content = "Hello World\nThis is a test\nThird line"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test default behavior (return full content)
        loaded_content = _load_txt(temp_path)
        assert loaded_content == content
        
        # Test with strip
        loaded_stripped = _load_txt(temp_path, strip=True)
        assert loaded_stripped == content.strip()
        
        # Test as_lines mode
        loaded_lines = _load_txt(temp_path, as_lines=True)
        assert loaded_lines == ["Hello World", "This is a test", "Third line"]
    finally:
        os.unlink(temp_path)


def test_load_txt_empty_lines():
    """Test handling of empty lines."""
from scitex.io._load_modules import _load_txt
    
    content = "Line 1\n\n\nLine 2\n   \nLine 3\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # as_lines mode should filter out empty lines
        loaded_lines = _load_txt(temp_path, as_lines=True)
        assert loaded_lines == ["Line 1", "Line 2", "Line 3"]
        
        # Default mode should preserve everything
        loaded_content = _load_txt(temp_path)
        assert loaded_content == content
    finally:
        os.unlink(temp_path)


def test_load_txt_different_extensions():
    """Test loading files with different extensions."""
from scitex.io._load_modules import _load_txt
    
    content = "Test content"
    extensions = ['.txt', '.log', '.event', '.py', '.sh']
    
    for ext in extensions:
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            loaded = _load_txt(temp_path)
            assert loaded == content
        finally:
            os.unlink(temp_path)


def test_load_txt_unexpected_extension_warning():
    """Test warning for unexpected file extensions."""
from scitex.io._load_modules import _load_txt
    
    content = "Test content"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            loaded = _load_txt(temp_path)
            
            # Should still load the file
            assert loaded == content
            
            # Should have warned about unexpected extension
            assert len(w) == 1
            assert "Unexpected extension" in str(w[0].message)
    finally:
        os.unlink(temp_path)


def test_load_txt_unicode_content():
    """Test loading files with Unicode content."""
from scitex.io._load_modules import _load_txt
    
    unicode_content = "Hello 世界\n日本語テスト\n🎉 Emoji test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(unicode_content)
        temp_path = f.name
    
    try:
        loaded = _load_txt(temp_path)
        assert loaded == unicode_content
        
        # Test as_lines mode with Unicode
        loaded_lines = _load_txt(temp_path, as_lines=True)
        assert loaded_lines == ["Hello 世界", "日本語テスト", "🎉 Emoji test"]
    finally:
        os.unlink(temp_path)


def test_load_txt_different_encodings():
    """Test loading files with different encodings."""
from scitex.io._load_modules import _load_txt
    
    # Test Latin-1 encoded content
    latin1_content = "Café résumé naïve"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='latin1') as f:
        f.write(latin1_content)
        temp_path = f.name
    
    try:
        # Should handle encoding fallback
        loaded = _load_txt(temp_path)
        assert loaded == latin1_content
    finally:
        os.unlink(temp_path)


def test_load_txt_with_strip():
    """Test strip functionality."""
from scitex.io._load_modules import _load_txt
    
    content_with_whitespace = "  \n  Hello World  \n  \n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content_with_whitespace)
        temp_path = f.name
    
    try:
        # Without strip
        loaded = _load_txt(temp_path)
        assert loaded == content_with_whitespace
        
        # With strip
        loaded_stripped = _load_txt(temp_path, strip=True)
        assert loaded_stripped == "Hello World"
        
        # as_lines with strip
        loaded_lines = _load_txt(temp_path, as_lines=True, strip=True)
        assert loaded_lines == ["Hello World"]
    finally:
        os.unlink(temp_path)


def test_load_txt_nonexistent_file():
    """Test loading a nonexistent file."""
from scitex.io._load_modules import _load_txt
    
    # The current implementation raises FileNotFoundError directly
    with pytest.raises(FileNotFoundError):
        _load_txt("/nonexistent/path/file.txt")


def test_load_txt_empty_file():
    """Test loading an empty file."""
from scitex.io._load_modules import _load_txt
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name
    
    try:
        # Default mode
        loaded = _load_txt(temp_path)
        assert loaded == ""
        
        # as_lines mode
        loaded_lines = _load_txt(temp_path, as_lines=True)
        assert loaded_lines == []
    finally:
        os.unlink(temp_path)


def test_load_txt_large_file():
    """Test loading a large text file."""
from scitex.io._load_modules import _load_txt
    
    # Create a file with many lines
    lines = [f"Line {i}: " + "x" * 100 for i in range(1000)]
    content = "\n".join(lines)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Load full content
        loaded = _load_txt(temp_path)
        assert loaded == content
        
        # Load as lines
        loaded_lines = _load_txt(temp_path, as_lines=True)
        assert len(loaded_lines) == 1000
        assert loaded_lines[0] == lines[0]
        assert loaded_lines[-1] == lines[-1]
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
