#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/decorators/_preserve_doc.py

from functools import wraps


def preserve_doc(loader_func):
    """Wrap the loader functions to preserve their docstrings"""

    @wraps(loader_func)
    def wrapper(*args, **kwargs):
        return loader_func(*args, **kwargs)

    return wrapper


# EOF
