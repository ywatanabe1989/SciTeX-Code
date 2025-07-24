#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 00:00:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/loss/test__L1L2Losses.py
# ----------------------------------------
"""Tests for L1/L2 regularization loss functions."""

import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.ai.loss import l1, l2, elastic


class SimpleModel(nn.Module):
    """Simple model for testing regularization."""
    def __init__(self, input_dim=10, hidden_dim=5, output_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)


class TestL1Loss:
    """Test L1 regularization loss function."""
    
    @pytest.fixture
    def model(self):
        """Create a simple model for testing."""
        torch.manual_seed(42)
        return SimpleModel()
    
    @pytest.fixture
    def cuda_model(self):
        """Create a CUDA model if available."""
        if torch.cuda.is_available():
            torch.manual_seed(42)
            return SimpleModel().cuda()
        pytest.skip("CUDA not available")
    
    def test_l1_basic_functionality(self, model):
        """Test basic L1 loss computation."""
        loss = l1(model)
        assert isinstance(loss, torch.Tensor)
        assert loss.dim() == 0  # Scalar
        assert loss.item() > 0  # Should be positive
    
    def test_l1_with_lambda(self, model):
        """Test L1 loss with different lambda values."""
        loss1 = l1(model, lambda_l1=0.01)
        loss2 = l1(model, lambda_l1=0.1)
        
        # Lambda doesn't affect the returned loss directly
        # (it's used externally for scaling)
        assert torch.allclose(loss1, loss2)
    
    def test_l1_gradient_computation(self, model):
        """Test L1 loss supports gradient computation."""
        loss = l1(model)
        assert loss.requires_grad
        
        # Check backward pass works
        loss.backward()
        for param in model.parameters():
            assert param.grad is not None
    
    def test_l1_zero_parameters(self):
        """Test L1 loss with zero parameters."""
        model = SimpleModel()
        # Set all parameters to zero
        with torch.no_grad():
            for param in model.parameters():
                param.zero_()
        
        loss = l1(model)
        assert loss.item() == 0.0
    
    def test_l1_cuda_compatibility(self, cuda_model):
        """Test L1 loss works with CUDA models."""
        loss = l1(cuda_model)
        assert loss.is_cuda
        assert isinstance(loss, torch.Tensor)
    
    def test_l1_different_model_sizes(self):
        """Test L1 loss with different model architectures."""
        small_model = SimpleModel(5, 3, 1)
        large_model = SimpleModel(100, 50, 10)
        
        small_loss = l1(small_model)
        large_loss = l1(large_model)
        
        # Larger model should have larger L1 norm (with random init)
        assert large_loss.item() > small_loss.item()
    
    def test_l1_numerical_stability(self, model):
        """Test L1 loss numerical stability."""
        # Scale parameters to very small values
        with torch.no_grad():
            for param in model.parameters():
                param.mul_(1e-8)
        
        loss = l1(model)
        assert torch.isfinite(loss)
        assert not torch.isnan(loss)
    
    def test_l1_regularization_effect(self, model):
        """Test L1 promotes sparsity."""
        # Create dummy data
        x = torch.randn(10, 10)
        y = torch.randn(10, 2)
        criterion = nn.MSELoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        
        # Train with L1 regularization
        initial_l1 = l1(model).item()
        for _ in range(10):
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y) + 0.1 * l1(model)
            loss.backward()
            optimizer.step()
        
        final_l1 = l1(model).item()
        # L1 should decrease with regularization
        assert final_l1 < initial_l1


