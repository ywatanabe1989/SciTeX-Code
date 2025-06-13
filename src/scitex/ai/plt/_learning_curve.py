#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-12 19:52:48 (ywatanabe)"

import re

import matplotlib
import matplotlib.pyplot as plt
import scitex
import numpy as np
import pandas as pd


def process_i_global(metrics_df):
    if metrics_df.index.name != "i_global":
        try:
            metrics_df = metrics_df.set_index("i_global")
        except KeyError:
            print(
                "Error: The DataFrame does not contain a column named 'i_global'. Please check the column names."
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("The index is already set to 'i_global'.")
    metrics_df["i_global"] = metrics_df.index  # alias
    return metrics_df


def set_yaxis_for_acc(ax, key_plt):
    if re.search("[aA][cC][cC]", key_plt):  # acc, ylim, yticks
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1.0])
    return ax


def plot_tra(ax, metrics_df, key_plt, lw=1, color="blue"):
    indi_step = scitex.gen.search("^[Tt]rain(ing)?", metrics_df.step, as_bool=True)[0]
    step_df = metrics_df[indi_step]

    if len(step_df) != 0:
        ax.plot(
            step_df.index,  # i_global
            step_df[key_plt],
            label="Training",
            color=color,
            linewidth=lw,
        )
        ax.legend()

    return ax


def scatter_val(ax, metrics_df, key_plt, s=3, color="green"):
    indi_step = scitex.gen.search("^[Vv]alid(ation)?", metrics_df.step, as_bool=True)[0]
    step_df = metrics_df[indi_step]
    if len(step_df) != 0:
        ax.scatter(
            step_df.index,
            step_df[key_plt],
            label="Validation",
            color=color,
            s=s,
            alpha=0.9,
        )
        ax.legend()
    return ax


def scatter_tes(ax, metrics_df, key_plt, s=3, color="red"):
    indi_step = scitex.gen.search("^[Tt]est", metrics_df.step, as_bool=True)[0]
    step_df = metrics_df[indi_step]
    if len(step_df) != 0:
        ax.scatter(
            step_df.index,
            step_df[key_plt],
            label="Test",
            color=color,
            s=s,
            alpha=0.9,
        )
        ax.legend()
    return ax


def vline_at_epochs(ax, metrics_df, color="grey"):
    # Determine the global iteration values where new epochs start
    epoch_starts = metrics_df[metrics_df["i_batch"] == 0].index.values
    epoch_labels = metrics_df[metrics_df["i_batch"] == 0].index.values
    ax.vlines(
        x=epoch_starts,
        ymin=-1e4,  # ax.get_ylim()[0],
        ymax=1e4,  # ax.get_ylim()[1],
        linestyle="--",
        color=color,
    )
    return ax


def select_ticks(metrics_df, max_n_ticks=4):
    # Calculate epoch starts and their corresponding labels for ticks
    unique_epochs = metrics_df["i_epoch"].drop_duplicates().values
    epoch_starts = (
        metrics_df[metrics_df["i_batch"] == 0]["i_global"].drop_duplicates().values
    )

    # Given the performance issue, let's just select a few epoch starts for labeling
    # We use MaxNLocator to pick ticks; however, it's used here to choose a reasonable number of epoch markers
    if len(epoch_starts) > max_n_ticks:
        selected_ticks = np.linspace(
            epoch_starts[0], epoch_starts[-1], max_n_ticks, dtype=int
        )
        # Ensure selected ticks are within the epoch starts for accurate labeling
        selected_labels = [
            metrics_df[metrics_df["i_global"] == tick]["i_epoch"].iloc[0]
            for tick in selected_ticks
        ]
    else:
        selected_ticks = epoch_starts
        selected_labels = unique_epochs
    return selected_ticks, selected_labels


def learning_curve(
    metrics_df,
    keys,
    title="Title",
    max_n_ticks=4,
    scattersize=3,
    linewidth=1,
    yscale="linear",
    spath=None,
):
    _plt, cc = scitex.plt.configure_mpl(plt, show=False)
    """
    Example:
        print(metrics_df)
        #                 step  i_global  i_epoch  i_batch      loss
        # 0       Training         0        0        0  0.717023
        # 1       Training         1        0        1  0.703844
        # 2       Training         2        0        2  0.696279
        # 3       Training         3        0        3  0.685384
        # 4       Training         4        0        4  0.670675
        # ...          ...       ...      ...      ...       ...
        # 123266      Test     66900      299      866  0.000067
        # 123267      Test     66900      299      867  0.000067
        # 123268      Test     66900      299      868  0.000067
        # 123269      Test     66900      299      869  0.000067
        # 123270      Test     66900      299      870  0.000068

        # [123271 rows x 5 columns]
    """
    metrics_df = process_i_global(metrics_df)
    selected_ticks, selected_labels = select_ticks(metrics_df)

    # fig, axes = plt.subplots(len(keys), 1, sharex=True, sharey=False)
    fig, axes = scitex.plt.subplots(len(keys), 1, sharex=True, sharey=False)
    axes = axes if len(keys) != 1 else [axes]

    axes[-1].set_xlabel("Iteration #")
    fig.text(0.5, 0.95, title, ha="center")

    for i_plt, key_plt in enumerate(keys):
        ax = axes[i_plt]
        ax.set_yscale(yscale)
        ax.set_ylabel(key_plt)

        ax = set_yaxis_for_acc(ax, key_plt)
        ax = plot_tra(ax, metrics_df, key_plt, lw=linewidth, color=cc["blue"])
        ax = scatter_val(ax, metrics_df, key_plt, s=scattersize, color=cc["green"])
        ax = scatter_tes(ax, metrics_df, key_plt, s=scattersize, color=cc["red"])

        # # Custom tick marks
        # ax = scitex.plt.ax.map_ticks(
        #     ax, selected_ticks, selected_labels, axis="x"
        # )

    if spath is not None:
        scitex.io.save(fig, spath)

    return fig


if __name__ == "__main__":

    plt, cc = scitex.plt.configure_mpl(plt)
    # lpath = "./scripts/ml/.old/pretrain_EEGPT_old/2024-01-29-12-04_eDflsnWv_v8/metrics.csv"
    lpath = "./scripts/ml/pretrain_EEGPT/[DEBUG] 2024-02-11-06-45_4uUpdfpb/metrics.csv"

    sdir, _, _ = scitex.gen.split_fpath(lpath)
    metrics_df = scitex.io.load(lpath)
    fig = learning_curve(metrics_df, title="Pretraining on db_v8", yscale="log")
    # plt.show()
    scitex.io.save(fig, sdir + "learning_curve.png")
