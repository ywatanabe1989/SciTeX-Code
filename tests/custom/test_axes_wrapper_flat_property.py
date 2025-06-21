#!/usr/bin/env python3
"""Test the flat property of AxesWrapper"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from scitex.plt._subplots._AxesWrapper import AxesWrapper
from scitex.plt._subplots._FigWrapper import FigWrapper


class TestAxesWrapperFlat:
    """Test suite for AxesWrapper.flat property"""
    
    def test_flat_returns_iterator(self):
        """Test that axes.flat returns a proper iterator like numpy arrays"""
        fig, axes_array = plt.subplots(2, 3)
        fig_wrapped = FigWrapper(fig)
        axes = AxesWrapper(fig_wrapped, axes_array)
        
        # Check that flat returns a numpy flatiter
        assert hasattr(axes, 'flat')
        flat_result = axes.flat
        assert type(flat_result).__name__ == 'flatiter'
        
        # Verify we can iterate over it
        flat_list = list(flat_result)
        assert len(flat_list) == 6  # 2x3 = 6 axes
        
        # Verify all items are matplotlib axes
        for ax in flat_list:
            assert hasattr(ax, 'plot')
            assert hasattr(ax, 'set_xlabel')
    
    def test_flat_matches_numpy_behavior(self):
        """Test that axes.flat behaves like numpy array flat"""
        fig, axes_array = plt.subplots(3, 4)
        fig_wrapped = FigWrapper(fig)
        axes = AxesWrapper(fig_wrapped, axes_array)
        
        # Compare with numpy behavior
        axes_flat = list(axes.flat)
        numpy_flat = list(axes_array.flat)
        
        assert len(axes_flat) == len(numpy_flat)
        assert len(axes_flat) == 12  # 3x4 = 12
        
        # Verify order is the same (row-major)
        for i, (ax1, ax2) in enumerate(zip(axes_flat, numpy_flat)):
            assert ax1 is ax2
    
    def test_flat_not_list_of_lists(self):
        """Regression test: ensure flat doesn't return list of lists"""
        fig, axes_array = plt.subplots(2, 2)
        fig_wrapped = FigWrapper(fig)
        axes = AxesWrapper(fig_wrapped, axes_array)
        
        flat_result = axes.flat
        flat_list = list(flat_result)
        
        # Should NOT be a list of lists
        assert not isinstance(flat_list[0], list)
        # Should be matplotlib axes
        assert hasattr(flat_list[0], 'plot')
        
    def test_flat_with_single_axis(self):
        """Test flat property with a single axis"""
        fig, ax = plt.subplots()
        # Need to make it an array to match expected structure
        axes_array = np.array([[ax]])
        fig_wrapped = FigWrapper(fig) 
        axes = AxesWrapper(fig_wrapped, axes_array)
        
        flat_list = list(axes.flat)
        assert len(flat_list) == 1
        assert flat_list[0] is ax


if __name__ == "__main__":
    pytest.main([__file__, "-v"])