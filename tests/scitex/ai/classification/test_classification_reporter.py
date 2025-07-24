#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex/ai/classification/test_classification_reporter.py

import os
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest


class TestClassificationReporterModule(unittest.TestCase):
    """Test classification_reporter module structure and functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'classification', 'classification_reporter.py'
        )

    def test_classification_reporter_module_exists(self):
        """Test that classification_reporter module exists."""
        assert os.path.exists(self.module_path), f"Module not found at {self.module_path}"

    def test_classification_reporter_module_has_required_classes(self):
        """Test that classification_reporter module defines required classes."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for main classes
        assert 'class ClassificationReporter(' in content, "Should have ClassificationReporter class"
        assert 'class MultiClassificationReporter(' in content, "Should have MultiClassificationReporter class"

    def test_classification_reporter_module_has_required_imports(self):
        """Test that classification_reporter module has required imports."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for critical imports
        required_imports = [
            'import matplotlib',
            'import numpy',
            'import pandas',
            'from sklearn.metrics import',
            'balanced_accuracy_score',
            'classification_report',
            'confusion_matrix',
            'matthews_corrcoef'
        ]
        
        for import_stmt in required_imports:
            assert import_stmt in content, f"Should import: {import_stmt}"

    def test_classification_reporter_class_has_required_methods(self):
        """Test that ClassificationReporter class defines required methods."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for essential methods
        required_methods = [
            'def __init__(',
            'def add(',
            'def calc_bACC(',
            'def calc_mcc(',
            'def calc_conf_mat(',
            'def calc_clf_report(',
            'def calc_AUCs(',
            'def _calc_AUCs_binary('
        ]
        
        for method in required_methods:
            assert method in content, f"ClassificationReporter should have: {method}"

    def test_classification_reporter_class_has_static_methods(self):
        """Test that ClassificationReporter class has static method decorators."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for static method decorators
        static_methods = [
            '@staticmethod\n    def calc_bACC(',
            '@staticmethod\n    def calc_mcc(',
            '@staticmethod\n    def calc_conf_mat(',
            '@staticmethod\n    def calc_clf_report('
        ]
        
        for static_method in static_methods:
            assert static_method in content, f"Should have static method: {static_method}"

    def test_multi_classification_reporter_class_has_required_methods(self):
        """Test that MultiClassificationReporter class defines required methods."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for MultiClassificationReporter methods
        required_methods = [
            'def __init__(',
            'def add(',
            'def calc_metrics(',
            'def summarize(',
            'def save(',
            'def plot_and_save_conf_mats('
        ]
        
        for method in required_methods:
            assert method in content, f"MultiClassificationReporter should have: {method}"

    def test_classification_reporter_initialization_pattern(self):
        """Test that ClassificationReporter initialization follows proper pattern."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check initialization patterns
        init_patterns = [
            'self.sdir = sdir',
            'self.folds_dict = _defaultdict(list)',
            '_fix_seeds('
        ]
        
        for pattern in init_patterns:
            assert pattern in content, f"Should have initialization pattern: {pattern}"

    def test_classification_reporter_has_metric_calculations(self):
        """Test that ClassificationReporter has metric calculation functionality."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for metric calculations
        metric_patterns = [
            '_balanced_accuracy_score(true_class, pred_class)',
            '_matthews_corrcoef(true_class, pred_class)',
            '_confusion_matrix(',
            '_classification_report('
        ]
        
        for pattern in metric_patterns:
            assert pattern in content, f"Should have metric calculation: {pattern}"

    def test_classification_reporter_has_auc_calculation_support(self):
        """Test that ClassificationReporter supports AUC calculations."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for AUC calculation support
        auc_patterns = [
            'def calc_AUCs(',
            'def _calc_AUCs_binary(',
            'roc_curve',
            'precision_recall_curve',
            'RocCurveDisplay',
            'PrecisionRecallDisplay'
        ]
        
        for pattern in auc_patterns:
            assert pattern in content, f"Should have AUC support: {pattern}"

    def test_classification_reporter_has_plotting_configuration(self):
        """Test that ClassificationReporter has plotting configuration."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for plotting configuration
        plot_patterns = [
            'auc_plt_config=dict(',
            'figsize=(7, 7)',
            'labelsize=8',
            'fontsize=7',
            'tick_size=0.8'
        ]
        
        for pattern in plot_patterns:
            assert pattern in content, f"Should have plotting config: {pattern}"

    def test_classification_reporter_has_fold_management(self):
        """Test that ClassificationReporter manages fold data properly."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for fold management
        fold_patterns = [
            'self.folds_dict[obj_name].append(obj)',
            'i_fold',
            'show=True',
            'show=False'
        ]
        
        for pattern in fold_patterns:
            assert pattern in content, f"Should have fold management: {pattern}"

    def test_multi_classification_reporter_has_target_mapping(self):
        """Test that MultiClassificationReporter manages target mapping."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for target mapping
        target_patterns = [
            'self.tgt2id = {tgt: i_tgt for i_tgt, tgt in enumerate(tgts)}',
            'self.reporters = [ClassificationReporter(sdir) for sdir in sdirs]',
            'i_tgt = self.tgt2id[tgt]',
            'self.reporters[i_tgt]'
        ]
        
        for pattern in target_patterns:
            assert pattern in content, f"Should have target mapping: {pattern}"

    def test_classification_reporter_has_binary_classification_support(self):
        """Test that ClassificationReporter supports binary classification."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for binary classification specific code
        binary_patterns = [
            'n_classes == 2',
            'assert n_classes == 2, "This method is only for binary classification"',
            'ROC_fig',
            'PRE_REC_fig'
        ]
        
        for pattern in binary_patterns:
            assert pattern in content, f"Should have binary classification support: {pattern}"

    def test_classification_reporter_has_error_handling(self):
        """Test that ClassificationReporter has proper error handling."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for error handling
        error_patterns = [
            'assert isinstance(obj_name, str)',
            'assert len(_np.unique(true_class)) == n_classes',
            'except Exception as e:'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Should have error handling: {pattern}"

    def test_classification_reporter_has_verbose_output_support(self):
        """Test that ClassificationReporter supports verbose output."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for verbose output support
        verbose_patterns = [
            'show=True',
            'show=False',
            'if show:',
            'print(f"',
            '_pprint('
        ]
        
        for pattern in verbose_patterns:
            assert pattern in content, f"Should have verbose output support: {pattern}"

    def test_classification_reporter_has_dataframe_operations(self):
        """Test that ClassificationReporter has pandas DataFrame operations."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for DataFrame operations
        df_patterns = [
            '_pd.DataFrame(',
            '.set_index(',
            '.round(',
            '.rename(',
            'pd.concat('
        ]
        
        for pattern in df_patterns:
            assert pattern in content, f"Should have DataFrame operations: {pattern}"

    def test_classification_reporter_has_matplotlib_integration(self):
        """Test that ClassificationReporter integrates with matplotlib."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for matplotlib integration
        mpl_patterns = [
            '_plt.subplots(',
            'fig_roc, ax_roc',
            'fig_prerec, ax_prerec',
            'ax_roc.plot(',
            'ax_roc.set_xlabel(',
            'ax_roc.set_ylabel(',
            'ax_roc.legend('
        ]
        
        for pattern in mpl_patterns:
            assert pattern in content, f"Should have matplotlib integration: {pattern}"

    def test_classification_reporter_has_configuration_defaults(self):
        """Test that ClassificationReporter has proper configuration defaults."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for configuration defaults
        config_patterns = [
            'patience=7',
            'verbose=False',
            'delta=1e-5',
            'direction="minimize"',
            'figsize=(7, 7)',
            'labelsize=8'
        ]
        
        for pattern in config_patterns:
            assert pattern in content, f"Should have configuration default: {pattern}"

    def test_classification_reporter_has_model_saving_support(self):
        """Test that ClassificationReporter supports model saving."""
        with open(self.module_path, 'r') as f:
            content = f.read()
        
        # Check for model saving support
        save_patterns = [
            'scitex.io.save(',
            'files_to_repro',
            'meta_dict'
        ]
        
        for pattern in save_patterns:
            assert pattern in content, f"Should have model saving support: {pattern}"


if __name__ == '__main__':
    unittest.main()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/classification/classification_reporter.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-15 01:38:28 (ywatanabe)"
# # File: ./src/scitex/ai/ClassificationReporter.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/ClassificationReporter.py"
# 
# import os as _os
# import random as _random
# import sys as _sys
# from collections import defaultdict as _defaultdict
# from glob import glob as _glob
# from pprint import pprint as _pprint
# 
# import matplotlib as _matplotlib
# import matplotlib.pyplot as _plt
# import scitex as _scitex
# import numpy as _np
# import pandas as _pd
# import torch as _torch
# from sklearn.metrics import (
#     balanced_accuracy_score as _balanced_accuracy_score,
#     classification_report as _classification_report,
#     confusion_matrix as _confusion_matrix,
#     matthews_corrcoef as _matthews_corrcoef,
# )
# 
# # Lazy import to avoid circular dependency
# def _get_fix_seeds():
#     import scitex
#     return scitex.repro.fix_seeds
# 
# _fix_seeds = None  # Will be loaded when needed
# 
# 
# class MultiClassificationReporter(object):
#     def __init__(self, sdir, tgts=None):
#         if tgts is None:
#             sdirs = [""]
#         else:
#             sdirs = [_os.path.join(sdir, tgt, "/") for tgt in tgts]
#         sdirs = [sdir + tgt + "/" for tgt in tgts]
# 
#         self.tgt2id = {tgt: i_tgt for i_tgt, tgt in enumerate(tgts)}
#         self.reporters = [ClassificationReporter(sdir) for sdir in sdirs]
# 
#     def add(self, obj_name, obj, tgt=None):
#         i_tgt = self.tgt2id[tgt]
#         self.reporters[i_tgt].add(obj_name, obj)
# 
#     def calc_metrics(
#         self,
#         true_class,
#         pred_class,
#         pred_proba,
#         labels=None,
#         i_fold=None,
#         show=True,
#         auc_plt_config=dict(
#             figsize=(7, 7),
#             labelsize=8,
#             fontsize=7,
#             legendfontsize=6,
#             tick_size=0.8,
#             tick_width=0.2,
#         ),
#         tgt=None,
#     ):
#         i_tgt = self.tgt2id[tgt]
#         self.reporters[i_tgt].calc_metrics(
#             true_class,
#             pred_class,
#             pred_proba,
#             labels=labels,
#             i_fold=i_fold,
#             show=show,
#             auc_plt_config=auc_plt_config,
#         )
# 
#     def summarize(
#         self,
#         n_round=3,
#         show=False,
#         tgt=None,
#     ):
#         i_tgt = self.tgt2id[tgt]
#         self.reporters[i_tgt].summarize(
#             n_round=n_round,
#             show=show,
#         )
# 
#     def save(
#         self,
#         files_to_repro=None,
#         meta_dict=None,
#         tgt=None,
#     ):
#         i_tgt = self.tgt2id[tgt]
#         self.reporters[i_tgt].save(
#             files_to_repro=files_to_repro,
#             meta_dict=meta_dict,
#         )
# 
#     def plot_and_save_conf_mats(
#         self,
#         plt,
#         extend_ratio=1.0,
#         colorbar=True,
#         confmat_plt_config=None,
#         sci_notation_kwargs=None,
#         tgt=None,
#     ):
#         i_tgt = self.tgt2id[tgt]
#         self.reporters[i_tgt].plot_and_save_conf_mats(
#             plt,
#             extend_ratio=extend_ratio,
#             colorbar=colorbar,
#             confmat_plt_config=confmat_plt_config,
#             sci_notation_kwargs=sci_notation_kwargs,
#         )
# 
# 
# class ClassificationReporter(object):
#     """Saves the following metrics under sdir.
#        - Balanced Accuracy
#        - MCC
#        - Confusion Matrix
#        - Classification Report
#        - ROC AUC score / curve
#        - PRE-REC AUC score / curve
# 
#     Example is described in this file.
#     """
# 
#     def __init__(self, sdir):
#         self.sdir = sdir
#         self.folds_dict = _defaultdict(list)
#         # Use lazy-loaded fix_seeds
#         fix_seeds_func = _fix_seeds or _get_fix_seeds()
#         fix_seeds_func(os=_os, random=_random, np=_np, torch=_torch, verbose=False)
# 
#     def add(
#         self,
#         obj_name,
#         obj,
#     ):
#         """
#         ## fig
#         fig, ax = plt.subplots()
#         ax.plot(np.random.rand(10))
#         reporter.add("manu_figs", fig)
# 
#         ## DataFrame
#         df = pd.DataFrame(np.random.rand(5, 3))
#         reporter.add("manu_dfs", df)
# 
#         ## scalar
#         scalar = random.random()
#         reporter.add("manu_scalers", scalar)
#         """
#         assert isinstance(obj_name, str)
#         self.folds_dict[obj_name].append(obj)
# 
#     @staticmethod
#     def calc_bACC(true_class, pred_class, i_fold, show=False):
#         """Balanced ACC"""
#         balanced_acc = _balanced_accuracy_score(true_class, pred_class)
#         if show:
#             print(f"\nBalanced ACC in fold#{i_fold} was {balanced_acc:.3f}\n")
#         return balanced_acc
# 
#     @staticmethod
#     def calc_mcc(true_class, pred_class, i_fold, show=False):
#         """MCC"""
#         mcc = float(_matthews_corrcoef(true_class, pred_class))
#         if show:
#             print(f"\nMCC in fold#{i_fold} was {mcc:.3f}\n")
#         return mcc
# 
#     @staticmethod
#     def calc_conf_mat(true_class, pred_class, labels, i_fold, show=False):
#         """
#         Confusion Matrix
#         This method assumes unique classes of true_class and pred_class are the same.
#         """
#         conf_mat = _pd.DataFrame(
#             data=_confusion_matrix(
#                 true_class, pred_class, labels=_np.arange(len(labels))
#             ),
#             columns=labels,
#         ).set_index(_pd.Series(list(labels)))
# 
#         if show:
#             print(f"\nConfusion Matrix in fold#{i_fold}: \n")
#             _pprint(conf_mat)
#             print()
# 
#         return conf_mat
# 
#     @staticmethod
#     def calc_clf_report(
#         true_class, pred_class, labels, balanced_acc, i_fold, show=False
#     ):
#         """Classification Report"""
#         clf_report = _pd.DataFrame(
#             _classification_report(
#                 true_class,
#                 pred_class,
#                 labels=_np.arange(len(labels)),
#                 target_names=labels,
#                 output_dict=True,
#             )
#         )
# 
#         clf_report["accuracy"] = balanced_acc
#         clf_report = _pd.concat(
#             [
#                 clf_report[labels],
#                 clf_report[["accuracy", "macro avg", "weighted avg"]],
#             ],
#             axis=1,
#         )
#         clf_report = clf_report.rename(columns={"accuracy": "balanced accuracy"})
#         clf_report = clf_report.round(3)
#         clf_report["index"] = clf_report.index
#         clf_report.loc["support", "index"] = "sample size"
#         clf_report.set_index("index", drop=True, inplace=True)
#         clf_report.index.name = None
#         if show:
#             print(f"\nClassification Report for fold#{i_fold}:\n")
#             _pprint(clf_report)
#             print()
#         return clf_report
# 
#     def calc_AUCs(
#         self,
#         true_class,
#         pred_proba,
#         labels,
#         i_fold,
#         show=True,
#         auc_plt_config=dict(
#             figsize=(7, 7),
#             labelsize=8,
#             fontsize=7,
#             legendfontsize=6,
#             tick_size=0.8,
#             tick_width=0.2,
#         ),
#     ):
#         """ROC AUC and PRE-REC AUC."""
#         n_classes = len(labels)
#         assert len(_np.unique(true_class)) == n_classes
#         if n_classes == 2:
#             roc_auc = self._calc_AUCs_binary(
#                 true_class,
#                 pred_proba,
#                 i_fold,
#                 show=show,
#                 auc_plt_config=auc_plt_config,
#             )
#         else:
#             roc_auc = self._calc_AUCs_multiple(
#                 true_class,
#                 pred_proba,
#                 labels,
#                 i_fold,
#                 show=show,
#                 auc_plt_config=auc_plt_config,
#             )
#         return roc_auc
# 
#     def _calc_AUCs_binary(
#         self,
#         true_class,
#         pred_proba,
#         i_fold,
#         show=False,
#         auc_plt_config=dict(
#             figsize=(7, 7),
#             labelsize=8,
#             fontsize=7,
#             legendfontsize=6,
#             tick_size=0.8,
#             tick_width=0.2,
#         ),
#     ):
#         """Calculates metrics for binary classification."""
#         from sklearn.metrics import (
#             PrecisionRecallDisplay,
#             RocCurveDisplay,
#             auc,
#             precision_recall_curve,
#             roc_curve,
#         )
# 
#         unique_classes = sorted(list(_np.unique(true_class)))
#         n_classes = len(unique_classes)
#         assert n_classes == 2, "This method is only for binary classification"
# 
#         # ROC curve
#         fpr, tpr, _ = roc_curve(true_class, pred_proba)
#         roc_auc = auc(fpr, tpr)
# 
#         fig_size = auc_plt_config["figsize"]
#         fontsize = auc_plt_config["fontsize"]
#         labelsize = auc_plt_config["labelsize"]
#         legendfontsize = auc_plt_config["legendfontsize"]
#         tick_size = auc_plt_config["tick_size"]
#         tick_width = auc_plt_config["tick_width"]
# 
#         fig_roc, ax_roc = _plt.subplots(figsize=fig_size)
#         RocCurveDisplay(
#             fpr=fpr,
#             tpr=tpr,
#             roc_auc=roc_auc,
#         ).plot(ax=ax_roc)
#         ax_roc.plot([0, 1], [0, 1], "k:")
#         ax_roc.set_xlabel("False Positive Rate", fontsize=labelsize)
#         ax_roc.set_ylabel("True Positive Rate", fontsize=labelsize)
#         ax_roc.set_title("ROC Curve", fontsize=fontsize)
#         ax_roc.legend(fontsize=legendfontsize)
#         ax_roc.tick_params(
#             axis="both",
#             which="major",
#             labelsize=tick_size,
#             width=tick_width,
#         )
#         self.folds_dict["ROC_fig"].append(fig_roc)
#         if show:
#             print(f"\nROC AUC in fold#{i_fold} is {roc_auc:.3f}\n")
# 
#         # PRE-REC curve
#         fig_prerec, ax_prerec = _plt.subplots(figsize=fig_size)
#         PrecisionRecallDisplay.from_predictions(
#             true_class,
#             pred_proba,
#             ax=ax_prerec,
#         )
#         ax_prerec.set_xlabel("Recall", fontsize=labelsize)
#         ax_prerec.set_ylabel("Precision", fontsize=labelsize)
#         ax_prerec.set_title("Precision-Recall Curve", fontsize=fontsize)
#         ax_prerec.legend(fontsize=legendfontsize)
#         ax_prerec.tick_params(
#             axis="both",
#             which="major",
#             labelsize=tick_size,
#             width=tick_width,
#         )
#         self.folds_dict["PRE_REC_fig"].append(fig_prerec)
# 
#         return roc_auc
# 
# 
# # #!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # # Time-stamp: "2024-11-20 00:15:08 (ywatanabe)"
# # # File: ./scitex_repo/src/scitex/ai/ClassificationReporter.py
# 
# # THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/ClassificationReporter.py"
# 
# # #!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # # Time-stamp: "2024-11-13 12:54:17 (ywatanabe)"
# # # File: ./scitex_repo/src/scitex/ai/ClassificationReporter.py
# 
# # import os
# # import random
# # import sys
# # from collections import defaultdict as _defaultdict
# # from glob import glob as _glob
# # from pprint import pprint as _pprint
# 
# # import matplotlib
# # import matplotlib.pyplot as plt
# # import scitex
# # import numpy as np
# # import pandas as pd
# # import torch
# # from sklearn.metrics import (
# #     balanced_accuracy_score,
# #     classification_report,
# #     confusion_matrix,
# #     matthews_corrcoef,
# # )
# 
# # from ..repro import fix_seeds
# 
# 
# # class MultiClassificationReporter(object):
# #     def __init__(self, sdir, tgts=None):
# #         if tgts is None:
# #             sdirs = [""]
# #         else:
# #             sdirs = [os.path.join(sdir, tgt, "/") for tgt in tgts]
# #         sdirs = [sdir + tgt + "/" for tgt in tgts]
# 
# #         self.tgt2id = {tgt: i_tgt for i_tgt, tgt in enumerate(tgts)}
# #         self.reporters = [ClassificationReporter(sdir) for sdir in sdirs]
# 
# #     def add(self, obj_name, obj, tgt=None):
# #         i_tgt = self.tgt2id[tgt]
# #         self.reporters[i_tgt].add(obj_name, obj)
# 
# #     def calc_metrics(
# #         self,
# #         true_class,
# #         pred_class,
# #         pred_proba,
# #         labels=None,
# #         i_fold=None,
# #         show=True,
# #         auc_plt_config=dict(
# #             figsize=(7, 7),
# #             labelsize=8,
# #             fontsize=7,
# #             legendfontsize=6,
# #             tick_size=0.8,
# #             tick_width=0.2,
# #         ),
# #         tgt=None,
# #     ):
# #         i_tgt = self.tgt2id[tgt]
# #         self.reporters[i_tgt].calc_metrics(
# #             true_class,
# #             pred_class,
# #             pred_proba,
# #             labels=labels,
# #             i_fold=i_fold,
# #             show=show,
# #             auc_plt_config=auc_plt_config,
# #         )
# 
# #     def summarize(
# #         self,
# #         n_round=3,
# #         show=False,
# #         tgt=None,
# #     ):
# #         i_tgt = self.tgt2id[tgt]
# #         self.reporters[i_tgt].summarize(
# #             n_round=n_round,
# #             show=show,
# #         )
# 
# #     def save(
# #         self,
# #         files_to_repro=None,
# #         meta_dict=None,
# #         tgt=None,
# #     ):
# #         i_tgt = self.tgt2id[tgt]
# #         self.reporters[i_tgt].save(
# #             files_to_repro=files_to_repro,
# #             meta_dict=meta_dict,
# #         )
# 
# #     def plot_and_save_conf_mats(
# #         self,
# #         plt,
# #         extend_ratio=1.0,
# #         colorbar=True,
# #         confmat_plt_config=None,
# #         sci_notation_kwargs=None,
# #         tgt=None,
# #     ):
# #         i_tgt = self.tgt2id[tgt]
# #         self.reporters[i_tgt].plot_and_save_conf_mats(
# #             plt,
# #             extend_ratio=extend_ratio,
# #             colorbar=colorbar,
# #             confmat_plt_config=confmat_plt_config,
# #             sci_notation_kwargs=sci_notation_kwargs,
# #         )
# 
# 
# # class ClassificationReporter(object):
# #     """Saves the following metrics under sdir.
# #        - Balanced Accuracy
# #        - MCC
# #        - Confusion Matrix
# #        - Classification Report
# #        - ROC AUC score / curve
# #        - PRE-REC AUC score / curve
# 
# #     Example is described in this file.
# #     """
# 
# #     def __init__(self, sdir):
# #         self.sdir = sdir
# #         self.folds_dict = _defaultdict(list)
# #         fix_seeds(os=os, random=random, np=np, torch=torch, show=False)
# 
# #     def add(
# #         self,
# #         obj_name,
# #         obj,
# #     ):
# #         """
# #         ## fig
# #         fig, ax = plt.subplots()
# #         ax.plot(np.random.rand(10))
# #         reporter.add("manu_figs", fig)
# 
# #         ## DataFrame
# #         df = pd.DataFrame(np.random.rand(5, 3))
# #         reporter.add("manu_dfs", df)
# 
# #         ## scalar
# #         scalar = random.random()
# #         reporter.add("manu_scalers", scalar)
# #         """
# #         assert isinstance(obj_name, str)
# #         self.folds_dict[obj_name].append(obj)
# 
# #     @staticmethod
# #     def calc_bACC(true_class, pred_class, i_fold, show=False):
# #         """Balanced ACC"""
# #         balanced_acc = balanced_accuracy_score(true_class, pred_class)
# #         if show:
# #             print(f"\nBalanced ACC in fold#{i_fold} was {balanced_acc:.3f}\n")
# #         return balanced_acc
# 
# #     @staticmethod
# #     def calc_mcc(true_class, pred_class, i_fold, show=False):
# #         """MCC"""
# #         mcc = float(matthews_corrcoef(true_class, pred_class))
# #         if show:
# #             print(f"\nMCC in fold#{i_fold} was {mcc:.3f}\n")
# #         return mcc
# 
# #     @staticmethod
# #     def calc_conf_mat(true_class, pred_class, labels, i_fold, show=False):
# #         """
# #         Confusion Matrix
# #         This method assumes unique classes of true_class and pred_class are the same.
# #         """
# #         # conf_mat = pd.DataFrame(
# #         #     data=confusion_matrix(true_class, pred_class),
# #         #     columns=pred_labels,
# #         #     index=true_labels,
# #         # )
# 
# #         conf_mat = pd.DataFrame(
# #             data=confusion_matrix(
# #                 true_class, pred_class, labels=np.arange(len(labels))
# #             ),
# #             columns=labels,
# #         ).set_index(pd.Series(list(labels)))
# 
# #         if show:
# #             print(f"\nConfusion Matrix in fold#{i_fold}: \n")
# #             _pprint(conf_mat)
# #             print()
# 
# #         return conf_mat
# 
# #     @staticmethod
# #     def calc_clf_report(
# #         true_class, pred_class, labels, balanced_acc, i_fold, show=False
# #     ):
# #         """Classification Report"""
# #         clf_report = pd.DataFrame(
# #             classification_report(
# #                 true_class,
# #                 pred_class,
# #                 labels=np.arange(len(labels)),
# #                 target_names=labels,
# #                 output_dict=True,
# #             )
# #         )
# 
# #         # ACC to bACC
# #         clf_report["accuracy"] = balanced_acc
# #         clf_report = pd.concat(
# #             [
# #                 clf_report[labels],
# #                 clf_report[["accuracy", "macro avg", "weighted avg"]],
# #             ],
# #             axis=1,
# #         )
# #         clf_report = clf_report.rename(
# #             columns={"accuracy": "balanced accuracy"}
# #         )
# #         clf_report = clf_report.round(3)
# #         # Renames 'support' to 'sample size'
# #         clf_report["index"] = clf_report.index
# #         clf_report.loc["support", "index"] = "sample size"
# #         clf_report.set_index("index", drop=True, inplace=True)
# #         clf_report.index.name = None
# #         if show:
# #             print(f"\nClassification Report for fold#{i_fold}:\n")
# #             _pprint(clf_report)
# #             print()
# #         return clf_report
# 
# #     @staticmethod
# #     def calc_and_plot_roc_curve(
# #         true_class, pred_proba, labels, sdir_for_csv=None
# #     ):
# #         # ROC-AUC
# #         fig_roc, metrics_roc_auc_dict = scitex.ml.plt.roc_auc(
# #             plt,
# #             true_class,
# #             pred_proba,
# #             labels,
# #             sdir_for_csv=sdir_for_csv,
# #         )
# #         plt.close()
# #         return fig_roc, metrics_roc_auc_dict
# 
# #     @staticmethod
# #     def calc_and_plot_pre_rec_curve(true_class, pred_proba, labels):
# #         # PRE-REC AUC
# #         fig_pre_rec, metrics_pre_rec_auc_dict = scitex.ml.plt.pre_rec_auc(
# #             plt, true_class, pred_proba, labels
# #         )
# #         plt.close()
# #         return fig_pre_rec, metrics_pre_rec_auc_dict
# 
# #     def calc_metrics(
# #         self,
# #         true_class,
# #         pred_class,
# #         pred_proba,
# #         labels=None,
# #         i_fold=None,
# #         show=True,
# #         auc_plt_config=dict(
# #             figsize=(7, 7),
# #             labelsize=8,
# #             fontsize=7,
# #             legendfontsize=6,
# #             tick_size=0.8,
# #             tick_width=0.2,
# #         ),
# #     ):
# #         """
# #         Calculates ACC, Confusion Matrix, Classification Report, and ROC-AUC score on a fold.
# #         Metrics and curves will be kept in self.folds_dict.
# #         """
# 
# #         ## Preparation
# #         # for convenience
# #         true_class = scitex.gen.torch_to_arr(true_class).astype(int).reshape(-1)
# #         pred_class = (
# #             scitex.gen.torch_to_arr(pred_class).astype(np.float64).reshape(-1)
# #         )
# #         pred_proba = scitex.gen.torch_to_arr(pred_proba).astype(np.float64)
# 
# #         # for curves
# #         scitex.plt.configure_mpl(
# #             plt,
# #             **auc_plt_config,
# #         )
# 
# #         ## Calc metrics
# #         # Balanced ACC
# #         bacc = self.calc_bACC(true_class, pred_class, i_fold, show=show)
# #         self.folds_dict["balanced_acc"].append(bacc)
# 
# #         # MCC
# #         self.folds_dict["mcc"].append(
# #             self.calc_mcc(true_class, pred_class, i_fold, show=show)
# #         )
# 
# #         # Confusion Matrix
# #         self.folds_dict["conf_mat/conf_mat"].append(
# #             self.calc_conf_mat(
# #                 true_class,
# #                 pred_class,
# #                 labels,
# #                 i_fold,
# #                 show=show,
# #             )
# #         )
# 
# #         # Classification Report
# #         self.folds_dict["clf_report"].append(
# #             self.calc_clf_report(
# #                 true_class, pred_class, labels, bacc, i_fold, show=show
# #             )
# #         )
# 
# #         ## Curves
# #         # ROC curve
# #         self.sdir_for_roc_csv = f"{self.sdir}roc/csv/"
# #         fig_roc, metrics_roc_auc_dict = self.calc_and_plot_roc_curve(
# #             true_class,
# #             pred_proba,
# #             labels,
# #             sdir_for_csv=self.sdir_for_roc_csv + f"fold#{i_fold}/",
# #         )
# #         self.folds_dict["roc/micro"].append(
# #             metrics_roc_auc_dict["roc_auc"]["micro"]
# #         )
# #         self.folds_dict["roc/macro"].append(
# #             metrics_roc_auc_dict["roc_auc"]["macro"]
# #         )
# #         self.folds_dict["roc/figs"].append(fig_roc)
# 
# #         # PRE-REC curve
# #         fig_pre_rec, metrics_pre_rec_auc_dict = (
# #             self.calc_and_plot_pre_rec_curve(true_class, pred_proba, labels)
# #         )
# #         self.folds_dict["pre_rec/micro"].append(
# #             metrics_pre_rec_auc_dict["pre_rec_auc"]["micro"]
# #         )
# #         self.folds_dict["pre_rec/macro"].append(
# #             metrics_pre_rec_auc_dict["pre_rec_auc"]["macro"]
# #         )
# #         self.folds_dict["pre_rec/figs"].append(fig_pre_rec)
# 
# #     @staticmethod
# #     def _mk_cv_index(n_folds):
# #         return [
# #             f"{n_folds}-folds_CV_mean",
# #             f"{n_folds}-fold_CV_std",
# #         ] + [f"fold#{i_fold}" for i_fold in range(n_folds)]
# 
# #     def summarize_roc(
# #         self,
# #     ):
# 
# #         folds_dirs = _glob(self.sdir_for_roc_csv + "fold#*")
# #         n_folds = len(folds_dirs)
# 
# #         # get class names
# #         _csv_files = _glob(os.path.join(folds_dirs[0], "*"))
# #         classes_str = [
# #             csv_file.split("/")[-1].split(".csv")[0] for csv_file in _csv_files
# #         ]
# 
# #         # dfs_classes = []
# #         # take mean and std by each class
# #         for cls_str in classes_str:
# 
# #             fpaths_cls = [
# #                 os.path.join(fold_dir, f"{cls_str}.csv")
# #                 for fold_dir in folds_dirs
# #             ]
# 
# #             ys = []
# #             roc_aucs = []
# #             for fpath_cls in fpaths_cls:
# #                 loaded_df = scitex.io.load(fpath_cls)
# #                 ys.append(loaded_df["y"])
# #                 roc_aucs.append(loaded_df["roc_auc"])
# #             ys = pd.concat(ys, axis=1)
# #             roc_aucs = pd.concat(roc_aucs, axis=1)
# 
# #             df_cls = loaded_df[["x"]].copy()
# #             df_cls["y_mean"] = ys.mean(axis=1)
# #             df_cls["y_std"] = ys.std(axis=1)
# #             df_cls["roc_auc_mean"] = roc_aucs.mean(axis=1)
# #             df_cls["roc_auc_std"] = roc_aucs.std(axis=1)
# 
# #             spath_cls = os.path.join(
# #                 self.sdir_for_roc_csv, f"k-fold_mean_std/{cls_str}.csv"
# #             )
# #             scitex.io.save(df_cls, spath_cls)
# #             # dfs_classes.append(df_cls)
# 
# #     def summarize(
# #         self,
# #         n_round=3,
# #         show=False,
# #     ):
# #         """
# #         1) Take mean and std of scalars/pd.Dataframes for folds.
# #         2) Replace self.folds_dict with the summarized DataFrames.
# #         """
# #         self.summarize_roc()
# 
# #         _n_folds_all = [
# #             len(self.folds_dict[k]) for k in self.folds_dict.keys()
# #         ]  # sometimes includes 0 because AUC curves are not always defined.
# #         self.n_folds_intended = max(_n_folds_all)
# 
# #         for i_k, k in enumerate(self.folds_dict.keys()):
# #             n_folds = _n_folds_all[i_k]
# 
# #             if n_folds != 0:
# #                 ## listed scalars
# #                 if is_listed_X(self.folds_dict[k], [float, int]):
# #                     mm = np.mean(self.folds_dict[k])
# #                     ss = np.std(self.folds_dict[k], ddof=1)
# #                     sr = pd.DataFrame(
# #                         data=[mm, ss] + self.folds_dict[k],
# #                         index=self._mk_cv_index(n_folds),
# #                         columns=[k],
# #                     )
# #                     self.folds_dict[k] = sr.round(n_round)
# 
# #                 ## listed pd.DataFrames
# #                 elif is_listed_X(self.folds_dict[k], pd.DataFrame):
# #                     zero_df_for_mm = 0 * self.folds_dict[k][0].copy()
# #                     zero_df_for_ss = 0 * self.folds_dict[k][0].copy()
# 
# #                     mm = (
# #                         zero_df_for_mm
# #                         + np.stack(self.folds_dict[k]).mean(axis=0)
# #                     ).round(n_round)
# 
# #                     ss = (
# #                         zero_df_for_ss
# #                         + np.stack(self.folds_dict[k]).std(axis=0, ddof=1)
# #                     ).round(n_round)
# 
# #                     self.folds_dict[k] = [mm, ss] + [
# #                         df_fold.round(n_round)
# #                         for df_fold in self.folds_dict[k]
# #                     ]
# 
# #                     if show:
# #                         print(
# #                             "\n----------------------------------------\n"
# #                             f"\n{k}\n"
# #                             f"\n{n_folds}-fold-CV mean:\n"
# #                         )
# #                         _pprint(self.folds_dict[k][0])
# #                         print(f"\n\n{n_folds}-fold-CV std.:\n")
# #                         _pprint(self.folds_dict[k][1])
# #                         print("\n\n----------------------------------------\n")
# 
# #                 ## listed figures
# #                 elif is_listed_X(self.folds_dict[k], matplotlib.figure.Figure):
# #                     pass
# 
# #                 else:
# #                     print(f"{k} was not summarized")
# #                     print(type(self.folds_dict[k][0]))
# 
# #     def save(
# #         self,
# #         files_to_repro=None,
# #         meta_dict=None,
# #     ):
# #         """
# #         1) Saves the content of self.folds_dict.
# #         2) Plots the colormap of confusion matrices and saves them.
# #         3) Saves passed meta_dict under self.sdir
# 
# #         Example:
# #             meta_df_1 = pd.DataFrame(data=np.random.rand(3,3))
# #             meta_dict_1 = {"a": 0}
# #             meta_dict_2 = {"b": 0}
# #             meta_dict = {"meta_1.csv": meta_df_1,
# #                          "meta_1.yaml": meta_dict_1,
# #                          "meta_2.yaml": meta_dict_1,
# #             }
# 
# #         """
# #         if meta_dict is not None:
# #             for k, v in meta_dict.items():
# #                 scitex.io.save(v, self.sdir + k)
# 
# #         for k in self.folds_dict.keys():
# 
# #             ## pd.Series / pd.DataFrame
# #             if isinstance(self.folds_dict[k], pd.Series) or isinstance(
# #                 self.folds_dict[k], pd.DataFrame
# #             ):
# #                 scitex.io.save(self.folds_dict[k], self.sdir + f"{k}.csv")
# 
# #             ## listed pd.DataFrame
# #             elif is_listed_X(self.folds_dict[k], pd.DataFrame):
# #                 scitex.io.save(
# #                     self.folds_dict[k],
# #                     self.sdir + f"{k}.csv",
# #                     # indi_suffix=self.cv_index,
# #                     indi_suffix=self._mk_cv_index(len(self.folds_dict[k])),
# #                 )
# 
# #             ## listed figures
# #             elif is_listed_X(self.folds_dict[k], matplotlib.figure.Figure):
# #                 for i_fold, fig in enumerate(self.folds_dict[k]):
# #                     scitex.io.save(
# #                         self.folds_dict[k][i_fold],
# #                         self.sdir + f"{k}/fold#{i_fold}.png",
# #                     )
# 
# #             else:
# #                 print(f"{k} was not saved")
# #                 print(type(self.folds_dict[k]))
# 
# #         if files_to_repro is not None:
# #             if isinstance(files_to_repro, list):
# #                 files_to_repro = [files_to_repro]
# #             for f in files_to_repro:
# #                 scitex.io.save(f, self.sdir)
# 
# #     def plot_and_save_conf_mats(
# #         self,
# #         plt,
# #         extend_ratio=1.0,
# #         colorbar=True,
# #         confmat_plt_config=None,
# #         sci_notation_kwargs=None,
# #     ):
# #         def _inner_plot_conf_mat(
# #             plt,
# #             cm_df,
# #             title,
# #             extend_ratio=1.0,
# #             colorbar=True,
# #             sci_notation_kwargs=None,
# #         ):
# #             labels = list(cm_df.columns)
# #             fig_conf_mat = scitex.ml.plt.confusion_matrix(
# #                 plt,
# #                 cm_df.T,
# #                 labels=labels,
# #                 title=title,
# #                 x_extend_ratio=extend_ratio,
# #                 y_extend_ratio=extend_ratio,
# #                 colorbar=colorbar,
# #             )
# 
# #             if sci_notation_kwargs is not None:
# #                 fig_conf_mat.axes[-1] = scitex.plt.ax_scientific_notation(
# #                     fig_conf_mat.axes[-1], **sci_notation_kwargs
# #                 )
# #             return fig_conf_mat
# 
# #         ## Configures mpl
# #         scitex.plt.configure_mpl(
# #             plt,
# #             **confmat_plt_config,
# #         )
# 
# #         ########################################
# #         ## Prepares confmats dfs
# #         ########################################
# #         ## Drops mean and std for the folds
# #         try:
# #             conf_mats = self.folds_dict["conf_mat/conf_mat"][
# #                 -self.n_folds_intended :
# #             ]
# 
# #         except Exception as e:
# #             print(e)
# #             conf_mats = self.folds_dict["conf_mat/conf_mat"]
# 
# #         ## Prepaires conf_mat_overall_sum
# #         conf_mat_zero = 0 * conf_mats[0].copy()  # get the table format
# #         conf_mat_overall_sum = conf_mat_zero + np.stack(conf_mats).sum(axis=0)
# 
# #         ########################################
# #         ## Plots & Saves
# #         ########################################
# #         # each fold's conf
# #         for i_fold, cm in enumerate(conf_mats):
# #             title = f"Test fold#{i_fold}"
# #             fig_conf_mat_fold = _inner_plot_conf_mat(
# #                 plt,
# #                 cm,
# #                 title,
# #                 extend_ratio=extend_ratio,
# #                 colorbar=colorbar,
# #                 sci_notation_kwargs=sci_notation_kwargs,
# #             )
# #             scitex.io.save(
# #                 fig_conf_mat_fold,
# #                 self.sdir + f"conf_mat/figs/fold#{i_fold}.png",
# #             )
# #             plt.close()
# 
# #         ## overall_sum conf_mat
# #         title = f"{self.n_folds_intended}-CV overall sum"
# #         fig_conf_mat_overall_sum = _inner_plot_conf_mat(
# #             plt,
# #             conf_mat_overall_sum,
# #             title,
# #             extend_ratio=extend_ratio,
# #             colorbar=colorbar,
# #             sci_notation_kwargs=sci_notation_kwargs,
# #         )
# #         scitex.io.save(
# #             fig_conf_mat_overall_sum,
# #             self.sdir
# #             + f"conf_mat/figs/{self.n_folds_intended}-fold_cv_overall-sum.png",
# #         )
# #         plt.close()
# 
# 
# # if __name__ == "__main__":
# #     import random
# #     import sys
# 
# #     import scitex
# #     import numpy as np
# #     from catboost import CatBoostClassifier, Pool
# #     from sklearn.datasets import load_digits
# #     from sklearn.model_selection import StratifiedKFold
# 
# #     ################################################################################
# #     ## Sets tee
# #     ################################################################################
# #     sdir = scitex.io.mk_spath(
# #         "./tmp/sdir-ClassificationReporter/"
# #     )  # "/tmp/sdir/"
# #     sys.stdout, sys.stderr = scitex.gen.tee(sys, sdir)
# 
# #     ################################################################################
# #     ## Fixes seeds
# #     ################################################################################
# #     fix_seeds(np=np)
# 
# #     ## Loads
# #     mnist = load_digits()
# #     X, T = mnist.data, mnist.target
# #     labels = mnist.target_names.astype(str)
# 
# #     ## Main
# #     skf = StratifiedKFold(n_splits=5, shuffle=True)
# #     # reporter = ClassificationReporter(sdir)
# #     mreporter = MultiClassificationReporter(sdir, tgts=["Test1", "Test2"])
# #     for i_fold, (indi_tra, indi_tes) in enumerate(skf.split(X, T)):
# #         X_tra, T_tra = X[indi_tra], T[indi_tra]
# #         X_tes, T_tes = X[indi_tes], T[indi_tes]
# 
# #         clf = CatBoostClassifier(verbose=False)
# 
# #         clf.fit(X_tra, T_tra, verbose=False)
# 
# #         ## Prediction
# #         pred_proba_tes = clf.predict_proba(X_tes)
# #         pred_cls_tes = np.argmax(pred_proba_tes, axis=1)
# 
# #         pred_cls_tes[pred_cls_tes == 9] = 8  # overide 9 as 8 # fixme
# 
# #         ##############################
# #         ## Manually adds objects to reporter to save
# #         ##############################
# #         ## Figure
# #         fig, ax = plt.subplots()
# #         ax.plot(np.arange(10))
# #         # reporter.add("manu_figs", fig)
# #         mreporter.add("manu_figs", fig, tgt="Test1")
# #         mreporter.add("manu_figs", fig, tgt="Test2")
# 
# #         ## DataFrame
# #         df = pd.DataFrame(np.random.rand(5, 3))
# #         # reporter.add("manu_dfs", df)
# #         mreporter.add("manu_dfs", df, tgt="Test1")
# #         mreporter.add("manu_dfs", df, tgt="Test2")
# 
# #         ## Scalar
# #         scalar = random.random()
# #         # reporter.add(
# #         #     "manu_scalars",
# #         #     scalar,
# #         # )
# #         mreporter.add("manu_scalars", scalar, tgt="Test1")
# #         mreporter.add("manu_scalars", scalar, tgt="Test2")
# 
# #         ########################################
# #         ## Metrics
# #         ########################################
# #         mreporter.calc_metrics(
# #             T_tes,
# #             pred_cls_tes,
# #             pred_proba_tes,
# #             labels=labels,
# #             i_fold=i_fold,
# #             tgt="Test1",
# #         )
# #         mreporter.calc_metrics(
# #             T_tes,
# #             pred_cls_tes,
# #             pred_proba_tes,
# #             labels=labels,
# #             i_fold=i_fold,
# #             tgt="Test2",
# #         )
# 
# #     # reporter.summarize(show=True)
# #     mreporter.summarize(show=True, tgt="Test1")
# #     mreporter.summarize(show=True, tgt="Test2")
# 
# #     fake_fpaths = ["fake_file_1.txt", "fake_file_2.txt"]
# #     for ff in fake_fpaths:
# #         scitex.io.touch(ff)
# 
# #     files_to_repro = [
# #         scitex.gen.get_this_fpath(when_ipython="/dev/null"),
# #         *fake_fpaths,
# #     ]
# #     # reporter.save(files_to_repro=files_to_repro)
# #     mreporter.save(files_to_repro=files_to_repro, tgt="Test1")
# #     mreporter.save(files_to_repro=files_to_repro, tgt="Test2")
# 
# #     confmat_plt_config = dict(
# #         figsize=(8, 8),
# #         # labelsize=8,
# #         # fontsize=6,
# #         # legendfontsize=6,
# #         figscale=2,
# #         tick_size=0.8,
# #         tick_width=0.2,
# #     )
# 
# #     sci_notation_kwargs = dict(
# #         order=1,
# #         fformat="%1.0d",
# #         scilimits=(-3, 3),
# #         x=False,
# #         y=True,
# #     )  # "%3.1f"
# 
# #     # sci_notation_kwargs = None
# #     # reporter.plot_and_save_conf_mats(
# #     #     plt,
# #     #     extend_ratio=1.0,
# #     #     confmat_plt_config=confmat_plt_config,
# #     #     sci_notation_kwargs=sci_notation_kwargs,
# #     # )
# 
# #     mreporter.plot_and_save_conf_mats(
# #         plt,
# #         extend_ratio=1.0,
# #         confmat_plt_config=confmat_plt_config,
# #         sci_notation_kwargs=sci_notation_kwargs,
# #         tgt="Test1",
# #     )
# #     mreporter.plot_and_save_conf_mats(
# #         plt,
# #         extend_ratio=1.0,
# #         confmat_plt_config=confmat_plt_config,
# #         sci_notation_kwargs=sci_notation_kwargs,
# #         tgt="Test2",
# #     )
# 
# # python -m scitex.ai.ClassificationReporter
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/classification/classification_reporter.py
# --------------------------------------------------------------------------------
