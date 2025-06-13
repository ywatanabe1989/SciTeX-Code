#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04"
# Author: ywatanabe
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/plt/_subplots/test_export_as_csv_for_sigmaplot.py

"""Test export_as_csv_for_sigmaplot functionality."""

import numpy as np
import pandas as pd
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import scitex


class TestExportAsCSVForSigmaPlot:
    """Test export_as_csv_for_sigmaplot functionality."""

    def test_basic_export_with_visual_params(self):
        """Test basic export with visual parameters included."""
        fig, ax = scitex.plt.subplots()
        
        # Create some plots
        x = [1, 2, 3]
        y1 = [4, 5, 6]
        y2 = [7, 8, 9]
        
        ax.plot(x, y1, id="line1")
        ax.scatter(x, y2, id="scatter1")
        
        # Export with visual params
        df = ax.export_as_csv_for_sigmaplot(include_visual_params=True)
        
        # Check that dataframe is not empty
        assert not df.empty
        
        # Check that visual parameter columns exist
        assert "visual parameter label" in df.columns
        assert "visual parameter value" in df.columns
        assert "xticks" in df.columns
        assert "yticks" in df.columns
        
        # Check that data columns exist
        assert "line1_plot_x" in df.columns
        assert "line1_plot_y" in df.columns
        assert "scatter1_scatter_x" in df.columns
        assert "scatter1_scatter_y" in df.columns
        
    def test_export_without_visual_params(self):
        """Test export without visual parameters."""
        fig, ax = scitex.plt.subplots()
        
        # Create some plots
        x = [1, 2, 3]
        y = [4, 5, 6]
        
        ax.plot(x, y, id="test_plot")
        
        # Export without visual params
        df = ax.export_as_csv_for_sigmaplot(include_visual_params=False)
        
        # Check that visual parameter columns don't exist
        assert "visual parameter label" not in df.columns
        assert "visual parameter value" not in df.columns
        
        # Check that data columns exist
        assert "test_plot_plot_x" in df.columns
        assert "test_plot_plot_y" in df.columns
        
    def test_different_plot_types(self):
        """Test export with different plot types."""
        fig, ax = scitex.plt.subplots()
        
        # Bar plot
        ax.bar(["A", "B", "C"], [1, 2, 3], yerr=[0.1, 0.2, 0.3], id="bar1")
        
        df = ax.export_as_csv_for_sigmaplot()
        
        # Check bar-specific visual parameters
        params_df = df[["visual parameter label", "visual parameter value"]].dropna()
        params_dict = dict(zip(params_df["visual parameter label"], 
                              params_df["visual parameter value"]))
        
        # Bar plots should have category scale and rotated labels
        assert params_dict.get("xscale") == "category"
        assert params_dict.get("xrot") == 45
        assert params_dict.get("ymin") == 0
        
    def test_data_padding(self):
        """Test that data is properly padded with NaN."""
        fig, ax = scitex.plt.subplots()
        
        # Create plots with different lengths
        ax.plot([1, 2, 3], [4, 5, 6], id="short")
        ax.plot([1, 2, 3, 4, 5], [7, 8, 9, 10, 11], id="long")
        
        df = ax.export_as_csv_for_sigmaplot()
        
        # All columns should have the same length
        col_lengths = [len(df[col]) for col in df.columns]
        assert len(set(col_lengths)) == 1
        
        # Check that NaN padding exists
        assert df["short_plot_x"].isna().any()
        assert df["short_plot_y"].isna().any()
        
    def test_empty_history(self):
        """Test export with empty plotting history."""
        fig, ax = scitex.plt.subplots()
        
        # No plots created
        df = ax.export_as_csv_for_sigmaplot()
        
        # Should return empty dataframe
        assert df.empty
        
    def test_preserved_columns(self):
        """Test that preserved columns are added for SigmaPlot compatibility."""
        fig, ax = scitex.plt.subplots()
        
        ax.plot([1, 2, 3], [4, 5, 6], id="test")
        
        df = ax.export_as_csv_for_sigmaplot()
        
        # Check for preserved columns
        preserved_cols = [col for col in df.columns if col.startswith("preserved")]
        assert len(preserved_cols) > 0
        
        # Preserved columns should contain "NONE_STR"
        for col in preserved_cols:
            assert (df[col] == "NONE_STR").all()


