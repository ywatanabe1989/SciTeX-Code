#!/usr/bin/env python3
"""Scitex centralized plotting module.

Note: Metric calculation functions (calc_*) are imported from scitex.ml.metrics
but re-exported here for backward compatibility. New code should import directly
from scitex.ml.metrics instead.
"""

from .plot_conf_mat import calc_bACC_from_conf_mat, calc_bacc_from_conf_mat, plot_conf_mat, conf_mat
from .plot_learning_curve import (
    plot_learning_curve,
    _prepare_metrics_df,
    _configure_accuracy_axis,
    _plot_training_data,
    _plot_validation_data,
    _plot_test_data,
    _add_epoch_vlines,
    _select_epoch_ticks,
)
from .plot_optuna_study import optuna_study, plot_optuna_study
from .plot_roc_curve import plot_roc_curve
from .plot_pre_rec_curve import plot_pre_rec_curve

# Backward compatibility aliases
learning_curve = plot_learning_curve
plot_tra = _plot_training_data
process_i_global = _prepare_metrics_df
scatter_tes = _plot_test_data
scatter_val = _plot_validation_data
select_ticks = _select_epoch_ticks
set_yaxis_for_acc = _configure_accuracy_axis
vline_at_epochs = _add_epoch_vlines

__all__ = [
    # Plotting functions
    "plot_conf_mat",
    "conf_mat",  # backward compat
    "plot_learning_curve",
    "learning_curve",  # backward compat
    "optuna_study",
    "plot_optuna_study",
    "plot_roc_curve",
    "plot_pre_rec_curve",
    "plot_tra",
    "process_i_global",
    "scatter_tes",
    "scatter_val",
    "select_ticks",
    "set_yaxis_for_acc",
    "vline_at_epochs",
    # Metric calculations (re-exported from scitex.ml.metrics for backward compat)
    "calc_bACC_from_conf_mat",
    "calc_bacc_from_conf_mat",
]
