#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test comprehensive matplotlib tracking functionality

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'src'))

import scitex


class TestComprehensiveTracking:
    """Test comprehensive matplotlib plotting function tracking."""
    
    def setup_method(self):
        """Setup for each test method."""
        plt.close('all')
        
    def teardown_method(self):
        """Cleanup after each test method."""
        plt.close('all')
    
    def test_basic_plot(self):
        """Test basic plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        ax.plot(x, y, id="test_plot")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_plot_plot_x" in df.columns
        assert "test_plot_plot_y" in df.columns
        np.testing.assert_array_equal(df["test_plot_plot_x"].values, x)
        np.testing.assert_array_equal(df["test_plot_plot_y"].values, y)
        
    def test_scatter_plot(self):
        """Test scatter plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        sizes = np.array([10, 20, 30, 40])
        colors = np.array([0.1, 0.3, 0.5, 0.7])
        
        ax.scatter(x, y, sizes, colors, id="test_scatter")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_scatter_scatter_x" in df.columns
        assert "test_scatter_scatter_y" in df.columns
        assert "test_scatter_scatter_s" in df.columns
        assert "test_scatter_scatter_c" in df.columns
        
    def test_bar_plot(self):
        """Test bar plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = ['A', 'B', 'C', 'D']
        y = [1, 3, 2, 4]
        yerr = [0.1, 0.2, 0.15, 0.25]
        
        ax.bar(x, y, yerr=yerr, id="test_bar")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_bar_bar_x" in df.columns
        assert "test_bar_bar_y" in df.columns
        assert "test_bar_bar_yerr" in df.columns
        
    def test_barh_plot(self):
        """Test horizontal bar plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        y = ['A', 'B', 'C', 'D']
        x = [1, 3, 2, 4]
        
        ax.barh(y, x, id="test_barh")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_barh_barh_x" in df.columns
        assert "test_barh_barh_y" in df.columns
        
    def test_hist_plot(self):
        """Test histogram tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        data = np.random.normal(0, 1, 100)
        
        ax.hist(data, id="test_hist")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_hist_hist_x" in df.columns
        np.testing.assert_array_equal(df["test_hist_hist_x"].values, data)
        
    def test_boxplot(self):
        """Test boxplot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        data = [np.random.normal(0, 1, 50), np.random.normal(1, 1.5, 50)]
        
        ax.boxplot(data, id="test_boxplot")
        
        df = ax.export_as_csv()
        assert not df.empty
        # Boxplot should have columns for each box
        assert any("test_boxplot_boxplot" in col for col in df.columns)
        
    def test_violinplot(self):
        """Test violin plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        data = [np.random.normal(0, 1, 50), np.random.normal(1, 1.5, 50)]
        
        ax.violinplot(data, id="test_violin")
        
        df = ax.export_as_csv()
        assert not df.empty
        # Violin plot should have columns for each violin
        assert any("test_violin_violinplot" in col for col in df.columns)
        
    def test_fill_between(self):
        """Test fill_between tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        ax.fill_between(x, y1, y2, id="test_fill")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_fill_fill_between_x" in df.columns
        assert "test_fill_fill_between_y1" in df.columns
        assert "test_fill_fill_between_y2" in df.columns
        
    def test_fill_betweenx(self):
        """Test fill_betweenx tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        y = np.linspace(0, 10, 50)
        x1 = np.sin(y)
        x2 = np.cos(y)
        
        ax.fill_betweenx(y, x1, x2, id="test_fillx")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_fillx_fill_betweenx_y" in df.columns
        assert "test_fillx_fill_betweenx_x1" in df.columns
        assert "test_fillx_fill_betweenx_x2" in df.columns
        
    def test_errorbar(self):
        """Test errorbar tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        yerr = np.array([0.1, 0.2, 0.3, 0.4])
        xerr = np.array([0.05, 0.1, 0.15, 0.2])
        
        ax.errorbar(x, y, yerr=yerr, xerr=xerr, id="test_errorbar")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_errorbar_errorbar_x" in df.columns
        assert "test_errorbar_errorbar_y" in df.columns
        assert "test_errorbar_errorbar_yerr" in df.columns
        assert "test_errorbar_errorbar_xerr" in df.columns
        
    def test_step_plot(self):
        """Test step plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        
        ax.step(x, y, id="test_step")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_step_step_x" in df.columns
        assert "test_step_step_y" in df.columns
        
    def test_stem_plot(self):
        """Test stem plot tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        
        ax.stem(x, y, id="test_stem")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_stem_stem_x" in df.columns
        assert "test_stem_stem_y" in df.columns
        
    def test_hist2d(self):
        """Test hist2d tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.random.normal(0, 1, 100)
        y = np.random.normal(0, 1, 100)
        
        ax.hist2d(x, y, id="test_hist2d")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_hist2d_hist2d_x" in df.columns
        assert "test_hist2d_hist2d_y" in df.columns
        
    def test_hexbin(self):
        """Test hexbin tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.random.normal(0, 1, 100)
        y = np.random.normal(0, 1, 100)
        
        ax.hexbin(x, y, id="test_hexbin")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_hexbin_hexbin_x" in df.columns
        assert "test_hexbin_hexbin_y" in df.columns
        
    def test_pie_chart(self):
        """Test pie chart tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        sizes = [30, 25, 20, 15, 10]
        labels = ['A', 'B', 'C', 'D', 'E']
        
        ax.pie(sizes, labels=labels, id="test_pie")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_pie_pie_values" in df.columns
        assert "test_pie_pie_labels" in df.columns
        
    def test_imshow(self):
        """Test imshow tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        data = np.random.random((10, 10))
        
        ax.imshow(data, id="test_imshow")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_imshow_imshow_row" in df.columns
        assert "test_imshow_imshow_col" in df.columns
        assert "test_imshow_imshow_value" in df.columns
        assert len(df) == 100  # 10x10 = 100 pixels
        
    def test_contour(self):
        """Test contour tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.linspace(-3, 3, 20)
        y = np.linspace(-3, 3, 20)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        
        ax.contour(X, Y, Z, id="test_contour")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_contour_contour_X" in df.columns
        assert "test_contour_contour_Y" in df.columns
        assert "test_contour_contour_Z" in df.columns
        
    def test_quiver(self):
        """Test quiver tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        x = np.array([1, 2, 3])
        y = np.array([1, 2, 3])
        u = np.array([0.5, 1.0, 1.5])
        v = np.array([0.3, 0.6, 0.9])
        
        ax.quiver(x, y, u, v, id="test_quiver")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_quiver_quiver_X" in df.columns
        assert "test_quiver_quiver_Y" in df.columns
        assert "test_quiver_quiver_U" in df.columns
        assert "test_quiver_quiver_V" in df.columns
        
    def test_text_annotation(self):
        """Test text annotation tracking."""
        fig, ax = scitex.plt.subplots(track=True)
        
        ax.text(0.5, 0.5, "Test Text", id="test_text")
        ax.annotate("Test Annotation", xy=(0.3, 0.7), id="test_annotate")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "test_text_text_x" in df.columns
        assert "test_text_text_y" in df.columns
        assert "test_text_text_text" in df.columns
        assert "test_annotate_annotate_x" in df.columns
        assert "test_annotate_annotate_y" in df.columns
        assert "test_annotate_annotate_text" in df.columns
        
    def test_twinx_tracking(self):
        """Test that twinx axes are properly wrapped and tracked."""
        fig, ax1 = scitex.plt.subplots(track=True)
        
        # Plot on primary axis
        x = np.array([1, 2, 3, 4])
        y1 = np.array([2, 4, 6, 8])
        ax1.plot(x, y1, id="primary_plot")
        
        # Create twin axis and plot
        ax2 = ax1.twinx()
        y2 = np.array([1, 3, 5, 7])
        ax2.plot(x, y2, id="secondary_plot")
        
        # Check that both axes can export data
        df1 = ax1.export_as_csv()
        df2 = ax2.export_as_csv()
        
        assert not df1.empty
        assert not df2.empty
        assert "primary_plot_plot_x" in df1.columns
        assert "secondary_plot_plot_x" in df2.columns
        
    def test_twiny_tracking(self):
        """Test that twiny axes are properly wrapped and tracked."""
        fig, ax1 = scitex.plt.subplots(track=True)
        
        # Plot on primary axis
        x1 = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        ax1.plot(x1, y, id="primary_plot")
        
        # Create twin axis and plot
        ax2 = ax1.twiny()
        x2 = np.array([10, 20, 30, 40])
        ax2.plot(x2, y, id="secondary_plot")
        
        # Check that both axes can export data
        df1 = ax1.export_as_csv()
        df2 = ax2.export_as_csv()
        
        assert not df1.empty
        assert not df2.empty
        assert "primary_plot_plot_x" in df1.columns
        assert "secondary_plot_plot_x" in df2.columns
        
    def test_torch_tensor_conversion(self):
        """Test torch tensor to numpy conversion."""
        try:
            import torch
            
            fig, ax = scitex.plt.subplots(track=True)
            x_torch = torch.tensor([1.0, 2.0, 3.0, 4.0])
            y_torch = torch.tensor([2.0, 4.0, 6.0, 8.0])
            
            ax.plot(x_torch, y_torch, id="torch_plot")
            
            df = ax.export_as_csv()
            assert not df.empty
            assert "torch_plot_plot_x" in df.columns
            assert "torch_plot_plot_y" in df.columns
            
            # Check that values are correctly converted
            np.testing.assert_array_equal(
                df["torch_plot_plot_x"].values,
                x_torch.numpy()
            )
            
        except ImportError:
            pytest.skip("PyTorch not available")
            
    def test_pandas_series_conversion(self):
        """Test pandas series to numpy conversion."""
        fig, ax = scitex.plt.subplots(track=True)
        x_pd = pd.Series([1, 2, 3, 4])
        y_pd = pd.Series([2, 4, 6, 8])
        
        ax.plot(x_pd, y_pd, id="pandas_plot")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert "pandas_plot_plot_x" in df.columns
        assert "pandas_plot_plot_y" in df.columns
        
        # Check that values are correctly converted
        np.testing.assert_array_equal(
            df["pandas_plot_plot_x"].values,
            x_pd.values
        )
        
    def test_multiple_plot_formats(self):
        """Test various matplotlib plot argument formats."""
        fig, ax = scitex.plt.subplots(track=True)
        
        # Test different plot argument formats
        y_only = np.array([1, 2, 3, 4])
        ax.plot(y_only, id="y_only_plot")
        
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        ax.plot(x, y, 'r-', id="xy_fmt_plot")
        
        # Multiple line plots in one call
        ax.plot(x, y, 'b-', x, y*2, 'g--', id="multi_line_plot")
        
        df = ax.export_as_csv()
        assert not df.empty
        
        # Check that all plots are captured
        assert "y_only_plot_plot_x" in df.columns
        assert "xy_fmt_plot_plot_x" in df.columns
        assert "multi_line_plot_plot_x00" in df.columns
        assert "multi_line_plot_plot_x01" in df.columns
        
    def test_tracking_disabled(self):
        """Test that tracking can be disabled."""
        fig, ax = scitex.plt.subplots(track=False)
        x = np.array([1, 2, 3, 4])
        y = np.array([2, 4, 6, 8])
        ax.plot(x, y, id="disabled_plot")
        
        df = ax.export_as_csv()
        # Should return empty DataFrame when tracking is disabled
        assert df.empty
        
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        fig, ax = scitex.plt.subplots(track=True)
        
        # Create large dataset
        n_points = 10000
        x = np.linspace(0, 100, n_points)
        y = np.sin(x) + np.random.normal(0, 0.1, n_points)
        
        ax.plot(x, y, id="large_plot")
        
        df = ax.export_as_csv()
        assert not df.empty
        assert len(df) == n_points
        assert "large_plot_plot_x" in df.columns
        assert "large_plot_plot_y" in df.columns


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])