def test_integration_with_io_save_dataframe():
    """Test that exported dataframe can be saved with scitex.io.save."""
    import tempfile
    import os
    
    fig, ax = scitex.plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.scatter([1, 2, 3], [7, 8, 9])
    
    # Export for SigmaPlot
    df = ax.export_as_csv_for_sigmaplot()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        temp_path = tmp.name
        
    try:
        scitex.io.save(df, temp_path)
        
        # Verify file exists and can be read
        assert os.path.exists(temp_path)
        df_loaded = pd.read_csv(temp_path)
        assert len(df_loaded) == len(df)
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_automatic_sigmaplot_export_on_figure_save():
    """Test that saving a figure automatically creates a SigmaPlot CSV."""
    import tempfile
    import os
    
    fig, ax = scitex.plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6], id="test_plot")
    ax.scatter([1, 2, 3], [7, 8, 9], id="test_scatter")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save figure
        img_path = os.path.join(tmpdir, "test_figure.png")
        scitex.io.save(fig, img_path, verbose=True)
        
        # Check that image was saved
        assert os.path.exists(img_path)
        
        # Check that regular CSV was saved
        csv_path = img_path.replace(".png", ".csv")
        assert os.path.exists(csv_path), f"Regular CSV not found at {csv_path}"
        
        # Check that SigmaPlot CSV was saved
        sigmaplot_csv_path = img_path.replace(".png", "_for_sigmaplot.csv")
        
        # List all files in the directory for debugging
        print(f"\nFiles in {tmpdir}:")
        for f in os.listdir(tmpdir):
            print(f"  {f}")
        
        # Check if figure has the export method
        print(f"\nFigure has export_as_csv: {hasattr(fig, 'export_as_csv')}")
        print(f"Figure has export_as_csv_for_sigmaplot: {hasattr(fig, 'export_as_csv_for_sigmaplot')}")
        
        assert os.path.exists(sigmaplot_csv_path), f"SigmaPlot CSV not found at {sigmaplot_csv_path}"
        
        # Verify SigmaPlot CSV contains visual parameters
        df_sigmaplot = pd.read_csv(sigmaplot_csv_path)
        assert "visual parameter label" in df_sigmaplot.columns
        assert "visual parameter value" in df_sigmaplot.columns
        
        # Verify regular CSV doesn't contain visual parameters
        df_regular = pd.read_csv(csv_path)
        assert "visual parameter label" not in df_regular.columns
        
        # Verify both contain plot data
        # Note: FigWrapper prefixes columns with ax_00_ when exporting from multiple axes
        assert any("test_plot_plot_x" in col for col in df_regular.columns)
        assert any("test_plot_plot_x" in col for col in df_sigmaplot.columns)


def test_multiple_plot_types_sigmaplot_export():
    """Test SigmaPlot export with various plot types."""
    fig, ax = scitex.plt.subplots()
    
    # Create various plot types
    x = np.linspace(0, 10, 20)
    y = np.sin(x)
    
    # Line plot
    ax.plot(x, y, id="line")
    
    # Scatter plot
    ax.scatter(x[::2], y[::2] + 0.1, id="scatter")
    
    # Bar plot
    ax.bar([1, 2, 3], [0.5, 0.7, 0.3], id="bar")
    
    # Error bar
    yerr = np.random.rand(5) * 0.1
    ax.errorbar([2, 4, 6, 8, 10], [0.2, 0.4, 0.6, 0.8, 1.0], yerr=yerr, id="errorbar")
    
    # Fill between
    ax.fill_between([0, 5, 10], [0, 0.5, 0], [0.2, 0.7, 0.2], id="fill")
    
    # Export for SigmaPlot
    df = ax.export_as_csv_for_sigmaplot()
    
    # Verify all plot data is present
    assert "line_plot_x" in df.columns
    assert "scatter_scatter_x" in df.columns
    assert "bar_bar_x" in df.columns
    assert "errorbar_errorbar_x" in df.columns
    assert "errorbar_errorbar_yerr" in df.columns
    assert "fill_fill_between_x" in df.columns
    assert "fill_fill_between_y1" in df.columns
    
    # Verify visual parameters are included
    assert "visual parameter label" in df.columns
    assert not df.empty


def test_no_tracking_export():
    """Test that export returns empty dataframe when tracking is disabled."""
    fig, ax = scitex.plt.subplots(track=False)
    
    ax.plot([1, 2, 3], [4, 5, 6])
    
    # Should return empty dataframe
    df = ax.export_as_csv_for_sigmaplot()
    assert df.empty


def test_figure_without_export_method():
    """Test that regular matplotlib figures don't break io.save."""
    import tempfile
    import os
    
    # Create regular matplotlib figure (not scitex wrapped)
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save figure - should not raise error
        img_path = os.path.join(tmpdir, "regular_figure.png")
        scitex.io.save(fig, img_path, verbose=False)
        
        # Check that image was saved
        assert os.path.exists(img_path)
        
        # Check that no CSV files were created (since it's not tracked)
        csv_path = img_path.replace(".png", ".csv")
        sigmaplot_csv_path = img_path.replace(".png", "_for_sigmaplot.csv")
        assert not os.path.exists(csv_path)
        assert not os.path.exists(sigmaplot_csv_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])