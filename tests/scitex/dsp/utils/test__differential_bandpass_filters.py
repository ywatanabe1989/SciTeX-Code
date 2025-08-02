#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test__differential_bandpass_filters.py

"""Tests for differential bandpass filters."""

import os
import pytest
import numpy as np
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock


def test_init_bandpass_filters_basic():
    """Test basic initialization of bandpass filters."""
    from scitex.dsp.utils import init_bandpass_filters
    
    sig_len = 1000
    fs = 250
    
    # Test basic initialization
    try:
        filters, pha_mids, amp_mids = init_bandpass_filters(sig_len, fs)
        
        # Check that parameters are returned
        assert isinstance(filters, torch.Tensor)
        assert isinstance(pha_mids, nn.Parameter)
        assert isinstance(amp_mids, nn.Parameter)
        
        # Check default parameter ranges
        assert pha_mids.min() >= 2  # pha_low_hz default
        assert pha_mids.max() <= 20  # pha_high_hz default
        assert amp_mids.min() >= 60  # amp_low_hz default
        assert amp_mids.max() <= 160  # amp_high_hz default
        
    except ImportError:
        # Skip if torchaudio.prototype not available
        pytest.skip("torchaudio.prototype not available")


def test_init_bandpass_filters_custom_params():
    """Test bandpass filter initialization with custom parameters."""
    from scitex.dsp.utils import init_bandpass_filters
    
    sig_len = 2000
    fs = 500
    pha_low_hz = 1
    pha_high_hz = 30
    pha_n_bands = 20
    amp_low_hz = 50
    amp_high_hz = 200
    amp_n_bands = 40
    cycle = 5
    
    try:
        filters, pha_mids, amp_mids = init_bandpass_filters(
            sig_len, fs, pha_low_hz, pha_high_hz, pha_n_bands,
            amp_low_hz, amp_high_hz, amp_n_bands, cycle
        )
        
        # Check parameter shapes
        assert pha_mids.shape == (pha_n_bands,)
        assert amp_mids.shape == (amp_n_bands,)
        
        # Check parameter ranges
        assert pha_mids.min() >= pha_low_hz
        assert pha_mids.max() <= pha_high_hz
        assert amp_mids.min() >= amp_low_hz
        assert amp_mids.max() <= amp_high_hz
        
        # Check filter shape
        total_bands = pha_n_bands + amp_n_bands
        assert filters.shape[0] == total_bands
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_build_bandpass_filters_basic():
    """Test basic bandpass filter building."""
    from scitex.dsp.utils import build_bandpass_filters
    
    sig_len = 1000
    fs = 250
    pha_mids = torch.linspace(2, 20, 10)
    amp_mids = torch.linspace(60, 160, 15)
    cycle = 3
    
    try:
        filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        
        # Check output shape
        assert isinstance(filters, torch.Tensor)
        assert filters.ndim == 2
        assert filters.shape[0] == len(pha_mids) + len(amp_mids)  # Total bands
        
        # Filters should have odd length (impulse response characteristic)
        assert filters.shape[1] % 2 == 1
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_build_bandpass_filters_gradients():
    """Test that gradients flow through bandpass filter building."""
    from scitex.dsp.utils import build_bandpass_filters
    
    sig_len = 500
    fs = 250
    pha_mids = torch.linspace(2, 20, 5, requires_grad=True)
    amp_mids = torch.linspace(60, 160, 8, requires_grad=True)
    cycle = 3
    
    try:
        filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        
        # Compute loss and backpropagate
        loss = filters.sum()
        loss.backward()
        
        # Check that gradients are computed
        assert pha_mids.grad is not None
        assert amp_mids.grad is not None
        assert not torch.allclose(pha_mids.grad, torch.zeros_like(pha_mids.grad))
        assert not torch.allclose(amp_mids.grad, torch.zeros_like(amp_mids.grad))
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_build_bandpass_filters_torch_fn_decorator():
    """Test that torch_fn decorator works correctly."""
    from scitex.dsp.utils import build_bandpass_filters
    
    sig_len = 500
    fs = 250
    # Test with numpy arrays (should be converted by decorator)
    pha_mids = np.linspace(2, 20, 5)
    amp_mids = np.linspace(60, 160, 8)
    cycle = 3
    
    try:
        filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        
        # Should return torch tensor
        assert isinstance(filters, torch.Tensor)
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_bandpass_filters_real_eeg_scenario():
    """Test bandpass filters with realistic EEG parameters."""
    from scitex.dsp.utils import init_bandpass_filters
    
    # Realistic EEG parameters
    fs = 250  # Common EEG sampling rate
    duration = 2.0  # 2 seconds of data
    sig_len = int(fs * duration)
    
    # Phase frequencies: alpha and beta bands
    pha_low_hz = 8    # Alpha start
    pha_high_hz = 30  # Beta end
    pha_n_bands = 20
    
    # Amplitude frequencies: gamma band
    amp_low_hz = 30
    amp_high_hz = 100
    amp_n_bands = 30
    
    cycle = 3
    
    try:
        filters, pha_mids, amp_mids = init_bandpass_filters(
            sig_len, fs, pha_low_hz, pha_high_hz, pha_n_bands,
            amp_low_hz, amp_high_hz, amp_n_bands, cycle
        )
        
        # Check that we have appropriate number of filters
        total_bands = pha_n_bands + amp_n_bands
        assert filters.shape[0] == total_bands
        
        # Check frequency ranges are appropriate for EEG
        assert pha_mids.min() >= 8.0  # Alpha band start
        assert pha_mids.max() <= 30.0  # Beta band end
        assert amp_mids.min() >= 30.0  # Gamma band start
        assert amp_mids.max() <= 100.0  # Gamma band end
        
        # Check that parameters are learnable
        assert pha_mids.requires_grad
        assert amp_mids.requires_grad
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_bandpass_filters_different_signal_lengths():
    """Test bandpass filters with different signal lengths."""
    from scitex.dsp.utils import build_bandpass_filters
    
    fs = 250
    pha_mids = torch.linspace(2, 20, 5)
    amp_mids = torch.linspace(60, 160, 5)
    cycle = 3
    
    signal_lengths = [100, 500, 1000, 2000]
    
    try:
        for sig_len in signal_lengths:
            filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
            
            # Should successfully create filters for all lengths
            assert isinstance(filters, torch.Tensor)
            assert filters.shape[0] == len(pha_mids) + len(amp_mids)
            
            # Filter length should be appropriate for signal length
            assert filters.shape[1] <= sig_len
            
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_bandpass_filters_edge_cases():
    """Test bandpass filters with edge cases."""
    from scitex.dsp.utils import build_bandpass_filters
    
    try:
        # Test with single band
        sig_len = 1000
        fs = 250
        pha_mids = torch.tensor([10.0])
        amp_mids = torch.tensor([80.0])
        cycle = 3
        
        filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        assert filters.shape[0] == 2  # One pha + one amp band
        
        # Test with very short signal
        sig_len = 100
        filters_short = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        assert filters_short.shape[1] <= sig_len
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")


