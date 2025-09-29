#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-02 09:21:12 (ywatanabe)"

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import scitex
from ..decorators import numpy_fn, torch_fn


class Spectrogram(nn.Module):
    def __init__(
        self,
        sampling_rate,
        n_fft=256,
        hop_length=None,
        win_length=None,
        window="hann",
    ):
        super().__init__()
        self.sampling_rate = sampling_rate
        self.n_fft = n_fft
        self.hop_length = hop_length if hop_length is not None else n_fft // 4
        self.win_length = win_length if win_length is not None else n_fft
        if window == "hann":
            self.window = torch.hann_window(window_length=self.win_length)
        else:
            raise ValueError(
                "Unsupported window type. Extend this to support more window types."
            )

    def forward(self, x):
        """
        Computes the spectrogram for each channel in the input signal.

        Parameters:
        - signal (torch.Tensor): Input signal of shape (batch_size, n_chs, seq_len).

        Returns:
        - spectrograms (torch.Tensor): The computed spectrograms for each channel.
        """

        x = scitex.dsp.ensure_3d(x)

        batch_size, n_chs, seq_len = x.shape
        spectrograms = []

        for ch in range(n_chs):
            x_ch = x[:, ch, :].unsqueeze(1)  # Maintain expected input shape for stft
            spec = torch.stft(
                x_ch.squeeze(1),
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                win_length=self.win_length,
                window=self.window.to(x.device),
                center=True,
                pad_mode="reflect",
                normalized=False,
                return_complex=True,
            )
            magnitude = torch.abs(spec).unsqueeze(1)  # Keep channel dimension
            spectrograms.append(magnitude)

        # Concatenate spectrograms along channel dimension
        spectrograms = torch.cat(spectrograms, dim=1)

        # Calculate frequencies (y-axis)
        freqs = torch.linspace(0, self.sampling_rate / 2, steps=self.n_fft // 2 + 1)

        # Calculate times (x-axis)
        # The number of frames can be computed from the size of the last dimension of the spectrogram
        n_frames = spectrograms.shape[-1]
        # Time of each frame in seconds, considering the hop length and sampling rate
        times_sec = torch.arange(0, n_frames) * (self.hop_length / self.sampling_rate)

        return spectrograms, freqs, times_sec


@torch_fn
def spectrograms(x, fs, cuda=False):
    return Spectrogram(fs)(x)


@torch_fn
def my_softmax(x, dim=-1):
    return F.softmax(x, dim=dim)


@torch_fn
def unbias(x, func="min", dim=-1, cuda=False):
    if func == "min":
        return x - x.min(dim=dim, keepdims=True)[0]
    if func == "mean":
        return x - x.mean(dim=dim, keepdims=True)[0]


@torch_fn
def normalize(x, axis=-1, amp=1.0, cuda=False):
    high = torch.abs(x.max(axis=axis, keepdims=True)[0])
    low = torch.abs(x.min(axis=axis, keepdims=True)[0])
    return amp * x / torch.maximum(high, low)


@torch_fn
def spectrograms(x, fs, dj=0.125, cuda=False):
    try:
        from wavelets_pytorch.transform import (
            WaveletTransformTorch,
        )  # PyTorch version
    except ImportError:
        raise ImportError(
            "The spectrograms function requires the wavelets-pytorch package. "
            "Install it with: pip install wavelets-pytorch"
        )

    dt = 1 / fs
    # dj = 0.125
    batch_size, n_chs, seq_len = x.shape

    x = x.cpu().numpy()

    # # Batch of signals to process
    # batch = np.array([batch_size * seq_len])

    # Initialize wavelet filter banks (scipy and torch implementation)
    # wa_scipy = WaveletTransform(dt, dj)
    wa_torch = WaveletTransformTorch(dt, dj, cuda=True)

    # Performing wavelet transform (and compute scalogram)
    # cwt_scipy = wa_scipy.cwt(batch)
    x = x[:, 0][:, np.newaxis]
    cwt_torch = wa_torch.cwt(x)

    return cwt_torch


if __name__ == "__main__":
    import scitex
    import seaborn as sns
    import torchaudio

    fs = 1024  # 128
    t_sec = 10
    x = scitex.dsp.np.demo_sig(t_sec=t_sec, fs=fs, type="ripple")

    normalize(unbias(x, cuda=True), cuda=True)

    # My implementtion
    ss = spectrograms(x, fs, cuda=True)
    fig, axes = plt.subplots(nrows=2)
    axes[0].plot(np.arange(x[0, 0]) / fs, x[0, 0])
    sns.heatmap(ss[0], ax=axes[1])
    plt.show()

    ss, ff, tt = spectrograms(x, fs, cuda=True)
    fig, axes = plt.subplots(nrows=2)
    axes[0].plot(np.arange(x[0, 0]) / fs, x[0, 0])
    sns.heatmap(ss[0], ax=axes[1])
    plt.show()

    # Torch Audio
    transform = torchaudio.transforms.Spectrogram(n_fft=16, normalized=True).cuda()
    xx = torch.tensor(x).float().cuda()[0, 0]
    ss = transform(xx)
    sns.heatmap(ss.detach().cpu().numpy())

    plt.show()
