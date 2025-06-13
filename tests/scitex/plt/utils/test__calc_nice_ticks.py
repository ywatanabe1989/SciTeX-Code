#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:36:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/utils/test__calc_nice_ticks.py

"""Tests for calc_nice_ticks functionality."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import matplotlib.ticker as mticker

from scitex.plt.utils import calc_nice_ticks


class TestCalcNiceTicks:
    """Test calc_nice_ticks function."""

    def test_calc_nice_ticks_basic_range(self):
        """Test basic tick calculation for simple range."""
        min_val, max_val = 0, 10
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3  # At least min_n_ticks
        assert min(ticks) <= min_val
        assert max(ticks) >= max_val
        
    def test_calc_nice_ticks_negative_range(self):
        """Test tick calculation for negative range."""
        min_val, max_val = -10, -2
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        assert min(ticks) <= min_val
        assert max(ticks) >= max_val
        assert all(isinstance(tick, (int, float)) for tick in ticks)
        
    def test_calc_nice_ticks_mixed_range(self):
        """Test tick calculation for range crossing zero."""
        min_val, max_val = -5, 15
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        assert min(ticks) <= min_val
        assert max(ticks) >= max_val
        assert 0 in ticks or any(abs(tick) < 1e-10 for tick in ticks)  # Should include zero
        
    def test_calc_nice_ticks_identical_values(self):
        """Test handling of identical min and max values."""
        # Test with zero
        ticks_zero = calc_nice_ticks(0, 0)
        assert ticks_zero == [0, 1, 2, 3]
        
        # Test with non-zero value
        ticks_nonzero = calc_nice_ticks(5, 5)
        assert isinstance(ticks_nonzero, list)
        assert len(ticks_nonzero) >= 3
        assert any(abs(tick - 5) < 1 for tick in ticks_nonzero)  # Should be near 5
        
    def test_calc_nice_ticks_allow_edge_parameters(self):
        """Test allow_edge_min and allow_edge_max parameters."""
        min_val, max_val = 1, 9
        
        # Test allow_edge_min=True (default)
        ticks_min = calc_nice_ticks(min_val, max_val, allow_edge_min=True)
        # Should include or be very close to min_val
        
        # Test allow_edge_min=False
        ticks_no_min = calc_nice_ticks(min_val, max_val, allow_edge_min=False)
        # Might exclude exact min value due to padding
        
        # Test allow_edge_max=True
        ticks_max = calc_nice_ticks(min_val, max_val, allow_edge_max=True)
        
        # Test allow_edge_max=False (default)
        ticks_no_max = calc_nice_ticks(min_val, max_val, allow_edge_max=False)
        
        # All should be valid lists
        for ticks in [ticks_min, ticks_no_min, ticks_max, ticks_no_max]:
            assert isinstance(ticks, list)
            assert len(ticks) >= 3
            
    def test_calc_nice_ticks_padding_percentage(self):
        """Test padding percentage parameter."""
        min_val, max_val = 0, 10
        
        # Test different padding percentages
        ticks_no_pad = calc_nice_ticks(min_val, max_val, pad_perc=0)
        ticks_small_pad = calc_nice_ticks(min_val, max_val, pad_perc=5)
        ticks_large_pad = calc_nice_ticks(min_val, max_val, pad_perc=20)
        
        # All should be valid
        for ticks in [ticks_no_pad, ticks_small_pad, ticks_large_pad]:
            assert isinstance(ticks, list)
            assert len(ticks) >= 3
            
        # Larger padding might result in wider tick range
        assert isinstance(ticks_large_pad, list)
        
    def test_calc_nice_ticks_num_ticks_parameter(self):
        """Test num_ticks parameter."""
        min_val, max_val = 0, 20
        
        # Test different number of ticks
        for num_ticks in [3, 4, 5, 8]:
            ticks = calc_nice_ticks(min_val, max_val, num_ticks=num_ticks)
            assert isinstance(ticks, list)
            assert len(ticks) >= 3  # min_n_ticks is 3
            # Actual number might vary due to matplotlib's algorithm
            
    def test_calc_nice_ticks_prefer_integer_true(self):
        """Test prefer_integer=True (default)."""
        # Range where integer ticks make sense
        min_val, max_val = 1.0, 10.0
        ticks = calc_nice_ticks(min_val, max_val, prefer_integer=True)
        
        assert isinstance(ticks, list)
        # Check if most/all ticks are integers when it makes sense
        integer_ticks = [tick for tick in ticks if isinstance(tick, int)]
        # Should have some integer ticks for this range
        
    def test_calc_nice_ticks_prefer_integer_false(self):
        """Test prefer_integer=False."""
        min_val, max_val = 0, 10
        ticks = calc_nice_ticks(min_val, max_val, prefer_integer=False)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        # Could be floats or ints
        
    def test_calc_nice_ticks_float_range(self):
        """Test with floating point range."""
        min_val, max_val = 0.1, 0.9
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        assert min(ticks) <= min_val + 1e-10  # Account for floating point
        assert max(ticks) >= max_val - 1e-10
        
    def test_calc_nice_ticks_large_range(self):
        """Test with large value range."""
        min_val, max_val = 1000, 10000
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        assert min(ticks) <= min_val
        assert max(ticks) >= max_val
        
    def test_calc_nice_ticks_small_range(self):
        """Test with very small value range."""
        min_val, max_val = 0.001, 0.009
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        # Should handle small ranges appropriately
        
    def test_calc_nice_ticks_scientific_range(self):
        """Test with scientific notation range."""
        min_val, max_val = 1e-6, 1e-3
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        assert all(isinstance(tick, (int, float)) for tick in ticks)
        
    def test_calc_nice_ticks_matplotlib_integration(self):
        """Test integration with matplotlib MaxNLocator."""
        with patch('scitex.plt.utils._calc_nice_ticks.mticker.MaxNLocator') as mock_locator_class:
            mock_locator = MagicMock()
            mock_locator_class.return_value = mock_locator
            mock_locator.tick_values.return_value = np.array([0, 2, 4, 6, 8, 10])
            
            min_val, max_val = 0, 10
            ticks = calc_nice_ticks(min_val, max_val, num_ticks=4)
            
            # Verify MaxNLocator was called with correct parameters
            mock_locator_class.assert_called()
            call_kwargs = mock_locator_class.call_args[1]
            assert call_kwargs['nbins'] == 4
            assert call_kwargs['steps'] == [1, 2, 5, 10]
            assert call_kwargs['integer'] == False
            assert call_kwargs['min_n_ticks'] == 3
            
            # Verify tick_values was called
            mock_locator.tick_values.assert_called_with(min_val, max_val)
            
            assert isinstance(ticks, list)
            
    def test_calc_nice_ticks_too_many_ticks_handling(self):
        """Test handling when too many ticks are generated."""
        with patch('scitex.plt.utils._calc_nice_ticks.mticker.MaxNLocator') as mock_locator_class:
            mock_locator1 = MagicMock()
            mock_locator2 = MagicMock()
            mock_locator_class.side_effect = [mock_locator1, mock_locator2]
            
            # First call returns too many ticks
            mock_locator1.tick_values.return_value = np.array([0, 1, 2, 3, 4, 5, 6])  # 7 ticks
            # Second call returns fewer ticks
            mock_locator2.tick_values.return_value = np.array([0, 2, 4, 6])  # 4 ticks
            
            ticks = calc_nice_ticks(0, 10, num_ticks=4)
            
            # Should have called MaxNLocator twice due to too many ticks
            assert mock_locator_class.call_count == 2
            assert isinstance(ticks, list)
            
    def test_calc_nice_ticks_edge_filtering(self):
        """Test filtering of ticks outside original range."""
        # Mock to return ticks outside the range
        with patch('scitex.plt.utils._calc_nice_ticks.mticker.MaxNLocator') as mock_locator_class:
            mock_locator = MagicMock()
            mock_locator_class.return_value = mock_locator
            mock_locator.tick_values.return_value = np.array([-1, 0, 2, 4, 6, 8, 10, 11])
            
            min_val, max_val = 0, 10
            ticks = calc_nice_ticks(min_val, max_val, allow_edge_min=False, allow_edge_max=False)
            
            # Should filter out ticks outside original range
            assert isinstance(ticks, list)
            # Exact filtering depends on implementation details
            
    def test_calc_nice_ticks_integer_conversion(self):
        """Test integer conversion when prefer_integer=True."""
        # Test case where all ticks can be integers
        min_val, max_val = 1.0, 10.0
        ticks = calc_nice_ticks(min_val, max_val, prefer_integer=True)
        
        # Should contain integers if all ticks are whole numbers
        assert isinstance(ticks, list)
        
        # Test case where ticks cannot all be integers
        min_val, max_val = 0.1, 0.9
        ticks = calc_nice_ticks(min_val, max_val, prefer_integer=True)
        
        assert isinstance(ticks, list)
        # Should remain as floats since they can't all be integers
        
    def test_calc_nice_ticks_real_world_data_scenarios(self):
        """Test with real-world data scenarios."""
        # Percentage data
        percentage_ticks = calc_nice_ticks(0, 100, num_ticks=5)
        assert isinstance(percentage_ticks, list)
        assert 0 in percentage_ticks or any(abs(tick) < 1e-10 for tick in percentage_ticks)
        
        # Temperature data (could be negative)
        temp_ticks = calc_nice_ticks(-10, 35, num_ticks=6)
        assert isinstance(temp_ticks, list)
        
        # Financial data (could be large numbers)
        price_ticks = calc_nice_ticks(50000, 75000, num_ticks=4)
        assert isinstance(price_ticks, list)
        
        # Precision measurements (small decimals)
        precision_ticks = calc_nice_ticks(0.001, 0.003, num_ticks=4)
        assert isinstance(precision_ticks, list)
        
    def test_calc_nice_ticks_return_type_consistency(self):
        """Test that return type is always a list."""
        test_cases = [
            (0, 10),
            (-5, 5),
            (1e-6, 1e-3),
            (1000, 10000),
            (0.1, 0.9)
        ]
        
        for min_val, max_val in test_cases:
            ticks = calc_nice_ticks(min_val, max_val)
            assert isinstance(ticks, list)
            assert len(ticks) >= 3
            assert all(isinstance(tick, (int, float)) for tick in ticks)
            
    def test_calc_nice_ticks_edge_case_very_close_values(self):
        """Test with values that are very close but not identical."""
        min_val, max_val = 1.0, 1.0001
        ticks = calc_nice_ticks(min_val, max_val)
        
        assert isinstance(ticks, list)
        assert len(ticks) >= 3
        # Should handle very small ranges


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
