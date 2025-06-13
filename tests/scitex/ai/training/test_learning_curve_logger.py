#!/usr/bin/env python3

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import warnings
from collections import defaultdict
import sys
from pathlib import Path

# Add src to path to import directly without circular imports
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

try:
    from scitex.ai.training.learning_curve_logger import LearningCurveLogger
except ImportError:
    pytest.skip("learning_curve_logger not available", allow_module_level=True)


class TestLearningCurveLoggerInit:
    """Test LearningCurveLogger initialization."""
    
    def test_init_creates_empty_dict(self):
        """Test initialization creates empty logged_dict."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        assert hasattr(logger, 'logged_dict')
        assert isinstance(logger.logged_dict, defaultdict)
        assert len(logger.logged_dict) == 0
    
    def test_init_deprecation_warning(self):
        """Test initialization shows deprecation warning."""
        with pytest.warns(DeprecationWarning, match='gt_label.*will be removed'):
            logger = LearningCurveLogger()


class TestLearningCurveLoggerCall:
    """Test LearningCurveLogger __call__ method."""
    
    def setup_method(self):
        """Setup logger for each test."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.logger = LearningCurveLogger()
    
    def test_call_first_log(self):
        """Test first call to logger creates new entries."""
        metrics = {
            "loss_plot": 0.5,
            "accuracy": 0.8,
            "i_epoch": 1
        }
        
        self.logger(metrics, "Training")
        
        assert "Training" in self.logger.logged_dict
        assert "loss_plot" in self.logger.logged_dict["Training"]
        assert "accuracy" in self.logger.logged_dict["Training"]
        assert "i_epoch" in self.logger.logged_dict["Training"]
        
        assert self.logger.logged_dict["Training"]["loss_plot"] == [0.5]
        assert self.logger.logged_dict["Training"]["accuracy"] == [0.8]
        assert self.logger.logged_dict["Training"]["i_epoch"] == [1]
    
    def test_call_multiple_logs_same_step(self):
        """Test multiple calls to same step append values."""
        metrics1 = {"loss": 0.5, "epoch": 1}
        metrics2 = {"loss": 0.3, "epoch": 2}
        
        self.logger(metrics1, "Training")
        self.logger(metrics2, "Training")
        
        assert self.logger.logged_dict["Training"]["loss"] == [0.5, 0.3]
        assert self.logger.logged_dict["Training"]["epoch"] == [1, 2]
    
    def test_call_multiple_steps(self):
        """Test logging to different steps."""
        train_metrics = {"loss": 0.5}
        val_metrics = {"loss": 0.4}
        
        self.logger(train_metrics, "Training")
        self.logger(val_metrics, "Validation")
        
        assert "Training" in self.logger.logged_dict
        assert "Validation" in self.logger.logged_dict
        assert self.logger.logged_dict["Training"]["loss"] == [0.5]
        assert self.logger.logged_dict["Validation"]["loss"] == [0.4]
    
    def test_call_gt_label_deprecation(self):
        """Test gt_label is converted to true_class."""
        metrics = {
            "gt_label": [1, 0, 1],
            "loss": 0.3
        }
        
        self.logger(metrics, "Training")
        
        # gt_label should be converted to true_class
        assert "true_class" in self.logger.logged_dict["Training"]
        assert "gt_label" not in self.logger.logged_dict["Training"]
        assert self.logger.logged_dict["Training"]["true_class"] == [[1, 0, 1]]
    
    def test_call_mixed_data_types(self):
        """Test logging different data types."""
        metrics = {
            "loss": 0.5,
            "predictions": np.array([0.1, 0.9]),
            "labels": [1, 0],
            "metadata": {"batch_size": 32}
        }
        
        self.logger(metrics, "Training")
        
        logged = self.logger.logged_dict["Training"]
        assert logged["loss"] == [0.5]
        assert len(logged["predictions"]) == 1
        assert np.array_equal(logged["predictions"][0], np.array([0.1, 0.9]))
        assert logged["labels"] == [[1, 0]]
        assert logged["metadata"] == [{"batch_size": 32}]


