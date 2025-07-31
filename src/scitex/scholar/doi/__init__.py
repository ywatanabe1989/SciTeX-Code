#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 01:41:27 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""DOI resolution module for Scholar."""

from ._DOIResolver import DOIResolver
from ._resolve_dois import resolve_dois

__all__ = [
    "DOIResolver",
    "resolve_dois",
]

# EOF
