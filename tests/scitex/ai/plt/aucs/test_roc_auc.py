#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 09:55:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/plt/aucs/test_roc_auc.py

"""Comprehensive tests for ROC AUC plotting functionality.

This module tests the roc_auc function and related utilities for generating
ROC curves and calculating AUC scores for both binary and multiclass problems.
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve
from unittest.mock import patch, MagicMock
import tempfile
import os
import warnings


class TestROCAUC:
    """Test suite for ROC AUC functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Store original matplotlib state
        self.original_backend = plt.get_backend()
        
        yield
        
        # Cleanup
        plt.close('all')
    
    def test_roc_auc_import(self):
        """Test that roc_auc can be imported successfully."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        assert callable(roc_auc), "roc_auc should be callable"
    
    def test_helper_functions_import(self):
        """Test that helper functions can be imported."""
        from scitex.ai.plt.aucs.roc_auc import (
            interpolate_roc_data_points,
            to_onehot
        )
        assert callable(interpolate_roc_data_points)
        assert callable(to_onehot)
    
    def test_to_onehot_conversion(self):
        """Test one-hot encoding functionality."""
        from scitex.ai.plt.aucs.roc_auc import to_onehot
        
        # Test cases
        labels = np.array([0, 1, 2, 0, 1, 2])
        n_classes = 3
        
        onehot = to_onehot(labels, n_classes)
        
        # Verify shape
        assert onehot.shape == (6, 3)
        
        # Verify correctness
        expected = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        assert np.array_equal(onehot, expected)
    
    def test_roc_auc_binary_classification(self):
        """Test ROC AUC for binary classification."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create binary classification data
        np.random.seed(42)
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [0.9, 0.1],
            [0.2, 0.8],
            [0.8, 0.2],
            [0.3, 0.7],
            [0.7, 0.3],
            [0.1, 0.9],
            [0.6, 0.4],
            [0.4, 0.6]
        ])
        labels = ["Negative", "Positive"]
        
        # Generate ROC curve
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Verify outputs
        assert fig is not None
        assert isinstance(metrics, dict)
        assert 'roc_auc' in metrics
        assert 'fpr' in metrics
        assert 'tpr' in metrics
        assert 'threshold' in metrics
        
        # Check that AUC values are computed for each class
        assert 0 in metrics['roc_auc']
        assert 1 in metrics['roc_auc']
        
        # Verify AUC values are in valid range
        for auc in metrics['roc_auc'].values():
            if not np.isnan(auc):
                assert 0 <= auc <= 1
        
        plt.close('all')
    
    def test_roc_auc_multiclass(self):
        """Test ROC AUC for multiclass classification."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create multiclass data
        np.random.seed(42)
        n_samples = 30
        n_classes = 4
        
        y_true = np.random.randint(0, n_classes, n_samples)
        y_proba = np.random.rand(n_samples, n_classes)
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        
        labels = [f"Class {i}" for i in range(n_classes)]
        
        # Generate ROC curves
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Verify outputs
        assert fig is not None
        assert len(metrics['roc_auc']) >= n_classes
        
        # Check micro and macro averages
        assert 'micro' in metrics['roc_auc']
        assert 'macro' in metrics['roc_auc']
        
        plt.close('all')
    
    def test_perfect_classifier(self):
        """Test ROC AUC with perfect classifier."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Perfect predictions
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0]
        ])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Perfect classifier should have AUC = 1.0
        assert np.isclose(metrics['roc_auc'][0], 1.0)
        assert np.isclose(metrics['roc_auc'][1], 1.0)
        
        plt.close('all')
    
    def test_worst_classifier(self):
        """Test ROC AUC with worst possible classifier."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Completely wrong predictions
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [0.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0]
        ])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Worst classifier should have AUC = 0.0
        assert np.isclose(metrics['roc_auc'][0], 0.0)
        assert np.isclose(metrics['roc_auc'][1], 0.0)
        
        plt.close('all')
    
    def test_random_classifier(self):
        """Test ROC AUC with random classifier."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Random predictions (should give AUC ≈ 0.5)
        np.random.seed(42)
        n_samples = 1000
        y_true = np.random.randint(0, 2, n_samples)
        y_proba = np.random.rand(n_samples, 2)
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Random classifier should have AUC ≈ 0.5
        for class_idx in [0, 1]:
            assert 0.4 < metrics['roc_auc'][class_idx] < 0.6
        
        plt.close('all')
    
    def test_interpolate_roc_data_points(self):
        """Test ROC curve interpolation functionality."""
        from scitex.ai.plt.aucs.roc_auc import interpolate_roc_data_points
        
        # Create sample ROC data
        df = pd.DataFrame({
            'fpr': [0.0, 0.2, 0.4, 1.0],
            'tpr': [0.0, 0.6, 0.8, 1.0],
            'threshold': [1.0, 0.7, 0.3, 0.0],
            'roc_auc': [0.85, 0.85, 0.85, 0.85]
        })
        
        # Interpolate
        df_interp = interpolate_roc_data_points(df)
        
        # Check interpolation results
        assert len(df_interp) == 1001  # 0 to 1000
        assert df_interp['x'].min() == 0.0
        assert df_interp['x'].max() == 1.0
        assert 'y' in df_interp.columns
        assert 'threshold' in df_interp.columns
        assert 'roc_auc' in df_interp.columns
    
    def test_csv_output(self):
        """Test CSV output functionality."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create test data
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_proba = np.array([
            [0.8, 0.1, 0.1],
            [0.2, 0.7, 0.1],
            [0.1, 0.2, 0.7],
            [0.6, 0.3, 0.1],
            [0.3, 0.5, 0.2],
            [0.2, 0.3, 0.5]
        ])
        labels = ["ClassA", "ClassB", "ClassC"]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sdir = os.path.join(tmpdir, "roc_output/")
            
            # Generate ROC with CSV output
            fig, metrics = roc_auc(plt, y_true, y_proba, labels, sdir_for_csv=sdir)
            
            # Check CSV files were created
            assert os.path.exists(sdir)
            for label in labels:
                csv_path = os.path.join(sdir, f"{label}.csv")
                assert os.path.exists(csv_path)
                
                # Verify CSV content
                df = pd.read_csv(csv_path)
                assert 'x' in df.columns or 'fpr' in df.columns
                assert 'y' in df.columns or 'tpr' in df.columns
        
        plt.close('all')
    
    def test_figure_properties(self):
        """Test properties of generated ROC figure."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create test data
        y_true = np.array([0, 1, 0, 1])
        y_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3], [0.4, 0.6]])
        labels = ["Neg", "Pos"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Check figure properties
        assert len(fig.axes) == 1
        ax = fig.axes[0]
        
        # Check axis labels
        assert ax.get_xlabel() == "FPR"
        assert ax.get_ylabel() == "TPR"
        assert ax.get_title() == "ROC Curve"
        
        # Check axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        assert xlim[0] <= 0 and xlim[1] >= 1
        assert ylim[0] <= 0 and ylim[1] >= 1
        
        # Check diagonal line exists
        lines = ax.get_lines()
        assert len(lines) > 0
        
        plt.close('all')
    
    def test_edge_case_single_class_present(self):
        """Test behavior when only one class is present in y_true."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Only class 0 present
        y_true = np.zeros(10, dtype=int)
        y_proba = np.random.rand(10, 3)
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        labels = ["A", "B", "C"]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Should still generate figure and metrics
        assert fig is not None
        assert metrics is not None
        
        plt.close('all')
    
    def test_imbalanced_dataset(self):
        """Test ROC AUC with highly imbalanced dataset."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create imbalanced data (90% class 0, 10% class 1)
        np.random.seed(42)
        n_samples = 100
        n_pos = 10
        
        y_true = np.zeros(n_samples, dtype=int)
        y_true[:n_pos] = 1
        
        # Slightly better than random predictions
        y_proba = np.random.rand(n_samples, 2)
        y_proba[y_true == 1, 1] += 0.3
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        
        labels = ["Majority", "Minority"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Check that metrics are computed despite imbalance
        assert 0 in metrics['roc_auc']
        assert 1 in metrics['roc_auc']
        
        plt.close('all')
    
    def test_tie_handling(self):
        """Test handling of tied probability scores."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create data with many ties
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [0.7, 0.3],
            [0.3, 0.7],
            [0.7, 0.3],
            [0.3, 0.7],
            [0.5, 0.5],  # Tie
            [0.5, 0.5],  # Tie
            [0.5, 0.5],  # Tie
            [0.5, 0.5],  # Tie
        ])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Should handle ties gracefully
        assert fig is not None
        assert all(0 <= v <= 1 for v in metrics['roc_auc'].values() 
                  if not np.isnan(v))
        
        plt.close('all')
    
    def test_consistency_with_sklearn(self):
        """Test that our ROC AUC matches sklearn's implementation."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create test data
        np.random.seed(42)
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1, 1, 0])
        y_proba = np.array([
            [0.9, 0.1],
            [0.2, 0.8],
            [0.8, 0.2],
            [0.3, 0.7],
            [0.7, 0.3],
            [0.1, 0.9],
            [0.6, 0.4],
            [0.4, 0.6],
            [0.35, 0.65],
            [0.55, 0.45]
        ])
        labels = ["Class 0", "Class 1"]
        
        # Compute with our function
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Compute with sklearn
        sklearn_auc_0 = roc_auc_score(y_true == 0, y_proba[:, 0])
        sklearn_auc_1 = roc_auc_score(y_true == 1, y_proba[:, 1])
        
        # Compare results
        assert np.isclose(metrics['roc_auc'][0], sklearn_auc_0, rtol=1e-5)
        assert np.isclose(metrics['roc_auc'][1], sklearn_auc_1, rtol=1e-5)
        
        plt.close('all')
    
    def test_plot_aesthetics(self):
        """Test aesthetic properties of ROC plot."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create visually distinct data
        y_true = np.array([0, 1, 2] * 10)
        y_proba = np.zeros((30, 3))
        for i in range(30):
            y_proba[i, y_true[i]] = 0.8
            y_proba[i, (y_true[i] + 1) % 3] = 0.15
            y_proba[i, (y_true[i] + 2) % 3] = 0.05
        
        labels = ["Red Class", "Green Class", "Blue Class"]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        ax = fig.axes[0]
        
        # Check legend exists and has correct entries
        legend = ax.get_legend()
        assert legend is not None
        legend_texts = [t.get_text() for t in legend.get_texts()]
        assert "Chance" in legend_texts[0]
        
        # Check that ROC curves use different colors
        lines = ax.get_lines()
        colors = [line.get_color() for line in lines]
        # First line is chance level (gray), others should be different
        assert len(set(colors[1:])) == len(colors[1:])
        
        plt.close('all')
    
    def test_micro_macro_averaging(self):
        """Test micro and macro averaging calculations."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create multiclass data
        np.random.seed(42)
        n_samples = 50
        n_classes = 3
        
        # Create somewhat predictable data
        y_true = np.repeat(np.arange(n_classes), n_samples // n_classes + 1)[:n_samples]
        y_proba = np.random.rand(n_samples, n_classes)
        
        # Bias probabilities toward true class
        for i in range(n_samples):
            y_proba[i, y_true[i]] += 0.5
        
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        
        labels = [f"Class {i}" for i in range(n_classes)]
        
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        # Check micro and macro averages exist
        assert 'micro' in metrics['roc_auc']
        assert 'macro' in metrics['roc_auc']
        
        # Macro should be average of individual AUCs
        individual_aucs = [metrics['roc_auc'][i] for i in range(n_classes) 
                          if not np.isnan(metrics['roc_auc'][i])]
        expected_macro = np.mean(individual_aucs)
        
        assert np.isclose(metrics['roc_auc']['macro'], expected_macro, rtol=1e-5)
        
        plt.close('all')
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme probability values."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create data with extreme probabilities
        y_true = np.array([0, 1, 0, 1])
        y_proba = np.array([
            [1.0 - 1e-10, 1e-10],
            [1e-10, 1.0 - 1e-10],
            [0.999999, 0.000001],
            [0.000001, 0.999999]
        ])
        labels = ["Class 0", "Class 1"]
        
        # Should handle extreme values without errors
        fig, metrics = roc_auc(plt, y_true, y_proba, labels)
        
        assert fig is not None
        assert all(0 <= v <= 1 for v in metrics['roc_auc'].values() 
                  if not np.isnan(v))
        
        plt.close('all')
    
    def test_empty_input_handling(self):
        """Test handling of empty or invalid inputs."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Test with empty arrays
        with pytest.raises((ValueError, IndexError)):
            y_true = np.array([])
            y_proba = np.array([]).reshape(0, 2)
            labels = ["A", "B"]
            roc_auc(plt, y_true, y_proba, labels)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/plt/aucs/roc_auc.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
#
# import warnings
# from itertools import cycle
#
# import numpy as np
# from sklearn.metrics import roc_auc_score, roc_curve
# import pandas as pd
#
# import scitex
#
# def interpolate_roc_data_points(df):
#     df_new = pd.DataFrame({
#         "x": np.arange(1001)/1000,
#         "y": np.nan,
#         "threshold": np.nan,
#     })
#
#     for i_row in range(len(df)-1):
#         x_pre = df.iloc[i_row]["fpr"]
#         x_post = df.iloc[i_row+1]["fpr"]
#
#         indi = (x_pre <= df_new["x"]) * (df_new["x"] <= x_post)
#
#         y_pre = df.iloc[i_row]["tpr"]
#         y_post = df.iloc[i_row+1]["tpr"]
#
#         t_pre = df.iloc[i_row]["threshold"]
#         t_post = df.iloc[i_row+1]["threshold"]
#
#         df_new["y"][indi] = y_pre
#         df_new["threshold"][indi] = t_pre
#
#     df_new["y"].iloc[0] = df["tpr"].iloc[0]
#     df_new["y"].iloc[-1] = df["tpr"].iloc[-1]
#
#     df_new["threshold"].iloc[0] = df["threshold"].iloc[0]
#     df_new["threshold"].iloc[-1] = df["threshold"].iloc[-1]
#
#     df_new["roc_auc"] = df["roc_auc"].iloc[0]
#
#     # import ipdb; ipdb.set_trace()
#     # assert df_new["y"].isna().sum() == 0
#     return df_new
#
#
# def to_onehot(labels, n_classes):
#     eye = np.eye(n_classes, dtype=int)
#     return eye[labels]
#
#
# def roc_auc(plt, true_class, pred_proba, labels, sdir_for_csv=None):
#     """
#     Calculates ROC-AUC curve.
#     Return: fig, metrics (dict)
#     """
#
#     # Use label_binarize to be multi-label like settings
#     n_classes = len(labels)
#     true_class_onehot = to_onehot(true_class, n_classes)
#
#     # For each class
#     fpr = dict()
#     tpr = dict()
#     threshold = dict()
#     roc_auc = dict()
#     for i in range(n_classes):
#         true_class_i_onehot = true_class_onehot[:, i]
#         pred_proba_i = pred_proba[:, i]
#
#         try:
#             fpr[i], tpr[i], threshold[i] = roc_curve(true_class_i_onehot, pred_proba_i)
#             roc_auc[i] = roc_auc_score(true_class_i_onehot, pred_proba_i)
#         except Exception as e:
#             print(e)
#             fpr[i], tpr[i], threshold[i], roc_auc[i] = (
#                 [np.nan],
#                 [np.nan],
#                 [np.nan],
#                 np.nan,
#             )
#
#     ## Average fpr: micro and macro
#
#     # A "micro-average": quantifying score on all classes jointly
#     fpr["micro"], tpr["micro"], threshold["micro"] = roc_curve(
#         true_class_onehot.ravel(), pred_proba.ravel()
#     )
#     roc_auc["micro"] = roc_auc_score(true_class_onehot, pred_proba, average="micro")
#
#     # macro
#     _roc_aucs = []
#     for i in range(n_classes):
#         try:
#             _roc_aucs.append(
#                 roc_auc_score(
#                     true_class_onehot[:, i], pred_proba[:, i], average="macro"
#                 )
#             )
#         except Exception as e:
#             print(
#                 f'\nROC-AUC for "{labels[i]}" was not defined and NaN-filled '
#                 "for a calculation purpose (for the macro avg.)\n"
#             )
#             _roc_aucs.append(np.nan)
#     roc_auc["macro"] = np.nanmean(_roc_aucs)
#
#     if sdir_for_csv is not None:
#         # to dfs
#         for i in range(n_classes):
#             class_name = labels[i].replace(" ", "_")
#             df = pd.DataFrame(
#                 data={
#                     "fpr": fpr[i],
#                     "tpr": tpr[i],
#                     "threshold": threshold[i],
#                     "roc_auc": [roc_auc[i] for _ in range(len(fpr[i]))],
#                 },
#                 index=pd.Index(data=np.arange(len(fpr[i])), name=class_name),
#             )
#             df = interpolate_roc_data_points(df)
#             spath = f"{sdir_for_csv}{class_name}.csv"
#             scitex.io.save(df, spath)
#
#
#     # Plot FPR-TPR curve for each class and iso-f1 curves
#     colors = cycle(["navy", "turquoise", "darkorange", "cornflowerblue", "teal"])
#
#     fig, ax = plt.subplots()
#     ax.set_box_aspect(1)
#     lines = []
#     legends = []
#
#     ## Chance Level (the diagonal line)
#     (l,) = ax.plot(
#         np.linspace(0.01, 1),
#         np.linspace(0.01, 1),
#         color="gray",
#         lw=2,
#         linestyle="--",
#         alpha=0.8,
#     )
#     lines.append(l)
#     legends.append("Chance")
#
#     ## Each Class
#     for i, color in zip(range(n_classes), colors):
#         (l,) = plt.plot(fpr[i], tpr[i], color=color, lw=2)
#         lines.append(l)
#         legends.append("{0} (AUC = {1:0.2f})" "".format(labels[i], roc_auc[i]))
#
#     # fig = plt.gcf()
#     fig.subplots_adjust(bottom=0.25)
#     ax.set_xlim([-0.01, 1.01])
#     ax.set_ylim([-0.01, 1.01])
#     ax.set_xticks([0.0, 0.5, 1.0])
#     ax.set_yticks([0.0, 0.5, 1.0])
#     ax.set_xlabel("FPR")
#     ax.set_ylabel("TPR")
#     ax.set_title("ROC Curve")
#     ax.legend(lines, legends, loc="lower right")
#
#     metrics = dict(roc_auc=roc_auc, fpr=fpr, tpr=tpr, threshold=threshold)
#
#     # return fig, roc_auc, fpr, tpr, threshold
#     return fig, metrics
#
#
# if __name__ == "__main__":
#     import matplotlib.pyplot as plt
#     import numpy as np
#     from scipy.special import softmax
#     from sklearn import datasets, svm
#     from sklearn.model_selection import train_test_split
#
#     def mk_demo_data(n_classes=2, batch_size=16):
#         labels = ["cls{}".format(i_cls) for i_cls in range(n_classes)]
#         true_class = np.random.randint(0, n_classes, size=(batch_size,))
#         pred_proba = softmax(np.random.rand(batch_size, n_classes), axis=-1)
#         pred_class = np.argmax(pred_proba, axis=-1)
#         return labels, true_class, pred_proba, pred_class
#
#     ## Fix seed
#     np.random.seed(42)
#
#     """
#     ################################################################################
#     ## A Minimal Example
#     ################################################################################
#     labels, true_class, pred_proba, pred_class = \
#         mk_demo_data(n_classes=10, batch_size=256)
#
#     roc_auc, fpr, tpr, threshold = \
#         calc_roc_auc(true_class, pred_proba, labels, plot=False)
#     """
#
#     ################################################################################
#     ## MNIST
#     ################################################################################
#     from sklearn import datasets, metrics, svm
#     from sklearn.model_selection import train_test_split
#
#     digits = datasets.load_digits()
#
#     # flatten the images
#     n_samples = len(digits.images)
#     data = digits.images.reshape((n_samples, -1))
#
#     # Create a classifier: a support vector classifier
#     clf = svm.SVC(gamma=0.001, probability=True)
#
#     # Split data into 50% train and 50% test subsets
#     X_train, X_test, y_train, y_test = train_test_split(
#         data, digits.target, test_size=0.5, shuffle=False
#     )
#
#     # Learn the digits on the train subset
#     clf.fit(X_train, y_train)
#
#     # Predict the value of the digit on the test subset
#     predicted_proba = clf.predict_proba(X_test)
#     predicted = clf.predict(X_test)
#
#     n_classes = len(np.unique(digits.target))
#     labels = ["Class {}".format(i) for i in range(n_classes)]
#
#     ## Configures matplotlib
#     plt.rcParams["font.size"] = 20
#     plt.rcParams["legend.fontsize"] = "xx-small"
#     plt.rcParams["figure.figsize"] = (16 * 1.2, 9 * 1.2)
#
#     np.unique(y_test)
#     np.unique(predicted_proba)
#
#     y_test[y_test == 9] = 8  # override 9 as 8
#     ## Main
#     fig, metrics_dict = roc_auc(plt, y_test, predicted_proba, labels, sdir_for_csv="./tmp/roc_test/")
#
#     fig.show()
#
#     print(metrics_dict.keys())
#     # dict_keys(['roc_auc', 'fpr', 'tpr', 'threshold'])

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/plt/aucs/roc_auc.py
# --------------------------------------------------------------------------------
