#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 19:15:03 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_SourceResolutionStrategy.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Source-based DOI resolution strategy.

This module handles the core logic for resolving DOIs from multiple sources
with intelligent source selection, rate limiting, and failure handling.
Extracted from SingleDOIResolver to follow Single Responsibility Principle.
"""

import asyncio
import re
import time
from typing import Any, Dict, List, Optional, Type

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ..utils._RateLimitHandler import RateLimitHandler
from ._ArXivSource import ArXivSource
from ._BaseDOISource import BaseDOISource
from ._CrossRefSource import CrossRefSource
from ._OpenAlexSource import OpenAlexSource
from ._PubMedSource import PubMedSource
from ._SemanticScholarSource import SemanticScholarSource
from ._SourceRotationManager import SourceRotationManager
from ._URLDOISource import URLDOISource

logger = logging.getLogger(__name__)


class SourceResolutionStrategy:
    """Strategy for resolving DOIs from multiple API sources with intelligent selection."""

    # Source registry
    SOURCE_CLASSES: Dict[str, Type[BaseDOISource]] = {
        "url_doi_source": URLDOISource,
        "crossref": CrossRefSource,
        "pubmed": PubMedSource,
        "openalex": OpenAlexSource,
        "semantic_scholar": SemanticScholarSource,
        "arxiv": ArXivSource,
    }

    def __init__(
        self,
        sources: Optional[List[str]] = None,
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        rate_limit_handler: Optional[RateLimitHandler] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize source resolution strategy.

        Args:
            sources: List of source names to use (None for default sources)
            rate_limit_handler: Rate limit handler instance
            email_config: Email configuration for sources (source_name -> email)
        """
        self.config = config or ScholarConfig()

        # Souces
        self.sources = self.config.resolve("sources", sources)

        # Emails
        self.crossref_email = self.config.resolve(
            "crossref_email", email_crossref
        )
        self.pubmed_email = self.config.resolve("pubmed_email", email_pubmed)
        self.openalex_email = self.config.resolve(
            "openalex_email", email_openalex
        )
        self.semantic_scholar_email = self.config.resolve(
            "semantic_scholar_email",
            email_semantic_scholar,
        )
        self.arxiv_email = self.config.resolve("arxiv_email", email_arxiv)

        # Rate Limit Handler
        self.rate_limit_handler = rate_limit_handler or RateLimitHandler(
            config
        )

        # Source Rotation Manager
        self.source_rotation_manager = SourceRotationManager(
            self.rate_limit_handler
        )

        # Initialize source instances cache
        self._source_instances: Dict[str, BaseDOISource] = {}

        logger.debug(
            f"SourceResolutionStrategy initialized with sources: {self.sources}"
        )

    async def metadata2metadata_async(
        self,
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        corpus_id: Optional[str] = None,
        url: Optional[str] = None,
        year: Optional[int] = None,
        sources: Optional[List[str]] = None,
        **kwargs,
    ) -> Optional[Dict]:
        """Resolve DOI from sources with intelligent source rotation and rate limit handling.

        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)
            sources: Specific sources to use (optional, overrides instance sources)
            url: URL to extract DOI from (optional)
            **kwargs: Additional parameters for source resolution

        Returns:
            Dict with 'doi', 'source', and optional 'metadata' keys if found, None otherwise
        """

        # Try CorpusID resolution if URL contains CorpusID
        corpus_result = await self._corpusid2metadata_async(
            url, title, year, authors
        )
        if corpus_result:
            return corpus_result

        # Prepare paper info for intelligent source selection
        paper_info = {"title": title, "year": year, "authors": authors}

        # Get sources to use
        sources = self.config.resolve("sources", sources)

        # Get available sources (not rate limited)
        if self.rate_limit_handler:
            available_sources = self.rate_limit_handler.get_available_sources(
                sources
            )

            if not available_sources:
                # All sources are rate limited - get wait time for earliest available
                next_available_time = (
                    self.rate_limit_handler.get_next_available_time(sources)
                )
                wait_time = max(0, next_available_time - time.time())

                if wait_time > 0:
                    logger.warning(
                        f"All sources rate limited, waiting {wait_time:.1f}s for next available source"
                    )
                    await self.rate_limit_handler.wait_with_countdown_async(
                        wait_time, "any source"
                    )
                    # Retry with updated availability
                    available_sources = (
                        self.rate_limit_handler.get_available_sources(sources)
                    )

                if not available_sources:
                    logger.error(
                        "No sources available after waiting for rate limits"
                    )
                    return None
        else:
            available_sources = sources

        # Get optimal source order using intelligent selection
        if self.source_rotation_manager:
            optimal_sources = (
                self.source_rotation_manager.get_optimal_source_order(
                    paper_info, available_sources, max_sources=3
                )
            )
        else:
            # Fallback to first 3 sources
            optimal_sources = available_sources[:3]

        logger.debug(f"Trying sources in optimal order: {optimal_sources}")

        # Try primary sources with enhanced error handling and performance tracking
        primary_result = await self._try_sources(
            optimal_sources,
            title,
            year,
            authors,
            url,
            paper_info,
            **kwargs,
        )

        if primary_result:
            return primary_result

        # Try fallback sources if primary sources failed
        if self.source_rotation_manager:
            tried_sources = optimal_sources
            fallback_sources = (
                self.source_rotation_manager.get_fallback_sources(
                    tried_sources, sources
                )
            )

            if fallback_sources:
                logger.info(
                    f"Primary sources failed, trying fallbacks: {fallback_sources}"
                )

                fallback_result = await self._try_sources(
                    fallback_sources,
                    title,
                    year,
                    authors,
                    url,
                    paper_info,
                    **kwargs,
                )

                if fallback_result:
                    return fallback_result

        # No DOI found after trying all available sources
        all_tried = optimal_sources + (
            fallback_sources[:2]
            if self.source_rotation_manager and fallback_sources
            else []
        )
        logger.fail(
            f"DOI not found after searching {len(all_tried)} sources ({all_tried}): {title[:50]}..."
        )

        return None

    def get_available_sources(self) -> List[str]:
        """Get list of currently available (non-rate-limited) sources."""
        if self.rate_limit_handler:
            return self.rate_limit_handler.get_available_sources(self.sources)
        return self.sources.copy()

    def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics about source performance."""
        stats = {
            "configured_sources": self.sources.copy(),
            "instantiated_sources": list(self._source_instances.keys()),
            "available_sources": self.get_available_sources(),
        }

        # Add rate limiting stats if available
        if self.rate_limit_handler:
            stats["rate_limit_stats"] = (
                self.rate_limit_handler.get_statistics()
            )

        # Add source rotation stats if available
        if self.source_rotation_manager:
            stats["rotation_stats"] = (
                self.source_rotation_manager.get_statistics()
            )

        # Add individual source stats
        source_details = {}
        for name, source in self._source_instances.items():
            source_details[name] = source.get_request_stats()
        stats["source_details"] = source_details

        return stats

    def _get_source(self, name: str) -> Optional[BaseDOISource]:
        """Get or create source instance."""
        if name not in self._source_instances:
            source_class = self.SOURCE_CLASSES.get(name)
            if source_class:
                # Get appropriate email for each source
                email_map = {
                    "crossref": self.crossref_email,
                    "pubmed": self.pubmed_email,
                    "openalex": self.openalex_email,
                    "semantic_scholar": self.semantic_scholar_email,
                    "arxiv": self.arxiv_email,
                }

                # URLDOISource doesn't need email parameter
                if name == "url_doi_source":
                    source_instance = source_class()
                else:
                    email = email_map.get(name)
                    source_instance = source_class(email)

                # Inject rate limit handler into source
                if self.rate_limit_handler:
                    source_instance.set_rate_limit_handler(
                        self.rate_limit_handler
                    )

                self._source_instances[name] = source_instance
        return self._source_instances.get(name)

    async def _corpusid2metadata_async(
        self,
        url: Optional[str],
        title: str,
        year: Optional[int],
        authors: Optional[List[str]],
    ) -> Optional[Dict]:
        """Try CorpusID resolution if URL contains CorpusID."""
        if not url or "CorpusId:" not in url:
            return None

        corpus_match = re.search(r"CorpusId:(\d+)", url)
        if not corpus_match:
            return None

        corpus_id = corpus_match.group(1)
        logger.info(f"Attempting CorpusID resolution for: {corpus_id}")

        # Use Semantic Scholar source for CorpusID resolution
        semantic_source = None
        for source in self._source_instances.values():
            if isinstance(source, SemanticScholarSource) and hasattr(
                source, "resolve_corpus_id"
            ):
                semantic_source = source
                break

        # If not already instantiated, get the semantic scholar source
        if not semantic_source:
            semantic_source = self._get_source("semantic_scholar")
            if not semantic_source:
                semantic_source = self._get_source("semantic_scholar")

        if semantic_source:
            try:
                doi = semantic_source.resolve_corpus_id(corpus_id)
                if doi:
                    logger.success(
                        f"Successfully resolved CorpusID {corpus_id} → DOI: {doi}"
                    )
                    return {
                        "doi": doi,
                        "source": "semantic_scholar_corpus_id",
                        "metadata": {
                            "corpus_id": corpus_id,
                            "title": title,
                            "year": year,
                            "authors": authors,
                        },
                    }
            except Exception as e:
                logger.debug(
                    f"CorpusID resolution failed for {corpus_id}: {e}"
                )
        else:
            logger.warning(
                "Semantic Scholar source not available for CorpusID resolution"
            )

        return None

    async def _try_sources(
        self,
        source_names: List[str],
        title: str,
        year: Optional[int],
        authors: Optional[List[str]],
        url: Optional[str],
        paper_info: Dict,
        **kwargs,
    ) -> Optional[Dict]:
        """Try a list of sources and return first successful result."""
        for source_name in source_names:
            source = self._get_source(source_name)
            if not source:
                continue

            start_time = time.time()
            try:
                # Wait for any source-specific rate limiting
                await source._apply_rate_limiting_async()

                # Try this source
                doi = await self._search_source_async(
                    source, title, year, authors, url, **kwargs
                )

                response_time = time.time() - start_time

                # Try to get comprehensive metadata first
                metadata_result = await self._get_comprehensive_metadata_async(
                    source, title, year, authors
                )

                if metadata_result and metadata_result.get("doi"):
                    # Success with comprehensive metadata!
                    doi = metadata_result["doi"]
                    if self.source_rotation_manager:
                        self.source_rotation_manager.record_attempt(
                            source_name,
                            paper_info,
                            success=True,
                            response_time=response_time,
                        )

                    return {
                        "doi": doi,
                        "source": source_name,
                        "metadata": metadata_result,
                    }
                elif doi:
                    # Fallback: got DOI but no comprehensive metadata
                    if self.source_rotation_manager:
                        self.source_rotation_manager.record_attempt(
                            source_name,
                            paper_info,
                            success=True,
                            response_time=response_time,
                        )

                    return {"doi": doi, "source": source_name}
                else:
                    # No DOI found, but no error
                    if self.source_rotation_manager:
                        self.source_rotation_manager.record_attempt(
                            source_name,
                            paper_info,
                            success=False,
                            response_time=response_time,
                        )

            except Exception as e:
                response_time = time.time() - start_time
                logger.debug(f"Error searching {source_name}: {e}")

                # Record failure
                if self.source_rotation_manager:
                    self.source_rotation_manager.record_attempt(
                        source_name,
                        paper_info,
                        success=False,
                        response_time=response_time,
                    )

                # Check if this was a rate limit error
                if self.rate_limit_handler:
                    rate_limit_info = (
                        self.rate_limit_handler.detect_rate_limit(
                            source_name, exception=e
                        )
                    )
                    if rate_limit_info:
                        self.rate_limit_handler.record_rate_limit(
                            rate_limit_info
                        )
                        logger.warning(
                            f"Rate limit detected for {source_name}, skipping to next source"
                        )

                continue

        return None

    async def _search_source_async(
        self,
        source: BaseDOISource,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        url: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """Search single source asynchronously - sources handle their own retries."""
        try:
            loop = asyncio.get_event_loop()
            # Pass URL and kwargs to URLDOISource, regular params to others
            if hasattr(source, "name") and source.name == "url_doi_source":
                result = await loop.run_in_executor(
                    None, source.search, title, year, authors, url, **kwargs
                )
            else:
                result = await loop.run_in_executor(
                    None, source.search, title, year, authors
                )

            if result:
                logger.success(f"Found DOI via {source.name}")
                return result
            else:
                logger.debug(f"No DOI found via {source.name}")
                return None

        except Exception as e:
            logger.debug(f"Error searching {source.name}: {e}")
            return None

    async def _get_comprehensive_metadata_async(
        self,
        source: BaseDOISource,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        """Get comprehensive metadata from source asynchronously."""
        try:
            # Check if source has get_metadata method
            if not hasattr(source, "get_metadata"):
                return None

            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(
                None, source.get_metadata, title, year, authors
            )

            if metadata and metadata.get("doi"):
                logger.success(
                    f"Found comprehensive metadata via {source.name}: {metadata.get('doi')}"
                )
                if metadata.get("journal"):
                    logger.debug(f"  Journal: {metadata['journal']}")
                return metadata
            else:
                logger.debug(
                    f"No comprehensive metadata found via {source.name}"
                )
                return None

        except Exception as e:
            logger.debug(
                f"Error getting comprehensive metadata from {source.name}: {e}"
            )
            return None


if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    async def test_source_resolution_strategy():
        """Test the source resolution strategy functionality."""

        # Create strategy with default configuration
        strategy = SourceResolutionStrategy()

        # Test DOI resolution
        test_papers = [
            {
                "title": "Attention is All You Need",
                "year": 2017,
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "year": 2018,
                "authors": ["Jacob Devlin"],
            },
        ]

        for paper in test_papers:
            # print(f"\n   🔍 Searching: {paper['title'][:50]}...")
            result = await strategy.metadata2metadata_async(
                title=paper["title"],
                year=paper.get("year"),
                authors=paper.get("authors"),
            )

        # # Test CorpusID resolution
        # print("\n2. Testing CorpusID resolution:")
        # corpus_url = "https://www.semanticscholar.org/paper/Attention-Is-All-You-Need-Vaswani-Shazeer/204e3073870fae3d05bcbc2f6a8e263d9b72e776?p2df&CorpusId:13756489"

        # corpus_result = await strategy.metadata2metadata_async(
        #     title="Attention is All You Need", year=2017, url=corpus_url
        # )

        # if corpus_result:
        #     print(f"   ✅ CorpusID resolution: {corpus_result.get('doi')}")
        #     print(f"   📊 Source: {corpus_result.get('source')}")
        # else:
        #     print(f"   ℹ️ CorpusID resolution not available or failed")

        # # Test source availability
        # print("\n3. Testing source availability:")
        # available = strategy.get_available_sources()
        # print(f"   Available sources: {available}")

        # # Show statistics
        # print("\n4. Strategy statistics:")
        # stats = strategy.get_source_statistics()
        # print(f"   Configured sources: {len(stats['configured_sources'])}")
        # print(f"   Instantiated sources: {len(stats['instantiated_sources'])}")
        # print(f"   Available sources: {len(stats['available_sources'])}")

        # for source, details in stats["source_details"].items():
        #     print(f"   {source}: {details['total_requests']} requests")

        # print("\n✅ SourceResolutionStrategy test completed!")
        # print("\nUsage patterns:")
        # print("1. Basic: strategy = SourceResolutionStrategy()")
        # print(
        #     "2. Custom sources: SourceResolutionStrategy(sources=['crossref', 'pubmed'])"
        # )
        # print(
        #     "3. With rate limiting: SourceResolutionStrategy(rate_limit_handler=handler)"
        # )
        # print(
        #     "4. Async resolve: await strategy.metadata2metadata_async(title)"
        # )
        # print(
        #     "5. Strategy handles source rotation and rate limiting automatically"
        # )

    asyncio.run(test_source_resolution_strategy())


# python -m scitex.scholar.metadata.doi.sources._SourceResolutionStrategy

# EOF
