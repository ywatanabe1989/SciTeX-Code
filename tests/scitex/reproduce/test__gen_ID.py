#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:08:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__gen_ID.py

"""Tests for unique ID generation functionality."""

import os
import pytest
import re
from datetime import datetime
from unittest.mock import patch


def test_gen_id_basic():
    """Test basic ID generation."""
from scitex.str import gen_id
    
    id_str = gen_id()
    
    # Should contain underscore separator
    assert "_" in id_str
    
    # Should have timestamp and random parts
    parts = id_str.split("_")
    assert len(parts) == 2
    
    # Random part should be 8 characters by default
    assert len(parts[1]) == 8
    
    # Random part should be alphanumeric
    assert parts[1].isalnum()


def test_gen_id_default_format():
    """Test default timestamp format."""
from scitex.str import gen_id
    
    id_str = gen_id()
    timestamp_part = id_str.split("_")[0]
    
    # Should match format: YYYY-MM-DD-HHhMMmSSs
    pattern = r'\d{4}Y-\d{2}M-\d{2}D-\d{2}h\d{2}m\d{2}s'
    assert re.match(pattern, timestamp_part)


def test_gen_id_custom_time_format():
    """Test custom timestamp format."""
from scitex.str import gen_id
    
    # Test simple format
    id_str = gen_id(time_format="%Y%m%d")
    timestamp_part = id_str.split("_")[0]
    
    # Should be 8 digits (YYYYMMDD)
    assert len(timestamp_part) == 8
    assert timestamp_part.isdigit()
    
    # Test another format
    id_str = gen_id(time_format="%Y-%m-%d_%H:%M")
    timestamp_part = id_str.split("_")[0]
    
    # Should match YYYY-MM-DD format (before underscore)
    pattern = r'\d{4}-\d{2}-\d{2}'
    assert re.match(pattern, timestamp_part)


def test_gen_id_custom_random_length():
    """Test custom random string length."""
from scitex.str import gen_id
    
    # Test different lengths
    for n in [1, 4, 16, 32]:
        id_str = gen_id(N=n)
        random_part = id_str.split("_")[1]
        assert len(random_part) == n
        assert random_part.isalnum()


def test_gen_id_zero_random_length():
    """Test with zero random characters."""
from scitex.str import gen_id
    
    id_str = gen_id(N=0)
    
    # Should still have underscore but empty random part
    assert id_str.endswith("_")
    parts = id_str.split("_")
    assert len(parts) == 2
    assert parts[1] == ""


def test_gen_id_uniqueness():
    """Test that generated IDs are unique."""
from scitex.str import gen_id
    
    ids = [gen_id() for _ in range(100)]
    
    # All IDs should be unique
    assert len(set(ids)) == len(ids)


def test_gen_id_random_characters():
    """Test random character composition."""
from scitex.str import gen_id
    import string
    
    # Generate many IDs to test character set
    ids = [gen_id(N=50) for _ in range(10)]
    
    valid_chars = set(string.ascii_letters + string.digits)
    
    for id_str in ids:
        random_part = id_str.split("_")[1]
        random_chars = set(random_part)
        
        # All characters should be valid
        assert random_chars.issubset(valid_chars)


@patch('scitex.str._gen_ID._datetime')
def test_gen_id_deterministic_timestamp(mock_datetime):
    """Test with mocked datetime for deterministic testing."""
from scitex.str import gen_id
    
    # Mock a specific datetime
    mock_time = datetime(2025, 6, 2, 15, 30, 45)
    mock_datetime.now.return_value = mock_time
    
    # Test default format
    id_str = gen_id()
    timestamp_part = id_str.split("_")[0]
    expected = "2025Y-06M-02D-15h30m45s"
    assert timestamp_part == expected
    
    # Test custom format
    id_str = gen_id(time_format="%Y%m%d_%H%M%S")
    timestamp_part = id_str.split("_")[0]
    expected = "20250602"  # Only first part before underscore
    assert timestamp_part == expected


def test_gen_id_backward_compatibility():
    """Test backward compatibility alias."""
from scitex.str import gen_ID, gen_id
    
    # gen_ID should be the same function
    assert gen_ID is gen_id
    
    # Should work the same way
    id1 = gen_id()
    id2 = gen_ID()
    
    # Both should have same format
    assert "_" in id1
    assert "_" in id2
    assert len(id1.split("_")[1]) == 8
    assert len(id2.split("_")[1]) == 8


def test_gen_id_time_precision():
    """Test that IDs are unique even with rapid generation."""
from scitex.str import gen_id
    import time
    
    # Generate multiple IDs rapidly
    ids = []
    for _ in range(10):
        ids.append(gen_id(time_format="%Y%m%d_%H%M%S"))
        time.sleep(0.01)  # Very short delay
    
    # All IDs should be unique (due to random parts even if timestamps same)
    assert len(set(ids)) == len(ids)
    
    # All should have proper format
    for id_str in ids:
        parts = id_str.split("_")
        assert len(parts) >= 2  # timestamp_random (timestamp may have more underscores)
        assert parts[-1].isalnum()  # random part should be alphanumeric
        assert len(parts[-1]) == 8  # default random length


def test_gen_id_empty_time_format():
    """Test with empty time format."""
from scitex.str import gen_id
    
    id_str = gen_id(time_format="")
    
    # Should have empty timestamp part but still have structure
    parts = id_str.split("_")
    assert len(parts) == 2
    assert parts[0] == ""
    assert len(parts[1]) == 8


def test_gen_id_special_time_format():
    """Test with special characters in time format."""
from scitex.str import gen_id
    
    # Test format with special characters
    id_str = gen_id(time_format="exp-%Y-%m-%d")
    timestamp_part = id_str.split("_")[0]
    
    assert timestamp_part.startswith("exp-")
    assert re.match(r'exp-\d{4}-\d{2}-\d{2}', timestamp_part)


def test_gen_id_large_random_length():
    """Test with large random string length."""
from scitex.str import gen_id
    
    id_str = gen_id(N=1000)
    random_part = id_str.split("_")[1]
    
    assert len(random_part) == 1000
    assert random_part.isalnum()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])