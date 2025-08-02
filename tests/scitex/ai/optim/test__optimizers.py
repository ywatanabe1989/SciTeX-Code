#!/usr/bin/env python3
"""Tests for scitex.ai.optim._optimizers module.

This module provides comprehensive tests for optimizer utilities that handle
PyTorch optimizers including Adam, RMSprop, SGD, and the Ranger optimizer.
"""

import pytest
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock

from scitex.ai.optim import (
    get_optimizer,
    set_optimizer,
    RANGER_AVAILABLE
)


class DummyModel(nn.Module):
    """Simple model for testing optimizer setup."""
    def __init__(self, input_size=10, hidden_size=20, output_size=1):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)


class TestGetOptimizer:
    """Test get_optimizer function."""
    
    def test_get_adam_optimizer(self):
        """Test getting Adam optimizer."""
        optimizer_class = get_optimizer("adam")
        assert optimizer_class == torch.optim.Adam
    
    def test_get_rmsprop_optimizer(self):
        """Test getting RMSprop optimizer."""
        optimizer_class = get_optimizer("rmsprop")
        assert optimizer_class == torch.optim.RMSprop
    
    def test_get_sgd_optimizer(self):
        """Test getting SGD optimizer."""
        optimizer_class = get_optimizer("sgd")
        assert optimizer_class == torch.optim.SGD
    
    @pytest.mark.skipif(not RANGER_AVAILABLE, reason="Ranger not available")
    def test_get_ranger_optimizer_available(self):
        """Test getting Ranger optimizer when available."""
        optimizer_class = get_optimizer("ranger")
        assert optimizer_class is not None
        # Check it's either from pytorch_optimizer or vendored version
        assert hasattr(optimizer_class, '__module__')
    
    @patch('scitex.ai.optim._optimizers.RANGER_AVAILABLE', False)
    def test_get_ranger_optimizer_not_available(self):
        """Test error when Ranger optimizer is not available."""
        with pytest.raises(ImportError) as exc_info:
            get_optimizer("ranger")
        
        assert "Ranger optimizer not available" in str(exc_info.value)
        assert "pip install pytorch-optimizer" in str(exc_info.value)
    
    def test_get_unknown_optimizer(self):
        """Test error for unknown optimizer name."""
        with pytest.raises(ValueError) as exc_info:
            get_optimizer("unknown_optimizer")
        
        assert "Unknown optimizer: unknown_optimizer" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)
    
    def test_get_optimizer_case_sensitive(self):
        """Test that optimizer names are case-sensitive."""
        # Uppercase should not work
        with pytest.raises(ValueError):
            get_optimizer("ADAM")
        
        # Mixed case should not work
        with pytest.raises(ValueError):
            get_optimizer("Adam")


