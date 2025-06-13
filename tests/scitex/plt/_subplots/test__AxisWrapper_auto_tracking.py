#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 06:33:00 (ywatanabe)"
# File: ./tests/scitex/plt/_subplots/test__AxisWrapper_auto_tracking.py

import pytest
import numpy as np
import pandas as pd
import os
import tempfile


def test_auto_tracking_without_explicit_id():
    """Test that plotting methods are tracked automatically without explicit id."""
    import scitex
    
    fig, ax = scitex.plt.subplots(track=True)
    
    # Plot without explicit id
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.scatter([2, 3, 4], [5, 6, 7])
    ax.bar(['A', 'B', 'C'], [10, 20, 30])
    
    # Verify tracking
    assert len(ax.history) == 3, "Should have 3 tracked plots"
    assert 0 in ax.history, "First plot should have auto-generated id 0"
    assert 1 in ax.history, "Second plot should have auto-generated id 1"
    assert 2 in ax.history, "Third plot should have auto-generated id 2"
    
    # Verify export
    df = ax.export_as_csv()
    assert not df.empty, "Exported DataFrame should not be empty"
    assert df.shape[0] == 3, "Should have 3 rows of data"
    assert '0_plot_x' in df.columns, "Should have plot x data"
    assert '0_plot_y' in df.columns, "Should have plot y data"
    assert '1_scatter_x' in df.columns, "Should have scatter x data"
    assert '2_bar_y' in df.columns, "Should have bar y data"


def test_mixed_auto_and_explicit_id():
    """Test that auto-tracking and explicit id can be mixed."""
    import scitex
    
    fig, ax = scitex.plt.subplots()
    
    # Mix auto and explicit id
    ax.plot([1, 2, 3], [4, 5, 6])  # auto id = 0
    ax.plot([1, 2, 3], [7, 8, 9], id="myplot")  # explicit id
    ax.plot([1, 2, 3], [10, 11, 12])  # auto id = 2
    
    assert len(ax.history) == 3
    assert 0 in ax.history
    assert "myplot" in ax.history
    assert 2 in ax.history
    
    df = ax.export_as_csv()
    assert 'myplot_plot_x' in df.columns
    assert 'myplot_plot_y' in df.columns


def test_tracking_disabled():
    """Test that tracking can be disabled."""
    import scitex
    
    fig, ax = scitex.plt.subplots(track=False)
    
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.scatter([2, 3, 4], [5, 6, 7])
    
    assert len(ax.history) == 0, "Should have no tracked plots when tracking is disabled"
    
    df = ax.export_as_csv()
    assert df.empty, "Exported DataFrame should be empty when tracking is disabled"


def test_supported_plot_types():
    """Test that all common plot types are tracked."""
    import scitex
    
    fig, ax = scitex.plt.subplots()
    
    # Test various plot types
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.scatter([1, 2, 3], [4, 5, 6])
    ax.bar([1, 2, 3], [4, 5, 6])
    ax.hist([1, 2, 2, 3, 3, 3])
    ax.errorbar([1, 2, 3], [4, 5, 6], yerr=[0.1, 0.2, 0.1])
    ax.step([1, 2, 3], [4, 5, 6])
    ax.stem([1, 2, 3], [4, 5, 6])
    ax.fill_between([1, 2, 3], [3, 4, 5], [5, 6, 7])
    
    assert len(ax.history) >= 8, "Should track all supported plot types"


def test_save_with_csv_export():
    """Test that scitex.io.save exports CSV with plotting history."""
    import scitex
    
    with tempfile.TemporaryDirectory() as tmpdir:
        fig, ax = scitex.plt.subplots()
        
        # Create plots
        ax.plot([1, 2, 3, 4, 5], [2, 4, 3, 5, 6])
        ax.plot([1, 2, 3, 4, 5], [1, 3, 2, 4, 3])
        
        # Save to temporary directory
        png_path = os.path.join(tmpdir, "test.png")
        scitex.io.save(fig, png_path, verbose=False)
        
        # Check that CSV was created
        csv_path = png_path.replace(".png", ".csv")
        # The CSV is saved in a subdirectory with _out suffix
        base_dir = os.path.dirname(png_path)
        csv_dir = os.path.join(base_dir, "test__AxisWrapper_auto_tracking_out")
        csv_file = os.path.join(csv_dir, "test.csv")
        
        # Check if CSV exists in the expected location
        csv_exists = False
        if os.path.exists(csv_file):
            csv_exists = True
            df = pd.read_csv(csv_file)
            assert not df.empty, "Saved CSV should contain data"
            assert df.shape[0] == 5, "Should have 5 rows of data"
        
        # Also check if it's in the same directory (in case behavior changes)
        elif os.path.exists(csv_path):
            csv_exists = True
            df = pd.read_csv(csv_path)
            assert not df.empty, "Saved CSV should contain data"
            assert df.shape[0] == 5, "Should have 5 rows of data"
        
        assert csv_exists, "CSV file should be created when saving figure with plots"


def test_no_tracking_for_non_plot_methods():
    """Test that non-plotting methods are not tracked."""
    import scitex
    
    fig, ax = scitex.plt.subplots()
    
    # Non-plotting methods should not be tracked
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_title("Title")
    ax.grid(True)
    
    assert len(ax.history) == 0, "Non-plotting methods should not be tracked"
    
    # Add a plot to verify tracking still works
    ax.plot([1, 2, 3], [4, 5, 6])
    assert len(ax.history) == 1, "Plotting methods should still be tracked"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])