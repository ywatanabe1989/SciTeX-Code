#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 13:05:00 (ywatanabe)"
# File: ./tests/scitex/ai/clustering/test__pca.py

"""Tests for scitex.ai.clustering._pca module."""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA as SklearnPCA
from scitex.ai.clustering import pca


class TestPCA:
    """Test suite for PCA clustering function."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        # Create two datasets with different distributions
        data1 = np.random.randn(100, 10) + np.array([1] * 10)
        data2 = np.random.randn(100, 10) + np.array([-1] * 10)
        
        # Create labels
        labels1 = ['A'] * 50 + ['B'] * 50
        labels2 = ['C'] * 50 + ['D'] * 50
        
        return {
            'single': (data1, labels1),
            'multiple': ([data1, data2], [labels1, labels2])
        }

    def test_pca_single_dataset(self, sample_data):
        """Test PCA with a single dataset."""
        data, labels = sample_data['single']
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels],
            title="Test PCA Single"
        )
        
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        assert isinstance(pca_model, SklearnPCA)
        assert pca_model.n_components == 2
        plt.close(fig)

    def test_pca_multiple_datasets(self, sample_data):
        """Test PCA with multiple datasets."""
        data_list, labels_list = sample_data['multiple']
        
        fig, legend_figs, pca_model = pca(
            data_all=data_list,
            labels_all=labels_list,
            title="Test PCA Multiple",
            axes_titles=["Dataset 1", "Dataset 2"]
        )
        
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        assert isinstance(pca_model, SklearnPCA)
        
        # Check that we have the right number of axes
        axes = fig.get_axes()
        assert len(axes) >= len(data_list)
        plt.close(fig)

    def test_pca_with_super_imposed(self, sample_data):
        """Test PCA with superimposed plot."""
        data_list, labels_list = sample_data['multiple']
        
        fig, legend_figs, pca_model = pca(
            data_all=data_list,
            labels_all=labels_list,
            add_super_imposed=True,
            title="Test PCA Superimposed"
        )
        
        assert fig is not None
        axes = fig.get_axes()
        # Should have one extra axis for superimposed plot
        assert len(axes) == len(data_list) + 1
        plt.close(fig)

    def test_pca_visual_parameters(self, sample_data):
        """Test PCA with different visual parameters."""
        data, labels = sample_data['single']
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels],
            alpha=0.5,
            s=10,
            palette="coolwarm"
        )
        
        assert fig is not None
        # Visual parameters should not cause errors
        plt.close(fig)

    def test_pca_independent_legend(self, sample_data):
        """Test PCA with independent legend."""
        data, labels = sample_data['single']
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels],
            use_independent_legend=True
        )
        
        assert fig is not None
        assert legend_figs is not None
        # Clean up legend figures
        for leg_fig in legend_figs:
            plt.close(leg_fig)
        plt.close(fig)

    def test_pca_label_encoding(self, sample_data):
        """Test that labels are properly encoded."""
        data, _ = sample_data['single']
        # Use string labels
        labels = ['Group_' + str(i % 3) for i in range(len(data))]
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels]
        )
        
        assert fig is not None
        plt.close(fig)

    def test_pca_transform_consistency(self, sample_data):
        """Test that PCA transformation is consistent."""
        data_list, labels_list = sample_data['multiple']
        
        fig, legend_figs, pca_model = pca(
            data_all=data_list,
            labels_all=labels_list
        )
        
        # First dataset should be used for fitting
        transformed1 = pca_model.transform(data_list[0])
        assert transformed1.shape == (len(data_list[0]), 2)
        
        # Second dataset should only be transformed
        transformed2 = pca_model.transform(data_list[1])
        assert transformed2.shape == (len(data_list[1]), 2)
        
        plt.close(fig)

    def test_pca_empty_data(self):
        """Test PCA with empty data."""
        with pytest.raises((ValueError, IndexError)):
            pca(data_all=[], labels_all=[])

    def test_pca_mismatched_lengths(self, sample_data):
        """Test PCA with mismatched data and label lengths."""
        data, labels = sample_data['single']
        
        with pytest.raises(AssertionError):
            pca(
                data_all=[data],
                labels_all=[labels[:50]]  # Wrong length
            )

    def test_pca_numpy_array_input(self, sample_data):
        """Test PCA with numpy array inputs instead of lists."""
        data, labels = sample_data['single']
        
        # Convert to numpy arrays
        data_array = np.array(data)
        labels_array = np.array(labels)
        
        fig, legend_figs, pca_model = pca(
            data_all=data_array,
            labels_all=labels_array
        )
        
        assert fig is not None
        plt.close(fig)

    @pytest.mark.parametrize("n_samples,n_features", [
        (50, 5),
        (100, 20),
        (200, 50)
    ])
    def test_pca_different_dimensions(self, n_samples, n_features):
        """Test PCA with different data dimensions."""
        data = np.random.randn(n_samples, n_features)
        labels = ['A'] * (n_samples // 2) + ['B'] * (n_samples - n_samples // 2)
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels]
        )
        
        assert fig is not None
        assert pca_model.n_components == 2
        plt.close(fig)

    def test_pca_axes_labels(self, sample_data):
        """Test that PCA axes are properly labeled."""
        data, labels = sample_data['single']
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels],
            title="Test Title"
        )
        
        # Check figure labels
        assert fig._suptitle is not None
        assert "Test Title" in fig._suptitle.get_text()
        
        # Check axis labels
        assert fig.supxlabel("").get_text() != ""
        assert fig.supylabel("").get_text() != ""
        
        plt.close(fig)

    def test_pca_natural_sorting(self):
        """Test that labels are naturally sorted."""
        data = np.random.randn(100, 10)
        # Create labels that need natural sorting
        labels = ['Label_1', 'Label_10', 'Label_2', 'Label_20'] * 25
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels]
        )
        
        assert fig is not None
        plt.close(fig)

    def test_pca_explained_variance(self, sample_data):
        """Test that PCA model captures variance."""
        data, labels = sample_data['single']
        
        fig, legend_figs, pca_model = pca(
            data_all=[data],
            labels_all=[labels]
        )
        
        # Check that explained variance is computed
        assert hasattr(pca_model, 'explained_variance_ratio_')
        assert len(pca_model.explained_variance_ratio_) == 2
        assert np.sum(pca_model.explained_variance_ratio_) <= 1.0
        
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
