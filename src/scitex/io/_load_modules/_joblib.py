#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:39 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_joblib.py

from typing import Any

import joblib


def _load_joblib(lpath: str, **kwargs) -> Any:
    """Load joblib file."""
    if not lpath.endswith(".joblib"):
        raise ValueError("File must have .joblib extension")
    with open(lpath, "rb") as f:
        return joblib.load(f, **kwargs)


# EOF
