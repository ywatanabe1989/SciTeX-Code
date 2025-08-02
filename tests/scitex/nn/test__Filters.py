#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 00:00:00 (ywatanabe)"
# File: test__Filters.py

"""Comprehensive test suite for neural network filter layers."""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestBaseFilter1D:
    """Test abstract base filter class functionality."""
    
    def test_base_filter_initialization(self):
        """Test BaseFilter1D initialization."""
        from scitex.nn import BaseFilter1D
        
        # Create concrete implementation for testing
        class ConcreteFilter(BaseFilter1D):
            def init_kernels(self):
                return torch.randn(5, 64)
        
        filter_layer = ConcreteFilter(fp16=False, in_place=False)
        
        assert filter_layer.fp16 is False
        assert filter_layer.in_place is False
        
    def test_forward_without_kernels_raises_error(self):
        """Test forward pass fails without initialized kernels."""
        from scitex.nn import BaseFilter1D
        
        class ConcreteFilter(BaseFilter1D):
            def init_kernels(self):
                pass
        
        filter_layer = ConcreteFilter()
        filter_layer.kernels = None  # Explicitly set to None
        
        x = torch.randn(2, 4, 100)
        
        with pytest.raises(ValueError, match="Filter kernels has not been initialized"):
            filter_layer(x)
            
    def test_flip_extend(self):
        """Test signal extension by flipping edges."""
        from scitex.nn import BaseFilter1D
        
        x = torch.tensor([[[1, 2, 3, 4, 5]]])
        extended = BaseFilter1D.flip_extend(x, 2)
        
        # Should flip and extend: [2,1] + [1,2,3,4,5] + [5,4]
        expected = torch.tensor([[[2, 1, 1, 2, 3, 4, 5, 5, 4]]])
        assert torch.allclose(extended, expected)
        
    def test_batch_conv(self):
        """Test batched convolution operation."""
        from scitex.nn import BaseFilter1D
        
        batch_size, n_chs, seq_len = 2, 3, 10
        n_kernels, kernel_len = 4, 3
        
        x = torch.randn(batch_size, n_chs, seq_len)
        kernels = torch.randn(n_kernels, kernel_len)
        
        output = BaseFilter1D.batch_conv(x, kernels, padding=1)
        
        assert output.shape == (batch_size, n_chs, n_kernels, seq_len)
        
    def test_remove_edges(self):
        """Test edge removal from filtered signals."""
        from scitex.nn import BaseFilter1D
        
        x = torch.randn(2, 3, 100)
        
        # Test fixed edge length
        trimmed = BaseFilter1D.remove_edges(x, edge_len=10)
        assert trimmed.shape[-1] == 80
        
        # Test auto edge length (1/8 of signal)
        trimmed_auto = BaseFilter1D.remove_edges(x, edge_len="auto")
        assert trimmed_auto.shape[-1] == 100 - 2 * (100 // 8)
        
        # Test zero edge length
        no_trim = BaseFilter1D.remove_edges(x, edge_len=0)
        assert no_trim.shape == x.shape


class TestBandPassFilter:
    """Test BandPassFilter implementation."""
    
    def test_bandpass_initialization(self):
        """Test BandPassFilter initialization with valid parameters."""
        from scitex.nn import BandPassFilter
        
        bands = torch.tensor([[10, 20], [20, 40], [40, 80]])
        fs = 256
        seq_len = 1024
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(64)
            
            bp_filter = BandPassFilter(bands, fs, seq_len)
            
            assert hasattr(bp_filter, 'kernels')
            assert bp_filter.kernels.shape[0] == 3  # Number of bands
            assert mock_design.call_count == 3
            
    def test_bandpass_with_numpy_bands(self):
        """Test BandPassFilter accepts numpy array bands."""
        from scitex.nn import BandPassFilter
        
        bands = np.array([[10, 20], [20, 40]])
        fs = 256
        seq_len = 512
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            bp_filter = BandPassFilter(bands, fs, seq_len)
            assert bp_filter.kernels is not None
            
    def test_bandpass_nyquist_clipping(self):
        """Test frequency bands are clipped to Nyquist limit."""
        from scitex.nn import BandPassFilter
        
        fs = 100
        nyquist = fs / 2  # 50 Hz
        bands = torch.tensor([[10, 60], [30, 70]])  # Above Nyquist
        seq_len = 256
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            bp_filter = BandPassFilter(bands, fs, seq_len)
            
            # Check design_filter was called with clipped frequencies
            calls = mock_design.call_args_list
            for call in calls:
                _, kwargs = call
                assert kwargs['high_hz'] < nyquist
                
    def test_bandpass_forward_pass(self):
        """Test BandPassFilter forward pass."""
        from scitex.nn import BandPassFilter
        
        bands = torch.tensor([[5, 15], [15, 30]])
        fs = 128
        seq_len = 512
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            # Return different sized filters to simulate real behavior
            mock_design.return_value = np.random.randn(64)
            
            bp_filter = BandPassFilter(bands, fs, seq_len)
            bp_filter.kernels = torch.randn(2, 64)  # Mock kernels
            
            x = torch.randn(2, 3, seq_len)
            output = bp_filter(x)
            
            # Output shape: (batch, channels, n_bands, time)
            assert output.shape == (2, 3, 2, seq_len)
            
    def test_bandpass_with_fp16(self):
        """Test BandPassFilter with half precision."""
        from scitex.nn import BandPassFilter
        
        bands = torch.tensor([[10, 20]])
        fs = 256
        seq_len = 256
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            bp_filter = BandPassFilter(bands, fs, seq_len, fp16=True)
            
            assert bp_filter.fp16 is True
            assert bp_filter.kernels.dtype == torch.float16


class TestBandStopFilter:
    """Test BandStopFilter implementation."""
    
    def test_bandstop_initialization(self):
        """Test BandStopFilter initialization."""
        from scitex.nn import BandStopFilter
        
        bands = np.array([[45, 55], [95, 105]])  # Notch at 50Hz and 100Hz
        fs = 500
        seq_len = 1000
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(64)
            
            bs_filter = BandStopFilter(bands, fs, seq_len)
            
            assert hasattr(bs_filter, 'kernels')
            # Check design_filter called with is_bandstop=True
            for call in mock_design.call_args_list:
                assert call[1]['is_bandstop'] is True
                
    def test_bandstop_forward_pass(self):
        """Test BandStopFilter forward pass."""
        from scitex.nn import BandStopFilter
        
        bands = np.array([[48, 52]])  # 50Hz notch
        fs = 256
        seq_len = 512
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            bs_filter = BandStopFilter(bands, fs, seq_len)
            bs_filter.kernels = torch.randn(1, 32)  # Mock kernel
            
            x = torch.randn(1, 2, seq_len)
            output = bs_filter(x)
            
            assert output.shape == (1, 2, 1, seq_len)


class TestLowPassFilter:
    """Test LowPassFilter implementation."""
    
    def test_lowpass_initialization(self):
        """Test LowPassFilter initialization."""
        from scitex.nn import LowPassFilter
        
        cutoffs = np.array([10, 20, 30])
        fs = 100
        seq_len = 256
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            lp_filter = LowPassFilter(cutoffs, fs, seq_len)
            
            assert hasattr(lp_filter, 'kernels')
            assert mock_design.call_count == 3
            
            # Check low_hz is None for lowpass
            for call in mock_design.call_args_list:
                assert call[1]['low_hz'] is None
                
    def test_lowpass_cutoff_validation(self):
        """Test lowpass cutoff frequency validation."""
        from scitex.nn import LowPassFilter
        
        fs = 100
        cutoffs = np.array([60])  # Above Nyquist
        seq_len = 256
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            # Should clip to below Nyquist
            lp_filter = LowPassFilter(cutoffs, fs, seq_len)
            
            call_args = mock_design.call_args[1]
            assert call_args['high_hz'] < fs / 2
            
    def test_lowpass_forward_pass(self):
        """Test LowPassFilter forward pass."""
        from scitex.nn import LowPassFilter
        
        cutoffs = np.array([15, 25])
        fs = 100
        seq_len = 200
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(16)
            
            lp_filter = LowPassFilter(cutoffs, fs, seq_len)
            lp_filter.kernels = torch.randn(2, 16)  # Mock kernels
            
            x = torch.randn(3, 4, seq_len)
            output = lp_filter(x)
            
            assert output.shape == (3, 4, 2, seq_len)


class TestHighPassFilter:
    """Test HighPassFilter implementation."""
    
    def test_highpass_initialization(self):
        """Test HighPassFilter initialization."""
        from scitex.nn import HighPassFilter
        
        cutoffs = np.array([1, 5, 10])
        fs = 100
        seq_len = 256
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            hp_filter = HighPassFilter(cutoffs, fs, seq_len)
            
            assert hasattr(hp_filter, 'kernels')
            assert mock_design.call_count == 3
            
            # Check high_hz is None for highpass
            for call in mock_design.call_args_list:
                assert call[1]['high_hz'] is None
                
    def test_highpass_forward_pass(self):
        """Test HighPassFilter forward pass."""
        from scitex.nn import HighPassFilter
        
        cutoffs = np.array([0.5, 1.0])
        fs = 50
        seq_len = 400
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            hp_filter = HighPassFilter(cutoffs, fs, seq_len)
            hp_filter.kernels = torch.randn(2, 32)  # Mock kernels
            
            x = torch.randn(2, 3, seq_len)
            output = hp_filter(x)
            
            assert output.shape == (2, 3, 2, seq_len)


class TestGaussianFilter:
    """Test GaussianFilter implementation."""
    
    def test_gaussian_initialization(self):
        """Test GaussianFilter initialization."""
        from scitex.nn import GaussianFilter
        
        sigma = 5
        
        with patch('scitex.gen._to_even.to_even') as mock_to_even:
            mock_to_even.return_value = 6  # Make sigma even
            
            gauss_filter = GaussianFilter(sigma)
            
            assert hasattr(gauss_filter, 'kernels')
            assert gauss_filter.sigma == 6
            
    def test_gaussian_kernel_generation(self):
        """Test Gaussian kernel generation."""
        from scitex.nn import GaussianFilter
        
        sigma = 4
        kernel_size = sigma * 6  # +/- 3SD
        
        kernels = GaussianFilter.init_kernels(sigma)
        
        # Check kernel properties
        assert kernels.shape[0] == 1  # Single filter
        assert kernels.shape[1] >= kernel_size
        assert torch.allclose(kernels.sum(), torch.tensor(1.0), atol=1e-6)  # Normalized
        
    def test_gaussian_forward_pass(self):
        """Test GaussianFilter forward pass."""
        from scitex.nn import GaussianFilter
        
        with patch('scitex.gen._to_even.to_even') as mock_to_even:
            mock_to_even.return_value = 4
            
            gauss_filter = GaussianFilter(3)
            gauss_filter.kernels = torch.randn(1, 24)  # Mock kernel
            
            x = torch.randn(2, 3, 100)
            output = gauss_filter(x)
            
            assert output.shape == (2, 3, 1, 100)
            
    def test_gaussian_smoothing_effect(self):
        """Test that Gaussian filter provides smoothing."""
        from scitex.nn import GaussianFilter
        
        # Create a signal with noise
        t = torch.linspace(0, 1, 200)
        clean_signal = torch.sin(2 * np.pi * 5 * t)
        noise = torch.randn_like(t) * 0.5
        noisy_signal = clean_signal + noise
        noisy_signal = noisy_signal.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
        
        with patch('scitex.gen._to_even.to_even') as mock_to_even:
            mock_to_even.return_value = 8
            
            gauss_filter = GaussianFilter(8)
            
            smoothed = gauss_filter(noisy_signal)
            
            # Smoothed signal should have less variance than noisy signal
            assert smoothed.var() < noisy_signal.var()


class TestDifferentiableBandPassFilter:
    """Test DifferentiableBandPassFilter with learnable parameters."""
    
    def test_differentiable_initialization(self):
        """Test DifferentiableBandPassFilter initialization."""
        from scitex.nn import DifferentiableBandPassFilter
        
        sig_len = 512
        fs = 256
        
        with patch('scitex.nn._Filters.init_bandpass_filters') as mock_init:
            mock_kernels = torch.randn(80, 64)
            mock_pha_mids = torch.linspace(2, 20, 30)
            mock_amp_mids = torch.linspace(80, 160, 50)
            mock_init.return_value = (mock_kernels, mock_pha_mids, mock_amp_mids)
            
            dbp_filter = DifferentiableBandPassFilter(sig_len, fs)
            
            assert dbp_filter.sig_len == sig_len
            assert dbp_filter.fs == fs
            assert hasattr(dbp_filter, 'pha_mids')
            assert hasattr(dbp_filter, 'amp_mids')
            
    def test_differentiable_frequency_constraints(self):
        """Test frequency constraints are enforced."""
        from scitex.nn import DifferentiableBandPassFilter
        
        sig_len = 1024
        fs = 200  # Low fs to test Nyquist constraints
        
        with patch('scitex.nn._Filters.init_bandpass_filters') as mock_init:
            mock_init.return_value = (torch.randn(50, 64), torch.randn(20), torch.randn(30))
            
            # Try to set frequencies beyond Nyquist
            dbp_filter = DifferentiableBandPassFilter(
                sig_len, fs,
                pha_high_hz=150,  # Above Nyquist
                amp_high_hz=200   # Above Nyquist
            )
            
            # Should be constrained during initialization
            assert dbp_filter.pha_high_hz < fs / 2
            assert dbp_filter.amp_high_hz < fs / 2
            
    def test_differentiable_forward_pass(self):
        """Test DifferentiableBandPassFilter forward pass."""
        from scitex.nn import DifferentiableBandPassFilter
        
        sig_len = 256
        fs = 128
        
        with patch('scitex.nn._Filters.init_bandpass_filters') as mock_init:
            with patch('scitex.nn._Filters.build_bandpass_filters') as mock_build:
                # Setup mocks
                n_total_bands = 20
                mock_init.return_value = (
                    torch.randn(n_total_bands, 32),
                    torch.linspace(2, 20, 10),
                    torch.linspace(30, 60, 10)
                )
                mock_build.return_value = torch.randn(n_total_bands, 32)
                
                dbp_filter = DifferentiableBandPassFilter(sig_len, fs, pha_n_bands=10, amp_n_bands=10)
                
                x = torch.randn(2, 3, sig_len)
                output = dbp_filter(x)
                
                assert output.shape == (2, 3, n_total_bands, sig_len)
                assert mock_build.called  # Kernels rebuilt in forward
                
    def test_differentiable_gradient_flow(self):
        """Test gradient flow through learnable parameters."""
        from scitex.nn import DifferentiableBandPassFilter
        
        sig_len = 128
        fs = 64
        
        with patch('scitex.nn._Filters.init_bandpass_filters') as mock_init:
            with patch('scitex.nn._Filters.build_bandpass_filters') as mock_build:
                # Make pha_mids and amp_mids parameters
                pha_mids = nn.Parameter(torch.linspace(2, 20, 5))
                amp_mids = nn.Parameter(torch.linspace(25, 30, 5))
                
                mock_init.return_value = (torch.randn(10, 16), pha_mids, amp_mids)
                mock_build.return_value = torch.randn(10, 16)
                
                dbp_filter = DifferentiableBandPassFilter(sig_len, fs, pha_n_bands=5, amp_n_bands=5)
                dbp_filter.pha_mids = pha_mids
                dbp_filter.amp_mids = amp_mids
                
                x = torch.randn(1, 1, sig_len, requires_grad=True)
                output = dbp_filter(x)
                loss = output.sum()
                
                # Gradient should flow
                loss.backward()
                assert x.grad is not None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_short_sequence_handling(self):
        """Test filters with very short sequences."""
        from scitex.nn import BandPassFilter
        
        bands = torch.tensor([[5, 10]])
        fs = 50
        seq_len = 32  # Very short
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(8)
            
            bp_filter = BandPassFilter(bands, fs, seq_len)
            bp_filter.kernels = torch.randn(1, 8)
            
            x = torch.randn(1, 1, seq_len)
            output = bp_filter(x)
            
            assert output.shape[-1] <= seq_len
            
    def test_single_channel_single_batch(self):
        """Test filters with minimal dimensions."""
        from scitex.nn import LowPassFilter
        
        cutoffs = np.array([10])
        fs = 50
        seq_len = 100
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(16)
            
            lp_filter = LowPassFilter(cutoffs, fs, seq_len)
            lp_filter.kernels = torch.randn(1, 16)
            
            x = torch.randn(1, 1, seq_len)
            output = lp_filter(x)
            
            assert output.shape == (1, 1, 1, seq_len)
            
    def test_time_parameter_handling(self):
        """Test filters with optional time parameter."""
        from scitex.nn import HighPassFilter
        
        cutoffs = np.array([1.0])
        fs = 20
        seq_len = 200
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(16)
            
            hp_filter = HighPassFilter(cutoffs, fs, seq_len)
            hp_filter.kernels = torch.randn(1, 16)
            
            x = torch.randn(2, 3, seq_len)
            t = torch.linspace(0, 10, seq_len)
            
            # Test with time parameter
            x_out, t_out = hp_filter(x, t=t, edge_len=10)
            
            assert x_out.shape[-1] == t_out.shape[-1]
            assert t_out.shape[-1] == seq_len - 20  # 10 from each edge


class TestMultiFilterProcessing:
    """Test processing with multiple filters."""
    
    def test_multi_band_processing(self):
        """Test processing multiple frequency bands."""
        from scitex.nn import BandPassFilter
        
        # Define multiple bands
        bands = torch.tensor([
            [1, 4],    # Delta
            [4, 8],    # Theta
            [8, 13],   # Alpha
            [13, 30],  # Beta
            [30, 100]  # Gamma
        ])
        fs = 256
        seq_len = 1024
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(64)
            
            bp_filter = BandPassFilter(bands, fs, seq_len)
            bp_filter.kernels = torch.randn(5, 64)
            
            x = torch.randn(4, 8, seq_len)
            output = bp_filter(x)
            
            assert output.shape == (4, 8, 5, seq_len)
            
    def test_cascade_filtering(self):
        """Test cascading multiple filter types."""
        from scitex.nn import HighPassFilter, LowPassFilter
        
        fs = 100
        seq_len = 500
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            # Highpass then lowpass (bandpass equivalent)
            hp_filter = HighPassFilter(np.array([5]), fs, seq_len)
            lp_filter = LowPassFilter(np.array([20]), fs, seq_len)
            
            hp_filter.kernels = torch.randn(1, 32)
            lp_filter.kernels = torch.randn(1, 32)
            
            x = torch.randn(2, 3, seq_len)
            
            # Apply filters in sequence
            x_hp = hp_filter(x)
            x_bp = lp_filter(x_hp[:, :, 0, :])  # Take first filter output
            
            assert x_bp.shape[0:2] == x.shape[0:2]


class TestDeviceCompatibility:
    """Test filter operations on different devices."""
    
    def test_cpu_filtering(self):
        """Test filtering on CPU."""
        from scitex.nn import GaussianFilter
        
        with patch('scitex.gen._to_even.to_even') as mock_to_even:
            mock_to_even.return_value = 4
            
            gauss_filter = GaussianFilter(4)
            x = torch.randn(2, 3, 100)
            
            output = gauss_filter(x)
            
            assert output.device.type == 'cpu'
            
    def test_cuda_filtering(self):
        """Test filtering on CUDA if available."""
        from scitex.nn import BandPassFilter
        
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        bands = torch.tensor([[10, 20]]).cuda()
        fs = 100
        seq_len = 256
        
        with patch('scitex.nn._Filters.design_filter') as mock_design:
            mock_design.return_value = np.random.randn(32)
            
            bp_filter = BandPassFilter(bands, fs, seq_len).cuda()
            bp_filter.kernels = torch.randn(1, 32).cuda()
            
            x = torch.randn(2, 3, seq_len).cuda()
            output = bp_filter(x)
            
            assert output.is_cuda
            assert output.device == x.device


# Run tests if script is executed directly

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_Filters.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-28 17:05:26 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_Filters.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/nn/_Filters.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# # Time-stamp: "2024-11-26 22:23:40 (ywatanabe)"
# 
# import numpy as np
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_Filters.py"
# 
# """
# Implements various neural network filter layers:
#     - BaseFilter1D: Abstract base class for 1D filters
#     - BandPassFilter: Implements bandpass filtering
#     - BandStopFilter: Implements bandstop filtering
#     - LowPassFilter: Implements lowpass filtering
#     - HighPassFilter: Implements highpass filtering
#     - GaussianFilter: Implements Gaussian smoothing
#     - DifferentiableBandPassFilter: Implements learnable bandpass filtering
# """
# 
# # Imports
# import sys
# from abc import abstractmethod
# 
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# 
# from ..dsp.utils import build_bandpass_filters, init_bandpass_filters
# from ..dsp.utils._ensure_3d import ensure_3d
# from ..dsp.utils._ensure_even_len import ensure_even_len
# from ..dsp.utils._zero_pad import zero_pad
# from ..dsp.utils.filter import design_filter
# from ..gen._to_even import to_even
# 
# 
# class BaseFilter1D(nn.Module):
#     def __init__(self, fp16=False, in_place=False):
#         super().__init__()
#         self.fp16 = fp16
#         self.in_place = in_place
#         # self.kernels = None
# 
#     @abstractmethod
#     def init_kernels(
#         self,
#     ):
#         """
#         Abstract method to initialize filter kernels.
#         Must be implemented by subclasses.
#         """
#         pass
# 
#     def forward(self, x, t=None, edge_len=0):
#         """Apply the filter to input signal x with shape: (batch_size, n_chs, seq_len)"""
# 
#         # Shape check
#         if self.fp16:
#             x = x.half()
# 
#         x = ensure_3d(x)
#         batch_size, n_chs, seq_len = x.shape
# 
#         # Kernel Check
#         if self.kernels is None:
#             raise ValueError("Filter kernels has not been initialized.")
# 
#         # Filtering
#         x = self.flip_extend(x, self.kernel_size // 2)
#         x = self.batch_conv(x, self.kernels, padding=0)
#         x = x[..., :seq_len]
# 
#         assert x.shape == (
#             batch_size,
#             n_chs,
#             len(self.kernels),
#             seq_len,
#         ), f"The shape of the filtered signal ({x.shape}) does not match the expected shape: ({batch_size}, {n_chs}, {len(self.kernels)}, {seq_len})."
# 
#         # Edge remove
#         x = self.remove_edges(x, edge_len)
# 
#         if t is None:
#             return x
#         else:
#             t = self.remove_edges(t, edge_len)
#             return x, t
# 
#     @property
#     def kernel_size(
#         self,
#     ):
#         ks = self.kernels.shape[-1]
#         # if not ks % 2 == 0:
#         #     raise ValueError("Kernel size should be an even number.")
#         return ks
# 
#     @staticmethod
#     def flip_extend(x, extension_length):
#         first_segment = x[:, :, :extension_length].flip(dims=[-1])
#         last_segment = x[:, :, -extension_length:].flip(dims=[-1])
#         return torch.cat([first_segment, x, last_segment], dim=-1)
# 
#     @staticmethod
#     def batch_conv(x, kernels, padding="same"):
#         """
#         x: (batch_size, n_chs, seq_len)
#         kernels: (n_kernels, seq_len_filt)
#         """
#         assert x.ndim == 3
#         assert kernels.ndim == 2
#         batch_size, n_chs, n_time = x.shape
#         x = x.reshape(-1, x.shape[-1]).unsqueeze(1)
#         kernels = kernels.unsqueeze(1)  # add the channel dimension
#         n_kernels = len(kernels)
#         filted = F.conv1d(x, kernels.type_as(x), padding=padding)
#         return filted.reshape(batch_size, n_chs, n_kernels, -1)
# 
#     @staticmethod
#     def remove_edges(x, edge_len):
#         edge_len = x.shape[-1] // 8 if edge_len == "auto" else edge_len
# 
#         if 0 < edge_len:
#             return x[..., edge_len:-edge_len]
#         else:
#             return x
# 
# 
# class BandPassFilter(BaseFilter1D):
#     def __init__(self, bands, fs, seq_len, fp16=False):
#         super().__init__(fp16=fp16)
# 
#         self.fp16 = fp16
# 
#         # Ensures bands shape
#         assert bands.ndim == 2
# 
#         # Check bands definitions
#         nyq = fs / 2.0
#         # Convert bands to tensor if it's a numpy array
#         if isinstance(bands, np.ndarray):
#             bands = torch.tensor(bands)
#         bands = torch.clip(bands, 0.1, nyq - 1)
#         for ll, hh in bands:
#             assert 0 < ll
#             assert ll < hh
#             assert hh < nyq
# 
#         # Prepare kernels
#         kernels = self.init_kernels(seq_len, fs, bands)
#         if fp16:
#             kernels = kernels.half()
#         self.register_buffer(
#             "kernels",
#             kernels,
#         )
# 
#     @staticmethod
#     def init_kernels(seq_len, fs, bands):
#         # Convert seq_len and fs to numpy arrays for design_filter (expects numpy_fn)
#         seq_len_array = np.array([seq_len])
#         fs_array = np.array([fs])
#         filters = [
#             design_filter(
#                 seq_len_array,
#                 fs_array,
#                 low_hz=ll,
#                 high_hz=hh,
#                 is_bandstop=False,
#             )
#             for ll, hh in bands
#         ]
# 
#         # Convert filters list to tensors for zero_pad
#         filters_tensors = [
#             torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
#         ]
# 
#         kernels = zero_pad(filters_tensors)
#         kernels = ensure_even_len(kernels)
#         if not isinstance(kernels, torch.Tensor):
#             kernels = torch.tensor(kernels)
#         kernels = kernels.clone().detach()
#         # kernels = kernels.clone().detach().requires_grad_(True)
#         return kernels
# 
# 
# # /home/ywatanabe/proj/scitex/src/scitex/nn/_Filters.py:155: UserWarning: To copy construct from a tensor, it is recommended to use sourceTensor.clone().detach() or sourceTensor.clone().detach().requires_grad_(True), rather than torch.tensor(sourceTensor).
# #   kernels = torch.tensor(kernels).clone().detach()
# 
# 
# class BandStopFilter(BaseFilter1D):
#     def __init__(self, bands, fs, seq_len):
#         super().__init__()
# 
#         # Ensures bands shape
#         assert bands.ndim == 2
# 
#         # Check bands definitions
#         nyq = fs / 2.0
#         bands = np.clip(bands, 0.1, nyq - 1)
#         for ll, hh in bands:
#             assert 0 < ll
#             assert ll < hh
#             assert hh < nyq
# 
#         self.register_buffer("kernels", self.init_kernels(seq_len, fs, bands))
# 
#     @staticmethod
#     def init_kernels(seq_len, fs, bands):
#         # Convert to numpy arrays for design_filter
#         seq_len_array = np.array([seq_len])
#         fs_array = np.array([fs])
#         filters = [
#             design_filter(
#                 seq_len_array, fs_array, low_hz=ll, high_hz=hh, is_bandstop=True
#             )
#             for ll, hh in bands
#         ]
#         # Convert filters list to tensors for zero_pad
#         filters_tensors = [
#             torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
#         ]
#         kernels = zero_pad(filters_tensors)
#         kernels = ensure_even_len(kernels)
#         if not isinstance(kernels, torch.Tensor):
#             kernels = torch.tensor(kernels)
#         return kernels
# 
# 
# class LowPassFilter(BaseFilter1D):
#     def __init__(self, cutoffs_hz, fs, seq_len):
#         super().__init__()
# 
#         # Ensures bands shape
#         assert cutoffs_hz.ndim == 1
# 
#         # Check bands definitions
#         nyq = fs / 2.0
#         bands = np.clip(cutoffs_hz, 0.1, nyq - 1)
#         for cc in cutoffs_hz:
#             assert 0 < cc
#             assert cc < nyq
# 
#         self.register_buffer("kernels", self.init_kernels(seq_len, fs, cutoffs_hz))
# 
#     @staticmethod
#     def init_kernels(seq_len, fs, cutoffs_hz):
#         # Convert to numpy arrays for design_filter
#         seq_len_array = np.array([seq_len])
#         fs_array = np.array([fs])
#         filters = [
#             design_filter(
#                 seq_len_array, fs_array, low_hz=None, high_hz=cc, is_bandstop=False
#             )
#             for cc in cutoffs_hz
#         ]
#         # Convert filters list to tensors for zero_pad
#         filters_tensors = [
#             torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
#         ]
#         kernels = zero_pad(filters_tensors)
#         kernels = ensure_even_len(kernels)
#         if not isinstance(kernels, torch.Tensor):
#             kernels = torch.tensor(kernels)
#         return kernels
# 
# 
# class HighPassFilter(BaseFilter1D):
#     def __init__(self, cutoffs_hz, fs, seq_len):
#         super().__init__()
# 
#         # Ensures bands shape
#         assert cutoffs_hz.ndim == 1
# 
#         # Check bands definitions
#         nyq = fs / 2.0
#         bands = np.clip(cutoffs_hz, 0.1, nyq - 1)
#         for cc in cutoffs_hz:
#             assert 0 < cc
#             assert cc < nyq
# 
#         self.register_buffer("kernels", self.init_kernels(seq_len, fs, cutoffs_hz))
# 
#     @staticmethod
#     def init_kernels(seq_len, fs, cutoffs_hz):
#         # Convert to numpy arrays for design_filter
#         seq_len_array = np.array([seq_len])
#         fs_array = np.array([fs])
#         filters = [
#             design_filter(
#                 seq_len_array, fs_array, low_hz=cc, high_hz=None, is_bandstop=False
#             )
#             for cc in cutoffs_hz
#         ]
#         # Convert filters list to tensors for zero_pad
#         filters_tensors = [
#             torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
#         ]
#         kernels = zero_pad(filters_tensors)
#         kernels = ensure_even_len(kernels)
#         if not isinstance(kernels, torch.Tensor):
#             kernels = torch.tensor(kernels)
#         return kernels
# 
# 
# class GaussianFilter(BaseFilter1D):
#     def __init__(self, sigma):
#         super().__init__()
#         self.sigma = to_even(sigma)
#         self.register_buffer("kernels", self.init_kernels(sigma))
# 
#     @staticmethod
#     def init_kernels(sigma):
#         kernel_size = sigma * 6  # +/- 3SD
#         kernel_range = torch.arange(0, kernel_size) - kernel_size // 2
#         kernel = torch.exp(-0.5 * (kernel_range / sigma) ** 2)
#         kernel /= kernel.sum()
#         kernels = kernel.unsqueeze(0)  # n_filters = 1
#         kernels = ensure_even_len(kernels)
#         return torch.tensor(kernels)
# 
# 
# class DifferentiableBandPassFilter(BaseFilter1D):
#     def __init__(
#         self,
#         sig_len,
#         fs,
#         pha_low_hz=2,
#         pha_high_hz=20,
#         pha_n_bands=30,
#         amp_low_hz=80,
#         amp_high_hz=160,
#         amp_n_bands=50,
#         cycle=3,
#         fp16=False,
#     ):
#         super().__init__(fp16=fp16)
# 
#         # Attributes
#         self.pha_low_hz = pha_low_hz
#         self.pha_high_hz = pha_high_hz
#         self.amp_low_hz = amp_low_hz
#         self.amp_high_hz = amp_high_hz
#         self.sig_len = sig_len
#         self.fs = fs
#         self.cycle = cycle
#         self.fp16 = fp16
# 
#         # Check bands definitions
#         nyq = fs / 2.0
#         pha_high_hz = torch.tensor(pha_high_hz).clip(0.1, nyq - 1)
#         pha_low_hz = torch.tensor(pha_low_hz).clip(0.1, pha_high_hz - 1)
#         amp_high_hz = torch.tensor(amp_high_hz).clip(0.1, nyq - 1)
#         amp_low_hz = torch.tensor(amp_low_hz).clip(0.1, amp_high_hz - 1)
# 
#         assert pha_low_hz < pha_high_hz < nyq
#         assert amp_low_hz < amp_high_hz < nyq
# 
#         # Prepare kernels
#         self.init_kernels = init_bandpass_filters
#         self.build_bandpass_filters = build_bandpass_filters
#         kernels, self.pha_mids, self.amp_mids = self.init_kernels(
#             sig_len=sig_len,
#             fs=fs,
#             pha_low_hz=pha_low_hz,
#             pha_high_hz=pha_high_hz,
#             pha_n_bands=pha_n_bands,
#             amp_low_hz=amp_low_hz,
#             amp_high_hz=amp_high_hz,
#             amp_n_bands=amp_n_bands,
#             cycle=cycle,
#         )
# 
#         self.register_buffer(
#             "kernels",
#             kernels,
#         )
#         # self.register_buffer("pha_mids", pha_mids)
#         # self.register_buffer("amp_mids", amp_mids)
#         # self.pha_mids = nn.Parameter(pha_mids.detach())
#         # self.amp_mids = nn.Parameter(amp_mids.detach())
# 
#         if fp16:
#             self.kernels = self.kernels.half()
#             # self.pha_mids = self.pha_mids.half()
#             # self.amp_mids = self.amp_mids.half()
# 
#     def forward(self, x, t=None, edge_len=0):
#         # Constrains the parameter spaces
#         torch.clip(self.pha_mids, self.pha_low_hz, self.pha_high_hz)
#         torch.clip(self.amp_mids, self.amp_low_hz, self.amp_high_hz)
# 
#         self.kernels = self.build_bandpass_filters(
#             self.sig_len, self.fs, self.pha_mids, self.amp_mids, self.cycle
#         )
#         return super().forward(x=x, t=t, edge_len=edge_len)
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, fig_scale=5)
# 
#     xx, tt, fs = scitex.dsp.demo_sig(sig_type="chirp", fs=1024)
#     xx = torch.tensor(xx).cuda()
#     # bands = np.array([[2, 3], [3, 4]])
#     # BandPassFilter(bands, fs, xx.shape)
#     m = DifferentiableBandPassFilter(xx.shape[-1], fs).cuda()
# 
#     scitex.ml.utils.check_params(m)
#     # {'pha_mids': (torch.Size([30]), 'Learnable'),
#     #  'amp_mids': (torch.Size([50]), 'Learnable')}
# 
#     xf = m(xx)  # (8, 19, 80, 2048)
# 
#     xf.sum().backward()  # OK, differentiable
# 
#     m.pha_mids
#     # Parameter containing:
#     # tensor([ 2.0000,  2.6207,  3.2414,  3.8621,  4.4828,  5.1034,  5.7241,  6.3448,
#     #          6.9655,  7.5862,  8.2069,  8.8276,  9.4483, 10.0690, 10.6897, 11.3103,
#     #         11.9310, 12.5517, 13.1724, 13.7931, 14.4138, 15.0345, 15.6552, 16.2759,
#     #         16.8966, 17.5172, 18.1379, 18.7586, 19.3793, 20.0000],
#     #        requires_grad=True)
#     m.amp_mids
#     # Parameter containing:
#     # tensor([ 80.0000,  81.6327,  83.2653,  84.8980,  86.5306,  88.1633,  89.7959,
#     #          91.4286,  93.0612,  94.6939,  96.3265,  97.9592,  99.5918, 101.2245,
#     #         102.8571, 104.4898, 106.1225, 107.7551, 109.3878, 111.0204, 112.6531,
#     #         114.2857, 115.9184, 117.5510, 119.1837, 120.8163, 122.4490, 124.0816,
#     #         125.7143, 127.3469, 128.9796, 130.6122, 132.2449, 133.8775, 135.5102,
#     #         137.1429, 138.7755, 140.4082, 142.0408, 143.6735, 145.3061, 146.9388,
#     #         148.5714, 150.2041, 151.8367, 153.4694, 155.1020, 156.7347, 158.3673,
#     #         160.0000], requires_grad=True)
# 
#     # PSD
#     bands = torch.hstack([m.pha_mids, m.amp_mids])
# 
#     # Plots PSD
#     # matplotlib.use("TkAgg")
#     fig, axes = scitex.plt.subplots(nrows=1 + len(bands), ncols=2)
# 
#     psd, ff = scitex.dsp.psd(xx, fs)  # Orig
#     axes[0, 0].plot(tt, xx[0, 0].detach().cpu().numpy(), label="orig")
#     axes[0, 1].plot(
#         ff.detach().cpu().numpy(),
#         psd[0, 0].detach().cpu().numpy(),
#         label="orig",
#     )
# 
#     for i_filt in range(len(bands)):
#         mid_hz = int(bands[i_filt].item())
#         psd_f, ff_f = scitex.dsp.psd(xf[:, :, i_filt, :], fs)
#         axes[i_filt + 1, 0].plot(
#             tt,
#             xf[0, 0, i_filt].detach().cpu().numpy(),
#             label=f"filted at {mid_hz} Hz",
#         )
#         axes[i_filt + 1, 1].plot(
#             ff_f.detach().cpu().numpy(),
#             psd_f[0, 0].detach().cpu().numpy(),
#             label=f"filted at {mid_hz} Hz",
#         )
#     for ax in axes.ravel():
#         ax.legend(loc="upper left")
# 
#     scitex.io.save(fig, "traces.png")
#     # plt.show()
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# """
# /home/ywatanabe/proj/entrance/scitex/dsp/nn/_Filters.py
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/nn/_Filters.py
# --------------------------------------------------------------------------------
