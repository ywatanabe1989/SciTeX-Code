#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:41:37 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_yaml.py

import yaml


def _load_yaml(lpath, **kwargs):
    """Load YAML file with optional key lowercasing.

    Extension validation is handled by load() function, not here.
    This allows loading files without extensions when ext='yaml' is specified.
    """
    lower = kwargs.pop("lower", False)
    with open(lpath) as f:
        obj = yaml.safe_load(f, **kwargs)

    if lower:
        obj = {k.lower(): v for k, v in obj.items()}
    return obj


# EOF
