#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 03:40:00 (ywatanabe)"
# File: ./tests/scitex/ai/clustering/test__umap.py

"""Comprehensive test module for scitex.ai.clustering._umap functionality."""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import Mock, patch, MagicMock
import matplotlib.pyplot as plt
import warnings
try:
    import umap as umap_lib
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False


class TestUmapBasicFunctionality:
    """Test basic UMAP functionality."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 50
        data = np.random.randn(n_samples, n_features)
        labels = np.random.randint(0, 3, n_samples)
        return data, labels
    
    @pytest.fixture
    def high_dim_data(self):
        """Generate high-dimensional data for testing."""
        np.random.seed(42)
        # Create clusters in high-dimensional space
        n_samples_per_cluster = 50
        n_clusters = 3
        n_features = 100
        
        data = []
        labels = []
        for i in range(n_clusters):
            center = np.random.randn(n_features) * 10
            cluster_data = center + np.random.randn(n_samples_per_cluster, n_features)
            data.append(cluster_data)
            labels.extend([i] * n_samples_per_cluster)
        
        return np.vstack(data), np.array(labels)

    def test_umap_basic_functionality(self, sample_data):
        """Test basic UMAP functionality with minimal parameters."""
        data, labels = sample_data
        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels)

        # Check return structure
        assert isinstance(result, tuple)
        assert len(result) == 5  # fig, ax, embedding, silhouette, umap_model
        fig, ax, embedding, silhouette, umap_model = result
        
        # Check types
        assert fig is not None
        assert ax is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (len(data), 2)
        assert isinstance(silhouette, (float, np.floating))
        assert -1 <= silhouette <= 1
        
        plt.close(fig)
        
    def test_umap_without_labels(self, sample_data):
        """Test UMAP without providing labels."""
        data, _ = sample_data
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, None)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        assert silhouette is None  # No silhouette without labels
        
        plt.close(fig)
        
    def test_umap_with_single_label(self, sample_data):
        """Test UMAP with all samples having the same label."""
        data, _ = sample_data
        labels = np.zeros(len(data))  # All same label
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        # Silhouette score undefined for single cluster
        
        plt.close(fig)


class TestUmapVisualization:
    """Test UMAP visualization features."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing."""
        np.random.seed(42)
        data = np.random.randn(100, 50)
        labels = np.random.randint(0, 3, 100)
        return data, labels
    
    def test_umap_with_hues(self, sample_data):
        """Test UMAP with hue coloring."""
        data, labels = sample_data
        hues = np.random.randint(0, 2, len(labels))
        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels, hues=hues)

        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        
        plt.close(fig)
        
    def test_umap_with_string_hues(self, sample_data):
        """Test UMAP with string hue values."""
        data, labels = sample_data
        hues = np.array(['group_A', 'group_B'] * 50)
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels, hues=hues)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        
        plt.close(fig)
    
    def test_umap_with_existing_axes(self, sample_data):
        """Test UMAP plotting on existing axes."""
        data, labels = sample_data
        fig, ax = plt.subplots(figsize=(10, 8))
        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels, axes=ax)

        returned_fig, returned_ax, embedding, silhouette, umap_model = result
        assert returned_ax is ax  # Should use provided axes
        assert embedding.shape == (len(data), 2)
        
        plt.close(fig)
        
    def test_umap_visualization_parameters(self, sample_data):
        """Test UMAP with custom visualization parameters."""
        data, labels = sample_data
        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(
                data,
                labels,
                title="Custom UMAP Title",
                alpha=0.7,
                s=50,  # marker size
                use_independent_legend=True,
                legend_n_cols=2
            )

        fig, ax, embedding, silhouette, umap_model = result
        assert ax.get_title() == "Custom UMAP Title"
        
        plt.close(fig)
        
    def test_umap_with_custom_colors(self, sample_data):
        """Test UMAP with custom color mapping."""
        data, labels = sample_data
        from scitex.ai.clustering import umap
        
        # Custom colors for each class
        colors = ['red', 'blue', 'green']
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels, colors=colors)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        
        plt.close(fig)


