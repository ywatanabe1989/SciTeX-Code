#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 02:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""PDF download functionality for SciTeX Scholar.

This module provides comprehensive PDF download capabilities with multiple
strategies including direct downloads, Zotero translators, browser automation,
and anti-bot bypass techniques.
"""

from ._PDFDownloader import PDFDownloader
from ._BaseDownloadStrategy import BaseDownloadStrategy
from ._BrowserDownloadStrategy import BrowserBasedDownloader
from ._ZenRowsDownloadStrategy import ZenRowsDownloadStrategy
from ._PDFDiscoveryEngine import PDFDiscoveryEngine
from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner

__all__ = [
    "PDFDownloader",
    "BaseDownloadStrategy",
    "BrowserBasedDownloader", 
    "ZenRowsDownloadStrategy",
    "PDFDiscoveryEngine",
    "ZoteroTranslatorRunner",
]

# EOF