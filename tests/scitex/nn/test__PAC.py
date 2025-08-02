#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 00:00:00 (ywatanabe)"
# File: test__PAC.py

"""Comprehensive test suite for Phase-Amplitude Coupling (PAC) neural network layer."""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os


class TestPACInitialization:
    """Test PAC layer initialization with various configurations."""
    
    def test_basic_initialization(self):
        """Test basic PAC layer initialization with default parameters."""
        from scitex.nn import PAC
        
        seq_len = 1024
        fs = 512
        pac = PAC(seq_len, fs)
        
        assert pac.fp16 is False
        assert pac.n_perm is None
        assert pac.amp_prob is False
        assert pac.trainable is False
        
    def test_initialization_with_custom_frequency_bands(self):
        """Test PAC initialization with custom frequency band parameters."""
        from scitex.nn import PAC
        
        seq_len = 2048
        fs = 1000
        pac = PAC(
            seq_len, 
            fs,
            pha_start_hz=4,
            pha_end_hz=30,
            pha_n_bands=40,
            amp_start_hz=50,
            amp_end_hz=200,
            amp_n_bands=25
        )
        
        assert pac.BANDS_PHA.shape == (40, 2)
        assert pac.BANDS_AMP.shape == (25, 2)
        
    def test_initialization_with_fp16(self):
        """Test PAC initialization with half precision (fp16) enabled."""
        from scitex.nn import PAC
        
        pac = PAC(1024, 512, fp16=True)
        assert pac.fp16 is True
        
    def test_initialization_with_permutations(self):
        """Test PAC initialization with surrogate permutations enabled."""
        from scitex.nn import PAC
        
        pac = PAC(1024, 512, n_perm=100)
        assert pac.n_perm == 100
        
    def test_initialization_with_invalid_permutations(self):
        """Test PAC initialization fails with invalid permutation parameter."""
        from scitex.nn import PAC
        
        with pytest.raises(ValueError, match="n_perm should be None or an integer"):
            PAC(1024, 512, n_perm="invalid")
            
    def test_trainable_initialization(self):
        """Test PAC initialization with trainable bandpass filters."""
        from scitex.nn import PAC
        
        with patch('scitex.nn.DifferentiableBandPassFilter') as mock_filter:
            mock_instance = Mock()
            mock_instance.pha_mids = torch.tensor([10.0, 15.0])
            mock_instance.amp_mids = torch.tensor([100.0, 120.0])
            mock_filter.return_value = mock_instance
            
            pac = PAC(1024, 512, trainable=True)
            assert pac.trainable is True
            mock_filter.assert_called_once()
            
    def test_nyquist_frequency_capping(self):
        """Test amplitude frequency band capping based on Nyquist frequency."""
        from scitex.nn import PAC
        
        fs = 200  # Low sampling rate
        pac = PAC(1024, fs, amp_end_hz=200)  # Request beyond Nyquist
        
        # Should be capped below Nyquist
        expected_max = fs / 2 / 1.8 - 1  # Factor of 0.8 in code
        assert pac.BANDS_AMP[-1, 1] < fs / 2


