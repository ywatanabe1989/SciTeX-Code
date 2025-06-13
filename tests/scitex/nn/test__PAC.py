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
    pytest.main([__file__, "-v"])
