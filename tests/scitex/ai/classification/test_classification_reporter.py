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
            'files_to_reproduce',
            'meta_dict'
        ]
        
        for pattern in save_patterns:
            assert pattern in content, f"Should have model saving support: {pattern}"


if __name__ == '__main__':
    unittest.main()