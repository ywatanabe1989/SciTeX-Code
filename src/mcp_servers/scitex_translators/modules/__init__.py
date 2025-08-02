#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:48:00"
# File: __init__.py

"""Module-specific translators."""

# Import available translators
try:
    from .io_translator import IOTranslator
except ImportError:
    IOTranslator = None

try:
    from .plt_translator import PLTTranslator
except ImportError:
    PLTTranslator = None

try:
    from .ai_translator import AITranslator
except ImportError:
    AITranslator = None

try:
    from .gen_translator import GenTranslator
except ImportError:
    GenTranslator = None

# Module application order (most specific to most general)
MODULE_ORDER = [
    "ai",      # Most specific - AI/ML operations
    "plt",     # Plotting operations
    "io",      # I/O operations
    "gen",     # General utilities (most general)
]

__all__ = ["IOTranslator", "PLTTranslator", "AITranslator", "GenTranslator", "MODULE_ORDER"]