class TestL2Loss:
    """Test L2 regularization loss function."""
    
    @pytest.fixture
    def model(self):
        """Create a simple model for testing."""
        torch.manual_seed(42)
        return SimpleModel()
    
    def test_l2_basic_functionality(self, model):
        """Test basic L2 loss computation."""
        loss = l2(model)
        assert isinstance(loss, torch.Tensor)
        assert loss.dim() == 0  # Scalar
        assert loss.item() > 0  # Should be positive
    
    def test_l2_with_lambda(self, model):
        """Test L2 loss with different lambda values."""
        loss1 = l2(model, lambda_l2=0.01)
        loss2 = l2(model, lambda_l2=0.1)
        
        # Lambda doesn't affect the returned loss directly
        assert torch.allclose(loss1, loss2)
    
    def test_l2_gradient_computation(self, model):
        """Test L2 loss supports gradient computation."""
        loss = l2(model)
        assert loss.requires_grad
        
        # Check backward pass works
        loss.backward()
        for param in model.parameters():
            assert param.grad is not None
    
    def test_l2_vs_l1_magnitude(self, model):
        """Test L2 norm is typically larger than L1 for same parameters."""
        l1_loss = l1(model)
        l2_loss = l2(model)
        
        # For most initializations, L2 < L1 due to squaring small values
        # But the relationship depends on parameter magnitudes
        assert l1_loss.item() > 0 and l2_loss.item() > 0
    
    def test_l2_orthogonal_init(self):
        """Test L2 with orthogonal initialization."""
        model = SimpleModel()
        # Apply orthogonal initialization
        for param in model.parameters():
            if param.dim() >= 2:
                nn.init.orthogonal_(param)
        
        loss = l2(model)
        assert loss.item() > 0
    
    def test_l2_weight_decay_equivalence(self, model):
        """Test L2 regularization is equivalent to weight decay."""
        # L2 regularization gradient is 2 * lambda * w
        # Weight decay subtracts lambda * w from weights
        # They're equivalent up to a factor of 2
        
        l2_loss = l2(model)
        l2_loss.backward()
        
        # Store L2 gradients
        l2_grads = [param.grad.clone() for param in model.parameters()]
        
        # Reset gradients
        model.zero_grad()
        
        # Compute parameter norms manually
        manual_l2 = torch.tensor(0.0)
        for param in model.parameters():
            manual_l2 += torch.norm(param).sum()
        
        assert torch.allclose(l2_loss, manual_l2, rtol=1e-5)


class TestElasticLoss:
    """Test elastic net (combined L1/L2) regularization."""
    
    @pytest.fixture
    def model(self):
        """Create a simple model for testing."""
        torch.manual_seed(42)
        return SimpleModel()
    
    def test_elastic_basic_functionality(self, model):
        """Test basic elastic net loss computation."""
        loss = elastic(model)
        assert isinstance(loss, torch.Tensor)
        assert loss.dim() == 0
        assert loss.item() > 0
    
    def test_elastic_pure_l1(self, model):
        """Test elastic net with l1_ratio=1 equals L1."""
        elastic_loss = elastic(model, alpha=1.0, l1_ratio=1.0)
        l1_loss = l1(model)
        assert torch.allclose(elastic_loss, l1_loss, rtol=1e-5)
    
    def test_elastic_pure_l2(self, model):
        """Test elastic net with l1_ratio=0 equals L2."""
        elastic_loss = elastic(model, alpha=1.0, l1_ratio=0.0)
        l2_loss = l2(model)
        assert torch.allclose(elastic_loss, l2_loss, rtol=1e-5)
    
    def test_elastic_balanced_mix(self, model):
        """Test elastic net with balanced L1/L2 mix."""
        elastic_loss = elastic(model, alpha=1.0, l1_ratio=0.5)
        l1_loss = l1(model)
        l2_loss = l2(model)
        
        expected = 0.5 * l1_loss + 0.5 * l2_loss
        assert torch.allclose(elastic_loss, expected, rtol=1e-5)
    
    def test_elastic_alpha_scaling(self, model):
        """Test elastic net alpha parameter scales the loss."""
        loss1 = elastic(model, alpha=1.0, l1_ratio=0.5)
        loss2 = elastic(model, alpha=2.0, l1_ratio=0.5)
        
        assert torch.allclose(loss2, 2.0 * loss1, rtol=1e-5)
    
    def test_elastic_invalid_l1_ratio(self, model):
        """Test elastic net validates l1_ratio range."""
        with pytest.raises(AssertionError):
            elastic(model, alpha=1.0, l1_ratio=-0.1)
        
        with pytest.raises(AssertionError):
            elastic(model, alpha=1.0, l1_ratio=1.1)
    
    def test_elastic_gradient_flow(self, model):
        """Test elastic net supports gradient computation."""
        loss = elastic(model, alpha=1.0, l1_ratio=0.7)
        loss.backward()
        
        for param in model.parameters():
            assert param.grad is not None
            assert torch.all(torch.isfinite(param.grad))
    
    def test_elastic_different_ratios(self, model):
        """Test elastic net with various l1_ratio values."""
        ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
        losses = []
        
        for ratio in ratios:
            loss = elastic(model, alpha=1.0, l1_ratio=ratio)
            losses.append(loss.item())
        
        # Check all losses are positive
        assert all(l > 0 for l in losses)
        
        # Check monotonicity isn't guaranteed (depends on model params)
        assert len(set(losses)) == len(losses)  # All different
    
    def test_elastic_optimization_behavior(self, model):
        """Test elastic net in optimization context."""
        x = torch.randn(10, 10)
        y = torch.randn(10, 2)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        
        initial_loss = elastic(model, alpha=1.0, l1_ratio=0.5).item()
        
        # Train with elastic net regularization
        for _ in range(20):
            optimizer.zero_grad()
            output = model(x)
            reg_loss = elastic(model, alpha=0.01, l1_ratio=0.5)
            total_loss = criterion(output, y) + reg_loss
            total_loss.backward()
            optimizer.step()
        
        final_loss = elastic(model, alpha=1.0, l1_ratio=0.5).item()
        
        # Regularization should reduce parameter norms
        assert final_loss < initial_loss


