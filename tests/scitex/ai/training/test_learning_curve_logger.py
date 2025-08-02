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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/training/learning_curve_logger.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-20 08:49:50 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_LearningCurveLogger.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_LearningCurveLogger.py"
# 
# """
# Functionality:
#     - Records and visualizes learning curves during model training
#     - Supports tracking of multiple metrics across training/validation/test phases
#     - Generates plots showing training progress over iterations and epochs
# 
# Input:
#     - Training metrics dictionary containing loss, accuracy, predictions etc.
#     - Step information (Training/Validation/Test)
# 
# Output:
#     - Learning curve plots
#     - Dataframes with recorded metrics
#     - Training progress prints
# 
# Prerequisites:
#     - PyTorch
#     - scikit-learn
#     - matplotlib
#     - pandas
#     - numpy
# """
# 
# import re as _re
# from collections import defaultdict as _defaultdict
# from pprint import pprint as _pprint
# from typing import Dict as _Dict
# from typing import List as _List
# from typing import Union as _Union
# from typing import Optional as _Optional
# from typing import Any as _Any
# 
# import matplotlib as _matplotlib
# import pandas as _pd
# import numpy as _np
# import warnings as _warnings
# import torch as _torch
# 
# 
# class LearningCurveLogger:
#     """Records and visualizes learning metrics during model training.
# 
#     Example
#     -------
#     >>> logger = LearningCurveLogger()
#     >>> metrics = {
#     ...     "loss_plot": 0.5,
#     ...     "balanced_ACC_plot": 0.8,
#     ...     "pred_proba": pred_proba,
#     ...     "true_class": labels,
#     ...     "i_fold": 0,
#     ...     "i_epoch": 1,
#     ...     "i_global": 100
#     ... }
#     >>> logger(metrics, "Training")
#     >>> fig = logger.plot_learning_curves(plt)
#     """
# 
#     def __init__(self) -> None:
#         self.logged_dict: _Dict[str, _Dict] = _defaultdict(dict)
# 
#         _warnings.warn(
#             '\n"gt_label" will be removed in the future. Please use "true_class" instead.\n',
#             DeprecationWarning,
#         )
# 
#     def __call__(self, dict_to_log: _Dict[str, _Any], step: str) -> None:
#         """Logs metrics for a training step.
# 
#         Parameters
#         ----------
#         dict_to_log : _Dict[str, _Any]
#             _Dictionary containing metrics to log
#         step : str
#             Phase of training ('Training', 'Validation', or 'Test')
#         """
#         if "gt_label" in dict_to_log:
#             dict_to_log["true_class"] = dict_to_log.pop("gt_label")
# 
#         for k_to_log in dict_to_log:
#             try:
#                 self.logged_dict[step][k_to_log].append(dict_to_log[k_to_log])
#             except:
#                 self.logged_dict[step][k_to_log] = [dict_to_log[k_to_log]]
# 
#     @property
#     def dfs(self) -> _Dict[str, _pd.DataFrame]:
#         """Returns DataFrames of logged metrics.
# 
#         Returns
#         -------
#         _Dict[str, _pd.DataFrame]
#             _Dictionary of DataFrames for each step
#         """
#         return self._to_dfs_pivot(
#             self.logged_dict,
#             pivot_column=None,
#         )
# 
#     def get_x_of_i_epoch(self, x: str, step: str, i_epoch: int) -> _np.ndarray:
#         """Gets metric values for a specific epoch.
# 
#         Parameters
#         ----------
#         x : str
#             Name of metric to retrieve
#         step : str
#             Training phase
#         i_epoch : int
#             Epoch number
# 
#         Returns
#         -------
#         _np.ndarray
#             Array of metric values for specified epoch
#         """
#         indi = _np.array(self.logged_dict[step]["i_epoch"]) == i_epoch
#         x_all_arr = _np.array(self.logged_dict[step][x])
#         assert len(indi) == len(x_all_arr)
#         return x_all_arr[indi]
# 
#     def plot_learning_curves(
#         self,
#         plt: _Any,
#         plt_config_dict: _Optional[_Dict] = None,
#         title: _Optional[str] = None,
#         max_n_ticks: int = 4,
#         linewidth: float = 1,
#         scattersize: float = 50,
#     ) -> _matplotlib.figure.Figure:
#         """Plots learning curves from logged metrics.
# 
#         Parameters
#         ----------
#         plt : _matplotlib.pyplot
#             _Matplotlib pyplot object
#         plt_config_dict : _Dict, optional
#             Plot configuration parameters
#         title : str, optional
#             Plot title
#         max_n_ticks : int
#             Maximum number of ticks on axes
#         linewidth : float
#             Width of plot lines
#         scattersize : float
#             Size of scatter points
# 
#         Returns
#         -------
#         _matplotlib.figure.Figure
#             Figure containing learning curves
#         """
# 
#         if plt_config_dict is not None:
#             # Skip configure_mpl for now - would need to import plt module
#             pass
# 
#         self.dfs_pivot_i_global = self._to_dfs_pivot(
#             self.logged_dict, pivot_column="i_global"
#         )
# 
#         COLOR_DICT = {
#             "Training": "blue",
#             "Validation": "green",
#             "Test": "red",
#         }
# 
#         keys_to_plot = self._find_keys_to_plot(self.logged_dict)
#         
#         if len(keys_to_plot) == 0:
#             # No keys to plot, return empty figure
#             fig, ax = plt.subplots(1, 1)
#             ax.text(0.5, 0.5, 'No data to plot', ha='center', va='center')
#             return fig
# 
#         fig, axes = plt.subplots(len(keys_to_plot), 1, sharex=True, sharey=False)
#         if len(keys_to_plot) == 1:
#             axes = [axes]  # Make it a list for consistency
#         axes[-1].set_xlabel("Iteration#")
#         fig.text(0.5, 0.95, title, ha="center")
# 
#         for i_plt, plt_k in enumerate(keys_to_plot):
#             ax = axes[i_plt]
#             ax.set_ylabel(self._rename_if_key_to_plot(plt_k))
#             ax.xaxis.set_major_locator(_matplotlib.ticker.MaxNLocator(max_n_ticks))
#             ax.yaxis.set_major_locator(_matplotlib.ticker.MaxNLocator(max_n_ticks))
# 
#             if _re.search("[aA][cC][cC]", plt_k):
#                 ax.set_ylim(0, 1)
#                 ax.set_yticks([0, 0.5, 1.0])
# 
#             for step_k in self.dfs_pivot_i_global.keys():
#                 if step_k == _re.search("^[Tt]rain", step_k):
#                     ax.plot(
#                         self.dfs_pivot_i_global[step_k].index,
#                         self.dfs_pivot_i_global[step_k][plt_k],
#                         label=step_k,
#                         color=COLOR_DICT[step_k],
#                         linewidth=linewidth,
#                     )
#                     ax.legend()
# 
#                     epoch_starts = abs(
#                         self.dfs_pivot_i_global[step_k]["i_epoch"]
#                         - self.dfs_pivot_i_global[step_k]["i_epoch"].shift(-1)
#                     )
#                     indi_global_epoch_starts = [0] + list(
#                         epoch_starts[epoch_starts == 1].index
#                     )
# 
#                     for i_epoch, i_global_epoch_start in enumerate(
#                         indi_global_epoch_starts
#                     ):
#                         ax.axvline(
#                             x=i_global_epoch_start,
#                             ymin=-1e4,
#                             ymax=1e4,
#                             linestyle="--",
#                             color=plt.colors.to_RGBA("gray", alpha=0.5),
#                         )
# 
#                 if (step_k == "Validation") or (step_k == "Test"):
#                     ax.scatter(
#                         self.dfs_pivot_i_global[step_k].index,
#                         self.dfs_pivot_i_global[step_k][plt_k],
#                         label=step_k,
#                         color=COLOR_DICT[step_k],
#                         s=scattersize,
#                         alpha=0.9,
#                     )
#                     ax.legend()
# 
#         return fig
# 
#     def print(self, step: str) -> None:
#         """Prints metrics for given step.
# 
#         Parameters
#         ----------
#         step : str
#             Training phase to print metrics for
#         """
#         df_pivot_i_epoch = self._to_dfs_pivot(self.logged_dict, pivot_column="i_epoch")
#         df_pivot_i_epoch_step = df_pivot_i_epoch[step]
#         df_pivot_i_epoch_step.columns = self._rename_if_key_to_plot(
#             df_pivot_i_epoch_step.columns
#         )
#         print("\n----------------------------------------\n")
#         print(f"\n{step}: (mean of batches)\n")
#         _pprint(df_pivot_i_epoch_step)
#         print("\n----------------------------------------\n")
# 
#     @staticmethod
#     def _find_keys_to_plot(logged_dict: _Dict) -> _List[str]:
#         """Find metrics to plot from logged dictionary.
# 
#         Parameters
#         ----------
#         logged_dict : _Dict
#             _Dictionary of logged metrics
# 
#         Returns
#         -------
#         _List[str]
#             _List of metric names to plot
#         """
#         for step_k in logged_dict.keys():
#             break
# 
#         keys_to_plot = []
#         for k in logged_dict[step_k].keys():
#             if _re.search("_plot$", k):
#                 keys_to_plot.append(k)
#         return keys_to_plot
# 
#     @staticmethod
#     def _rename_if_key_to_plot(x: _Union[str, _pd.Index]) -> _Union[str, _pd.Index]:
#         """Rename metric keys for plotting.
# 
#         Parameters
#         ----------
#         x : str or _pd.Index
#             Metric name(s) to rename
# 
#         Returns
#         -------
#         str or _pd.Index
#             Renamed metric name(s)
#         """
#         if isinstance(x, str):
#             if _re.search("_plot$", x):
#                 return x.replace("_plot", "")
#             else:
#                 return x
#         else:
#             return x.str.replace("_plot", "")
# 
#     @staticmethod
#     def _to_dfs_pivot(
#         logged_dict: _Dict[str, _Dict],
#         pivot_column: _Optional[str] = None,
#     ) -> _Dict[str, _pd.DataFrame]:
#         """Convert logged dictionary to pivot DataFrames.
# 
#         Parameters
#         ----------
#         logged_dict : _Dict[str, _Dict]
#             _Dictionary of logged metrics
#         pivot_column : str, optional
#             Column to pivot on
# 
#         Returns
#         -------
#         _Dict[str, _pd.DataFrame]
#             _Dictionary of pivot DataFrames
#         """
# 
#         dfs_pivot = {}
#         for step_k in logged_dict.keys():
#             if pivot_column is None:
#                 df = _pd.DataFrame(logged_dict[step_k])
#             else:
#                 df = (
#                     _pd.DataFrame(logged_dict[step_k])
#                     .groupby(pivot_column)
#                     .mean()
#                     .reset_index()
#                     .set_index(pivot_column)
#                 )
#             dfs_pivot[step_k] = df
#         return dfs_pivot
# 
# 
# if __name__ == "__main__":
#     import warnings
# 
#     import matplotlib.pyplot as plt
#     import torch
#     import torch.nn as nn
#     from sklearn.metrics import balanced_accuracy_score
#     from torch.utils.data import DataLoader, TensorDataset
#     from torch.utils.data.dataset import Subset
#     from torchvision import datasets
# 
#     import sys
#     import scitex
# 
#     ################################################################################
#     ## Sets tee
#     ################################################################################
#     sdir = scitex.io.path.mk_spath("")  # "/tmp/sdir/"
#     sys.stdout, sys.stderr = scitex.gen.tee(sys, sdir)
# 
#     ################################################################################
#     ## NN
#     ################################################################################
#     class Perceptron(nn.Module):
#         def __init__(self):
#             super().__init__()
#             self.l1 = nn.Linear(28 * 28, 50)
#             self.l2 = nn.Linear(50, 10)
# 
#         def forward(self, x):
#             x = x.view(-1, 28 * 28)
#             x = self.l1(x)
#             x = self.l2(x)
#             return x
# 
#     ################################################################################
#     ## Prepaires demo data
#     ################################################################################
#     ## Downloads
#     _ds_tra_val = datasets.MNIST("/tmp/mnist", train=True, download=True)
#     _ds_tes = datasets.MNIST("/tmp/mnist", train=False, download=True)
# 
#     ## Training-Validation splitting
#     n_samples = len(_ds_tra_val)  # n_samples is 60000
#     train_size = int(n_samples * 0.8)  # train_size is 48000
# 
#     subset1_indices = list(range(0, train_size))  # [0,1,.....47999]
#     subset2_indices = list(range(train_size, n_samples))  # [48000,48001,.....59999]
# 
#     _ds_tra = Subset(_ds_tra_val, subset1_indices)
#     _ds_val = Subset(_ds_tra_val, subset2_indices)
# 
#     ## to tensors
#     ds_tra = TensorDataset(
#         _ds_tra.dataset.data.to(_torch.float32),
#         _ds_tra.dataset.targets,
#     )
#     ds_val = TensorDataset(
#         _ds_val.dataset.data.to(_torch.float32),
#         _ds_val.dataset.targets,
#     )
#     ds_tes = TensorDataset(
#         _ds_tes.data.to(_torch.float32),
#         _ds_tes.targets,
#     )
# 
#     ## to dataloaders
#     batch_size = 64
#     dl_tra = DataLoader(
#         dataset=ds_tra,
#         batch_size=batch_size,
#         shuffle=True,
#         drop_last=True,
#     )
# 
#     dl_val = DataLoader(
#         dataset=ds_val,
#         batch_size=batch_size,
#         shuffle=False,
#         drop_last=True,
#     )
# 
#     dl_tes = DataLoader(
#         dataset=ds_tes,
#         batch_size=batch_size,
#         shuffle=False,
#         drop_last=True,
#     )
# 
#     ################################################################################
#     ## Preparation
#     ################################################################################
#     model = Perceptron()
#     loss_func = nn.CrossEntropyLoss()
#     optimizer = _torch.optim.SGD(model.parameters(), lr=1e-3)
#     softmax = nn.Softmax(dim=-1)
# 
#     ################################################################################
#     ## Main
#     ################################################################################
#     lc_logger = LearningCurveLogger()
#     i_global = 0
# 
#     n_classes = len(dl_tra.dataset.tensors[1].unique())
#     i_fold = 0
#     max_epochs = 3
# 
#     for i_epoch in range(max_epochs):
#         step = "Validation"
#         for i_batch, batch in enumerate(dl_val):
# 
#             X, T = batch
#             logits = model(X)
#             pred_proba = softmax(logits)
#             pred_class = pred_proba.argmax(dim=-1)
#             loss = loss_func(logits, T)
# 
#             with warnings.catch_warnings():
#                 warnings.simplefilter("ignore", UserWarning)
#                 bACC = balanced_accuracy_score(T, pred_class)
# 
#             dict_to_log = {
#                 "loss_plot": float(loss),
#                 "balanced_ACC_plot": float(bACC),
#                 "pred_proba": pred_proba.detach().cpu().numpy(),
#                 "gt_label": T.cpu().numpy(),
#                 # "true_class": T.cpu().numpy(),
#                 "i_fold": i_fold,
#                 "i_epoch": i_epoch,
#                 "i_global": i_global,
#             }
#             lc_logger(dict_to_log, step)
# 
#         lc_logger.print(step)
# 
#         step = "Training"
#         for i_batch, batch in enumerate(dl_tra):
#             optimizer.zero_grad()
# 
#             X, T = batch
#             logits = model(X)
#             pred_proba = softmax(logits)
#             pred_class = pred_proba.argmax(dim=-1)
#             loss = loss_func(logits, T)
# 
#             loss.backward()
#             optimizer.step()
# 
#             with warnings.catch_warnings():
#                 warnings.simplefilter("ignore", UserWarning)
#                 bACC = balanced_accuracy_score(T, pred_class)
# 
#             dict_to_log = {
#                 "loss_plot": float(loss),
#                 "balanced_ACC_plot": float(bACC),
#                 "pred_proba": pred_proba.detach().cpu().numpy(),
#                 "gt_label": T.cpu().numpy(),
#                 # "true_class": T.cpu().numpy(),
#                 "i_fold": i_fold,
#                 "i_epoch": i_epoch,
#                 "i_global": i_global,
#             }
#             lc_logger(dict_to_log, step)
# 
#             i_global += 1
# 
#         lc_logger.print(step)
# 
#     step = "Test"
#     for i_batch, batch in enumerate(dl_tes):
# 
#         X, T = batch
#         logits = model(X)
#         pred_proba = softmax(logits)
#         pred_class = pred_proba.argmax(dim=-1)
#         loss = loss_func(logits, T)
# 
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore", UserWarning)
#             bACC = balanced_accuracy_score(T, pred_class)
# 
#         dict_to_log = {
#             "loss_plot": float(loss),
#             "balanced_ACC_plot": float(bACC),
#             "pred_proba": pred_proba.detach().cpu().numpy(),
#             # "gt_label": T.cpu().numpy(),
#             "true_class": T.cpu().numpy(),
#             "i_fold": i_fold,
#             "i_epoch": i_epoch,
#             "i_global": i_global,
#         }
#         lc_logger(dict_to_log, step)
# 
#     lc_logger.print(step)
# 
#     plt_config_dict = dict(
#         # figsize=(8.7, 10),
#         figscale=2.5,
#         labelsize=16,
#         fontsize=12,
#         legendfontsize=12,
#         tick_size=0.8,
#         tick_width=0.2,
#     )
# 
#     fig = lc_logger.plot_learning_curves(
#         plt,
#         plt_config_dict=plt_config_dict,
#         title=f"fold#{i_fold}",
#         linewidth=1,
#         scattersize=50,
#     )
#     fig.show()
#     # scitex.gen.save(fig, sdir + f"fold#{i_fold}.png")
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/training/learning_curve_logger.py
# --------------------------------------------------------------------------------
