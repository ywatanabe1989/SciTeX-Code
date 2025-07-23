#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 15:52:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_MetadataEnricher.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_MetadataEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Metadata enrichment module for SciTeX Scholar.

This module enriches scientific papers with additional metadata:
- Journal impact factors from impact_factor package
- Citation counts from Semantic Scholar and CrossRef
- Journal metrics (quartiles, rankings)
- Future: h-index, author metrics, altmetrics, etc.

All enrichment is done in-place on Paper objects.
"""

import asyncio
import logging
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..errors import EnrichmentError, warn_performance
from ._Paper import Paper

logger = logging.getLogger(__name__)


def _get_jcr_year():
    """Dynamically determine JCR data year from impact_factor package files."""
    try:
        import glob
        import re

        import impact_factor

        # Find Excel files in the package data directory
        package_dir = os.path.dirname(impact_factor.__file__)
        data_dir = os.path.join(package_dir, "data")

        if os.path.exists(data_dir):
            excel_files = glob.glob(os.path.join(data_dir, "*.xlsx"))
            years = []

            for file in excel_files:
                basename = os.path.basename(file)
                # Extract year from filename (e.g., "CopyofImpactFactor2024.xlsx")
                year_match = re.search(r"20\d{2}", basename)
                if year_match:
                    years.append(int(year_match.group()))

            if years:
                return max(years)  # Return the latest year
    except Exception as e:
        logger.debug(f"Could not determine JCR year from package: {e}")

    # Fallback to hardcoded year
    return 2024


# JCR data year - dynamically determined from impact_factor package
JCR_YEAR = _get_jcr_year()


class MetadataEnricher:
    """
    Metadata enricher for scientific papers.

    Enriches Paper objects with impact factors, citation counts,
    journal metrics, and other scholarly metadata from various sources.
    """

    def __init__(
        self,
        semantic_scholar_api_key: Optional[str] = None,
        crossref_api_key: Optional[str] = None,
        email: Optional[str] = None,
        journal_data_path: Optional[Path] = None,
        use_impact_factor_package: bool = True,
        cache_size: int = 1000,
    ) -> None:
        """
        Initialize unified enricher.

        Args:
            semantic_scholar_api_key: API key for Semantic Scholar
            crossref_api_key: API key for CrossRef (optional, for higher rate limits)
            email: Email for CrossRef API (used in User-Agent)
            journal_data_path: Path to custom journal metrics data
            use_impact_factor_package: Whether to use impact_factor package
            cache_size: Size of LRU cache for journal lookups
        """
        # API keys and email
        self.semantic_scholar_api_key: Optional[str] = semantic_scholar_api_key
        self.crossref_api_key: Optional[str] = crossref_api_key
        self.email: Optional[str] = email

        # Journal data
        self.journal_data_path: Optional[Path] = journal_data_path
        self.use_impact_factor_package: bool = use_impact_factor_package
        self._journal_data: Optional[Dict[str, Dict[str, Any]]] = None
        self._impact_factor_instance: Optional[Any] = None

        # Configure cache
        self._cache_size: int = cache_size
        self._get_journal_metrics = lru_cache(maxsize=cache_size)(
            self._get_journal_metrics_uncached
        )

        # Initialize components
        self._init_impact_factor_package()
        self._load_journal_data()

    def enrich_all(
        self,
        papers: List[Paper],
        enrich_impact_factors: bool = True,
        enrich_citations: bool = True,
        enrich_journal_metrics: bool = True,
        parallel: bool = True,
    ) -> List[Paper]:
        """
        Enrich papers with all available metadata.

        Args:
            papers: List of papers to enrich
            enrich_impact_factors: Add journal impact factors
            enrich_citations: Add citation counts from Semantic Scholar
            enrich_journal_metrics: Add quartiles, rankings
            parallel: Use parallel processing for API calls

        Returns:
            Same list with papers enriched in-place

        Raises:
            EnrichmentError: If enrichment fails critically
        """
        if not papers:
            return papers

        logger.info(f"Starting enrichment for {len(papers)} papers")

        # Enrich impact factors and journal metrics together (same data source)
        if enrich_impact_factors or enrich_journal_metrics:
            self._enrich_journal_data(
                papers,
                include_impact_factors=enrich_impact_factors,
                include_metrics=enrich_journal_metrics,
            )

        # Enrich citations (requires API calls)
        if enrich_citations:
            if parallel and len(papers) > 50:
                warn_performance(
                    "Citation enrichment",
                    f"Enriching {len(papers)} papers in parallel. This may take time.",
                )

            # Run async enrichment
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If already in async context, create task
                    task = asyncio.create_task(
                        self._enrich_citations_async(papers)
                    )
                    papers = asyncio.run_coroutine_threadsafe(
                        task, loop
                    ).result()
                else:
                    papers = loop.run_until_complete(
                        self._enrich_citations_async(papers)
                    )
            except RuntimeError:
                # No event loop, create new one
                papers = asyncio.run(self._enrich_citations_async(papers))

        logger.info("Enrichment completed")
        return papers

    def enrich_impact_factors(self, papers: List[Paper]) -> List[Paper]:
        """
        Enrich papers with journal impact factors only.

        Args:
            papers: List of papers to enrich

        Returns:
            Same list with impact factors added
        """
        return self.enrich_all(
            papers,
            enrich_impact_factors=True,
            enrich_citations=False,
            enrich_journal_metrics=False,
        )

    def enrich_citations(self, papers: List[Paper]) -> List[Paper]:
        """
        Enrich papers with citation counts only.

        Args:
            papers: List of papers to enrich

        Returns:
            Same list with citation counts added
        """
        return self.enrich_all(
            papers,
            enrich_impact_factors=False,
            enrich_citations=True,
            enrich_journal_metrics=False,
        )

    # Private methods for impact factor functionality

    def _init_impact_factor_package(self) -> None:
        """Initialize impact_factor package if available."""
        if self.use_impact_factor_package:
            try:
                from impact_factor.core import Factor

                self._impact_factor_instance = Factor()
                logger.info(
                    f"Impact factor package initialized (JCR {JCR_YEAR} data from impact_factor package)"
                )
            except ImportError:
                logger.warning(
                    "impact_factor package not available. Install with: pip install impact-factor\n"
                    "Journal impact factors will use fallback data if available."
                )
                self._impact_factor_instance = None

    def _load_journal_data(self) -> None:
        """Load custom journal data if provided."""
        if self.journal_data_path and self.journal_data_path.exists():
            try:
                import json

                with open(self.journal_data_path, "r") as f:
                    self._journal_data = json.load(f)
                logger.info(
                    f"Loaded custom journal data from {self.journal_data_path}"
                )
            except Exception as e:
                logger.warning(f"Failed to load custom journal data: {e}")
                self._journal_data = None
        else:
            self._journal_data = None

    def _enrich_journal_data(
        self,
        papers: List[Paper],
        include_impact_factors: bool = True,
        include_metrics: bool = True,
    ) -> None:
        """
        Enrich papers with journal-related data.

        Args:
            papers: Papers to enrich (modified in-place)
            include_impact_factors: Add impact factors
            include_metrics: Add quartiles, rankings
        """
        enriched_count: int = 0

        for paper in papers:
            if not paper.journal:
                continue

            metrics = self._get_journal_metrics(paper.journal)
            if not metrics:
                continue

            # Add requested data
            if include_impact_factors and "impact_factor" in metrics:
                paper.impact_factor = metrics["impact_factor"]
                paper.impact_factor_source = metrics.get(
                    "source", f"JCR {JCR_YEAR}"
                )
                paper.metadata["impact_factor_source"] = (
                    paper.impact_factor_source
                )
                enriched_count += 1

            if include_metrics:
                if "quartile" in metrics:
                    paper.journal_quartile = metrics["quartile"]
                    paper.quartile_source = metrics.get(
                        "source", f"JCR {JCR_YEAR}"
                    )
                    paper.metadata["quartile_source"] = paper.quartile_source
                if "rank" in metrics:
                    paper.journal_rank = metrics["rank"]
                if "h_index" in metrics:
                    paper.h_index = metrics["h_index"]

        logger.info(
            f"Enriched {enriched_count}/{len(papers)} papers with journal data"
        )

    def _get_journal_metrics_uncached(
        self, journal_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get journal metrics from available sources (uncached version).

        Args:
            journal_name: Name of the journal

        Returns:
            Dictionary with available metrics or None
        """
        metrics: Dict[str, Any] = {}

        # Try impact_factor package first (real 2024 JCR data)
        if self._impact_factor_instance:
            try:
                # Search for journal
                search_results = self._impact_factor_instance.search(
                    journal_name
                )

                if search_results:
                    # Get best match
                    best_match = self._find_best_journal_match(
                        journal_name, [r["journal"] for r in search_results]
                    )

                    if best_match:
                        # Find the matching result
                        for result in search_results:
                            if result["journal"] == best_match:
                                factor_value = result.get("factor")
                                if factor_value is not None:
                                    metrics["impact_factor"] = float(
                                        factor_value
                                    )
                                metrics["quartile"] = result.get(
                                    "jcr", "Unknown"
                                )
                                metrics["rank"] = result.get("rank")
                                metrics["source"] = f"JCR {JCR_YEAR}"
                                break

            except Exception as e:
                logger.debug(
                    f"Impact factor lookup failed for '{journal_name}': {e}"
                )

        # Fall back to custom data if no impact factor found
        if not metrics and self._journal_data:
            normalized_name = self._normalize_journal_name(journal_name)
            if normalized_name in self._journal_data:
                custom_metrics = self._journal_data[normalized_name]
                metrics.update(custom_metrics)
                metrics["source"] = "Custom data"

        return metrics if metrics else None

    def _find_best_journal_match(
        self, query: str, candidates: List[str], threshold: float = 0.85
    ) -> Optional[str]:
        """
        Find best matching journal name from candidates.

        Args:
            query: Journal name to match
            candidates: List of candidate journal names
            threshold: Minimum similarity score

        Returns:
            Best matching journal name or None
        """
        if not candidates:
            return None

        query_normalized = self._normalize_journal_name(query)
        best_match: Optional[str] = None
        best_score: float = 0.0

        for candidate in candidates:
            candidate_normalized = self._normalize_journal_name(candidate)
            score = SequenceMatcher(
                None, query_normalized, candidate_normalized
            ).ratio()

            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate

        return best_match

    def _normalize_journal_name(self, name: str) -> str:
        """Normalize journal name for matching."""
        import re

        # Convert to lowercase and remove punctuation
        normalized = name.lower()
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = " ".join(normalized.split())
        return normalized

    # Private methods for citation functionality

    async def _enrich_citations_async(
        self, papers: List[Paper]
    ) -> List[Paper]:
        """
        Asynchronously enrich papers with citation counts.

        Args:
            papers: Papers to enrich

        Returns:
            Same list with citations added where possible
        """
        # Group papers that need citation enrichment
        papers_needing_citations: List[Tuple[int, Paper]] = [
            (i, p) for i, p in enumerate(papers) if p.citation_count is None
        ]

        if not papers_needing_citations:
            logger.info("All papers already have citation counts")
            return papers

        logger.info(
            f"Enriching {len(papers_needing_citations)} papers with citation counts"
        )

        # Create tasks for concurrent enrichment
        tasks = [
            self._get_citation_count_for_paper(paper)
            for _, paper in papers_needing_citations
        ]

        # Run with semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

        async def limited_task(task):
            async with semaphore:
                return await task

        results = await asyncio.gather(
            *[limited_task(task) for task in tasks], return_exceptions=True
        )

        # Update papers with results
        enriched_count: int = 0
        for (idx, paper), result in zip(papers_needing_citations, results):
            if isinstance(result, Exception):
                logger.debug(
                    f"Failed to get citations for '{paper.title[:50]}...': {result}"
                )
            elif result is not None:
                paper.citation_count = result
                enriched_count += 1

        logger.info(
            f"Successfully enriched {enriched_count}/{len(papers_needing_citations)} papers with citations"
        )
        return papers

    async def _get_citation_count_for_paper(
        self, paper: Paper
    ) -> Optional[int]:
        """
        Get citation count for a single paper.

        Args:
            paper: Paper to get citation count for

        Returns:
            Citation count or None
        """
        # Try CrossRef first if DOI is available
        if paper.doi:
            try:
                from ..web._search_pubmed import get_crossref_metrics

                metrics = get_crossref_metrics(
                    paper.doi, api_key=self.crossref_api_key, email=self.email
                )
                if metrics and "citations" in metrics:
                    logger.debug(
                        f"Got citation count from CrossRef for {paper.doi}: {metrics['citations']}"
                    )
                    # Update paper metadata to indicate source
                    paper.metadata["citation_count_source"] = "CrossRef"
                    return metrics["citations"]
            except Exception as e:
                logger.debug(
                    f"CrossRef citation lookup failed for {paper.doi}: {e}"
                )

        # Fall back to Semantic Scholar
        # Import here to avoid circular dependency
        from ._SearchEngines import SemanticScholarEngine

        # Build search query
        query: Optional[str] = None
        if paper.doi:
            query = f"doi:{paper.doi}"
        elif paper.title:
            query = paper.title
        else:
            return None

        try:
            # Create Semantic Scholar engine
            semantic_scholar_engine = SemanticScholarEngine(
                api_key=self.semantic_scholar_api_key
            )

            # Search for the paper
            results = await semantic_scholar_engine.search(query, limit=3)

            # Find best match
            for result in results:
                # Check if titles match
                if self._papers_match(paper, result):
                    # Update metadata to indicate source
                    paper.metadata["citation_count_source"] = (
                        "Semantic Scholar"
                    )
                    return result.citation_count

        except Exception as e:
            logger.debug(f"Semantic Scholar citation lookup failed: {e}")

        return None

    def _papers_match(
        self, paper1: Paper, paper2: Paper, threshold: float = 0.85
    ) -> bool:
        """
        Check if two papers are the same.

        Args:
            paper1: First paper
            paper2: Second paper
            threshold: Similarity threshold for title matching

        Returns:
            True if papers match
        """
        # Check DOI match first (most reliable)
        if paper1.doi and paper2.doi:
            return paper1.doi.lower() == paper2.doi.lower()

        # Check title match
        if paper1.title and paper2.title:
            return self._titles_match(paper1.title, paper2.title, threshold)

        return False

    def _titles_match(
        self, title1: str, title2: str, threshold: float = 0.85
    ) -> bool:
        """
        Check if two titles match using fuzzy matching.

        Args:
            title1: First title
            title2: Second title
            threshold: Minimum similarity score

        Returns:
            True if titles match
        """
        if not title1 or not title2:
            return False

        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Exact match
        if t1 == t2:
            return True

        # Fuzzy match
        similarity = SequenceMatcher(None, t1, t2).ratio()
        return similarity >= threshold

    def get_enrichment_stats(self, papers: List[Paper]) -> Dict[str, Any]:
        """
        Get statistics about enrichment coverage.

        Args:
            papers: List of papers to analyze

        Returns:
            Dictionary with enrichment statistics
        """
        total = len(papers)
        if total == 0:
            return {
                "total_papers": 0,
                "with_impact_factor": 0,
                "with_citations": 0,
                "with_quartile": 0,
                "fully_enriched": 0,
                "coverage_percentage": 0.0,
            }

        with_if = sum(1 for p in papers if p.impact_factor is not None)
        with_cite = sum(1 for p in papers if p.citation_count is not None)
        with_quartile = sum(
            1 for p in papers if p.journal_quartile is not None
        )
        fully_enriched = sum(
            1
            for p in papers
            if p.impact_factor is not None and p.citation_count is not None
        )

        return {
            "total_papers": total,
            "with_impact_factor": with_if,
            "with_citations": with_cite,
            "with_quartile": with_quartile,
            "fully_enriched": fully_enriched,
            "impact_factor_coverage": (with_if / total) * 100,
            "citation_coverage": (with_cite / total) * 100,
            "quartile_coverage": (with_quartile / total) * 100,
            "full_coverage": (fully_enriched / total) * 100,
        }


