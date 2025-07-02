#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:29:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__gen_timestamp_comprehensive.py

"""Comprehensive tests for timestamp generation functionality."""

import os
import pytest
import re
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class TestGenTimestampBasic:
    """Test basic timestamp generation functionality."""
    
    def test_basic_generation(self):
        """Test basic timestamp generation."""
        from scitex.repro import gen_timestamp
        
        timestamp = gen_timestamp()
        
        assert isinstance(timestamp, str)
        assert len(timestamp) == 14  # YYYY-MMDD-HHMM
        assert timestamp.count('-') == 2
    
    def test_format_pattern(self):
        """Test timestamp follows expected pattern."""
        from scitex.repro import gen_timestamp
        
        timestamp = gen_timestamp()
        
        # Strict pattern matching
        pattern = r'^(\d{4})-(\d{2})(\d{2})-(\d{2})(\d{2})$'
        match = re.match(pattern, timestamp)
        
        assert match is not None
        
        # Extract and validate components
        year, month, day, hour, minute = match.groups()
        
        assert 2000 <= int(year) <= 2100
        assert 1 <= int(month) <= 12
        assert 1 <= int(day) <= 31
        assert 0 <= int(hour) <= 23
        assert 0 <= int(minute) <= 59
    
    def test_timestamp_alias(self):
        """Test timestamp function alias."""
        from scitex.repro import gen_timestamp, timestamp
        
        # Should be same function
        assert timestamp is gen_timestamp
        
        # Should produce same format
        ts1 = gen_timestamp()
        ts2 = timestamp()
        
        assert len(ts1) == len(ts2) == 14
        assert ts1.count('-') == ts2.count('-') == 2
    
    def test_multiple_calls(self):
        """Test multiple calls produce valid timestamps."""
        from scitex.repro import gen_timestamp
        
        timestamps = [gen_timestamp() for _ in range(10)]
        
        # All should be valid
        pattern = r'^\d{4}-\d{4}-\d{4}$'
        for ts in timestamps:
            assert re.match(pattern, ts)
        
        # All should have same format
        assert all(len(ts) == 14 for ts in timestamps)


class TestGenTimestampComponents:
    """Test individual timestamp components."""
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_year_component(self, mock_datetime):
        """Test year component formatting."""
        from scitex.repro import gen_timestamp
        
        # Test various years
        years = [2000, 2020, 2025, 2099, 2100]
        
        for year in years:
            mock_datetime.now.return_value = datetime(year, 6, 15, 12, 30)
            timestamp = gen_timestamp()
            assert timestamp.startswith(str(year))
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_month_component(self, mock_datetime):
        """Test month component with proper padding."""
        from scitex.repro import gen_timestamp
        
        # Test all months
        for month in range(1, 13):
            mock_datetime.now.return_value = datetime(2025, month, 15, 12, 30)
            timestamp = gen_timestamp()
            
            month_str = timestamp[5:7]
            assert month_str == f"{month:02d}"
            assert len(month_str) == 2
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_day_component(self, mock_datetime):
        """Test day component with proper padding."""
        from scitex.repro import gen_timestamp
        
        # Test various days
        days = [1, 9, 10, 15, 28, 29, 30, 31]
        
        for day in days:
            mock_datetime.now.return_value = datetime(2025, 1, day, 12, 30)
            timestamp = gen_timestamp()
            
            day_str = timestamp[7:9]
            assert day_str == f"{day:02d}"
            assert len(day_str) == 2
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_hour_component(self, mock_datetime):
        """Test hour component (0-23) with proper padding."""
        from scitex.repro import gen_timestamp
        
        # Test all hours
        for hour in range(24):
            mock_datetime.now.return_value = datetime(2025, 6, 15, hour, 30)
            timestamp = gen_timestamp()
            
            hour_str = timestamp[10:12]
            assert hour_str == f"{hour:02d}"
            assert len(hour_str) == 2
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_minute_component(self, mock_datetime):
        """Test minute component with proper padding."""
        from scitex.repro import gen_timestamp
        
        # Test various minutes
        minutes = [0, 1, 9, 10, 30, 59]
        
        for minute in minutes:
            mock_datetime.now.return_value = datetime(2025, 6, 15, 12, minute)
            timestamp = gen_timestamp()
            
            minute_str = timestamp[12:14]
            assert minute_str == f"{minute:02d}"
            assert len(minute_str) == 2


