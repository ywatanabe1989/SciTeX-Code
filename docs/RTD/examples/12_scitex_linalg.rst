12 SciTeX Linalg
================

.. note::
   This page is generated from the Jupyter notebook `12_scitex_linalg.ipynb <https://github.com/scitex/scitex/blob/main/examples/12_scitex_linalg.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 12_scitex_linalg.ipynb


This notebook demonstrates the complete functionality of the
``scitex.linalg`` module, which provides linear algebra utilities for
scientific computing.

Module Overview
---------------

The ``scitex.linalg`` module includes: - Distance calculations
(Euclidean, various distance metrics) - Geometric median computation -
Miscellaneous linear algebra utilities (cosine similarity, norms, vector
operations) - Coordinate transformations

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import numpy as np
    import torch
    import matplotlib.pyplot as plt
    
    # Import scitex linalg module
    import scitex.linalg as linalg
    
    # Set random seed for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    print("Available functions in scitex.linalg:")
    print([attr for attr in dir(linalg) if not attr.startswith('_')])

1. Distance Calculations
------------------------

Euclidean Distance
~~~~~~~~~~~~~~~~~~

The ``euclidean_distance`` function computes Euclidean distances between
arrays along specified axes.

.. code:: ipython3

    # Example 1: Basic Euclidean distance between two vectors
    v1 = np.array([1, 2, 3])
    v2 = np.array([4, 5, 6])
    
    dist = linalg.euclidean_distance(v1, v2)
    print(f"Euclidean distance between {v1} and {v2}: {dist:.4f}")
    
    # Verify with manual calculation
    manual_dist = np.sqrt(np.sum((v1 - v2)**2))
    print(f"Manual calculation: {manual_dist:.4f}")
    print(f"Match: {np.isclose(dist, manual_dist)}")

.. code:: ipython3

    # Example 2: Euclidean distance along different axes
    # Create a 3D array representing multiple vectors
    data = np.random.randn(4, 3, 5)  # 4 time points, 3 features, 5 samples
    reference = np.random.randn(4, 3, 5)
    
    # Distance along axis 0 (time axis)
    dist_axis0 = linalg.euclidean_distance(data, reference, axis=0)
    print(f"Distance along axis 0 shape: {dist_axis0.shape}")
    
    # Distance along axis 1 (feature axis)
    dist_axis1 = linalg.euclidean_distance(data, reference, axis=1)
    print(f"Distance along axis 1 shape: {dist_axis1.shape}")
    
    # Distance along axis 2 (sample axis)
    dist_axis2 = linalg.euclidean_distance(data, reference, axis=2)
    print(f"Distance along axis 2 shape: {dist_axis2.shape}")

Comprehensive Distance Metrics with cdist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``cdist`` function provides access to various distance metrics
through scipy’s distance module.

.. code:: ipython3

    # Example 3: Using cdist for multiple distance metrics
    # Generate sample data points
    X = np.random.randn(5, 3)  # 5 points in 3D space
    Y = np.random.randn(4, 3)  # 4 points in 3D space
    
    print("Sample data points:")
    print(f"X shape: {X.shape}")
    print(f"Y shape: {Y.shape}")
    
    # Euclidean distance matrix
    dist_euclidean = linalg.cdist(X, Y, 'euclidean')
    print(f"\nEuclidean distance matrix shape: {dist_euclidean.shape}")
    print(f"Euclidean distances:\n{dist_euclidean}")
    
    # Manhattan distance
    dist_manhattan = linalg.cdist(X, Y, 'cityblock')
    print(f"\nManhattan distance matrix shape: {dist_manhattan.shape}")
    print(f"Manhattan distances:\n{dist_manhattan}")
    
    # Cosine distance
    dist_cosine = linalg.cdist(X, Y, 'cosine')
    print(f"\nCosine distance matrix shape: {dist_cosine.shape}")
    print(f"Cosine distances:\n{dist_cosine}")

Alias: edist
~~~~~~~~~~~~

The ``edist`` function is an alias for ``euclidean_distance``.

.. code:: ipython3

    # Example 4: Using edist (alias for euclidean_distance)
    v1 = np.array([0, 0, 0])
    v2 = np.array([3, 4, 5])
    
    dist1 = linalg.euclidean_distance(v1, v2)
    dist2 = linalg.edist(v1, v2)
    
    print(f"euclidean_distance result: {dist1:.4f}")
    print(f"edist result: {dist2:.4f}")
    print(f"Results match: {np.isclose(dist1, dist2)}")

2. Geometric Median
-------------------

The ``geometric_median`` function computes the geometric median of a set
of points, which is the point that minimizes the sum of distances to all
other points.

.. code:: ipython3

    # Example 5: Geometric median computation
    # Create a set of 2D points
    points = torch.tensor([
        [1.0, 2.0],
        [3.0, 4.0],
        [5.0, 6.0],
        [2.0, 3.0],
        [4.0, 5.0]
    ])
    
    print(f"Input points shape: {points.shape}")
    print(f"Input points:\n{points}")
    
    # Compute geometric median
    median = linalg.geometric_median(points, dim=0)
    print(f"\nGeometric median: {median}")
    
    # Compare with arithmetic mean
    arithmetic_mean = points.mean(dim=0)
    print(f"Arithmetic mean: {arithmetic_mean}")
    
    # Visualize the result
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.scatter(points[:, 0], points[:, 1], c='blue', label='Data points', alpha=0.7)
    ax.scatter(median[0], median[1], c='red', s=100, marker='x', label='Geometric median')
    ax.scatter(arithmetic_mean[0], arithmetic_mean[1], c='green', s=100, marker='+', label='Arithmetic mean')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_title('Geometric Median vs Arithmetic Mean')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

.. code:: ipython3

    # Example 6: Geometric median with outliers
    # Create points with one outlier
    points_with_outlier = torch.tensor([
        [1.0, 1.0],
        [2.0, 2.0],
        [3.0, 3.0],
        [2.5, 2.5],
        [10.0, 10.0]  # Outlier
    ])
    
    median_outlier = linalg.geometric_median(points_with_outlier, dim=0)
    mean_outlier = points_with_outlier.mean(dim=0)
    
    print(f"Points with outlier:\n{points_with_outlier}")
    print(f"Geometric median with outlier: {median_outlier}")
    print(f"Arithmetic mean with outlier: {mean_outlier}")
    
    # Visualize robustness to outliers
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.scatter(points_with_outlier[:-1, 0], points_with_outlier[:-1, 1], c='blue', label='Normal points', alpha=0.7)
    ax.scatter(points_with_outlier[-1, 0], points_with_outlier[-1, 1], c='orange', s=100, marker='o', label='Outlier')
    ax.scatter(median_outlier[0], median_outlier[1], c='red', s=100, marker='x', label='Geometric median')
    ax.scatter(mean_outlier[0], mean_outlier[1], c='green', s=100, marker='+', label='Arithmetic mean')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_title('Robustness to Outliers: Geometric Median vs Arithmetic Mean')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

3. Miscellaneous Linear Algebra Utilities
-----------------------------------------

Cosine Similarity
~~~~~~~~~~~~~~~~~

The ``cosine`` function computes cosine similarity between vectors.

.. code:: ipython3

    # Example 7: Cosine similarity
    v1 = np.array([1, 2, 3])
    v2 = np.array([2, 4, 6])  # Parallel vector
    v3 = np.array([1, 0, 0])  # Orthogonal vector
    v4 = np.array([-1, -2, -3])  # Anti-parallel vector
    
    cos_parallel = linalg.cosine(v1, v2)
    cos_orthogonal = linalg.cosine(v1, v3)
    cos_antiparallel = linalg.cosine(v1, v4)
    
    print(f"Vector 1: {v1}")
    print(f"Vector 2 (parallel): {v2}")
    print(f"Vector 3 (orthogonal): {v3}")
    print(f"Vector 4 (anti-parallel): {v4}")
    print(f"\nCosine similarity v1-v2 (parallel): {cos_parallel:.4f}")
    print(f"Cosine similarity v1-v3 (orthogonal): {cos_orthogonal:.4f}")
    print(f"Cosine similarity v1-v4 (anti-parallel): {cos_antiparallel:.4f}")
    
    # Test with NaN values
    v_nan = np.array([1, np.nan, 3])
    cos_nan = linalg.cosine(v1, v_nan)
    print(f"\nCosine with NaN values: {cos_nan}")

NaN-aware Norm
~~~~~~~~~~~~~~

The ``nannorm`` function computes vector norms with NaN handling.

.. code:: ipython3

    # Example 8: NaN-aware norm calculation
    v_normal = np.array([3, 4, 5])
    v_with_nan = np.array([3, np.nan, 5])
    
    norm_normal = linalg.nannorm(v_normal)
    norm_with_nan = linalg.nannorm(v_with_nan)
    
    print(f"Normal vector: {v_normal}")
    print(f"Normal vector norm: {norm_normal:.4f}")
    print(f"Expected norm: {np.sqrt(3**2 + 4**2 + 5**2):.4f}")
    
    print(f"\nVector with NaN: {v_with_nan}")
    print(f"NaN-aware norm: {norm_with_nan}")
    
    # Test with different axes
    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    norm_axis0 = linalg.nannorm(matrix, axis=0)
    norm_axis1 = linalg.nannorm(matrix, axis=1)
    
    print(f"\nMatrix:\n{matrix}")
    print(f"Norm along axis 0: {norm_axis0}")
    print(f"Norm along axis 1: {norm_axis1}")

Vector Rebasing
~~~~~~~~~~~~~~~

The ``rebase_a_vec`` function projects one vector onto another and
returns the signed magnitude.

.. code:: ipython3

    # Example 9: Vector rebasing (projection)
    v = np.array([3, 4])  # Vector to project
    v_base = np.array([1, 0])  # Base vector (x-axis)
    
    rebased = linalg.rebase_a_vec(v, v_base)
    print(f"Vector to project: {v}")
    print(f"Base vector: {v_base}")
    print(f"Rebased (projected) magnitude: {rebased:.4f}")
    
    # Test with different base vectors
    v_base_y = np.array([0, 1])  # y-axis
    v_base_diag = np.array([1, 1])  # diagonal
    
    rebased_y = linalg.rebase_a_vec(v, v_base_y)
    rebased_diag = linalg.rebase_a_vec(v, v_base_diag)
    
    print(f"\nProjection onto y-axis: {rebased_y:.4f}")
    print(f"Projection onto diagonal: {rebased_diag:.4f}")
    
    # Visualize vector projection
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    
    # Original vector
    ax.arrow(0, 0, v[0], v[1], head_width=0.1, head_length=0.1, fc='blue', ec='blue', label='Original vector')
    
    # Base vectors
    ax.arrow(0, 0, v_base[0]*5, v_base[1]*5, head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.7, label='Base vector (x-axis)')
    ax.arrow(0, 0, v_base_y[0]*5, v_base_y[1]*5, head_width=0.1, head_length=0.1, fc='green', ec='green', alpha=0.7, label='Base vector (y-axis)')
    
    # Projections
    ax.arrow(0, 0, rebased, 0, head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.5, linestyle='--', label=f'Projection on x-axis: {rebased:.2f}')
    ax.arrow(0, 0, 0, rebased_y, head_width=0.1, head_length=0.1, fc='green', ec='green', alpha=0.5, linestyle='--', label=f'Projection on y-axis: {rebased_y:.2f}')
    
    ax.set_xlim(-1, 6)
    ax.set_ylim(-1, 6)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Vector Projection (Rebasing)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.show()

4. Coordinate Transformations
-----------------------------

Triangle Coordinates from Line Lengths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``three_line_lengths_to_coords`` function converts three line
lengths to 3D coordinates of a triangle.

.. code:: ipython3

    # Example 10: Convert triangle line lengths to coordinates
    # Define triangle with sides of length 3, 4, 5 (right triangle)
    a, b, c = 3, 4, 5
    
    O, A, B = linalg.three_line_lengths_to_coords(a, b, c)
    
    print(f"Triangle with sides {a}, {b}, {c}:")
    print(f"Point O (origin): {O}")
    print(f"Point A: {A}")
    print(f"Point B: {B}")
    
    # Verify the distances
    O_np = np.array(O)
    A_np = np.array(A)
    B_np = np.array(B)
    
    dist_OA = np.linalg.norm(A_np - O_np)
    dist_OB = np.linalg.norm(B_np - O_np)
    dist_AB = np.linalg.norm(B_np - A_np)
    
    print(f"\nVerification:")
    print(f"Distance O-A: {dist_OA:.4f} (expected: {a})")
    print(f"Distance O-B: {dist_OB:.4f} (expected: {b})")
    print(f"Distance A-B: {dist_AB:.4f} (expected: {c})")
    
    # Test with different triangle
    print(f"\n" + "="*50)
    a2, b2, c2 = 2, np.sqrt(3), 1
    O2, A2, B2 = linalg.three_line_lengths_to_coords(a2, b2, c2)
    
    print(f"Triangle with sides {a2}, {b2:.3f}, {c2}:")
    print(f"Point O (origin): {O2}")
    print(f"Point A: {A2}")
    print(f"Point B: {B2}")
    
    # Verify the distances
    O2_np = np.array(O2)
    A2_np = np.array(A2)
    B2_np = np.array(B2)
    
    dist_OA2 = np.linalg.norm(A2_np - O2_np)
    dist_OB2 = np.linalg.norm(B2_np - O2_np)
    dist_AB2 = np.linalg.norm(B2_np - A2_np)
    
    print(f"\nVerification:")
    print(f"Distance O-A: {dist_OA2:.4f} (expected: {a2})")
    print(f"Distance O-B: {dist_OB2:.4f} (expected: {b2:.3f})")
    print(f"Distance A-B: {dist_AB2:.4f} (expected: {c2})")

5. Practical Applications
-------------------------

Clustering with Geometric Median
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s use the geometric median for robust clustering.

.. code:: ipython3

    # Example 11: Robust clustering using geometric median
    # Generate sample data with two clusters
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Cluster 1: centered around (2, 2)
    cluster1 = np.random.normal([2, 2], 0.5, (20, 2))
    # Cluster 2: centered around (6, 6)
    cluster2 = np.random.normal([6, 6], 0.5, (20, 2))
    # Add some outliers
    outliers = np.array([[0, 8], [8, 0], [10, 10]])
    
    # Combine all data
    all_data = np.vstack([cluster1, cluster2, outliers])
    
    # Convert to torch for geometric median
    cluster1_torch = torch.from_numpy(cluster1).float()
    cluster2_torch = torch.from_numpy(cluster2).float()
    
    # Compute centroids using both methods
    # Arithmetic mean
    mean1 = cluster1_torch.mean(dim=0)
    mean2 = cluster2_torch.mean(dim=0)
    
    # Geometric median
    median1 = linalg.geometric_median(cluster1_torch, dim=0)
    median2 = linalg.geometric_median(cluster2_torch, dim=0)
    
    # Visualize results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Arithmetic mean
    ax1.scatter(cluster1[:, 0], cluster1[:, 1], c='blue', alpha=0.6, label='Cluster 1')
    ax1.scatter(cluster2[:, 0], cluster2[:, 1], c='red', alpha=0.6, label='Cluster 2')
    ax1.scatter(outliers[:, 0], outliers[:, 1], c='black', s=100, marker='x', label='Outliers')
    ax1.scatter(mean1[0], mean1[1], c='blue', s=200, marker='s', label='Mean 1')
    ax1.scatter(mean2[0], mean2[1], c='red', s=200, marker='s', label='Mean 2')
    ax1.set_title('Clustering with Arithmetic Mean')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Geometric median
    ax2.scatter(cluster1[:, 0], cluster1[:, 1], c='blue', alpha=0.6, label='Cluster 1')
    ax2.scatter(cluster2[:, 0], cluster2[:, 1], c='red', alpha=0.6, label='Cluster 2')
    ax2.scatter(outliers[:, 0], outliers[:, 1], c='black', s=100, marker='x', label='Outliers')
    ax2.scatter(median1[0], median1[1], c='blue', s=200, marker='D', label='Median 1')
    ax2.scatter(median2[0], median2[1], c='red', s=200, marker='D', label='Median 2')
    ax2.set_title('Clustering with Geometric Median')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"Cluster 1 - Mean: {mean1.numpy()}, Median: {median1.numpy()}")
    print(f"Cluster 2 - Mean: {mean2.numpy()}, Median: {median2.numpy()}")

Distance-based Data Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s use the distance functions for analyzing patterns in data.

.. code:: ipython3

    # Example 12: Time series similarity analysis
    # Generate sample time series data
    t = np.linspace(0, 4*np.pi, 100)
    signal1 = np.sin(t) + 0.1 * np.random.randn(100)
    signal2 = np.cos(t) + 0.1 * np.random.randn(100)
    signal3 = np.sin(t + np.pi/4) + 0.1 * np.random.randn(100)
    
    signals = np.array([signal1, signal2, signal3])
    
    # Compute pairwise distances
    distance_matrix = linalg.cdist(signals, signals, 'euclidean')
    
    print("Pairwise Euclidean distances between signals:")
    print(distance_matrix)
    
    # Compute cosine similarities
    cosine_similarities = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            cosine_similarities[i, j] = linalg.cosine(signals[i], signals[j])
    
    print("\nCosine similarities between signals:")
    print(cosine_similarities)
    
    # Visualize signals and their relationships
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    
    # Plot signals
    ax1.plot(t, signal1, label='Signal 1 (sin)', alpha=0.7)
    ax1.plot(t, signal2, label='Signal 2 (cos)', alpha=0.7)
    ax1.plot(t, signal3, label='Signal 3 (sin + π/4)', alpha=0.7)
    ax1.set_title('Time Series Signals')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Amplitude')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot distance matrix
    im1 = ax2.imshow(distance_matrix, cmap='viridis', aspect='auto')
    ax2.set_title('Euclidean Distance Matrix')
    ax2.set_xlabel('Signal Index')
    ax2.set_ylabel('Signal Index')
    plt.colorbar(im1, ax=ax2)
    
    # Plot cosine similarity matrix
    im2 = ax3.imshow(cosine_similarities, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    ax3.set_title('Cosine Similarity Matrix')
    ax3.set_xlabel('Signal Index')
    ax3.set_ylabel('Signal Index')
    plt.colorbar(im2, ax=ax3)
    
    # Scatter plot of signals in 2D (first two principal components)
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    signals_2d = pca.fit_transform(signals)
    
    ax4.scatter(signals_2d[:, 0], signals_2d[:, 1], c=['blue', 'red', 'green'], s=100)
    ax4.set_title('Signals in 2D PCA Space')
    ax4.set_xlabel('PC1')
    ax4.set_ylabel('PC2')
    ax4.grid(True, alpha=0.3)
    
    # Add labels
    for i, (x, y) in enumerate(signals_2d):
        ax4.annotate(f'Signal {i+1}', (x, y), xytext=(5, 5), textcoords='offset points')
    
    plt.tight_layout()
    plt.show()

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.linalg`` module:

Distance Functions
~~~~~~~~~~~~~~~~~~

-  **``euclidean_distance``** and **``edist``**: Compute Euclidean
   distances with support for different axes
-  **``cdist``**: Access to various distance metrics from scipy

Robust Statistics
~~~~~~~~~~~~~~~~~

-  **``geometric_median``**: Compute geometric median for robust central
   tendency

Utility Functions
~~~~~~~~~~~~~~~~~

-  **``cosine``**: Compute cosine similarity between vectors
-  **``nannorm``**: NaN-aware vector norm computation
-  **``rebase_a_vec``**: Vector projection and rebasing

Coordinate Transformations
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``three_line_lengths_to_coords``**: Convert triangle side lengths
   to 3D coordinates

Key Features
~~~~~~~~~~~~

1. **Robustness**: Functions handle NaN values appropriately
2. **Flexibility**: Support for different axes and dimensions
3. **Integration**: Seamless integration with NumPy and PyTorch
4. **Scientific Applications**: Suitable for clustering, similarity
   analysis, and coordinate transformations

The module provides essential linear algebra operations for scientific
computing with emphasis on robustness and practical applications.
