#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar storage module - Library and paper storage management.

Public API (actively used):
- LibraryManager: Low-level library operations
- ScholarLibrary: High-level library operations
- BibTeXHandler: BibTeX import/export and bibliography management
- PaperIO: Individual paper I/O operations

Internal (not for external use):
- _LibraryCacheManager: Used by ScholarLibrary
- _DeduplicationManager: Used by LibraryManager
"""

from ._LibraryManager import LibraryManager
from ._LibraryCacheManager import LibraryCacheManager
from .ScholarLibrary import ScholarLibrary
from .BibTeXHandler import BibTeXHandler
from .PaperIO import PaperIO

__all__ = [
    "LibraryManager",
    "ScholarLibrary",
    "BibTeXHandler",
    "PaperIO",
]