class TestGenTimestampEdgeCases:
    """Test edge cases and special dates."""
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_midnight(self, mock_datetime):
        """Test midnight timestamp."""
        from scitex.repro import gen_timestamp
        
        mock_datetime.now.return_value = datetime(2025, 6, 15, 0, 0, 0)
        timestamp = gen_timestamp()
        
        assert timestamp == "2025-0615-0000"
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_last_minute_of_day(self, mock_datetime):
        """Test 23:59 timestamp."""
        from scitex.repro import gen_timestamp
        
        mock_datetime.now.return_value = datetime(2025, 6, 15, 23, 59, 59)
        timestamp = gen_timestamp()
        
        assert timestamp == "2025-0615-2359"
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_new_year(self, mock_datetime):
        """Test New Year timestamp."""
        from scitex.repro import gen_timestamp
        
        # New Year midnight
        mock_datetime.now.return_value = datetime(2025, 1, 1, 0, 0, 0)
        timestamp = gen_timestamp()
        assert timestamp == "2025-0101-0000"
        
        # New Year's Eve last minute
        mock_datetime.now.return_value = datetime(2024, 12, 31, 23, 59, 59)
        timestamp = gen_timestamp()
        assert timestamp == "2024-1231-2359"
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_leap_year_date(self, mock_datetime):
        """Test leap year date (Feb 29)."""
        from scitex.repro import gen_timestamp
        
        # 2024 is a leap year
        mock_datetime.now.return_value = datetime(2024, 2, 29, 12, 30, 0)
        timestamp = gen_timestamp()
        assert timestamp == "2024-0229-1230"
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_month_boundaries(self, mock_datetime):
        """Test first and last days of months."""
        from scitex.repro import gen_timestamp
        
        test_dates = [
            (2025, 1, 31, "2025-0131"),  # January 31
            (2025, 2, 1, "2025-0201"),   # February 1
            (2025, 2, 28, "2025-0228"),  # February 28 (non-leap)
            (2025, 3, 1, "2025-0301"),   # March 1
            (2025, 4, 30, "2025-0430"),  # April 30
            (2025, 5, 1, "2025-0501"),   # May 1
        ]
        
        for year, month, day, expected_prefix in test_dates:
            mock_datetime.now.return_value = datetime(year, month, day, 15, 45)
            timestamp = gen_timestamp()
            assert timestamp.startswith(expected_prefix)
            assert timestamp.endswith("-1545")


class TestGenTimestampUniqueness:
    """Test timestamp uniqueness and ordering."""
    
    def test_timestamps_within_same_minute(self):
        """Test multiple timestamps within same minute."""
        from scitex.repro import gen_timestamp
        
        # Generate multiple timestamps quickly
        timestamps = []
        start_time = time.time()
        
        while time.time() - start_time < 0.5:  # Within 0.5 seconds
            timestamps.append(gen_timestamp())
        
        # All should be identical (same minute)
        if timestamps:
            first = timestamps[0]
            assert all(ts == first for ts in timestamps)
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_chronological_ordering(self, mock_datetime):
        """Test timestamps maintain chronological order."""
        from scitex.repro import gen_timestamp
        
        times = [
            datetime(2025, 1, 1, 0, 0),
            datetime(2025, 1, 1, 0, 1),
            datetime(2025, 1, 1, 1, 0),
            datetime(2025, 1, 2, 0, 0),
            datetime(2025, 2, 1, 0, 0),
            datetime(2026, 1, 1, 0, 0),
        ]
        
        timestamps = []
        for t in times:
            mock_datetime.now.return_value = t
            timestamps.append(gen_timestamp())
        
        # Should be lexicographically sorted
        assert timestamps == sorted(timestamps)
    
    def test_timestamp_precision_loss(self):
        """Test that seconds are not included (precision loss)."""
        from scitex.repro import gen_timestamp
        
        # Generate timestamp
        ts1 = gen_timestamp()
        
        # Wait less than a minute
        time.sleep(0.1)
        
        # Generate another
        ts2 = gen_timestamp()
        
        # Should be the same (same minute)
        assert ts1 == ts2


