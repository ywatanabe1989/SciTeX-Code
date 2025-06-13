#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 17:01:15 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_save_optuna_study_as_csv_and_pngs.py


def save_optuna_study_as_csv_and_pngs(study, sdir):
    import optuna
    from .._save import save

    ## Trials DataFrame
    trials_df = study.trials_dataframe()

    ## Figures
    hparams_keys = list(study.best_params.keys())
    slice_plot = optuna.visualization.plot_slice(study, params=hparams_keys)
    contour_plot = optuna.visualization.plot_contour(study, params=hparams_keys)
    optim_hist_plot = optuna.visualization.plot_optimization_history(study)
    parallel_coord_plot = optuna.visualization.plot_parallel_coordinate(
        study, params=hparams_keys
    )
    hparam_importances_plot = optuna.visualization.plot_param_importances(study)
    figs_dict = dict(
        slice_plot=slice_plot,
        contour_plot=contour_plot,
        optim_hist_plot=optim_hist_plot,
        parallel_coord_plot=parallel_coord_plot,
        hparam_importances_plot=hparam_importances_plot,
    )

    ## Saves
    save(trials_df, sdir + "trials_df.csv")

    for figname, fig in figs_dict.items():
        save(fig, sdir + f"{figname}.png")


# EOF
