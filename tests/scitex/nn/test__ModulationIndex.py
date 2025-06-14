#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 00:00:00 (ywatanabe)"
# File: test__ModulationIndex.py

"""Comprehensive test suite for Modulation Index computation neural network layer."""

import pytest
import torch
import torch.nn as nn
import numpy as np
import warnings
from unittest.mock import Mock, patch
import tempfile
import os


class TestModulationIndexInitialization:
    """Test ModulationIndex layer initialization."""
    
    def test_basic_initialization(self):
        """Test basic ModulationIndex initialization with default parameters."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        assert mi.n_bins == 18
        assert mi.fp16 is False
        assert mi.amp_prob is False
        assert hasattr(mi, 'pha_bin_cutoffs')
        
    def test_initialization_with_custom_bins(self):
        """Test initialization with custom number of phase bins."""
        from scitex.nn import ModulationIndex
        
        n_bins = 36
        mi = ModulationIndex(n_bins=n_bins)
        
        assert mi.n_bins == n_bins
        assert len(mi.pha_bin_cutoffs) == n_bins + 1
        assert mi.pha_bin_cutoffs[0] == -np.pi
        assert mi.pha_bin_cutoffs[-1] == np.pi
        
    def test_initialization_with_fp16(self):
        """Test initialization with half precision enabled."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(fp16=True)
        assert mi.fp16 is True
        
    def test_initialization_with_amp_prob(self):
        """Test initialization with amplitude probability output."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(amp_prob=True)
        assert mi.amp_prob is True
        
    def test_phase_bin_cutoffs_buffer(self):
        """Test phase bin cutoffs are registered as buffer."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=10)
        
        # Check it's a buffer (not parameter)
        assert 'pha_bin_cutoffs' in dict(mi.named_buffers())
        assert 'pha_bin_cutoffs' not in dict(mi.named_parameters())
        
    def test_phase_bin_centers_property(self):
        """Test phase bin centers calculation."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=18)
        centers = mi.pha_bin_centers
        
        assert len(centers) == 18
        assert centers[0] < 0  # First half negative
        assert centers[-1] > 0  # Second half positive
        assert np.isclose(centers[9], 0, atol=0.1)  # Middle near zero


class TestModulationIndexForward:
    """Test ModulationIndex forward pass computation."""
    
    def test_forward_basic(self):
        """Test basic forward pass with valid inputs."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Create test data
        batch_size, n_channels, n_freqs_pha, n_segments, seq_len = 2, 3, 5, 4, 100
        pha = torch.randn(batch_size, n_channels, n_freqs_pha, n_segments, seq_len)
        amp = torch.randn(batch_size, n_channels, n_freqs_pha, n_segments, seq_len)
        
        output = mi(pha, amp)
        
        assert output.shape == (batch_size, n_channels, n_freqs_pha, n_freqs_pha)
        assert not torch.isnan(output).any()
        
    def test_forward_with_different_freq_dimensions(self):
        """Test forward pass with different phase and amplitude frequency dimensions."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Different frequency dimensions
        batch_size, n_channels, n_segments, seq_len = 1, 2, 3, 50
        n_freqs_pha, n_freqs_amp = 4, 6
        
        pha = torch.randn(batch_size, n_channels, n_freqs_pha, n_segments, seq_len)
        amp = torch.randn(batch_size, n_channels, n_freqs_amp, n_segments, seq_len)
        
        output = mi(pha, amp)
        
        assert output.shape == (batch_size, n_channels, n_freqs_pha, n_freqs_amp)
        
    def test_forward_with_fp16(self):
        """Test forward pass with half precision."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(fp16=True)
        
        pha = torch.randn(1, 1, 2, 1, 100)
        amp = torch.randn(1, 1, 2, 1, 100)
        
        output = mi(pha, amp)
        
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
        
    def test_forward_returns_amp_prob(self):
        """Test forward pass returning amplitude probability distributions."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=20, amp_prob=True)
        
        pha = torch.randn(2, 2, 3, 2, 100)
        amp = torch.randn(2, 2, 3, 2, 100)
        
        output = mi(pha, amp)
        
        # Should have bins dimension
        assert output.shape[-1] == 20
        # Should be on CPU when amp_prob=True
        assert output.device.type == 'cpu'
        
    def test_forward_modulation_index_range(self):
        """Test modulation index output is in valid range [0, 1]."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        pha = torch.randn(1, 1, 1, 1, 1000)
        amp = torch.rand(1, 1, 1, 1, 1000) + 0.5  # Positive amplitudes
        
        output = mi(pha, amp)
        
        # MI should be between 0 and 1
        assert (output >= 0).all()
        assert (output <= 1).all()
        
    def test_forward_gradient_flow(self):
        """Test gradient flow through ModulationIndex layer."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        pha = torch.randn(1, 1, 2, 1, 100, requires_grad=True)
        amp = torch.randn(1, 1, 2, 1, 100, requires_grad=True)
        
        output = mi(pha, amp)
        loss = output.sum()
        loss.backward()
        
        assert pha.grad is not None
        assert amp.grad is not None
        assert not torch.isnan(pha.grad).any()
        assert not torch.isnan(amp.grad).any()


class TestPhaseToMasks:
    """Test phase binning functionality."""
    
    def test_phase_to_masks_basic(self):
        """Test basic phase to mask conversion."""
        from scitex.nn import ModulationIndex
        
        n_bins = 10
        phase_bin_cutoffs = torch.linspace(-np.pi, np.pi, n_bins + 1)
        
        # Create phase data
        pha = torch.tensor([[[-np.pi, 0, np.pi]]])  # Shape: (1, 1, 3)
        
        masks = ModulationIndex._phase_to_masks(pha, phase_bin_cutoffs)
        
        assert masks.shape == (1, 1, 3, n_bins)
        assert masks.dtype == torch.bool
        # Each phase value should be in exactly one bin
        assert (masks.sum(dim=-1) == 1).all()
        
    def test_phase_to_masks_edge_cases(self):
        """Test phase binning at bin edges."""
        from scitex.nn import ModulationIndex
        
        n_bins = 4
        phase_bin_cutoffs = torch.linspace(-np.pi, np.pi, n_bins + 1)
        
        # Test values at bin edges
        pha = phase_bin_cutoffs[:-1].unsqueeze(0).unsqueeze(0)
        
        masks = ModulationIndex._phase_to_masks(pha, phase_bin_cutoffs)
        
        assert masks.shape[-1] == n_bins
        assert (masks.sum(dim=-1) == 1).all()
        
    def test_phase_to_masks_out_of_range(self):
        """Test phase binning with out-of-range values."""
        from scitex.nn import ModulationIndex
        
        phase_bin_cutoffs = torch.linspace(-np.pi, np.pi, 10)
        
        # Values outside [-pi, pi]
        pha = torch.tensor([[[-4.0, 4.0]]])
        
        masks = ModulationIndex._phase_to_masks(pha, phase_bin_cutoffs)
        
        # Should be clamped to valid bin range
        assert (masks.sum(dim=-1) == 1).all()
        
    def test_phase_to_masks_large_input(self):
        """Test phase binning with large multidimensional input."""
        from scitex.nn import ModulationIndex
        
        phase_bin_cutoffs = torch.linspace(-np.pi, np.pi, 18 + 1)
        
        # Large input
        pha = torch.randn(4, 8, 10, 5, 1000)
        
        masks = ModulationIndex._phase_to_masks(pha, phase_bin_cutoffs)
        
        assert masks.shape == (4, 8, 10, 5, 1000, 18)
        assert masks.dtype == torch.bool


class TestModulationIndexCalculation:
    """Test modulation index calculation specifics."""
    
    def test_uniform_amplitude_distribution(self):
        """Test MI calculation with uniform amplitude distribution."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=10)
        
        # Create uniform phase distribution
        seq_len = 10000
        pha = torch.linspace(-np.pi, np.pi, seq_len).unsqueeze(0).unsqueeze(0).unsqueeze(0).unsqueeze(0)
        # Constant amplitude
        amp = torch.ones_like(pha)
        
        output = mi(pha, amp)
        
        # Uniform distribution should give MI close to 0
        assert output.item() < 0.1
        
    def test_concentrated_amplitude_distribution(self):
        """Test MI calculation with concentrated amplitude distribution."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=10)
        
        # Phase values
        pha = torch.zeros(1, 1, 1, 1, 1000)  # All at phase 0
        # High amplitude
        amp = torch.ones_like(pha) * 10
        
        output = mi(pha, amp)
        
        # Concentrated distribution should give higher MI
        assert output.item() > 0.5
        
    def test_nan_warning(self):
        """Test NaN warning is raised appropriately."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Create data that might produce NaN
        pha = torch.randn(1, 1, 1, 1, 10)
        amp = torch.zeros_like(pha)  # Zero amplitude might cause issues
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            output = mi(pha, amp)
            
            # Check if warning was raised
            if torch.isnan(output).any():
                assert any("NaN values detected" in str(warning.message) for warning in w)


