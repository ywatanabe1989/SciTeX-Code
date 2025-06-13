#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 19:54:02 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_getsize.py

import os

import numpy as np


def getsize(path):
    if os.path.exists(path):
        return os.path.getsize(path)
    else:
        return np.nan


# EOF
