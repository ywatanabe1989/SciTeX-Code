#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 09:16:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_wrap.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/decorators/_wrap.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


def wrap(func):
    """Basic function wrapper that preserves function metadata.
    Usage:
    @wrap
    def my_function(x):
        return x + 1
    # Or manually:
    def my_function(x):
        return x + 1
    wrapped_func = wrap(my_function)
    This wrapper is useful as a template for creating more complex decorators
    or when you want to ensure function metadata is preserved.
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Store reference to original function
    wrapper._original_func = func
    # Mark as a wrapper for detection
    wrapper._is_wrapper = True
    return wrapper


# EOF
