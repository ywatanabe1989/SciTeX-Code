#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 13:19:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search_engine/_BaseSearchEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/search_engine/_BaseSearchEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Base search engine abstract class for SciTeX Scholar.

This module provides the abstract base class that all search engines
must inherit from to ensure consistent interface across different sources.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional

from scitex.scholar.core import Paper


class BaseSearchEngine(ABC):
    """Abstract base class for all search engines in SciTeX Scholar."""

    def __init__(self, name: str, rate_limit: float = 0.1):
        """Initialize base search engine.

        Parameters
        ----------
        name : str
            Name of the search engine (e.g., 'pubmed', 'arxiv')
        rate_limit : float
            Minimum seconds between API requests
        """
        self.name = name
        self.rate_limit = rate_limit
        self._last_request = 0

    @abstractmethod
    async def search_async(
        self, query: str, limit: int = 20, **kwargs
    ) -> List[Paper]:
        """Search for papers asynchronously.

        Parameters
        ----------
        query : str
            Search query string
        limit : int
            Maximum number of results to return
        **kwargs : dict
            Additional search parameters (e.g., year_min, year_max)

        Returns
        -------
        List[Paper]
            List of Paper objects matching the search criteria

        Raises
        ------
        SearchError
            If the search fails
        """
        pass

    @abstractmethod
    async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
        """Fetch single paper by ID (DOI, PMID, etc)."""
        pass

    @abstractmethod
    async def get_citation_count_async(self, doi: str) -> Optional[int]:
        """Get citation count for DOI."""
        pass

    @abstractmethod
    async def resolve_doi_async(
        self, title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """Resolve title to DOI."""
        pass

    async def _rate_limit_async(self):
        """Enforce rate limiting between API requests."""
        import time

        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()

    def __repr__(self) -> str:
        """String representation of the search engine."""
        return f"{self.__class__.__name__}(name='{self.name}', rate_limit={self.rate_limit})"

# EOF
