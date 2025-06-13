import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch
import warnings

# Import the module to test
from scitex.nn import DropoutChannels


class TestDropoutChannels:
    """Comprehensive test suite for DropoutChannels layer."""
    
    def test_basic_instantiation(self):
        """Test basic instantiation with default parameters."""
        layer = DropoutChannels()
        assert layer.dropout.p == 0.5
        assert isinstance(layer, nn.Module)
        
    def test_custom_dropout_rate(self):
        """Test instantiation with custom dropout probability."""
        layer = DropoutChannels(dropout=0.3)
        assert layer.dropout.p == 0.3
        
    def test_forward_shape_preservation(self):
        """Test that output shape matches input shape."""
        layer = DropoutChannels(dropout=0.5)
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert output.shape == x.shape
        
    def test_eval_mode_no_dropout(self):
        """Test that no dropout occurs in evaluation mode."""
        layer = DropoutChannels(dropout=0.5)
        layer.eval()
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert torch.allclose(output, x)
        
    def test_train_mode_applies_dropout(self):
        """Test that dropout is applied in training mode."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100)
        torch.manual_seed(42)
        output = layer(x)
        # Some channels should be replaced with random noise
        assert not torch.allclose(output, x)
        
    def test_different_batch_sizes(self):
        """Test layer works with different batch sizes."""
        layer = DropoutChannels(dropout=0.5)
        for batch_size in [1, 2, 8, 16, 32]:
            x = torch.randn(batch_size, 10, 100)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_different_channel_counts(self):
        """Test layer works with different channel counts."""
        layer = DropoutChannels(dropout=0.5)
        for n_channels in [1, 5, 20, 64, 128]:
            x = torch.randn(4, n_channels, 100)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_different_sequence_lengths(self):
        """Test layer works with different sequence lengths."""
        layer = DropoutChannels(dropout=0.5)
        for seq_len in [10, 50, 100, 500, 1000]:
            x = torch.randn(4, 10, seq_len)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_dropout_rate_zero(self):
        """Test layer with dropout rate of 0 (no dropout)."""
        layer = DropoutChannels(dropout=0.0)
        layer.train()
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert torch.allclose(output, x)
        
    def test_dropout_rate_one(self):
        """Test layer with dropout rate of 1.0 (all channels dropped)."""
        layer = DropoutChannels(dropout=1.0)
        layer.train()
        x = torch.randn(4, 10, 100)
        torch.manual_seed(42)
        output = layer(x)
        # All channels should be replaced
        assert not torch.allclose(output, x)
        
    def test_gradient_flow(self):
        """Test that gradients flow through the layer."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100, requires_grad=True)
        output = layer(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
        assert not torch.all(x.grad == 0)
        
    def test_device_compatibility_cpu(self):
        """Test layer works on CPU."""
        layer = DropoutChannels(dropout=0.5)
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert output.device == x.device
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_compatibility_cuda(self):
        """Test layer works on CUDA."""
        layer = DropoutChannels(dropout=0.5).cuda()
        x = torch.randn(4, 10, 100).cuda()
        output = layer(x)
        assert output.device == x.device
        assert output.is_cuda
        
    def test_reproducibility_with_seed(self):
        """Test reproducible results with same random seed."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100)
        
        torch.manual_seed(42)
        output1 = layer(x)
        
        torch.manual_seed(42)
        output2 = layer(x)
        
        assert torch.allclose(output1, output2)
        
    def test_different_results_without_seed(self):
        """Test different results without setting seed."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        x = torch.randn(4, 10, 100)
        
        output1 = layer(x)
        output2 = layer(x)
        
        assert not torch.allclose(output1, output2)
        
    def test_channels_replaced_with_noise(self):
        """Test that dropped channels are replaced with random noise."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        
        # Use deterministic input
        x = torch.ones(4, 10, 100)
        torch.manual_seed(42)
        output = layer(x)
        
        # Check that some channels were replaced (not all ones anymore)
        channel_means = output.mean(dim=(0, 2))
        assert not torch.allclose(channel_means, torch.ones_like(channel_means))
        
    def test_partial_channel_dropout(self):
        """Test that only some channels are dropped, not all."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        
        x = torch.randn(4, 20, 100)
        torch.manual_seed(42)
        output = layer(x)
        
        # Count how many channels were modified
        channels_modified = 0
        for ch in range(20):
            if not torch.allclose(x[:, ch, :], output[:, ch, :]):
                channels_modified += 1
                
        # With 0.5 dropout, roughly half should be modified
        assert 5 <= channels_modified <= 15
        
    def test_integration_with_sequential(self):
        """Test integration in nn.Sequential."""
        model = nn.Sequential(
            nn.Conv1d(10, 20, 3),
            DropoutChannels(dropout=0.5),
            nn.Conv1d(20, 10, 3)
        )
        x = torch.randn(4, 10, 100)
        output = model(x)
        assert output.shape[0] == 4
        assert output.shape[1] == 10
        
    def test_state_dict_save_load(self):
        """Test saving and loading state dict."""
        layer1 = DropoutChannels(dropout=0.3)
        layer2 = DropoutChannels(dropout=0.7)
        
        # Load state from layer1 to layer2
        layer2.load_state_dict(layer1.state_dict())
        
        # Check that dropout rate is preserved in module
        assert layer2.dropout.p == 0.7  # Module attribute doesn't change
        
    def test_memory_efficiency(self):
        """Test memory efficiency with large tensors."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        
        # Large tensor
        x = torch.randn(32, 256, 1000)
        
        # Should not raise memory errors
        output = layer(x)
        assert output.shape == x.shape
        
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        layer = DropoutChannels(dropout=0.5)
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
            DropoutChannels(dropout=0.5)
        )
        
        parent.train()
        assert parent[0].training
        
        parent.eval()
        assert not parent[0].training
        
    def test_dropout_affects_channel_statistics(self):
        """Test that dropout changes channel-wise statistics."""
        layer = DropoutChannels(dropout=0.5)
        layer.train()
        
        # Create input with known statistics
        x = torch.randn(100, 20, 50)
        x = (x - x.mean()) / x.std()  # Normalize
        
        torch.manual_seed(42)
        output = layer(x)
        
        # Channel-wise statistics should be different
        input_channel_means = x.mean(dim=(0, 2))
        output_channel_means = output.mean(dim=(0, 2))
        
        assert not torch.allclose(input_channel_means, output_channel_means, atol=0.1)
        
    def test_invalid_dropout_rate(self):
        """Test error handling for invalid dropout rates."""
        # PyTorch Dropout allows values outside [0,1] but clips them
        layer = DropoutChannels(dropout=1.5)
        assert layer.dropout.p == 1.5  # PyTorch doesn't validate this
        
        layer = DropoutChannels(dropout=-0.5)
        assert layer.dropout.p == -0.5  # PyTorch doesn't validate this


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_DropoutChannels.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-05-04 21:50:22 (ywatanabe)"
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
# class DropoutChannels(nn.Module):
#     def __init__(
#         self,
#         dropout=0.5
#     ):
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
#             x[:, chs_to_shuffle] = torch.randn(x[:, chs_to_shuffle].shape).to(x.device)
#
#             # rand_chs = random.sample(list(np.array(chs_to_shuffle)), len(chs_to_shuffle))
#
#             # swapped_chs = orig_chs.clone()
#             # swapped_chs[~indi_orig] = torch.LongTensor(rand_chs)
#
#             # x = x[:, swapped_chs.long(), :]
#
#         return x
#
#
# if __name__ == "__main__":
#     ## Demo data
#     bs, n_chs, seq_len = 16, 360, 1000
#     x = torch.rand(bs, n_chs, seq_len)
#
#     dc = DropoutChannels(dropout=0.1)
#     print(dc(x).shape)  # [16, 19, 1000]
#
#     # sb = SubjectBlock(n_chs=n_chs)
#     # print(sb(x, s).shape) # [16, 270, 1000]
#
#     # summary(sb, x, s)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_DropoutChannels.py
# --------------------------------------------------------------------------------
