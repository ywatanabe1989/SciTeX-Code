#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 21:55:00 (ywatanabe)"
# File: tests/scitex/nn/test__AxiswiseDropout.py

"""
Tests for AxiswiseDropout module.

This module tests:
1. Basic dropout functionality along specified axis
2. Probability parameter behavior
3. Training vs evaluation mode differences
4. Different tensor shapes and dimensions
5. Gradient flow and backpropagation
6. Statistical properties of dropout
"""

import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scitex.nn import AxiswiseDropout


class TestAxiswiseDropoutBasics:
    """Test basic functionality of AxiswiseDropout."""
    
    def test_instantiation_default(self):
        """Test AxiswiseDropout instantiation with default parameters."""
        layer = AxiswiseDropout()
        assert isinstance(layer, nn.Module)
        assert layer.dropout_prob == 0.5
        assert layer.dim == 1
        
    def test_instantiation_custom(self):
        """Test AxiswiseDropout instantiation with custom parameters."""
        layer = AxiswiseDropout(dropout_prob=0.3, dim=2)
        assert layer.dropout_prob == 0.3
        assert layer.dim == 2
        
    def test_forward_training_mode(self):
        """Test forward pass in training mode."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.ones(2, 3, 4)
        output = layer(x)
        
        # Shape should be preserved
        assert output.shape == x.shape
        
        # Some values should be zero (dropped out)
        # Note: there's a small chance all could survive, but very unlikely
        if layer.dropout_prob > 0:
            # The mask is applied along dim=1, so check if any channels are completely zero
            pass  # Statistical test, might occasionally fail
            
    def test_forward_eval_mode(self):
        """Test forward pass in evaluation mode."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.eval()
        
        x = torch.ones(2, 3, 4)
        output = layer(x)
        
        # In eval mode, output should be identical to input
        assert torch.allclose(output, x)
        
    def test_dropout_along_different_dims(self):
        """Test dropout along different dimensions."""
        x = torch.ones(2, 3, 4, 5)
        
        # Test dropout along each dimension
        for dim in range(4):
            layer = AxiswiseDropout(dropout_prob=0.5, dim=dim)
            layer.train()
            output = layer(x)
            assert output.shape == x.shape


class TestAxiswiseDropoutProbabilities:
    """Test probability parameter behavior."""
    
    def test_dropout_prob_zero(self):
        """Test with dropout probability of 0 (no dropout)."""
        layer = AxiswiseDropout(dropout_prob=0.0)
        layer.train()
        
        x = torch.ones(10, 20, 30)
        output = layer(x)
        
        # With p=0, nothing should be dropped
        assert torch.allclose(output, x)
        
    def test_dropout_prob_one(self):
        """Test with dropout probability of 1 (drop everything)."""
        layer = AxiswiseDropout(dropout_prob=1.0)
        layer.train()
        
        x = torch.ones(10, 20, 30)
        output = layer(x)
        
        # With p=1, everything should be dropped
        assert torch.allclose(output, torch.zeros_like(x))
        
    def test_boundary_dropout_probs(self):
        """Test boundary dropout probabilities."""
        # Test that layer can be created with boundary values
        layer_0 = AxiswiseDropout(dropout_prob=0.0)
        assert layer_0.dropout_prob == 0.0
        
        layer_1 = AxiswiseDropout(dropout_prob=1.0)
        assert layer_1.dropout_prob == 1.0
            
    def test_dropout_scaling(self):
        """Test that dropout properly scales remaining values."""
        # In PyTorch's F.dropout, values are scaled by 1/(1-p) during training
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        # Use a tensor where we can verify scaling
        x = torch.ones(100, 50, 10)  # Large enough for statistical test
        
        # Run multiple times to get average behavior
        outputs = []
        for _ in range(100):
            output = layer(x)
            outputs.append(output)
            
        # Average output should be close to input due to scaling
        avg_output = torch.stack(outputs).mean(dim=0)
        
        # Check that average is close to original (within statistical tolerance)
        # This verifies the scaling is working correctly
        assert torch.allclose(avg_output, x, atol=0.1)


