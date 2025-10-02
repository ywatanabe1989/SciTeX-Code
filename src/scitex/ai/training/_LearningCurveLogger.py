#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2024-11-20 08:49:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/training/_LearningCurveLogger.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionality:
    - Records and visualizes learning curves during model training
    - Supports tracking of multiple metrics across training/validation/test phases
    - Generates plots showing training progress over iterations and epochs
    - Delegates plotting to scitex.ml.plt.plot_learning_curve for consistency

Input:
    - Training metrics dictionary containing loss, accuracy, predictions etc.
    - Step information (Training/Validation/Test)

Output:
    - Learning curve plots via scitex.ml.plt.plot_learning_curve
    - DataFrames with recorded metrics
    - Training progress prints

Prerequisites:
    - PyTorch
    - scikit-learn
    - matplotlib
    - pandas
    - numpy
    - scitex
"""

import re
import warnings
from collections import defaultdict
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class LearningCurveLogger:
    """Records and visualizes learning metrics during model training.

    Example
    -------
    >>> logger = LearningCurveLogger()
    >>> metrics = {
    ...     "loss_plot": 0.5,
    ...     "balanced_ACC_plot": 0.8,
    ...     "pred_proba": pred_proba,
    ...     "true_class": labels,
    ...     "i_fold": 0,
    ...     "i_epoch": 1,
    ...     "i_global": 100
    ... }
    >>> logger(metrics, "Training")
    >>> fig = logger.plot_learning_curves()
    """

    def __init__(self) -> None:
        self.logged_dict: Dict[str, Dict] = defaultdict(dict)

        warnings.warn(
            '\n"gt_label" will be removed in the future. Please use "true_class" instead.\n',
            DeprecationWarning,
        )

    def __call__(self, dict_to_log: Dict[str, Any], step: str) -> None:
        """Logs metrics for a training step.

        Parameters
        ----------
        dict_to_log : Dict[str, Any]
            Dictionary containing metrics to log
        step : str
            Phase of training ('Training', 'Validation', or 'Test')
        """
        # Handle deprecated gt_label
        if "gt_label" in dict_to_log:
            dict_to_log["true_class"] = dict_to_log.pop("gt_label")

        for k_to_log in dict_to_log:
            try:
                self.logged_dict[step][k_to_log].append(dict_to_log[k_to_log])
            except KeyError:
                self.logged_dict[step][k_to_log] = [dict_to_log[k_to_log]]

    @property
    def dfs(self) -> Dict[str, pd.DataFrame]:
        """Returns DataFrames of logged metrics.

        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary of DataFrames for each step
        """
        return self._to_dfs_pivot(self.logged_dict, pivot_column=None)

    def to_metrics_df(self) -> pd.DataFrame:
        """Convert logged data to metrics DataFrame for plot_learning_curve.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: step, i_global, i_epoch, i_batch, and metric columns
        """
        all_rows = []

        for step, metrics in self.logged_dict.items():
            n_samples = len(metrics['i_global'])

            for i in range(n_samples):
                row = {'step': step}
                for key, values in metrics.items():
                    # Only include scalar metrics for the DataFrame
                    if key.endswith('_plot') or key in ['i_global', 'i_epoch', 'i_batch', 'i_fold']:
                        row[key] = values[i]
                all_rows.append(row)

        df = pd.DataFrame(all_rows)

        # Rename _plot columns
        df.columns = [col.replace('_plot', '') if col.endswith('_plot') else col
                      for col in df.columns]

        # Ensure i_batch exists (create dummy if not logged)
        if 'i_batch' not in df.columns:
            df['i_batch'] = df.groupby(['step', 'i_epoch']).cumcount()

        return df

    def plot_learning_curves(
        self,
        title: Optional[str] = None,
        max_n_ticks: int = 4,
        linewidth: float = 1,
        scattersize: float = 3,
        yscale: str = "linear",
        spath: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """Plots learning curves from logged metrics.

        Delegates to scitex.ml.plt.plot_learning_curve for consistent plotting.

        Parameters
        ----------
        title : str, optional
            Plot title
        max_n_ticks : int
            Maximum number of ticks on axes
        linewidth : float
            Width of plot lines
        scattersize : float
            Size of scatter points
        yscale : str
            Y-axis scale ('linear' or 'log')
        spath : str, optional
            Save path for the figure

        Returns
        -------
        matplotlib.figure.Figure
            Figure containing learning curves
        """
        from scitex.ml.plt import plot_learning_curve

        # Convert to metrics DataFrame
        metrics_df = self.to_metrics_df()

        # Find keys to plot (exclude metadata columns)
        keys_to_plot = [
            col for col in metrics_df.columns
            if col not in ['step', 'i_global', 'i_epoch', 'i_batch', 'i_fold']
        ]

        if len(keys_to_plot) == 0:
            # Create empty plot when no plot keys found
            fig, ax = plt.subplots(1, 1)
            ax.set_xlabel("Iteration #")
            ax.set_ylabel("No metrics to plot")
            if title:
                fig.text(0.5, 0.95, title, ha="center")
            return fig

        # Delegate to centralized plotting function
        fig = plot_learning_curve(
            metrics_df=metrics_df,
            keys=keys_to_plot,
            title=title or "Learning Curves",
            max_n_ticks=max_n_ticks,
            scattersize=scattersize,
            linewidth=linewidth,
            yscale=yscale,
            spath=spath,
        )

        return fig

    def get_x_of_i_epoch(self, x: str, step: str, i_epoch: int) -> np.ndarray:
        """Gets metric values for a specific epoch.

        Parameters
        ----------
        x : str
            Name of metric to retrieve
        step : str
            Training phase
        i_epoch : int
            Epoch number

        Returns
        -------
        np.ndarray
            Array of metric values for specified epoch
        """
        indi = np.array(self.logged_dict[step]["i_epoch"]) == i_epoch
        x_all_arr = np.array(self.logged_dict[step][x])
        assert len(indi) == len(x_all_arr)
        return x_all_arr[indi]

    def print(self, step: str) -> None:
        """Prints metrics for given step.

        Parameters
        ----------
        step : str
            Training phase to print metrics for
        """
        df_pivot_i_epoch = self._to_dfs_pivot(self.logged_dict, pivot_column="i_epoch")
        df_pivot_i_epoch_step = df_pivot_i_epoch[step]
        df_pivot_i_epoch_step.columns = self._rename_if_key_to_plot(
            df_pivot_i_epoch_step.columns
        )
        print("\n----------------------------------------\n")
        print(f"\n{step}: (mean of batches)\n")
        pprint(df_pivot_i_epoch_step)
        print("\n----------------------------------------\n")

    @staticmethod
    def _rename_if_key_to_plot(x: Union[str, pd.Index]) -> Union[str, pd.Index]:
        """Rename metric keys for plotting.

        Parameters
        ----------
        x : str or pd.Index
            Metric name(s) to rename

        Returns
        -------
        str or pd.Index
            Renamed metric name(s)
        """
        if isinstance(x, str):
            if re.search("_plot$", x):
                return x.replace("_plot", "")
            else:
                return x
        else:
            return x.str.replace("_plot", "")

    @staticmethod
    def _to_dfs_pivot(
        logged_dict: Dict[str, Dict],
        pivot_column: Optional[str] = None,
    ) -> Dict[str, pd.DataFrame]:
        """Convert logged dictionary to pivot DataFrames.

        Parameters
        ----------
        logged_dict : Dict[str, Dict]
            Dictionary of logged metrics
        pivot_column : str, optional
            Column to pivot on

        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary of pivot DataFrames
        """
        dfs_pivot = {}
        for step_k in logged_dict.keys():
            if pivot_column is None:
                df = pd.DataFrame(logged_dict[step_k])
            else:
                df = (
                    pd.DataFrame(logged_dict[step_k])
                    .groupby(pivot_column)
                    .mean()
                    .reset_index()
                    .set_index(pivot_column)
                )
            dfs_pivot[step_k] = df
        return dfs_pivot


"""Functions & Classes"""
def main(args):
    """Demo learning curve logger with MNIST training."""
    import torch
    import torch.nn as nn
    from sklearn.metrics import balanced_accuracy_score
    from torch.utils.data import DataLoader, TensorDataset
    from torch.utils.data.dataset import Subset
    from torchvision import datasets
    import scitex

    ################################################################################
    ## NN
    ################################################################################
    class Perceptron(nn.Module):
        def __init__(self):
            super().__init__()
            self.l1 = nn.Linear(28 * 28, 50)
            self.l2 = nn.Linear(50, 10)

        def forward(self, x):
            x = x.view(-1, 28 * 28)
            x = self.l1(x)
            x = self.l2(x)
            return x

    ################################################################################
    ## Prepare demo data
    ################################################################################
    ## Downloads
    _ds_tra_val = datasets.MNIST("/tmp/mnist", train=True, download=True)
    _ds_tes = datasets.MNIST("/tmp/mnist", train=False, download=True)

    ## Training-Validation splitting
    n_samples = len(_ds_tra_val)
    train_size = int(n_samples * 0.8)

    subset1_indices = list(range(0, train_size))
    subset2_indices = list(range(train_size, n_samples))

    _ds_tra = Subset(_ds_tra_val, subset1_indices)
    _ds_val = Subset(_ds_tra_val, subset2_indices)

    ## to tensors
    ds_tra = TensorDataset(
        _ds_tra.dataset.data.to(torch.float32),
        _ds_tra.dataset.targets,
    )
    ds_val = TensorDataset(
        _ds_val.dataset.data.to(torch.float32),
        _ds_val.dataset.targets,
    )
    ds_tes = TensorDataset(
        _ds_tes.data.to(torch.float32),
        _ds_tes.targets,
    )

    ## to dataloaders
    batch_size = 64
    dl_tra = DataLoader(
        dataset=ds_tra,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
    )

    dl_val = DataLoader(
        dataset=ds_val,
        batch_size=batch_size,
        shuffle=False,
        drop_last=True,
    )

    dl_tes = DataLoader(
        dataset=ds_tes,
        batch_size=batch_size,
        shuffle=False,
        drop_last=True,
    )

    ################################################################################
    ## Preparation
    ################################################################################
    model = Perceptron()
    loss_func = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)
    softmax = nn.Softmax(dim=-1)

    ################################################################################
    ## Main
    ################################################################################
    lc_logger = LearningCurveLogger()
    i_global = 0

    i_fold = 0
    max_epochs = 3

    for i_epoch in range(max_epochs):
        step = "Validation"
        for i_batch, batch in enumerate(dl_val):
            X, T = batch
            logits = model(X)
            pred_proba = softmax(logits)
            pred_class = pred_proba.argmax(dim=-1)
            loss = loss_func(logits, T)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                bACC = balanced_accuracy_score(T, pred_class)

            dict_to_log = {
                "loss_plot": float(loss),
                "balanced_ACC_plot": float(bACC),
                "pred_proba": pred_proba.detach().cpu().numpy(),
                "true_class": T.cpu().numpy(),
                "i_fold": i_fold,
                "i_epoch": i_epoch,
                "i_batch": i_batch,
                "i_global": i_global,
            }
            lc_logger(dict_to_log, step)

        lc_logger.print(step)

        step = "Training"
        for i_batch, batch in enumerate(dl_tra):
            optimizer.zero_grad()

            X, T = batch
            logits = model(X)
            pred_proba = softmax(logits)
            pred_class = pred_proba.argmax(dim=-1)
            loss = loss_func(logits, T)

            loss.backward()
            optimizer.step()

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                bACC = balanced_accuracy_score(T, pred_class)

            dict_to_log = {
                "loss_plot": float(loss),
                "balanced_ACC_plot": float(bACC),
                "pred_proba": pred_proba.detach().cpu().numpy(),
                "true_class": T.cpu().numpy(),
                "i_fold": i_fold,
                "i_epoch": i_epoch,
                "i_batch": i_batch,
                "i_global": i_global,
            }
            lc_logger(dict_to_log, step)

            i_global += 1

        lc_logger.print(step)

    step = "Test"
    for i_batch, batch in enumerate(dl_tes):
        X, T = batch
        logits = model(X)
        pred_proba = softmax(logits)
        pred_class = pred_proba.argmax(dim=-1)
        loss = loss_func(logits, T)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            bACC = balanced_accuracy_score(T, pred_class)

        dict_to_log = {
            "loss_plot": float(loss),
            "balanced_ACC_plot": float(bACC),
            "pred_proba": pred_proba.detach().cpu().numpy(),
            "true_class": T.cpu().numpy(),
            "i_fold": i_fold,
            "i_epoch": i_epoch,
            "i_batch": i_batch,
            "i_global": i_global,
        }
        lc_logger(dict_to_log, step)

    lc_logger.print(step)

    # Plot using refactored method
    fig = lc_logger.plot_learning_curves(
        title=f"fold#{i_fold}",
        linewidth=1,
        scattersize=50,
        spath="learning_curve_logger_demo.jpg",
    )

    return 0


import argparse
def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Demo learning curve logger')
    return parser.parse_args()


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
