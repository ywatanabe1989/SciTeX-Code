#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 09:30:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__readable_bytes_enhanced.py

"""Comprehensive tests for readable bytes formatting functionality."""

import pytest
from unittest.mock import patch


class TestReadableBytesEnhanced:
    """Enhanced test suite for readable_bytes function."""

    def test_zero_bytes(self):
        """Test zero byte formatting."""
        from scitex.str._readable_bytes import readable_bytes
        
        result = readable_bytes(0)
        assert result == "0.0 B"

    def test_small_bytes(self):
        """Test byte values under 1024."""
        from scitex.str._readable_bytes import readable_bytes
        
        assert readable_bytes(1) == "1.0 B"
        assert readable_bytes(512) == "512.0 B"
        assert readable_bytes(1023) == "1023.0 B"

    def test_kilobytes(self):
        """Test kilobyte formatting (KiB)."""
        from scitex.str._readable_bytes import readable_bytes
        
        assert readable_bytes(1024) == "1.0 KiB"
        assert readable_bytes(1536) == "1.5 KiB"
        assert readable_bytes(2048) == "2.0 KiB"
        assert readable_bytes(1024 * 10) == "10.0 KiB"

    def test_megabytes(self):
        """Test megabyte formatting (MiB)."""
        from scitex.str._readable_bytes import readable_bytes
        
        mb = 1024 * 1024
        assert readable_bytes(mb) == "1.0 MiB"
        assert readable_bytes(int(mb * 2.5)) == "2.5 MiB"
        assert readable_bytes(mb * 10) == "10.0 MiB"

    def test_gigabytes(self):
        """Test gigabyte formatting (GiB)."""
        from scitex.str._readable_bytes import readable_bytes
        
        gb = 1024 ** 3
        assert readable_bytes(gb) == "1.0 GiB"
        assert readable_bytes(int(gb * 1.5)) == "1.5 GiB"
        assert readable_bytes(gb * 4) == "4.0 GiB"

    def test_terabytes(self):
        """Test terabyte formatting (TiB)."""
        from scitex.str._readable_bytes import readable_bytes
        
        tb = 1024 ** 4
        assert readable_bytes(tb) == "1.0 TiB"
        assert readable_bytes(int(tb * 2.2)) == "2.2 TiB"

    def test_petabytes(self):
        """Test petabyte formatting (PiB)."""
        from scitex.str._readable_bytes import readable_bytes
        
        pb = 1024 ** 5
        assert readable_bytes(pb) == "1.0 PiB"
        assert readable_bytes(int(pb * 3.7)) == "3.7 PiB"

    def test_exabytes(self):
        """Test exabyte formatting (EiB)."""
        from scitex.str._readable_bytes import readable_bytes
        
        eb = 1024 ** 6
        result = readable_bytes(eb)
        assert "1.0 EiB" in result

    def test_very_large_values(self):
        """Test extremely large values."""
        from scitex.str._readable_bytes import readable_bytes
        
        zb = 1024 ** 7
        result = readable_bytes(zb)
        assert "1.0 ZiB" in result
        
        yb = 1024 ** 8
        result = readable_bytes(yb)
        assert "1.0 YiB" in result

    def test_negative_values(self):
        """Test negative byte values."""
        from scitex.str._readable_bytes import readable_bytes
        
        assert readable_bytes(-1024) == "-1.0 KiB"
        assert readable_bytes(-1024 * 1024) == "-1.0 MiB"
        assert readable_bytes(-512) == "-512.0 B"

    def test_float_values(self):
        """Test floating point byte values."""
        from scitex.str._readable_bytes import readable_bytes
        
        assert readable_bytes(1024.5) == "1.0 KiB"  # Truncated to 1.0 after division
        assert readable_bytes(1536.7) == "1.5 KiB"

    def test_custom_suffix(self):
        """Test custom suffix parameter."""
        from scitex.str._readable_bytes import readable_bytes
        
        assert readable_bytes(1024, suffix="ytes") == "1.0 Kiytes"
        assert readable_bytes(1024 * 1024, suffix="it") == "1.0 Miit"
        assert readable_bytes(512, suffix="") == "512.0 "

    def test_precision_formatting(self):
        """Test decimal precision."""
        from scitex.str._readable_bytes import readable_bytes
        
        # Check that we get exactly 1 decimal place
        result = readable_bytes(1536)  # 1.5 KiB
        assert ".5" in result
        
        result = readable_bytes(1024 * 1024 * 2.7)  # 2.7 MiB
        assert "2.7" in result

    def test_boundary_values(self):
        """Test values at unit boundaries."""
        from scitex.str._readable_bytes import readable_bytes
        
        # Just under next unit
        assert readable_bytes(1023) == "1023.0 B"
        assert readable_bytes(1024 * 1023) == "1023.0 KiB"
        
        # Exactly at unit boundary
        assert readable_bytes(1024) == "1.0 KiB"
        assert readable_bytes(1024 ** 2) == "1.0 MiB"

    def test_edge_case_very_small(self):
        """Test very small fractional values."""
        from scitex.str._readable_bytes import readable_bytes
        
        result = readable_bytes(0.1)
        assert "0.1 B" in result
        
        result = readable_bytes(0.99)
        assert "0.9 B" in result or "1.0 B" in result

    def test_consistency_across_scales(self):
        """Test that scaling is consistent."""
        from scitex.str._readable_bytes import readable_bytes
        
        kb = 1024
        mb = kb * 1024
        gb = mb * 1024
        
        assert "1.0 KiB" in readable_bytes(kb)
        assert "1.0 MiB" in readable_bytes(mb)
        assert "1.0 GiB" in readable_bytes(gb)

    def test_format_string_consistency(self):
        """Test that format string produces consistent output."""
        from scitex.str._readable_bytes import readable_bytes
        
        # All results should have the pattern: number space unit
        test_values = [0, 1, 1024, 1024**2, 1024**3]
        for value in test_values:
            result = readable_bytes(value)
            parts = result.split()
            assert len(parts) == 2  # number and unit
            assert parts[1].endswith("B")  # unit ends with B

    def test_large_numbers_scientific_fallback(self):
        """Test extremely large numbers beyond yottabytes."""
        from scitex.str._readable_bytes import readable_bytes
        
        # Value larger than yottabyte scale
        massive_value = 1024 ** 10
        result = readable_bytes(massive_value)
        # Should still work and contain YiB
        assert "YiB" in result

    def test_zero_division_safety(self):
        """Test that function handles edge cases safely."""
        from scitex.str._readable_bytes import readable_bytes
        
        # These should not raise exceptions
        try:
            readable_bytes(float('inf'))
            readable_bytes(float('-inf'))
        except (ValueError, OverflowError):
            # Acceptable to fail on infinity
            pass

    def test_type_compatibility(self):
        """Test different numeric types."""
        from scitex.str._readable_bytes import readable_bytes
        
        # int
        assert "1.0 KiB" in readable_bytes(1024)
        
        # float
        assert "1.0 KiB" in readable_bytes(1024.0)
        
        # Should handle various numeric inputs
        import numpy as np
        assert "1.0 KiB" in readable_bytes(np.int64(1024))


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])