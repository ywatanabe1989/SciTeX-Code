#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 02:07:36 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/_mne.py

import mne
import pandas as pd
from .params import EEG_MONTAGE_1020


def get_eeg_pos(channel_names=EEG_MONTAGE_1020):
    # Load the standard 10-20 montage
    standard_montage = mne.channels.make_standard_montage("standard_1020")
    standard_montage.ch_names = [
        ch_name.upper() for ch_name in standard_montage.ch_names
    ]

    # Get the positions of the electrodes in the standard montage
    positions = standard_montage.get_positions()

    df = pd.DataFrame(positions["ch_pos"])[channel_names]

    df.set_index(pd.Series(["x", "y", "z"]))

    return df


if __name__ == "__main__":
    print(get_eeg_pos())


# EOF
