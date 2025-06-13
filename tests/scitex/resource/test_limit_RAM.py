#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:06:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/resource/test_limit_RAM.py

"""Tests for RAM limiting functionality."""

import pytest
import os
import resource
from unittest.mock import patch, mock_open, MagicMock


class TestLimitRAM:
    """Test cases for scitex.resource.limit_ram module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Store original resource limits to restore later
        self.original_limits = None
        try:
            self.original_limits = resource.getrlimit(resource.RLIMIT_AS)
        except (OSError, resource.error):
            # Some systems might not support this
            pass

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Restore original limits if possible
        if self.original_limits:
            try:
                resource.setrlimit(resource.RLIMIT_AS, self.original_limits)
            except (OSError, resource.error):
                # Ignore errors when restoring
                pass

    def test_limit_ram_imports(self):
        """Test that limit_ram functions can be imported successfully."""
        from scitex.resource.limit_ram import limit_ram, get_ram
        assert callable(limit_ram)
        assert callable(get_ram)

    def test_backward_compatibility_imports(self):
        """Test that deprecated uppercase functions are available."""
        from scitex.resource.limit_ram import limit_RAM, get_RAM
        assert callable(limit_RAM)
        assert callable(get_RAM)

    @patch("builtins.open", new_callable=mock_open, read_data="""MemTotal:        8000000 kB
MemFree:         2000000 kB
MemAvailable:    4000000 kB
Buffers:          500000 kB
Cached:          1000000 kB
SwapCached:            0 kB
Active:          3000000 kB
Inactive:        1000000 kB""")
    def test_get_ram_basic_functionality(self, mock_file):
        """Test basic get_ram functionality."""
        from scitex.resource.limit_ram import get_ram
        
        ram = get_ram()
        
        # Should sum MemFree + Buffers + Cached = 2000000 + 500000 + 1000000 = 3500000
        assert ram == 3500000
        mock_file.assert_called_once_with("/proc/meminfo", "r")

    @patch("builtins.open", new_callable=mock_open, read_data="""MemTotal:        4000000 kB
MemFree:         1000000 kB
Buffers:          200000 kB
Cached:           300000 kB""")
    def test_get_ram_smaller_values(self, mock_file):
        """Test get_ram with smaller memory values."""
        from scitex.resource.limit_ram import get_ram
        
        ram = get_ram()
        
        # Should sum MemFree + Buffers + Cached = 1000000 + 200000 + 300000 = 1500000
        assert ram == 1500000

    @patch("builtins.open", new_callable=mock_open, read_data="""MemTotal:        8000000 kB
MemAvailable:    4000000 kB
Active:          3000000 kB
Inactive:        1000000 kB""")
    def test_get_ram_missing_fields(self, mock_file):
        """Test get_ram when some expected fields are missing."""
        from scitex.resource.limit_ram import get_ram
        
        ram = get_ram()
        
        # Should return 0 since MemFree, Buffers, and Cached are missing
        assert ram == 0

    @patch("builtins.open", new_callable=mock_open, read_data="""MemTotal:        8000000 kB
