#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 20:30:56 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_cache_disk_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/decorators/_cache_disk_async.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Async disk caching decorator using joblib.Memory."""

import asyncio
import functools

from joblib import Memory as _Memory


def cache_disk_async(func):
    """Disk caching decorator for async functions.

    Usage:
        @cache_disk_async
        async def expensive_async_function(x):
            await asyncio.sleep(1)
            return x ** 2
    """
    scitex_dir = os.getenv("SCITEX_DIR", os.path.expanduser("~/.scitex"))
    cache_dir = os.path.join(scitex_dir, "cache", "functions")
    memory = _Memory(cache_dir, verbose=0)

    # Create sync wrapper for joblib
    def sync_wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    cached_sync = memory.cache(sync_wrapper)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Run cached sync version in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: cached_sync(*args, **kwargs))
        return result

    return async_wrapper

# EOF
