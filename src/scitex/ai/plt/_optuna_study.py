#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-03-30 08:24:55 (ywatanabe)"
import os


def optuna_study(lpath, value_str, sort=False):
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
    scitex.io.save(study_history, sdir + "study_history.csv")
    print(study_history)

    # To visualize the optimization history:
    fig = optuna.visualization.plot_optimization_history(study, target_name=value_str)
    scitex.io.save(fig, sdir + "optimization_history.png")
    scitex.io.save(fig, sdir + "optimization_history.html")
    plt.close()

    # To visualize the parameter importances:
    fig = optuna.visualization.plot_param_importances(study, target_name=value_str)
    scitex.io.save(fig, sdir + "param_importances.png")
    scitex.io.save(fig, sdir + "param_importances.html")
    plt.close()

    # To visualize the slice of the study:
    fig = optuna.visualization.plot_slice(study, target_name=value_str)
    scitex.io.save(fig, sdir + "slice.png")
    scitex.io.save(fig, sdir + "slice.html")
    plt.close()

    # To visualize the contour plot of the study:
    fig = optuna.visualization.plot_contour(study, target_name=value_str)
    scitex.io.save(fig, sdir + "contour.png")
    scitex.io.save(fig, sdir + "contour.html")
    plt.close()

    # To visualize the parallel coordinate plot of the study:
    fig = optuna.visualization.plot_parallel_coordinate(study, target_name=value_str)
    scitex.io.save(fig, sdir + "parallel_coordinate.png")
    scitex.io.save(fig, sdir + "parallel_coordinate.html")
    plt.close()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scitex
    scitex.plt.configure_mpl(plt, fig_scale=3)
    lpath = "sqlite:///scripts/ml/clf/sub_conv_transformer_optuna/optuna_studies/optuna_study_v001.db"
    lpath = "sqlite:///scripts/ml/clf/rocket_optuna/optuna_studies/optuna_study_v001.db"
    optuna_study(lpath, "Validation bACC")
    # scripts/ml/clf/sub_conv_transformer/optuna_studies/optuna_study_v032

    lpath = "sqlite:///scripts/ml/clf/sub_conv_transformer_optuna/optuna_studies/optuna_study_v020.db"
    scitex.ml.plt.optuna_study(lpath, "val_loss", sort=True)
