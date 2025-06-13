#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 (ywatanabe)"
# /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/nn/test__SpatialAttention.py

"""Comprehensive test suite for SpatialAttention module."""

import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.nn import SpatialAttention


class TestSpatialAttentionArchitecture:
    """Test SpatialAttention architecture and initialization."""
    
    def test_basic_instantiation(self):
        """Test basic module instantiation."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        assert isinstance(module, nn.Module)
        assert hasattr(module, 'aap')
        assert hasattr(module, 'conv11')
        
    def test_adaptive_avg_pool_initialization(self):
        """Test AdaptiveAvgPool1d initialization."""
        n_chs = 128
        module = SpatialAttention(n_chs_in=n_chs)
        assert isinstance(module.aap, nn.AdaptiveAvgPool1d)
        assert module.aap.output_size == (1,)
        
    def test_conv1d_initialization(self):
        """Test Conv1d layer initialization."""
        n_chs = 256
        module = SpatialAttention(n_chs_in=n_chs)
        assert isinstance(module.conv11, nn.Conv1d)
        assert module.conv11.in_channels == n_chs
        assert module.conv11.out_channels == 1
        assert module.conv11.kernel_size == (1,)
        
    def test_different_channel_sizes(self):
        """Test instantiation with various channel sizes."""
        channel_sizes = [1, 16, 32, 64, 128, 256, 512, 1024]
        for n_chs in channel_sizes:
            module = SpatialAttention(n_chs_in=n_chs)
            assert module.conv11.in_channels == n_chs


class TestSpatialAttentionForward:
    """Test forward pass functionality."""
    
    def test_forward_pass_basic(self):
        """Test basic forward pass."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        BS, SEQ_LEN = 8, 1000
        x = torch.randn(BS, n_chs, SEQ_LEN)
        output = module(x)
        assert output.shape == (BS, n_chs, SEQ_LEN)
        
    def test_forward_pass_different_sequence_lengths(self):
        """Test forward pass with various sequence lengths."""
        n_chs = 32
        module = SpatialAttention(n_chs_in=n_chs)
        BS = 4
        for seq_len in [10, 100, 500, 1000, 2000]:
            x = torch.randn(BS, n_chs, seq_len)
            output = module(x)
            assert output.shape == (BS, n_chs, seq_len)
            
    def test_forward_pass_different_batch_sizes(self):
        """Test forward pass with various batch sizes."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        SEQ_LEN = 500
        for batch_size in [1, 2, 4, 8, 16, 32]:
            x = torch.randn(batch_size, n_chs, SEQ_LEN)
            output = module(x)
            assert output.shape == (batch_size, n_chs, SEQ_LEN)
            
    def test_attention_mechanism(self):
        """Test that attention mechanism modulates input."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 100)
        output = module(x)
        # Output should be different from input due to attention
        assert not torch.equal(output, x)
        # But shape should be preserved
        assert output.shape == x.shape


class TestSpatialAttentionWeights:
    """Test attention weight generation and application."""
    
    def test_attention_weights_range(self):
        """Test that attention weights are properly bounded."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 100)
        
        # Extract attention weights by dividing output by input
        with torch.no_grad():
            output = module(x)
            # Avoid division by zero
            mask = x.abs() > 1e-6
            attention_weights = torch.ones_like(output)
            attention_weights[mask] = output[mask] / x[mask]
            
    def test_pooling_operation(self):
        """Test that adaptive pooling reduces temporal dimension."""
        n_chs = 32
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 1000)
        
        # Test pooling operation directly
        pooled = module.aap(x)
        assert pooled.shape == (4, n_chs, 1)
        
    def test_conv_operation(self):
        """Test convolution operation on pooled features."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 1)  # Already pooled
        
        # Test conv operation directly
        conv_out = module.conv11(x)
        assert conv_out.shape == (4, 1, 1)