class TestMultiChannelProcessing:
    """Test multi-channel and multi-segment processing."""
    
    def test_multi_channel_independence(self):
        """Test that channels are processed independently."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Create data with different patterns per channel
        batch_size, n_channels, n_freqs, n_segments, seq_len = 1, 3, 2, 1, 500
        
        pha = torch.zeros(batch_size, n_channels, n_freqs, n_segments, seq_len)
        amp = torch.ones_like(pha)
        
        # Make channel 1 different
        pha[:, 1, :, :, :] = torch.randn_like(pha[:, 1, :, :, :])
        
        output = mi(pha, amp)
        
        # Channel 0 and 2 should be similar, channel 1 different
        assert not torch.allclose(output[:, 0], output[:, 1])
        assert torch.allclose(output[:, 0], output[:, 2], atol=0.01)
        
    def test_multi_segment_averaging(self):
        """Test that MI is averaged across segments."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Single segment
        pha_single = torch.randn(1, 1, 1, 1, 1000)
        amp_single = torch.rand(1, 1, 1, 1, 1000) + 0.5
        
        # Multiple segments with same data repeated
        n_segments = 5
        pha_multi = pha_single.repeat(1, 1, 1, n_segments, 1)
        amp_multi = amp_single.repeat(1, 1, 1, n_segments, 1)
        
        output_single = mi(pha_single, amp_single)
        output_multi = mi(pha_multi, amp_multi)
        
        # Should be similar (averaged across segments)
        assert torch.allclose(output_single, output_multi, atol=0.1)


