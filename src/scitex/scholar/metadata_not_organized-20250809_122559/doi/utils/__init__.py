#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 08:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/utils/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/utils/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
DOI Resolution Utilities

This package provides utilities to enhance DOI resolution by:
1. Extracting DOIs from URL fields
2. Converting PubMed IDs to DOIs
3. Normalizing text encoding for better search accuracy

All utilities are designed to be pluggable, testable, and independent.
"""

from .url_doi_extractor import URLDOISource
from .pubmed_converter import PubMedConverter
from .text_normalizer import TextNormalizer

__all__ = [
    "URLDOISource",
    "PubMedConverter",
    "TextNormalizer",
]

# Convenience function for quick access
def create_doi_utilities(
    ascii_fallback: bool = False,
    email: str = None,
    api_key: str = None
) -> tuple[URLDOISource, PubMedConverter, TextNormalizer]:
    """
    Create all DOI utilities with consistent configuration.

    Args:
        ascii_fallback: Enable ASCII fallback for text normalization
        email: Email for PubMed API requests
        api_key: API key for PubMed (optional)

    Returns:
        Tuple of (URLDOISource, PubMedConverter, TextNormalizer)
    """
    url_doi_source = URLDOISource()
    pubmed_converter = PubMedConverter(email=email, api_key=api_key)
    text_normalizer = TextNormalizer(ascii_fallback=ascii_fallback)

    return url_doi_source, pubmed_converter, text_normalizer

# Convenience function for creating just a text normalizer with title matching
def create_text_normalizer(ascii_fallback: bool = False) -> TextNormalizer:
    """
    Create a TextNormalizer for title matching and text processing.

    Args:
        ascii_fallback: Enable ASCII fallback for text normalization

    Returns:
        Configured TextNormalizer instance
    """
    return TextNormalizer(ascii_fallback=ascii_fallback)


# EOF
