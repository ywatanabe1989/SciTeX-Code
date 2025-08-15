#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 19:15:03 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/engines/_EngineResolutionStrategy.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/engines/_EngineResolutionStrategy.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Engine-based DOI resolution strategy.

This module handles the core logic for resolving DOIs from multiple engines
with intelligent engine selection, rate limiting, and failure handling.
Extracted from SingleDOIResolver to follow Single Responsibility Principle.
"""

import asyncio
import re
import time
from typing import Any, Dict, List, Optional, Type

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ._RateLimitHandler import RateLimitHandler
from ._ArXivEngine import ArXivEngine
from ._BaseDOIEngine import BaseDOIEngine
from ._CrossRefEngine import CrossRefEngine
from ._OpenAlexEngine import OpenAlexEngine
from ._PubMedEngine import PubMedEngine
from ._SemanticScholarEngine import SemanticScholarEngine
from ._EngineRotationManager import EngineRotationManager
from ._URLDOIEngine import URLDOIEngine

logger = logging.getLogger(__name__)


class EngineResolutionStrategy:
    """Strategy for resolving DOIs from multiple API engines with intelligent selection."""

    # Engine registry
    ENGINE_CLASSES: Dict[str, Type[BaseDOIEngine]] = {
        "url_doi_engine": URLDOIEngine,
        "crossref": CrossRefEngine,
        "pubmed": PubMedEngine,
        "openalex": OpenAlexEngine,
        "semantic_scholar": SemanticScholarEngine,
        "arxiv": ArXivEngine,
    }

    def __init__(
        self,
        engines: Optional[List[str]] = None,
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        rate_limit_handler: Optional[RateLimitHandler] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize engine resolution strategy.

        Args:
            engines: List of engine names to use (None for default engines)
            rate_limit_handler: Rate limit handler instance
            email_config: Email configuration for engines (engine_name -> email)
        """
        self.config = config or ScholarConfig()

        # Souces
        self.engines = self.config.resolve("engines", engines)

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

        # Engine Rotation Manager
        self.engine_rotation_manager = EngineRotationManager(
            self.rate_limit_handler
        )

        # Initialize engine instances cache
        self._engine_instances: Dict[str, BaseDOIEngine] = {}

        logger.debug(
            f"EngineResolutionStrategy initialized with engines: {self.engines}"
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
        engines: Optional[List[str]] = None,
        **kwargs,
    ) -> Optional[Dict]:
        """Resolve DOI from engines with intelligent engine rotation and rate limit handling.

        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)
            engines: Specific engines to use (optional, overrides instance engines)
            url: URL to extract DOI from (optional)
            **kwargs: Additional parameters for engine resolution

        Returns:
            Dict with 'doi', 'engine', and optional 'metadata' keys if found, None otherwise
        """

        # Try CorpusID resolution if URL contains CorpusID
        corpus_result = await self._corpusid2metadata_async(
            url, title, year, authors
        )
        if corpus_result:
            return corpus_result

        # Prepare paper info for intelligent engine selection
        paper_info = {"title": title, "year": year, "authors": authors}

        # Get engines to use
        engines = self.config.resolve("engines", engines)

        # Get available engines (not rate limited)
        if self.rate_limit_handler:
            available_engines = self.rate_limit_handler.get_available_engines(
                engines
            )

            if not available_engines:
                # All engines are rate limited - get wait time for earliest available
                next_available_time = (
                    self.rate_limit_handler.get_next_available_time(engines)
                )
                wait_time = max(0, next_available_time - time.time())

                if wait_time > 0:
                    logger.warning(
                        f"All engines rate limited, waiting {wait_time:.1f}s for next available engine"
                    )
                    await self.rate_limit_handler.wait_with_countdown_async(
                        wait_time, "any engine"
                    )
                    # Retry with updated availability
                    available_engines = (
                        self.rate_limit_handler.get_available_engines(engines)
                    )

                if not available_engines:
                    logger.error(
                        "No engines available after waiting for rate limits"
                    )
                    return None
        else:
            available_engines = engines

        # Get optimal engine order using intelligent selection
        if self.engine_rotation_manager:
            optimal_engines = (
                self.engine_rotation_manager.get_optimal_engine_order(
                    paper_info, available_engines, max_engines=3
                )
            )
        else:
            # Fallback to first 3 engines
            optimal_engines = available_engines[:3]

        logger.debug(f"Trying engines in optimal order: {optimal_engines}")

        # Try primary engines with enhanced error handling and performance tracking
        primary_result = await self._try_engines(
            optimal_engines,
            title,
            year,
            authors,
            url,
            paper_info,
            **kwargs,
        )

        if primary_result:
            return primary_result

        # Try fallback engines if primary engines failed
        if self.engine_rotation_manager:
            tried_engines = optimal_engines
            fallback_engines = (
                self.engine_rotation_manager.get_fallback_engines(
                    tried_engines, engines
                )
            )

            if fallback_engines:
                logger.info(
                    f"Primary engines failed, trying fallbacks: {fallback_engines}"
                )

                fallback_result = await self._try_engines(
                    fallback_engines,
                    title,
                    year,
                    authors,
                    url,
                    paper_info,
                    **kwargs,
                )

                if fallback_result:
                    return fallback_result

        # No DOI found after trying all available engines
        all_tried = optimal_engines + (
            fallback_engines[:2]
            if self.engine_rotation_manager and fallback_engines
            else []
        )
        logger.fail(
            f"DOI not found after searching {len(all_tried)} engines ({all_tried}): {title[:50]}..."
        )

        return None

    def get_available_engines(self) -> List[str]:
        """Get list of currently available (non-rate-limited) engines."""
        if self.rate_limit_handler:
            return self.rate_limit_handler.get_available_engines(self.engines)
        return self.engines.copy()

    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get statistics about engine performance."""
        stats = {
            "configured_engines": self.engines.copy(),
            "instantiated_engines": list(self._engine_instances.keys()),
            "available_engines": self.get_available_engines(),
        }

        # Add rate limiting stats if available
        if self.rate_limit_handler:
            stats["rate_limit_stats"] = (
                self.rate_limit_handler.get_statistics()
            )

        # Add engine rotation stats if available
        if self.engine_rotation_manager:
            stats["rotation_stats"] = (
                self.engine_rotation_manager.get_statistics()
            )

        # Add individual engine stats
        engine_details = {}
        for name, engine in self._engine_instances.items():
            engine_details[name] = engine.get_request_stats()
        stats["engine_details"] = engine_details

        return stats

    def _get_engine(self, name: str) -> Optional[BaseDOIEngine]:
        """Get or create engine instance."""
        if name not in self._engine_instances:
            engine_class = self.ENGINE_CLASSES.get(name)
            if engine_class:
                # Get appropriate email for each engine
                email_map = {
                    "crossref": self.crossref_email,
                    "pubmed": self.pubmed_email,
                    "openalex": self.openalex_email,
                    "semantic_scholar": self.semantic_scholar_email,
                    "arxiv": self.arxiv_email,
                }

                # URLDOIEngine doesn't need email parameter
                if name == "url_doi_engine":
                    engine_instance = engine_class()
                else:
                    email = email_map.get(name)
                    engine_instance = engine_class(email)

                # Inject rate limit handler into engine
                if self.rate_limit_handler:
                    engine_instance.set_rate_limit_handler(
                        self.rate_limit_handler
                    )

                self._engine_instances[name] = engine_instance
        return self._engine_instances.get(name)

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

        # Use Semantic Scholar engine for CorpusID resolution
        semantic_engine = None
        for engine in self._engine_instances.values():
            if isinstance(engine, SemanticScholarEngine) and hasattr(
                engine, "resolve_corpus_id"
            ):
                semantic_engine = engine
                break

        # If not already instantiated, get the semantic scholar engine
        if not semantic_engine:
            semantic_engine = self._get_engine("semantic_scholar")
            if not semantic_engine:
                semantic_engine = self._get_engine("semantic_scholar")

        if semantic_engine:
            try:
                doi = semantic_engine.resolve_corpus_id(corpus_id)
                if doi:
                    logger.success(
                        f"Successfully resolved CorpusID {corpus_id} → DOI: {doi}"
                    )
                    return {
                        "doi": doi,
                        "engine": "semantic_scholar_corpus_id",
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
                "Semantic Scholar engine not available for CorpusID resolution"
            )

        return None

    async def _try_engines(
        self,
        engine_names: List[str],
        title: str,
        year: Optional[int],
        authors: Optional[List[str]],
        url: Optional[str],
        paper_info: Dict,
        **kwargs,
    ) -> Optional[Dict]:
        """Try a list of engines and return first successful result."""
        for engine_name in engine_names:
            engine = self._get_engine(engine_name)
            if not engine:
                continue

            start_time = time.time()
            try:
                # Wait for any engine-specific rate limiting
                await engine._apply_rate_limiting_async()

                # Try this engine
                doi = await self._search_engine_async(
                    engine, title, year, authors, url, **kwargs
                )

                response_time = time.time() - start_time

                # Try to get comprehensive metadata first
                metadata_result = await self._get_comprehensive_metadata_async(
                    engine, title, year, authors
                )

                if metadata_result and metadata_result.get("doi"):
                    # Success with comprehensive metadata!
                    doi = metadata_result["doi"]
                    if self.engine_rotation_manager:
                        self.engine_rotation_manager.record_attempt(
                            engine_name,
                            paper_info,
                            success=True,
                            response_time=response_time,
                        )

                    return {
                        "doi": doi,
                        "engine": engine_name,
                        "metadata": metadata_result,
                    }
                elif doi:
                    # Fallback: got DOI but no comprehensive metadata
                    if self.engine_rotation_manager:
                        self.engine_rotation_manager.record_attempt(
                            engine_name,
                            paper_info,
                            success=True,
                            response_time=response_time,
                        )

                    return {"doi": doi, "engine": engine_name}
                else:
                    # No DOI found, but no error
                    if self.engine_rotation_manager:
                        self.engine_rotation_manager.record_attempt(
                            engine_name,
                            paper_info,
                            success=False,
                            response_time=response_time,
                        )

            except Exception as e:
                response_time = time.time() - start_time
                logger.debug(f"Error searching {engine_name}: {e}")

                # Record failure
                if self.engine_rotation_manager:
                    self.engine_rotation_manager.record_attempt(
                        engine_name,
                        paper_info,
                        success=False,
                        response_time=response_time,
                    )

                # Check if this was a rate limit error
                if self.rate_limit_handler:
                    rate_limit_info = (
                        self.rate_limit_handler.detect_rate_limit(
                            engine_name, exception=e
                        )
                    )
                    if rate_limit_info:
                        self.rate_limit_handler.record_rate_limit(
                            rate_limit_info
                        )
                        logger.warning(
                            f"Rate limit detected for {engine_name}, skipping to next engine"
                        )

                continue

        return None

    async def _search_engine_async(
        self,
        engine: BaseDOIEngine,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        url: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """Search single engine asynchronously - engines handle their own retries."""
        try:
            loop = asyncio.get_event_loop()
            # Pass URL and kwargs to URLDOIEngine, regular params to others
            if hasattr(engine, "name") and engine.name == "url_doi_engine":
                result = await loop.run_in_executor(
                    None, engine.search, title, year, authors, url, **kwargs
                )
            else:
                result = await loop.run_in_executor(
                    None, engine.search, title, year, authors
                )

            if result:
                logger.success(f"Found DOI via {engine.name}")
                return result
            else:
                logger.debug(f"No DOI found via {engine.name}")
                return None

        except Exception as e:
            logger.debug(f"Error searching {engine.name}: {e}")
            return None

    async def _get_comprehensive_metadata_async(
        self,
        engine: BaseDOIEngine,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        """Get comprehensive metadata from engine asynchronously."""
        try:
            # Check if engine has get_metadata method
            if not hasattr(engine, "get_metadata"):
                return None

            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(
                None, engine.get_metadata, title, year, authors
            )

            if metadata and metadata.get("doi"):
                logger.success(
                    f"Found comprehensive metadata via {engine.name}: {metadata.get('doi')}"
                )
                if metadata.get("journal"):
                    logger.debug(f"  Journal: {metadata['journal']}")
                return metadata
            else:
                logger.debug(
                    f"No comprehensive metadata found via {engine.name}"
                )
                return None

        except Exception as e:
            logger.debug(
                f"Error getting comprehensive metadata from {engine.name}: {e}"
            )
            return None


if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    async def test_engine_resolution_strategy():
        """Test the engine resolution strategy functionality."""

        # Create strategy with default configuration
        strategy = EngineResolutionStrategy()

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
        #     print(f"   📊 Engine: {corpus_result.get('engine')}")
        # else:
        #     print(f"   ℹ️ CorpusID resolution not available or failed")

        # # Test engine availability
        # print("\n3. Testing engine availability:")
        # available = strategy.get_available_engines()
        # print(f"   Available engines: {available}")

        # # Show statistics
        # print("\n4. Strategy statistics:")
        # stats = strategy.get_engine_statistics()
        # print(f"   Configured engines: {len(stats['configured_engines'])}")
        # print(f"   Instantiated engines: {len(stats['instantiated_engines'])}")
        # print(f"   Available engines: {len(stats['available_engines'])}")

        # for engine, details in stats["engine_details"].items():
        #     print(f"   {engine}: {details['total_requests']} requests")

        # print("\n✅ EngineResolutionStrategy test completed!")
        # print("\nUsage patterns:")
        # print("1. Basic: strategy = EngineResolutionStrategy()")
        # print(
        #     "2. Custom engines: EngineResolutionStrategy(engines=['crossref', 'pubmed'])"
        # )
        # print(
        #     "3. With rate limiting: EngineResolutionStrategy(rate_limit_handler=handler)"
        # )
        # print(
        #     "4. Async resolve: await strategy.metadata2metadata_async(title)"
        # )
        # print(
        #     "5. Strategy handles engine rotation and rate limiting automatically"
        # )

    asyncio.run(test_engine_resolution_strategy())


# python -m scitex.scholar.engines.individual._EngineResolutionStrategy

# EOF
