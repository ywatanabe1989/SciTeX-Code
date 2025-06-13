#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:40 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_json.py

import json
from typing import Any


def _load_json(lpath: str, **kwargs) -> Any:
    """Load JSON file."""
    if not lpath.endswith(".json"):
        raise ValueError("File must have .json extension")
    with open(lpath, "r") as f:
        return json.load(f)


# EOF