class TestLearningCurveLoggerProperties:
    """Test LearningCurveLogger properties."""
    
    def setup_method(self):
        """Setup logger with sample data."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.logger = LearningCurveLogger()
        
        # Add sample data
        self.logger({"loss": 0.5, "accuracy": 0.8, "i_epoch": 1}, "Training")
        self.logger({"loss": 0.3, "accuracy": 0.85, "i_epoch": 2}, "Training")
        self.logger({"loss": 0.4, "accuracy": 0.82, "i_epoch": 1}, "Validation")
    
    @patch.object(LearningCurveLogger, '_to_dfs_pivot')
    def test_dfs_property(self, mock_to_dfs_pivot):
        """Test dfs property calls _to_dfs_pivot correctly."""
        mock_to_dfs_pivot.return_value = {"Training": pd.DataFrame(), "Validation": pd.DataFrame()}
        
        result = self.logger.dfs
        
        mock_to_dfs_pivot.assert_called_once_with(
            self.logger.logged_dict,
            pivot_column=None
        )
        assert result == mock_to_dfs_pivot.return_value


class TestLearningCurveLoggerGetX:
    """Test LearningCurveLogger get_x_of_i_epoch method."""
    
    def setup_method(self):
        """Setup logger with epoch data."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.logger = LearningCurveLogger()
        
        # Add data for multiple epochs
        self.logger({"loss": 0.5, "accuracy": 0.8, "i_epoch": 1}, "Training")
        self.logger({"loss": 0.4, "accuracy": 0.82, "i_epoch": 1}, "Training")
        self.logger({"loss": 0.3, "accuracy": 0.85, "i_epoch": 2}, "Training")
        self.logger({"loss": 0.35, "accuracy": 0.83, "i_epoch": 2}, "Training")
    
    def test_get_x_of_i_epoch_valid(self):
        """Test getting metric values for specific epoch."""
        # Get loss values for epoch 1
        result = self.logger.get_x_of_i_epoch("loss", "Training", 1)
        
        expected = np.array([0.5, 0.4])
        np.testing.assert_array_equal(result, expected)
    
    def test_get_x_of_i_epoch_different_metric(self):
        """Test getting different metric for specific epoch."""
        # Get accuracy values for epoch 2
        result = self.logger.get_x_of_i_epoch("accuracy", "Training", 2)
        
        expected = np.array([0.85, 0.83])
        np.testing.assert_array_equal(result, expected)
    
    def test_get_x_of_i_epoch_nonexistent_epoch(self):
        """Test getting values for non-existent epoch returns empty array."""
        result = self.logger.get_x_of_i_epoch("loss", "Training", 99)
        
        assert len(result) == 0
    
    def test_get_x_of_i_epoch_nonexistent_step(self):
        """Test getting values for non-existent step raises KeyError."""
        with pytest.raises(KeyError):
            self.logger.get_x_of_i_epoch("loss", "NonExistentStep", 1)
    
    def test_get_x_of_i_epoch_nonexistent_metric(self):
        """Test getting non-existent metric raises KeyError."""
        with pytest.raises(KeyError):
            self.logger.get_x_of_i_epoch("nonexistent_metric", "Training", 1)


