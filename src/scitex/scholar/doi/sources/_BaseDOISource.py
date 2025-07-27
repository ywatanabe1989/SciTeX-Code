#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 15:45:00 (ywatanabe)"
# File: ./src/scitex/scholar/core/_doi_sources/_BaseDOISource.py
# ----------------------------------------
from __future__ import annotations

"""
Abstract base class for DOI sources.

This module defines the interface that all DOI sources must implement.
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional

class BaseDOISource(ABC):
    """Abstract base class for DOI sources."""

    @abstractmethod
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search for DOI by title."""
        pass

    @abstractmethod
    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract by DOI."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Source name for logging."""
        pass

    @property
    def rate_limit_delay(self) -> float:
        """Delay between requests in seconds."""
        return 0.5

    def extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI from URL if present."""
        if not url:
            return None

        # Direct DOI URLs
        if "doi.org/" in url:
            match = re.search(r"doi\.org/(.+?)(?:\?|$|#)", url)
            if match:
                return match.group(1).strip()

        # DOI pattern in URL
        doi_pattern = r"10\.\d{4,}/[-._;()/:\w]+"
        match = re.search(doi_pattern, url)
        if match:
            return match.group(0)

        return None

    def _is_title_match(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two titles match."""
        # Normalize titles
        def normalize(s: str) -> str:
            import string
            s = s.lower()
            # Remove punctuation
            translator = str.maketrans('', '', string.punctuation)
            s = s.translate(translator)
            # Remove extra whitespace
            s = ' '.join(s.split())
            return s
        
        t1 = normalize(title1)
        t2 = normalize(title2)
        
        # Exact match
        if t1 == t2:
            return True
            
        # Calculate simple similarity
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return False
            
        intersection = words1 & words2
        union = words1 | words2
        
        jaccard = len(intersection) / len(union)
        return jaccard >= threshold

# EOF