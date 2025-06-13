#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:51:45 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_con.py

from typing import Any

import mne


def _load_con(lpath: str, **kwargs) -> Any:
    if not lpath.endswith(".con"):
        raise ValueError("File must have .con extension")
    obj = mne.io.read_raw_fif(lpath, preload=True, **kwargs)
    obj = obj.to_data_frame()
    obj["samp_rate"] = obj.info["sfreq"]
    return obj


# EOF
