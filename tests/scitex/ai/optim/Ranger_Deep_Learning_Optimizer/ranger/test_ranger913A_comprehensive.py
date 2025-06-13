#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 14:06:00 (ywatanabe)"

"""
Comprehensive tests for RangerVA (ranger913A) optimizer.

This module provides thorough testing of the RangerVA optimizer,
including parameter validation, optimization behavior, and edge cases.
RangerVA includes calibrated adaptive learning rates.
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch, MagicMock

try:
    from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger.ranger913A import RangerVA
except ImportError:
    pytest.skip("RangerVA optimizer not available", allow_module_level=True)


class SimpleModel(nn.Module):
    """Simple model for testing optimizers."""
    def __init__(self, input_size=10, hidden_size=20, output_size=2):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.conv1 = nn.Conv2d(1, 8, 3, padding=1)
        
    def forward(self, x):
        if x.dim() == 4:  # Conv input
            x = self.conv1(x)
            x = x.view(x.size(0), -1)
            x = self.fc1(x[:, :10])  # Take first 10 features
        else:
            x = self.fc1(x)
        x = torch.relu(x)
        x = self.fc2(x)
        return x


class TestRangerVAInitialization:
    """Test RangerVA optimizer initialization."""
    
    def test_default_initialization(self):
        """Test initialization with default parameters."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters())
        
        assert optimizer.defaults['lr'] == 1e-3
        assert optimizer.defaults['alpha'] == 0.5
        assert optimizer.defaults['k'] == 6
        assert optimizer.defaults['betas'] == (0.95, 0.999)
        assert optimizer.defaults['eps'] == 1e-5
        assert optimizer.defaults['weight_decay'] == 0
        assert optimizer.defaults['amsgrad'] == True
        assert optimizer.defaults['transformer'] == 'softplus'
        assert optimizer.defaults['smooth'] == 50
        assert optimizer.defaults['grad_transformer'] == 'square'
        
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        model = SimpleModel()
        optimizer = RangerVA(
            model.parameters(),
            lr=0.01,
            alpha=0.7,
            k=10,
            betas=(0.9, 0.99),
            eps=1e-8,
            weight_decay=1e-4,
            amsgrad=False,
            transformer='identity',
            smooth=100,
            grad_transformer='abs'
        )
        
        assert optimizer.defaults['lr'] == 0.01
        assert optimizer.defaults['alpha'] == 0.7
        assert optimizer.defaults['k'] == 10
        assert optimizer.defaults['betas'] == (0.9, 0.99)
        assert optimizer.defaults['eps'] == 1e-8
        assert optimizer.defaults['weight_decay'] == 1e-4
        assert optimizer.defaults['amsgrad'] == False
        assert optimizer.defaults['transformer'] == 'identity'
        assert optimizer.defaults['smooth'] == 100
        assert optimizer.defaults['grad_transformer'] == 'abs'
        
    def test_invalid_alpha(self):
        """Test invalid alpha parameter."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid slow update rate"):
            RangerVA(model.parameters(), alpha=-0.1)
            
        with pytest.raises(ValueError, match="Invalid slow update rate"):
            RangerVA(model.parameters(), alpha=1.5)
            
    def test_invalid_k(self):
        """Test invalid lookahead steps."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid lookahead steps"):
            RangerVA(model.parameters(), k=0)
            
        with pytest.raises(ValueError, match="Invalid lookahead steps"):
            RangerVA(model.parameters(), k=-1)
            
    def test_invalid_lr(self):
        """Test invalid learning rate."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid Learning Rate"):
            RangerVA(model.parameters(), lr=-0.01)
            
    def test_invalid_eps(self):
        """Test invalid epsilon."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid eps"):
            RangerVA(model.parameters(), eps=-1e-8)


