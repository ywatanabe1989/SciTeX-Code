import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch
import random

# Import the module to test
from scitex.nn import SwapChannels


class TestSwapChannels:
    """Comprehensive test suite for SwapChannels layer."""
    
    def test_basic_instantiation(self):
        """Test basic instantiation with default parameters."""
        layer = SwapChannels()
        assert layer.dropout.p == 0.5
        assert isinstance(layer, nn.Module)
        
    def test_custom_dropout_rate(self):
        """Test instantiation with custom dropout probability."""
        layer = SwapChannels(dropout=0.3)
        assert layer.dropout.p == 0.3
        
    def test_forward_shape_preservation(self):
        """Test that output shape matches input shape."""
        layer = SwapChannels(dropout=0.5)
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert output.shape == x.shape
        
    def test_eval_mode_no_swapping(self):
        """Test that no channel swapping occurs in evaluation mode."""
        layer = SwapChannels(dropout=0.5)
        layer.eval()
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert torch.allclose(output, x)
        
    def test_train_mode_applies_swapping(self):
        """Test that channel swapping is applied in training mode."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100)
        
        # Set seeds for reproducibility
        torch.manual_seed(42)
        random.seed(42)
        
        output = layer(x)
        
        # Check that some channels were swapped
        channels_same = 0
        for ch in range(10):
            if torch.allclose(x[:, ch, :], output[:, ch, :]):
                channels_same += 1
                
        # Not all channels should be the same
        assert channels_same < 10
        
    def test_different_batch_sizes(self):
        """Test layer works with different batch sizes."""
        layer = SwapChannels(dropout=0.5)
        for batch_size in [1, 2, 8, 16, 32]:
            x = torch.randn(batch_size, 10, 100)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_different_channel_counts(self):
        """Test layer works with different channel counts."""
        layer = SwapChannels(dropout=0.5)
        for n_channels in [1, 5, 20, 64, 128]:
            x = torch.randn(4, n_channels, 100)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_different_sequence_lengths(self):
        """Test layer works with different sequence lengths."""
        layer = SwapChannels(dropout=0.5)
        for seq_len in [10, 50, 100, 500, 1000]:
            x = torch.randn(4, 10, seq_len)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_dropout_rate_zero(self):
        """Test layer with dropout rate of 0 (no swapping)."""
        layer = SwapChannels(dropout=0.0)
        layer.train()
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert torch.allclose(output, x)
        
    def test_dropout_rate_one(self):
        """Test layer with dropout rate of 1.0 (all channels eligible for swapping)."""
        layer = SwapChannels(dropout=1.0)
        layer.train()
        
        # Create distinct channels
        x = torch.zeros(4, 10, 100)
        for i in range(10):
            x[:, i, :] = i
            
        torch.manual_seed(42)
        random.seed(42)
        output = layer(x)
        
        # All channels should be swapped
        channels_same = 0
        for ch in range(10):
            if torch.allclose(x[:, ch, :], output[:, ch, :]):
                channels_same += 1
                
        assert channels_same == 0  # All channels should be swapped
        
    def test_gradient_flow(self):
        """Test that gradients flow through the layer."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100, requires_grad=True)
        output = layer(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
        assert not torch.all(x.grad == 0)
        
    def test_device_compatibility_cpu(self):
        """Test layer works on CPU."""
        layer = SwapChannels(dropout=0.5)
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert output.device == x.device
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_compatibility_cuda(self):
        """Test layer works on CUDA."""
        layer = SwapChannels(dropout=0.5).cuda()
        x = torch.randn(4, 10, 100).cuda()
        output = layer(x)
        assert output.device == x.device
        assert output.is_cuda
        
    def test_reproducibility_with_seed(self):
        """Test reproducible results with same random seed."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100)
        
        torch.manual_seed(42)
        random.seed(42)
        output1 = layer(x)
        
        torch.manual_seed(42)
        random.seed(42)
        output2 = layer(x)
        
        assert torch.allclose(output1, output2)
        
    def test_channel_permutation_properties(self):
        """Test that swapping is a permutation (no data loss)."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        # Create distinct channels
        x = torch.zeros(4, 10, 100)
        for i in range(10):
            x[:, i, :] = i
            
        torch.manual_seed(42)
        random.seed(42)
        output = layer(x)
        
        # Check all original values are present
        original_values = set(range(10))
        output_values = set(output[:, :, 0].flatten().tolist())
        
        assert original_values == output_values
        
    def test_swap_maintains_channel_integrity(self):
        """Test that entire channels are swapped, not mixed."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        # Create channels with unique patterns
        x = torch.zeros(2, 5, 10)
        for ch in range(5):
            x[:, ch, :] = ch * torch.ones(2, 10)
            
        output = layer(x)
        
        # Each output channel should still be uniform
        for ch in range(5):
            channel_data = output[:, ch, :]
            assert torch.all(channel_data == channel_data[0, 0])
            
    def test_integration_with_sequential(self):
        """Test integration in nn.Sequential."""
        model = nn.Sequential(
            nn.Conv1d(10, 20, 3),
            SwapChannels(dropout=0.5),
            nn.Conv1d(20, 10, 3)
        )
        x = torch.randn(4, 10, 100)
        output = model(x)
        assert output.shape[0] == 4
        assert output.shape[1] == 10
        
    def test_state_dict_save_load(self):
        """Test saving and loading state dict."""
        layer1 = SwapChannels(dropout=0.3)
        layer2 = SwapChannels(dropout=0.7)
        
        # Load state from layer1 to layer2
        layer2.load_state_dict(layer1.state_dict())
        
        # Dropout rate should remain as initialized
        assert layer2.dropout.p == 0.7
        
    def test_memory_efficiency(self):
        """Test memory efficiency with large tensors."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        # Large tensor
        x = torch.randn(32, 256, 1000)
        
        # Should not raise memory errors
        output = layer(x)
        assert output.shape == x.shape
        
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        # Test with very large values
        x = torch.randn(4, 10, 100) * 1e6
        output = layer(x)
        assert not torch.any(torch.isnan(output))
        assert not torch.any(torch.isinf(output))
        
        # Test with very small values
        x = torch.randn(4, 10, 100) * 1e-6
        output = layer(x)
        assert not torch.any(torch.isnan(output))
        assert not torch.any(torch.isinf(output))
        
    def test_training_flag_inheritance(self):
        """Test that training flag is properly inherited from parent module."""
        parent = nn.Sequential(
            SwapChannels(dropout=0.5)
        )
        
        parent.train()
        assert parent[0].training
        
        parent.eval()
        assert not parent[0].training
        
    def test_partial_channel_swapping(self):
        """Test that only some channels are swapped based on dropout rate."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        # Run multiple times to check statistical properties
        total_swaps = 0
        n_trials = 100
        n_channels = 20
        
        for _ in range(n_trials):
            x = torch.arange(n_channels).float().unsqueeze(0).unsqueeze(-1).expand(1, -1, 10)
            torch.manual_seed(None)  # Random seed
            output = layer(x)
            
            # Count swapped channels
            for ch in range(n_channels):
                if output[0, ch, 0] != ch:
                    total_swaps += 1
                    
        # Average swap rate should be close to dropout rate
        avg_swap_rate = total_swaps / (n_trials * n_channels)
        assert 0.4 <= avg_swap_rate <= 0.6  # Allow some variance
        
    def test_single_channel_no_swap(self):
        """Test that single channel input is unchanged."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        x = torch.randn(4, 1, 100)
        output = layer(x)
        assert torch.allclose(output, x)
        
    def test_zero_input_preservation(self):
        """Test that zero inputs remain zero after swapping."""
        layer = SwapChannels(dropout=0.5)
        layer.train()
        
        x = torch.zeros(4, 10, 100)
        output = layer(x)
        assert torch.all(output == 0)
        
    def test_channel_swap_symmetry(self):
        """Test that channel swapping is symmetric (bijective mapping)."""
        layer = SwapChannels(dropout=1.0)  # All channels swap
        layer.train()
        
        # Create identifiable channels
        n_channels = 10
        x = torch.arange(n_channels).float().view(1, n_channels, 1).expand(1, -1, 10)
        
        torch.manual_seed(42)
        random.seed(42)
        output = layer(x)
        
        # Find the permutation
        permutation = []
        for ch in range(n_channels):
            value = output[0, ch, 0].item()
            permutation.append(int(value))
            
        # Check it's a valid permutation
        assert sorted(permutation) == list(range(n_channels))
        assert len(set(permutation)) == n_channels  # All unique

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_SwapChannels.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-05-04 21:21:19 (ywatanabe)"
# 
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torchsummary import summary
# import scitex
# import numpy as np
# import random
# 
# 
# class SwapChannels(nn.Module):
#     def __init__(self, dropout=0.5):
#         super().__init__()
#         self.dropout = nn.Dropout(p=dropout)
# 
#     def forward(self, x):
#         """x: [batch_size, n_chs, seq_len]"""
#         if self.training:
#             orig_chs = torch.arange(x.shape[1])
# 
#             indi_orig = self.dropout(torch.ones(x.shape[1])).bool()
#             chs_to_shuffle = orig_chs[~indi_orig]
# 
#             rand_chs = random.sample(
#                 list(np.array(chs_to_shuffle)), len(chs_to_shuffle)
#             )
# 
#             swapped_chs = orig_chs.clone()
#             swapped_chs[~indi_orig] = torch.LongTensor(rand_chs)
# 
#             x = x[:, swapped_chs.long(), :]
# 
#         return x
# 
# 
# if __name__ == "__main__":
#     ## Demo data
#     bs, n_chs, seq_len = 16, 360, 1000
#     x = torch.rand(bs, n_chs, seq_len)
# 
#     sc = SwapChannels()
#     print(sc(x).shape)  # [16, 19, 1000]
# 
#     # sb = SubjectBlock(n_chs=n_chs)
#     # print(sb(x, s).shape) # [16, 270, 1000]
# 
#     # summary(sb, x, s)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_SwapChannels.py
# --------------------------------------------------------------------------------
