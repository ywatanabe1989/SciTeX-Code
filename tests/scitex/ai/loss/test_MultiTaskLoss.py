#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 00:00:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/loss/test_MultiTaskLoss.py
# ----------------------------------------
"""Tests for MultiTaskLoss module for multi-task learning."""

import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.ai.loss import MultiTaskLoss


class TestMultiTaskLossBasics:
    """Test basic MultiTaskLoss functionality."""
    
    def test_initialization_default(self):
        """Test default initialization of MultiTaskLoss."""
        mtl = MultiTaskLoss()
        assert isinstance(mtl, nn.Module)
        assert mtl.reduction == "none"
        assert len(mtl.log_vars) == 2  # Default two tasks
    
    def test_initialization_custom_tasks(self):
        """Test initialization with custom number of tasks."""
        are_regression = [True, False, True]
        mtl = MultiTaskLoss(are_regression)
        assert len(mtl.log_vars) == 3
        assert torch.all(mtl.are_regression == torch.tensor([True, False, True]))
    
    def test_log_vars_are_parameters(self):
        """Test that log_vars are learnable parameters."""
        mtl = MultiTaskLoss([True, True])
        assert isinstance(mtl.log_vars, nn.Parameter)
        assert mtl.log_vars.requires_grad
    
    def test_are_regression_buffer(self):
        """Test that are_regression is registered as buffer."""
        are_regression = [False, True]
        mtl = MultiTaskLoss(are_regression)
        assert 'are_regression' in mtl._buffers
        assert torch.all(mtl.are_regression == torch.tensor([False, True]))
    
    def test_forward_basic(self):
        """Test basic forward pass."""
        mtl = MultiTaskLoss([False, False])
        losses = [torch.tensor(1.0, requires_grad=True), 
                  torch.tensor(2.0, requires_grad=True)]
        scaled_losses = mtl(losses)
        
        assert len(scaled_losses) == 2
        assert all(isinstance(loss, torch.Tensor) for loss in scaled_losses)
        assert all(loss.requires_grad for loss in scaled_losses)
    
    def test_forward_shape_preservation(self):
        """Test that forward preserves loss shapes."""
        mtl = MultiTaskLoss([True, False])
        batch_size = 4
        losses = [torch.randn(batch_size, requires_grad=True),
                  torch.randn(batch_size, requires_grad=True)]
        
        scaled_losses = mtl(losses)
        assert all(loss.shape == torch.Size([batch_size]) for loss in scaled_losses)
    
    def test_device_compatibility(self):
        """Test MultiTaskLoss works on different devices."""
        if torch.cuda.is_available():
            mtl = MultiTaskLoss([True, False]).cuda()
            losses = [torch.randn(1).cuda(), torch.randn(1).cuda()]
            scaled_losses = mtl(losses)
            assert all(loss.is_cuda for loss in scaled_losses)
        else:
            pytest.skip("CUDA not available")


