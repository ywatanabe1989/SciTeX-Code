#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:03:00 (ywatanabe)"
# File: ./src/scitex/scholar/core/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/core/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Core components module for Scholar."""

# Import core components
from ._MetadataEnricher import MetadataEnricher
from ._PDFParser import PDFParser
from ._DOIResolver import DOIResolver
from ._OpenURLResolver import OpenURLResolver

__all__ = [
    "MetadataEnricher",
    "PDFParser",
    "DOIResolver",
    "OpenURLResolver"
]

# EOF