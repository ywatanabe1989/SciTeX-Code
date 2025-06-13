#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-29 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/plt/_subplots/test__SubplotsWrapper.py

import numpy as np
import pytest
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

import scitex


class TestSubplotsWrapper:
    """Test cases for scitex.plt.subplots wrapper functionality."""

    def test_single_axis(self):
        """Test that single axis returns an AxisWrapper object."""
        fig, ax = scitex.plt.subplots()
        assert hasattr(ax, "plot"), "Single axis should have plot method"
        assert hasattr(ax, "export_as_csv"), "Should have export_as_csv method"
        plt.close(fig)

    def test_1d_array_single_row(self):
        """Test that single row multiple columns returns 1D array."""
        fig, axes = scitex.plt.subplots(1, 3)
        assert hasattr(axes, "__len__"), "Should return array-like object"
        assert len(axes) == 3, "Should have 3 axes"
        # Test individual axis access
        for i in range(3):
            assert hasattr(axes[i], "plot"), f"axes[{i}] should have plot method"
        plt.close(fig)

    def test_1d_array_single_column(self):
        """Test that multiple rows single column returns 1D array."""
        fig, axes = scitex.plt.subplots(3, 1)
        assert hasattr(axes, "__len__"), "Should return array-like object"
        assert len(axes) == 3, "Should have 3 axes"
        # Test individual axis access
        for i in range(3):
            assert hasattr(axes[i], "plot"), f"axes[{i}] should have plot method"
        plt.close(fig)

    def test_2d_array_indexing(self):
        """Test that 2D grid allows 2D indexing (the main bug fix)."""
        fig, axes = scitex.plt.subplots(4, 3)

        # Test shape property
        assert hasattr(axes, "shape"), "Should have shape property"
        assert axes.shape == (4, 3), "Shape should be (4, 3)"

        # Test 2D indexing - this is the core fix
        for row in range(4):
            for col in range(3):
                ax = axes[row, col]
                assert hasattr(
                    ax, "plot"
                ), f"axes[{row}, {col}] should have plot method"
                # Test that we can actually plot
                ax.plot([1, 2, 3], [1, 2, 3])

        plt.close(fig)

    def test_2d_array_row_access(self):
        """Test accessing entire rows from 2D array."""
        fig, axes = scitex.plt.subplots(4, 3)

        # Access entire row
        row_axes = axes[0]  # First row
        assert len(row_axes) == 3, "Row should have 3 axes"

        # Each element in row should be plottable
        for i, ax in enumerate(row_axes):
            assert hasattr(ax, "plot"), f"Row axis [{i}] should have plot method"

        plt.close(fig)

    def test_2d_array_slice_access(self):
        """Test slice access on 2D array."""
        fig, axes = scitex.plt.subplots(4, 3)

        # Access slice of rows
        slice_axes = axes[1:3]  # Rows 1 and 2
        assert hasattr(slice_axes, "shape"), "Slice should return AxesWrapper"
        assert slice_axes.shape == (2, 3), "Slice shape should be (2, 3)"

        plt.close(fig)

    def test_backward_compatibility_flat_iteration(self):
        """Test that flat iteration still works for backward compatibility."""
        fig, axes = scitex.plt.subplots(4, 3)

        # Test iteration (should be flattened)
        ax_list = list(axes)
        assert len(ax_list) == 12, "Iteration should yield 12 axes (flattened)"

        # Test each axis is plottable
        for i, ax in enumerate(axes):
            assert hasattr(ax, "plot"), f"Iterated axis {i} should have plot method"

        plt.close(fig)

    def test_export_as_csv_multi_axes(self):
        """Test export_as_csv functionality with multiple axes."""
        fig, axes = scitex.plt.subplots(2, 2)

        # Plot on each axis
        axes[0, 0].plot([1, 2, 3], [1, 2, 3], id="plot00")
        axes[0, 1].plot([1, 2, 3], [3, 2, 1], id="plot01")
        axes[1, 0].plot([1, 2, 3], [2, 3, 4], id="plot10")
        axes[1, 1].plot([1, 2, 3], [4, 3, 2], id="plot11")

        # Test export functionality
        df = axes.export_as_csv()
        assert df is not None, "Should return a DataFrame"
        assert len(df.columns) > 0, "DataFrame should have columns"

        plt.close(fig)

    def test_matplotlib_compatibility(self):
        """Test that the behavior matches matplotlib's for common use cases."""
        # Compare with matplotlib behavior
        mpl_fig, mpl_axes = plt.subplots(3, 2)
        scitex_fig, scitex_axes = scitex.plt.subplots(3, 2)

        # Both should have the same shape
        assert scitex_axes.shape == mpl_axes.shape, "Should have same shape as matplotlib"

        # Both should allow 2D indexing
        for i in range(3):
            for j in range(2):
                # This should not raise an error
                mpl_ax = mpl_axes[i, j]
                scitex_ax = scitex_axes[i, j]
                assert hasattr(scitex_ax, "plot"), "scitex axis should have plot method"

        plt.close(mpl_fig)
        plt.close(scitex_fig)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
