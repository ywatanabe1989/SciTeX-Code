#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 20:31:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_cache_disk.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/decorators/_cache_disk.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2024-11-07 06:08:45 (ywatanabe)"

import functools

from joblib import Memory as _Memory


def cache_disk(func):
    """Disk caching decorator that uses joblib.Memory.

    Usage:
        @cache_disk
        def expensive_function(x):
            return x ** 2
    """
    scitex_dir = os.getenv("SCITEX_DIR", "~/.scitex")
    cache_dir = os.path.join(scitex_dir, "cache", "functions")
    memory = _Memory(cache_dir, verbose=0)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cached_func = memory.cache(func)
        return cached_func(*args, **kwargs)

    return wrapper

# EOF
