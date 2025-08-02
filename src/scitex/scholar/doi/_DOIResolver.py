#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 18:40:35 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/_DOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/_DOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any

"""
Clean, optimized DOI resolver with pluggable sources.

This module orchestrates DOI resolution across multiple sources
(CrossRef, PubMed, OpenAlex, Semantic Scholar).
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Dict, List, Optional, Type

import requests
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential
from tqdm import tqdm

from scitex import logging

from .sources import (
    ArXivSource,
    BaseDOISource,
    CrossRefSource,
    OpenAlexSource,
    PubMedSource,
    SemanticScholarSource,
)

logger = logging.getLogger(__name__)


class DOIResolver:
    """Clean, optimized DOI resolver with configurable sources."""

    # Default source order (based on rate limits and reliability)
    DEFAULT_SOURCES = ["crossref", "semantic_scholar", "pubmed", "openalex"]

    # Source registry
    SOURCE_CLASSES: Dict[str, Type[BaseDOISource]] = {
        "crossref": CrossRefSource,
        "pubmed": PubMedSource,
        "openalex": OpenAlexSource,
        "semantic_scholar": SemanticScholarSource,
        "arxiv": ArXivSource,
    }

    def __init__(
        self,
        email_crossref: str = os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL"),
        email_pubmed: str = os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL"),
        email_openalex: str = os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL"),
        email_semantic_scholar: str = os.getenv(
            "SCITEX_SCHOLAR_CROSSREF_EMAIL"
        ),
        email_arxiv: str = os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL"),
        sources: Optional[List[str]] = None,
        config: Optional[Any] = None,
    ):
        """Initialize resolver with specified sources.

        Args:
            email_crossref: Email for CrossRef API
            email_pubmed: Email for PubMed API
            email_openalex: Email for OpenAlex API
            email_semantic_scholar: Email for Semantic Scholar API
            email_arxiv: Email for ArXiv API
            sources: List of source names to use (default: all available)
            config: ScholarConfig object
        """
        if config is None:
            from ..config import ScholarConfig

            config = ScholarConfig()

        self.config = config

        # Direct params override config
        self.email_crossref = config.resolve(
            "crossref_email", email_crossref, "research@example.com"
        )
        self.email_pubmed = config.resolve(
            "pubmed_email", email_pubmed, "research@example.com"
        )
        self.email_openalex = config.resolve(
            "openalex_email", email_openalex, "research@example.com"
        )
        self.email_semantic_scholar = config.resolve(
            "semantic_scholar_email", email_semantic_scholar, "research@example.com"
        )
        self.email_arxiv = config.resolve(
            "arxiv_email", email_arxiv, "research@example.com"
        )

        # Default fallback
        default_email = "research@example.com"

        self.sources = sources or self.DEFAULT_SOURCES
        self._source_instances: Dict[str, BaseDOISource] = {}

    def _get_source(self, name: str) -> Optional[BaseDOISource]:
        """Get or create source instance."""
        if name not in self._source_instances:
            source_class = self.SOURCE_CLASSES.get(name)
            if source_class:
                # Get appropriate email for each source
                email_map = {
                    "crossref": self.email_crossref,
                    "pubmed": self.email_pubmed,
                    "openalex": self.email_openalex,
                    "semantic_scholar": self.email_semantic_scholar,
                    "arxiv": self.email_arxiv,
                }
                email = email_map.get(name, "research@example.com")
                self._source_instances[name] = source_class(email)
        return self._source_instances.get(name)

    # @lru_cache(maxsize=1000)
    # def title_to_doi(
    #     self,
    #     title: str,
    #     year: Optional[int] = None,
    #     authors: Optional[tuple] = None,  # Tuple for hashability
    #     sources: Optional[tuple] = None,  # Tuple for hashability
    # ) -> Optional[str]:
    #     """
    #     Resolve DOI from title with caching.

    #     Args:
    #         title: Paper title
    #         year: Publication year (optional)
    #         authors: Author list as tuple (optional)
    #         sources: Specific sources to use as tuple (optional)

    #     Returns:
    #         DOI if found, None otherwise
    #     """
    #     if not title:
    #         return None

    #     # Normalize inputs
    #     authors_list = list(authors) if authors else None
    #     sources_list = list(sources) if sources else self.sources

    #     # Try each source
    #     for source_name in sources_list:
    #         source = self._get_source(source_name)
    #         if not source:
    #             continue

    #         try:
    #             doi = source.search(title, year, authors_list)
    #             if doi:
    #                 logger.info(f"Found DOI via {source.name}: {doi}")
    #                 return doi

    #             # Rate limit
    #             time.sleep(source.rate_limit_delay)

    #         except Exception as e:
    #             logger.warning(
    #                 f"Error searching {source_name}: {e}", exc_info=True
    #             )

    #     return None

    async def title_to_doi_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Resolve DOI from title - tries sources sequentially, stops after first success.

        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)
            sources: Specific sources to use (optional)

        Returns:
            DOI if found, None otherwise
        """
        if not title:
            return None

        sources_list = sources or self.sources

        # Try sources sequentially - stop after first success
        for source_name in sources_list:
            source = self._get_source(source_name)
            if not source:
                continue

            try:
                # Try this source
                doi = await self._search_source_async(
                    source, title, year, authors
                )

                if doi:
                    # Success! Return immediately, no need to try other sources
                    return {"doi": doi, "source": source_name}

            except Exception as e:
                logger.debug(f"Error searching {source_name}: {e}")
                continue

            # Small delay between sources to be polite
            await asyncio.sleep(1.0)  # 1 second between sources

        return None

    # async def _search_source_async(
    #     self,
    #     source: BaseDOISource,
    #     title: str,
    #     year: Optional[int] = None,
    #     authors: Optional[List[str]] = None,
    # ) -> Optional[str]:
    #     """Search single source asynchronously."""
    #     try:
    #         # Run blocking call in thread pool
    #         loop = asyncio.get_event_loop()
    #         doi = await loop.run_in_executor(
    #             None, source.search, title, year, authors
    #         )
    #         if doi:
    #             logger.info(f"Found DOI via {source.name}: {doi}")
    #         return doi
    #     except Exception as e:
    #         logger.debug(f"Error searching {source.name}: {e}")
    #         return None

    async def _search_source_async(
        self,
        source: BaseDOISource,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search single source asynchronously - sources handle their own retries."""
        try:
            loop = asyncio.get_event_loop()
            doi = await loop.run_in_executor(
                None, source.search, title, year, authors
            )

            if doi:
                logger.info(f"Found DOI via {source.name}: {doi}")
                return doi
            else:
                logger.debug(f"No DOI found via {source.name}")
                return None

        except Exception as e:
            logger.debug(f"Error searching {source.name}: {e}")
            return None

    # @lru_cache(maxsize=1000)
    # def title_to_doi(
    #     self,
    #     title: str,
    #     year: Optional[int] = None,
    #     authors: Optional[tuple] = None,
    #     sources: Optional[tuple] = None,
    # ) -> Optional[str]:
    #     """Sync wrapper for async DOI resolution with caching."""
    #     # Convert tuples back to lists
    #     authors_list = list(authors) if authors else None
    #     sources_list = list(sources) if sources else None

    #     # Create new event loop if needed
    #     try:
    #         loop = asyncio.get_event_loop()
    #     except RuntimeError:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)

    #     # Run async version
    #     return loop.run_until_complete(
    #         self.title_to_doi_async(title, year, authors_list, sources_list)
    #     )

    def title_to_doi(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Sync wrapper for async DOI resolution."""
        if not title:
            return None

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.title_to_doi_async(title, year, authors, sources)
        )

    # def get_abstract(
    #     self, doi: str, sources: Optional[List[str]] = None
    # ) -> Optional[str]:
    #     """
    #     Get abstract by DOI from configured sources.

    #     Args:
    #         doi: DOI to look up
    #         sources: Specific sources to use (optional)

    #     Returns:
    #         Abstract text if found, None otherwise
    #     """
    #     if not doi:
    #         return None

    #     sources_to_try = sources or self.sources

    #     for source_name in sources_to_try:
    #         source = self._get_source(source_name)
    #         if not source:
    #             continue

    #         try:
    #             abstract = source.get_abstract(doi)
    #             if abstract:
    #                 logger.info(f"Found abstract via {source.name}")
    #                 return abstract

    #             # Rate limit
    #             time.sleep(source.rate_limit_delay)

    #         except Exception as e:
    #             logger.warning(
    #                 f"Error getting abstract from {source_name}: {e}",
    #                 exc_info=True,
    #             )

    #     return None
    def get_abstract(
        self, doi: str, sources: Optional[List[str]] = None
    ) -> Optional[str]:
        """Get abstract by DOI from configured sources."""
        if not doi:
            return None

        sources_to_try = sources or self.sources
        for source_name in sources_to_try:
            source = self._get_source(source_name)
            if not source:
                continue

            try:
                abstract = source.get_abstract(doi)
                if abstract:
                    logger.info(f"Found abstract via {source.name}")
                    return abstract
                time.sleep(source.rate_limit_delay)
            except requests.HTTPError as exc:
                if exc.response and exc.response.status_code == 429:
                    logger.warning(
                        f"Rate limit hit for {source_name}. Consider adding API key or waiting between requests."
                    )
                else:
                    logger.debug(
                        f"HTTP error getting abstract from {source_name}: {exc}"
                    )
                continue
            except Exception as exc:
                logger.debug(
                    f"Error getting abstract from {source_name}: {exc}"
                )
                continue

        return None

    def batch_resolve(
        self,
        titles: List[str],
        years: Optional[List[Optional[int]]] = None,
        max_workers: int = 4,
        show_progress: bool = True,
    ) -> Dict[str, Optional[str]]:
        """
        Batch resolve DOIs for multiple titles.

        Args:
            titles: List of paper titles
            years: Corresponding years (optional)
            max_workers: Number of concurrent workers
            show_progress: Show progress bar

        Returns:
            Dict mapping titles to DOIs (or None if not found)
        """
        if not titles:
            return {}

        # Prepare inputs
        if not years:
            years = [None] * len(titles)

        results = {}

        # Progress bar setup
        pbar = None
        if show_progress:
            pbar = tqdm(total=len(titles), desc="Resolving DOIs")

        def resolve_single(idx: int) -> tuple[str, Optional[str]]:
            """Resolve single title."""
            title = titles[idx]
            year = years[idx] if idx < len(years) else None
            doi = self.title_to_doi(title, year)
            if pbar:
                pbar.update(1)
            return title, doi

        # Process in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(resolve_single, i) for i in range(len(titles))
            ]

            for future in as_completed(futures):
                try:
                    title, doi = future.result()
                    results[title] = doi
                except Exception as e:
                    logger.error(f"Error in batch resolve: {e}")

        if pbar:
            pbar.close()

        return results

    def extract_dois_from_text(self, text: str) -> List[str]:
        """
        Extract all DOIs from text.

        Args:
            text: Text to search

        Returns:
            List of unique DOIs found
        """
        import re

        doi_pattern = r"10\.\d{4,}/[-._;()/:\w]+"
        matches = re.findall(doi_pattern, text)

        # Deduplicate while preserving order
        seen = set()
        unique_dois = []
        for doi in matches:
            if doi not in seen:
                seen.add(doi)
                unique_dois.append(doi)

        return unique_dois

    def validate_doi(self, doi: str) -> bool:
        """
        Validate DOI format.

        Args:
            doi: DOI to validate

        Returns:
            True if valid DOI format
        """
        import re

        if not doi:
            return False

        # Basic DOI pattern
        pattern = r"^10\.\d{4,}/[-._;()/:\w]+$"
        return bool(re.match(pattern, doi))

    # def get_comprehensive_metadata(
    #     self,
    #     title: str,
    #     year: Optional[int] = None,
    #     authors: Optional[List[str]] = None,
    #     sources: Optional[List[str]] = None,
    # ) -> Optional[Dict[str, Any]]:
    #     """Get comprehensive metadata from title with all available fields."""
    #     if not title:
    #         return None

    #     sources_list = sources or self.sources

    #     for source_name in sources_list:
    #         source = self._get_source(source_name)
    #         if not source:
    #             continue

    #         try:
    #             # Try get_metadata first if available
    #             if hasattr(source, "get_metadata"):
    #                 metadata = source.get_metadata(title, year, authors)
    #                 if metadata and metadata.get("doi"):
    #                     metadata["source"] = source_name
    #                     logger.info(
    #                         f"Found comprehensive metadata via {source.name}"
    #                     )
    #                     return metadata

    #             # Fallback to DOI-only search
    #             doi = source.search(title, year, authors)
    #             if doi:
    #                 # Try to get additional metadata
    #                 metadata = {"doi": doi, "source": source_name}

    #                 # Try to get abstract
    #                 if hasattr(source, "get_abstract"):
    #                     abstract = source.get_abstract(doi)
    #                     if abstract:
    #                         metadata["abstract"] = abstract

    #                 return metadata

    #             time.sleep(source.rate_limit_delay)

    #         except Exception as exc:
    #             logger.warning(
    #                 f"Error getting metadata from {source_name}: {exc}"
    #             )

    #     return None

    def get_comprehensive_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from title with all available fields."""
        if not title:
            return None

        sources_list = sources or self.sources
        for source_name in sources_list:
            source = self._get_source(source_name)
            if not source:
                continue

            try:
                if hasattr(source, "get_metadata"):
                    metadata = source.get_metadata(title, year, authors)
                    if metadata and metadata.get("doi"):
                        metadata["source"] = source_name
                        logger.info(
                            f"Found comprehensive metadata via {source.name}"
                        )
                        return metadata

                doi = source.search(title, year, authors)
                if doi:
                    metadata = {"doi": doi, "source": source_name}
                    if hasattr(source, "get_abstract"):
                        try:
                            abstract = source.get_abstract(doi)
                            if abstract:
                                metadata["abstract"] = abstract
                        except Exception:
                            pass
                    return metadata

                time.sleep(source.rate_limit_delay)
            except requests.HTTPError as exc:
                if exc.response and exc.response.status_code == 429:
                    logger.warning(
                        f"Rate limit hit for {source_name}. Consider adding API key or waiting between requests."
                    )
                else:
                    logger.debug(
                        f"HTTP error getting metadata from {source_name}: {exc}"
                    )
                continue
            except Exception as exc:
                logger.debug(
                    f"Error getting metadata from {source_name}: {exc}"
                )
                continue

        return None


if __name__ == "__main__":
    import asyncio

    async def main():
        resolver = DOIResolver()
        title = "Attention is All You Need"
        doi = await resolver.title_to_doi_async(title)
        if doi:
            print(f"\nFound DOI: {doi}")
            print(f"URL: https://doi.org/{doi}")
        else:
            print("\nNo DOI found")

    asyncio.run(main())


# python -m scitex.scholar.doi._DOIResolver

# EOF
