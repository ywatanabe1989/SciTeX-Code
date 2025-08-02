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

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_LearningCurveLogger.py
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
# # Import scitex modules for plotting
# try:
#     import scitex.plt.utils as _plt_utils
#     import scitex.plt.color as _plt_color
#     
#     class _plt_module:
#         configure_mpl = _plt_utils.configure_mpl
#         colors = _plt_color
# except ImportError:
#     # Mock for testing when scitex is not available
#     class _plt_module:
#         @staticmethod
#         def configure_mpl(*args, **kwargs):
#             pass
#         
#         class colors:
#             @staticmethod
#             def to_RGBA(color, alpha=1.0):
#                 return color
#             
#             @staticmethod
#             def to_rgba(color, alpha=1.0):
#                 return color
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
#             _plt_module.configure_mpl(plt, **plt_config_dict)
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
#             # Create empty plot when no plot keys found
#             fig, axes = plt.subplots(1, 1)
#             axes.set_xlabel("Iteration#")
#             axes.set_ylabel("No metrics to plot")
#             fig.text(0.5, 0.95, title, ha="center")
#             return fig
# 
#         fig, axes = plt.subplots(len(keys_to_plot), 1, sharex=True, sharey=False)
#         
#         # Handle both single and multiple axes cases
#         if len(keys_to_plot) == 1:
#             axes = [axes]  # Make it a list for consistent indexing
#         
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
#                         color=_plt_module.colors.to_rgba(COLOR_DICT[step_k], alpha=0.9),
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
#                             color=_plt_module.colors.to_rgba("gray", alpha=0.5),
#                         )
# 
#                 if (step_k == "Validation") or (step_k == "Test"):
#                     ax.scatter(
#                         self.dfs_pivot_i_global[step_k].index,
#                         self.dfs_pivot_i_global[step_k][plt_k],
#                         label=step_k,
#                         color=_plt_module.colors.to_rgba(COLOR_DICT[step_k], alpha=0.9),
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
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_LearningCurveLogger.py
# --------------------------------------------------------------------------------
