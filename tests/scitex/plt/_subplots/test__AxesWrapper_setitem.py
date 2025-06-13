#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 06:20:00 (ywatanabe)"
# File: ./tests/scitex/plt/_subplots/test__AxesWrapper_setitem.py

import pytest
import numpy as np
import matplotlib.pyplot as plt


def test_axes_wrapper_item_assignment():
    """Test that AxesWrapper supports item assignment (fixes TypeError: 'AxesWrapper' object does not support item assignment)."""
    import scitex
    
    # Create subplots using scitex
    fig, axes = scitex.plt.subplots(3, 2, figsize=(8, 6))
    
    # Verify initial setup
    assert hasattr(axes, '__setitem__'), "AxesWrapper should have __setitem__ method"
    original_ax = axes[2, 1]
    
    # Test the critical item assignment that was failing
    new_ax = plt.subplot(3, 2, 6, projection="polar")
    axes[2, 1] = new_ax
    
    # Verify assignment worked
    assert axes[2, 1] is new_ax, "Item assignment should replace the axis object"
    assert axes[2, 1] != original_ax, "New axis should be different from original"
    
    # Verify we can use the new polar axis
    theta = np.linspace(0, 2*np.pi, 100)
    r = np.sin(4*theta)
    axes[2, 1].plot(theta, r)
    axes[2, 1].set_title("Test Polar Plot")
    
    plt.close(fig._fig_mpl if hasattr(fig, '_fig_mpl') else fig)


def test_axes_wrapper_multiple_assignments():
    """Test multiple item assignments to verify robustness."""
    import scitex
    
    fig, axes = scitex.plt.subplots(2, 2, figsize=(8, 6))
    
    # Store original axes
    originals = {}
    for i in range(2):
        for j in range(2):
            originals[(i, j)] = axes[i, j]
    
    # Test multiple assignments
    new_axes = {}
    for i in range(2):
        for j in range(2):
            subplot_num = i * 2 + j + 1
            if (i, j) == (1, 1):  # Make last one polar
                new_ax = plt.subplot(2, 2, subplot_num, projection="polar")
            else:
                new_ax = plt.subplot(2, 2, subplot_num)
            axes[i, j] = new_ax
            new_axes[(i, j)] = new_ax
    
    # Verify all assignments worked
    for i in range(2):
        for j in range(2):
            assert axes[i, j] is new_axes[(i, j)], f"Assignment failed at [{i}, {j}]"
            assert axes[i, j] != originals[(i, j)], f"Original axis not replaced at [{i}, {j}]"
    
    plt.close(fig._fig_mpl if hasattr(fig, '_fig_mpl') else fig)


def test_axes_wrapper_assignment_with_slicing():
    """Test item assignment compatibility with slicing operations."""
    import scitex
    
    fig, axes = scitex.plt.subplots(3, 3, figsize=(9, 9))
    
    # Test single element assignment
    new_ax = plt.subplot(3, 3, 5)  # Middle element
    axes[1, 1] = new_ax
    assert axes[1, 1] is new_ax
    
    # Test that slicing still works for reading
    first_row = axes[0, :]
    assert hasattr(first_row, '__len__')
    assert len(first_row) == 3
    
    first_col = axes[:, 0]
    assert hasattr(first_col, '__len__')
    assert len(first_col) == 3
    
    plt.close(fig._fig_mpl if hasattr(fig, '_fig_mpl') else fig)


def test_axes_wrapper_assignment_edge_cases():
    """Test edge cases for item assignment."""
    import scitex
    
    # Test with 2x1 grid (minimum for AxesWrapper)
    fig, axes = scitex.plt.subplots(2, 1, figsize=(6, 8))
    
    # For 2x1 grid, indexing is [row] not [row, col]
    original_ax_0 = axes[0]
    original_ax_1 = axes[1]
    
    new_ax_0 = plt.subplot(2, 1, 1)
    new_ax_1 = plt.subplot(2, 1, 2, projection="polar")
    
    axes[0] = new_ax_0
    axes[1] = new_ax_1
    
    assert axes[0] is new_ax_0
    assert axes[1] is new_ax_1
    assert axes[0] != original_ax_0
    assert axes[1] != original_ax_1
    
    plt.close(fig._fig_mpl if hasattr(fig, '_fig_mpl') else fig)


def test_axes_wrapper_assignment_preserves_other_functionality():
    """Test that item assignment doesn't break other AxesWrapper functionality."""
    import scitex
    
    fig, axes = scitex.plt.subplots(2, 2, figsize=(8, 6))
    
    # Test shape property
    assert axes.shape == (2, 2)
    
    # Test flat property
    assert len(list(axes.flat)) == 4
    
    # Test indexing still works
    ax_00 = axes[0, 0]
    assert ax_00 is not None
    
    # Perform assignment
    new_ax = plt.subplot(2, 2, 1)
    axes[0, 0] = new_ax
    
    # Verify other functionality still works
    assert axes.shape == (2, 2)
    assert len(list(axes.flat)) == 4
    assert axes[0, 0] is new_ax
    
    # Test that we can still iterate
    count = 0
    for ax in axes:
        count += 1
    assert count == 2  # Two rows
    
    plt.close(fig._fig_mpl if hasattr(fig, '_fig_mpl') else fig)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])