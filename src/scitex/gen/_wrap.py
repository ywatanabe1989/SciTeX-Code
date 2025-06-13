#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 02:13:22 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_wrap.py

import functools


def wrap(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# EOF
