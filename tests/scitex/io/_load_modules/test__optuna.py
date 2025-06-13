#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:15:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__optuna.py

"""Comprehensive tests for Optuna study and YAML configuration loading functionality."""

import os
import tempfile
import pytest
import yaml
from unittest.mock import patch, MagicMock


class TestLoadOptunaFunctions:
    """Test suite for Optuna loading functions"""
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_load_yaml_as_optuna_dict_categorical(self, mock_load):
        """Test YAML to Optuna dict conversion with categorical parameters"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Mock YAML data with categorical parameter
        yaml_data = {
            'optimizer': {
                'distribution': 'categorical',
                'values': ['adam', 'sgd', 'rmsprop']
            },
            'activation': {
                'distribution': 'categorical', 
                'values': ['relu', 'tanh', 'sigmoid']
            }
        }
        mock_load.return_value = yaml_data
        
        # Mock trial object
        mock_trial = MagicMock()
        mock_trial.suggest_categorical.side_effect = lambda k, v: v[0]  # Return first value
        
        # Call function
        result = load_yaml_as_an_optuna_dict('config.yaml', mock_trial)
        
        # Verify load was called
        mock_load.assert_called_once_with('config.yaml')
        
        # Verify trial.suggest_categorical was called correctly
        mock_trial.suggest_categorical.assert_any_call('optimizer', ['adam', 'sgd', 'rmsprop'])
        mock_trial.suggest_categorical.assert_any_call('activation', ['relu', 'tanh', 'sigmoid'])
        
        # Verify results
        assert result['optimizer'] == 'adam'
        assert result['activation'] == 'relu'
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_load_yaml_as_optuna_dict_uniform(self, mock_load):
        """Test YAML to Optuna dict conversion with uniform parameters"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Mock YAML data with uniform parameter
        yaml_data = {
            'batch_size': {
                'distribution': 'uniform',
                'min': 16,
                'max': 128
            },
            'epochs': {
                'distribution': 'uniform',
                'min': 10,
                'max': 100
            }
        }
        mock_load.return_value = yaml_data
        
        # Mock trial object
        mock_trial = MagicMock()
        mock_trial.suggest_int.side_effect = lambda k, min_val, max_val: min_val + 1
        
        # Call function
        result = load_yaml_as_an_optuna_dict('config.yaml', mock_trial)
        
        # Verify trial.suggest_int was called correctly
        mock_trial.suggest_int.assert_any_call('batch_size', 16.0, 128.0)
        mock_trial.suggest_int.assert_any_call('epochs', 10.0, 100.0)
        
        # Verify results
        assert result['batch_size'] == 17  # min_val + 1
        assert result['epochs'] == 11     # min_val + 1
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_load_yaml_as_optuna_dict_loguniform(self, mock_load):
        """Test YAML to Optuna dict conversion with loguniform parameters"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Mock YAML data with loguniform parameter
        yaml_data = {
            'learning_rate': {
                'distribution': 'loguniform',
                'min': 1e-5,
                'max': 1e-1
            },
            'weight_decay': {
                'distribution': 'loguniform',
                'min': 1e-6,
                'max': 1e-3
            }
        }
        mock_load.return_value = yaml_data
        
        # Mock trial object
        mock_trial = MagicMock()
        mock_trial.suggest_loguniform.side_effect = lambda k, min_val, max_val: min_val * 10
        
        # Call function
        result = load_yaml_as_an_optuna_dict('config.yaml', mock_trial)
        
        # Verify trial.suggest_loguniform was called correctly
        mock_trial.suggest_loguniform.assert_any_call('learning_rate', 1e-5, 1e-1)
        mock_trial.suggest_loguniform.assert_any_call('weight_decay', 1e-6, 1e-3)
        
        # Verify results
        assert result['learning_rate'] == 1e-4   # min_val * 10
        assert result['weight_decay'] == 1e-5    # min_val * 10
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_load_yaml_as_optuna_dict_intloguniform(self, mock_load):
        """Test YAML to Optuna dict conversion with intloguniform parameters"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Mock YAML data with intloguniform parameter
        yaml_data = {
            'hidden_size': {
                'distribution': 'intloguniform',
                'min': 8,
                'max': 512
            }
        }
        mock_load.return_value = yaml_data
        
        # Mock trial object
        mock_trial = MagicMock()
        mock_trial.suggest_int.side_effect = lambda k, min_val, max_val, log=False: int(min_val * 2)
        
        # Call function
        result = load_yaml_as_an_optuna_dict('config.yaml', mock_trial)
        
        # Verify trial.suggest_int was called with log=True
        mock_trial.suggest_int.assert_called_once_with('hidden_size', 8.0, 512.0, log=True)
        
        # Verify results
        assert result['hidden_size'] == 16  # int(min_val * 2)
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_load_yaml_as_optuna_dict_mixed_parameters(self, mock_load):
        """Test YAML to Optuna dict conversion with mixed parameter types"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Mock YAML data with mixed parameters
        yaml_data = {
            'optimizer': {
                'distribution': 'categorical',
                'values': ['adam', 'sgd']
            },
            'learning_rate': {
                'distribution': 'loguniform',
                'min': 1e-4,
                'max': 1e-1
            },
            'batch_size': {
                'distribution': 'uniform',
                'min': 32,
                'max': 256
            },
            'hidden_layers': {
                'distribution': 'intloguniform',
                'min': 1,
                'max': 8
            }
        }
        mock_load.return_value = yaml_data
        
        # Mock trial object
        mock_trial = MagicMock()
        mock_trial.suggest_categorical.return_value = 'adam'
        mock_trial.suggest_loguniform.return_value = 0.001
        mock_trial.suggest_int.side_effect = lambda k, min_val, max_val, log=False: 64 if not log else 2
        
        # Call function
        result = load_yaml_as_an_optuna_dict('config.yaml', mock_trial)
        
        # Verify all suggestion methods were called
        mock_trial.suggest_categorical.assert_called_once()
        mock_trial.suggest_loguniform.assert_called_once()
        assert mock_trial.suggest_int.call_count == 2
        
        # Verify results
        assert result['optimizer'] == 'adam'
        assert result['learning_rate'] == 0.001
        assert result['batch_size'] == 64
        assert result['hidden_layers'] == 2
    
    @patch('scitex.io._load_modules._optuna.optuna')
    def test_load_study_rdb_basic(self, mock_optuna):
        """Test loading Optuna study from RDB storage"""
from scitex.io._load_modules import load_study_rdb
        
        # Mock storage and study
        mock_storage = MagicMock()
        mock_study = MagicMock()
        mock_optuna.storages.RDBStorage.return_value = mock_storage
        mock_optuna.load_study.return_value = mock_study
        
        # Call function
        study_name = 'test_study'
        rdb_url = 'sqlite:///test.db'
        result = load_study_rdb(study_name, rdb_url)
        
        # Verify storage creation
        mock_optuna.storages.RDBStorage.assert_called_once_with(url=rdb_url)
        
        # Verify study loading
        mock_optuna.load_study.assert_called_once_with(study_name=study_name, storage=mock_storage)
        
        # Verify result
        assert result == mock_study
    
    @patch('scitex.io._load_modules._optuna.optuna')
    def test_load_study_rdb_different_storage_types(self, mock_optuna):
        """Test loading studies from different RDB storage types"""
from scitex.io._load_modules import load_study_rdb
        
        mock_storage = MagicMock()
        mock_study = MagicMock()
        mock_optuna.storages.RDBStorage.return_value = mock_storage
        mock_optuna.load_study.return_value = mock_study
        
        # Test different storage URLs
        storage_urls = [
            'sqlite:///path/to/study.db',
            'postgresql://user:password@localhost/dbname',
            'mysql://user:password@localhost/dbname'
        ]
        
        for url in storage_urls:
            mock_optuna.storages.RDBStorage.reset_mock()
            mock_optuna.load_study.reset_mock()
            
            result = load_study_rdb('test_study', url)
            
            mock_optuna.storages.RDBStorage.assert_called_once_with(url=url)
            mock_optuna.load_study.assert_called_once_with(study_name='test_study', storage=mock_storage)
            assert result == mock_study
    
    @patch('scitex.io._load_modules._optuna.optuna')
    def test_load_study_rdb_error_handling(self, mock_optuna):
        """Test error handling in study loading"""
from scitex.io._load_modules import load_study_rdb
        import optuna
        
        # Test storage creation error
        mock_optuna.storages.RDBStorage.side_effect = Exception("Invalid storage URL")
        
        with pytest.raises(Exception, match="Invalid storage URL"):
            load_study_rdb('test_study', 'invalid://url')
        
        # Reset and test study loading error
        mock_optuna.storages.RDBStorage.side_effect = None
        mock_storage = MagicMock()
        mock_optuna.storages.RDBStorage.return_value = mock_storage
        mock_optuna.load_study.side_effect = optuna.exceptions.StorageInvalidUsageError("Study not found")
        
        with pytest.raises(optuna.exceptions.StorageInvalidUsageError, match="Study not found"):
            load_study_rdb('nonexistent_study', 'sqlite:///test.db')
    
    @patch('scitex.io._load_modules._optuna.optuna')
    @patch('builtins.print')
    def test_load_study_rdb_prints_message(self, mock_print, mock_optuna):
        """Test that load_study_rdb prints loading message"""
from scitex.io._load_modules import load_study_rdb
        
        mock_storage = MagicMock()
        mock_study = MagicMock()
        mock_optuna.storages.RDBStorage.return_value = mock_storage
        mock_optuna.load_study.return_value = mock_study
        
        rdb_url = 'sqlite:///test_study.db'
        load_study_rdb('test_study', rdb_url)
        
        # Verify print was called with the URL
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert rdb_url in call_args
    
    def test_function_signatures(self):
        """Test function signatures and docstrings"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict, load_study_rdb
        import inspect
        
        # Test load_yaml_as_an_optuna_dict signature
        sig1 = inspect.signature(load_yaml_as_an_optuna_dict)
        assert 'fpath_yaml' in sig1.parameters
        assert 'trial' in sig1.parameters
        
        # Test load_study_rdb signature
        sig2 = inspect.signature(load_study_rdb)
        assert 'study_name' in sig2.parameters
        assert 'rdb_raw_bytes_url' in sig2.parameters
        
        # Test docstrings
        assert load_yaml_as_an_optuna_dict.__doc__ is not None
        assert 'YAML' in load_yaml_as_an_optuna_dict.__doc__
        assert 'Optuna' in load_yaml_as_an_optuna_dict.__doc__
        
        assert load_study_rdb.__doc__ is not None
        assert 'study' in load_study_rdb.__doc__.lower()
        assert 'RDB' in load_study_rdb.__doc__
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_yaml_parameter_edge_cases(self, mock_load):
        """Test edge cases in YAML parameter processing"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Test with string min/max values (should be converted to float)
        yaml_data = {
            'param1': {
                'distribution': 'uniform',
                'min': '10',  # String value
                'max': '100'  # String value
            }
        }
        mock_load.return_value = yaml_data
        
        mock_trial = MagicMock()
        mock_trial.suggest_int.return_value = 50
        
        result = load_yaml_as_an_optuna_dict('config.yaml', mock_trial)
        
        # Verify string values were converted to float
        mock_trial.suggest_int.assert_called_once_with('param1', 10.0, 100.0)
        assert result['param1'] == 50
    
    @patch('scitex.io._load_modules._optuna.load')
    def test_empty_yaml_handling(self, mock_load):
        """Test handling of empty YAML configuration"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Empty YAML data
        mock_load.return_value = {}
        mock_trial = MagicMock()
        
        result = load_yaml_as_an_optuna_dict('empty.yaml', mock_trial)
        
        assert result == {}
        # No suggestion methods should be called
        assert not mock_trial.suggest_categorical.called
        assert not mock_trial.suggest_int.called
        assert not mock_trial.suggest_loguniform.called
    
    def test_real_world_ml_hyperparameter_scenario(self):
        """Test realistic ML hyperparameter optimization scenario"""