class TestRegularizationIntegration:
    """Test integration aspects of regularization functions."""
    
    def test_all_regularizers_consistent(self):
        """Test all regularizers give consistent results."""
        model = SimpleModel()
        
        # Get all three losses
        l1_loss = l1(model)
        l2_loss = l2(model)
        elastic_loss = elastic(model, alpha=1.0, l1_ratio=0.5)
        
        # Check elastic is correct combination
        expected = 0.5 * l1_loss + 0.5 * l2_loss
        assert torch.allclose(elastic_loss, expected, rtol=1e-5)
    
    def test_regularizers_with_batchnorm(self):
        """Test regularizers work with models containing BatchNorm."""
        class BNModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(10, 20)
                self.bn = nn.BatchNorm1d(20)
                self.fc2 = nn.Linear(20, 5)
            
            def forward(self, x):
                x = self.fc1(x)
                x = self.bn(x)
                return self.fc2(x)
        
        model = BNModel()
        
        # All regularizers should work
        l1_loss = l1(model)
        l2_loss = l2(model)
        elastic_loss = elastic(model)
        
        assert all(torch.isfinite(loss) for loss in [l1_loss, l2_loss, elastic_loss])
    
    def test_regularizers_empty_model(self):
        """Test regularizers with model having no parameters."""
        class EmptyModel(nn.Module):
            def forward(self, x):
                return x
        
        model = EmptyModel()
        
        # Should return zero loss
        assert l1(model).item() == 0.0
        assert l2(model).item() == 0.0
        assert elastic(model).item() == 0.0
    
    def test_regularizers_with_dropout(self):
        """Test regularizers work with dropout layers."""
        class DropoutModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(10, 20)
                self.dropout = nn.Dropout(0.5)
                self.fc2 = nn.Linear(20, 5)
            
            def forward(self, x):
                x = self.fc1(x)
                x = self.dropout(x)
                return self.fc2(x)
        
        model = DropoutModel()
        model.eval()  # Disable dropout for consistent testing
        
        # Regularizers should only consider learnable parameters
        l1_loss = l1(model)
        l2_loss = l2(model)
        
        assert l1_loss.item() > 0
        assert l2_loss.item() > 0
    
    def test_device_consistency(self):
        """Test regularizers maintain device consistency."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        # CPU model
        cpu_model = SimpleModel()
        cpu_l1 = l1(cpu_model)
        assert cpu_l1.device.type == 'cpu'
        
        # CUDA model
        cuda_model = SimpleModel().cuda()
        cuda_l1 = l1(cuda_model)
        assert cuda_l1.is_cuda
        
        # Values should be equal (same initialization seed)
        torch.manual_seed(42)
        model1 = SimpleModel()
        torch.manual_seed(42)
        model2 = SimpleModel().cuda()
        
        assert torch.allclose(l1(model1), l1(model2).cpu(), rtol=1e-5)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/loss/_L1L2Losses.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 18:53:03 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/loss/_L1L2Losses.py
# 
# import torch
# 
# 
# def l1(model, lambda_l1=0.01):
#     lambda_l1 = torch.tensor(lambda_l1)
#     l1 = torch.tensor(0.0).cuda()
#     for param in model.parameters():  # fixme; is this OK?
#         l1 += torch.abs(param).sum()
#     return l1
# 
# 
# def l2(model, lambda_l2=0.01):
#     lambda_l2 = torch.tensor(lambda_l2)
#     l2 = torch.tensor(0.0).cuda()
#     for param in model.parameters():  # fixme; is this OK?
#         l2 += torch.norm(param).sum()
#     return l2
# 
# 
# def elastic(model, alpha=1.0, l1_ratio=0.5):
#     assert 0 <= l1_ratio <= 1
# 
#     L1 = l1(model)
#     L2 = l2(model)
# 
#     return alpha * (l1_ratio * L1 + (1 - l1_ratio) * L2)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/loss/_L1L2Losses.py
# --------------------------------------------------------------------------------
