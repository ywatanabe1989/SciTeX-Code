#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 00:53:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from ._OpenURLResolver import OpenURLResolver
from ._OpenURLResolverWithZenRows import OpenURLResolverWithZenRows
from ._ZenRowsOpenURLResolver import ZenRowsOpenURLResolver
from ._ResumableOpenURLResolver import ResumableOpenURLResolver

__all__ = [
    "OpenURLResolver",
    "OpenURLResolverWithZenRows",  # API-based ZenRows integration
    "ZenRowsOpenURLResolver",       # Browser-based ZenRows integration
    "ResumableOpenURLResolver",     # Resumable resolver with progress tracking
]

# EOF
