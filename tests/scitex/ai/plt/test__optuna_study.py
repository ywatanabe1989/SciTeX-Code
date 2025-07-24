#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 00:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/tests/scitex/ai/plt/test__optuna_study.py

"""
Comprehensive tests for Optuna study visualization functionality
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import tempfile
import os
import shutil
import sqlite3


class TestOptunaStudy:
    """Test class for Optuna study visualization"""
    
    @pytest.fixture
    def mock_study(self):
        """Create a mock Optuna study"""
        study = MagicMock()
        
        # Mock best trial
        best_trial = MagicMock()
        best_trial.number = 5
        best_trial.value = 0.95
        best_trial.params = {'learning_rate': 0.001, 'n_layers': 3}
        best_trial.user_attrs = {'model_type': 'CNN', 'dataset': 'test'}
        study.best_trial = best_trial
        
        # Mock trials
        trials = []
        for i in range(10):
            trial = MagicMock()
            trial.number = i
            trial.value = 0.8 + 0.02 * i
            trial.params = {'learning_rate': 0.001 * (i + 1), 'n_layers': i % 4 + 1}
            trial.user_attrs = {'model_type': 'CNN', 'dataset': 'test', 'SDIR': f'/path/trial_{i}'}
            trials.append(trial)
        study.trials = trials
        
        # Mock directions
        study.directions = [MagicMock(name='MINIMIZE')]
        
        # Mock trials_dataframe
        df_data = {
            'number': list(range(10)),
            'value': [0.8 + 0.02 * i for i in range(10)],
            'params_learning_rate': [0.001 * (i + 1) for i in range(10)],
            'params_n_layers': [i % 4 + 1 for i in range(10)],
            'state': ['COMPLETE'] * 10
        }
        study.trials_dataframe.return_value = pd.DataFrame(df_data)
        
        return study
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield f"sqlite:///{db_path}"
        # Cleanup
        if os.path.exists(db_path.replace("sqlite:///", "")):
            os.unlink(db_path.replace("sqlite:///", ""))
            
    def test_basic_optuna_study(self, mock_study, temp_db_path):
        """Test basic Optuna study visualization"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history') as mock_opt_hist:
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            mock_opt_hist.return_value = MagicMock()
                                            
                                            optuna_study(temp_db_path, "Validation Loss")
                                            
        # Verify load_study was called
        mock_load.assert_called_once_with(study_name=None, storage=temp_db_path)
        
    def test_optuna_study_with_sort(self, mock_study, temp_db_path):
        """Test Optuna study visualization with sorting"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            optuna_study(temp_db_path, "Validation Loss", sort=True)
                                            
                                            # Check that study history was saved
                                            save_calls = [call for call in mock_save.call_args_list 
                                                        if 'study_history.csv' in str(call)]
                                            assert len(save_calls) > 0
                                            
    def test_optuna_study_best_trial_info(self, mock_study, temp_db_path):
        """Test that best trial information is printed"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            with patch('builtins.print') as mock_print:
                                                mock_load.return_value = mock_study
                                                
                                                optuna_study(temp_db_path, "Validation Loss")
                                                
                                                # Verify best trial info was printed
                                                print_calls = mock_print.call_args_list
                                                assert any('Best trial number: 5' in str(call) for call in print_calls)
                                                assert any('Best trial value: 0.95' in str(call) for call in print_calls)
                                                
    def test_optuna_study_save_directory_creation(self, mock_study, temp_db_path):
        """Test that save directory is created correctly"""
        from scitex.ai.plt import optuna_study
        
        # Extract the expected directory from the path
        db_file = temp_db_path.replace("sqlite:///", "")
        expected_dir = db_file.replace(".db", "/")
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            optuna_study(temp_db_path, "Validation Loss")
                                            
                                            # Check save calls use correct directory
                                            for call in mock_save.call_args_list:
                                                if len(call[0]) > 1:
                                                    save_path = call[0][1]
                                                    assert expected_dir in save_path
                                                    
    def test_optuna_study_all_visualizations(self, mock_study, temp_db_path):
        """Test that all visualization types are generated"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        mock_load.return_value = mock_study
                        
                        # Mock all visualization functions
                        viz_funcs = {
                            'plot_optimization_history': MagicMock(return_value=MagicMock()),
                            'plot_param_importances': MagicMock(return_value=MagicMock()),
                            'plot_slice': MagicMock(return_value=MagicMock()),
                            'plot_contour': MagicMock(return_value=MagicMock()),
                            'plot_parallel_coordinate': MagicMock(return_value=MagicMock())
                        }
                        
                        with patch.multiple('optuna.visualization', **viz_funcs):
                            optuna_study(temp_db_path, "Validation Loss")
                            
                            # Verify each visualization was called
                            for func_name, func_mock in viz_funcs.items():
                                func_mock.assert_called_once()
                                
    def test_optuna_study_file_formats(self, mock_study, temp_db_path):
        """Test that visualizations are saved in both PNG and HTML formats"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            optuna_study(temp_db_path, "Validation Loss")
                                            
                                            # Check that both PNG and HTML files are saved
                                            save_paths = [call[0][1] for call in mock_save.call_args_list if len(call[0]) > 1]
                                            
                                            # Expected file types
                                            expected_files = [
                                                'optimization_history.png', 'optimization_history.html',
                                                'param_importances.png', 'param_importances.html',
                                                'slice.png', 'slice.html',
                                                'contour.png', 'contour.html',
                                                'parallel_coordinate.png', 'parallel_coordinate.html'
                                            ]
                                            
                                            for expected in expected_files:
                                                assert any(expected in path for path in save_paths), f"Missing {expected}"
                                                
    def test_optuna_study_symlink_creation(self, mock_study, temp_db_path):
        """Test that symlink to best trial is created"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink') as mock_symlink:
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            with patch('scitex.gen.mv_col') as mock_mv_col:
                                                mock_load.return_value = mock_study
                                                
                                                # Setup mv_col to return a modified dataframe
                                                df = mock_study.trials_dataframe.return_value.copy()
                                                df['SDIR'] = [f'/path/trial_{i}' for i in range(10)]
                                                mock_mv_col.return_value = df
                                                
                                                optuna_study(temp_db_path, "Validation Loss")
                                                
                                                # Verify symlink was created
                                                mock_symlink.assert_called()
                                                
    def test_optuna_study_error_handling(self, mock_study, temp_db_path):
        """Test error handling in optuna_study"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink') as mock_symlink:
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            with patch('builtins.print') as mock_print:
                                                mock_load.return_value = mock_study
                                                
                                                # Make symlink raise an exception
                                                mock_symlink.side_effect = Exception("Symlink error")
                                                
                                                # Should not raise, but print error
                                                optuna_study(temp_db_path, "Validation Loss")
                                                
                                                # Verify error was printed
                                                print_calls = [str(call) for call in mock_print.call_args_list]
                                                assert any('Symlink error' in call for call in print_calls)
                                                
    def test_optuna_study_user_attrs_merge(self, mock_study, temp_db_path):
        """Test that user attributes are properly merged into study history"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            optuna_study(temp_db_path, "Validation Loss")
                                            
                                            # Find the call that saved study_history.csv
                                            csv_save_calls = [call for call in mock_save.call_args_list 
                                                            if len(call[0]) > 1 and 'study_history.csv' in call[0][1]]
                                            
                                            assert len(csv_save_calls) > 0
                                            saved_df = csv_save_calls[0][0][0]
                                            
                                            # Check that user attributes are in the dataframe
                                            assert 'model_type' in saved_df.columns
                                            assert 'dataset' in saved_df.columns
                                            
    def test_optuna_study_minimize_direction(self, mock_study, temp_db_path):
        """Test handling of MINIMIZE optimization direction"""
        from scitex.ai.plt import optuna_study
        
        # Set to MINIMIZE
        mock_study.directions = [MagicMock(name='MINIMIZE')]
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            optuna_study(temp_db_path, "Loss", sort=True)
                                            
                                            # When minimizing and sorting, values should be in ascending order
                                            csv_save_calls = [call for call in mock_save.call_args_list 
                                                            if len(call[0]) > 1 and 'study_history.csv' in call[0][1]]
                                            
                                            if csv_save_calls:
                                                saved_df = csv_save_calls[0][0][0]
                                                # Check if Loss column exists and is sorted
                                                if 'Loss' in saved_df.columns:
                                                    values = saved_df['Loss'].values
                                                    assert all(values[i] <= values[i+1] for i in range(len(values)-1))
                                                    
    def test_optuna_study_maximize_direction(self, mock_study, temp_db_path):
        """Test handling of MAXIMIZE optimization direction"""
        from scitex.ai.plt import optuna_study
        
        # Set to MAXIMIZE
        mock_study.directions = [MagicMock(name='MAXIMIZE')]
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            # Should not raise error
                                            optuna_study(temp_db_path, "Accuracy", sort=True)
                                            
    def test_optuna_study_path_replacement(self, mock_study):
        """Test path replacements in optuna_study"""
        from scitex.ai.plt import optuna_study
        
        # Test with ./ prefix
        lpath = "./test_study.db"
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            mock_load.return_value = mock_study
                                            
                                            optuna_study(lpath, "Metric")
                                            
                                            # Check that ./ was replaced with /
                                            actual_path = mock_load.call_args[1]['storage']
                                            assert not actual_path.startswith('./')
                                            
    def test_optuna_study_sdir_processing(self, mock_study, temp_db_path):
        """Test SDIR processing and RUNNING->FINISHED replacement"""
        from scitex.ai.plt import optuna_study
        
        # Modify trials to have RUNNING in SDIR
        for trial in mock_study.trials:
            trial.user_attrs['SDIR'] = f'/path/RUNNING/trial_{trial.number}'
            
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save') as mock_save:
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            with patch('scitex.gen.mv_col') as mock_mv_col:
                                                mock_load.return_value = mock_study
                                                
                                                # Setup mv_col to return dataframe
                                                df = mock_study.trials_dataframe.return_value.copy()
                                                df['SDIR'] = [f'/path/RUNNING/trial_{i}' for i in range(10)]
                                                mock_mv_col.return_value = df
                                                
                                                optuna_study(temp_db_path, "Metric")
                                                
                                                # Find the saved study history
                                                csv_calls = [call for call in mock_save.call_args_list 
                                                           if len(call[0]) > 1 and 'study_history.csv' in call[0][1]]
                                                
                                                if csv_calls:
                                                    saved_df = csv_calls[0][0][0]
                                                    # Check RUNNING was replaced with FINISHED
                                                    assert all('FINISHED' in str(sdir) for sdir in saved_df['SDIR'])
                                                    assert not any('RUNNING' in str(sdir) for sdir in saved_df['SDIR'])
                                                    
    def test_optuna_study_matplotlib_backend(self, mock_study, temp_db_path):
        """Test that matplotlib backend is set to Agg"""
        from scitex.ai.plt import optuna_study
        
        with patch('matplotlib.use') as mock_use:
            with patch('optuna.load_study') as mock_load:
                with patch('scitex.io.save'):
                    with patch('scitex.gen.symlink'):
                        with patch('matplotlib.pyplot.close'):
                            with patch('optuna.visualization.plot_optimization_history'):
                                with patch('optuna.visualization.plot_param_importances'):
                                    with patch('optuna.visualization.plot_slice'):
                                        with patch('optuna.visualization.plot_contour'):
                                            with patch('optuna.visualization.plot_parallel_coordinate'):
                                                mock_load.return_value = mock_study
                                                
                                                # Import and run to trigger matplotlib.use
                                                import importlib
                                                import scitex.ai.plt._optuna_study
                                                importlib.reload(scitex.ai.plt._optuna_study)
                                                
                                                scitex.ai.plt._optuna_study.optuna_study(temp_db_path, "Metric")
                                                
                                                # Verify Agg backend was set
                                                mock_use.assert_called_with('Agg')
                                                
    def test_optuna_study_configure_mpl(self, mock_study, temp_db_path):
        """Test that matplotlib is configured properly"""
        from scitex.ai.plt import optuna_study
        
        with patch('optuna.load_study') as mock_load:
            with patch('scitex.io.save'):
                with patch('scitex.gen.symlink'):
                    with patch('matplotlib.pyplot.close'):
                        with patch('optuna.visualization.plot_optimization_history'):
                            with patch('optuna.visualization.plot_param_importances'):
                                with patch('optuna.visualization.plot_slice'):
                                    with patch('optuna.visualization.plot_contour'):
                                        with patch('optuna.visualization.plot_parallel_coordinate'):
                                            with patch('scitex.plt.configure_mpl') as mock_configure:
                                                mock_load.return_value = mock_study
                                                mock_configure.return_value = (MagicMock(), {})
                                                
                                                optuna_study(temp_db_path, "Metric")
                                                
                                                # Verify configure_mpl was called with correct scale
                                                mock_configure.assert_called()
                                                call_args = mock_configure.call_args
                                                assert call_args[1]['fig_scale'] == 3


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/plt/_optuna_study.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-30 08:24:55 (ywatanabe)"
# import os
# 
# 
# def optuna_study(lpath, value_str, sort=False):
#     """
#     Loads an Optuna study and generates various visualizations for each target metric.
# 
#     Parameters:
#     - lpath (str): Path to the Optuna study database.
#     - value_str (str): The name of the column to be used as the optimization target.
# 
#     Returns:
#     - None
#     """
#     import matplotlib
# 
#     matplotlib.use("Agg")
#     import matplotlib.pyplot as plt
#     import scitex
#     import optuna
#     import pandas as pd
# 
#     plt, CC = scitex.plt.configure_mpl(plt, fig_scale=3)
# 
#     lpath = lpath.replace("./", "/")
# 
#     study = optuna.load_study(study_name=None, storage=lpath)
# 
#     sdir = lpath.replace("sqlite:///", "./").replace(".db", "/")
# 
#     # To get the best trial:
#     best_trial = study.best_trial
#     print(f"Best trial number: {best_trial.number}")
#     print(f"Best trial value: {best_trial.value}")
#     print(f"Best trial parameters: {best_trial.params}")
#     print(f"Best trial user attributes: {best_trial.user_attrs}")
# 
#     # Merge the user attributes into the study history DataFrame
#     study_history = study.trials_dataframe().rename(columns={"value": value_str})
# 
#     if sort:
#         ascending = "MINIMIZE" in str(study.directions[0])  # [REVISED]
#         study_history = study_history.sort_values([value_str], ascending=ascending)
# 
#     # Add user attributes to the study history DataFrame
#     attrs_df = []
#     for trial in study.trials:
#         user_attrs = trial.user_attrs
#         user_attrs = {k: v for k, v in user_attrs.items()}
#         attrs_df.append({"number": trial.number, **user_attrs})
#     attrs_df = pd.DataFrame(attrs_df).set_index("number")
# 
#     # Updates study history
#     study_history = study_history.merge(
#         attrs_df, left_index=True, right_index=True, how="left"
#     ).set_index("number")
#     try:
#         study_history = scitex.gen.mv_col(study_history, "SDIR", 1)
#         study_history["SDIR"] = study_history["SDIR"].apply(
#             lambda x: str(x).replace("RUNNING", "FINISHED")
#         )
#         best_trial_dir = study_history["SDIR"].iloc[0]
#         scitex.gen.symlink(best_trial_dir, sdir + "best_trial", force=True)
#     except Exception as e:
#         print(e)
#     scitex.io.save(study_history, sdir + "study_history.csv")
#     print(study_history)
# 
#     # To visualize the optimization history:
#     fig = optuna.visualization.plot_optimization_history(study, target_name=value_str)
#     scitex.io.save(fig, sdir + "optimization_history.png")
#     scitex.io.save(fig, sdir + "optimization_history.html")
#     plt.close()
# 
#     # To visualize the parameter importances:
#     fig = optuna.visualization.plot_param_importances(study, target_name=value_str)
#     scitex.io.save(fig, sdir + "param_importances.png")
#     scitex.io.save(fig, sdir + "param_importances.html")
#     plt.close()
# 
#     # To visualize the slice of the study:
#     fig = optuna.visualization.plot_slice(study, target_name=value_str)
#     scitex.io.save(fig, sdir + "slice.png")
#     scitex.io.save(fig, sdir + "slice.html")
#     plt.close()
# 
#     # To visualize the contour plot of the study:
#     fig = optuna.visualization.plot_contour(study, target_name=value_str)
#     scitex.io.save(fig, sdir + "contour.png")
#     scitex.io.save(fig, sdir + "contour.html")
#     plt.close()
# 
#     # To visualize the parallel coordinate plot of the study:
#     fig = optuna.visualization.plot_parallel_coordinate(study, target_name=value_str)
#     scitex.io.save(fig, sdir + "parallel_coordinate.png")
#     scitex.io.save(fig, sdir + "parallel_coordinate.html")
#     plt.close()
# 
# 
# if __name__ == "__main__":
#     import matplotlib.pyplot as plt
#     import scitex
#     scitex.plt.configure_mpl(plt, fig_scale=3)
#     lpath = "sqlite:///scripts/ml/clf/sub_conv_transformer_optuna/optuna_studies/optuna_study_v001.db"
#     lpath = "sqlite:///scripts/ml/clf/rocket_optuna/optuna_studies/optuna_study_v001.db"
#     optuna_study(lpath, "Validation bACC")
#     # scripts/ml/clf/sub_conv_transformer/optuna_studies/optuna_study_v032
# 
#     lpath = "sqlite:///scripts/ml/clf/sub_conv_transformer_optuna/optuna_studies/optuna_study_v020.db"
#     scitex.ml.plt.optuna_study(lpath, "val_loss", sort=True)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/plt/_optuna_study.py
# --------------------------------------------------------------------------------