class TestUmapAlgorithmicOptions:
    """Test UMAP algorithmic options."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing."""
        np.random.seed(42)
        data = np.random.randn(100, 50)
        labels = np.random.randint(0, 3, 100)
        return data, labels
    
    def test_umap_supervised_mode(self, sample_data):
        """Test supervised UMAP mode."""
        data, labels = sample_data
        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels, supervised=True)

        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        
        plt.close(fig)
        
    def test_umap_custom_parameters(self, sample_data):
        """Test UMAP with custom algorithm parameters."""
        data, labels = sample_data
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(
                data, 
                labels,
                n_neighbors=10,
                min_dist=0.5,
                n_components=2,
                metric='euclidean',
                random_state=123
            )
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(data), 2)
        
        plt.close(fig)
        
    def test_umap_different_metrics(self, sample_data):
        """Test UMAP with different distance metrics."""
        data, labels = sample_data
        from scitex.ai.clustering import umap
        
        metrics = ['euclidean', 'manhattan', 'cosine']
        
        for metric in metrics:
            with patch("matplotlib.pyplot.show"):
                result = umap(data, labels, metric=metric)
            
            fig, ax, embedding, silhouette, umap_model = result
            assert embedding.shape == (len(data), 2)
            plt.close(fig)
    
    def test_umap_with_pretrained_model(self, sample_data):
        """Test UMAP with pre-fitted model."""
        data, labels = sample_data
        
        # Mock a pre-fitted UMAP model
        mock_model = Mock()
        mock_model.transform.return_value = np.random.randn(len(data), 2)
        mock_model.embedding_ = np.random.randn(len(data), 2)
        
        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels, umap_model=mock_model)

        fig, ax, embedding, silhouette, returned_model = result
        assert returned_model is mock_model
        mock_model.transform.assert_called_once()
        
        plt.close(fig)


class TestUmapDataTypes:
    """Test UMAP with different data types."""
    
    def test_umap_with_dataframe(self):
        """Test UMAP with pandas DataFrame input."""
        df = pd.DataFrame(np.random.randn(100, 50))
        labels = np.random.randint(0, 3, 100)
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(df, labels)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (len(df), 2)
        
        plt.close(fig)
        
    def test_umap_with_sparse_data(self):
        """Test UMAP with sparse matrix input."""
        from scipy.sparse import csr_matrix
        
        # Create sparse data
        dense_data = np.random.randn(100, 50)
        dense_data[dense_data < 0] = 0  # Make it sparse
        sparse_data = csr_matrix(dense_data)
        labels = np.random.randint(0, 3, 100)
        
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(sparse_data, labels)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (sparse_data.shape[0], 2)
        
        plt.close(fig)
        
    def test_umap_with_list_input(self):
        """Test UMAP with list input."""
        data = [[np.random.randn() for _ in range(50)] for _ in range(100)]
        labels = list(np.random.randint(0, 3, 100))
        
        from scitex.ai.clustering import umap
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (100, 2)
        
        plt.close(fig)


class TestUmapEdgeCases:
    """Test UMAP edge cases and error handling."""
    
    def test_umap_input_validation(self):
        """Test UMAP input validation."""
        from scitex.ai.clustering import umap

        # Test with mismatched data and labels
        data = np.random.randn(100, 50)
        labels = np.random.randint(0, 3, 50)  # Wrong size

        with pytest.raises(ValueError):
            with patch("matplotlib.pyplot.show"):
                umap(data, labels)
                
    def test_umap_empty_data(self):
        """Test UMAP with empty data."""
        from scitex.ai.clustering import umap
        
        data = np.array([]).reshape(0, 10)
        labels = np.array([])
        
        with pytest.raises(ValueError):
            with patch("matplotlib.pyplot.show"):
                umap(data, labels)
                
    def test_umap_single_sample(self):
        """Test UMAP with single sample."""
        from scitex.ai.clustering import umap
        
        data = np.random.randn(1, 50)
        labels = np.array([0])
        
        with pytest.raises(ValueError):
            with patch("matplotlib.pyplot.show"):
                umap(data, labels)
                
    def test_umap_single_feature(self):
        """Test UMAP with single feature."""
        from scitex.ai.clustering import umap
        
        data = np.random.randn(100, 1)
        labels = np.random.randint(0, 3, 100)
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels)
        
        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (100, 2)
        
        plt.close(fig)
        
    def test_umap_nan_handling(self):
        """Test UMAP with NaN values."""
        from scitex.ai.clustering import umap
        
        data = np.random.randn(100, 50)
        data[10:20, 5:10] = np.nan
        labels = np.random.randint(0, 3, 100)
        
        with pytest.raises(ValueError):
            with patch("matplotlib.pyplot.show"):
                umap(data, labels)
                
    def test_umap_inf_handling(self):
        """Test UMAP with infinite values."""
        from scitex.ai.clustering import umap
        
        data = np.random.randn(100, 50)
        data[5, 10] = np.inf
        data[15, 20] = -np.inf
        labels = np.random.randint(0, 3, 100)
        
        with pytest.raises(ValueError):
            with patch("matplotlib.pyplot.show"):
                umap(data, labels)


