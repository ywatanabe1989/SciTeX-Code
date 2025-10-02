<!-- ---
!-- Timestamp: 2025-10-02 18:51:12
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/TODO.md
!-- --- -->

- [X] Metrics calculation should be centralized in
  - [X] ~/proj/scitex_repo/src/scitex/ml/metrics/
  - [X] Fixed label handling for integer labels with string names
  - [X] Reporters delegate to centralized metrics
- [X] Plotting should be centralized in
  - [X] ~/proj/scitex_repo/src/scitex/ml/plt
  - [X] Moved Plotter class to scitex.ml.plt.classification
  - [X] Plotting should use scitex.plt.subplots (wrappers) as it will handle advanced features
    - [X] scitex plotting system with stx.io.save is quite powerful
    - [X] Especially, this is critical when we integrate with SciTeX Viz, which calls sigmaplot from python; predefined csv format is essential
    - [X] So please use stx.plt.subplots as much as possible
      - [X] bugs can be fixed but not-using them will be a higher risk
      - [X] Fixed CSV export bug in stx.io.save
      - [X] Fixed AxisWrapper.legend() signature compatibility
      - [X] Documented make_axes_locatable incompatibility in KNOWN_ISSUES.md
    - [ ] You can check how the wrappers work here:

      ``` plaintex
      /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots:
      drwxr-sr-x 5 ywatanabe punim2354 4.0K Sep 21 01:56 .
      drwxr-sr-x 7 ywatanabe punim2354 4.0K Oct  1 19:29 ..
      -rwxr-xr-x 1 ywatanabe punim2354 5.8K Jul  1 21:35 _AxesWrapper.py
      drwxr-sr-x 3 ywatanabe punim2354 4.0K Sep 24 13:51 _AxisWrapperMixins
      -rwxr-xr-x 1 ywatanabe punim2354  10K Sep  1 06:50 _AxisWrapper.py
      drwxr-sr-x 3 ywatanabe punim2354 4.0K Sep 21 01:51 _export_as_csv_formatters
      -rwxr-xr-x 1 ywatanabe punim2354 5.5K Sep 21 01:52 _export_as_csv_formatters.py
      -rwxr-xr-x 1 ywatanabe punim2354 9.8K Sep 21 01:56 _export_as_csv.py
      -rwxr-xr-x 1 ywatanabe punim2354 9.2K Sep  8 13:29 _FigWrapper.py
      -rwxr-xr-x 1 ywatanabe punim2354 3.2K Jul  1 21:35 __init__.py
      drwxr-sr-x 2 ywatanabe punim2354 4.0K Sep 21 01:56 __pycache__
      -rwxr-xr-x 1 ywatanabe punim2354 6.8K Jul  1 21:35 _SubplotsWrapper.py
      -rw-r--r-- 1 ywatanabe punim2354  920 Jul  1 21:35 TODO.md
      ```
    - [X] stx.plt.subplots system itself should be improved gradually. actually, they are buggy and often not beautiful.
      - [X] matplotlib plotters should be prefixed by ax.plot_xxx
        - [X] Added plot_bar, plot_barh, plot_scatter, plot_errorbar, plot_fill_between, plot_contour, plot_imshow, plot_boxplot, plot_violinplot
      - [X] searborn plotters should be prefixed by ax.sns_xxx
        - [X] Already implemented: sns_barplot, sns_boxplot, sns_heatmap, sns_histplot, sns_kdeplot, sns_scatterplot, sns_stripplot, sns_swarmplot, sns_violinplot, sns_pairplot, sns_jointplot, sns_lineplot
      - [X] oritinal methods also accepted (fallback via __getattr__)
      - [X] all methods available in matplotlib.pyplot.subplots are also available with fallback
      - [ ] Docstrings should be systematically handled with correct information exposed (e.g., using docstring of referenced function but updating changes to ensure all the information exposed to the user is correct)
      - [X] test codes should mirror the source code organization:
        - [X] tree ./tests/scitex/plt/
        - [X] Created test_matplotlib_plot_methods.py
        - [ ] Implement/organize/refactor/fix test codes in appropriate timings (ongoing)
        - [X] I do not recommend run all tests at once (especially for the entire scitex package! quite large and buggy, unfortunatelly). So, step by step, one by one, please


