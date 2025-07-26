#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:03:00 (ywatanabe)"
# File: ./src/scitex/scholar/_exceptions.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_exceptions.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Custom exceptions for the Scholar module."""

"""Imports"""
from ..errors import ScholarError

"""Custom Exceptions"""
class AuthenticationError(ScholarError):
    """Raised when authentication fails."""
    pass

class DownloadError(ScholarError):
    """Raised when PDF download fails."""
    pass

class SearchError(ScholarError):
    """Raised when paper search fails."""
    pass

class EnrichmentError(ScholarError):
    """Raised when metadata enrichment fails."""
    pass

class ParseError(ScholarError):
    """Raised when PDF parsing fails."""
    pass

class ResolverError(ScholarError):
    """Raised when DOI/OpenURL resolution fails."""
    pass

# EOF