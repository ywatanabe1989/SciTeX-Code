#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-10-01 22:19:43"
# /home/ywatanabe/scitex_repo/tests/scitex/io/test__save_optuna_study_as_csv_and_pngs.py


"""Tests for save_optuna_study_as_csv_and_pngs functionality."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.io import save_optuna_study_as_csv_and_pngs
from unittest.mock import Mock, patch, MagicMock, call
import pandas as pd
import tempfile
import shutil


class TestBasicFunctionality:
    """Test basic functionality of save_optuna_study_as_csv_and_pngs."""

    def test_saves_trials_dataframe(self, tmp_path):
        """Test that trials dataframe is saved correctly."""
        # Create mock study
        study = Mock()
        trials_df = pd.DataFrame(
            {
                "number": [0, 1, 2],
                "value": [0.5, 0.3, 0.7],
                "params_x": [1, 2, 3],
                "params_y": [4, 5, 6],
            }
        )
        study.trials_dataframe.return_value = trials_df
        study.best_params = {"x": 2, "y": 5}

        # Mock visualization functions
        with patch("optuna.visualization.plot_slice") as mock_slice, patch(
            "optuna.visualization.plot_contour"
        ) as mock_contour, patch(
            "optuna.visualization.plot_optimization_history"
        ) as mock_hist, patch(
            "optuna.visualization.plot_parallel_coordinate"
        ) as mock_parallel, patch(
            "optuna.visualization.plot_param_importances"
        ) as mock_importance, patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            # Run function
            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify save was called for CSV
            csv_call = mock_save.call_args_list[0]
            assert csv_call[0][0].equals(trials_df)
            assert csv_call[0][1] == str(tmp_path) + "/trials_df.csv"

    def test_creates_all_visualization_plots(self, tmp_path):
        """Test that all visualization plots are created."""
        # Create mock study
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"x": 1, "y": 2, "z": 3}

        # Mock visualization functions
        mock_plots = {
            "slice": Mock(),
            "contour": Mock(),
            "hist": Mock(),
            "parallel": Mock(),
            "importance": Mock(),
        }

        with patch(
            "optuna.visualization.plot_slice", return_value=mock_plots["slice"]
        ) as mock_slice, patch(
            "optuna.visualization.plot_contour", return_value=mock_plots["contour"]
        ) as mock_contour, patch(
            "optuna.visualization.plot_optimization_history",
            return_value=mock_plots["hist"],
        ) as mock_hist, patch(
            "optuna.visualization.plot_parallel_coordinate",
            return_value=mock_plots["parallel"],
        ) as mock_parallel, patch(
            "optuna.visualization.plot_param_importances",
            return_value=mock_plots["importance"],
        ) as mock_importance, patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify all plot functions were called
            mock_slice.assert_called_once_with(study, params=["x", "y", "z"])
            mock_contour.assert_called_once_with(study, params=["x", "y", "z"])
            mock_hist.assert_called_once_with(study)
            mock_parallel.assert_called_once_with(study, params=["x", "y", "z"])
            mock_importance.assert_called_once_with(study)

    def test_saves_all_plot_files(self, tmp_path):
        """Test that all plot files are saved with correct names."""
        # Create mock study
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"param1": 10}

        # Track save calls
        save_calls = []

        def mock_save(obj, path):
            save_calls.append((obj, path))

        with patch("optuna.visualization.plot_slice", return_value="slice_fig"), patch(
            "optuna.visualization.plot_contour", return_value="contour_fig"
        ), patch(
            "optuna.visualization.plot_optimization_history", return_value="hist_fig"
        ), patch(
            "optuna.visualization.plot_parallel_coordinate", return_value="parallel_fig"
        ), patch(
            "optuna.visualization.plot_param_importances", return_value="importance_fig"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save", side_effect=mock_save
        ):

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Check all files were saved (1 CSV + 5 PNGs)
            assert len(save_calls) == 6

            # Check plot files
            expected_plots = {
                "slice_plot.png": "slice_fig",
                "contour_plot.png": "contour_fig",
                "optim_hist_plot.png": "hist_fig",
                "parallel_coord_plot.png": "parallel_fig",
                "hparam_importances_plot.png": "importance_fig",
            }

            for call in save_calls[1:]:  # Skip CSV
                filename = os.path.basename(call[1])
                assert filename in expected_plots
                assert call[0] == expected_plots[filename]


class TestParameterHandling:
    """Test parameter handling in save_optuna_study_as_csv_and_pngs."""

    def test_handles_empty_best_params(self, tmp_path):
        """Test handling when study has no best params."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {}

        with patch("optuna.visualization.plot_slice") as mock_slice, patch(
            "optuna.visualization.plot_contour"
        ) as mock_contour, patch(
            "optuna.visualization.plot_optimization_history"
        ), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ) as mock_parallel, patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ):

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify empty params list was passed
            mock_slice.assert_called_once_with(study, params=[])
            mock_contour.assert_called_once_with(study, params=[])
            mock_parallel.assert_called_once_with(study, params=[])

    def test_handles_many_hyperparameters(self, tmp_path):
        """Test handling study with many hyperparameters."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        # Create 20 hyperparameters
        study.best_params = {f"param_{i}": i for i in range(20)}

        with patch("optuna.visualization.plot_slice") as mock_slice, patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ):

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify all params were included
            call_params = mock_slice.call_args[1]["params"]
            assert len(call_params) == 20
            assert all(f"param_{i}" in call_params for i in range(20))

    def test_preserves_parameter_order(self, tmp_path):
        """Test that parameter order from best_params is preserved."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        # Use ordered dict to ensure consistent order
        from collections import OrderedDict

        study.best_params = OrderedDict([("z", 3), ("a", 1), ("m", 2)])

        with patch("optuna.visualization.plot_slice") as mock_slice, patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ):

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify order is preserved
            call_params = mock_slice.call_args[1]["params"]
            assert call_params == ["z", "a", "m"]


