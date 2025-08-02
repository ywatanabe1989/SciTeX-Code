#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./tests/scitex/dsp/test_params.py

import pytest
import numpy as np
import pandas as pd


def test_params_bands_exists():
    """Test that BANDS DataFrame exists."""
    from scitex.dsp.params import BANDS
    
    assert BANDS is not None
    assert isinstance(BANDS, pd.DataFrame)


def test_params_bands_structure():
    """Test BANDS DataFrame structure and dimensions."""
    from scitex.dsp.params import BANDS
    
    # Test shape
    assert BANDS.shape == (2, 6)  # 2 rows (low_hz, high_hz), 6 bands
    
    # Test index
    expected_index = ["low_hz", "high_hz"]
    assert list(BANDS.index) == expected_index
    
    # Test columns (frequency bands)
    expected_columns = ["delta", "theta", "lalpha", "halpha", "beta", "gamma"]
    assert list(BANDS.columns) == expected_columns


def test_params_bands_values():
    """Test BANDS DataFrame contains correct frequency values."""
    from scitex.dsp.params import BANDS
    
    # Test expected frequency ranges
    expected_values = {
        "delta": [0.5, 4],
        "theta": [4, 8], 
        "lalpha": [8, 10],
        "halpha": [10, 13],
        "beta": [13, 32],
        "gamma": [32, 75]
    }
    
    for band, (low, high) in expected_values.items():
        assert BANDS.loc["low_hz", band] == low
        assert BANDS.loc["high_hz", band] == high


def test_params_bands_data_types():
    """Test BANDS DataFrame contains numeric data."""
    from scitex.dsp.params import BANDS
    
    # Test all values are numeric
    assert BANDS.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all()
    
    # Test no NaN values
    assert not BANDS.isnull().any().any()


def test_params_bands_frequency_ordering():
    """Test that frequency bands are properly ordered (non-overlapping)."""
    from scitex.dsp.params import BANDS
    
    # Test that each band's high frequency equals next band's low frequency
    bands = ["delta", "theta", "lalpha", "halpha", "beta", "gamma"]
    
    for i in range(len(bands) - 1):
        current_high = BANDS.loc["high_hz", bands[i]]
        next_low = BANDS.loc["low_hz", bands[i + 1]]
        assert current_high == next_low, f"{bands[i]} high should equal {bands[i+1]} low"


def test_params_eeg_montage_1020_exists():
    """Test that EEG_MONTAGE_1020 exists and is a list."""
    from scitex.dsp.params import EEG_MONTAGE_1020
    
    assert EEG_MONTAGE_1020 is not None
    assert isinstance(EEG_MONTAGE_1020, list)


def test_params_eeg_montage_1020_structure():
    """Test EEG_MONTAGE_1020 structure and content."""
    from scitex.dsp.params import EEG_MONTAGE_1020
    
    # Test expected number of electrodes
    assert len(EEG_MONTAGE_1020) == 19
    
    # Test all elements are strings
    assert all(isinstance(electrode, str) for electrode in EEG_MONTAGE_1020)
    
    # Test specific expected electrodes
    expected_electrodes = [
        "FP1", "F3", "C3", "P3", "O1", "FP2", "F4", "C4", "P4", "O2",
        "F7", "T7", "P7", "F8", "T8", "P8", "FZ", "CZ", "PZ"
    ]
    assert EEG_MONTAGE_1020 == expected_electrodes


def test_params_eeg_montage_1020_no_duplicates():
    """Test that EEG_MONTAGE_1020 has no duplicate electrodes."""
    from scitex.dsp.params import EEG_MONTAGE_1020
    
    assert len(EEG_MONTAGE_1020) == len(set(EEG_MONTAGE_1020))


def test_params_eeg_montage_bipolar_exists():
    """Test that EEG_MONTAGE_BIPOLAR_TRANVERSE exists and is a list."""
    from scitex.dsp.params import EEG_MONTAGE_BIPOLAR_TRANVERSE
    
    assert EEG_MONTAGE_BIPOLAR_TRANVERSE is not None
    assert isinstance(EEG_MONTAGE_BIPOLAR_TRANVERSE, list)