def test_bandpass_filters_parameter_validation():
    """Test parameter validation in bandpass filter functions."""
    from scitex.dsp.utils import build_bandpass_filters
    
    sig_len = 1000
    fs = 250
    cycle = 3
    
    try:
        # Test with overlapping pha and amp frequency ranges
        pha_mids = torch.linspace(5, 25, 5)
        amp_mids = torch.linspace(20, 100, 5)  # Overlap with pha range
        
        filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        assert isinstance(filters, torch.Tensor)
        
        # Test with wide frequency range
        pha_mids = torch.linspace(1, 50, 10)
        amp_mids = torch.linspace(60, 120, 10)
        
        filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
        assert isinstance(filters, torch.Tensor)
        
    except ImportError:
        pytest.skip("torchaudio.prototype not available")

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/utils/_differential_bandpass_filters.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-26 22:24:13 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dsp/utils/_differential_bandpass_filters.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dsp/utils/_differential_bandpass_filters.py"
# 
# import sys
# 
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# import torch.nn as nn
# 
# from ...decorators import torch_fn
# from ...gen._to_even import to_even
# from ...gen._to_odd import to_odd
# 
# try:
#     from torchaudio.prototype.functional import sinc_impulse_response
# except:
#     pass
# 
# 
# # Functions
# @torch_fn
# def init_bandpass_filters(
#     sig_len,
#     fs,
#     pha_low_hz=2,
#     pha_high_hz=20,
#     pha_n_bands=30,
#     amp_low_hz=60,
#     amp_high_hz=160,
#     amp_n_bands=50,
#     cycle=3,
# ):
#     # Learnable parameters
#     pha_mids = nn.Parameter(torch.linspace(pha_low_hz, pha_high_hz, pha_n_bands))
#     amp_mids = nn.Parameter(torch.linspace(amp_low_hz, amp_high_hz, amp_n_bands))
#     filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)
#     return filters, pha_mids, amp_mids
# 
# 
# @torch_fn
# def build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle):
#     def _define_freqs(mids, factor):
#         lows = mids - mids / factor
#         highs = mids + mids / factor
#         return lows, highs
# 
#     def define_order(low_hz, fs, sig_len, cycle):
#         order = cycle * int((fs // low_hz))
#         order = order if 3 * order >= sig_len else (sig_len - 1) // 3
#         order = to_even(order)
#         return order
# 
#     def _calc_filters(lows_hz, highs_hz, fs, order):
#         nyq = fs / 2.0
#         order = to_odd(order)
#         # lowpass filters
#         irs_ll = sinc_impulse_response(lows_hz / nyq, window_size=order)
#         irs_hh = sinc_impulse_response(highs_hz / nyq, window_size=order)
#         irs = irs_ll - irs_hh
#         return irs
# 
#     # Main
#     pha_lows, pha_highs = _define_freqs(pha_mids, factor=4.0)
#     amp_lows, amp_highs = _define_freqs(amp_mids, factor=8.0)
# 
#     lowest = min(pha_lows.min().item(), amp_lows.min().item())
#     order = define_order(lowest, fs, sig_len, cycle)
# 
#     pha_bp_filters = _calc_filters(pha_lows, pha_highs, fs, order)
#     amp_bp_filters = _calc_filters(amp_lows, amp_highs, fs, order)
#     return torch.vstack([pha_bp_filters, amp_bp_filters])
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, agg=True)
# 
#     # Demo signal
#     freqs_hz = [10, 30, 100, 300]
#     fs = 1024
#     xx, tt, fs = scitex.dsp.demo_sig(fs=fs, freqs_hz=freqs_hz)
# 
#     # Main
#     filters, pha_mids, amp_mids = init_bandpass_filters(xx.shape[-1], fs)
# 
#     filters.sum().backward()  # OK. The filtering bands are trainable with backpropagation.
# 
#     # Update 'pha_mids' and 'amp_mids' in the forward method.
#     # Then, re-build filters using optimized parameters like this:
#     # self.filters = build_bandpass_filters(self.sig_len, self.fs, self.pha_mids, self.amp_mids, self.cycle)
# 
#     mids_all = np.concatenate(
#         [pha_mids.detach().cpu().numpy(), amp_mids.detach().cpu().numpy()]
#     )
# 
#     for i_filter in range(len(mids_all)):
#         mid = mids_all[i_filter]
#         fig = scitex.dsp.utils.filter.plot_filter_responses(
#             filters[i_filter].detach().cpu().numpy(), fs, title=f"{mid:.1f} Hz"
#         )
#         scitex.io.save(
#             fig,
#             f"differentiable_bandpass_filter_reponses_filter#{i_filter:03d}_{mid:.1f}_Hz.png",
#         )
#     # plt.show()
# 
# # EOF
# 
# """
# python -m scitex.dsp.utils._differential_bandpass_filters
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/utils/_differential_bandpass_filters.py
# --------------------------------------------------------------------------------
