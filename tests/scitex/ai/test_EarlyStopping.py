#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 11:00:00 (ywatanabe)"
# File: ./tests/scitex/ai/test_EarlyStopping.py

"""Comprehensive tests for EarlyStopping functionality."""

import os
import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from unittest import mock
import torch
import torch.nn as nn

import scitex
from scitex.ai import EarlyStopping


class DummyModel(nn.Module):
    """Simple dummy model for testing."""
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 1)
    
    def forward(self, x):
        return self.linear(x)


class TestEarlyStopping:
    """Test suite for EarlyStopping class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def model_setup(self, temp_dir):
        """Setup models and save paths for testing."""
        model1 = DummyModel()
        model2 = DummyModel()
        
        spath1 = os.path.join(temp_dir, "model1.pth")
        spath2 = os.path.join(temp_dir, "model2.pth")
        
        models_spaths_dict = {
            model1: spath1,
            model2: spath2
        }
        
        return {
            'model1': model1,
            'model2': model2,
            'models_spaths_dict': models_spaths_dict,
            'spath1': spath1,
            'spath2': spath2
        }
    
    def test_initialization_minimize(self):
        """Test EarlyStopping initialization with minimize direction."""
        early_stopping = EarlyStopping(patience=5, verbose=False, delta=0.001, direction="minimize")
        
        assert early_stopping.patience == 5
        assert early_stopping.verbose == False
        assert early_stopping.delta == 0.001
        assert early_stopping.direction == "minimize"
        assert early_stopping.counter == 0
        assert early_stopping.best_score == np.inf
        assert early_stopping.best_i_global is None
        assert isinstance(early_stopping.models_spaths_dict, dict)
    
    def test_initialization_maximize(self):
        """Test EarlyStopping initialization with maximize direction."""
        early_stopping = EarlyStopping(patience=10, verbose=True, delta=0.01, direction="maximize")
        
        assert early_stopping.patience == 10
        assert early_stopping.verbose == True
        assert early_stopping.delta == 0.01
        assert early_stopping.direction == "maximize"
        assert early_stopping.counter == 0
        assert early_stopping.best_score == -np.inf
        assert early_stopping.best_i_global is None
    
    def test_is_best_minimize(self):
        """Test is_best method for minimization."""
        early_stopping = EarlyStopping(direction="minimize", delta=0.01)
        early_stopping.best_score = 0.5
        
        # Better score (lower)
        assert early_stopping.is_best(0.4) == True
        
        # Worse score (higher)
        assert early_stopping.is_best(0.6) == False
        
        # Within delta range (not better enough)
        assert early_stopping.is_best(0.495) == False
    
    def test_is_best_maximize(self):
        """Test is_best method for maximization."""
        early_stopping = EarlyStopping(direction="maximize", delta=0.01)
        early_stopping.best_score = 0.5
        
        # Better score (higher)
        assert early_stopping.is_best(0.6) == True
        
        # Worse score (lower)
        assert early_stopping.is_best(0.4) == False
        
        # Within delta range (not better enough)
        assert early_stopping.is_best(0.505) == False
    
    def test_first_call(self, model_setup):
        """Test the first call to early stopping."""
        early_stopping = EarlyStopping(patience=3, verbose=False)
        
        # First call should always save and return False
        result = early_stopping(
            current_score=0.8,
            models_spaths_dict=model_setup['models_spaths_dict'],
            i_global=0
        )
        
        assert result == False
        assert early_stopping.best_score == 0.8
        assert early_stopping.best_i_global == 0
        assert early_stopping.counter == 0
        
        # Check that models were saved
        assert os.path.exists(model_setup['spath1'])
        assert os.path.exists(model_setup['spath2'])
    
    def test_improvement_resets_counter(self, model_setup):
        """Test that improvement resets the counter."""
        early_stopping = EarlyStopping(patience=3, verbose=False, direction="minimize")
        
        # First call
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        
        # Make some non-improving calls
        early_stopping(1.1, model_setup['models_spaths_dict'], 1)
        early_stopping(1.2, model_setup['models_spaths_dict'], 2)
        assert early_stopping.counter == 2
        
        # Improving call should reset counter
        result = early_stopping(0.8, model_setup['models_spaths_dict'], 3)
        assert result == False
        assert early_stopping.counter == 0
        assert early_stopping.best_score == 0.8
        assert early_stopping.best_i_global == 3
    
    def test_patience_exhausted(self, model_setup):
        """Test early stopping when patience is exhausted."""
        early_stopping = EarlyStopping(patience=2, verbose=False, direction="minimize")
        
        # First call
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        
        # Non-improving calls
        assert early_stopping(1.1, model_setup['models_spaths_dict'], 1) == False
        assert early_stopping.counter == 1
        
        result = early_stopping(1.2, model_setup['models_spaths_dict'], 2)
        assert early_stopping.counter == 2
        
        # This should trigger early stopping if patience is reached
        if early_stopping.counter >= early_stopping.patience:
            assert result == True
        else:
            assert result == False
    
    def test_verbose_mode(self, model_setup, capsys):
        """Test verbose output."""
        early_stopping = EarlyStopping(patience=2, verbose=True, direction="minimize")
        
        # First call with verbose
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        captured = capsys.readouterr()
        assert "Update the best score" in captured.out
        
        # Non-improving call
        early_stopping(1.1, model_setup['models_spaths_dict'], 1)
        captured = capsys.readouterr()
        assert "EarlyStopping counter: 1 out of 2" in captured.out
        
        # Trigger early stopping
        early_stopping(1.2, model_setup['models_spaths_dict'], 2)
        early_stopping(1.3, model_setup['models_spaths_dict'], 3)
        captured = capsys.readouterr()
        assert "Early-stopped" in captured.out
    
    def test_delta_parameter(self, model_setup):
        """Test that delta parameter works correctly."""
        early_stopping = EarlyStopping(patience=5, delta=0.1, direction="minimize")
        
        # First call
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        
        # Score improved but not by enough (within delta)
        result = early_stopping(0.95, model_setup['models_spaths_dict'], 1)
        assert result == False
        assert early_stopping.counter == 1  # Should count as non-improvement
        assert early_stopping.best_score == 1.0  # Should not update
        
        # Score improved by more than delta
        result = early_stopping(0.85, model_setup['models_spaths_dict'], 2)
        assert result == False
        assert early_stopping.counter == 0  # Should reset
        assert early_stopping.best_score == 0.85  # Should update
    
    def test_save_function(self, model_setup):
        """Test the save function directly."""
        early_stopping = EarlyStopping(verbose=False)
        
        # Call save directly
        early_stopping.save(
            current_score=0.75,
            models_spaths_dict=model_setup['models_spaths_dict'],
            i_global=10
        )
        
        assert early_stopping.best_score == 0.75
        assert early_stopping.best_i_global == 10
        assert os.path.exists(model_setup['spath1'])
        assert os.path.exists(model_setup['spath2'])
        
        # Verify saved models can be loaded
        state_dict1 = torch.load(model_setup['spath1'])
        state_dict2 = torch.load(model_setup['spath2'])
        assert isinstance(state_dict1, dict)
        assert isinstance(state_dict2, dict)
    
    def test_multiple_models_tracking(self, temp_dir):
        """Test tracking multiple models."""
        early_stopping = EarlyStopping(patience=3, verbose=False)
        
        # Create multiple models
        models = [DummyModel() for _ in range(5)]
        models_spaths_dict = {
            model: os.path.join(temp_dir, f"model_{i}.pth")
            for i, model in enumerate(models)
        }
        
        # First call
        early_stopping(0.5, models_spaths_dict, 0)
        
        # Check all models were saved
        for spath in models_spaths_dict.values():
            assert os.path.exists(spath)
        
        # Check internal tracking
        assert len(early_stopping.models_spaths_dict) == 5
    
    def test_maximize_direction_full_workflow(self, model_setup):
        """Test full workflow with maximize direction."""
        early_stopping = EarlyStopping(patience=2, direction="maximize", verbose=False)
        
        # Simulating accuracy scores (want to maximize)
        scores = [0.7, 0.75, 0.73, 0.72, 0.71]  # Peak at 0.75
        
        results = []
        for i, score in enumerate(scores):
            result = early_stopping(score, model_setup['models_spaths_dict'], i)
            results.append(result)
        
        # Should not stop at improvement
        assert results[0] == False  # First call
        assert results[1] == False  # Improvement
        assert results[2] == False  # First decline
        # Second decline may trigger early stopping depending on patience
        assert results[4] == True   # Should stop (patience exhausted)
        
        # Best score should be from index 1
        assert early_stopping.best_score == 0.75
        assert early_stopping.best_i_global == 1
    
    def test_edge_cases(self, model_setup):
        """Test edge cases."""
        # Zero patience
        early_stopping = EarlyStopping(patience=0, verbose=False)
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        assert early_stopping(1.1, model_setup['models_spaths_dict'], 1) == True
        
        # Very large delta - even large improvements won't qualify
        early_stopping = EarlyStopping(patience=5, delta=10.0, direction="minimize")
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        # Even improvement from 1.0 to 0.0 won't qualify with delta=10.0
        result = early_stopping(0.0, model_setup['models_spaths_dict'], 1)
        assert result == False
        assert early_stopping.counter == 1  # Should increment counter as not enough improvement
    
    def test_consistent_state(self, model_setup):
        """Test that internal state remains consistent."""
        early_stopping = EarlyStopping(patience=3, verbose=False)
        
        # Make several calls
        early_stopping(1.0, model_setup['models_spaths_dict'], 0)
        early_stopping(0.9, model_setup['models_spaths_dict'], 1)  # Improvement
        early_stopping(0.95, model_setup['models_spaths_dict'], 2)  # No improvement
        
        # Check state consistency
        assert early_stopping.best_score == 0.9
        assert early_stopping.best_i_global == 1
        assert early_stopping.counter == 1
        assert len(early_stopping.models_spaths_dict) == 2
    
    def test_none_best_score_handling(self, model_setup):
        """Test handling when best_score is None (shouldn't happen but test anyway)."""
        early_stopping = EarlyStopping(patience=3, verbose=False)
        early_stopping.best_score = None  # Force None
        
        # Should handle gracefully
        result = early_stopping(0.5, model_setup['models_spaths_dict'], 0)
        assert result == False
        assert early_stopping.best_score == 0.5
    
    def test_integration_with_training_loop(self, model_setup):
        """Test integration with a simulated training loop."""
        early_stopping = EarlyStopping(patience=3, direction="minimize", verbose=False)
        
        # Simulate validation losses over epochs
        val_losses = [0.5, 0.4, 0.35, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38]
        
        for epoch, val_loss in enumerate(val_losses):
            if early_stopping(val_loss, model_setup['models_spaths_dict'], epoch):
                break
        
        # Should stop at epoch 6 (after 3 non-improvements from epoch 3)
        assert epoch == 6
        assert early_stopping.best_score == 0.33
        assert early_stopping.best_i_global == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/EarlyStopping.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # Time-stamp: "2024-09-07 01:09:38 (ywatanabe)"
#
# import os
#
# import scitex
# import numpy as np
#
#
# class EarlyStopping:
#     """
#     Early stops the training if the validation score doesn't improve after a given patience period.
#
#     """
#
#     def __init__(
#         self, patience=7, verbose=False, delta=1e-5, direction="minimize"
#     ):
#         """
#         Args:
#             patience (int): How long to wait after last time validation score improved.
#                             Default: 7
#             verbose (bool): If True, prints a message for each validation score improvement.
#                             Default: False
#             delta (float): Minimum change in the monitored quantity to qualify as an improvement.
#                             Default: 0
#         """
#         self.patience = patience
#         self.verbose = verbose
#         self.direction = direction
#
#         self.delta = delta
#
#         # default
#         self.counter = 0
#         self.best_score = np.Inf if direction == "minimize" else -np.Inf
#         self.best_i_global = None
#         self.models_spaths_dict = {}
#
#     def is_best(self, val_score):
#         is_smaller = val_score < self.best_score - abs(self.delta)
#         is_larger = self.best_score + abs(self.delta) < val_score
#         return is_smaller if self.direction == "minimize" else is_larger
#
#     def __call__(self, current_score, models_spaths_dict, i_global):
#         # The 1st call
#         if self.best_score is None:
#             self.save(current_score, models_spaths_dict, i_global)
#             return False
#
#         # After the 2nd call
#         if self.is_best(current_score):
#             self.save(current_score, models_spaths_dict, i_global)
#             self.counter = 0
#             return False
#
#         else:
#             self.counter += 1
#             if self.verbose:
#                 print(
#                     f"\nEarlyStopping counter: {self.counter} out of {self.patience}\n"
#                 )
#             if self.counter >= self.patience:
#                 if self.verbose:
#                     scitex.gen.print_block("Early-stopped.", c="yellow")
#                 return True
#
#     def save(self, current_score, models_spaths_dict, i_global):
#         """Saves model when validation score decrease."""
#
#         if self.verbose:
#             print(
#                 f"\nUpdate the best score: ({self.best_score:.6f} --> {current_score:.6f})"
#             )
#
#         self.best_score = current_score
#         self.best_i_global = i_global
#
#         for model, spath in models_spaths_dict.items():
#             scitex.io.save(model.state_dict(), spath)
#
#         self.models_spaths_dict = models_spaths_dict
#
#
# if __name__ == "__main__":
#     pass
#     # # starts the current fold's loop
#     # i_global = 0
#     # lc_logger = scitex.ml.LearningCurveLogger()
#     # early_stopping = utils.EarlyStopping(patience=50, verbose=True)
#     # for i_epoch, epoch in enumerate(tqdm(range(merged_conf["MAX_EPOCHS"]))):
#
#     #     dlf.fill(i_fold, reset_fill_counter=False)
#
#     #     step_str = "Validation"
#     #     for i_batch, batch in enumerate(dlf.dl_val):
#     #         _, loss_diag_val = utils.base_step(
#     #             step_str,
#     #             model,
#     #             mtl,
#     #             batch,
#     #             device,
#     #             i_fold,
#     #             i_epoch,
#     #             i_batch,
#     #             i_global,
#     #             lc_logger,
#     #             no_mtl=args.no_mtl,
#     #             print_batch_interval=False,
#     #         )
#     #     lc_logger.print(step_str)
#
#     #     step_str = "Training"
#     #     for i_batch, batch in enumerate(dlf.dl_tra):
#     #         optimizer.zero_grad()
#     #         loss, _ = utils.base_step(
#     #             step_str,
#     #             model,
#     #             mtl,
#     #             batch,
#     #             device,
#     #             i_fold,
#     #             i_epoch,
#     #             i_batch,
#     #             i_global,
#     #             lc_logger,
#     #             no_mtl=args.no_mtl,
#     #             print_batch_interval=False,
#     #         )
#     #         loss.backward()
#     #         optimizer.step()
#     #         i_global += 1
#     #     lc_logger.print(step_str)
#
#     #     bACC_val = np.array(lc_logger.logged_dict["Validation"]["bACC_diag_plot"])[
#     #         np.array(lc_logger.logged_dict["Validation"]["i_epoch"]) == i_epoch
#     #     ].mean()
#
#     #     model_spath = (
#     #         merged_conf["sdir"]
#     #         + f"checkpoints/model_fold#{i_fold}_epoch#{i_epoch:03d}.pth"
#     #     )
#     #     mtl_spath = model_spath.replace("model_fold", "mtl_fold")
#     #     models_spaths_dict = {model_spath: model, mtl_spath: mtl}
#
#     #     early_stopping(loss_diag_val, models_spaths_dict, i_epoch, i_global)
#     #     # early_stopping(-bACC_val, models_spaths_dict, i_epoch, i_global)
#
#     #     if early_stopping.early_stop:
#     #         print("Early stopping")
#     #         break

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/EarlyStopping.py
# --------------------------------------------------------------------------------
