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

"""Download functionality for SciTeX Scholar - Focused on paywalled content."""

# Core download components
from ._DirectPDFDownloader import DirectPDFDownloader, download_pdf_simple

# Legacy components (to be refactored)
try:
    from ._SmartPDFDownloader import SmartPDFDownloader
except ImportError:
    SmartPDFDownloader = None

try:
    from ._AuthenticatedBrowserStrategy import AuthenticatedBrowserStrategy
except ImportError:
    AuthenticatedBrowserStrategy = None

try:
    from ._BaseDownloadStrategy import BaseDownloadStrategy
except ImportError:
    BaseDownloadStrategy = None

try:
    from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner
except ImportError:
    ZoteroTranslatorRunner = None

__all__ = [
    "DirectPDFDownloader",
    "download_pdf_simple",
    "SmartPDFDownloader",
    "AuthenticatedBrowserStrategy",
    "BaseDownloadStrategy",
    "ZoteroTranslatorRunner"
]

# EOF