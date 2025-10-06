#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 04:06:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search_engine/web/_SemanticScholarSearchEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Semantic Scholar search engine implementation for SciTeX Scholar.

This module provides search functionality through the Semantic Scholar API,
offering access to a large corpus of academic papers with citation information.
"""

from typing import Any, Dict, List, Optional

import aiohttp

from scitex import logging

from scitex.errors import SearchError
from scitex.scholar.core import Paper
from scitex.scholar.config import ScholarConfig
from .._BaseSearchEngine import BaseSearchEngine

logger = logging.getLogger(__name__)


class SemanticScholarSearchEngine(BaseSearchEngine):
    """Semantic Scholar search engine using their Graph API."""

    def __init__(
        self,
        config: Optional[ScholarConfig] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize Semantic Scholar search engine.

        Parameters
        ----------
        config : ScholarConfig, optional
            Scholar configuration object
        api_key : str, optional
            API key for Semantic Scholar (enables higher rate limits)
            Uses sophisticated config resolution: direct → config → env → default
        """
        self.config = config or ScholarConfig()

        # Use sophisticated config resolution: direct → config → env → default
        self.api_key = self.config.resolve(
            key="semantic_scholar_api_key",
            direct_val=api_key,
            default=None,
            type=str,
        )

        # Faster rate limit with API key
        rate_limit = 0.1 if self.api_key else 1.0
        super().__init__(name="semantic_scholar", rate_limit=rate_limit)

        self.base_url = "https://api.semanticscholar.org/graph/v1"

    async def search_async(
        self, query: str, limit: int = 20, **kwargs
    ) -> List[Paper]:
        """Search Semantic Scholar for papers.

        Parameters
        ----------
        query : str
            Search query (can include special prefixes like 'CorpusId:')
        limit : int
            Maximum number of results
        **kwargs : dict
            Additional parameters (year_min, year_max)

        Returns
        -------
        List[Paper]
            List of papers from Semantic Scholar
        """
        await self._rate_limit_async()

        # Check if query is for a specific paper ID
        if query.startswith("CorpusId:"):
            corpus_id = query.replace("CorpusId:", "").strip()
            paper = await self._fetch_paper_by_id_async(
                f"CorpusId:{corpus_id}"
            )
            return [paper] if paper else []

        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": "title,authors,abstract,year,citationCount,journal,paperId,venue,fieldsOfStudy,isOpenAccess,url,tldr,doi,externalIds",
        }

        # Add year filters if provided
        if "year_min" in kwargs:
            params["year"] = f"{kwargs['year_min']}-"
        if "year_max" in kwargs:
            if "year" in params:
                params["year"] = f"{kwargs['year_min']}-{kwargs['year_max']}"
            else:
                params["year"] = f"-{kwargs['year_max']}"

        papers = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/paper/search",
                    params=params,
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for item in data.get("data", []):
                            paper = self._parse_paper(item)
                            if paper:
                                papers.append(paper)
                    else:
                        error_msg = await response.text()

                        if response.status == 429:
                            # Rate limiting
                            logger.warning(
                                "Semantic Scholar rate limit reached"
                            )
                            raise SearchError(
                                query=query,
                                source="semantic_scholar",
                                reason="Rate limit reached. Please wait 1-2 seconds between searches or get a free API key.",
                            )
                        else:
                            logger.debug(
                                f"Semantic Scholar API returned {response.status}: {error_msg}"
                            )
                            return []

        except SearchError:
            raise
        except Exception as e:
            logger.debug(f"Semantic Scholar search error: {e}")
            return []

        return papers

    async def _fetch_paper_by_id_async(self, paper_id: str) -> Optional[Paper]:
        """Fetch a specific paper by its ID.

        Parameters
        ----------
        paper_id : str
            Paper ID (CorpusId, DOI, arXiv ID, etc.)

        Returns
        -------
        Optional[Paper]
            Paper object if found, None otherwise
        """
        await self._rate_limit_async()

        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        url = f"{self.base_url}/paper/{paper_id}"
        params = {
            "fields": "title,authors,abstract,year,citationCount,journal,paperId,venue,fieldsOfStudy,isOpenAccess,url,tldr,externalIds"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_paper(data)
                    else:
                        logger.debug(
                            f"Failed to fetch paper {paper_id}: {response.status}"
                        )
                        return None

        except Exception as e:
            logger.debug(f"Error fetching paper {paper_id}: {e}")
            return None

    def _parse_paper(self, data: Dict[str, Any]) -> Optional[Paper]:
        """Parse Semantic Scholar paper data into a Paper object.

        Parameters
        ----------
        data : dict
            Paper data from Semantic Scholar API

        Returns
        -------
        Optional[Paper]
            Parsed Paper object or None if parsing fails
        """
        if not data or not isinstance(data, dict):
            logger.warning("Received invalid data for Semantic Scholar paper")
            return None

        try:
            # Extract authors
            authors = []
            for author_data in data.get("authors", []):
                name = author_data.get("name", "")
                if name:
                    authors.append(name)

            # Get PDF URL if available
            pdf_url = None
            if data.get("isOpenAccess"):
                pdf_url = data.get("url")

            # Extract journal/venue
            journal_data = data.get("journal")
            journal = ""
            if journal_data and isinstance(journal_data, dict):
                journal = journal_data.get("name", "")
            if not journal:
                journal = data.get("venue", "")

            # Extract DOI from externalIds if not directly available
            doi = data.get("doi")
            if not doi and data.get("externalIds"):
                doi = data.get("externalIds", {}).get("DOI")

            # Get abstract or TLDR if abstract is missing
            abstract = data.get("abstract", "")
            if not abstract and data.get("tldr"):
                tldr = data.get("tldr", {})
                if isinstance(tldr, dict):
                    abstract = tldr.get("text", "")

            # Create paper
            paper = Paper(
                title=data.get("title", ""),
                authors=authors,
                abstract=abstract,
                source="semantic_scholar",
                year=data.get("year"),
                doi=doi,
                journal=journal,
                keywords=data.get("fieldsOfStudy", []),
                citation_count=data.get("citationCount", 0),
                pdf_url=pdf_url,
                metadata={
                    "semantic_scholar_paper_id": data.get("paperId"),
                    "fields_of_study": data.get("fieldsOfStudy", []),
                    "is_open_access": data.get("isOpenAccess", False),
                    "citation_count_source": (
                        "Semantic Scholar"
                        if data.get("citationCount") is not None
                        else None
                    ),
                    "external_ids": data.get("externalIds", {}),
                    "venue": data.get("venue", ""),
                    "tldr": data.get("tldr", {}),
                },
            )

            return paper

        except Exception as e:
            logger.warning(f"Failed to parse Semantic Scholar paper: {e}")
            return None

    async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
        """Fetch single paper by ID from Semantic Scholar."""
        # Use the existing _fetch_paper_by_id_async method
        return await self._fetch_paper_by_id_async(identifier)

    async def get_citation_count_async(self, doi: str) -> Optional[int]:
        """Get citation count for DOI from Semantic Scholar."""
        try:
            # Fetch the paper by DOI
            paper = await self.fetch_by_id_async(doi)
            return paper.citation_count if paper else None

        except Exception as e:
            logger.error(f"Error getting citation count for {doi}: {e}")
            return None

    async def resolve_doi_async(
        self, title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """Resolve title to DOI using Semantic Scholar search."""
        try:
            # Search for the paper by title
            search_query = title
            if year:
                search_query += f" {year}"

            papers = await self.search_async(search_query, limit=5)

            # Look for exact or close title matches
            title_lower = title.lower().strip()
            for paper in papers:
                if paper.doi and paper.title:
                    paper_title_lower = paper.title.lower().strip()
                    # Simple matching - could be improved with fuzzy matching
                    if (
                        title_lower in paper_title_lower
                        or paper_title_lower in title_lower
                    ):
                        # If year is specified, prefer papers from that year
                        if year and paper.year and abs(paper.year - year) <= 1:
                            return paper.doi
                        elif not year:
                            return paper.doi

            # If no exact match but we have results with DOI, return the first DOI
            for paper in papers:
                if paper.doi:
                    return paper.doi

            return None

        except Exception as e:
            logger.error(f"Error resolving DOI for title '{title}': {e}")
            return None


async def main():
    """Test function for SemanticScholarSearchEngine."""
    from scitex.scholar.config import ScholarConfig

    config = ScholarConfig()
    engine = SemanticScholarSearchEngine(config=config)

    print("Testing Semantic Scholar search engine...")
    print(f"API Key: {'Set' if engine.api_key else 'Not set'}")
    print(f"Rate limit: {engine.rate_limit}s")

    try:
        papers = await engine.search_async("neural networks", limit=5)
        print(f"Found {len(papers)} papers:")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}")
            print(f"   Citations: {paper.citation_count}")
            print(f"   DOI: {paper.doi}")
            print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

# EOF
