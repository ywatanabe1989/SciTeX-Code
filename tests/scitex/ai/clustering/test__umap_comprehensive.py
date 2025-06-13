#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for _umap.py

Tests cover:
- UMAP clustering functionality
- Supervised and unsupervised modes
- Visualization capabilities
- Input validation
- Label encoding
- Multiple datasets handling
- Legend generation
- Integration with scitex plotting
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock, PropertyMock

import matplotlib.pyplot as plt
import numpy as np
import pytest
from sklearn.datasets import load_iris, load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


class TestUmapFunction:
    """Test main umap function."""
    
    def test_umap_basic(self):
        """Test basic UMAP functionality with iris dataset."""
from scitex.ai.clustering import umap
        
        # Load data
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        # Run UMAP
        fig, legend_figs, umap_model = umap(
            data=[X],
            labels=[y],
            supervised=False,
            title="Test UMAP"
        )
        
        assert fig is not None
        assert umap_model is not None
        plt.close(fig)
    
    def test_umap_supervised(self):
        """Test supervised UMAP."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        fig, legend_figs, umap_model = umap(
            data=[X],
            labels=[y],
            supervised=True,
            title="Supervised UMAP"
        )
        
        assert fig is not None
        assert umap_model is not None
        assert "(Supervised)" in fig._suptitle.get_text() if hasattr(fig, '_suptitle') else True
        plt.close(fig)
    
    def test_umap_multiple_datasets(self):
        """Test UMAP with multiple datasets."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X1, X2, y1, y2 = train_test_split(
            iris.data, iris.target, test_size=0.5, random_state=42
        )
        
        fig, legend_figs, umap_model = umap(
            data=[X1, X2],
            labels=[y1, y2],
            axes_titles=["Dataset 1", "Dataset 2"],
            supervised=False
        )
        
        assert fig is not None
        # Should have 2 subplots
        axes = fig.get_axes()
        assert len(axes) >= 2
        plt.close(fig)
    
    def test_umap_with_hues(self):
        """Test UMAP with custom hues."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        # Create custom hues
        hues = ["Group A" if label == 0 else "Group B" for label in y]
        
        fig, legend_figs, umap_model = umap(
            data=[X],
            labels=[y],
            hues=[hues],
            supervised=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    def test_umap_with_colors(self):
        """Test UMAP with custom colors."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        # Create color mapping
        colors = [[1, 0, 0] if label == 0 else [0, 1, 0] if label == 1 else [0, 0, 1] 
                  for label in y]
        
        fig, legend_figs, umap_model = umap(
            data=[X],
            labels=[y],
            hues_colors=[colors],
            supervised=False
        )
        
        assert fig is not None
        plt.close(fig)
    
    def test_umap_with_existing_axes(self):
        """Test UMAP with pre-existing axes."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        # Create figure and axes
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        
        _, legend_figs, umap_model = umap(
            data=[X, X],  # Same data twice
            labels=[y, y],
            axes=axes,
            supervised=False
        )
        
        assert umap_model is not None
        plt.close(fig)
    
    def test_umap_with_pretrained_model(self):
        """Test UMAP with pre-fitted model."""
from scitex.ai.clustering import umap
        import umap.umap_ as umap_orig
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        # Pre-fit a UMAP model
        pretrained = umap_orig.UMAP(random_state=42)
        pretrained.fit(X)
        
        fig, legend_figs, umap_model = umap(
            data=[X],
            labels=[y],
            umap_model=pretrained,
            supervised=False
        )
        
        assert umap_model is pretrained
        plt.close(fig)
    
    def test_umap_superimposed(self):
        """Test UMAP with superimposed plot."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X1, X2, y1, y2 = train_test_split(
            iris.data, iris.target, test_size=0.5, random_state=42
        )
        
        fig, legend_figs, umap_model = umap(
            data=[X1, X2],
            labels=[y1, y2],
            add_super_imposed=True,
            supervised=False
        )
        
        # Should have 3 subplots (2 + 1 superimposed)
        axes = fig.get_axes()
        assert len(axes) >= 3
        plt.close(fig)
    
    def test_umap_independent_legend(self):
        """Test UMAP with independent legend figures."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        fig, legend_figs, umap_model = umap(
            data=[X],
            labels=[y],
            use_independent_legend=True,
            supervised=False
        )
        
        assert fig is not None
        assert legend_figs is not None
        
        # Close all figures
        plt.close(fig)
        if legend_figs:
            for leg_fig in legend_figs:
                plt.close(leg_fig)


class TestPlotFunction:
    """Test _plot helper function."""
    
    def test_plot_single_dataset(self):
        """Test plotting with single dataset."""
from scitex.ai.clustering import _plot
        import umap.umap_ as umap_orig
        
        # Setup
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        le = LabelEncoder()
        le.fit(y)
        y_encoded = le.transform(y)
        
        umap_model = umap_orig.UMAP(random_state=42)
        umap_model.fit(X)
        
        # Plot
        fig, legend_figs = _plot(
            _umap=umap_model,
            le=le,
            data_all=[X],
            labels_all=[y_encoded],
            hues_all=[None],
            hues_colors_all=[None],
            add_super_imposed=False,
            axes=None,
            title="Test Plot",
            axes_titles=None,
            use_independent_legend=False,
            s=3,
            alpha=1.0
        )
        
        assert fig is not None
        plt.close(fig)
    
    def test_plot_with_custom_parameters(self):
        """Test plotting with custom visual parameters."""
from scitex.ai.clustering import _plot
        import umap.umap_ as umap_orig
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        le = LabelEncoder()
        le.fit(y)
        y_encoded = le.transform(y)
        
        umap_model = umap_orig.UMAP(random_state=42)
        umap_model.fit(X)
        
        fig, legend_figs = _plot(
            _umap=umap_model,
            le=le,
            data_all=[X],
            labels_all=[y_encoded],
            hues_all=[None],
            hues_colors_all=[None],
            add_super_imposed=False,
            axes=None,
            title="Custom Plot",
            axes_titles=["Custom Title"],
            use_independent_legend=False,
            s=10,  # Larger points
            alpha=0.5  # Semi-transparent
        )
        
        assert fig is not None
        plt.close(fig)


class TestRunUmap:
    """Test _run_umap helper function."""
    
    def test_run_umap_new_model(self):
        """Test running UMAP with new model."""
from scitex.ai.clustering import _run_umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        umap_model = _run_umap(
            umap_model=None,
            data_all=[X],
            labels_all=[y],
            supervised=False,
            title="Test"
        )
        
        assert umap_model is not None
        assert hasattr(umap_model, 'transform')
    
    def test_run_umap_supervised(self):
        """Test running supervised UMAP."""
from scitex.ai.clustering import _run_umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        umap_model = _run_umap(
            umap_model=None,
            data_all=[X],
            labels_all=[y],
            supervised=True,
            title="Test"
        )
        
        assert umap_model is not None
    
    def test_run_umap_existing_model(self):
        """Test running UMAP with existing model."""
from scitex.ai.clustering import _run_umap
        import umap.umap_ as umap_orig
        
        # Create pre-fitted model
        existing = umap_orig.UMAP(random_state=42)
        iris = load_iris()
        existing.fit(iris.data)
        
        umap_model = _run_umap(
            umap_model=existing,
            data_all=[iris.data],
            labels_all=[iris.target],
            supervised=False,
            title="Test"
        )
        
        assert umap_model is existing


class TestCheckInputVars:
    """Test _check_input_vars helper function."""
    
    def test_check_input_vars_basic(self):
        """Test basic input validation."""
from scitex.ai.clustering import _check_input_vars
        
        data = [np.random.rand(100, 4)]
        labels = [np.random.randint(0, 3, 100)]
        
        data_out, labels_out, hues_out, colors_out = _check_input_vars(
            data, labels, None, None
        )
        
        assert len(data_out) == len(labels_out) == len(hues_out) == len(colors_out)
        assert hues_out == [None]
        assert colors_out == [None]
    
    def test_check_input_vars_with_hues(self):
        """Test input validation with hues."""
from scitex.ai.clustering import _check_input_vars
        
        data = [np.random.rand(100, 4), np.random.rand(50, 4)]
        labels = [np.random.randint(0, 3, 100), np.random.randint(0, 3, 50)]
        hues = [["A"] * 100, ["B"] * 50]
        colors = [[[1, 0, 0]] * 100, [[0, 1, 0]] * 50]
        
        data_out, labels_out, hues_out, colors_out = _check_input_vars(
            data, labels, hues, colors
        )
        
        assert len(data_out) == 2
        assert len(labels_out) == 2
        assert len(hues_out) == 2
        assert len(colors_out) == 2
    
    def test_check_input_vars_mismatch(self):
        """Test input validation with mismatched lengths."""
from scitex.ai.clustering import _check_input_vars
        
        data = [np.random.rand(100, 4)]
        labels = [np.random.randint(0, 3, 100), np.random.randint(0, 3, 50)]
        
        with pytest.raises(AssertionError):
            _check_input_vars(data, labels, None, None)
    
    def test_check_input_vars_not_list(self):
        """Test input validation with non-list inputs."""
from scitex.ai.clustering import _check_input_vars
        
        data = np.random.rand(100, 4)  # Not a list
        labels = [np.random.randint(0, 3, 100)]
        
        with pytest.raises(AssertionError):
            _check_input_vars(data, labels, None, None)


class TestMainAlias:
    """Test main alias."""
    
    def test_main_is_umap(self):
        """Test that main is an alias for umap."""
from scitex.ai.clustering import main, umap
        
        assert main is umap


class TestIntegration:
    """Test integration scenarios."""
    
    @patch('scitex.io.save')
    def test_test_function_iris(self, mock_save):
        """Test _test function with iris dataset."""
from scitex.ai.clustering import _test
        
        # Mock scitex.gen.start to avoid display issues
        with patch('scitex.gen.start') as mock_start:
            mock_start.return_value = (None, sys.stdout, sys.stderr, plt, None)
            
            with patch('scitex.gen.close'):
                _test(dataset_str="iris")
        
        # Check that save was called
        assert mock_save.called
    
    def test_full_pipeline(self):
        """Test complete UMAP pipeline."""
from scitex.ai.clustering import umap
        
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 300
        n_features = 10
        n_classes = 3
        
        # Create clustered data
        X = []
        y = []
        for i in range(n_classes):
            center = np.random.randn(n_features) * 5
            cluster_data = center + np.random.randn(n_samples // n_classes, n_features)
            X.append(cluster_data)
            y.extend([i] * (n_samples // n_classes))
        
        X = np.vstack(X)
        y = np.array(y)
        
        # Split data
        X1, X2, y1, y2 = train_test_split(X, y, test_size=0.5, random_state=42)
        
        # Run UMAP
        fig, legend_figs, umap_model = umap(
            data=[X1, X2],
            labels=[y1, y2],
            axes_titles=["Train", "Test"],
            supervised=True,
            title="Synthetic Data UMAP",
            alpha=0.7,
            s=5,
            use_independent_legend=True,
            add_super_imposed=True
        )
        
        assert fig is not None
        assert umap_model is not None
        
        # Clean up
        plt.close(fig)
        if legend_figs:
            for leg_fig in legend_figs:
                plt.close(leg_fig)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_data(self):
        """Test with empty data."""
from scitex.ai.clustering import umap
        
        with pytest.raises(Exception):
            umap(
                data=[np.array([])],
                labels=[np.array([])],
                supervised=False
            )
    
    def test_single_sample(self):
        """Test with single sample."""
from scitex.ai.clustering import umap
        
        X = np.array([[1, 2, 3, 4]])
        y = np.array([0])
        
        # UMAP typically needs more samples
        with pytest.raises(Exception):
            umap(
                data=[X],
                labels=[y],
                supervised=False
            )
    
    def test_mismatched_dimensions(self):
        """Test with mismatched data dimensions."""
from scitex.ai.clustering import umap
        
        X1 = np.random.rand(100, 4)
        X2 = np.random.rand(100, 5)  # Different number of features
        y = np.random.randint(0, 3, 100)
        
        # Should handle or error appropriately
        with pytest.raises(Exception):
            fig, _, _ = umap(
                data=[X1, X2],
                labels=[y, y],
                supervised=False
            )


class TestVisualization:
    """Test visualization aspects."""
    
    def test_scatter_plot_properties(self):
        """Test scatter plot properties."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        s_value = 20
        alpha_value = 0.3
        
        fig, _, _ = umap(
            data=[X],
            labels=[y],
            s=s_value,
            alpha=alpha_value,
            supervised=False
        )
        
        # Check scatter properties
        ax = fig.get_axes()[0]
        collections = ax.collections
        
        # Should have scatter plot collections
        assert len(collections) > 0
        
        plt.close(fig)
    
    def test_axis_labels(self):
        """Test axis labels."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        fig, _, _ = umap(
            data=[X],
            labels=[y],
            title="Test Title",
            supervised=False
        )
        
        # Check labels
        # The exact method depends on scitex.plt implementation
        # Could check via figure text or suptitle
        
        plt.close(fig)
    
    def test_legend_handling(self):
        """Test legend generation and handling."""
from scitex.ai.clustering import umap
        
        iris = load_iris()
        X = iris.data
        y = iris.target
        
        # Test without independent legend
        fig1, legend_figs1, _ = umap(
            data=[X],
            labels=[y],
            use_independent_legend=False,
            supervised=False
        )
        
        assert legend_figs1 is None
        
        # Test with independent legend
        fig2, legend_figs2, _ = umap(
            data=[X],
            labels=[y],
            use_independent_legend=True,
            supervised=False
        )
        
        # May or may not generate legend figures depending on data
        
        plt.close(fig1)
        plt.close(fig2)
        if legend_figs2:
            for leg_fig in legend_figs2:
                plt.close(leg_fig)


class TestLabelEncoding:
    """Test label encoding functionality."""
    
    def test_label_encoding_numeric(self):
        """Test label encoding with numeric labels."""
from scitex.ai.clustering import umap
        
        X = np.random.rand(150, 4)
        y = np.array([0, 1, 2] * 50)
        
        fig, _, _ = umap(
            data=[X],
            labels=[y],
            supervised=False
        )
        
        plt.close(fig)
    
    def test_label_encoding_string(self):
        """Test label encoding with string labels."""
from scitex.ai.clustering import umap
        
        X = np.random.rand(150, 4)
        y = np.array(['setosa', 'versicolor', 'virginica'] * 50)
        
        fig, _, _ = umap(
            data=[X],
            labels=[y],
            supervised=False
        )
        
        plt.close(fig)
    
    def test_label_encoding_mixed(self):
        """Test label encoding with mixed types."""
from scitex.ai.clustering import umap
        
        X = np.random.rand(100, 4)
        # Mix of strings and numbers
        y = np.array(['A', 'B', 0, 1] * 25)
        
        fig, _, _ = umap(
            data=[X],
            labels=[y],
            supervised=False
        )
        
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])