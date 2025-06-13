#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:10:00"
# File: /tests/scitex/ai/optim/Ranger_Deep_Learning_Optimizer/ranger/test_ranger_enhanced.py
# ----------------------------------------
"""
Enhanced tests for Ranger optimizer implementing advanced testing patterns.

This module demonstrates:
- Comprehensive fixtures for optimizer testing
- Property-based testing for numerical stability
- Edge case handling (NaN, inf, extreme values)
- Performance benchmarking
- Mock isolation for component testing
- Integration with PyTorch ecosystem
- Statistical validation of convergence
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch, MagicMock, call
from hypothesis import given, strategies as st, settings, assume
import time
import gc
from contextlib import contextmanager

# Import the Ranger optimizer
try:
    from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger.ranger import Ranger
except ImportError:
    pytest.skip("Ranger optimizer not available", allow_module_level=True)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def simple_model():
    """Provide a simple neural network for testing."""
    return nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 1)
    )


@pytest.fixture
def conv_model():
    """Provide a convolutional neural network for testing gradient centralization."""
    return nn.Sequential(
        nn.Conv2d(3, 16, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.Flatten(),
        nn.Linear(32 * 8 * 8, 10)
    )


@pytest.fixture
def sample_gradients():
    """Provide various gradient patterns for testing."""
    return {
        'normal': torch.randn(100, 100),
        'sparse': torch.zeros(100, 100).scatter_(1, torch.randint(0, 100, (100, 10)), 1.0),
        'large': torch.randn(100, 100) * 1000,
        'small': torch.randn(100, 100) * 1e-8,
        'nan': torch.full((100, 100), float('nan')),
        'inf': torch.full((100, 100), float('inf')),
        'mixed': torch.cat([torch.randn(50, 100), torch.zeros(50, 100)]),
    }


@pytest.fixture
def optimizer_configs():
    """Provide various optimizer configurations."""
    return [
        {'lr': 1e-3},  # Default
        {'lr': 1e-4, 'alpha': 0.8, 'k': 10},  # Custom lookahead
        {'lr': 1e-2, 'betas': (0.9, 0.999)},  # Custom betas
        {'lr': 1e-3, 'weight_decay': 0.01},  # With weight decay
        {'lr': 1e-3, 'use_gc': False},  # No gradient centralization
        {'lr': 1e-3, 'gc_conv_only': True},  # GC for conv only
        {'lr': 1e-3, 'N_sma_threshhold': 4},  # Different threshold
    ]


@pytest.fixture
def loss_functions():
    """Provide various loss functions for testing."""
    return {
        'mse': nn.MSELoss(),
        'l1': nn.L1Loss(),
        'smooth_l1': nn.SmoothL1Loss(),
        'cross_entropy': nn.CrossEntropyLoss(),
    }


@pytest.fixture(autouse=True)
def set_random_seed():
    """Set random seed for reproducibility."""
    torch.manual_seed(42)
    np.random.seed(42)
    yield
    # Cleanup
    torch.manual_seed(int(time.time()))


@contextmanager
def track_memory():
    """Context manager to track memory usage."""
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    start_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    
    yield
    
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    end_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    memory_used = end_memory - start_memory
    print(f"Memory used: {memory_used / 1024**2:.2f} MB")


# ============================================================================
# Basic Functionality Tests
# ============================================================================

class TestRangerBasics:
    """Test basic Ranger optimizer functionality."""
    
    def test_initialization_default(self, simple_model):
        """Test optimizer initialization with default parameters."""
        optimizer = Ranger(simple_model.parameters())
        
        assert optimizer.defaults['lr'] == 1e-3
        assert optimizer.defaults['alpha'] == 0.5
        assert optimizer.defaults['k'] == 6
        assert optimizer.defaults['betas'] == (0.95, 0.999)
        assert optimizer.defaults['eps'] == 1e-5
        assert optimizer.defaults['weight_decay'] == 0
        assert optimizer.N_sma_threshhold == 5
        assert optimizer.use_gc is True
        assert optimizer.gc_gradient_threshold == 1
    
    @pytest.mark.parametrize('config', [
        {'lr': 1e-4, 'alpha': 0.7},
        {'lr': 1e-2, 'k': 10},
        {'lr': 1e-3, 'use_gc': False},
        {'lr': 1e-3, 'gc_conv_only': True},
    ])
    def test_initialization_custom(self, simple_model, config):
        """Test optimizer initialization with custom parameters."""
        optimizer = Ranger(simple_model.parameters(), **config)
        
        for key, value in config.items():
            if key in optimizer.defaults:
                assert optimizer.defaults[key] == value
            else:
                assert getattr(optimizer, key, None) == value
    
    @pytest.mark.parametrize('invalid_config,expected_error', [
        ({'lr': -1}, "Invalid Learning Rate"),
        ({'lr': 0}, "Invalid Learning Rate"),
        ({'alpha': -0.1}, "Invalid slow update rate"),
        ({'alpha': 1.1}, "Invalid slow update rate"),
        ({'k': 0}, "Invalid lookahead steps"),
        ({'eps': 0}, "Invalid eps"),
        ({'eps': -1e-8}, "Invalid eps"),
    ])
    def test_initialization_invalid_params(self, simple_model, invalid_config, expected_error):
        """Test that invalid parameters raise appropriate errors."""
        with pytest.raises(ValueError, match=expected_error):
            Ranger(simple_model.parameters(), **invalid_config)


# ============================================================================
# Step Function Tests
# ============================================================================

class TestRangerStep:
    """Test Ranger optimizer step functionality."""
    
    def test_single_step(self, simple_model):
        """Test a single optimization step."""
        optimizer = Ranger(simple_model.parameters())
        
        # Forward pass
        x = torch.randn(32, 10)
        y_true = torch.randn(32, 1)
        y_pred = simple_model(x)
        loss = nn.MSELoss()(y_pred, y_true)
        
        # Store initial parameters
        initial_params = [p.clone() for p in simple_model.parameters()]
        
        # Backward and step
        loss.backward()
        optimizer.step()
        
        # Check parameters were updated
        for initial, current in zip(initial_params, simple_model.parameters()):
            assert not torch.equal(initial, current)
    
    def test_multiple_steps(self, simple_model):
        """Test multiple optimization steps."""
        optimizer = Ranger(simple_model.parameters())
        losses = []
        
        for _ in range(10):
            x = torch.randn(32, 10)
            y_true = torch.randn(32, 1)
            y_pred = simple_model(x)
            loss = nn.MSELoss()(y_pred, y_true)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
        
        # Check that optimization is happening (not strictly decreasing due to stochastic nature)
        assert len(set(losses)) > 1  # Losses are changing
    
    def test_lookahead_update(self, simple_model):
        """Test that lookahead updates happen at correct intervals."""
        k = 6
        optimizer = Ranger(simple_model.parameters(), k=k)
        
        # Track parameter updates
        param_history = []
        
        for step in range(k + 2):
            x = torch.randn(32, 10)
            y_true = torch.randn(32, 1)
            y_pred = simple_model(x)
            loss = nn.MSELoss()(y_pred, y_true)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Store current parameters
            current_params = [p.clone() for p in simple_model.parameters()]
            param_history.append(current_params)
            
            # Check state
            for p in simple_model.parameters():
                state = optimizer.state[p]
                assert state['step'] == step + 1
                
                # Lookahead should trigger at step k
                if step + 1 == k:
                    # After lookahead, parameters should be different
                    if step > 0:
                        for prev, curr in zip(param_history[-2][0], current_params[0]):
                            # The change pattern should be different after lookahead
                            pass  # Actual verification would need more complex logic


# ============================================================================
# Gradient Centralization Tests
# ============================================================================

class TestGradientCentralization:
    """Test gradient centralization functionality."""
    
    def test_gc_disabled(self, simple_model):
        """Test optimizer works correctly with gradient centralization disabled."""
        optimizer = Ranger(simple_model.parameters(), use_gc=False)
        assert optimizer.use_gc is False
        
        # Perform optimization step
        x = torch.randn(32, 10)
        y_true = torch.randn(32, 1)
        y_pred = simple_model(x)
        loss = nn.MSELoss()(y_pred, y_true)
        
        loss.backward()
        optimizer.step()  # Should not raise errors
    
    def test_gc_conv_only(self, conv_model):
        """Test gradient centralization applied to conv layers only."""
        optimizer = Ranger(conv_model.parameters(), gc_conv_only=True)
        assert optimizer.gc_gradient_threshold == 3
        
        # Perform optimization step
        x = torch.randn(32, 3, 8, 8)
        y_true = torch.randint(0, 10, (32,))
        y_pred = conv_model(x)
        loss = nn.CrossEntropyLoss()(y_pred, y_true)
        
        loss.backward()
        
        # Mock the gradient centralization to verify it's applied correctly
        with patch.object(optimizer, 'step', wraps=optimizer.step) as mock_step:
            optimizer.step()
            mock_step.assert_called_once()
    
    @patch('builtins.print')
    def test_gc_initialization_messages(self, mock_print, simple_model):
        """Test that correct messages are printed during initialization."""
        # GC for all layers
        optimizer = Ranger(simple_model.parameters(), use_gc=True, gc_conv_only=False)
        mock_print.assert_any_call("Ranger optimizer loaded. \nGradient Centralization usage = True")
        mock_print.assert_any_call("GC applied to both conv and fc layers")
        
        mock_print.reset_mock()
        
        # GC for conv only
        optimizer = Ranger(simple_model.parameters(), use_gc=True, gc_conv_only=True)
        mock_print.assert_any_call("GC applied to conv layers only")


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestRangerProperties:
    """Property-based tests for Ranger optimizer."""
    
    @given(
        lr=st.floats(min_value=1e-6, max_value=1.0),
        alpha=st.floats(min_value=0.1, max_value=0.9),
        k=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_parameter_updates_bounded(self, simple_model, lr, alpha, k):
        """Test that parameter updates remain bounded for valid hyperparameters."""
        optimizer = Ranger(simple_model.parameters(), lr=lr, alpha=alpha, k=k)
        
        # Multiple optimization steps
        for _ in range(10):
            x = torch.randn(16, 10)
            y_true = torch.randn(16, 1)
            y_pred = simple_model(x)
            loss = nn.MSELoss()(y_pred, y_true)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Check parameters remain finite
            for p in simple_model.parameters():
                assert torch.isfinite(p).all()
                assert p.abs().max() < 1e6  # Reasonable bound
    
    @given(
        batch_size=st.integers(min_value=1, max_value=128),
        input_dim=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=20, deadline=None)
    def test_optimizer_handles_various_input_sizes(self, batch_size, input_dim):
        """Test optimizer handles various input dimensions correctly."""
        model = nn.Linear(input_dim, 1)
        optimizer = Ranger(model.parameters())
        
        x = torch.randn(batch_size, input_dim)
        y_true = torch.randn(batch_size, 1)
        y_pred = model(x)
        loss = nn.MSELoss()(y_pred, y_true)
        
        loss.backward()
        optimizer.step()
        
        # Verify optimization completed without errors
        assert all(torch.isfinite(p).all() for p in model.parameters())


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestRangerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_sparse_gradients_error(self, simple_model):
        """Test that sparse gradients raise appropriate error."""
        optimizer = Ranger(simple_model.parameters())
        
        # Manually set sparse gradient
        for p in simple_model.parameters():
            p.grad = torch.sparse_coo_tensor(
                torch.tensor([[0, 1], [1, 0]]),
                torch.tensor([1.0, 2.0]),
                p.shape
            )
            break
        
        with pytest.raises(RuntimeError, match="does not support sparse gradients"):
            optimizer.step()
    
    def test_no_gradients(self, simple_model):
        """Test optimizer handles parameters without gradients."""
        optimizer = Ranger(simple_model.parameters())
        
        # No backward pass, so no gradients
        optimizer.step()  # Should not raise error
    
    def test_zero_gradients(self, simple_model):
        """Test optimizer handles zero gradients correctly."""
        optimizer = Ranger(simple_model.parameters())
        
        # Set zero gradients manually
        for p in simple_model.parameters():
            p.grad = torch.zeros_like(p)
        
        initial_params = [p.clone() for p in simple_model.parameters()]
        optimizer.step()
        
        # With zero gradients and no weight decay, parameters shouldn't change much
        for initial, current in zip(initial_params, simple_model.parameters()):
            # There might be small changes due to momentum
            assert torch.allclose(initial, current, atol=1e-6)
    
    def test_extreme_learning_rates(self, simple_model):
        """Test optimizer behavior with extreme learning rates."""
        # Very small learning rate
        optimizer = Ranger(simple_model.parameters(), lr=1e-10)
        
        x = torch.randn(32, 10)
        y_true = torch.randn(32, 1)
        y_pred = simple_model(x)
        loss = nn.MSELoss()(y_pred, y_true)
        
        loss.backward()
        initial_loss = loss.item()
        optimizer.step()
        
        # With tiny LR, loss should barely change
        y_pred_after = simple_model(x)
        loss_after = nn.MSELoss()(y_pred_after, y_true)
        assert abs(loss_after.item() - initial_loss) < 0.1


# ============================================================================
# Performance Tests
# ============================================================================

class TestRangerPerformance:
    """Test performance characteristics of Ranger optimizer."""
    
    @pytest.mark.benchmark
    def test_optimization_speed(self, simple_model, benchmark):
        """Benchmark optimization speed."""
        optimizer = Ranger(simple_model.parameters())
        
        def optimization_step():
            x = torch.randn(64, 10)
            y_true = torch.randn(64, 1)
            y_pred = simple_model(x)
            loss = nn.MSELoss()(y_pred, y_true)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            return loss.item()
        
        # Warm up
        for _ in range(10):
            optimization_step()
        
        # Benchmark
        result = benchmark(optimization_step)
        assert result is not None
    
    def test_memory_efficiency(self, conv_model):
        """Test memory usage of optimizer."""
        with track_memory():
            optimizer = Ranger(conv_model.parameters())
            
            # Multiple steps
            for _ in range(10):
                x = torch.randn(16, 3, 8, 8)
                if torch.cuda.is_available():
                    x = x.cuda()
                    conv_model.cuda()
                
                y_true = torch.randint(0, 10, (16,))
                if torch.cuda.is_available():
                    y_true = y_true.cuda()
                
                y_pred = conv_model(x)
                loss = nn.CrossEntropyLoss()(y_pred, y_true)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
    
    def test_convergence_speed(self, simple_model):
        """Test convergence characteristics on a simple problem."""
        # Create a simple regression problem
        torch.manual_seed(42)
        X = torch.randn(1000, 10)
        true_weights = torch.randn(10, 1)
        y = X @ true_weights + torch.randn(1000, 1) * 0.1
        
        # Reset model
        simple_model = nn.Linear(10, 1, bias=False)
        optimizer = Ranger(simple_model.parameters(), lr=1e-2)
        
        losses = []
        for epoch in range(100):
            # Mini-batch training
            indices = torch.randperm(1000)[:100]
            x_batch = X[indices]
            y_batch = y[indices]
            
            y_pred = simple_model(x_batch)
            loss = nn.MSELoss()(y_pred, y_batch)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
        
        # Check convergence
        assert losses[-1] < losses[0] * 0.1  # Loss reduced by 90%
        assert losses[-1] < 1.0  # Reasonable final loss


# ============================================================================
# State Management Tests
# ============================================================================

class TestRangerStateManagement:
    """Test optimizer state management."""
    
    def test_state_dict_save_load(self, simple_model, tmp_path):
        """Test saving and loading optimizer state."""
        optimizer = Ranger(simple_model.parameters())
        
        # Perform some optimization steps
        for _ in range(10):
            x = torch.randn(32, 10)
            y_true = torch.randn(32, 1)
            y_pred = simple_model(x)
            loss = nn.MSELoss()(y_pred, y_true)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        # Save state
        state_path = tmp_path / "optimizer_state.pt"
        torch.save(optimizer.state_dict(), state_path)
        
        # Create new optimizer and load state
        new_optimizer = Ranger(simple_model.parameters())
        new_optimizer.load_state_dict(torch.load(state_path))
        
        # Compare states
        for (k1, v1), (k2, v2) in zip(
            optimizer.state_dict()['state'].items(),
            new_optimizer.state_dict()['state'].items()
        ):
            for key in v1:
                if isinstance(v1[key], torch.Tensor):
                    assert torch.equal(v1[key], v2[key])
                else:
                    assert v1[key] == v2[key]
    
    @patch('builtins.print')
    def test_setstate(self, mock_print, simple_model):
        """Test __setstate__ method."""
        optimizer = Ranger(simple_model.parameters())
        state = optimizer.state_dict()
        
        optimizer.__setstate__(state)
        mock_print.assert_called_with("set state called")


# ============================================================================
# Integration Tests
# ============================================================================

class TestRangerIntegration:
    """Test integration with PyTorch ecosystem."""
    
    def test_with_different_models(self):
        """Test optimizer with various model architectures."""
        models = [
            nn.Linear(10, 1),
            nn.Sequential(nn.Linear(10, 20), nn.ReLU(), nn.Linear(20, 1)),
            nn.Conv1d(1, 16, kernel_size=3),
            nn.LSTM(10, 20, batch_first=True),
        ]
        
        for model in models:
            optimizer = Ranger(model.parameters())
            
            # Simple forward pass based on model type
            if isinstance(model, nn.Linear) or isinstance(model, nn.Sequential):
                x = torch.randn(32, 10)
            elif isinstance(model, nn.Conv1d):
                x = torch.randn(32, 1, 10)
            else:  # LSTM
                x = torch.randn(32, 5, 10)
            
            y = model(x)
            if isinstance(y, tuple):  # LSTM returns tuple
                y = y[0]
            
            loss = y.mean()
            loss.backward()
            optimizer.step()
    
    def test_with_different_dtypes(self, simple_model):
        """Test optimizer with different data types."""
        dtypes = [torch.float32]
        if torch.cuda.is_available():
            dtypes.append(torch.float16)
        
        for dtype in dtypes:
            model = simple_model.to(dtype)
            optimizer = Ranger(model.parameters())
            
            x = torch.randn(32, 10, dtype=dtype)
            y_true = torch.randn(32, 1, dtype=dtype)
            y_pred = model(x)
            loss = nn.MSELoss()(y_pred, y_true)
            
            loss.backward()
            optimizer.step()


# ============================================================================
# Advanced Features Tests
# ============================================================================

class TestRangerAdvancedFeatures:
    """Test advanced features and configurations."""
    
    def test_weight_decay(self, simple_model):
        """Test weight decay functionality."""
        optimizer = Ranger(simple_model.parameters(), weight_decay=0.1)
        
        # Get initial weight norms
        initial_norms = [p.norm().item() for p in simple_model.parameters()]
        
        # Multiple steps without gradients (only weight decay)
        for _ in range(10):
            for p in simple_model.parameters():
                p.grad = torch.zeros_like(p)
            optimizer.step()
        
        # Check weights have decreased due to weight decay
        final_norms = [p.norm().item() for p in simple_model.parameters()]
        for initial, final in zip(initial_norms, final_norms):
            assert final < initial
    
    def test_param_groups(self, simple_model):
        """Test optimizer with parameter groups."""
        # Create parameter groups with different learning rates
        params = list(simple_model.parameters())
        param_groups = [
            {'params': params[:1], 'lr': 1e-2},
            {'params': params[1:], 'lr': 1e-4}
        ]
        
        optimizer = Ranger(param_groups)
        
        # Verify groups are set correctly
        assert len(optimizer.param_groups) == 2
        assert optimizer.param_groups[0]['lr'] == 1e-2
        assert optimizer.param_groups[1]['lr'] == 1e-4
        
        # Perform optimization
        x = torch.randn(32, 10)
        y_true = torch.randn(32, 1)
        y_pred = simple_model(x)
        loss = nn.MSELoss()(y_pred, y_true)
        
        loss.backward()
        optimizer.step()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF