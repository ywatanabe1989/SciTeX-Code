#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:03:00 (ywatanabe)"
# File: ./src/scitex/scholar/download/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/download/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Download module for Scholar."""

# Import download components
from ._PDFDownloader import PDFDownloader
from ._BaseDownloadStrategy import BaseDownloadStrategy
from ._DirectDownloadStrategy import DirectDownloadStrategy
from ._SciHubDownloadStrategy import SciHubDownloadStrategy
from ._BrowserDownloadStrategy import BrowserDownloadStrategy

__all__ = [
    "PDFDownloader",
    "BaseDownloadStrategy",
    "DirectDownloadStrategy",
    "SciHubDownloadStrategy",
    "BrowserDownloadStrategy"
]

# EOF