#!/usr/bin/env python3

import numpy as np
import pytest
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import os
import sys
from pathlib import Path

# Add src to path to import directly without circular imports
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

try:
    from scitex.ai.training.early_stopping import EarlyStopping
except ImportError:
    pytest.skip("EarlyStopping not available due to import issues", allow_module_level=True)


class TestEarlyStoppingInit:
    """Test EarlyStopping initialization."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        es = EarlyStopping()
        assert es.patience == 7
        assert es.verbose is False
        assert es.delta == 1e-5
        assert es.direction == "minimize"
        assert es.counter == 0
        assert es.best_score == np.inf
        assert es.best_i_global is None
        assert es.models_spaths_dict == {}
    
    def test_init_custom_params_minimize(self):
        """Test initialization with custom parameters for minimize direction."""
        es = EarlyStopping(patience=10, verbose=True, delta=0.01, direction="minimize")
        assert es.patience == 10
        assert es.verbose is True
        assert es.delta == 0.01
        assert es.direction == "minimize"
        assert es.best_score == np.inf
    
    def test_init_custom_params_maximize(self):
        """Test initialization with custom parameters for maximize direction."""
        es = EarlyStopping(patience=5, verbose=False, delta=0.001, direction="maximize")
        assert es.patience == 5
        assert es.verbose is False
        assert es.delta == 0.001
        assert es.direction == "maximize"
        assert es.best_score == -np.inf


class TestEarlyStoppingIsBest:
    """Test EarlyStopping is_best method."""
    
    def test_is_best_minimize_improvement(self):
        """Test is_best with minimize direction showing improvement."""
        es = EarlyStopping(direction="minimize", delta=0.01)
        es.best_score = 1.0
        
        # Score improved significantly
        assert es.is_best(0.8) is True
        # Score improved slightly beyond delta
        assert es.is_best(0.985) is True
    
    def test_is_best_minimize_no_improvement(self):
        """Test is_best with minimize direction showing no improvement."""
        es = EarlyStopping(direction="minimize", delta=0.01)
        es.best_score = 1.0
        
        # Score worse
        assert es.is_best(1.1) is False
        # Score improved but within delta threshold
        assert es.is_best(0.995) is False
    
    def test_is_best_maximize_improvement(self):
        """Test is_best with maximize direction showing improvement."""
        es = EarlyStopping(direction="maximize", delta=0.01)
        es.best_score = 0.8
        
        # Score improved significantly
        assert es.is_best(0.9) is True
        # Score improved slightly beyond delta
        assert es.is_best(0.815) is True
    
    def test_is_best_maximize_no_improvement(self):
        """Test is_best with maximize direction showing no improvement."""
        es = EarlyStopping(direction="maximize", delta=0.01)
        es.best_score = 0.8
        
        # Score worse
        assert es.is_best(0.7) is False
        # Score improved but within delta threshold
        assert es.is_best(0.805) is False


class TestEarlyStoppingSave:
    """Test EarlyStopping save method."""
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    @patch('scitex.ai.training.early_stopping.scitex.str.printc')
    def test_save_verbose_false(self, mock_print_block, mock_io_save):
        """Test save method with verbose=False."""
        es = EarlyStopping(verbose=False)
        
        # Mock models
        model1 = MagicMock()
        model1.state_dict.return_value = {'param1': 'value1'}
        model2 = MagicMock()
        model2.state_dict.return_value = {'param2': 'value2'}
        
        models_spaths_dict = {
            model1: '/path/to/model1.pth',
            model2: '/path/to/model2.pth'
        }
        
        es.save(0.5, models_spaths_dict, 10)
        
        # Check state updates
        assert es.best_score == 0.5
        assert es.best_i_global == 10
        assert es.models_spaths_dict == models_spaths_dict
        
        # Check save calls
        assert mock_io_save.call_count == 2
        mock_io_save.assert_any_call({'param1': 'value1'}, '/path/to/model1.pth')
        mock_io_save.assert_any_call({'param2': 'value2'}, '/path/to/model2.pth')
        
        # Should not print when verbose=False
        mock_print_block.assert_not_called()
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    @patch('builtins.print')
    def test_save_verbose_true(self, mock_print, mock_io_save):
        """Test save method with verbose=True."""
        es = EarlyStopping(verbose=True)
        es.best_score = 1.0
        
        model = MagicMock()
        model.state_dict.return_value = {'param': 'value'}
        models_spaths_dict = {model: '/path/to/model.pth'}
        
        es.save(0.8, models_spaths_dict, 15)
        
        # Check verbose output
        mock_print.assert_called_once()
        printed_message = mock_print.call_args[0][0]
        assert "Update the best score" in printed_message
        assert "1.000000" in printed_message
        assert "0.800000" in printed_message


class TestEarlyStoppingCall:
    """Test EarlyStopping __call__ method."""
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    def test_call_first_time(self, mock_io_save):
        """Test first call to EarlyStopping."""
        es = EarlyStopping()
        es.best_score = None  # Simulate first call
        
        model = MagicMock()
        model.state_dict.return_value = {}
        models_spaths_dict = {model: '/path/to/model.pth'}
        
        result = es(0.5, models_spaths_dict, 0)
        
        assert result is False  # Should not stop
        assert es.best_score == 0.5
        assert es.best_i_global == 0
        assert es.counter == 0
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    def test_call_improvement_minimize(self, mock_io_save):
        """Test call with improvement in minimize direction."""
        es = EarlyStopping(direction="minimize", delta=0.01)
        es.best_score = 1.0
        es.counter = 3
        
        model = MagicMock()
        model.state_dict.return_value = {}
        models_spaths_dict = {model: '/path/to/model.pth'}
        
        result = es(0.8, models_spaths_dict, 5)
        
        assert result is False  # Should not stop
        assert es.best_score == 0.8
        assert es.best_i_global == 5
        assert es.counter == 0  # Reset counter
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    @patch('builtins.print')
    def test_call_no_improvement_verbose(self, mock_print, mock_io_save):
        """Test call with no improvement and verbose output."""
        es = EarlyStopping(direction="minimize", patience=3, verbose=True)
        es.best_score = 0.5
        es.counter = 0
        
        model = MagicMock()
        models_spaths_dict = {model: '/path/to/model.pth'}
        
        # No improvement
        result = es(0.6, models_spaths_dict, 5)
        
        assert result is False  # Should not stop yet
        assert es.counter == 1
        mock_print.assert_called_once()
        assert "EarlyStopping counter: 1 out of 3" in mock_print.call_args[0][0]
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    @patch('scitex.ai.training.early_stopping.scitex.str.printc')
    @patch('builtins.print')
    def test_call_early_stopping_triggered(self, mock_print, mock_print_block, mock_io_save):
        """Test call when early stopping is triggered."""
        es = EarlyStopping(direction="minimize", patience=2, verbose=True)
        es.best_score = 0.5
        es.counter = 1  # Already at patience-1
        
        model = MagicMock()
        models_spaths_dict = {model: '/path/to/model.pth'}
        
        # No improvement - should trigger early stopping
        result = es(0.6, models_spaths_dict, 10)
        
        assert result is True  # Should stop
        assert es.counter == 2
        mock_print_block.assert_called_once_with("Early-stopped.", c="yellow")
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    def test_call_no_improvement_silent(self, mock_io_save):
        """Test call with no improvement and verbose=False."""
        es = EarlyStopping(direction="minimize", patience=5, verbose=False)
        es.best_score = 0.5
        es.counter = 2
        
        model = MagicMock()
        models_spaths_dict = {model: '/path/to/model.pth'}
        
        result = es(0.6, models_spaths_dict, 8)
        
        assert result is False
        assert es.counter == 3
        assert es.best_score == 0.5  # Unchanged


class TestEarlyStoppingIntegration:
    """Test EarlyStopping integration scenarios."""
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    def test_training_loop_simulation_minimize(self, mock_io_save):
        """Test simulation of a training loop with minimize direction."""
        es = EarlyStopping(patience=3, direction="minimize", verbose=False)
        
        model = MagicMock()
        model.state_dict.return_value = {'weights': 'data'}
        models_spaths_dict = {model: '/tmp/model.pth'}
        
        # Simulate validation scores (improving then worsening)
        val_scores = [1.0, 0.8, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        should_stop = False
        for i, score in enumerate(val_scores):
            should_stop = es(score, models_spaths_dict, i)
            if should_stop:
                break
        
        # Should stop after 3 non-improving scores (indices 3, 4, 5)
        assert should_stop is True
        assert es.best_score == 0.6  # Best score achieved
        assert es.best_i_global == 2  # When best score was achieved
        assert es.counter == 3  # Patience reached
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    def test_training_loop_simulation_maximize(self, mock_io_save):
        """Test simulation of a training loop with maximize direction."""
        es = EarlyStopping(patience=2, direction="maximize", verbose=False)
        
        model = MagicMock()
        model.state_dict.return_value = {'weights': 'data'}
        models_spaths_dict = {model: '/tmp/model.pth'}
        
        # Simulate accuracy scores (improving then plateauing)
        acc_scores = [0.5, 0.7, 0.9, 0.85, 0.8]
        
        should_stop = False
        for i, score in enumerate(acc_scores):
            should_stop = es(score, models_spaths_dict, i)
            if should_stop:
                break
        
        # Should stop after 2 non-improving scores
        assert should_stop is True
        assert es.best_score == 0.9
        assert es.best_i_global == 2
    
    @patch('scitex.ai.training.early_stopping.scitex.io.save')
    def test_continuous_improvement_no_stopping(self, mock_io_save):
        """Test that continuous improvement prevents early stopping."""
        es = EarlyStopping(patience=2, direction="minimize", verbose=False)
        
        model = MagicMock()
        models_spaths_dict = {model: '/tmp/model.pth'}
        
        # Continuously improving scores
        improving_scores = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        
        should_stop = False
        for i, score in enumerate(improving_scores):
            should_stop = es(score, models_spaths_dict, i)
            assert should_stop is False  # Should never stop
            assert es.counter == 0  # Counter should always reset
        
        assert es.best_score == 0.5  # Final best score
    
    def test_delta_threshold_behavior(self):
        """Test delta threshold behavior for improvement detection."""
        es = EarlyStopping(direction="minimize", delta=0.1, verbose=False)
        es.best_score = 1.0
        
        # Small improvement within delta - should not count as improvement
        assert es.is_best(0.95) is False
        
        # Improvement beyond delta - should count as improvement
        assert es.is_best(0.85) is True
        
        # Exact delta boundary
        assert es.is_best(0.9) is False
        assert es.is_best(0.89) is True


if __name__ == "__main__":
    pytest.main([__file__])
