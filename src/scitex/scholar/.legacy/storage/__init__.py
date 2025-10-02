#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Storage functionality for SciTeX Scholar."""

from ._EnhancedStorageManager import EnhancedStorageManager

__all__ = ["EnhancedStorageManager"]

# EOF