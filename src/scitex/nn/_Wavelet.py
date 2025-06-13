#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 07:17:26 (ywatanabe)"
# File: ./scitex_repo/src/scitex/nn/_Wavelet.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-05-30 11:04:45 (ywatanabe)"


import scitex
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..gen._to_even import to_even
from ..gen._to_odd import to_odd


class Wavelet(nn.Module):
    def __init__(
        self, samp_rate, kernel_size=None, freq_scale="linear", out_scale="log"
    ):
        super().__init__()
        self.register_buffer("dummy", torch.tensor(0))
        self.kernel = None
        self.init_kernel(samp_rate, kernel_size=kernel_size, freq_scale=freq_scale)
        self.out_scale = out_scale

    def forward(self, x):
        """Apply the 2D filter (n_filts, kernel_size) to input signal x with shape: (batch_size, n_chs, seq_len)"""
        x = scitex.dsp.ensure_3d(x).to(self.dummy.device)
        seq_len = x.shape[-1]

        # Ensure the kernel is initialized
        if self.kernel is None:
            self.init_kernel()
            if self.kernel is None:
                raise ValueError("Filter kernel has not been initialized.")
        assert self.kernel.ndim == 2
        self.kernel = self.kernel.to(x.device)  # cuda, torch.complex128

        # Edge handling and convolution
        extension_length = self.radius
        first_segment = x[:, :, :extension_length].flip(dims=[-1])
        last_segment = x[:, :, -extension_length:].flip(dims=[-1])
        extended_x = torch.cat([first_segment, x, last_segment], dim=-1)

        # working??
        kernel_batched = self.kernel.unsqueeze(1)
        extended_x_reshaped = extended_x.view(-1, 1, extended_x.shape[-1])

        filtered_x_real = F.conv1d(
            extended_x_reshaped, kernel_batched.real.float(), groups=1
        )
        filtered_x_imag = F.conv1d(
            extended_x_reshaped, kernel_batched.imag.float(), groups=1
        )

        filtered_x = torch.view_as_complex(
            torch.stack([filtered_x_real, filtered_x_imag], dim=-1)
        )

        filtered_x = filtered_x.view(
            x.shape[0], x.shape[1], kernel_batched.shape[0], -1
        )
        filtered_x = filtered_x.view(
            x.shape[0], x.shape[1], kernel_batched.shape[0], -1
        )
        filtered_x = filtered_x[..., :seq_len]
        assert filtered_x.shape[-1] == seq_len

        pha = filtered_x.angle()
        amp = filtered_x.abs()

        # Repeats freqs
        freqs = (
            self.freqs.unsqueeze(0).unsqueeze(0).repeat(pha.shape[0], pha.shape[1], 1)
        )

        if self.out_scale == "log":
            return pha, torch.log(amp + 1e-5), freqs
        else:
            return pha, amp, freqs

    def init_kernel(self, samp_rate, kernel_size=None, freq_scale="log"):
        device = self.dummy.device
        morlets, freqs = self.gen_morlet_to_nyquist(
            samp_rate, kernel_size=kernel_size, freq_scale=freq_scale
        )
        self.kernel = torch.tensor(morlets).to(device)
        self.freqs = torch.tensor(freqs).float().to(device)

    @staticmethod
    def gen_morlet_to_nyquist(samp_rate, kernel_size=None, freq_scale="linear"):
        """
        Generates Morlet wavelets for exponentially increasing frequency bands up to the Nyquist frequency.

        Parameters:
        - samp_rate (int): The sampling rate of the signal, in Hertz.
        - kernel_size (int): The size of the kernel, in number of samples.

        Returns:
        - np.ndarray: A 2D array of complex values representing the Morlet wavelets for each frequency band.
        """
        if kernel_size is None:
            kernel_size = int(samp_rate)  # * 2.5)

        nyquist_freq = samp_rate / 2

        # Log freq_scale
        def calc_freq_boundaries_log(nyquist_freq):
            n_kernels = int(np.floor(np.log2(nyquist_freq)))
            mid_hz = np.array([2 ** (n + 1) for n in range(n_kernels)])
            width_hz = np.hstack([np.array([1]), np.diff(mid_hz) / 2]) + 1
            low_hz = mid_hz - width_hz
            high_hz = mid_hz + width_hz
            low_hz[0] = 0.1
            return low_hz, high_hz

        def calc_freq_boundaries_linear(nyquist_freq):
            n_kernels = int(nyquist_freq)
            high_hz = np.linspace(1, nyquist_freq, n_kernels)
            low_hz = high_hz - np.hstack([np.array(1), np.diff(high_hz)])
            low_hz[0] = 0.1
            return low_hz, high_hz

        if freq_scale == "linear":
            fn = calc_freq_boundaries_linear
        if freq_scale == "log":
            fn = calc_freq_boundaries_log
        low_hz, high_hz = fn(nyquist_freq)

        morlets = []
        freqs = []

        for _, (ll, hh) in enumerate(zip(low_hz, high_hz)):
            if ll > nyquist_freq:
                break

            center_frequency = (ll + hh) / 2

            t = np.arange(-kernel_size // 2, kernel_size // 2) / samp_rate
            # Calculate standard deviation of the gaussian window for a given center frequency
            sigma = 7 / (2 * np.pi * center_frequency)
            sine_wave = np.exp(2j * np.pi * center_frequency * t)
            gaussian_window = np.exp(-(t**2) / (2 * sigma**2))
            morlet_wavelet = sine_wave * gaussian_window

            freqs.append(center_frequency)
            morlets.append(morlet_wavelet)

        return np.array(morlets), np.array(freqs)

    @property
    def kernel_size(
        self,
    ):
        return to_even(self.kernel.shape[-1])

    @property
    def radius(
        self,
    ):
        return to_even(self.kernel_size // 2)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scitex

    xx, tt, fs = scitex.dsp.demo_sig(sig_type="chirp")

    pha, amp, ff = scitex.dsp.wavelet(xx, fs)

    fig, ax = scitex.plt.subplots()
    ax.imshow2d(amp[0, 0].T)
    ax = scitex.plt.ax.set_ticks(ax, xticks=tt, yticks=ff)
    ax = scitex.plt.ax.set_n_ticks(ax)
    plt.show()


# EOF
