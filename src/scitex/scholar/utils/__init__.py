#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scholar utilities - Organized by function.

Structure:
- text/: Text processing utilities (TextNormalizer)
- bibtex/: BibTeX parsing utilities
- cleanup/: Maintenance and cleanup scripts

For backward compatibility, TextNormalizer is re-exported at top level.
"""

from .text import TextNormalizer
from .bibtex import parse_bibtex

__all__ = [
    "TextNormalizer",  # Most commonly used
    "parse_bibtex",
]

# EOF