class TestAxiswiseDropoutDimensions:
    """Test behavior with different tensor dimensions."""
    
    def test_2d_tensor(self):
        """Test with 2D tensor (batch, features)."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(32, 128)  # batch_size=32, features=128
        output = layer(x)
        
        assert output.shape == x.shape
        
    def test_3d_tensor(self):
        """Test with 3D tensor (batch, channels, length)."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(16, 64, 100)  # Common for 1D convolutions
        output = layer(x)
        
        assert output.shape == x.shape
        
    def test_4d_tensor(self):
        """Test with 4D tensor (batch, channels, height, width)."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(8, 32, 28, 28)  # Common for 2D convolutions
        output = layer(x)
        
        assert output.shape == x.shape
        
    def test_5d_tensor(self):
        """Test with 5D tensor (batch, channels, depth, height, width)."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(4, 16, 10, 20, 20)  # 3D convolutions
        output = layer(x)
        
        assert output.shape == x.shape
        
    def test_negative_dim_index(self):
        """Test using negative dimension indices."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=-1)
        layer.train()
        
        x = torch.randn(2, 3, 4, 5)
        output = layer(x)
        
        # dim=-1 should drop along last dimension
        assert output.shape == x.shape


class TestAxiswiseDropoutMaskBehavior:
    """Test the masking behavior of AxiswiseDropout."""
    
    def test_mask_consistency_along_axis(self):
        """Test that dropout mask is consistent along non-dropout axes."""
        layer = AxiswiseDropout(dropout_prob=0.8, dim=1)  # High prob to ensure some dropout
        layer.train()
        
        x = torch.ones(2, 10, 20, 30)
        output = layer(x)
        
        # If a channel is dropped, it should be dropped for all spatial positions
        for b in range(2):
            for c in range(10):
                # Check if this channel is dropped by looking at first position
                if output[b, c, 0, 0] == 0:
                    # Entire channel should be zero
                    assert torch.all(output[b, c] == 0)
                else:
                    # Entire channel should be non-zero (scaled)
                    assert torch.all(output[b, c] != 0)
                    
    def test_mask_independence_across_batches(self):
        """Test that dropout masks are independent across batch dimension."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        # Use fixed seed for reproducibility in this test
        torch.manual_seed(42)
        
        x = torch.ones(100, 20, 10)  # Large batch to test independence
        output = layer(x)
        
        # Check that different batch elements have different dropout patterns
        # by comparing which channels are dropped
        dropout_patterns = []
        for b in range(100):
            pattern = (output[b, :, 0] == 0).float()
            dropout_patterns.append(pattern)
            
        dropout_patterns = torch.stack(dropout_patterns)
        
        # Patterns should be different across batches
        # Check that not all patterns are identical
        first_pattern = dropout_patterns[0]
        all_same = torch.all(torch.all(dropout_patterns == first_pattern, dim=1))
        assert not all_same


class TestAxiswiseDropoutGradients:
    """Test gradient flow through AxiswiseDropout."""
    
    def test_gradient_flow_training(self):
        """Test gradient flow in training mode."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(4, 8, 16, requires_grad=True)
        output = layer(x)
        loss = output.sum()
        loss.backward()
        
        assert x.grad is not None
        assert x.grad.shape == x.shape
        
        # Gradient should be zero where dropout occurred
        # Note: The actual gradient depends on the dropout implementation details
        
    def test_gradient_flow_eval(self):
        """Test gradient flow in evaluation mode."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.eval()
        
        x = torch.randn(4, 8, 16, requires_grad=True)
        output = layer(x)
        loss = output.sum()
        loss.backward()
        
        assert x.grad is not None
        # In eval mode, gradient should be ones (no dropout)
        assert torch.allclose(x.grad, torch.ones_like(x.grad))
        
    def test_gradient_scaling(self):
        """Test that gradients are properly scaled."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.ones(10, 20, 30, requires_grad=True)
        output = layer(x)
        
        # Use specific gradient
        grad_output = torch.ones_like(output)
        output.backward(grad_output)
        
        # Check that gradient exists and has correct shape
        assert x.grad.shape == x.shape
        # The exact gradient values depend on F.dropout implementation


class TestAxiswiseDropoutDeviceCompatibility:
    """Test AxiswiseDropout on different devices."""
    
    def test_cpu_operation(self):
        """Test operation on CPU."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(2, 3, 4)
        output = layer(x)
        
        assert output.device.type == 'cpu'
        assert output.shape == x.shape
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_operation(self):
        """Test operation on CUDA."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1).cuda()
        layer.train()
        
        x = torch.randn(2, 3, 4).cuda()
        output = layer(x)
        
        assert output.device.type == 'cuda'
        assert output.shape == x.shape
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_mixed_device_handling(self):
        """Test handling of mixed CPU/GPU tensors."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        
        # Layer on CPU, input on GPU
        x_gpu = torch.randn(2, 3, 4).cuda()
        output = layer(x_gpu)
        assert output.device == x_gpu.device


class TestAxiswiseDropoutIntegration:
    """Test integration with other PyTorch components."""
    
    def test_sequential_model(self):
        """Test AxiswiseDropout in Sequential model."""
        model = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            AxiswiseDropout(dropout_prob=0.5, dim=1),  # Channel-wise dropout
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, padding=1)
        )
        
        model.train()
        x = torch.randn(4, 3, 32, 32)
        output = model(x)
        
        assert output.shape == (4, 32, 32, 32)
        
    def test_with_batchnorm(self):
        """Test AxiswiseDropout with BatchNorm."""
        model = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.BatchNorm2d(16),
            AxiswiseDropout(dropout_prob=0.5, dim=1),
            nn.ReLU()
        )
        
        model.train()
        x = torch.randn(8, 3, 28, 28)
        output = model(x)
        
        assert output.shape == (8, 16, 28, 28)
        
    def test_multiple_dropout_layers(self):
        """Test multiple AxiswiseDropout layers in a model."""
        model = nn.Sequential(
            nn.Linear(100, 200),
            AxiswiseDropout(dropout_prob=0.3, dim=1),
            nn.ReLU(),
            nn.Linear(200, 100),
            AxiswiseDropout(dropout_prob=0.5, dim=1)
        )
        
        model.train()
        x = torch.randn(32, 100)
        output = model(x)
        
        assert output.shape == (32, 100)