class TestPACForward:
    """Test PAC layer forward pass functionality."""
    
    def test_forward_3d_input(self):
        """Test forward pass with 3D input (batch, channels, time)."""
        from scitex.nn import PAC
        
        batch_size, n_chs, seq_len = 2, 4, 1024
        fs = 512
        pac = PAC(seq_len, fs)
        
        x = torch.randn(batch_size, n_chs, seq_len)
        output = pac(x)
        
        # Output shape: (batch, channels, n_pha_bands, n_amp_bands)
        assert output.ndim == 4
        assert output.shape[0] == batch_size
        assert output.shape[1] == n_chs
        
    def test_forward_4d_input(self):
        """Test forward pass with 4D input (batch, channels, segments, time)."""
        from scitex.nn import PAC
        
        batch_size, n_chs, n_segments, seq_len = 2, 3, 5, 1024
        fs = 512
        pac = PAC(seq_len, fs)
        
        x = torch.randn(batch_size, n_chs, n_segments, seq_len)
        output = pac(x)
        
        assert output.ndim == 4
        assert output.shape[0] == batch_size
        assert output.shape[1] == n_chs
        
    def test_forward_with_cuda(self):
        """Test forward pass on CUDA device if available."""
        from scitex.nn import PAC
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        pac = PAC(1024, 512).cuda()
        x = torch.randn(2, 4, 1024).cuda()
        output = pac(x)
        
        assert output.is_cuda
        assert output.device == x.device
        
    def test_forward_with_amp_prob(self):
        """Test forward pass returning amplitude probability distributions."""
        from scitex.nn import PAC
        
        pac = PAC(1024, 512, amp_prob=True)
        x = torch.randn(2, 4, 1024)
        output = pac(x)
        
        # Should return probability distributions
        assert output.shape[-1] == 18  # Default n_bins
        
    def test_forward_gradient_flow(self):
        """Test gradient flow through PAC layer in trainable mode."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256, trainable=True)
        x = torch.randn(1, 2, 512, requires_grad=True)
        
        output = pac(x)
        loss = output.sum()
        loss.backward()
        
        assert x.grad is not None
        assert not torch.isnan(x.grad).any()


class TestPACSurrogates:
    """Test PAC surrogate generation and z-score normalization."""
    
    def test_generate_surrogates_basic(self):
        """Test basic surrogate PAC value generation."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256, n_perm=10)
        
        # Create mock phase and amplitude data
        pha = torch.randn(1, 2, 5, 1, 400)  # After edge removal
        amp = torch.randn(1, 2, 5, 1, 400)
        
        surrogates = pac.generate_surrogates(pha, amp)
        
        # Should have n_perm dimension
        assert surrogates.shape[2] == 10
        
    def test_z_score_normalization(self):
        """Test z-score normalization using surrogate distributions."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256, n_perm=50)
        
        # Mock data
        pha = torch.randn(1, 1, 5, 1, 400)
        amp = torch.randn(1, 1, 5, 1, 400)
        observed = torch.randn(1, 1, 5, 5)
        
        z_scores = pac.to_z_using_surrogate(pha, amp, observed)
        
        assert z_scores.shape == observed.shape
        assert not torch.isnan(z_scores).any()
        
    def test_surrogate_batch_processing(self):
        """Test surrogate generation with batch processing."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256, n_perm=20)
        
        # Larger batch size
        pha = torch.randn(4, 2, 5, 2, 400)
        amp = torch.randn(4, 2, 5, 2, 400)
        
        surrogates = pac.generate_surrogates(pha, amp, bs=2)
        
        assert surrogates.shape[0] == 4
        assert surrogates.shape[2] == 20


class TestPACBandCalculations:
    """Test frequency band calculation methods."""
    
    def test_calc_bands_pha_default(self):
        """Test phase frequency band calculation with default parameters."""
        from scitex.nn import PAC
        
        bands = PAC.calc_bands_pha()
        
        assert bands.shape == (100, 2)  # Default 100 bands
        assert bands[:, 0].min() >= 0  # Lower bounds positive
        assert (bands[:, 1] > bands[:, 0]).all()  # Upper > lower
        
    def test_calc_bands_pha_custom(self):
        """Test phase frequency band calculation with custom parameters."""
        from scitex.nn import PAC
        
        bands = PAC.calc_bands_pha(start_hz=5, end_hz=40, n_bands=20)
        
        assert bands.shape == (20, 2)
        assert bands[0, 0] >= 5 * 0.75  # 25% bandwidth
        assert bands[-1, 1] <= 40 * 1.25
        
    def test_calc_bands_amp_default(self):
        """Test amplitude frequency band calculation with default parameters."""
        from scitex.nn import PAC
        
        bands = PAC.calc_bands_amp()
        
        assert bands.shape == (100, 2)
        assert bands[:, 0].min() >= 0
        assert (bands[:, 1] > bands[:, 0]).all()
        
    def test_calc_bands_amp_custom(self):
        """Test amplitude frequency band calculation with custom parameters."""
        from scitex.nn import PAC
        
        bands = PAC.calc_bands_amp(start_hz=40, end_hz=200, n_bands=30)
        
        assert bands.shape == (30, 2)
        assert bands[0, 0] >= 40 * 0.875  # 12.5% bandwidth
        assert bands[-1, 1] <= 200 * 1.125