# Convenience functions for backward compatibility


def _enrich_papers_with_all(
    papers: List[Paper],
    semantic_scholar_api_key: Optional[str] = None,
    **kwargs,
) -> List[Paper]:
    """
    Convenience function to enrich papers with all available data.

    Args:
        papers: List of papers to enrich
        semantic_scholar_api_key: Optional API key
        **kwargs: Additional arguments for MetadataEnricher

    Returns:
        Enriched papers
    """
    enricher = MetadataEnricher(
        semantic_scholar_api_key=semantic_scholar_api_key, **kwargs
    )
    return enricher.enrich_all(papers)


def _enrich_papers_with_impact_factors(
    papers: List[Paper], use_impact_factor_package: bool = True
) -> List[Paper]:
    """
    Convenience function to enrich papers with impact factors only.

    Args:
        papers: List of papers
        use_impact_factor_package: Whether to use impact_factor package

    Returns:
        Papers with impact factors
    """
    enricher = MetadataEnricher(
        use_impact_factor_package=use_impact_factor_package
    )
    return enricher.enrich_impact_factors(papers)


def _enrich_papers_with_citations(
    papers: List[Paper], semantic_scholar_api_key: Optional[str] = None
) -> List[Paper]:
    """
    Convenience function to enrich papers with citations only.

    Args:
        papers: List of papers
        semantic_scholar_api_key: Optional API key

    Returns:
        Papers with citation counts
    """
    enricher = MetadataEnricher(
        semantic_scholar_api_key=semantic_scholar_api_key
    )
    return enricher.enrich_citations(papers)


__all__ = [
    "UnifiedEnricher",
    "_enrich_papers_with_all",
    "_enrich_papers_with_impact_factors",
    "_enrich_papers_with_citations",
]

# EOF
