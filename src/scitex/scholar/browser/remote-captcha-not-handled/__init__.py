#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 22:34:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/remote/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/remote/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Remote browser managers for ZenRows services

from ._ZenRowsRemoteBrowserManager import ZenRowsRemoteBrowserManager

__all__ = ["ZenRowsRemoteBrowserManager"]

# EOF
