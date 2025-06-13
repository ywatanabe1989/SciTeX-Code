#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 13:30:41 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_alternate_kwarg.py


def alternate_kwarg(kwargs, primary_key, alternate_key):
    alternate_value = kwargs.pop(alternate_key, None)
    kwargs[primary_key] = kwargs.get(primary_key) or alternate_value
    return kwargs


# EOF
