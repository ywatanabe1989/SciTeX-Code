#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 09:50:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/ai/plt/aucs/test_example.py

"""Comprehensive tests for scitex.ai.plt.aucs.example module.

This module tests the example functionality for AUC plotting, including
the integration of ROC and PR curve generation with real datasets.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, svm
from sklearn.model_selection import train_test_split
from unittest.mock import patch, MagicMock
import tempfile
import os


class TestAUCsExample:
    """Test suite for the AUCs example module."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Store original rcParams
        self.original_rcParams = plt.rcParams.copy()
        
        yield
        
        # Restore original rcParams
        plt.rcParams.update(self.original_rcParams)
        plt.close('all')
    
    def test_example_imports(self):
        """Test that example module imports work correctly."""
        try:
            from scitex.ai.plt.aucs.example import (
                plt as example_plt,
                np as example_np,
                datasets,
                svm,
                train_test_split
            )
            assert example_plt is not None
            assert example_np is not None
        except ImportError as e:
            pytest.fail(f"Failed to import from example module: {e}")
    
    def test_digits_dataset_loading(self):
        """Test loading and preparing the digits dataset."""
        digits = datasets.load_digits()
        
        assert hasattr(digits, 'images'), "Digits dataset should have images"
        assert hasattr(digits, 'target'), "Digits dataset should have targets"
        
        # Test data reshaping
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        assert data.shape[0] == n_samples
        assert data.shape[1] == 64  # 8x8 images flattened
    
    def test_classifier_setup(self):
        """Test SVM classifier setup and training."""
        digits = datasets.load_digits()
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        # Create classifier
        clf = svm.SVC(gamma=0.001, probability=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            data, digits.target, test_size=0.5, shuffle=False
        )
        
        # Train classifier
        clf.fit(X_train, y_train)
        
        # Test predictions
        predicted_proba = clf.predict_proba(X_test)
        predicted = clf.predict(X_test)
        
        assert predicted_proba.shape[0] == X_test.shape[0]
        assert predicted_proba.shape[1] == len(np.unique(digits.target))
        assert predicted.shape[0] == X_test.shape[0]
    
    def test_matplotlib_configuration(self):
        """Test matplotlib configuration in example."""
        original_font_size = plt.rcParams["font.size"]
        original_legend_size = plt.rcParams["legend.fontsize"]
        original_figsize = plt.rcParams["figure.figsize"]
        
        # Apply example configurations
        plt.rcParams["font.size"] = 20
        plt.rcParams["legend.fontsize"] = "xx-small"
        scale = 0.75
        plt.rcParams["figure.figsize"] = (16 * scale, 9 * scale)
        
        assert plt.rcParams["font.size"] == 20
        assert plt.rcParams["legend.fontsize"] == "xx-small"
        assert plt.rcParams["figure.figsize"] == (16 * scale, 9 * scale)
    
    def test_label_generation(self):
        """Test generation of class labels."""
        n_classes = 10
        labels = ["Class {}".format(i) for i in range(n_classes)]
        
        assert len(labels) == n_classes
        assert labels[0] == "Class 0"
        assert labels[-1] == "Class 9"
    
    @patch('scitex.ai.plt.aucs.roc_auc.roc_auc')
    @patch('scitex.ai.plt.aucs.pre_rec_auc.pre_rec_auc')
    def test_example_workflow_mocked(self, mock_pre_rec, mock_roc):
        """Test the complete example workflow with mocked plotting functions."""
        # Setup mock returns
        mock_fig_roc = MagicMock()
        mock_metrics_roc = {'roc_auc': {i: 0.9 for i in range(10)}}
        mock_roc.return_value = (mock_fig_roc, mock_metrics_roc)
        
        mock_fig_pr = MagicMock()
        mock_metrics_pr = {'pre_rec_auc': {i: 0.8 for i in range(10)}}
        mock_pre_rec.return_value = (mock_fig_pr, mock_metrics_pr)
        
        # Run example workflow
        digits = datasets.load_digits()
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        clf = svm.SVC(gamma=0.001, probability=True)
        X_train, X_test, y_train, y_test = train_test_split(
            data, digits.target, test_size=0.5, shuffle=False
        )
        clf.fit(X_train, y_train)
        predicted_proba = clf.predict_proba(X_test)
        
        n_classes = len(np.unique(digits.target))
        labels = ["Class {}".format(i) for i in range(n_classes)]
        
        # Call plotting functions
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        fig_roc, metrics_roc = roc_auc(plt, y_test, predicted_proba, labels)
        fig_pre_rec, metrics_pre_rec = pre_rec_auc(plt, y_test, predicted_proba, labels)
        
        # Verify calls
        mock_roc.assert_called_once()
        mock_pre_rec.assert_called_once()
    
    def test_example_with_small_dataset(self):
        """Test example functionality with a small synthetic dataset."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create small synthetic dataset
        np.random.seed(42)
        n_samples = 100
        n_classes = 3
        
        # Generate synthetic probabilities
        y_test = np.random.randint(0, n_classes, n_samples)
        predicted_proba = np.random.rand(n_samples, n_classes)
        predicted_proba = predicted_proba / predicted_proba.sum(axis=1, keepdims=True)
        
        labels = ["Class {}".format(i) for i in range(n_classes)]
        
        # Test ROC curve generation
        fig_roc, metrics_roc = roc_auc(plt, y_test, predicted_proba, labels)
        assert fig_roc is not None
        assert 'roc_auc' in metrics_roc
        assert 'fpr' in metrics_roc
        assert 'tpr' in metrics_roc
        
        # Test PR curve generation
        fig_pr, metrics_pr = pre_rec_auc(plt, y_test, predicted_proba, labels)
        assert fig_pr is not None
        assert 'pre_rec_auc' in metrics_pr
        assert 'precision' in metrics_pr
        assert 'recall' in metrics_pr
        
        plt.close('all')
    
    def test_different_classifier_types(self):
        """Test example with different classifier types."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        
        digits = datasets.load_digits()
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        X_train, X_test, y_train, y_test = train_test_split(
            data, digits.target, test_size=0.5, random_state=42
        )
        
        classifiers = [
            svm.SVC(gamma=0.001, probability=True),
            RandomForestClassifier(n_estimators=10, random_state=42),
            LogisticRegression(max_iter=1000, random_state=42)
        ]
        
        for clf in classifiers:
            clf.fit(X_train, y_train)
            predicted_proba = clf.predict_proba(X_test)
            
            assert predicted_proba.shape == (X_test.shape[0], 10)
            assert np.allclose(predicted_proba.sum(axis=1), 1.0)
    
    def test_example_with_binary_classification(self):
        """Test example adapted for binary classification."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Create binary classification problem
        digits = datasets.load_digits()
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        # Convert to binary: 0-4 vs 5-9
        binary_target = (digits.target >= 5).astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            data, binary_target, test_size=0.5, random_state=42
        )
        
        clf = svm.SVC(gamma=0.001, probability=True)
        clf.fit(X_train, y_train)
        predicted_proba = clf.predict_proba(X_test)
        
        labels = ["Low (0-4)", "High (5-9)"]
        
        # Generate curves
        fig_roc, metrics_roc = roc_auc(plt, y_test, predicted_proba, labels)
        fig_pr, metrics_pr = pre_rec_auc(plt, y_test, predicted_proba, labels)
        
        assert fig_roc is not None
        assert fig_pr is not None
        assert len(metrics_roc['roc_auc']) >= 2
        assert len(metrics_pr['pre_rec_auc']) >= 2
        
        plt.close('all')
    
    def test_example_data_splits(self):
        """Test example with different train/test split ratios."""
        digits = datasets.load_digits()
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        split_ratios = [0.2, 0.5, 0.8]
        
        for test_size in split_ratios:
            X_train, X_test, y_train, y_test = train_test_split(
                data, digits.target, test_size=test_size, random_state=42
            )
            
            assert X_train.shape[0] == int(n_samples * (1 - test_size))
            assert X_test.shape[0] == n_samples - X_train.shape[0]
            assert len(y_train) == X_train.shape[0]
            assert len(y_test) == X_test.shape[0]
    
    def test_example_with_csv_output(self):
        """Test example with CSV output functionality."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # Create small dataset
        np.random.seed(42)
        y_test = np.array([0, 1, 2, 0, 1, 2])
        predicted_proba = np.array([
            [0.8, 0.1, 0.1],
            [0.2, 0.7, 0.1],
            [0.1, 0.2, 0.7],
            [0.6, 0.3, 0.1],
            [0.3, 0.5, 0.2],
            [0.2, 0.3, 0.5]
        ])
        labels = ["Class 0", "Class 1", "Class 2"]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sdir = os.path.join(tmpdir, "roc_curves/")
            fig, metrics = roc_auc(plt, y_test, predicted_proba, labels, 
                                 sdir_for_csv=sdir)
            
            # Check if CSV files were created
            assert os.path.exists(sdir)
            for i, label in enumerate(labels):
                csv_file = os.path.join(sdir, f"Class_{i}.csv")
                assert os.path.exists(csv_file)
        
        plt.close('all')
    
    def test_figure_customization(self):
        """Test customization of generated figures."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
        
        # Setup data
        np.random.seed(42)
        y_test = np.array([0, 1, 0, 1, 0, 1])
        predicted_proba = np.array([
            [0.9, 0.1],
            [0.2, 0.8],
            [0.7, 0.3],
            [0.3, 0.7],
            [0.8, 0.2],
            [0.1, 0.9]
        ])
        labels = ["Negative", "Positive"]
        
        # Generate figures
        fig_roc, _ = roc_auc(plt, y_test, predicted_proba, labels)
        fig_pr, _ = pre_rec_auc(plt, y_test, predicted_proba, labels)
        
        # Check figure properties
        assert fig_roc.get_figwidth() > 0
        assert fig_roc.get_figheight() > 0
        assert len(fig_roc.axes) > 0
        
        assert fig_pr.get_figwidth() > 0
        assert fig_pr.get_figheight() > 0
        assert len(fig_pr.axes) > 0
        
        plt.close('all')
    
    def test_edge_case_single_class(self):
        """Test behavior when only one class is present in test data."""
        from scitex.ai.plt.aucs.roc_auc import roc_auc
        
        # All samples belong to class 0
        y_test = np.zeros(10, dtype=int)
        predicted_proba = np.random.rand(10, 3)
        predicted_proba = predicted_proba / predicted_proba.sum(axis=1, keepdims=True)
        labels = ["Class 0", "Class 1", "Class 2"]
        
        # This should handle the edge case gracefully
        fig, metrics = roc_auc(plt, y_test, predicted_proba, labels)
        
        assert fig is not None
        assert metrics is not None
        
        plt.close('all')
    
    def test_reproducibility_with_seed(self):
        """Test that results are reproducible with fixed random seed."""
        from sklearn.datasets import make_classification
        
        # Create reproducible dataset
        X1, y1 = make_classification(n_samples=100, n_features=20, 
                                     n_classes=3, n_informative=15,
                                     random_state=42)
        X2, y2 = make_classification(n_samples=100, n_features=20, 
                                     n_classes=3, n_informative=15,
                                     random_state=42)
        
        assert np.array_equal(X1, X2)
        assert np.array_equal(y1, y2)
        
        # Train classifiers
        clf1 = svm.SVC(gamma=0.001, probability=True, random_state=42)
        clf2 = svm.SVC(gamma=0.001, probability=True, random_state=42)
        
        clf1.fit(X1[:80], y1[:80])
        clf2.fit(X2[:80], y2[:80])
        
        pred1 = clf1.predict_proba(X1[80:])
        pred2 = clf2.predict_proba(X2[80:])
        
        assert np.allclose(pred1, pred2)
    
    def test_example_memory_efficiency(self):
        """Test that example doesn't create memory leaks with plots."""
        import gc
        
        initial_figures = len(plt.get_fignums())
        
        # Run example multiple times
        for _ in range(3):
            from scitex.ai.plt.aucs.roc_auc import roc_auc
            from scitex.ai.plt.aucs.pre_rec_auc import pre_rec_auc
            
            y_test = np.array([0, 1, 0, 1])
            pred_proba = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3], [0.4, 0.6]])
            labels = ["Class 0", "Class 1"]
            
            fig1, _ = roc_auc(plt, y_test, pred_proba, labels)
            fig2, _ = pre_rec_auc(plt, y_test, pred_proba, labels)
            
            plt.close(fig1)
            plt.close(fig2)
        
        gc.collect()
        
        # Check no figures are left open
        final_figures = len(plt.get_fignums())
        assert final_figures == initial_figures


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
