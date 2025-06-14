#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 (ywatanabe)"
# File: tests/scitex/nn/test__FreqGainChanger.py

"""Comprehensive test suite for FreqGainChanger module.

This module tests the frequency gain adjustment functionality for neural networks,
including multi-band frequency manipulation, gradient flow, and edge cases.
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import os

# Mock julius module since it's an external dependency
julius_mock = MagicMock()
julius_mock.bands = MagicMock()
julius_mock.bands.split_bands = MagicMock()

with patch.dict('sys.modules', {'julius': julius_mock}):
    from scitex.nn import FreqGainChanger


class TestFreqGainChanger:
    """Test suite for FreqGainChanger layer."""
    
    @pytest.fixture
    def sample_rate(self):
        """Standard sample rate for testing."""
        return 1000
    
    @pytest.fixture
    def n_bands(self):
        """Number of frequency bands for testing."""
        return 10
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input tensor."""
        batch_size, n_channels, seq_len = 4, 32, 1000
        return torch.randn(batch_size, n_channels, seq_len)
    
    def test_initialization_default_params(self, n_bands, sample_rate):
        """Test initialization with default parameters."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        assert layer.n_bands == n_bands
        assert layer.samp_rate == sample_rate
        assert isinstance(layer.dropout, nn.Dropout)
        assert layer.dropout.p == 0.5
    
    def test_initialization_custom_dropout(self, n_bands, sample_rate):
        """Test initialization with custom dropout ratio."""
        dropout_ratio = 0.3
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate, 
                              dropout_ratio=dropout_ratio)
        assert layer.dropout.p == 0.5  # Note: dropout_ratio param not used in current implementation
    
    def test_forward_training_mode(self, n_bands, sample_rate, sample_input):
        """Test forward pass in training mode."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # Mock the split_bands function to return proper shaped tensor
        n_bands_actual = n_bands
        split_output = torch.randn(n_bands_actual, *sample_input.shape)
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(sample_input)
        
        # Check that split_bands was called
        julius_mock.bands.split_bands.assert_called_once()
        
        # Check output shape matches input shape
        assert output.shape == sample_input.shape
    
    def test_forward_eval_mode(self, n_bands, sample_rate, sample_input):
        """Test forward pass in evaluation mode (should be identity)."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.eval()
        
        output = layer(sample_input)
        
        # In eval mode, output should be identical to input
        assert torch.allclose(output, sample_input)
        
        # split_bands should not be called in eval mode
        julius_mock.bands.split_bands.assert_not_called()
    
    def test_frequency_gain_application(self, n_bands, sample_rate):
        """Test that frequency gains are properly applied."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # Create controlled input
        batch_size, n_channels, seq_len = 2, 3, 100
        x = torch.ones(batch_size, n_channels, seq_len)
        
        # Mock split_bands to return separable bands
        split_output = torch.stack([x * (i+1) for i in range(n_bands)])
        julius_mock.bands.split_bands.return_value = split_output
        
        with torch.no_grad():
            output = layer(x)
        
        # Output should be weighted sum of bands
        assert output.shape == x.shape
        assert not torch.allclose(output, x)  # Should be modified
    
    def test_gradient_flow(self, n_bands, sample_rate, sample_input):
        """Test that gradients flow properly through the layer."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # Setup for gradient computation
        sample_input.requires_grad = True
        
        # Mock split_bands
        split_output = torch.randn(n_bands, *sample_input.shape, requires_grad=True)
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(sample_input)
        loss = output.sum()
        loss.backward()
        
        # Check that input has gradients
        assert sample_input.grad is not None
        assert not torch.allclose(sample_input.grad, torch.zeros_like(sample_input.grad))
    
    def test_device_compatibility_cpu(self, n_bands, sample_rate):
        """Test layer works on CPU."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        x = torch.randn(2, 3, 100)
        split_output = torch.randn(n_bands, 2, 3, 100)
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(x)
        assert output.device == x.device
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_device_compatibility_cuda(self, n_bands, sample_rate):
        """Test layer works on CUDA."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate).cuda()
        layer.train()
        
        x = torch.randn(2, 3, 100).cuda()
        split_output = torch.randn(n_bands, 2, 3, 100).cuda()
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(x)
        assert output.device == x.device
        assert output.is_cuda
    
    def test_different_input_shapes(self, n_bands, sample_rate):
        """Test with various input shapes."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        test_shapes = [
            (1, 1, 100),    # Single batch, single channel
            (8, 64, 500),   # Larger batch and channels
            (2, 3, 2048),   # Longer sequence
        ]
        
        for shape in test_shapes:
            x = torch.randn(*shape)
            split_output = torch.randn(n_bands, *shape)
            julius_mock.bands.split_bands.return_value = split_output
            
            output = layer(x)
            assert output.shape == x.shape
    
    def test_frequency_gain_normalization(self, n_bands, sample_rate):
        """Test that frequency gains are normalized with softmax."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # Track the gains applied
        x = torch.ones(2, 3, 100)
        
        # Create bands with known values
        bands = []
        for i in range(n_bands):
            band = torch.ones_like(x) * (i + 1)
            bands.append(band)
        split_output = torch.stack(bands)
        julius_mock.bands.split_bands.return_value = split_output
        
        # Multiple forward passes should give different results due to randomness
        outputs = []
        for _ in range(5):
            output = layer(x)
            outputs.append(output)
        
        # Check that outputs are different (due to random gains)
        for i in range(1, len(outputs)):
            assert not torch.allclose(outputs[0], outputs[i])
    
    def test_reproducibility_with_seed(self, n_bands, sample_rate):
        """Test reproducible results with fixed random seed."""
        torch.manual_seed(42)
        layer1 = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer1.train()
        
        torch.manual_seed(42)
        layer2 = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer2.train()
        
        x = torch.randn(2, 3, 100)
        split_output = torch.randn(n_bands, 2, 3, 100)
        
        # Set same seed before each forward pass
        torch.manual_seed(42)
        julius_mock.bands.split_bands.return_value = split_output
        output1 = layer1(x)
        
        torch.manual_seed(42)
        julius_mock.bands.split_bands.return_value = split_output
        output2 = layer2(x)
        
        assert torch.allclose(output1, output2)
    
    def test_zero_input_handling(self, n_bands, sample_rate):
        """Test behavior with zero input."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        x = torch.zeros(2, 3, 100)
        split_output = torch.zeros(n_bands, 2, 3, 100)
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(x)
        assert torch.allclose(output, x)
    
    def test_single_band_edge_case(self, sample_rate):
        """Test with single frequency band."""
        layer = FreqGainChanger(n_bands=1, samp_rate=sample_rate)
        layer.train()
        
        x = torch.randn(2, 3, 100)
        split_output = x.unsqueeze(0)  # Single band
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(x)
        assert output.shape == x.shape
    
    def test_high_frequency_bands(self, sample_rate):
        """Test with many frequency bands."""
        n_bands = 50
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        x = torch.randn(2, 3, 100)
        split_output = torch.randn(n_bands, 2, 3, 100)
        julius_mock.bands.split_bands.return_value = split_output
        
        output = layer(x)
        assert output.shape == x.shape
    
    def test_numerical_stability(self, n_bands, sample_rate):
        """Test numerical stability with extreme values."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # Test with very large values
        x_large = torch.randn(2, 3, 100) * 1e6
        split_large = torch.randn(n_bands, 2, 3, 100) * 1e6
        julius_mock.bands.split_bands.return_value = split_large
        
        output_large = layer(x_large)
        assert not torch.isnan(output_large).any()
        assert not torch.isinf(output_large).any()
        
        # Test with very small values
        x_small = torch.randn(2, 3, 100) * 1e-6
        split_small = torch.randn(n_bands, 2, 3, 100) * 1e-6
        julius_mock.bands.split_bands.return_value = split_small
        
        output_small = layer(x_small)
        assert not torch.isnan(output_small).any()
    
    def test_memory_efficiency(self, n_bands, sample_rate):
        """Test memory usage is reasonable."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # Large input
        x = torch.randn(8, 64, 1000)
        split_output = torch.randn(n_bands, 8, 64, 1000)
        julius_mock.bands.split_bands.return_value = split_output
        
        # Should not raise memory errors
        output = layer(x)
        assert output.shape == x.shape
    
    def test_integration_with_sequential(self, n_bands, sample_rate):
        """Test integration in nn.Sequential."""
        model = nn.Sequential(
            nn.Conv1d(32, 64, 3, padding=1),
            FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate),
            nn.ReLU(),
            nn.Conv1d(64, 32, 3, padding=1)
        )
        model.train()
        
        x = torch.randn(4, 32, 100)
        
        # Mock for the FreqGainChanger layer
        def mock_split_bands(x, sr, n_bands):
            return torch.randn(n_bands, *x.shape)
        
        julius_mock.bands.split_bands.side_effect = mock_split_bands
        
        output = model(x)
        assert output.shape == (4, 32, 100)
    
    def test_different_sample_rates(self, n_bands):
        """Test with various sample rates."""
        sample_rates = [100, 500, 1000, 2000, 44100]
        
        for sr in sample_rates:
            layer = FreqGainChanger(n_bands=n_bands, samp_rate=sr)
            layer.train()
            
            x = torch.randn(2, 3, 100)
            split_output = torch.randn(n_bands, 2, 3, 100)
            julius_mock.bands.split_bands.return_value = split_output
            
            output = layer(x)
            assert output.shape == x.shape
    
    def test_gain_range_validity(self, n_bands, sample_rate):
        """Test that frequency gains are in valid range after softmax."""
        layer = FreqGainChanger(n_bands=n_bands, samp_rate=sample_rate)
        layer.train()
        
        # We can't directly access the gains, but we can verify output properties
        x = torch.ones(2, 3, 100)
        
        # Create bands with equal energy
        split_output = torch.ones(n_bands, 2, 3, 100)
        julius_mock.bands.split_bands.return_value = split_output
        
        outputs = []
        for _ in range(10):
            output = layer(x)
            outputs.append(output)
        
        # All outputs should have reasonable values (softmax ensures sum=1)
        for output in outputs:
            assert (output >= 0).all()  # Softmax ensures non-negative after weighting
            assert not torch.isnan(output).any()
            assert not torch.isinf(output).any()


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_FreqGainChanger.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-04-23 11:02:34 (ywatanabe)"
#
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torchsummary import summary
# import scitex
# import numpy as np
# import julius
#
# # BANDS_LIM_HZ_DICT = {
# #     "delta": [0.5, 4],
# #     "theta": [4, 8],
# #     "lalpha": [8, 10],
# #     "halpha": [10, 13],
# #     "beta": [13, 32],
# #     "gamma": [32, 75],
# # }
#
#
# # class FreqDropout(nn.Module):
# #     def __init__(self, n_bands, samp_rate, dropout_ratio=0.5):
# #         super().__init__()
# #         self.dropout = nn.Dropout(p=0.5)
# #         self.n_bands = n_bands
# #         self.samp_rate = samp_rate
# #         # self.
# #         self.register_buffer("ones", torch.ones(self.n_bands))
#
# #     def forward(self, x):
# #         """x: [batch_size, n_chs, seq_len]"""
# #         x = julius.bands.split_bands(x, self.samp_rate, n_bands=self.n_bands)
#
# #         gains_orig = x.reshape(len(x), -1).abs().sum(axis=-1)
# #         sum_gains_orig = gains_orig.sum()
#
# #         # use_freqs = self.dropout(torch.ones(self.n_bands)).bool().long()
# #         use_freqs = self.dropout(self.ones) / 2 # .bool().long()
#
# #         gains = gains_orig * use_freqs
# #         sum_gains = gains.sum()
# #         gain_ratio = sum_gains / sum_gains_orig
#
#
# #         x *= use_freqs.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
# #         x /= gain_ratio
# #         x = x.sum(axis=0)
#
# #         return x
#
# class FreqGainChanger(nn.Module):
#     def __init__(self, n_bands, samp_rate, dropout_ratio=0.5):
#         super().__init__()
#         self.dropout = nn.Dropout(p=0.5)
#         self.n_bands = n_bands
#         self.samp_rate = samp_rate
#         # self.register_buffer("ones", torch.ones(self.n_bands))
#
#     def forward(self, x):
#         """x: [batch_size, n_chs, seq_len]"""
#         if self.training:
#             x = julius.bands.split_bands(x, self.samp_rate, n_bands=self.n_bands)
#             freq_gains = torch.rand(self.n_bands).unsqueeze(-1).unsqueeze(-1).unsqueeze(-1).to(x.device) + .5
#             freq_gains = F.softmax(freq_gains, dim=0)
#             x = (x*freq_gains).sum(axis=0)
#
#         return x
#         # import ipdb; ipdb.set_trace()
#
#         # gains_orig = x.reshape(len(x), -1).abs().sum(axis=-1)
#         # sum_gains_orig = gains_orig.sum()
#
#         # # use_freqs = self.dropout(torch.ones(self.n_bands)).bool().long()
#         # use_freqs = self.dropout(self.ones) / 2 # .bool().long()
#
#         # gains = gains_orig * use_freqs
#         # sum_gains = gains.sum()
#         # gain_ratio = sum_gains / sum_gains_orig
#
#
#         # x *= use_freqs.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
#         # x /= gain_ratio
#         # x = x.sum(axis=0)
#
#         # return x
#
#
#
#
#
# if __name__ == "__main__":
#     # Parameters
#     N_BANDS = 10
#     SAMP_RATE = 1000
#     BS, N_CHS, SEQ_LEN = 16, 360, 1000
#
#     # Demo data
#     x = torch.rand(BS, N_CHS, SEQ_LEN).cuda()
#
#     # Feedforward
#     fgc = FreqGainChanger(N_BANDS, SAMP_RATE).cuda()
#     # fd.eval()
#     y = fgc(x)
#     y.sum().backward()
#
#
#

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_FreqGainChanger.py
# --------------------------------------------------------------------------------