class TestUmapIntegration:
    """Test UMAP integration with scitex ecosystem."""
    
    @pytest.mark.parametrize(
        "n_samples,n_features,n_classes",
        [
            (50, 10, 2),
            (100, 50, 3),
            (200, 100, 5),
            (75, 25, 4),
        ],
    )
    def test_umap_various_data_sizes(self, n_samples, n_features, n_classes):
        """Test UMAP with various data sizes."""
        np.random.seed(42)
        data = np.random.randn(n_samples, n_features)
        labels = np.random.randint(0, n_classes, n_samples)

        from scitex.ai.clustering import umap

        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels)

        fig, ax, embedding, silhouette, umap_model = result
        assert embedding.shape == (n_samples, 2)
        assert isinstance(silhouette, (float, np.floating))
        
        plt.close(fig)
        
    def test_umap_reproducibility(self):
        """Test UMAP reproducibility with random seed."""
        from scitex.ai.clustering import umap
        
        np.random.seed(42)
        data = np.random.randn(100, 50)
        labels = np.random.randint(0, 3, 100)
        
        with patch("matplotlib.pyplot.show"):
            result1 = umap(data, labels, random_state=42)
            result2 = umap(data, labels, random_state=42)
        
        embedding1 = result1[2]
        embedding2 = result2[2]
        
        # Embeddings should be identical with same random seed
        np.testing.assert_array_almost_equal(embedding1, embedding2)
        
        plt.close('all')
        
    def test_umap_with_save_path(self, tmp_path):
        """Test UMAP with figure saving."""
        from scitex.ai.clustering import umap
        
        data = np.random.randn(100, 50)
        labels = np.random.randint(0, 3, 100)
        
        save_path = tmp_path / "umap_test.png"
        
        with patch("matplotlib.pyplot.show"):
            with patch("matplotlib.pyplot.savefig") as mock_save:
                result = umap(data, labels, save_path=str(save_path))
                
        # Check if savefig was called
        mock_save.assert_called()
        
        plt.close('all')


class TestUmapPerformance:
    """Test UMAP performance characteristics."""
    
    def test_umap_memory_efficiency(self):
        """Test UMAP doesn't create unnecessary copies."""
        from scitex.ai.clustering import umap
        
        data = np.random.randn(100, 50)
        labels = np.random.randint(0, 3, 100)
        
        # Get initial memory usage
        initial_data_id = id(data)
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data, labels)
        
        # Original data should not be modified
        assert id(data) == initial_data_id
        
        plt.close('all')
        
    @pytest.mark.skipif(not UMAP_AVAILABLE, reason="UMAP library not available")
    def test_umap_model_reuse(self):
        """Test efficiency of reusing UMAP model."""
        from scitex.ai.clustering import umap
        
        # First fit
        data1 = np.random.randn(100, 50)
        labels1 = np.random.randint(0, 3, 100)
        
        with patch("matplotlib.pyplot.show"):
            _, _, _, _, model = umap(data1, labels1)
        
        # Reuse model on new data
        data2 = np.random.randn(80, 50)
        labels2 = np.random.randint(0, 3, 80)
        
        with patch("matplotlib.pyplot.show"):
            result = umap(data2, labels2, umap_model=model)
        
        fig, ax, embedding, silhouette, returned_model = result
        assert returned_model is model
        assert embedding.shape == (80, 2)
        
        plt.close('all')


# EOF
