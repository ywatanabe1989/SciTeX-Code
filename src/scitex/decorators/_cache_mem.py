#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 05:52:33 (ywatanabe)"
# File: ./scitex_repo/src/scitex/decorators/_cache_mem.py

from functools import lru_cache as _lru_cache

# Memory cache
cache_mem = _lru_cache(maxsize=None)


# EOF
