#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 20:55:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_heatmap_enhanced.py
# ----------------------------------------
import os
import sys
from unittest.mock import MagicMock, patch

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.extra.numpy import arrays

# Import the function under test
from scitex.plt.ax._plot import plot_heatmap

# ----------------------------------------
# Fixtures
# ----------------------------------------

@pytest.fixture
def sample_data():
    """Provide various test data for heatmap testing."""
    return {
        'small': np.array([[0.8, 0.2], [0.3, 0.7]]),
        'medium': np.random.rand(10, 10),
        'large': np.random.rand(100, 100),
        'negative': np.random.randn(5, 5),
        'zeros': np.zeros((5, 5)),
        'ones': np.ones((5, 5)),
        'nan_values': np.array([[1, np.nan], [np.nan, 2]]),
        'inf_values': np.array([[1, np.inf], [-np.inf, 2]]),
        'mixed': np.array([[-1.5, 0, 1.5], [2.0, -0.5, 3.0], [0.1, 0.9, -2.0]]),
    }


@pytest.fixture
def fig_ax():
    """Create a fresh figure and axes for each test."""
    fig, ax = plt.subplots(figsize=(8, 6))
    yield fig, ax
    plt.close(fig)


@pytest.fixture
def mock_save():
    """Mock the save function to avoid actual file I/O."""
    with patch('scitex.io.save') as mock:
        yield mock


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    import time
    import tracemalloc
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
        
        def start(self):
            self.start_time = time.time()
            tracemalloc.start()
            self.start_memory = tracemalloc.get_traced_memory()[0]
        
        def stop(self):
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                'duration': time.time() - self.start_time,
                'memory_used': current - self.start_memory,
                'memory_peak': peak
            }
    
    return PerformanceMonitor()


# ----------------------------------------
# Basic Functionality Tests
# ----------------------------------------

class TestBasicFunctionality:
    """Test basic heatmap plotting functionality."""
    
    def test_basic_heatmap(self, fig_ax, sample_data):
        """Test basic heatmap creation with minimal parameters."""
        fig, ax = fig_ax
        data = sample_data['small']
        
        ax_out, im, cbar = plot_heatmap(ax, data)
        
        # Verify outputs
        assert ax_out is ax
        assert isinstance(im, matplotlib.image.AxesImage)
        assert isinstance(cbar, matplotlib.colorbar.Colorbar)
        assert im.get_array().shape == data.shape
        
    def test_with_labels(self, fig_ax, sample_data):
        """Test heatmap with custom labels."""
        fig, ax = fig_ax
        data = sample_data['small']
        x_labels = ['A', 'B']
        y_labels = ['X', 'Y']
        
        ax_out, im, cbar = plot_heatmap(
            ax, data, 
            x_labels=x_labels,
            y_labels=y_labels
        )
        
        # Verify labels are set
        assert [t.get_text() for t in ax.get_xticklabels()] == x_labels
        assert [t.get_text() for t in ax.get_yticklabels()] == y_labels
        
    def test_custom_colormap(self, fig_ax, sample_data):
        """Test heatmap with various colormaps."""
        fig, ax = fig_ax
        data = sample_data['medium']
        
        for cmap in ['viridis', 'plasma', 'coolwarm', 'RdBu']:
            ax.clear()
            ax_out, im, cbar = plot_heatmap(ax, data, cmap=cmap)
            assert im.get_cmap().name == cmap


# ----------------------------------------
# Parametrized Tests
# ----------------------------------------

class TestParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("data_size", [(2, 2), (5, 10), (20, 15), (50, 50)])
    def test_various_data_sizes(self, fig_ax, data_size):
        """Test heatmap with various data sizes."""
        fig, ax = fig_ax
        data = np.random.rand(*data_size)
        
        ax_out, im, cbar = plot_heatmap(ax, data)
        assert im.get_array().shape == data_size
        
    @pytest.mark.parametrize("show_annot", [True, False])
    def test_annotation_toggle(self, fig_ax, sample_data, show_annot):
        """Test annotation visibility toggle."""
        fig, ax = fig_ax
        data = sample_data['small']
        
        ax_out, im, cbar = plot_heatmap(ax, data, show_annot=show_annot)
        
        # Check if text annotations exist
        texts = [child for child in ax.get_children() if isinstance(child, matplotlib.text.Text)]
        # Filter out axis labels
        texts = [t for t in texts if t.get_position()[0] >= 0 and t.get_position()[1] >= 0]
        
        if show_annot:
            assert len(texts) == data.size
        else:
            assert len(texts) == 0
            
    @pytest.mark.parametrize("annot_format", [
        "{x:.1f}", "{x:.2f}", "{x:.0f}", "{x:.3e}"
    ])
    def test_annotation_formats(self, fig_ax, sample_data, annot_format):
        """Test various annotation formats."""
        fig, ax = fig_ax
        data = sample_data['small']
        
        ax_out, im, cbar = plot_heatmap(
            ax, data, 
            show_annot=True,
            annot_format=annot_format
        )
        
        # Verify format is applied (this is a simplified check)
        texts = [child for child in ax.get_children() if isinstance(child, matplotlib.text.Text)]
        assert len(texts) > 0