class TestDirectoryHandling:
    """Test directory handling in save_optuna_study_as_csv_and_pngs."""

    def test_handles_directory_without_trailing_slash(self, tmp_path):
        """Test function works when directory has no trailing slash."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"x": 1}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            # Call without trailing slash
            save_optuna_study_as_csv_and_pngs(study, str(tmp_path))

            # Verify paths are still correct
            csv_path = mock_save.call_args_list[0][0][1]
            assert csv_path == str(tmp_path) + "trials_df.csv"

    def test_handles_nested_directory_path(self, tmp_path):
        """Test saving to nested directory path."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"x": 1}

        nested_dir = tmp_path / "experiments" / "optuna" / "run1"

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(nested_dir) + "/")

            # Verify correct nested path
            csv_path = mock_save.call_args_list[0][0][1]
            assert str(nested_dir) in csv_path

    def test_handles_relative_directory_path(self):
        """Test with relative directory path."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"x": 1}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, "./results/")

            # Verify relative path is preserved
            csv_path = mock_save.call_args_list[0][0][1]
            assert csv_path == "./results/trials_df.csv"


class TestDataFrameContent:
    """Test dataframe content handling."""

    def test_handles_empty_trials_dataframe(self, tmp_path):
        """Test with empty trials dataframe."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame()
        study.best_params = {}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify empty dataframe was saved
            saved_df = mock_save.call_args_list[0][0][0]
            assert isinstance(saved_df, pd.DataFrame)
            assert len(saved_df) == 0

    def test_handles_large_trials_dataframe(self, tmp_path):
        """Test with large trials dataframe."""
        study = Mock()
        # Create large dataframe with 1000 trials
        large_df = pd.DataFrame(
            {
                "number": range(1000),
                "value": [i * 0.001 for i in range(1000)],
                "params_x": range(1000),
                "params_y": range(1000, 2000),
            }
        )
        study.trials_dataframe.return_value = large_df
        study.best_params = {"x": 500, "y": 1500}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify large dataframe was saved
            saved_df = mock_save.call_args_list[0][0][0]
            assert len(saved_df) == 1000

    def test_preserves_all_dataframe_columns(self, tmp_path):
        """Test that all columns in trials dataframe are preserved."""
        study = Mock()
        # Create dataframe with various column types
        df = pd.DataFrame(
            {
                "number": [0, 1],
                "value": [0.5, 0.3],
                "datetime_start": ["2023-01-01", "2023-01-02"],
                "datetime_complete": ["2023-01-01", "2023-01-02"],
                "duration": [100.5, 200.3],
                "params_learning_rate": [0.01, 0.001],
                "params_batch_size": [32, 64],
                "user_attrs_custom": ["a", "b"],
                "system_attrs_test": [1, 2],
            }
        )
        study.trials_dataframe.return_value = df
        study.best_params = {"learning_rate": 0.01, "batch_size": 32}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify all columns preserved
            saved_df = mock_save.call_args_list[0][0][0]
            assert list(saved_df.columns) == list(df.columns)