class TestMultiTaskLossComputations:
    """Test MultiTaskLoss mathematical computations."""
    
    def test_regression_vs_classification_coefficients(self):
        """Test different coefficients for regression vs classification."""
        mtl = MultiTaskLoss([True, False])  # Regression, Classification
        
        # Set log_vars to zero for easier testing
        with torch.no_grad():
            mtl.log_vars.zero_()
        
        losses = [torch.tensor(1.0), torch.tensor(1.0)]
        scaled_losses = mtl(losses)
        
        # Regression coefficient: 1/(2*var), Classification: 1/var
        # With var=1 (log_var=0): regression coeff = 0.5, classification coeff = 1.0
        assert scaled_losses[0].item() < scaled_losses[1].item()
    
    def test_log_vars_effect(self):
        """Test effect of different log_vars values."""
        mtl = MultiTaskLoss([False, False])
        
        # Test with different log_vars
        with torch.no_grad():
            mtl.log_vars[0] = torch.log(torch.tensor(0.5))
            mtl.log_vars[1] = torch.log(torch.tensor(2.0))
        
        losses = [torch.tensor(1.0), torch.tensor(1.0)]
        scaled_losses = mtl(losses)
        
        # Higher variance should lead to lower coefficient
        assert scaled_losses[0].item() > scaled_losses[1].item()
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme log_vars."""
        mtl = MultiTaskLoss([True, False])
        
        # Test with very small and very large log_vars
        with torch.no_grad():
            mtl.log_vars[0] = -10.0  # Very small variance
            mtl.log_vars[1] = 10.0   # Very large variance
        
        losses = [torch.tensor(1.0), torch.tensor(1.0)]
        scaled_losses = mtl(losses)
        
        # Check for NaN or Inf
        assert all(torch.isfinite(loss) for loss in scaled_losses)
    
    def test_gradient_flow(self):
        """Test gradient flows through MultiTaskLoss."""
        mtl = MultiTaskLoss([True, True])
        losses = [torch.tensor(1.0, requires_grad=True),
                  torch.tensor(2.0, requires_grad=True)]
        
        scaled_losses = mtl(losses)
        total_loss = sum(scaled_losses)
        total_loss.backward()
        
        # Check gradients exist
        assert mtl.log_vars.grad is not None
        assert all(torch.isfinite(mtl.log_vars.grad))


class TestMultiTaskLossOptimization:
    """Test MultiTaskLoss in optimization scenarios."""
    
    def test_learnable_weights_update(self):
        """Test that log_vars update during optimization."""
        mtl = MultiTaskLoss([True, False])
        optimizer = torch.optim.Adam(mtl.parameters(), lr=0.1)
        
        initial_log_vars = mtl.log_vars.clone()
        
        # Simulate training steps
        for _ in range(10):
            losses = [torch.randn(1, requires_grad=True) + 1,
                      torch.randn(1, requires_grad=True) + 2]
            scaled_losses = mtl(losses)
            total_loss = sum(scaled_losses).mean()
            
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
        
        # Check log_vars have been updated
        assert not torch.allclose(mtl.log_vars, initial_log_vars)
    
    def test_task_weighting_adaptation(self):
        """Test that task weights adapt based on loss magnitudes."""
        mtl = MultiTaskLoss([False, False])
        optimizer = torch.optim.SGD(mtl.parameters(), lr=0.01)
        
        # Simulate one task having consistently higher loss
        for _ in range(50):
            losses = [torch.tensor(10.0, requires_grad=True),  # High loss
                      torch.tensor(0.1, requires_grad=True)]   # Low loss
            scaled_losses = mtl(losses)
            total_loss = sum(scaled_losses)
            
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
        
        # The high-loss task should have higher variance (higher log_var)
        assert mtl.log_vars[0] > mtl.log_vars[1]
    
    def test_convergence_behavior(self):
        """Test MultiTaskLoss helps with convergence."""
        # Create simple multi-task model
        class MultiTaskModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.shared = nn.Linear(10, 20)
                self.task1 = nn.Linear(20, 1)
                self.task2 = nn.Linear(20, 2)
            
            def forward(self, x):
                shared = torch.relu(self.shared(x))
                return self.task1(shared), self.task2(shared)
        
        model = MultiTaskModel()
        mtl = MultiTaskLoss([True, False])  # Regression, Classification
        optimizer = torch.optim.Adam(list(model.parameters()) + list(mtl.parameters()))
        
        # Dummy data
        x = torch.randn(32, 10)
        y1 = torch.randn(32, 1)
        y2 = torch.randint(0, 2, (32,))
        
        # Training loop
        losses_history = []
        for _ in range(20):
            out1, out2 = model(x)
            
            # Task losses
            loss1 = nn.MSELoss()(out1, y1)
            loss2 = nn.CrossEntropyLoss()(out2, y2)
            
            # Apply multi-task loss
            scaled_losses = mtl([loss1, loss2])
            total_loss = sum(scaled_losses)
            
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
            
            losses_history.append(total_loss.item())
        
        # Check loss decreases
        assert losses_history[-1] < losses_history[0]


class TestMultiTaskLossEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_task(self):
        """Test MultiTaskLoss with single task."""
        mtl = MultiTaskLoss([True])
        losses = [torch.tensor(1.5, requires_grad=True)]
        scaled_losses = mtl(losses)
        
        assert len(scaled_losses) == 1
        assert isinstance(scaled_losses[0], torch.Tensor)
    
    def test_many_tasks(self):
        """Test MultiTaskLoss with many tasks."""
        n_tasks = 10
        are_regression = [i % 2 == 0 for i in range(n_tasks)]
        mtl = MultiTaskLoss(are_regression)
        
        losses = [torch.randn(1, requires_grad=True) for _ in range(n_tasks)]
        scaled_losses = mtl(losses)
        
        assert len(scaled_losses) == n_tasks
        assert all(loss.requires_grad for loss in scaled_losses)
    
    def test_zero_loss_input(self):
        """Test behavior with zero loss input."""
        mtl = MultiTaskLoss([True, False])
        losses = [torch.tensor(0.0, requires_grad=True),
                  torch.tensor(1.0, requires_grad=True)]
        
        scaled_losses = mtl(losses)
        # First loss should still have regularization term
        assert scaled_losses[0].item() != 0.0  # Due to log(std) term
    
    def test_mismatched_task_count(self):
        """Test error handling for mismatched task count."""
        mtl = MultiTaskLoss([True, False])
        losses = [torch.tensor(1.0)]  # Only one loss, expecting two
        
        with pytest.raises((IndexError, RuntimeError)):
            mtl(losses)
    
    def test_dtype_compatibility(self):
        """Test MultiTaskLoss with different dtypes."""
        mtl = MultiTaskLoss([True, False])
        
        # Test with float32
        losses_f32 = [torch.tensor(1.0, dtype=torch.float32),
                      torch.tensor(2.0, dtype=torch.float32)]
        scaled_f32 = mtl(losses_f32)
        assert all(loss.dtype == torch.float32 for loss in scaled_f32)
        
        # Test with float64
        mtl_f64 = MultiTaskLoss([True, False]).double()
        losses_f64 = [torch.tensor(1.0, dtype=torch.float64),
                      torch.tensor(2.0, dtype=torch.float64)]
        scaled_f64 = mtl_f64(losses_f64)
        assert all(loss.dtype == torch.float64 for loss in scaled_f64)
    
    def test_reproducibility(self):
        """Test reproducibility with fixed seeds."""
        # Create two identical MTL instances
        torch.manual_seed(42)
        mtl1 = MultiTaskLoss([True, False])
        
        torch.manual_seed(42)
        mtl2 = MultiTaskLoss([True, False])
        
        # Should have identical initial parameters
        assert torch.allclose(mtl1.log_vars, mtl2.log_vars)
        
        # Should produce identical outputs
        losses = [torch.tensor(1.0), torch.tensor(2.0)]
        out1 = mtl1(losses)
        out2 = mtl2(losses)
        
        assert all(torch.allclose(o1, o2) for o1, o2 in zip(out1, out2))


class TestMultiTaskLossIntegration:
    """Test integration with real multi-task scenarios."""
    
    def test_with_different_loss_functions(self):
        """Test MultiTaskLoss with various loss function types."""
        mtl = MultiTaskLoss([True, False, False])
        
        # Different types of losses
        mse_loss = torch.tensor(0.5, requires_grad=True)  # Regression
        ce_loss = torch.tensor(1.2, requires_grad=True)   # Classification
        bce_loss = torch.tensor(0.8, requires_grad=True)  # Binary classification
        
        losses = [mse_loss, ce_loss, bce_loss]
        scaled_losses = mtl(losses)
        
        assert len(scaled_losses) == 3
        assert all(loss.requires_grad for loss in scaled_losses)
    
    def test_state_dict_serialization(self):
        """Test saving and loading MultiTaskLoss state."""
        mtl1 = MultiTaskLoss([True, False, True])
        
        # Modify parameters
        with torch.no_grad():
            mtl1.log_vars[0] = 1.5
            mtl1.log_vars[1] = -0.5
            mtl1.log_vars[2] = 0.3
        
        # Save state
        state = mtl1.state_dict()
        
        # Load into new instance
        mtl2 = MultiTaskLoss([True, False, True])
        mtl2.load_state_dict(state)
        
        # Check parameters match
        assert torch.allclose(mtl1.log_vars, mtl2.log_vars)
        assert torch.allclose(mtl1.are_regression, mtl2.are_regression)
    
    def test_mixed_precision_training(self):
        """Test MultiTaskLoss with mixed precision training."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA required for mixed precision")
        
        mtl = MultiTaskLoss([True, False]).cuda()
        
        with torch.cuda.amp.autocast():
            losses = [torch.randn(1).cuda(), torch.randn(1).cuda()]
            scaled_losses = mtl(losses)
            total_loss = sum(scaled_losses)
        
        # Should work without errors
        assert torch.isfinite(total_loss)
    
    def test_reduction_parameter(self):
        """Test different reduction parameters."""
        # Note: Current implementation doesn't use reduction parameter
        # This test documents expected behavior
        mtl_none = MultiTaskLoss([True, False], reduction="none")
        mtl_mean = MultiTaskLoss([True, False], reduction="mean")
        mtl_sum = MultiTaskLoss([True, False], reduction="sum")
        
        losses = [torch.randn(4), torch.randn(4)]
        
        # All should return list of losses (reduction not implemented)
        out_none = mtl_none(losses)
        out_mean = mtl_mean(losses)
        out_sum = mtl_sum(losses)
        
        assert all(isinstance(out, list) for out in [out_none, out_mean, out_sum])
        assert all(len(out) == 2 for out in [out_none, out_mean, out_sum])
    
    def test_comparison_with_manual_weighting(self):
        """Compare MultiTaskLoss with manual fixed weighting."""
        # MultiTaskLoss with learned weights
        mtl = MultiTaskLoss([False, False])
        
        # Manual fixed weights
        manual_weights = [0.7, 0.3]
        
        losses = [torch.tensor(1.0, requires_grad=True),
                  torch.tensor(2.0, requires_grad=True)]
        
        # MTL output
        mtl_scaled = mtl(losses)
        mtl_total = sum(mtl_scaled)
        
        # Manual weighting
        manual_total = sum(w * l for w, l in zip(manual_weights, losses))
        
        # Both should be valid loss values
        assert torch.isfinite(mtl_total)
        assert torch.isfinite(manual_total)
        
        # MTL should adapt weights based on uncertainty
        assert mtl_total != manual_total  # Different weighting strategies


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    
    pytest.main([os.path.abspath(__file__), "-v"])
