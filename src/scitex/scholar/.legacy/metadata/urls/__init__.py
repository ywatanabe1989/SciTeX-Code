#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-08 01:22:00 (assistant)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/urls/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URL Module - Unified URL handling for Scholar

Provides a single abstracted interface for all URL operations.
Internal functions (_finder, _resolver) are available but not exposed.
"""

# Import the main handler class
from ._handler import URLHandler

# Keep the existing URLMetadataHandler for backward compatibility
from ._URLMetadataHandler import (
    URLMetadataHandler,
    add_urls_to_paper,
    get_papers_for_download
)

__all__ = [
    # Main abstracted interface
    "URLHandler",

    # Backward compatibility
    "URLMetadataHandler",
    "add_urls_to_paper",
    "get_papers_for_download"
]

# EOF