MemFree:         0 kB
Buffers:         0 kB
Cached:          0 kB""")
    def test_get_ram_zero_values(self, mock_file):
        """Test get_ram with zero values."""
        from scitex.resource.limit_ram import get_ram
        
        ram = get_ram()
        
        # Should return 0 when all relevant fields are 0
        assert ram == 0

    @patch("builtins.open", side_effect=FileNotFoundError("No such file"))
    def test_get_ram_file_not_found(self, mock_file):
        """Test get_ram when /proc/meminfo doesn't exist."""
        from scitex.resource.limit_ram import get_ram
        
        with pytest.raises(FileNotFoundError):
            get_ram()

    @patch("builtins.open", new_callable=mock_open, read_data="invalid content")
    def test_get_ram_invalid_format(self, mock_file):
        """Test get_ram with invalid /proc/meminfo format."""
        from scitex.resource.limit_ram import get_ram
        
        # Should handle malformed content gracefully
        ram = get_ram()
        assert ram == 0  # No valid fields found

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    @patch('scitex.gen.fmt_size')
    @patch('builtins.print')
    def test_limit_ram_basic_functionality(self, mock_print, mock_fmt_size, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test basic limit_ram functionality."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup
        mock_get_ram.return_value = 4000000  # 4GB in KB
        mock_getrlimit.return_value = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        mock_fmt_size.return_value = "1.6 GB"
        
        # Call function
        limit_ram(0.4)  # Limit to 40% of available RAM
        
        # Verify get_ram was called
        assert mock_get_ram.call_count >= 1
        
        # Verify getrlimit was called
        mock_getrlimit.assert_called_once_with(resource.RLIMIT_AS)
        
        # Verify setrlimit was called with correct calculation
        # max_val should be min(0.4 * 4000000 * 1024, 4000000 * 1024) = 0.4 * 4000000 * 1024
        expected_max_val = int(0.4 * 4000000 * 1024)
        mock_setrlimit.assert_called_once_with(resource.RLIMIT_AS, (expected_max_val, resource.RLIM_INFINITY))
        
        # Verify print was called
        mock_print.assert_called_once()
        mock_fmt_size.assert_called_once_with(expected_max_val)

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    @patch('scitex.gen.fmt_size')
    @patch('builtins.print')
    def test_limit_ram_factor_greater_than_one(self, mock_print, mock_fmt_size, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test limit_ram when factor is greater than 1.0."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup
        mock_get_ram.return_value = 2000000  # 2GB in KB
        mock_getrlimit.return_value = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        mock_fmt_size.return_value = "2.0 GB"
        
        # Call function with factor > 1
        limit_ram(1.5)  # Try to limit to 150% of available RAM
        
        # Should use min() so actual limit should be get_ram() * 1024
        expected_max_val = 2000000 * 1024
        mock_setrlimit.assert_called_once_with(resource.RLIMIT_AS, (expected_max_val, resource.RLIM_INFINITY))

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    @patch('scitex.gen.fmt_size')
    @patch('builtins.print')
    def test_limit_ram_zero_factor(self, mock_print, mock_fmt_size, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test limit_ram with zero factor."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup
        mock_get_ram.return_value = 4000000
        mock_getrlimit.return_value = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        mock_fmt_size.return_value = "0 B"
        
        # Call function with factor = 0
        limit_ram(0.0)
        
        # Should set limit to 0
        mock_setrlimit.assert_called_once_with(resource.RLIMIT_AS, (0, resource.RLIM_INFINITY))

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    def test_limit_ram_with_existing_hard_limit(self, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test limit_ram when there's an existing hard limit."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup with existing hard limit
        existing_hard_limit = 8000000 * 1024  # 8GB
        mock_get_ram.return_value = 4000000
        mock_getrlimit.return_value = (1000000 * 1024, existing_hard_limit)
        
        # Call function
        limit_ram(0.5)
        
        # Should preserve the existing hard limit
        expected_max_val = int(0.5 * 4000000 * 1024)
        mock_setrlimit.assert_called_once_with(resource.RLIMIT_AS, (expected_max_val, existing_hard_limit))

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    def test_limit_ram_resource_error_handling(self, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test limit_ram when resource operations fail."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup
        mock_get_ram.return_value = 4000000
        mock_getrlimit.side_effect = OSError("Permission denied")
        
        # Should raise the OSError
        with pytest.raises(OSError):
            limit_ram(0.5)

    def test_backward_compatibility_limit_RAM(self):
        """Test that limit_RAM is the same as limit_ram."""
        from scitex.resource.limit_ram import limit_ram, limit_RAM
        
        # Should be the same function
        assert limit_RAM is limit_ram

    def test_backward_compatibility_get_RAM(self):
        """Test that get_RAM is the same as get_ram."""
        from scitex.resource.limit_ram import get_ram, get_RAM
        
        # Should be the same function
        assert get_RAM is get_ram

    @patch("builtins.open", new_callable=mock_open, read_data="""MemTotal:        16000000 kB
MemFree:         8000000 kB
MemAvailable:    12000000 kB
Buffers:         1000000 kB
Cached:          2000000 kB
SwapCached:            0 kB""")
    def test_get_ram_realistic_values(self, mock_file):
        """Test get_ram with realistic memory values."""
        from scitex.resource.limit_ram import get_ram
        
        ram = get_ram()
        
        # Should sum MemFree + Buffers + Cached = 8000000 + 1000000 + 2000000 = 11000000
        assert ram == 11000000

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    @patch('scitex.gen.fmt_size')
    @patch('builtins.print')
    def test_limit_ram_negative_factor(self, mock_print, mock_fmt_size, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test limit_ram with negative factor."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup
        mock_get_ram.return_value = 4000000
        mock_getrlimit.return_value = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        mock_fmt_size.return_value = "0 B"
        
        # Call function with negative factor
        limit_ram(-0.1)
        
        # The min() function should result in 0 since negative * positive = negative
        # and min(negative, positive) = negative, but we can't set negative limits
        # The actual behavior depends on implementation details
        mock_setrlimit.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data="""MemTotal:        8000000 kB
MemFree:         abc kB
Buffers:         500000 kB
Cached:          def kB""")
    def test_get_ram_invalid_numbers(self, mock_file):
        """Test get_ram with non-numeric values in /proc/meminfo."""
        from scitex.resource.limit_ram import get_ram
        
        # Should handle ValueError when converting non-numeric strings
        with pytest.raises(ValueError):
            get_ram()

    @patch('scitex.resource.limit_ram.get_ram')
    @patch('resource.getrlimit')
    @patch('resource.setrlimit')
    @patch('scitex.gen.fmt_size')
    @patch('builtins.print')
    def test_limit_ram_prints_formatted_size(self, mock_print, mock_fmt_size, mock_setrlimit, mock_getrlimit, mock_get_ram):
        """Test that limit_ram prints the formatted size correctly."""
        from scitex.resource.limit_ram import limit_ram
        
        # Mock setup
        mock_get_ram.return_value = 4000000
        mock_getrlimit.return_value = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        mock_fmt_size.return_value = "1.6 GB"
        
        # Call function
        limit_ram(0.4)
        
        # Verify that fmt_size was called with the calculated max_val
        expected_max_val = int(0.4 * 4000000 * 1024)
        mock_fmt_size.assert_called_once_with(expected_max_val)
        
        # Verify that print was called with the formatted message
        expected_message = f"\nFree RAM was limited to 1.6 GB"
        mock_print.assert_called_once_with(expected_message)

    def test_limit_ram_integration_with_scitex_gen(self):
        """Test that limit_ram correctly integrates with scitex.gen.fmt_size."""
        # This is more of an integration test - we're testing that the import works
        from scitex.resource.limit_ram import limit_ram
        import scitex.gen
        
        # Verify that scitex.gen.fmt_size is accessible
        assert hasattr(scitex.gen, 'fmt_size')
        assert callable(scitex.gen.fmt_size)


if __name__ == "__main__":
    pytest.main([__file__])