class TestGenTimestampConcurrency:
    """Test concurrent timestamp generation."""
    
    def test_thread_safety(self):
        """Test thread-safe timestamp generation."""
        from scitex.repro import gen_timestamp
        
        results = []
        lock = threading.Lock()
        
        def generate_timestamp():
            ts = gen_timestamp()
            with lock:
                results.append(ts)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=generate_timestamp)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # All should be valid timestamps
        pattern = r'^\d{4}-\d{4}-\d{4}$'
        assert all(re.match(pattern, ts) for ts in results)
        assert len(results) == 10
    
    def test_multiprocess_generation(self):
        """Test timestamp generation across processes."""
        from scitex.repro import gen_timestamp
        
        def generate_in_process():
            return gen_timestamp()
        
        # Use process pool
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_in_process) for _ in range(8)]
            results = [f.result() for f in futures]
        
        # All should be valid
        pattern = r'^\d{4}-\d{4}-\d{4}$'
        assert all(re.match(pattern, ts) for ts in results)
        assert len(results) == 8


class TestGenTimestampUsagePatterns:
    """Test common usage patterns."""
    
    def test_filename_generation(self):
        """Test using timestamp in filenames."""
        from scitex.repro import gen_timestamp
        
        timestamp = gen_timestamp()
        
        # Common filename patterns
        filenames = [
            f"backup_{timestamp}.tar.gz",
            f"log_{timestamp}.txt",
            f"data_{timestamp}.csv",
            f"{timestamp}_experiment.json",
            f"model_checkpoint_{timestamp}.pth"
        ]
        
        # All should be valid filenames
        for filename in filenames:
            # No problematic characters
            assert all(c not in filename for c in '<>:"|?*')
            # Contains timestamp
            assert timestamp in filename
    
    def test_directory_naming(self):
        """Test using timestamp for directory names."""
        from scitex.repro import gen_timestamp
        
        timestamp = gen_timestamp()
        
        # Common directory patterns
        dirnames = [
            f"run_{timestamp}",
            f"backup/{timestamp}",
            f"experiments/{timestamp}/results",
            f"{timestamp}_output"
        ]
        
        # All should be valid paths
        for dirname in dirnames:
            # No problematic characters for paths
            assert all(c not in dirname for c in '<>"|?*')
            assert timestamp in dirname
    
    def test_sorting_compatibility(self):
        """Test that timestamps sort correctly."""
        from scitex.repro import gen_timestamp
        
        # Mock different times
        with patch('scitex.str._gen_timestamp._datetime') as mock_dt:
            timestamps = []
            
            # Generate timestamps for different times
            times = [
                datetime(2025, 1, 1, 10, 30),
                datetime(2025, 1, 1, 10, 31),
                datetime(2025, 1, 2, 9, 0),
                datetime(2025, 2, 1, 8, 0),
                datetime(2026, 1, 1, 7, 0),
            ]
            
            for t in times:
                mock_dt.now.return_value = t
                timestamps.append(gen_timestamp())
            
            # Lexicographic sort should match chronological order
            assert timestamps == sorted(timestamps)
    
    def test_database_compatibility(self):
        """Test timestamp format for database storage."""
        from scitex.repro import gen_timestamp
        
        timestamp = gen_timestamp()
        
        # Should be fixed length (good for VARCHAR)
        assert len(timestamp) == 14
        
        # Should contain only alphanumeric and dash
        assert all(c.isalnum() or c == '-' for c in timestamp)
        
        # Should be ASCII only
        assert timestamp.isascii()


