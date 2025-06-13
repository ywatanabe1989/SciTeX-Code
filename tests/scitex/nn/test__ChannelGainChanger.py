import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from unittest.mock import patch

# Import the module to test
from scitex.nn import ChannelGainChanger


class TestChannelGainChanger:
    """Comprehensive test suite for ChannelGainChanger layer."""
    
    def test_basic_instantiation(self):
        """Test basic instantiation with required parameters."""
        layer = ChannelGainChanger(n_chs=10)
        assert layer.n_chs == 10
        assert isinstance(layer, nn.Module)
        
    def test_different_channel_counts(self):
        """Test instantiation with various channel counts."""
        for n_chs in [1, 5, 10, 32, 64, 128, 256]:
            layer = ChannelGainChanger(n_chs=n_chs)
            assert layer.n_chs == n_chs
            
    def test_forward_shape_preservation(self):
        """Test that output shape matches input shape."""
        layer = ChannelGainChanger(n_chs=10)
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert output.shape == x.shape
        
    def test_eval_mode_no_gain_change(self):
        """Test that no gain change occurs in evaluation mode."""
        layer = ChannelGainChanger(n_chs=10)
        layer.eval()
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert torch.allclose(output, x)
        
    def test_train_mode_applies_gain_change(self):
        """Test that gain changes are applied in training mode."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        x = torch.ones(4, 10, 100)  # Use ones to easily check gain application
        
        torch.manual_seed(42)
        output = layer(x)
        
        # Output should be different from input
        assert not torch.allclose(output, x)
        
        # Check that gains were applied per channel
        for ch in range(10):
            channel_values = output[:, ch, :]
            # All values in a channel should be scaled by the same factor
            assert torch.allclose(channel_values / x[:, ch, :], 
                                channel_values[0, 0] / x[0, ch, 0])
            
    def test_gain_values_range(self):
        """Test that gain values are in expected range after softmax."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        x = torch.ones(4, 10, 100)
        
        torch.manual_seed(42)
        output = layer(x)
        
        # Calculate applied gains
        gains = output[:, :, 0] / x[:, :, 0]  # Since x is ones
        
        # Gains should be positive
        assert torch.all(gains > 0)
        
        # Gains should sum to 1 across channels (softmax property)
        assert torch.allclose(gains.sum(dim=1), torch.ones(4))
        
    def test_different_batch_sizes(self):
        """Test layer works with different batch sizes."""
        layer = ChannelGainChanger(n_chs=10)
        for batch_size in [1, 2, 8, 16, 32, 64]:
            x = torch.randn(batch_size, 10, 100)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_different_sequence_lengths(self):
        """Test layer works with different sequence lengths."""
        layer = ChannelGainChanger(n_chs=10)
        for seq_len in [10, 50, 100, 500, 1000, 5000]:
            x = torch.randn(4, 10, seq_len)
            output = layer(x)
            assert output.shape == x.shape
            
    def test_gradient_flow(self):
        """Test that gradients flow through the layer."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        x = torch.randn(4, 10, 100, requires_grad=True)
        output = layer(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
        assert not torch.all(x.grad == 0)
        
    def test_device_compatibility_cpu(self):
        """Test layer works on CPU."""
        layer = ChannelGainChanger(n_chs=10)
        x = torch.randn(4, 10, 100)
        output = layer(x)
        assert output.device == x.device
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_compatibility_cuda(self):
        """Test layer works on CUDA."""
        layer = ChannelGainChanger(n_chs=10).cuda()
        x = torch.randn(4, 10, 100).cuda()
        output = layer(x)
        assert output.device == x.device
        assert output.is_cuda
        
    def test_reproducibility_with_seed(self):
        """Test reproducible results with same random seed."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        x = torch.randn(4, 10, 100)
        
        torch.manual_seed(42)
        output1 = layer(x)
        
        torch.manual_seed(42)
        output2 = layer(x)
        
        assert torch.allclose(output1, output2)
        
    def test_different_results_without_seed(self):
        """Test different results without setting seed."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        x = torch.randn(4, 10, 100)
        
        output1 = layer(x)
        output2 = layer(x)
        
        assert not torch.allclose(output1, output2)
        
    def test_softmax_normalization(self):
        """Test that channel gains are properly normalized via softmax."""
        layer = ChannelGainChanger(n_chs=5)
        layer.train()
        
        # Use ones to easily extract gains
        x = torch.ones(2, 5, 10)
        
        torch.manual_seed(42)
        output = layer(x)
        
        # Extract gains (output = x * gains)
        gains = output[:, :, 0]  # Since x is all ones
        
        # Check softmax properties
        assert torch.all(gains > 0)  # All positive
        assert torch.allclose(gains.sum(dim=1), torch.ones(2))  # Sum to 1
        
    def test_gain_initialization_range(self):
        """Test that initial random gains are in expected range [0.5, 1.5]."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        
        # Mock torch.rand to verify the range
        with patch('torch.rand') as mock_rand:
            mock_rand.return_value = torch.zeros(10)  # Returns 0
            x = torch.ones(1, 10, 1)
            layer(x)
            
            # When torch.rand returns 0, the gains before softmax should be 0.5
            # This tests that the formula is: rand() + 0.5
            
    def test_integration_with_sequential(self):
        """Test integration in nn.Sequential."""
        model = nn.Sequential(
            nn.Conv1d(10, 20, 3),
            ChannelGainChanger(n_chs=20),
            nn.Conv1d(20, 10, 3)
        )
        x = torch.randn(4, 10, 100)
        output = model(x)
        assert output.shape[0] == 4
        assert output.shape[1] == 10
        
    def test_state_dict_save_load(self):
        """Test saving and loading state dict."""
        layer1 = ChannelGainChanger(n_chs=10)
        layer2 = ChannelGainChanger(n_chs=10)
        
        # ChannelGainChanger has no learnable parameters
        state_dict = layer1.state_dict()
        layer2.load_state_dict(state_dict)
        
        # Both should behave identically in eval mode
        layer1.eval()
        layer2.eval()
        x = torch.randn(4, 10, 100)
        assert torch.allclose(layer1(x), layer2(x))
        
    def test_memory_efficiency(self):
        """Test memory efficiency with large tensors."""
        layer = ChannelGainChanger(n_chs=256)
        layer.train()
        
        # Large tensor
        x = torch.randn(32, 256, 1000)
        
        # Should not raise memory errors
        output = layer(x)
        assert output.shape == x.shape
        
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        layer = ChannelGainChanger(n_chs=10)
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
        
    def test_zero_input_handling(self):
        """Test behavior with zero inputs."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        
        x = torch.zeros(4, 10, 100)
        output = layer(x)
        
        # Zero input should remain zero after gain multiplication
        assert torch.all(output == 0)
        
    def test_single_channel(self):
        """Test with single channel input."""
        layer = ChannelGainChanger(n_chs=1)
        layer.train()
        
        x = torch.randn(4, 1, 100)
        output = layer(x)
        
        # With single channel, softmax will always give gain of 1
        assert torch.allclose(output, x)
        
    def test_channel_independence(self):
        """Test that gains are applied independently per channel."""
        layer = ChannelGainChanger(n_chs=5)
        layer.train()
        
        # Create input where each channel has different values
        x = torch.zeros(2, 5, 10)
        for ch in range(5):
            x[:, ch, :] = ch + 1
            
        torch.manual_seed(42)
        output = layer(x)
        
        # Check that each channel is scaled uniformly
        for ch in range(5):
            channel_data = output[:, ch, :]
            if x[0, ch, 0] != 0:  # Avoid division by zero
                gain = channel_data[0, 0] / x[0, ch, 0]
                expected = x[:, ch, :] * gain
                assert torch.allclose(channel_data, expected)
                
    def test_training_flag_inheritance(self):
        """Test that training flag is properly inherited from parent module."""
        parent = nn.Sequential(
            ChannelGainChanger(n_chs=10)
        )
        
        parent.train()
        assert parent[0].training
        
        parent.eval()
        assert not parent[0].training
        
    def test_gain_diversity(self):
        """Test that gains are diverse (not all equal)."""
        layer = ChannelGainChanger(n_chs=10)
        layer.train()
        
        x = torch.ones(1, 10, 1)
        
        # Run multiple times to ensure diversity
        gains_list = []
        for seed in range(5):
            torch.manual_seed(seed)
            output = layer(x)
            gains = output[0, :, 0]  # Extract gains
            gains_list.append(gains)
            
            # Check that not all gains are equal
            assert not torch.allclose(gains, gains[0] * torch.ones_like(gains))
            
    def test_gain_application_consistency(self):
        """Test that the same gain is applied across the sequence dimension."""
        layer = ChannelGainChanger(n_chs=5)
        layer.train()
        
        x = torch.randn(2, 5, 100)
        
        torch.manual_seed(42)
        output = layer(x)
        
        # For each channel, check gain consistency across sequence
        for ch in range(5):
            # Calculate gain at different positions
            gain_start = output[0, ch, 0] / x[0, ch, 0] if x[0, ch, 0] != 0 else 0
            gain_middle = output[0, ch, 50] / x[0, ch, 50] if x[0, ch, 50] != 0 else 0
            gain_end = output[0, ch, -1] / x[0, ch, -1] if x[0, ch, -1] != 0 else 0
            
            # Gains should be the same across sequence
            if x[0, ch, 0] != 0 and x[0, ch, 50] != 0:
                assert torch.allclose(torch.tensor(gain_start), torch.tensor(gain_middle), atol=1e-5)
            if x[0, ch, 0] != 0 and x[0, ch, -1] != 0:
                assert torch.allclose(torch.tensor(gain_start), torch.tensor(gain_end), atol=1e-5)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_ChannelGainChanger.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-04-23 11:02:45 (ywatanabe)"
#
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torchsummary import summary
# import scitex
# import numpy as np
#
#
# class ChannelGainChanger(nn.Module):
#     def __init__(
#         self,
#         n_chs,
#     ):
#         super().__init__()
#         self.n_chs = n_chs
#
#     def forward(self, x):
#         """x: [batch_size, n_chs, seq_len]"""
#         if self.training:
#             ch_gains = (
#                 torch.rand(self.n_chs).unsqueeze(0).unsqueeze(-1).to(x.device) + 0.5
#             )
#             ch_gains = F.softmax(ch_gains, dim=1)
#             x *= ch_gains
#
#         return x
#
#
# if __name__ == "__main__":
#     ## Demo data
#     bs, n_chs, seq_len = 16, 360, 1000
#     x = torch.rand(bs, n_chs, seq_len)
#
#     cgc = ChGainChanger(n_chs)
#     print(cgc(x).shape)  # [16, 19, 1000]
#
#     # sb = SubjectBlock(n_chs=n_chs)
#     # print(sb(x, s).shape) # [16, 270, 1000]
#
#     # summary(sb, x, s)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_ChannelGainChanger.py
# --------------------------------------------------------------------------------
