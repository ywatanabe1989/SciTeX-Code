#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 12:45:25 (ywatanabe)"
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
# from .local._ZenRowsBrowserManager import ZenRowsBrowserManager
# from .local._ChromeExtensionManager import ChromeExtensionManager
# from .local._SeleniumBrowserManager import SeleniumBrowserManager
# from .local._HybridBrowserManager import HybridBrowserManager
from .remote._ZenRowsRemoteBrowserManager import ZenRowsRemoteBrowserManager
from .remote._ZenRowsAPIBrowser import ZenRowsAPIBrowser

__all__ = [
    "BrowserManager",
    # "ZenRowsBrowserManager",
    # "ChromeExtensionManager",
    # "SeleniumBrowserManager",
    # "HybridBrowserManager",
    "ZenRowsRemoteBrowserManager",
    "ZenRowsAPIBrowser",
]

# EOF