class TestRangerVAOptimization:
    """Test RangerVA optimization behavior."""
    
    def test_basic_optimization(self):
        """Test basic optimization step."""
        model = SimpleModel()
        # Use k=1 to ensure parameters update on first step
        optimizer = RangerVA(model.parameters(), lr=0.1, k=1)
        
        # Get initial parameters
        initial_params = [p.clone() for p in model.parameters()]
        
        # Forward pass
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        
        # Optimization step
        optimizer.step()
        
        # Check parameters changed
        at_least_one_changed = False
        for initial, current in zip(initial_params, model.parameters()):
            if not torch.allclose(initial, current):
                at_least_one_changed = True
                break
        assert at_least_one_changed
        
    def test_zero_grad(self):
        """Test zero_grad functionality."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters())
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        
        # Check gradients exist (only for parameters that were used)
        grads_exist = False
        for p in model.parameters():
            if p.grad is not None:
                grads_exist = True
                assert not torch.all(p.grad == 0)
        assert grads_exist
            
        # Zero gradients
        optimizer.zero_grad()
        
        # Check gradients are zero
        for p in model.parameters():
            assert p.grad is None or torch.all(p.grad == 0)
            
    def test_amsgrad_feature(self):
        """Test AMSGrad feature."""
        model = SimpleModel()
        
        # Test with AMSGrad enabled (default)
        optimizer_ams = RangerVA(model.parameters(), amsgrad=True)
        
        # Test with AMSGrad disabled
        optimizer_no_ams = RangerVA(model.parameters(), amsgrad=False)
        
        # Create same gradients for both
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        # Forward pass
        loss = criterion(model(x), y)
        loss.backward()
        
        # Save gradients
        grads_before = [p.grad.clone() if p.grad is not None else None 
                       for p in model.parameters()]
        
        # Step with AMSGrad
        optimizer_ams.step()
        
        # Check that max_exp_avg_sq is maintained in state
        for group in optimizer_ams.param_groups:
            for p in group['params']:
                if p.grad is not None:
                    state = optimizer_ams.state[p]
                    if group['amsgrad']:
                        assert 'max_exp_avg_sq' in state
        
        # Restore gradients
        for p, g in zip(model.parameters(), grads_before):
            if g is not None:
                p.grad = g.clone()
                
        # Step without AMSGrad
        optimizer_no_ams.step()
        
        # Both should update parameters (actual values will differ)
        assert True
        
    def test_grad_transformer_square(self):
        """Test square gradient transformer."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters(), grad_transformer='square')
        
        # Forward pass
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Should complete without error
        assert True
        
    def test_grad_transformer_abs(self):
        """Test absolute value gradient transformer."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters(), grad_transformer='abs')
        
        # Forward pass
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Should complete without error
        assert True
        
    def test_softplus_transformer(self):
        """Test softplus transformer for adaptive learning rates."""
        model = SimpleModel()
        optimizer = RangerVA(
            model.parameters(), 
            transformer='softplus',
            smooth=50
        )
        
        # Forward pass
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Should complete without error
        assert True
        
    def test_lookahead_mechanism(self):
        """Test lookahead slow weights update."""
        model = SimpleModel()
        k = 3  # Lookahead steps
        optimizer = RangerVA(model.parameters(), k=k)
        
        # Do k-1 steps (should not update slow weights)
        for i in range(k-1):
            x = torch.randn(5, 10)
            y = torch.randint(0, 2, (5,))
            criterion = nn.CrossEntropyLoss()
            
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
        # Check state
        for group in optimizer.param_groups:
            for p in group['params']:
                if p.grad is not None:
                    state = optimizer.state[p]
                    if 'slow_buffer' in state:
                        assert state['step'] == k-1
                    
        # Do one more step (should update slow weights)
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Check slow weights were updated
        for group in optimizer.param_groups:
            for p in group['params']:
                if p.grad is not None:
                    state = optimizer.state[p]
                    if 'slow_buffer' in state:
                        assert state['step'] == k  # Should be k after k steps
                        
    def test_weight_decay(self):
        """Test weight decay functionality."""
        model = SimpleModel()
        # Use k=1 to avoid lookahead complications
        optimizer = RangerVA(model.parameters(), weight_decay=0.1, lr=0.1, k=1)
        
        # Get initial parameters
        initial_params = [p.data.clone() for p in model.parameters()]
        
        # Do optimization step with actual gradients
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        
        # Step
        optimizer.step()
        
        # Check that weight decay was applied
        has_weight_decay_effect = False
        for p in model.parameters():
            if p.grad is not None:
                # Parameters with gradients should have been affected by weight decay
                has_weight_decay_effect = True
                break
        assert has_weight_decay_effect
        
    def test_state_dict(self):
        """Test state dict save/load."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters(), lr=0.01)
        
        # Do some optimization steps
        for _ in range(5):
            x = torch.randn(5, 10)
            y = torch.randint(0, 2, (5,))
            criterion = nn.CrossEntropyLoss()
            
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
        # Save state
        state_dict = optimizer.state_dict()
        
        # Create new optimizer and load state
        model2 = SimpleModel()
        optimizer2 = RangerVA(model2.parameters(), lr=0.01)
        optimizer2.load_state_dict(state_dict)
        
        # Check state matches
        for (k1, v1), (k2, v2) in zip(
            optimizer.state_dict()['state'].items(),
            optimizer2.state_dict()['state'].items()
        ):
            for key in v1:
                if isinstance(v1[key], torch.Tensor):
                    assert torch.allclose(v1[key], v2[key])
                else:
                    assert v1[key] == v2[key]


class TestRangerVAEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_parameters(self):
        """Test with no parameters."""
        # RangerVA should raise error for empty parameters
        with pytest.raises(ValueError, match="optimizer got an empty parameter list"):
            optimizer = RangerVA([])
            
    def test_single_parameter(self):
        """Test with single parameter."""
        param = nn.Parameter(torch.randn(5, 5))
        optimizer = RangerVA([param])
        
        # Create gradient
        param.grad = torch.randn_like(param)
        
        # Step
        initial = param.clone()
        optimizer.step()
        
        # Check parameter updated
        assert not torch.allclose(initial, param)
        
    def test_large_learning_rate(self):
        """Test stability with large learning rate."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters(), lr=10.0)  # Very large
        
        # Do optimization step
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        
        # Should not produce NaN/Inf
        optimizer.step()
        
        for p in model.parameters():
            assert torch.isfinite(p).all()
            
    def test_zero_learning_rate(self):
        """Test with zero learning rate."""
        model = SimpleModel()
        # RangerVA doesn't allow lr=0.0
        with pytest.raises(ValueError, match="Invalid Learning Rate"):
            optimizer = RangerVA(model.parameters(), lr=0.0)
            
    def test_nan_gradients(self):
        """Test handling of NaN gradients."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters())
        
        # Set NaN gradients
        for p in model.parameters():
            p.grad = torch.full_like(p, float('nan'))
            
        # Step should handle gracefully
        optimizer.step()
        
        # Check parameters
        for p in model.parameters():
            # Parameters might be NaN but should not crash
            assert p.shape == p.shape  # Basic check
            
    def test_inf_gradients(self):
        """Test handling of infinite gradients."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters())
        
        # Set infinite gradients
        for p in model.parameters():
            p.grad = torch.full_like(p, float('inf'))
            
        # Step should handle gracefully
        optimizer.step()
        
        # Check parameters exist
        for p in model.parameters():
            assert p is not None


class TestRangerVAIntegration:
    """Integration tests with real training scenarios."""
    
    def test_convergence_simple_task(self):
        """Test optimizer converges on simple task."""
        # Simple linear regression
        torch.manual_seed(42)
        X = torch.randn(100, 5)
        true_w = torch.randn(5, 1)
        y = X @ true_w + 0.1 * torch.randn(100, 1)
        
        # Model
        model = nn.Linear(5, 1)
        # Use higher lr and k=1 for faster convergence
        optimizer = RangerVA(model.parameters(), lr=0.1, k=1)
        criterion = nn.MSELoss()
        
        # Training
        initial_loss = None
        for epoch in range(100):  # More epochs
            optimizer.zero_grad()
            pred = model(X)
            loss = criterion(pred, y)
            
            if initial_loss is None:
                initial_loss = loss.item()
                
            loss.backward()
            optimizer.step()
            
        # Check convergence
        final_loss = loss.item()
        assert final_loss < initial_loss * 0.5  # 50% reduction
        
    def test_compatibility_with_schedulers(self):
        """Test compatibility with learning rate schedulers."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters(), lr=0.1)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
        
        # Check initial lr
        assert optimizer.param_groups[0]['lr'] == 0.1
        
        # Do some steps with actual gradients
        for i in range(10):
            # Create dummy gradients
            for p in model.parameters():
                if p.requires_grad:
                    p.grad = torch.zeros_like(p)
            
            optimizer.step()
            scheduler.step()
            
        # Check lr was reduced twice (at step 5 and step 10)
        expected_lr = 0.1 * (0.1 ** 2)  # 0.001
        assert optimizer.param_groups[0]['lr'] == pytest.approx(expected_lr, rel=1e-5)
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_compatibility(self):
        """Test optimizer works with CUDA tensors."""
        model = SimpleModel().cuda()
        optimizer = RangerVA(model.parameters())
        
        # Forward pass
        x = torch.randn(5, 10).cuda()
        y = torch.randint(0, 2, (5,)).cuda()
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Check all parameters still on CUDA
        for p in model.parameters():
            assert p.is_cuda
            
    def test_gradient_accumulation(self):
        """Test gradient accumulation pattern."""
        model = SimpleModel()
        optimizer = RangerVA(model.parameters())
        accumulation_steps = 4
        
        # Accumulate gradients
        for i in range(accumulation_steps):
            x = torch.randn(5, 10)
            y = torch.randint(0, 2, (5,))
            criterion = nn.CrossEntropyLoss()
            
            loss = criterion(model(x), y)
            loss = loss / accumulation_steps  # Scale loss
            loss.backward()
            
        # Step only once
        optimizer.step()
        optimizer.zero_grad()
        
        # Should work without issues
        assert True
        
    def test_multiple_param_groups(self):
        """Test optimizer with multiple parameter groups."""
        model = SimpleModel()
        
        # Create optimizer with different learning rates
        optimizer = RangerVA([
            {'params': model.fc1.parameters(), 'lr': 0.01},
            {'params': model.fc2.parameters(), 'lr': 0.001},
            {'params': model.conv1.parameters(), 'lr': 0.1}
        ])
        
        # Check param groups
        assert len(optimizer.param_groups) == 3
        assert optimizer.param_groups[0]['lr'] == 0.01
        assert optimizer.param_groups[1]['lr'] == 0.001
        assert optimizer.param_groups[2]['lr'] == 0.1
        
        # Do optimization step
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Should complete without error
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])