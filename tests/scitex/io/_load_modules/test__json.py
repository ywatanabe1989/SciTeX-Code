#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:20:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__json.py

"""Tests for JSON file loading functionality.

This module tests the _load_json function from scitex.io._load_modules._json,
which handles loading JSON files with proper validation and error handling.
"""

import json
import os
import tempfile
from pathlib import Path
import pytest


def test_load_json_basic():
    """Test loading a basic JSON file."""
    from scitex.io._load_modules import _load_json
    
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        json.dump(data, f)
        temp_path = f.name
    
    try:
        # Load the JSON file
        loaded_data = _load_json(temp_path)
        
        # Verify the data
        assert loaded_data == data
        assert loaded_data["key"] == "value"
        assert loaded_data["number"] == 42
        assert loaded_data["list"] == [1, 2, 3]
    finally:
        # Clean up
        os.unlink(temp_path)


def test_load_json_complex_structure():
    """Test loading JSON with nested structures."""
    from scitex.io._load_modules import _load_json
    
    # Create complex data
    complex_data = {
        "nested": {
            "level1": {
                "level2": {
                    "value": "deep"
                }
            }
        },
        "array_of_objects": [
            {"id": 1, "name": "first"},
            {"id": 2, "name": "second"}
        ],
        "null_value": None,
        "boolean": True,
        "float": 3.14159
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(complex_data, f)
        temp_path = f.name
    
    try:
        loaded_data = _load_json(temp_path)
        
        assert loaded_data == complex_data
        assert loaded_data["nested"]["level1"]["level2"]["value"] == "deep"
        assert len(loaded_data["array_of_objects"]) == 2
        assert loaded_data["null_value"] is None
        assert loaded_data["boolean"] is True
        assert abs(loaded_data["float"] - 3.14159) < 1e-6
    finally:
        os.unlink(temp_path)


def test_load_json_invalid_extension():
    """Test that loading non-JSON file raises ValueError."""
    from scitex.io._load_modules import _load_json
    
    # Try to load a file without .json extension
    with pytest.raises(ValueError, match="File must have .json extension"):
        _load_json("test.txt")
    
    with pytest.raises(ValueError, match="File must have .json extension"):
        _load_json("/path/to/file.yaml")


def test_load_json_invalid_json_content():
    """Test handling of invalid JSON content."""
    from scitex.io._load_modules import _load_json
    
    # Create a file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("This is not valid JSON {incomplete:")
        temp_path = f.name
    
    try:
        with pytest.raises(json.JSONDecodeError):
            _load_json(temp_path)
    finally:
        os.unlink(temp_path)


def test_load_json_empty_file():
    """Test loading an empty JSON file."""
    from scitex.io._load_modules import _load_json
    
    # Create an empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        with pytest.raises(json.JSONDecodeError):
            _load_json(temp_path)
    finally:
        os.unlink(temp_path)


def test_load_json_unicode_content():
    """Test loading JSON with Unicode characters."""
    from scitex.io._load_modules import _load_json
    
    # Create JSON with Unicode
    unicode_data = {
        "japanese": "こんにちは",
        "emoji": "🎉🐍",
        "mixed": "Hello 世界"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(unicode_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        loaded_data = _load_json(temp_path)
        
        assert loaded_data == unicode_data
        assert loaded_data["japanese"] == "こんにちは"
        assert loaded_data["emoji"] == "🎉🐍"
    finally:
        os.unlink(temp_path)


def test_load_json_nonexistent_file():
    """Test loading a nonexistent file."""
    from scitex.io._load_modules import _load_json
    
    with pytest.raises(FileNotFoundError):
        _load_json("/nonexistent/path/file.json")


def test_load_json_large_file():
    """Test loading a large JSON file."""
    from scitex.io._load_modules import _load_json
    
    # Create a large JSON structure
    large_data = {
        f"key_{i}": {
            "value": i,
            "data": list(range(100))
        } for i in range(100)
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(large_data, f)
        temp_path = f.name
    
    try:
        loaded_data = _load_json(temp_path)
        
        assert len(loaded_data) == 100
        assert loaded_data["key_50"]["value"] == 50
        assert len(loaded_data["key_99"]["data"]) == 100
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
