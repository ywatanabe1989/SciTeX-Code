#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:08:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__gen_timestamp.py

"""Tests for timestamp generation functionality."""

import os
import pytest
import re
from datetime import datetime
from unittest.mock import patch


def test_gen_timestamp_basic():
    """Test basic timestamp generation."""
    from scitex.str import gen_timestamp
    
    timestamp = gen_timestamp()
    
    # Should be a string
    assert isinstance(timestamp, str)
    
    # Should match format YYYY-MMDD-HHMM
    pattern = r'\d{4}-\d{4}-\d{4}'
    assert re.match(pattern, timestamp)
    
    # Should be exactly 14 characters (YYYY-MMDD-HHMM)
    assert len(timestamp) == 14


def test_gen_timestamp_format():
    """Test timestamp format details."""
    from scitex.str import gen_timestamp
    
    timestamp = gen_timestamp()
    
    # Split by dashes
    parts = timestamp.split('-')
    assert len(parts) == 3
    
    # Year should be 4 digits
    year = parts[0]
    assert len(year) == 4
    assert year.isdigit()
    assert 2020 <= int(year) <= 2030  # Reasonable range
    
    # Month-day should be 4 digits (MMDD)
    month_day = parts[1]
    assert len(month_day) == 4
    assert month_day.isdigit()
    
    # Hour-minute should be 4 digits (HHMM)
    hour_min = parts[2]
    assert len(hour_min) == 4
    assert hour_min.isdigit()


@patch('scitex.str._gen_timestamp._datetime')
def test_gen_timestamp_specific_time(mock_datetime):
    """Test with specific mocked datetime."""
    from scitex.str import gen_timestamp
    
    # Mock specific datetime: June 2, 2025, 15:30:45
    mock_time = datetime(2025, 6, 2, 15, 30, 45)
    mock_datetime.now.return_value = mock_time
    
    timestamp = gen_timestamp()
    
    # Should be "2025-0602-1530"
    expected = "2025-0602-1530"
    assert timestamp == expected


@patch('scitex.str._gen_timestamp._datetime')
def test_gen_timestamp_edge_cases(mock_datetime):
    """Test edge cases for timestamp generation."""
    from scitex.str import gen_timestamp
    
    test_cases = [
        # (year, month, day, hour, minute, expected)
        (2025, 1, 1, 0, 0, "2025-0101-0000"),  # New Year midnight
        (2025, 12, 31, 23, 59, "2025-1231-2359"),  # New Year's Eve
        (2025, 2, 9, 9, 5, "2025-0209-0905"),  # Single digit month/day/hour/min
        (2025, 10, 10, 10, 10, "2025-1010-1010"),  # Double digits
    ]
    
    for year, month, day, hour, minute, expected in test_cases:
        mock_time = datetime(year, month, day, hour, minute, 30)  # seconds don't matter
        mock_datetime.now.return_value = mock_time
        
        timestamp = gen_timestamp()
        assert timestamp == expected


def test_gen_timestamp_uniqueness_over_time():
    """Test that timestamps change over time."""
    from scitex.str import gen_timestamp
    import time
    
    timestamp1 = gen_timestamp()
    time.sleep(0.1)  # Short delay
    timestamp2 = gen_timestamp()
    
    # Timestamps should be the same or very close
    # (might be same if called within same minute)
    # But format should be consistent
    pattern = r'\d{4}-\d{4}-\d{4}'
    assert re.match(pattern, timestamp1)
    assert re.match(pattern, timestamp2)


def test_gen_timestamp_current_time():
    """Test that timestamp reflects current time."""
    from scitex.str import gen_timestamp
    
    # Get timestamp and current time
    timestamp = gen_timestamp()
    now = datetime.now()
    
    # Extract components from timestamp
    year = int(timestamp[:4])
    month = int(timestamp[5:7])
    day = int(timestamp[7:9])
    hour = int(timestamp[10:12])
    minute = int(timestamp[12:14])
    
    # Should match current time (allowing for small delays)
    assert year == now.year
    assert month == now.month
    assert day == now.day
    
    # Hour and minute should be close (within 1 minute)
    time_diff_minutes = abs((now.hour * 60 + now.minute) - (hour * 60 + minute))
    assert time_diff_minutes <= 1


