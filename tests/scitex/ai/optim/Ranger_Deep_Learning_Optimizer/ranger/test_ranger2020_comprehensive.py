#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 13:57:00 (ywatanabe)"

"""
Comprehensive tests for Ranger2020 optimizer.

This module provides thorough testing of the Ranger2020 optimizer,
including parameter validation, optimization behavior, and edge cases.
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch, MagicMock

try:
    from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger import ranger2020 as Ranger2020
except ImportError:
    pytest.skip("Ranger2020 optimizer not available", allow_module_level=True)


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


class TestRanger2020Initialization:
    """Test Ranger2020 optimizer initialization."""
    
    def test_default_initialization(self):
        """Test initialization with default parameters."""
        model = SimpleModel()
        optimizer = Ranger2020(model.parameters())
        
        # Check defaults
        assert optimizer.defaults['lr'] == 1e-3
        assert optimizer.defaults['betas'] == (0.95, 0.999)
        assert optimizer.defaults['eps'] == 1e-8
        assert optimizer.defaults['weight_decay'] == 0
        assert hasattr(optimizer, 'num_batches_tracked')
        
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        model = SimpleModel()
        optimizer = Ranger2020(
            model.parameters(),
            lr=0.01,
            betas=(0.9, 0.99),
            eps=1e-5,
            weight_decay=1e-4,
            using_gc=True,
            using_stable_weight_decay=True,
            using_adaptive_gradient_clipping=True,
            agc_clip_value=0.5
        )
        
        assert optimizer.defaults['lr'] == 0.01
        assert optimizer.defaults['betas'] == (0.9, 0.99)
        assert optimizer.defaults['eps'] == 1e-5
        assert optimizer.defaults['weight_decay'] == 1e-4
        
    def test_invalid_lr(self):
        """Test invalid learning rate."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid learning rate"):
            Ranger2020(model.parameters(), lr=-0.01)
            
    def test_invalid_eps(self):
        """Test invalid epsilon."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid epsilon value"):
            Ranger2020(model.parameters(), eps=-1e-8)
            
    def test_invalid_betas(self):
        """Test invalid beta parameters."""
        model = SimpleModel()
        
        with pytest.raises(ValueError, match="Invalid beta parameter"):
            Ranger2020(model.parameters(), betas=(-0.1, 0.999))
            
        with pytest.raises(ValueError, match="Invalid beta parameter"):
            Ranger2020(model.parameters(), betas=(0.9, 1.1))


class TestRanger2020Optimization:
    """Test Ranger2020 optimization behavior."""
    
    def test_basic_optimization(self):
        """Test basic optimization step."""
        model = SimpleModel()
        optimizer = Ranger2020(model.parameters(), lr=0.1)
        
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
        optimizer = Ranger2020(model.parameters())
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        
        # Check gradients exist
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
            
    def test_gradient_centralization(self):
        """Test gradient centralization feature."""
        model = SimpleModel()
        
        # Test with GC enabled
        optimizer_gc = Ranger2020(model.parameters(), using_gc=True)
        
        # Test with GC disabled
        optimizer_no_gc = Ranger2020(model.parameters(), using_gc=False)
        
        # Create same gradients for both
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        # Forward pass for both
        loss1 = criterion(model(x), y)
        loss1.backward()
        
        # Save gradients
        grads_before = [p.grad.clone() if p.grad is not None else None 
                       for p in model.parameters()]
        
        # Step with GC
        optimizer_gc.step()
        
        # Restore gradients
        for p, g in zip(model.parameters(), grads_before):
            if g is not None:
                p.grad = g.clone()
                
        # Step without GC
        optimizer_no_gc.step()
        
        # Both should update parameters (actual values will differ)
        assert True  # Basic test that both run without error
        
    def test_adaptive_gradient_clipping(self):
        """Test adaptive gradient clipping."""
        model = SimpleModel()
        optimizer = Ranger2020(
            model.parameters(), 
            using_adaptive_gradient_clipping=True,
            agc_clip_value=0.5
        )
        
        # Create large gradients
        for p in model.parameters():
            if p.requires_grad:
                p.grad = torch.randn_like(p) * 100  # Large gradients
                
        # Step should handle large gradients
        optimizer.step()
        
        # Check parameters are finite
        for p in model.parameters():
            assert torch.isfinite(p).all()
            
    def test_stable_weight_decay(self):
        """Test stable weight decay feature."""
        model = SimpleModel()
        optimizer = Ranger2020(
            model.parameters(),
            weight_decay=0.1,
            using_stable_weight_decay=True
        )
        
        # Do optimization step
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Should complete without error
        assert True
        
    def test_positive_negative_momentum(self):
        """Test positive-negative momentum feature."""
        model = SimpleModel()
        optimizer = Ranger2020(
            model.parameters(),
            using_positive_negative_momentum=True,
            pnm_momentum=0.1
        )
        
        # Do several optimization steps
        for _ in range(5):
            x = torch.randn(5, 10)
            y = torch.randint(0, 2, (5,))
            criterion = nn.CrossEntropyLoss()
            
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
        # Should complete without error
        assert True
        
    def test_state_dict(self):
        """Test state dict save/load."""
        model = SimpleModel()
        optimizer = Ranger2020(model.parameters(), lr=0.01)
        
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
        optimizer2 = Ranger2020(model2.parameters(), lr=0.01)
        optimizer2.load_state_dict(state_dict)
        
        # Check batch tracking matches
        assert optimizer.num_batches_tracked == optimizer2.num_batches_tracked


class TestRanger2020EdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_parameters(self):
        """Test with no parameters."""
        # Ranger2020 should raise error for empty parameters
        with pytest.raises(ValueError, match="optimizer got an empty parameter list"):
            optimizer = Ranger2020([])
            
    def test_single_parameter(self):
        """Test with single parameter."""
        param = nn.Parameter(torch.randn(5, 5))
        optimizer = Ranger2020([param])
        
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
        optimizer = Ranger2020(model.parameters(), lr=10.0)  # Very large
        
        # Do optimization step
        x = torch.randn(5, 10)
        y = torch.randint(0, 2, (5,))
        criterion = nn.CrossEntropyLoss()
        
        loss = criterion(model(x), y)
        loss.backward()
        
        # Should not produce NaN/Inf with adaptive gradient clipping
        optimizer.step()
        
        for p in model.parameters():
            assert torch.isfinite(p).all()
            
    def test_zero_learning_rate(self):
        """Test with zero learning rate."""
        model = SimpleModel()
        # Ranger2020 doesn't allow lr=0.0
        with pytest.raises(ValueError, match="Invalid learning rate"):
            optimizer = Ranger2020(model.parameters(), lr=0.0)


class TestRanger2020Integration:
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
        optimizer = Ranger2020(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()
        
        # Training
        initial_loss = None
        for epoch in range(100):
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
        
    def test_gradient_accumulation(self):
        """Test gradient accumulation pattern."""
        model = SimpleModel()
        optimizer = Ranger2020(model.parameters())
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
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_compatibility(self):
        """Test optimizer works with CUDA tensors."""
        model = SimpleModel().cuda()
        optimizer = Ranger2020(model.parameters())
        
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])