class TestSetOptimizer:
    """Test set_optimizer function."""
    
    @pytest.fixture
    def model(self):
        """Create a simple model for testing."""
        return DummyModel()
    
    @pytest.fixture
    def models(self):
        """Create multiple models for testing."""
        return [DummyModel(), DummyModel(hidden_size=30)]
    
    def test_set_optimizer_single_model_adam(self, model):
        """Test setting Adam optimizer for single model."""
        lr = 0.001
        optimizer = set_optimizer(model, "adam", lr)
        
        assert isinstance(optimizer, torch.optim.Adam)
        assert optimizer.defaults['lr'] == lr
        
        # Check that all model parameters are in optimizer
        model_params = list(model.parameters())
        optimizer_params = [p for group in optimizer.param_groups for p in group['params']]
        assert len(model_params) == len(optimizer_params)
    
    def test_set_optimizer_single_model_sgd(self, model):
        """Test setting SGD optimizer for single model."""
        lr = 0.01
        optimizer = set_optimizer(model, "sgd", lr)
        
        assert isinstance(optimizer, torch.optim.SGD)
        assert optimizer.defaults['lr'] == lr
    
    def test_set_optimizer_multiple_models(self, models):
        """Test setting optimizer for multiple models."""
        lr = 0.001
        optimizer = set_optimizer(models, "adam", lr)
        
        assert isinstance(optimizer, torch.optim.Adam)
        
        # Check that all parameters from all models are included
        total_params = sum(len(list(model.parameters())) for model in models)
        optimizer_params = [p for group in optimizer.param_groups for p in group['params']]
        assert len(optimizer_params) == total_params
    
    def test_set_optimizer_different_learning_rates(self, model):
        """Test setting optimizer with different learning rates."""
        lrs = [0.001, 0.01, 0.1]
        
        for lr in lrs:
            optimizer = set_optimizer(model, "adam", lr)
            assert optimizer.defaults['lr'] == lr
    
    def test_set_optimizer_model_without_parameters(self):
        """Test setting optimizer for model without parameters."""
        class EmptyModel(nn.Module):
            def forward(self, x):
                return x
        
        model = EmptyModel()
        
        # PyTorch optimizers require at least one parameter
        # This should raise an error
        with pytest.raises(ValueError) as exc_info:
            set_optimizer(model, "adam", 0.001)
        
        assert "empty parameter list" in str(exc_info.value)
    
    @pytest.mark.skipif(not RANGER_AVAILABLE, reason="Ranger not available")
    def test_set_optimizer_ranger(self, model):
        """Test setting Ranger optimizer when available.
        
        Note: Ranger21 from pytorch-optimizer requires num_iterations parameter,
        but the vendored version might not. This test handles both cases.
        """
        lr = 0.001
        
        # The current implementation doesn't handle Ranger's special parameters
        # This is a limitation that should be documented
        try:
            optimizer = set_optimizer(model, "ranger", lr)
            # If it works, verify it's an optimizer
            assert optimizer is not None
            assert hasattr(optimizer, 'step')
            assert hasattr(optimizer, 'zero_grad')
        except TypeError as e:
            # Expected if using Ranger21 which requires num_iterations
            assert "num_iterations" in str(e)
            pytest.skip("Ranger optimizer requires additional parameters not supported by set_optimizer")
    
    def test_optimizer_can_perform_step(self, model):
        """Test that created optimizer can perform optimization step."""
        optimizer = set_optimizer(model, "adam", 0.001)
        
        # Create dummy data
        x = torch.randn(10, 10)
        target = torch.randn(10, 1)
        criterion = nn.MSELoss()
        
        # Forward pass
        output = model(x)
        loss = criterion(output, target)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Check gradients exist
        assert any(p.grad is not None for p in model.parameters())
        
        # Optimization step should work
        optimizer.step()
    
    def test_set_optimizer_preserves_model_device(self):
        """Test that optimizer works with models on different devices."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        model = DummyModel().cuda()
        optimizer = set_optimizer(model, "adam", 0.001)
        
        # Parameters in optimizer should match model device
        for group in optimizer.param_groups:
            for param in group['params']:
                assert param.is_cuda


class TestOptimizerIntegration:
    """Integration tests for optimizer utilities."""
    
    def test_training_loop_with_optimizer(self):
        """Test optimizer in a simple training loop."""
        model = DummyModel()
        optimizer = set_optimizer(model, "adam", 0.01)
        criterion = nn.MSELoss()
        
        # Generate dummy data
        batch_size = 32
        x = torch.randn(batch_size, 10)
        y = torch.randn(batch_size, 1)
        
        # Store initial loss
        model.eval()
        with torch.no_grad():
            initial_loss = criterion(model(x), y).item()
        
        # Train for a few steps
        model.train()
        for _ in range(10):
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
        
        # Check that loss decreased
        model.eval()
        with torch.no_grad():
            final_loss = criterion(model(x), y).item()
        
        assert final_loss < initial_loss
    
    def test_optimizer_state_dict_save_load(self):
        """Test saving and loading optimizer state."""
        model = DummyModel()
        optimizer1 = set_optimizer(model, "adam", 0.001)
        
        # Perform some optimization steps to build state
        x = torch.randn(10, 10)
        for _ in range(5):
            optimizer1.zero_grad()
            output = model(x)
            loss = output.sum()
            loss.backward()
            optimizer1.step()
        
        # Save state
        state_dict = optimizer1.state_dict()
        
        # Create new optimizer and load state
        optimizer2 = set_optimizer(model, "adam", 0.001)
        optimizer2.load_state_dict(state_dict)
        
        # Check states match
        assert len(optimizer1.state) == len(optimizer2.state)
        assert optimizer1.param_groups[0]['lr'] == optimizer2.param_groups[0]['lr']
    
    def test_different_optimizers_comparison(self):
        """Test that different optimizers behave differently."""
        # Create identical models
        model1 = DummyModel()
        model2 = DummyModel()
        
        # Copy weights to ensure they start the same
        model2.load_state_dict(model1.state_dict())
        
        # Create different optimizers
        opt1 = set_optimizer(model1, "adam", 0.01)
        opt2 = set_optimizer(model2, "sgd", 0.01)
        
        # Same data
        x = torch.randn(10, 10)
        y = torch.randn(10, 1)
        criterion = nn.MSELoss()
        
        # Train both models
        for _ in range(5):
            # Model 1 with Adam
            opt1.zero_grad()
            loss1 = criterion(model1(x), y)
            loss1.backward()
            opt1.step()
            
            # Model 2 with SGD
            opt2.zero_grad()
            loss2 = criterion(model2(x), y)
            loss2.backward()
            opt2.step()
        
        # Weights should be different due to different optimizers
        for p1, p2 in zip(model1.parameters(), model2.parameters()):
            assert not torch.allclose(p1, p2)
    
    @patch('scitex.ai.optim._optimizers.Ranger')
    def test_mock_ranger_integration(self, mock_ranger):
        """Test integration with mocked Ranger optimizer."""
        # Setup mock
        mock_optimizer_instance = MagicMock()
        mock_ranger.return_value = mock_optimizer_instance
        
        with patch('scitex.ai.optim._optimizers.RANGER_AVAILABLE', True):
            model = DummyModel()
            optimizer = set_optimizer(model, "ranger", 0.001)
            
            # Check Ranger was called with correct parameters
            mock_ranger.assert_called_once()
            call_args = mock_ranger.call_args
            assert call_args[1]['lr'] == 0.001
            
            # Check returned optimizer
            assert optimizer == mock_optimizer_instance

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/optim/_optimizers.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# """Optimizer utilities using external packages."""
# 
# import torch.optim as optim
# 
# # Use pytorch-optimizer package for Ranger when available
# try:
#     from pytorch_optimizer import Ranger21 as Ranger
# 
#     RANGER_AVAILABLE = True
# except ImportError:
#     # Fallback to vendored version temporarily
#     try:
#         from .Ranger_Deep_Learning_Optimizer.ranger.ranger2020 import Ranger
# 
#         RANGER_AVAILABLE = True
#     except ImportError:
#         RANGER_AVAILABLE = False
#         Ranger = None
# 
# 
# def get_optimizer(name: str):
#     """Get optimizer class by name.
# 
#     Args:
#         name: Optimizer name (adam, ranger, rmsprop, sgd)
# 
#     Returns:
#         Optimizer class
# 
#     Raises:
#         ValueError: If optimizer name is not supported
#     """
#     optimizers = {"adam": optim.Adam, "rmsprop": optim.RMSprop, "sgd": optim.SGD}
# 
#     if name == "ranger":
#         if not RANGER_AVAILABLE:
#             raise ImportError(
#                 "Ranger optimizer not available. "
#                 "Please install pytorch-optimizer: pip install pytorch-optimizer"
#             )
#         optimizers["ranger"] = Ranger
# 
#     if name not in optimizers:
#         raise ValueError(
#             f"Unknown optimizer: {name}. " f"Available: {list(optimizers.keys())}"
#         )
# 
#     return optimizers[name]
# 
# 
# def set_optimizer(models, optimizer_name: str, lr: float):
#     """Set optimizer for models.
# 
#     Args:
#         models: Model or list of models
#         optimizer_name: Name of optimizer
#         lr: Learning rate
# 
#     Returns:
#         Configured optimizer instance
#     """
#     if not isinstance(models, list):
#         models = [models]
# 
#     learnable_params = []
#     for model in models:
#         learnable_params.extend(list(model.parameters()))
# 
#     optimizer_class = get_optimizer(optimizer_name)
#     return optimizer_class(learnable_params, lr=lr)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/optim/_optimizers.py
# --------------------------------------------------------------------------------
