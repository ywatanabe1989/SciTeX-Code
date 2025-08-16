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

from .local.ScholarBrowserManager import ScholarBrowserManager
from .BrowserUtils import BrowserUtils
from .PlaywrightVision import PlaywrightVision
# from .remote._ZenRowsRemoteScholarBrowserManager import ZenRowsRemoteScholarBrowserManager
# from .remote._ZenRowsAPIBrowser import ZenRowsAPIBrowser

__all__ = [
    "ScholarBrowserManager",
    "BrowserUtils",
    "PlaywrightVision",
    # "ZenRowsRemoteScholarBrowserManager",
    # "ZenRowsAPIBrowser",
]

# EOF
