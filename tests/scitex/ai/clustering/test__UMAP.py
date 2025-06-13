#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 12:00:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/ai/clustering/test__UMAP.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/ai/clustering/test__UMAP.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/clustering/_UMAP.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-02-11 22:10:09 (ywatanabe)"
#
# # Assuming the existence of an 'scitex/ml/cluster.py' module, add the following:
#
# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sns
# import umap.umap_ as umap  # Ensure to import UMAP correctly based on your installation
#
#
# class UMAP:
#     """
#     A class to encapsulate UMAP clustering within the scitex.ml.cluster module.
#     """
#
#     @staticmethod
#     def cluster(data, labels=None, supervised=False):
#         """
#         Performs UMAP clustering on the given data, with options for supervised or unsupervised learning,
#         and visualizes the result.
#
#         Parameters:
#         - data (np.ndarray): The input data for clustering.
#         - labels (np.array, optional): Labels for each data point, used in supervised mode.
#         - supervised (bool, default=False): If True, performs supervised clustering using the provided labels.
#
#         Returns:
#         - fig (matplotlib.figure.Figure): The figure object for the UMAP visualization.
#         - embedding (np.ndarray): The 2D embedding of the input data after UMAP reduction.
#         """
#         if supervised and labels is None:
#             raise ValueError("Labels are required for supervised learning.")
#
#         umap_model = umap.UMAP()
#
#         if supervised:
#             embedding = umap_model.fit_transform(data, y=labels)
#         else:
#             embedding = umap_model.fit_transform(data)
#
#         fig = plt.figure(figsize=(10, 8))
#         if labels is not None:
#             unique_labels = np.unique(labels)
#             palette = sns.color_palette("hsv", len(unique_labels))
#             for i, label in enumerate(unique_labels):
#                 indices = labels == label
#                 plt.scatter(
#                     embedding[indices, 0],
#                     embedding[indices, 1],
#                     label=label,
#                     s=5,
#                     color=palette[i],
#                 )
#             plt.legend(markerscale=3.0, title="Labels")
#         else:
#             plt.scatter(embedding[:, 0], embedding[:, 1], s=5)
#
#         plt.title("UMAP Clustering")
#         plt.xlabel("UMAP 1")
#         plt.ylabel("UMAP 2")
#
#         return fig, embedding
#
#
# # Example usage in your library context:
# # from scitex.ml.cluster import UMAP
#
# # data, labels = <your_data>, <your_labels>
# # fig, clustered = UMAP.cluster(data, labels, supervised=False)
# # plt.show()  # Display the clustering result visualization

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/clustering/_UMAP.py
# --------------------------------------------------------------------------------
