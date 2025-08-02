#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:20:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Download functionality for SciTeX Scholar."""

from ._BrowserDownloadHelper import BrowserDownloadHelper

__all__ = ["BrowserDownloadHelper"]

# EOF