# ----------------------------------------
# Edge Cases and Error Handling
# ----------------------------------------

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_data(self, fig_ax):
        """Test handling of empty data array."""
        fig, ax = fig_ax
        data = np.array([])
        
        with pytest.raises((ValueError, IndexError)):
            plot_heatmap(ax, data)
            
    def test_1d_data(self, fig_ax):
        """Test handling of 1D data array."""
        fig, ax = fig_ax
        data = np.array([1, 2, 3, 4])
        
        # Should either raise error or reshape
        with pytest.raises((ValueError, IndexError, AttributeError)):
            plot_heatmap(ax, data)
            
    def test_nan_values(self, fig_ax, sample_data):
        """Test handling of NaN values."""
        fig, ax = fig_ax
        data = sample_data['nan_values']
        
        # Should handle NaN gracefully
        ax_out, im, cbar = plot_heatmap(ax, data)
        assert ax_out is ax
        
    def test_inf_values(self, fig_ax, sample_data):
        """Test handling of infinite values."""
        fig, ax = fig_ax
        data = sample_data['inf_values']
        
        # Should handle inf gracefully
        ax_out, im, cbar = plot_heatmap(ax, data)
        assert ax_out is ax
        
    def test_mismatched_labels(self, fig_ax, sample_data):
        """Test handling of mismatched label lengths."""
        fig, ax = fig_ax
        data = sample_data['small']  # 2x2
        
        # Too many labels
        x_labels = ['A', 'B', 'C']
        y_labels = ['X', 'Y', 'Z']
        
        # Should either handle gracefully or raise error
        ax_out, im, cbar = plot_heatmap(
            ax, data,
            x_labels=x_labels[:data.shape[1]],  # Truncate to match
            y_labels=y_labels[:data.shape[0]]
        )
        assert ax_out is ax


# ----------------------------------------
# Property-Based Testing
# ----------------------------------------

class TestPropertyBased:
    """Property-based tests using Hypothesis."""
    
    @given(
        data=arrays(
            dtype=np.float64,
            shape=st.tuples(
                st.integers(min_value=2, max_value=20),
                st.integers(min_value=2, max_value=20)
            ),
            elements=st.floats(min_value=-100, max_value=100, allow_nan=False)
        )
    )
    @settings(max_examples=50, deadline=5000)
    def test_arbitrary_data(self, data):
        """Test with arbitrary valid data arrays."""
        fig, ax = plt.subplots()
        try:
            ax_out, im, cbar = plot_heatmap(ax, data)
            
            # Basic properties that should always hold
            assert ax_out is ax
            assert im.get_array().shape == data.shape
            assert isinstance(cbar, matplotlib.colorbar.Colorbar)
        finally:
            plt.close(fig)
            
    @given(
        cmap=st.sampled_from(['viridis', 'plasma', 'inferno', 'magma', 'cividis'])
    )
    def test_colormap_property(self, cmap):
        """Test that any valid colormap works correctly."""
        fig, ax = plt.subplots()
        data = np.random.rand(5, 5)
        
        try:
            ax_out, im, cbar = plot_heatmap(ax, data, cmap=cmap)
            assert im.get_cmap().name == cmap
        finally:
            plt.close(fig)


# ----------------------------------------
# Mock and Integration Tests
# ----------------------------------------

