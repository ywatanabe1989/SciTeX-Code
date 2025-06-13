#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-05-14 00:58:26 (ywatanabe)"

import matplotlib.pyplot as plt
import scitex
import numpy as np
import seaborn as sns
from natsort import natsorted
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder


def pca(
    data_all,
    labels_all,
    axes_titles=None,
    title="PCA Clustering",
    alpha=0.1,
    s=3,
    use_independent_legend=False,
    add_super_imposed=False,
    palette="viridis",
):

    assert len(data_all) == len(labels_all)

    if isinstance(data_all, list):
        data_all = list(data_all)
        labels_all = list(labels_all)

    le = LabelEncoder()
    # le.fit(np.hstack(labels_all))
    le.fit(natsorted(np.hstack(labels_all)))
    labels_all = [le.transform(labels) for labels in labels_all]

    pca_model = PCA(n_components=2)

    ncols = len(data_all) + 1 if add_super_imposed else len(data_all)
    share = True if ncols > 1 else False
    fig, axes = plt.subplots(ncols=ncols, sharex=share, sharey=share)

    fig.suptitle(title)
    fig.supxlabel("PCA 1")
    fig.supylabel("PCA 2")

    for ii, (data, labels) in enumerate(zip(data_all, labels_all)):
        if ii == 0:
            _pca = pca_model.fit(data)
            embedding = _pca.transform(data)
        else:
            embedding = pca_model.transform(data)

        if ncols == 1:
            ax = axes
        else:
            ax = axes[ii + 1] if add_super_imposed else axes[ii]

        sns.scatterplot(
            x=embedding[:, 0],
            y=embedding[:, 1],
            hue=le.inverse_transform(labels),
            ax=ax,
            palette=palette,
            s=s,
            alpha=alpha,
        )

        ax.set_box_aspect(1)

        if axes_titles is not None:
            ax.set_title(axes_titles[ii])

        if not use_independent_legend:
            ax.legend(loc="upper left")

        if add_super_imposed:
            axes[0].set_title("Superimposed")
            axes[0].set_aspect("equal")

            sns.scatterplot(
                x=embedding[:, 0],
                y=embedding[:, 1],
                hue=le.inverse_transform(labels),
                ax=axes[0],
                palette=palette,
                legend="full" if ii == 0 else False,
                s=s,
                alpha=alpha,
            )

    if not use_independent_legend:
        return fig, None, pca_model

    elif use_independent_legend:
        legend_figs = []
        for i, ax in enumerate(axes):
            legend = ax.get_legend()
            if legend:
                legend_fig = plt.figure(figsize=(3, 2))
                new_legend = legend_fig.gca().legend(
                    handles=legend.legendHandles,
                    labels=legend.texts,
                    loc="center",
                )
                legend_fig.canvas.draw()
                legend_filename = f"legend_{i}.png"
                legend_fig.savefig(legend_filename, bbox_inches="tight")
                legend_figs.append(legend_fig)
                plt.close(legend_fig)

        for ax in axes:
            ax.legend_ = None
            # ax.remove_legend()
            return fig, legend_figs, pca_model
