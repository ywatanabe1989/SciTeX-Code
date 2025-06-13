#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 15:29:11 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/plt/utils/test__is_valid_axis.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/plt/utils/test__is_valid_axis.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import pytest

# Import the assertion function
from scitex.plt.utils import assert_valid_axis, is_valid_axis


class TestAxisValidation:
    def test_matplotlib_axis_is_valid(self):
        """Test that a standard matplotlib axis is valid."""
        # Create a matplotlib figure and axis
        fig, ax = plt.subplots()
        
        # Test the validation function
        assert is_valid_axis(ax) is True
        
        # Test the assertion function (should not raise)
        assert_valid_axis(ax, "Test message")
        
        # Clean up
        plt.close(fig)
    
    def test_scitex_axis_wrapper_is_valid(self):
        """Test that an SciTeX AxisWrapper is valid."""
        # Create an SciTeX figure and axis
        import scitex.plt as mplt
        fig, ax = mplt.subplots()
        
        # Test the validation function
        assert is_valid_axis(ax) is True
        
        # Test the assertion function (should not raise)
        assert_valid_axis(ax, "Test message")
        
        # Clean up - need to use the underlying matplotlib figure
        plt.close(fig._fig_mpl)
    
    def test_non_axis_is_invalid(self):
        """Test that a non-axis object is correctly identified as invalid."""
        # Create a non-axis object
        not_an_axis = "I am not an axis"
        
        # Test the validation function
        assert is_valid_axis(not_an_axis) is False
        
        # Test the assertion function (should raise AssertionError)
        with pytest.raises(AssertionError):
            assert_valid_axis(not_an_axis, "Test message")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

# EOF