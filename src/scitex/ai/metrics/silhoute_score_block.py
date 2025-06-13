#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-20 00:22:25 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/silhoute_score_block.py

THIS_FILE = "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/silhoute_score_block.py"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 03:03:13 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/silhoute_score_block.py

# https://gist.github.com/AlexandreAbraham/5544803

""" Unsupervised evaluation metrics. """

# License: BSD Style.

from itertools import combinations as _combinations

import numpy as _np

# from sklearn.externals.joblib import Parallel, delayed
from joblib import Parallel as _Parallel
from joblib import delayed as _delayed
from sklearn.metrics.pairwise import distance_metrics as _distance_metrics
from sklearn.metrics.pairwise import pairwise_distances as _pairwise_distances
from sklearn.utils import check_random_state as _check_random_state


def silhouette_score_slow(
    X, labels, metric="euclidean", sample_size=None, random_state=None, **kwds
):
    """Compute the mean Silhouette Coefficient of all samples.

    This method is computationally expensive compared to the reference one.

    The Silhouette Coefficient is calculated using the mean intra-cluster
    distance (a) and the mean nearest-cluster distance (b) for each sample.
    The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
    To clarrify, b is the distance between a sample and the nearest cluster
    that b is not a part of.

    This function returns the mean Silhoeutte Coefficient over all samples.
    To obtain the values for each sample, use silhouette_samples

    The best value is 1 and the worst value is -1. Values near 0 indicate
    overlapping clusters. Negative values genly indicate that a sample has
    been assigned to the wrong cluster, as a different cluster is more similar.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
        label values for each sample

    metric : string, or callable
        The metric to use when calculating distance between instances in a
        feature array. If metric is a string, it must be one of the options
        allowed by metrics.pairwise._pairwise_distances. If X is the distance
        array itself, use "precomputed" as the metric.

    sample_size : int or None
        The size of the sample to use when computing the Silhouette
        Coefficient. If sample_size is None, no sampling is used.

    random_state : integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

    `**kwds` : optional keyword parameters
        Any further parameters are passed directly to the distance function.
        If using a scipy.spatial.distance metric, the parameters are still
        metric dependent. See the scipy docs for usage examples.

    Returns
    -------
    silhouette : float
        Mean Silhouette Coefficient for all samples.

    References
    ----------

    Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
        Interpretation and Validation of Cluster Analysis". Computational
        and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.

    http://en.wikipedia.org/wiki/Silhouette_(clustering)

    """
    if sample_size is not None:
        random_state = _check_random_state(random_state)
        indices = random_state.permutation(X.shape[0])[:sample_size]
        if metric == "precomputed":
            raise ValueError("Distance matrix cannot be precomputed")
        else:
            X, labels = X[indices], labels[indices]
    return _np.mean(silhouette_samples_slow(X, labels, metric=metric, **kwds))


def silhouette_samples_slow(X, labels, metric="euclidean", **kwds):
    """Compute the Silhouette Coefficient for each sample.

    The Silhoeutte Coefficient is a measure of how well samples are clustered
    with samples that are similar to themselves. Clustering models with a high
    Silhouette Coefficient are said to be dense, where samples in the same
    cluster are similar to each other, and well separated, where samples in
    different clusters are not very similar to each other.

    The Silhouette Coefficient is calculated using the mean intra-cluster
    distance (a) and the mean nearest-cluster distance (b) for each sample.
    The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.

    This function returns the Silhoeutte Coefficient for each sample.

    The best value is 1 and the worst value is -1. Values near 0 indicate
    overlapping clusters.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
             label values for each sample

    metric : string, or callable
        The metric to use when calculating distance between instances in a
        feature array. If metric is a string, it must be one of the options
        allowed by metrics.pairwise._pairwise_distances. If X is the distance
        array itself, use "precomputed" as the metric.

    `**kwds` : optional keyword parameters
        Any further parameters are passed directly to the distance function.
        If using a scipy.spatial.distance metric, the parameters are still
        metric dependent. See the scipy docs for usage examples.

    Returns
    -------
    silhouette : array, shape = [n_samples]
        Silhouette Coefficient for each samples.

    References
    ----------

    Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
        Interpretation and Validation of Cluster Analysis". Computational
        and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.

    http://en.wikipedia.org/wiki/Silhouette_(clustering)

    """
    metric = _distance_metrics()[metric]
    n = labels.shape[0]
    A = _np.array(
        [_intra_cluster_distance_slow(X, labels, metric, i) for i in range(n)]
    )
    B = _np.array(
        [_nearest_cluster_distance_slow(X, labels, metric, i) for i in range(n)]
    )
    sil_samples = (B - A) / _np.maximum(A, B)
    # nan values are for clusters of size 1, and should be 0
    return _np.nan_to_num(sil_samples)


