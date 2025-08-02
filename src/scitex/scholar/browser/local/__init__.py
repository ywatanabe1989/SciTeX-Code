#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 12:44:12 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from ._BrowserManager import BrowserManager
# from ._ChromeExtensionManager import ChromeExtensionManager
# from ._SeleniumBrowserManager import SeleniumBrowserManager
# from ._HybridBrowserManager import HybridBrowserManager

__all__ = [
    "BrowserManager",
    # "ZenRowsBrowserManager",
    # "ChromeExtensionManager",
    # "SeleniumBrowserManager",
    # "HybridBrowserManager"
]

# EOF
