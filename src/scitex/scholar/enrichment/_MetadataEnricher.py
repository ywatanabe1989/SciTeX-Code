#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:55:06 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_MetadataEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_MetadataEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Metadata enrichment module for SciTeX Scholar.

This module orchestrates enrichment using specialized enrichers."""

from scitex import logging
from typing import Any, Dict, List, Optional

from ...errors import EnrichmentError, warn_performance
from .._Paper import Paper
from ._EnricherPipeline import EnricherPipeline

logger = logging.getLogger(__name__)


class MetadataEnricher:
    """Metadata enricher for scientific papers.

    Orchestrates enrichment through a pipeline of specialized enrichers."""

    def __init__(
        self,
        config: Optional[Any] = None,
        semantic_scholar_api_key: Optional[str] = None,
        crossref_api_key: Optional[str] = None,
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        cache_size: int = 1000,
    ) -> None:
        """Initialize unified enricher.

        Email priority:
        1. Source-specific parameters (email_crossref, etc.)
        2. Config object attributes
        3. Environment variables (SCITEX_SCHOLAR_*_EMAIL)
        4. General email parameter
        5. Default fallback
        """
        # Default fallback
        default_email = "research@example.com"

        # Handle API keys
        if config:
            self.semantic_scholar_api_key = getattr(
                config, "semantic_scholar_api_key", semantic_scholar_api_key
            )
            self.crossref_api_key = getattr(
                config, "crossref_api_key", crossref_api_key
            )
        else:
            self.semantic_scholar_api_key = semantic_scholar_api_key
            self.crossref_api_key = crossref_api_key

        # Handle emails with priority
        if config:
            # Get from config, then env vars, then general email
            final_email_crossref = (
                email_crossref
                or getattr(config, "crossref_email", None)
                or os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL")
                or default_email
            )
            final_email_pubmed = (
                email_pubmed
                or getattr(config, "pubmed_email", None)
                or os.getenv("SCITEX_SCHOLAR_PUBMED_EMAIL")
                or default_email
            )
            final_email_openalex = (
                email_openalex
                or getattr(config, "openalex_email", None)
                or os.getenv("SCITEX_SCHOLAR_OPENALEX_EMAIL")
                or default_email
            )
            final_email_semantic_scholar = (
                email_semantic_scholar
                or getattr(config, "semantic_scholar_email", None)
                or os.getenv("SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_EMAIL")
                or default_email
            )
        else:
            # Direct params -> env vars -> general email -> default
            final_email_crossref = (
                email_crossref
                or os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL")
                or default_email
            )
            final_email_pubmed = (
                email_pubmed
                or os.getenv("SCITEX_SCHOLAR_PUBMED_EMAIL")
                or default_email
            )
            final_email_openalex = (
                email_openalex
                or os.getenv("SCITEX_SCHOLAR_OPENALEX_EMAIL")
                or default_email
            )
            final_email_semantic_scholar = (
                email_semantic_scholar
                or os.getenv("SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_EMAIL")
                or default_email
            )

        # Store for reference
        self.email_crossref = email_crossref
        self.email_pubmed = email_pubmed
        self.email_openalex = email_openalex
        self.email_semantic_scholar = email_semantic_scholar

        # Initialize the pipeline
        self._pipeline = EnricherPipeline(
            email_crossref=final_email_crossref,
            email_pubmed=final_email_pubmed,
            email_openalex=final_email_openalex,
            email_semantic_scholar=final_email_semantic_scholar,
            semantic_scholar_api_key=self.semantic_scholar_api_key,
        )

    def enrich_all(
        self,
        papers: List[Paper],
        enrich_impact_factors: bool = True,
        enrich_citations: bool = True,
        enrich_journal_metrics: bool = True,
        enrich_abstracts: bool = True,
        parallel: bool = True,
        use_semantic_scholar_for_citations: bool = True,
    ) -> List[Paper]:
        """Enrich papers with all available metadata.

        Args:
            papers: List of papers to enrich
            enrich_impact_factors: Add journal impact factors
            enrich_citations: Add citation counts
            enrich_journal_metrics: Add quartiles, rankings
            enrich_abstracts: Add abstracts
            parallel: Use parallel processing (kept for compatibility)
            use_semantic_scholar_for_citations: Use SS for citations (kept for compatibility)

        Returns:
            Same list with papers enriched in-place
        """
        if not papers:
            return papers

        logger.info(f"Starting enrichment for {len(papers)} papers")

        # Use pipeline to enrich
        self._pipeline.enrich(papers)

        logger.info("Enrichment completed")
        return papers

    def enrich_dois(self, papers: List[Paper]) -> List[Paper]:
        """Enrich papers with DOIs only."""
        if not papers:
            return papers

        self._pipeline.doi_enricher.enrich(papers)
        return papers

    def enrich_impact_factors(self, papers: List[Paper]) -> List[Paper]:
        """Enrich papers with journal impact factors only."""
        if not papers:
            return papers

        # Ensure DOIs first
        self._pipeline.doi_enricher.enrich(papers)
        # Only run impact factor enricher
        self._pipeline.impact_enricher.enrich(papers)
        return papers

    def enrich_citations(self, papers: List[Paper]) -> List[Paper]:
        """Enrich papers with citation counts only."""
        if not papers:
            return papers

        # Ensure DOIs first, then citations
        self._pipeline.doi_enricher.enrich(papers)
        self._pipeline.citation_enricher.enrich(papers)
        return papers

    def enrich_abstracts(self, papers: List[Paper]) -> List[Paper]:
        """Enrich papers with abstracts only."""
        if not papers:
            return papers

        # Ensure DOIs first, then abstracts
        self._pipeline.doi_enricher.enrich(papers)
        self._pipeline.abstract_enricher.enrich(papers)
        return papers

    def get_enrichment_stats(self, papers: List[Paper]) -> Dict[str, Any]:
        """Get statistics about enrichment coverage."""
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
        with_abstract = sum(1 for p in papers if p.abstract)
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
            "with_abstract": with_abstract,
            "fully_enriched": fully_enriched,
            "impact_factor_coverage": (with_if / total) * 100,
            "citation_coverage": (with_cite / total) * 100,
            "quartile_coverage": (with_quartile / total) * 100,
            "abstract_coverage": (with_abstract / total) * 100,
            "full_coverage": (fully_enriched / total) * 100,
        }


# Convenience functions for backward compatibility
def _enrich_papers_with_all(
    papers: List[Paper],
    semantic_scholar_api_key: Optional[str] = None,
    **kwargs,
) -> List[Paper]:
    """Convenience function to enrich papers with all available data."""
    enricher = MetadataEnricher(
        semantic_scholar_api_key=semantic_scholar_api_key, **kwargs
    )
    return enricher.enrich_all(papers)


def _enrich_papers_with_impact_factors(
    papers: List[Paper], use_impact_factor_package: bool = True
) -> List[Paper]:
    """Convenience function to enrich papers with impact factors only."""
    enricher = MetadataEnricher()
    return enricher.enrich_impact_factors(papers)


def _enrich_papers_with_citations(
    papers: List[Paper], semantic_scholar_api_key: Optional[str] = None
) -> List[Paper]:
    """Convenience function to enrich papers with citations only."""
    enricher = MetadataEnricher(
        semantic_scholar_api_key=semantic_scholar_api_key
    )
    return enricher.enrich_citations(papers)


def _enrich_papers_with_abstracts(
    papers: List[Paper], **kwargs
) -> List[Paper]:
    """Convenience function to enrich papers with abstracts only."""
    enricher = MetadataEnricher(**kwargs)
    return enricher.enrich_abstracts(papers)


__all__ = [
    "MetadataEnricher",
    "_enrich_papers_with_all",
    "_enrich_papers_with_impact_factors",
    "_enrich_papers_with_citations",
    "_enrich_papers_with_abstracts",
]

# EOF