class TestMemoryEfficiency:
    """Test memory efficiency of ModulationIndex computation."""
    
    def test_large_batch_processing(self):
        """Test processing large batches efficiently."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Large batch
        batch_size = 32
        pha = torch.randn(batch_size, 4, 5, 2, 100)
        amp = torch.randn(batch_size, 4, 5, 2, 100)
        
        output = mi(pha, amp)
        
        assert output.shape[0] == batch_size
        assert not torch.isnan(output).any()
        
    def test_memory_consumption_with_broadcasting(self):
        """Test memory-efficient broadcasting in coupling computation."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=50)  # More bins
        
        # Moderate size that tests broadcasting
        pha = torch.randn(2, 2, 10, 2, 500)
        amp = torch.randn(2, 2, 10, 2, 500)
        
        # Should complete without memory error
        output = mi(pha, amp)
        
        assert output.shape == (2, 2, 10, 10)


class TestDeviceCompatibility:
    """Test ModulationIndex on different devices."""
    
    def test_cpu_computation(self):
        """Test computation on CPU."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        pha = torch.randn(1, 1, 2, 1, 100)
        amp = torch.randn(1, 1, 2, 1, 100)
        
        output = mi(pha, amp)
        
        assert output.device.type == 'cpu'
        
    def test_cuda_computation(self):
        """Test computation on CUDA if available."""
        from scitex.nn import ModulationIndex
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        mi = ModulationIndex().cuda()
        
        pha = torch.randn(2, 2, 3, 2, 200).cuda()
        amp = torch.randn(2, 2, 3, 2, 200).cuda()
        
        output = mi(pha, amp)
        
        assert output.is_cuda
        assert output.device == pha.device
        
    def test_device_consistency_with_amp_prob(self):
        """Test device handling when returning amplitude probabilities."""
        from scitex.nn import ModulationIndex
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        mi = ModulationIndex(amp_prob=True).cuda()
        
        pha = torch.randn(1, 1, 1, 1, 100).cuda()
        amp = torch.randn(1, 1, 1, 1, 100).cuda()
        
        output = mi(pha, amp)
        
        # Should be moved to CPU when amp_prob=True
        assert output.device.type == 'cpu'


class TestNumericalStability:
    """Test numerical stability of ModulationIndex."""
    
    def test_epsilon_handling(self):
        """Test epsilon prevents division by zero."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Create scenario with potential division by zero
        pha = torch.randn(1, 1, 1, 1, 100)
        amp = torch.zeros_like(pha)  # Zero amplitude
        
        output = mi(pha, amp)
        
        # Should handle gracefully without inf
        assert not torch.isinf(output).any()
        
    def test_log_stability(self):
        """Test logarithm computation stability."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Very small amplitudes
        pha = torch.randn(1, 1, 1, 1, 100)
        amp = torch.ones_like(pha) * 1e-10
        
        output = mi(pha, amp)
        
        assert not torch.isinf(output).any()
        assert torch.isfinite(output).all()
        
    def test_extreme_values(self):
        """Test handling of extreme input values."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex()
        
        # Mix of extreme values
        pha = torch.randn(1, 1, 2, 1, 100) * 10  # Large phase values
        amp = torch.randn(1, 1, 2, 1, 100).abs() * 1000  # Large amplitudes
        
        output = mi(pha, amp)
        
        assert torch.isfinite(output).all()


