#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 18:46:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_optuna_study.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Loads Optuna study and generates various visualizations
  - Creates optimization history, parameter importances, slice plots
  - Saves study history and visualization results

Dependencies:
  - packages:
    - optuna
    - pandas
    - scitex

IO:
  - input-files:
    - Optuna study database (.db file)
  - output-files:
    - study_history.csv
    - optimization_history.png/html
    - param_importances.png/html
    - slice.png/html
    - contour.png/html
    - parallel_coordinate.png/html
"""

"""Imports"""
import argparse

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


def plot_optuna_study(lpath, value_str, sort=False):
    """
    Loads an Optuna study and generates various visualizations for each target metric.

    Parameters:
    - lpath (str): Path to the Optuna study database.
    - value_str (str): The name of the column to be used as the optimization target.

    Returns:
    - None
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import scitex
    import optuna
    import pandas as pd

    plt, CC = scitex.plt.configure_mpl(plt, fig_scale=3)

    lpath = lpath.replace("./", "/")

    study = optuna.load_study(study_name=None, storage=lpath)

    sdir = lpath.replace("sqlite:///", "./").replace(".db", "/")

    # To get the best trial:
    best_trial = study.best_trial
    print(f"Best trial number: {best_trial.number}")
    print(f"Best trial value: {best_trial.value}")
    print(f"Best trial parameters: {best_trial.params}")
    print(f"Best trial user attributes: {best_trial.user_attrs}")

    # Merge the user attributes into the study history DataFrame
    study_history = study.trials_dataframe().rename(columns={"value": value_str})

    if sort:
        ascending = "MINIMIZE" in str(study.directions[0])  # [REVISED]
        study_history = study_history.sort_values([value_str], ascending=ascending)

    # Add user attributes to the study history DataFrame
    attrs_df = []
    for trial in study.trials:
        user_attrs = trial.user_attrs
        user_attrs = {k: v for k, v in user_attrs.items()}
        attrs_df.append({"number": trial.number, **user_attrs})
    attrs_df = pd.DataFrame(attrs_df).set_index("number")

    # Updates study history
    study_history = study_history.merge(
        attrs_df, left_index=True, right_index=True, how="left"
    ).set_index("number")
    try:
        study_history = scitex.gen.mv_col(study_history, "SDIR", 1)
        study_history["SDIR"] = study_history["SDIR"].apply(
            lambda x: str(x).replace("RUNNING", "FINISHED")
        )
        best_trial_dir = study_history["SDIR"].iloc[0]
        scitex.gen.symlink(best_trial_dir, sdir + "best_trial", force=True)
    except Exception as e:
        print(e)
    stx.io.save(study_history, sdir + "study_history.csv", use_caller_path=True)
    print(study_history)

    # To visualize the optimization history:
    fig = optuna.visualization.plot_optimization_history(study, target_name=value_str)
    stx.io.save(fig, sdir + "optimization_history.png", use_caller_path=True)
    stx.io.save(fig, sdir + "optimization_history.html", use_caller_path=True)
    plt.close()

    # To visualize the parameter importances:
    fig = optuna.visualization.plot_param_importances(study, target_name=value_str)
    stx.io.save(fig, sdir + "param_importances.png", use_caller_path=True)
    stx.io.save(fig, sdir + "param_importances.html", use_caller_path=True)
    plt.close()

    # To visualize the slice of the study:
    fig = optuna.visualization.plot_slice(study, target_name=value_str)
    stx.io.save(fig, sdir + "slice.png", use_caller_path=True)
    stx.io.save(fig, sdir + "slice.html", use_caller_path=True)
    plt.close()

    # To visualize the contour plot of the study:
    fig = optuna.visualization.plot_contour(study, target_name=value_str)
    stx.io.save(fig, sdir + "contour.png", use_caller_path=True)
    stx.io.save(fig, sdir + "contour.html", use_caller_path=True)
    plt.close()

    # To visualize the parallel coordinate plot of the study:
    fig = optuna.visualization.plot_parallel_coordinate(study, target_name=value_str)
    stx.io.save(fig, sdir + "parallel_coordinate.png", use_caller_path=True)
    stx.io.save(fig, sdir + "parallel_coordinate.html", use_caller_path=True)
    plt.close()


# Keep backward compatibility
optuna_study = plot_optuna_study


"""Functions & Classes"""
def main(args):
    """
    Demonstrate Optuna study visualization.
    """
    # Example: Would require actual Optuna study database
    logger.info("This script requires an existing Optuna study database.")
    logger.info("Usage example:")
    logger.info('  lpath = "sqlite:///path/to/optuna_study.db"')
    logger.info('  plot_optuna_study(lpath, "Validation bACC", sort=True)')

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Visualize Optuna study results"
    )
    parser.add_argument(
        "--lpath",
        type=str,
        default=None,
        help="Path to Optuna study database (e.g., sqlite:///study.db)",
    )
    parser.add_argument(
        "--value_str",
        type=str,
        default="value",
        help="Target metric name (default: %(default)s)",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        default=False,
        help="Sort study history by target metric (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


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

    if args.lpath:
        plot_optuna_study(args.lpath, args.value_str, args.sort)
        exit_status = 0
    else:
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