class TestErrorHandling:
    """Test error handling in save_optuna_study_as_csv_and_pngs."""

    def test_handles_visualization_error_gracefully(self, tmp_path):
        """Test that visualization errors don't stop the entire process."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"x": 1}

        # Make one visualization fail
        with patch(
            "optuna.visualization.plot_slice", side_effect=Exception("Viz error")
        ), patch(
            "optuna.visualization.plot_contour", return_value="contour_fig"
        ), patch(
            "optuna.visualization.plot_optimization_history", return_value="hist_fig"
        ), patch(
            "optuna.visualization.plot_parallel_coordinate", return_value="parallel_fig"
        ), patch(
            "optuna.visualization.plot_param_importances", return_value="importance_fig"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ):

            # Should raise the exception (no error handling in the function)
            with pytest.raises(Exception, match="Viz error"):
                save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

    def test_handles_missing_study_methods(self, tmp_path):
        """Test handling when study is missing expected methods."""
        study = Mock()
        # Remove trials_dataframe method
        del study.trials_dataframe
        study.best_params = {"x": 1}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ):

            with pytest.raises(AttributeError):
                save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

    def test_handles_none_study(self, tmp_path):
        """Test with None study object."""
        with patch("scitex.io._save_optuna_study_as_csv_and_pngs.save"):
            with pytest.raises(AttributeError):
                save_optuna_study_as_csv_and_pngs(None, str(tmp_path) + "/")


class TestIntegrationScenarios:
    """Test integration scenarios for save_optuna_study_as_csv_and_pngs."""

    def test_typical_ml_hyperparameter_tuning_workflow(self, tmp_path):
        """Test typical ML hyperparameter tuning scenario."""
        study = Mock()
        # Simulate 50 trials of hyperparameter tuning
        trials_data = []
        for i in range(50):
            trials_data.append(
                {
                    "number": i,
                    "value": 0.9
                    - (i * 0.01)
                    + (0.1 if i % 5 == 0 else 0),  # Some variance
                    "params_learning_rate": 10 ** (-3 + i * 0.02),
                    "params_batch_size": [16, 32, 64, 128][i % 4],
                    "params_dropout": 0.1 + (i % 10) * 0.05,
                    "state": "COMPLETE",
                    "datetime_start": f"2023-01-01 {i//2:02d}:{i%2*30:02d}:00",
                    "datetime_complete": f"2023-01-01 {i//2:02d}:{i%2*30+1:02d}:00",
                }
            )

        study.trials_dataframe.return_value = pd.DataFrame(trials_data)
        study.best_params = {"learning_rate": 0.001, "batch_size": 32, "dropout": 0.3}

        with patch("optuna.visualization.plot_slice") as mock_slice, patch(
            "optuna.visualization.plot_contour"
        ) as mock_contour, patch(
            "optuna.visualization.plot_optimization_history"
        ) as mock_hist, patch(
            "optuna.visualization.plot_parallel_coordinate"
        ) as mock_parallel, patch(
            "optuna.visualization.plot_param_importances"
        ) as mock_importance, patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/optuna_results/")

            # Verify all components were called correctly
            assert mock_save.call_count == 6  # 1 CSV + 5 plots

            # Verify hyperparameters were passed to relevant plots
            expected_params = ["learning_rate", "batch_size", "dropout"]
            mock_slice.assert_called_once_with(study, params=expected_params)
            mock_contour.assert_called_once_with(study, params=expected_params)
            mock_parallel.assert_called_once_with(study, params=expected_params)

    def test_multi_objective_optimization_scenario(self, tmp_path):
        """Test multi-objective optimization scenario."""
        study = Mock()
        # Multi-objective with accuracy and inference time
        trials_df = pd.DataFrame(
            {
                "number": range(30),
                "values_0": [0.9 + i * 0.002 for i in range(30)],  # accuracy
                "values_1": [100 - i * 2 for i in range(30)],  # inference time (ms)
                "params_model_size": ["small", "medium", "large"] * 10,
                "params_optimization_level": [0, 1, 2] * 10,
            }
        )
        study.trials_dataframe.return_value = trials_df
        study.best_params = {"model_size": "medium", "optimization_level": 1}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify multi-objective data is preserved
            saved_df = mock_save.call_args_list[0][0][0]
            assert "values_0" in saved_df.columns
            assert "values_1" in saved_df.columns

    def test_pruned_trials_scenario(self, tmp_path):
        """Test scenario with pruned trials."""
        study = Mock()
        # Mix of complete and pruned trials
        trials_df = pd.DataFrame(
            {
                "number": range(20),
                "value": [0.5 if i < 10 else float("nan") for i in range(20)],
                "state": ["COMPLETE"] * 10 + ["PRUNED"] * 10,
                "params_x": range(20),
                "params_y": range(20, 40),
            }
        )
        study.trials_dataframe.return_value = trials_df
        study.best_params = {"x": 5, "y": 25}

        with patch("optuna.visualization.plot_slice"), patch(
            "optuna.visualization.plot_contour"
        ), patch("optuna.visualization.plot_optimization_history"), patch(
            "optuna.visualization.plot_parallel_coordinate"
        ), patch(
            "optuna.visualization.plot_param_importances"
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify pruned trials are included
            saved_df = mock_save.call_args_list[0][0][0]
            assert len(saved_df) == 20
            assert (saved_df["state"] == "PRUNED").sum() == 10


class TestVisualizationBehavior:
    """Test specific visualization behavior."""

    def test_figure_objects_passed_to_save(self, tmp_path):
        """Test that actual figure objects are passed to save function."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"x": 1}

        # Create mock figure objects with specific attributes
        mock_figures = {
            "slice": Mock(name="slice_figure"),
            "contour": Mock(name="contour_figure"),
            "hist": Mock(name="hist_figure"),
            "parallel": Mock(name="parallel_figure"),
            "importance": Mock(name="importance_figure"),
        }

        with patch(
            "optuna.visualization.plot_slice", return_value=mock_figures["slice"]
        ), patch(
            "optuna.visualization.plot_contour", return_value=mock_figures["contour"]
        ), patch(
            "optuna.visualization.plot_optimization_history",
            return_value=mock_figures["hist"],
        ), patch(
            "optuna.visualization.plot_parallel_coordinate",
            return_value=mock_figures["parallel"],
        ), patch(
            "optuna.visualization.plot_param_importances",
            return_value=mock_figures["importance"],
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ) as mock_save:

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify each figure was passed to save
            saved_objects = [call[0][0] for call in mock_save.call_args_list[1:]]
            assert mock_figures["slice"] in saved_objects
            assert mock_figures["contour"] in saved_objects
            assert mock_figures["hist"] in saved_objects
            assert mock_figures["parallel"] in saved_objects
            assert mock_figures["importance"] in saved_objects

    def test_consistent_parameter_passing(self, tmp_path):
        """Test that same parameters are passed to all relevant visualizations."""
        study = Mock()
        study.trials_dataframe.return_value = pd.DataFrame({"value": [0.5]})
        study.best_params = {"alpha": 0.1, "beta": 0.2, "gamma": 0.3}

        params_calls = {}

        def track_slice_call(study, **kwargs):
            params_calls["slice"] = kwargs.get("params", [])
            return Mock()

        def track_contour_call(study, **kwargs):
            params_calls["contour"] = kwargs.get("params", [])
            return Mock()

        def track_parallel_call(study, **kwargs):
            params_calls["parallel"] = kwargs.get("params", [])
            return Mock()

        with patch(
            "optuna.visualization.plot_slice", side_effect=track_slice_call
        ), patch(
            "optuna.visualization.plot_contour", side_effect=track_contour_call
        ), patch(
            "optuna.visualization.plot_optimization_history", return_value=Mock()
        ), patch(
            "optuna.visualization.plot_parallel_coordinate",
            side_effect=track_parallel_call,
        ), patch(
            "optuna.visualization.plot_param_importances", return_value=Mock()
        ), patch(
            "scitex.io._save_optuna_study_as_csv_and_pngs.save"
        ):

            save_optuna_study_as_csv_and_pngs(study, str(tmp_path) + "/")

            # Verify same params passed to all
            assert params_calls["slice"] == params_calls["contour"]
            assert params_calls["slice"] == params_calls["parallel"]
            assert set(params_calls["slice"]) == {"alpha", "beta", "gamma"}

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_optuna_study_as_csv_and_pngs.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 17:01:15 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_save_optuna_study_as_csv_and_pngs.py
# 
# 
# def save_optuna_study_as_csv_and_pngs(study, sdir):
#     import optuna
#     from .._save import save
# 
#     ## Trials DataFrame
#     trials_df = study.trials_dataframe()
# 
#     ## Figures
#     hparams_keys = list(study.best_params.keys())
#     slice_plot = optuna.visualization.plot_slice(study, params=hparams_keys)
#     contour_plot = optuna.visualization.plot_contour(study, params=hparams_keys)
#     optim_hist_plot = optuna.visualization.plot_optimization_history(study)
#     parallel_coord_plot = optuna.visualization.plot_parallel_coordinate(
#         study, params=hparams_keys
#     )
#     hparam_importances_plot = optuna.visualization.plot_param_importances(study)
#     figs_dict = dict(
#         slice_plot=slice_plot,
#         contour_plot=contour_plot,
#         optim_hist_plot=optim_hist_plot,
#         parallel_coord_plot=parallel_coord_plot,
#         hparam_importances_plot=hparam_importances_plot,
#     )
# 
#     ## Saves
#     save(trials_df, sdir + "trials_df.csv")
# 
#     for figname, fig in figs_dict.items():
#         save(fig, sdir + f"{figname}.png")
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_optuna_study_as_csv_and_pngs.py
# --------------------------------------------------------------------------------