class TestPACInputHandling:
    """Test input validation and reshaping."""
    
    def test_ensure_4d_input_from_3d(self):
        """Test conversion of 3D input to 4D."""
        from scitex.nn import PAC
        
        x_3d = torch.randn(2, 4, 512)
        x_4d = PAC._ensure_4d_input(x_3d)
        
        assert x_4d.shape == (2, 4, 1, 512)
        
    def test_ensure_4d_input_already_4d(self):
        """Test 4D input passes through unchanged."""
        from scitex.nn import PAC
        
        x_4d = torch.randn(2, 4, 3, 512)
        output = PAC._ensure_4d_input(x_4d)
        
        assert output.shape == x_4d.shape
        assert output is x_4d
        
    def test_ensure_4d_input_invalid_shape(self):
        """Test invalid input shapes raise errors."""
        from scitex.nn import PAC
        
        # 2D input
        with pytest.raises(ValueError, match="Input tensor must be 4D"):
            PAC._ensure_4d_input(torch.randn(10, 512))
            
        # 5D input  
        with pytest.raises(ValueError, match="Input tensor must be 4D"):
            PAC._ensure_4d_input(torch.randn(2, 4, 3, 5, 512))


class TestPACEdgeCases:
    """Test edge cases and numerical stability."""
    
    def test_very_short_sequence(self):
        """Test PAC with very short sequence length."""
        from scitex.nn import PAC
        
        # Minimum reasonable length
        pac = PAC(128, 64)
        x = torch.randn(1, 1, 128)
        
        output = pac(x)
        assert not torch.isnan(output).any()
        
    def test_single_channel_single_batch(self):
        """Test PAC with minimal input dimensions."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256)
        x = torch.randn(1, 1, 512)
        
        output = pac(x)
        assert output.shape[0] == 1
        assert output.shape[1] == 1
        
    def test_large_batch_processing(self):
        """Test PAC with large batch size for memory efficiency."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256)
        x = torch.randn(32, 8, 512)
        
        output = pac(x)
        assert output.shape[0] == 32
        assert output.shape[1] == 8
        
    def test_numerical_stability_with_fp16(self):
        """Test numerical stability with half precision."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256, fp16=True)
        x = torch.randn(2, 4, 512)
        
        output = pac(x)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()


class TestPACIntegration:
    """Test PAC integration with PyTorch models."""
    
    def test_integration_in_sequential_model(self):
        """Test PAC layer in a Sequential model."""
        from scitex.nn import PAC
        
        model = nn.Sequential(
            nn.Conv1d(1, 8, 3, padding=1),
            nn.ReLU(),
            PAC(512, 256),
        )
        
        x = torch.randn(2, 1, 512)
        # Need to reshape conv output for PAC
        conv_out = model[0](x)
        conv_out = model[1](conv_out)
        pac_out = model[2](conv_out.transpose(1, 2).unsqueeze(1))
        
        assert pac_out is not None
        
    def test_model_save_load(self):
        """Test saving and loading a model containing PAC layer."""
        from scitex.nn import PAC
        
        pac = PAC(512, 256)
        
        with tempfile.NamedTemporaryFile(suffix='.pth') as f:
            torch.save(pac.state_dict(), f.name)
            
            pac_loaded = PAC(512, 256)
            pac_loaded.load_state_dict(torch.load(f.name))
            
            # Test forward pass
            x = torch.randn(1, 2, 512)
            out1 = pac(x)
            out2 = pac_loaded(x)
            
            assert torch.allclose(out1, out2)
            
    def test_multi_gpu_data_parallel(self):
        """Test PAC with DataParallel for multi-GPU training."""
        from scitex.nn import PAC
        
        if torch.cuda.device_count() < 2:
            pytest.skip("Multi-GPU test requires at least 2 GPUs")
            
        pac = PAC(512, 256)
        pac = nn.DataParallel(pac)
        pac = pac.cuda()
        
        x = torch.randn(4, 8, 512).cuda()
        output = pac(x)
        
        assert output.shape[0] == 4


class TestPACFrequencyAnalysis:
    """Test frequency-specific PAC computations."""
    
    def test_specific_frequency_coupling(self):
        """Test PAC computation for specific frequency combinations."""
        from scitex.nn import PAC
        
        # Theta-gamma coupling
        pac = PAC(
            1024, 512,
            pha_start_hz=4, pha_end_hz=8,  # Theta
            amp_start_hz=30, amp_end_hz=100,  # Gamma
            pha_n_bands=2,
            amp_n_bands=5
        )
        
        x = torch.randn(1, 1, 1024)
        output = pac(x)
        
        assert output.shape[2] == 2  # pha bands
        assert output.shape[3] == 5  # amp bands
        
    def test_cross_frequency_resolution(self):
        """Test PAC with different frequency resolutions."""
        from scitex.nn import PAC
        
        # High resolution
        pac_high = PAC(2048, 1024, pha_n_bands=100, amp_n_bands=100)
        
        # Low resolution  
        pac_low = PAC(2048, 1024, pha_n_bands=10, amp_n_bands=10)
        
        x = torch.randn(1, 1, 2048)
        
        out_high = pac_high(x)
        out_low = pac_low(x)
        
        assert out_high.shape[2] == 100
        assert out_low.shape[2] == 10


class TestPACMemoryEfficiency:
    """Test memory efficiency and optimization."""
    
    def test_memory_efficient_surrogate_generation(self):
        """Test memory-efficient surrogate generation with batching."""
        from scitex.nn import PAC
        
        pac = PAC(1024, 512, n_perm=100)
        
        # Large input that would require batched processing
        pha = torch.randn(8, 4, 10, 2, 800)
        amp = torch.randn(8, 4, 10, 2, 800)
        
        # Should process in batches without memory error
        surrogates = pac.generate_surrogates(pha, amp, bs=2)
        
        assert surrogates.shape[2] == 100
        
    def test_gpu_memory_cleanup(self):
        """Test GPU memory cleanup after surrogate generation."""
        from scitex.nn import PAC
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        pac = PAC(512, 256, n_perm=50).cuda()
        
        initial_memory = torch.cuda.memory_allocated()
        
        pha = torch.randn(4, 2, 5, 1, 400).cuda()
        amp = torch.randn(4, 2, 5, 1, 400).cuda()
        
        surrogates = pac.generate_surrogates(pha, amp)
        
        # Memory should be released after generation
        torch.cuda.synchronize()
        final_memory = torch.cuda.memory_allocated()
        
        # Some memory increase is expected but should be reasonable
        assert final_memory - initial_memory < 100 * 1024 * 1024  # 100MB


# Run tests if script is executed directly

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_PAC.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-26 10:33:30 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/nn/_PAC.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_PAC.py"
# 
# # Imports
# import sys
# import warnings
# 
# import matplotlib.pyplot as plt
# import scitex
# import torch
# import torch.nn as nn
# 
# 
# # Functions
# class PAC(nn.Module):
#     def __init__(
#         self,
#         seq_len,
#         fs,
#         pha_start_hz=2,
#         pha_end_hz=20,
#         pha_n_bands=50,
#         amp_start_hz=60,
#         amp_end_hz=160,
#         amp_n_bands=30,
#         n_perm=None,
#         trainable=False,
#         in_place=True,
#         fp16=False,
#         amp_prob=False,
#     ):
#         super().__init__()
# 
#         self.fp16 = fp16
#         self.n_perm = n_perm
#         self.amp_prob = amp_prob
#         self.trainable = trainable
# 
#         if n_perm is not None:
#             if not isinstance(n_perm, int):
#                 raise ValueError("n_perm should be None or an integer.")
# 
#         # caps amp_end_hz
#         factor = 0.8
#         amp_end_hz = int(min(fs / 2 / (1 + factor) - 1, amp_end_hz))
# 
#         self.bandpass = self.init_bandpass(
#             seq_len,
#             fs,
#             pha_start_hz=pha_start_hz,
#             pha_end_hz=pha_end_hz,
#             pha_n_bands=pha_n_bands,
#             amp_start_hz=amp_start_hz,
#             amp_end_hz=amp_end_hz,
#             amp_n_bands=amp_n_bands,
#             fp16=fp16,
#             trainable=trainable,
#         )
# 
#         self.hilbert = scitex.nn.Hilbert(seq_len, dim=-1, fp16=fp16)
# 
#         self.Modulation_index = scitex.nn.ModulationIndex(
#             n_bins=18,
#             fp16=fp16,
#             amp_prob=amp_prob,
#         )
# 
#         # Data Handlers
#         self.dh_pha = scitex.gen.DimHandler()
#         self.dh_amp = scitex.gen.DimHandler()
# 
#     def forward(self, x):
#         """x.shape: (batch_size, n_chs, seq_len) or (batch_size, n_chs, n_segments, seq_len)"""
# 
#         with torch.set_grad_enabled(bool(self.trainable)):
#             x = self._ensure_4d_input(x)
#             # (batch_size, n_chs, n_segments, seq_len)
# 
#             batch_size, n_chs, n_segments, seq_len = x.shape
# 
#             x = x.reshape(batch_size * n_chs, n_segments, seq_len)
#             # (batch_size * n_chs, n_segments, seq_len)
# 
#             x = self.bandpass(x, edge_len=0)
#             # (batch_size*n_chs, n_segments, n_pha_bands + n_amp_bands, seq_len)
# 
#             x = self.hilbert(x)
#             # (batch_size*n_chs, n_segments, n_pha_bands + n_amp_bands, seq_len, pha + amp)
# 
#             x = x.reshape(batch_size, n_chs, *x.shape[1:])
#             # (batch_size, n_chs, n_segments, n_pha_bands + n_amp_bands, seq_len, pha + amp)
# 
#             x = x.transpose(2, 3)
#             # (batch_size, n_chs, n_pha_bands + n_amp_bands, n_segments, pha + amp)
# 
#             if self.fp16:
#                 x = x.half()
# 
#             pha = x[:, :, : len(self.PHA_MIDS_HZ), :, :, 0]
#             # (batch_size, n_chs, n_freqs_pha, n_segments, sequence_length)
# 
#             amp = x[:, :, -len(self.AMP_MIDS_HZ) :, :, :, 1]
#             # (batch_size, n_chs, n_freqs_amp, n_segments, sequence_length)()
# 
#             edge_len = int(pha.shape[-1] // 8)
# 
#             pha = pha[..., edge_len:-edge_len].half()
#             amp = amp[..., edge_len:-edge_len].half()
# 
#             pac_or_amp_prob = self.Modulation_index(pha, amp)  # .squeeze()
#             # print(pac_or_amp_prob.shape)
#             # pac_or_amp_prob = pac_or_amp_prob.squeeze()
# 
#             if self.n_perm is None:
#                 return pac_or_amp_prob
#             else:
#                 return self.to_z_using_surrogate(pha, amp, pac_or_amp_prob)
# 
#     def to_z_using_surrogate(self, pha, amp, observed):
#         surrogates = self.generate_surrogates(pha, amp)
#         mm = surrogates.mean(dim=2).to(observed.device)
#         ss = surrogates.std(dim=2).to(observed.device)
#         return (observed - mm) / (ss + 1e-5)
# 
#         # if self.amp_prob:
#         #     amp_prob = self.Modulation_index(pha, amp).squeeze()
#         #     amp_prob.shape  # torch.Size([2, 8, 50, 50, 3, 18])
#         #     pac_surrogates = self.generate_surrogates(pha, amp)
#         #     # torch.Size([2, 8, 3, 50, 50, 3, 18])
#         #     __import__("ipdb").set_trace()
#         #     return amp_prob
# 
#         # elif not self.amp_prob:
#         #     pac = self.Modulation_index(pha, amp).squeeze() # torch.Size([2, 8, 50, 50])
# 
#         # if self.n_perm is not None:
#         #     pac_surrogates = self.generate_surrogates(pha, amp)
#         #     # torch.Size([2, 8, 3, 50, 50]) # self.amp_prob = False
#         #     __import__("ipdb").set_trace()
#         #     mm = pac_surrogates.mean(dim=2).to(pac.device)
#         #     ss = pac_surrogates.std(dim=2).to(pac.device)
#         #     pac_z = (pac - mm) / (ss + 1e-5)
#         #     return pac_z
# 
#         # return pac
# 
#     def generate_surrogates(self, pha, amp, bs=1):
#         # Shape of pha: [batch_size, n_chs, n_freqs_pha, n_segments, sequence_length]
#         batch_size, n_chs, n_freqs_pha, n_segments, seq_len = pha.shape
#         _, _, n_freqs_amp, _, _ = amp.shape
# 
#         # cut and shuffle
#         cut_points = torch.randint(seq_len, (self.n_perm,), device=pha.device)
#         ranges = torch.arange(seq_len, device=pha.device)
#         indices = cut_points.unsqueeze(0) - ranges.unsqueeze(1)
# 
#         pha = pha[..., indices]
#         amp = amp.unsqueeze(-1).expand(-1, -1, -1, -1, -1, self.n_perm)
# 
#         pha = self.dh_pha.fit(pha, keepdims=[2, 3, 4])
#         amp = self.dh_amp.fit(amp, keepdims=[2, 3, 4])
# 
#         if self.fp16:
#             pha = pha.half()
#             amp = amp.half()
# 
#         # print("\nCalculating surrogate PAC values...")
# 
#         surrogate_pacs = []
#         n_batches = (len(pha) + bs - 1) // bs
#         device = "cuda"
#         with torch.no_grad():
#             # ########################################
#             # # fixme
#             # pha = pha.to(device)
#             # amp = amp.to(device)
#             # ########################################
# 
#             for i_batch in range(n_batches):
#                 start = i_batch * bs
#                 end = min((i_batch + 1) * bs, pha.shape[0])
# 
#                 _pha = pha[start:end].unsqueeze(1).to(device)  # n_chs = 1
#                 _amp = amp[start:end].unsqueeze(1).to(device)  # n_chs = 1
# 
#                 _surrogate_pacs = self.Modulation_index(_pha, _amp).cpu()
#                 surrogate_pacs.append(_surrogate_pacs)
# 
#                 # # Optionally clear cache if memory is an issue
#                 # torch.cuda.empty_cache()
# 
#         torch.cuda.empty_cache()
#         surrogate_pacs = torch.vstack(surrogate_pacs).squeeze()
#         surrogate_pacs = self.dh_pha.unfit(surrogate_pacs)
# 
#         return surrogate_pacs
# 
#     def init_bandpass(
#         self,
#         seq_len,
#         fs,
#         pha_start_hz=2,
#         pha_end_hz=20,
#         pha_n_bands=50,
#         amp_start_hz=60,
#         amp_end_hz=160,
#         amp_n_bands=30,
#         trainable=False,
#         fp16=False,
#     ):
# 
#         # A static, gen purpose BandPassFilter
#         if not trainable:
#             # First, bands definitions for phase and amplitude are declared
#             self.BANDS_PHA = self.calc_bands_pha(
#                 start_hz=pha_start_hz,
#                 end_hz=pha_end_hz,
#                 n_bands=pha_n_bands,
#             )
#             self.BANDS_AMP = self.calc_bands_amp(
#                 start_hz=amp_start_hz,
#                 end_hz=amp_end_hz,
#                 n_bands=amp_n_bands,
#             )
#             bands_all = torch.vstack([self.BANDS_PHA, self.BANDS_AMP])
# 
#             # Instanciation of the static bandpass filter module
#             self.bandpass = scitex.nn.BandPassFilter(
#                 bands_all,
#                 fs,
#                 seq_len,
#                 fp16=fp16,
#             )
#             self.PHA_MIDS_HZ = self.BANDS_PHA.mean(-1)
#             self.AMP_MIDS_HZ = self.BANDS_AMP.mean(-1)
# 
#         # A trainable BandPassFilter specifically for PAC calculation. Bands will be optimized.
#         elif trainable:
#             self.bandpass = scitex.nn.DifferentiableBandPassFilter(
#                 seq_len,
#                 fs,
#                 fp16=fp16,
#                 pha_low_hz=pha_start_hz,
#                 pha_high_hz=pha_end_hz,
#                 pha_n_bands=pha_n_bands,
#                 amp_low_hz=amp_start_hz,
#                 amp_high_hz=amp_end_hz,
#                 amp_n_bands=amp_n_bands,
#             )
#             self.PHA_MIDS_HZ = self.bandpass.pha_mids
#             self.AMP_MIDS_HZ = self.bandpass.amp_mids
# 
#         return self.bandpass
# 
#     @staticmethod
#     def calc_bands_pha(start_hz=2, end_hz=20, n_bands=100):
#         start_hz = start_hz if start_hz is not None else 2
#         end_hz = end_hz if end_hz is not None else 20
#         mid_hz = torch.linspace(start_hz, end_hz, n_bands)
#         return torch.cat(
#             (
#                 mid_hz.unsqueeze(1) - mid_hz.unsqueeze(1) / 4.0,
#                 mid_hz.unsqueeze(1) + mid_hz.unsqueeze(1) / 4.0,
#             ),
#             dim=1,
#         )
# 
#     @staticmethod
#     def calc_bands_amp(start_hz=30, end_hz=160, n_bands=100):
#         start_hz = start_hz if start_hz is not None else 30
#         end_hz = end_hz if end_hz is not None else 160
#         mid_hz = torch.linspace(start_hz, end_hz, n_bands)
#         return torch.cat(
#             (
#                 mid_hz.unsqueeze(1) - mid_hz.unsqueeze(1) / 8.0,
#                 mid_hz.unsqueeze(1) + mid_hz.unsqueeze(1) / 8.0,
#             ),
#             dim=1,
#         )
# 
#     @staticmethod
#     def _ensure_4d_input(x):
#         if x.ndim != 4:
#             message = f"Input tensor must be 4D with the shape (batch_size, n_chs, n_segments, seq_len). Received shape: {x.shape}"
# 
#         if x.ndim == 3:
#             # warnings.warn(
#             #     "'n_segments' was determined to be 1, assuming your input is (batch_size, n_chs, seq_len).",
#             #     UserWarning,
#             # )
#             x = x.unsqueeze(-2)
# 
#         if x.ndim != 4:
#             raise ValueError(message)
# 
#         return x
# 
# 
# if __name__ == "__main__":
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     ts = scitex.gen.TimeStamper()
# 
#     # Parameters
#     FS = 512
#     T_SEC = 8
#     PLOT = False
#     fp16 = True
#     trainable = False
#     n_perm = 3
#     in_place = True
#     amp_prob = True
# 
#     # Demo Signal
#     xx, tt, fs = scitex.dsp.demo_sig(
#         batch_size=2,
#         n_chs=8,
#         n_segments=3,
#         fs=FS,
#         t_sec=T_SEC,
#         sig_type="tensorpac",
#         # sig_type="pac",
#     )
#     xx = torch.tensor(xx).cuda()
#     xx.requires_grad = False
#     # (2, 8, 2, 4096)
# 
#     # PAC object initialization
#     ts("PAC initialization starts")
#     m = PAC(
#         xx.shape[-1],
#         fs,
#         pha_start_hz=2,
#         pha_end_hz=20,
#         pha_n_bands=50,
#         amp_start_hz=60,
#         amp_end_hz=160,
#         amp_n_bands=50,
#         fp16=fp16,
#         trainable=trainable,
#         n_perm=n_perm,
#         in_place=in_place,
#         amp_prob=amp_prob,
#     ).cuda()
#     ts("PAC initialization ends")
# 
#     # PAC calculation
#     ts("PAC calculation starts")
#     pac = m(xx)
#     ts("PAC calculation ends")
# 
#     """
#     amp_prob = m(xx)
#     amp_prob = amp_prob.reshape(-1, amp_prob.shape[-1])
#     xx = m.Modulation_index.pha_bin_centers
#     plt.bar(xx, amp_prob[0])
#     """
# 
#     scitex.gen.print_block(f"PAC calculation time: {ts.delta(-1,-2):.3f} sec", c="yellow")
#     # 0.17 sec
#     scitex.gen.print_block(
#         f"x.shape: {xx.shape}"
#         f"\nfp16: {fp16}"
#         f"\ntrainable: {trainable}"
#         f"\nn_perm: {n_perm}"
#         f"\nin_place: {in_place}"
#     )
# 
#     # # Plots
#     # if PLOT:
#     #     pac = pac.detach().cpu().numpy()
#     #     fig, ax = scitex.plt.subplots()
#     #     ax.imshow2d(pac[0, 0], cbar_label="PAC value [zscore]")
#     #     ax.set_ticks(
#     #         x_vals=m.PHA_MIDS_HZ,
#     #         x_ticks=np.linspace(m.PHA_MIDS_HZ[0], m.PHA_MIDS_HZ[-1], 4),
#     #         y_vals=m.AMP_MIDS_HZ,
#     #         y_ticks=np.linspace(m.AMP_MIDS_HZ[0], m.AMP_MIDS_HZ[-1], 4),
#     #     )
#     #     ax.set_xyt(
#     #         "Frequency for phase [Hz]",
#     #         "Amplitude for phase [Hz]",
#     #         "PAC values",
#     #     )
#     #     plt.show()
# 
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/entrance/scitex/dsp/nn/_PAC.py
# """
# 
# # # close
# # fig, axes = scitex.plt.subplots(ncols=2)
# # axes[0].imshow2d(pac_scitex[i_batch, i_ch])
# # axes[1].imshow2d(pac_tp)
# # scitex.io.save(fig, CONFIG["SDIR"] + "pac.png")
# # import numpy as np
# # np.corrcoef(pac_scitex[i_batch, i_ch], pac_tp)[0, 1]
# # import matplotlib
# 
# # plt.close("all")
# # matplotlib.use("TkAgg")
# # plt.scatter(pac_scitex[i_batch, i_ch].reshape(-1), pac_tp.reshape(-1))
# # plt.show()
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_PAC.py
# --------------------------------------------------------------------------------
