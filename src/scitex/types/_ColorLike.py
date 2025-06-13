#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 17:09:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/types/_ColorLike.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/types/_ColorLike.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from typing import List, Tuple, Union

# Define ColorLike type
ColorLike = Union[
    str,
    Tuple[float, float, float],
    Tuple[float, float, float, float],
    List[float],
]

# EOF