def test_params_eeg_montage_bipolar_structure():
    """Test EEG_MONTAGE_BIPOLAR_TRANVERSE structure and content."""
    from scitex.dsp.params import EEG_MONTAGE_BIPOLAR_TRANVERSE
    
    # Test expected number of bipolar channels
    assert len(EEG_MONTAGE_BIPOLAR_TRANVERSE) == 14
    
    # Test all elements are strings with proper format
    for channel in EEG_MONTAGE_BIPOLAR_TRANVERSE:
        assert isinstance(channel, str)
        assert "-" in channel  # Bipolar channels should have "-" separator
        parts = channel.split("-")
        assert len(parts) == 2  # Should have exactly 2 electrode names


def test_params_eeg_montage_bipolar_content():
    """Test specific bipolar channel pairs."""
    from scitex.dsp.params import EEG_MONTAGE_BIPOLAR_TRANVERSE
    
    # Test some expected bipolar pairs
    expected_channels = [
        "FP1-FP2", "F7-F3", "F3-FZ", "FZ-F4", "F4-F8",
        "T7-C3", "C3-CZ", "CZ-C4", "C4-T8",
        "P7-P3", "P3-PZ", "PZ-P4", "P4-P8",
        "O1-O2"
    ]
    
    assert EEG_MONTAGE_BIPOLAR_TRANVERSE == expected_channels


def test_params_eeg_montage_bipolar_no_duplicates():
    """Test that EEG_MONTAGE_BIPOLAR_TRANVERSE has no duplicate channels."""
    from scitex.dsp.params import EEG_MONTAGE_BIPOLAR_TRANVERSE
    
    assert len(EEG_MONTAGE_BIPOLAR_TRANVERSE) == len(set(EEG_MONTAGE_BIPOLAR_TRANVERSE))


def test_params_all_imports():
    """Test that all expected parameters can be imported together."""
    from scitex.dsp.params import BANDS, EEG_MONTAGE_1020, EEG_MONTAGE_BIPOLAR_TRANVERSE
    
    # Basic existence checks
    assert BANDS is not None
    assert EEG_MONTAGE_1020 is not None  
    assert EEG_MONTAGE_BIPOLAR_TRANVERSE is not None
    
    # Type checks
    assert isinstance(BANDS, pd.DataFrame)
    assert isinstance(EEG_MONTAGE_1020, list)
    assert isinstance(EEG_MONTAGE_BIPOLAR_TRANVERSE, list)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/params.py
# --------------------------------------------------------------------------------
# import numpy as np
# import pandas as pd
# 
# BANDS = pd.DataFrame(
#     data=np.array([[0.5, 4], [4, 8], [8, 10], [10, 13], [13, 32], [32, 75]]).T,
#     index=["low_hz", "high_hz"],
#     columns=["delta", "theta", "lalpha", "halpha", "beta", "gamma"],
# )
# 
# EEG_MONTAGE_1020 = [
#     "FP1",
#     "F3",
#     "C3",
#     "P3",
#     "O1",
#     "FP2",
#     "F4",
#     "C4",
#     "P4",
#     "O2",
#     "F7",
#     "T7",
#     "P7",
#     "F8",
#     "T8",
#     "P8",
#     "FZ",
#     "CZ",
#     "PZ",
# ]
# 
# EEG_MONTAGE_BIPOLAR_TRANVERSE = [
#     # Frontal
#     "FP1-FP2",
#     "F7-F3",
#     "F3-FZ",
#     "FZ-F4",
#     "F4-F8",
#     # Central
#     "T7-C3",
#     "C3-CZ",
#     "CZ-C4",
#     "C4-T8",
#     # Parietal
#     "P7-P3",
#     "P3-PZ",
#     "PZ-P4",
#     "P4-P8",
#     # Occipital
#     "O1-O2",
# ]

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dsp/params.py
# --------------------------------------------------------------------------------