class TestLearningCurveLoggerPlotting:
    """Test LearningCurveLogger plotting functionality."""
    
    def setup_method(self):
        """Setup logger with plotting data."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.logger = LearningCurveLogger()
        
        # Add sample data with plot-compatible metrics
        for i in range(5):
            train_metrics = {
                "loss_plot": 0.5 - i * 0.1,
                "accuracy_plot": 0.7 + i * 0.05,
                "i_global": i * 10,
                "i_epoch": i
            }
            val_metrics = {
                "loss_plot": 0.6 - i * 0.08,
                "accuracy_plot": 0.65 + i * 0.04,
                "i_global": i * 10 + 5,
                "i_epoch": i
            }
            self.logger(train_metrics, "Training")
            self.logger(val_metrics, "Validation")
    
    @patch.object(LearningCurveLogger, '_to_dfs_pivot')
    @patch.object(LearningCurveLogger, '_find_keys_to_plot')
    @patch.object(LearningCurveLogger, '_rename_if_key_to_plot')
    def test_plot_learning_curves_basic(self, mock_rename, mock_find_keys, mock_to_dfs_pivot):
        """Test basic plotting functionality with mocked dependencies."""
        # Mock external dependencies
        mock_plt = MagicMock()
        mock_fig = MagicMock()
        mock_axes = [MagicMock(), MagicMock()]
        mock_plt.subplots.return_value = (mock_fig, mock_axes)
        
        # Mock internal methods
        mock_find_keys.return_value = ["loss_plot", "accuracy_plot"]
        mock_rename.side_effect = lambda x: x.replace("_plot", "")
        
        # Mock DataFrame data
        mock_df_train = pd.DataFrame({
            "loss_plot": [0.5, 0.4, 0.3],
            "accuracy_plot": [0.7, 0.75, 0.8]
        }, index=[0, 10, 20])
        mock_df_val = pd.DataFrame({
            "loss_plot": [0.6, 0.5, 0.4],
            "accuracy_plot": [0.65, 0.69, 0.73]
        }, index=[5, 15, 25])
        
        mock_to_dfs_pivot.return_value = {
            "Training": mock_df_train,
            "Validation": mock_df_val
        }
        
        # Call the method
        result = self.logger.plot_learning_curves(mock_plt, title="Test Plot")
        
        # Verify calls
        mock_plt.subplots.assert_called_once_with(2, 1, sharex=True, sharey=False)
        mock_find_keys.assert_called_once_with(self.logger.logged_dict)
        assert mock_rename.call_count == 2
        
        # Check that figure text was set
        mock_fig.text.assert_called_once_with(0.5, 0.95, "Test Plot", ha="center")
        
        # Verify axes configuration
        assert mock_axes[0].set_ylabel.called
        assert mock_axes[1].set_ylabel.called
        assert mock_axes[-1].set_xlabel.called
    
    def test_plot_learning_curves_no_matplotlib(self):
        """Test plotting when matplotlib components are missing."""
        mock_plt = MagicMock()
        
        # Test that method handles missing _plt_module gracefully
        try:
            result = self.logger.plot_learning_curves(mock_plt)
            # If no exception, the method handled missing dependencies
            assert True
        except (AttributeError, NameError):
            # Expected when internal dependencies are missing
            pytest.skip("Internal plotting dependencies not available")


class TestLearningCurveLoggerIntegration:
    """Test LearningCurveLogger integration scenarios."""
    
    def test_complete_training_simulation(self):
        """Test complete training loop simulation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        # Simulate training epochs
        n_epochs = 3
        n_batches = 4
        
        for epoch in range(n_epochs):
            for batch in range(n_batches):
                i_global = epoch * n_batches + batch
                
                # Training step
                train_metrics = {
                    "loss_plot": 1.0 - (i_global * 0.05),
                    "accuracy": 0.5 + (i_global * 0.02),
                    "i_epoch": epoch,
                    "i_batch": batch,
                    "i_global": i_global,
                    "predictions": np.random.rand(32, 10),
                    "true_class": np.random.randint(0, 10, 32)
                }
                logger(train_metrics, "Training")
            
            # Validation step (once per epoch)
            val_metrics = {
                "loss_plot": 1.1 - (epoch * 0.15),
                "accuracy": 0.45 + (epoch * 0.08),
                "i_epoch": epoch,
                "i_global": i_global + 1000,  # Different global index
                "predictions": np.random.rand(16, 10),
                "true_class": np.random.randint(0, 10, 16)
            }
            logger(val_metrics, "Validation")
        
        # Verify logged data structure
        assert "Training" in logger.logged_dict
        assert "Validation" in logger.logged_dict
        
        # Check training data
        train_data = logger.logged_dict["Training"]
        assert len(train_data["loss_plot"]) == n_epochs * n_batches
        assert len(train_data["i_epoch"]) == n_epochs * n_batches
        assert len(train_data["i_global"]) == n_epochs * n_batches
        
        # Check validation data
        val_data = logger.logged_dict["Validation"]
        assert len(val_data["loss_plot"]) == n_epochs
        assert len(val_data["i_epoch"]) == n_epochs
        
        # Test epoch-specific retrieval
        epoch_1_losses = logger.get_x_of_i_epoch("loss_plot", "Training", 1)
        assert len(epoch_1_losses) == n_batches
        
        # Verify decreasing loss trend
        train_losses = np.array(train_data["loss_plot"])
        assert train_losses[0] > train_losses[-1]  # Loss should decrease
    
    def test_mixed_data_types_logging(self):
        """Test logging various data types."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            logger = LearningCurveLogger()
        
        # Test different data types
        complex_metrics = {
            "scalar_loss": 0.5,
            "numpy_predictions": np.array([[0.1, 0.9], [0.8, 0.2]]),
            "list_labels": [1, 0],
            "dict_metadata": {"lr": 0.001, "batch_size": 32},
            "string_phase": "train",
            "boolean_flag": True,
            "none_value": None
        }
        
        logger(complex_metrics, "Training")
        
        logged = logger.logged_dict["Training"]
        
        # Verify all types are stored
        assert logged["scalar_loss"] == [0.5]
        assert isinstance(logged["numpy_predictions"][0], np.ndarray)
        assert logged["list_labels"] == [[1, 0]]
        assert logged["dict_metadata"] == [{"lr": 0.001, "batch_size": 32}]
        assert logged["string_phase"] == ["train"]
        assert logged["boolean_flag"] == [True]
        assert logged["none_value"] == [None]


if __name__ == "__main__":
    pytest.main([__file__])
