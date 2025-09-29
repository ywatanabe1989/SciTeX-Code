#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "ywatanabe (2024-11-02 22:50:46)"
# File: ./scitex_repo/src/scitex/dsp/_crop.py

import numpy as np


def crop(sig_2d, window_length, overlap_factor=0.0, axis=-1, time=None):
    """
    Crops the input signal into overlapping windows of a specified length,
    allowing for an arbitrary axis and considering a time vector.

    Parameters:
    - sig_2d (numpy.ndarray): The input sig_2d array to be cropped. Can be multi-dimensional.
    - window_length (int): The length of each window to crop the sig_2d into.
    - overlap_factor (float): The fraction of the window that consecutive windows overlap. For example, an overlap_factor of 0.5 means 50% overlap.
    - axis (int): The time axis along which to crop the sig_2d.
        - time (numpy.ndarray): The time vector associated with the signal. Its length should match the signal's length along the cropping axis.

    Returns:
    - cropped_windows (numpy.ndarray): The cropped signal windows. The shape depends on the input shape and the specified axis.
    """
    # Ensure axis is in a valid range
    if axis < 0:
        axis += sig_2d.ndim
    if axis >= sig_2d.ndim or axis < 0:
        raise ValueError("Invalid axis. Axis out of range for sig_2d dimensions.")

    if time is not None:
        # Validate the length of the time vector against the signal's dimension
        if sig_2d.shape[axis] != len(time):
            raise ValueError(
                "Length of time vector does not match signal's dimension along the specified axis."
            )

    # Move the target axis to the last position
    axes = np.arange(sig_2d.ndim)
    axes[axis], axes[-1] = axes[-1], axes[axis]
    sig_2d_permuted = np.transpose(sig_2d, axes)

    # Compute the number of windows and the step size
    seq_len = sig_2d_permuted.shape[-1]
    step = int(window_length * (1 - overlap_factor))
    n_windows = max(
        1, ((seq_len - window_length) // step + 1)
    )  # Ensure at least 1 window

    # Crop the sig_2d into windows
    cropped_windows = []
    cropped_times = []
    for i in range(n_windows):
        start = i * step
        end = start + window_length
        cropped_windows.append(sig_2d_permuted[..., start:end])
        if time is not None:
            cropped_times.append(time[start:end])

    # Convert list of windows back to numpy array
    cropped_windows = np.array(cropped_windows)
    cropped_times = np.array(cropped_times)

    # Move the last axis back to its original position if necessary
    if axis != sig_2d.ndim - 1:
        # Compute the inverse permutation
        inv_axes = np.argsort(axes)
        cropped_windows = np.transpose(cropped_windows, axes=inv_axes)

    if time is None:
        return cropped_windows
    else:
        return cropped_windows, cropped_times


def main():
    import random

    FS = 128
    N_CHS = 19
    RECORD_S = 13
    WINDOW_S = 2
    FACTOR = 0.5

    # To pts
    record_pts = int(RECORD_S * FS)
    window_pts = int(WINDOW_S * FS)

    # Demo signal
    sig2d = np.random.rand(N_CHS, record_pts)
    time = np.arange(record_pts) / FS

    # Main
    xx, tt = crop(sig2d, window_pts, overlap_factor=FACTOR, time=time)

    print(f"sig2d.shape: {sig2d.shape}")
    print(f"xx.shape: {xx.shape}")

    # Validation
    i_seg = random.randint(0, len(xx) - 1)
    start = int(i_seg * window_pts * FACTOR)
    end = start + window_pts
    assert np.allclose(sig2d[:, start:end], xx[i_seg])


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='')
    # import argparse
    # # Argument Parser
    import sys

    import matplotlib.pyplot as plt
    import scitex

    # parser.add_argument('--var', '-v', type=int, default=1, help='')
    # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
    # args = parser.parse_args()
    # Main
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, verbose=False)
    main()
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
