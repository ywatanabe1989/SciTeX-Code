#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 12:01:06 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/ai/clustering/test__umap_working.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/ai/clustering/test__umap_working.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Add your tests here

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/clustering/_umap_working.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-07-12 18:19:59 (ywatanabe)"
#
# import matplotlib.pyplot as plt
# import scitex
# import numpy as np
# import seaborn as sns
# import umap.umap_ as umap_orig
# from natsort import natsorted
# from sklearn.preprocessing import LabelEncoder
#
#
# def umap(
#     data_all,
#     labels_all,
#     axes_titles=None,
#     supervised=False,
#     title="UMAP Clustering",
#     alpha=0.1,
#     s=3,
#     use_independent_legend=False,
#     add_super_imposed=False,
#     palette="viridis",
# ):
#
#     assert len(data_all) == len(labels_all)
#
#     if isinstance(data_all, list):
#         data_all = list(data_all)
#         labels_all = list(labels_all)
#
#     le = LabelEncoder()
#     le.fit(natsorted(np.hstack(labels_all)))
#     labels_all = [le.transform(labels) for labels in labels_all]
#
#     umap_model = umap_orig.UMAP(random_state=42)
#
#     if supervised:
#         _umap = umap_model.fit(data_all[0], y=labels_all[0])
#         title = f"(Supervised) {title}"
#     else:
#         _umap = umap_model.fit(data_all[0])
#         title = f"(Unsupervised) {title}"
#
#     ncols = len(data_all) + 1 if add_super_imposed else len(data_all)
#     share = True if ncols > 1 else False
#     fig, axes = plt.subplots(ncols=ncols, sharex=share, sharey=share)
#     fig.suptitle(title)
#     fig.supxlabel("UMAP 1")
#     fig.supylabel("UMAP 2")
#
#     for ii, (data, labels) in enumerate(zip(data_all, labels_all)):
#         embedding = _umap.transform(data)
#
#         if ncols == 1:
#             ax = axes
#         else:
#             ax = axes[ii + 1] if add_super_imposed else axes[ii]
#
#         sns.scatterplot(
#             x=embedding[:, 0],
#             y=embedding[:, 1],
#             hue=le.inverse_transform(labels),
#             ax=ax,
#             palette=palette,
#             s=s,
#             alpha=alpha,
#         )
#
#         ax.set_box_aspect(1)
#
#         if axes_titles is not None:
#             ax.set_title(axes_titles[ii])
#
#         if not use_independent_legend:
#             ax.legend(loc="upper left")
#
#         if add_super_imposed:
#             axes[0].set_title("Superimposed")
#             axes[0].set_aspect("equal")
#             sns.scatterplot(
#                 x=embedding[:, 0],
#                 y=embedding[:, 1],
#                 hue=le.inverse_transform(labels),
#                 ax=axes[0],
#                 palette=palette,
#                 legend="full" if ii == 0 else False,
#                 s=s,
#                 alpha=alpha,
#             )
#
#     if not use_independent_legend:
#         return fig, None, _umap
#
#     elif use_independent_legend:
#         legend_figs = []
#         for i, ax in enumerate(axes):
#             legend = ax.get_legend()
#             if legend:
#                 legend_fig = plt.figure(figsize=(3, 2))
#                 new_legend = legend_fig.gca().legend(
#                     handles=legend.legendHandles,
#                     labels=legend.texts,
#                     loc="center",
#                 )
#                 legend_fig.canvas.draw()
#                 legend_filename = f"legend_{i}.png"
#                 legend_fig.savefig(legend_filename, bbox_inches="tight")
#                 legend_figs.append(legend_fig)
#                 plt.close(legend_fig)
#
#         for ax in axes:
#             ax.legend_ = None
#
#         return fig, legend_figs, _umap

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/clustering/_umap_working.py
# --------------------------------------------------------------------------------
