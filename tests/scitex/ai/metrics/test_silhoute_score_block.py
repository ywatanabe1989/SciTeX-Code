#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/metrics/test_silhoute_score_block.py

"""
Comprehensive test suite for the silhouette score block implementation.
Tests parallel computation, various metrics, edge cases, and performance.
"""

import os
import numpy as np
import pytest
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.datasets import make_blobs
from scitex.ai.metrics.silhoute_score_block import (
    silhouette_score_block,
    silhouette_samples_block,
    silhouette_score_slow,
    silhouette_samples_slow,
    _intra_cluster_distance_slow,
    _nearest_cluster_distance_slow,
    _intra_cluster_distances_block,
    _nearest_cluster_distance_block
)


class TestSilhouetteScoreBlock:
    """Test suite for silhouette score block implementation."""
    
    @pytest.fixture
    def simple_clustered_data(self):
        """Generate simple well-separated clusters."""
        X, y = make_blobs(n_samples=50, n_features=2, centers=3, 
                         cluster_std=0.5, random_state=42)
        return X, y
    
    @pytest.fixture
    def overlapping_clusters(self):
        """Generate overlapping clusters."""
        X, y = make_blobs(n_samples=60, n_features=2, centers=3, 
                         cluster_std=2.0, random_state=42)
        return X, y
    
    def test_silhouette_score_block_basic(self, simple_clustered_data):
        """Test basic functionality of silhouette_score_block."""
        X, labels = simple_clustered_data
        score = silhouette_score_block(X, labels)
        assert -1 <= score <= 1
        assert isinstance(score, float)
    
    def test_consistency_with_sklearn(self, simple_clustered_data):
        """Test consistency with sklearn's silhouette_score."""
        X, labels = simple_clustered_data
        our_score = silhouette_score_block(X, labels)
        sklearn_score = silhouette_score(X, labels)
        # Allow small numerical differences
        assert abs(our_score - sklearn_score) < 0.01
    
    def test_parallel_computation(self, simple_clustered_data):
        """Test parallel computation with different n_jobs."""
        X, labels = simple_clustered_data
        score_serial = silhouette_score_block(X, labels, n_jobs=1)
        score_parallel = silhouette_score_block(X, labels, n_jobs=2)
        # Results should be identical
        assert abs(score_serial - score_parallel) < 1e-10
    
    def test_different_metrics(self, simple_clustered_data):
        """Test with different distance metrics."""
        X, labels = simple_clustered_data
        metrics = ['euclidean', 'manhattan', 'cosine']
        scores = []
        for metric in metrics:
            score = silhouette_score_block(X, labels, metric=metric)
            assert -1 <= score <= 1
            scores.append(score)
        # Different metrics should give different scores
        assert len(set(scores)) > 1
    
    def test_sample_size_parameter(self, simple_clustered_data):
        """Test sampling functionality."""
        X, labels = simple_clustered_data
        # Test with sample size
        score_sampled = silhouette_score_block(X, labels, sample_size=30, random_state=42)
        assert -1 <= score_sampled <= 1
    
    def test_precomputed_metric_error(self):
        """Test error handling for precomputed metric with sampling."""
        X = np.random.rand(50, 50)  # Fake distance matrix
        labels = np.random.randint(0, 3, 50)
        with pytest.raises(ValueError, match="Distance matrix cannot be precomputed"):
            silhouette_score_block(X, labels, metric="precomputed", sample_size=30)
    
    def test_silhouette_samples_block(self, simple_clustered_data):
        """Test silhouette_samples_block function."""
        X, labels = simple_clustered_data
        samples = silhouette_samples_block(X, labels)
        assert len(samples) == len(labels)
        assert np.all(samples >= -1) and np.all(samples <= 1)
    
    def test_single_cluster_edge_case(self):
        """Test with all samples in one cluster."""
        X = np.random.rand(20, 5)
        labels = np.zeros(20, dtype=int)
        score = silhouette_score_block(X, labels)
        # Should return 0 for single cluster
        assert score == 0.0
    
    def test_perfect_clusters(self):
        """Test with perfectly separated clusters."""
        # Create very well separated clusters
        X1 = np.random.randn(20, 2) + [0, 0]
        X2 = np.random.randn(20, 2) + [10, 10]
        X3 = np.random.randn(20, 2) + [-10, -10]
        X = np.vstack([X1, X2, X3])
        labels = np.array([0]*20 + [1]*20 + [2]*20)
        
        score = silhouette_score_block(X, labels)
        # Should be close to 1 for perfect clusters
        assert score > 0.8
    
    def test_slow_vs_block_implementation(self, simple_clustered_data):
        """Test consistency between slow and block implementations."""
        X, labels = simple_clustered_data
        score_slow = silhouette_score_slow(X, labels)
        score_block = silhouette_score_block(X, labels)
        assert abs(score_slow - score_block) < 0.01
    
    def test_intra_cluster_distances(self, simple_clustered_data):
        """Test intra-cluster distance computation."""
        X, labels = simple_clustered_data
        distances = _intra_cluster_distances_block(X, labels, metric='euclidean')
        assert len(distances) == len(labels)
        assert np.all(distances >= 0)
    
    def test_nearest_cluster_distances(self, simple_clustered_data):
        """Test nearest-cluster distance computation."""
        X, labels = simple_clustered_data
        distances = _nearest_cluster_distance_block(X, labels, metric='euclidean')
        assert len(distances) == len(labels)
        assert np.all(distances > 0)
    
    def test_nan_handling(self):
        """Test handling of edge cases that produce NaN."""
        # Single point clusters should produce NaN -> 0
        X = np.array([[0, 0], [1, 1], [2, 2]])
        labels = np.array([0, 1, 2])
        samples = silhouette_samples_block(X, labels)
        # Single point clusters should have silhouette score of 0
        assert np.all(samples == 0)
    
    def test_large_dataset_performance(self):
        """Test performance on larger dataset."""
        X, labels = make_blobs(n_samples=500, n_features=10, centers=5, random_state=42)
        score = silhouette_score_block(X, labels, n_jobs=2)
        assert -1 <= score <= 1
    
    def test_random_state_consistency(self):
        """Test random state produces consistent results."""
        X = np.random.rand(100, 5)
        labels = np.random.randint(0, 3, 100)
        
        score1 = silhouette_score_block(X, labels, sample_size=50, random_state=42)
        score2 = silhouette_score_block(X, labels, sample_size=50, random_state=42)
        assert score1 == score2
    
    def test_different_cluster_sizes(self):
        """Test with very imbalanced cluster sizes."""
        # Create imbalanced clusters
        X1 = np.random.randn(5, 2)
        X2 = np.random.randn(50, 2) + [5, 5]
        X3 = np.random.randn(100, 2) + [-5, -5]
        X = np.vstack([X1, X2, X3])
        labels = np.array([0]*5 + [1]*50 + [2]*100)
        
        score = silhouette_score_block(X, labels)
        assert -1 <= score <= 1
    
    def test_two_clusters_only(self):
        """Test with exactly two clusters."""
        X, labels = make_blobs(n_samples=40, n_features=2, centers=2, random_state=42)
        score = silhouette_score_block(X, labels)
        sklearn_score = silhouette_score(X, labels)
        assert abs(score - sklearn_score) < 0.01
    
    def test_high_dimensional_data(self):
        """Test with high-dimensional data."""
        X, labels = make_blobs(n_samples=50, n_features=50, centers=3, random_state=42)
        score = silhouette_score_block(X, labels)
        assert -1 <= score <= 1
    
    def test_overlapping_clusters_low_score(self, overlapping_clusters):
        """Test that overlapping clusters produce lower scores."""
        X, labels = overlapping_clusters
        score = silhouette_score_block(X, labels)
        # Overlapping clusters should have lower score
        assert score < 0.5


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
