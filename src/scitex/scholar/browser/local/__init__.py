#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 12:44:12 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .ScholarBrowserManager import ScholarBrowserManager
# from ._ChromeProfileManager import ChromeProfileManager
# from ._SeleniumScholarBrowserManager import SeleniumScholarBrowserManager
# from ._HybridScholarBrowserManager import HybridScholarBrowserManager

__all__ = [
    "ScholarBrowserManager",
    # "ZenRowsScholarBrowserManager",
    # "ChromeProfileManager",
    # "SeleniumScholarBrowserManager",
    # "HybridScholarBrowserManager"
]

# EOF