class TestGenTimestampPerformance:
    """Test performance characteristics."""
    
    def test_generation_speed(self):
        """Test timestamp generation is fast."""
        from scitex.repro import gen_timestamp
        import time
        
        start = time.time()
        for _ in range(1000):
            gen_timestamp()
        duration = time.time() - start
        
        # Should be very fast (less than 0.1 seconds for 1000 generations)
        assert duration < 0.1
    
    def test_memory_efficiency(self):
        """Test memory usage is reasonable."""
        from scitex.repro import gen_timestamp
        import sys
        
        # Generate many timestamps
        timestamps = [gen_timestamp() for _ in range(1000)]
        
        # Each timestamp should be small
        for ts in timestamps:
            assert sys.getsizeof(ts) < 100  # bytes
        
        # All should have same size
        sizes = [sys.getsizeof(ts) for ts in timestamps]
        assert len(set(sizes)) == 1


class TestGenTimestampInternational:
    """Test international datetime handling."""
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_timezone_agnostic(self, mock_datetime):
        """Test that timestamp generation is timezone agnostic."""
        from scitex.repro import gen_timestamp
        
        # Same time in different timezones would give same timestamp
        # (since we use datetime.now() which is local time)
        base_time = datetime(2025, 6, 15, 12, 30)
        mock_datetime.now.return_value = base_time
        
        timestamp = gen_timestamp()
        assert timestamp == "2025-0615-1230"
    
    def test_locale_independence(self):
        """Test that timestamp format is locale-independent."""
        from scitex.repro import gen_timestamp
        
        # Timestamp should always use same format regardless of locale
        timestamp = gen_timestamp()
        
        # Always uses numeric format, not locale-specific
        assert '-' in timestamp
        assert not any(c.isalpha() for c in timestamp if c != '-')


class TestGenTimestampComparison:
    """Test timestamp comparison operations."""
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_timestamp_comparison(self, mock_datetime):
        """Test comparing timestamps."""
        from scitex.repro import gen_timestamp
        
        # Earlier time
        mock_datetime.now.return_value = datetime(2025, 6, 15, 10, 30)
        ts1 = gen_timestamp()
        
        # Later time
        mock_datetime.now.return_value = datetime(2025, 6, 15, 11, 30)
        ts2 = gen_timestamp()
        
        # String comparison should work correctly
        assert ts1 < ts2
        assert ts2 > ts1
        assert ts1 != ts2
    
    @patch('scitex.repro._gen_timestamp._datetime')
    def test_timestamp_equality(self, mock_datetime):
        """Test timestamp equality."""
        from scitex.repro import gen_timestamp
        
        # Same time
        mock_datetime.now.return_value = datetime(2025, 6, 15, 10, 30)
        ts1 = gen_timestamp()
        ts2 = gen_timestamp()
        
        assert ts1 == ts2
        assert not (ts1 < ts2)
        assert not (ts1 > ts2)


class TestGenTimestampDocumentation:
    """Test that function behaves as documented."""
    
    def test_format_as_documented(self):
        """Test format matches documentation."""
        from scitex.repro import gen_timestamp
        
        timestamp = gen_timestamp()
        
        # Should be "YYYY-MMDD-HHMM" format
        parts = timestamp.split('-')
        assert len(parts) == 3
        
        year_part = parts[0]
        monthday_part = parts[1]
        hourmin_part = parts[2]
        
        assert len(year_part) == 4
        assert len(monthday_part) == 4
        assert len(hourmin_part) == 4
    
    def test_example_usage(self):
        """Test documented example usage."""
        from scitex.repro import gen_timestamp
        
        # Example: Creating timestamped filename
        timestamp = gen_timestamp()
        filename = f"experiment_{timestamp}.log"
        
        # Should create valid filename
        assert filename.startswith("experiment_")
        assert filename.endswith(".log")
        assert len(filename) == len("experiment_") + 14 + len(".log")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])