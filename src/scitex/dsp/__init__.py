#!/usr/bin/env python3
"""Scitex dsp module."""

from ._crop import crop, main
from ._demo_sig import demo_sig
from ._detect_ripples import detect_ripples, main
from ._ensure_3d import ensure_3d
from ._hilbert import hilbert
from ._listen import list_and_select_device
from ._misc import ensure_3d
from ._mne import get_eeg_pos
from ._modulation_index import modulation_index
from ._pac import pac
from ._psd import band_powers, psd
from ._resample import resample
from ._time import main, time
from ._transform import to_segments, to_sktime_df
from ._wavelet import wavelet

__all__ = [
    "band_powers",
    "crop",
    "demo_sig",
    "detect_ripples",
    "ensure_3d",
    "ensure_3d",
    "get_eeg_pos",
    "hilbert",
    "list_and_select_device",
    "main",
    "main",
    "main",
    "modulation_index",
    "pac",
    "psd",
    "resample",
    "time",
    "to_segments",
    "to_sktime_df",
    "wavelet",
]