- [ ] Standardize plotting API in the stx.ml module (see docs/from_agents/plotting_api_standardization_plan.md)
  - [ ] All plotting functions should have plot_ prefix
  - [ ] All plotting functions should return fig only (user has ax if they provided it)
  - [ ] All plotting functions should accept ax=None, plot=True (no save_path - Users may handle saving, potentially with stx.io.save)
- [X] stx.io.save with use_caller_path=True option; this will be helpful when stx.io.save is called in internal scripts, which is not recommended in general but in stx.ml.classification reporter
  - [X] Implemented use_caller_path parameter in stx.io.save
  - [X] Added smart path detection that skips internal scitex library frames
  - [X] Updated all scitex.ml.plt functions to use use_caller_path=True
  - [X] Fixed bug where outputs were saved to wrong paths:
        # Before: ./../SciTeX-Code/src/scitex/ml/plt/classification_out/scripts/pac/classification/classify_pac_out/...
        # After: ./scripts/pac/classification/classify_pac_out/...

- [X] Classification Reporter may utilize label encoder as well to track labels robustly
  - [X] Labels are stored with each fold's metrics
  - [X] Labels parameter is accepted in calculate_metrics()
  - [X] Auto-generates labels if not provided
  - [X] Labels are consistently used across confusion matrix, ROC, PR curves
  - [X] Supports both string and integer labels
- [X] stx.ml.plt should only focus on plotting logic
  - [X] Moved calc_bacc_from_conf_mat to scitex.ml.metrics
  - [X] scitex.ml.plt now imports from scitex.ml.metrics (backward compat)
- [X] stx.ml.metrics should handle metrics calculation
  - [X] This module can be referenced from stx.ml.plt and stx.ml.ClassificationReporter, and user-manual scripts
  - [X] All classification metrics centralized in scitex.ml.metrics.classification
  - [X] In binary cases, both one- and two-column posterior formats should be handled gracefully
    - [X] 2D with 2 columns: uses column 1 for positive class
    - [X] 1D array: uses directly
    - [X] Multiclass: uses OVR averaging

## Focus this now
- [ ] Any scitex code should use the scitex session with main guard, main, parse_args, run_main.
  - [ ] This enables users (mostly I) can check by python -m scitex.... to with checking their outputs in /path/to/script_name_out directory
  - [ ] For example, see /home/ywatanabe/proj/scitex_repo/src/scitex/ml/template.py
  - [X] Updated scitex.ml.plt files with session pattern:
  - [X]  (use plot_ prefix for file names and function names)
    - [X] scitex.ml.plt.plot_conf_mat.py
    - [X] scitex.ml.plt.plot_learning_curve.py
    - [X] scitex.ml.plt.plot_pre_rec_curve.py (flattened from aucs/)
    - [X] scitex.ml.plt.plot_roc_curve.py (flattened from aucs/)
    - [X] scitex.ml.plt.plot_optuna_study.py
    - [X] scitex.ml.plt.legacy/_conf_mat_v01.py
  - [X] Can run: python -m scitex.ml.plt._conf_mat, _learning_curve, _plot_roc_curve, _plot_pre_rec_curve
  - [X] Flattened aucs/ directory:
    - [X] aucs/roc_auc.py → _plot_roc_curve.py
    - [X] aucs/pre_rec_auc.py → _plot_pre_rec_curve.py
    - [X] Removed aucs/ directory
  - [X] scitex.ml.metrics (use calc_ prefix for file names and function names)
    - [X] scitex.ml.metrics._calc_conf_mat.py
    - [X] scitex.ml.metrics._calc_roc_auc.py
    - [X] scitex.ml.metrics._calc_pre_rec_auc.py
    - [X] scitex.ml.metrics._calc_bacc.py
    - [X] scitex.ml.metrics._calc_clf_report.py
    - [X] scitex.ml.metrics._calc_mcc.py

<!-- EOF -->