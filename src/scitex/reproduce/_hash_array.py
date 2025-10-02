#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-14 02:18:30 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/reproduce/_hash_array.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib

import numpy as np


def hash_array(array_data: np.ndarray) -> str:
    """Generate hash for ECoG data array."""
    data_bytes = array_data.tobytes()
    return hashlib.sha256(data_bytes).hexdigest()[:16]

# EOF
