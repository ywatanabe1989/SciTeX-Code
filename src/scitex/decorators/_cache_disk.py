#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 06:08:45 (ywatanabe)"
# File: ./scitex_repo/src/scitex/decorators/_cache_disk.py

import functools
import os

from joblib import Memory as _Memory


def cache_disk(func):
    """Disk caching decorator that uses joblib.Memory.

    Usage:
        @cache_disk
        def expensive_function(x):
            return x ** 2
    """
    scitex_dir = os.getenv("SciTeX_DIR", "~/.cache/scitex/")
    cache_dir = scitex_dir + "cache/"
    memory = _Memory(cache_dir, verbose=0)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cached_func = memory.cache(func)
        return cached_func(*args, **kwargs)

    return wrapper


# EOF
