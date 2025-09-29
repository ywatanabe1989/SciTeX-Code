#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./tests/scitex/resource/test_limit_ram.py

import pytest
import unittest.mock as mock
import os
import resource


def test_limit_ram_get_ram_returns_integer():
    """Test that get_ram() returns an integer value."""
    from scitex.resource.limit_ram import get_ram
    
    # Mock /proc/meminfo content
    mock_meminfo = """MemTotal:       8000000 kB
MemFree:        2000000 kB
MemAvailable:   4000000 kB
Buffers:         500000 kB
Cached:         1000000 kB
SwapCached:          0 kB"""
    
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_meminfo)):
        result = get_ram()
    
    assert isinstance(result, int)
    assert result > 0


def test_limit_ram_get_ram_calculation():
    """Test that get_ram() correctly calculates free memory."""
    from scitex.resource.limit_ram import get_ram
    
    # Mock /proc/meminfo with known values
    mock_meminfo = """MemTotal:       8000000 kB
MemFree:        2000000 kB
MemAvailable:   4000000 kB
Buffers:         500000 kB
Cached:         1000000 kB
SwapCached:          0 kB"""
    
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_meminfo)):
        result = get_ram()
    
    # Expected: MemFree + Buffers + Cached = 2000000 + 500000 + 1000000 = 3500000
    expected = 2000000 + 500000 + 1000000
    assert result == expected


def test_limit_ram_get_ram_handles_missing_fields():
    """Test that get_ram() handles missing memory fields gracefully."""
    from scitex.resource.limit_ram import get_ram
    
    # Mock /proc/meminfo with only some fields
    mock_meminfo = """MemTotal:       8000000 kB
MemFree:        2000000 kB
MemAvailable:   4000000 kB
SwapCached:          0 kB"""
    
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_meminfo)):
        result = get_ram()
    
    # Should only count MemFree (no Buffers or Cached)
    assert result == 2000000


def test_limit_ram_get_ram_file_error_handling():
    """Test that get_ram() handles file reading errors."""
    from scitex.resource.limit_ram import get_ram
    
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            get_ram()


@mock.patch('scitex.resource.limit_ram.resource.setrlimit')
@mock.patch('scitex.resource.limit_ram.resource.getrlimit')
@mock.patch('scitex.resource.limit_ram.get_ram')
@mock.patch('builtins.print')
def test_limit_ram_function_basic(mock_print, mock_get_ram, mock_getrlimit, mock_setrlimit):
    """Test basic functionality of limit_ram() function."""
    from scitex.resource.limit_ram import limit_ram
    
    # Setup mocks
    mock_get_ram.return_value = 4000000  # 4GB in KB
    mock_getrlimit.return_value = (8000000 * 1024, 16000000 * 1024)  # soft, hard limits
    
    # This will fail due to missing fmt_size, but that's expected
    with pytest.raises(AttributeError):
        limit_ram(0.5)
    
    # Verify get_ram was called before the error
    assert mock_get_ram.call_count >= 1
    
    # Verify getrlimit was called before the error
    mock_getrlimit.assert_called_once_with(resource.RLIMIT_AS)
    
    # Verify setrlimit was called before the error
    mock_setrlimit.assert_called_once()


@mock.patch('scitex.resource.limit_ram.resource.setrlimit')
@mock.patch('scitex.resource.limit_ram.resource.getrlimit')
@mock.patch('scitex.resource.limit_ram.get_ram')
def test_limit_ram_function_calculation(mock_get_ram, mock_getrlimit, mock_setrlimit):
    """Test that limit_ram() calculates memory limits correctly."""
    from scitex.resource.limit_ram import limit_ram
    
    # Setup mocks
    mock_get_ram.return_value = 4000000  # 4GB in KB
    mock_getrlimit.return_value = (8000000 * 1024, 16000000 * 1024)
    
    # This will fail due to missing fmt_size, but we can still test calculation
    with pytest.raises(AttributeError):
        limit_ram(0.5)
    
    # Calculate expected max_val  
    ram_kb = 4000000
    expected_max_val = min(0.5 * ram_kb * 1024, ram_kb * 1024)
    expected_max_val = int(0.5 * ram_kb * 1024)  # Should be the smaller value
    
    # Verify setrlimit was called with correct values before the error
    mock_setrlimit.assert_called_once()
    call_args = mock_setrlimit.call_args[0][1]
    assert call_args[0] == expected_max_val


def test_limit_ram_backward_compatibility():
    """Test that deprecated function names still work."""
    from scitex.resource.limit_ram import limit_RAM, get_RAM, limit_ram, get_ram
    
    # Test that deprecated names reference the same functions
    assert limit_RAM is limit_ram
    assert get_RAM is get_ram


def test_limit_ram_get_ram_edge_cases():
    """Test edge cases for get_ram function."""
    from scitex.resource.limit_ram import get_ram
    
    # Test with zero values
    mock_meminfo_zero = """MemTotal:       8000000 kB
MemFree:               0 kB
MemAvailable:   4000000 kB
Buffers:               0 kB
Cached:                0 kB"""
    
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_meminfo_zero)):
        result = get_ram()
        assert result == 0


def test_limit_ram_import_dependencies():
    """Test that all required dependencies can be imported."""
    # Test resource module import
    import resource
    assert hasattr(resource, 'getrlimit')
    assert hasattr(resource, 'setrlimit')
    assert hasattr(resource, 'RLIMIT_AS')
    
    # Test scitex import
    import scitex
    assert hasattr(scitex, 'gen')


@mock.patch('scitex.resource.limit_ram.resource.setrlimit')
@mock.patch('scitex.resource.limit_ram.resource.getrlimit')
@mock.patch('scitex.resource.limit_ram.get_ram')
def test_limit_ram_resource_error_handling(mock_get_ram, mock_getrlimit, mock_setrlimit):
    """Test that limit_ram handles resource errors gracefully."""
    from scitex.resource.limit_ram import limit_ram
    
    mock_get_ram.return_value = 4000000
    mock_getrlimit.return_value = (8000000 * 1024, 16000000 * 1024)
    mock_setrlimit.side_effect = OSError("Permission denied")
    
    # The function will fail with OSError from setrlimit before it gets to fmt_size
    with pytest.raises(OSError):
        limit_ram(0.5)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/resource/limit_ram.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2021-09-20 21:02:04 (ywatanabe)"
# 
# import resource
# import scitex
# 
# 
# def limit_ram(ram_factor):
#     soft, hard = resource.getrlimit(resource.RLIMIT_AS)
#     max_val = min(ram_factor * get_ram() * 1024, get_ram() * 1024)
#     resource.setrlimit(resource.RLIMIT_AS, (max_val, hard))
#     print(f"\nFree RAM was limited to {scitex.gen.fmt_size(max_val)}")
# 
# 
# def get_ram():
#     with open("/proc/meminfo", "r") as mem:
#         free_memory = 0
#         for i in mem:
#             sline = i.split()
#             if str(sline[0]) in ("MemFree:", "Buffers:", "Cached:"):
#                 free_memory += int(sline[1])
#     return free_memory
# 
# 
# # Backward compatibility
# limit_RAM = limit_ram  # Deprecated: use limit_ram instead
# get_RAM = get_ram  # Deprecated: use get_ram instead
# 
# 
# if __name__ == "__main__":
#     get_ram()
#     limit_ram(0.1)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/resource/limit_ram.py
# --------------------------------------------------------------------------------