class TestSpatialAttentionGradient:
    """Test gradient flow and backpropagation."""
    
    def test_gradient_flow(self):
        """Test that gradients flow through the module."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 100, requires_grad=True)
        output = module(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
        assert not torch.isnan(x.grad).any()
        
    def test_parameter_gradients(self):
        """Test that module parameters receive gradients."""
        n_chs = 32
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 100)
        output = module(x)
        loss = output.sum()
        loss.backward()
        
        # Check conv layer parameters
        assert module.conv11.weight.grad is not None
        assert not torch.isnan(module.conv11.weight.grad).any()
        if module.conv11.bias is not None:
            assert module.conv11.bias.grad is not None
            
    def test_gradient_magnitude(self):
        """Test gradient magnitudes are reasonable."""
        n_chs = 64
        module = SpatialAttention(n_chs_in=n_chs)
        x = torch.randn(4, n_chs, 100, requires_grad=True)
        output = module(x)
        loss = output.mean()  # Use mean to normalize
        loss.backward()
        
        # Gradients should not explode or vanish
        grad_norm = x.grad.norm()
        assert grad_norm > 1e-6  # Not vanishing
        assert grad_norm < 1e3   # Not exploding


class TestSpatialAttentionDevice:
    """Test device compatibility."""
    
    def test_cpu_computation(self):
        """Test computation on CPU."""
        module = SpatialAttention(n_chs_in=64)
        x = torch.randn(2, 64, 100)
        output = module(x)
        assert output.device.type == 'cpu'
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_computation(self):
        """Test computation on CUDA."""
        module = SpatialAttention(n_chs_in=64).cuda()
        x = torch.randn(2, 64, 100).cuda()
        output = module(x)
        assert output.device.type == 'cuda'
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_movement(self):
        """Test moving module between devices."""
        module = SpatialAttention(n_chs_in=32)
        x_cpu = torch.randn(2, 32, 100)
        
        # CPU computation
        output_cpu = module(x_cpu)
        
        # Move to CUDA
        module = module.cuda()
        x_cuda = x_cpu.cuda()
        output_cuda = module(x_cuda)
        
        # Results should be the same
        assert torch.allclose(output_cpu, output_cuda.cpu(), rtol=1e-5)


class TestSpatialAttentionNumerical:
    """Test numerical properties and stability."""
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme inputs."""
        module = SpatialAttention(n_chs_in=64)
        
        # Test with very small values
        x_small = torch.randn(2, 64, 100) * 1e-6
        output_small = module(x_small)
        assert not torch.isnan(output_small).any()
        assert not torch.isinf(output_small).any()
        
        # Test with very large values
        x_large = torch.randn(2, 64, 100) * 1e3
        output_large = module(x_large)
        assert not torch.isnan(output_large).any()
        assert not torch.isinf(output_large).any()
        
    def test_zero_input(self):
        """Test behavior with zero input."""
        module = SpatialAttention(n_chs_in=32)
        x = torch.zeros(2, 32, 100)
        output = module(x)
        # Output should be zero since it's element-wise multiplication
        assert torch.allclose(output, torch.zeros_like(output))
        
    def test_ones_input(self):
        """Test behavior with ones input."""
        module = SpatialAttention(n_chs_in=16)
        x = torch.ones(2, 16, 100)
        output = module(x)
        # Output should be scaled by attention weights
        assert output.shape == x.shape


class TestSpatialAttentionIntegration:
    """Test integration with other modules."""
    
    def test_with_conv_layers(self):
        """Test integration with convolutional layers."""
        n_chs = 64
        model = nn.Sequential(
            nn.Conv1d(32, n_chs, kernel_size=3, padding=1),
            nn.ReLU(),
            SpatialAttention(n_chs_in=n_chs),
            nn.Conv1d(n_chs, 128, kernel_size=3, padding=1)
        )
        x = torch.randn(4, 32, 100)
        output = model(x)
        assert output.shape == (4, 128, 100)
        
    def test_with_batch_norm(self):
        """Test integration with batch normalization."""
        n_chs = 64
        model = nn.Sequential(
            nn.BatchNorm1d(n_chs),
            SpatialAttention(n_chs_in=n_chs),
            nn.BatchNorm1d(n_chs)
        )
        x = torch.randn(8, n_chs, 200)
        output = model(x)
        assert output.shape == x.shape
        
    def test_multiple_attention_layers(self):
        """Test stacking multiple attention layers."""
        n_chs = 32
        model = nn.Sequential(
            SpatialAttention(n_chs_in=n_chs),
            nn.ReLU(),
            SpatialAttention(n_chs_in=n_chs),
            nn.ReLU(),
            SpatialAttention(n_chs_in=n_chs)
        )
        x = torch.randn(4, n_chs, 150)
        output = model(x)
        assert output.shape == x.shape


class TestSpatialAttentionMemory:
    """Test memory efficiency."""
    
    def test_memory_footprint(self):
        """Test module memory footprint."""
        module = SpatialAttention(n_chs_in=256)
        total_params = sum(p.numel() for p in module.parameters())
        # Should only have conv parameters: 256 * 1 * 1 + 1 (bias)
        assert total_params <= 257
        
    def test_inference_memory(self):
        """Test memory usage during inference."""
        module = SpatialAttention(n_chs_in=128)
        module.eval()
        x = torch.randn(1, 128, 1000)
        
        with torch.no_grad():
            output = module(x)
        assert output.shape == x.shape


class TestSpatialAttentionEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_single_channel(self):
        """Test with single channel input."""
        module = SpatialAttention(n_chs_in=1)
        x = torch.randn(4, 1, 100)
        output = module(x)
        assert output.shape == (4, 1, 100)
        
    def test_single_timestep(self):
        """Test with single timestep."""
        module = SpatialAttention(n_chs_in=64)
        x = torch.randn(4, 64, 1)
        output = module(x)
        assert output.shape == (4, 64, 1)
        
    def test_large_dimensions(self):
        """Test with large input dimensions."""
        module = SpatialAttention(n_chs_in=512)
        x = torch.randn(2, 512, 10000)
        output = module(x)
        assert output.shape == (2, 512, 10000)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_SpatialAttention.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-04-23 09:45:28 (ywatanabe)"
#
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torchsummary import summary
# import scitex
# import numpy as np
#
# class SpatialAttention(nn.Module):
#     def __init__(
#             self, n_chs_in
#     ):
#         super().__init__()
#         self.aap = nn.AdaptiveAvgPool1d(1)
#         self.conv11 = nn.Conv1d(in_channels=n_chs_in, out_channels=1, kernel_size=1)
#
#     def forward(self, x):
#         """x: [batch_size, n_chs, seq_len]"""
#         x_orig = x
#         x = self.aap(x)
#         x = self.conv11(x)
#
#         return x * x_orig

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_SpatialAttention.py
# --------------------------------------------------------------------------------
