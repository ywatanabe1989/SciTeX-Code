#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:33:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_KeywordsEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_KeywordsEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Keyword enricher using DOI sources."""

from scitex import logging
from typing import List, Optional

from .._Paper import Paper
from ..doi._SingleDOIResolver import SingleDOIResolver
from ._BaseEnricher import BaseEnricher

logger = logging.getLogger(__name__)


class KeywordEnricher(BaseEnricher):
    """Enriches papers with keywords from various sources."""

    def __init__(
        self,
        email_crossref: str = "research@example.com",
        email_pubmed: str = "research@example.com",
        email_openalex: str = "research@example.com",
        email_semantic_scholar: str = "research@example.com",
        sources: Optional[List[str]] = None,
    ):
        self.resolver = SingleDOIResolver(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
            sources=sources or ["semantic_scholar", "crossref", "pubmed"],
        )

    @property
    def name(self) -> str:
        return "KeywordEnricher"

    def can_enrich(self, paper: Paper) -> bool:
        """Check if paper needs keywords."""
        return not paper.keywords and paper.doi is not None

    def enrich(self, papers: List[Paper]) -> None:
        """Add keywords to papers."""
        papers_to_enrich = [p for p in papers if self.can_enrich(p)]
        if not papers_to_enrich:
            return

        count = 0
        for paper in papers_to_enrich:
            # Try to get comprehensive metadata which may include keywords
            metadata = self.resolver.get_comprehensive_metadata(
                title=paper.title, year=paper.year, authors=paper.authors
            )

            if metadata and metadata.get("keywords"):
                source_name = metadata.get("source", "unknown")
                paper.update_field_with_source(
                    "keywords", metadata["keywords"], source_name
                )
                count += 1
                logger.debug(
                    f"Found keywords for '{paper.title[:50]}...' from {source_name}"
                )

        if count:
            logger.info(f"Enriched {count} papers with keywords")

# EOF
