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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/metrics/silhoute_score_block.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-20 00:22:25 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/silhoute_score_block.py
# 
# THIS_FILE = "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/silhoute_score_block.py"
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-03 03:03:13 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/silhoute_score_block.py
# 
# # https://gist.github.com/AlexandreAbraham/5544803
# 
# """ Unsupervised evaluation metrics. """
# 
# # License: BSD Style.
# 
# from itertools import combinations as _combinations
# 
# import numpy as _np
# 
# # from sklearn.externals.joblib import Parallel, delayed
# from joblib import Parallel as _Parallel
# from joblib import delayed as _delayed
# from sklearn.metrics.pairwise import distance_metrics as _distance_metrics
# from sklearn.metrics.pairwise import pairwise_distances as _pairwise_distances
# from sklearn.utils import check_random_state as _check_random_state
# 
# 
# def silhouette_score_slow(
#     X, labels, metric="euclidean", sample_size=None, random_state=None, **kwds
# ):
#     """Compute the mean Silhouette Coefficient of all samples.
# 
#     This method is computationally expensive compared to the reference one.
# 
#     The Silhouette Coefficient is calculated using the mean intra-cluster
#     distance (a) and the mean nearest-cluster distance (b) for each sample.
#     The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
#     To clarrify, b is the distance between a sample and the nearest cluster
#     that b is not a part of.
# 
#     This function returns the mean Silhoeutte Coefficient over all samples.
#     To obtain the values for each sample, use silhouette_samples
# 
#     The best value is 1 and the worst value is -1. Values near 0 indicate
#     overlapping clusters. Negative values genly indicate that a sample has
#     been assigned to the wrong cluster, as a different cluster is more similar.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#         label values for each sample
# 
#     metric : string, or callable
#         The metric to use when calculating distance between instances in a
#         feature array. If metric is a string, it must be one of the options
#         allowed by metrics.pairwise._pairwise_distances. If X is the distance
#         array itself, use "precomputed" as the metric.
# 
#     sample_size : int or None
#         The size of the sample to use when computing the Silhouette
#         Coefficient. If sample_size is None, no sampling is used.
# 
#     random_state : integer or numpy.RandomState, optional
#         The generator used to initialize the centers. If an integer is
#         given, it fixes the seed. Defaults to the global numpy random
#         number generator.
# 
#     `**kwds` : optional keyword parameters
#         Any further parameters are passed directly to the distance function.
#         If using a scipy.spatial.distance metric, the parameters are still
#         metric dependent. See the scipy docs for usage examples.
# 
#     Returns
#     -------
#     silhouette : float
#         Mean Silhouette Coefficient for all samples.
# 
#     References
#     ----------
# 
#     Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
#         Interpretation and Validation of Cluster Analysis". Computational
#         and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.
# 
#     http://en.wikipedia.org/wiki/Silhouette_(clustering)
# 
#     """
#     if sample_size is not None:
#         random_state = _check_random_state(random_state)
#         indices = random_state.permutation(X.shape[0])[:sample_size]
#         if metric == "precomputed":
#             raise ValueError("Distance matrix cannot be precomputed")
#         else:
#             X, labels = X[indices], labels[indices]
#     return _np.mean(silhouette_samples_slow(X, labels, metric=metric, **kwds))
# 
# 
# def silhouette_samples_slow(X, labels, metric="euclidean", **kwds):
#     """Compute the Silhouette Coefficient for each sample.
# 
#     The Silhoeutte Coefficient is a measure of how well samples are clustered
#     with samples that are similar to themselves. Clustering models with a high
#     Silhouette Coefficient are said to be dense, where samples in the same
#     cluster are similar to each other, and well separated, where samples in
#     different clusters are not very similar to each other.
# 
#     The Silhouette Coefficient is calculated using the mean intra-cluster
#     distance (a) and the mean nearest-cluster distance (b) for each sample.
#     The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
# 
#     This function returns the Silhoeutte Coefficient for each sample.
# 
#     The best value is 1 and the worst value is -1. Values near 0 indicate
#     overlapping clusters.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#              label values for each sample
# 
#     metric : string, or callable
#         The metric to use when calculating distance between instances in a
#         feature array. If metric is a string, it must be one of the options
#         allowed by metrics.pairwise._pairwise_distances. If X is the distance
#         array itself, use "precomputed" as the metric.
# 
#     `**kwds` : optional keyword parameters
#         Any further parameters are passed directly to the distance function.
#         If using a scipy.spatial.distance metric, the parameters are still
#         metric dependent. See the scipy docs for usage examples.
# 
#     Returns
#     -------
#     silhouette : array, shape = [n_samples]
#         Silhouette Coefficient for each samples.
# 
#     References
#     ----------
# 
#     Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
#         Interpretation and Validation of Cluster Analysis". Computational
#         and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.
# 
#     http://en.wikipedia.org/wiki/Silhouette_(clustering)
# 
#     """
#     metric = _distance_metrics()[metric]
#     n = labels.shape[0]
#     A = _np.array(
#         [_intra_cluster_distance_slow(X, labels, metric, i) for i in range(n)]
#     )
#     B = _np.array(
#         [_nearest_cluster_distance_slow(X, labels, metric, i) for i in range(n)]
#     )
#     sil_samples = (B - A) / _np.maximum(A, B)
#     # nan values are for clusters of size 1, and should be 0
#     return _np.nan_to_num(sil_samples)
# 
# 
# def _intra_cluster_distance_slow(X, labels, metric, i):
#     """Calculate the mean intra-cluster distance for sample i.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#         label values for each sample
# 
#     metric: function
#         Pairwise metric function
# 
#     i : int
#         Sample index being calculated. It is excluded from calculation and
#         used to determine the current label
# 
#     Returns
#     -------
#     a : float
#         Mean intra-cluster distance for sample i
#     """
#     indices = _np.where(labels == labels[i])[0]
#     if len(indices) == 0:
#         return 0.0
#     a = _np.mean([metric(X[i], X[j]) for j in indices if not i == j])
#     return a
# 
# 
# def _nearest_cluster_distance_slow(X, labels, metric, i):
#     """Calculate the mean nearest-cluster distance for sample i.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#         label values for each sample
# 
#     metric: function
#         Pairwise metric function
# 
#     i : int
#         Sample index being calculated. It is used to determine the current
#         label.
# 
#     Returns
#     -------
#     b : float
#         Mean nearest-cluster distance for sample i
#     """
#     label = labels[i]
#     b = _np.min(
#         [
#             _np.mean([metric(X[i], X[j]) for j in _np.where(labels == cur_label)[0]])
#             for cur_label in set(labels)
#             if not cur_label == label
#         ]
#     )
#     return b
# 
# 
# def silhouette_score_block(
#     X, labels, metric="euclidean", sample_size=None, random_state=None, n_jobs=1, **kwds
# ):
#     """Compute the mean Silhouette Coefficient of all samples.
# 
#     The Silhouette Coefficient is calculated using the mean intra-cluster
#     distance (a) and the mean nearest-cluster distance (b) for each sample.
#     The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
#     To clarrify, b is the distance between a sample and the nearest cluster
#     that b is not a part of.
# 
#     This function returns the mean Silhoeutte Coefficient over all samples.
#     To obtain the values for each sample, use silhouette_samples
# 
#     The best value is 1 and the worst value is -1. Values near 0 indicate
#     overlapping clusters. Negative values genly indicate that a sample has
#     been assigned to the wrong cluster, as a different cluster is more similar.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#              label values for each sample
# 
#     metric : string, or callable
#         The metric to use when calculating distance between instances in a
#         feature array. If metric is a string, it must be one of the options
#         allowed by metrics.pairwise._pairwise_distances. If X is the distance
#         array itself, use "precomputed" as the metric.
# 
#     sample_size : int or None
#         The size of the sample to use when computing the Silhouette
#         Coefficient. If sample_size is None, no sampling is used.
# 
#     random_state : integer or numpy.RandomState, optional
#         The generator used to initialize the centers. If an integer is
#         given, it fixes the seed. Defaults to the global numpy random
#         number generator.
# 
#     `**kwds` : optional keyword parameters
#         Any further parameters are passed directly to the distance function.
#         If using a scipy.spatial.distance metric, the parameters are still
#         metric dependent. See the scipy docs for usage examples.
# 
#     Returns
#     -------
#     silhouette : float
#         Mean Silhouette Coefficient for all samples.
# 
#     References
#     ----------
# 
#     Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
#         Interpretation and Validation of Cluster Analysis". Computational
#         and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.
# 
#     http://en.wikipedia.org/wiki/Silhouette_(clustering)
# 
#     """
#     if sample_size is not None:
#         random_state = _check_random_state(random_state)
#         indices = random_state.permutation(X.shape[0])[:sample_size]
#         if metric == "precomputed":
#             raise ValueError("Distance matrix cannot be precomputed")
#         else:
#             X, labels = X[indices], labels[indices]
#     return _np.mean(
#         silhouette_samples_block(X, labels, metric=metric, n_jobs=n_jobs, **kwds)
#     )
# 
# 
# def silhouette_samples_block(X, labels, metric="euclidean", n_jobs=1, **kwds):
#     """Compute the Silhouette Coefficient for each sample.
# 
#     The Silhoeutte Coefficient is a measure of how well samples are clustered
#     with samples that are similar to themselves. Clustering models with a high
#     Silhouette Coefficient are said to be dense, where samples in the same
#     cluster are similar to each other, and well separated, where samples in
#     different clusters are not very similar to each other.
# 
#     The Silhouette Coefficient is calculated using the mean intra-cluster
#     distance (a) and the mean nearest-cluster distance (b) for each sample.
#     The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
# 
#     This function returns the Silhoeutte Coefficient for each sample.
# 
#     The best value is 1 and the worst value is -1. Values near 0 indicate
#     overlapping clusters.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#              label values for each sample
# 
#     metric : string, or callable
#         The metric to use when calculating distance between instances in a
#         feature array. If metric is a string, it must be one of the options
#         allowed by metrics.pairwise._pairwise_distances. If X is the distance
#         array itself, use "precomputed" as the metric.
# 
#     `**kwds` : optional keyword parameters
#         Any further parameters are passed directly to the distance function.
#         If using a scipy.spatial.distance metric, the parameters are still
#         metric dependent. See the scipy docs for usage examples.
# 
#     Returns
#     -------
#     silhouette : array, shape = [n_samples]
#         Silhouette Coefficient for each samples.
# 
#     References
#     ----------
# 
#     Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
#         Interpretation and Validation of Cluster Analysis". Computational
#         and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.
# 
#     http://en.wikipedia.org/wiki/Silhouette_(clustering)
# 
#     """
#     A = _intra_cluster_distances_block(X, labels, metric, n_jobs=n_jobs, **kwds)
#     B = _nearest_cluster_distance_block(X, labels, metric, n_jobs=n_jobs, **kwds)
#     sil_samples = (B - A) / _np.maximum(A, B)
#     # nan values are for clusters of size 1, and should be 0
#     return _np.nan_to_num(sil_samples)
# 
# 
# def _intra_cluster_distances_block_(subX, metric, **kwds):
#     distances = _pairwise_distances(subX, metric=metric, **kwds)
#     return distances.sum(axis=1) / (distances.shape[0] - 1)
# 
# 
# def _intra_cluster_distances_block(X, labels, metric, n_jobs=1, **kwds):
#     """Calculate the mean intra-cluster distance for sample i.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#         label values for each sample
# 
#     metric : string, or callable
#         The metric to use when calculating distance between instances in a
#         feature array. If metric is a string, it must be one of the options
#         allowed by metrics.pairwise._pairwise_distances. If X is the distance
#         array itself, use "precomputed" as the metric.
# 
#     `**kwds` : optional keyword parameters
#         Any further parameters are passed directly to the distance function.
#         If using a scipy.spatial.distance metric, the parameters are still
#         metric dependent. See the scipy docs for usage examples.
# 
#     Returns
#     -------
#     a : array [n_samples_a]
#         Mean intra-cluster distance
#     """
#     intra_dist = _np.zeros(labels.size, dtype=float)
#     values = _Parallel(n_jobs=n_jobs)(
#         _delayed(_intra_cluster_distances_block_)(
#             X[_np.where(labels == label)[0]], metric, **kwds
#         )
#         for label in _np.unique(labels)
#     )
#     for label, values_ in zip(_np.unique(labels), values):
#         intra_dist[_np.where(labels == label)[0]] = values_
#     return intra_dist
# 
# 
# def _nearest_cluster_distance_block_(subX_a, subX_b, metric, **kwds):
#     dist = _pairwise_distances(subX_a, subX_b, metric=metric, **kwds)
#     dist_a = dist.mean(axis=1)
#     dist_b = dist.mean(axis=0)
#     return dist_a, dist_b
# 
# 
# def _nearest_cluster_distance_block(X, labels, metric, n_jobs=1, **kwds):
#     """Calculate the mean nearest-cluster distance for sample i.
# 
#     Parameters
#     ----------
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     labels : array, shape = [n_samples]
#         label values for each sample
# 
#     metric : string, or callable
#         The metric to use when calculating distance between instances in a
#         feature array. If metric is a string, it must be one of the options
#         allowed by metrics.pairwise._pairwise_distances. If X is the distance
#         array itself, use "precomputed" as the metric.
# 
#     `**kwds` : optional keyword parameters
#         Any further parameters are passed directly to the distance function.
#         If using a scipy.spatial.distance metric, the parameters are still
#         metric dependent. See the scipy docs for usage examples.
#     X : array [n_samples_a, n_features]
#         Feature array.
# 
#     Returns
#     -------
#     b : float
#         Mean nearest-cluster distance for sample i
#     """
#     inter_dist = _np.empty(labels.size, dtype=float)
#     inter_dist.fill(_np.inf)
#     # Compute cluster distance between pairs of clusters
#     unique_labels = _np.unique(labels)
# 
#     values = _Parallel(n_jobs=n_jobs)(
#         _delayed(_nearest_cluster_distance_block_)(
#             X[_np.where(labels == label_a)[0]],
#             X[_np.where(labels == label_b)[0]],
#             metric,
#             **kwds
#         )
#         for label_a, label_b in _combinations(unique_labels, 2)
#     )
# 
#     for (label_a, label_b), (values_a, values_b) in zip(
#         _combinations(unique_labels, 2), values
#     ):
# 
#         indices_a = _np.where(labels == label_a)[0]
#         inter_dist[indices_a] = _np.minimum(values_a, inter_dist[indices_a])
#         del indices_a
#         indices_b = _np.where(labels == label_b)[0]
#         inter_dist[indices_b] = _np.minimum(values_b, inter_dist[indices_b])
#         del indices_b
#     return inter_dist
# 
# 
# if __name__ == "__main__":
#     import time
# 
#     # from sklearn.metrics.cluster.unsupervised import silhouette_score
#     from sklearn.metrics import silhouette_score
# 
#     _np.random.seed(0)
#     X = _np.random.random((10000, 100))
#     y = _np.repeat(_np.arange(100), 100)
#     t0 = time.time()
#     s = silhouette_score(X, y)
#     t = time.time() - t0
#     print("Scikit silhouette (%fs): %f" % (t, s))
#     t0 = time.time()
#     s = silhouette_score_block(X, y)
#     t = time.time() - t0
#     print("Block silhouette (%fs): %f" % (t, s))
#     t0 = time.time()
#     s = silhouette_score_block(X, y, n_jobs=2)
#     t = time.time() - t0
#     print("Block silhouette parallel (%fs): %f" % (t, s))
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/metrics/silhoute_score_block.py
# --------------------------------------------------------------------------------
