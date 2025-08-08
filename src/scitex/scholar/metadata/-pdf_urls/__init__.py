#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-08 00:55:00 (assistant)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/pdf_urls/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/pdf_urls/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""PDF URL extraction using Zotero translators."""

from ._PDFUrlExtractor import PDFUrlExtractor, extract_pdf_urls

__all__ = [
    "PDFUrlExtractor",
    "extract_pdf_urls"
]

# EOF