def _intra_cluster_distance_slow(X, labels, metric, i):
    """Calculate the mean intra-cluster distance for sample i.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
        label values for each sample

    metric: function
        Pairwise metric function

    i : int
        Sample index being calculated. It is excluded from calculation and
        used to determine the current label

    Returns
    -------
    a : float
        Mean intra-cluster distance for sample i
    """
    indices = _np.where(labels == labels[i])[0]
    if len(indices) == 0:
        return 0.0
    a = _np.mean([metric(X[i], X[j]) for j in indices if not i == j])
    return a


def _nearest_cluster_distance_slow(X, labels, metric, i):
    """Calculate the mean nearest-cluster distance for sample i.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
        label values for each sample

    metric: function
        Pairwise metric function

    i : int
        Sample index being calculated. It is used to determine the current
        label.

    Returns
    -------
    b : float
        Mean nearest-cluster distance for sample i
    """
    label = labels[i]
    b = _np.min(
        [
            _np.mean([metric(X[i], X[j]) for j in _np.where(labels == cur_label)[0]])
            for cur_label in set(labels)
            if not cur_label == label
        ]
    )
    return b


def silhouette_score_block(
    X, labels, metric="euclidean", sample_size=None, random_state=None, n_jobs=1, **kwds
):
    """Compute the mean Silhouette Coefficient of all samples.

    The Silhouette Coefficient is calculated using the mean intra-cluster
    distance (a) and the mean nearest-cluster distance (b) for each sample.
    The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.
    To clarrify, b is the distance between a sample and the nearest cluster
    that b is not a part of.

    This function returns the mean Silhoeutte Coefficient over all samples.
    To obtain the values for each sample, use silhouette_samples

    The best value is 1 and the worst value is -1. Values near 0 indicate
    overlapping clusters. Negative values genly indicate that a sample has
    been assigned to the wrong cluster, as a different cluster is more similar.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
             label values for each sample

    metric : string, or callable
        The metric to use when calculating distance between instances in a
        feature array. If metric is a string, it must be one of the options
        allowed by metrics.pairwise._pairwise_distances. If X is the distance
        array itself, use "precomputed" as the metric.

    sample_size : int or None
        The size of the sample to use when computing the Silhouette
        Coefficient. If sample_size is None, no sampling is used.

    random_state : integer or numpy.RandomState, optional
        The generator used to initialize the centers. If an integer is
        given, it fixes the seed. Defaults to the global numpy random
        number generator.

    `**kwds` : optional keyword parameters
        Any further parameters are passed directly to the distance function.
        If using a scipy.spatial.distance metric, the parameters are still
        metric dependent. See the scipy docs for usage examples.

    Returns
    -------
    silhouette : float
        Mean Silhouette Coefficient for all samples.

    References
    ----------

    Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
        Interpretation and Validation of Cluster Analysis". Computational
        and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.

    http://en.wikipedia.org/wiki/Silhouette_(clustering)

    """
    if sample_size is not None:
        random_state = _check_random_state(random_state)
        indices = random_state.permutation(X.shape[0])[:sample_size]
        if metric == "precomputed":
            raise ValueError("Distance matrix cannot be precomputed")
        else:
            X, labels = X[indices], labels[indices]
    return _np.mean(
        silhouette_samples_block(X, labels, metric=metric, n_jobs=n_jobs, **kwds)
    )


def silhouette_samples_block(X, labels, metric="euclidean", n_jobs=1, **kwds):
    """Compute the Silhouette Coefficient for each sample.

    The Silhoeutte Coefficient is a measure of how well samples are clustered
    with samples that are similar to themselves. Clustering models with a high
    Silhouette Coefficient are said to be dense, where samples in the same
    cluster are similar to each other, and well separated, where samples in
    different clusters are not very similar to each other.

    The Silhouette Coefficient is calculated using the mean intra-cluster
    distance (a) and the mean nearest-cluster distance (b) for each sample.
    The Silhouette Coefficient for a sample is ``(b - a) / max(a, b)``.

    This function returns the Silhoeutte Coefficient for each sample.

    The best value is 1 and the worst value is -1. Values near 0 indicate
    overlapping clusters.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
             label values for each sample

    metric : string, or callable
        The metric to use when calculating distance between instances in a
        feature array. If metric is a string, it must be one of the options
        allowed by metrics.pairwise._pairwise_distances. If X is the distance
        array itself, use "precomputed" as the metric.

    `**kwds` : optional keyword parameters
        Any further parameters are passed directly to the distance function.
        If using a scipy.spatial.distance metric, the parameters are still
        metric dependent. See the scipy docs for usage examples.

    Returns
    -------
    silhouette : array, shape = [n_samples]
        Silhouette Coefficient for each samples.

    References
    ----------

    Peter J. Rousseeuw (1987). "Silhouettes: a Graphical Aid to the
        Interpretation and Validation of Cluster Analysis". Computational
        and Applied Mathematics 20: 53-65. doi:10.1016/0377-0427(87)90125-7.

    http://en.wikipedia.org/wiki/Silhouette_(clustering)

    """
    A = _intra_cluster_distances_block(X, labels, metric, n_jobs=n_jobs, **kwds)
    B = _nearest_cluster_distance_block(X, labels, metric, n_jobs=n_jobs, **kwds)
    sil_samples = (B - A) / _np.maximum(A, B)
    # nan values are for clusters of size 1, and should be 0
    return _np.nan_to_num(sil_samples)


