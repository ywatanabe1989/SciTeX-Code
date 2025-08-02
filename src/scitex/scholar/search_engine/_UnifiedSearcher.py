#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 17:56:55 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search_engine/_UnifiedSearcher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/search_engine/_UnifiedSearcher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Unified search functionality for SciTeX Scholar.

This module provides a unified interface to search across multiple sources
including PubMed, Semantic Scholar, arXiv, and local collections.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import logging

from ...errors import SearchError
from .._Paper import Paper
from ._BaseSearchEngine import BaseSearchEngine
from .local._LocalSearchEngine import LocalSearchEngine
from .local._VectorSearchEngine import VectorSearchEngine
from .web._ArxivSearchEngine import ArxivSearchEngine
from .web._CrossRefSearchEngine import CrossRefSearchEngine
from .web._GoogleScholarSearchEngine import GoogleScholarSearchEngine
from .web._PubMedSearchEngine import PubMedSearchEngine
from .web._SemanticScholarSearchEngine import SemanticScholarSearchEngine

logger = logging.getLogger(__name__)


class UnifiedSearcher:
    """
    Unified searcher that combines results from multiple engines.

    Attributes
    ----------
    email : str
        Email for API authentication
    semantic_scholar_api_key : str
        API key for Semantic Scholar
    crossref_api_key : str
        API key for CrossRef
    google_scholar_timeout : int
        Timeout for Google Scholar searches
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        email: Optional[str] = None,
        semantic_scholar_api_key: Optional[str] = None,
        crossref_api_key: Optional[str] = None,
        google_scholar_timeout: int = 10,
    ):
        """Initialize unified searcher with configuration.

        Args:
            config: ScholarConfig object (takes precedence over individual params)
            email: Email for API authentication (fallback)
            semantic_scholar_api_key: API key for Semantic Scholar (fallback)
            crossref_api_key: API key for CrossRef (fallback)
            google_scholar_timeout: Timeout for Google Scholar searches (fallback)
        """
        # Use config if provided, otherwise use individual params
        if config:
            self.email = getattr(config, "pubmed_email", email)
            self.semantic_scholar_api_key = getattr(
                config, "semantic_scholar_api_key", semantic_scholar_api_key
            )
            self.crossref_api_key = getattr(
                config, "crossref_api_key", crossref_api_key
            )
            self.google_scholar_timeout = getattr(
                config, "google_scholar_timeout", google_scholar_timeout
            )
        else:
            self.email = email
            self.semantic_scholar_api_key = semantic_scholar_api_key
            self.crossref_api_key = crossref_api_key
            self.google_scholar_timeout = google_scholar_timeout
        self._engines = {}  # Lazy-loaded engines

    @property
    def engines(self):
        """Get dictionary of available engines."""
        return self._engines

    def _get_engine(self, source: str) -> BaseSearchEngine:
        """Get or create engine for a source.

        Parameters
        ----------
        source : str
            Name of the search source

        Returns
        -------
        BaseSearchEngine
            The search engine instance

        Raises
        ------
        ValueError
            If source is not recognized
        """
        if source not in self._engines:
            if source == "semantic_scholar":
                self._engines[source] = SemanticScholarSearchEngine(
                    self.semantic_scholar_api_key
                )
            elif source == "pubmed":
                self._engines[source] = PubMedSearchEngine(self.email)
            elif source == "arxiv":
                self._engines[source] = ArxivSearchEngine()
            elif source == "google_scholar":
                self._engines[source] = GoogleScholarSearchEngine(
                    timeout=self.google_scholar_timeout
                )
            elif source == "crossref":
                self._engines[source] = CrossRefSearchEngine(
                    api_key=self.crossref_api_key, email=self.email
                )
            elif source == "local":
                self._engines[source] = LocalSearchEngine()
            elif source == "vector":
                self._engines[source] = VectorSearchEngine()
            else:
                raise ValueError(f"Unknown source: {source}")
        return self._engines[source]

    async def search_async(
        self,
        query: str,
        sources: List[str] = None,
        limit: int = 20,
        deduplicate: bool = True,
        **kwargs,
    ) -> List[Paper]:
        """
        Search across multiple sources and merge results.

        Parameters
        ----------
        query : str
            Search query
        sources : List[str], optional
            List of sources to search (default: ['pubmed'])
        limit : int
            Maximum results per source
        deduplicate : bool
            Remove duplicate papers
        **kwargs : dict
            Additional parameters for engines

        Returns
        -------
        List[Paper]
            Merged and ranked list of papers
        """
        if sources is None:
            sources = ["pubmed"]  # Default to PubMed only

        # Filter to valid sources
        valid_sources = [
            "pubmed",
            "semantic_scholar",
            "google_scholar",
            "crossref",
            "arxiv",
            "local",
            "vector",
        ]
        sources = [s for s in sources if s in valid_sources]

        if not sources:
            logger.warning("No valid search sources specified")
            return []

        # Search all sources concurrently
        tasks = []
        for source in sources:
            try:
                engine = self._get_engine(source)
                task = engine.search_async(query, limit, **kwargs)
                tasks.append(task)
            except Exception as e:
                logger.debug(f"Failed to initialize {source} engine: {e}")

        logger.debug(f"Searching {len(tasks)} sources: {sources}")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results
        all_papers = []
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                logger.debug(f"Search failed for {source}: {result}")
            else:
                logger.debug(f"{source} returned {len(result)} papers")
                all_papers.extend(result)

        # Deduplicate if requested
        if deduplicate:
            all_papers = self._deduplicate_papers(all_papers)

        # Sort by relevance (using citation count as proxy)
        all_papers.sort(key=lambda p: p.citation_count or 0, reverse=True)

        return all_papers[:limit]

    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """Remove duplicate papers based on similarity.

        Parameters
        ----------
        papers : List[Paper]
            List of papers to deduplicate

        Returns
        -------
        List[Paper]
            Deduplicated list of papers
        """
        if not papers:
            return []

        unique_papers = [papers[0]]

        for paper in papers[1:]:
            is_duplicate = False

            for unique_paper in unique_papers:
                if paper.similarity_score(unique_paper) > 0.85:
                    is_duplicate = True
                    # Keep the one with more information
                    if (paper.citation_count or 0) > (
                        unique_paper.citation_count or 0
                    ):
                        unique_papers.remove(unique_paper)
                        unique_papers.append(paper)
                    break

            if not is_duplicate:
                unique_papers.append(paper)

        return unique_papers

    def build_local_index(
        self, pdf_dirs: List[Union[str, Path]]
    ) -> Dict[str, Any]:
        """Build local search index.

        Parameters
        ----------
        pdf_dirs : List[Union[str, Path]]
            Directories containing PDFs

        Returns
        -------
        Dict[str, Any]
            Indexing statistics
        """
        pdf_dirs = [Path(d) for d in pdf_dirs]
        local_engine = self._get_engine("local")
        return local_engine.build_index(pdf_dirs)

    def add_to_vector_index(self, papers: List[Paper]) -> None:
        """Add papers to vector search index.

        Parameters
        ----------
        papers : List[Paper]
            Papers to add to the index
        """
        vector_engine = self._get_engine("vector")
        vector_engine.add_papers(papers)


# Convenience functions
async def search_async(
    query: str,
    sources: List[str] = None,
    limit: int = 20,
    email: Optional[str] = None,
    semantic_scholar_api_key: Optional[str] = None,
    **kwargs,
) -> List[Paper]:
    """
    Async convenience function for searching papers.

    Parameters
    ----------
    query : str
        Search query
    sources : List[str], optional
        Sources to search
    limit : int
        Maximum results
    email : str, optional
        Email for APIs
    semantic_scholar_api_key : str, optional
        API key for Semantic Scholar
    **kwargs : dict
        Additional search parameters

    Returns
    -------
    List[Paper]
        Search results
    """
    searcher = UnifiedSearcher(
        email=email, semantic_scholar_api_key=semantic_scholar_api_key
    )
    return await searcher.search_async(query, sources, limit, **kwargs)


def search_sync(
    query: str,
    sources: List[str] = None,
    limit: int = 20,
    email: Optional[str] = None,
    semantic_scholar_api_key: Optional[str] = None,
    **kwargs,
) -> List[Paper]:
    """
    Synchronous convenience function for searching papers.

    Parameters
    ----------
    query : str
        Search query
    sources : List[str], optional
        Sources to search
    limit : int
        Maximum results
    email : str, optional
        Email for APIs
    semantic_scholar_api_key : str, optional
        API key for Semantic Scholar
    **kwargs : dict
        Additional search parameters

    Returns
    -------
    List[Paper]
        Search results
    """
    return asyncio.run(
        search_async(
            query, sources, limit, email, semantic_scholar_api_key, **kwargs
        )
    )


def build_index(
    paths: List[Union[str, Path]], vector_index: bool = True
) -> Dict[str, Any]:
    """
    Build local search indices.

    Parameters
    ----------
    paths : List[Union[str, Path]]
        Directories containing PDFs
    vector_index : bool
        Also build vector similarity index

    Returns
    -------
    Dict[str, Any]
        Statistics about indexing
    """
    searcher = UnifiedSearcher()
    stats = searcher.build_local_index(paths)

    if vector_index:
        # Add papers to vector index
        local_engine = searcher._get_engine("local")
        papers = local_engine._search_sync("*", 9999, {})
        if papers:
            searcher.add_to_vector_index(papers)
            stats["vector_indexed"] = len(papers)

    return stats


# Export all classes and functions
__all__ = ["UnifiedSearcher", "search_async", "search_sync", "build_index"]

# EOF
