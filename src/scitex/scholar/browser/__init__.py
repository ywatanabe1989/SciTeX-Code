#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 17:03:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .local.ScholarBrowserManager import ScholarBrowserManager
# from .BrowserUtils import BrowserUtils
# from .PlaywrightVision import PlaywrightVision
from scitex.browser.interaction import (
    click_center_async,
    close_popups_async,
    PopupHandler,
)
from scitex.browser.pdf import (
    click_download_for_chrome_pdf_viewer_async,
    detect_chrome_pdf_viewer_async,
)
from scitex.browser.debugging import (
    show_grid_async,
    show_popup_and_capture_async,
)

# from .remote._ZenRowsRemoteScholarBrowserManager import ZenRowsRemoteScholarBrowserManager
# from .remote._ZenRowsAPIBrowser import ZenRowsAPIBrowser

__all__ = [
    "ScholarBrowserManager",
    # "BrowserUtils",
    # "PlaywrightVision",
    "click_center_async",
    "click_download_for_chrome_pdf_viewer_async",
    "close_popups_async",
    "detect_chrome_pdf_viewer_async",
    "PopupHandler",
    "show_grid_async",
    "show_popup_and_capture_async",
    # "ZenRowsRemoteScholarBrowserManager",
    # "ZenRowsAPIBrowser",
]

# EOF
