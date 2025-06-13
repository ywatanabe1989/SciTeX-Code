#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:22:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__yaml.py

"""Tests for YAML file loading functionality.

This module tests the _load_yaml function from scitex.io._load_modules._yaml,
which handles loading YAML files with validation and optional key lowercasing.
"""

import os
import tempfile
import pytest
import yaml


def test_load_yaml_basic():
    """Test loading a basic YAML file."""
from scitex.io._load_modules import _load_yaml
    
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml_data = """
key: value
number: 42
list:
  - 1
  - 2
  - 3
"""
        f.write(yaml_data)
        temp_path = f.name
    
    try:
        loaded_data = _load_yaml(temp_path)
        
        assert loaded_data["key"] == "value"
        assert loaded_data["number"] == 42
        assert loaded_data["list"] == [1, 2, 3]
    finally:
        os.unlink(temp_path)


def test_load_yaml_yml_extension():
    """Test loading a .yml file."""
from scitex.io._load_modules import _load_yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("test: yml_extension")
        temp_path = f.name
    
    try:
        loaded_data = _load_yaml(temp_path)
        assert loaded_data["test"] == "yml_extension"
    finally:
        os.unlink(temp_path)


def test_load_yaml_complex_structure():
    """Test loading YAML with nested structures."""
from scitex.io._load_modules import _load_yaml
    
    yaml_data = """
nested:
  level1:
    level2:
      value: deep
array_of_objects:
  - id: 1
    name: first
  - id: 2
    name: second
null_value: null
boolean: true
float: 3.14159
multiline: |
  This is a
  multiline string
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_data)
        temp_path = f.name
    
    try:
        loaded_data = _load_yaml(temp_path)
        
        assert loaded_data["nested"]["level1"]["level2"]["value"] == "deep"
        assert len(loaded_data["array_of_objects"]) == 2
        assert loaded_data["null_value"] is None
        assert loaded_data["boolean"] is True
        assert abs(loaded_data["float"] - 3.14159) < 1e-6
        assert "multiline string" in loaded_data["multiline"]
    finally:
        os.unlink(temp_path)


def test_load_yaml_lowercase_keys():
    """Test loading YAML with lowercase key option."""
from scitex.io._load_modules import _load_yaml
    
    yaml_data = """
UpperCase: value1
MixedCase: value2
lowercase: value3
ALLCAPS: value4
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_data)
        temp_path = f.name
    
    try:
        # Load without lowercasing
        normal_data = _load_yaml(temp_path)
        assert "UpperCase" in normal_data
        assert "MixedCase" in normal_data
        
        # Load with lowercasing
        lower_data = _load_yaml(temp_path, lower=True)
        assert "uppercase" in lower_data
        assert "mixedcase" in lower_data
        assert "lowercase" in lower_data
        assert "allcaps" in lower_data
        
        # Verify values are preserved
        assert lower_data["uppercase"] == "value1"
        assert lower_data["mixedcase"] == "value2"
        assert lower_data["lowercase"] == "value3"
        assert lower_data["allcaps"] == "value4"
    finally:
        os.unlink(temp_path)


def test_load_yaml_invalid_extension():
    """Test that loading non-YAML file raises ValueError."""
from scitex.io._load_modules import _load_yaml
    
    with pytest.raises(ValueError, match="File must have .yaml or .yml extension"):
        _load_yaml("test.txt")
    
    with pytest.raises(ValueError, match="File must have .yaml or .yml extension"):
        _load_yaml("/path/to/file.json")


def test_load_yaml_invalid_yaml_content():
    """Test handling of invalid YAML content."""
from scitex.io._load_modules import _load_yaml
    
    # Create a file with invalid YAML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid:\n  - item1\n    item2")  # Bad indentation
        temp_path = f.name
    
    try:
        with pytest.raises(yaml.YAMLError):
            _load_yaml(temp_path)
    finally:
        os.unlink(temp_path)


def test_load_yaml_empty_file():
    """Test loading an empty YAML file."""
from scitex.io._load_modules import _load_yaml
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name
    
    try:
        loaded_data = _load_yaml(temp_path)
        assert loaded_data is None
    finally:
        os.unlink(temp_path)


def test_load_yaml_unicode_content():
    """Test loading YAML with Unicode characters."""
from scitex.io._load_modules import _load_yaml
    
    yaml_data = """
japanese: こんにちは
emoji: 🎉🐍
mixed: Hello 世界
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write(yaml_data)
        temp_path = f.name
    
    try:
        loaded_data = _load_yaml(temp_path)
        
        assert loaded_data["japanese"] == "こんにちは"
        assert loaded_data["emoji"] == "🎉🐍"
        assert loaded_data["mixed"] == "Hello 世界"
    finally:
        os.unlink(temp_path)


def test_load_yaml_nonexistent_file():
    """Test loading a nonexistent file."""
from scitex.io._load_modules import _load_yaml
    
    with pytest.raises(FileNotFoundError):
        _load_yaml("/nonexistent/path/file.yaml")


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