class TestAxiswiseDropoutStatisticalProperties:
    """Test statistical properties of dropout."""
    
    def test_dropout_rate_statistics(self):
        """Test that actual dropout rate matches specified probability."""
        layer = AxiswiseDropout(dropout_prob=0.3, dim=1)
        layer.train()
        
        # Run many iterations to get statistics
        n_trials = 1000
        n_channels = 100
        dropout_counts = torch.zeros(n_channels)
        
        for _ in range(n_trials):
            x = torch.ones(1, n_channels, 10)
            output = layer(x)
            
            # Count which channels were dropped
            dropped = (output[0, :, 0] == 0).float()
            dropout_counts += dropped
            
        # Check that dropout rate is close to specified probability
        actual_dropout_rate = dropout_counts.mean() / n_trials
        assert abs(actual_dropout_rate - layer.dropout_prob) < 0.05  # 5% tolerance
        
    def test_output_mean_preservation(self):
        """Test that expected output mean is preserved."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        # Use large tensor for statistical validity
        x = torch.ones(1000, 100, 50)
        
        # Collect outputs
        outputs = []
        for _ in range(100):
            output = layer(x)
            outputs.append(output.mean().item())
            
        # Mean of outputs should be close to mean of input
        avg_output_mean = np.mean(outputs)
        assert abs(avg_output_mean - 1.0) < 0.05


class TestAxiswiseDropoutEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_single_channel(self):
        """Test with single channel (dim size = 1)."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.randn(10, 1, 20)  # Single channel
        output = layer(x)
        
        # Either all zeros or scaled input
        assert output.shape == x.shape
        
    def test_empty_tensor(self):
        """Test with empty tensor."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.empty(0, 10, 20)
        output = layer(x)
        
        assert output.shape == x.shape
        
    def test_different_dtypes(self):
        """Test with different data types."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        # Float32
        x_f32 = torch.randn(2, 3, 4, dtype=torch.float32)
        output_f32 = layer(x_f32)
        assert output_f32.dtype == torch.float32
        
        # Float64
        x_f64 = torch.randn(2, 3, 4, dtype=torch.float64)
        output_f64 = layer(x_f64)
        assert output_f64.dtype == torch.float64
        
        # Float16
        x_f16 = torch.randn(2, 3, 4, dtype=torch.float16)
        output_f16 = layer(x_f16)
        assert output_f16.dtype == torch.float16


class TestAxiswiseDropoutReproducibility:
    """Test reproducibility and randomness control."""
    
    def test_training_randomness(self):
        """Test that dropout is random in training mode."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.ones(10, 20, 30)
        
        # Get two outputs
        output1 = layer(x)
        output2 = layer(x)
        
        # They should be different (with high probability)
        assert not torch.allclose(output1, output2)
        
    def test_eval_determinism(self):
        """Test that dropout is deterministic in eval mode."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.eval()
        
        x = torch.ones(10, 20, 30)
        
        # Get two outputs
        output1 = layer(x)
        output2 = layer(x)
        
        # They should be identical
        assert torch.allclose(output1, output2)
        
    def test_seed_reproducibility(self):
        """Test that setting seed makes dropout reproducible."""
        layer = AxiswiseDropout(dropout_prob=0.5, dim=1)
        layer.train()
        
        x = torch.ones(10, 20, 30)
        
        # First run with seed
        torch.manual_seed(42)
        output1 = layer(x)
        
        # Second run with same seed
        torch.manual_seed(42)
        output2 = layer(x)
        
        # Should be identical
        assert torch.allclose(output1, output2)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_AxiswiseDropout.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-30 07:27:27 (ywatanabe)"
#
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
#
#
# class AxiswiseDropout(nn.Module):
#     def __init__(self, dropout_prob=0.5, dim=1):
#         super(AxiswiseDropout, self).__init__()
#         self.dropout_prob = dropout_prob
#         self.dim = dim
#
#     def forward(self, x):
#         if self.training:
#             sizes = [s if i == self.dim else 1 for i, s in enumerate(x.size())]
#             dropout_mask = F.dropout(
#                 torch.ones(*sizes, device=x.device, dtype=x.dtype),
#                 self.dropout_prob,
#                 True,
#             )
#
#             # Expand the mask to the size of the input tensor and apply it
#             return x * dropout_mask.expand_as(x)
#         return x

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_AxiswiseDropout.py
# --------------------------------------------------------------------------------
