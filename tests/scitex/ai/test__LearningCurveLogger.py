#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:00:00"

import warnings
from collections import defaultdict
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from scitex.ai import LearningCurveLogger


class TestLearningCurveLoggerBasic:
    def test_init_default(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        assert hasattr(logger, 'logged_dict')
        assert isinstance(logger.logged_dict, defaultdict)

    def test_init_shows_deprecation_warning(self):
        with pytest.warns(DeprecationWarning, match='gt_label.*will be removed'):
            logger = LearningCurveLogger()


class TestLearningCurveLoggerLogging:
    def test_call_basic_logging(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {
            "loss_plot": 0.5,
            "balanced_ACC_plot": 0.8,
            "i_fold": 0,
            "i_epoch": 1,
            "i_global": 100
        }
        
        logger(metrics, "Training")
        
        assert "Training" in logger.logged_dict
        assert "loss_plot" in logger.logged_dict["Training"]
        assert logger.logged_dict["Training"]["loss_plot"] == [0.5]
        assert logger.logged_dict["Training"]["balanced_ACC_plot"] == [0.8]

    def test_call_multiple_steps(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        train_metrics = {"loss_plot": 0.5, "i_epoch": 1}
        val_metrics = {"loss_plot": 0.3, "i_epoch": 1}
        
        logger(train_metrics, "Training")
        logger(val_metrics, "Validation")
        
        assert "Training" in logger.logged_dict
        assert "Validation" in logger.logged_dict
        assert logger.logged_dict["Training"]["loss_plot"] == [0.5]
        assert logger.logged_dict["Validation"]["loss_plot"] == [0.3]

    def test_call_multiple_epochs(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        for epoch in range(3):
            metrics = {"loss_plot": 0.5 - epoch * 0.1, "i_epoch": epoch}
            logger(metrics, "Training")
        
        expected_losses = [0.5, 0.4, 0.3]
        assert logger.logged_dict["Training"]["loss_plot"] == expected_losses

    def test_call_gt_label_deprecation(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {
            "loss_plot": 0.5,
            "gt_label": np.array([0, 1, 2]),
            "i_epoch": 1
        }
        
        logger(metrics, "Training")
        
        assert "true_class" in logger.logged_dict["Training"]
        assert "gt_label" not in logger.logged_dict["Training"]
        np.testing.assert_array_equal(
            logger.logged_dict["Training"]["true_class"][0], 
            np.array([0, 1, 2])
        )

    def test_call_with_arrays(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        pred_proba = np.array([[0.1, 0.9], [0.8, 0.2]])
        true_class = np.array([1, 0])
        
        metrics = {
            "loss_plot": 0.5,
            "pred_proba": pred_proba,
            "true_class": true_class,
            "i_epoch": 1
        }
        
        logger(metrics, "Training")
        
        np.testing.assert_array_equal(
            logger.logged_dict["Training"]["pred_proba"][0], 
            pred_proba
        )
        np.testing.assert_array_equal(
            logger.logged_dict["Training"]["true_class"][0], 
            true_class
        )


class TestLearningCurveLoggerProperties:
    def test_dfs_property_empty(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        dfs = logger.dfs
        assert isinstance(dfs, dict)
        assert len(dfs) == 0

    def test_dfs_property_with_data(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {
            "loss_plot": 0.5,
            "balanced_ACC_plot": 0.8,
            "i_epoch": 1,
            "i_global": 100
        }
        
        logger(metrics, "Training")
        logger(metrics, "Validation")
        
        dfs = logger.dfs
        assert "Training" in dfs
        assert "Validation" in dfs
        assert isinstance(dfs["Training"], pd.DataFrame)
        assert "loss_plot" in dfs["Training"].columns


class TestLearningCurveLoggerEpochRetrieval:
    def test_get_x_of_i_epoch_basic(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        # Log data for multiple epochs
        for epoch in range(3):
            for batch in range(2):
                metrics = {
                    "loss_plot": 0.5 - epoch * 0.1 + batch * 0.01,
                    "i_epoch": epoch,
                    "i_global": epoch * 2 + batch
                }
                logger(metrics, "Training")
        
        epoch_1_losses = logger.get_x_of_i_epoch("loss_plot", "Training", 1)
        expected_losses = np.array([0.4, 0.41])  # epoch 1 losses
        np.testing.assert_array_almost_equal(epoch_1_losses, expected_losses)

    def test_get_x_of_i_epoch_no_data(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {"loss_plot": 0.5, "i_epoch": 0}
        logger(metrics, "Training")
        
        # Request epoch that doesn't exist
        epoch_5_losses = logger.get_x_of_i_epoch("loss_plot", "Training", 5)
        assert len(epoch_5_losses) == 0


class TestLearningCurveLoggerStaticMethods:
    def test_find_keys_to_plot_empty(self):
        logged_dict = {"Training": {}}
        keys = LearningCurveLogger._find_keys_to_plot(logged_dict)
        assert keys == []

    def test_find_keys_to_plot_with_plot_keys(self):
        logged_dict = {
            "Training": {
                "loss_plot": [0.5],
                "balanced_ACC_plot": [0.8],
                "i_epoch": [1],
                "pred_proba": [np.array([0.1, 0.9])]
            }
        }
        
        keys = LearningCurveLogger._find_keys_to_plot(logged_dict)
        assert "loss_plot" in keys
        assert "balanced_ACC_plot" in keys
        assert "i_epoch" not in keys
        assert "pred_proba" not in keys

    def test_rename_if_key_to_plot_string(self):
        result = LearningCurveLogger._rename_if_key_to_plot("loss_plot")
        assert result == "loss"
        
        result = LearningCurveLogger._rename_if_key_to_plot("balanced_ACC_plot")
        assert result == "balanced_ACC"
        
        result = LearningCurveLogger._rename_if_key_to_plot("i_epoch")
        assert result == "i_epoch"

    def test_rename_if_key_to_plot_pandas_index(self):
        index = pd.Index(["loss_plot", "balanced_ACC_plot", "i_epoch"])
        result = LearningCurveLogger._rename_if_key_to_plot(index)
        
        expected = pd.Index(["loss", "balanced_ACC", "i_epoch"])
        pd.testing.assert_index_equal(result, expected)

    def test_to_dfs_pivot_no_pivot(self):
        logged_dict = {
            "Training": {
                "loss_plot": [0.5, 0.4],
                "i_epoch": [0, 1]
            }
        }
        
        result = LearningCurveLogger._to_dfs_pivot(logged_dict, pivot_column=None)
        
        assert "Training" in result
        assert isinstance(result["Training"], pd.DataFrame)
        assert len(result["Training"]) == 2

    def test_to_dfs_pivot_with_pivot(self):
        logged_dict = {
            "Training": {
                "loss_plot": [0.5, 0.4, 0.45, 0.35],
                "i_epoch": [0, 1, 0, 1],
                "i_global": [0, 2, 1, 3]
            }
        }
        
        result = LearningCurveLogger._to_dfs_pivot(logged_dict, pivot_column="i_epoch")
        
        assert "Training" in result
        df = result["Training"]
        assert len(df) == 2  # 2 unique epochs
        assert df.index.name == "i_epoch"


class TestLearningCurveLoggerPrint:
    @patch('builtins.print')
    @patch('scitex.ai._LearningCurveLogger._pprint')
    def test_print_method(self, mock_pprint, mock_print):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {
            "loss_plot": 0.5,
            "balanced_ACC_plot": 0.8,
            "i_epoch": 1
        }
        logger(metrics, "Training")
        
        logger.print("Training")
        
        assert mock_print.call_count >= 2  # Multiple print calls for formatting
        mock_pprint.assert_called_once()


@pytest.mark.skipif(
    not pytest.importorskip("matplotlib", reason="matplotlib not available"), 
    reason="matplotlib required for plotting tests"
)
class TestLearningCurveLoggerPlotting:
    def test_plot_learning_curves_basic(self):
        import matplotlib.pyplot as plt

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        # Log some training data
        for i in range(10):
            metrics = {
                "loss_plot": 0.5 - i * 0.02,
                "balanced_ACC_plot": 0.5 + i * 0.03,
                "i_epoch": i // 5,
                "i_global": i
            }
            logger(metrics, "Training")
        
        # Log some validation data
        for i in range(0, 10, 5):
            metrics = {
                "loss_plot": 0.4 - i * 0.01,
                "balanced_ACC_plot": 0.6 + i * 0.02,
                "i_epoch": i // 5,
                "i_global": i
            }
            logger(metrics, "Validation")
        
        with patch('scitex.ai._LearningCurveLogger._plt_module.configure_mpl') as mock_configure:
            fig = logger.plot_learning_curves(plt)
        
        assert fig is not None
        assert hasattr(fig, 'axes')
        plt.close(fig)

    def test_plot_learning_curves_with_config(self):
        import matplotlib.pyplot as plt

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {
            "loss_plot": 0.5,
            "i_epoch": 0,
            "i_global": 0
        }
        logger(metrics, "Training")
        
        plt_config = {"figsize": (10, 8)}
        
        with patch('scitex.ai._LearningCurveLogger._plt_module.configure_mpl') as mock_configure:
            fig = logger.plot_learning_curves(
                plt, 
                plt_config_dict=plt_config,
                title="Test Plot",
                max_n_ticks=6,
                linewidth=2,
                scattersize=100
            )
        
        mock_configure.assert_called_once_with(plt, **plt_config)
        assert fig is not None
        plt.close(fig)

    def test_plot_learning_curves_no_plot_keys(self):
        import matplotlib.pyplot as plt

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        # Log data without _plot suffix
        metrics = {
            "loss": 0.5,  # No _plot suffix
            "i_epoch": 0,
            "i_global": 0
        }
        logger(metrics, "Training")
        
        with patch('scitex.plt.utils._configure_mpl'):
            fig = logger.plot_learning_curves(plt)
        
        # Should create empty plot since no _plot keys
        assert fig is not None
        plt.close(fig)


class TestLearningCurveLoggerErrorHandling:
    def test_invalid_step_access(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {"loss_plot": 0.5, "i_epoch": 1}
        logger(metrics, "Training")
        
        # Accessing non-existent step should raise KeyError
        with pytest.raises(KeyError):
            logger.get_x_of_i_epoch("loss_plot", "NonExistentStep", 1)

    def test_invalid_metric_access(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        metrics = {"loss_plot": 0.5, "i_epoch": 1}
        logger(metrics, "Training")
        
        # Accessing non-existent metric should raise KeyError
        with pytest.raises(KeyError):
            logger.get_x_of_i_epoch("NonExistentMetric", "Training", 1)


class TestLearningCurveLoggerIntegration:
    def test_full_workflow_simulation(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        # Simulate 3 epochs of training with multiple batches
        i_global = 0
        for epoch in range(3):
            # Training phase
            for batch in range(5):
                loss = 1.0 - epoch * 0.2 - batch * 0.01
                acc = 0.3 + epoch * 0.2 + batch * 0.01
                
                metrics = {
                    "loss_plot": loss,
                    "balanced_ACC_plot": acc,
                    "pred_proba": np.random.rand(32, 10),
                    "true_class": np.random.randint(0, 10, 32),
                    "i_fold": 0,
                    "i_epoch": epoch,
                    "i_global": i_global
                }
                logger(metrics, "Training")
                i_global += 1
            
            # Validation phase
            val_loss = 0.8 - epoch * 0.15
            val_acc = 0.4 + epoch * 0.15
            
            val_metrics = {
                "loss_plot": val_loss,
                "balanced_ACC_plot": val_acc,
                "pred_proba": np.random.rand(32, 10),
                "true_class": np.random.randint(0, 10, 32),
                "i_fold": 0,
                "i_epoch": epoch,
                "i_global": i_global
            }
            logger(val_metrics, "Validation")
        
        # Verify data structure
        assert len(logger.logged_dict) == 2  # Training and Validation
        assert len(logger.logged_dict["Training"]["loss_plot"]) == 15  # 3 epochs * 5 batches
        assert len(logger.logged_dict["Validation"]["loss_plot"]) == 3  # 3 epochs
        
        # Test epoch-specific retrieval
        epoch_0_losses = logger.get_x_of_i_epoch("loss_plot", "Training", 0)
        assert len(epoch_0_losses) == 5  # 5 batches in epoch 0
        
        # Test DataFrame conversion
        dfs = logger.dfs
        assert "Training" in dfs
        assert "Validation" in dfs


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])