class TestIntegration:
    """Test ModulationIndex integration with other modules."""
    
    def test_in_sequential_model(self):
        """Test ModulationIndex in a sequential model."""
        from scitex.nn import ModulationIndex
        
        # Custom wrapper to handle 5D input requirement
        class MIWrapper(nn.Module):
            def __init__(self, n_bins=18):
                super().__init__()
                self.mi = ModulationIndex(n_bins=n_bins)
                
            def forward(self, x):
                # Assume x is (batch, channels, time)
                # Reshape to 5D for MI
                B, C, T = x.shape
                x_5d = x.view(B, C, 1, 1, T)
                pha = x_5d
                amp = x_5d.abs()  # Use absolute value as amplitude
                return self.mi(pha, amp)
        
        model = nn.Sequential(
            nn.Conv1d(1, 4, 3, padding=1),
            nn.ReLU(),
            MIWrapper(n_bins=10)
        )
        
        x = torch.randn(2, 1, 100)
        output = model(x)
        
        assert output.shape == (2, 4, 1, 1)
        
    def test_model_save_load(self):
        """Test saving and loading a model with ModulationIndex."""
        from scitex.nn import ModulationIndex
        
        mi = ModulationIndex(n_bins=24)
        
        with tempfile.NamedTemporaryFile(suffix='.pth', delete=False) as f:
            torch.save(mi.state_dict(), f.name)
            
            mi_loaded = ModulationIndex(n_bins=24)
            mi_loaded.load_state_dict(torch.load(f.name))
            
            # Test outputs match
            pha = torch.randn(1, 1, 2, 1, 100)
            amp = torch.randn(1, 1, 2, 1, 100)
            
            out1 = mi(pha, amp)
            out2 = mi_loaded(pha, amp)
            
            assert torch.allclose(out1, out2)
            
            os.unlink(f.name)


# Run tests if script is executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
