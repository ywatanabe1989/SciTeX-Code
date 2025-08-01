#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Database module for organizing research papers."""

from ._PaperDatabase import PaperDatabase
from ._DatabaseEntry import DatabaseEntry
from ._DatabaseIndex import DatabaseIndex
from ._ScholarDatabaseIntegration import ScholarDatabaseIntegration

__all__ = [
    "PaperDatabase",
    "DatabaseEntry",
    "DatabaseIndex",
    "ScholarDatabaseIntegration",
]


# EOF