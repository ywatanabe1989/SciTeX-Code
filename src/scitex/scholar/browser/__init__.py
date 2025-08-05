#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 17:03:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .local._BrowserManager import BrowserManager
# from .remote._ZenRowsRemoteBrowserManager import ZenRowsRemoteBrowserManager
# from .remote._ZenRowsAPIBrowser import ZenRowsAPIBrowser

__all__ = [
    "BrowserManager",
    # "ZenRowsRemoteBrowserManager",
    # "ZenRowsAPIBrowser",
]

# EOF