def _intra_cluster_distances_block_(subX, metric, **kwds):
    distances = _pairwise_distances(subX, metric=metric, **kwds)
    return distances.sum(axis=1) / (distances.shape[0] - 1)


def _intra_cluster_distances_block(X, labels, metric, n_jobs=1, **kwds):
    """Calculate the mean intra-cluster distance for sample i.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
        label values for each sample

    metric : string, or callable
        The metric to use when calculating distance between instances in a
        feature array. If metric is a string, it must be one of the options
        allowed by metrics.pairwise._pairwise_distances. If X is the distance
        array itself, use "precomputed" as the metric.

    `**kwds` : optional keyword parameters
        Any further parameters are passed directly to the distance function.
        If using a scipy.spatial.distance metric, the parameters are still
        metric dependent. See the scipy docs for usage examples.

    Returns
    -------
    a : array [n_samples_a]
        Mean intra-cluster distance
    """
    intra_dist = _np.zeros(labels.size, dtype=float)
    values = _Parallel(n_jobs=n_jobs)(
        _delayed(_intra_cluster_distances_block_)(
            X[_np.where(labels == label)[0]], metric, **kwds
        )
        for label in _np.unique(labels)
    )
    for label, values_ in zip(_np.unique(labels), values):
        intra_dist[_np.where(labels == label)[0]] = values_
    return intra_dist


def _nearest_cluster_distance_block_(subX_a, subX_b, metric, **kwds):
    dist = _pairwise_distances(subX_a, subX_b, metric=metric, **kwds)
    dist_a = dist.mean(axis=1)
    dist_b = dist.mean(axis=0)
    return dist_a, dist_b


def _nearest_cluster_distance_block(X, labels, metric, n_jobs=1, **kwds):
    """Calculate the mean nearest-cluster distance for sample i.

    Parameters
    ----------
    X : array [n_samples_a, n_features]
        Feature array.

    labels : array, shape = [n_samples]
        label values for each sample

    metric : string, or callable
        The metric to use when calculating distance between instances in a
        feature array. If metric is a string, it must be one of the options
        allowed by metrics.pairwise._pairwise_distances. If X is the distance
        array itself, use "precomputed" as the metric.

    `**kwds` : optional keyword parameters
        Any further parameters are passed directly to the distance function.
        If using a scipy.spatial.distance metric, the parameters are still
        metric dependent. See the scipy docs for usage examples.
    X : array [n_samples_a, n_features]
        Feature array.

    Returns
    -------
    b : float
        Mean nearest-cluster distance for sample i
    """
    inter_dist = _np.empty(labels.size, dtype=float)
    inter_dist.fill(_np.inf)
    # Compute cluster distance between pairs of clusters
    unique_labels = _np.unique(labels)

    values = _Parallel(n_jobs=n_jobs)(
        _delayed(_nearest_cluster_distance_block_)(
            X[_np.where(labels == label_a)[0]],
            X[_np.where(labels == label_b)[0]],
            metric,
            **kwds
        )
        for label_a, label_b in _combinations(unique_labels, 2)
    )

    for (label_a, label_b), (values_a, values_b) in zip(
        _combinations(unique_labels, 2), values
    ):

        indices_a = _np.where(labels == label_a)[0]
        inter_dist[indices_a] = _np.minimum(values_a, inter_dist[indices_a])
        del indices_a
        indices_b = _np.where(labels == label_b)[0]
        inter_dist[indices_b] = _np.minimum(values_b, inter_dist[indices_b])
        del indices_b
    return inter_dist


if __name__ == "__main__":
    import time

    # from sklearn.metrics.cluster.unsupervised import silhouette_score
    from sklearn.metrics import silhouette_score

    _np.random.seed(0)
    X = _np.random.random((10000, 100))
    y = _np.repeat(_np.arange(100), 100)
    t0 = time.time()
    s = silhouette_score(X, y)
    t = time.time() - t0
    print("Scikit silhouette (%fs): %f" % (t, s))
    t0 = time.time()
    s = silhouette_score_block(X, y)
    t = time.time() - t0
    print("Block silhouette (%fs): %f" % (t, s))
    t0 = time.time()
    s = silhouette_score_block(X, y, n_jobs=2)
    t = time.time() - t0
    print("Block silhouette parallel (%fs): %f" % (t, s))


# EOF
