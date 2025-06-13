#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-28 17:05:26 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_Filters.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/nn/_Filters.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-11-26 22:23:40 (ywatanabe)"

import numpy as np

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_Filters.py"

"""
Implements various neural network filter layers:
    - BaseFilter1D: Abstract base class for 1D filters
    - BandPassFilter: Implements bandpass filtering
    - BandStopFilter: Implements bandstop filtering
    - LowPassFilter: Implements lowpass filtering
    - HighPassFilter: Implements highpass filtering
    - GaussianFilter: Implements Gaussian smoothing
    - DifferentiableBandPassFilter: Implements learnable bandpass filtering
"""

# Imports
import sys
from abc import abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..dsp.utils import build_bandpass_filters, init_bandpass_filters
from ..dsp.utils._ensure_3d import ensure_3d
from ..dsp.utils._ensure_even_len import ensure_even_len
from ..dsp.utils._zero_pad import zero_pad
from ..dsp.utils.filter import design_filter
from ..gen._to_even import to_even


class BaseFilter1D(nn.Module):
    def __init__(self, fp16=False, in_place=False):
        super().__init__()
        self.fp16 = fp16
        self.in_place = in_place
        # self.kernels = None

    @abstractmethod
    def init_kernels(
        self,
    ):
        """
        Abstract method to initialize filter kernels.
        Must be implemented by subclasses.
        """
        pass

    def forward(self, x, t=None, edge_len=0):
        """Apply the filter to input signal x with shape: (batch_size, n_chs, seq_len)"""

        # Shape check
        if self.fp16:
            x = x.half()

        x = ensure_3d(x)
        batch_size, n_chs, seq_len = x.shape

        # Kernel Check
        if self.kernels is None:
            raise ValueError("Filter kernels has not been initialized.")

        # Filtering
        x = self.flip_extend(x, self.kernel_size // 2)
        x = self.batch_conv(x, self.kernels, padding=0)
        x = x[..., :seq_len]

        assert x.shape == (
            batch_size,
            n_chs,
            len(self.kernels),
            seq_len,
        ), f"The shape of the filtered signal ({x.shape}) does not match the expected shape: ({batch_size}, {n_chs}, {len(self.kernels)}, {seq_len})."

        # Edge remove
        x = self.remove_edges(x, edge_len)

        if t is None:
            return x
        else:
            t = self.remove_edges(t, edge_len)
            return x, t

    @property
    def kernel_size(
        self,
    ):
        ks = self.kernels.shape[-1]
        # if not ks % 2 == 0:
        #     raise ValueError("Kernel size should be an even number.")
        return ks

    @staticmethod
    def flip_extend(x, extension_length):
        first_segment = x[:, :, :extension_length].flip(dims=[-1])
        last_segment = x[:, :, -extension_length:].flip(dims=[-1])
        return torch.cat([first_segment, x, last_segment], dim=-1)

    @staticmethod
    def batch_conv(x, kernels, padding="same"):
        """
        x: (batch_size, n_chs, seq_len)
        kernels: (n_kernels, seq_len_filt)
        """
        assert x.ndim == 3
        assert kernels.ndim == 2
        batch_size, n_chs, n_time = x.shape
        x = x.reshape(-1, x.shape[-1]).unsqueeze(1)
        kernels = kernels.unsqueeze(1)  # add the channel dimension
        n_kernels = len(kernels)
        filted = F.conv1d(x, kernels.type_as(x), padding=padding)
        return filted.reshape(batch_size, n_chs, n_kernels, -1)

    @staticmethod
    def remove_edges(x, edge_len):
        edge_len = x.shape[-1] // 8 if edge_len == "auto" else edge_len

        if 0 < edge_len:
            return x[..., edge_len:-edge_len]
        else:
            return x


class BandPassFilter(BaseFilter1D):
    def __init__(self, bands, fs, seq_len, fp16=False):
        super().__init__(fp16=fp16)

        self.fp16 = fp16

        # Ensures bands shape
        assert bands.ndim == 2

        # Check bands definitions
        nyq = fs / 2.0
        # Convert bands to tensor if it's a numpy array
        if isinstance(bands, np.ndarray):
            bands = torch.tensor(bands)
        bands = torch.clip(bands, 0.1, nyq - 1)
        for ll, hh in bands:
            assert 0 < ll
            assert ll < hh
            assert hh < nyq

        # Prepare kernels
        kernels = self.init_kernels(seq_len, fs, bands)
        if fp16:
            kernels = kernels.half()
        self.register_buffer(
            "kernels",
            kernels,
        )

    @staticmethod
    def init_kernels(seq_len, fs, bands):
        # Convert seq_len and fs to numpy arrays for design_filter (expects numpy_fn)
        seq_len_array = np.array([seq_len])
        fs_array = np.array([fs])
        filters = [
            design_filter(
                seq_len_array,
                fs_array,
                low_hz=ll,
                high_hz=hh,
                is_bandstop=False,
            )
            for ll, hh in bands
        ]

        # Convert filters list to tensors for zero_pad
        filters_tensors = [
            torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
        ]

        kernels = zero_pad(filters_tensors)
        kernels = ensure_even_len(kernels)
        if not isinstance(kernels, torch.Tensor):
            kernels = torch.tensor(kernels)
        kernels = kernels.clone().detach()
        # kernels = kernels.clone().detach().requires_grad_(True)
        return kernels


# /home/ywatanabe/proj/scitex/src/scitex/nn/_Filters.py:155: UserWarning: To copy construct from a tensor, it is recommended to use sourceTensor.clone().detach() or sourceTensor.clone().detach().requires_grad_(True), rather than torch.tensor(sourceTensor).
#   kernels = torch.tensor(kernels).clone().detach()


class BandStopFilter(BaseFilter1D):
    def __init__(self, bands, fs, seq_len):
        super().__init__()

        # Ensures bands shape
        assert bands.ndim == 2

        # Check bands definitions
        nyq = fs / 2.0
        bands = np.clip(bands, 0.1, nyq - 1)
        for ll, hh in bands:
            assert 0 < ll
            assert ll < hh
            assert hh < nyq

        self.register_buffer("kernels", self.init_kernels(seq_len, fs, bands))

    @staticmethod
    def init_kernels(seq_len, fs, bands):
        # Convert to numpy arrays for design_filter
        seq_len_array = np.array([seq_len])
        fs_array = np.array([fs])
        filters = [
            design_filter(
                seq_len_array, fs_array, low_hz=ll, high_hz=hh, is_bandstop=True
            )
            for ll, hh in bands
        ]
        # Convert filters list to tensors for zero_pad
        filters_tensors = [
            torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
        ]
        kernels = zero_pad(filters_tensors)
        kernels = ensure_even_len(kernels)
        if not isinstance(kernels, torch.Tensor):
            kernels = torch.tensor(kernels)
        return kernels


class LowPassFilter(BaseFilter1D):
    def __init__(self, cutoffs_hz, fs, seq_len):
        super().__init__()

        # Ensures bands shape
        assert cutoffs_hz.ndim == 1

        # Check bands definitions
        nyq = fs / 2.0
        bands = np.clip(cutoffs_hz, 0.1, nyq - 1)
        for cc in cutoffs_hz:
            assert 0 < cc
            assert cc < nyq

        self.register_buffer("kernels", self.init_kernels(seq_len, fs, cutoffs_hz))

    @staticmethod
    def init_kernels(seq_len, fs, cutoffs_hz):
        # Convert to numpy arrays for design_filter
        seq_len_array = np.array([seq_len])
        fs_array = np.array([fs])
        filters = [
            design_filter(
                seq_len_array, fs_array, low_hz=None, high_hz=cc, is_bandstop=False
            )
            for cc in cutoffs_hz
        ]
        # Convert filters list to tensors for zero_pad
        filters_tensors = [
            torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
        ]
        kernels = zero_pad(filters_tensors)
        kernels = ensure_even_len(kernels)
        if not isinstance(kernels, torch.Tensor):
            kernels = torch.tensor(kernels)
        return kernels


class HighPassFilter(BaseFilter1D):
    def __init__(self, cutoffs_hz, fs, seq_len):
        super().__init__()

        # Ensures bands shape
        assert cutoffs_hz.ndim == 1

        # Check bands definitions
        nyq = fs / 2.0
        bands = np.clip(cutoffs_hz, 0.1, nyq - 1)
        for cc in cutoffs_hz:
            assert 0 < cc
            assert cc < nyq

        self.register_buffer("kernels", self.init_kernels(seq_len, fs, cutoffs_hz))

    @staticmethod
    def init_kernels(seq_len, fs, cutoffs_hz):
        # Convert to numpy arrays for design_filter
        seq_len_array = np.array([seq_len])
        fs_array = np.array([fs])
        filters = [
            design_filter(
                seq_len_array, fs_array, low_hz=cc, high_hz=None, is_bandstop=False
            )
            for cc in cutoffs_hz
        ]
        # Convert filters list to tensors for zero_pad
        filters_tensors = [
            torch.tensor(f) if not isinstance(f, torch.Tensor) else f for f in filters
        ]
        kernels = zero_pad(filters_tensors)
        kernels = ensure_even_len(kernels)
        if not isinstance(kernels, torch.Tensor):
            kernels = torch.tensor(kernels)
        return kernels


class GaussianFilter(BaseFilter1D):
    def __init__(self, sigma):
        super().__init__()
        self.sigma = to_even(sigma)
        self.register_buffer("kernels", self.init_kernels(sigma))

    @staticmethod
    def init_kernels(sigma):
        kernel_size = sigma * 6  # +/- 3SD
        kernel_range = torch.arange(0, kernel_size) - kernel_size // 2
        kernel = torch.exp(-0.5 * (kernel_range / sigma) ** 2)
        kernel /= kernel.sum()
        kernels = kernel.unsqueeze(0)  # n_filters = 1
        kernels = ensure_even_len(kernels)
        return torch.tensor(kernels)


class DifferentiableBandPassFilter(BaseFilter1D):
    def __init__(
        self,
        sig_len,
        fs,
        pha_low_hz=2,
        pha_high_hz=20,
        pha_n_bands=30,
        amp_low_hz=80,
        amp_high_hz=160,
        amp_n_bands=50,
        cycle=3,
        fp16=False,
    ):
        super().__init__(fp16=fp16)

        # Attributes
        self.pha_low_hz = pha_low_hz
        self.pha_high_hz = pha_high_hz
        self.amp_low_hz = amp_low_hz
        self.amp_high_hz = amp_high_hz
        self.sig_len = sig_len
        self.fs = fs
        self.cycle = cycle
        self.fp16 = fp16

        # Check bands definitions
        nyq = fs / 2.0
        pha_high_hz = torch.tensor(pha_high_hz).clip(0.1, nyq - 1)
        pha_low_hz = torch.tensor(pha_low_hz).clip(0.1, pha_high_hz - 1)
        amp_high_hz = torch.tensor(amp_high_hz).clip(0.1, nyq - 1)
        amp_low_hz = torch.tensor(amp_low_hz).clip(0.1, amp_high_hz - 1)

        assert pha_low_hz < pha_high_hz < nyq
        assert amp_low_hz < amp_high_hz < nyq

        # Prepare kernels
        self.init_kernels = init_bandpass_filters
        self.build_bandpass_filters = build_bandpass_filters
        kernels, self.pha_mids, self.amp_mids = self.init_kernels(
            sig_len=sig_len,
            fs=fs,
            pha_low_hz=pha_low_hz,
            pha_high_hz=pha_high_hz,
            pha_n_bands=pha_n_bands,
            amp_low_hz=amp_low_hz,
            amp_high_hz=amp_high_hz,
            amp_n_bands=amp_n_bands,
            cycle=cycle,
        )

        self.register_buffer(
            "kernels",
            kernels,
        )
        # self.register_buffer("pha_mids", pha_mids)
        # self.register_buffer("amp_mids", amp_mids)
        # self.pha_mids = nn.Parameter(pha_mids.detach())
        # self.amp_mids = nn.Parameter(amp_mids.detach())

        if fp16:
            self.kernels = self.kernels.half()
            # self.pha_mids = self.pha_mids.half()
            # self.amp_mids = self.amp_mids.half()

    def forward(self, x, t=None, edge_len=0):
        # Constrains the parameter spaces
        torch.clip(self.pha_mids, self.pha_low_hz, self.pha_high_hz)
        torch.clip(self.amp_mids, self.amp_low_hz, self.amp_high_hz)

        self.kernels = self.build_bandpass_filters(
            self.sig_len, self.fs, self.pha_mids, self.amp_mids, self.cycle
        )
        return super().forward(x=x, t=t, edge_len=edge_len)


if __name__ == "__main__":
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, fig_scale=5)

    xx, tt, fs = scitex.dsp.demo_sig(sig_type="chirp", fs=1024)
    xx = torch.tensor(xx).cuda()
    # bands = np.array([[2, 3], [3, 4]])
    # BandPassFilter(bands, fs, xx.shape)
    m = DifferentiableBandPassFilter(xx.shape[-1], fs).cuda()

    scitex.ml.utils.check_params(m)
    # {'pha_mids': (torch.Size([30]), 'Learnable'),
    #  'amp_mids': (torch.Size([50]), 'Learnable')}

    xf = m(xx)  # (8, 19, 80, 2048)

    xf.sum().backward()  # OK, differentiable

    m.pha_mids
    # Parameter containing:
    # tensor([ 2.0000,  2.6207,  3.2414,  3.8621,  4.4828,  5.1034,  5.7241,  6.3448,
    #          6.9655,  7.5862,  8.2069,  8.8276,  9.4483, 10.0690, 10.6897, 11.3103,
    #         11.9310, 12.5517, 13.1724, 13.7931, 14.4138, 15.0345, 15.6552, 16.2759,
    #         16.8966, 17.5172, 18.1379, 18.7586, 19.3793, 20.0000],
    #        requires_grad=True)
    m.amp_mids
    # Parameter containing:
    # tensor([ 80.0000,  81.6327,  83.2653,  84.8980,  86.5306,  88.1633,  89.7959,
    #          91.4286,  93.0612,  94.6939,  96.3265,  97.9592,  99.5918, 101.2245,
    #         102.8571, 104.4898, 106.1225, 107.7551, 109.3878, 111.0204, 112.6531,
    #         114.2857, 115.9184, 117.5510, 119.1837, 120.8163, 122.4490, 124.0816,
    #         125.7143, 127.3469, 128.9796, 130.6122, 132.2449, 133.8775, 135.5102,
    #         137.1429, 138.7755, 140.4082, 142.0408, 143.6735, 145.3061, 146.9388,
    #         148.5714, 150.2041, 151.8367, 153.4694, 155.1020, 156.7347, 158.3673,
    #         160.0000], requires_grad=True)

    # PSD
    bands = torch.hstack([m.pha_mids, m.amp_mids])

    # Plots PSD
    # matplotlib.use("TkAgg")
    fig, axes = scitex.plt.subplots(nrows=1 + len(bands), ncols=2)

    psd, ff = scitex.dsp.psd(xx, fs)  # Orig
    axes[0, 0].plot(tt, xx[0, 0].detach().cpu().numpy(), label="orig")
    axes[0, 1].plot(
        ff.detach().cpu().numpy(),
        psd[0, 0].detach().cpu().numpy(),
        label="orig",
    )

    for i_filt in range(len(bands)):
        mid_hz = int(bands[i_filt].item())
        psd_f, ff_f = scitex.dsp.psd(xf[:, :, i_filt, :], fs)
        axes[i_filt + 1, 0].plot(
            tt,
            xf[0, 0, i_filt].detach().cpu().numpy(),
            label=f"filted at {mid_hz} Hz",
        )
        axes[i_filt + 1, 1].plot(
            ff_f.detach().cpu().numpy(),
            psd_f[0, 0].detach().cpu().numpy(),
            label=f"filted at {mid_hz} Hz",
        )
    for ax in axes.ravel():
        ax.legend(loc="upper left")

    scitex.io.save(fig, "traces.png")
    # plt.show()

    # Close
    scitex.gen.close(CONFIG)

"""
/home/ywatanabe/proj/entrance/scitex/dsp/nn/_Filters.py
"""

# EOF