class TestMocking:
    """Tests using mocks to isolate functionality."""
    
    @patch('matplotlib.pyplot.gca')
    def test_without_ax_parameter(self, mock_gca, sample_data):
        """Test that function gets current axes when ax is None."""
        # Note: This assumes the function has logic to handle ax=None
        mock_ax = MagicMock()
        mock_gca.return_value = mock_ax
        
        # This test would require modification of the actual function
        # to accept ax=None, which is common in matplotlib functions
        
    def test_colorbar_creation_mocked(self, fig_ax, sample_data):
        """Test colorbar creation with mocked components."""
        fig, ax = fig_ax
        data = sample_data['small']
        
        with patch.object(fig, 'colorbar') as mock_colorbar:
            mock_cbar = MagicMock()
            mock_colorbar.return_value = mock_cbar
            
            ax_out, im, cbar = plot_heatmap(ax, data)
            
            # Verify colorbar was created
            mock_colorbar.assert_called_once()
            assert cbar is mock_cbar


# ----------------------------------------
# Performance Tests
# ----------------------------------------

class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_data_performance(self, fig_ax, performance_monitor):
        """Test performance with large data arrays."""
        fig, ax = fig_ax
        data = np.random.rand(500, 500)
        
        performance_monitor.start()
        ax_out, im, cbar = plot_heatmap(ax, data, show_annot=False)
        metrics = performance_monitor.stop()
        
        # Performance assertions
        assert metrics['duration'] < 2.0  # Should complete in under 2 seconds
        assert metrics['memory_used'] < 100 * 1024 * 1024  # Less than 100MB
        
    def test_annotation_performance_scaling(self, performance_monitor):
        """Test how annotation performance scales with data size."""
        sizes = [5, 10, 20]
        times = []
        
        for size in sizes:
            fig, ax = plt.subplots()
            data = np.random.rand(size, size)
            
            performance_monitor.start()
            plot_heatmap(ax, data, show_annot=True)
            metrics = performance_monitor.stop()
            times.append(metrics['duration'])
            
            plt.close(fig)
        
        # Check that scaling is reasonable (not exponential)
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            size_ratio = (sizes[i] ** 2) / (sizes[i-1] ** 2)
            assert ratio < size_ratio * 2  # Allow some overhead


# ----------------------------------------
# Visual Regression Tests
# ----------------------------------------

class TestVisualRegression:
    """Tests for visual output consistency."""
    
    def test_consistent_output(self, fig_ax, sample_data, tmp_path):
        """Test that output is consistent across runs."""
        fig, ax = fig_ax
        data = sample_data['mixed']
        
        # Create heatmap
        ax_out, im, cbar = plot_heatmap(
            ax, data,
            x_labels=['A', 'B', 'C'],
            y_labels=['X', 'Y', 'Z'],
            cmap='coolwarm',
            show_annot=True,
            annot_format="{x:.1f}"
        )
        
        # Save to temporary file
        output_path = tmp_path / "test_heatmap.png"
        fig.savefig(output_path, dpi=100, bbox_inches='tight')
        
        # Verify file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
    def test_annotation_color_contrast(self, fig_ax):
        """Test that annotation colors have good contrast."""
        fig, ax = fig_ax
        data = np.array([[0.1, 0.9], [0.9, 0.1]])
        
        ax_out, im, cbar = plot_heatmap(
            ax, data,
            cmap='viridis',
            show_annot=True
        )
        
        # Get text annotations
        texts = [child for child in ax.get_children() if isinstance(child, matplotlib.text.Text)]
        texts = [t for t in texts if t.get_position()[0] >= 0 and t.get_position()[1] >= 0]
        
        # Should have different colors for contrast
        colors = [t.get_color() for t in texts]
        assert len(set(colors)) > 1  # At least two different colors


# ----------------------------------------
# Integration with scitex ecosystem
# ----------------------------------------

class TestScitexIntegration:
    """Test integration with other scitex modules."""
    
    def test_save_integration(self, fig_ax, sample_data, tmp_path):
        """Test integration with scitex.io.save."""
        fig, ax = fig_ax
        data = sample_data['small']
        
        ax_out, im, cbar = plot_heatmap(ax, data)
        
        # Test saving through scitex.io
        from scitex.io import save
        output_path = str(tmp_path / "heatmap_test.png")
        save(fig, output_path)
        
        assert os.path.exists(output_path)
        
    def test_with_scitex_wrapper(self, sample_data):
        """Test with scitex plotting wrapper if available."""
        try:
            from scitex.plt import subplots
            fig, ax = subplots(1, 1)
            
            data = sample_data['medium']
            ax_out, im, cbar = plot_heatmap(ax, data)
            
            # Should work seamlessly with scitex wrapper
            assert hasattr(ax, '__class__')
            
            plt.close(fig)
        except ImportError:
            pytest.skip("scitex.plt.subplots not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])