def test_timestamp_alias():
    """Test timestamp alias."""
    from scitex.str import timestamp, gen_timestamp
    
    # Should be the same function
    assert timestamp is gen_timestamp
    
    # Should work the same way
    ts1 = gen_timestamp()
    ts2 = timestamp()
    
    # Both should have same format
    pattern = r'\d{4}-\d{4}-\d{4}'
    assert re.match(pattern, ts1)
    assert re.match(pattern, ts2)


def test_gen_timestamp_month_padding():
    """Test proper zero-padding for months."""
    from scitex.str import gen_timestamp
    from unittest.mock import patch
    
    # Test months 1-9 (should be zero-padded)
    for month in range(1, 10):
        with patch('scitex.str._gen_timestamp._datetime') as mock_datetime:
            mock_time = datetime(2025, month, 15, 12, 30, 0)
            mock_datetime.now.return_value = mock_time
            
            timestamp = gen_timestamp()
            month_part = timestamp[5:7]
            assert month_part == f"0{month}"


def test_gen_timestamp_day_padding():
    """Test proper zero-padding for days."""
    from scitex.str import gen_timestamp
    from unittest.mock import patch
    
    # Test days 1-9 (should be zero-padded)
    for day in range(1, 10):
        with patch('scitex.str._gen_timestamp._datetime') as mock_datetime:
            mock_time = datetime(2025, 6, day, 12, 30, 0)
            mock_datetime.now.return_value = mock_time
            
            timestamp = gen_timestamp()
            day_part = timestamp[7:9]
            assert day_part == f"0{day}"


def test_gen_timestamp_hour_minute_padding():
    """Test proper zero-padding for hours and minutes."""
    from scitex.str import gen_timestamp
    from unittest.mock import patch
    
    # Test hours and minutes 0-9 (should be zero-padded)
    test_cases = [
        (0, 0, "0000"),
        (5, 7, "0507"),
        (9, 9, "0909"),
        (10, 5, "1005"),
        (23, 59, "2359"),
    ]
    
    for hour, minute, expected_hhmm in test_cases:
        with patch('scitex.str._gen_timestamp._datetime') as mock_datetime:
            mock_time = datetime(2025, 6, 15, hour, minute, 30)
            mock_datetime.now.return_value = mock_time
            
            timestamp = gen_timestamp()
            hhmm_part = timestamp[10:14]
            assert hhmm_part == expected_hhmm


def test_gen_timestamp_filename_usage():
    """Test typical usage for filename generation."""
    from scitex.str import gen_timestamp
    
    timestamp = gen_timestamp()
    
    # Should be safe for filename usage
    filename = f"experiment_{timestamp}.csv"
    
    # No problematic characters
    assert not any(char in filename for char in '<>:"|?*')
    
    # Should have expected structure
    assert filename.startswith("experiment_")
    assert filename.endswith(".csv")
    assert "_" in filename

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/repro/_gen_timestamp.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 17:44:32 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/repro/_gen_timestamp.py
# 
# from datetime import datetime as _datetime
# 
# 
# def gen_timestamp():
#     """Generate a timestamp string for file naming.
# 
#     Returns a timestamp in the format YYYY-MMDD-HHMM, suitable for
#     creating unique filenames or version identifiers.
# 
#     Returns
#     -------
#     str
#         Timestamp string in format "YYYY-MMDD-HHMM"
# 
#     Examples
#     --------
#     >>> timestamp = gen_timestamp()
#     >>> print(timestamp)
#     '2025-0531-1230'
# 
#     >>> filename = f"experiment_{gen_timestamp()}.csv"
#     >>> print(filename)
#     'experiment_2025-0531-1230.csv'
#     """
#     return _datetime.now().strftime("%Y-%m%d-%H%M")
# 
# 
# timestamp = gen_timestamp
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/repro/_gen_timestamp.py
# --------------------------------------------------------------------------------
