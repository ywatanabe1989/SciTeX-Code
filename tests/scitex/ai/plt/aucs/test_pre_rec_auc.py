#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 10:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/plt/aucs/test_pre_rec_auc.py

"""Comprehensive tests for Precision-Recall AUC plotting functionality.

This module tests the pre_rec_auc function and related utilities for generating
Precision-Recall curves and calculating average precision scores.
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score, precision_recall_curve
from unittest.mock import patch, MagicMock
import warnings


class TestPrecisionRecallAUC:
    """Test suite for Precision-Recall AUC functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        yield
        plt.close('all')
    
    def test_pre_rec_auc_import(self):
        """Test that pre_rec_auc can be imported successfully."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        assert callable(pre_rec_auc), "pre_rec_auc should be callable"
    
    def test_helper_functions_import(self):
        """Test that helper functions can be imported."""
        from scitex.ai.plt.aucs.pre_rec_auc import (
            solve_the_intersection_of_a_line_and_iso_f1_curve,
            to_onehot
        )
        assert callable(solve_the_intersection_of_a_line_and_iso_f1_curve)
        assert callable(to_onehot)
    
    def test_to_onehot_consistency(self):
        """Test that to_onehot is consistent with roc_auc module."""
        from scitex.ai.plt.aucs.pre_rec_auc import to_onehot
        
        labels = np.array([0, 1, 2, 0, 1, 2])
        n_classes = 3
        
        onehot = to_onehot(labels, n_classes)
        
        assert onehot.shape == (6, 3)
        expected = np.eye(3)[labels]
        assert np.array_equal(onehot, expected)
    
    def test_iso_f1_curve_intersection(self):
        """Test calculation of iso-F1 curve intersection."""
        from scitex.ai.plt.aucs.pre_rec_auc import solve_the_intersection_of_a_line_and_iso_f1_curve
        
        # Test with line y = 0.5x + 0.5 and F1 = 0.6
        f1 = 0.6
        a = 0.5  # slope
        b = 0.5  # intercept
        
        x_f, y_f = solve_the_intersection_of_a_line_and_iso_f1_curve(f1, a, b)
        
        # Verify the point lies on both curves
        # Line equation: y = ax + b
        assert np.isclose(y_f, a * x_f + b, rtol=1e-5)
        
        # Iso-F1 curve equation: y = f1 * x / (2 * x - f1)
        expected_y = f1 * x_f / (2 * x_f - f1)
        assert np.isclose(y_f, expected_y, rtol=1e-5)
    
    def test_pre_rec_auc_binary_classification(self):
        """Test Precision-Recall AUC for binary classification."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
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
        
        # Generate PR curve
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Verify outputs
        assert fig is not None
        assert isinstance(metrics, dict)
        assert 'pre_rec_auc' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'threshold' in metrics
        
        # Check that AUC values are computed for each class
        assert 0 in metrics['pre_rec_auc']
        assert 1 in metrics['pre_rec_auc']
        
        # Verify AUC values are in valid range
        for auc in metrics['pre_rec_auc'].values():
            if not np.isnan(auc):
                assert 0 <= auc <= 1
        
        plt.close('all')
    
    def test_pre_rec_auc_multiclass(self):
        """Test Precision-Recall AUC for multiclass classification."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create multiclass data
        np.random.seed(42)
        n_samples = 30
        n_classes = 4
        
        y_true = np.random.randint(0, n_classes, n_samples)
        y_proba = np.random.rand(n_samples, n_classes)
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        
        labels = [f"Class {i}" for i in range(n_classes)]
        
        # Generate PR curves
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Verify outputs
        assert fig is not None
        assert len(metrics['pre_rec_auc']) >= n_classes
        
        # Check micro and macro averages
        assert 'micro' in metrics['pre_rec_auc']
        assert 'macro' in metrics['pre_rec_auc']
        
        plt.close('all')
    
    def test_perfect_classifier_precision_recall(self):
        """Test PR AUC with perfect classifier."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
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
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Perfect classifier should have high average precision
        assert metrics['pre_rec_auc'][0] > 0.99
        assert metrics['pre_rec_auc'][1] > 0.99
        
        plt.close('all')
    
    def test_imbalanced_dataset_precision_recall(self):
        """Test PR AUC with imbalanced dataset."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create imbalanced data (90% class 0, 10% class 1)
        np.random.seed(42)
        n_samples = 100
        n_pos = 10
        
        y_true = np.zeros(n_samples, dtype=int)
        y_true[:n_pos] = 1
        
        # Slightly better than random predictions for minority class
        y_proba = np.random.rand(n_samples, 2)
        y_proba[y_true == 1, 1] += 0.4
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        
        labels = ["Majority", "Minority"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Check that metrics are computed despite imbalance
        assert 0 in metrics['pre_rec_auc']
        assert 1 in metrics['pre_rec_auc']
        
        # PR curves are more sensitive to imbalance than ROC
        # Minority class should have lower average precision
        assert metrics['pre_rec_auc'][1] < metrics['pre_rec_auc'][0]
        
        plt.close('all')
    
    def test_figure_properties(self):
        """Test properties of generated PR figure."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create test data
        y_true = np.array([0, 1, 0, 1])
        y_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3], [0.4, 0.6]])
        labels = ["Neg", "Pos"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Check figure properties
        assert len(fig.axes) == 1
        ax = fig.axes[0]
        
        # Check axis labels
        assert ax.get_xlabel() == "Recall"
        assert ax.get_ylabel() == "Precision"
        assert ax.get_title() == "Precision-Recall Curve"
        
        # Check axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        assert xlim[0] <= 0 and xlim[1] >= 1
        assert ylim[0] <= 0 and ylim[1] >= 1
        
        plt.close('all')
    
    def test_iso_f1_curves_plotting(self):
        """Test that iso-F1 curves are plotted correctly."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create test data
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [0.8, 0.2],
            [0.3, 0.7],
            [0.6, 0.4],
            [0.4, 0.6],
            [0.7, 0.3],
            [0.2, 0.8]
        ])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        ax = fig.axes[0]
        lines = ax.get_lines()
        
        # Should have iso-F1 curves (gray lines) plus class curves
        # Count gray lines
        gray_lines = [l for l in lines if l.get_color() == 'gray']
        assert len(gray_lines) > 0  # Should have iso-F1 curves
        
        # Check legend
        legend = ax.get_legend()
        assert legend is not None
        legend_texts = [t.get_text() for t in legend.get_texts()]
        assert any('iso-f1' in text.lower() for text in legend_texts)
        
        plt.close('all')
    
    def test_edge_case_single_class_present(self):
        """Test behavior when only one class is present in y_true."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Only class 0 present
        y_true = np.zeros(10, dtype=int)
        y_proba = np.random.rand(10, 3)
        y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)
        labels = ["A", "B", "C"]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Should still generate figure and metrics
        assert fig is not None
        assert metrics is not None
        
        plt.close('all')
    
    def test_consistency_with_sklearn(self):
        """Test that our PR AUC matches sklearn's implementation."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
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
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Compute with sklearn
        sklearn_ap_0 = average_precision_score(y_true == 0, y_proba[:, 0])
        sklearn_ap_1 = average_precision_score(y_true == 1, y_proba[:, 1])
        
        # Compare results
        assert np.isclose(metrics['pre_rec_auc'][0], sklearn_ap_0, rtol=1e-5)
        assert np.isclose(metrics['pre_rec_auc'][1], sklearn_ap_1, rtol=1e-5)
        
        plt.close('all')
    
    def test_precision_recall_values(self):
        """Test that precision and recall values are valid."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create test data
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [0.9, 0.1],
            [0.2, 0.8],
            [0.7, 0.3],
            [0.3, 0.7],
            [0.8, 0.2],
            [0.1, 0.9]
        ])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Check precision and recall values
        for class_idx in [0, 1]:
            if not isinstance(metrics['precision'][class_idx], float):  # Not NaN
                precision_vals = metrics['precision'][class_idx]
                recall_vals = metrics['recall'][class_idx]
                
                # Precision and recall should be between 0 and 1
                assert np.all((0 <= precision_vals) & (precision_vals <= 1))
                assert np.all((0 <= recall_vals) & (recall_vals <= 1))
                
                # Recall should be monotonically decreasing (from right to left)
                assert np.all(np.diff(recall_vals) <= 0)
        
        plt.close('all')
    
    def test_micro_macro_averaging(self):
        """Test micro and macro averaging for PR curves."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
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
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Check micro and macro averages exist
        assert 'micro' in metrics['pre_rec_auc']
        assert 'macro' in metrics['pre_rec_auc']
        
        # Macro should be average of individual APs
        individual_aps = [metrics['pre_rec_auc'][i] for i in range(n_classes) 
                         if not np.isnan(metrics['pre_rec_auc'][i])]
        expected_macro = np.mean(individual_aps)
        
        assert np.isclose(metrics['pre_rec_auc']['macro'], expected_macro, rtol=1e-5)
        
        plt.close('all')
    
    def test_threshold_ordering(self):
        """Test that thresholds are properly ordered."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create test data
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_proba = np.array([
            [0.9, 0.1],
            [0.2, 0.8],
            [0.7, 0.3],
            [0.3, 0.7],
            [0.8, 0.2],
            [0.1, 0.9]
        ])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        # Check threshold values
        for class_idx in [0, 1]:
            if 'threshold' in metrics and class_idx in metrics['threshold']:
                thresholds = metrics['threshold'][class_idx]
                if not isinstance(thresholds, float):  # Not NaN
                    # Thresholds should be sorted in descending order
                    assert np.all(np.diff(thresholds) <= 0)
        
        plt.close('all')
    
    def test_plot_aesthetics(self):
        """Test aesthetic properties of PR plot."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create visually distinct data
        y_true = np.array([0, 1, 2] * 10)
        y_proba = np.zeros((30, 3))
        for i in range(30):
            y_proba[i, y_true[i]] = 0.8
            y_proba[i, (y_true[i] + 1) % 3] = 0.15
            y_proba[i, (y_true[i] + 2) % 3] = 0.05
        
        labels = ["Red Class", "Green Class", "Blue Class"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        ax = fig.axes[0]
        
        # Check that curves use different colors
        lines = [l for l in ax.get_lines() if l.get_color() != 'gray']
        colors = [line.get_color() for line in lines]
        assert len(set(colors)) == len(colors)
        
        # Check legend location
        legend = ax.get_legend()
        assert legend is not None
        # PR curves typically have legend in lower left
        assert legend.get_bbox_to_anchor().transformed(ax.transAxes.inverted()).x0 < 0.5
        
        plt.close('all')
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme probability values."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
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
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        assert fig is not None
        assert all(0 <= v <= 1 for v in metrics['pre_rec_auc'].values() 
                  if not np.isnan(v))
        
        plt.close('all')
    
    def test_baseline_comparison(self):
        """Test comparison with random baseline in PR space."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # For PR curves, the baseline is not a diagonal but depends on class balance
        np.random.seed(42)
        
        # Balanced case
        y_true_balanced = np.array([0, 1] * 50)
        y_proba_random = np.random.rand(100, 2)
        y_proba_random = y_proba_random / y_proba_random.sum(axis=1, keepdims=True)
        
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = pre_rec_auc(plt, y_true_balanced, y_proba_random, labels)
        
        # Random classifier baseline AP ≈ proportion of positive class
        baseline_0 = np.mean(y_true_balanced == 0)
        baseline_1 = np.mean(y_true_balanced == 1)
        
        # Should be close to baseline (with some variance)
        assert abs(metrics['pre_rec_auc'][0] - baseline_0) < 0.15
        assert abs(metrics['pre_rec_auc'][1] - baseline_1) < 0.15
        
        plt.close('all')
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Mismatched dimensions
        with pytest.raises((ValueError, IndexError, AssertionError)):
            y_true = np.array([0, 1, 0])
            y_proba = np.array([[0.5, 0.5], [0.6, 0.4]])  # Wrong size
            labels = ["A", "B"]
            pre_rec_auc(plt, y_true, y_proba, labels)
    
    def test_annotation_positioning(self):
        """Test F1 score annotation positioning."""
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create simple data
        y_true = np.array([0, 1, 0, 1])
        y_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3], [0.4, 0.6]])
        labels = ["Class 0", "Class 1"]
        
        fig, metrics = pre_rec_auc(plt, y_true, y_proba, labels)
        
        ax = fig.axes[0]
        
        # Check for F1 score annotations
        texts = ax.texts
        f1_annotations = [t for t in texts if 'f1=' in t.get_text()]
        
        # Should have annotations for iso-F1 curves
        assert len(f1_annotations) > 0
        
        # Check that annotations are positioned reasonably
        for text in f1_annotations:
            x, y = text.get_position()
            assert -0.2 <= x <= 1.2  # Slightly outside plot bounds is OK
            assert -0.2 <= y <= 1.2
        
        plt.close('all')


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/plt/aucs/pre_rec_auc.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# 
# import warnings
# from itertools import cycle
# 
# import numpy as np
# from sklearn.metrics import average_precision_score, precision_recall_curve
# 
# 
# def solve_the_intersection_of_a_line_and_iso_f1_curve(f1, a, b):
#     """
#     Determines the intersection of the following lines:
#         1) a line: y = a * x + b
#         2) the iso-f1 curve: y = f1 * x / (2 * x - f1)
#     , where a, b, and f1 are the constant values.
#     """
#     _a = 2 * a
#     _b = -a * f1 + 2 * b - f1
#     _c = -b * f1
# 
#     x_f = (-_b + np.sqrt(_b**2 - 4 * _a * _c)) / (2 * _a)
#     y_f = a * x_f + b
# 
#     return (x_f, y_f)
# 
# 
# def to_onehot(labels, n_classes):
#     eye = np.eye(n_classes, dtype=int)
#     return eye[labels]
# 
# 
# def pre_rec_auc(plt, true_class, pred_proba, labels):
#     """
#     Calculates the precision recall curve.
#     """
# 
#     # Use label_binarize to be multi-label like settings
#     n_classes = len(labels)
#     true_class_onehot = to_onehot(true_class, n_classes)
# 
#     # For each class
#     precision = dict()
#     recall = dict()
#     threshold = dict()
#     pre_rec_auc = dict()
#     for i in range(n_classes):
#         true_class_i_onehot = true_class_onehot[:, i]
#         pred_proba_i = pred_proba[:, i]
# 
#         try:
#             precision[i], recall[i], threshold[i] = precision_recall_curve(
#                 true_class_i_onehot,
#                 pred_proba_i,
#             )
#             pre_rec_auc[i] = average_precision_score(true_class_i_onehot, pred_proba_i)
#         except Exception as e:
#             print(e)
#             precision[i], recall[i], threshold[i], pre_rec_auc[i] = (
#                 np.nan,
#                 np.nan,
#                 np.nan,
#                 np.nan,
#             )
# 
#     ## Average precision: micro and macro
# 
#     # A "micro-average": quantifying score on all classes jointly
#     precision["micro"], recall["micro"], threshold["micro"] = precision_recall_curve(
#         true_class_onehot.ravel(), pred_proba.ravel()
#     )
#     pre_rec_auc["micro"] = average_precision_score(
#         true_class_onehot, pred_proba, average="micro"
#     )
# 
#     # macro
#     _pre_rec_aucs = []
#     for i in range(n_classes):
#         try:
#             _pre_rec_aucs.append(
#                 average_precision_score(
#                     true_class_onehot[:, i], pred_proba[:, i], average="macro"
#                 )
#             )
#         except Exception as e:
#             print(
#                 f'\nPRE-REC-AUC for "{labels[i]}" was not defined and NaN-filled '
#                 "for a calculation purpose (for the macro avg.)\n"
#             )
#             _pre_rec_aucs.append(np.nan)
#     pre_rec_auc["macro"] = np.nanmean(_pre_rec_aucs)
# 
#     # pre_rec_auc["macro"] = average_precision_score(
#     #     true_class_onehot, pred_proba, average="macro"
#     # )
# 
#     # Plot Precision-Recall curve for each class and iso-f1 curves
#     colors = cycle(["navy", "turquoise", "darkorange", "cornflowerblue", "teal"])
#     fig, ax = plt.subplots()
#     ax.set_box_aspect(1)
#     lines = []
#     legends = []
# 
#     # iso-F1: By definition, an iso-F1 curve contains all points
#     #         in the precision/recall space whose F1 scores are the same.
#     f_scores = np.linspace(0.2, 0.8, num=4)
#     # for f_score in f_scores:
#     for i_f, f_score in enumerate(f_scores):
#         x = np.linspace(0.01, 1)  # num=50
#         y = f_score * x / (2 * x - f_score)
#         (l,) = ax.plot(x[y >= 0], y[y >= 0], color="gray", alpha=0.2)
# 
#         # ax.annotate("f1={0:0.1f}".format(f_score), xy=(0.9, y[45] + 0.02))
#         x_f, y_f = solve_the_intersection_of_a_line_and_iso_f1_curve(f_score, 0.5, 0.5)
#         ax.annotate("f1={0:0.1f}".format(f_score), xy=(x_f - 0.1, y_f - 0.1 * 0.5))
#         # ax.annotate("f1={0:0.1f}".format(f_score), xy=(y[35] - 0.02 * (3 - i_f), 0.85))
# 
#     lines.append(l)
#     legends.append("iso-f1 curves")
# 
#     """
#     ## In this project, average precision-recall curve is not drawn.
#     (l,) = ax.plot(recall["micro"], precision["micro"], color="gold", lw=2)
#     lines.append(l)
#     legends.append("micro-average\n(AUC = {0:0.2f})" "".format(pre_rec_auc["micro"]))
#     """
# 
#     ## Each Class
#     for i, color in zip(range(n_classes), colors):
#         (l,) = ax.plot(recall[i], precision[i], color=color, lw=2)
#         lines.append(l)
#         legends.append("{0} (AUC = {1:0.2f})" "".format(labels[i], pre_rec_auc[i]))
# 
#     # fig = plt.gcf()
#     fig.subplots_adjust(bottom=0.25)
#     ax.set_xlim([-0.01, 1.01])
#     ax.set_ylim([-0.01, 1.01])
#     ax.set_xticks([0.0, 0.5, 1.0])
#     ax.set_yticks([0.0, 0.5, 1.0])
#     ax.set_xlabel("Recall")
#     ax.set_ylabel("Precision")
#     ax.set_title("Precision-Recall Curve")
#     ax.legend(lines, legends, loc="lower left")
# 
#     metrics = dict(
#         pre_rec_auc=pre_rec_auc,
#         precision=precision,
#         recall=recall,
#         threshold=threshold,
#     )
# 
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
#     pre_rec_auc, precision, recall, threshold = \
#         calc_pre_rec_auc(true_class, pred_proba, labels, plot=False)
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
#     ## Main
#     fig, metrics_dict = pre_rec_auc(plt, y_test, predicted_proba, labels)
# 
#     fig.show()
# 
#     print(metrics_dict.keys())
#     # dict_keys(['pre_rec_auc', 'precision', 'recall', 'threshold'])

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/plt/aucs/pre_rec_auc.py
# --------------------------------------------------------------------------------