from scitex.io._load_modules import load_yaml_as_an_optuna_dict
        
        # Create realistic ML configuration
        ml_config = {
            'model_type': {
                'distribution': 'categorical',
                'values': ['cnn', 'rnn', 'transformer']
            },
            'learning_rate': {
                'distribution': 'loguniform',
                'min': 1e-5,
                'max': 1e-1
            },
            'batch_size': {
                'distribution': 'uniform',
                'min': 16,
                'max': 128
            },
            'num_layers': {
                'distribution': 'intloguniform',
                'min': 1,
                'max': 10
            },
            'dropout_rate': {
                'distribution': 'uniform',
                'min': 0.0,
                'max': 0.5
            }
        }
        
        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(ml_config, f)
            temp_yaml_path = f.name
        
        try:
            # Mock trial with realistic suggestions
            mock_trial = MagicMock()
            mock_trial.suggest_categorical.return_value = 'transformer'
            mock_trial.suggest_loguniform.return_value = 0.001
            mock_trial.suggest_int.side_effect = lambda k, min_val, max_val, log=False: {
                'batch_size': 64, 'num_layers': 4, 'dropout_rate': 32
            }.get(k, 32)
            
            # Load via the actual load function (we need to patch the load import)
            with patch('scitex.io._load_modules._optuna.load') as mock_load:
                mock_load.return_value = ml_config
                
                result = load_yaml_as_an_optuna_dict(temp_yaml_path, mock_trial)
                
                # Verify realistic ML parameters
                assert result['model_type'] == 'transformer'
                assert result['learning_rate'] == 0.001
                assert result['batch_size'] in [64, 32]  # Could be either based on mock
                assert result['num_layers'] in [4, 32]   # Could be either based on mock
                
        finally:
            os.unlink(temp_yaml_path)


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__), "-v"])
