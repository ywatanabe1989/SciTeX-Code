#!/usr/bin/env python3
"""Scitex dsp module."""

import warnings

# Core imports that should always work
from ._crop import crop
from ._demo_sig import demo_sig
from ._detect_ripples import detect_ripples, _preprocess, _find_events, _drop_ripples_at_edges, _calc_relative_peak_position, _sort_columns
from ._ensure_3d import ensure_3d
from ._hilbert import hilbert
from ._modulation_index import modulation_index, _reshape
from ._pac import pac
from ._psd import band_powers, psd
from ._resample import resample
from ._time import time
from ._transform import to_segments, to_sktime_df
from ._wavelet import wavelet

# Import example and params modules as submodules
from . import example
from . import params

# Try to import audio-related functions that require PortAudio
try:
    from ._listen import list_and_select_device
    _audio_available = True
except (ImportError, OSError) as e:
    warnings.warn(
        "Audio functionality unavailable: PortAudio library not found. "
        "Install PortAudio to use audio features (e.g., sudo apt-get install portaudio19-dev)",
        ImportWarning
    )
    list_and_select_device = None
    _audio_available = False

# Try to import MNE-related functions
try:
    from ._mne import get_eeg_pos
    _mne_available = True
except ImportError:
    warnings.warn(
        "MNE functionality unavailable. Install MNE-Python to use EEG position features.",
        ImportWarning
    )
    get_eeg_pos = None
    _mne_available = False

__all__ = [
    "_calc_relative_peak_position",
    "_drop_ripples_at_edges",
    "_find_events",
    "_preprocess",
    "_reshape",
    "_sort_columns",
    "band_powers",
    "crop",
    "demo_sig",
    "detect_ripples",
    "ensure_3d",
    "get_eeg_pos",
    "hilbert",
    "list_and_select_device",
    "modulation_index",
    "pac",
    "psd",
    "resample",
    "time",
    "to_segments",
    "to_sktime_df",
    "wavelet",
]